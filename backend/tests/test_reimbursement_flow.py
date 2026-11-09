"""Automated tests for Phase 4 reimbursement flow scenarios S11, S12, S13."""

import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_s11_reimbursement_upload_now(async_client: AsyncClient):
    # S11: Reimbursement, upload all mandatory docs now -> SR COMPLETE, DONE
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000011"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})

    # State: CLAIM_TYPE -> Reimbursement
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "REIMBURSEMENT"}})
    assert res.json()["state"] == "SELF_I_OFFER"

    # Self-I Offer -> No (continue here)
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "NO"}})
    assert res.json()["state"] == "PATIENT"

    # PATIENT block
    p_form = {"patient": "Neha Shah", "intimator_name": "Neha Shah", "intimator_email": "neha.shah@example.com", "intimation_type": "PLANNED"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": p_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    # ADMISSION block
    a_form = {"doa": "2026-09-24", "doctor_name": "Dr. Deshmukh", "diagnosis": "Acute appendicitis"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": a_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    # HOSPITAL block
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "400050"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "MUM-002"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    # REVIEW -> Submit
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "CONFIRM"}})
    assert res.json()["state"] == "DOC_CHOICE"

    # DOC_CHOICE -> Upload Now
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    assert res.json()["state"] == "DOC_UPLOAD"

    # Upload all 6 mandatory docs
    mandatory_codes = ["CLAIM_FORM", "DISCHARGE", "FINAL_BILL", "RECEIPTS", "BANK", "ID_PROOF"]
    pdf_bytes = b"%PDF-1.4 test document content %EOF"

    for code in mandatory_codes:
        files = {"file": (f"{code}.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        data = {"session_id": session_id, "doc_code": code}
        res = await async_client.post("/chat/upload", data=data, files=files)

    # After last mandatory upload -> DONE
    assert res.json()["state"] == "DONE"


@pytest.mark.asyncio
async def test_s12_reimbursement_upload_later(async_client: AsyncClient):
    # S12: Reimbursement, choose upload later -> SR_PENDING with SR number
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000011"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "REIMBURSEMENT"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "NO"}})

    p_form = {"patient": "Neha Shah", "intimator_name": "Neha Shah", "intimator_email": "neha.shah@example.com", "intimation_type": "PLANNED"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": p_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    a_form = {"doa": "2026-09-24", "doctor_name": "Dr. Deshmukh", "diagnosis": "Acute appendicitis"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": a_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "400050"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "MUM-002"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "CONFIRM"}})

    # DOC_CHOICE -> Upload Later
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "NO"}})
    assert res.json()["state"] == "SR_PENDING"
    assert any("SR-" in m for m in res.json()["messages"])


@pytest.mark.asyncio
async def test_s13_invalid_file_upload(async_client: AsyncClient):
    # S13: Invalid file (.exe or > 5MB) -> validation error, stays DOC_UPLOAD
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000011"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "REIMBURSEMENT"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "NO"}})

    p_form = {"patient": "Neha Shah", "intimator_name": "Neha Shah", "intimator_email": "neha.shah@example.com", "intimation_type": "PLANNED"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": p_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    a_form = {"doa": "2026-09-24", "doctor_name": "Dr. Deshmukh", "diagnosis": "Acute appendicitis"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": a_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "400050"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "MUM-002"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "CONFIRM"}})

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    # Upload invalid file type (.exe)
    exe_bytes = b"MZ\x90\x00\x03\x00\x00\x00"
    files = {"file": ("malicious.exe", io.BytesIO(exe_bytes), "application/x-msdownload")}
    data = {"session_id": session_id, "doc_code": "CLAIM_FORM"}

    res = await async_client.post("/chat/upload", data=data, files=files)
    assert res.json()["state"] == "DOC_UPLOAD"
    assert res.json()["error"] is not None
    assert "Invalid file type" in res.json()["error"]["message"]
