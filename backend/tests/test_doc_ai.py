"""Unit and integration tests for Phase 7 Document AI module."""

import os
from pathlib import Path
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.doc_ai.fake_doc_ai import FakeDocAI
from app.doc_ai.gemini_doc_ai import GeminiDocAI
from app.main import app
from scripts.generate_sample_pdfs import generate_all_samples

client = TestClient(app)


@pytest.fixture(scope="module")
def sample_pdfs():
    """Ensure sample PDFs exist before running tests."""
    out_dir = Path("./sample_docs")
    return generate_all_samples(out_dir)


@pytest.mark.asyncio
async def test_fake_doc_ai_extraction_ok(sample_pdfs):
    """Test standard valid document extraction with matching patient and DOA."""
    doc_ai = FakeDocAI()
    pdf_path = str(sample_pdfs["discharge_summary"])
    res = await doc_ai.extract_and_validate(
        file_path=pdf_path,
        doc_code="DISCHARGE_SUMMARY",
        expected_patient_name="Rahul Sharma",
        expected_doa="2026-09-20",
    )

    assert res.status == "OK"
    assert res.detected_type == "DISCHARGE_SUMMARY"
    assert res.fields["patient_name"].value == "Rahul Sharma"
    assert res.fields["doa"].value == "2026-09-20"
    assert len(res.mismatches) == 0


@pytest.mark.asyncio
async def test_patient_name_mismatch_detection(sample_pdfs):
    """Test detection of patient name mismatch against policy member."""
    doc_ai = FakeDocAI()
    pdf_path = str(sample_pdfs["mismatch_patient"])
    res = await doc_ai.extract_and_validate(
        file_path=pdf_path,
        doc_code="DISCHARGE_SUMMARY",
        expected_patient_name="Rahul Sharma",
        expected_doa="2026-09-20",
    )

    assert res.status == "MISMATCH"
    assert len(res.mismatches) > 0
    assert any("Patient name" in m for m in res.mismatches)


@pytest.mark.asyncio
async def test_doa_mismatch_detection(sample_pdfs):
    """Test detection of admission date mismatch against intimation DOA."""
    doc_ai = FakeDocAI()
    pdf_path = str(sample_pdfs["mismatch_doa"])
    res = await doc_ai.extract_and_validate(
        file_path=pdf_path,
        doc_code="DISCHARGE_SUMMARY",
        expected_patient_name="Rahul Sharma",
        expected_doa="2026-09-20",
    )

    assert res.status == "MISMATCH"
    assert len(res.mismatches) > 0
    assert any("Admission date" in m for m in res.mismatches)


@pytest.mark.asyncio
async def test_wrong_doc_type_detection(sample_pdfs):
    """Test detection of wrong document type (e.g. prescription uploaded as discharge summary)."""
    doc_ai = FakeDocAI()
    pdf_path = str(sample_pdfs["prescription"])
    res = await doc_ai.extract_and_validate(
        file_path=pdf_path,
        doc_code="DISCHARGE_SUMMARY",
        expected_patient_name="Rahul Sharma",
        expected_doa="2026-09-20",
    )

    assert res.status == "WRONG_TYPE"
    assert res.detected_type == "PRESCRIPTION"
    assert any("Document type mismatch" in m for m in res.mismatches)


@pytest.mark.asyncio
async def test_upload_doc_ai_mismatch_and_accept_flow(async_client: AsyncClient, sample_pdfs):
    """Scenario S17: End-to-end test of Document AI mismatch card & user accept flow."""
    # 1. Start session
    resp = await async_client.post("/chat/start")
    sid = resp.json()["session_id"]

    # 2. Consent YES
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "YES"}})
    # 3. Auth via RMN
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "RMN"}})
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"text": "9000000011"}})
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "123456"}})
    # 4. Select Reimbursement
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "REIMBURSEMENT"}})
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "NO"}})  # continue here

    # 5. Fill patient block
    resp = await async_client.post(
        "/chat/message",
        json={
            "session_id": sid,
            "input": {
                "value": {
                    "patient": "Neha Shah",
                    "intimator_name": "Neha Shah",
                    "intimator_email": "neha.shah@example.com",
                    "intimation_type": "EMERGENCY",
                }
            },
        },
    )
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "YES"}})

    # 6. Fill admission block
    resp = await async_client.post(
        "/chat/message",
        json={
            "session_id": sid,
            "input": {
                "value": {
                    "doa": "2026-09-20",
                    "doctor_name": "Dr. Verma",
                    "diagnosis": "Acute Appendicitis",
                }
            },
        },
    )
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "YES"}})

    # 7. Fill hospital block
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"text": "400050"}})
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "MUM-002"}})
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "YES"}})

    # 8. Submit claim
    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "CONFIRM"}})
    assert resp.json()["state"] == "DOC_CHOICE"

    resp = await async_client.post("/chat/message", json={"session_id": sid, "input": {"value": "YES"}})
    assert resp.json()["state"] == "DOC_UPLOAD"

    # 9. Upload mismatch_patient.pdf
    with open(sample_pdfs["mismatch_patient"], "rb") as f:
        up_resp = await async_client.post(
            "/chat/upload",
            data={"session_id": sid, "doc_code": "DISCHARGE_SUMMARY"},
            files={"file": ("mismatch_patient.pdf", f, "application/pdf")},
        )

    data = up_resp.json()
    assert data["ui"]["type"] == "extraction"
    assert data["ui"]["data"]["status"] == "MISMATCH"
    assert len(data["ui"]["data"]["mismatches"]) > 0

    # 10. User clicks ACCEPT_EXTRACTION
    acc_resp = await async_client.post(
        "/chat/message",
        json={"session_id": sid, "input": {"value": "ACCEPT_EXTRACTION"}},
    )
    assert acc_resp.status_code == 200
    assert "Document accepted" in acc_resp.json()["messages"][0]



@pytest.mark.gemini
@pytest.mark.asyncio
async def test_gemini_doc_ai_live(sample_pdfs):
    """Live test calling Google Gemini Multimodal API if key configured."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    doc_ai = GeminiDocAI()
    pdf_path = str(sample_pdfs["discharge_summary"])
    res = await doc_ai.extract_and_validate(
        file_path=pdf_path,
        doc_code="DISCHARGE_SUMMARY",
        expected_patient_name="Rahul Sharma",
        expected_doa="2026-09-20",
    )

    assert res.doc_code == "DISCHARGE_SUMMARY"
    assert res.status in ("OK", "MISMATCH")
