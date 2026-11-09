"""Automated tests for Phase 6 Gemini NLU integration and free-text scenarios S18-S24."""

from datetime import date, timedelta
import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.llm.gemini_nlu import GeminiNLU
from app.llm.nlu import InterpretRequest


@pytest.mark.asyncio
async def test_s18_freetext_claim_type(async_client: AsyncClient):
    # S18: Free-text claim type -> acts as clicking Cashless button
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]

    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000001"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "123456"}})

    # Type free-text at CLAIM_TYPE
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "it's a cashless one"}},
    )
    assert res.json()["state"] == "PATIENT"


@pytest.mark.asyncio
async def test_s19_freetext_extraction_admission(async_client: AsyncClient):
    # S19: Free-text entity extraction at ADMISSION -> pre-fills form data
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

    # At ADMISSION, send free text
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "admitted yesterday by Dr Mehta for dengue"}},
    )
    assert res.json()["state"] == "ADMISSION"
    fields = res.json()["ui"]["fields"]
    doctor_field = next((f for f in fields if f["name"] == "doctor_name"), None)
    assert doctor_field is not None
    assert "Mehta" in str(doctor_field["value"])


@pytest.mark.asyncio
async def test_s20_faq_mid_flow(async_client: AsyncClient):
    # S20: FAQ mid-flow -> shows answer + disclaimer, step state unchanged
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

    # At HOSPITAL_PIN, ask FAQ
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "what is a network hospital?"}},
    )
    assert res.json()["state"] == "HOSPITAL_PIN"
    assert any("tie-up" in m for m in res.json()["messages"])
    assert res.json()["ui"]["disclaimer"] is not None


@pytest.mark.asyncio
async def test_s21_agent_by_text(async_client: AsyncClient):
    # S21: Free text agent request -> AGENT_HANDOFF
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})

    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "talk to a person"}},
    )
    assert res.json()["state"] == "AGENT_HANDOFF"


@pytest.mark.asyncio
async def test_s22_pii_guard_sensitive_state(async_client: AsyncClient):
    # S22: Free text at sensitive state (OTP_INPUT) -> NLU NOT called
    res = await async_client.post("/chat/start")
    session_id = res.json()["session_id"]
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "YES"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"value": "RMN"}})
    await async_client.post("/chat/message", json={"session_id": session_id, "input": {"text": "9000000001"}})

    # At OTP_INPUT, send invalid OTP text
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "111111"}},
    )
    assert res.json()["state"] == "OTP_INPUT"
    assert res.json()["error"] is not None


@pytest.mark.asyncio
async def test_s24_hallucinated_value_rejected(async_client: AsyncClient):
    # S24: Hallucinated code Z99.9 -> dropped by grounding filter
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

    # Send hallucinated code Z99.9
    res = await async_client.post(
        "/chat/message",
        json={"session_id": session_id, "input": {"text": "diagnosis is Z99.9"}},
    )
    assert res.json()["state"] == "ADMISSION"


@pytest.mark.gemini
@pytest.mark.asyncio
async def test_live_gemini_nlu():
    # Live Gemini API test (requires GEMINI_API_KEY)
    if not settings.gemini_api_key:
        pytest.skip("GEMINI_API_KEY not configured")

    nlu = GeminiNLU()
    req = InterpretRequest(
        state="CLAIM_TYPE",
        text="I want to file a cashless claim please",
        today=date(2026, 9, 29),
        allowed_values=["CASHLESS", "REIMBURSEMENT"],
    )

    interp = await nlu.interpret(req)
    assert interp.intent in ("ANSWER", "OFF_TOPIC")
    if interp.intent == "ANSWER":
        assert interp.value == "CASHLESS"
