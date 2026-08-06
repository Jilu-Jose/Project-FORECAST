"""Scenario & Sensitivity Agent — perturbs key assumptions and re-evaluates
the formula graph to measure impact on key output metrics.

Uses the `formulas` library for genuine Excel recalculation, not LLM guessing.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.agents.state import AuditState

logger = logging.getLogger(__name__)

# Perturbation levels
PERTURBATIONS = [
    ("+20%", 1.20),
    ("-20%", 0.80),
]

# Output metrics to track (heuristic label matching)
OUTPUT_METRIC_PATTERNS = {
    "runway_months": ["runway", "months of cash", "cash runway"],
    "ending_cash": ["ending cash", "cash balance", "cash & equiv", "total cash"],
    "year1_revenue": ["total revenue", "net revenue", "year 1 revenue", "revenue y1"],
    "year3_revenue": ["year 3 revenue", "revenue y3", "revenue year 3"],
    "monthly_burn": ["burn rate", "monthly burn", "cash burn", "net burn"],
    "ebitda": ["ebitda"],
}


async def scenario_node(state: AuditState) -> dict:
    """Run scenario/sensitivity analysis by perturbing assumptions.

    Reads: file_path, assumptions
    Writes: scenario_results
    """
    logger.info("Scenario Agent: running sensitivity analysis")

    assumptions = state.get("assumptions", [])
    file_path = state.get("file_path", "")

    if not assumptions:
        logger.info("Scenario Agent: no assumptions to perturb")
        return {"current_agent": "scenario", "scenario_results": []}

    results = []

    try:
        # Try to use the formulas library for genuine recalculation
        results = await _run_formulas_scenarios(file_path, assumptions)
    except Exception as e:
        logger.warning(f"Formulas library failed, falling back to estimation: {e}")
        # Fallback: use simple arithmetic estimation based on dependency fan-out
        results = _estimate_scenarios(assumptions, state)

    logger.info(f"Scenario Agent: generated {len(results)} scenario results")
    return {
        "current_agent": "scenario",
        "scenario_results": results,
    }


async def _run_formulas_scenarios(
    file_path: str, assumptions: list[dict]
) -> list[dict]:
    """Use the `formulas` library for genuine Excel recalculation."""
    import formulas

    results = []

    try:
        xl_model = formulas.ExcelModel().loads(file_path).finish()
    except Exception as e:
        logger.error(f"Failed to load ExcelModel: {e}")
        raise

    # Get the workbook name for cell reference formatting
    wb_name = Path(file_path).name

    # First, calculate baseline values
    try:
        baseline = xl_model.calculate()
    except Exception as e:
        logger.warning(f"Baseline calculation failed: {e}")
        raise

    # Find output cells by scanning baseline results for metric labels
    output_cells = _find_output_cells(baseline, wb_name)

    if not output_cells:
        logger.warning("Scenario Agent: could not identify output metric cells")
        raise ValueError("No output metric cells found")

    # For each assumption, perturb and recalculate
    for assumption in assumptions[:10]:  # Limit to top 10 assumptions
        sheet = assumption.get("sheet", "")
        cell = assumption.get("cell", "")
        value = assumption.get("value", 0)
        name = assumption.get("name", "Unknown")

        if value == 0:
            continue

        # Build the qualified cell reference for the formulas library
        # Format: "'[workbook.xlsx]Sheet1'!B2"
        qual_ref = f"'[{wb_name}]{sheet}'!{cell}"

        for perturbation_label, multiplier in PERTURBATIONS:
            perturbed_value = value * multiplier

            try:
                perturbed = xl_model.calculate(
                    inputs={qual_ref: perturbed_value},
                )

                # Compare output metrics
                for metric_name, metric_cell in output_cells.items():
                    baseline_val = _get_cell_value(baseline, metric_cell)
                    perturbed_val = _get_cell_value(perturbed, metric_cell)

                    if baseline_val is not None and perturbed_val is not None:
                        delta_pct = 0.0
                        if baseline_val != 0:
                            delta_pct = ((perturbed_val - baseline_val) / abs(baseline_val)) * 100

                        results.append({
                            "assumption_perturbed": name,
                            "perturbation": perturbation_label,
                            "impact_metric": metric_name,
                            "baseline_value": round(float(baseline_val), 2),
                            "perturbed_value": round(float(perturbed_val), 2),
                            "delta_pct": round(delta_pct, 2),
                        })

            except Exception as e:
                logger.warning(f"Perturbation failed for {name} {perturbation_label}: {e}")

    return results


def _find_output_cells(baseline_results: dict, wb_name: str) -> dict[str, str]:
    """Scan calculation results to find cells matching output metric patterns."""
    output_cells = {}

    if not isinstance(baseline_results, dict):
        return output_cells

    for cell_ref, value in baseline_results.items():
        if not isinstance(value, (int, float)):
            continue

        cell_ref_str = str(cell_ref).lower()
        for metric_name, patterns in OUTPUT_METRIC_PATTERNS.items():
            if metric_name not in output_cells:
                for pattern in patterns:
                    if pattern.lower() in cell_ref_str:
                        output_cells[metric_name] = cell_ref
                        break

    return output_cells


def _get_cell_value(results: dict, cell_ref: str) -> float | None:
    """Extract a numeric value from calculation results."""
    val = results.get(cell_ref)
    if isinstance(val, (int, float)):
        return float(val)
    return None


def _estimate_scenarios(assumptions: list[dict], state: dict) -> list[dict]:
    """Fallback: estimate scenario impact using simple arithmetic.

    When the formulas library can't load the workbook (e.g., unsupported features),
    we use dependency graph fan-out as a proxy for impact magnitude.
    """
    results = []
    dep_graph = state.get("dependency_graph", {})
    edges = dep_graph.get("edges", [])

    # Count how many cells each assumption feeds into
    fanout_map: dict[str, int] = {}
    for assumption in assumptions:
        qual_ref = f"{assumption.get('sheet', '')}!{assumption.get('cell', '')}"
        fanout = sum(1 for src, _ in edges if src == qual_ref)
        fanout_map[assumption.get("name", "")] = fanout

    for assumption in assumptions[:10]:
        name = assumption.get("name", "Unknown")
        value = assumption.get("value", 0)
        fanout = fanout_map.get(name, 1)

        if value == 0:
            continue

        for perturbation_label, multiplier in PERTURBATIONS:
            perturbed_value = value * multiplier

            # Estimate: more downstream dependencies → larger impact
            estimated_impact = (multiplier - 1.0) * 100 * (1 + fanout * 0.1)

            results.append({
                "assumption_perturbed": name,
                "perturbation": perturbation_label,
                "impact_metric": "estimated_impact",
                "baseline_value": round(float(value), 2),
                "perturbed_value": round(float(perturbed_value), 2),
                "delta_pct": round(estimated_impact, 2),
            })

    return results
