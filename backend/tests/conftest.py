"""Pytest fixtures for backend tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.core.config import settings
from app.main import app
from app.repository.json_repo import JsonDataStore


@pytest.fixture(scope="session")
def data_store() -> JsonDataStore:
    # load data store fixture
    return JsonDataStore(settings.data_path)


@pytest.fixture
async def async_client():
    # async test client with clean DB state
    import asyncpg
    try:
        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/claimbot")
        await conn.execute("TRUNCATE TABLE chat_sessions, claim_intimations, service_requests, uploaded_documents, audit_log, document_extractions, guardrail_events CASCADE;")
        await conn.close()
    except Exception:
        pass

    app.state.data_store = JsonDataStore(settings.data_path)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
