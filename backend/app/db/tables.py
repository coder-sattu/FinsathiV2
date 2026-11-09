"""SQLAlchemy ORM tables matching 001_init.sql."""

import uuid
from datetime import date, datetime
from typing import Any
from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    DATE,
    INTEGER,
    JSON,
    SMALLINT,
    TEXT,
    TIMESTAMP,
    UUID,
    Sequence,
    ForeignKey,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class."""

    pass


# sequences
claim_no_seq = Sequence("claim_no_seq", start=100)
sr_no_seq = Sequence("sr_no_seq", start=100)


class ChatSessionTable(Base):
    """Chat sessions table."""

    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state: Mapped[str] = mapped_column(TEXT, nullable=False)
    policy_no: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    attempts: Mapped[int] = mapped_column(SMALLINT, nullable=False, default=0)
    llm_calls: Mapped[int] = mapped_column(SMALLINT, nullable=False, default=0)
    editing: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    consent_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    guard_hits: Mapped[int] = mapped_column(SMALLINT, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)


class ClaimIntimationTable(Base):
    """Claim intimations table."""

    __tablename__ = "claim_intimations"

    claim_no: Mapped[str] = mapped_column(TEXT, primary_key=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chat_sessions.id"), nullable=True)
    policy_no: Mapped[str] = mapped_column(TEXT, nullable=False)
    uhid: Mapped[str] = mapped_column(TEXT, nullable=False)
    patient_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    claim_type: Mapped[str] = mapped_column(TEXT, nullable=False)
    status: Mapped[str] = mapped_column(TEXT, nullable=False, default="OPEN")
    intimator_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    intimator_email: Mapped[str] = mapped_column(TEXT, nullable=False)
    intimation_type: Mapped[str] = mapped_column(TEXT, nullable=False)
    doa: Mapped[date] = mapped_column(DATE, nullable=False)
    doctor_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    diagnosis_code: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    diagnosis_text: Mapped[str] = mapped_column(TEXT, nullable=False)
    hospital_id: Mapped[str] = mapped_column(TEXT, nullable=False)
    approx_cost: Mapped[int | None] = mapped_column(INTEGER, nullable=True)
    needs_review: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    review_reason: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    doc_mismatch: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class ServiceRequestTable(Base):
    """Service requests table."""

    __tablename__ = "service_requests"

    sr_number: Mapped[str] = mapped_column(TEXT, primary_key=True)
    claim_no: Mapped[str] = mapped_column(ForeignKey("claim_intimations.claim_no"), nullable=False)
    type: Mapped[str] = mapped_column(TEXT, nullable=False, default="DOCUMENT_PENDING")
    status: Mapped[str] = mapped_column(TEXT, nullable=False, default="DOCUMENT_PENDING")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class UploadedDocumentTable(Base):
    """Uploaded documents table."""

    __tablename__ = "uploaded_documents"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    sr_number: Mapped[str] = mapped_column(ForeignKey("service_requests.sr_number"), nullable=False)
    doc_code: Mapped[str] = mapped_column(TEXT, nullable=False)
    original_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    stored_path: Mapped[str] = mapped_column(TEXT, nullable=False)
    mime: Mapped[str] = mapped_column(TEXT, nullable=False)
    size_bytes: Mapped[int] = mapped_column(INTEGER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class AuditLogTable(Base):
    """Audit log table."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    event: Mapped[str] = mapped_column(TEXT, nullable=False)
    from_state: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    to_state: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    detail: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class DocumentExtractionTable(Base):
    """Document extractions table."""

    __tablename__ = "document_extractions"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False)
    doc_code: Mapped[str] = mapped_column(TEXT, nullable=False)
    detected_type: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    status: Mapped[str] = mapped_column(TEXT, nullable=False)
    fields: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    checks: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    user_accepted: Mapped[bool | None] = mapped_column(BOOLEAN, nullable=True)
    model: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(INTEGER, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class GuardrailEventTable(Base):
    """Guardrail events table."""

    __tablename__ = "guardrail_events"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    stage: Mapped[str] = mapped_column(TEXT, nullable=False)
    code: Mapped[str] = mapped_column(TEXT, nullable=False)
    action: Mapped[str] = mapped_column(TEXT, nullable=False)
    snippet: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
