"""将研究 Agent 的章节证据持久化为前端可读取的结构化卡片。"""

import json
from pathlib import Path
from typing import Any

from engines.contracts.evidence import EvidenceRecord


def _serialize_record(
    record: EvidenceRecord,
    rerank_score: float | None = None,
) -> dict[str, Any]:
    doc = record.evidence_document
    return {
        "evidence_id": record.id,
        "platform": doc.platform,
        "source_table": doc.source_table,
        "source_name": doc.source_name,
        "title": doc.title,
        "url": doc.url,
        "content": doc.content,
        "published_at": str(doc.published_at),
        "hotness_score": float(doc.hotness_score or 0),
        "engagement": doc.engagement,
        "matched_queries": list(record.retrieval_meta.matched_queries),
        "retrieval_channels": dict(record.retrieval_meta.channel_scores),
        "rerank_score": rerank_score,
    }


def persist_section_evidence(
    output_dir: str | Path,
    task_id: str,
    role: str,
    section_key: str,
    section_title: str,
    retrieval_text: str,
    records: list[EvidenceRecord],
    rerank_scores: dict[str, float] | None = None,
) -> Path:
    """按章节增量写入 evidence.json；同一 role 图按章节串行生成，可安全覆盖本角色文件。"""
    output_path = Path(output_dir) / "evidence.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "task_id": task_id,
        "role": role,
        "sections": {},
    }
    if output_path.exists():
        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    score_map = rerank_scores or {}
    payload.setdefault("sections", {})[section_key] = {
        "section_key": section_key,
        "title": section_title,
        "retrieval_text": retrieval_text,
        "evidence": [
            _serialize_record(record, score_map.get(record.id))
            for record in records
        ],
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path
