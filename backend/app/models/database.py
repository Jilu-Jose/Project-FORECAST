"""SQLAlchemy async database models and engine setup.

Uses SQLite (aiosqlite) for local dev. Switch to PostgreSQL by changing
DATABASE_URL to a postgres+asyncpg:// connection string.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
    event,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship

from app.config import settings


# ── Engine & session ──────────────────────────────────────────────────────────

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ── ORM models ────────────────────────────────────────────────────────────────

class AuditRunDB(Base):
    """Persisted audit run record."""
    __tablename__ = "audit_runs"

    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    company_name = Column(String, nullable=False, index=True)
    sector = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    status = Column(String, nullable=False, default="queued")  # queued/running/complete/error
    current_agent = Column(String, nullable=True)
    progress_pct = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    n8n_status = Column(String, nullable=True, default="pending")

    # Full audit state as JSON blob — enables version diffing
    state_json = Column(Text, nullable=True)

    # Report paths
    report_markdown = Column(Text, nullable=True)
    report_docx_path = Column(String, nullable=True)
    report_pdf_path = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    findings = relationship("AuditFindingDB", back_populates="audit_run", cascade="all, delete-orphan")

    def set_state(self, state_dict: dict):
        """Serialize audit state to JSON."""
        self.state_json = json.dumps(state_dict, default=str)

    def get_state(self) -> dict:
        """Deserialize audit state from JSON."""
        if self.state_json:
            return json.loads(self.state_json)
        return {}


class AuditFindingDB(Base):
    """Individual finding within an audit run (denormalized for fast queries)."""
    __tablename__ = "audit_findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_run_id = Column(String, ForeignKey("audit_runs.id"), nullable=False, index=True)
    finding_type = Column(String, nullable=False)  # formula_anomaly, consistency, cap_table, etc.
    severity = Column(String, nullable=False)       # critical, warning, info
    sheet = Column(String, nullable=True)
    cell = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    details_json = Column(Text, nullable=True)      # full finding object as JSON

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    audit_run = relationship("AuditRunDB", back_populates="findings")


# ── Database lifecycle ────────────────────────────────────────────────────────

async def init_db():
    """Create all tables. Call on app startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """FastAPI dependency: yield an async DB session."""
    async with async_session() as session:
        yield session
