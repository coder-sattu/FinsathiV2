"""PII detection and masking utilities."""

import re

# PII regex patterns
AADHAAR_REGEX = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
PAN_REGEX = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.IGNORECASE)
MOBILE_REGEX = re.compile(r"\b[6-9]\d{9}\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
POLICY_REGEX = re.compile(r"\bHP-(?:RET|GRP)-\d{4}-\d{4}\b", re.IGNORECASE)
UHID_REGEX = re.compile(r"\bUH\d{10}\b", re.IGNORECASE)
ACCOUNT_CARD_REGEX = re.compile(r"\b\d{9,18}\b")


def mask_pii(text: str) -> tuple[str, bool]:
    # mask sensitive PII tokens in text
    sensitive_detected = False

    # check sensitive patterns (aadhaar, pan, bank account)
    if AADHAAR_REGEX.search(text) or PAN_REGEX.search(text) or ACCOUNT_CARD_REGEX.search(text):
        sensitive_detected = True

    masked = text
    masked = AADHAAR_REGEX.sub("[AADHAAR]", masked)
    masked = PAN_REGEX.sub("[PAN]", masked)
    masked = POLICY_REGEX.sub("[POLICY]", masked)
    masked = UHID_REGEX.sub("[UHID]", masked)
    masked = EMAIL_REGEX.sub("[EMAIL]", masked)
    masked = MOBILE_REGEX.sub("[PHONE]", masked)
    masked = ACCOUNT_CARD_REGEX.sub("[NUM]", masked)

    return masked, sensitive_detected


def redact_last4(number_str: str) -> str:
    # mask all but last 4 digits
    digits = re.sub(r"\D", "", number_str)
    if len(digits) <= 4:
        return digits
    return f"{'*' * (len(digits) - 4)}{digits[-4:]}"
