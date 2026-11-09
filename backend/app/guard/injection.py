"""Prompt injection detection heuristics."""

import re

# Prompt injection regex patterns
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all|previous|above)", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"you\s+are\s+now", re.IGNORECASE),
    re.compile(r"act\s+as", re.IGNORECASE),
    re.compile(r"developer\s+mode", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"reveal", re.IGNORECASE),
    re.compile(r"pretend", re.IGNORECASE),
    re.compile(r"forget\s+(your\s+)?instructions", re.IGNORECASE),
    re.compile(r"```"),
    re.compile(r"<script", re.IGNORECASE),
    re.compile(r"\{\{"),
    re.compile(r"role:", re.IGNORECASE),
]


def is_prompt_injection(text: str) -> bool:
    # check prompt injection heuristics
    clean = text.strip()
    for pattern in INJECTION_PATTERNS:
        if pattern.search(clean):
            return True
    return False
