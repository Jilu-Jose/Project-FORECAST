"""Pydantic schemas for audit data structures."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ── Severity & Verdict enums ──────────────────────────────────────────────────

class Severity(str, Enum):
    critical = "critical"
    warning = "warning"
    info = "info"


class BenchmarkVerdict(str, Enum):
    realistic = "realistic"
    aggressive = "aggressive"
    unrealistic = "unrealistic"
    unknown = "unknown"


# ── Core finding models ───────────────────────────────────────────────────────

class FormulaAnomaly(BaseModel):
    """A detected formula-level issue in a spreadsheet cell."""
    sheet: str
    cell: str
    issue_type: Literal[
        "broken_ref",
        "hardcoded_in_formula",
        "inconsistent_pattern",
        "error_value",
        "circular_ref",
    ]
    description: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)


class Assumption(BaseModel):
    """An extracted financial assumption from the model."""
    name: str                # e.g. "MoM Growth Rate"
    sheet: str
    cell: str
    value: float
    unit: str                # "%", "INR", "USD", "months"
    benchmark_range: str | None = None
    benchmark_verdict: BenchmarkVerdict | None = None
    benchmark_source: str | None = None
    benchmark_reasoning: str | None = None


class ConsistencyIssue(BaseModel):
    """A cross-sheet or unit/currency consistency problem."""
    description: str
    sheets_involved: list[str]
    cells_involved: list[str]
    severity: Severity
    issue_type: Literal[
        "cross_sheet_mismatch",
        "unit_mismatch",
        "currency_mismatch",
        "magnitude_mismatch",
        "time_period_mismatch",
        "historical_projected_gap",
        "balance_sheet_imbalance",
    ] = "cross_sheet_mismatch"


class ScenarioResult(BaseModel):
    """Result of perturbing a single assumption."""
    assumption_perturbed: str
    perturbation: str        # e.g. "+20%", "-20%"
    impact_metric: str       # e.g. "runway_months", "year1_revenue"
    baseline_value: float
    perturbed_value: float
    delta_pct: float = 0.0   # percentage change


class CapTableIssue(BaseModel):
    """A cap table sanity check finding."""
    description: str
    severity: Severity
    cells_involved: list[str] = []
    issue_type: Literal[
        "ownership_sum",
        "dilution_math",
        "option_pool",
        "safe_conversion",
        "pre_post_money",
        "other",
    ] = "other"


# ── Sheet metadata ────────────────────────────────────────────────────────────

class SheetMetadata(BaseModel):
    """Metadata about a single sheet in the workbook."""
    name: str
    row_count: int
    col_count: int
    has_formulas: bool
    detected_type: Literal[
        "assumptions",
        "pnl",
        "cash_flow",
        "balance_sheet",
        "cap_table",
        "revenue",
        "costs",
        "headcount",
        "unknown",
    ] = "unknown"
    labeled_sections: list[str] = []


# ── API request/response models ──────────────────────────────────────────────

class AuditUploadResponse(BaseModel):
    """Response from /audit/upload."""
    job_id: str
    status: str = "queued"
    message: str = "Audit queued for processing"


class AuditStatusResponse(BaseModel):
    """Response from /audit/status/{job_id}."""
    job_id: str
    status: Literal["queued", "running", "complete", "error"]
    current_agent: str | None = None
    progress_pct: float = 0.0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class AuditReportResponse(BaseModel):
    """Response from /audit/report/{job_id}."""
    job_id: str
    company_name: str
    sector: str | None = None
    summary: AuditSummary | None = None
    formula_anomalies: list[FormulaAnomaly] = []
    assumptions: list[Assumption] = []
    consistency_issues: list[ConsistencyIssue] = []
    scenario_results: list[ScenarioResult] = []
    cap_table_issues: list[CapTableIssue] = []
    report_markdown: str = ""
    report_file_url: str | None = None
    created_at: datetime | None = None


class AuditSummary(BaseModel):
    """High-level summary of audit findings."""
    total_issues: int = 0
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    sheets_analyzed: int = 0
    assumptions_extracted: int = 0
    scenarios_run: int = 0


class AuditHistoryItem(BaseModel):
    """A single entry in audit history."""
    id: str
    company_name: str
    sector: str | None = None
    status: str
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    created_at: datetime
    completed_at: datetime | None = None


class VersionDiff(BaseModel):
    """Comparison between two audit versions."""
    audit_id_1: str
    audit_id_2: str
    company_name: str
    assumptions_changed: list[AssumptionChange] = []
    new_issues: list[str] = []
    resolved_issues: list[str] = []
    runway_delta: float | None = None
    summary: str = ""


class AssumptionChange(BaseModel):
    """A change in an assumption between two versions."""
    name: str
    old_value: float
    new_value: float
    old_verdict: BenchmarkVerdict | None = None
    new_verdict: BenchmarkVerdict | None = None
    delta_pct: float = 0.0
