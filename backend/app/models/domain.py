"""Domain models for health insurance claim bot."""

from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Policy(BaseModel):
    """Health insurance policy model."""

    model_config = ConfigDict(extra="forbid")

    policy_no: str
    type: Literal["RETAIL", "GROUP"]
    product: str
    status: Literal["ACTIVE", "LAPSED", "EXPIRED"]
    rmn: str
    holder_name: str
    email: str
    city: str
    sum_insured: int
    start_date: date
    end_date: date
    corporate_name: str | None = None


class Member(BaseModel):
    """Insured member model."""

    model_config = ConfigDict(extra="forbid")

    uhid: str
    emp_code: str | None = None
    policy_no: str
    name: str
    relation: Literal["SELF", "SPOUSE", "SON", "DAUGHTER", "FATHER", "MOTHER"]
    dob: date
    gender: Literal["M", "F"]


class Claim(BaseModel):
    """Existing claim model."""

    model_config = ConfigDict(extra="forbid")

    claim_no: str
    policy_no: str
    uhid: str
    patient_name: str
    claim_type: Literal["CASHLESS", "REIMBURSEMENT"]
    status: Literal["OPEN", "IN_PROCESS", "SETTLED", "REJECTED", "CLOSED"]
    doa: date
    hospital_id: str
    diagnosis: str
    intimated_on: date


class Hospital(BaseModel):
    """Hospital reference model."""

    model_config = ConfigDict(extra="forbid")

    hospital_id: str
    name: str
    area: str
    address: str
    city: str
    pincode: str
    network: bool
    tier: Literal["A", "B", "C"]
    approx_cost: int


class Diagnosis(BaseModel):
    """ICD-10 diagnosis model."""

    model_config = ConfigDict(extra="forbid")

    code: str
    name: str


class RequiredDoc(BaseModel):
    """Required document specification."""

    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    mandatory: bool


class Option(BaseModel):
    """Generic label/value option."""

    model_config = ConfigDict(extra="forbid")

    value: str
    label: str


class FAQ(BaseModel):
    """FAQ item model."""

    model_config = ConfigDict(extra="forbid")

    id: str
    question: str
    answer: str


class UploadConfig(BaseModel):
    """Upload rules config."""

    max_mb: int = 5
    allowed_types: list[str] = Field(default_factory=lambda: ["application/pdf", "image/jpeg", "image/png"])


class DoaRulesConfig(BaseModel):
    """DOA rules config."""

    max_past_days: int = 30
    max_future_days_planned: int = 30


class LinksConfig(BaseModel):
    """External links config."""

    website_url: str
    self_i_url: str


class AppConfig(BaseModel):
    """App reference config model."""

    dev_otp: str = "123456"
    max_attempts: int = 3
    session_ttl_minutes: int = 30
    upload: UploadConfig = Field(default_factory=UploadConfig)
    doa_rules: DoaRulesConfig = Field(default_factory=DoaRulesConfig)
    links: LinksConfig
    agent_handoff_message: str
