"""Automated tests for Phase 2 authentication and duplicate claim scenarios S2-S8, S15."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_language_choice_english_and_hindi(async_client: AsyncClient):
    # Test EN language selection
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    assert res.json()["state"] == "LANGUAGE_CHOICE"
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    assert res.json()["state"] == "AUTH_CHOICE"

    # Test HI language selection
    res = await async_client.post("/chat/start")
    session_id_hi = res.json()["session_id"]
    res = await async_client.post("/chat/message", json={"session_id": session_id_hi, "input": {"value": "YES"}})
    assert res.json()["state"] == "LANGUAGE_CHOICE"
    res = await async_client.post("/chat/message", json={"session_id": session_id_hi, "input": {"value": "HI"}})
    assert res.json()["state"] == "AUTH_CHOICE"


@pytest.mark.asyncio
async def test_s2_group_policy_via_emp_code(async_client: AsyncClient):
    # S2: Group policy via Emp code
    res = await async_client.post("/chat/start")
    assert res.status_code == 200
    session_id = res.json()["session_id"]

    # CONSENT -> I agree
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"value": "YES"}},
    )
    assert res.json()["state"] == "LANGUAGE_CHOICE"

    # LANGUAGE_CHOICE -> EN
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"value": "EN"}},
    )
    assert res.json()["state"] == "AUTH_CHOICE"

    # AUTH_CHOICE -> Policy Number
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"value": "POLICY"}},
    )
    assert res.json()["state"] == "POLICY_INPUT"

    # Enter Group Policy HP-GRP-2026-0001
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "HP-GRP-2026-0001"}},
    )
    assert res.json()["state"] == "MEMBER_VERIFY"

    # Enter Employee Code EMP10001
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "EMP10001"}},
    )
    # Verified -> active policy -> no open claims -> CLAIM_TYPE
    assert res.json()["state"] == "CLAIM_TYPE"


@pytest.mark.asyncio
async def test_s3_multiple_policies_one_rmn(async_client: AsyncClient):
    # S3: Multiple policies on one RMN
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})

    # Enter RMN with 2 policies
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "9000000003"}},
    )
    assert res.json()["state"] == "OTP_INPUT"

    # Enter correct OTP
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"value": "123456"}},
    )
    assert res.json()["state"] == "SELECT_POLICY"
    options = res.json()["ui"]["options"]
    assert len(options) == 2


@pytest.mark.asyncio
async def test_s4_open_claim_different_doa(async_client: AsyncClient):
    # S4: Open claim, different DOA -> proceeds to CLAIM_TYPE
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000004"}})
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})

    # Policy HP-RET-2026-0004 has open claim CLM-2026-000010 (DOA 2026-09-20)
    assert res.json()["state"] == "OPEN_CLAIM"

    # Continue Yes
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"value": "YES"}},
    )
    assert res.json()["state"] == "DOA_CHECK"

    # Enter different DOA 2026-09-25
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"value": "2026-09-25"}},
    )
    assert res.json()["state"] == "CLAIM_TYPE"


@pytest.mark.asyncio
async def test_s5_open_claim_same_doa(async_client: AsyncClient):
    # S5: Open claim, same DOA -> AGENT_HANDOFF
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000004"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    # Enter same DOA 2026-09-20
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"value": "2026-09-20"}},
    )
    assert res.json()["state"] == "AGENT_HANDOFF"


@pytest.mark.asyncio
async def test_s6_lapsed_policy(async_client: AsyncClient):
    # S6: Lapsed policy -> END_INACTIVE
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000006"}})
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})

    assert res.json()["state"] == "END_INACTIVE"


@pytest.mark.asyncio
async def test_s7_unregistered_mobile(async_client: AsyncClient):
    # S7: Unregistered mobile -> error message, stays RMN_INPUT
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})

    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "9999999999"}},
    )
    assert res.json()["state"] == "RMN_INPUT"
    assert res.json()["error"] is not None


@pytest.mark.asyncio
async def test_s8_wrong_otp_3_times(async_client: AsyncClient):
    # S8: Wrong OTP 3 times -> LOCKED
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000001"}})

    # Wrong OTP 1
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "111111"}})
    assert res.json()["state"] == "OTP_INPUT"

    # Wrong OTP 2
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "111111"}})
    assert res.json()["state"] == "OTP_INPUT"

    # Wrong OTP 3 -> LOCKED
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "111111"}})
    assert res.json()["state"] == "LOCKED"


@pytest.mark.asyncio
async def test_s15_closed_claim_ignored(async_client: AsyncClient):
    # S15: Closed/settled claim ignored -> proceeds to CLAIM_TYPE
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "EN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000005"}})
    res = await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})

    # Policy HP-RET-2026-0005 has a SETTLED claim, so no open claim -> CLAIM_TYPE directly
    assert res.json()["state"] == "CLAIM_TYPE"
