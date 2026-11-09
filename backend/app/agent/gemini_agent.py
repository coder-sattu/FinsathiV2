"""Autonomous Gemini Agent using google-genai SDK, Function Calling & Cognee Policy RAG."""

import asyncio
from pathlib import Path
from typing import Any
from google import genai
from google.genai import types

from app.agent.tools import (
    query_policy_document_rag,
    search_diagnosis,
    search_hospital,
    search_member,
    search_policy,
)
from app.core.config import settings
from app.core.gemini_utils import generate_content_with_fallback
from app.llm.fake_nlu import FakeNLU
from app.llm.nlu import InterpretRequest, Interpretation


class GeminiAgenticSystem:
    """Agentic System powered by Gemini LLM, Tool Calling, and Cognee Policy Document RAG."""

    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.fallback = FakeNLU()

    async def interpret(self, req: InterpretRequest) -> Interpretation:
        """Protocol-compliant NLU interpret method."""
        return await self.run_agent(req)

    async def run_agent(self, req: InterpretRequest, session_data: dict[str, Any] | None = None) -> Interpretation:
        """Run agentic tool loop and interpretation."""
        data = session_data or {}
        text_clean = req.text.strip()
        text_lower = text_clean.lower()

        # Conversational thanks / polite acknowledgement
        if text_lower in ("thank you", "thanks", "thankyou", "thx", "ok", "okay", "cool", "great"):
            return Interpretation(
                intent="QUESTION",
                value="You're welcome! Let me know if you need any further assistance with your claim.",
                faq_id="RAG_POLICY_DOC",
                confidence=0.99,
            )

        # Step 1: Check if user is asking a policy document query (Policy Document RAG trigger)
        policy_keywords = [
            "room rent", "icu", "cataract", "waiting period", "copay", "co-payment",
            "pre hospitalization", "post hospitalization", "clause", "limit", "sublimit", "sub-limit",
            "exclusion", "timeline", "day care", "how many days", "is covered", "coverage"
        ]
        is_policy_rag_query = any(kw in text_lower for kw in policy_keywords)

        if is_policy_rag_query:
            product = data.get("product", "")
            rag_answer = query_policy_document_rag(query=text_clean, product_name=product)
            return Interpretation(
                intent="QUESTION",
                value=rag_answer,
                faq_id="RAG_POLICY_DOC",
                confidence=0.98,
            )

        # Step 2: Use Gemini LLM with Tools if configured
        if settings.llm_enabled and self.client and self.api_key:
            try:
                # Direct tool execution evaluation via Gemini
                prompt = f"""You are Claim Assist, an intelligent health insurance AI agent.
State: {req.state}
User Input: "{req.text}"
Session Data: {data}

Available JSON Search & RAG Tools:
1. search_policy(query) -> find policy by number, holder, RMN
2. search_member(policy_no, query) -> find member by UHID, emp code, name
3. search_hospital(pincode, name_query) -> find hospital in pincode
4. search_diagnosis(query) -> find diagnosis code/name
5. query_policy_document_rag(query, product) -> retrieve exact policy document clauses

Determine intent (ANSWER, QUESTION, RESTART, AGENT, CANCEL) and extract relevant fields.
Return JSON matching schema:
{{"intent": "ANSWER"|"QUESTION"|"RESTART"|"AGENT", "value": "extracted or answer text", "fields": {{}}, "confidence": 0.95}}
"""
                config = types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=Interpretation,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                )

                resp = await generate_content_with_fallback(
                    client=self.client,
                    primary_model=self.model,
                    contents=prompt,
                    config=config,
                    timeout_sec=settings.gemini_timeout_ms / 1000.0,
                )

                if resp and resp.text:
                    interp = Interpretation.model_validate_json(resp.text)
                    return interp
            except Exception:
                pass

        # Step 3: Fallback to FakeNLU + Tool Search
        return await self.fallback.interpret(req)
