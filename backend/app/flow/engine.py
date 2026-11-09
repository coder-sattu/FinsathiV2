"""State machine orchestrator and flow engine."""

import uuid
from datetime import datetime, timedelta
from typing import Any
from app.core.clock import Clock
from app.core.config import settings
from app.db.store import DBStore
from app.db.tables import ChatSessionTable, ClaimIntimationTable, ServiceRequestTable, UploadedDocumentTable
from app.flow.messages import MESSAGES
from app.flow.states import State, TERMINAL_STATES
from app.flow.validators import (
    clean_mobile,
    validate_email,
    validate_mobile,
    validate_pincode,
    validate_policy_no,
)
from app.guard.disclaimers import get_disclaimer
from app.idgen import generate_claim_no, generate_sr_no
from app.llm.nlu import DiagnosisHint, FAQHint, InterpretRequest, MemberHint, NLU
from app.models.domain import Member, Policy
from app.repository.base import ClaimRepo, HospitalRepo, MasterRepo, MemberRepo, PolicyRepo
from app.schemas.api import BotReply, ChatError, UI, UIField, UIOption
from app.services.email_service import send_claim_confirmation_email


class FlowSession:
    """In-memory wrapper for chat session state."""

    def __init__(self, db_obj: ChatSessionTable) -> None:
        # initialize session
        self.id = db_obj.id
        self.state = State(db_obj.state)
        self.policy_no = db_obj.policy_no
        self.data: dict[str, Any] = db_obj.data or {}
        self.attempts = db_obj.attempts
        self.llm_calls = db_obj.llm_calls
        self.editing = db_obj.editing
        self.consent_at = db_obj.consent_at
        self.guard_hits = db_obj.guard_hits
        self.expires_at = db_obj.expires_at

    def to_db(self) -> ChatSessionTable:
        # convert to ORM model
        return ChatSessionTable(
            id=self.id,
            state=self.state.value,
            policy_no=self.policy_no,
            data=self.data,
            attempts=self.attempts,
            llm_calls=self.llm_calls,
            editing=self.editing,
            consent_at=self.consent_at,
            guard_hits=self.guard_hits,
            expires_at=self.expires_at,
        )


class FlowEngine:
    """State machine engine."""

    def __init__(
        self,
        policy_repo: PolicyRepo,
        member_repo: MemberRepo,
        claim_repo: ClaimRepo,
        master_repo: MasterRepo,
        hospital_repo: HospitalRepo | None = None,
        nlu: NLU | None = None,
        db_store: DBStore | None = None,
        clock: Clock | None = None,
    ) -> None:
        # initialize engine dependencies
        self.policy_repo = policy_repo
        self.member_repo = member_repo
        self.claim_repo = claim_repo
        self.master_repo = master_repo
        self.hospital_repo = hospital_repo
        self.nlu = nlu
        self.db_store = db_store
        self.clock = clock or Clock()
        self.config = master_repo.config()

    def create_session(self) -> FlowSession:
        # create new session
        now = self.clock.now()
        expires = now + timedelta(minutes=self.config.session_ttl_minutes)
        db_obj = ChatSessionTable(
            id=uuid.uuid4(),
            state=State.CONSENT.value,
            policy_no=None,
            data={},
            attempts=0,
            llm_calls=0,
            editing=False,
            consent_at=None,
            guard_hits=0,
            expires_at=expires,
        )
        return FlowSession(db_obj)

    def get_doc_checklist(self, session: FlowSession) -> list[dict[str, Any]]:
        # build document checklist
        c_type = session.data.get("claim_type", "REIMBURSEMENT")
        req_docs = self.master_repo.required_docs(c_type)
        uploaded = session.data.get("uploaded_docs", {})
        checklist = []
        for doc in req_docs:
            is_up = doc.code in uploaded
            checklist.append({
                "code": doc.code,
                "name": doc.name,
                "mandatory": doc.mandatory,
                "uploaded": is_up,
                "file_name": uploaded.get(doc.code, {}).get("original_name") if is_up else None,
            })
        return checklist

    def check_mandatory_docs_done(self, session: FlowSession) -> bool:
        # check if all mandatory documents uploaded
        checklist = self.get_doc_checklist(session)
        for item in checklist:
            if item["mandatory"] and not item["uploaded"]:
                return False
        return True

    def build_reply(
        self,
        session: FlowSession,
        messages: list[str] | None = None,
        error: ChatError | None = None,
    ) -> BotReply:
        # build bot reply for state
        msgs = messages or []
        st = session.state
        ui = UI(type="message")

        if st == State.CONSENT:
            if not msgs:
                msgs = [MESSAGES["consent"]]
            ui = UI(
                type="consent",
                options=[
                    UIOption(value="YES", label="I agree"),
                    UIOption(value="NO", label="No"),
                ],
            )
        elif st == State.LANGUAGE_CHOICE:
            if not msgs:
                msgs = ["Please select your preferred language / अपनी पसंदीदा भाषा चुनें:"]
            ui = UI(
                type="buttons",
                options=[
                    UIOption(value="EN", label="English"),
                    UIOption(value="HI", label="Hindi / हिन्दी"),
                ],
            )
        elif st == State.AUTH_CHOICE:
            if not msgs:
                msgs = [MESSAGES["welcome"]]
            ui = UI(
                type="buttons",
                options=[
                    UIOption(value="POLICY", label="Policy Number"),
                    UIOption(value="RMN", label="Registered Mobile Number"),
                ],
            )
        elif st == State.POLICY_INPUT:
            if not msgs:
                msgs = ["Please enter your Policy Number (e.g. HP-RET-2026-0001)."]
            ui = UI(type="text")
        elif st == State.MEMBER_VERIFY:
            p_no = session.policy_no or ""
            policy = self.policy_repo.by_number(p_no)
            if policy and policy.type == "GROUP":
                label = "Please enter your Employee Code (e.g. EMP10001) or UHID."
            else:
                label = "Please enter your UHID (e.g. UH1000000001)."
            if not msgs:
                msgs = [label]
            ui = UI(type="text")
        elif st == State.RMN_INPUT:
            if not msgs:
                msgs = ["Please enter your 10-digit Registered Mobile Number."]
            ui = UI(type="text")
        elif st == State.OTP_INPUT:
            rmn = session.data.get("rmn", "")
            last4 = rmn[-4:] if len(rmn) >= 4 else rmn
            if not msgs:
                msgs = [MESSAGES["otp_sent"].format(last4=last4)]
            ui = UI(type="otp")
        elif st == State.SELECT_POLICY:
            if not msgs:
                msgs = ["Multiple policies found. Please select one:"]
            policies = session.data.get("available_policies", [])
            opts = [
                UIOption(
                    value=p["policy_no"],
                    label=f"{p['policy_no']} ({p['product']})",
                    subtext=f"Insured: {p['holder_name']} | Type: {p['type']}",
                )
                for p in policies
            ]
            ui = UI(type="list", options=opts)
        elif st == State.OPEN_CLAIM:
            claim_info = session.data.get("open_claim", {})
            if not msgs:
                msgs = [
                    MESSAGES["open_claim"],
                    f"Claim No: {claim_info.get('claim_no')} | Patient: {claim_info.get('patient_name')} | DOA: {claim_info.get('doa')} | Status: {claim_info.get('status')}",
                    MESSAGES["continue_q"],
                ]
            ui = UI(
                type="buttons",
                options=[
                    UIOption(value="YES", label="Yes, intimate new claim"),
                    UIOption(value="NO", label="No, track existing claim"),
                ],
                data=claim_info,
            )
        elif st == State.DOA_CHECK:
            if not msgs:
                msgs = ["Please enter the Date of Admission (DOA) for your new claim:"]
            ui = UI(type="date")
        elif st == State.CLAIM_TYPE:
            if not msgs:
                msgs = [MESSAGES["claim_type_q"]]
            ui = UI(
                type="buttons",
                options=[
                    UIOption(value="CASHLESS", label="Cashless"),
                    UIOption(value="REIMBURSEMENT", label="Reimbursement"),
                ],
            )
        elif st == State.SELF_I_OFFER:
            if not msgs:
                msgs = [MESSAGES["self_i_q"]]
            ui = UI(
                type="buttons",
                options=[
                    UIOption(value="YES", label="Yes, go to Website / App"),
                    UIOption(value="NO", label="No, continue here"),
                ],
            )
        elif st == State.PATIENT:
            if not msgs:
                msgs = ["Please share patient details:"]
            members = self.member_repo.by_policy(session.policy_no or "")
            m_opts = [{"value": m.name, "label": f"{m.name} ({m.relation})"} for m in members]
            p_data = session.data.get("patient_block", {})
            p_no = session.policy_no or ""
            pol = self.policy_repo.by_number(p_no)

            ui = UI(
                type="form",
                fields=[
                    UIField(name="patient", label="Patient Name", type="select", options=m_opts, value=p_data.get("patient", session.data.get("patient_name", ""))),
                    UIField(name="intimator_name", label="Intimator Name", type="text", value=p_data.get("intimator_name", pol.holder_name if pol else "")),
                    UIField(name="intimator_email", label="Intimator Email", type="email", value=p_data.get("intimator_email", pol.email if pol else "")),
                    UIField(name="intimation_type", label="Intimation Type", type="select", options=[{"value": "PLANNED", "label": "Planned hospitalisation"}, {"value": "EMERGENCY", "label": "Emergency hospitalisation"}], value=p_data.get("intimation_type", "EMERGENCY")),
                ],
            )
        elif st == State.PATIENT_CONFIRM:
            p_data = session.data.get("patient_block", {})
            if not msgs:
                msgs = [MESSAGES["confirm_q"]]
            ui = UI(
                type="summary",
                data=p_data,
                options=[
                    UIOption(value="YES", label="Confirm Patient Details"),
                    UIOption(value="NO", label="Edit Patient Details"),
                ],
            )
        elif st == State.ADMISSION:
            if not msgs:
                msgs = ["Please share admission details:"]
            diag_opts = [{"value": d.name, "label": f"{d.code} - {d.name}"} for d in self.master_repo.diagnoses()]
            a_data = session.data.get("admission_block", {})
            default_doa = a_data.get("doa", session.data.get("doa", str(self.clock.today())))

            ui = UI(
                type="form",
                fields=[
                    UIField(name="doa", label="Date of Admission", type="date", value=default_doa),
                    UIField(name="doctor_name", label="Doctor Name", type="text", value=a_data.get("doctor_name", "")),
                    UIField(name="diagnosis", label="Diagnosis", type="search_select", options_ref="diagnoses", allow_other=True, options=diag_opts, value=a_data.get("diagnosis", "")),
                ],
            )
        elif st == State.ADMISSION_CONFIRM:
            a_data = session.data.get("admission_block", {})
            if not msgs:
                msgs = [MESSAGES["confirm_q"]]
            ui = UI(
                type="summary",
                data=a_data,
                options=[
                    UIOption(value="YES", label="Confirm Admission Details"),
                    UIOption(value="NO", label="Edit Admission Details"),
                ],
            )
        elif st == State.HOSPITAL_PIN:
            if not msgs:
                msgs = ["Please enter the 6-digit hospital Pincode:"]
            ui = UI(type="text")
        elif st == State.HOSPITAL_PICK:
            h_list = session.data.get("hospital_candidates", [])
            exact = session.data.get("hospital_exact_match", True)
            if not msgs:
                if exact:
                    msgs = ["Select hospital:"]
                else:
                    pin = session.data.get("pincode", "")
                    msgs = [f"No hospital found at {pin}. Here are hospitals near you:"]

            opts = [
                UIOption(
                    value=h["hospital_id"],
                    label=h["name"],
                    subtext=f"{h['address']} | {'Network' if h['network'] else 'Non-network'}",
                    badge="Network" if h["network"] else "Non-network",
                    data=h,
                )
                for h in h_list
            ]
            ui = UI(type="list", options=opts)
        elif st == State.NON_NETWORK:
            h_name = session.data.get("hospital_block", {}).get("name", "Selected hospital")
            if not msgs:
                msgs = [MESSAGES["non_network"].format(hospital=h_name)]
            ui = UI(
                type="buttons",
                options=[
                    UIOption(value="YES", label="Yes, switch to Reimbursement"),
                    UIOption(value="NO", label="No, select another hospital"),
                ],
            )
        elif st == State.HOSPITAL_CONFIRM:
            h_data = session.data.get("hospital_block", {})
            if not msgs:
                msgs = [MESSAGES["confirm_q"]]
            ui = UI(
                type="summary",
                data=h_data,
                options=[
                    UIOption(value="YES", label="Confirm Hospital Details"),
                    UIOption(value="NO", label="Edit Hospital Details"),
                ],
            )
        elif st == State.REVIEW:
            if not msgs:
                msgs = ["Please review your claim intimation summary:"]
            summary_data = {
                "Claim Type": session.data.get("claim_type", "CASHLESS"),
                "Patient": session.data.get("patient_block", {}).get("patient", ""),
                "Intimator": session.data.get("patient_block", {}).get("intimator_name", ""),
                "DOA": session.data.get("admission_block", {}).get("doa", ""),
                "Doctor": session.data.get("admission_block", {}).get("doctor_name", ""),
                "Diagnosis": session.data.get("admission_block", {}).get("diagnosis", ""),
                "Hospital": session.data.get("hospital_block", {}).get("name", ""),
                "Pincode": session.data.get("hospital_block", {}).get("pincode", ""),
                "Approx Cost": f"₹{session.data.get('hospital_block', {}).get('approx_cost', 0):,}",
            }
            ui = UI(
                type="summary",
                data=summary_data,
                options=[
                    UIOption(value="CONFIRM", label="Confirm & Submit Claim"),
                    UIOption(value="EDIT_PATIENT", label="Edit Patient Block"),
                    UIOption(value="EDIT_ADMISSION", label="Edit Admission Block"),
                    UIOption(value="EDIT_HOSPITAL", label="Edit Hospital Block"),
                ],
            )
        elif st == State.DOC_CHOICE:
            sr_no = session.data.get("sr_number", "")
            if not msgs:
                msgs = [MESSAGES["upload_q"].format(sr=sr_no)]
            ui = UI(
                type="buttons",
                options=[
                    UIOption(value="YES", label="Yes, upload documents now"),
                    UIOption(value="NO", label="No, upload later"),
                ],
            )
        elif st == State.DOC_UPLOAD:
            checklist = self.get_doc_checklist(session)
            if not msgs:
                msgs = ["Please upload the required documents for your reimbursement claim:"]
            ui = UI(
                type="file",
                data={"checklist": checklist, "sr_number": session.data.get("sr_number")},
                options=[
                    UIOption(value="LATER", label="Finish later"),
                ],
            )
        elif st == State.DONE:
            claim_no = session.data.get("claim_no", "")
            if not msgs:
                msgs = [
                    MESSAGES["cashless_done"].format(claim_no=claim_no) if session.data.get("claim_type") == "CASHLESS" else f"Claim No: {claim_no}. All required documents have been received.",
                    MESSAGES["final"],
                ]
            ui = UI(type="message")
        elif st == State.SR_PENDING:
            sr_no = session.data.get("sr_number", "")
            if not msgs:
                msgs = [
                    MESSAGES["sr_pending"].format(sr=sr_no),
                    MESSAGES["final"],
                ]
            ui = UI(type="message")
        elif st == State.END_REDIRECT:
            if not msgs:
                msgs = [
                    f"Please visit our website: {self.config.links.website_url} or download the Self-I app: {self.config.links.self_i_url}"
                ]
            ui = UI(type="message")
        elif st == State.LOCKED:
            if not msgs:
                msgs = [MESSAGES["locked"]]
            ui = UI(type="handoff")
        elif st == State.END_INACTIVE:
            p_no = session.policy_no or ""
            if not msgs:
                msgs = [MESSAGES["policy_inactive"].format(policy_no=p_no)]
            ui = UI(type="message")
        elif st == State.END_TRACK:
            claim_no = session.data.get("open_claim", {}).get("claim_no", "")
            if not msgs:
                msgs = [f"Thank you. You can track your claim with claim no. {claim_no}."]
            ui = UI(type="message")
        elif st == State.END_NO_CONSENT:
            if not msgs:
                msgs = [
                    f"Thank you. For more information please visit our website: {self.config.links.website_url}"
                ]
            ui = UI(type="message")
        elif st == State.AGENT_HANDOFF:
            if not msgs:
                msgs = [self.config.agent_handoff_message]
            ui = UI(type="handoff")

        return BotReply(
            session_id=str(session.id),
            state=session.state.value,
            messages=msgs,
            ui=ui,
            error=error,
        )

    async def process_step(
        self,
        session: FlowSession,
        input_value: Any = None,
        input_text: str | None = None,
    ) -> BotReply:
        # process state transition
        now = self.clock.now()
        if session.expires_at < now:
            return BotReply(
                session_id=str(session.id),
                state=session.state.value,
                messages=["Session expired. Please start over."],
                ui=UI(type="message"),
                error=ChatError(message="Session expired"),
            )

        session.expires_at = now + timedelta(minutes=self.config.session_ttl_minutes)
        st = session.state

        # global command check
        text_str = (str(input_text or input_value or "")).strip().lower()
        if text_str == "restart":
            session.state = State.CONSENT
            session.attempts = 0
            session.data = {}
            session.editing = False
            return self.build_reply(session, messages=["Restarted session."])
        elif text_str == "agent":
            session.state = State.AGENT_HANDOFF
            return self.build_reply(session)

        # I5: Sensitive states check (NEVER call NLU in auth states)
        sensitive_states = {State.POLICY_INPUT, State.MEMBER_VERIFY, State.RMN_INPUT, State.OTP_INPUT, State.LANGUAGE_CHOICE}

        # NLU Free-text processing for non-sensitive states
        if input_text and not input_value and st not in sensitive_states and self.nlu and session.llm_calls < 20:
            members_hints = [MemberHint(first_name=m.name.split()[0], relation=m.relation) for m in self.member_repo.by_policy(session.policy_no or "")]
            diag_hints = [DiagnosisHint(code=d.code, name=d.name) for d in self.master_repo.diagnoses()]
            faq_hints = [FAQHint(id=f.id, question=f.question) for f in self.master_repo.faqs()]

            req = InterpretRequest(
                state=st.value,
                text=input_text,
                today=self.clock.today(),
                allowed_values=["CASHLESS", "REIMBURSEMENT"] if st == State.CLAIM_TYPE else (["YES", "NO"] if "CONFIRM" in st.value or st in (State.CONSENT, State.SELF_I_OFFER, State.OPEN_CLAIM, State.DOC_CHOICE) else []),
                members=members_hints,
                diagnoses=diag_hints,
                faq=faq_hints,
            )

            interp = await self.nlu.interpret(req)
            session.llm_calls += 1

            if self.db_store:
                await self.db_store.log_audit(session.id, event="llm_call", from_state=st.value, detail=interp.model_dump())

            # O2 Grounding Check
            all_diag_codes = {d.code for d in self.master_repo.diagnoses()}
            if interp.fields.get("diagnosis_code") and interp.fields["diagnosis_code"] not in all_diag_codes:
                if self.db_store:
                    await self.db_store.log_guardrail(session.id, stage="OUTPUT", code="O2", action="DROPPED", snippet=interp.fields["diagnosis_code"])
                interp.fields.pop("diagnosis_code", None)

            all_faq_ids = {f.id for f in self.master_repo.faqs()}
            if interp.faq_id and interp.faq_id not in all_faq_ids:
                if self.db_store:
                    await self.db_store.log_guardrail(session.id, stage="OUTPUT", code="O2", action="DROPPED", snippet=interp.faq_id)
                interp.faq_id = ""

            if interp.confidence >= 0.6:
                if interp.intent == "AGENT":
                    session.state = State.AGENT_HANDOFF
                    return self.build_reply(session)
                elif interp.intent == "RESTART":
                    session.state = State.CONSENT
                    session.data = {}
                    return self.build_reply(session, messages=["Restarted session."])
                elif interp.intent == "QUESTION":
                    answer = interp.value
                    if interp.faq_id and interp.faq_id != "RAG_POLICY_DOC":
                        faq_item = next((f for f in self.master_repo.faqs() if f.id == interp.faq_id), None)
                        if faq_item:
                            answer = faq_item.answer
                    if answer:
                        reply = self.build_reply(session, messages=[answer])
                        reply.ui.disclaimer = get_disclaimer("faq")
                        return reply
                elif interp.intent == "ANSWER":
                    if interp.value:
                        input_value = interp.value
                    elif interp.fields:
                        if st == State.ADMISSION:
                            a_data = session.data.get("admission_block", {})
                            a_data.update(interp.fields)
                            session.data["admission_block"] = a_data
                            return self.build_reply(session)
                        elif st == State.PATIENT:
                            p_data = session.data.get("patient_block", {})
                            p_data.update(interp.fields)
                            session.data["patient_block"] = p_data
                            return self.build_reply(session)

        # state handlers
        if st == State.CONSENT:
            val = (str(input_value or input_text or "")).strip().upper()
            if val in ("YES", "AGREE", "I AGREE"):
                session.consent_at = now
                session.state = State.LANGUAGE_CHOICE
                return self.build_reply(session)
            elif val in ("NO", "DISAGREE"):
                session.state = State.END_NO_CONSENT
                return self.build_reply(session)
            else:
                return self.build_reply(session, error=ChatError(message="Please choose I agree or No."))

        elif st == State.LANGUAGE_CHOICE:
            val = (str(input_value or input_text or "")).strip().upper()
            if val in ("EN", "ENGLISH"):
                session.data["language"] = "EN"
                session.state = State.AUTH_CHOICE
                return self.build_reply(session)
            elif val in ("HI", "HINDI", "HINDI / HINDI", "HINDI / हिन्‍दी", "HINDI / हिन्दी"):
                session.data["language"] = "HI"
                session.state = State.AUTH_CHOICE
                return self.build_reply(session)
            else:
                return self.build_reply(
                    session,
                    error=ChatError(message="Please select English or Hindi / कृपया अंग्रेजी या हिंदी चुनें।")
                )

        elif st == State.AUTH_CHOICE:
            val = (str(input_value or input_text or "")).strip().upper()
            if "POLICY" in val:
                session.state = State.POLICY_INPUT
                return self.build_reply(session)
            elif "RMN" in val or "MOBILE" in val or "NUMBER" in val:
                session.state = State.RMN_INPUT
                return self.build_reply(session)
            else:
                return self.build_reply(session, error=ChatError(message="Please choose Policy Number or Registered Mobile Number."))

        elif st == State.POLICY_INPUT:
            raw = str(input_text or input_value or "")
            p_no = validate_policy_no(raw)
            if not p_no:
                session.attempts += 1
                if session.attempts >= self.config.max_attempts:
                    session.state = State.LOCKED
                    return self.build_reply(session)
                return self.build_reply(session, error=ChatError(message="Invalid policy number format. Example: HP-RET-2026-0001."))

            policy = self.policy_repo.by_number(p_no)
            if not policy:
                session.attempts += 1
                if session.attempts >= self.config.max_attempts:
                    session.state = State.LOCKED
                    return self.build_reply(session)
                return self.build_reply(session, error=ChatError(message="Policy not found. Please check and try again."))

            session.policy_no = policy.policy_no
            session.attempts = 0
            session.state = State.MEMBER_VERIFY
            return self.build_reply(session)

        elif st == State.MEMBER_VERIFY:
            raw = str(input_text or input_value or "").strip()
            p_no = session.policy_no or ""
            member = self.member_repo.verify(p_no, raw)
            if not member:
                session.attempts += 1
                if session.attempts >= self.config.max_attempts:
                    session.state = State.LOCKED
                    return self.build_reply(session)
                return self.build_reply(session, error=ChatError(message="Member details could not be verified. Please check UHID / Emp code."))

            session.data["uhid"] = member.uhid
            session.data["patient_name"] = member.name
            session.attempts = 0
            session.state = State.POLICY_CHECK
            return await self._run_system_checks(session)

        elif st == State.RMN_INPUT:
            raw = str(input_text or input_value or "")
            mob = validate_mobile(raw)
            if not mob:
                session.attempts += 1
                if session.attempts >= self.config.max_attempts:
                    session.state = State.LOCKED
                    return self.build_reply(session)
                return self.build_reply(session, error=ChatError(message="Please enter a valid 10-digit mobile number."))

            policies = self.policy_repo.by_mobile(mob)
            if not policies:
                session.attempts += 1
                if session.attempts >= self.config.max_attempts:
                    session.state = State.LOCKED
                    return self.build_reply(session)
                return self.build_reply(session, error=ChatError(message=MESSAGES["not_registered"]))

            session.data["rmn"] = mob
            session.data["available_policies"] = [p.model_dump(mode="json") for p in policies]
            session.attempts = 0
            session.state = State.OTP_INPUT
            return self.build_reply(session)

        elif st == State.OTP_INPUT:
            raw = str(input_value or input_text or "").strip()
            if raw != self.config.dev_otp:
                session.attempts += 1
                if session.attempts >= self.config.max_attempts:
                    session.state = State.LOCKED
                    return self.build_reply(session)
                return self.build_reply(session, error=ChatError(message="Invalid OTP. Please try again."))

            session.attempts = 0
            policies = session.data.get("available_policies", [])
            if len(policies) == 1:
                session.policy_no = policies[0]["policy_no"]
                session.state = State.POLICY_CHECK
                return await self._run_system_checks(session)
            else:
                session.state = State.SELECT_POLICY
                return self.build_reply(session)

        elif st == State.SELECT_POLICY:
            selected_p = str(input_value or input_text or "").strip().upper()
            policies = session.data.get("available_policies", [])
            valid_nos = [p["policy_no"].upper() for p in policies]
            if selected_p not in valid_nos:
                return self.build_reply(session, error=ChatError(message="Please select a valid policy from the list."))

            session.policy_no = selected_p
            session.state = State.POLICY_CHECK
            return await self._run_system_checks(session)

        elif st == State.OPEN_CLAIM:
            val = str(input_value or input_text or "").strip().upper()
            if val in ("YES", "TRUE", "YES, INTIMATE NEW CLAIM"):
                session.state = State.DOA_CHECK
                return self.build_reply(session)
            elif val in ("NO", "FALSE", "NO, TRACK EXISTING CLAIM"):
                session.state = State.END_TRACK
                return self.build_reply(session)
            else:
                return self.build_reply(session, error=ChatError(message="Please choose Yes or No."))

        elif st == State.DOA_CHECK:
            raw_doa = str(input_value or input_text or "").strip()
            open_c = session.data.get("open_claim", {})
            if raw_doa == open_c.get("doa"):
                msgs = [MESSAGES["same_doa"], self.config.agent_handoff_message]
                session.state = State.AGENT_HANDOFF
                return self.build_reply(session, messages=msgs)

            session.data["doa"] = raw_doa
            session.state = State.CLAIM_TYPE
            return self.build_reply(session)

        elif st == State.CLAIM_TYPE:
            val = str(input_value or input_text or "").strip().upper()
            if "CASHLESS" in val:
                session.data["claim_type"] = "CASHLESS"
                session.state = State.PATIENT
                return self.build_reply(session)
            elif "REIMBURSEMENT" in val:
                session.data["claim_type"] = "REIMBURSEMENT"
                session.state = State.SELF_I_OFFER
                return self.build_reply(session)
            else:
                return self.build_reply(session, error=ChatError(message="Please choose Cashless or Reimbursement."))

        elif st == State.SELF_I_OFFER:
            val = str(input_value or input_text or "").strip().upper()
            if val in ("YES", "GO TO WEBSITE", "YES, GO TO WEBSITE / APP"):
                session.state = State.END_REDIRECT
                return self.build_reply(session)
            elif val in ("NO", "CONTINUE", "NO, CONTINUE HERE"):
                session.state = State.PATIENT
                return self.build_reply(session)
            else:
                return self.build_reply(session, error=ChatError(message="Please choose Yes or No."))

        elif st == State.PATIENT:
            form = input_value if isinstance(input_value, dict) else {}
            patient = form.get("patient") or session.data.get("patient_name")
            intimator_name = form.get("intimator_name")
            intimator_email = form.get("intimator_email")
            intimation_type = form.get("intimation_type", "EMERGENCY")

            if not patient or not intimator_name or not intimator_email:
                return self.build_reply(session, error=ChatError(message="Please fill in all patient fields."))

            if not validate_email(intimator_email):
                return self.build_reply(session, error=ChatError(field="intimator_email", message="Please enter a valid email address."))

            members = self.member_repo.by_policy(session.policy_no or "")
            uhid = None
            for m in members:
                if m.name.lower() == patient.lower():
                    uhid = m.uhid
                    break
            if not uhid and members:
                uhid = members[0].uhid

            session.data["patient_block"] = {
                "patient": patient,
                "uhid": uhid or session.data.get("uhid", "UH1000000001"),
                "intimator_name": intimator_name,
                "intimator_email": intimator_email,
                "intimation_type": intimation_type,
            }
            session.state = State.PATIENT_CONFIRM
            return self.build_reply(session)

        elif st == State.PATIENT_CONFIRM:
            val = str(input_value or input_text or "").strip().upper()
            if val in ("YES", "CONFIRM", "CONFIRM PATIENT DETAILS"):
                if session.editing:
                    session.editing = False
                    session.state = State.REVIEW
                else:
                    session.state = State.ADMISSION
                return self.build_reply(session)
            else:
                session.editing = True
                session.state = State.PATIENT
                return self.build_reply(session)

        elif st == State.ADMISSION:
            form = input_value if isinstance(input_value, dict) else {}
            doa = form.get("doa") or session.data.get("doa")
            doctor_name = form.get("doctor_name")
            diagnosis = form.get("diagnosis")

            if not doa or not doctor_name or not diagnosis:
                return self.build_reply(session, error=ChatError(message="Please fill in all admission fields."))

            d_code = None
            d_text = diagnosis
            for d in self.master_repo.diagnoses():
                if d.name.lower() == diagnosis.lower():
                    d_code = d.code
                    break

            session.data["admission_block"] = {
                "doa": doa,
                "doctor_name": doctor_name,
                "diagnosis_code": d_code,
                "diagnosis": d_text,
            }
            session.state = State.ADMISSION_CONFIRM
            return self.build_reply(session)

        elif st == State.ADMISSION_CONFIRM:
            val = str(input_value or input_text or "").strip().upper()
            if val in ("YES", "CONFIRM", "CONFIRM ADMISSION DETAILS"):
                if session.editing:
                    session.editing = False
                    session.state = State.REVIEW
                else:
                    session.state = State.HOSPITAL_PIN
                return self.build_reply(session)
            else:
                session.editing = True
                session.state = State.ADMISSION
                return self.build_reply(session)

        elif st == State.HOSPITAL_PIN:
            raw_pin = str(input_value or input_text or "").strip()
            pin = validate_pincode(raw_pin)
            if not pin:
                return self.build_reply(session, error=ChatError(message="Please enter a valid 6-digit pincode."))

            if not self.hospital_repo:
                return self.build_reply(session, error=ChatError(message="Hospital repository unavailable."))

            candidates, exact = self.hospital_repo.by_pincode(pin)
            if not candidates:
                return self.build_reply(
                    session,
                    error=ChatError(message="We couldn't find hospitals for this pincode. Please try another pincode."),
                )

            session.data["pincode"] = pin
            session.data["hospital_candidates"] = [h.model_dump(mode="json") for h in candidates]
            session.data["hospital_exact_match"] = exact
            session.state = State.HOSPITAL_PICK
            return self.build_reply(session)

        elif st == State.HOSPITAL_PICK:
            selected_id = str(input_value or input_text or "").strip().upper()
            candidates = session.data.get("hospital_candidates", [])
            chosen = None
            for h in candidates:
                if h["hospital_id"].upper() == selected_id:
                    chosen = h
                    break

            if not chosen and self.hospital_repo:
                h_obj = self.hospital_repo.by_id(selected_id)
                if h_obj:
                    chosen = h_obj.model_dump(mode="json")

            if not chosen:
                return self.build_reply(session, error=ChatError(message="Please select a valid hospital from the list."))

            session.data["hospital_block"] = chosen
            claim_type = session.data.get("claim_type", "CASHLESS")

            if claim_type == "CASHLESS" and not chosen["network"]:
                session.state = State.NON_NETWORK
                return self.build_reply(session)

            session.state = State.HOSPITAL_CONFIRM
            return self.build_reply(session)

        elif st == State.NON_NETWORK:
            val = str(input_value or input_text or "").strip().upper()
            if val in ("YES", "CONFIRM", "YES, SWITCH TO REIMBURSEMENT"):
                session.data["claim_type"] = "REIMBURSEMENT"
                session.state = State.HOSPITAL_CONFIRM
                return self.build_reply(session)
            else:
                session.state = State.HOSPITAL_PIN
                return self.build_reply(session)

        elif st == State.HOSPITAL_CONFIRM:
            val = str(input_value or input_text or "").strip().upper()
            if val in ("YES", "CONFIRM", "CONFIRM HOSPITAL DETAILS"):
                session.editing = False
                session.state = State.REVIEW
                return self.build_reply(session)
            else:
                session.editing = True
                if session.data.get("hospital_candidates"):
                    session.state = State.HOSPITAL_PICK
                else:
                    session.state = State.HOSPITAL_PIN
                return self.build_reply(session)

        elif st == State.REVIEW:
            val = str(input_value or input_text or "").strip().upper()
            if "CONFIRM" in val or "SUBMIT" in val:
                session.state = State.SUBMIT
                return await self._submit_claim(session)
            elif "PATIENT" in val:
                session.editing = True
                session.state = State.PATIENT
                return self.build_reply(session)
            elif "ADMISSION" in val:
                session.editing = True
                session.state = State.ADMISSION
                return self.build_reply(session)
            elif "HOSPITAL" in val:
                session.editing = True
                if session.data.get("hospital_candidates"):
                    session.state = State.HOSPITAL_PICK
                else:
                    session.state = State.HOSPITAL_PIN
                return self.build_reply(session)
            else:
                return self.build_reply(session, error=ChatError(message="Please choose to Confirm or Edit a block."))

        elif st == State.DOC_CHOICE:
            val = str(input_value or input_text or "").strip().upper()
            if val in ("YES", "UPLOAD NOW", "YES, UPLOAD DOCUMENTS NOW"):
                session.state = State.DOC_UPLOAD
                return self.build_reply(session)
            elif val in ("NO", "LATER", "NO, UPLOAD LATER"):
                session.state = State.SR_PENDING
                await send_claim_confirmation_email(session.data, policy_no=session.policy_no or "")
                return self.build_reply(session)
            else:
                return self.build_reply(session, error=ChatError(message="Please choose Yes or No."))

        elif st == State.DOC_UPLOAD:
            val = str(input_value or input_text or "").strip().upper()
            if val in ("LATER", "FINISH LATER"):
                session.state = State.SR_PENDING
                return self.build_reply(session)
            elif "ACCEPT" in val:
                extractions = session.data.get("extractions", {})
                last_doc = session.data.get("last_uploaded_doc")
                if last_doc and last_doc in extractions:
                    extractions[last_doc]["user_accepted"] = True

                if self.check_mandatory_docs_done(session):
                    session.state = State.DONE
                    await send_claim_confirmation_email(session.data, policy_no=session.policy_no or "")
                    sr_number = session.data.get("sr_number")
                    if self.db_store and self.db_store.session and sr_number:
                        try:
                            await self.db_store.session.execute(
                                ServiceRequestTable.__table__.update()
                                .where(ServiceRequestTable.sr_number == sr_number)
                                .values(status="COMPLETE")
                            )
                            await self.db_store.session.commit()
                        except Exception:
                            pass
                    return self.build_reply(
                        session,
                        messages=[
                            "Document accepted. All required documents have been received.",
                            MESSAGES["final"],
                        ],
                    )
                else:
                    return self.build_reply(
                        session,
                        messages=["Document accepted. Please upload the remaining required documents."],
                    )
            elif "REUPLOAD" in val:
                last_doc = session.data.get("last_uploaded_doc")
                if last_doc:
                    session.data.get("uploaded_docs", {}).pop(last_doc, None)
                    session.data.get("extractions", {}).pop(last_doc, None)
                return self.build_reply(
                    session,
                    messages=["Please re-upload a clear and correct document file."],
                )


        return self.build_reply(session)

    async def _run_system_checks(self, session: FlowSession) -> BotReply:
        # run POLICY_CHECK and DUP_CHECK system transitions
        p_no = session.policy_no or ""
        policy = self.policy_repo.by_number(p_no)

        if not policy or policy.status != "ACTIVE":
            session.state = State.END_INACTIVE
            return self.build_reply(session)

        open_json_claims = await self.claim_repo.open_by_policy(p_no)
        open_db_claims = []
        if self.db_store:
            open_db_claims = await self.db_store.open_claims_by_policy(p_no)

        all_open = open_json_claims + open_db_claims
        if all_open:
            first_open = all_open[0]
            session.data["open_claim"] = {
                "claim_no": first_open.claim_no,
                "patient_name": first_open.patient_name,
                "doa": str(first_open.doa),
                "status": first_open.status,
            }
            session.state = State.OPEN_CLAIM
            return self.build_reply(session)

        session.state = State.CLAIM_TYPE
        return self.build_reply(session)

    async def _submit_claim(self, session: FlowSession) -> BotReply:
        # execute claim submission
        p_block = session.data.get("patient_block", {})
        a_block = session.data.get("admission_block", {})
        h_block = session.data.get("hospital_block", {})
        c_type = session.data.get("claim_type", "CASHLESS")

        db_sess = self.db_store.session if self.db_store else None
        claim_no = await generate_claim_no(db_sess)
        session.data["claim_no"] = claim_no

        approx_cost = h_block.get("approx_cost", 0)
        needs_review = approx_cost > settings.high_value_threshold
        review_reason = "High value claim > 500,000" if needs_review else None

        intimation = ClaimIntimationTable(
            claim_no=claim_no,
            session_id=session.id,
            policy_no=session.policy_no or "",
            uhid=p_block.get("uhid", "UH1000000001"),
            patient_name=p_block.get("patient", ""),
            claim_type=c_type,
            status="OPEN",
            intimator_name=p_block.get("intimator_name", ""),
            intimator_email=p_block.get("intimator_email", ""),
            intimation_type=p_block.get("intimation_type", "EMERGENCY"),
            doa=datetime.strptime(a_block.get("doa"), "%Y-%m-%d").date() if isinstance(a_block.get("doa"), str) else a_block.get("doa"),
            doctor_name=a_block.get("doctor_name", ""),
            diagnosis_code=a_block.get("diagnosis_code"),
            diagnosis_text=a_block.get("diagnosis", ""),
            hospital_id=h_block.get("hospital_id", ""),
            approx_cost=approx_cost,
            needs_review=needs_review,
            review_reason=review_reason,
            doc_mismatch=False,
            payload=session.data,
        )

        if self.db_store and self.db_store.session:
            try:
                await self.db_store.save_session(session.to_db())
                self.db_store.session.add(intimation)
                await self.db_store.session.commit()
            except Exception as e:
                print("SUBMIT_CLAIM INTIMATION ERROR:", e)
                try:
                    await self.db_store.session.rollback()
                except Exception:
                    pass

        if c_type == "CASHLESS":
            session.state = State.DONE
            await send_claim_confirmation_email(session.data, policy_no=session.policy_no or "")
            msgs = [
                MESSAGES["cashless_done"].format(claim_no=claim_no),
            ]
            if needs_review:
                msgs.append(MESSAGES["high_value"])
            msgs.append(MESSAGES["final"])
            return self.build_reply(session, messages=msgs)
        else:
            sr_no = await generate_sr_no(db_sess)
            session.data["sr_number"] = sr_no
            session.state = State.DOC_CHOICE

            sr_rec = ServiceRequestTable(
                sr_number=sr_no,
                claim_no=claim_no,
                type="DOCUMENT_PENDING",
                status="DOCUMENT_PENDING",
            )
            if self.db_store and self.db_store.session:
                try:
                    self.db_store.session.add(sr_rec)
                    await self.db_store.session.commit()
                except Exception as e:
                    print("SUBMIT_CLAIM SR ERROR:", e)
                    try:
                        await self.db_store.session.rollback()
                    except Exception:
                        pass

            msgs = [
                f"Your claim has been registered. Claim No: {claim_no}.",
                MESSAGES["upload_q"].format(sr=sr_no),
            ]
            return self.build_reply(session, messages=msgs)
