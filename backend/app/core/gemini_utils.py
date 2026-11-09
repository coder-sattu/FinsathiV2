"""Gemini API model utilities, availability check, and safe execution fallback."""

import asyncio
import copy
import logging
from typing import Any

import aiohttp
import aiohttp.client_exceptions
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError
from app.core.config import settings

# Safely alias ClientConnectorDNSError if missing in installed aiohttp version (e.g., aiohttp 3.10.5)
if not hasattr(aiohttp, "ClientConnectorDNSError"):
    from aiohttp.client_exceptions import ClientConnectorError
    setattr(aiohttp, "ClientConnectorDNSError", ClientConnectorError)

if not hasattr(aiohttp.client_exceptions, "ClientConnectorDNSError"):
    from aiohttp.client_exceptions import ClientConnectorError
    setattr(aiohttp.client_exceptions, "ClientConnectorDNSError", ClientConnectorError)

logger = logging.getLogger(__name__)

# Fallback candidate models in order of priority
FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
]


def clean_schema(schema: Any) -> Any:
    """Clean Pydantic model_json_schema dict by recursively removing 'additionalProperties'
    which is forbidden in Gemini Developer API mode.
    """
    if hasattr(schema, "model_json_schema"):
        schema_dict = schema.model_json_schema()
    elif isinstance(schema, dict):
        schema_dict = schema
    else:
        return schema

    def _remove_additional(obj: Any) -> None:
        if isinstance(obj, dict):
            obj.pop("additionalProperties", None)
            for key, val in list(obj.items()):
                _remove_additional(val)
        elif isinstance(obj, list):
            for item in obj:
                _remove_additional(item)

    cl = copy.deepcopy(schema_dict)
    _remove_additional(cl)
    return cl


def verify_gemini_models_safe() -> list[str]:
    """Check Gemini model availability without exposing credentials or API keys.

    Returns a list of model names currently accessible to the configured client.
    """
    if not settings.gemini_api_key:
        logger.info("[Gemini Check] GEMINI_API_KEY is not configured.")
        return []

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        models = [m.name.replace("models/", "") for m in client.models.list()]
        logger.info(f"[Gemini Check] Successfully connected. Accessible models count: {len(models)}")
        return models
    except Exception:
        logger.exception("[Gemini Check] Could not verify models due to an exception:")
        return []


async def generate_content_with_fallback(
    client: genai.Client,
    primary_model: str,
    contents: Any,
    config: types.GenerateContentConfig | None = None,
    timeout_sec: float = 4.0,
) -> Any:
    """Execute generate_content with safe model fallback (e.g., if 404/503 occurs).

    Disables automatic function calling warning when appropriate and catches
    model-not-found / model-deprecated errors cleanly.
    """
    if config is None:
        config = types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )
    else:
        if config.automatic_function_calling is None:
            config.automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True)
        if config.response_schema is not None:
            config.response_schema = clean_schema(config.response_schema)

    candidate_models = [primary_model]
    for alt in FALLBACK_MODELS:
        if alt not in candidate_models:
            candidate_models.append(alt)

    last_error: Exception | None = None

    expected_exceptions = (
        ClientError,
        ServerError,
        APIError,
        ValueError,
        asyncio.TimeoutError,
        aiohttp.ClientError,
        aiohttp.ClientConnectorError,
        aiohttp.ClientOSError,
        aiohttp.ServerDisconnectedError,
    )

    for model in candidate_models:
        try:
            resp = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                ),
                timeout=timeout_sec,
            )
            return resp
        except expected_exceptions as e:
            last_error = e
            logger.warning(
                f"[Gemini Fallback] Model '{model}' failed: {type(e).__name__} ({e}). Trying next fallback model if available..."
            )
            continue
        except Exception as e:
            last_error = e
            logger.exception(f"[Gemini Fallback] Unexpected error on model '{model}':")
            break

    if last_error:
        raise last_error
    raise RuntimeError("Gemini content generation failed across all candidate models.")
