"""teaching.v1 教学证据目录装配：4 片段/8000 字节域内有限词项检索。"""
from __future__ import annotations

from .contracts import CatalogEntry, sha
from .evidence import LearningRefusal, Unit, rank_term_candidates


def assemble_teaching_catalog(query: str, units: tuple[Unit, ...], request_sha256: str) -> list[CatalogEntry]:
    """教学目录：至多 4 片段、总 4000 字符/8000 字节；沿 G7 片段验证。"""
    fragments = []
    lookup = {}
    for item in units:
        from app.retrieval.evidence import build_fragments, verify_fragment
        try:
            parts = build_fragments(item.unit, max_fragments=512)
        except ValueError:
            raise LearningRefusal("learning_scope_limit", "原文或片段超过有限读取边界，请缩小资料范围") from None
        if len(fragments) + len(parts) > 512:
            raise LearningRefusal("learning_scope_limit", "资料超过512片段，请缩小资料范围")
        for fragment in parts:
            if not verify_fragment(item.unit, fragment):
                raise LearningRefusal("integrity_error", "原文片段完整性检查失败")
            if fragment.evidence_id in lookup:
                raise LearningRefusal("integrity_error", "资料中有无法区分的重复证据身份，请缩小范围")
            lookup[fragment.evidence_id] = item
        fragments.extend(parts)
    candidates = rank_term_candidates(query, tuple(fragments),
        allowed_versions=frozenset((u.unit.source_id, u.unit.version_id) for u in units), top_k=4)
    if not candidates:
        raise LearningRefusal("no_evidence", "有限词项检索没有找到相关证据；请明确目标或调整资料范围",
                              kind="no_evidence")
    entries = []
    for candidate in candidates:
        fragment = candidate.fragment
        item = lookup[fragment.evidence_id]
        entries.append(CatalogEntry(source_id=fragment.source_id, version_id=fragment.version_id,
            source_revision=fragment.source_revision,
            citation_id="lc_" + sha(request_sha256 + fragment.evidence_id)[:24],
            evidence_id=fragment.evidence_id, title=item.source["title"],
            format=item.source["format"], original_sha256=item.source["sha256"],
            unit_sha256=sha(item.unit.text), fragment_sha256=fragment.text_sha256,
            start_line=fragment.start_line, end_line=fragment.end_line,
            start_offset=fragment.start_offset, end_offset=fragment.end_offset,
            physical_page=fragment.physical_page, origin_kind=fragment.origin_kind,
            supplement_id=item.supplement_id, text=fragment.text))
    if sum(len(e.text) for e in entries) > 4000 or sum(len(e.text.encode("utf-8")) for e in entries) > 8000:
        raise LearningRefusal("teaching_context_limit", "教学证据目录超过限额，请缩小目标或活动范围")
    return entries
