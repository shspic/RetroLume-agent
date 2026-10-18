"""全部写入口、跨进程维护围栏和真实自有工作登记。"""
from contextlib import contextmanager
import contextvars
from dataclasses import dataclass
import re
import time
from uuid import uuid4
from .contracts import DataContext, DataError
from .files import RootLease

CURRENT_PERMIT = contextvars.ContextVar("retrolume_data_permit", default=None)
CLOSE_LANE = contextvars.ContextVar("retrolume_data_close_lane", default=None)

NEW_WORK = frozenset(('create_activity','revise_scope','claim_lease','admit','admit_tool_operation','mark_tool_started',
                     'mark_dispatch_started','apply_teaching_local','accept_teaching_command','claim_teaching_launch',
                     'apply_interview_local','accept_interview_command','claim_interview_launch','accept_html_command',
                     'claim_html_command','reserve_html_preview','apply_memory_command'))


def outgoing_operation(operation):
    parts = operation.__qualname__.split('.<locals>.')[0].split('.')
    return parts[-1] in NEW_WORK


def worker_gate(value):
    from .control import ControlHub
    from .contracts import uuid
    if not isinstance(value, dict) or set(value) != {'root','control_id','origin','owned_id'}:
        raise DataError('worker_control_invalid',503)
    root = value['root']
    from pathlib import Path
    if not (Path(root)/'journal.bin').is_file():raise DataError('control_unavailable',503)
    hub = ControlHub(root)
    origin = value['origin']
    if hub.control_id!=value['control_id'] or not isinstance(origin,dict):raise DataError('worker_control_invalid',503)
    owned_id = uuid(value['owned_id'])
    owned = hub.state()['owned'].get(owned_id)
    if owned is None or owned.get('state')!='registered' or owned.get('origin')!=origin:
        raise DataError('owned_work_unknown',503)
    context = DataContext(hub.control_id,origin['selection_generation'],origin['dataset_id'],origin['instance_id'],'normal')
    def current():
        state = hub.state()
        selection = state['selection']
        if selection:return DataContext(hub.control_id,selection['generation'],selection['dataset_id'],selection['instance_id'],'restored_readonly',selection['target_id'])
        if state['fence'] is not None and state['fence']['state']=='frozen':
            return DataContext(hub.control_id,context.generation,context.dataset_id,context.instance_id,'frozen')
        return context
    return MutationGate(hub,current),owned_id


@dataclass
class MutationPermit:
    gate: object
    context: DataContext
    lease: object
    owned_id: str | None = None
    live: bool = True

    def check(self, *, outgoing=False):
        if not self.live: raise DataError("mutation_permit_closed", 503)
        self.lease.check()
        state = self.gate.hub.assert_writable()
        current = self.gate.context()
        if (current.control_id, current.generation, current.dataset_id, current.instance_id) != (
            self.context.control_id, self.context.generation, self.context.dataset_id, self.context.instance_id):
            raise DataError("selection_changed")
        if state["fence"] is not None:
            owner = state["owned"].get(CLOSE_LANE.get())
            if outgoing or owner is None or owner.get("state") != "registered" or owner.get("origin") != self.context.public():
                raise DataError("maintenance_unconfirmed", 503)
        if current.mode != "normal": raise DataError("data_readonly")


class MutationGate:
    def __init__(self, hub, context):
        self.hub, self.context = hub, context
        self.lock = RootLease(hub.root, ".mutation.lock")
        self.admission_lock = RootLease(hub.root, '.admission.lock')

    @contextmanager
    def outgoing_section(self):
        with self.admission_lock.acquire():
            with self.acquire(outgoing=True) as permit:yield permit

    @contextmanager
    def acquire(self, *, outgoing=False, expected=None):
        inherited = CURRENT_PERMIT.get()
        if inherited is not None and inherited.gate is self:
            inherited.check(outgoing=outgoing)
            if expected is not None and inherited.context != expected: raise DataError("selection_changed")
            yield inherited
            return
        with self.lock.acquire() as lease:
            permit = MutationPermit(self, self.context(), lease)
            if expected is not None and permit.context != expected: raise DataError("selection_changed")
            permit.check(outgoing=outgoing)
            token = CURRENT_PERMIT.set(permit)
            try: yield permit
            finally:
                permit.live = False
                CURRENT_PERMIT.reset(token)

    def register_owned(self, kind, identity):
        permit = CURRENT_PERMIT.get()
        if permit is None or permit.gate is not self: raise DataError("mutation_permit_required", 503)
        permit.check(outgoing=True)
        owned_id = str(uuid4())
        def check(state):
            if state['fence'] is not None:raise DataError('maintenance_unconfirmed',503)
            selected=state['selection']
            if selected is not None:raise DataError('data_readonly')
        self.hub.commit("owned.begin", {"owned_id": owned_id, "kind": kind, "identity": identity,
                                       "origin": permit.context.public(), "state": "registered", "parent_owned_id": CLOSE_LANE.get()},validate=check)
        return owned_id

    def end_owned(self, owned_id, *, confirmed, proof_sha256=None):
        self.hub.commit("owned.end", {"owned_id": owned_id,
                                     "state": "ended" if confirmed else "unknown", "proof_sha256": proof_sha256})

    @contextmanager
    def close_lane(self, owned_id):
        token = CLOSE_LANE.set(owned_id)
        try: yield
        finally: CLOSE_LANE.reset(token)


WRITE_SQL = re.compile(r"\b(INSERT|UPDATE|DELETE|TRUNCATE|ALTER|CREATE|DROP|GRANT|REVOKE|COPY)\b", re.I)
WRITE_FUNCTION = re.compile(r"\b(html_(?:accept_command|claim_command|commit_artifact|finish_command|reserve_preview|update_preview)|purge_learning_memory|data_(?:reference|source_delete|control_frozen|observe_job))\s*\(", re.I)


def sql_writes(sql):
    text = sql if isinstance(sql,str) else sql.as_string() if hasattr(sql,'as_string') else str(sql)
    text = re.sub(r"'(?:''|[^'])*'|/\*.*?\*/|--[^\n]*", " ", text, flags=re.S)
    text = re.sub(r"\bFOR\s+(?:KEY\s+)?(?:UPDATE|SHARE)(?:\s+OF\s+[\w,]+)?", " ", text, flags=re.I)
    return bool(WRITE_SQL.search(text) or WRITE_FUNCTION.search(text))


class GuardedAsyncConnection:
    """在第一次业务写之前取得 permit，并持有至真实事务退出。"""
    def __init__(self, connection, gate, readonly=False):
        self.connection, self.gate, self.readonly = connection, gate, readonly
        self._context = None

    def _check(self, sql):
        if sql_writes(sql):
            if self.readonly or self.gate is None: raise DataError("data_readonly")
            if self._context is None:
                self._context = self.gate.acquire()
                self._permit = self._context.__enter__()
            self._permit.check()

    async def execute(self, sql, *args, **kwargs):
        self._check(sql)
        if self.readonly and not sql_writes(sql):
            sql = re.sub(r"\s+FOR\s+(?:KEY\s+)?(?:UPDATE|SHARE)(?:\s+OF\s+[\w,]+)?", "", str(sql), flags=re.I)
        return await self.connection.execute(sql, *args, **kwargs)

    def cursor(self, *args, **kwargs):
        return GuardedAsyncCursor(self, self.connection.cursor(*args, **kwargs))

    def __getattr__(self, name): return getattr(self.connection, name)

    def close_permit(self):
        if self._context is not None:
            self._context.__exit__(None, None, None)
            self._context = None


class GuardedAsyncCursor:
    def __init__(self, connection, cursor): self.connection, self.inner = connection, cursor
    async def __aenter__(self):
        await self.inner.__aenter__(); return self
    async def __aexit__(self, *args): return await self.inner.__aexit__(*args)
    async def execute(self, sql, *args, **kwargs):
        self.connection._check(sql); return await self.inner.execute(sql, *args, **kwargs)
    async def executemany(self, sql, *args, **kwargs):
        self.connection._check(sql); return await self.inner.executemany(sql, *args, **kwargs)
    def __getattr__(self, name): return getattr(self.inner, name)


class MaintenanceCoordinator:
    def __init__(self, gate, source, maintenance_key, close_owned=None):
        self.gate, self.source, self.maintenance_key, self.close_owned = gate, source, maintenance_key, close_owned

    async def drain_for_readonly_switch(self, expected_generation, deadline):
        context = self.gate.context()
        state=self.gate.hub.state()
        confirmed_frozen=context.mode=='frozen' and state['fence'] is not None and state['fence']['state']=='frozen'
        if context.generation != expected_generation or (context.mode != "normal" and not confirmed_frozen): raise DataError("selection_changed")
        with self.gate.admission_lock.acquire(True):
            self.gate.hub.commit("maintenance.fence", {"origin": context.public(), "state": "draining"})
        if self.close_owned is not None:
            await self.close_owned()
        # 原监督链负责具体停止，未知自有树阻止切换；旧历史未知不登记为本次 owner。
        while any(v.get("state") != "ended" for v in self.gate.hub.state()["owned"].values()):
            if time.monotonic() >= deadline: raise DataError("maintenance_unconfirmed", 503)
            import asyncio
            await asyncio.sleep(0.02)
        remaining = max(0, deadline - time.monotonic())
        lease = self.gate.lock.acquire(True, timeout=remaining)
        try:
            with self.source.connection() as connection:
                connection.execute("SELECT public.data_control_frozen(%s,%s,%s)",
                                   (context.dataset_id, context.instance_id, self.maintenance_key))
            self.gate.hub.commit("maintenance.fence", {"origin": context.public(), "state": "frozen"})
            return lease
        except BaseException:
            lease.close()
            raise


def owned_service(function):
    """登记到领域最终提交，不能在 native 子树结束后遗忘结果收尾。"""
    from functools import wraps
    @wraps(function)
    async def wrapped(*args,**kwargs):
        subject=args[0] if args else kwargs.get('request',kwargs.get('self'))
        ledger=getattr(subject,'ledger',None)
        if ledger is None and hasattr(subject,'app'):ledger=getattr(subject.app.state,'activities_ledger',None)
        gate=getattr(ledger,'mutation_gate',None)
        if gate is None:return await function(*args,**kwargs)
        import os
        from app.preview.process import birth
        with gate.acquire(outgoing=True):
            parent=birth(os.getpid())
            if parent['state']!='running':raise DataError('owned_work_unknown',503)
            identity={'parent':{'pid':os.getpid(),'birth':parent['birth']},'service':function.__qualname__}
            owned=gate.register_owned('domain_service',identity)
            try:
                with gate.close_lane(owned):return await function(*args,**kwargs)
            finally:
                children=[v for v in gate.hub.state()['owned'].values() if v.get('parent_owned_id')==owned]
                gate.end_owned(owned,confirmed=all(v.get('state')=='ended' for v in children))
    import inspect
    wrapped.__signature__=inspect.signature(function,eval_str=True)
    return wrapped
