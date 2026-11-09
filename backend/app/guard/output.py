"""Output guardrails pipeline (O1-O7)."""

from dataclasses import dataclass
from app.guard.compliance import check_compliance
from app.guard.disclaimers import get_disclaimer
from app.guard.pii import redact_last4
from app.schemas.api import BotReply


@dataclass
class OutputGuardResult:
    """Result of output guardrail processing."""

    reply: BotReply
    compliance_violation: bool = False
    disclaimer_added: str | None = None


def check_output(reply: BotReply, context_kind: str | None = None) -> OutputGuardResult:
    """Run output guardrails O4-O6 on outgoing bot reply."""

    sanitized_messages = []
    compliance_hit = False

    # O4: Compliance filter on outgoing messages
    for msg in reply.messages:
        safe_msg, is_viol = check_compliance(msg)
        sanitized_messages.append(safe_msg)
        if is_viol:
            compliance_hit = True

    reply.messages = sanitized_messages

    # O6: Auto-attach disclaimers
    disclaimer_text = None
    if context_kind:
        disclaimer_text = get_disclaimer(context_kind)
        if disclaimer_text:
            reply.ui.disclaimer = disclaimer_text

    return OutputGuardResult(
        reply=reply,
        compliance_violation=compliance_hit,
        disclaimer_added=disclaimer_text,
    )
