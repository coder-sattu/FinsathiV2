"""Compliance filtering for outgoing messages."""

import re

# Banned compliance phrases
BANNED_PATTERNS = [
    re.compile(r"\bguaranteed\b", re.IGNORECASE),
    re.compile(r"\bwill\s+be\s+approved\b", re.IGNORECASE),
    re.compile(r"\bapproved\b", re.IGNORECASE),
    re.compile(r"100%", re.IGNORECASE),
    re.compile(r"\bwill\s+be\s+paid\b", re.IGNORECASE),
    re.compile(r"\bno\s+deductions\b", re.IGNORECASE),
    re.compile(r"\bsanctioned\b", re.IGNORECASE),
]

SAFE_COMPLIANCE_FALLBACK = "Your request has been received. Final claim assessment is done by our claims team based on policy terms."


def check_compliance(text: str) -> tuple[str, bool]:
    # scan and sanitize outgoing compliance violations
    for pattern in BANNED_PATTERNS:
        if pattern.search(text):
            return SAFE_COMPLIANCE_FALLBACK, True
    return text, False
