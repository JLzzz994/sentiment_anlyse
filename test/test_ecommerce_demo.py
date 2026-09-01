from app.services.research.research_cases import ECOMMERCE_RESEARCH_CASES


def test_demo_contains_five_distinct_business_cases():
    assert len(ECOMMERCE_RESEARCH_CASES) == 5
    ids = [case["id"] for case in ECOMMERCE_RESEARCH_CASES]
    assert len(ids) == len(set(ids))


def test_demo_cases_cover_core_ecommerce_scenarios():
    combined = " ".join(str(case["query"]) for case in ECOMMERCE_RESEARCH_CASES)
    for keyword in ("售后", "库存", "商品", "竞品", "知识库"):
        assert keyword in combined


def test_every_case_declares_expected_evidence():
    assert all(case["expected_evidence"] for case in ECOMMERCE_RESEARCH_CASES)
