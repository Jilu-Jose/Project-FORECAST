"""Report Generation Agent — compiles the final findings into a comprehensive
investor-grade report using NIM for narrative generation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.agents.state import AuditState
from app.services.llm import get_nim_client

logger = logging.getLogger(__name__)

REPORT_SYSTEM_PROMPT = """You are compiling an investor-grade financial model audit. Given structural anomalies, assumption
benchmark verdicts, consistency issues, and scenario results, write a report with sections:
Executive Summary (3 sentences), Critical Issues, Warnings, Assumption Realism Table, Sensitivity
Summary, Recommendation. Reference exact sheet/cell for every finding. Be direct and specific —
no hedging language. Output markdown."""


async def report_node(state: AuditState) -> dict:
    """Compile all findings into a markdown report + generate files.

    Reads: all agent outputs
    Writes: report_markdown
    """
    logger.info("Report Agent: compiling audit report")

    try:
        # ── 1. Build structured summary ──────────────────────────────────
        formula_anomalies = state.get("formula_anomalies", [])
        assumptions = state.get("assumptions", [])
        consistency_issues = state.get("consistency_issues", [])
        scenario_results = state.get("scenario_results", [])
        cap_table_issues = state.get("cap_table_issues", [])
        agent_errors = state.get("agent_errors", [])

        # Count severities
        all_findings = formula_anomalies + consistency_issues + cap_table_issues
        critical_count = sum(1 for f in all_findings if f.get("severity") == "critical")
        warning_count = sum(1 for f in all_findings if f.get("severity") == "warning")
        info_count = sum(1 for f in all_findings if f.get("severity") == "info")

        # Count unrealistic assumptions
        unrealistic = [a for a in assumptions if a.get("benchmark_verdict") == "unrealistic"]
        aggressive = [a for a in assumptions if a.get("benchmark_verdict") == "aggressive"]

        # ── 2. Generate narrative with NIM ────────────────────────────
        report_md = await _generate_narrative(state)

        # ── 3. Prepend metadata header ───────────────────────────────────
        header = _build_report_header(
            company_name=state.get("company_name", "Unknown"),
            sector=state.get("sector"),
            sheets_analyzed=len(state.get("sheet_metadata", [])),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            assumptions_count=len(assumptions),
            scenarios_count=len(scenario_results),
            agent_errors=agent_errors,
        )

        full_report = header + "\n\n" + report_md

    except Exception as e:
        logger.error(f"Report Agent error: {e}")
        full_report = _build_fallback_report(state)
        return {
            "current_agent": "report",
            "agent_errors": [f"Report Agent error: {str(e)}"],
            "report_markdown": full_report,
        }

    logger.info(f"Report Agent: report generated ({len(full_report)} chars)")
    return {
        "current_agent": "report",
        "report_markdown": full_report,
    }


async def _generate_narrative(state: AuditState) -> str:
    """Use LLM to generate the narrative report."""
    nim = get_nim_client()
    company_name = state.get("company_name", "Unknown")
    sector = state.get("sector")
    formula_anomalies = state.get("formula_anomalies", [])
    assumptions = state.get("assumptions", [])
    consistency_issues = state.get("consistency_issues", [])
    scenario_results = state.get("scenario_results", [])
    cap_table_issues = state.get("cap_table_issues", [])
    
    all_findings = formula_anomalies + consistency_issues + cap_table_issues
    critical_count = sum(1 for f in all_findings if f.get("severity") == "critical")

    # Build the data summary for Gemini
    prompt = f"""Compile an investor-grade financial model audit report for {company_name} (sector: {sector or 'Unknown'}).

## Data for the report:

### Formula Anomalies ({len(formula_anomalies)} total, {critical_count} critical):
"""
    for a in formula_anomalies[:20]:
        prompt += f"- [{a.get('severity', 'info').upper()}] {a.get('sheet', '')}!{a.get('cell', '')}: {a.get('description', '')}\n"

    prompt += f"\n### Assumptions ({len(assumptions)} extracted):\n"
    for a in assumptions[:15]:
        verdict = a.get("benchmark_verdict", "not benchmarked")
        prompt += (
            f"- {a.get('name', 'Unknown')}: {a.get('value', 0)} {a.get('unit', '')} "
            f"[{verdict}] (benchmark: {a.get('benchmark_range', 'N/A')}, "
            f"source: {a.get('benchmark_source', 'N/A')})\n"
        )

    prompt += f"\n### Consistency Issues ({len(consistency_issues)} total):\n"
    for i in consistency_issues[:15]:
        prompt += f"- [{i.get('severity', 'info').upper()}] {i.get('description', '')}\n"

    prompt += f"\n### Scenario Results ({len(scenario_results)} perturbations):\n"
    for s in scenario_results[:20]:
        prompt += (
            f"- {s.get('assumption_perturbed', '')}{s.get('perturbation', '')}: "
            f"{s.get('impact_metric', '')} changes by {s.get('delta_pct', 0):.1f}% "
            f"({s.get('baseline_value', 0)} → {s.get('perturbed_value', 0)})\n"
        )

    if cap_table_issues:
        prompt += f"\n### Cap Table Issues ({len(cap_table_issues)} total):\n"
        for c in cap_table_issues[:10]:
            prompt += f"- [{c.get('severity', 'info').upper()}] {c.get('description', '')}\n"

    try:
        messages = [
            {"role": "system", "content": REPORT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        report = await nim.chat(
            messages=messages,
            temperature=0.3,
        )
        return report
    except Exception as e:
        logger.error(f"NIM report generation failed: {e}")
        # Build a structured fallback without LLM
        return _build_structured_sections(
            formula_anomalies, assumptions, consistency_issues,
            scenario_results, cap_table_issues
        )


def _build_report_header(
    company_name: str,
    sector: str | None,
    sheets_analyzed: int,
    critical_count: int,
    warning_count: int,
    info_count: int,
    assumptions_count: int,
    scenarios_count: int,
    agent_errors: list[str],
) -> str:
    """Build the metadata header for the report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    header = f"""# FORECAST — Financial Model Audit Report

| Field | Value |
|-------|-------|
| **Company** | {company_name} |
| **Sector** | {sector or 'Not specified'} |
| **Date** | {now} |
| **Sheets Analyzed** | {sheets_analyzed} |
| **Critical Issues** | {critical_count} |
| **Warnings** | {warning_count} |
| **Info Items** | {info_count} |
| **Assumptions Extracted** | {assumptions_count} |
| **Scenarios Run** | {scenarios_count} |
"""

    if agent_errors:
        header += "\n> ⚠️ **Agent Errors**: Some agents encountered issues during processing:\n"
        for err in agent_errors:
            header += f"> - {err}\n"

    return header


def _build_structured_sections(
    formula_anomalies, assumptions, consistency_issues,
    scenario_results, cap_table_issues,
) -> str:
    """Build structured report sections without LLM (fallback)."""
    sections = []

    # Critical issues
    criticals = [f for f in formula_anomalies + consistency_issues + cap_table_issues
                 if f.get("severity") == "critical"]
    if criticals:
        sections.append("## 🔴 Critical Issues\n")
        for f in criticals:
            sections.append(f"- **{f.get('sheet', '')}!{f.get('cell', '')}**: {f.get('description', '')}")

    # Warnings
    warnings = [f for f in formula_anomalies + consistency_issues + cap_table_issues
                if f.get("severity") == "warning"]
    if warnings:
        sections.append("\n## 🟡 Warnings\n")
        for f in warnings:
            sections.append(f"- **{f.get('sheet', '')}!{f.get('cell', '')}**: {f.get('description', '')}")

    # Assumptions table
    if assumptions:
        sections.append("\n## Assumption Realism\n")
        sections.append("| Metric | Value | Unit | Verdict | Benchmark Range |")
        sections.append("|--------|-------|------|---------|----------------|")
        for a in assumptions:
            verdict = a.get("benchmark_verdict", "—")
            emoji = {"realistic": "✅", "aggressive": "⚠️", "unrealistic": "❌"}.get(verdict, "—")
            sections.append(
                f"| {a.get('name', '')} | {a.get('value', '')} | {a.get('unit', '')} "
                f"| {emoji} {verdict} | {a.get('benchmark_range', 'N/A')} |"
            )

    # Sensitivity
    if scenario_results:
        sections.append("\n## Sensitivity Summary\n")
        sections.append("| Assumption | Perturbation | Metric | Δ% |")
        sections.append("|------------|-------------|--------|-----|")
        for s in scenario_results:
            sections.append(
                f"| {s.get('assumption_perturbed', '')} | {s.get('perturbation', '')} "
                f"| {s.get('impact_metric', '')} | {s.get('delta_pct', 0):+.1f}% |"
            )

    return "\n".join(sections)


def _build_fallback_report(state: dict) -> str:
    """Build a minimal report when the Report Agent fails."""
    return _build_report_header(
        company_name=state.get("company_name", "Unknown"),
        sector=state.get("sector"),
        sheets_analyzed=len(state.get("sheet_metadata", [])),
        critical_count=0,
        warning_count=0,
        info_count=0,
        assumptions_count=len(state.get("assumptions", [])),
        scenarios_count=len(state.get("scenario_results", [])),
        agent_errors=state.get("agent_errors", []),
    ) + "\n\n⚠️ Report generation encountered errors. Raw findings are available via the API."
