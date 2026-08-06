"""Assumption Extraction Agent — identifies key financial assumptions
from labeled cells using regex heuristics + NIM fallback.
"""

from __future__ import annotations

import logging
import re

from app.agents.state import AuditState
from app.agents.ingestion import get_cached_workbook
from app.services.llm import get_nim_client

logger = logging.getLogger(__name__)

# ── Known assumption patterns ─────────────────────────────────────────────────

ASSUMPTION_PATTERNS = {
    "Growth Rate": re.compile(r"growth\s*rate|revenue\s*growth|mom\s*growth|yoy\s*growth|cagr", re.IGNORECASE),
    "Churn Rate": re.compile(r"churn\s*rate|attrition|customer\s*churn", re.IGNORECASE),
    "CAC": re.compile(r"\bcac\b|customer\s*acquisition\s*cost|acquisition\s*cost", re.IGNORECASE),
    "LTV": re.compile(r"\bltv\b|\bclv\b|life\s*time\s*value|customer\s*lifetime", re.IGNORECASE),
    "Gross Margin": re.compile(r"gross\s*margin|gm\s*%", re.IGNORECASE),
    "Net Margin": re.compile(r"net\s*margin|net\s*profit\s*margin", re.IGNORECASE),
    "Burn Rate": re.compile(r"burn\s*rate|monthly\s*burn|cash\s*burn", re.IGNORECASE),
    "Runway": re.compile(r"runway|months\s*of\s*cash|cash\s*runway", re.IGNORECASE),
    "Conversion Rate": re.compile(r"conversion\s*rate|cvr|conv\s*rate", re.IGNORECASE),
    "ARPU": re.compile(r"\barpu\b|average\s*revenue\s*per\s*user", re.IGNORECASE),
    "MRR": re.compile(r"\bmrr\b|monthly\s*recurring\s*revenue", re.IGNORECASE),
    "ARR": re.compile(r"\barr\b|annual\s*recurring\s*revenue", re.IGNORECASE),
    "Tax Rate": re.compile(r"tax\s*rate|effective\s*tax|income\s*tax\s*rate", re.IGNORECASE),
    "Discount Rate": re.compile(r"discount\s*rate|wacc|cost\s*of\s*capital", re.IGNORECASE),
    "Inflation Rate": re.compile(r"inflation\s*rate|inflation", re.IGNORECASE),
    "Retention Rate": re.compile(r"retention\s*rate|customer\s*retention", re.IGNORECASE),
    "Payback Period": re.compile(r"payback\s*period|payback\s*months", re.IGNORECASE),
    "Operating Expenses": re.compile(r"opex|operating\s*expense|total\s*opex", re.IGNORECASE),
    "Headcount Growth": re.compile(r"headcount\s*growth|hiring\s*rate|team\s*growth", re.IGNORECASE),
    "Price": re.compile(r"\bprice\b|pricing|unit\s*price|avg\s*price|average\s*selling\s*price|\basp\b", re.IGNORECASE),
}

# Unit detection patterns
UNIT_PATTERNS = [
    (re.compile(r"%|percent|pct", re.IGNORECASE), "%"),
    (re.compile(r"₹|INR|rupee", re.IGNORECASE), "INR"),
    (re.compile(r"\$|USD|dollar", re.IGNORECASE), "USD"),
    (re.compile(r"month", re.IGNORECASE), "months"),
    (re.compile(r"year|annual", re.IGNORECASE), "years"),
    (re.compile(r"x|multiple|times", re.IGNORECASE), "x"),
]

ASSUMPTION_NIM_PROMPT = """You are a financial model analyst. Given a list of spreadsheet cells with their labels and values,
identify which ones represent key financial assumptions (growth rates, margins, costs, conversion metrics, etc.).

For each identified assumption, extract:
- name: A standardized name for the assumption
- sheet: The sheet name
- cell: The cell reference
- value: The numeric value
- unit: The unit ("%", "INR", "USD", "months", "x", etc.)

Only include genuine assumptions — not computed outputs or intermediate calculations.
Output strict JSON: {"assumptions": [...]}"""


async def assumption_node(state: AuditState) -> dict:
    """Extract key financial assumptions from the model.

    Reads: file_path
    Writes: assumptions
    """
    logger.info("Assumption Agent: extracting assumptions")

    wb_data = get_cached_workbook(state["file_path"])
    if not wb_data:
        return {
            "current_agent": "assumption",
            "agent_errors": ["Assumption Agent: no cached workbook data"],
            "assumptions": [],
        }

    assumptions = []
    unmatched_candidates = []

    try:
        # ── Pass 1: Regex/heuristic matching ─────────────────────────────
        for sheet_name, cells in wb_data.sheets.items():
            for cell in cells:
                if cell.label is None:
                    continue
                if cell.data_type == "f":
                    # Skip formula cells — we want input assumptions
                    continue
                if not isinstance(cell.value, (int, float)):
                    continue

                matched = False
                for metric_name, pattern in ASSUMPTION_PATTERNS.items():
                    if pattern.search(cell.label):
                        unit = _detect_unit(cell.label, cell.value)
                        assumptions.append({
                            "name": metric_name,
                            "sheet": cell.sheet,
                            "cell": cell.cell_ref,
                            "value": float(cell.value),
                            "unit": unit,
                        })
                        matched = True
                        break

                if not matched:
                    # Candidate for NIM fallback
                    unmatched_candidates.append({
                        "sheet": cell.sheet,
                        "cell": cell.cell_ref,
                        "label": cell.label,
                        "value": cell.value,
                    })

        # ── Pass 2: NIM fallback for ambiguous labels ────────────────────
        # Also look for unlabeled constants that feed many formulas
        high_fanout_constants = _find_high_fanout_constants(wb_data)
        unmatched_candidates.extend(high_fanout_constants)

        if unmatched_candidates:
            logger.info(f"Assumption Agent: sending {len(unmatched_candidates)} candidates to LLM")
            nim_assumptions = await _nim_extract_assumptions(unmatched_candidates)
            # De-duplicate: if NIM found something that our regex already found, skip it.
            # Simple heuristic: check cell refs.
            regex_cells = {a["cell"] for a in assumptions}
            for na in nim_assumptions:
                if na["cell"] not in regex_cells:
                    assumptions.append(na)

    except Exception as e:
        logger.error(f"Assumption Agent error: {e}")
        return {
            "current_agent": "assumption",
            "agent_errors": [f"Assumption Agent error: {str(e)}"],
            "assumptions": assumptions,
        }

    logger.info(f"Assumption Agent: found {len(assumptions)} assumptions total")
    return {
        "current_agent": "assumption",
        "assumptions": assumptions,
    }


def _detect_unit(label: str, value: float) -> str:
    """Detect the unit of an assumption from its label and value."""
    for pattern, unit in UNIT_PATTERNS:
        if pattern.search(label):
            return unit

    # Heuristic: if value is between 0 and 1, likely a percentage (stored as decimal)
    if 0 < abs(value) < 1:
        return "%"
    # If value is between 1 and 100 and label suggests a rate
    if 1 <= abs(value) <= 100 and re.search(r"rate|margin|pct|percent", label, re.IGNORECASE):
        return "%"

    return "absolute"


def _find_high_fanout_constants(wb_data) -> list[dict]:
    """Find constant cells that are referenced by many formula cells.

    These are likely unlabeled assumptions.
    """
    candidates = []
    graph = wb_data.dependency_graph

    for node in graph.nodes():
        # Check out-degree (number of cells that depend on this)
        if graph.out_degree(node) >= 3:
            # This cell feeds 3+ formulas — might be an assumption
            cell_data = wb_data.all_cells.get(node)
            if cell_data and cell_data.data_type != "f" and isinstance(cell_data.value, (int, float)):
                candidates.append({
                    "sheet": cell_data.sheet,
                    "cell": cell_data.cell_ref,
                    "label": cell_data.label or f"[unlabeled, feeds {graph.out_degree(node)} cells]",
                    "value": cell_data.value,
                })

    return candidates[:30]  # Limit to avoid excessive NIM calls


async def _nim_extract_assumptions(candidates: list[dict]) -> list[dict]:
    """Use LLM to classify ambiguous cells as assumptions."""
    assumptions = []
    nim = get_nim_client()

    # Batch in groups of 25
    batch_size = 25
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i : i + batch_size]

        prompt = "Analyze these spreadsheet cells and identify any that are key financial assumptions:\n\n"
        for j, c in enumerate(batch):
            prompt += f"{j+1}. Sheet: {c['sheet']}, Cell: {c['cell']}, Label: {c['label']}, Value: {c['value']}\n"

        try:
            response = await nim.chat_json(
                messages=[
                    {"role": "system", "content": ASSUMPTION_NIM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )

            if isinstance(response, dict) and "assumptions" in response:
                for a in response["assumptions"]:
                    if isinstance(a, dict) and "name" in a:
                        assumptions.append({
                            "name": a.get("name", "Unknown"),
                            "sheet": a.get("sheet", ""),
                            "cell": a.get("cell", ""),
                            "value": float(a.get("value", 0)),
                            "unit": a.get("unit", "absolute"),
                        })
        except Exception as e:
            logger.warning(f"NIM assumption extraction batch failed: {e}")

    return assumptions
