"""Input validation utilities."""

import re
from datetime import date


def clean_mobile(raw: str) -> str:
    # clean mobile number
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    return digits


def validate_mobile(raw: str) -> str | None:
    # validate mobile format
    mob = clean_mobile(raw)
    if re.match(r"^[6-9]\d{9}$", mob):
        return mob
    return None


def validate_policy_no(raw: str) -> str | None:
    # validate policy number format
    clean = raw.strip().upper()
    if re.match(r"^HP-(RET|GRP)-\d{4}-\d{4}$", clean):
        return clean
    return None


def validate_otp(raw: str, dev_otp: str = "123456") -> bool:
    # validate otp
    clean = raw.strip()
    return clean == dev_otp


def validate_uhid(raw: str) -> str | None:
    # validate uhid format
    clean = raw.strip().upper()
    if re.match(r"^UH\d{10}$", clean):
        return clean
    return None


def validate_emp_code(raw: str) -> str | None:
    # validate emp code format
    clean = raw.strip().upper()
    if re.match(r"^EMP\d{5}$", clean):
        return clean
    return None


def validate_pincode(raw: str) -> str | None:
    # validate pincode format
    clean = raw.strip()
    if re.match(r"^[1-9]\d{5}$", clean):
        return clean
    return None


def validate_email(raw: str) -> str | None:
    # validate email format
    clean = raw.strip()
    if re.match(r"^[^@]+@[^@]+\.[^@]+$", clean):
        return clean
    return None
