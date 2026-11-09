"""Agentic Tool registry for JSON searching and Policy Document RAG."""

import json
from pathlib import Path
from typing import Any
from rapidfuzz import fuzz
from app.agent.cognee_rag import CogneePolicyRAG

_DATA_DIR = Path(__file__).parent.parent.parent / "data"

_rag_retriever = CogneePolicyRAG()


def search_policy(query: str) -> list[dict[str, Any]]:
    """Search policy record by policy number, holder name, mobile number, or product name in policies.json."""
    path = _DATA_DIR / "policies.json"
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        policies = json.load(f)

    q = query.strip().upper()
    results = []

    for p in policies:
        p_no = p.get("policy_no", "").upper()
        rmn = p.get("rmn", "")
        holder = p.get("holder_name", "").upper()
        prod = p.get("product", "").upper()

        if q in p_no or q == rmn or q in holder or q in prod:
            results.append(p)

    return results or policies[:2]


def search_member(policy_no: str = "", query: str = "") -> list[dict[str, Any]]:
    """Search member record by UHID, employee code, or member name in members.json."""
    path = _DATA_DIR / "members.json"
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        members = json.load(f)

    q = query.strip().upper()
    p_no = policy_no.strip().upper()

    results = []
    for m in members:
        m_pol = m.get("policy_no", "").upper()
        uhid = m.get("uhid", "").upper()
        name = m.get("name", "").upper()
        emp = (m.get("employee_code") or "").upper()

        if p_no and m_pol != p_no:
            continue

        if not q or q in uhid or q in name or q in emp:
            results.append(m)

    return results


def search_hospital(pincode: str = "", name_query: str = "") -> list[dict[str, Any]]:
    """Search hospitals by 6-digit pincode or hospital name in hospitals.json."""
    path = _DATA_DIR / "hospitals.json"
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        hospitals = json.load(f)

    pin = pincode.strip()
    name_q = name_query.strip().upper()

    results = []
    for h in hospitals:
        h_pin = str(h.get("pincode", ""))
        h_name = h.get("name", "").upper()

        if pin and h_pin == pin:
            results.append(h)
        elif name_q and (name_q in h_name or fuzz.partial_ratio(name_q, h_name) > 75):
            results.append(h)

    return results or hospitals[:3]


def search_diagnosis(query: str) -> list[dict[str, Any]]:
    """Search diagnoses by code or illness name in diagnoses.json."""
    path = _DATA_DIR / "diagnoses.json"
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        diagnoses = json.load(f)

    q = query.strip().upper()
    results = []

    for d in diagnoses:
        code = d.get("code", "").upper()
        name = d.get("name", "").upper()

        if q in code or q in name or fuzz.partial_ratio(q, name) > 70:
            results.append(d)

    return results


def query_policy_document_rag(query: str, product_name: str = "") -> str:
    """Query policy document clauses via Cognee RAG to retrieve exact coverage, capping, and waiting period rules."""
    return _rag_retriever.get_grounded_clause_summary(query=query, product_name=product_name)
