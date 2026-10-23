"""teaching.v1 受信教学命令合同与低信任输出严格校验。

依据 TASK-099 合同第 3—5 节实现：封闭命令 DTO、canonical request_body、
semantic_slot、回执、受信 profile、教学输出联合与全部大小边界。
本文件纯校验/纯函数，不联网、不 exec/eval；模型输出只是低信任建议，
任何 trusted goal/scope/version/permission/progress/passed 字段整项拒绝。
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .contracts import Strict, SourceIdentity, CatalogEntry, canonical, sha

TEACHING_PROFILE = "teaching.v1"
TEACHING_PREFIX_MODEL = "teach8m."
TEACHING_PREFIX_TOOL = "teach8t."
STATE_SCHEMA = "teaching.state.v1"
CONTEXT_SCHEMA = "teaching.context.v1"
WORKSPACE_SCHEMA = "teaching.workspace.v1"
PROMPT_VERSION = "teaching-prompt-v1"

# --- 大小边界（099 第 5.3 节；字符按 Unicode 码点，另核 UTF-8 字节） ---
MAX_GOAL_CHARS, MAX_GOAL_BYTES = 1024, 4096
MAX_SELF_REPORT_CHARS, MAX_SELF_REPORT_BYTES = 512, 2048
MAX_DOMAIN_CHARS, MAX_DOMAIN_BYTES = 80, 320
MAX_ANSWER_CHARS, MAX_ANSWER_BYTES = 4096, 12288
MAX_CORRECTION_CHARS, MAX_CORRECTION_BYTES = 1024, 4096
MAX_HTTP_BODY_BYTES = 32768
MAX_REQUEST_BODY_BYTES = 32768
MAX_CONTEXT_BODY_BYTES = 49152
MAX_RECORD_BODY_BYTES = 32768
MAX_STATE_AFTER_BYTES = 8192
MAX_OUTPUT_TOKENS = 2048
MAX_COMMANDS_PER_ACTIVITY = 1024
MAX_GOAL_VERSION = 32
MAX_RECORDS = 4096
MAX_EXERCISES = 128
MAX_ANSWERS = 512
MAX_CORRECTIONS = 128
MAX_PATHS = 32
HISTORY_DEFAULT, HISTORY_MAX = 20, 50
HISTORY_ITEM_BYTES = 512
HISTORY_PAGE_BYTES = 65536
WORKSPACE_ENCODE_BYTES = 196608
PENDING_SUMMARY_ROWS = 8

MODEL_ACTIONS = frozenset({"plan", "exercise", "evaluate"})
TOOL_ACTIONS = frozenset({"calculate"})
LAUNCH_ACTIONS = MODEL_ACTIONS | TOOL_ACTIONS
LOCAL_ACTIONS = frozenset({"goal", "accept_path", "expose", "answer", "correct", "abandon", "select_node"})
ALL_ACTIONS = sorted(MODEL_ACTIONS | TOOL_ACTIONS | LOCAL_ACTIONS)

COMMAND_STATUSES = ("accepted", "started", "committed", "history", "not_sent", "failed", "unknown", "abandoned")
QUALIFICATIONS = ("current", "history_only", "source_invalid", "cancelled", "integrity_error", "unconfirmed", "memory_invalid")
RECORD_KINDS = ("goal", "path_proposal", "path_accept", "exercise", "exposure", "answer", "calculation",
                "feedback", "progress", "correction", "node_selection")
PHASES = ("needs_goal", "needs_plan", "path_review", "ready", "exercise_ready", "answer_saved", "feedback_ready")
EXERCISE_TYPES = ("calculation", "concept", "program")
PURPOSES = ("initial", "continuation", "retest")

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_NODE_ID = re.compile(r"^n[1-6]$")
_ERROR_CODE = re.compile(r"^[A-Za-z0-9._:/-]{1,64}$")


class TeachingRefusal(ValueError):
    """教学域统一拒绝；code 为封闭错误码，message 面向用户。"""

    def __init__(self, code: str, message: str):
        self.code, self.message = code, message
        super().__init__(code)


def _uuid_text(value: str, field: str) -> str:
    if type(value) is not str or str(UUID(value)) != value:
        raise ValueError(f"invalid_{field}")
    return value


def _bounded_text(value: str, *, chars: int, byte_limit: int, strip: bool = True) -> str:
    if type(value) is not str:
        raise ValueError("invalid_input")
    normalized = value.strip() if strip else value
    if "\x00" in value or not normalized or normalized != value.strip():
        raise ValueError("invalid_input")
    if len(value) > chars or len(value.encode("utf-8")) > byte_limit:
        raise ValueError("input_too_large")
    return value


def normalize_goal_text(value: str) -> str:
    if type(value) is not str:
        raise ValueError("invalid_input")
    value = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not value or "\x00" in value:
        raise ValueError("invalid_input")
    if len(value) > MAX_GOAL_CHARS or len(value.encode("utf-8")) > MAX_GOAL_BYTES:
        raise ValueError("input_too_large")
    return value


def normalize_answer_text(value: str) -> str:
    """作答保留缩进/空行；仅拒全空、NUL、孤立代理与超限。"""
    if type(value) is not str:
        raise ValueError("invalid_input")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in value or not value.strip():
        raise ValueError("invalid_input")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("invalid_input") from None
    if len(value) > MAX_ANSWER_CHARS or len(value.encode("utf-8")) > MAX_ANSWER_BYTES:
        raise ValueError("input_too_large")
    return value


# --- O01—O11 各 action body 的封闭判别联合 ---

class GoalBody(Strict):
    goal: str
    self_report: str | None = None
    domain: str | None = None
    seed_operation_id: str | None = Field(default=None, min_length=1, max_length=128,
                                          pattern=r"^[A-Za-z0-9._:/-]+$")
    seed_payload_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def check(self):
        # frozen 严格模型：规范化结果按 Pydantic 语义写入 __dict__，
        # 不绕过 extra=forbid/strict 校验。
        object.__setattr__(self, "goal", normalize_goal_text(self.goal))
        if self.self_report is not None:
            _bounded_text(self.self_report, chars=MAX_SELF_REPORT_CHARS, byte_limit=MAX_SELF_REPORT_BYTES)
        if self.domain is not None:
            _bounded_text(self.domain, chars=MAX_DOMAIN_CHARS, byte_limit=MAX_DOMAIN_BYTES)
        if (self.seed_operation_id is None) != (self.seed_payload_sha256 is None):
            raise ValueError("invalid_input")
        return self


class PlanBody(Strict):
    confirmed: Literal[True]
    correction_record_id: str | None = None
    retry_of: str | None = None

    @field_validator("confirmed", mode="before")
    @classmethod
    def _explicit(cls, value):
        if type(value) is not bool or value is not True:
            raise ValueError("explicit_confirmation_required")
        return value

    @field_validator("correction_record_id", "retry_of")
    @classmethod
    def _uuids(cls, value):
        return None if value is None else _uuid_text(value, "record")


class AcceptPathBody(Strict):
    proposal_record_id: str

    @field_validator("proposal_record_id")
    @classmethod
    def _uuid(cls, value):
        return _uuid_text(value, "record")


class ExerciseBody(Strict):
    confirmed: Literal[True]
    path_record_id: str
    node_id: str = Field(pattern=r"^n[1-6]$")
    purpose: Literal["initial", "continuation", "retest"]
    parent_feedback_record_id: str | None = None
    retry_of: str | None = None

    @field_validator("confirmed", mode="before")
    @classmethod
    def _explicit(cls, value):
        if type(value) is not bool or value is not True:
            raise ValueError("explicit_confirmation_required")
        return value

    @field_validator("path_record_id", "parent_feedback_record_id", "retry_of")
    @classmethod
    def _uuids(cls, value):
        return None if value is None else _uuid_text(value, "record")

    @model_validator(mode="after")
    def check(self):
        if self.purpose == "initial" and self.parent_feedback_record_id is not None:
            raise ValueError("invalid_input")
        if self.purpose in ("continuation", "retest") and self.parent_feedback_record_id is None:
            raise ValueError("invalid_input")
        return self


class ExposeBody(Strict):
    exercise_record_id: str
    part: Literal["hint", "reference"]

    @field_validator("exercise_record_id")
    @classmethod
    def _uuid(cls, value):
        return _uuid_text(value, "record")


class AnswerBody(Strict):
    exercise_record_id: str
    kind: Literal["initial", "continuation", "revision"]
    text: str
    supersedes_answer_record_id: str | None = None

    @field_validator("exercise_record_id", "supersedes_answer_record_id")
    @classmethod
    def _uuids(cls, value):
        return None if value is None else _uuid_text(value, "record")

    @model_validator(mode="after")
    def check(self):
        object.__setattr__(self, "text", normalize_answer_text(self.text))
        if self.kind == "initial" and self.supersedes_answer_record_id is not None:
            raise ValueError("invalid_input")
        if self.kind in ("continuation", "revision") and self.supersedes_answer_record_id is None:
            raise ValueError("invalid_input")
        return self


class CalculateBody(Strict):
    confirmed: Literal[True]
    exercise_record_id: str
    answer_record_id: str
    reference_point_id: str = Field(pattern=r"^p[1-4]$")
    retry_of: str | None = None

    @field_validator("confirmed", mode="before")
    @classmethod
    def _explicit(cls, value):
        if type(value) is not bool or value is not True:
            raise ValueError("explicit_confirmation_required")
        return value

    @field_validator("exercise_record_id", "answer_record_id", "retry_of")
    @classmethod
    def _uuids(cls, value):
        return None if value is None else _uuid_text(value, "record")


class EvaluateBody(Strict):
    confirmed: Literal[True]
    exercise_record_id: str
    answer_record_id: str
    correction_record_id: str | None = None
    retry_of: str | None = None

    @field_validator("confirmed", mode="before")
    @classmethod
    def _explicit(cls, value):
        if type(value) is not bool or value is not True:
            raise ValueError("explicit_confirmation_required")
        return value

    @field_validator("exercise_record_id", "answer_record_id", "correction_record_id", "retry_of")
    @classmethod
    def _uuids(cls, value):
        return None if value is None else _uuid_text(value, "record")


class CorrectBody(Strict):
    target_record_id: str
    text: str
    disputed_dimensions: list[str] = Field(max_length=4)

    @field_validator("target_record_id")
    @classmethod
    def _uuid(cls, value):
        return _uuid_text(value, "record")

    @field_validator("disputed_dimensions")
    @classmethod
    def _dims(cls, value):
        for item in value:
            _bounded_text(item, chars=64, byte_limit=256)
        if len(set(value)) != len(value):
            raise ValueError("invalid_input")
        return value

    @model_validator(mode="after")
    def check(self):
        object.__setattr__(self, "text", _bounded_text(
            self.text, chars=MAX_CORRECTION_CHARS, byte_limit=MAX_CORRECTION_BYTES))
        return self


class AbandonBody(Strict):
    target_business_key: str

    @field_validator("target_business_key")
    @classmethod
    def _uuid(cls, value):
        return _uuid_text(value, "record")


class SelectNodeBody(Strict):
    path_record_id: str
    node_id: str = Field(pattern=r"^n[1-6]$")
    archive_current: bool = False

    @field_validator("path_record_id")
    @classmethod
    def _uuid(cls, value):
        return _uuid_text(value, "record")

    @field_validator("archive_current", mode="before")
    @classmethod
    def _strict_bool(cls, value):
        if type(value) is not bool:
            raise ValueError("invalid_input")
        return value


_BODY_MODELS = {
    "goal": GoalBody, "plan": PlanBody, "accept_path": AcceptPathBody,
    "exercise": ExerciseBody, "expose": ExposeBody, "answer": AnswerBody,
    "calculate": CalculateBody, "evaluate": EvaluateBody, "correct": CorrectBody,
    "abandon": AbandonBody, "select_node": SelectNodeBody,
}


class TeachingCommandInput(Strict):
    """统一命令输入；恰有 business_key、三 CAS 前提、action、body。"""

    business_key: str
    expected_revision: int = Field(ge=0, le=2_147_483_647)
    expected_goal_version: int = Field(ge=0, le=MAX_GOAL_VERSION)
    expected_scope_revision: int = Field(ge=1, le=2_147_483_647)
    action: Literal["goal", "plan", "accept_path", "exercise", "expose", "answer",
                    "calculate", "evaluate", "correct", "abandon", "select_node"]
    body: dict
    retrieval_ref: "RetrievalRef | None" = None

    @field_validator("business_key")
    @classmethod
    def _key(cls, value):
        return _uuid_text(value, "business_key")

    @model_validator(mode="after")
    def check(self):
        if type(self.expected_revision) is not int or type(self.expected_goal_version) is not int \
                or type(self.expected_scope_revision) is not int:
            raise ValueError("invalid_input")
        if self.expected_goal_version == 0 and self.action != "goal":
            raise ValueError("invalid_input")
        body_model = _BODY_MODELS[self.action]
        try:
            validated = body_model.model_validate(self.body)
        except Exception:
            raise ValueError("invalid_input") from None
        object.__setattr__(self, "body", validated.model_dump())
        if self.retrieval_ref is not None and self.action not in MODEL_ACTIONS:raise ValueError('invalid_input')
        return self

    def canonical_request_body(self, activity_id: str) -> dict:
        return {
            "activity_id": _uuid_text(activity_id, "activity_id"),
            "action": self.action,
            "expected_revision": self.expected_revision,
            "expected_goal_version": self.expected_goal_version,
            "expected_scope_revision": self.expected_scope_revision,
            "body": self.body,
            **({'retrieval_ref':self.retrieval_ref.model_dump()} if self.retrieval_ref is not None else {}),
        }

    def request_sha256(self, activity_id: str) -> str:
        return sha(canonical(self.canonical_request_body(activity_id)))

    def operation_id(self, activity_id: str) -> str:
        prefix = TEACHING_PREFIX_TOOL if self.action in TOOL_ACTIONS else TEACHING_PREFIX_MODEL
        return prefix + self.business_key + "." + self.request_sha256(activity_id)


def semantic_slot(activity_id: str, command: TeachingCommandInput, anchors: dict) -> str:
    """业务语义槽 canonical hash：只含 action、scope 身份与父级实体 ID。

    anchors 由调用方（服务端锁前组包）提供：goal_record_id、path_record_id、
    node_id、exercise_record_id、answer_record_id、correction_record_id、
    proposal_record_id、parent_feedback_record_id、target_record_id、
    reference_point_id、part、supersedes_answer_record_id、kind、purpose、
    target_business_key。文本内容与 business_key/retry_of 不进入槽。
    """
    value = {"activity_id": _uuid_text(activity_id, "activity_id"), "action": command.action,
             "scope_revision": command.expected_scope_revision}
    body = command.body
    if command.action == "goal":
        value["goal_record_id"] = anchors.get("goal_record_id")
        value["goal_version"] = command.expected_goal_version
        value["expected_revision"] = command.expected_revision
    elif command.action == "plan":
        value["goal_record_id"] = anchors.get("goal_record_id")
        value["correction_record_id"] = body.get("correction_record_id")
        value["diagnostic_anchor"] = anchors.get("diagnostic_anchor")
    elif command.action == "accept_path":
        value["goal_record_id"] = anchors.get("goal_record_id")
        value["proposal_record_id"] = body.get("proposal_record_id")
    elif command.action == "exercise":
        value["goal_record_id"] = anchors.get("goal_record_id")
        value["path_record_id"] = body.get("path_record_id")
        value["node_id"] = body.get("node_id")
        value["purpose"] = body.get("purpose")
        value["parent_feedback_record_id"] = body.get("parent_feedback_record_id")
        value["reason_record_id"] = anchors.get("reason_record_id")
    elif command.action == "expose":
        value["exercise_record_id"] = body.get("exercise_record_id")
        value["part"] = body.get("part")
    elif command.action == "answer":
        value["exercise_record_id"] = body.get("exercise_record_id")
        value["supersedes_answer_record_id"] = body.get("supersedes_answer_record_id")
    elif command.action == "calculate":
        value["exercise_record_id"] = body.get("exercise_record_id")
        value["answer_record_id"] = body.get("answer_record_id")
        value["reference_point_id"] = body.get("reference_point_id")
    elif command.action == "evaluate":
        value["exercise_record_id"] = body.get("exercise_record_id")
        value["answer_record_id"] = body.get("answer_record_id")
        value["correction_record_id"] = body.get("correction_record_id")
    elif command.action == "correct":
        value["target_record_id"] = body.get("target_record_id")
        value["expected_revision"] = command.expected_revision
    elif command.action == "abandon":
        value["target_business_key"] = body.get("target_business_key")
    elif command.action == "select_node":
        value["path_record_id"] = body.get("path_record_id")
        value["node_id"] = body.get("node_id")
        value["expected_revision"] = command.expected_revision
    # 出口统一归一：UUID 等非原生类型一律转文本，None 保持 None。
    # 语义槽只允许由可序列化的身份文本决定，否则同槽判定会因调用方
    # 传参形态不同而漂移（这正是去重与竞争裁决的基础）。
    normalized = {key: (None if item is None else
                        item if isinstance(item, (str, int, bool)) else str(item))
                  for key, item in value.items()}
    return sha(canonical(normalized))


# --- 命令回执（099 第 5.1 节） ---

class RecordRef(Strict):
    record_id: str
    kind: str
    seq: int = Field(ge=1, le=MAX_RECORDS)

    @field_validator("record_id")
    @classmethod
    def _uuid(cls, value):
        return _uuid_text(value, "record")

    @field_validator("kind")
    @classmethod
    def _kind(cls, value):
        if value not in RECORD_KINDS:
            raise ValueError("invalid_input")
        return value


class TeachingCommandReceipt(Strict):
    activity_id: str
    business_key: str
    action: str
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    status: Literal["accepted", "started", "committed", "history", "not_sent", "failed", "unknown", "abandoned"]
    duplicate_of: str | None = None
    record_ids: list[RecordRef] = Field(max_length=4)
    operation_id: str | None = None
    payload_sha256: str | None = None
    applied_revision: int | None = Field(default=None, ge=1, le=2_147_483_647)
    head_revision_now: int = Field(ge=0)
    qualification: Literal["current", "history_only", "source_invalid", "cancelled",
                           "integrity_error", "unconfirmed", "memory_invalid"] = "current"
    error_code: str | None = Field(default=None, pattern=r"^[A-Za-z0-9._:/-]{1,64}$")
    model_called: bool | None = None
    tool_called: bool | None = None
    retry_policy: Literal["none", "same_key_before_claim", "explicit_new_key_after_confirmed_failure",
                          "read_only"] = "none"
    exposed_part: dict | None = None
    outbound_approval: dict | None = None


# --- 受信内部 profile（099 第 5.2 节） ---

class TeachingProfile(Strict):
    """受信教学调用 profile；不携完整作答与前史（避免双份答案）。"""

    profile: Literal["teaching.v1"] = TEACHING_PROFILE
    action: Literal["plan", "exercise", "evaluate"]
    command_key: str
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    activity_id: str
    expected_revision: int = Field(ge=0)
    goal_record_id: str
    goal_version: int = Field(ge=1, le=MAX_GOAL_VERSION)
    path_record_id: str | None = None
    node_id: str | None = Field(default=None, pattern=r"^n[1-6]$")
    exercise_record_id: str | None = None
    answer_record_id: str | None = None
    correction_record_id: str | None = None
    scope_revision: int = Field(ge=1)
    sources: list[SourceIdentity] = Field(min_length=1, max_length=10)
    catalog: list[CatalogEntry] = Field(min_length=1, max_length=4)
    messages_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    max_output_tokens: int = Field(ge=1, le=MAX_OUTPUT_TOKENS)

    @field_validator("command_key", "activity_id", "goal_record_id", "path_record_id",
                     "exercise_record_id", "answer_record_id", "correction_record_id")
    @classmethod
    def _uuids(cls, value):
        return None if value is None else _uuid_text(value, "record")

    @model_validator(mode="after")
    def check(self):
        identities = [s.model_dump() for s in self.sources]
        if len({s.source_id for s in self.sources}) != len(self.sources) \
                or identities != sorted(identities, key=lambda x: x["source_id"]):
            raise ValueError("invalid_teaching_scope")
        allowed = {(s.source_id, s.version_id, s.source_revision) for s in self.sources}
        seen = set()
        for entry in self.catalog:
            if ((entry.source_id, entry.version_id, entry.source_revision) not in allowed
                    or entry.citation_id in seen
                    or entry.citation_id != "lc_" + sha(self.request_sha256 + entry.evidence_id)[:24]):
                raise ValueError("invalid_teaching_catalog")
            seen.add(entry.citation_id)
        if sum(len(e.text) for e in self.catalog) > 4000 or sum(len(e.text.encode("utf-8")) for e in self.catalog) > 8000:
            raise ValueError("teaching_context_limit")
        return self


class TeachingCallBinding(Strict):
    """由 gateway 受信 profile 构造的准入绑定；公开 API 不能直接构造。"""

    command_key: str
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_revision: int = Field(ge=0)
    goal_version: int = Field(ge=1, le=MAX_GOAL_VERSION)

    @field_validator("command_key")
    @classmethod
    def _key(cls, value):
        return _uuid_text(value, "business_key")


class ReferenceHash(Strict):
    record_id: str
    body_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("record_id")
    @classmethod
    def _uuid(cls, value):
        return _uuid_text(value, "record")


class ToolFrozenCall(Strict):
    call_id: str
    name: Literal["finite_calculate"]
    arguments_json: str = Field(min_length=1, max_length=2048)
    arguments_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class TeachingFrozenContext(Strict):
    """锁前冻结上下文；model/tool 判别联合。"""

    schema_: Literal["teaching.context.v1"] = Field(alias="schema", default=CONTEXT_SCHEMA)
    kind: Literal["model", "tool"]
    reference_hashes: list[ReferenceHash] = Field(max_length=12)
    operation_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    profile_version: Literal["teaching.v1"] | None = None
    prompt_version: str | None = None
    max_output_tokens: int | None = Field(default=None, ge=1, le=MAX_OUTPUT_TOKENS)
    messages: list[dict] | None = None
    catalog: list[CatalogEntry] | None = None
    call: ToolFrozenCall | None = None

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, populate_by_name=True)

    @model_validator(mode="after")
    def check(self):
        if self.kind == "model":
            if (self.profile_version is None or self.prompt_version is None
                    or self.max_output_tokens is None or self.messages is None
                    or self.catalog is None or self.call is not None):
                raise ValueError("invalid_input")
            if len(self.messages) > 3:
                raise ValueError("invalid_input")
        else:
            if (self.profile_version is not None or self.prompt_version is not None
                    or self.max_output_tokens is not None or self.messages is not None
                    or self.catalog is not None or self.call is None):
                raise ValueError("invalid_input")
        return self


class TeachingLaunchDecision(Strict):
    launch_allowed: bool
    receipt: TeachingCommandReceipt


def frozen_context_digest(frozen: TeachingFrozenContext) -> str:
    return sha(canonical(frozen.model_dump(by_alias=True, exclude={"context_sha256"})))


def stored_teaching_result(profile: TeachingProfile, result: dict, messages) -> dict:
    """服务端封套身份取受信 profile，低信任结果另行核引用及答案片段。"""
    catalog_ids = {e.citation_id for e in profile.catalog}
    def check_citations(value):
        if isinstance(value, dict):
            if "citations" in value and any(c not in catalog_ids for c in value["citations"]):
                raise ValueError("invalid_teaching_citation")
            for child in value.values():
                check_citations(child)
        elif isinstance(value, list):
            for child in value:
                check_citations(child)
    check_citations(result)
    user = json.loads(next(m.content for m in reversed(messages) if m.role == "user"))
    task = user.get("task", {})
    if result["result_type"] == "exercise":
        variant = result["variant"]
        for field in ("purpose", "parent_exercise_record_id", "parent_feedback_record_id"):
            if variant.get(field) != task.get(field):
                raise ValueError("invalid_teaching_variant")
    if result["result_type"] == "feedback":
        exercise = task["exercise"]
        points = {p["point_id"] for p in exercise["reference_points"]}
        dimensions = {d["id"] for d in exercise["dimensions"]}
        for field in ("correct_parts", "errors", "evidence_gaps"):
            for item in result[field]:
                if item["answer_excerpt"] not in task["answer_text"] or any(p not in points for p in item["point_ids"]):
                    raise ValueError("invalid_teaching_answer_reference")
        if any(d["id"] not in dimensions or any(p not in points for p in d["point_ids"])
               for d in result["dimension_observations"]):
            raise ValueError("invalid_teaching_dimension")
    value = profile.model_dump(exclude={"sources", "messages_sha256", "max_output_tokens"})
    value["limitations"] = ["模型评价是有限建议；引用身份不等于语义已经独立验证。", "程序题只阅读推理，不执行代码。"]
    value["result"] = result
    if len(canonical(value).encode("utf-8")) > MAX_RECORD_BODY_BYTES:
        raise ValueError("teaching_output_limit")
    return value


class TeachingSupervisionFacts(Strict):
    """原监督观察事实；不接受客户端陈述恢复。"""

    state: str = Field(min_length=1, max_length=64)
    definitely_not_admitted: bool
    model_receipt: dict | None = None
    tool_receipt: dict | None = None
    settled_seconds: int | None = Field(default=None, ge=0)
    reserved_seconds: int | None = Field(default=None, ge=0)
    pending_fold_seconds: int | None = Field(default=None, ge=0)
    cleanup_incomplete: bool = False


# --- 低信任模型输出封闭联合（099 第 5.2 节） ---

_TRUSTED_KEYS = frozenset({"passed", "mastered", "trusted", "permission", "permissions",
                           "catalog", "goal_version", "progress", "scope", "authority", "budget"})


def _reject_trusted_fields(value: dict):
    for key in value:
        if key in _TRUSTED_KEYS:
            raise ValueError("trusted_field_rejected")


class PathNode(Strict):
    title: str = Field(min_length=1, max_length=80)
    objective: str = Field(min_length=1, max_length=160)
    prerequisites: list[int] = Field(max_length=5)
    rationale: str = Field(min_length=1, max_length=240)
    citations: list[str] = Field(min_length=1, max_length=4)
    completion_dimensions: list[dict] = Field(min_length=1, max_length=4)

    @field_validator("citations")
    @classmethod
    def _citations(cls, value):
        if len(set(value)) != len(value):
            raise ValueError("invalid_input")
        return value

    @model_validator(mode="after")
    def check(self):
        for dimension in self.completion_dimensions:
            if set(dimension) != {"dimension", "required_point"}:
                raise ValueError("invalid_input")
            if not isinstance(dimension["dimension"], str) or not 1 <= len(dimension["dimension"]) <= 64:
                raise ValueError("invalid_input")
            if not isinstance(dimension["required_point"], str) or not 1 <= len(dimension["required_point"]) <= 160:
                raise ValueError("invalid_input")
        seen = {d["dimension"] for d in self.completion_dimensions}
        if len(seen) != len(self.completion_dimensions) or any(p < 0 for p in self.prerequisites):
            raise ValueError("invalid_input")
        return self


class PathOutput(Strict):
    result_type: Literal["path"]
    message: str = Field(min_length=1, max_length=256)
    nodes: list[PathNode] = Field(min_length=1, max_length=6)

    @model_validator(mode="after")
    def check(self):
        _reject_trusted_fields(self.model_dump())
        for index, node in enumerate(self.nodes):
            if any(p >= index for p in node.prerequisites):
                raise ValueError("invalid_path_prerequisites")
        return self


class NumericRef(Strict):
    value_decimal: str
    unit: str | None = Field(default=None, min_length=1, max_length=32)
    operation: Literal["add", "subtract", "multiply", "divide", "power"]
    left: str
    right: str
    tolerance_decimal: str | None = Field(default=None, min_length=1, max_length=32)

    @field_validator("value_decimal", "left", "right", "tolerance_decimal")
    @classmethod
    def _decimal(cls, value, info):
        from decimal import Decimal, InvalidOperation
        if value is None:
            return value
        if not re.fullmatch(r"-?[0-9]+(\.[0-9]+)?", value):
            raise ValueError("invalid_input")
        try:
            number = Decimal(value)
        except InvalidOperation:
            raise ValueError("invalid_input") from None
        maximum = Decimal("1e18") if info.field_name == "value_decimal" else Decimal("1e12")
        if (not number.is_finite() or number.copy_abs() > maximum
                or info.field_name == "tolerance_decimal" and
                (number < 0 or number > 1 or number.as_tuple().exponent < -12)):
            raise ValueError("invalid_input")
        return value


class ReferencePoint(Strict):
    point_id: str = Field(pattern=r"^p[1-4]$")
    text: str = Field(min_length=1, max_length=240)
    citations: list[str] = Field(min_length=1, max_length=4)
    numeric: NumericRef | None = None

    @field_validator("citations")
    @classmethod
    def _citations(cls, value):
        if len(set(value)) != len(value):
            raise ValueError("invalid_input")
        return value


class DimensionSpec(Strict):
    id: str = Field(min_length=1, max_length=64)
    point_ids: list[str] = Field(min_length=1, max_length=4)
    description: str = Field(min_length=1, max_length=160)


class VariantData(Strict):
    purpose: Literal["initial", "continuation", "retest"]
    parent_exercise_record_id: str | None = None
    parent_feedback_record_id: str | None = None
    instance_data: dict

    @field_validator("parent_exercise_record_id", "parent_feedback_record_id")
    @classmethod
    def _uuids(cls, value):
        return None if value is None else _uuid_text(value, "record")

    @model_validator(mode="after")
    def check(self):
        if self.purpose == "initial" and (self.parent_exercise_record_id is not None
                                          or self.parent_feedback_record_id is not None):
            raise ValueError("invalid_input")
        if self.purpose in ("continuation", "retest") and (self.parent_exercise_record_id is None
                                                           or self.parent_feedback_record_id is None):
            raise ValueError("invalid_input")
        _validate_instance_data(self.instance_data)
        return self


def _validate_instance_data(data: dict) -> None:
    """instance_data 封闭签名：calculation/concept/program 三类。"""
    if type(data) is not dict:
        raise ValueError("invalid_input")
    kind = data.get("kind")
    if kind == "calculation":
        if set(data) != {"kind", "quantities"} or not 1 <= len(data["quantities"]) <= 8:
            raise ValueError("invalid_input")
        names = set()
        for item in data["quantities"]:
            if set(item) != {"name", "value_decimal", "unit"}:
                raise ValueError("invalid_input")
            if not isinstance(item["name"], str) or not 1 <= len(item["name"]) <= 32:
                raise ValueError("invalid_input")
            if not isinstance(item["unit"], str) or not 1 <= len(item["unit"]) <= 16:
                raise ValueError("invalid_input")
            value = item["value_decimal"]
            if type(value) is not str or not re.fullmatch(r"-?[0-9]+(\.[0-9]+)?", value):
                raise ValueError("invalid_input")
            from decimal import Decimal
            if Decimal(value).copy_abs() > Decimal("1e18"):
                raise ValueError("invalid_input")
            if item["name"] in names:
                raise ValueError("invalid_input")
            names.add(item["name"])
    elif kind == "concept":
        if set(data) != {"kind", "scenarios"} or not 1 <= len(data["scenarios"]) <= 2:
            raise ValueError("invalid_input")
        for item in data["scenarios"]:
            if set(item) != {"label", "text"}:
                raise ValueError("invalid_input")
            if not isinstance(item["label"], str) or not 1 <= len(item["label"]) <= 80:
                raise ValueError("invalid_input")
            if not isinstance(item["text"], str) or not 1 <= len(item["text"]) <= 512:
                raise ValueError("invalid_input")
    elif kind == "program":
        if set(data) != {"kind", "language", "code", "inputs", "manual_expected"}:
            raise ValueError("invalid_input")
        if data["language"] != "Python":
            raise ValueError("invalid_input")
        code = data["code"]
        if not isinstance(code, str) or not code.strip():
            raise ValueError("invalid_input")
        if len(code.splitlines()) > 32 or len(code) > 2048 or len(code.encode("utf-8")) > 6144:
            raise ValueError("code_limit")
        if not isinstance(data["inputs"], list) or len(data["inputs"]) > 4:
            raise ValueError("invalid_input")
        names = set()
        for item in data["inputs"]:
            if set(item) != {"name", "value_json"}:
                raise ValueError("invalid_input")
            if not isinstance(item["name"], str) or not 1 <= len(item["name"]) <= 32:
                raise ValueError("invalid_input")
            if not isinstance(item["value_json"], str) or len(item["value_json"].encode("utf-8")) > 1024:
                raise ValueError("invalid_input")
            if item["name"] in names:
                raise ValueError("invalid_input")
            names.add(item["name"])
        if not isinstance(data["manual_expected"], str) or not 1 <= len(data["manual_expected"]) <= 512:
            raise ValueError("invalid_input")
    else:
        raise ValueError("invalid_input")


class ExerciseOutput(Strict):
    result_type: Literal["exercise"]
    message: str = Field(min_length=1, max_length=256)
    exercise_type: Literal["calculation", "concept", "program"]
    difficulty: int = Field(ge=1, le=3)
    stem: str = Field(min_length=1, max_length=1024)
    reference_points: list[ReferencePoint] = Field(min_length=1, max_length=4)
    reference_explanation: str = Field(min_length=1, max_length=512)
    dimensions: list[DimensionSpec] = Field(min_length=1, max_length=4)
    hint: str | None = Field(default=None, min_length=1, max_length=240)
    variant: VariantData

    @model_validator(mode="after")
    def check(self):
        _reject_trusted_fields(self.model_dump())
        ids = [p.point_id for p in self.reference_points]
        if len(set(ids)) != len(ids):
            raise ValueError("invalid_input")
        for dimension in self.dimensions:
            if any(pid not in ids for pid in dimension.point_ids):
                raise ValueError("invalid_input")
        if len({d.id for d in self.dimensions}) != len(self.dimensions):
            raise ValueError("invalid_input")
        return self


class FeedbackItem(Strict):
    answer_excerpt: str = Field(min_length=1, max_length=200)
    explanation: str = Field(min_length=1, max_length=240)
    point_ids: list[str] = Field(max_length=4)
    citations: list[str] = Field(max_length=4)


class Hypothesis(Strict):
    hypothesis: str = Field(min_length=1, max_length=240)
    evidence_for: str = Field(min_length=1, max_length=240)
    missing_evidence: str = Field(min_length=1, max_length=240)
    confidence: Literal["tentative", "unknown"]


class DimensionObservation(Strict):
    id: str = Field(min_length=1, max_length=64)
    observation: Literal["met", "partial", "not_met", "unknown"]
    reason: str = Field(min_length=1, max_length=240)
    point_ids: list[str] = Field(max_length=4)


class NextFocus(Strict):
    focus_dimension: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=240)
    suggested_mode: Literal["continuation", "retest", "review"]


class FeedbackOutput(Strict):
    result_type: Literal["feedback"]
    message: str = Field(min_length=1, max_length=256)
    correct_parts: list[FeedbackItem] = Field(max_length=4)
    errors: list[FeedbackItem] = Field(max_length=4)
    evidence_gaps: list[FeedbackItem] = Field(max_length=4)
    cause_hypotheses: list[Hypothesis] = Field(max_length=4)
    dimension_observations: list[DimensionObservation] = Field(min_length=1, max_length=4)
    next_focus: NextFocus

    @model_validator(mode="after")
    def check(self):
        _reject_trusted_fields(self.model_dump())
        if len({d.id for d in self.dimension_observations}) != len(self.dimension_observations):
            raise ValueError("invalid_input")
        return self


class ClarificationOutput(Strict):
    result_type: Literal["clarification"]
    message: str = Field(min_length=1, max_length=256)
    questions: list[str] = Field(min_length=1, max_length=2)

    @model_validator(mode="after")
    def check(self):
        _reject_trusted_fields(self.model_dump())
        for question in self.questions:
            if not question.strip() or len(question) > 160:
                raise ValueError("invalid_input")
        return self


class NoEvidenceOutput(Strict):
    result_type: Literal["no_evidence"]
    message: str = Field(min_length=1, max_length=256)
    missing: list[str] = Field(min_length=1, max_length=4)

    @model_validator(mode="after")
    def check(self):
        _reject_trusted_fields(self.model_dump())
        for item in self.missing:
            if not item.strip() or len(item) > 160:
                raise ValueError("invalid_input")
        return self


class ConflictClaim(Strict):
    text: str = Field(min_length=1, max_length=256)
    citations: list[str] = Field(min_length=1, max_length=4)


class ConflictOutput(Strict):
    result_type: Literal["conflict"]
    message: str = Field(min_length=1, max_length=256)
    claims: list[ConflictClaim] = Field(min_length=2, max_length=4)

    @model_validator(mode="after")
    def check(self):
        _reject_trusted_fields(self.model_dump())
        return self


def parse_teaching_output(raw: str, action: str) -> dict:
    """解析并按 action 验证低信任输出联合；重复键/非有限数拒。"""
    if len(raw.encode("utf-8")) > 16384:
        raise ValueError("teaching_output_limit")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_teaching_field")
            result[key] = value
        return result

    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid_teaching_number")))
    if not isinstance(value, dict):
        raise ValueError("invalid_teaching_output")
    result_type = value.get("result_type")
    if action == "plan":
        if result_type == "path":
            output = PathOutput.model_validate(value)
        elif result_type == "clarification":
            output = ClarificationOutput.model_validate(value)
        elif result_type == "no_evidence":
            output = NoEvidenceOutput.model_validate(value)
        elif result_type == "conflict":
            output = ConflictOutput.model_validate(value)
        else:
            raise ValueError("invalid_teaching_output")
    elif action == "exercise":
        if result_type == "exercise":
            output = ExerciseOutput.model_validate(value)
        elif result_type in ("clarification", "no_evidence", "conflict"):
            output = _NEUTRAL_MODELS[result_type].model_validate(value)
        else:
            raise ValueError("invalid_teaching_output")
    elif action == "evaluate":
        if result_type == "feedback":
            output = FeedbackOutput.model_validate(value)
        elif result_type in ("clarification", "no_evidence", "conflict"):
            output = _NEUTRAL_MODELS[result_type].model_validate(value)
        else:
            raise ValueError("invalid_teaching_output")
    else:
        raise ValueError("invalid_teaching_action")
    if len(canonical(output.model_dump()).encode("utf-8")) > MAX_RECORD_BODY_BYTES:
        raise ValueError("teaching_output_limit")
    return output.model_dump()


_NEUTRAL_MODELS = {"clarification": ClarificationOutput, "no_evidence": NoEvidenceOutput,
                   "conflict": ConflictOutput}


def validate_exposed_part(value: dict) -> dict:
    """O05 exposed_part 封闭联合 {part:'hint',text} 或 reference 投影。"""
    if type(value) is not dict:
        raise ValueError("invalid_input")
    if value.get("part") == "hint":
        if set(value) != {"part", "text"} or not isinstance(value["text"], str) or not value["text"].strip():
            raise ValueError("invalid_input")
        if len(value["text"]) > 240:
            raise ValueError("input_too_large")
        return value
    if value.get("part") == "reference":
        if set(value) != {"part", "reference_points", "reference_explanation"}:
            raise ValueError("invalid_input")
        if not isinstance(value["reference_points"], list) or not 1 <= len(value["reference_points"]) <= 4:
            raise ValueError("invalid_input")
        if not isinstance(value["reference_explanation"], str) or len(value["reference_explanation"]) > 512:
            raise ValueError("invalid_input")
        return value
    raise ValueError("invalid_input")


# --- 工作区只读视图（099 第 7.1 节） ---

class TeachingOverlay(Strict):
    source_invalid: bool = False
    cancelled: bool = False
    expired: bool = False
    processing: bool = False
    unknown: bool = False
    teaching_disabled_reason: str | None = Field(default=None, max_length=256)


class TeachingHeadView(Strict):
    revision: int = Field(ge=0)
    goal_version: int = Field(ge=0, le=MAX_GOAL_VERSION)
    phase: Literal["needs_goal", "needs_plan", "path_review", "ready", "exercise_ready",
                   "answer_saved", "feedback_ready"]
    goal_record_id: str | None = None
    path_record_id: str | None = None
    node_id: str | None = Field(default=None, pattern=r"^n[1-6]$")
    exercise_record_id: str | None = None
    answer_record_id: str | None = None
    feedback_record_id: str | None = None
    reason_record_id: str | None = None
    pending_business_key: str | None = None


class NodeStatusView(Strict):
    node_id: str = Field(pattern=r"^n[1-6]$")
    status: Literal["not_started", "practising", "needs_repair", "evidence_sufficient", "deferred"]
    independent_answers: list[str] = Field(max_length=2)
    contested: bool = False
    assisted: bool = False


class WorkspaceBudgets(Strict):
    requests_reserved: int
    max_requests: int
    cost_reserved_microunits: int
    max_cost_microunits: int
    tools_reserved: int
    max_tool_calls: int | None
    running_settled_seconds: int
    running_reserved_seconds: int
    max_running_seconds: int
    deadline_at: str


class PendingSummary(Strict):
    business_key: str
    action: str
    status: str
    created_at: str


class HistoryItem(Strict):
    record_id: str
    kind: str
    seq: int = Field(ge=1, le=MAX_RECORDS)
    goal_version: int = Field(ge=1, le=MAX_GOAL_VERSION)
    parent_record_id: str | None = None
    created_at: str
    label: str = Field(min_length=1, max_length=32)


class TeachingWorkspaceView(Strict):
    schema_: Literal["teaching.workspace.v1"] = Field(alias="schema", default=WORKSPACE_SCHEMA)
    activity_id: str
    view_token: str = Field(pattern=r"^[0-9a-f]{64}$")
    read_at: str
    head: TeachingHeadView
    overlay: TeachingOverlay
    memory_invalid: bool = False
    memory_selected: bool = False
    goal: dict | None = None
    path: dict | None = None
    proposal: dict | None = None
    exercise: dict | None = None
    answer: dict | None = None
    feedback: dict | None = None
    reason: dict | None = None
    nodes: list[NodeStatusView] = Field(max_length=6)
    sources: list[dict] = Field(max_length=10)
    budgets: WorkspaceBudgets | None = None
    pending: list[PendingSummary] = Field(max_length=PENDING_SUMMARY_ROWS)
    history: list[HistoryItem] = Field(max_length=HISTORY_MAX)
    next_cursor: str | None = None
    limits: dict

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, populate_by_name=True)


class TeachingRecordView(Strict):
    record_id: str
    kind: str
    seq: int = Field(ge=1, le=MAX_RECORDS)
    goal_version: int = Field(ge=1, le=MAX_GOAL_VERSION)
    scope_revision: int = Field(ge=1)
    parent_record_id: str | None = None
    exercise_record_id: str | None = None
    answer_record_id: str | None = None
    supersedes_record_id: str | None = None
    body_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    created_at: str
    qualification: Literal["current", "history_only", "source_invalid", "cancelled",
                           "integrity_error", "unconfirmed", "memory_invalid"] = "current"
    public_body: dict | None = None


class TeachingHistoryPage(Strict):
    activity_id: str
    view_token: str = Field(pattern=r"^[0-9a-f]{64}$")
    read_at: str
    watermark_last_seq: int = Field(ge=0, le=MAX_RECORDS)
    items: list[HistoryItem] = Field(max_length=HISTORY_MAX)
    next_cursor: str | None = Field(default=None, max_length=1024)


# G9 另立v2类型，旧v1字段及model_dump不增加默认键。
from app.memory.contracts import MemoryChoice
from app.retrieval.contracts import RetrievalRef
TeachingCommandInput.model_rebuild()

class TeachingMemoryFrozenContext(Strict):
    schema_: Literal["teaching.context.v2"] = Field(alias="schema",default="teaching.context.v2")
    kind: Literal["model"] = "model"
    reference_hashes: list[ReferenceHash] = Field(min_length=1,max_length=12)
    operation_id: str = Field(min_length=1,max_length=128)
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    profile_version: Literal["teaching.v2"] = "teaching.v2"
    prompt_version: Literal["teaching-memory-prompt-v1"] = "teaching-memory-prompt-v1"
    projection_policy_version: Literal["teaching.memory.recipe.v1"] = "teaching.memory.recipe.v1"
    max_output_tokens: int = Field(ge=1,le=2048)
    catalog: list[CatalogEntry] = Field(min_length=1,max_length=4)
    recipe: dict
    memory_selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    memory_refs: list[MemoryChoice] = Field(min_length=1,max_length=4)
    assembled_messages_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_config=ConfigDict(extra="forbid",strict=True,frozen=True,populate_by_name=True)


class TeachingMemoryProfile(TeachingProfile):
    profile: Literal["teaching.v2"] = "teaching.v2"
    memory_selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    memory_refs: list[MemoryChoice] = Field(min_length=1,max_length=4)
    assembled_messages_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class TeachingMemoryCallBinding(TeachingCallBinding):
    memory_selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    assembled_messages_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class TeachingHybridFrozenContext(TeachingMemoryFrozenContext):
    schema_: Literal['teaching.context.v3'] = Field(alias='schema',default='teaching.context.v3')
    profile_version: Literal['teaching.v3'] = 'teaching.v3'
    prompt_version: Literal['teaching-hybrid-prompt-v1'] = 'teaching-hybrid-prompt-v1'
    recipe: dict | None
    messages: list[dict] | None
    memory_selection_sha256: str | None = Field(pattern=r'^[0-9a-f]{64}$')
    memory_dependency_sha256: str | None = Field(pattern=r'^[0-9a-f]{64}$')
    memory_refs: list[MemoryChoice] = Field(max_length=4)
    retrieval_ref: RetrievalRef

    @model_validator(mode='after')
    def hybrid_shape(self):
        if self.memory_selection_sha256 is None:
            if self.recipe is not None or self.messages is None or self.memory_refs or self.memory_dependency_sha256 is not None:raise ValueError('invalid_hybrid_context')
        elif self.recipe is None or self.messages is not None or not self.memory_refs or self.memory_dependency_sha256 is None:raise ValueError('invalid_hybrid_context')
        return self


class TeachingHybridProfile(TeachingMemoryProfile):
    profile: Literal['teaching.v3']='teaching.v3'
    memory_selection_sha256: str | None = Field(pattern=r'^[0-9a-f]{64}$')
    memory_dependency_sha256: str | None = Field(pattern=r'^[0-9a-f]{64}$')
    memory_refs: list[MemoryChoice] = Field(max_length=4)
    retrieval_ref: RetrievalRef


class TeachingHybridCallBinding(TeachingMemoryCallBinding):
    memory_selection_sha256: str | None = Field(pattern=r'^[0-9a-f]{64}$')
    memory_dependency_sha256: str | None = Field(pattern=r'^[0-9a-f]{64}$')
    retrieval_ref: RetrievalRef


def parse_frozen_context(value):
    if isinstance(value,str):
        import json
        value=json.loads(value)
    kind=TeachingHybridFrozenContext if value.get('schema')=='teaching.context.v3' else TeachingMemoryFrozenContext if value.get("schema")=="teaching.context.v2" else TeachingFrozenContext
    return kind.model_validate(value)
