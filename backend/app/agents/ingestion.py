"""Ingestion Agent — parses uploaded Excel file, builds dependency graph,
identifies sheet types, and prepares the initial audit state.
"""

from __future__ import annotations

import logging

from app.agents.state import AuditState
from app.services.spreadsheet import parse_workbook

logger = logging.getLogger(__name__)


async def ingestion_node(state: AuditState) -> dict:
    """Parse the uploaded spreadsheet and populate initial state.

    Reads: file_path
    Writes: dependency_graph, sheet_metadata, error_cells, has_cap_table
    """
    logger.info(f"Ingestion Agent: parsing {state['file_path']}")

    try:
        wb_data = parse_workbook(state["file_path"])
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return {
            "current_agent": "ingestion",
            "agent_errors": [f"Ingestion failed: {str(e)}"],
            "dependency_graph": {},
            "sheet_metadata": [],
            "error_cells": [],
            "has_cap_table": False,
        }

    # Serialize dependency graph to dict of edges
    dep_graph_dict = {
        "nodes": list(wb_data.dependency_graph.nodes()),
        "edges": list(wb_data.dependency_graph.edges()),
        "node_count": wb_data.dependency_graph.number_of_nodes(),
        "edge_count": wb_data.dependency_graph.number_of_edges(),
    }

    # Serialize sheet metadata
    sheet_meta = [sm.model_dump() for sm in wb_data.sheet_metadata]

    # Serialize error cells
    error_cells = [
        {
            "sheet": cell.sheet,
            "cell": cell.cell_ref,
            "qualified_ref": cell.qualified_ref,
            "value": str(cell.value),
            "formula": cell.formula,
        }
        for cell in wb_data.error_cells
    ]

    # Check if any sheet is a cap table
    has_cap_table = any(sm.detected_type == "cap_table" for sm in wb_data.sheet_metadata)

    # Store workbook data in a temporary location for downstream agents
    # We use a module-level cache since LangGraph state must be serializable
    _workbook_cache[state["file_path"]] = wb_data

    logger.info(
        f"Ingestion complete: {len(wb_data.sheets)} sheets, "
        f"{len(wb_data.formula_cells)} formula cells, "
        f"{len(wb_data.error_cells)} error cells, "
        f"cap_table={'yes' if has_cap_table else 'no'}"
    )

    return {
        "current_agent": "ingestion",
        "dependency_graph": dep_graph_dict,
        "sheet_metadata": sheet_meta,
        "error_cells": error_cells,
        "has_cap_table": has_cap_table,
    }


# Module-level cache for parsed workbook data (not serializable in state)
_workbook_cache: dict = {}


def get_cached_workbook(file_path: str):
    """Retrieve cached WorkbookData for downstream agents."""
    return _workbook_cache.get(file_path)


def clear_workbook_cache(file_path: str):
    """Clean up cached workbook data after pipeline completes."""
    _workbook_cache.pop(file_path, None)
