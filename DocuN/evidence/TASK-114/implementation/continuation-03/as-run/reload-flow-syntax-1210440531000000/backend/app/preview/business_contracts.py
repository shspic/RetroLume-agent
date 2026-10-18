"""v2业务输入和受信模型绑定，独立于旧h0诊断协议。"""
from __future__ import annotations
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from .description import canonical, digest, load_json

PREFIX = "html11m."
HEX = r"^[0-9a-f]{64}$"


class HtmlRefusal(ValueError):
    def __init__(self, code, message="交互解释暂不可用，原学习成果已保留", status=409):
        self.code, self.message, self.status = code, message, status
        super().__init__(code)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class LearningParent(Strict):
    kind: Literal["learning"]
    operation_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")
    payload_sha256: str = Field(pattern=HEX)
    segment_index: int = Field(ge=0, le=31)


class TeachingParent(Strict):
    kind: Literal["teaching"]
    record_id: str
    body_sha256: str = Field(pattern=HEX)
    point_id: str | None = Field(default=None, max_length=64)

    @field_validator("record_id")
    @classmethod
    def uuid_id(cls, value):
        if str(UUID(value)) != value:
            raise ValueError("invalid_uuid")
        return value


class HtmlCommand(Strict):
    business_key: str
    parent: LearningParent | TeachingParent = Field(discriminator="kind")
    focus: str = Field(min_length=1, max_length=1024)
    expected_config_sha256: str = Field(pattern=HEX)
    confirmed: Literal[True]

    @field_validator("confirmed", mode="before")
    @classmethod
    def true_boolean(cls, value):
        if type(value) is not bool or not value:
            raise ValueError("confirmation_required")
        return value

    @field_validator("business_key")
    @classmethod
    def uuid_id(cls, value):
        if str(UUID(value)) != value:
            raise ValueError("invalid_uuid")
        return value

    @field_validator("focus")
    @classmethod
    def focus_input(cls, value):
        if value != value.strip() or len(value.encode("utf-8")) > 4096 or "\0" in value:
            raise ValueError("invalid_focus")
        return value


class HtmlProfile(Strict):
    profile: Literal["html_explanation.v2"] = "html_explanation.v2"
    activity_id: str
    business_key: str
    request_sha256: str = Field(pattern=HEX)
    context_sha256: str = Field(pattern=HEX)
    context_json: str = Field(min_length=2, max_length=24576)
    renderer_sha256: str = Field(pattern=HEX)
    max_output_tokens: int = Field(ge=1, le=4096)

    @model_validator(mode="after")
    def validate_binding(self):
        if str(UUID(self.activity_id)) != self.activity_id or str(UUID(self.business_key)) != self.business_key:
            raise ValueError("invalid_html_profile")
        context = load_json(self.context_json)
        if (canonical(context) != self.context_json or digest(context) != self.context_sha256
                or context.get("schema") != "html.context.v2" or context.get("activity_id") != self.activity_id
                or context.get("business_key") != self.business_key or context.get("request_sha256") != self.request_sha256
                or context.get("renderer_sha256") != self.renderer_sha256):
            raise ValueError("invalid_html_profile")
        return self


class HtmlCallBinding(Strict):
    business_key: str
    request_sha256: str = Field(pattern=HEX)
    context_sha256: str = Field(pattern=HEX)
    renderer_sha256: str = Field(pattern=HEX)
    memory_selection_sha256: str | None = Field(default=None, pattern=HEX)


class OpenPreview(Strict):
    start_key: str
    expected_artifact_sha256: str = Field(pattern=HEX)
    input_owner_key: str = Field(pattern=HEX)
    confirmed: Literal[True]

    @field_validator("confirmed", mode="before")
    @classmethod
    def true_boolean(cls, value):
        if type(value) is not bool or not value:
            raise ValueError("confirmation_required")
        return value

    @field_validator("start_key")
    @classmethod
    def uuid_id(cls, value):
        if str(UUID(value)) != value:
            raise ValueError("invalid_uuid")
        return value


class SetNumber(Strict):
    type: Literal["set_number"]
    control_id: str = Field(pattern=r"^hctl_[A-Za-z0-9_]{1,24}$")
    value: str = Field(min_length=1, max_length=24)


class Activate(Strict):
    type: Literal["activate"]
    action_id: str = Field(pattern=r"^hact_[A-Za-z0-9_]{1,24}$")


class PreviewInput(Strict):
    preview_generation: int = Field(ge=1)
    seq: int = Field(ge=1, le=1200)
    payload_sha256: str = Field(pattern=HEX)
    event: SetNumber | Activate = Field(discriminator="type")


class StopPreview(Strict):
    generation: int = Field(ge=1)
    stop_key: str
    reason: Literal["user", "back_to_learning"]

    @field_validator("stop_key")
    @classmethod
    def uuid_id(cls, value):
        if str(UUID(value)) != value:
            raise ValueError("invalid_uuid")
        return value


def operation_id(key):
    return PREFIX + UUID(key).hex


def messages_for(profile):
    contract = {"output": "interactive_description.v1", "input_kinds": ["number", "range", "integer"],
                "math_ops": ["add", "sub", "mul", "div", "neg", "abs", "min", "max", "pow_int", "sqrt", "sin", "cos", "binomial_pmf"],
                "view_kinds": ["readout", "bar", "curve", "points_lines"], "actions": ["reset"],
                "limits": {"inputs": 8, "calculations": 32, "ast_nodes": 256, "ast_depth": 16, "points": 128, "utf8_bytes": 24576}}
    contract["root"]={"schema":"interactive_description.v1","title":"text<=128","concept":"text<=1024",
      "inputs":"1..8 input objects","calculations":"1..32 calculation objects","views":"1..4 view objects",
      "actions":"0..4 action objects","calculation_notes":"1..4 note objects","limitations":"0..8 texts<=256",
      "citations":"1..8 unique citation_id strings from context.catalog","constraints":"optional 0..4 le objects"}
    contract["objects"]={
      "input":{"id":"hctl_ plus 1..24 ASCII letters/digits/underscores","kind":"number|range|integer","label":"text<=80",
        "description":"text<=256, empty allowed","min":"decimal string","max":"decimal string","step":"positive decimal string","default":"decimal string on min-based grid"},
      "calculation":{"id":"hcalc_ plus 1..24 ASCII identifier characters","expression":"AST; only prior calculation references"},
      "readout":{"id":"hout_ plus 1..24 ASCII identifier characters","kind":"readout","label":"text<=80","calculation":"defined hcalc_ id","unit":"text<=24, empty allowed"},
      "figure":{"id":"hview_ plus 1..24 ASCII identifier characters","kind":"bar|curve|points_lines","label":"text<=80","source":"one matching source object"},
      "action":{"id":"hact_ plus 1..24 ASCII identifier characters","kind":"reset","label":"text<=80"},
      "constraint":{"kind":"le","left":"defined hctl_ id","right":"defined hctl_ id"},
      "note":{"formula":"text<=512, explanatory text only","domain":"text<=256","error":"text<=128",
        "samples":"2..4 objects with input text<=256 and expected text<=128","citations":"1..4 citation ids also listed at root"}}
    contract["ast"]={"const":{"op":"const","value":"canonical decimal string"},"input":{"op":"input","id":"defined hctl_ id"},
      "result":{"op":"result","id":"prior hcalc_ id"},"sample_x":{"op":"sample_x"},
      "math":{"op":"one declared math_op","args":"fixed arity: unary neg/abs/sqrt/sin/cos; binomial_pmf has 3; all others have 2"}}
    contract["sources"]={"bar_values":{"kind":"values","values":"1..21 objects {label:text<=80,value:AST}"},
      "bar_distribution":{"kind":"binomial_distribution","n":"AST","p":"AST"},
      "curve":{"min":"decimal string","max":"larger decimal string","samples":"integer 2..128","expression":"AST; sample_x allowed only here"},
      "points_lines":{"points":"1..128 objects {x:AST,y:AST}","join":"boolean"}}
    return [{"role": "system", "content": "仅以封闭JSON描述有来源的计算和图形交互。禁止HTML/JS/CSS/URL/DOM/工具、可执行公式字符串。"
            "数字参数与常量采用规范十进制字符串；公式采用固定op/args AST；引用只能来自catalog。"
            "所有对象仅含对应声明字段，id全局唯一；十进制绝对值不超过1000000，不用指数、前导0、尾随小数0或负零。"
            "integer控件全部数值为整数；range最多100个等间距步。图形最多2幅且合计128点，distribution按最大21柱计。"
            "binomial的n整数0..20，k整数0..n，p为0..1；pow_int指数整数0..10且0^0约定1。首个完整计算必须有效。"
            "必须给正常和边界样例、适用域和限制；不支持的概念不得伪造静态答案为交互。合同="+canonical(contract)},
            {"role": "user", "content": profile.context_json}]
