"""FastAPI dependency injection utilities."""

from typing import Annotated
from fastapi import Depends, Request
from app.core.clock import Clock
from app.core.config import settings
from app.llm.fake_nlu import FakeNLU
from app.llm.gemini_nlu import GeminiNLU
from app.llm.nlu import NLU
from app.repository.base import HospitalRepo, MasterRepo, MemberRepo, PolicyRepo
from app.repository.json_repo import (
    JsonDataStore,
    JsonHospitalRepo,
    JsonMasterRepo,
    JsonMemberRepo,
    JsonPolicyRepo,
)

# global clock instance
default_clock = Clock()


def get_clock() -> Clock:
    # return clock
    return default_clock


def get_data_store(request: Request) -> JsonDataStore:
    # get loaded json data store from app state or load on demand
    store = getattr(request.app.state, "data_store", None)
    if store is None:
        store = JsonDataStore(settings.data_dir)
        request.app.state.data_store = store
    return store


def get_policy_repo(store: Annotated[JsonDataStore, Depends(get_data_store)]) -> PolicyRepo:
    # get policy repo
    return JsonPolicyRepo(store)


def get_member_repo(store: Annotated[JsonDataStore, Depends(get_data_store)]) -> MemberRepo:
    # get member repo
    return JsonMemberRepo(store)


def get_hospital_repo(store: Annotated[JsonDataStore, Depends(get_data_store)]) -> HospitalRepo:
    # get hospital repo
    return JsonHospitalRepo(store)


def get_master_repo(store: Annotated[JsonDataStore, Depends(get_data_store)]) -> MasterRepo:
    # get master repo
    return JsonMasterRepo(store)


def get_nlu() -> NLU:
    # get Agentic NLU interpreter with Tool Calling & Cognee Policy RAG
    from app.agent.gemini_agent import GeminiAgenticSystem
    if settings.llm_enabled and settings.gemini_api_key:
        return GeminiAgenticSystem()
    return FakeNLU()


def get_doc_ai():
    # get Doc AI service
    from app.doc_ai.fake_doc_ai import FakeDocAI
    from app.doc_ai.gemini_doc_ai import GeminiDocAI
    if settings.doc_ai_enabled and settings.gemini_api_key:
        return GeminiDocAI()
    return FakeDocAI()

