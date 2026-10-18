"""PostgreSQL 活动与调用账本。

所有会影响准入的写入都使用短事务。锁顺序固定为来源 UUID 排序、活动、操作；
网络调用由上层在事务结束后执行。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import enum
import json
import math
import re
from typing import Awaitable, Callable, TypeVar
from uuid import UUID, uuid4

from app.capabilities.contracts import (
    AdmissionDenied,
    AdmissionIntent,
    AdmissionPermit,
    AdmissionUnavailable,
    CallContext,
    LedgerDisposition,
    LedgerOutcome,
    RecordOutcome,
    ResultConsumptionRef,
    ToolAdmissionPermit,
    ToolExecutionInput,
    ToolIntent,
    validate_business_payload,
)
from app.capabilities.tools import MAX_ABS_RESULT as _MAX_ABS_TOOL_RESULT
from app.learning.teaching_contracts import TeachingRefusal

from .teaching_repository import TeachingLedgerMethods
from .interview_repository import InterviewLedgerMethods
from app.interview.contracts import InterviewRefusal
from app.memory.repository import MemoryLedgerMethods
from app.memory.contracts import MemorySelectionInput, MemoryRefusal
from app.learning.contracts import canonical, sha
from app.preview.repository import HtmlLedgerMethods


_T = TypeVar("_T")
_SAFE_FACT = re.compile(r"^[A-Za-z0-9._:/-]+$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_MAX_USAGE = 2_147_483_647
_MAX_TOOL_CALLS = 2_147_483_647
_MAX_RESPONSE_BYTES = 67_108_864
# 时间账本（TASK-077）：M/R/S 计数上限与 004 迁移的 BIGINT CHECK 上界一致。
_MAX_RUNNING_SECONDS = 2_147_483_647
_MAX_WINDOW_SECONDS = 3_600
_MAX_WINDOWS_SESSION_ID = 4_294_967_295


class ActivityLedgerConflict(RuntimeError):
    """活动状态或调用方提供的版本已不再适用。"""


def _tool_payload_semantics_ok(payload_format: str | None, payload: str | None) -> bool:
    """工具成功正文必须是 text 封套内原精度 50 规范有限十进制字符串。

    除通用封套校验外的应用层 kind 条件校验：合法 JSON 形态、有限数值域
    （绝对值不超过工具原上限）、且重新规范化后逐字节等于存储值。007 的
    通用格式 CHECK 不冒充跨表工具约束；同表的 model json 许可不自动给 tool。
    """
    if payload_format != "text" or not isinstance(payload, str):
        return False
    try:
        parsed = json.loads(payload, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
    except (json.JSONDecodeError, ValueError, RecursionError):
        return False
    if not isinstance(parsed, dict) or set(parsed) != {"format", "value"} or parsed["format"] != "text":
        return False
    value = parsed["value"]
    if not isinstance(value, str) or not value:
        return False
    try:
        number = Decimal(value)
        if not number.is_finite() or abs(number) > _MAX_ABS_TOOL_RESULT:
            return False
        return format(number.normalize(), "f") == value
    except (InvalidOperation, ValueError, ArithmeticError):
        return False


class ResultIntegrityError(RuntimeError):
    """持久结果行与权威绑定或规范字节不一致；失败关闭，不冒充读取状态。"""


class ResultReadStatus(enum.Enum):
    """read/list 的业务读取状态；不是业务成功，也不是执行/发送资格。"""

    COMMITTED_CURRENT = "committed_current"
    COMMITTED_HISTORY_CANCELLED = "committed_history_cancelled"
    INVALIDATED_SCOPE_CHANGED = "invalidated_scope_changed"
    INVALIDATED_SOURCE = "invalidated_source"
    INVALIDATED_MEMORY = "invalidated_memory"
    INVALIDATED_INTERVIEW = "invalidated_interview"
    UNRESOLVED = "unresolved"
    TERMINAL_WITHOUT_PAYLOAD = "terminal_without_payload"
    NO_OPERATION = "no_operation"


@dataclass(frozen=True)
class CommittedResultSnapshot:
    """read/list 的业务读取快照；只在有效绑定下携带正文，不授予新执行/写入权。"""

    activity_id: str
    operation_id: str
    read_status: ResultReadStatus
    admission_id: str | None = None
    execution_generation: int | None = None
    scope_revision: int | None = None
    provider: str | None = None
    configured_model: str | None = None
    finish_reason: str | None = None
    returned_model: str | None = None
    remote_request_id: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    response_bytes: int | None = None
    payload_format: str | None = None
    payload: str | None = field(default=None, repr=False)
    payload_sha256: str | None = field(default=None, repr=False)
    committed_at: datetime | None = None
    activity_status_now: str | None = None
    activity_scope_revision_now: int | None = None
    # G5 轻量类型元数据：NO_OPERATION 全为 None，不伪造 model。
    kind: str | None = None
    tool_call_id: str | None = None
    arguments_sha256: str | None = None
    tool_names: tuple[str, ...] | None = None


class SettleResult(enum.Enum):
    """settle_execution_window 的持久结果；不是执行资格，也不是停止证明。"""

    SETTLED = "settled"
    ALREADY_SETTLED = "already_settled"


class CloseResult(enum.Enum):
    CLOSED = "closed"
    ALREADY_CLOSED = "already_closed"


@dataclass(frozen=True)
class WindowSnapshot:
    status: str
    execution_generation: int
    running_reserved_seconds: int
    dispatch_closed: bool
    running_owner_session_id: int | None = None
    lease_recoverable: bool = False
    sources_valid: bool = False


@dataclass(frozen=True)
class SourceSnapshot:
    source_id: str
    version_id: str
    revision: int


@dataclass(frozen=True)
class ScopeSnapshot:
    activity_id: str
    scope_revision: int
    sources: tuple[SourceSnapshot, ...]


class ScopeConflict(ActivityLedgerConflict, AdmissionDenied):
    """来源集合在取提示与活动锁之间变化；整事务回滚。"""


@dataclass(frozen=True)
class ActivitySpec:
    activity_id: str
    sources: tuple[SourceSnapshot, ...]
    deadline_at: datetime
    max_requests: int
    max_cost_microunits: int
    reserve_cost_microunits: int
    max_request_bytes: int
    max_output_tokens: int
    max_running_seconds: int
    allowed_models: tuple[tuple[str, str], ...]
    allowed_tools: tuple[str, ...] = ()
    scope_revision: int = 1
    # G5：独立工具次数上限；None=未配置（必须已用 0），0=明确禁用。
    max_tool_calls: int | None = None


@dataclass(frozen=True)
class ActivityLease:
    activity_id: str
    executor_id: str
    execution_generation: int
    scope_revision: int
    lease_expires_at: datetime
    window_seconds: int
    running_owner_session_id: int | None = None


@dataclass(frozen=True)
class UnresolvedOperation:
    """活动内未决操作的观察快照；它只用于发现与对账，不是后续写入的授权。"""

    operation_id: str
    admission_id: str
    executor_id: str
    execution_generation: int
    scope_revision: int
    reserved_at: datetime
    dispatch_started_at: datetime | None


# --- G6 活动工作区只读投影（TASK-095）。以下类型只承载已持久事实，不含
# admission/executor/G/remote_request_id 等内部标识；不构成任何执行资格。 ---


@dataclass(frozen=True)
class ActivitySourceView:
    """活动范围逐来源视图；valid 与 claim/admit 的有效性口径一致。"""

    source_id: str
    title: str
    valid: bool


@dataclass(frozen=True)
class ActivityFactView:
    """活动详情只读投影；列表与详情共用同一投影与同一单条 SQL。"""

    activity_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    deadline_at: datetime
    cancelled_at: datetime | None
    scope_revision: int
    max_requests: int
    requests_reserved: int
    max_cost_microunits: int
    cost_reserved_microunits: int
    reserve_cost_microunits: int
    max_running_seconds: int
    running_reserved_seconds: int
    running_settled_seconds: int
    last_settled_generation: int | None
    last_settled_seconds: int | None
    max_tool_calls: int | None
    tools_reserved: int
    allowed_models: tuple[tuple[str, str], ...]
    sources: tuple[ActivitySourceView, ...]
    memory_selection: dict | None = None
    business_domain: str | None = None


@dataclass(frozen=True)
class OperationRow:
    """操作只读投影；read_status 与 read_committed_result 同源判定。"""

    operation_id: str
    kind: str
    state: str
    disposition: str | None
    error_code: str | None
    reserved_at: datetime
    dispatch_started_at: datetime | None
    recorded_at: datetime | None
    prompt_tokens: int | None
    completion_tokens: int | None
    finish_reason: str | None
    returned_model: str | None
    committed_at: datetime | None
    read_status: ResultReadStatus
    payload_available: bool
    payload: str | None = field(default=None, repr=False)


class PostgresAdmissionLedger(TeachingLedgerMethods, MemoryLedgerMethods, InterviewLedgerMethods, HtmlLedgerMethods):
    """`AdmissionLedger` 的失败关闭 PostgreSQL 实现。

    连接、锁和语句都有限时；任何数据库错误对准入调用统一表现为 unavailable，
    不把连接串或服务器错误泄露给上层。G8 教学方法经 TeachingLedgerMethods
    Mixin 注入（同一 _transaction/锁序；teach8m./teach8t. 前缀在锁内薄扩展）。
    """

    def __init__(
        self,
        dsn: str,
        *,
        connect_timeout_seconds: int = 3,
        statement_timeout_ms: int = 3_000,
        lock_timeout_ms: int = 2_000,
        data_guard: dict | None = None,
    ) -> None:
        if not dsn:
            raise ValueError("数据库连接不能为空")
        if not 1 <= connect_timeout_seconds <= 10:
            raise ValueError("连接超时必须在 1 到 10 秒之间")
        if not 100 <= statement_timeout_ms <= 30_000:
            raise ValueError("语句超时范围非法")
        if not 100 <= lock_timeout_ms <= statement_timeout_ms:
            raise ValueError("锁超时范围非法")
        self._dsn = dsn
        self._connect_timeout = connect_timeout_seconds
        self._statement_timeout_ms = statement_timeout_ms
        self._lock_timeout_ms = lock_timeout_ms
        self.mutation_gate = None
        self.data_enabled = None
        self.data_readonly = False
        self.data_owned_id = None
        if data_guard is not None:
            from app.data_exit.maintenance import worker_gate
            self.mutation_gate, self.data_owned_id = worker_gate(data_guard)
            self.data_enabled = True

    async def _transaction(self, operation: Callable[[object], Awaitable[_T]]) -> _T:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            raise AdmissionUnavailable("PostgreSQL 驱动不可用") from None
        guarded = None
        outgoing = None
        try:
            connection = await psycopg.AsyncConnection.connect(
                self._dsn,
                connect_timeout=self._connect_timeout,
                row_factory=dict_row,
            )
            async with connection:
                async with connection.transaction():
                    await connection.execute(
                        "SELECT set_config('statement_timeout', %s, true)",
                        (f"{self._statement_timeout_ms}ms",),
                    )
                    await connection.execute(
                        "SELECT set_config('lock_timeout', %s, true)",
                        (f"{self._lock_timeout_ms}ms",),
                    )
                    await connection.execute(
                        "SET LOCAL idle_in_transaction_session_timeout = '5s'"
                    )
                    if self.data_enabled is None:
                        cursor=await connection.execute("SELECT to_regclass('public.data_control') IS NOT NULL AS enabled")
                        self.data_enabled=(await cursor.fetchone())['enabled']
                    if self.data_enabled:
                        from app.data_exit.maintenance import GuardedAsyncConnection, outgoing_operation, CLOSE_LANE
                        from app.data_exit.contracts import DataError
                        if self.mutation_gate is not None and outgoing_operation(operation):
                            outgoing=self.mutation_gate.outgoing_section()
                            outgoing.__enter__()
                        guarded=GuardedAsyncConnection(connection,self.mutation_gate,self.data_readonly)
                        if self.data_owned_id is not None:
                            with self.mutation_gate.close_lane(self.data_owned_id):
                                result=await operation(guarded)
                        else:result=await operation(guarded)
                    else:result=await operation(connection)
                return result
        except (AdmissionDenied, ActivityLedgerConflict):
            raise
        except psycopg.Error:
            raise AdmissionUnavailable("持久准入账本暂不可用") from None
        finally:
            if guarded is not None:guarded.close_permit()
            if outgoing is not None:outgoing.__exit__(None,None,None)

    @staticmethod
    def _uuid(value: str, field: str) -> str:
        try:
            return str(UUID(value))
        except (ValueError, TypeError, AttributeError):
            raise ValueError(f"{field} 必须是 UUID") from None

    @staticmethod
    def _bounded_name(value: str, field: str, *, maximum: int = 128) -> str:
        if not isinstance(value, str) or not 1 <= len(value) <= maximum or not _SAFE_FACT.fullmatch(value):
            raise ValueError(f"{field} 格式非法")
        return value

    @classmethod
    def _validate_spec(cls, spec: ActivitySpec) -> tuple[str, tuple[SourceSnapshot, ...]]:
        activity_id = cls._uuid(spec.activity_id, "activity_id")
        if spec.scope_revision < 1:
            raise ValueError("scope_revision 必须为正数")
        if not spec.sources:
            raise ValueError("活动必须具有有限来源快照")
        normalized_sources = cls._normalize_scope(spec.sources)
        now = datetime.now(timezone.utc)
        if spec.deadline_at.tzinfo is None or spec.deadline_at <= now:
            raise ValueError("活动期限必须是未来的带时区时间")
        positive_limits = (
            spec.max_requests,
            spec.max_cost_microunits,
            spec.reserve_cost_microunits,
            spec.max_request_bytes,
            spec.max_output_tokens,
        )
        if any(isinstance(item, bool) or not isinstance(item, int) or item <= 0 for item in positive_limits):
            raise ValueError("可执行活动的全部限额必须为正整数")
        if (
            isinstance(spec.max_running_seconds, bool)
            or not isinstance(spec.max_running_seconds, int)
            or not 0 < spec.max_running_seconds <= _MAX_RUNNING_SECONDS
        ):
            raise ValueError("活动时间预算必须是 1 到 2147483647 之间的整数")
        if spec.reserve_cost_microunits > spec.max_cost_microunits:
            raise ValueError("单次保守预留不能超过累计费用上限")
        if not spec.allowed_models:
            raise ValueError("活动必须显式允许至少一个 provider/model")
        models = set()
        for provider, model in spec.allowed_models:
            models.add((cls._bounded_name(provider, "provider", maximum=64), cls._bounded_name(model, "model")))
        if len(models) != len(spec.allowed_models):
            raise ValueError("允许模型不能重复")
        if len(spec.allowed_tools) > 32 or len(set(spec.allowed_tools)) != len(spec.allowed_tools):
            raise ValueError("允许工具数量或唯一性非法")
        for tool in spec.allowed_tools:
            cls._bounded_name(tool, "tool", maximum=64)
        if spec.max_tool_calls is not None and (
            isinstance(spec.max_tool_calls, bool)
            or not isinstance(spec.max_tool_calls, int)
            or not 0 <= spec.max_tool_calls <= _MAX_TOOL_CALLS
        ):
            raise ValueError("工具次数上限必须是 0 到 2147483647 之间的整数或 None")
        return activity_id, normalized_sources

    async def _source_rows(self, connection: object, activity_id: str) -> list[dict]:
        cursor = await connection.execute(
            """SELECT source_id, version_id, source_revision
                 FROM activity_scope_sources
                WHERE activity_id = %s
                ORDER BY source_id""",
            (activity_id,),
        )
        return list(await cursor.fetchall())

    async def _lock_sources(self, connection: object, snapshots: list[dict] | tuple[SourceSnapshot, ...]) -> bool:
        valid = True
        for snapshot in snapshots:
            source_id = snapshot["source_id"] if isinstance(snapshot, dict) else snapshot.source_id
            version_id = snapshot["version_id"] if isinstance(snapshot, dict) else snapshot.version_id
            revision = snapshot["source_revision"] if isinstance(snapshot, dict) else snapshot.revision
            cursor = await connection.execute(
                "SELECT current_version, revision FROM material_sources WHERE id = %s FOR UPDATE",
                (source_id,),
            )
            row = await cursor.fetchone()
            if (
                row is None
                or row["current_version"] is None
                or str(row["current_version"]) != str(version_id)
                or row["revision"] != revision
            ):
                valid = False
        return valid

    @staticmethod
    def _scope_key(rows):
        return tuple(sorted((str(x["source_id"]),str(x["version_id"]),x["source_revision"]) for x in rows))

    async def _verify_scope_hint(self, connection, activity_id, hint):
        if self._scope_key(hint) != self._scope_key(await self._source_rows(connection,activity_id)):
            raise ScopeConflict("scope_conflict")

    @classmethod
    def _normalize_scope(cls, sources):
        if not isinstance(sources,(tuple,list)) or len(sources)>128:
            raise ValueError("invalid_input")
        normalized=[]
        for x in sources:
            if type(x) is not SourceSnapshot or type(x.source_id) is not str or type(x.version_id) is not str or type(x.revision) is not int or not 0<=x.revision<=2_147_483_647:
                raise ValueError("invalid_input")
            normalized.append(SourceSnapshot(cls._uuid(x.source_id,"source_id"),cls._uuid(x.version_id,"version_id"),x.revision))
        normalized.sort(key=lambda x:UUID(x.source_id).int)
        if len({x.source_id for x in normalized})!=len(normalized):raise ValueError("invalid_input")
        return tuple(normalized)

    async def inspect_scope(self, activity_id: str) -> ScopeSnapshot | None:
        activity_id=self._uuid(activity_id,"activity_id")
        async def operation(connection):
            cursor=await connection.execute("""SELECT a.scope_revision,
                COALESCE(jsonb_agg(jsonb_build_array(s.source_id,s.version_id,s.source_revision)
                ORDER BY s.source_id) FILTER (WHERE s.source_id IS NOT NULL),'[]'::jsonb) AS sources
                FROM activities a LEFT JOIN activity_scope_sources s ON s.activity_id=a.id
                WHERE a.id=%s GROUP BY a.id""",(activity_id,))
            row=await cursor.fetchone()
            if row is None:return None
            return ScopeSnapshot(activity_id,row["scope_revision"],tuple(SourceSnapshot(*x) for x in row["sources"]))
        return await self._transaction(operation)

    async def revise_scope(self, activity_id: str, expected_scope_revision: int, sources) -> ScopeSnapshot:
        activity_id=self._uuid(activity_id,"activity_id")
        if type(expected_scope_revision) is not int or not 1<=expected_scope_revision<=2_147_483_647:
            raise ValueError("invalid_input")
        sources=self._normalize_scope(sources)
        async def operation(connection):
            hint=await self._source_rows(connection,activity_id)
            # 旧新并集先按UUID锁定；来源有效性只针对新集合。
            ids=sorted({str(x["source_id"]) for x in hint}|{x.source_id for x in sources},key=lambda x:UUID(x).int)
            locked={}
            for source_id in ids:
                cursor=await connection.execute("SELECT current_version,revision FROM material_sources WHERE id=%s FOR UPDATE",(source_id,))
                locked[source_id]=await cursor.fetchone()
            cursor=await connection.execute("SELECT * FROM activities WHERE id=%s FOR UPDATE",(activity_id,))
            row=await cursor.fetchone()
            await self._verify_scope_hint(connection,activity_id,hint)
            await self._interview_require_non_domain(connection,activity_id)
            return await self._apply_scope_locked(connection,activity_id,row,locked,expected_scope_revision,sources)
        return await self._transaction(operation)

    async def _apply_scope_locked(self,connection,activity_id,row,locked,expected_scope_revision,sources,force_revision=False):
        if row is None:raise ActivityLedgerConflict("not_found")
        if row["scope_revision"]!=expected_scope_revision:raise ScopeConflict("scope_conflict")
        if row["status"]=="cancelled":raise ActivityLedgerConflict("cancelled")
        if row["status"] not in ("pending","running") or row["deadline_at"]<=datetime.now(timezone.utc):
            raise ActivityLedgerConflict("activity_expired")
        for x in sources:
            actual=locked[x.source_id]
            if actual is None or str(actual["current_version"])!=x.version_id or actual["revision"]!=x.revision:
                raise ActivityLedgerConflict("source_invalid")
        new_key=tuple(sorted((x.source_id,x.version_id,x.revision) for x in sources))
        if not force_revision and self._scope_key(await self._source_rows(connection,activity_id))==new_key:return ScopeSnapshot(activity_id,expected_scope_revision,sources)
        if expected_scope_revision==2_147_483_647:raise ActivityLedgerConflict("scope_revision_limit")
        await connection.execute("DELETE FROM activity_scope_sources WHERE activity_id=%s",(activity_id,))
        for x in sources:
            await connection.execute("INSERT INTO activity_scope_sources(activity_id,source_id,version_id,source_revision) VALUES (%s,%s,%s,%s)",(activity_id,x.source_id,x.version_id,x.revision))
        await connection.execute("UPDATE activities SET scope_revision=scope_revision+1,updated_at=CURRENT_TIMESTAMP WHERE id=%s",(activity_id,))
        return ScopeSnapshot(activity_id,expected_scope_revision+1,sources)

    async def create_activity(self, spec: ActivitySpec, *, memory_selection=None) -> None:
        activity_id, sources = self._validate_spec(spec)
        selection = None if memory_selection is None else MemorySelectionInput.model_validate(memory_selection.model_dump() if isinstance(memory_selection, MemorySelectionInput) else memory_selection)
        create_sha = sha(canonical({'activity_id':activity_id,'source_ids':sorted(x.source_id for x in sources),'memory_selection':selection.model_dump() if selection else None}))

        async def operation(connection: object) -> None:
            if selection:
                await self._memory_assert_schema(connection)
                cursor=await connection.execute("SELECT create_request_sha256 FROM public.activity_memory_bindings WHERE activity_id=%s",(activity_id,))
                previous=await cursor.fetchone()
                if previous is not None:
                    if previous['create_request_sha256']==create_sha:return
                    raise MemoryRefusal('activity_exists_conflict','活动编号已绑定不同选择')
                extra=[{'source_id':x.source_id,'version_id':x.version_id,'source_revision':x.revision} for x in sources]
                memory_state=await self._memory_lock_prefix(connection,activity_id,extra_sources=extra,memory_ids=[x.memory_id for x in selection.entries])
                # 全部来源已在记忆/活动之前锁住；此处只读复核，不反向加新来源锁。
                cursor=await connection.execute("SELECT id,current_version,revision FROM material_sources WHERE id=ANY(%s::uuid[])",([x.source_id for x in sources],))
                source_rows={str(r['id']):r for r in await cursor.fetchall()}
                sources_valid=all(x.source_id in source_rows and str(source_rows[x.source_id]['current_version'])==x.version_id and source_rows[x.source_id]['revision']==x.revision for x in sources)
            else:
                sources_valid=await self._lock_sources(connection,sources)
            if not sources_valid:
                raise ActivityLedgerConflict("来源快照已撤销或被替换")
            cursor = await connection.execute("SELECT 1 FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            if await cursor.fetchone() is not None:
                raise ActivityLedgerConflict("活动 ID 已存在")
            await connection.execute(
                """INSERT INTO activities(
                       id, status, scope_revision, execution_generation, deadline_at,
                       max_requests, max_cost_microunits, reserve_cost_microunits,
                       max_request_bytes, max_output_tokens,
                       max_running_seconds, running_reserved_seconds, running_settled_seconds,
                       allowed_tools, max_tool_calls)
                     VALUES (%s, 'pending', %s, 0, %s, %s, %s, %s, %s, %s, %s, 0, 0, %s, %s)""",
                (
                    activity_id,
                    spec.scope_revision,
                    spec.deadline_at,
                    spec.max_requests,
                    spec.max_cost_microunits,
                    spec.reserve_cost_microunits,
                    spec.max_request_bytes,
                    spec.max_output_tokens,
                    spec.max_running_seconds,
                    list(spec.allowed_tools),
                    spec.max_tool_calls,
                ),
            )
            for source in sources:
                await connection.execute(
                    """INSERT INTO activity_scope_sources(
                           activity_id, source_id, version_id, source_revision)
                         VALUES (%s, %s, %s, %s)""",
                    (activity_id, source.source_id, source.version_id, source.revision),
                )
            for provider, model in sorted(spec.allowed_models):
                await connection.execute(
                    "INSERT INTO activity_allowed_models(activity_id, provider, model) VALUES (%s, %s, %s)",
                    (activity_id, provider, model),
                )

            if selection:
                await self._memory_insert_selection(connection,spec,selection,create_sha)

        await self._transaction(operation)

    async def claim_lease(
        self,
        activity_id: str,
        executor_id: str,
        *,
        lease_seconds: int,
        window_seconds: int,
        running_owner_session_id: int | None = None,
        expected_previous_generation: int | None = None,
    ) -> ActivityLease | None:
        """认领活动租约并预扣时间预算；时间预算耗尽返回 None，其余冲突仍抛异常。

        window_seconds 是本次希望预扣的执行时间窗口；实际预扣
        W_eff = min(window_seconds, 剩余预算 A = M - S - R)。
        lease_seconds、租约到期和墙钟只用于冲突判定，不构成对实际单调
        执行耗时的测量或保证。None 的唯一含义是“未获得新租约：时间预算
        耗尽”，与未知活动/已取消/过期/有效租约冲突（异常）可区分。

        代次递增规则（每条路径各一次，不硬编码示例值）：
        - 成功认领（无论是否折叠旧租约残留）：execution_generation +1，
          折叠与新租约在同一 UPDATE 原子完成；
        - 折叠后余额耗尽：提交折叠并关闭（pending、executor/lease 清空、
          代次失效）同样 +1，返回 None，不以事务内异常回滚撤销折叠；
        - 活动已是 pending 且 A=0：不写任何行、不递增代次，直接返回 None。

        低层缺省 NULL 仅供合成调用兼容，不授予旧 Job 自动恢复资格；
        生产 SUP 必须提供自身 Windows 会话号并先完成旧树核查。
        过期 running 租约按既有接续规则处理：先把真实残留 R 全额保守折叠
        入 S 并清零、关闭旧代次资格；已结算（pending、R=0）的窗口不折叠。
        不得抢占有效租约。
        """
        activity_id = self._uuid(activity_id, "activity_id")
        executor_id = self._bounded_name(executor_id, "executor_id")
        if isinstance(lease_seconds, bool) or not isinstance(lease_seconds, int) or not 1 <= lease_seconds <= 3600:
            raise ValueError("租约必须在 1 到 3600 秒之间")
        if (
            isinstance(window_seconds, bool)
            or not isinstance(window_seconds, int)
            or not 1 <= window_seconds <= _MAX_WINDOW_SECONDS
        ):
            raise ValueError("时间窗口必须在 1 到 3600 秒之间")
        if running_owner_session_id is not None and (
            type(running_owner_session_id) is not int
            or not 0 <= running_owner_session_id <= _MAX_WINDOWS_SESSION_ID
        ):
            raise ValueError("Windows 会话号必须在 DWORD 域内")
        if expected_previous_generation is not None and (
            type(expected_previous_generation) is not int or expected_previous_generation < 0
        ):
            raise ValueError("旧执行代次必须是非负整数")

        async def operation(connection: object) -> ActivityLease | None:
            snapshots = await self._source_rows(connection, activity_id)
            sources_valid = bool(snapshots) and await self._lock_sources(connection, snapshots)
            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            row = await cursor.fetchone()
            await self._verify_scope_hint(connection, activity_id, snapshots)
            now = datetime.now(timezone.utc)  # 来源及活动锁均已取得。
            if row is None or not sources_valid:
                raise ActivityLedgerConflict("活动或来源快照不可用")
            if expected_previous_generation is not None and (
                row["status"] != "running"
                or row["execution_generation"] != expected_previous_generation
                or row["running_owner_session_id"] != running_owner_session_id
            ):
                raise ActivityLedgerConflict("已核查旧代次或会话身份已变化")
            if row["status"] == "cancelled" or row["deadline_at"] <= now:
                raise ActivityLedgerConflict("活动已取消或过期")
            if row["status"] == "running" and row["lease_expires_at"] is not None and row["lease_expires_at"] > now:
                raise ActivityLedgerConflict("活动已有有效租约")
            settled = row["running_settled_seconds"]
            reserved = row["running_reserved_seconds"]
            folds_residual = row["status"] == "running" and reserved > 0
            if folds_residual:
                # 允许接续的过期租约：残留预扣全额保守移入已结算并清零，
                # 旧代次资格由本次代次递增关闭。
                settled += reserved
                reserved = 0
            available = row["max_running_seconds"] - settled - reserved
            if available <= 0:
                if folds_residual:
                    # 折叠耗尽：提交折叠与关闭，返回 None；不能用事务内异常
                    # 回滚后再声称已关闭。
                    await connection.execute(
                        """UPDATE activities
                              SET status = 'pending',
                                  execution_generation = execution_generation + 1,
                                  executor_id = NULL, lease_expires_at = NULL,
                                  running_owner_session_id = NULL,
                                  dispatch_closed = TRUE,
                                  running_reserved_seconds = 0,
                                  running_settled_seconds = %s,
                                  updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s""",
                        (settled, activity_id),
                    )
                return None
            effective_window = min(window_seconds, available)
            generation = row["execution_generation"] + 1
            lease_expires_at = min(row["deadline_at"], now + timedelta(seconds=lease_seconds))
            await connection.execute(
                """UPDATE activities
                      SET status = 'running', executor_id = %s, execution_generation = %s,
                          lease_expires_at = %s, running_reserved_seconds = %s,
                          running_owner_session_id = %s,
                          dispatch_closed = FALSE,
                          running_settled_seconds = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s""",
                (executor_id, generation, lease_expires_at, effective_window,
                 running_owner_session_id, settled, activity_id),
            )
            return ActivityLease(
                activity_id,
                executor_id,
                generation,
                row["scope_revision"],
                lease_expires_at,
                effective_window,
                running_owner_session_id,
            )

        return await self._transaction(operation)

    async def inspect_window(self, activity_id: str) -> WindowSnapshot:
        """恢复入口短事务快照；来源锁沿用 claim 顺序，调用方须持活动互斥。"""
        activity_id = self._uuid(activity_id, "activity_id")

        async def operation(connection: object) -> WindowSnapshot:
            snapshots = await self._source_rows(connection, activity_id)
            sources_valid = bool(snapshots) and await self._lock_sources(connection, snapshots)
            cursor = await connection.execute(
                """SELECT status, execution_generation, running_reserved_seconds, dispatch_closed,
                          running_owner_session_id, lease_expires_at, deadline_at
                     FROM activities WHERE id = %s FOR UPDATE""",
                (activity_id,),
            )
            row = await cursor.fetchone()
            await self._verify_scope_hint(connection, activity_id, snapshots)
            if row is None:
                raise ActivityLedgerConflict("活动不存在")
            now = datetime.now(timezone.utc)  # 与 claim 一致，在锁后判断资格。
            return WindowSnapshot(
                row["status"], row["execution_generation"],
                row["running_reserved_seconds"], row["dispatch_closed"],
                row["running_owner_session_id"],
                bool((row["lease_expires_at"] is None or row["lease_expires_at"] <= now)
                     and row["deadline_at"] > now),
                sources_valid,
            )

        return await self._transaction(operation)

    async def begin_window_close(
        self, activity_id: str, executor_id: str, execution_generation: int,
    ) -> CloseResult:
        """只关闭当前代次的出站门；不退款、不改预扣或代次。"""
        activity_id = self._uuid(activity_id, "activity_id")
        executor_id = self._bounded_name(executor_id, "executor_id")
        if (
            isinstance(execution_generation, bool)
            or not isinstance(execution_generation, int)
            or execution_generation < 0
        ):
            raise ValueError("执行代次必须是非负整数")

        async def operation(connection: object) -> CloseResult:
            snapshots = await self._source_rows(connection, activity_id)
            await self._lock_sources(connection, snapshots)
            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            row = await cursor.fetchone()
            await self._verify_scope_hint(connection, activity_id, snapshots)
            if (
                row is None or row["status"] != "running"
                or row["executor_id"] != executor_id
                or row["execution_generation"] != execution_generation
            ):
                raise ActivityLedgerConflict("关闭请求与当前运行代次不匹配")
            if row["dispatch_closed"]:
                return CloseResult.ALREADY_CLOSED
            await connection.execute(
                """UPDATE activities SET dispatch_closed = TRUE, updated_at = CURRENT_TIMESTAMP
                     WHERE id = %s""",
                (activity_id,),
            )
            return CloseResult.CLOSED

        return await self._transaction(operation)

    async def settle_execution_window(
        self,
        activity_id: str,
        executor_id: str,
        execution_generation: int,
        *,
        window_seconds: int,
        elapsed_seconds: float,
    ) -> SettleResult:
        """结算一个执行窗口：S+=C、R-=W 并关闭本代次；仅限可信内部合成调用。

        当前无外部路由，生产组合保持未接线；本接口不提供停止证明，也不
        等于准许生产退款，未来调用方必须先证明该窗口不能继续出站/执行。

        C = ceil(elapsed_seconds)，向上取整，0 仅表示真实零耗时；C>W 直接
        拒绝，不静默钳制超额。整数范围与 004 的 SQL 列一致（BIGINT，
        实际受 W<=3600 与余额不变量约束）。

        幂等只承诺“最近一次已结算代次 G 及规范化秒数 C”的受限确认：相同
        G 且相同 C 返回 ALREADY_SETTLED 不改账；相同 G 不同 C 拒绝且不改账；
        更旧或未知 G 拒绝且不改账。五列账本不保存任意历史 executor/W，
        不虚构完整请求回放能力；确认分支的这些参数只做格式校验，不授予
        任何执行资格。提交成功但响应丢失时，按持久事实重试即得
        ALREADY_SETTLED，不重新折叠或退款。
        """
        activity_id = self._uuid(activity_id, "activity_id")
        executor_id = self._bounded_name(executor_id, "executor_id")
        if (
            isinstance(execution_generation, bool)
            or not isinstance(execution_generation, int)
            or execution_generation < 0
        ):
            raise ValueError("执行代次必须是非负整数")
        if (
            isinstance(window_seconds, bool)
            or not isinstance(window_seconds, int)
            or not 1 <= window_seconds <= _MAX_WINDOW_SECONDS
        ):
            raise ValueError("时间窗口必须在 1 到 3600 秒之间")
        if (
            isinstance(elapsed_seconds, bool)
            or not isinstance(elapsed_seconds, (int, float))
            or not math.isfinite(elapsed_seconds)
            or elapsed_seconds < 0
        ):
            raise ValueError("耗时必须是有限非负数")
        settled_seconds = math.ceil(elapsed_seconds)
        if settled_seconds > window_seconds:
            raise ValueError("结算秒数超过窗口预扣，拒绝而不钳制超额")

        async def operation(connection: object) -> SettleResult:
            snapshots = await self._source_rows(connection, activity_id)
            await self._lock_sources(connection, snapshots)
            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            row = await cursor.fetchone()
            await self._verify_scope_hint(connection, activity_id, snapshots)
            if row is None:
                raise ActivityLedgerConflict("活动不存在")
            if row["last_settled_generation"] == execution_generation:
                # 受限幂等确认先于运行态检查，已关闭（pending/cancelled）状态
                # 不会拒绝合法重试；确认不校验也不回放历史 executor/W。
                if row["last_settled_seconds"] == settled_seconds:
                    return SettleResult.ALREADY_SETTLED
                raise ActivityLedgerConflict("该代次已按不同耗时结算，拒绝冲突重试")
            if (
                row["status"] != "running"
                or row["executor_id"] != executor_id
                or row["execution_generation"] != execution_generation
                or row["running_reserved_seconds"] != window_seconds
                or not row["dispatch_closed"]
            ):
                raise ActivityLedgerConflict("执行窗口与当前运行代次不匹配")
            await connection.execute(
                """UPDATE activities
                      SET status = 'pending',
                          execution_generation = execution_generation + 1,
                          executor_id = NULL, lease_expires_at = NULL,
                          running_owner_session_id = NULL,
                          running_reserved_seconds = 0,
                          running_settled_seconds = running_settled_seconds + %s,
                          dispatch_closed = TRUE,
                          last_settled_generation = %s, last_settled_seconds = %s,
                          updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s""",
                (settled_seconds, execution_generation, settled_seconds, activity_id),
            )
            return SettleResult.SETTLED

        return await self._transaction(operation)

    async def cancel_activity(self, activity_id: str) -> int:
        """按既有锁序取消活动；在途时间预扣 R 全额保守转入 S 后清零。

        重复取消幂等：终态直接返回当前代次，不重复扣账；模型次数/费用
        预留不动，旧操作不重发（UNKNOWN 纪律由 record_outcome 保持）。
        """
        activity_id = self._uuid(activity_id, "activity_id")

        async def operation(connection: object) -> int:
            snapshots = await self._source_rows(connection, activity_id)
            await self._lock_sources(connection, snapshots)
            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            row = await cursor.fetchone()
            await self._verify_scope_hint(connection, activity_id, snapshots)
            if row is None:
                raise ActivityLedgerConflict("活动不存在")
            if row["status"] == "cancelled":
                return row["execution_generation"]
            generation = row["execution_generation"] + 1
            await connection.execute(
                """UPDATE activities
                      SET status = 'cancelled', execution_generation = %s, executor_id = NULL,
                          lease_expires_at = NULL, cancelled_at = CURRENT_TIMESTAMP,
                          running_owner_session_id = NULL,
                          dispatch_closed = TRUE,
                          running_reserved_seconds = 0,
                          running_settled_seconds = running_settled_seconds + running_reserved_seconds,
                          updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s""",
                (generation, activity_id),
            )
            return generation

        return await self._transaction(operation)

    async def recover_unknown(self, activity_id: str, *, error_code: str = "executor_lost") -> int:
        activity_id = self._uuid(activity_id, "activity_id")
        error_code = self._bounded_name(error_code, "error_code", maximum=64)

        async def operation(connection: object) -> int:
            snapshots = await self._source_rows(connection, activity_id)
            await self._lock_sources(connection, snapshots)
            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            activity = await cursor.fetchone()
            await self._verify_scope_hint(connection, activity_id, snapshots)
            if activity is None:
                raise ActivityLedgerConflict("活动不存在")
            now = datetime.now(timezone.utc)
            recoverable = (
                activity["status"] == "cancelled"
                or activity["deadline_at"] <= now
                or activity["lease_expires_at"] is None
                or activity["lease_expires_at"] <= now
            )
            if not recoverable:
                raise ActivityLedgerConflict("有效租约仍在，不能推断调用未知")
            cursor = await connection.execute(
                """SELECT operation_id FROM activity_operations
                    WHERE activity_id = %s AND state IN ('reserved', 'dispatched')
                    ORDER BY operation_id FOR UPDATE""",
                (activity_id,),
            )
            operations = list(await cursor.fetchall())
            if operations:
                await connection.execute(
                    """UPDATE activity_operations
                          SET state = 'unknown', disposition = 'unknown', error_code = %s,
                              recorded_at = CURRENT_TIMESTAMP
                        WHERE activity_id = %s AND state IN ('reserved', 'dispatched')""",
                    (error_code, activity_id),
                )
            return len(operations)
        return await self._transaction(operation)

    async def list_unresolved_operations(
        self,
        activity_id: str,
        *,
        limit: int = 100,
        after_operation_id: str | None = None,
    ) -> tuple[UnresolvedOperation, ...]:
        """有界列出本活动 reserved/dispatched 的未决操作；只读观察，不加行锁。"""
        activity_id = self._uuid(activity_id, "activity_id")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
            raise ValueError("limit 必须是 1 到 200 之间的整数")
        if after_operation_id is not None:
            after_operation_id = self._bounded_name(after_operation_id, "after_operation_id")

        conditions = "activity_id = %s AND state IN ('reserved', 'dispatched')"
        params: list[object] = [activity_id]
        if after_operation_id is not None:
            conditions += " AND operation_id > %s"
            params.append(after_operation_id)
        params.append(limit)

        async def operation(connection: object) -> tuple[UnresolvedOperation, ...]:
            cursor = await connection.execute(
                f"""SELECT operation_id, admission_id, executor_id, execution_generation,
                           scope_revision, reserved_at, dispatch_started_at
                      FROM activity_operations
                     WHERE {conditions}
                     ORDER BY operation_id
                     LIMIT %s""",
                tuple(params),
            )
            rows = list(await cursor.fetchall())
            return tuple(
                UnresolvedOperation(
                    row["operation_id"],
                    str(row["admission_id"]),
                    row["executor_id"],
                    row["execution_generation"],
                    row["scope_revision"],
                    row["reserved_at"],
                    row["dispatch_started_at"],
                )
                for row in rows
            )

        return await self._transaction(operation)

    async def recover_obsolete_operations(
        self,
        activity_id: str,
        *,
        error_code: str = "executor_lost",
        limit: int = 100,
    ) -> int:
        """把执行代次低于活动当前代次的未决操作收敛为 unknown；单批有界，不退预留、不重发。

        锁序保持来源→活动→操作；判据只用代次差，不使用墙钟。
        单次事务只锁定并改写按 operation_id 排序的前 limit 个候选，
        返回值是本批实际改动数，不代表整个活动已恢复完毕；调用方按
        有界次数/总期限重复调用至返回 0 并复查，本方法不循环、不重试。
        当前代次与未来代次操作、既有终态一律不动；不改变 recover_unknown
        的取消/租约/时钟语义，也不接 worker 或自动调用。
        limit 只约束加锁与改写行数，不约束扫描/排序输入规模，也不消除锁等待。
        """
        activity_id = self._uuid(activity_id, "activity_id")
        error_code = self._bounded_name(error_code, "error_code", maximum=64)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
            raise ValueError("limit 必须是 1 到 200 之间的整数")

        async def operation(connection: object) -> int:
            snapshots = await self._source_rows(connection, activity_id)
            await self._lock_sources(connection, snapshots)
            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            activity = await cursor.fetchone()
            await self._verify_scope_hint(connection, activity_id, snapshots)
            if activity is None:
                raise ActivityLedgerConflict("活动不存在")
            current_generation = activity["execution_generation"]
            cursor = await connection.execute(
                """SELECT operation_id FROM activity_operations
                    WHERE activity_id = %s
                      AND state IN ('reserved', 'dispatched')
                      AND execution_generation < %s
                    ORDER BY operation_id
                    LIMIT %s
                    FOR UPDATE""",
                (activity_id, current_generation, limit),
            )
            # 只锁定本批候选（Limit 位于 LockRows 之上，行锁随取出行生效）；
            # UPDATE 限定为该确切 ID 集合并重复原谓词，不重扫全部旧项。
            locked_ids = [row["operation_id"] for row in await cursor.fetchall()]
            if not locked_ids:
                return 0
            cursor = await connection.execute(
                """UPDATE activity_operations
                      SET state = 'unknown', disposition = 'unknown', error_code = %s,
                          recorded_at = CURRENT_TIMESTAMP
                    WHERE activity_id = %s
                      AND state IN ('reserved', 'dispatched')
                      AND execution_generation < %s
                      AND operation_id = ANY(%s)
                    RETURNING operation_id""",
                (error_code, activity_id, current_generation, locked_ids),
            )
            changed = list(await cursor.fetchall())
            return len(changed)

        return await self._transaction(operation)

    @staticmethod
    def _intent_fields(intent: AdmissionIntent) -> tuple[str, str, str, str, str]:
        context = intent.context
        try:
            activity_id = str(UUID(context.activity_id))
        except (ValueError, TypeError, AttributeError):
            raise AdmissionDenied("活动 ID 非法") from None
        try:
            operation_id = PostgresAdmissionLedger._bounded_name(context.operation_id, "operation_id")
            executor_id = PostgresAdmissionLedger._bounded_name(context.executor_id, "executor_id")
            provider = PostgresAdmissionLedger._bounded_name(str(intent.provider), "provider", maximum=64)
            model = PostgresAdmissionLedger._bounded_name(intent.configured_model, "model")
        except ValueError as exc:
            raise AdmissionDenied(str(exc)) from None
        if (
            isinstance(intent.request_bytes, bool)
            or not isinstance(intent.request_bytes, int)
            or intent.request_bytes <= 0
            or isinstance(intent.max_output_tokens, bool)
            or not isinstance(intent.max_output_tokens, int)
            or intent.max_output_tokens <= 0
        ):
            raise AdmissionDenied("请求限额字段非法")
        if tuple(sorted(set(intent.tool_names))) != intent.tool_names or len(intent.tool_names) > 32:
            raise AdmissionDenied("工具集合必须有限、排序且无重复")
        try:
            for tool in intent.tool_names:
                PostgresAdmissionLedger._bounded_name(tool, "tool", maximum=64)
        except ValueError as exc:
            raise AdmissionDenied(str(exc)) from None
        return activity_id, operation_id, executor_id, provider, model

    @staticmethod
    def _activity_allows(activity: dict, intent: AdmissionIntent, executor_id: str, *, now: datetime) -> bool:
        context = intent.context
        return (
            activity["status"] == "running"
            and not activity["dispatch_closed"]
            and activity["executor_id"] == executor_id
            and activity["execution_generation"] == context.execution_generation
            and activity["scope_revision"] == context.scope_revision
            and activity["lease_expires_at"] is not None
            and activity["lease_expires_at"] > now
            and activity["deadline_at"] > now
            and intent.request_bytes <= activity["max_request_bytes"]
            and intent.max_output_tokens <= activity["max_output_tokens"]
            and set(intent.tool_names).issubset(set(activity["allowed_tools"]))
            and activity["requests_reserved"] < activity["max_requests"]
            and activity["cost_reserved_microunits"] + activity["reserve_cost_microunits"]
            <= activity["max_cost_microunits"]
        )

    async def admit(self, intent: AdmissionIntent) -> AdmissionPermit:
        activity_id, operation_id, executor_id, provider, model = self._intent_fields(intent)

        async def operation(connection: object) -> AdmissionPermit:
            memory_state=await self._memory_lock_prefix(connection,activity_id)
            snapshots=memory_state['snapshots']
            sources_valid=memory_state['sources_valid']
            activity=memory_state['activity']
            await self._interview_require_call(connection,activity,operation_id,intent.interview_binding)
            if operation_id.startswith("html11m."):
                await self._html_require_call(connection,activity,operation_id,intent.html_binding)
            else:
                if intent.html_binding is not None: raise AdmissionDenied("invalid_html_profile")
                self._memory_require_call(activity,operation_id,intent.teaching_binding)
            if intent.input_result is not None and activity is not None:
                if activity["status"]=="cancelled":raise AdmissionDenied("cancelled")
                if not sources_valid:raise AdmissionDenied("source_invalid")
                if activity["scope_revision"]!=intent.context.scope_revision:raise AdmissionDenied("result_invalidated")
                if activity["requests_reserved"]>=activity["max_requests"] or activity["cost_reserved_microunits"]+activity["reserve_cost_microunits"]>activity["max_cost_microunits"]:
                    raise AdmissionDenied("budget_exhausted")
            if activity is None or not sources_valid or not self._activity_allows(
                activity, intent, executor_id, now=datetime.now(timezone.utc)
            ):
                raise AdmissionDenied("活动、来源、租约或限额拒绝本次调用")
            cursor = await connection.execute(
                "SELECT 1 FROM activity_allowed_models WHERE activity_id = %s AND provider = %s AND model = %s",
                (activity_id, provider, model),
            )
            if await cursor.fetchone() is None:
                raise AdmissionDenied("provider/model 未获活动授权")
            ref=intent.input_result
            if ref is not None:
                try:ref=ResultConsumptionRef.model_validate(ref.model_dump())
                except Exception:raise AdmissionDenied("invalid_input") from None
                if ref.activity_id!=activity_id or ref.operation_id==operation_id or intent.tool_names:
                    raise AdmissionDenied("invalid_input")
                if ref.scope_revision!=activity["scope_revision"] or ref.scope_revision!=intent.context.scope_revision:
                    raise AdmissionDenied("result_invalidated")
            if operation_id.startswith(('teach8m.','teach8t.','int10m.','html11m.')):
                await self._teaching_lock_operations(connection,activity_id)
            keys=sorted({operation_id}|({ref.operation_id} if ref else set()))
            cursor=await connection.execute("SELECT * FROM activity_operations WHERE activity_id=%s AND operation_id=ANY(%s) ORDER BY operation_id FOR UPDATE",(activity_id,keys))
            calls={x["operation_id"]:x for x in await cursor.fetchall()}
            if operation_id.startswith("teach8m."):
                # G8：模型教学命令的锁内绑定/状态/废弃复核；失败即拒且零副作用。
                try:
                    await self._locked_teaching_binding(connection, activity, operation_id,
                                                        intent.teaching_binding, "admit")
                except TeachingRefusal as exc:
                    raise AdmissionDenied(exc.code) from None
            if operation_id.startswith("int10m."):
                try: await self._locked_interview_binding(connection,activity,operation_id,intent.interview_binding,"admit")
                except InterviewRefusal as exc: raise AdmissionDenied(exc.code) from None
            if operation_id in calls:raise AdmissionDenied("操作键已经占用，不能获得第二次发送资格")
            if ref and ref.operation_id.startswith("int10m."):raise AdmissionDenied("interview_parent_forbidden")
            if ref and ref.operation_id.startswith("html11m."):raise AdmissionDenied("html_parent_forbidden")
            if ref:
                parent=calls.get(ref.operation_id)
                if parent is not None and parent["kind"]!="model":
                    # 工具结果不得成为模型父输入，即使引用结构完整、allowed_tools 为空。
                    raise AdmissionDenied("result_kind_not_consumable")
                if parent is None or parent["state"]!="received" or parent["scope_revision"]!=ref.scope_revision:
                    raise AdmissionDenied("result_invalidated")
                try:payload=await self._stored_payload_row(connection,parent)
                except (AdmissionDenied,ResultIntegrityError,ValueError):raise AdmissionDenied("integrity_error") from None
                if payload is None or payload[2]!=ref.payload_sha256:raise AdmissionDenied("result_invalidated")
                try:validate_business_payload(payload[1],payload[0],payload[2])
                except ValueError:raise AdmissionDenied("integrity_error") from None
            admission_id = str(uuid4())
            await connection.execute(
                """UPDATE activities
                      SET requests_reserved = requests_reserved + 1,
                          cost_reserved_microunits = cost_reserved_microunits + reserve_cost_microunits,
                          updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s""",
                (activity_id,),
            )
            await connection.execute(
                """INSERT INTO activity_operations(
                       activity_id, operation_id, admission_id, executor_id,
                       execution_generation, scope_revision, provider, configured_model,
                       request_bytes, max_output_tokens, tool_names, reserved_cost_microunits,
                       kind)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'model')""",
                (
                    activity_id,
                    operation_id,
                    admission_id,
                    executor_id,
                    intent.context.execution_generation,
                    intent.context.scope_revision,
                    provider,
                    model,
                    intent.request_bytes,
                    intent.max_output_tokens,
                    list(intent.tool_names),
                    activity["reserve_cost_microunits"],
                ),
            )
            return AdmissionPermit(admission_id, operation_id, executor_id)

        return await self._transaction(operation)

    # --- G5 受控工具仓储接口：专用凭证；kind 与参数身份在锁内由 DB 行权威复核。

    @classmethod
    def _tool_permit_fields(cls, permit: ToolAdmissionPermit) -> tuple:
        if type(permit) is not ToolAdmissionPermit:
            raise AdmissionDenied("invalid_input")
        try:
            admission_id = cls._uuid(permit.admission_id, "admission_id")
            operation_id = cls._bounded_name(permit.operation_id, "operation_id")
            executor_id = cls._bounded_name(permit.executor_id, "executor_id")
            activity_id = cls._uuid(permit.activity_id, "activity_id")
            tool_name = cls._bounded_name(permit.tool_name, "tool_name", maximum=64)
            tool_call_id = cls._bounded_name(permit.tool_call_id, "tool_call_id")
        except ValueError as exc:
            raise AdmissionDenied(str(exc)) from None
        if type(permit.execution_generation) is not int or permit.execution_generation < 0:
            raise AdmissionDenied("execution_generation 非法")
        if type(permit.scope_revision) is not int or permit.scope_revision < 1:
            raise AdmissionDenied("scope_revision 非法")
        if type(permit.arguments_sha256) is not str or _HEX64.fullmatch(permit.arguments_sha256) is None:
            raise AdmissionDenied("arguments_sha256 非法")
        return (
            admission_id, operation_id, executor_id, activity_id,
            permit.execution_generation, permit.scope_revision,
            tool_name, tool_call_id, permit.arguments_sha256,
        )

    @staticmethod
    def _tool_identity_matches(operation: dict, fields: tuple) -> bool:
        (_, operation_id, executor_id, _, generation, scope, tool_name, tool_call_id, digest) = fields
        return (
            operation["kind"] == "tool"
            and operation["operation_id"] == operation_id
            and operation["executor_id"] == executor_id
            and operation["execution_generation"] == generation
            and operation["scope_revision"] == scope
            and list(operation["tool_names"]) == [tool_name]
            and operation["tool_call_id"] == tool_call_id
            and operation["arguments_sha256"] == digest
        )

    async def admit_tool_operation(self, intent: ToolIntent) -> ToolAdmissionPermit:
        """工具专用准入：来源→活动→操作键锁序；通过才同事务预留一次并＋1。

        准入提交即计一次工具尝试；响应丢失不假定 DB 无行、不重新 admit。
        上限未配置/已满、键被占用、白名单缺名、来源或租约失效一律拒绝且
        零持久副作用。工具动作不查模型 provider 白名单，也不预留模型请求
        或费用；模型与工具计数互相独立。
        """
        if type(intent) is not ToolIntent:
            raise AdmissionDenied("invalid_input")
        call = intent.call
        context = intent.context
        if type(call) is not ToolExecutionInput or type(context) is not CallContext:
            raise AdmissionDenied("invalid_input")
        try:
            context = CallContext.model_validate(context.model_dump(), strict=True)
            wire = call.to_wire()
            activity_id = self._uuid(context.activity_id, "activity_id")
            operation_id = self._bounded_name(context.operation_id, "operation_id")
            executor_id = self._bounded_name(context.executor_id, "executor_id")
        except (ValueError, TypeError, AttributeError):
            raise AdmissionDenied("invalid_input") from None
        if call.operation_id != operation_id:
            raise AdmissionDenied("invalid_input")

        async def operation(connection: object) -> ToolAdmissionPermit:
            memory_state=await self._memory_lock_prefix(connection,activity_id)
            snapshots=memory_state['snapshots']
            sources_valid=memory_state['sources_valid']
            activity=memory_state['activity']
            await self._interview_require_call(connection,activity,operation_id,tool=True)
            self._memory_require_call(activity,operation_id,tool=True)
            now = datetime.now(timezone.utc)  # 来源与活动锁均已取得。
            if activity is None or not sources_valid:
                raise AdmissionDenied("source_invalid")
            if activity["status"] == "cancelled":
                raise AdmissionDenied("cancelled")
            if activity["deadline_at"] <= now:
                raise AdmissionDenied("activity_expired")
            if (
                activity["status"] != "running"
                or activity["dispatch_closed"]
                or activity["executor_id"] != executor_id
                or activity["execution_generation"] != context.execution_generation
                or activity["lease_expires_at"] is None
                or activity["lease_expires_at"] <= now
            ):
                raise AdmissionDenied("lease_invalid")
            if activity["scope_revision"] != context.scope_revision:
                raise AdmissionDenied("scope_changed")
            if call.name not in set(activity["allowed_tools"]):
                raise AdmissionDenied("tool_not_allowed")
            maximum = activity["max_tool_calls"]
            if maximum is None:
                raise AdmissionDenied("tool_limit_unconfigured")
            if activity["tools_reserved"] >= maximum:
                # 先比较上限再 +1；不先算可能溢出的加法。
                raise AdmissionDenied("tool_limit_exhausted")
            if operation_id.startswith('teach8t.'):
                await self._teaching_lock_operations(connection,activity_id)
            cursor = await connection.execute(
                "SELECT * FROM activity_operations WHERE activity_id = %s AND operation_id = %s FOR UPDATE",
                (activity_id, operation_id),
            )
            existing = await cursor.fetchone()
            if operation_id.startswith("teach8t."):
                # G8 工具教学分支：以实际 operation_id 定位唯一 command，
                # 再对原 canonical arguments_sha/name/call_id 核固定 recipe。
                try:
                    command = await self._locked_teaching_binding(connection, activity, operation_id, None, "admit")
                except TeachingRefusal as exc:
                    raise AdmissionDenied(exc.code) from None
                if (command["operation_id"] != operation_id
                        or json.loads(command["context_body"])["kind"] != "tool"):
                    raise AdmissionDenied("unknown_slot")
                frozen_call = json.loads(command["context_body"]).get("call") or {}
                if (frozen_call.get("arguments_sha256") != wire["arguments_sha256"]
                        or frozen_call.get("name") != call.name
                        or frozen_call.get("call_id") != call.call_id):
                    raise AdmissionDenied("tool_input_conflict")
            if existing is not None:
                if existing["kind"] != "tool":
                    raise AdmissionDenied("operation_key_conflict")
                same = (
                    list(existing["tool_names"]) == [call.name]
                    and existing["tool_call_id"] == call.call_id
                    and existing["arguments_sha256"] == wire["arguments_sha256"]
                )
                raise AdmissionDenied("operation_already_exists" if same else "tool_input_conflict")
            admission_id = str(uuid4())
            await connection.execute(
                """UPDATE activities
                      SET tools_reserved = tools_reserved + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s""",
                (activity_id,),
            )
            await connection.execute(
                """INSERT INTO activity_operations(
                       activity_id, operation_id, admission_id, executor_id,
                       execution_generation, scope_revision, kind, tool_names,
                       reserved_cost_microunits, arguments_sha256, tool_call_id)
                     VALUES (%s, %s, %s, %s, %s, %s, 'tool', %s, 0, %s, %s)""",
                (
                    activity_id, operation_id, admission_id, executor_id,
                    context.execution_generation, context.scope_revision,
                    [call.name], wire["arguments_sha256"], call.call_id,
                ),
            )
            return ToolAdmissionPermit(
                admission_id, operation_id, executor_id, activity_id,
                context.execution_generation, context.scope_revision,
                call.name, call.call_id, wire["arguments_sha256"],
            )

        return await self._transaction(operation)

    async def mark_tool_started(self, permit: ToolAdmissionPermit, call: ToolExecutionInput) -> None:
        """把工具操作从 reserved 推进为 dispatched；提交确认后允许唯一执行。

        同一凭证第二次 mark 即拒绝，不返回 ALREADY_STARTED 给再次执行；
        凭证、参数身份与锁内 DB 行完整对齐（不信客户端自称 kind）。
        """
        fields = self._tool_permit_fields(permit)
        try:
            wire = call.to_wire()
        except (ValueError, TypeError, AttributeError):
            raise AdmissionDenied("invalid_input") from None
        (admission_id, operation_id, executor_id, activity_id, _, _, tool_name, tool_call_id, digest) = fields
        if (
            call.operation_id != operation_id or call.name != tool_name
            or call.call_id != tool_call_id or wire["arguments_sha256"] != digest
        ):
            raise AdmissionDenied("admission_permit_mismatch")

        async def operation(connection: object) -> None:
            cursor = await connection.execute(
                "SELECT activity_id FROM activity_operations WHERE admission_id = %s",
                (admission_id,),
            )
            locator = await cursor.fetchone()
            if locator is None:
                raise AdmissionDenied("admission_permit_unknown")
            if str(locator["activity_id"]) != activity_id:
                raise AdmissionDenied("admission_permit_mismatch")
            memory_state=await self._memory_lock_prefix(connection,activity_id)
            snapshots=memory_state['snapshots']
            sources_valid=memory_state['sources_valid']
            activity=memory_state['activity']
            cursor = await connection.execute(
                "SELECT * FROM activity_operations WHERE admission_id = %s FOR UPDATE",
                (admission_id,),
            )
            row = await cursor.fetchone()
            if activity is None or row is None or not self._tool_identity_matches(row, fields):
                raise AdmissionDenied("admission_permit_mismatch")
            if row["state"] != "reserved":
                raise AdmissionDenied("start_qualification_consumed")
            if operation_id.startswith("teach8t."):
                try:
                    await self._locked_teaching_binding(connection,activity,operation_id,None,"mark")
                except TeachingRefusal as exc:
                    raise AdmissionDenied(exc.code) from None
            if activity["dispatch_closed"] or not self._operation_is_current(activity, row, sources_valid):
                raise AdmissionDenied("qualification_invalid")
            await connection.execute(
                """UPDATE activity_operations
                      SET state = 'dispatched', dispatch_started_at = CURRENT_TIMESTAMP
                    WHERE admission_id = %s AND state = 'reserved'""",
                (admission_id,),
            )

        await self._transaction(operation)

    async def record_tool_outcome(
        self, permit: ToolAdmissionPermit, call: ToolExecutionInput, outcome: LedgerOutcome,
    ) -> RecordOutcome:
        """工具终态与（成功）正文的原子提交；与模型共用受控核心但不共用凭证。

        工具行不携带任何模型元数据，也不接受 not_sent；成功正文额外复查
        text 封套内的原精度 50 规范有限十进制字符串。终态严格等值幂等、
        正文三字段同存同缺、关门拒绝正文新写等纪律与模型路径一致。
        """
        fields = self._tool_permit_fields(permit)
        try:
            wire = call.to_wire()
        except (ValueError, TypeError, AttributeError):
            raise AdmissionDenied("invalid_input") from None
        (admission_id, operation_id, executor_id, activity_id, _, _, tool_name, tool_call_id, digest) = fields
        if (
            call.operation_id != operation_id or call.name != tool_name
            or call.call_id != tool_call_id or wire["arguments_sha256"] != digest
        ):
            raise AdmissionDenied("admission_permit_mismatch")
        values = self._outcome_values(outcome)
        if outcome.disposition is LedgerDisposition.NOT_SENT:
            raise AdmissionDenied("工具结果不接受 not_sent 终态")
        if any(value is not None for value in values[2:]):
            raise AdmissionDenied("工具行不携带模型元数据")
        payload_triple = self._payload_values(outcome)
        if payload_triple is not None and not _tool_payload_semantics_ok(payload_triple[0], payload_triple[1]):
            raise AdmissionDenied("invalid_tool_payload")

        async def operation(connection: object) -> RecordOutcome:
            cursor = await connection.execute(
                "SELECT activity_id FROM activity_operations WHERE admission_id = %s",
                (admission_id,),
            )
            locator = await cursor.fetchone()
            if locator is None:
                raise AdmissionDenied("admission_permit_unknown")
            if str(locator["activity_id"]) != activity_id:
                raise AdmissionDenied("admission_permit_mismatch")
            memory_state=await self._memory_lock_prefix(connection,activity_id)
            snapshots=memory_state['snapshots']
            sources_valid=memory_state['sources_valid']
            activity=memory_state['activity']
            cursor = await connection.execute(
                "SELECT * FROM activity_operations WHERE admission_id = %s FOR UPDATE",
                (admission_id,),
            )
            row = await cursor.fetchone()
            if activity is None or row is None or not self._tool_identity_matches(row, fields):
                raise AdmissionDenied("admission_permit_mismatch")
            confirmed = await self._terminal_confirmation(connection, row, values, payload_triple)
            if confirmed is not None:
                if row["operation_id"].startswith("teach8t."):
                    await self._teaching_confirm_integrity(connection,row,payload_triple)
                return confirmed
            current = self._operation_is_current(activity, row, sources_valid)
            if not current and outcome.disposition is not LedgerDisposition.UNKNOWN:
                raise AdmissionDenied("失效或过期执行只能登记 unknown 诊断")
            if row["state"] == "reserved" and outcome.disposition is not LedgerDisposition.UNKNOWN:
                raise AdmissionDenied("尚未越过发送边界的调用不能登记该结果")
            if payload_triple is not None and activity["dispatch_closed"]:
                raise AdmissionDenied("关闭门后不接受正文新写")
            await self._write_outcome(connection, row, values, payload_triple)
            if operation_id.startswith(("teach8m.", "teach8t.")):
                await self._write_teaching_outcome(connection, activity, row, outcome, payload_triple)
            return RecordOutcome.RECORDED

        return await self._transaction(operation)

    async def _locked_operation(
        self, connection: object, permit: AdmissionPermit, *, kind: str = "model",
    ) -> tuple[dict, dict, bool]:
        try:
            admission_id = self._uuid(permit.admission_id, "admission_id")
            operation_id = self._bounded_name(permit.operation_id, "operation_id")
            executor_id = self._bounded_name(permit.executor_id, "executor_id")
        except ValueError as exc:
            raise AdmissionDenied(str(exc)) from None
        cursor = await connection.execute(
            "SELECT activity_id FROM activity_operations WHERE admission_id = %s",
            (admission_id,),
        )
        locator = await cursor.fetchone()
        if locator is None:
            raise AdmissionDenied("准入凭证不存在")
        activity_id = str(locator["activity_id"])
        memory_state=await self._memory_lock_prefix(connection,activity_id)
        snapshots=memory_state['snapshots']
        sources_valid=memory_state['sources_valid']
        activity=memory_state['activity']
        if operation_id.startswith(('teach8m.','teach8t.','int10m.','html11m.')):
            await self._teaching_lock_operations(connection,activity_id)
        cursor = await connection.execute(
            "SELECT * FROM activity_operations WHERE admission_id = %s FOR UPDATE",
            (admission_id,),
        )
        operation = await cursor.fetchone()
        if (
            activity is None
            or operation is None
            or operation["operation_id"] != operation_id
            or operation["executor_id"] != executor_id
            or operation["kind"] != kind
        ):
            raise AdmissionDenied("准入凭证与操作或执行者不匹配")
        return activity, operation, sources_valid

    @staticmethod
    def _operation_is_current(activity: dict, operation: dict, sources_valid: bool) -> bool:
        now = datetime.now(timezone.utc)
        return (
            sources_valid
            and activity.get("_memory_eligible", True)
            and activity["status"] == "running"
            and activity["executor_id"] == operation["executor_id"]
            and activity["execution_generation"] == operation["execution_generation"]
            and activity["scope_revision"] == operation["scope_revision"]
            and activity["lease_expires_at"] is not None
            and activity["lease_expires_at"] > now
            and activity["deadline_at"] > now
        )

    async def mark_dispatch_started(self, permit: AdmissionPermit) -> None:
        async def operation(connection: object) -> AdmissionPermit:
            activity, call, sources_valid = await self._locked_operation(connection, permit)
            if call["operation_id"].startswith("html11m."):
                await self._html_locked_binding(connection,activity,call["operation_id"])
            if call["operation_id"].startswith("teach8m."):
                # G8：mark 锁内复核教学命令仍为 started 且未被废弃。
                try:
                    await self._locked_teaching_binding(connection, activity, call["operation_id"], None, "mark")
                except TeachingRefusal as exc:
                    raise AdmissionDenied(exc.code) from None
            if call["operation_id"].startswith("int10m."):
                try: await self._locked_interview_binding(connection,activity,call["operation_id"],None,"mark")
                except InterviewRefusal as exc: raise AdmissionDenied(exc.code) from None
            if (
                call["state"] != "reserved" or activity["dispatch_closed"]
                or not self._operation_is_current(activity, call, sources_valid)
            ):
                raise AdmissionDenied("发送资格已消费或活动已失效")
            await connection.execute(
                """UPDATE activity_operations
                      SET state = 'dispatched', dispatch_started_at = CURRENT_TIMESTAMP
                    WHERE admission_id = %s AND state = 'reserved'""",
                (permit.admission_id,),
            )

        await self._transaction(operation)

    @classmethod
    def _outcome_values(cls, outcome: LedgerOutcome) -> tuple:
        if not isinstance(outcome.disposition, LedgerDisposition):
            raise AdmissionDenied("结果 disposition 非法")
        for field, value, maximum in (
            ("error_code", outcome.error_code, 64),
            ("remote_request_id", outcome.remote_request_id, 128),
            ("returned_model", outcome.returned_model, 128),
            ("finish_reason", outcome.finish_reason, 64),
        ):
            if value is not None:
                try:
                    cls._bounded_name(value, field, maximum=maximum)
                except ValueError as exc:
                    raise AdmissionDenied(str(exc)) from None
        for field, value, maximum in (
            ("prompt_tokens", outcome.prompt_tokens, _MAX_USAGE),
            ("completion_tokens", outcome.completion_tokens, _MAX_USAGE),
            ("response_bytes", outcome.response_bytes, _MAX_RESPONSE_BYTES),
        ):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum
            ):
                raise AdmissionDenied(f"{field} 非法")
        return (
            outcome.disposition.value,
            outcome.error_code,
            outcome.remote_request_id,
            outcome.returned_model,
            outcome.finish_reason,
            outcome.prompt_tokens,
            outcome.completion_tokens,
            outcome.response_bytes,
        )

    @staticmethod
    def _payload_values(outcome: LedgerOutcome) -> tuple[str, str, str] | None:
        """正文三字段同存同缺；合法时返回 (format, payload, sha256) 规范三元组。

        对实际 payload 文本复查封套/format/value 类型/有限数/深度节点/编码
        长度/规范形式/SHA-256 匹配（共享 helper），不是 hash 正则直通，也不
        把已有封套再包一层。正文只允许随 received 终态登记。
        """
        fields = (outcome.payload_format, outcome.payload, outcome.payload_sha256)
        if all(value is None for value in fields):
            return None
        if any(value is None for value in fields):
            raise AdmissionDenied("正文三字段必须同存同缺")
        if outcome.disposition is not LedgerDisposition.RECEIVED:
            raise AdmissionDenied("正文只能随 received 终态登记")
        try:
            return validate_business_payload(outcome.payload, outcome.payload_format, outcome.payload_sha256)
        except ValueError as exc:
            raise AdmissionDenied(f"正文封套不合法（{exc}）") from None

    @staticmethod
    def _stored_outcome(call: dict) -> tuple:
        return tuple(
            call[name]
            for name in (
                "disposition",
                "error_code",
                "remote_request_id",
                "returned_model",
                "finish_reason",
                "prompt_tokens",
                "completion_tokens",
                "response_bytes",
            )
        )

    @staticmethod
    async def _stored_payload_row(connection: object, call: dict) -> tuple[str, str, str] | None:
        cursor = await connection.execute(
            """SELECT admission_id, execution_generation, scope_revision,
                      payload_format, payload, payload_sha256
                 FROM activity_operation_results
                WHERE activity_id = %s AND operation_id = %s""",
            (call["activity_id"], call["operation_id"]),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        if any(row[name] != call[name] for name in (
            "admission_id", "execution_generation", "scope_revision"
        )):
            raise AdmissionDenied("历史正文与操作权威绑定不一致")
        return (row["payload_format"], row["payload"], row["payload_sha256"])

    @staticmethod
    async def _terminal_confirmation(
        connection: object, call: dict, values: tuple, payload_triple: tuple[str, str, str] | None,
    ) -> RecordOutcome | None:
        """已终结行的严格等值无写幂等确认；语义冲突抛拒绝，未终结返回 None。

        带正文与无正文不等价，旧 received 无正文不能补写，异文冲突保留已有；
        该确认先于任何当前资格/关门检查。
        """
        if call["state"] not in {"not_sent", "received", "unknown"}:
            return None
        if PostgresAdmissionLedger._stored_outcome(call) == values:
            stored_payload = await PostgresAdmissionLedger._stored_payload_row(connection, call)
            if payload_triple is None and stored_payload is None:
                return RecordOutcome.ALREADY_PRESENT
            if payload_triple is not None and stored_payload is not None and stored_payload == payload_triple:
                return RecordOutcome.ALREADY_PRESENT
            if stored_payload is None:
                raise AdmissionDenied("已终结无正文状态不能补写正文")
            raise AdmissionDenied("已终结正文与提交不一致")
        raise AdmissionDenied("已终结调用不能覆盖为不同结果")

    @staticmethod
    async def _write_outcome(
        connection: object, call: dict, values: tuple, payload_triple: tuple[str, str, str] | None,
    ) -> None:
        """写入终态与（可缺省的）正文，同一事务；身份冗余值取锁内权威操作行。"""
        await connection.execute(
            """UPDATE activity_operations
                  SET state = %s, disposition = %s, error_code = %s,
                      remote_request_id = %s, returned_model = %s, finish_reason = %s,
                      prompt_tokens = %s, completion_tokens = %s, response_bytes = %s,
                      recorded_at = CURRENT_TIMESTAMP
                WHERE admission_id = %s""",
            (values[0], *values, call["admission_id"]),
        )
        if payload_triple is not None:
            await connection.execute(
                """INSERT INTO activity_operation_results(
                       activity_id, operation_id, admission_id, execution_generation,
                       scope_revision, payload_format, payload, payload_sha256)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    call["activity_id"],
                    call["operation_id"],
                    call["admission_id"],
                    call["execution_generation"],
                    call["scope_revision"],
                    payload_triple[0],
                    payload_triple[1],
                    payload_triple[2],
                ),
            )

    async def record_outcome(self, permit: AdmissionPermit, outcome: LedgerOutcome) -> RecordOutcome:
        """原子登记终态与（可缺省的）业务正文；返回持久提交确认枚举。

        正文新写与 received 终态在同一短事务内（来源→活动→操作锁序），
        COMMIT 确认后才返回 RECORDED；COMMIT 后响应丢失按持久事实重读。
        分支序：终态严格等值的无写幂等（含正文存在性与 format/规范内容/hash，
        带正文与无正文不等价，旧 received 无正文不能补写，异文冲突保留已有）
        先于失效/未发送新写资格拒绝；正文新写额外显式检查 dispatch_closed
        （_operation_is_current 本身不含关门）。诊断/UNKNOWN 记录合同不变，
        不扩展为正文授权。凭证仅接受 kind=model 行。
        """
        values = self._outcome_values(outcome)
        payload_triple = self._payload_values(outcome)

        async def operation(connection: object) -> RecordOutcome:
            activity, call, sources_valid = await self._locked_operation(connection, permit)
            confirmed = await self._terminal_confirmation(connection, call, values, payload_triple)
            if confirmed is not None:
                if call["operation_id"].startswith("html11m."):
                    await self._html_confirm_integrity(connection,call,payload_triple)
                if call["operation_id"].startswith("teach8m."):
                    await self._teaching_confirm_integrity(connection,call,payload_triple)
                if call["operation_id"].startswith("int10m."):
                    await self._interview_confirm_integrity(connection,call,payload_triple)
                return confirmed
            current = self._operation_is_current(activity, call, sources_valid)
            if not current and outcome.disposition is not LedgerDisposition.UNKNOWN:
                raise AdmissionDenied("失效或过期执行只能登记 unknown 诊断")
            if call["state"] == "reserved" and outcome.disposition is not LedgerDisposition.UNKNOWN:
                raise AdmissionDenied("尚未越过发送边界的调用不能登记该结果")
            if payload_triple is not None and activity["dispatch_closed"]:
                raise AdmissionDenied("关闭门后不接受正文新写")
            await self._write_outcome(connection, call, values, payload_triple)
            if call["operation_id"].startswith(("teach8m.", "teach8t.")):
                # G8：教学事实/进度/暴露与终态正文同一 COMMIT；失败整笔回滚。
                await self._write_teaching_outcome(connection, activity, call, outcome, payload_triple)
            if call["operation_id"].startswith("int10m."):
                await self._write_interview_outcome(connection,activity,call,outcome,payload_triple)
            if call["operation_id"].startswith("html11m."):
                await self._write_html_outcome(connection,activity,call,outcome,payload_triple)
            return RecordOutcome.RECORDED

        return await self._transaction(operation)

    # --- G3 只读恢复接口：资格判定与正文投影在单语句内完成；失效不投影正文。

    _RESULT_READ_SQL = """\
SELECT o.state, o.disposition, o.operation_id,
       o.admission_id AS op_admission_id, o.execution_generation AS op_generation,
       o.scope_revision AS op_scope, o.provider, o.configured_model,
       o.finish_reason, o.returned_model, o.remote_request_id,
       o.prompt_tokens, o.completion_tokens, o.response_bytes,
       o.kind, o.tool_call_id, o.arguments_sha256, o.tool_names,
       r.admission_id AS result_admission_id, r.execution_generation AS result_generation,
       r.scope_revision AS result_scope, r.payload_format, r.payload_sha256, r.committed_at,
       a.status AS activity_status_now, a.scope_revision AS activity_scope_revision_now,
       (r.payload_sha256 IS NOT NULL
        AND r.admission_id = o.admission_id
        AND r.execution_generation = o.execution_generation
        AND r.scope_revision = o.scope_revision) AS binding_consistent,
       (r.payload_sha256 IS NOT NULL AND a.scope_revision = r.scope_revision) AS scope_current,
       (EXISTS (SELECT 1 FROM activity_scope_sources s WHERE s.activity_id = o.activity_id)
        AND NOT EXISTS (
            SELECT 1 FROM activity_scope_sources s
              LEFT JOIN material_sources m ON m.id = s.source_id
             WHERE s.activity_id = o.activity_id
               AND (m.id IS NULL OR m.current_version IS NULL
                    OR m.current_version <> s.version_id
                    OR m.revision <> s.source_revision)
        )) AS sources_valid, /*memory*/TRUE AS memory_qualified, /*interview*/TRUE AS interview_qualified"""

    @staticmethod
    def _read_status(row: dict, *, has_result: bool) -> ResultReadStatus:
        """行内绑定不一致抛完整性错误；scope 检查先于来源检查。"""
        if row["payload_sha256"] is not None and not row["binding_consistent"]:
            raise ResultIntegrityError("结果行与操作权威绑定不一致")
        if not has_result:
            return ResultReadStatus.UNRESOLVED
        if not row["scope_current"]:
            return ResultReadStatus.INVALIDATED_SCOPE_CHANGED
        if not row["sources_valid"]:
            return ResultReadStatus.INVALIDATED_SOURCE
        if not row.get("memory_qualified", True):
            return ResultReadStatus.INVALIDATED_MEMORY
        if not row.get("interview_qualified",True):
            return ResultReadStatus.INVALIDATED_INTERVIEW
        if row["activity_status_now"] == "cancelled":
            return ResultReadStatus.COMMITTED_HISTORY_CANCELLED
        return ResultReadStatus.COMMITTED_CURRENT

    @staticmethod
    def _snapshot_from_row(row: dict, status: ResultReadStatus, payload: str | None) -> CommittedResultSnapshot:
        has_result = row["payload_sha256"] is not None
        return CommittedResultSnapshot(
            activity_id=str(row["activity_id"]),
            operation_id=row["operation_id"],
            read_status=status,
            admission_id=str(row["result_admission_id"] if has_result else row["op_admission_id"]),
            execution_generation=row["result_generation"] if has_result else row["op_generation"],
            scope_revision=row["result_scope"] if has_result else row["op_scope"],
            provider=row["provider"],
            configured_model=row["configured_model"],
            finish_reason=row["finish_reason"],
            returned_model=row["returned_model"],
            remote_request_id=row["remote_request_id"],
            prompt_tokens=row["prompt_tokens"],
            completion_tokens=row["completion_tokens"],
            response_bytes=row["response_bytes"],
            payload_format=row["payload_format"],
            payload=payload,
            payload_sha256=row["payload_sha256"],
            committed_at=row["committed_at"],
            activity_status_now=row["activity_status_now"],
            activity_scope_revision_now=row["activity_scope_revision_now"],
            kind=row["kind"],
            tool_call_id=row["tool_call_id"],
            arguments_sha256=row["arguments_sha256"],
            tool_names=tuple(row["tool_names"]) if row["tool_names"] is not None else None,
        )

    async def read_committed_result(self, activity_id: str, operation_id: str) -> CommittedResultSnapshot:
        """内部只读恢复接口（无 HTTP）；失败关闭，失效分支不投影正文。

        有效正文需要：结果行与操作/活动/admission/G/scope 完整绑定；结果
        scope 与活动当前 scope 一致；来源快照非空且每项来源存在、版本与
        revision 一致。有效返回前重算存储字节 hash 并复查合法封套；不以
        hash 正确替代来源授权。取消后的历史成果仅来源/scope 有效才可读，
        不授予新写/发送资格；快照之后的变化不声称可撤回已返回字节。
        """
        activity_id = self._uuid(activity_id, "activity_id")
        operation_id = self._bounded_name(operation_id, "operation_id")

        async def operation(connection: object) -> CommittedResultSnapshot:
            cursor = await connection.execute(
                await self._interview_result_sql(connection,await self._memory_result_sql(connection,f"""{self._RESULT_READ_SQL},
       CASE WHEN r.payload_sha256 IS NOT NULL
             AND r.admission_id = o.admission_id
             AND r.execution_generation = o.execution_generation
             AND r.scope_revision = o.scope_revision
             AND a.scope_revision = r.scope_revision
             AND EXISTS (SELECT 1 FROM activity_scope_sources s WHERE s.activity_id = o.activity_id)
             AND NOT EXISTS (
                 SELECT 1 FROM activity_scope_sources s
                   LEFT JOIN material_sources m ON m.id = s.source_id
                  WHERE s.activity_id = o.activity_id
                    AND (m.id IS NULL OR m.current_version IS NULL
                         OR m.current_version <> s.version_id
                         OR m.revision <> s.source_revision))
            AND /*interview*/TRUE THEN r.payload ELSE NULL END AS payload,
       o.activity_id
  FROM activity_operations o
  JOIN activities a ON a.id = o.activity_id
  LEFT JOIN activity_operation_results r
         ON r.activity_id = o.activity_id AND r.operation_id = o.operation_id
 WHERE o.activity_id = %s AND o.operation_id = %s""")),
                (activity_id, operation_id),
            )
            row = await cursor.fetchone()
            if row is None:
                # 无操作行：仅已知请求 ID，不伪造 admission/G/provider；
                # 缺失活动同样明确返回未找到。
                return CommittedResultSnapshot(
                    activity_id=activity_id,
                    operation_id=operation_id,
                    read_status=ResultReadStatus.NO_OPERATION,
                )
            if row["payload_sha256"] is None:
                status = (
                    ResultReadStatus.UNRESOLVED
                    if row["state"] in ("reserved", "dispatched", "unknown")
                    else ResultReadStatus.TERMINAL_WITHOUT_PAYLOAD
                )
                return self._snapshot_from_row(row, status, None)
            status = self._read_status(row, has_result=True)
            payload: str | None = None
            if status in (ResultReadStatus.COMMITTED_CURRENT, ResultReadStatus.COMMITTED_HISTORY_CANCELLED):
                payload = row["payload"]
                if payload is None:
                    raise ResultIntegrityError("payload_integrity")
                try:
                    validate_business_payload(payload, row["payload_format"], row["payload_sha256"])
                except ValueError:
                    raise ResultIntegrityError("payload_integrity") from None
                if row["kind"] == "tool" and not _tool_payload_semantics_ok(row["payload_format"], payload):
                    # 工具结果语义复查；同表 model json 许可不自动给 tool。
                    raise ResultIntegrityError("payload_integrity")
            return self._snapshot_from_row(row, status, payload)

        return await self._transaction(operation)

    async def list_committed_results(
        self,
        activity_id: str,
        *,
        limit: int = 100,
        after_operation_id: str | None = None,
    ) -> tuple[CommittedResultSnapshot, ...]:
        """只列真正 results 行（含失效记录的轻量元数据，不含正文）。

        operation_id 稳定游标有界分页，limit 1..200；整页轻量元数据编码
        超过 256KiB 明确拒绝，不静默丢项；不把无正文操作混成已提交列表。
        """
        activity_id = self._uuid(activity_id, "activity_id")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
            raise ValueError("limit 必须是 1 到 200 之间的整数")
        if after_operation_id is not None:
            after_operation_id = self._bounded_name(after_operation_id, "after_operation_id")
        conditions = "r.activity_id = %s"
        params: list[object] = [activity_id]
        if after_operation_id is not None:
            conditions += " AND r.operation_id > %s"
            params.append(after_operation_id)
        params.append(limit)

        async def operation(connection: object) -> tuple[CommittedResultSnapshot, ...]:
            cursor = await connection.execute(
                await self._interview_result_sql(connection,await self._memory_result_sql(connection,f"""{self._RESULT_READ_SQL},
       CASE WHEN r.payload_sha256 IS NOT NULL
             AND r.admission_id = o.admission_id
             AND r.execution_generation = o.execution_generation
             AND r.scope_revision = o.scope_revision
             AND a.scope_revision = r.scope_revision
             AND EXISTS (SELECT 1 FROM activity_scope_sources s WHERE s.activity_id = o.activity_id)
             AND NOT EXISTS (
                 SELECT 1 FROM activity_scope_sources s
                   LEFT JOIN material_sources m ON m.id = s.source_id
                  WHERE s.activity_id = o.activity_id
                    AND (m.id IS NULL OR m.current_version IS NULL
                         OR m.current_version <> s.version_id
                         OR m.revision <> s.source_revision))
            AND /*interview*/TRUE THEN r.payload ELSE NULL END AS payload,
       o.activity_id
  FROM activity_operation_results r
  JOIN activity_operations o
    ON o.activity_id = r.activity_id AND o.operation_id = r.operation_id
  JOIN activities a ON a.id = r.activity_id
 WHERE {conditions}
 ORDER BY r.operation_id
 LIMIT %s""")),
                tuple(params),
            )
            rows = list(await cursor.fetchall())
            snapshots = []
            for row in rows:
                if row["kind"] == "tool" and row["payload"] is not None:
                    # 与 read 一致：SQL 资格成立且 kind=tool 时复查工具结果语义。
                    try:
                        validate_business_payload(row["payload"], row["payload_format"], row["payload_sha256"])
                    except ValueError:
                        raise ResultIntegrityError("payload_integrity") from None
                    if not _tool_payload_semantics_ok(row["payload_format"], row["payload"]):
                        raise ResultIntegrityError("payload_integrity")
                snapshots.append(self._snapshot_from_row(row, self._read_status(row, has_result=True), None))
            snapshots = tuple(snapshots)
            encoded = json.dumps(
                [
                    {
                        "activity_id": item.activity_id,
                        "operation_id": item.operation_id,
                        "read_status": item.read_status.value,
                        "admission_id": item.admission_id,
                        "execution_generation": item.execution_generation,
                        "scope_revision": item.scope_revision,
                        "provider": item.provider,
                        "configured_model": item.configured_model,
                        "finish_reason": item.finish_reason,
                        "returned_model": item.returned_model,
                        "remote_request_id": item.remote_request_id,
                        "prompt_tokens": item.prompt_tokens,
                        "completion_tokens": item.completion_tokens,
                        "response_bytes": item.response_bytes,
                        "payload_format": item.payload_format,
                        "payload_sha256": item.payload_sha256,
                        "committed_at": item.committed_at.isoformat() if item.committed_at else None,
                        "activity_status_now": item.activity_status_now,
                        "activity_scope_revision_now": item.activity_scope_revision_now,
                        "kind": item.kind,
                        "tool_call_id": item.tool_call_id,
                        "arguments_sha256": item.arguments_sha256,
                        "tool_names": list(item.tool_names) if item.tool_names is not None else None,
                    }
                    for item in snapshots
                ],
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            if len(encoded) > 262_144:
                raise ValueError("结果页编码超过 256KiB")
            return snapshots

        return await self._transaction(operation)

    # --- G6 活动工作区只读方法（TASK-095）。仅新增读取；不改 _transaction、
    # 状态判定规则与既有写方法。每请求恰一条 SQL，行内绑定判定在同一语句。 ---

    _ACTIVITY_FACT_SQL = """\
SELECT a.id, a.status, a.created_at, a.updated_at, a.deadline_at, a.cancelled_at,
       a.scope_revision, a.max_requests, a.requests_reserved,
       a.max_cost_microunits, a.cost_reserved_microunits, a.reserve_cost_microunits,
       a.max_running_seconds, a.running_reserved_seconds, a.running_settled_seconds,
       a.last_settled_generation, a.last_settled_seconds,
       a.max_tool_calls, a.tools_reserved,
       COALESCE((SELECT jsonb_agg(jsonb_build_array(am.provider, am.model)
                                  ORDER BY am.provider, am.model)
                   FROM activity_allowed_models am
                  WHERE am.activity_id = a.id),
                '[]'::jsonb) AS allowed_models,
       COALESCE((SELECT jsonb_agg(jsonb_build_object(
                        'source_id', s.source_id::text,
                        'title', COALESCE(sm.title, '（来源已移除）'),
                        'valid', (sm.id IS NOT NULL
                                  AND sm.current_version IS NOT NULL
                                  AND sm.current_version = s.version_id
                                  AND sm.revision = s.source_revision))
                    ORDER BY s.source_id)
                   FROM activity_scope_sources s
                   LEFT JOIN material_sources sm ON sm.id = s.source_id
                  WHERE s.activity_id = a.id),
                '[]'::jsonb) AS sources, /*memory_meta*/NULL::jsonb AS memory_selection
  FROM activities a"""

    @staticmethod
    def _activity_fact_from_row(row: dict) -> ActivityFactView:
        return ActivityFactView(
            activity_id=str(row["id"]),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deadline_at=row["deadline_at"],
            cancelled_at=row["cancelled_at"],
            scope_revision=row["scope_revision"],
            max_requests=row["max_requests"],
            requests_reserved=row["requests_reserved"],
            max_cost_microunits=row["max_cost_microunits"],
            cost_reserved_microunits=row["cost_reserved_microunits"],
            reserve_cost_microunits=row["reserve_cost_microunits"],
            max_running_seconds=row["max_running_seconds"],
            running_reserved_seconds=row["running_reserved_seconds"],
            running_settled_seconds=row["running_settled_seconds"],
            last_settled_generation=row["last_settled_generation"],
            last_settled_seconds=row["last_settled_seconds"],
            max_tool_calls=row["max_tool_calls"],
            tools_reserved=row["tools_reserved"],
            allowed_models=tuple((str(p), str(m)) for p, m in row["allowed_models"]),
            memory_selection=row.get("memory_selection"),
            business_domain=row.get("business_domain"),
            sources=tuple(
                ActivitySourceView(str(x["source_id"]), str(x["title"]), bool(x["valid"]))
                for x in row["sources"]
            ),
        )

    async def probe_storage(self) -> bool:
        """活动存储就绪探测；单条只读语句，缺表返回 False 而非异常。"""

        async def operation(connection: object) -> bool:
            cursor = await connection.execute(
                "SELECT to_regclass('activities') IS NOT NULL"
                " AND to_regclass('activity_operations') IS NOT NULL"
                " AND to_regclass('activity_operation_results') IS NOT NULL AS ready"
            )
            row = await cursor.fetchone()
            return bool(row["ready"])

        return await self._transaction(operation)

    async def list_activities(
        self,
        *,
        limit: int,
        after_created_at: datetime | None = None,
        after_activity_id: str | None = None,
    ) -> tuple[ActivityFactView, ...]:
        """活动列表单条 SQL 快照；(created_at,id) 双键倒序游标，行内自洽。"""
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
            raise ValueError("limit 必须是 1 到 200 之间的整数")
        if (after_created_at is None) != (after_activity_id is None):
            raise ValueError("游标必须同时给出时间与活动编号")
        if after_activity_id is not None:
            after_activity_id = self._uuid(after_activity_id, "after_activity_id")
            if not isinstance(after_created_at, datetime) or after_created_at.tzinfo is None:
                raise ValueError("游标时间必须带时区")

        async def operation(connection: object) -> tuple[ActivityFactView, ...]:
            cursor = await connection.execute(
                await self._memory_result_sql(connection,f"""{self._ACTIVITY_FACT_SQL}
 WHERE %s::timestamptz IS NULL
    OR (a.created_at, a.id) < (%s::timestamptz, %s::uuid)
 ORDER BY a.created_at DESC, a.id DESC
 LIMIT %s"""),
                (after_created_at, after_created_at, after_activity_id, limit),
            )
            return tuple(self._activity_fact_from_row(row) for row in await cursor.fetchall())

        return await self._transaction(operation)

    async def read_activity_facts(self, activity_id: str) -> ActivityFactView | None:
        """活动详情单条 SQL 快照；不存在返回 None。"""
        activity_id = self._uuid(activity_id, "activity_id")

        async def operation(connection: object) -> ActivityFactView | None:
            cursor = await connection.execute(
                await self._memory_result_sql(connection,f"{self._ACTIVITY_FACT_SQL} WHERE a.id = %s"), (activity_id,),
            )
            row = await cursor.fetchone()
            if row is not None:
                domain=await self._interview_domain(connection,activity_id)
                row=dict(row,business_domain=None if domain=="existing" else domain)
            return None if row is None else self._activity_fact_from_row(row)

        return await self._transaction(operation)

    async def read_scope_source_versions(self, source_ids: list[str]) -> dict[str, dict]:
        """按来源编号读取当前版本与修订；只读，用于新建活动前的范围构建。"""
        if type(source_ids) is not list or not 1 <= len(source_ids) <= 128:
            raise ValueError("来源编号必须为非空列表")
        normalized = [self._uuid(item, "source_id") for item in source_ids]
        if len(set(normalized)) != len(normalized):
            raise ValueError("来源编号必须唯一")

        async def operation(connection: object) -> dict[str, dict]:
            cursor = await connection.execute(
                "SELECT id, current_version, revision FROM material_sources WHERE id = ANY(%s)",
                (normalized,),
            )
            return {str(row["id"]): dict(row) for row in await cursor.fetchall()}

        return await self._transaction(operation)

    _OPERATIONS_SELECT = _RESULT_READ_SQL + """,
       o.error_code, o.reserved_at, o.dispatch_started_at, o.recorded_at,
       CASE WHEN r.payload_sha256 IS NOT NULL
             AND r.admission_id = o.admission_id
             AND r.execution_generation = o.execution_generation
             AND r.scope_revision = o.scope_revision
             AND a.scope_revision = r.scope_revision
             AND EXISTS (SELECT 1 FROM activity_scope_sources s WHERE s.activity_id = o.activity_id)
             AND NOT EXISTS (
                 SELECT 1 FROM activity_scope_sources s
                   LEFT JOIN material_sources m ON m.id = s.source_id
                  WHERE s.activity_id = o.activity_id
                    AND (m.id IS NULL OR m.current_version IS NULL
                         OR m.current_version <> s.version_id
                         OR m.revision <> s.source_revision))
            AND /*interview*/TRUE THEN r.payload ELSE NULL END AS payload
  FROM activity_operations o
  JOIN activities a ON a.id = o.activity_id
  LEFT JOIN activity_operation_results r
         ON r.activity_id = o.activity_id AND r.operation_id = o.operation_id"""

    # 续作01（O1 裁定）：操作列表专用投影。数据库不返回正文列；
    # payload_eligible 是同一语句内判定的"正文候选资格"（绑定一致且
    # scope/来源当前），不承诺正文已通过内容完整性校验——列表候选的
    # 最终有效性由单条正文读决定；正文损坏只影响单条读取，不再使整页
    # 元数据列表失败。绑定损坏（binding_consistent=False）仍失败关闭。
    _OPERATIONS_LIST_SELECT = _RESULT_READ_SQL + """,
       o.error_code, o.reserved_at, o.dispatch_started_at, o.recorded_at,
       (r.payload_sha256 IS NOT NULL
        AND r.admission_id = o.admission_id
        AND r.execution_generation = o.execution_generation
        AND r.scope_revision = o.scope_revision
        AND a.scope_revision = r.scope_revision
        AND EXISTS (SELECT 1 FROM activity_scope_sources s WHERE s.activity_id = o.activity_id)
        AND NOT EXISTS (
            SELECT 1 FROM activity_scope_sources s
              LEFT JOIN material_sources m ON m.id = s.source_id
             WHERE s.activity_id = o.activity_id
               AND (m.id IS NULL OR m.current_version IS NULL
                    OR m.current_version <> s.version_id
                    OR m.revision <> s.source_revision)) AND /*memory*/TRUE AND /*interview*/TRUE) AS payload_eligible
  FROM activity_operations o
  JOIN activities a ON a.id = o.activity_id
  LEFT JOIN activity_operation_results r
         ON r.activity_id = o.activity_id AND r.operation_id = o.operation_id"""

    def _operation_row_from_row(self, row: dict) -> OperationRow:
        has_result = row["payload_sha256"] is not None
        if not has_result:
            status = (
                ResultReadStatus.UNRESOLVED
                if row["state"] in ("reserved", "dispatched", "unknown")
                else ResultReadStatus.TERMINAL_WITHOUT_PAYLOAD
            )
        else:
            status = self._read_status(row, has_result=True)
        payload = row["payload"]
        if payload is not None:
            try:
                validate_business_payload(payload, row["payload_format"], row["payload_sha256"])
            except (ValueError, TypeError):
                raise ResultIntegrityError("payload_integrity") from None
            if row["kind"] == "tool" and not _tool_payload_semantics_ok(row["payload_format"], payload):
                raise ResultIntegrityError("payload_integrity")
        available = payload is not None and status in (
            ResultReadStatus.COMMITTED_CURRENT,
            ResultReadStatus.COMMITTED_HISTORY_CANCELLED,
        )
        return OperationRow(
            operation_id=row["operation_id"],
            kind=row["kind"],
            state=row["state"],
            disposition=row["disposition"],
            error_code=row["error_code"],
            reserved_at=row["reserved_at"],
            dispatch_started_at=row["dispatch_started_at"],
            recorded_at=row["recorded_at"],
            prompt_tokens=row["prompt_tokens"],
            completion_tokens=row["completion_tokens"],
            finish_reason=row["finish_reason"],
            returned_model=row["returned_model"],
            committed_at=row["committed_at"],
            read_status=status,
            payload_available=available,
            payload=payload,
        )

    def _operation_list_row_from_row(self, row: dict) -> OperationRow:
        """列表行转换：数据库行无正文列；状态与绑定判定仍行内完成。

        payload_available 取 SQL 候选资格投影，并与状态推导双向复核——
        两者不一致按完整性错误失败关闭，不静默采用任一侧。
        """
        has_result = row["payload_sha256"] is not None
        if not has_result:
            status = (
                ResultReadStatus.UNRESOLVED
                if row["state"] in ("reserved", "dispatched", "unknown")
                else ResultReadStatus.TERMINAL_WITHOUT_PAYLOAD
            )
        else:
            status = self._read_status(row, has_result=True)
        eligible = bool(row["payload_eligible"])
        expected = status in (
            ResultReadStatus.COMMITTED_CURRENT,
            ResultReadStatus.COMMITTED_HISTORY_CANCELLED,
        )
        if eligible != expected:
            raise ResultIntegrityError("payload_integrity")
        return OperationRow(
            operation_id=row["operation_id"],
            kind=row["kind"],
            state=row["state"],
            disposition=row["disposition"],
            error_code=row["error_code"],
            reserved_at=row["reserved_at"],
            dispatch_started_at=row["dispatch_started_at"],
            recorded_at=row["recorded_at"],
            prompt_tokens=row["prompt_tokens"],
            completion_tokens=row["completion_tokens"],
            finish_reason=row["finish_reason"],
            returned_model=row["returned_model"],
            committed_at=row["committed_at"],
            read_status=status,
            payload_available=eligible,
            payload=None,
        )

    async def list_operations(
        self,
        activity_id: str,
        *,
        limit: int,
        after_operation_id: str | None = None,
    ) -> tuple[OperationRow, ...]:
        """活动操作列表单条 SQL 快照；含无结果操作行；数据库不返回正文列。

        payload_available 为行内候选资格投影（绑定/scope/来源单语句判定），
        不承诺正文内容完整性校验；单条正文读是最终有效性判定。正文损坏
        只拒绝单项读取，不使整页元数据列表失败；行内绑定损坏仍失败关闭。
        """
        activity_id = self._uuid(activity_id, "activity_id")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
            raise ValueError("limit 必须是 1 到 200 之间的整数")
        if after_operation_id is not None:
            after_operation_id = self._bounded_name(after_operation_id, "after_operation_id")
        conditions = "o.activity_id = %s"
        params: list[object] = [activity_id]
        if after_operation_id is not None:
            conditions += " AND o.operation_id > %s"
            params.append(after_operation_id)

        async def operation(connection: object) -> tuple[OperationRow, ...]:
            cursor = await connection.execute(
                await self._interview_result_sql(connection,await self._memory_result_sql(connection,f"{self._OPERATIONS_LIST_SELECT} WHERE {conditions} ORDER BY o.operation_id LIMIT %s")),
                (*params, limit),
            )
            return tuple(self._operation_list_row_from_row(row) for row in await cursor.fetchall())

        return await self._transaction(operation)

    async def read_operation(self, activity_id: str, operation_id: str) -> OperationRow | None:
        """单操作单条 SQL 快照；正文仅在绑定与来源复查成立时随行返回。"""
        activity_id = self._uuid(activity_id, "activity_id")
        operation_id = self._bounded_name(operation_id, "operation_id")

        async def operation(connection: object) -> OperationRow | None:
            cursor = await connection.execute(
                await self._interview_result_sql(connection,await self._memory_result_sql(connection,f"{self._OPERATIONS_SELECT} WHERE o.activity_id = %s AND o.operation_id = %s")),
                (activity_id, operation_id),
            )
            row = await cursor.fetchone()
            return None if row is None else self._operation_row_from_row(row)

        return await self._transaction(operation)

    async def read_learning_snapshot(self, activity_id: str) -> dict | None:
        """学习组包的有限单语句元数据快照，不读取原件或PDF正文。"""
        activity_id = self._uuid(activity_id, "activity_id")

        async def operation(connection):
            cursor = await connection.execute(await self._memory_result_sql(connection,"""SELECT a.id::text AS activity_id,
                a.status, a.scope_revision, a.deadline_at, a.max_request_bytes,
                /*learning_memory*/TRUE AS memory_eligible, /*learning_selected*/FALSE AS memory_selected,
                a.max_output_tokens, a.max_requests, a.requests_reserved,
                a.max_cost_microunits, a.cost_reserved_microunits, a.reserve_cost_microunits,
                a.max_running_seconds, a.running_reserved_seconds, a.running_settled_seconds,
                (SELECT count(*) FROM activity_scope_sources s WHERE s.activity_id=a.id) AS source_count,
                COALESCE((SELECT jsonb_agg(x ORDER BY x->>'source_id') FROM (
                    SELECT jsonb_build_object('source_id',s.source_id::text,
                        'version_id',s.version_id::text,'source_revision',s.source_revision,
                        'valid',COALESCE(m.current_version=s.version_id AND m.revision=s.source_revision,false),
                        'title',v.filename,'format',v.format,'sha256',v.sha256,'size',v.size,
                        'ready',CASE WHEN v.format IN ('txt','md') THEN true
                          WHEN v.format='pdf' THEN EXISTS (
                            SELECT 1 FROM pdf_review_candidates c WHERE c.version_id=s.version_id
                            AND c.status='confirmed' AND c.page_count BETWEEN 1 AND 50
                            AND (SELECT count(*) FROM pdf_review_pages p WHERE p.candidate_id=c.id)=c.page_count
                            AND (SELECT count(*) FROM pdf_extracted_pages p WHERE p.version_id=c.version_id)=c.page_count)
                          ELSE false END) AS x
                    FROM activity_scope_sources s LEFT JOIN material_sources m ON m.id=s.source_id
                    LEFT JOIN material_versions v ON v.id=s.version_id AND v.source_id=s.source_id
                    WHERE s.activity_id=a.id ORDER BY s.source_id LIMIT 11) bounded),
                    '[]'::jsonb) AS sources
                FROM activities a WHERE a.id=%s"""), (activity_id,))
            row = await cursor.fetchone()
            return None if row is None else dict(row)

        return await self._transaction(operation)

    async def find_learning_operation(self, activity_id: str, prefix: str) -> str | None:
        """只读学习槽位定位，连未提交操作也占槽；最多两个ID，无正文。"""
        activity_id = self._uuid(activity_id, "activity_id")
        from app.learning.contracts import FIRST_PREFIX, NEXT_PREFIX
        if prefix != FIRST_PREFIX:
            if not prefix.startswith(NEXT_PREFIX) or not prefix.endswith("."):
                raise ValueError("invalid_learning_slot")
            self._uuid(prefix[len(NEXT_PREFIX):-1], "business_key")

        async def operation(connection):
            cursor = await connection.execute("""SELECT operation_id FROM activity_operations
                WHERE activity_id=%s AND left(operation_id,%s)=%s ORDER BY operation_id LIMIT 2""",
                (activity_id, len(prefix), prefix))
            rows = await cursor.fetchall()
            if len(rows) > 1:
                raise ResultIntegrityError("invalid_learning_slot")
            return None if not rows else rows[0]["operation_id"]

        return await self._transaction(operation)
