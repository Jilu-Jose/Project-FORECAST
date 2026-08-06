"""LangGraph state schema for the FORECAST audit pipeline.

Uses TypedDict with Annotated reducers for append-only list updates,
allowing each agent node to return partial state updates.
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from app.models.schemas import (
    Assumption,
    CapTableIssue,
    ConsistencyIssue,
    FormulaAnomaly,
    ScenarioResult,
    SheetMetadata,
)


class AuditState(TypedDict):
    """Full state flowing through the LangGraph audit pipeline.

    Each agent reads what it needs and returns a dict with only the keys it updates.
    List fields use operator.add as the reducer → appending to existing lists.
    """

    # ── Input / metadata ──────────────────────────────────────────────────    # Upload info
    file_path: str
    company_name: str
    sector: str | None

    # ── Ingestion outputs ─────────────────────────────────────────────────
    # Serialized dependency graph edges: list of [source, target] pairs
    dependency_graph: dict
    sheet_metadata: Annotated[list[dict], operator.add]
    error_cells: Annotated[list[dict], operator.add]
    has_cap_table: bool

    # ── Agent outputs (append-only via reducer) ───────────────────────────
    formula_anomalies: Annotated[list[dict], operator.add]
    assumptions: Annotated[list[dict], operator.add]
    consistency_issues: Annotated[list[dict], operator.add]
    scenario_results: Annotated[list[dict], operator.add]
    cap_table_issues: Annotated[list[dict], operator.add]

    # ── Report ────────────────────────────────────────────────────────────
    report_markdown: str
    report_file_path: str

    # ── Version diffing ───────────────────────────────────────────────────
    prior_version_state: dict | None

    # ── Status tracking ───────────────────────────────────────────────────
    current_agent: str
    agent_errors: Annotated[list[str], operator.add]
