"""Document AI interfaces and domain models for document extraction & verification."""

from datetime import date
from typing import Any, Protocol
from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    """Single extracted field from document."""

    value: Any = None
    evidence: str | None = None
    confidence: float = 1.0


class ExtractionCheck(BaseModel):
    """Validation check result for an extracted field."""

    code: str  # DOC_TYPE_MATCH, PATIENT_NAME_MATCH, DOA_MATCH
    status: str  # OK, WARNING, ERROR
    label: str
    message: str


class DocExtractionResult(BaseModel):
    """Extraction and verification result for an uploaded document."""

    doc_code: str
    detected_type: str | None = None
    status: str = "OK"  # OK, MISMATCH, WRONG_TYPE, EXTRACTION_FAILED, SKIPPED
    fields: dict[str, ExtractedField] = Field(default_factory=dict)
    checks: list[ExtractionCheck] = Field(default_factory=list)
    mismatches: list[str] = Field(default_factory=list)
    user_accepted: bool | None = None
    model: str = "fake-doc-ai"
    latency_ms: int = 0


class DocumentAIExtractor(Protocol):
    """Protocol for Document AI extraction services."""

    async def extract_and_validate(
        self,
        file_path: str,
        doc_code: str,
        expected_patient_name: str | None = None,
        expected_doa: str | date | None = None,
        original_name: str | None = None,
    ) -> DocExtractionResult:
        """Extract fields from file and validate against expected values."""
        ...
