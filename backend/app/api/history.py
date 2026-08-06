"""History and version-diffing API endpoints."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AuditRunDB, AuditFindingDB, get_session

router = APIRouter()


@router.get("/history")
async def list_audit_history(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    """List all audit runs, most recent first."""
    stmt = (
        select(AuditRunDB)
        .order_by(desc(AuditRunDB.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    runs = result.scalars().all()

    items = []
    for run in runs:
        # Count findings by severity
        findings_stmt = select(AuditFindingDB).where(AuditFindingDB.audit_run_id == run.id)
        findings_result = await session.execute(findings_stmt)
        findings = findings_result.scalars().all()

        items.append({
            "id": run.id,
            "company_name": run.company_name,
            "sector": run.sector,
            "status": run.status,
            "original_filename": run.original_filename,
            "critical_count": sum(1 for f in findings if f.severity == "critical"),
            "warning_count": sum(1 for f in findings if f.severity == "warning"),
            "info_count": sum(1 for f in findings if f.severity == "info"),
            "created_at": run.created_at,
            "completed_at": run.completed_at,
        })

    return {"items": items, "total": len(items), "limit": limit, "offset": offset}


@router.get("/history/{company}")
async def get_company_history(
    company: str,
    session: AsyncSession = Depends(get_session),
):
    """Get audit history for a specific company."""
    stmt = (
        select(AuditRunDB)
        .where(AuditRunDB.company_name.ilike(f"%{company}%"))
        .order_by(desc(AuditRunDB.created_at))
    )
    result = await session.execute(stmt)
    runs = result.scalars().all()

    items = []
    for run in runs:
        state = run.get_state()
        items.append({
            "id": run.id,
            "company_name": run.company_name,
            "sector": run.sector,
            "status": run.status,
            "assumptions_count": len(state.get("assumptions", [])),
            "anomalies_count": len(state.get("formula_anomalies", [])),
            "created_at": run.created_at,
            "completed_at": run.completed_at,
        })

    return {"company": company, "audits": items}


@router.get("/diff/{id1}/{id2}")
async def diff_versions(
    id1: str,
    id2: str,
    session: AsyncSession = Depends(get_session),
):
    """Compare two audit runs and show what changed."""
    run1 = await session.get(AuditRunDB, id1)
    run2 = await session.get(AuditRunDB, id2)

    if not run1 or not run2:
        raise HTTPException(status_code=404, detail="One or both audit runs not found")

    state1 = run1.get_state()
    state2 = run2.get_state()

    # Compare assumptions
    assumptions_1 = {a["name"]: a for a in state1.get("assumptions", []) if isinstance(a, dict)}
    assumptions_2 = {a["name"]: a for a in state2.get("assumptions", []) if isinstance(a, dict)}

    assumption_changes = []
    all_names = set(list(assumptions_1.keys()) + list(assumptions_2.keys()))

    for name in sorted(all_names):
        a1 = assumptions_1.get(name)
        a2 = assumptions_2.get(name)

        if a1 and a2:
            old_val = a1.get("value", 0)
            new_val = a2.get("value", 0)
            if old_val != new_val:
                delta_pct = 0
                if old_val != 0:
                    delta_pct = ((new_val - old_val) / abs(old_val)) * 100
                assumption_changes.append({
                    "name": name,
                    "old_value": old_val,
                    "new_value": new_val,
                    "old_verdict": a1.get("benchmark_verdict"),
                    "new_verdict": a2.get("benchmark_verdict"),
                    "delta_pct": round(delta_pct, 2),
                })
        elif a1 and not a2:
            assumption_changes.append({
                "name": name,
                "old_value": a1.get("value", 0),
                "new_value": None,
                "status": "removed",
            })
        elif not a1 and a2:
            assumption_changes.append({
                "name": name,
                "old_value": None,
                "new_value": a2.get("value", 0),
                "status": "added",
            })

    # Compare finding counts
    anomalies_1 = set(
        f"{a.get('sheet', '')}!{a.get('cell', '')}:{a.get('issue_type', '')}"
        for a in state1.get("formula_anomalies", [])
    )
    anomalies_2 = set(
        f"{a.get('sheet', '')}!{a.get('cell', '')}:{a.get('issue_type', '')}"
        for a in state2.get("formula_anomalies", [])
    )

    new_issues = list(anomalies_2 - anomalies_1)
    resolved_issues = list(anomalies_1 - anomalies_2)

    return {
        "audit_id_1": id1,
        "audit_id_2": id2,
        "company_name": run1.company_name,
        "date_1": run1.created_at,
        "date_2": run2.created_at,
        "assumptions_changed": assumption_changes,
        "new_issues": new_issues,
        "resolved_issues": resolved_issues,
        "summary": (
            f"{len(assumption_changes)} assumptions changed, "
            f"{len(new_issues)} new issues, "
            f"{len(resolved_issues)} resolved issues"
        ),
    }

@router.delete("/audit/{job_id}")
async def delete_audit(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete an audit run."""
    run = await session.get(AuditRunDB, job_id)
    if not run:
        raise HTTPException(status_code=404, detail="Audit run not found")
    
    await session.delete(run)
    await session.commit()
    return {"status": "success", "message": f"Audit {job_id} deleted"}
