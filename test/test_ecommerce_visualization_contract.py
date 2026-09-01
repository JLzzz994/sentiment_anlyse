from pathlib import Path

from engines.common.evidence_persistence import persist_section_evidence
from engines.contracts.evidence import EvidenceDocument, EvidenceRecord, RetrievalMeta


def test_evidence_card_persistence_contains_source_and_channel(tmp_path: Path):
    record = EvidenceRecord(
        evidence_document=EvidenceDocument(
            platform="internal_crm",
            source_table="customer_ticket",
            source_id="1001",
            content="商家咨询售后规则变化",
            published_at="2026-08-18 09:20:00",
            hotness_score=92,
        ),
        retrieval_meta=RetrievalMeta(
            matched_queries=["售后规则"],
            channel_scores={"db_call": 1.0, "vector_call": 0.81},
        ),
    )
    path = persist_section_evidence(
        output_dir=tmp_path,
        task_id="task_demo",
        role="insight",
        section_key="platform_rule_changes",
        section_title="平台规则变化与业务影响",
        retrieval_text="售后规则变化",
        records=[record],
        rerank_scores={record.id: 0.88},
    )
    text = path.read_text(encoding="utf-8")
    assert "customer_ticket" in text
    assert "db_call" in text
    assert "vector_call" in text
    assert "0.88" in text
