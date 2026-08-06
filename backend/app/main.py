"""FastAPI application factory and startup lifecycle."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models.database import init_db
from app.api.audit import router as audit_router
from app.api.history import router as history_router
from app.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle events."""
    # Startup
    settings.ensure_dirs()
    await init_db()
    yield
    # Shutdown — nothing to clean up yet


app = FastAPI(
    title="FORECAST",
    description="Agentic Financial Model Auditor — ingests startup financial models and produces investor-grade audit reports.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount report files for download
settings.ensure_dirs()
app.mount("/reports", StaticFiles(directory=str(settings.report_dir)), name="reports")


# Register routers
app.include_router(health_router, tags=["Health"])
app.include_router(audit_router, prefix="/api", tags=["Audit"])
app.include_router(history_router, prefix="/api", tags=["History"])
