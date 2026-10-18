"""纯函数证据片段及词项基线；位置始终指向未改写的输入原文。"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from app.materials.locations import line_spans


MIB = 1024 * 1024
MAX_SOURCE_BYTES = 5 * MIB
MAX_FRAGMENT_CODEPOINTS = 2_048
MAX_FRAGMENTS_PER_UNIT = 2_048
MAX_QUERY_BYTES = 16 * 1024
MAX_QUERY_TERMS = 24
MAX_TOP_K = 50
_ENGLISH_WORD = re.compile(r"[A-Za-z0-9_]+")
_CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


@dataclass(frozen=True)
class SourceTextUnit:
    """一个已确认可学习的原始页或用户补充，不能由 HTTP 自报状态替代。"""

    source_id: str
    version_id: str
    source_revision: int
    physical_page: int | None
    origin_kind: str
    text: str
    ready_for_learning: bool


@dataclass(frozen=True)
class EvidenceFragment:
    evidence_id: str
    source_id: str
    version_id: str
    source_revision: int
    physical_page: int | None
    origin_kind: str
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int
    text_sha256: str
    text: str


@dataclass(frozen=True)
class RetrievalCandidate:
    fragment: EvidenceFragment
    score: int
    matched_terms: tuple[str, ...]


def build_fragments(unit: SourceTextUnit, *, max_fragment_codepoints: int = MAX_FRAGMENT_CODEPOINTS, max_fragments: int = MAX_FRAGMENTS_PER_UNIT) -> tuple[EvidenceFragment, ...]:
    """逐字分片。换行保留在片段内；offset 是 Python Unicode code point 的右开区间。"""
    _validate_unit(unit)
    _bounded_int("max_fragment_codepoints", max_fragment_codepoints, 1, MAX_FRAGMENT_CODEPOINTS)
    _bounded_int("max_fragments", max_fragments, 1, MAX_FRAGMENTS_PER_UNIT)
    fragments: list[EvidenceFragment] = []
    spans = iter(line_spans(unit.text))
    line_start, _line_end = next(spans)
    line_number = 1
    for next_start, _next_end in spans:
        # 此行到下一行开头包含原来的 CRLF/LF/CR；空行的换行也不丢失。
        _append_line_fragments(unit, fragments, line_number, line_start, next_start, max_fragment_codepoints, max_fragments)
        line_start = next_start
        line_number += 1
    _append_line_fragments(unit, fragments, line_number, line_start, len(unit.text), max_fragment_codepoints, max_fragments)
    return tuple(fragments)


def verify_fragment(unit: SourceTextUnit, fragment: EvidenceFragment) -> bool:
    """在同一原文单元中回查来源、版本、位置、摘要和可复算 ID。"""
    try:
        _validate_unit(unit)
        if not unit.ready_for_learning:
            return False
        if (fragment.source_id, fragment.version_id, fragment.source_revision, fragment.physical_page, fragment.origin_kind) != (
            unit.source_id, unit.version_id, unit.source_revision, unit.physical_page, unit.origin_kind
        ):
            return False
        if not 0 <= fragment.start_offset < fragment.end_offset <= len(unit.text):
            return False
        if unit.text[fragment.start_offset:fragment.end_offset] != fragment.text:
            return False
        if _sha256(fragment.text) != fragment.text_sha256:
            return False
        expected_start, expected_end = _line_bounds(unit.text, fragment.start_offset, fragment.end_offset)
        if (fragment.start_line, fragment.end_line) != (expected_start, expected_end):
            return False
        return fragment.evidence_id == _evidence_id(fragment)
    except (TypeError, ValueError):
        return False


def rank_term_candidates(query: str, fragments: tuple[EvidenceFragment, ...], *, allowed_versions: frozenset[tuple[str, str]], top_k: int = 10) -> tuple[RetrievalCandidate, ...]:
    """范围先过滤的中英词项候选排序；空结果代表本通道没有证据。"""
    if not isinstance(query, str):
        raise ValueError("查询必须是文字")
    if len(query.encode("utf-8")) > MAX_QUERY_BYTES:
        raise ValueError("查询超过16 KiB上限")
    _bounded_int("top_k", top_k, 1, MAX_TOP_K)
    if not isinstance(allowed_versions, frozenset) or not all(_valid_scope(item) for item in allowed_versions):
        raise ValueError("允许范围必须是来源和版本的冻结集合")
    terms = _terms(query)
    if len(terms) > MAX_QUERY_TERMS:
        raise ValueError("查询词项数量超过上限")
    ranked: list[RetrievalCandidate] = []
    for fragment in fragments:
        if (fragment.source_id, fragment.version_id) not in allowed_versions:
            continue
        lowered = fragment.text.casefold()
        matched = tuple(term for term in terms if term in lowered)
        if matched:
            score = sum(lowered.count(term) for term in matched)
            ranked.append(RetrievalCandidate(fragment=fragment, score=score, matched_terms=matched))
    ranked.sort(key=lambda item: (-item.score, item.fragment.evidence_id))
    return tuple(ranked[:top_k])


def _validate_unit(unit: SourceTextUnit) -> None:
    if not isinstance(unit, SourceTextUnit):
        raise ValueError("输入必须是原文文本单元")
    if not all(isinstance(value, str) and value for value in (unit.source_id, unit.version_id)):
        raise ValueError("来源和版本不能为空")
    if type(unit.source_revision) is not int or not 0 <= unit.source_revision <= 2_147_483_647:
        raise ValueError("来源修订号无效")
    if unit.physical_page is not None and (type(unit.physical_page) is not int or unit.physical_page < 1):
        raise ValueError("PDF物理页无效")
    if unit.origin_kind not in {"original", "user_supplement"}:
        raise ValueError("原文身份无效")
    if not isinstance(unit.text, str) or not unit.text:
        raise ValueError("原文必须是非空文字")
    if len(unit.text.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("原文超过5 MiB来源边界")
    if unit.ready_for_learning is not True:
        raise ValueError("未就绪原文不能生成学习证据")


def _fragment(unit: SourceTextUnit, start_line: int, end_line: int, start_offset: int, end_offset: int) -> EvidenceFragment:
    text = unit.text[start_offset:end_offset]
    fragment = EvidenceFragment(
        evidence_id="",
        source_id=unit.source_id,
        version_id=unit.version_id,
        source_revision=unit.source_revision,
        physical_page=unit.physical_page,
        origin_kind=unit.origin_kind,
        start_line=start_line,
        end_line=end_line,
        start_offset=start_offset,
        end_offset=end_offset,
        text_sha256=_sha256(text),
        text=text,
    )
    return EvidenceFragment(**{**fragment.__dict__, "evidence_id": _evidence_id(fragment)})


def _append_line_fragments(unit: SourceTextUnit, fragments: list[EvidenceFragment], line_number: int, start_offset: int, end_offset: int, max_fragment_codepoints: int, max_fragments: int) -> None:
    length = end_offset - start_offset
    required = (length + max_fragment_codepoints - 1) // max_fragment_codepoints
    if len(fragments) + required > max_fragments:
        raise ValueError("证据片段数量超过上限")
    cursor = start_offset
    while cursor < end_offset:
        end = min(cursor + max_fragment_codepoints, end_offset)
        fragments.append(_fragment(unit, line_number, line_number, cursor, end))
        cursor = end


def _evidence_id(fragment: EvidenceFragment) -> str:
    stable = {
        "end_offset": fragment.end_offset,
        "origin_kind": fragment.origin_kind,
        "physical_page": fragment.physical_page,
        "source_id": fragment.source_id,
        "source_revision": fragment.source_revision,
        "start_offset": fragment.start_offset,
        "text_sha256": fragment.text_sha256,
        "version_id": fragment.version_id,
    }
    encoded = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "ev_" + hashlib.sha256(encoded).hexdigest()


def _line_bounds(text: str, start_offset: int, end_offset: int) -> tuple[int, int]:
    if not 0 <= start_offset < end_offset <= len(text):
        raise ValueError("位置不在原文内")
    starts = [start for start, _end in line_spans(text)]

    def line_at(offset: int) -> int:
        # 换行符属于前一行，匹配 materials.locations 的约定。
        for number, start in enumerate(starts[1:], start=1):
            if offset < start:
                return number
        return len(starts)

    return line_at(start_offset), line_at(end_offset - 1)


def _terms(query: str) -> tuple[str, ...]:
    normalized = query.casefold()
    english = _ENGLISH_WORD.findall(normalized)
    cjk_runs = re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+", normalized)
    chinese = [run[index:index + 2] for run in cjk_runs for index in range(len(run) - 1)]
    return tuple(dict.fromkeys((*english, *chinese)))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _bounded_int(name: str, value: object, minimum: int, maximum: int) -> None:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} 超出允许范围")


def _valid_scope(value: object) -> bool:
    return isinstance(value, tuple) and len(value) == 2 and all(isinstance(part, str) and part for part in value)
