"""Cap Table Agent — validates equity structure, dilution math,
option pools, and SAFE conversion logic. Only runs when a cap table
sheet is detected (conditional LangGraph edge).
"""

from __future__ import annotations

import logging
import re

from app.agents.state import AuditState
from app.agents.ingestion import get_cached_workbook
from app.services.llm import get_nim_client

logger = logging.getLogger(__name__)

CAP_TABLE_SYSTEM_PROMPT = """You are a startup cap table auditor. Given cap table data extracted from a spreadsheet,
identify any issues with:
1. Ownership percentages not summing to 100%
2. Dilution math errors (pre/post money inconsistencies)
3. Option pool sizing outside standard ranges (typically 10-20% for early stage)
4. SAFE/convertible note conversion logic errors
5. Pre-money vs post-money valuation calculation errors

For each issue found, output: description, severity (critical/warning/info), cells_involved, issue_type.
Output strict JSON: {"issues": [...]}"""


async def captable_node(state: AuditState) -> dict:
    """Validate cap table structure and math.

    Reads: file_path, has_cap_table
    Writes: cap_table_issues
    """
    logger.info("Cap Table Agent: analyzing equity structure")

    if not state.get("has_cap_table", False):
        logger.info("Cap Table Agent: no cap table detected, skipping")
        return {"current_agent": "captable"}

    wb_data = get_cached_workbook(state["file_path"])
    if not wb_data:
        return {
            "current_agent": "captable",
            "agent_errors": ["Cap Table Agent: no cached workbook data"],
            "cap_table_issues": [],
        }

    issues = []

    try:
        # Find cap table sheet(s)
        cap_sheets = [
            sm for sm in wb_data.sheet_metadata
            if sm.detected_type == "cap_table"
        ]

        for sheet_meta in cap_sheets:
            cells = wb_data.sheets.get(sheet_meta.name, [])

            # ── 1. Check ownership percentage sum ────────────────────────
            ownership_issues = _check_ownership_sum(cells, sheet_meta.name)
            issues.extend(ownership_issues)

            # ── 2. Check option pool sizing ──────────────────────────────
            pool_issues = _check_option_pool(cells, sheet_meta.name)
            issues.extend(pool_issues)

            # ── 3. NIM-powered deep analysis ─────────────────────────────
            nim_issues = await _nim_analyze_captable(cells, sheet_meta.name)
            issues.extend(nim_issues)

    except Exception as e:
        logger.error(f"Cap Table Agent error: {e}")
        return {
            "current_agent": "captable",
            "agent_errors": [f"Cap Table Agent error: {str(e)}"],
            "cap_table_issues": issues,
        }

    logger.info(f"Cap Table Agent: found {len(issues)} issues")
    return {
        "current_agent": "captable",
        "cap_table_issues": issues,
    }


def _check_ownership_sum(cells: list, sheet_name: str) -> list[dict]:
    """Check that ownership percentages sum to ~100%."""
    issues = []

    # Find cells that look like ownership percentages
    ownership_cells = []
    for cell in cells:
        if isinstance(cell.value, (int, float)):
            label = (cell.label or "").lower()
            if re.search(r"(%|percent|ownership|stake|share|equity)", label, re.IGNORECASE):
                if 0 < cell.value <= 100:
                    ownership_cells.append(cell)
                elif 0 < cell.value <= 1:
                    # Might be stored as decimal
                    ownership_cells.append(cell)

    if ownership_cells:
        # Determine if values are percentages or decimals
        values = [c.value for c in ownership_cells]
        total = sum(values)

        # If all values are <= 1, they're probably decimals
        if all(v <= 1 for v in values):
            total = total * 100

        if abs(total - 100) > 1.0:
            cell_refs = [f"{sheet_name}!{c.cell_ref}" for c in ownership_cells]
            issues.append({
                "description": f"Ownership percentages sum to {total:.1f}% instead of 100%",
                "severity": "critical" if abs(total - 100) > 5 else "warning",
                "cells_involved": cell_refs[:10],
                "issue_type": "ownership_sum",
            })

    return issues


def _check_option_pool(cells: list, sheet_name: str) -> list[dict]:
    """Check option pool sizing against standard ranges."""
    issues = []

    for cell in cells:
        label = (cell.label or "").lower()
        if re.search(r"option\s*pool|esop|stock\s*option", label, re.IGNORECASE):
            if isinstance(cell.value, (int, float)):
                pool_pct = cell.value
                if pool_pct <= 1:
                    pool_pct *= 100  # Convert decimal to percentage

                if pool_pct < 5:
                    issues.append({
                        "description": f"Option pool ({pool_pct:.1f}%) is unusually small — standard is 10-20% for early-stage companies",
                        "severity": "warning",
                        "cells_involved": [f"{sheet_name}!{cell.cell_ref}"],
                        "issue_type": "option_pool",
                    })
                elif pool_pct > 25:
                    issues.append({
                        "description": f"Option pool ({pool_pct:.1f}%) is unusually large — standard is 10-20% for early-stage companies",
                        "severity": "warning",
                        "cells_involved": [f"{sheet_name}!{cell.cell_ref}"],
                        "issue_type": "option_pool",
                    })

    return issues


async def _nim_analyze_captable(cells: list, sheet_name: str) -> list[dict]:
    """Use LLM for deeper cap table analysis (SAFE conversion, dilution math)."""
    issues = []
    nim = get_nim_client()

    # Extract relevant cap table data
    cap_data = []
    for cell in cells:
        if cell.value is not None:
            cap_data.append({
                "cell": cell.cell_ref,
                "label": cell.label or "",
                "value": str(cell.value),
                "formula": cell.formula or "",
            })

    if not cap_data:
        return issues

    # Limit data sent to NIM
    cap_data = cap_data[:60]

    prompt = f"Analyze this cap table data from sheet '{sheet_name}':\n\n"
    for entry in cap_data:
        prompt += f"Cell {entry['cell']}: Label='{entry['label']}', Value={entry['value']}"
        if entry['formula']:
            prompt += f", Formula={entry['formula']}"
        prompt += "\n"

    try:
        response = await nim.chat_json(
            messages=[
                {"role": "system", "content": CAP_TABLE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        if isinstance(response, dict) and "issues" in response:
            for issue in response["issues"]:
                if isinstance(issue, dict):
                    issues.append({
                        "description": issue.get("description", ""),
                        "severity": issue.get("severity", "info"),
                        "cells_involved": issue.get("cells_involved", []),
                        "issue_type": issue.get("issue_type", "other"),
                    })
    except Exception as e:
        logger.warning(f"NIM cap table analysis failed: {e}")

    return issues
