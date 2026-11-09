"""JSON-backed implementation of repositories."""

import json
from pathlib import Path
from typing import Any
from app.models.domain import AppConfig, Claim, Diagnosis, FAQ, Hospital, Member, Option, Policy, RequiredDoc


def _load_json(file_path: Path) -> Any:
    # load json file
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


class JsonDataStore:
    """Loaded JSON reference data."""

    def __init__(self, data_dir: Path | str) -> None:
        # load all data
        dir_path = Path(data_dir)
        self.data_dir = dir_path
        self.config = AppConfig.model_validate(_load_json(dir_path / "config.json"))
        self.policies = [Policy.model_validate(p) for p in _load_json(dir_path / "policies.json")]
        self.members = [Member.model_validate(m) for m in _load_json(dir_path / "members.json")]
        self.claims = [Claim.model_validate(c) for c in _load_json(dir_path / "claims.json")]
        self.hospitals = [Hospital.model_validate(h) for h in _load_json(dir_path / "hospitals.json")]
        self.diagnoses = [Diagnosis.model_validate(d) for d in _load_json(dir_path / "diagnoses.json")]
        raw_docs = _load_json(dir_path / "required_docs.json")
        self.required_docs = {
            k: [RequiredDoc.model_validate(doc) for doc in v]
            for k, v in raw_docs.items()
        }
        self.intimation_types = [Option.model_validate(i) for i in _load_json(dir_path / "intimation_types.json")]
        self.faqs = [FAQ.model_validate(f) for f in _load_json(dir_path / "faq.json")]


class JsonPolicyRepo:
    """Policy repo implementation."""

    def __init__(self, store: JsonDataStore) -> None:
        # store reference
        self._store = store

    def by_mobile(self, mobile: str) -> list[Policy]:
        # lookup by mobile
        return [p for p in self._store.policies if p.rmn == mobile]

    def by_number(self, policy_no: str) -> Policy | None:
        # lookup by policy_no
        target = policy_no.upper().strip()
        for p in self._store.policies:
            if p.policy_no.upper() == target:
                return p
        return None


class JsonMemberRepo:
    """Member repo implementation."""

    def __init__(self, store: JsonDataStore) -> None:
        # store reference
        self._store = store

    def by_policy(self, policy_no: str) -> list[Member]:
        # lookup by policy
        target = policy_no.upper().strip()
        return [m for m in self._store.members if m.policy_no.upper() == target]

    def verify(self, policy_no: str, uhid_or_emp: str) -> Member | None:
        # verify member
        target_policy = policy_no.upper().strip()
        target_id = uhid_or_emp.upper().strip()
        for m in self._store.members:
            if m.policy_no.upper() == target_policy:
                if m.uhid.upper() == target_id or (m.emp_code and m.emp_code.upper() == target_id):
                    return m
        return None


class JsonClaimRepo:
    """Claim repo implementation."""

    def __init__(self, store: JsonDataStore) -> None:
        # store reference
        self._store = store

    async def open_by_policy(self, policy_no: str) -> list[Claim]:
        # get open claims from json
        target = policy_no.upper().strip()
        return [
            c for c in self._store.claims
            if c.policy_no.upper() == target and c.status in ("OPEN", "IN_PROCESS")
        ]


class JsonHospitalRepo:
    """Hospital repo implementation."""

    def __init__(self, store: JsonDataStore) -> None:
        # store reference
        self._store = store

    def by_pincode(self, pin: str) -> tuple[list[Hospital], bool]:
        # search by pincode
        clean_pin = pin.strip()
        exact = [h for h in self._store.hospitals if h.pincode == clean_pin]
        if exact:
            return exact, True

        # check pincode prefix
        if len(clean_pin) == 6 and clean_pin.isdigit():
            target_num = int(clean_pin)
            prefix = clean_pin[:3]
            if prefix in ("411", "412"):
                candidates = [h for h in self._store.hospitals if h.pincode[:3] in ("411", "412")]
            elif prefix == "400":
                candidates = [h for h in self._store.hospitals if h.pincode[:3] == "400"]
            else:
                candidates = []

            if candidates:
                # sort nearest 5
                sorted_cand = sorted(candidates, key=lambda h: abs(int(h.pincode) - target_num))
                return sorted_cand[:5], False

        return [], False

    def by_id(self, hospital_id: str) -> Hospital | None:
        # lookup by hospital_id
        target = hospital_id.upper().strip()
        for h in self._store.hospitals:
            if h.hospital_id.upper() == target:
                return h
        return None


class JsonMasterRepo:
    """Master reference repo implementation."""

    def __init__(self, store: JsonDataStore) -> None:
        # store reference
        self._store = store

    def diagnoses(self) -> list[Diagnosis]:
        # list diagnoses
        return self._store.diagnoses

    def required_docs(self, claim_type: str) -> list[RequiredDoc]:
        # list docs
        return self._store.required_docs.get(claim_type.upper(), [])

    def intimation_types(self) -> list[Option]:
        # list intimation types
        return self._store.intimation_types

    def faqs(self) -> list[FAQ]:
        # list faqs
        return self._store.faqs

    def config(self) -> AppConfig:
        # get config
        return self._store.config
