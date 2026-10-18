"""确定性的有限工具目录；不含文件、网络或代码执行能力。"""

from __future__ import annotations

import json
import math
from decimal import Decimal, InvalidOperation, localcontext
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from .contracts import ToolCallPlan


TOOL_NAME = "finite_calculate"
MAX_ARGUMENT_BYTES = 2048
MAX_ABS_INPUT = Decimal("1e12")
MAX_ABS_RESULT = Decimal("1e18")


class ToolValidationError(ValueError):
    pass


class CalculationArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    operation: Literal["add", "subtract", "multiply", "divide", "power"]
    left: int | float
    right: int | float

    @field_validator("left", "right")
    @classmethod
    def finite_bounded_number(cls, value: int | float) -> int | float:
        if isinstance(value, bool) or not math.isfinite(float(value)):
            raise ValueError("参数必须是有限数值")
        if abs(Decimal(str(value))) > MAX_ABS_INPUT:
            raise ValueError("参数绝对值超过限制")
        return value

    @model_validator(mode="after")
    def operation_limits(self) -> "CalculationArguments":
        if self.operation == "divide" and Decimal(str(self.right)) == 0:
            raise ValueError("除数不能为零")
        if self.operation == "power":
            exponent = Decimal(str(self.right))
            if exponent != exponent.to_integral_value() or abs(exponent) > 12:
                raise ValueError("幂指数必须是 -12 到 12 的整数")
            if Decimal(str(self.left)) == 0 and exponent < 0:
                raise ValueError("零不能取负整数次幂")
        return self


CALCULATION_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "对两个有限数值执行加、减、乘、除或有界整数幂运算。",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide", "power"],
                },
                "left": {"type": "number"},
                "right": {"type": "number"},
            },
            "required": ["operation", "left", "right"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}


class ToolRegistry:
    def schemas_for(self, allowed_tools: frozenset[str]) -> list[dict[str, Any]]:
        unknown = allowed_tools - {TOOL_NAME}
        if unknown:
            raise ToolValidationError("授权集合包含未登记工具")
        return [CALCULATION_SCHEMA] if TOOL_NAME in allowed_tools else []

    def plan(self, call_id: Any, name: Any, raw_arguments: Any, allowed_tools: frozenset[str]) -> ToolCallPlan:
        if not isinstance(call_id, str) or not call_id or len(call_id) > 128:
            raise ToolValidationError("工具调用 ID 非法")
        if not isinstance(name, str) or name != TOOL_NAME:
            raise ToolValidationError("模型建议了未登记工具")
        if name not in allowed_tools:
            raise ToolValidationError("模型建议的工具未获本活动授权")
        if not isinstance(raw_arguments, str) or len(raw_arguments.encode("utf-8")) > MAX_ARGUMENT_BYTES:
            raise ToolValidationError("工具参数不是有界 JSON 字符串")
        try:
            payload = json.loads(raw_arguments, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
            arguments = CalculationArguments.model_validate(payload)
        except (json.JSONDecodeError, ValueError, RecursionError) as exc:
            raise ToolValidationError("工具参数未通过精确 Schema 校验") from exc
        return ToolCallPlan(call_id=call_id, name=name, arguments=arguments.model_dump())

    def execute(self, plan: ToolCallPlan) -> str:
        """显式执行一个已校验计划；模型入口不会自动调用本方法。"""

        if plan.name != TOOL_NAME:
            raise ToolValidationError("工具计划名称非法")
        try:
            args = CalculationArguments.model_validate(dict(plan.arguments))
            left, right = Decimal(str(args.left)), Decimal(str(args.right))
            with localcontext() as context:
                context.prec = 50
                result = {
                    "add": lambda: left + right,
                    "subtract": lambda: left - right,
                    "multiply": lambda: left * right,
                    "divide": lambda: left / right,
                    "power": lambda: left ** int(right),
                }[args.operation]()
                rendered = format(result.normalize(), "f")
        except (InvalidOperation, OverflowError, ZeroDivisionError, ValueError) as exc:
            raise ToolValidationError("计算无法在有限边界内完成") from exc
        if not result.is_finite() or abs(result) > MAX_ABS_RESULT:
            raise ToolValidationError("计算结果超过有限边界")
        return rendered
