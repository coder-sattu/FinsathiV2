"""NLU data models and Protocol definition."""

from datetime import date
from typing import Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field

Intent = Literal["ANSWER", "QUESTION", "RESTART", "AGENT", "CANCEL", "OFF_TOPIC"]


class MemberHint(BaseModel):
    """Member hint model for NLU prompt context."""

    first_name: str
    relation: str


class DiagnosisHint(BaseModel):
    """Diagnosis hint model for NLU prompt context."""

    code: str
    name: str


class FAQHint(BaseModel):
    """FAQ hint model for NLU prompt context."""

    id: str
    question: str


class InterpretRequest(BaseModel):
    """Request context sent to NLU interpreter."""

    state: str
    text: str
    today: date
    allowed_values: list[str] = Field(default_factory=list)
    fields: list[str] = Field(default_factory=list)
    members: list[MemberHint] = Field(default_factory=list)
    diagnoses: list[DiagnosisHint] = Field(default_factory=list)
    faq: list[FAQHint] = Field(default_factory=list)


class Interpretation(BaseModel):
    """Structured response from NLU interpreter."""

    model_config = ConfigDict(extra="forbid")

    intent: Intent
    value: str = ""
    fields: dict[str, str] = Field(default_factory=dict)
    faq_id: str = ""
    confidence: float = Field(ge=0, le=1)


class NLU(Protocol):
    """NLU interpreter protocol interface."""

    async def interpret(self, req: InterpretRequest) -> Interpretation: ...
