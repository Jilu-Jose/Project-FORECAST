"""Structural Agent — detects formula anomalies, circular references,
error values, and inconsistent patterns using algorithmic checks + NIM.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import networkx as nx

from app.agents.state import AuditState
from app.agents.ingestion import get_cached_workbook
from app.services.llm import get_nim_client
from app.services.spreadsheet import find_circular_references, find_formula_inconsistencies
from app.utils.formula_parser import parse_formula

logger = logging.getLogger(__name__)

STRUCTURAL_SYSTEM_PROMPT = """You are a spreadsheet forensic auditor. Given a list of (cell, formula, precedents, value) tuples,
flag ONLY genuine anomalies: broken references, hardcoded numeric values inside formula cells that
should be formula-driven, formulas inconsistent with the pattern of adjacent cells in the same row/column,
and error values. For each, output: sheet, cell, issue_type, one-sentence description, severity
(critical/warning/info), confidence (0-1). Do not flag intentional constants (e.g. tax rate assumptions
in a clearly labeled assumptions block). Output strict JSON: {"anomalies": [...]}"""


async def structural_node(state: AuditState) -> dict:
    """Detect formula-level structural issues.

    Reads: file_path, dependency_graph
    Writes: formula_anomalies
    """
    logger.info("Structural Agent: analyzing formulas")

    anomalies = []
    wb_data = get_cached_workbook(state["file_path"])

    if not wb_data:
        return {
            "current_agent": "structural",
            "agent_errors": ["Structural Agent: no cached workbook data"],
            "formula_anomalies": [],
        }

    try:
        # ── 1. Circular reference detection (pure graph algorithm) ────────
        graph = wb_data.dependency_graph
        cycles = find_circular_references(graph)
        for cycle in cycles:
            # Each cycle is a list of cell refs
            for cell_ref in cycle:
                parts = cell_ref.split("!")
                sheet = parts[0] if len(parts) > 1 else "Unknown"
                cell = parts[-1]
                anomalies.append({
                    "sheet": sheet,
                    "cell": cell,
                    "issue_type": "circular_ref",
                    "description": f"Circular reference detected in cycle: {' → '.join(cycle[:5])}{'...' if len(cycle) > 5 else ''}",
                    "severity": "critical",
                    "confidence": 1.0,
                })

        # ── 2. Error value detection (pure parsing) ──────────────────────
        for err_cell in wb_data.error_cells:
            anomalies.append({
                "sheet": err_cell.sheet,
                "cell": err_cell.cell_ref,
                "issue_type": "error_value",
                "description": f"Cell contains error value: {err_cell.value}",
                "severity": "critical",
                "confidence": 1.0,
            })

        # ── 3. Formula inconsistency detection (algorithmic) ─────────────
        inconsistencies = find_formula_inconsistencies(wb_data)
        for qual_ref, sheet, reason in inconsistencies:
            cell = qual_ref.split("!")[-1]
            anomalies.append({
                "sheet": sheet,
                "cell": cell,
                "issue_type": "inconsistent_pattern",
                "description": reason,
                "severity": "warning",
                "confidence": 0.75,
            })

        # ── 4. Hardcoded values in formulas (detected during parsing) ────
        hardcoded_candidates = []
        for cell in wb_data.formula_cells:
            info = parse_formula(cell.formula, cell.sheet)
            # Flag formulas with hardcoded numbers that aren't simple
            # (more than just a constant — has refs AND constants)
            if info.hardcoded_numbers and info.precedent_refs:
                # This formula mixes refs and hardcoded numbers
                hardcoded_candidates.append({
                    "sheet": cell.sheet,
                    "cell": cell.cell_ref,
                    "formula": cell.formula,
                    "value": str(cell.value),
                    "label": cell.label or "",
                    "hardcoded_values": info.hardcoded_numbers,
                })

        # ── 5. NIM call for nuanced classification ───────────────────────
        if hardcoded_candidates:
            nim_anomalies = await _nim_classify_anomalies(hardcoded_candidates)
            anomalies.extend(nim_anomalies)

    except Exception as e:
        logger.error(f"Structural Agent error: {e}")
        return {
            "current_agent": "structural",
            "agent_errors": [f"Structural Agent error: {str(e)}"],
            "formula_anomalies": anomalies,
        }

    logger.info(f"Structural Agent: found {len(anomalies)} anomalies")
    return {
        "current_agent": "structural",
        "formula_anomalies": anomalies,
    }


async def _nim_classify_anomalies(candidates: list[dict]) -> list[dict]:
    """Send hardcoded-value candidates to LLM for nuanced classification."""
    anomalies = []
    nim = get_nim_client()

    # Batch in groups of 30
    batch_size = 30
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i : i + batch_size]

        prompt = (
            "Analyze these spreadsheet cells for genuine anomalies. "
            "Each entry has a formula with hardcoded numeric values mixed in. "
            "Determine if each hardcoded value is a genuine issue (should be a cell reference) "
            "or an intentional constant (like a tax rate or fixed multiplier).\n\n"
        )

        for j, c in enumerate(batch):
            prompt += (
                f"{j+1}. Sheet: {c['sheet']}, Cell: {c['cell']}, "
                f"Formula: {c['formula']}, Label: {c['label']}, "
                f"Hardcoded values: {c['hardcoded_values']}\n"
            )

        try:
            response = await nim.chat_json(
                messages=[
                    {"role": "system", "content": STRUCTURAL_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )

            if isinstance(response, dict) and "anomalies" in response:
                for a in response["anomalies"]:
                    if isinstance(a, dict) and "cell" in a:
                        anomalies.append({
                            "sheet": a.get("sheet", ""),
                            "cell": a.get("cell", ""),
                            "issue_type": a.get("issue_type", "hardcoded_in_formula"),
                            "description": a.get("description", "Hardcoded value in formula"),
                            "severity": a.get("severity", "warning"),
                            "confidence": float(a.get("confidence", 0.7)),
                        })
        except Exception as e:
            logger.warning(f"NIM classification batch failed: {e}")

    return anomalies
