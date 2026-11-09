"""Google Gemini NLU implementation using official google-genai SDK."""

import asyncio
from pathlib import Path
from google import genai
from google.genai import types
from pydantic import ValidationError
from app.core.config import settings
from app.core.gemini_utils import generate_content_with_fallback
from app.llm.fake_nlu import FakeNLU
from app.llm.nlu import InterpretRequest, Interpretation

# load interpret prompt
_PROMPT_PATH = Path(__file__).parent / "prompts" / "interpret.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


class GeminiNLU:
    """Gemini API NLU interpreter."""

    def __init__(self) -> None:
        # initialize Gemini client
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.fallback = FakeNLU()

    async def interpret(self, req: InterpretRequest) -> Interpretation:
        # interpret using Gemini API or fallback
        if not settings.llm_enabled or not self.client or not self.api_key:
            return await self.fallback.interpret(req)

        prompt_body = f"""Current step: {req.state}
Today's date: {req.today.isoformat()}
Allowed values: {req.allowed_values}
Fields to extract: {req.fields}
Insured members: {[m.model_dump() for m in req.members]}
Diagnoses list: {[d.model_dump() for d in req.diagnoses]}
FAQ items: {[f.model_dump() for f in req.faq]}

<user_input>
{req.text}
</user_input>"""

        config = types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            temperature=0,
            response_mime_type="application/json",
            response_schema=Interpretation,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        timeout_sec = settings.gemini_timeout_ms / 1000.0

        try:
            resp = await generate_content_with_fallback(
                client=self.client,
                primary_model=self.model,
                contents=prompt_body,
                config=config,
                timeout_sec=timeout_sec,
            )

            if resp and resp.text:
                return Interpretation.model_validate_json(resp.text)
        except Exception:
            # 1 retry with stricter prompt
            try:
                stricter_contents = f"{prompt_body}\n\nStricter instruction: Return ONLY valid JSON matching schema. Do not invent values."
                resp = await generate_content_with_fallback(
                    client=self.client,
                    primary_model=self.model,
                    contents=stricter_contents,
                    config=config,
                    timeout_sec=timeout_sec,
                )
                if resp and resp.text:
                    return Interpretation.model_validate_json(resp.text)
            except Exception:
                pass

        # fallback to FakeNLU on error / timeout
        return await self.fallback.interpret(req)
