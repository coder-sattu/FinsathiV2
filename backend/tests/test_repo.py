"""Unit tests for reference repositories and health endpoint."""

import pytest
from httpx import AsyncClient
from app.repository.json_repo import (
    JsonDataStore,
    JsonHospitalRepo,
    JsonMasterRepo,
    JsonMemberRepo,
    JsonPolicyRepo,
)


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    # test health check
    res = await async_client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


def test_golden_policies_load(data_store: JsonDataStore):
    # verify golden policies
    repo = JsonPolicyRepo(data_store)
    p1 = repo.by_number("HP-RET-2026-0001")
    assert p1 is not None
    assert p1.type == "RETAIL"
    assert p1.rmn == "9000000001"
    assert p1.holder_name == "Rohan Kulkarni"

    p2 = repo.by_number("HP-GRP-2026-0001")
    assert p2 is not None
    assert p2.type == "GROUP"
    assert p2.corporate_name == "Acme Infotech Pvt Ltd"

    p3 = repo.by_number("HP-RET-2026-0006")
    assert p3 is not None
    assert p3.status == "LAPSED"

    # test by mobile
    by_mob = repo.by_mobile("9000000003")
    assert len(by_mob) == 2


def test_golden_members_load(data_store: JsonDataStore):
    # verify golden members
    repo = JsonMemberRepo(data_store)
    m1 = repo.verify("HP-RET-2026-0001", "UH1000000001")
    assert m1 is not None
    assert m1.name == "Rohan Kulkarni"
    assert m1.relation == "SELF"

    m_emp = repo.verify("HP-GRP-2026-0001", "EMP10001")
    assert m_emp is not None
    assert m_emp.name == "Priya Deshmukh"

    m_list = repo.by_policy("HP-RET-2026-0001")
    assert len(m_list) == 3


def test_golden_master_data_load(data_store: JsonDataStore):
    # verify master data
    repo = JsonMasterRepo(data_store)
    diagnoses = repo.diagnoses()
    assert len(diagnoses) >= 20
    d_a90 = next((d for d in diagnoses if d.code == "A90"), None)
    assert d_a90 is not None
    assert d_a90.name == "Dengue fever"

    docs_cashless = repo.required_docs("CASHLESS")
    assert len(docs_cashless) == 2

    docs_reim = repo.required_docs("REIMBURSEMENT")
    assert len(docs_reim) == 8

    faqs = repo.faqs()
    assert len(faqs) == 10
    faq3 = next((f for f in faqs if f.id == "FAQ-03"), None)
    assert faq3 is not None
    assert faq3.question == "What is a network hospital?"

    config = repo.config()
    assert config.dev_otp == "123456"


@pytest.mark.parametrize(
    "pin, expected_count, is_exact, expected_first_id",
    [
        ("411045", 2, True, "PUN-005"),   # Pune Baner exact match
        ("411021", 5, False, "PUN-018"),  # Pune nearest fallback (411018 difference 3)
        ("400050", 2, True, "MUM-002"),   # Mumbai Bandra exact match
        ("999999", 0, False, None),       # Non-existent pincode prefix
    ],
)
def test_pincode_lookup(
    data_store: JsonDataStore,
    pin: str,
    expected_count: int,
    is_exact: bool,
    expected_first_id: str | None,
):
    # test pincode lookup
    repo = JsonHospitalRepo(data_store)
    hospitals, exact = repo.by_pincode(pin)
    assert exact == is_exact
    assert len(hospitals) == expected_count
    if expected_first_id:
        assert hospitals[0].hospital_id == expected_first_id
