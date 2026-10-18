"""learning.v1受信应用上下文与低信任模型输出的严格合同。"""
from __future__ import annotations

import hashlib
import json
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PROFILE = "learning.v1"
FIRST_PREFIX = "learn-first-v1."
NEXT_PREFIX = "learn-next-v1."
MAX_INPUT_CHARS = 1024
MAX_INPUT_BYTES = 4096
LIMITATIONS = [
    "当前使用有限词项检索，召回可能遗漏；未启用向量检索。",
    "引用身份、版本和位置可核对，不代表结论已独立验证。",
    "资料及模型文字不能授权工具；本次不使用工具。",
]


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_input(value: str) -> str:
    if type(value) is not str:
        raise ValueError("invalid_input")
    value = value.strip()
    if not value or "\x00" in value:
        raise ValueError("invalid_input")
    if len(value) > MAX_INPUT_CHARS or len(value.encode("utf-8")) > MAX_INPUT_BYTES:
        raise ValueError("input_too_large")
    return value


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class SourceIdentity(Strict):
    source_id: str
    version_id: str
    source_revision: int = Field(ge=0, le=2_147_483_647)

    @field_validator("source_id", "version_id")
    @classmethod
    def uuid_value(cls, value: str) -> str:
        if str(UUID(value)) != value:
            raise ValueError("invalid_source_identity")
        return value


class CatalogEntry(SourceIdentity):
    citation_id: str = Field(pattern=r"^lc_[0-9a-f]{24}$")
    evidence_id: str = Field(pattern=r"^ev_[0-9a-f]{64}$")
    title: str = Field(min_length=1, max_length=512)
    format: Literal["txt", "md", "pdf"]
    original_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    unit_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    fragment_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    start_line: int = Field(ge=1, le=5_242_881)
    end_line: int = Field(ge=1, le=5_242_881)
    start_offset: int = Field(ge=0, le=5_242_880)
    end_offset: int = Field(ge=1, le=5_242_880)
    physical_page: int | None = Field(default=None, ge=1, le=50)
    origin_kind: Literal["original", "user_supplement"]
    supplement_id: str | None = None
    text: str = Field(min_length=1, max_length=2048)

    @model_validator(mode="after")
    def validate_fragment(self):
        from app.retrieval.evidence import EvidenceFragment, _evidence_id
        if (self.start_line > self.end_line or self.start_offset >= self.end_offset
                or self.end_offset - self.start_offset != len(self.text)
                or sha(self.text) != self.fragment_sha256):
            raise ValueError("invalid_fragment")
        if (self.format == "pdf") != (self.physical_page is not None):
            raise ValueError("invalid_fragment_location")
        if self.origin_kind == "user_supplement":
            if self.format != "pdf" or self.supplement_id is None or str(UUID(self.supplement_id)) != self.supplement_id:
                raise ValueError("invalid_supplement_identity")
        elif self.supplement_id is not None:
            raise ValueError("invalid_supplement_identity")
        fragment = EvidenceFragment(self.evidence_id, self.source_id, self.version_id,
            self.source_revision, self.physical_page, self.origin_kind, self.start_line,
            self.end_line, self.start_offset, self.end_offset, self.fragment_sha256, self.text)
        if _evidence_id(fragment) != self.evidence_id:
            raise ValueError("invalid_evidence_identity")
        return self


def request_fingerprint(*, action, activity_id, goal, question, scope_revision, sources,
                        parent_operation_id, parent_payload_sha256, max_output_tokens):
    return sha(canonical({
        "profile": PROFILE, "action": action, "activity_id": activity_id,
        "goal": goal, "question": question, "scope_revision": scope_revision,
        "sources": [s.model_dump() if isinstance(s, SourceIdentity) else s for s in sources],
        "parent_operation_id": parent_operation_id, "parent_payload_sha256": parent_payload_sha256,
        "max_output_tokens": max_output_tokens,
    }))


class LearningProfile(Strict):
    profile: Literal["learning.v1"] = PROFILE
    action: Literal["first", "followup"]
    activity_id: str
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    goal: str = Field(min_length=1, max_length=MAX_INPUT_CHARS)
    question: str | None = Field(default=None, min_length=1, max_length=MAX_INPUT_CHARS)
    scope_revision: int = Field(ge=1, le=2_147_483_647)
    sources: list[SourceIdentity] = Field(min_length=1, max_length=10)
    parent_operation_id: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")
    parent_payload_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    history: str | None = Field(default=None, min_length=1, max_length=16384)
    max_output_tokens: int = Field(ge=1, le=256)
    retrieval_mode: Literal["terms.v1"] = "terms.v1"
    catalog: list[CatalogEntry] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def validate_context(self):
        if str(UUID(self.activity_id)) != self.activity_id or normalize_input(self.goal) != self.goal:
            raise ValueError("invalid_learning_context")
        if self.question is not None and normalize_input(self.question) != self.question:
            raise ValueError("invalid_learning_context")
        if (self.action == "first" and any(x is not None for x in
                (self.question, self.parent_operation_id, self.parent_payload_sha256, self.history))):
            raise ValueError("mixed_learning_action")
        if self.action == "followup" and any(x is None for x in
                (self.question, self.parent_operation_id, self.parent_payload_sha256, self.history)):
            raise ValueError("missing_learning_parent")
        identities = [s.model_dump() for s in self.sources]
        if (len({s.source_id for s in self.sources}) != len(self.sources)
                or identities != sorted(identities, key=lambda x: x["source_id"])):
            raise ValueError("invalid_learning_scope")
        args = self.model_dump(exclude={"profile", "request_sha256", "catalog", "retrieval_mode", "history"})
        if request_fingerprint(**args) != self.request_sha256:
            raise ValueError("invalid_learning_fingerprint")
        allowed = {(s.source_id, s.version_id, s.source_revision) for s in self.sources}
        seen = set()
        for entry in self.catalog:
            if ((entry.source_id, entry.version_id, entry.source_revision) not in allowed
                    or entry.citation_id in seen
                    or entry.citation_id != "lc_" + sha(self.request_sha256 + entry.evidence_id)[:24]):
                raise ValueError("invalid_learning_catalog")
            seen.add(entry.citation_id)
        if sum(len(e.text) for e in self.catalog) > 12000 or sum(len(e.text.encode("utf-8")) for e in self.catalog) > 24000:
            raise ValueError("learning_context_limit")
        return self


class Segment(Strict):
    text: str = Field(min_length=1, max_length=1024)
    citations: list[str] = Field(min_length=1, max_length=4)


class LearningOutput(Strict):
    kind: Literal["answer", "clarification", "no_evidence", "conflict"]
    message: str = Field(min_length=1, max_length=1024)
    segments: list[Segment] = Field(max_length=6)
    questions: list[str] = Field(max_length=3)

    @model_validator(mode="after")
    def validate_shape(self):
        if any(not q.strip() or len(q) > 512 for q in self.questions):
            raise ValueError("invalid_learning_questions")
        if self.kind == "answer" and (not self.segments or self.questions):
            raise ValueError("invalid_learning_answer")
        if self.kind == "clarification" and (not self.questions or self.segments):
            raise ValueError("invalid_learning_clarification")
        if self.kind == "no_evidence" and self.segments:
            raise ValueError("invalid_learning_no_evidence")
        if self.kind == "conflict" and not self.segments:
            raise ValueError("invalid_learning_conflict")
        if len(canonical(self.model_dump()).encode("utf-8")) > 16384:
            raise ValueError("learning_output_limit")
        return self


class StoredProfile(Strict):
    """持久业务上下文不携父消费摘要、凭证或历史正文副本。"""
    profile: Literal["learning.v1"]
    action: Literal["first", "followup"]
    activity_id: str
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    goal: str = Field(min_length=1, max_length=MAX_INPUT_CHARS)
    question: str | None = Field(min_length=1, max_length=MAX_INPUT_CHARS)
    scope_revision: int = Field(ge=1, le=2_147_483_647)
    sources: list[SourceIdentity] = Field(min_length=1, max_length=10)
    parent_operation_id: str | None = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")
    max_output_tokens: int = Field(ge=1, le=256)
    retrieval_mode: Literal["terms.v1"]
    catalog: list[CatalogEntry] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def validate_stored(self):
        if str(UUID(self.activity_id)) != self.activity_id or normalize_input(self.goal) != self.goal:
            raise ValueError("invalid_learning_document")
        if self.action == "first":
            if self.question is not None or self.parent_operation_id is not None:
                raise ValueError("invalid_learning_document")
            # 首次摘要不依赖任何消费凭证，可完整复算。
            LearningProfile(**self.model_dump(), parent_payload_sha256=None, history=None)
        elif self.question is None or self.parent_operation_id is None or normalize_input(self.question) != self.question:
            raise ValueError("invalid_learning_document")
        identities = [s.model_dump() for s in self.sources]
        if len({s.source_id for s in self.sources}) != len(self.sources) or identities != sorted(identities,key=lambda s:s["source_id"]):
            raise ValueError("invalid_learning_scope")
        allowed={(s.source_id,s.version_id,s.source_revision) for s in self.sources}
        ids=set()
        for e in self.catalog:
            if ((e.source_id,e.version_id,e.source_revision) not in allowed or e.citation_id in ids
                    or e.citation_id!="lc_"+sha(self.request_sha256+e.evidence_id)[:24]):
                raise ValueError("invalid_learning_catalog")
            ids.add(e.citation_id)
        if sum(len(e.text) for e in self.catalog)>12000 or sum(len(e.text.encode("utf-8")) for e in self.catalog)>24000:
            raise ValueError("learning_context_limit")
        # 续问摘要的父正文绑定由受信profile及G4在提交前完成；存储后依赖
        # G3封套hash与同活动只读资格，不把内部消费凭证再复制到业务JSON。
        return self


def validated_output(profile, value):
    result = LearningOutput.model_validate(value)
    catalog = {e.citation_id: e for e in profile.catalog}
    cited_sources = set()
    for segment in result.segments:
        if not segment.text.strip() or len(set(segment.citations)) != len(segment.citations):
            raise ValueError("invalid_learning_citations")
        for citation in segment.citations:
            if citation not in catalog:
                raise ValueError("invalid_learning_citation")
            cited_sources.add(catalog[citation].source_id)
    if result.kind == "conflict" and len(cited_sources) < 2:
        raise ValueError("invalid_learning_conflict")
    return result


def normalize_result(profile: LearningProfile, value: object) -> dict:
    profile = LearningProfile.model_validate(profile.model_dump())
    result = validated_output(profile,value)
    stored = StoredProfile.model_validate(profile.model_dump(exclude={"parent_payload_sha256", "history"}))
    return {**stored.model_dump(), "result": result.model_dump(), "limitations": list(LIMITATIONS)}


def parse_output(raw: str) -> object:
    if len(raw.encode("utf-8")) > 16384:
        raise ValueError("learning_output_limit")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_learning_field")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid_learning_number")))


def read_document(value: object, *, activity_id=None, operation_id=None) -> tuple[StoredProfile, LearningOutput]:
    if type(value) is not dict or set(value) != set(StoredProfile.model_fields) | {"result", "limitations"}:
        raise ValueError("invalid_learning_document")
    profile = StoredProfile.model_validate({k: value[k] for k in StoredProfile.model_fields})
    if activity_id is not None and profile.activity_id != activity_id:
        raise ValueError("invalid_learning_document_identity")
    if operation_id is not None:
        if profile.action == "first":
            valid = operation_id == FIRST_PREFIX + profile.request_sha256
        else:
            prefix, separator, digest = operation_id.rpartition(".")
            key = prefix.removeprefix(NEXT_PREFIX)
            try:
                valid = (prefix.startswith(NEXT_PREFIX) and str(UUID(key)) == key
                    and separator == "." and digest == profile.request_sha256)
            except (ValueError, AttributeError, TypeError):
                valid = False
        if not valid:
            raise ValueError("invalid_learning_document_identity")
    output = validated_output(profile,value["result"])
    if value["limitations"] != LIMITATIONS:
        raise ValueError("invalid_learning_document")
    return profile, output
