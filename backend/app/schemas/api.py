"""API request and response schemas."""

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class HealthCheck(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "0.1.0"


class UIField(BaseModel):
    """UI form field definition."""

    name: str
    label: str
    type: str  # text, date, search_select, select, email, etc.
    required: bool = True
    value: Any = None
    options_ref: str | None = None
    allow_other: bool = False
    options: list[dict[str, Any]] = Field(default_factory=list)


class UIOption(BaseModel):
    """UI selectable option."""

    value: str
    label: str
    subtext: str | None = None
    badge: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class UI(BaseModel):
    """UI state specification."""

    type: str  # consent, text, buttons, otp, date, form, list, summary, file, extraction, message, handoff
    fields: list[UIField] = Field(default_factory=list)
    options: list[UIOption] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    disclaimer: str | None = None
    warnings: list[str] = Field(default_factory=list)


class ChatError(BaseModel):
    """Chat error model."""

    field: str | None = None
    message: str


class BotReply(BaseModel):
    """Bot response shape."""

    session_id: str
    state: str
    messages: list[str] = Field(default_factory=list)
    ui: UI
    error: ChatError | None = None


class ChatInputValue(BaseModel):
    """Input payload wrapper."""

    value: Any = None
    text: str | None = None


class ChatMessageRequest(BaseModel):
    """Chat message request body."""

    session_id: str
    input: ChatInputValue
