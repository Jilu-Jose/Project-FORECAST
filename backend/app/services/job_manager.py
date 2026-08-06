"""In-process async job manager for audit pipeline execution.

Tracks job status, current agent step, and timestamps.
Upgradeable to ARQ + Redis by swapping this module.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
import httpx

from app.agents.graph import run_audit
from app.models.database import async_session, AuditRunDB, AuditFindingDB
from app.services.report_gen import generate_docx_report, generate_pdf_report

logger = logging.getLogger(__name__)


class JobManager:
    """In-process async job manager."""

    def __init__(self):
        self._jobs: dict[str, dict[str, Any]] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    def create_job(
        self,
        file_path: str,
        company_name: str,
        sector: str | None = None,
        original_filename: str | None = None,
    ) -> str:
        """Create a new audit job and start it asynchronously.

        Returns:
            The job ID.
        """
        job_id = uuid4().hex[:16]

        self._jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "current_agent": None,
            "progress_pct": 0.0,
            "error_message": None,
            "file_path": file_path,
            "company_name": company_name,
            "sector": sector,
            "original_filename": original_filename,
            "created_at": datetime.now(timezone.utc),
            "started_at": None,
            "completed_at": None,
            "result": None,
        }

        # Start the job as an async task
        task = asyncio.create_task(self._execute_job(job_id))
        self._tasks[job_id] = task

        return job_id

    def get_job_status(self, job_id: str) -> dict | None:
        """Get the current status of a job."""
        return self._jobs.get(job_id)

    def get_job_result(self, job_id: str) -> dict | None:
        """Get the final result of a completed job."""
        job = self._jobs.get(job_id)
        if job and job["status"] == "complete":
            return job.get("result")
        return None

    async def _execute_job(self, job_id: str):
        """Execute the audit pipeline and persist results."""
        job = self._jobs[job_id]

        try:
            job["status"] = "running"
            job["started_at"] = datetime.now(timezone.utc)

            # Create DB record
            async with async_session() as session:
                db_run = AuditRunDB(
                    id=job_id,
                    company_name=job["company_name"],
                    sector=job["sector"],
                    file_path=job["file_path"],
                    original_filename=job["original_filename"],
                    status="running",
                    started_at=job["started_at"],
                )
                session.add(db_run)
                await session.commit()

            # Run the LangGraph pipeline
            logger.info(f"Job {job_id}: starting audit pipeline")
            result = await run_audit(
                file_path=job["file_path"],
                company_name=job["company_name"],
                sector=job["sector"],
            )

            # Generate report files
            report_md = result.get("report_markdown", "")
            docx_path = ""
            pdf_path = ""

            if report_md:
                try:
                    findings_data = {
                        "assumptions": result.get("assumptions", []),
                        "formula_anomalies": result.get("formula_anomalies", []),
                        "consistency_issues": result.get("consistency_issues", []),
                        "scenario_results": result.get("scenario_results", []),
                    }
                    docx_path = generate_docx_report(
                        report_md, job["company_name"], job_id, findings_data
                    )
                    pdf_path = generate_pdf_report(
                        report_md, job["company_name"], job_id, findings_data
                    )
                except Exception as e:
                    logger.error(f"Report file generation failed: {e}")

            # Update job status
            job["status"] = "complete"
            job["completed_at"] = datetime.now(timezone.utc)
            job["progress_pct"] = 100.0
            job["result"] = {
                "formula_anomalies": result.get("formula_anomalies", []),
                "assumptions": result.get("assumptions", []),
                "consistency_issues": result.get("consistency_issues", []),
                "scenario_results": result.get("scenario_results", []),
                "cap_table_issues": result.get("cap_table_issues", []),
                "report_markdown": report_md,
                "report_docx_path": docx_path,
                "report_pdf_path": pdf_path,
                "sheet_metadata": result.get("sheet_metadata", []),
                "agent_errors": result.get("agent_errors", []),
            }

            # Persist to DB
            await self._persist_results(job_id, job, result, docx_path, pdf_path)
            
            # Trigger n8n webhook asynchronously
            asyncio.create_task(self._trigger_n8n_webhook(job_id, job))

            logger.info(f"Job {job_id}: audit complete")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            job["status"] = "error"
            job["error_message"] = str(e)
            job["completed_at"] = datetime.now(timezone.utc)

            # Update DB record
            try:
                async with async_session() as session:
                    db_run = await session.get(AuditRunDB, job_id)
                    if db_run:
                        db_run.status = "error"
                        db_run.error_message = str(e)
                        db_run.completed_at = job["completed_at"]
                        await session.commit()
            except Exception as db_err:
                logger.error(f"Failed to update DB: {db_err}")

    async def _persist_results(
        self, job_id: str, job: dict, result: dict,
        docx_path: str, pdf_path: str,
    ):
        """Persist audit results to the database."""
        async with async_session() as session:
            db_run = await session.get(AuditRunDB, job_id)
            if not db_run:
                return

            db_run.status = "complete"
            db_run.completed_at = job["completed_at"]
            db_run.report_markdown = result.get("report_markdown", "")
            db_run.report_docx_path = docx_path
            db_run.report_pdf_path = pdf_path

            # Serialize full state for version diffing
            state_for_storage = {
                "formula_anomalies": result.get("formula_anomalies", []),
                "assumptions": result.get("assumptions", []),
                "consistency_issues": result.get("consistency_issues", []),
                "scenario_results": result.get("scenario_results", []),
                "cap_table_issues": result.get("cap_table_issues", []),
                "sheet_metadata": result.get("sheet_metadata", []),
            }
            db_run.set_state(state_for_storage)

            # Persist individual findings for fast queries
            all_findings = []

            for anomaly in result.get("formula_anomalies", []):
                all_findings.append(AuditFindingDB(
                    audit_run_id=job_id,
                    finding_type="formula_anomaly",
                    severity=anomaly.get("severity", "info"),
                    sheet=anomaly.get("sheet"),
                    cell=anomaly.get("cell"),
                    description=anomaly.get("description", ""),
                    confidence=anomaly.get("confidence"),
                    details_json=json.dumps(anomaly),
                ))

            for issue in result.get("consistency_issues", []):
                all_findings.append(AuditFindingDB(
                    audit_run_id=job_id,
                    finding_type="consistency",
                    severity=issue.get("severity", "info"),
                    sheet=", ".join(issue.get("sheets_involved", [])),
                    cell=", ".join(issue.get("cells_involved", [])),
                    description=issue.get("description", ""),
                    details_json=json.dumps(issue),
                ))

            for issue in result.get("cap_table_issues", []):
                all_findings.append(AuditFindingDB(
                    audit_run_id=job_id,
                    finding_type="cap_table",
                    severity=issue.get("severity", "info"),
                    description=issue.get("description", ""),
                    details_json=json.dumps(issue),
                ))

            session.add_all(all_findings)
            await session.commit()

    async def _trigger_n8n_webhook(self, job_id: str, job: dict):
        """Trigger the local n8n workflow webhook."""
        webhook_url = "http://host.docker.internal:5678/webhook/forecast-audit-complete"
        # Fallback to localhost if not in docker network context
        
        payload = {
            "job_id": job_id,
            "company_name": job.get("company_name"),
            "report_url": f"http://localhost:8000/api/audit/report/{job_id}/download?format=pdf"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload, timeout=5.0)
                if response.status_code != 200:
                    # Retry with localhost if host.docker.internal fails (e.g. running n8n outside docker or from host)
                    webhook_url = "http://localhost:5678/webhook/forecast-audit-complete"
                    await client.post(webhook_url, json=payload, timeout=5.0)
        except Exception as e:
            logger.warning(f"Could not trigger n8n webhook: {e}")

    async def update_n8n_status(self, job_id: str, status: str) -> bool:
        """Update n8n status in memory and DB."""
        if job_id in self._jobs:
            self._jobs[job_id]["n8n_status"] = status
        
        try:
            async with async_session() as session:
                db_run = await session.get(AuditRunDB, job_id)
                if db_run:
                    db_run.n8n_status = status
                    await session.commit()
                    return True
        except Exception as e:
            logger.error(f"Failed to update n8n_status in DB: {e}")
        return False


# Singleton
_job_manager: JobManager | None = None


def get_job_manager() -> JobManager:
    """Get or create the job manager singleton."""
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager
