"""Repository interfaces (Protocols)."""

from typing import Protocol
from app.models.domain import AppConfig, Claim, Diagnosis, FAQ, Hospital, Member, Option, Policy, RequiredDoc


class PolicyRepo(Protocol):
    """Policy repository protocol."""

    def by_mobile(self, mobile: str) -> list[Policy]: ...
    def by_number(self, policy_no: str) -> Policy | None: ...


class MemberRepo(Protocol):
    """Member repository protocol."""

    def by_policy(self, policy_no: str) -> list[Member]: ...
    def verify(self, policy_no: str, uhid_or_emp: str) -> Member | None: ...


class ClaimRepo(Protocol):
    """Claim repository protocol."""

    async def open_by_policy(self, policy_no: str) -> list[Claim]: ...


class HospitalRepo(Protocol):
    """Hospital repository protocol."""

    def by_pincode(self, pin: str) -> tuple[list[Hospital], bool]: ...
    def by_id(self, hospital_id: str) -> Hospital | None: ...


class MasterRepo(Protocol):
    """Master reference data repository protocol."""

    def diagnoses(self) -> list[Diagnosis]: ...
    def required_docs(self, claim_type: str) -> list[RequiredDoc]: ...
    def intimation_types(self) -> list[Option]: ...
    def faqs(self) -> list[FAQ]: ...
    def config(self) -> AppConfig: ...
