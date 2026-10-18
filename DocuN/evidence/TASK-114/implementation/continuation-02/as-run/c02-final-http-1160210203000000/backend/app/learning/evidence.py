"""活动权威范围内的有界原文读取、词项证据包与引用复查。"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from app.materials.repository import VersionConflict
from app.retrieval.evidence import SourceTextUnit, build_fragments, rank_term_candidates, verify_fragment, _terms
from app.storage.originals import Original
from .contracts import CatalogEntry, SourceIdentity, sha

MAX_ORIGINAL_BYTES = 5 * 1024 * 1024


class LearningRefusal(ValueError):
    def __init__(self, code: str, message: str, *, kind: str | None = None):
        self.code, self.message, self.kind = code, message, kind
        super().__init__(code)


@dataclass(frozen=True)
class Unit:
    source: dict
    unit: SourceTextUnit
    supplement_id: str | None = None


def validate_snapshot(snapshot: dict | None, *, for_call=True) -> list[SourceIdentity]:
    if snapshot is None:
        raise LearningRefusal("not_found", "活动不存在")
    if for_call and snapshot["status"] == "cancelled":
        raise LearningRefusal("activity_cancelled", "活动已取消，不能开始学习")
    if snapshot["source_count"] > 10:
        raise LearningRefusal("learning_scope_limit", "学习最多10份资料，请新建较小范围的活动")
    rows = snapshot["sources"]
    if not rows:
        raise LearningRefusal("source_invalid", "活动没有可用资料范围")
    if any(not row["valid"] for row in rows):
        raise LearningRefusal("source_invalid", "资料已删除或替换，请用当前资料新建活动；历史成果保留")
    if any(not row["ready"] for row in rows):
        raise LearningRefusal("source_not_ready", "活动中有资料未就绪；PDF必须完成全部物理页核对")
    if any(type(row["size"]) is not int or not 0 < row["size"] <= MAX_ORIGINAL_BYTES for row in rows):
        raise LearningRefusal("learning_scope_limit", "资料大小超过有限读取边界，请缩小范围")
    if sum(row["size"] for row in rows) > MAX_ORIGINAL_BYTES:
        raise LearningRefusal("learning_scope_limit", "本次资料累计超过5 MiB，请缩小活动范围")
    return [SourceIdentity(source_id=r["source_id"], version_id=r["version_id"], source_revision=r["source_revision"]) for r in rows]


def load_units(snapshot, materials, originals) -> tuple[Unit, ...]:
    validate_snapshot(snapshot, for_call=False)
    units = []
    text_bytes = 0
    for source in snapshot["sources"]:
        raw = originals.read(Original(source["sha256"], source["size"]), max_bytes=MAX_ORIGINAL_BYTES)
        if source["format"] in {"txt", "md"}:
            parts = [(None, "original", raw.decode("utf-8-sig"), None)]
        else:
            pdf = materials.get_active_pdf_pages(source["source_id"], source["version_id"])
            if (pdf is None or pdf.get("query_ready") is not True
                    or pdf["material"]["revision"] != source["source_revision"]
                    or pdf["material"]["sha256"] != source["sha256"]):
                raise VersionConflict()
            if not 1 <= len(pdf["pages"]) <= 50:
                raise LearningRefusal("learning_scope_limit", "PDF物理页超过有限范围")
            parts = []
            for page in pdf["pages"]:
                parts.append((page["physical_page"], "original", page["raw_text"], None))
                parts.extend((page["physical_page"], "user_supplement", s["text"], s["id"]) for s in page["supplements"])
        for page, origin, text, supplement in parts:
            if not text:
                continue
            text_bytes += len(text.encode("utf-8"))
            if text_bytes > MAX_ORIGINAL_BYTES or len(units) >= 100:
                raise LearningRefusal("learning_scope_limit", "原文文字单元超过有限范围，请缩小资料范围")
            unit = SourceTextUnit(source["source_id"], source["version_id"], source["source_revision"], page, origin, text, True)
            units.append(Unit(source, unit, supplement))
    return tuple(units)


def query_check(query: str, snapshot: dict):
    terms = _terms(query)
    if len(terms) > 24:
        raise LearningRefusal("input_too_large", "问题超过24个词项，请缩短问题")
    if not terms:
        raise LearningRefusal("clarification_required", "请补充要学习的具体概念或问题", kind="clarification")
    titles = {}
    for source in snapshot["sources"]:
        titles.setdefault(source["title"].casefold(), []).append(source)
    if any(len(rows) > 1 for rows in titles.values()) and len(terms) <= 1:
        raise LearningRefusal("clarification_required", "范围中有同名资料，请说明目标领域或使用更明确的资料范围", kind="clarification")
    if query.casefold().strip() == "spring" and len(snapshot["sources"]) > 1:
        raise LearningRefusal("clarification_required", "Spring可能指不同领域，请说明要学习的领域或具体概念", kind="clarification")


def assemble_catalog(query: str, units: tuple[Unit, ...], request_sha256: str) -> list[CatalogEntry]:
    fragments = []
    lookup = {}
    for item in units:
        try:
            parts = build_fragments(item.unit, max_fragments=512)
        except ValueError:
            raise LearningRefusal("learning_scope_limit", "原文或片段超过有限读取边界，请缩小资料范围") from None
        if len(fragments) + len(parts) > 512:
            raise LearningRefusal("learning_scope_limit", "资料超过512片段，请缩小资料范围")
        for fragment in parts:
            if not verify_fragment(item.unit, fragment):
                raise LearningRefusal("integrity_error", "原文片段完整性检查失败")
            # 补充片段也按真实单元定位，不与PDF原文混合。
            if fragment.evidence_id in lookup:
                raise LearningRefusal("integrity_error", "资料中有无法区分的重复证据身份，请缩小范围")
            lookup[fragment.evidence_id] = item
        fragments.extend(parts)
    candidates = rank_term_candidates(query, tuple(fragments),
        allowed_versions=frozenset((u.unit.source_id, u.unit.version_id) for u in units), top_k=8)
    if not candidates:
        raise LearningRefusal("no_evidence", "有限词项检索没有找到相关证据；请明确问题或调整资料范围", kind="no_evidence")
    entries = []
    for candidate in candidates:
        f = candidate.fragment
        item = lookup[f.evidence_id]
        entries.append(CatalogEntry(source_id=f.source_id, version_id=f.version_id, source_revision=f.source_revision,
            citation_id="lc_" + sha(request_sha256 + f.evidence_id)[:24], evidence_id=f.evidence_id,
            title=item.source["title"], format=item.source["format"], original_sha256=item.source["sha256"],
            unit_sha256=sha(item.unit.text), fragment_sha256=f.text_sha256, start_line=f.start_line,
            end_line=f.end_line, start_offset=f.start_offset, end_offset=f.end_offset,
            physical_page=f.physical_page, origin_kind=f.origin_kind, supplement_id=item.supplement_id, text=f.text))
    if sum(len(e.text) for e in entries) > 12000 or sum(len(e.text.encode("utf-8")) for e in entries) > 24000:
        raise LearningRefusal("learning_context_limit", "候选证据超过单次限额，请缩小问题或活动范围")
    return entries


async def read_citation(ledger, materials, originals, activity_id, operation_id, citation_id):
    import json
    from app.retrieval.evidence import EvidenceFragment
    from .contracts import read_document
    snapshot = await ledger.read_committed_result(activity_id, operation_id)
    if snapshot.read_status.value not in {"committed_current", "committed_history_cancelled"}:
        raise LearningRefusal("citation_unavailable", "引用已失效或成果未提交，不能以当前新版本冒充原引用")
    profile, _ = read_document(json.loads(snapshot.payload)["value"], activity_id=activity_id, operation_id=operation_id)
    entry = next((e for e in profile.catalog if e.citation_id == citation_id), None)
    if entry is None:
        raise LearningRefusal("citation_not_found", "该引用不属于此成果")
    # 跨不同读取不声称共同SQL快照；最后再次复核持久资格。
    scope = await ledger.read_learning_snapshot(activity_id)
    validate_snapshot(scope, for_call=False)
    if scope["scope_revision"] != profile.scope_revision:
        raise LearningRefusal("citation_unavailable", "活动范围已变化，引用不可用")
    selected = [s for s in scope["sources"] if s["source_id"] == entry.source_id and s["version_id"] == entry.version_id
        and s["source_revision"] == entry.source_revision and s["sha256"] == entry.original_sha256]
    if len(selected) != 1:
        raise LearningRefusal("citation_unavailable", "原资料身份已变化，引用不可用")
    bounded_scope = {**scope, "source_count": 1, "sources": selected}
    units = await asyncio.to_thread(load_units, bounded_scope, materials, originals)
    item = next((u for u in units if u.unit.physical_page == entry.physical_page
        and u.unit.origin_kind == entry.origin_kind and u.supplement_id == entry.supplement_id), None)
    fragment = EvidenceFragment(entry.evidence_id, entry.source_id, entry.version_id, entry.source_revision,
        entry.physical_page, entry.origin_kind, entry.start_line, entry.end_line,
        entry.start_offset, entry.end_offset, entry.fragment_sha256, entry.text)
    if item is None or sha(item.unit.text) != entry.unit_sha256 or not verify_fragment(item.unit, fragment):
        raise LearningRefusal("citation_unavailable", "原文hash或位置检查失败，引用不可用")
    after = await ledger.read_committed_result(activity_id, operation_id)
    if after.read_status.value not in {"committed_current", "committed_history_cancelled"} or after.payload_sha256 != snapshot.payload_sha256:
        raise LearningRefusal("citation_unavailable", "读取期间资料或成果资格已变化，请刷新核对")
    return {"citation": entry.model_dump(), "read_at": datetime.now(timezone.utc).isoformat()}
