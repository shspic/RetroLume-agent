"""PostgreSQL 活动与调用账本。

所有会影响准入的写入都使用短事务。锁顺序固定为来源 UUID 排序、活动、操作；
网络调用由上层在事务结束后执行。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
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
    LedgerDisposition,
    LedgerOutcome,
    RecordOutcome,
    validate_business_payload,
)


_T = TypeVar("_T")
_SAFE_FACT = re.compile(r"^[A-Za-z0-9._:/-]+$")
_MAX_USAGE = 2_147_483_647
_MAX_RESPONSE_BYTES = 67_108_864
# 时间账本（TASK-077）：M/R/S 计数上限与 004 迁移的 BIGINT CHECK 上界一致。
_MAX_RUNNING_SECONDS = 2_147_483_647
_MAX_WINDOW_SECONDS = 3_600
_MAX_WINDOWS_SESSION_ID = 4_294_967_295


class ActivityLedgerConflict(RuntimeError):
    """活动状态或调用方提供的版本已不再适用。"""


class ResultIntegrityError(RuntimeError):
    """持久结果行与权威绑定或规范字节不一致；失败关闭，不冒充读取状态。"""


class ResultReadStatus(enum.Enum):
    """read/list 的业务读取状态；不是业务成功，也不是执行/发送资格。"""

    COMMITTED_CURRENT = "committed_current"
    COMMITTED_HISTORY_CANCELLED = "committed_history_cancelled"
    INVALIDATED_SCOPE_CHANGED = "invalidated_scope_changed"
    INVALIDATED_SOURCE = "invalidated_source"
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


class PostgresAdmissionLedger:
    """`AdmissionLedger` 的失败关闭 PostgreSQL 实现。

    连接、锁和语句都有限时；任何数据库错误对准入调用统一表现为 unavailable，
    不把连接串或服务器错误泄露给上层。
    """

    def __init__(
        self,
        dsn: str,
        *,
        connect_timeout_seconds: int = 3,
        statement_timeout_ms: int = 3_000,
        lock_timeout_ms: int = 2_000,
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

    async def _transaction(self, operation: Callable[[object], Awaitable[_T]]) -> _T:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            raise AdmissionUnavailable("PostgreSQL 驱动不可用") from None
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
                    return await operation(connection)
        except (AdmissionDenied, ActivityLedgerConflict):
            raise
        except psycopg.Error:
            raise AdmissionUnavailable("持久准入账本暂不可用") from None

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
        normalized_sources = tuple(
            sorted(
                (
                    SourceSnapshot(
                        cls._uuid(item.source_id, "source_id"),
                        cls._uuid(item.version_id, "version_id"),
                        item.revision,
                    )
                    for item in spec.sources
                ),
                key=lambda item: UUID(item.source_id).int,
            )
        )
        if len({item.source_id for item in normalized_sources}) != len(normalized_sources):
            raise ValueError("来源快照不能重复")
        if any(item.revision < 0 for item in normalized_sources):
            raise ValueError("来源 revision 非法")
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

    async def create_activity(self, spec: ActivitySpec) -> None:
        activity_id, sources = self._validate_spec(spec)

        async def operation(connection: object) -> None:
            if not await self._lock_sources(connection, sources):
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
                       allowed_tools)
                     VALUES (%s, 'pending', %s, 0, %s, %s, %s, %s, %s, %s, %s, 0, 0, %s)""",
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
            snapshots = await self._source_rows(connection, activity_id)
            sources_valid = bool(snapshots) and await self._lock_sources(connection, snapshots)
            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            activity = await cursor.fetchone()
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
            cursor = await connection.execute(
                """SELECT admission_id FROM activity_operations
                    WHERE activity_id = %s AND operation_id = %s FOR UPDATE""",
                (activity_id, operation_id),
            )
            if await cursor.fetchone() is not None:
                raise AdmissionDenied("操作键已经占用，不能获得第二次发送资格")
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
                       request_bytes, max_output_tokens, tool_names, reserved_cost_microunits)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
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

    async def _locked_operation(self, connection: object, permit: AdmissionPermit) -> tuple[dict, dict, bool]:
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
        snapshots = await self._source_rows(connection, activity_id)
        sources_valid = bool(snapshots) and await self._lock_sources(connection, snapshots)
        cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
        activity = await cursor.fetchone()
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
        ):
            raise AdmissionDenied("准入凭证与操作或执行者不匹配")
        return activity, operation, sources_valid

    @staticmethod
    def _operation_is_current(activity: dict, operation: dict, sources_valid: bool) -> bool:
        now = datetime.now(timezone.utc)
        return (
            sources_valid
            and activity["status"] == "running"
            and activity["executor_id"] == operation["executor_id"]
            and activity["execution_generation"] == operation["execution_generation"]
            and activity["scope_revision"] == operation["scope_revision"]
            and activity["lease_expires_at"] is not None
            and activity["lease_expires_at"] > now
            and activity["deadline_at"] > now
        )

    async def mark_dispatch_started(self, permit: AdmissionPermit) -> None:
        async def operation(connection: object) -> None:
            activity, call, sources_valid = await self._locked_operation(connection, permit)
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
            """SELECT payload_format, payload, payload_sha256
                 FROM activity_operation_results
                WHERE activity_id = %s AND operation_id = %s""",
            (call["activity_id"], call["operation_id"]),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return (row["payload_format"], row["payload"], row["payload_sha256"])

    async def record_outcome(self, permit: AdmissionPermit, outcome: LedgerOutcome) -> RecordOutcome:
        """原子登记终态与（可缺省的）业务正文；返回持久提交确认枚举。

        正文新写与 received 终态在同一短事务内（来源→活动→操作锁序），
        COMMIT 确认后才返回 RECORDED；COMMIT 后响应丢失按持久事实重读。
        分支序：终态严格等值的无写幂等（含正文存在性与 format/规范内容/hash，
        带正文与无正文不等价，旧 received 无正文不能补写，异文冲突保留已有）
        先于失效/未发送新写资格拒绝；正文新写额外显式检查 dispatch_closed
        （_operation_is_current 本身不含关门）。诊断/UNKNOWN 记录合同不变，
        不扩展为正文授权。
        """
        values = self._outcome_values(outcome)
        payload_triple = self._payload_values(outcome)

        async def operation(connection: object) -> RecordOutcome:
            activity, call, sources_valid = await self._locked_operation(connection, permit)
            if call["state"] in {"not_sent", "received", "unknown"}:
                if self._stored_outcome(call) == values:
                    stored_payload = await self._stored_payload_row(connection, call)
                    if payload_triple is None and stored_payload is None:
                        return RecordOutcome.ALREADY_PRESENT
                    if payload_triple is not None and stored_payload is not None and stored_payload == payload_triple:
                        return RecordOutcome.ALREADY_PRESENT
                    if stored_payload is None:
                        raise AdmissionDenied("已终结无正文状态不能补写正文")
                    raise AdmissionDenied("已终结正文与提交不一致")
                raise AdmissionDenied("已终结调用不能覆盖为不同结果")
            current = self._operation_is_current(activity, call, sources_valid)
            if not current and outcome.disposition is not LedgerDisposition.UNKNOWN:
                raise AdmissionDenied("失效或过期执行只能登记 unknown 诊断")
            if call["state"] == "reserved" and outcome.disposition is not LedgerDisposition.UNKNOWN:
                raise AdmissionDenied("尚未越过发送边界的调用不能登记该结果")
            if payload_triple is not None and activity["dispatch_closed"]:
                raise AdmissionDenied("关闭门后不接受正文新写")
            await connection.execute(
                """UPDATE activity_operations
                      SET state = %s, disposition = %s, error_code = %s,
                          remote_request_id = %s, returned_model = %s, finish_reason = %s,
                          prompt_tokens = %s, completion_tokens = %s, response_bytes = %s,
                          recorded_at = CURRENT_TIMESTAMP
                    WHERE admission_id = %s""",
                (values[0], *values, permit.admission_id),
            )
            if payload_triple is not None:
                # 身份冗余值取锁内权威操作行，不直接相信调用参数。
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
            return RecordOutcome.RECORDED

        return await self._transaction(operation)

    # --- G3 只读恢复接口：资格判定与正文投影在单语句内完成；失效不投影正文。

    _RESULT_READ_SQL = """\
SELECT o.state, o.disposition, o.operation_id,
       o.admission_id AS op_admission_id, o.execution_generation AS op_generation,
       o.scope_revision AS op_scope, o.provider, o.configured_model,
       o.finish_reason, o.returned_model, o.remote_request_id,
       o.prompt_tokens, o.completion_tokens, o.response_bytes,
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
        )) AS sources_valid"""

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
                f"""{self._RESULT_READ_SQL},
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
            THEN r.payload ELSE NULL END AS payload,
       o.activity_id
  FROM activity_operations o
  JOIN activities a ON a.id = o.activity_id
  LEFT JOIN activity_operation_results r
         ON r.activity_id = o.activity_id AND r.operation_id = o.operation_id
 WHERE o.activity_id = %s AND o.operation_id = %s""",
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
                f"""{self._RESULT_READ_SQL},
       o.activity_id
  FROM activity_operation_results r
  JOIN activity_operations o
    ON o.activity_id = r.activity_id AND o.operation_id = r.operation_id
  JOIN activities a ON a.id = r.activity_id
 WHERE {conditions}
 ORDER BY r.operation_id
 LIMIT %s""",
                tuple(params),
            )
            rows = list(await cursor.fetchall())
            snapshots = tuple(
                self._snapshot_from_row(row, self._read_status(row, has_result=True), None)
                for row in rows
            )
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
