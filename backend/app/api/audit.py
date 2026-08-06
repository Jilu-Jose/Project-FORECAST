"""Audit API endpoints — upload, status, report download."""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.services.job_manager import get_job_manager

router = APIRouter()


@router.post("/audit/upload")
async def upload_audit(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    sector: str = Form(None),
):
    """Upload an Excel file and start an audit.

    Returns a job_id for tracking progress.
    """
    # Validate file type
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx and .xls files are supported",
        )

    # Validate file size
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    contents = await file.read()
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    # Save the uploaded file
    settings.ensure_dirs()
    file_path = settings.upload_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(contents)

    # Start the audit job
    job_manager = get_job_manager()
    job_id = job_manager.create_job(
        file_path=str(file_path),
        company_name=company_name,
        sector=sector,
        original_filename=file.filename,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": f"Audit queued for '{company_name}'",
    }


@router.get("/audit/status/{job_id}")
async def get_audit_status(job_id: str):
    """Get the current status of an audit job."""
    job_manager = get_job_manager()
    job = job_manager.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job["id"],
        "status": job["status"],
        "current_agent": job.get("current_agent"),
        "progress_pct": job.get("progress_pct", 0),
        "error_message": job.get("error_message"),
        "started_at": job.get("started_at"),
        "completed_at": job.get("completed_at"),
        "n8n_status": job.get("n8n_status", "pending"),
    }


from pydantic import BaseModel

class N8nStatusUpdate(BaseModel):
    status: str

@router.post("/audit/{job_id}/n8n-status")
async def update_n8n_status(job_id: str, payload: N8nStatusUpdate):
    """Endpoint for n8n to update its workflow status in real-time."""
    job_manager = get_job_manager()
    success = await job_manager.update_n8n_status(job_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Status updated successfully", "n8n_status": payload.status}


@router.get("/audit/report/{job_id}")
async def get_audit_report(job_id: str):
    """Get the full audit report for a completed job."""
    job_manager = get_job_manager()
    job = job_manager.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "complete":
        raise HTTPException(
            status_code=202,
            detail=f"Audit still in progress (status: {job['status']})",
        )

    result = job_manager.get_job_result(job_id)
    if not result:
        raise HTTPException(status_code=500, detail="Results not available")

    # Count severities
    all_findings = (
        result.get("formula_anomalies", [])
        + result.get("consistency_issues", [])
        + result.get("cap_table_issues", [])
    )
    critical_count = sum(1 for f in all_findings if f.get("severity") == "critical")
    warning_count = sum(1 for f in all_findings if f.get("severity") == "warning")
    info_count = sum(1 for f in all_findings if f.get("severity") == "info")

    return {
        "job_id": job_id,
        "company_name": job["company_name"],
        "sector": job.get("sector"),
        "summary": {
            "total_issues": len(all_findings),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "sheets_analyzed": len(result.get("sheet_metadata", [])),
            "assumptions_extracted": len(result.get("assumptions", [])),
            "scenarios_run": len(result.get("scenario_results", [])),
        },
        "formula_anomalies": result.get("formula_anomalies", []),
        "assumptions": result.get("assumptions", []),
        "consistency_issues": result.get("consistency_issues", []),
        "scenario_results": result.get("scenario_results", []),
        "cap_table_issues": result.get("cap_table_issues", []),
        "report_markdown": result.get("report_markdown", ""),
        "agent_errors": result.get("agent_errors", []),
        "download_urls": {
            "docx": f"/api/audit/report/{job_id}/download?format=docx",
            "pdf": f"/api/audit/report/{job_id}/download?format=pdf",
        },
        "created_at": job.get("created_at"),
        "completed_at": job.get("completed_at"),
    }


@router.get("/audit/report/{job_id}/download")
async def download_report(job_id: str, format: str = "pdf"):
    """Download the generated report file."""
    job_manager = get_job_manager()
    result = job_manager.get_job_result(job_id)

    if not result:
        raise HTTPException(status_code=404, detail="Report not found")

    if format == "docx":
        file_path = result.get("report_docx_path")
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif format == "pdf":
        file_path = result.get("report_pdf_path")
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'docx'")

    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail=f"{format.upper()} report not generated")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=f"forecast_audit_{job_id}.{format}",
    )
