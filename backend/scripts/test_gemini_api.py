import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.agent.gemini_agent import GeminiAgenticSystem
from app.llm.nlu import InterpretRequest
from datetime import date

async def test_live_gemini():
    print(f"[CHECK] Gemini API Key present: {bool(settings.gemini_api_key)}")
    print(f"[CHECK] LLM Enabled: {settings.llm_enabled}")
    print(f"[CHECK] Gemini Model: {settings.gemini_model}")

    if not settings.gemini_api_key:
        print("[FAIL] No GEMINI_API_KEY set in .env! Using offline fallback.")
        return

    agent = GeminiAgenticSystem()
    print("[INFO] Testing live Gemini Agentic System call...")

    # Test 1: NLU Intent Interpretation
    req = InterpretRequest(
        state="CLAIM_TYPE",
        text="I need to initiate a cashless claim for hospital admission",
        today=date(2026, 9, 30),
        allowed_values=["CASHLESS", "REIMBURSEMENT"],
    )

    try:
        interp = await agent.run_agent(req)
        print(f"[SUCCESS] Gemini API Response Received!")
        print(f" -> Intent: {interp.intent}")
        print(f" -> Value: {interp.value}")
        print(f" -> Confidence: {interp.confidence}")
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")

    # Test 2: Cognee Policy Document RAG
    print("\n[INFO] Testing Cognee Policy Document RAG...")
    req_rag = InterpretRequest(
        state="HOSPITAL_PIN",
        text="What is the room rent limit for Family Health Optima policy?",
        today=date(2026, 9, 30),
    )
    try:
        interp_rag = await agent.run_agent(req_rag, session_data={"product": "Family Health Optima"})
        print(f"[SUCCESS] Cognee RAG Response Received!")
        print(f" -> Intent: {interp_rag.intent}")
        print(f" -> Value Snippet:\n{interp_rag.value.encode('ascii', 'ignore').decode('ascii')}")
    except Exception as e:
        print(f"[ERROR] RAG query failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_live_gemini())
