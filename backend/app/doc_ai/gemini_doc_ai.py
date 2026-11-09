"""Google Gemini Multimodal Document AI implementation using google-genai SDK."""

import asyncio
import mimetypes
import time
from datetime import date
from pathlib import Path
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.gemini_utils import generate_content_with_fallback
from app.doc_ai.doc_ai import DocExtractionResult, ExtractedField
from app.doc_ai.fake_doc_ai import FakeDocAI
from app.doc_ai.validator import validate_extraction


class GeminiDocSchema(BaseModel):
    """Pydantic schema for structured output from Gemini multimodal call."""

    detected_type: str = Field(description="Detected document type: DISCHARGE_SUMMARY, HOSPITAL_BILL, CLAIM_FORM, PRESCRIPTION, ID_PROOF, OTHER")
    patient_name: str | None = Field(default=None, description="Patient name extracted from document")
    patient_name_evidence: str | None = Field(default=None, description="Verbatim quote/evidence text for patient name")
    doa: str | None = Field(default=None, description="Date of admission in YYYY-MM-DD format if available")
    doa_evidence: str | None = Field(default=None, description="Verbatim quote/evidence text for admission date")
    total_amount: float | None = Field(default=None, description="Total bill amount in INR if applicable")
    hospital_name: str | None = Field(default=None, description="Hospital or clinic name")


class GeminiDocAI:
    """Gemini multimodal document extraction service."""

    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.fallback = FakeDocAI()

    async def extract_and_validate(
        self,
        file_path: str,
        doc_code: str,
        expected_patient_name: str | None = None,
        expected_doa: str | date | None = None,
        original_name: str | None = None,
    ) -> DocExtractionResult:
        """Extract fields using Gemini Multimodal API or fallback to FakeDocAI on failure/disable."""
        if not settings.doc_ai_enabled or not self.client or not self.api_key:
            return await self.fallback.extract_and_validate(
                file_path=file_path,
                doc_code=doc_code,
                expected_patient_name=expected_patient_name,
                expected_doa=expected_doa,
                original_name=original_name,
            )

        start_t = time.time()
        path = Path(file_path)
        if not path.exists():
            return await self.fallback.extract_and_validate(
                file_path=file_path,
                doc_code=doc_code,
                expected_patient_name=expected_patient_name,
                expected_doa=expected_doa,
                original_name=original_name,
            )

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/pdf" if path.suffix.lower() == ".pdf" else "image/jpeg"

        try:
            content_bytes = path.read_bytes()
            doc_part = types.Part.from_bytes(data=content_bytes, mime_type=mime_type)

            prompt = f"""Analyze this health insurance document carefully.
Expected document code requested from user: {doc_code}
Expected patient name: {expected_patient_name or 'Unknown'}
Expected date of admission: {expected_doa or 'Unknown'}

Extract:
1. Document type (DISCHARGE_SUMMARY, HOSPITAL_BILL, CLAIM_FORM, PRESCRIPTION, ID_PROOF, OTHER)
2. Patient full name and verbatim evidence text
3. Date of admission (DOA) and verbatim evidence text
4. Hospital name and total bill amount if present."""

            config = types.GenerateContentConfig(
                system_instruction="You are an expert medical document AI parser. Return JSON matching schema strictly.",
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=GeminiDocSchema,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )

            resp = await generate_content_with_fallback(
                client=self.client,
                primary_model=self.model,
                contents=[doc_part, prompt],
                config=config,
                timeout_sec=settings.doc_ai_timeout_ms / 1000.0,
            )

            if resp and resp.text:
                raw_data = GeminiDocSchema.model_validate_json(resp.text)
                fields: dict[str, ExtractedField] = {}
                if raw_data.patient_name:
                    fields["patient_name"] = ExtractedField(
                        value=raw_data.patient_name,
                        evidence=raw_data.patient_name_evidence,
                        confidence=0.95,
                    )
                if raw_data.doa:
                    fields["doa"] = ExtractedField(
                        value=raw_data.doa,
                        evidence=raw_data.doa_evidence,
                        confidence=0.92,
                    )
                if raw_data.total_amount:
                    fields["total_amount"] = ExtractedField(value=raw_data.total_amount, confidence=0.98)
                if raw_data.hospital_name:
                    fields["hospital_name"] = ExtractedField(value=raw_data.hospital_name, confidence=0.95)

                res = validate_extraction(
                    doc_code=doc_code,
                    detected_type=raw_data.detected_type,
                    extracted_fields=fields,
                    expected_patient_name=expected_patient_name,
                    expected_doa=expected_doa,
                )
                res.model = self.model
                res.latency_ms = int((time.time() - start_t) * 1000)
                return res

        except Exception:
            # Fallback cleanly on Gemini 503/Quota/Timeout errors
            pass

        return await self.fallback.extract_and_validate(
            file_path=file_path,
            doc_code=doc_code,
            expected_patient_name=expected_patient_name,
            expected_doa=expected_doa,
            original_name=original_name,
        )
