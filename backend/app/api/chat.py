"""Chat API router for start, message, session, and upload endpoints with guardrails and NLU."""

import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated
import filetype
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.deps import (
    get_clock,
    get_hospital_repo,
    get_master_repo,
    get_member_repo,
    get_nlu,
    get_policy_repo,
)
from app.db.engine import get_db_session
from app.db.store import DBStore
from app.db.tables import ChatSessionTable, ServiceRequestTable, UploadedDocumentTable
from app.flow.engine import FlowEngine, FlowSession
from app.flow.messages import MESSAGES
from app.flow.states import State
from app.guard.input import check_input
from app.guard.output import check_output
from app.llm.nlu import NLU
from app.llm.sarvam_translator import SarvamTranslator
from app.repository.base import ClaimRepo, HospitalRepo, MasterRepo, MemberRepo, PolicyRepo
from app.repository.json_repo import JsonClaimRepo, JsonDataStore
from app.schemas.api import BotReply, ChatError, ChatMessageRequest, UI, UIOption


router = APIRouter(prefix="/chat", tags=["chat"])

_memory_sessions: dict[str, ChatSessionTable] = {}


def get_claim_repo(request: Request) -> ClaimRepo:
    # get claim repo from app state
    store: JsonDataStore = request.app.state.data_store
    return JsonClaimRepo(store)


@router.post("/start", response_model=BotReply)
async def chat_start(
    policy_repo: Annotated[PolicyRepo, Depends(get_policy_repo)],
    member_repo: Annotated[MemberRepo, Depends(get_member_repo)],
    claim_repo: Annotated[ClaimRepo, Depends(get_claim_repo)],
    hospital_repo: Annotated[HospitalRepo, Depends(get_hospital_repo)],
    master_repo: Annotated[MasterRepo, Depends(get_master_repo)],
    nlu: Annotated[NLU, Depends(get_nlu)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BotReply:
    """Start a new chat session."""
    db_store = DBStore(db_session)
    engine = FlowEngine(
        policy_repo=policy_repo,
        member_repo=member_repo,
        claim_repo=claim_repo,
        master_repo=master_repo,
        hospital_repo=hospital_repo,
        nlu=nlu,
        db_store=db_store,
    )

    session = engine.create_session()
    _memory_sessions[str(session.id)] = session.to_db()

    try:
        await db_store.save_session(session.to_db())
    except Exception:
        pass

    reply = engine.build_reply(session)
    out_res = check_output(reply)
    return out_res.reply


@router.post("/message", response_model=BotReply)
async def chat_message(
    req: ChatMessageRequest,
    policy_repo: Annotated[PolicyRepo, Depends(get_policy_repo)],
    member_repo: Annotated[MemberRepo, Depends(get_member_repo)],
    claim_repo: Annotated[ClaimRepo, Depends(get_claim_repo)],
    hospital_repo: Annotated[HospitalRepo, Depends(get_hospital_repo)],
    master_repo: Annotated[MasterRepo, Depends(get_master_repo)],
    nlu: Annotated[NLU, Depends(get_nlu)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BotReply:
    """Process a user message or widget input."""
    try:
        sess_uuid = uuid.UUID(req.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    db_store = DBStore(db_session)
    db_obj = None
    try:
        db_obj = await db_store.get_session(sess_uuid)
    except Exception:
        pass

    if not db_obj:
        db_obj = _memory_sessions.get(req.session_id)

    if not db_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    session = FlowSession(db_obj)
    engine = FlowEngine(
        policy_repo=policy_repo,
        member_repo=member_repo,
        claim_repo=claim_repo,
        master_repo=master_repo,
        hospital_repo=hospital_repo,
        nlu=nlu,
        db_store=db_store,
    )

    input_text = req.input.text or (req.input.value if isinstance(req.input.value, str) else "")
    
    # Hinglish translation
    translator = SarvamTranslator()
    was_hinglish = False
    is_widget_click = req.input.value is not None and not req.input.text
    if input_text and not is_widget_click and translator.is_hinglish(input_text):
        was_hinglish = True
        input_text = await translator.translate_hinglish_to_english(input_text)

    if input_text:
        g_res = check_input(
            text=input_text,
            state=session.state.value,
            session_id=str(session.id),
            current_time=time.time(),
            injection_hits=session.guard_hits,
        )

        if not g_res.allowed:
            if g_res.code == "I6":
                session.guard_hits += 1
                await db_store.log_guardrail(session.id, stage="INPUT", code="I6", action="BLOCKED", snippet=g_res.masked_text)
                if g_res.trigger_agent_handoff:
                    session.state = State.AGENT_HANDOFF
                    reply = engine.build_reply(session)
                    _memory_sessions[str(session.id)] = session.to_db()
                    await db_store.save_session(session.to_db())
                    return reply
            else:
                if g_res.code:
                    await db_store.log_guardrail(session.id, stage="INPUT", code=g_res.code, action="BLOCKED", snippet=g_res.masked_text)

            reply = engine.build_reply(session, error=ChatError(message=g_res.error_message or "Invalid input."))
            if g_res.warning_message:
                reply.ui.warnings.append(g_res.warning_message)
            _memory_sessions[str(session.id)] = session.to_db()
            await db_store.save_session(session.to_db())
            return reply

    reply = await engine.process_step(
        session,
        input_value=req.input.value,
        input_text=input_text,  # Use translated text
    )

    if input_text:
        g_res = check_input(input_text, session.state.value)
        if g_res.warning_message:
            reply.ui.warnings.append(g_res.warning_message)

    out_res = check_output(reply)
    if out_res.compliance_violation:
        await db_store.log_guardrail(session.id, stage="OUTPUT", code="O4", action="COMPLIANCE_BLOCKED", snippet="banned term replaced")

    # Translate reply messages to Hinglish if original input was Hinglish or session language is HI
    if was_hinglish or session.data.get("language") == "HI":
        translated_messages = []
        for msg in reply.messages:
            translated_msg = await translator.translate_english_to_hinglish(msg)
            translated_messages.append(translated_msg)
        reply.messages = translated_messages

    _memory_sessions[str(session.id)] = session.to_db()
    try:
        await db_store.save_session(session.to_db())
    except Exception:
        pass

    return out_res.reply


@router.post("/upload", response_model=BotReply)
async def upload_document(
    session_id: Annotated[str, Form()],
    doc_code: Annotated[str, Form()],
    file: UploadFile = File(...),
    policy_repo: Annotated[PolicyRepo, Depends(get_policy_repo)] = None,
    member_repo: Annotated[MemberRepo, Depends(get_member_repo)] = None,
    claim_repo: Annotated[ClaimRepo, Depends(get_claim_repo)] = None,
    hospital_repo: Annotated[HospitalRepo, Depends(get_hospital_repo)] = None,
    master_repo: Annotated[MasterRepo, Depends(get_master_repo)] = None,
    nlu: Annotated[NLU, Depends(get_nlu)] = None,
    db_session: Annotated[AsyncSession, Depends(get_db_session)] = None,
) -> BotReply:
    """Upload a document for a reimbursement claim."""
    try:
        sess_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    db_store = DBStore(db_session)
    db_obj = None
    try:
        db_obj = await db_store.get_session(sess_uuid)
    except Exception:
        pass

    if not db_obj:
        db_obj = _memory_sessions.get(session_id)

    if not db_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    session = FlowSession(db_obj)
    engine = FlowEngine(
        policy_repo=policy_repo,
        member_repo=member_repo,
        claim_repo=claim_repo,
        master_repo=master_repo,
        hospital_repo=hospital_repo,
        nlu=nlu,
        db_store=db_store,
    )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)

    if size_mb > settings.max_upload_mb:
        await db_store.log_guardrail(session.id, stage="INPUT", code="I9", action="BLOCKED", snippet=f"file too large {size_mb:.1f}MB")
        return engine.build_reply(
            session,
            error=ChatError(message=f"File too large ({size_mb:.1f} MB). Max allowed size is {settings.max_upload_mb} MB."),
        )

    kind = filetype.guess(content)
    mime = kind.mime if kind else file.content_type

    if not kind and (file.filename.lower().endswith(".pdf") or file.content_type == "application/pdf"):
        if content.startswith(b"%PDF"):
            mime = "application/pdf"
            ext = "pdf"
        else:
            mime = None
    elif kind:
        ext = kind.extension
    else:
        ext = "bin"

    allowed_mimes = ["application/pdf", "image/jpeg", "image/png"]
    if mime not in allowed_mimes:
        await db_store.log_guardrail(session.id, stage="INPUT", code="I9", action="BLOCKED", snippet=f"invalid mime {mime}")
        return engine.build_reply(
            session,
            error=ChatError(message="Invalid file type. Allowed formats: PDF, JPG, PNG."),
        )

    sr_number = session.data.get("sr_number", "SR_UNKNOWN")
    save_dir = settings.upload_path / sr_number
    save_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{doc_code}_{int(time.time())}.{ext}"
    file_path = save_dir / filename

    with open(file_path, "wb") as f:
        f.write(content)

    if "uploaded_docs" not in session.data:
        session.data["uploaded_docs"] = {}

    session.data["uploaded_docs"][doc_code] = {
        "original_name": file.filename,
        "stored_path": str(file_path),
        "mime": mime,
        "size_bytes": len(content),
    }

    doc_id = 0
    if db_store and db_store.session:
        try:
            # Ensure service request exists in DB before inserting uploaded document
            from sqlalchemy import select
            sr_check = await db_store.session.execute(
                select(ServiceRequestTable).where(ServiceRequestTable.sr_number == sr_number)
            )
            if not sr_check.scalar_one_or_none():
                claim_no = session.data.get("claim_no", "CLM_FALLBACK")
                # Ensure claim_intimation exists if claim_no is referenced
                from app.db.tables import ClaimIntimationTable
                claim_check = await db_store.session.execute(
                    select(ClaimIntimationTable).where(ClaimIntimationTable.claim_no == claim_no)
                )
                if not claim_check.scalar_one_or_none():
                    p_block = session.data.get("patient_block", {})
                    a_block = session.data.get("admission_block", {})
                    h_block = session.data.get("hospital_block", {})
                    c_type = session.data.get("claim_type", "REIMBURSEMENT")
                    intimation = ClaimIntimationTable(
                        claim_no=claim_no,
                        session_id=session.id,
                        policy_no=session.policy_no or "",
                        uhid=p_block.get("uhid", "UH1000000001"),
                        patient_name=p_block.get("patient", session.data.get("patient_name", "")),
                        claim_type=c_type,
                        status="OPEN",
                        intimator_name=p_block.get("intimator_name", ""),
                        intimator_email=p_block.get("intimator_email", ""),
                        intimation_type=p_block.get("intimation_type", "EMERGENCY"),
                        doa=datetime.strptime(a_block.get("doa"), "%Y-%m-%d").date() if isinstance(a_block.get("doa"), str) else a_block.get("doa", self.clock.today() if hasattr(self, "clock") else datetime.now().date()),
                        doctor_name=a_block.get("doctor_name", ""),
                        diagnosis_code=a_block.get("diagnosis_code"),
                        diagnosis_text=a_block.get("diagnosis", ""),
                        hospital_id=h_block.get("hospital_id", ""),
                        approx_cost=h_block.get("approx_cost", 0),
                        needs_review=False,
                        review_reason=None,
                        doc_mismatch=False,
                        payload=session.data,
                    )
                    db_store.session.add(intimation)
                    await db_store.session.flush()

                sr_rec = ServiceRequestTable(
                    sr_number=sr_number,
                    claim_no=claim_no,
                    type="DOCUMENT_PENDING",
                    status="DOCUMENT_PENDING",
                )
                db_store.session.add(sr_rec)
                await db_store.session.flush()

            up_doc = UploadedDocumentTable(
                sr_number=sr_number,
                doc_code=doc_code,
                original_name=file.filename,
                stored_path=str(file_path),
                mime=mime,
                size_bytes=len(content),
            )
            db_store.session.add(up_doc)
            await db_store.session.commit()
            await db_store.session.refresh(up_doc)
            doc_id = up_doc.id
        except Exception as e:
            try:
                await db_store.session.rollback()
            except Exception:
                pass

    # Document AI Extraction & Verification
    from app.core.deps import get_doc_ai
    doc_ai = get_doc_ai()
    exp_patient = session.data.get("patient_block", {}).get("patient") or session.data.get("patient_name")
    exp_doa = session.data.get("admission_block", {}).get("doa") or session.data.get("doa")

    extraction_res = await doc_ai.extract_and_validate(
        file_path=str(file_path),
        doc_code=doc_code,
        expected_patient_name=exp_patient,
        expected_doa=exp_doa,
        original_name=file.filename,
    )

    if "extractions" not in session.data:
        session.data["extractions"] = {}
    session.data["extractions"][doc_code] = extraction_res.model_dump(mode="json")
    session.data["last_uploaded_doc"] = doc_code

    if doc_id and db_store:
        try:
            await db_store.log_document_extraction(
                document_id=doc_id,
                doc_code=doc_code,
                detected_type=extraction_res.detected_type,
                status=extraction_res.status,
                fields={k: v.model_dump() for k, v in extraction_res.fields.items()},
                checks=[c.model_dump() for c in extraction_res.checks],
                user_accepted=extraction_res.user_accepted,
                model=extraction_res.model,
                latency_ms=extraction_res.latency_ms,
            )
        except Exception:
            pass

    if extraction_res.status in ("MISMATCH", "WRONG_TYPE"):
        session.data["doc_mismatch"] = True
        claim_no = session.data.get("claim_no")
        if claim_no and db_store and db_store.session:
            try:
                from app.db.tables import ClaimIntimationTable
                await db_store.session.execute(
                    ClaimIntimationTable.__table__.update()
                    .where(ClaimIntimationTable.claim_no == claim_no)
                    .values(
                        doc_mismatch=True,
                        needs_review=True,
                        review_reason=f"Document validation warning ({extraction_res.status})",
                    )
                )
                await db_store.session.commit()
            except Exception:
                pass

        _memory_sessions[str(session.id)] = session.to_db()
        try:
            await db_store.save_session(session.to_db())
        except Exception:
            pass

        reply = engine.build_reply(session)
        reply.messages = [
            f"Uploaded {file.filename} for {doc_code}.",
            f"Warning: Document verification flag detected ({extraction_res.status}).",
        ]
        reply.ui = UI(
            type="extraction",
            data={
                "doc_code": doc_code,
                "status": extraction_res.status,
                "detected_type": extraction_res.detected_type,
                "checks": [c.model_dump() for c in extraction_res.checks],
                "mismatches": extraction_res.mismatches,
            },
            options=[
                UIOption(value="ACCEPT_EXTRACTION", label="Accept & Continue", subtext="Proceed despite verification warning"),
                UIOption(value="REUPLOAD_DOC", label="Re-upload Document", subtext="Upload a replacement document file"),
            ],
        )
        return reply

    if engine.check_mandatory_docs_done(session):
        session.state = State.DONE
        from app.services.email_service import send_claim_confirmation_email
        await send_claim_confirmation_email(session.data, policy_no=session.policy_no or "")
        if db_store and db_store.session:
            try:
                await db_store.session.execute(
                    ServiceRequestTable.__table__.update()
                    .where(ServiceRequestTable.sr_number == sr_number)
                    .values(status="COMPLETE")
                )
                await db_store.session.commit()
            except Exception:
                pass

        _memory_sessions[str(session.id)] = session.to_db()
        return engine.build_reply(
            session,
            messages=[
                "All required documents have been uploaded successfully.",
                MESSAGES["final"],
            ],
        )

    _memory_sessions[str(session.id)] = session.to_db()
    try:
        await db_store.save_session(session.to_db())
    except Exception:
        pass

    return engine.build_reply(
        session,
        messages=[f"Uploaded {file.filename} for {doc_code}."],
    )



@router.get("/session/{session_id}", response_model=BotReply)
async def get_session_state(
    session_id: str,
    policy_repo: Annotated[PolicyRepo, Depends(get_policy_repo)],
    member_repo: Annotated[MemberRepo, Depends(get_member_repo)],
    claim_repo: Annotated[ClaimRepo, Depends(get_claim_repo)],
    hospital_repo: Annotated[HospitalRepo, Depends(get_hospital_repo)],
    master_repo: Annotated[MasterRepo, Depends(get_master_repo)],
    nlu: Annotated[NLU, Depends(get_nlu)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BotReply:
    """Retrieve current session state for refresh resume."""
    try:
        sess_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    db_store = DBStore(db_session)
    db_obj = None
    try:
        db_obj = await db_store.get_session(sess_uuid)
    except Exception:
        pass

    if not db_obj:
        db_obj = _memory_sessions.get(session_id)

    if not db_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    session = FlowSession(db_obj)
    engine = FlowEngine(
        policy_repo=policy_repo,
        member_repo=member_repo,
        claim_repo=claim_repo,
        master_repo=master_repo,
        hospital_repo=hospital_repo,
        nlu=nlu,
        db_store=db_store,
    )

    return engine.build_reply(session)
