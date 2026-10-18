"""G10 closed commands, trusted carrier and bounded, low-trust outputs."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.learning.contracts import CatalogEntry

PROFILE = "interview.v1"
PREFIX = "int10m."
PROMPT_VERSION = "interview.prompt.v1"
ACTIONS = ("start", "goal", "ask", "answer", "correct_answer", "review", "bind_scope", "abandon", "finish")
PHASES = ("needs_goal", "ready", "question_ready", "answer_ready", "feedback_ready", "ended")
STATUSES = ("accepted", "started", "committed", "history", "not_sent", "failed", "unknown", "abandoned")
KINDS = ("start", "goal", "scope", "question", "answer", "probe", "feedback", "finish", "abandon")
MODEL_ACTIONS = frozenset(("ask", "review"))
MAX_COMMAND = 32768
MAX_CONTEXT = 49152
MAX_VALUE = 32768
MAX_RECORDS = MAX_COMMANDS = 4096
MAX_REVISION = 2147483647
Role = Literal["resume", "experience", "measurement", "reference", "unspecified"]
Action = Literal["start", "goal", "ask", "answer", "correct_answer", "review", "bind_scope", "abandon", "finish"]


class InterviewRefusal(ValueError):
    def __init__(self, code: str, message: str = "本次面试操作无法完成", status: int | None = None):
        self.code, self.message, self.status = code, message, status
        super().__init__(code)


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="strict")).hexdigest()


def uuid_text(value: str) -> str:
    if type(value) is not str or str(UUID(value)) != value:
        raise ValueError("interview_invalid_input")
    return value


def text_bound(value: str, chars: int, size: int) -> str:
    if type(value) is not str or not value.strip() or "\x00" in value:
        raise ValueError("interview_invalid_input")
    if len(value) > chars or len(value.encode("utf-8", errors="strict")) > size:
        raise ValueError("interview_invalid_input")
    return value


def load_json(raw: str | bytes) -> Any:
    def unique(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError("interview_invalid_input")
            result[key] = item
        return result
    value = json.loads(raw, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("interview_invalid_input")))
    count = 0
    def visit(item, depth=0):
        nonlocal count
        count += 1
        if depth > 12 or count > 2000:
            raise ValueError("interview_invalid_input")
        if isinstance(item, dict):
            for child in item.values(): visit(child, depth + 1)
        elif isinstance(item, list):
            for child in item: visit(child, depth + 1)
    visit(value)
    return value


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, serialize_by_alias=True)


class SourceRole(Strict):
    source_id: str
    role: Role = "unspecified"
    _id = field_validator("source_id")(uuid_text)


class SourceBinding(Strict):
    source_id: str
    version_id: str
    source_revision: int = Field(ge=1, le=MAX_REVISION)
    original_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    _ids = field_validator("source_id", "version_id")(uuid_text)


class GoalBody(Strict):
    target: str
    focus: str | None = None
    clarifications: list[str] = Field(default_factory=list, max_length=8)
    material_roles: list[SourceRole] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def bounded(self):
        text_bound(self.target, 1024, 4096)
        if self.focus is not None: text_bound(self.focus, 1024, 4096)
        for item in self.clarifications: text_bound(item, 256, 1024)
        if len({x.source_id for x in self.material_roles}) != len(self.material_roles):
            raise ValueError("interview_invalid_input")
        return self


class StartBody(Strict):
    goal: GoalBody | None


class GoalCommandBody(Strict):
    goal: GoalBody


class AskBody(Strict):
    mode: Literal["first", "next"]
    parent_feedback_id: str | None = None
    retry_of: str | None = None
    _ids = field_validator("parent_feedback_id", "retry_of")(lambda v: None if v is None else uuid_text(v))
    @model_validator(mode="after")
    def parent(self):
        if (self.mode == "first") != (self.parent_feedback_id is None):
            raise ValueError("interview_invalid_input")
        return self


class AnswerBody(Strict):
    question_record_id: str
    text: str
    _id = field_validator("question_record_id")(uuid_text)
    _text = field_validator("text")(lambda v: text_bound(v, 4096, 16384))


class CorrectAnswerBody(Strict):
    answer_record_id: str
    expected_answer_version: int = Field(ge=1, le=256)
    text: str
    _id = field_validator("answer_record_id")(uuid_text)
    _text = field_validator("text")(lambda v: text_bound(v, 4096, 16384))


class ReviewBody(Strict):
    question_record_id: str
    answer_record_id: str
    retry_of: str | None = None
    _ids = field_validator("question_record_id", "answer_record_id", "retry_of")(lambda v: None if v is None else uuid_text(v))


class ScopeBody(Strict):
    sources: list[SourceBinding] = Field(min_length=1, max_length=10)
    material_roles: list[SourceRole] = Field(default_factory=list, max_length=10)
    @model_validator(mode="after")
    def distinct(self):
        ids = {s.source_id for s in self.sources}
        if len(ids) != len(self.sources) or len({s.source_id for s in self.material_roles}) != len(self.material_roles) or any(s.source_id not in ids for s in self.material_roles):
            raise ValueError("interview_invalid_input")
        return self


class AbandonBody(Strict):
    pending_key: str
    _id = field_validator("pending_key")(uuid_text)


class EmptyBody(Strict):
    pass


BODY_TYPES = dict(start=StartBody, goal=GoalCommandBody, ask=AskBody, answer=AnswerBody,
                  correct_answer=CorrectAnswerBody, review=ReviewBody, bind_scope=ScopeBody,
                  abandon=AbandonBody, finish=EmptyBody)


class InterviewCommandInput(Strict):
    schema_id: Literal["interview.command.v1"] = Field(default="interview.command.v1", alias="schema")
    business_key: str
    action: Action
    expected_head_revision: int = Field(ge=0, le=MAX_REVISION)
    expected_goal_version: int = Field(ge=0, le=32)
    expected_scope_revision: int = Field(ge=1, le=MAX_REVISION)
    body: dict
    _key = field_validator("business_key")(uuid_text)

    @model_validator(mode="after")
    def validate_body(self):
        model = BODY_TYPES[self.action].model_validate(self.body)
        object.__setattr__(self, "body", model.model_dump())
        if self.action == "start":
            if self.expected_head_revision != 0 or self.expected_goal_version != 0: raise ValueError("interview_invalid_input")
        elif self.expected_head_revision == 0: raise ValueError("interview_invalid_input")
        if len(canonical(self.model_dump()).encode("utf-8")) > MAX_COMMAND: raise ValueError("interview_invalid_input")
        return self

    def request_body(self, activity_id: str) -> str:
        data = self.model_dump(exclude={"business_key"})
        data["activity_id"] = uuid_text(activity_id)
        return canonical(data)

    def request_hash(self, activity_id: str) -> str:
        return sha(self.request_body(activity_id))


class InterviewCatalogEntry(CatalogEntry):
    citation_id: str = Field(pattern=r"^ic_[0-9a-f]{24}$")


class RecordRef(Strict):
    record_id: str
    kind: str
    version: int | None = None
    body_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    body: dict
    operation_id: str | None = None
    payload_sha256: str | None = None
    _id = field_validator("record_id")(uuid_text)


class Identity(Strict):
    provider: Literal["deepseek_chat_completions"]
    model: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")


class InterviewLimits(Strict):
    max_output_tokens: int = Field(ge=1, le=2048)
    max_followups_per_round: int = Field(ge=1, le=4)


class InterviewContext(Strict):
    schema_id: Literal["interview.context.v1"] = Field(default="interview.context.v1", alias="schema")
    activity_id: str
    business_key: str
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    action: Literal["ask", "review"]
    expected_head_revision: int = Field(ge=1, le=MAX_REVISION)
    expected_goal_version: int = Field(ge=1, le=32)
    expected_scope_revision: int = Field(ge=1, le=MAX_REVISION)
    goal_record_id: str
    goal_body: GoalBody
    sources: list[SourceBinding] = Field(min_length=1, max_length=10)
    material_roles: list[SourceRole] = Field(min_length=1, max_length=10)
    round_index: int = Field(ge=0, le=4096)
    probe_depth: int = Field(ge=0, le=4)
    parent_record_refs: list[RecordRef] = Field(max_length=12)
    catalog: list[InterviewCatalogEntry] = Field(max_length=12)
    prompt_version: Literal["interview.prompt.v1"] = PROMPT_VERSION
    identity: Identity
    input_policy: Literal["user_statements_not_verified"] = "user_statements_not_verified"
    limits: InterviewLimits
    _ids = field_validator("activity_id", "business_key", "goal_record_id")(uuid_text)
    @model_validator(mode="after")
    def capacity(self):
        if sum(len(x.text.encode("utf-8")) for x in self.catalog) > 8192: raise ValueError("interview_context_too_large")
        answers = [r for r in self.parent_record_refs if r.kind == "answer"]
        if sum(len(canonical(r.body).encode("utf-8")) for r in answers) > 16384: raise ValueError("interview_context_too_large")
        if len(canonical(self.model_dump()).encode("utf-8")) > MAX_CONTEXT: raise ValueError("interview_context_too_large")
        ids={s.source_id for s in self.sources}
        if len(ids)!=len(self.sources) or {s.source_id for s in self.material_roles}!=ids: raise ValueError("interview_binding_invalid")
        if any(c.source_id not in ids for c in self.catalog): raise ValueError("interview_binding_invalid")
        return self


class InterviewProfile(Strict):
    schema_id: Literal["interview.v1"] = Field(default=PROFILE, alias="schema")
    activity_id: str
    business_key: str
    action: Literal["ask", "review"]
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_head_revision: int = Field(ge=1, le=MAX_REVISION)
    goal_version: int = Field(ge=1, le=32)
    scope_revision: int = Field(ge=1, le=MAX_REVISION)
    round_index: int = Field(ge=0, le=4096)
    probe_depth: int = Field(ge=0, le=4)
    goal_record_id: str
    question_record_id: str | None = None
    answer_record_id: str | None = None
    prompt_version: Literal["interview.prompt.v1"] = PROMPT_VERSION
    _ids = field_validator("activity_id", "business_key", "goal_record_id", "question_record_id", "answer_record_id")(lambda v: None if v is None else uuid_text(v))


class InterviewCallBinding(Strict):
    business_key: str
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_head_revision: int = Field(ge=1, le=MAX_REVISION)
    goal_version: int = Field(ge=1, le=32)
    _id = field_validator("business_key")(uuid_text)


class Recognition(Strict):
    answer_record_id: str
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=1)
    answer_excerpt: str
    reference_ids: list[str] = Field(max_length=6)
    semantic_support: Literal["supports", "unclear"]
    explanation: str
    _id = field_validator("answer_record_id")(uuid_text)
    _texts = field_validator("answer_excerpt", "explanation")(lambda v: text_bound(v, 512, 2048))


class Gap(Strict):
    answer_record_id: str
    text: str
    reference_ids: list[str] = Field(default_factory=list, max_length=6)
    _id = field_validator("answer_record_id")(uuid_text)
    _text = field_validator("text")(lambda v: text_bound(v, 512, 2048))


class Conflict(Strict):
    text: str
    reference_ids: list[str] = Field(min_length=2, max_length=6)
    _text = field_validator("text")(lambda v: text_bound(v, 512, 2048))


class QuestionOutput(Strict):
    type: Literal["question"]
    purpose: Literal["interview", "clarification"]
    reason: Literal["topic", "ambiguous_target", "missing_material", "missing_claim_evidence"]
    text: str
    reference_ids: list[str] = Field(max_length=6)
    _text = field_validator("text")(lambda v: text_bound(v, 2048, 8192))


class ProbeOutput(Strict):
    type: Literal["probe"]
    reason: Literal["ambiguous_answer", "missing_claim_evidence", "conflicting_sources"]
    text: str
    recognitions: list[Recognition] = Field(max_length=8)
    gaps: list[Gap] = Field(max_length=8)
    reference_ids: list[str] = Field(max_length=6)
    _text = field_validator("text")(lambda v: text_bound(v, 2048, 8192))


class FeedbackOutput(Strict):
    type: Literal["feedback"]
    summary: str
    recognitions: list[Recognition] = Field(max_length=8)
    gaps: list[Gap] = Field(max_length=8)
    conflicts: list[Conflict] = Field(max_length=4)
    next_steps: list[str] = Field(max_length=4)
    _summary = field_validator("summary")(lambda v: text_bound(v, 1024, 4096))
    @field_validator("next_steps")
    @classmethod
    def steps(cls, values):
        for value in values: text_bound(value, 512, 2048)
        return values


def operation_id(key: str) -> str:
    return PREFIX + UUID(uuid_text(key)).hex


def profile_for(frozen: InterviewContext) -> InterviewProfile:
    refs = {r.kind: r for r in frozen.parent_record_refs}
    return InterviewProfile(activity_id=frozen.activity_id, business_key=frozen.business_key, action=frozen.action,
        request_sha256=frozen.request_sha256, context_sha256=sha(canonical(frozen.model_dump())),
        expected_head_revision=frozen.expected_head_revision, goal_version=frozen.expected_goal_version,
        scope_revision=frozen.expected_scope_revision, round_index=frozen.round_index, probe_depth=frozen.probe_depth,
        goal_record_id=frozen.goal_record_id, question_record_id=(refs.get("probe") or refs.get("question")).record_id if (refs.get("probe") or refs.get("question")) else None,
        answer_record_id=refs["answer"].record_id if "answer" in refs else None)
