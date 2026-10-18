"""记忆命令、固定选择及有限配置的封闭数据合同。"""
from __future__ import annotations
import json
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.learning.contracts import canonical, sha


class MemoryRefusal(RuntimeError):
    def __init__(self, code, message, status=409):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


def uuid_text(value):
    if type(value) is not str or str(UUID(value)) != value:
        raise ValueError("invalid_uuid")
    return value


def text_ok(value, maximum, empty=False):
    if type(value) is not str or len(value)>maximum or "\0" in value:
        raise ValueError("invalid_text")
    value.encode("utf-8", "strict")
    if not empty and not value.strip():
        raise ValueError("empty_text")
    return value


class Capture(Strict):
    activity_id: str
    progress_record_id: str
    record_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    view_token: str = Field(pattern=r"^[0-9a-f]{64}$")
    _ids = field_validator("activity_id", "progress_record_id")(uuid_text)


class SaveBody(Strict):
    kind: Literal["self_report","preference","focus","learning_observation"]
    title: str
    text: str = ""
    capture: Capture | None = None

    @model_validator(mode="after")
    def check(self):
        text_ok(self.title,80)
        text_ok(self.text,1024,empty=self.kind=="learning_observation")
        if (self.kind=="learning_observation") != (self.capture is not None):
            raise ValueError("capture_kind_mismatch")
        return self


class ReviseBody(Strict):
    title: str
    text: str
    kind: Literal["self_report","preference","focus","learning_observation"]
    base_body_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    impact_token: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def check(self):
        text_ok(self.title,80);text_ok(self.text,1024,empty=self.kind=="learning_observation")
        return self


def confirmed_bool(value):
    if type(value) is not bool or value is not True:raise ValueError("confirmation_required")
    return value


class RevokeBody(Strict):
    impact_token: str = Field(pattern=r"^[0-9a-f]{64}$")
    confirm_revoke: Literal[True]
    purge_memory_content: Literal[True]
    _confirm=field_validator('confirm_revoke','purge_memory_content',mode='before')(confirmed_bool)


class PurgeBody(Strict):
    revocation_key: str
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    confirm_memory_cleanup: Literal[True]
    _confirm=field_validator('confirm_memory_cleanup',mode='before')(confirmed_bool)
    _id = field_validator("revocation_key")(uuid_text)


class MemoryCommandInput(Strict):
    schema_: Literal["memory.command.v1"] = Field(alias="schema",default="memory.command.v1")
    business_key: str
    memory_id: str
    expected_revision: int = Field(ge=0,le=2147483647)
    action: Literal["save","revise","revoke","purge"]
    body: dict
    model_config=ConfigDict(extra="forbid",strict=True,frozen=True,populate_by_name=True)
    _ids=field_validator("business_key","memory_id")(uuid_text)

    @model_validator(mode="after")
    def check(self):
        kind={"save":SaveBody,"revise":ReviseBody,"revoke":RevokeBody,"purge":PurgeBody}[self.action]
        kind.model_validate(self.body)
        if (self.action=="save") != (self.expected_revision==0):
            raise ValueError("revision_shape")
        if len(canonical(self.canonical_body()).encode("utf-8"))>32768:
            raise ValueError("request_too_large")
        return self

    def canonical_body(self):
        return {"schema":"memory.command.v1","memory_id":self.memory_id,
                "expected_revision":self.expected_revision,"action":self.action,"body":self.body}

    def request_sha(self):
        return sha(canonical(self.canonical_body()))

    def slot(self):
        if self.action=="save": return sha("save|"+self.memory_id)
        if self.action=="purge":
            return sha("purge|"+self.body["revocation_key"]+"|"+self.body["manifest_sha256"])
        return sha("modify|"+self.memory_id+"|"+str(self.expected_revision))


class MemoryChoice(Strict):
    memory_id: str
    version: int = Field(ge=1,le=32)
    revision: int = Field(ge=1,le=2147483647)
    body_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    _id=field_validator("memory_id")(uuid_text)


class MemorySelectionInput(Strict):
    confirmed: Literal[True]
    _confirm=field_validator('confirmed',mode='before')(confirmed_bool)
    entries: list[MemoryChoice] = Field(min_length=1,max_length=4)

    @model_validator(mode="after")
    def check(self):
        if len({e.memory_id for e in self.entries}) != len(self.entries):
            raise ValueError("duplicate_memory_choice")
        return self

    def digest(self):
        return sha("\n".join(f"{x.memory_id}|{x.version}|{x.revision}|{x.body_sha256}" for x in self.entries))


class MemoryContextConfig(Strict):
    selected_items: int = Field(ge=1,le=4)
    max_memory_bytes: int = Field(ge=1,le=4096)
    max_memory_chars: int = Field(ge=1,le=2048)
    model_context_tokens: int = Field(gt=0,le=2097152)
    max_input_tokens_estimate: int = Field(gt=0,le=2097152)
    protocol_reserve_tokens: int = Field(gt=0,le=65536)
    reserved_output_tokens: int = Field(gt=0,le=2048)
    safety_tokens: int = Field(gt=0,le=65536)
    estimate_policy: Literal["utf8_bytes.v1"]
    model_identity: dict[str,str]

    @model_validator(mode="after")
    def check(self):
        if set(self.model_identity)!={"provider","model"}:
            raise ValueError("memory_model_identity")
        if self.max_input_tokens_estimate+self.reserved_output_tokens+self.safety_tokens>self.model_context_tokens:
            raise ValueError("memory_capacity_incompatible")
        return self


def dependency_line(d):
    kind=d["dependency_kind"]
    if kind=="source":
        keys=("source_id","source_version_id","source_revision","original_sha256")
    elif kind=="event":
        keys=("origin_activity_id","record_id","record_kind","origin_scope_revision","origin_goal_version","record_sha256")
    elif kind=="memory":
        keys=("upstream_memory_id","upstream_version","upstream_body_sha256")
    else: raise MemoryRefusal("memory_dependency_invalid","记忆依赖类型不可核对")
    return kind+"|"+"|".join(str(d[k]) for k in keys)


def order_dependencies(items):
    unique={dependency_line(d):d for d in items}
    counts={k:sum(d["dependency_kind"]==k for d in unique.values()) for k in ("source","event","memory")}
    if len(unique)>32 or counts["source"]>10 or counts["event"]>8 or counts["memory"]>14:
        raise MemoryRefusal("memory_dependency_limit","依据关联超过有限容量，请保存更小的观察或独立用户笔记")
    return [unique[k] for k in sorted(unique)]


def dependencies_digest(items):
    return sha("\n".join(dependency_line(d) for d in items))


def bounded_json(value, limit=65536):
    text=canonical(value)
    if len(text.encode("utf-8"))>limit:
        raise MemoryRefusal("memory_context_limit","数据超过有限显示容量",413)
    return value


async def read_bounded_json(request, maximum=32768):
    data=bytearray()
    async for part in request.stream():
        data.extend(part)
        if len(data)>maximum: raise MemoryRefusal("request_too_large","请求超过有限容量",413)
    def pairs(items):
        obj={}
        for k,v in items:
            if k in obj: raise ValueError("duplicate_key")
            obj[k]=v
        return obj
    def invalid(value): raise ValueError("nonfinite")
    try:
        value=json.loads(bytes(data).decode("utf-8","strict"),object_pairs_hook=pairs,parse_constant=invalid)
        if type(value) is not dict: raise ValueError("object_required")
        canonical(value).encode("utf-8","strict")
        def depth(x,n=0):
            if n>12: raise ValueError("json_depth")
            if isinstance(x,dict):
                for child in x.values():depth(child,n+1)
            elif isinstance(x,list):
                for child in x:depth(child,n+1)
        depth(value)
        return value
    except (ValueError,UnicodeError,RecursionError):
        raise MemoryRefusal("invalid_input","请求内容不可核对",400) from None

