"""FastAPI application main entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.core.config import settings
from app.core.gemini_utils import verify_gemini_models_safe
from app.core.logging import setup_logging
from app.repository.json_repo import JsonDataStore
from app.schemas.api import HealthCheck


@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup logging and load data store
    setup_logging()
    app.state.data_store = JsonDataStore(settings.data_path)
    verify_gemini_models_safe()
    yield


app = FastAPI(
    title="Health Insurance Claim Bot API",
    version="0.1.0",
    lifespan=lifespan,
)

# setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(chat_router)


@app.get("/health", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """Return application health status."""
    return HealthCheck(status="ok", version="0.1.0")
