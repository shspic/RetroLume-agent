"""受控工具适配器：规范验证 → admit → mark → 执行一次 → record。

纯内部组件，只由固定受控 worker 通过 ClosingCallGate 调用。不新增网络、
文件、命令或子进程能力；执行严格在数据库事务之外；实际执行只从同一不可变
规范输入重建计划，不再读取调用方原始 Mapping。
"""

from __future__ import annotations

from .contracts import (
    AdmissionDenied,
    AdmissionUnavailable,
    CallContext,
    LedgerDisposition,
    LedgerOutcome,
    RecordOutcome,
    RejectingToolAdmissionLedger,
    ToolAdmissionLedger,
    ToolAdmissionPermit,
    ToolCallResult,
    ToolCallStatus,
    ToolExecutionInput,
    ToolIntent,
    build_business_payload,
)
from .tools import ToolRegistry, ToolValidationError


# 有限脱敏错误码 allowlist：其余准入拒绝统一收敛为 admission_denied。
_ADMISSION_DENIED_CODES = frozenset({
    "scope_conflict", "scope_changed", "source_invalid", "cancelled",
    "activity_expired", "lease_invalid", "budget_exhausted",
    "tool_not_allowed", "tool_limit_unconfigured", "tool_limit_exhausted",
    "operation_key_conflict", "tool_input_conflict", "operation_already_exists",
    "admission_permit_unknown", "admission_permit_mismatch",
    "start_qualification_consumed", "qualification_invalid",
    "invalid_input", "integrity_error", "result_kind_not_consumable",
})


def _bounded_code(exc: BaseException) -> str:
    code = str(exc)
    return code if code in _ADMISSION_DENIED_CODES else "admission_denied"


class ControlledToolExecutor:
    """实现一次工具动作的最小受控执行器。

    每个调用内部至多一次实际 execute；预扣、最后资格与提交共享同一参数
    快照。提交失败/未知不重试、不覆写未知、不把本地答案冒充持久成功。
    """

    def __init__(self, ledger: ToolAdmissionLedger | None = None, *, tools: ToolRegistry | None = None) -> None:
        self._ledger = ledger or RejectingToolAdmissionLedger()
        self._tools = tools or ToolRegistry()

    def _result(
        self,
        call: ToolExecutionInput,
        status: ToolCallStatus,
        error_code: str | None = None,
        payload_sha256: str | None = None,
    ) -> ToolCallResult:
        return ToolCallResult(
            status=status,
            name=call.name,
            call_id=call.call_id,
            arguments_sha256=call.arguments_sha256,
            error_code=error_code,
            payload_sha256=payload_sha256,
        )

    async def call(self, context: CallContext, call: ToolExecutionInput) -> ToolCallResult:
        # 边界完整复核：解码端与执行端各自从同一不可变规范输入重建计划。
        wire = call.to_wire()
        plan = self._tools.plan(
            call.call_id, call.name, wire["arguments_json"], frozenset({call.name}),
        )
        del wire
        try:
            permit = await self._ledger.admit_tool_operation(ToolIntent(context=context, call=call))
        except AdmissionDenied as exc:
            # 已持久登记的凭证不因代次关闭误拒；此处为明确拒绝，无执行。
            return self._result(call, ToolCallStatus.REJECTED, _bounded_code(exc))
        except AdmissionUnavailable:
            # 本次无凭证确认：不 mark、不 execute；不推 DB 无行。
            return self._result(call, ToolCallStatus.UNKNOWN, "admission_unconfirmed")
        if type(permit) is not ToolAdmissionPermit:
            return self._result(call, ToolCallStatus.UNKNOWN, "admission_unconfirmed")
        try:
            await self._ledger.mark_tool_started(permit, call)
        except AdmissionDenied as exc:
            # mark 明确回滚：无执行资格，也不重试 mark。
            return self._result(call, ToolCallStatus.REJECTED, _bounded_code(exc))
        except AdmissionUnavailable:
            # 持久行可能 reserved 或 dispatched；绝不获取执行资格或 execute。
            return self._result(call, ToolCallStatus.UNKNOWN, "mark_unconfirmed")
        try:
            rendered = self._tools.execute(plan)
        except ToolValidationError:
            # 确定计算失败：received + tool_execution_failed、无正文。
            return await self._record(
                permit, call,
                LedgerOutcome(LedgerDisposition.RECEIVED, error_code="tool_execution_failed"),
                ToolCallStatus.FAILED, "tool_execution_failed",
            )
        except Exception:
            # 意外异常：best-effort UNKNOWN 诊断；不携带成功正文。
            await self._record_unknown_best_effort(permit, call, "tool_execution_unknown")
            return self._result(call, ToolCallStatus.UNKNOWN, "tool_execution_unknown")
        try:
            payload_format, payload, payload_sha256 = build_business_payload(text=rendered)
        except (ValueError, TypeError, RecursionError):
            return await self._record(
                permit, call,
                LedgerOutcome(LedgerDisposition.RECEIVED, error_code="tool_execution_failed"),
                ToolCallStatus.FAILED, "tool_execution_failed",
            )
        return await self._record(
            permit, call,
            LedgerOutcome(
                LedgerDisposition.RECEIVED,
                payload_format=payload_format, payload=payload, payload_sha256=payload_sha256,
            ),
            ToolCallStatus.SUCCEEDED, None,
        )

    async def _record(
        self,
        permit: ToolAdmissionPermit,
        call: ToolExecutionInput,
        outcome: LedgerOutcome,
        status: ToolCallStatus,
        error_code: str | None,
    ) -> ToolCallResult:
        try:
            confirmation = await self._ledger.record_tool_outcome(permit, call, outcome)
        except AdmissionDenied:
            # 提交被明确拒绝：不否认既有历史；本次未获确认。
            return self._result(call, ToolCallStatus.UNKNOWN, "record_denied")
        except Exception:
            return self._result(call, ToolCallStatus.UNKNOWN, "record_unconfirmed")
        if not isinstance(confirmation, RecordOutcome):
            return self._result(call, ToolCallStatus.UNKNOWN, "record_unconfirmed")
        if status is ToolCallStatus.SUCCEEDED:
            if not isinstance(outcome.payload_sha256, str):
                return self._result(call, ToolCallStatus.UNKNOWN, "record_unconfirmed")
            return self._result(call, status, None, payload_sha256=outcome.payload_sha256)
        return self._result(call, status, error_code)

    async def _record_unknown_best_effort(
        self, permit: ToolAdmissionPermit, call: ToolExecutionInput, error_code: str,
    ) -> None:
        try:
            await self._ledger.record_tool_outcome(
                permit, call, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code=error_code),
            )
        except Exception:
            pass
