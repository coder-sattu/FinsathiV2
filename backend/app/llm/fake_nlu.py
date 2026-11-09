"""Rule-based Fake NLU implementation for offline testing."""

import re
from datetime import timedelta
from app.llm.nlu import InterpretRequest, Interpretation


class FakeNLU:
    """Deterministic rule-based NLU interpreter."""

    async def interpret(self, req: InterpretRequest) -> Interpretation:
        # interpret input via rules
        text_lower = req.text.lower().strip()

        # check AGENT intent
        if any(w in text_lower for w in ["agent", "human", "talk to a person", "call me", "representative"]):
            return Interpretation(intent="AGENT", confidence=0.95)

        # check RESTART intent
        if any(w in text_lower for w in ["restart", "start over", "reset"]):
            return Interpretation(intent="RESTART", confidence=0.95)

        # check allowed_values match FIRST
        for allowed in req.allowed_values:
            if allowed.lower() in text_lower:
                return Interpretation(intent="ANSWER", value=allowed, confidence=0.90)

        # check FAQ / QUESTION intent
        for faq in req.faq:
            faq_q = faq.question.lower()
            # match keywords
            if ("network hospital" in text_lower and "network hospital" in faq_q) or \
               ("cashless claim" in text_lower and "cashless claim" in faq_q) or \
               ("reimbursement claim" in text_lower and "reimbursement claim" in faq_q) or \
               (faq.id.lower() in text_lower):
                return Interpretation(intent="QUESTION", faq_id=faq.id, confidence=0.90)

        # state specific text matching
        if req.state == "CLAIM_TYPE":
            if "cashless" in text_lower:
                return Interpretation(intent="ANSWER", value="CASHLESS", confidence=0.90)
            elif "reimbursement" in text_lower:
                return Interpretation(intent="ANSWER", value="REIMBURSEMENT", confidence=0.90)

        # entity extraction for form states
        extracted_fields: dict[str, str] = {}

        # date extraction
        if "yesterday" in text_lower:
            extracted_fields["doa"] = str(req.today - timedelta(days=1))
        elif "today" in text_lower:
            extracted_fields["doa"] = str(req.today)

        # doctor extraction
        doc_match = re.search(r"\b(dr\.?\s+[a-z]+)\b", text_lower, re.IGNORECASE)
        if doc_match:
            extracted_fields["doctor_name"] = doc_match.group(1).title()

        # diagnosis extraction
        for d in req.diagnoses:
            if d.name.lower() in text_lower:
                extracted_fields["diagnosis_code"] = d.code
                extracted_fields["diagnosis"] = d.name
                break

        # hallucination test case
        if "z99.9" in text_lower:
            extracted_fields["diagnosis_code"] = "Z99.9"

        # member extraction
        for m in req.members:
            if m.first_name.lower() in text_lower or m.relation.lower() in text_lower:
                extracted_fields["patient"] = m.first_name
                break

        if extracted_fields:
            return Interpretation(intent="ANSWER", fields=extracted_fields, confidence=0.85)

        return Interpretation(intent="OFF_TOPIC", confidence=0.30)
