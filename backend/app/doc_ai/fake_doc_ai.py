"""Fake deterministic Document AI extractor for testing and fallback mode."""

import os
import re
import time
from datetime import date
from pathlib import Path
from app.doc_ai.doc_ai import DocExtractionResult, ExtractedField
from app.doc_ai.validator import validate_extraction


class FakeDocAI:
    """Fake Document AI extractor providing deterministic extractions for unit tests."""

    async def extract_and_validate(
        self,
        file_path: str,
        doc_code: str,
        expected_patient_name: str | None = None,
        expected_doa: str | date | None = None,
        original_name: str | None = None,
    ) -> DocExtractionResult:
        """Deterministically extract fields from file and run validation checks."""
        start_t = time.time()
        filename = (original_name or Path(file_path).name).lower()

        # inspect file content for text hints if text file or simple PDF
        file_text = ""
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    # extract readable ASCII sequences
                    strings = re.findall(rb"[\x20-\x7e]{4,}", content)
                    file_text = " ".join([s.decode("latin1", errors="ignore") for s in strings])
            except Exception:
                pass

        # check for explicit override keywords in path or file text
        detected_type = doc_code.upper()
        if "prescription" in filename or "prescription" in file_text.lower():
            detected_type = "PRESCRIPTION"
        elif "wrong_type" in filename:
            detected_type = "PRESCRIPTION" if doc_code.upper() != "PRESCRIPTION" else "OTHER"

        # extract patient name
        patient_name = expected_patient_name or "Rahul Sharma"
        if "mismatch_patient" in filename or "mismatch" in filename or "wrong_patient" in filename or "john doe" in file_text.lower():
            patient_name = "John Doe"
        elif "patient:" in file_text.lower():
            m = re.search(r"patient:\s*([A-Za-z\s]+)", file_text, re.IGNORECASE)
            if m:
                patient_name = m.group(1).strip()

        # extract doa
        doa_val = str(expected_doa) if expected_doa else "2026-09-20"
        if "mismatch_doa" in filename or "wrong_doa" in filename:
            doa_val = "2026-01-01"
        elif "doa:" in file_text.lower() or "admission date:" in file_text.lower():
            m = re.search(r"(?:doa|admission date):\s*([\d\-/]+)", file_text, re.IGNORECASE)
            if m:
                doa_val = m.group(1).strip()

        fields: dict[str, ExtractedField] = {
            "patient_name": ExtractedField(value=patient_name, evidence=f"Found patient '{patient_name}' in document", confidence=0.95),
            "doa": ExtractedField(value=doa_val, evidence=f"Found DOA '{doa_val}' in document", confidence=0.92),
        }

        if doc_code.upper() == "HOSPITAL_BILL":
            fields["total_amount"] = ExtractedField(value=45000, evidence="Total Bill Amount: Rs. 45,000", confidence=0.98)
        elif doc_code.upper() == "DISCHARGE_SUMMARY":
            fields["hospital_name"] = ExtractedField(value="Ruby Hall Clinic", evidence="Ruby Hall Clinic Pune", confidence=0.99)

        result = validate_extraction(
            doc_code=doc_code,
            detected_type=detected_type,
            extracted_fields=fields,
            expected_patient_name=expected_patient_name,
            expected_doa=expected_doa,
        )

        result.model = "fake-doc-ai"
        result.latency_ms = int((time.time() - start_t) * 1000)
        return result
