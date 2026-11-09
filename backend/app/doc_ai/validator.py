"""Validation helper routines for Document AI extractions."""

import re
from datetime import date, datetime
from app.doc_ai.doc_ai import DocExtractionResult, ExtractedField, ExtractionCheck


def normalize_name(name: str) -> str:
    """Normalize patient name by removing honorifics and non-alphanumeric chars."""
    if not name:
        return ""
    clean = name.lower()
    clean = re.sub(r"\b(mr|mrs|ms|dr|master|shri|smt)\b\.?", "", clean)
    clean = re.sub(r"[^\w\s]", " ", clean)
    return " ".join(clean.split())


def names_match(name1: str, name2: str) -> bool:
    """Check if two names match with flexible token overlap."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    if not n1 or not n2:
        return True
    if n1 == n2:
        return True
    tokens1 = set(n1.split())
    tokens2 = set(n2.split())
    # match if major tokens overlap
    if tokens1.issubset(tokens2) or tokens2.issubset(tokens1):
        return True
    common = tokens1.intersection(tokens2)
    return len(common) >= min(len(tokens1), len(tokens2))


def parse_date(date_str: str | date | None) -> str | None:
    """Parse various date formats into YYYY-MM-DD string."""
    if not date_str:
        return None
    if isinstance(date_str, date):
        return date_str.isoformat()
    s = str(date_str).strip()
    # ISO YYYY-MM-DD
    m = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # DD/MM/YYYY or DD-MM-YYYY
    m = re.search(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", s)
    if m:
        return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return s


def validate_extraction(
    doc_code: str,
    detected_type: str | None,
    extracted_fields: dict[str, ExtractedField],
    expected_patient_name: str | None = None,
    expected_doa: str | date | None = None,
) -> DocExtractionResult:
    """Run verification checks on extracted document fields against expected claim data."""
    checks: list[ExtractionCheck] = []
    mismatches: list[str] = []
    status = "OK"

    # 1. Document type check
    doc_code_norm = doc_code.upper().strip()
    det_norm = (detected_type or doc_code_norm).upper().strip()

    known_types = {"DISCHARGE_SUMMARY", "HOSPITAL_BILL", "CLAIM_FORM", "ID_PROOF", "PRESCRIPTION", "OTHER"}
    if det_norm in known_types and det_norm != doc_code_norm and det_norm != "OTHER":
        checks.append(
            ExtractionCheck(
                code="DOC_TYPE_MATCH",
                status="WARNING",
                label="Document Type",
                message=f"Uploaded file appears to be a {det_norm.replace('_', ' ').title()}, expected {doc_code_norm.replace('_', ' ').title()}.",
            )
        )
        mismatches.append(f"Document type mismatch: Detected {det_norm}, expected {doc_code_norm}")
        status = "WRONG_TYPE"
    else:
        checks.append(
            ExtractionCheck(
                code="DOC_TYPE_MATCH",
                status="OK",
                label="Document Type",
                message=f"Verified as {doc_code_norm.replace('_', ' ').title()}.",
            )
        )

    # 2. Patient name check
    ext_name_field = extracted_fields.get("patient_name")
    if ext_name_field and ext_name_field.value and expected_patient_name:
        ext_name = str(ext_name_field.value)
        if names_match(ext_name, expected_patient_name):
            checks.append(
                ExtractionCheck(
                    code="PATIENT_NAME_MATCH",
                    status="OK",
                    label="Patient Name",
                    message=f"Patient name verified ('{ext_name}').",
                )
            )
        else:
            checks.append(
                ExtractionCheck(
                    code="PATIENT_NAME_MATCH",
                    status="WARNING",
                    label="Patient Name",
                    message=f"Name mismatch: Extracted '{ext_name}', expected '{expected_patient_name}'.",
                )
            )
            mismatches.append(f"Patient name in document ('{ext_name}') does not match policy member ('{expected_patient_name}')")
            if status == "OK":
                status = "MISMATCH"

    # 3. DOA check
    ext_doa_field = extracted_fields.get("doa")
    if ext_doa_field and ext_doa_field.value and expected_doa:
        ext_doa_parsed = parse_date(str(ext_doa_field.value))
        exp_doa_parsed = parse_date(expected_doa)
        if ext_doa_parsed and exp_doa_parsed and ext_doa_parsed == exp_doa_parsed:
            checks.append(
                ExtractionCheck(
                    code="DOA_MATCH",
                    status="OK",
                    label="Admission Date",
                    message=f"Date of admission verified ({ext_doa_parsed}).",
                )
            )
        else:
            checks.append(
                ExtractionCheck(
                    code="DOA_MATCH",
                    status="WARNING",
                    label="Admission Date",
                    message=f"DOA mismatch: Extracted '{ext_doa_parsed or ext_doa_field.value}', expected '{exp_doa_parsed}'.",
                )
            )
            mismatches.append(f"Admission date in document ({ext_doa_parsed or ext_doa_field.value}) does not match intimation DOA ({exp_doa_parsed})")
            if status == "OK":
                status = "MISMATCH"

    return DocExtractionResult(
        doc_code=doc_code_norm,
        detected_type=det_norm,
        status=status,
        fields=extracted_fields,
        checks=checks,
        mismatches=mismatches,
    )
