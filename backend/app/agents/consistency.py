"""Consistency Agent — checks cross-sheet reconciliation,
unit/currency consistency, and historical-vs-projected bridges.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict

from app.agents.state import AuditState
from app.agents.ingestion import get_cached_workbook

logger = logging.getLogger(__name__)

# Label patterns for key financial line items
RECONCILIATION_LABELS = {
    "total_revenue": re.compile(r"total\s*revenue|net\s*revenue|gross\s*revenue|total\s*sales", re.IGNORECASE),
    "total_expenses": re.compile(r"total\s*expense|total\s*cost|total\s*opex", re.IGNORECASE),
    "net_income": re.compile(r"net\s*income|net\s*profit|net\s*loss|profit\s*after\s*tax|pat\b", re.IGNORECASE),
    "total_assets": re.compile(r"total\s*assets", re.IGNORECASE),
    "total_liabilities": re.compile(r"total\s*liab", re.IGNORECASE),
    "total_equity": re.compile(r"total\s*equity|shareholder.*equity|net\s*worth", re.IGNORECASE),
    "cash_balance": re.compile(r"cash\s*balance|ending\s*cash|cash\s*(and|&)\s*equiv|total\s*cash", re.IGNORECASE),
    "operating_cash_flow": re.compile(r"operating\s*cash\s*flow|cfo\b|cash\s*from\s*operations", re.IGNORECASE),
    "ebitda": re.compile(r"ebitda", re.IGNORECASE),
}

# Currency/unit detection patterns
CURRENCY_PATTERNS = {
    "INR": re.compile(r"₹|INR|rupee|Rs\.?", re.IGNORECASE),
    "USD": re.compile(r"\$|USD|dollar", re.IGNORECASE),
    "EUR": re.compile(r"€|EUR|euro", re.IGNORECASE),
}

MAGNITUDE_PATTERNS = {
    "lakhs": re.compile(r"\blakh|₹\s*L\b|in\s*lakh", re.IGNORECASE),
    "crores": re.compile(r"\bcrore|₹\s*Cr\b|in\s*crore", re.IGNORECASE),
    "thousands": re.compile(r"\b(000|K|thousand)\b", re.IGNORECASE),
    "millions": re.compile(r"\b(M|million|mn)\b", re.IGNORECASE),
    "absolute": re.compile(r"absolute|actual", re.IGNORECASE),
}

TIME_PERIOD_PATTERNS = {
    "monthly": re.compile(r"month|monthly|per\s*month|/mo", re.IGNORECASE),
    "quarterly": re.compile(r"quarter|quarterly|per\s*quarter|Q[1-4]", re.IGNORECASE),
    "annual": re.compile(r"annual|yearly|per\s*year|/yr|FY", re.IGNORECASE),
}


async def consistency_node(state: AuditState) -> dict:
    """Check cross-sheet consistency, units, currencies, and bridges.

    Reads: file_path, sheet_metadata
    Writes: consistency_issues
    """
    logger.info("Consistency Agent: checking cross-sheet consistency")

    wb_data = get_cached_workbook(state["file_path"])
    if not wb_data:
        return {
            "current_agent": "consistency",
            "agent_errors": ["Consistency Agent: no cached workbook data"],
            "consistency_issues": [],
        }

    issues = []

    try:
        # ── 1. Cross-sheet value reconciliation ──────────────────────────
        issues.extend(_check_cross_sheet_reconciliation(wb_data))

        # ── 2. Balance sheet balance check ────────────────────────────────
        issues.extend(_check_balance_sheet(wb_data))

        # ── 3. Currency consistency ───────────────────────────────────────
        issues.extend(_check_currency_consistency(wb_data))

        # ── 4. Magnitude consistency ──────────────────────────────────────
        issues.extend(_check_magnitude_consistency(wb_data))

        # ── 5. Time period consistency ────────────────────────────────────
        issues.extend(_check_time_period_consistency(wb_data))

        # ── 6. Historical-vs-projected bridge ─────────────────────────────
        issues.extend(_check_historical_projected_bridge(wb_data))

    except Exception as e:
        logger.error(f"Consistency Agent error: {e}")
        return {
            "current_agent": "consistency",
            "agent_errors": [f"Consistency Agent error: {str(e)}"],
            "consistency_issues": issues,
        }

    logger.info(f"Consistency Agent: found {len(issues)} consistency issues")
    return {
        "current_agent": "consistency",
        "consistency_issues": issues,
    }


def _check_cross_sheet_reconciliation(wb_data) -> list[dict]:
    """Check that the same named line items reconcile across sheets."""
    issues = []

    # Find matching labels across different sheets
    label_locations: dict[str, list[tuple[str, str, float]]] = defaultdict(list)

    for sheet_name, cells in wb_data.sheets.items():
        for cell in cells:
            if cell.label and isinstance(cell.value, (int, float)):
                for label_key, pattern in RECONCILIATION_LABELS.items():
                    if pattern.search(cell.label):
                        label_locations[label_key].append(
                            (sheet_name, cell.cell_ref, float(cell.value))
                        )

    # Compare values across sheets for the same label
    for label_key, locations in label_locations.items():
        if len(locations) < 2:
            continue

        # Group by value — all should match (within tolerance)
        values = [(sheet, cell, val) for sheet, cell, val in locations]
        base_sheet, base_cell, base_val = values[0]

        for sheet, cell, val in values[1:]:
            if base_val == 0 and val == 0:
                continue

            # Allow 1% tolerance for floating point
            tolerance = max(abs(base_val) * 0.01, 1.0) if base_val != 0 else 1.0

            if abs(val - base_val) > tolerance:
                issues.append({
                    "description": (
                        f"'{label_key.replace('_', ' ').title()}' mismatch: "
                        f"{base_sheet}!{base_cell}={base_val:,.2f} vs "
                        f"{sheet}!{cell}={val:,.2f} "
                        f"(difference: {abs(val - base_val):,.2f})"
                    ),
                    "sheets_involved": [base_sheet, sheet],
                    "cells_involved": [f"{base_sheet}!{base_cell}", f"{sheet}!{cell}"],
                    "severity": "critical" if label_key in ("total_revenue", "net_income", "cash_balance") else "warning",
                    "issue_type": "cross_sheet_mismatch",
                })

    return issues


def _check_balance_sheet(wb_data) -> list[dict]:
    """Check that Assets = Liabilities + Equity on balance sheet."""
    issues = []

    for metadata in wb_data.sheet_metadata:
        if metadata.detected_type != "balance_sheet":
            continue

        cells = wb_data.sheets.get(metadata.name, [])
        totals = {}

        for cell in cells:
            if cell.label and isinstance(cell.value, (int, float)):
                for label_key in ("total_assets", "total_liabilities", "total_equity"):
                    if RECONCILIATION_LABELS[label_key].search(cell.label):
                        totals[label_key] = (cell.cell_ref, float(cell.value))

        if all(k in totals for k in ("total_assets", "total_liabilities", "total_equity")):
            assets_cell, assets_val = totals["total_assets"]
            liab_cell, liab_val = totals["total_liabilities"]
            equity_cell, equity_val = totals["total_equity"]

            expected = liab_val + equity_val
            tolerance = max(abs(assets_val) * 0.01, 1.0) if assets_val != 0 else 1.0

            if abs(assets_val - expected) > tolerance:
                issues.append({
                    "description": (
                        f"Balance sheet does not balance: "
                        f"Assets ({assets_val:,.2f}) ≠ "
                        f"Liabilities ({liab_val:,.2f}) + Equity ({equity_val:,.2f}) = {expected:,.2f}"
                    ),
                    "sheets_involved": [metadata.name],
                    "cells_involved": [
                        f"{metadata.name}!{assets_cell}",
                        f"{metadata.name}!{liab_cell}",
                        f"{metadata.name}!{equity_cell}",
                    ],
                    "severity": "critical",
                    "issue_type": "balance_sheet_imbalance",
                })

    return issues


def _check_currency_consistency(wb_data) -> list[dict]:
    """Detect mixed currencies across the workbook."""
    issues = []

    # Collect all currency references from labels
    sheet_currencies: dict[str, set] = defaultdict(set)

    for sheet_name, cells in wb_data.sheets.items():
        for cell in cells:
            if cell.label:
                for currency, pattern in CURRENCY_PATTERNS.items():
                    if pattern.search(cell.label):
                        sheet_currencies[sheet_name].add(currency)

    # Flag sheets with mixed currencies
    for sheet, currencies in sheet_currencies.items():
        if len(currencies) > 1:
            issues.append({
                "description": f"Mixed currencies detected in sheet '{sheet}': {', '.join(sorted(currencies))}",
                "sheets_involved": [sheet],
                "cells_involved": [],
                "severity": "warning",
                "issue_type": "currency_mismatch",
            })

    # Flag cross-sheet currency inconsistency
    all_currencies = set()
    for currencies in sheet_currencies.values():
        all_currencies.update(currencies)

    if len(all_currencies) > 1:
        sheets_with_currency = [s for s in sheet_currencies.keys()]
        issues.append({
            "description": f"Multiple currencies used across workbook: {', '.join(sorted(all_currencies))}",
            "sheets_involved": sheets_with_currency,
            "cells_involved": [],
            "severity": "warning",
            "issue_type": "currency_mismatch",
        })

    return issues


def _check_magnitude_consistency(wb_data) -> list[dict]:
    """Detect mixed magnitudes (lakhs vs crores vs absolute)."""
    issues = []

    sheet_magnitudes: dict[str, set] = defaultdict(set)

    for sheet_name, cells in wb_data.sheets.items():
        for cell in cells:
            if cell.label:
                for magnitude, pattern in MAGNITUDE_PATTERNS.items():
                    if pattern.search(cell.label):
                        sheet_magnitudes[sheet_name].add(magnitude)

    for sheet, magnitudes in sheet_magnitudes.items():
        if len(magnitudes) > 1:
            issues.append({
                "description": f"Mixed magnitudes in sheet '{sheet}': {', '.join(sorted(magnitudes))}",
                "sheets_involved": [sheet],
                "cells_involved": [],
                "severity": "warning",
                "issue_type": "magnitude_mismatch",
            })

    return issues


def _check_time_period_consistency(wb_data) -> list[dict]:
    """Detect mixed time periods (monthly vs annual assumptions)."""
    issues = []

    sheet_periods: dict[str, set] = defaultdict(set)

    for sheet_name, cells in wb_data.sheets.items():
        for cell in cells:
            if cell.label:
                for period, pattern in TIME_PERIOD_PATTERNS.items():
                    if pattern.search(cell.label):
                        sheet_periods[sheet_name].add(period)

    for sheet, periods in sheet_periods.items():
        if len(periods) > 1:
            issues.append({
                "description": f"Mixed time periods in sheet '{sheet}': {', '.join(sorted(periods))}. Ensure all assumptions use consistent time units.",
                "sheets_involved": [sheet],
                "cells_involved": [],
                "severity": "info",
                "issue_type": "time_period_mismatch",
            })

    return issues


def _check_historical_projected_bridge(wb_data) -> list[dict]:
    """Detect discontinuities between historical and projected data."""
    issues = []

    for sheet_name, cells in wb_data.sheets.items():
        # Look for "actual" / "projected" / "forecast" markers in headers
        has_actual = False
        has_projected = False

        for cell in cells:
            if cell.label:
                if re.search(r"actual|historical|ytd", cell.label, re.IGNORECASE):
                    has_actual = True
                if re.search(r"projected|forecast|budget|plan", cell.label, re.IGNORECASE):
                    has_projected = True

        if has_actual and has_projected:
            # Find numeric rows and check for large jumps at the boundary
            # This is a heuristic — look for adjacent numeric cells with >50% jump
            row_values: dict[int, list[tuple[int, float]]] = defaultdict(list)
            for cell in cells:
                if isinstance(cell.value, (int, float)) and cell.value != 0:
                    row_values[cell.row].append((cell.col, float(cell.value)))

            for row, vals in row_values.items():
                vals.sort(key=lambda x: x[0])
                for i in range(1, len(vals)):
                    prev_val = vals[i - 1][1]
                    curr_val = vals[i][1]
                    if prev_val != 0:
                        change = abs(curr_val - prev_val) / abs(prev_val)
                        if change > 0.5:  # >50% jump
                            issues.append({
                                "description": (
                                    f"Potential historical/projected discontinuity in "
                                    f"'{sheet_name}' row {row}: "
                                    f"value jumps from {prev_val:,.2f} to {curr_val:,.2f} "
                                    f"({change:.0%} change)"
                                ),
                                "sheets_involved": [sheet_name],
                                "cells_involved": [],
                                "severity": "info",
                                "issue_type": "historical_projected_gap",
                            })
                            break  # Only flag once per row

    return issues
