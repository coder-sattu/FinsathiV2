"""Input guardrails pipeline (I1-I9)."""

import re
import unicodedata
from dataclasses import dataclass
from typing import Any
from app.core.config import settings
from app.flow.messages import MESSAGES
from app.flow.states import State
from app.guard.injection import is_prompt_injection
from app.guard.pii import mask_pii

# Abuse profanity patterns
ABUSE_REGEX = re.compile(r"\b(bastard|bitch|idiot|stupid|scam|fraud|abuse|fool|mad)\b", re.IGNORECASE)


@dataclass
class InputGuardResult:
    """Result of input guardrail checks."""

    allowed: bool
    cleaned_text: str
    masked_text: str
    error_message: str | None = None
    warning_message: str | None = None
    code: str | None = None
    trigger_agent_handoff: bool = False


# session message timestamps for rate limiting
_session_message_history: dict[str, list[float]] = {}


def check_input(
    text: str,
    state: str,
    session_id: str | None = None,
    current_time: float | None = None,
    injection_hits: int = 0,
) -> InputGuardResult:
    """Run input guardrails I1-I8 on user text."""

    if not text:
        return InputGuardResult(allowed=True, cleaned_text="", masked_text="")

    # I1: Sanitise + length
    clean = re.sub(r"<[^>]*>", "", text)
    clean = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    if len(clean) > settings.max_input_chars:
        return InputGuardResult(
            allowed=False,
            cleaned_text=clean,
            masked_text=clean,
            error_message=MESSAGES["too_long"],
            code="I1",
        )

    # I2: Rate limit (max 20 messages / minute)
    if session_id and current_time:
        history = _session_message_history.get(session_id, [])
        history = [t for t in history if current_time - t <= 60]
        if len(history) >= 20:
            return InputGuardResult(
                allowed=False,
                cleaned_text=clean,
                masked_text=clean,
                error_message=MESSAGES["rate_limited"],
                code="I2",
            )
        history.append(current_time)
        _session_message_history[session_id] = history

    # I3: Language check (Devanagari, Arabic, Non-Latin > 30%)
    alpha_chars = [c for c in clean if c.isalpha()]
    if alpha_chars:
        non_latin = [c for c in alpha_chars if "LATIN" not in unicodedata.name(c, "")]
        if len(non_latin) / len(alpha_chars) > 0.30:
            return InputGuardResult(
                allowed=False,
                cleaned_text=clean,
                masked_text=clean,
                error_message=MESSAGES["english_only"],
                code="I3",
            )

    # I6: Prompt injection defence
    if is_prompt_injection(clean):
        new_hits = injection_hits + 1
        trigger_handoff = new_hits >= 3
        return InputGuardResult(
            allowed=False,
            cleaned_text=clean,
            masked_text=clean,
            error_message=MESSAGES["injection_block"],
            code="I6",
            trigger_agent_handoff=trigger_handoff,
        )

    # I8: Abuse filter
    if ABUSE_REGEX.search(clean):
        return InputGuardResult(
            allowed=False,
            cleaned_text=clean,
            masked_text=clean,
            error_message="I'm here to help with your claim. Let's continue.",
            code="I8",
        )

    # I4: PII masking
    masked_text, pii_warning_triggered = mask_pii(clean)
    warning = MESSAGES["pii_warning"] if pii_warning_triggered else None

    return InputGuardResult(
        allowed=True,
        cleaned_text=clean,
        masked_text=masked_text,
        warning_message=warning,
    )
