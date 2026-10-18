"""受信内部范围与持久成果续接；每次显式意图最多一次受监督调用。

这是内部应用边界，不能作为任意外部客户端的权限凭证。读取不出站，
取消历史只展示；线程中的监督必须完成自身有界收尾才传播调用方取消。
"""
from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
import json
from pydantic import ValidationError
from app.capabilities.contracts import (
    AdmissionUnavailable,
    ModelCallRequest,
    ModelServiceConfig,
    ResultConsumptionRef,
    ToolCallPlan,
    ToolExecutionInput,
    canonical_tool_arguments,
    validate_business_payload,
)
from .repository import PostgresAdmissionLedger, CommittedResultSnapshot, ResultReadStatus, ResultIntegrityError


@dataclass(frozen=True)
class ReadOutcome:
    status: str
    snapshot: CommittedResultSnapshot | None = None


@dataclass(frozen=True)
class SettlementFacts:
    settled_seconds: int | None
    reserved_seconds: int | None
    pending_fold_seconds: int | None
    cleanup_incomplete: bool


@dataclass(frozen=True)
class ContinuationOutcome:
    status: str
    business: ReadOutcome | None = None
    supervision: object | None = None
    settlement: SettlementFacts | None = None


@dataclass(frozen=True)
class ToolActionOutcome:
    """一次显式工具动作的结果；业务读、监督与结算事实互相独立。"""

    status: str
    business: ReadOutcome | None = None
    supervision: object | None = None
    settlement: SettlementFacts | None = None


def _canonical_tool_execution_input(operation_id, plan) -> ToolExecutionInput | None:
    """把受信调用方计划一次性转换为私有规范输入；失败返回 None。

    只读取调用方 Mapping 一次到私有浅拷贝；之后解析、Schema 校验与规范
    编码全部作用于私有值，不再触碰原 Mapping，也不为其内容变化背书。
    """
    if type(plan) is not ToolCallPlan or not isinstance(plan.arguments, Mapping):
        return None
    try:
        snapshot = dict(plan.arguments)
    except (TypeError, ValueError, RuntimeError):
        return None
    try:
        arguments_json, arguments_sha256 = canonical_tool_arguments(snapshot)
        call = ToolExecutionInput(operation_id, plan.call_id, plan.name, arguments_json, arguments_sha256)
        call.to_wire()
    except (ValueError, TypeError, AttributeError, RecursionError):
        return None
    return call


class ActivityService:
    def __init__(self, ledger: PostgresAdmissionLedger):
        self.ledger=ledger

    async def read_result(self, activity_id, operation_id) -> ReadOutcome:
        try:
            snapshot=await self.ledger.read_committed_result(activity_id,operation_id)
            return ReadOutcome(snapshot.read_status.value,snapshot)
        except AdmissionUnavailable:
            return ReadOutcome("read_unavailable")
        except ResultIntegrityError:
            return ReadOutcome("integrity_error")
        except (ValueError,TypeError):
            return ReadOutcome("invalid_input")

    async def resume_result(self, activity_id, operation_id) -> ReadOutcome:
        return await self.read_result(activity_id,operation_id)

    async def read_scope(self, activity_id):
        # None明确表示不存在，数据库未知继续以脱敏unavailable异常区分。
        return await self.ledger.inspect_scope(activity_id)

    async def revise_scope(self, activity_id, expected_scope_revision, sources):
        return await self.ledger.revise_scope(activity_id,expected_scope_revision,sources)

    async def continue_from_result(self, activity_id, parent_operation_id, new_operation_id,
                                   followup, service, config, executor_id, run_tag) -> ContinuationOutcome:
        from app.worker.one_call import OneCallInput,run_one_call,validate_identity
        from app.worker.session import SessionConfig
        try:
            validate_identity(activity_id,executor_id,new_operation_id,run_tag)
            from app.learning.contracts import FIRST_PREFIX, NEXT_PREFIX
            from app.learning.teaching_contracts import TEACHING_PREFIX_MODEL, TEACHING_PREFIX_TOOL
            if new_operation_id.startswith((FIRST_PREFIX, NEXT_PREFIX)):
                return ContinuationOutcome("invalid_input")
            if new_operation_id.startswith((TEACHING_PREFIX_MODEL, TEACHING_PREFIX_TOOL)) \
                    or parent_operation_id.startswith((TEACHING_PREFIX_MODEL, TEACHING_PREFIX_TOOL)):
                # G8：教学操作不接受通用继续绕过教学阶段。
                return ContinuationOutcome("invalid_input")
            self.ledger._bounded_name(parent_operation_id,"parent_operation_id")
            if parent_operation_id==new_operation_id or type(followup) is not str or not followup.strip():
                return ContinuationOutcome("invalid_input")
        except (ValueError,TypeError,AttributeError):
            return ContinuationOutcome("invalid_input")
        from app.interview.contracts import InterviewRefusal
        try: await self.ledger.require_non_interview(activity_id)
        except InterviewRefusal as exc: return ContinuationOutcome(exc.code)
        if parent_operation_id.startswith("int10m.") or new_operation_id.startswith("int10m."):return ContinuationOutcome("interview_parent_forbidden")
        selected=await self.ledger.read_memory_selection(activity_id)
        if selected.get('selected') or not selected.get('eligible',True):
            return ContinuationOutcome('memory_profile_required')
        # 同键只核事实；无正文、未知或不可读都不生成替代新键、不重发。
        existing=await self.read_result(activity_id,new_operation_id)
        if existing.status != ResultReadStatus.NO_OPERATION.value:
            return ContinuationOutcome(existing.status,existing)
        parent=await self.read_result(activity_id,parent_operation_id)
        if parent.status != ResultReadStatus.COMMITTED_CURRENT.value:
            mapping={"committed_history_cancelled":"cancelled","invalidated_scope_changed":"result_invalidated","invalidated_source":"source_invalid"}
            return ContinuationOutcome(mapping.get(parent.status,parent.status),parent)
        if parent.snapshot.kind != "model":
            # 工具结果仅可只读；不作为模型父输入，也不启动任何监督。
            return ContinuationOutcome("result_kind_not_consumable",parent)
        if parent_operation_id.startswith((FIRST_PREFIX, NEXT_PREFIX)):
            return ContinuationOutcome("learning_followup_required",parent)
        if type(service) is not ModelServiceConfig or type(config) is not SessionConfig:
            return ContinuationOutcome("invalid_input")
        # 确定的 one_call 配置冲突在监督线程及任何 launcher 副作用之前拒绝。
        if config.request_timeout_seconds > 120 or service.timeout_seconds > config.request_timeout_seconds:
            return ContinuationOutcome("invalid_input")
        snapshot=parent.snapshot
        try:
            validate_business_payload(snapshot.payload,snapshot.payload_format,snapshot.payload_sha256)
        except (ValueError,TypeError,AttributeError):
            return ContinuationOutcome("integrity_error",parent)
        try:
            value=json.loads(snapshot.payload)["value"]
            content=value if snapshot.payload_format=="text" else json.dumps(value,ensure_ascii=False,separators=(",",":"),allow_nan=False)
            ref=ResultConsumptionRef(activity_id=activity_id,operation_id=parent_operation_id,
                scope_revision=snapshot.scope_revision,payload_sha256=snapshot.payload_sha256)
            request=ModelCallRequest(messages=[{"role":"assistant","content":content},
                {"role":"user","content":followup}],max_output_tokens=min(256,service.max_output_tokens_limit),
                input_result=ref,allowed_tools=frozenset())
            OneCallInput(new_operation_id,request,service).to_wire()
        except ValidationError as exc:
            too_large=any(x["type"] in {"string_too_long","too_long"} for x in exc.errors(include_input=False))
            return ContinuationOutcome("input_too_large" if too_large else "invalid_input")
        except ValueError as exc:
            too_large=str(exc) in {"one_call data exceeds contract","internal one_call supports at most 65536 configured body bytes"}
            return ContinuationOutcome("input_too_large" if too_large else "invalid_input")
        except (TypeError,AttributeError,RecursionError):
            return ContinuationOutcome("invalid_input")
        task=asyncio.create_task(asyncio.to_thread(run_one_call,self.ledger,config,activity_id,
            executor_id,new_operation_id,request,service,run_tag=run_tag))
        cancelled=False
        # shield只隔离调用方取消；监督线程由既有deadline/自有Job收尾，禁止后台遗留。
        while True:
            try:
                supervision=await asyncio.shield(task)
                break
            except Exception:
                if cancelled:raise asyncio.CancelledError
                return ContinuationOutcome("supervision_unknown",await self.read_result(activity_id,new_operation_id))
            except asyncio.CancelledError:
                cancelled=True
                if task.done():
                    supervision=task.result()
                    break
        if cancelled:raise asyncio.CancelledError
        business=await self.read_result(activity_id,new_operation_id)
        settlement=SettlementFacts(supervision.settled_seconds,supervision.reserved_seconds,
            supervision.pending_fold_seconds,supervision.cleanup_incomplete)
        status=business.status
        if business.status in ("no_operation","unresolved"):
            status=supervision.state if supervision.state in {"cancelled","budget_exhausted"} else "supervision_unknown"
            receipt=supervision.model_receipt
            if receipt and receipt["result"].get("error_code"):
                status=receipt["result"]["error_code"]
        return ContinuationOutcome(status,business,supervision,settlement)

    async def execute_tool_action(self, activity_id, operation_id, plan, config,
                                  executor_id, run_tag) -> ToolActionOutcome:
        """显式一次工具动作；唯一finite_calculate，经固定受控worker执行。

        工具次数在准入提交时持久耗用；同键同身份只读返回已知事实，同键异
        身份或模型占键明确冲突且零监督；UNKNOWN/无正文/暂不可读都不启动
        新监督、不生成替代键。服务不claim、不execute、不settle。
        """
        from app.worker.one_call import validate_identity
        from app.worker.one_tool import run_one_tool
        from app.worker.session import SessionConfig
        try:
            validate_identity(activity_id,executor_id,operation_id,run_tag)
        except (ValueError,TypeError,AttributeError):
            return ToolActionOutcome("invalid_input")
        from app.interview.contracts import InterviewRefusal
        try: await self.ledger.require_non_interview(activity_id)
        except InterviewRefusal as exc: return ToolActionOutcome(exc.code)
        selected=await self.ledger.read_memory_selection(activity_id)
        if (selected.get('selected') or not selected.get('eligible',True)) and not operation_id.startswith('teach8t.'):
            return ToolActionOutcome('memory_profile_required')
        call=_canonical_tool_execution_input(operation_id,plan)
        if call is None:
            return ToolActionOutcome("invalid_input")
        # 同键只核事实；任何既存状态都不在此获得第二次执行资格。
        existing=await self.read_result(activity_id,operation_id)
        if existing.status != ResultReadStatus.NO_OPERATION.value:
            snapshot=existing.snapshot
            if snapshot is None:
                # 读取不可用或完整性错误：原样返回只读状态，不冲突定性、不监督。
                return ToolActionOutcome(existing.status,existing)
            if snapshot.kind != "tool":
                return ToolActionOutcome("operation_key_conflict",existing)
            if (snapshot.tool_call_id != call.call_id
                    or snapshot.arguments_sha256 != call.arguments_sha256):
                return ToolActionOutcome("tool_input_conflict",existing)
            return ToolActionOutcome(existing.status,existing)
        if type(config) is not SessionConfig:
            return ToolActionOutcome("invalid_input")
        # 确定的工具配置冲突在监督线程及任何launcher副作用之前拒绝。
        if config.request_timeout_seconds > 120:
            return ToolActionOutcome("invalid_input")
        task=asyncio.create_task(asyncio.to_thread(run_one_tool,self.ledger,config,activity_id,
            executor_id,call,run_tag=run_tag))
        cancelled=False
        # shield只隔离调用方取消；监督线程由既有deadline/自有Job收尾。
        while True:
            try:
                supervision=await asyncio.shield(task)
                break
            except Exception:
                if cancelled:raise asyncio.CancelledError
                return ToolActionOutcome("supervision_unknown",await self.read_result(activity_id,operation_id))
            except asyncio.CancelledError:
                cancelled=True
                if task.done():
                    supervision=task.result()
                    break
        if cancelled:raise asyncio.CancelledError
        business=await self.read_result(activity_id,operation_id)
        settlement=SettlementFacts(supervision.settled_seconds,supervision.reserved_seconds,
            supervision.pending_fold_seconds,supervision.cleanup_incomplete)
        status=business.status
        if business.status in ("no_operation","unresolved"):
            status=supervision.state if supervision.state in {"cancelled","budget_exhausted"} else "supervision_unknown"
            receipt=supervision.tool_receipt
            if receipt and receipt["result"].get("error_code"):
                status=receipt["result"]["error_code"]
        return ToolActionOutcome(status,business,supervision,settlement)

    # --- G6 活动工作区薄包装（TASK-095）：只读与既有取消；不新增语义。 ---

    async def probe_storage(self) -> bool:
        return await self.ledger.probe_storage()

    async def list_activities(self, *, limit, after_created_at=None, after_activity_id=None):
        return await self.ledger.list_activities(
            limit=limit, after_created_at=after_created_at, after_activity_id=after_activity_id,
        )

    async def read_activity(self, activity_id):
        return await self.ledger.read_activity_facts(activity_id)

    async def list_activity_operations(self, activity_id, *, limit, after_operation_id=None):
        return await self.ledger.list_operations(
            activity_id, limit=limit, after_operation_id=after_operation_id,
        )

    async def read_operation(self, activity_id, operation_id):
        return await self.ledger.read_operation(activity_id, operation_id)

    async def list_scope_source_versions(self, source_ids):
        return await self.ledger.read_scope_source_versions(source_ids)

    async def cancel_activity(self, activity_id):
        """既有幂等仓储取消的薄包装；不新增退款或停止权。"""
        return await self.ledger.cancel_activity(activity_id)
