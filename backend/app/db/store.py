"""Database store layer for PostgreSQL operations."""

import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.tables import AuditLogTable, ChatSessionTable, ClaimIntimationTable, GuardrailEventTable, ServiceRequestTable
from app.models.domain import Claim


class DBStore:
    """Async database operations store."""

    def __init__(self, session: AsyncSession | None) -> None:
        # set session
        self.session = session

    async def get_session(self, session_id: uuid.UUID) -> ChatSessionTable | None:
        # load session from db
        if not self.session:
            return None
        try:
            result = await self.session.execute(select(ChatSessionTable).where(ChatSessionTable.id == session_id))
            return result.scalar_one_or_none()
        except Exception as e:
            try:
                await self.session.rollback()
            except Exception:
                pass
            return None

    async def save_session(self, session_obj: ChatSessionTable) -> None:
        # save session to db
        if not self.session:
            return
        try:
            from sqlalchemy.orm.attributes import flag_modified
            merged = await self.session.merge(session_obj)
            flag_modified(merged, "data")
            await self.session.commit()
        except Exception as e:
            print("SAVE_SESSION ERROR:", e)
            try:
                await self.session.rollback()
            except Exception:
                pass

    async def open_claims_by_policy(self, policy_no: str) -> list[Claim]:
        # query open claims
        if not self.session:
            return []
        target = policy_no.upper().strip()
        try:
            result = await self.session.execute(
                select(ClaimIntimationTable).where(
                    ClaimIntimationTable.policy_no == target,
                    ClaimIntimationTable.status == "OPEN"
                )
            )
            rows = result.scalars().all()
            claims: list[Claim] = []
            for r in rows:
                claims.append(
                    Claim(
                        claim_no=r.claim_no,
                        policy_no=r.policy_no,
                        uhid=r.uhid,
                        patient_name=r.patient_name,
                        claim_type=r.claim_type,  # type: ignore
                        status=r.status,  # type: ignore
                        doa=r.doa,
                        hospital_id=r.hospital_id,
                        diagnosis=r.diagnosis_text,
                        intimated_on=r.created_at.date() if isinstance(r.created_at, datetime) else r.doa,
                    )
                )
            return claims
        except Exception as e:
            try:
                await self.session.rollback()
            except Exception:
                pass
            return []

    async def log_audit(
        self,
        session_id: uuid.UUID | None,
        event: str,
        from_state: str | None = None,
        to_state: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        # log audit event
        if not self.session:
            return
        try:
            entry = AuditLogTable(
                session_id=session_id,
                event=event,
                from_state=from_state,
                to_state=to_state,
                detail=detail,
            )
            self.session.add(entry)
            await self.session.commit()
        except Exception as e:
            try:
                await self.session.rollback()
            except Exception:
                pass

    async def log_guardrail(
        self,
        session_id: uuid.UUID | None,
        stage: str,
        code: str,
        action: str,
        snippet: str | None = None,
    ) -> None:
        # log guardrail hit
        if not self.session:
            return
        try:
            entry = GuardrailEventTable(
                session_id=session_id,
                stage=stage,
                code=code,
                action=action,
                snippet=snippet[:100] if snippet else None,
            )
            self.session.add(entry)
            await self.session.commit()
        except Exception as e:
            try:
                await self.session.rollback()
            except Exception:
                pass

    async def log_document_extraction(
        self,
        document_id: int,
        doc_code: str,
        detected_type: str | None,
        status: str,
        fields: dict[str, Any] | None,
        checks: list[dict[str, Any]] | None,
        user_accepted: bool | None = None,
        model: str | None = None,
        latency_ms: int | None = None,
    ) -> None:
        # log document extraction
        if not self.session:
            return
        try:
            from app.db.tables import DocumentExtractionTable
            entry = DocumentExtractionTable(
                document_id=document_id,
                doc_code=doc_code,
                detected_type=detected_type,
                status=status,
                fields=fields,
                checks={"checks": checks} if checks else None,
                user_accepted=user_accepted,
                model=model,
                latency_ms=latency_ms,
            )
            self.session.add(entry)
            await self.session.commit()
        except Exception as e:
            try:
                await self.session.rollback()
            except Exception:
                pass

