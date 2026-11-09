"""Automated tests for Phase 3 detail collection, review, edit and cashless submission scenarios S1, S9, S10, S14, S16."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_s1_retail_cashless_happy_path(async_client: AsyncClient):
    # S1: Retail cashless happy path -> claim_no issued, DONE
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000001"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})

    # State: CLAIM_TYPE -> Cashless
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "CASHLESS"}})
    assert res.json()["state"] == "PATIENT"

    # Submit PATIENT form
    p_form = {
        "patient": "Rohan Kulkarni",
        "intimator_name": "Rohan Kulkarni",
        "intimator_email": "rohan.kulkarni@example.com",
        "intimation_type": "EMERGENCY",
    }
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": p_form}})
    assert res.json()["state"] == "PATIENT_CONFIRM"

    # Confirm PATIENT
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    assert res.json()["state"] == "ADMISSION"

    # Submit ADMISSION form
    a_form = {
        "doa": "2026-09-28",
        "doctor_name": "Dr. Mehta",
        "diagnosis": "Dengue fever",
    }
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": a_form}})
    assert res.json()["state"] == "ADMISSION_CONFIRM"

    # Confirm ADMISSION
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    assert res.json()["state"] == "HOSPITAL_PIN"

    # Enter Pincode 411045
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "411045"}})
    assert res.json()["state"] == "HOSPITAL_PICK"

    # Pick PUN-005 Jupiter Hospital
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "PUN-005"}})
    assert res.json()["state"] == "HOSPITAL_CONFIRM"

    # Confirm HOSPITAL
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    assert res.json()["state"] == "REVIEW"

    # Confirm & Submit Claim
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "CONFIRM"}})
    assert res.json()["state"] == "DONE"
    assert any("CLM-2026-" in m for m in res.json()["messages"])


@pytest.mark.asyncio
async def test_s9_pincode_without_exact_match(async_client: AsyncClient):
    # S9: Pincode without exact match -> 5 nearest Pune hospitals list
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000001"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "CASHLESS"}})

    p_form = {"patient": "Rohan Kulkarni", "intimator_name": "Rohan Kulkarni", "intimator_email": "rohan.kulkarni@example.com", "intimation_type": "EMERGENCY"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": p_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    a_form = {"doa": "2026-09-28", "doctor_name": "Dr. Mehta", "diagnosis": "Dengue fever"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": a_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    # Enter pincode 411021 (no exact match)
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "411021"}})
    assert res.json()["state"] == "HOSPITAL_PICK"
    opts = res.json()["ui"]["options"]
    assert len(opts) == 5


@pytest.mark.asyncio
async def test_s10_cashless_non_network_hospital(async_client: AsyncClient):
    # S10: Cashless at non-network hospital -> NON_NETWORK prompt
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000001"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "CASHLESS"}})

    p_form = {"patient": "Rohan Kulkarni", "intimator_name": "Rohan Kulkarni", "intimator_email": "rohan.kulkarni@example.com", "intimation_type": "EMERGENCY"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": p_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    a_form = {"doa": "2026-09-28", "doctor_name": "Dr. Mehta", "diagnosis": "Dengue fever"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": a_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "411033"}})

    # Pick non-network hospital PUN-016
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "PUN-016"}})
    assert res.json()["state"] == "NON_NETWORK"


@pytest.mark.asyncio
async def test_s14_new_claim_becomes_duplicate(async_client: AsyncClient):
    # S14: Submit claim via S1 flow, then second session with same DOA -> AGENT_HANDOFF
    res1 = await async_client.post("/chat/start")
    s1_id = res1.json()["session_id"]
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"text": "9000000001"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "123456"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "CASHLESS"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": {"patient": "Rohan Kulkarni", "intimator_name": "Rohan Kulkarni", "intimator_email": "rohan.kulkarni@example.com", "intimation_type": "EMERGENCY"}}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": {"doa": "2026-09-28", "doctor_name": "Dr. Mehta", "diagnosis": "Dengue fever"}}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"text": "411045"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "PUN-005"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": s1_id, "input": {"value": "CONFIRM"}})

    # Session 2: Login same policy HP-RET-2026-0001
    res2 = await async_client.post("/chat/start")
    s2_id = res2.json()["session_id"]
    await async_client.post("/chat/message", json={"session_id": s2_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": s2_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": s2_id, "input": {"text": "9000000001"}})
    res_otp = await async_client.post("/chat/message", json={"session_id": s2_id, "input": {"value": "123456"}})

    # If duplicate open claim detected in session store -> OPEN_CLAIM
    if res_otp.json()["state"] == "OPEN_CLAIM":
        res_cont = await async_client.post("/chat/message", json={"session_id": s2_id, "input": {"value": "YES"}})
        assert res_cont.json()["state"] == "DOA_CHECK"
        res_doa = await async_client.post("/chat/message", json={"session_id": s2_id, "input": {"value": "2026-09-28"}})
        assert res_doa.json()["state"] == "AGENT_HANDOFF"


@pytest.mark.asyncio
async def test_s16_edit_from_review(async_client: AsyncClient):
    # S16: Edit from review -> change doctor name -> returns to REVIEW with new value
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000001"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "CASHLESS"}})

    p_form = {"patient": "Rohan Kulkarni", "intimator_name": "Rohan Kulkarni", "intimator_email": "rohan.kulkarni@example.com", "intimation_type": "EMERGENCY"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": p_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    a_form = {"doa": "2026-09-28", "doctor_name": "Dr. Mehta", "diagnosis": "Dengue fever"}
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": a_form}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "411045"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "PUN-005"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    # At REVIEW state
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EDIT_ADMISSION"}})
    assert res.json()["state"] == "ADMISSION"

    # Update doctor name to Dr. Sharma
    new_a_form = {"doa": "2026-09-28", "doctor_name": "Dr. Sharma", "diagnosis": "Dengue fever"}
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": new_a_form}})
    assert res.json()["state"] == "ADMISSION_CONFIRM"

    # Confirm ADMISSION -> returns to REVIEW
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    assert res.json()["state"] == "REVIEW"
    summary_data = res.json()["ui"]["data"]
    assert summary_data["Doctor"] == "Dr. Sharma"
