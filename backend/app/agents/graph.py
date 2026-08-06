"""LangGraph state machine — wires all agents into a sequential
pipeline with conditional cap table edge.
"""

from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.agents.state import AuditState
from app.agents.ingestion import ingestion_node, clear_workbook_cache
from app.agents.structural import structural_node
from app.agents.assumption import assumption_node
from app.agents.benchmark import benchmark_node
from app.agents.consistency import consistency_node
from app.agents.scenario import scenario_node
from app.agents.captable import captable_node
from app.agents.report import report_node

logger = logging.getLogger(__name__)


def cap_table_router(state: AuditState) -> Literal["captable", "report"]:
    """Route to cap table agent if a cap table sheet was detected."""
    if state.get("has_cap_table", False):
        logger.info("Router: cap table detected → running Cap Table Agent")
        return "captable"
    logger.info("Router: no cap table → skipping to Report Agent")
    return "report"


def build_audit_graph() -> StateGraph:
    """Build and compile the FORECAST audit pipeline graph.

    Pipeline:
        START → ingestion → structural → assumption → benchmark
              → consistency → scenario → [cap_table?] → report → END
    """
    builder = StateGraph(AuditState)

    # ── Add nodes ─────────────────────────────────────────────────────────
    builder.add_node("ingestion", ingestion_node)
    builder.add_node("structural", structural_node)
    builder.add_node("assumption", assumption_node)
    builder.add_node("benchmark", benchmark_node)
    builder.add_node("consistency", consistency_node)
    builder.add_node("scenario", scenario_node)
    builder.add_node("captable", captable_node)
    builder.add_node("report", report_node)

    # ── Wire edges (sequential pipeline) ──────────────────────────────────
    builder.add_edge(START, "ingestion")
    builder.add_edge("ingestion", "structural")
    builder.add_edge("structural", "assumption")
    builder.add_edge("assumption", "benchmark")
    builder.add_edge("benchmark", "consistency")
    builder.add_edge("consistency", "scenario")

    # Conditional edge: scenario → captable OR report
    builder.add_conditional_edges(
        "scenario",
        cap_table_router,
        {
            "captable": "captable",
            "report": "report",
        },
    )

    # Cap table always flows to report
    builder.add_edge("captable", "report")

    # Report is the terminal node
    builder.add_edge("report", END)

    return builder.compile()


# Compiled graph singleton
_audit_graph = None


def get_audit_graph():
    """Get or create the compiled audit graph."""
    global _audit_graph
    if _audit_graph is None:
        _audit_graph = build_audit_graph()
    return _audit_graph


async def run_audit(
    file_path: str,
    company_name: str,
    sector: str | None = None,
) -> AuditState:
    """Execute the full audit pipeline.

    Args:
        file_path: Path to the uploaded Excel file
        company_name: Name of the company being audited
        sector: Business sector for benchmark comparison
        llm_model: The LLM backend to use ("hybrid", "gemini", or "nim")

    Returns:
        The final AuditState with all findings.
    """
    graph = get_audit_graph()

    initial_state: AuditState = {
        "file_path": file_path,
        "company_name": company_name,
        "sector": sector,
        "dependency_graph": {},
        "sheet_metadata": [],
        "error_cells": [],
        "has_cap_table": False,
        "formula_anomalies": [],
        "assumptions": [],
        "consistency_issues": [],
        "scenario_results": [],
        "cap_table_issues": [],
        "report_markdown": "",
        "report_file_path": "",
        "prior_version_state": None,
        "current_agent": "starting",
        "agent_errors": [],
    }

    try:
        result = await graph.ainvoke(initial_state)
    finally:
        # Clean up cached workbook data
        clear_workbook_cache(file_path)

    return result
