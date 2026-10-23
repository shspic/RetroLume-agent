"""一次消费、一个进程时钟域、取消和不可逆准入的短CAS协议。

日志中只保存私有执行事实；进程重启不能恢复旧时钟域的执行权。
"""
from contextlib import contextmanager
import asyncio
import contextvars
import functools
import math
import time
from uuid import uuid4
from .contracts import DataError

CLOCK_DOMAIN = str(uuid4())
TERMINAL = frozenset(('published', 'received', 'verified', 'active_readonly', 'deleted',
                     'cancelled', 'failed', 'published_unconfirmed', 'upload_unconfirmed',
                     'restore_unconfirmed', 'activation_unconfirmed', 'cleanup_unconfirmed'))
ADMISSIONS = {'portable_export': ('file_publish', ('published',)), 'restore_checkpoint': ('file_publish', ('published',)),
              'upload': ('upload_publish', ('received',)), 'restore': ('readonly_seal', ('verified',)),
              'source_delete': ('source_tombstone_commit', ('deleted', 'deleted_pending')),
              'activate': ('readonly_maintenance_selector', ('active_readonly',))}


async def joined_thread(function, *args, **kwargs):
    """取消外层协程不能冒称同步线程已停；收尾须等准确消费者返回。"""
    context = contextvars.copy_context()
    future = asyncio.get_running_loop().run_in_executor(None, functools.partial(context.run, function, *args, **kwargs))
    cancelled = None
    while True:
        try:
            result = await asyncio.shield(future)
            if cancelled is not None: raise cancelled
            return result
        except asyncio.CancelledError as error:
            if future.done(): raise
            cancelled = error  # 重复协程cancel也不放弃准确同步消费者。
        except BaseException:
            if cancelled is not None: raise cancelled
            raise


def validate_success(job, state):
    execution = job.get('execution', {})
    phase, outcomes = ADMISSIONS[job['kind']]
    if (job['state'] != 'committing' or execution.get('clock_domain') != CLOCK_DOMAIN
        or (execution.get('admission') or {}).get('phase') != phase or state not in outcomes):
        raise DataError('operation_authority_unknown')
    if time.monotonic_ns() >= execution['deadline_ns']: raise DataError('operation_timeout', 504)


def request_cancel(hub, job_id):
    def decide(job):
        if job.get('execution_protocol') != 2:
            raise DataError('operation_authority_unknown')
        if job['state'] in ('cancel_requested', 'cancelled'):
            return None
        if job['state'] not in ('prepared', 'running') or job.get('execution', {}).get('admission'):
            raise DataError('operation_not_cancelable')
        return {'state': 'cancel_requested', 'stage': 'cancel_requested'}
    return hub.change_job(job_id, decide)


def acknowledge_unstarted(hub, job_id):
    def decide(job):
        if job.get('execution_protocol') != 2 or job.get('execution') is not None:
            raise DataError('operation_authority_unknown')
        if job['state'] == 'cancel_requested':
            return {'state': 'cancelled', 'stage': 'cancelled'}
        return None
    return hub.change_job(job_id, decide)


class Operation:
    def __init__(self, hub, job_id, seconds, stage, **changes):
        self.hub, self.job_id, self.actor = hub, job_id, str(uuid4())
        if not math.isfinite(seconds) or seconds <= 0: raise DataError('operation_timeout', 504)
        now = time.monotonic_ns()
        self.deadline_ns = now + int(seconds * 1e9)
        self.admission = None
        def begin(job):
            if job.get('execution_protocol') != 2 or job.get('completion_protocol') != 1 or job.get('execution') is not None:
                raise DataError('operation_authority_unknown')
            if job['state'] in ('cancel_requested', 'cancelled'):
                raise DataError('operation_cancelled')
            if job['state'] != 'prepared': raise DataError('request_conflict')
            return {**changes, 'state': 'running', 'stage': stage,
                    'execution': {'clock_domain': CLOCK_DOMAIN, 'actor_id': self.actor,
                                  'started_ns': now, 'deadline_ns': self.deadline_ns, 'admission': None}}
        self.revision = hub.change_job(job_id, begin)['revision']

    @classmethod
    def resume_cleanup(cls, hub, job_id):
        self = cls.__new__(cls)
        self.hub, self.job_id = hub, job_id
        job = hub.state()['jobs'][job_id]
        execution = job.get('execution', {})
        if job.get('execution_protocol') != 2 or execution.get('clock_domain') != CLOCK_DOMAIN:
            raise DataError('operation_authority_unknown')
        self.actor, self.deadline_ns, self.admission = execution['actor_id'], execution['deadline_ns'], execution['admission']
        def resume(current):
            if current['revision'] != job['revision'] or current['state'] not in ('deleted_pending', 'deletion_unconfirmed'):
                raise DataError('request_conflict')
            self.remaining()
            if self.admission is None: raise DataError('operation_authority_unknown')
            return {'state': 'committing', 'stage': 'cleanup_retry'}
        self.revision = hub.change_job(job_id, resume)['revision']
        return self

    def remaining(self, cap=None):
        remaining = (self.deadline_ns - time.monotonic_ns()) / 1e9
        if remaining <= 0: raise DataError('operation_timeout', 504)
        return min(remaining, cap) if cap is not None else remaining

    def _validate(self, job, *, deadline=True):
        execution = job.get('execution', {})
        if (execution.get('clock_domain') != CLOCK_DOMAIN or execution.get('actor_id') != self.actor
            or execution.get('deadline_ns') != self.deadline_ns):
            raise DataError('operation_authority_unknown')
        if job['state'] in ('cancel_requested', 'cancelled'): raise DataError('operation_cancelled')
        if job['state'] not in ('running', 'committing'): raise DataError('request_conflict')
        if deadline: self.remaining()

    def check(self):
        job = self.hub.execution_job(self.job_id)
        self._validate(job)
        if job['revision'] != self.revision: raise DataError('request_conflict')

    def stage(self, stage, **changes):
        self.check()
        receipt = self.hub.update_job(self.job_id, self.revision, expected_states=('running',),
                                      validate=self._validate, stage=stage, **changes)
        self.revision = receipt['revision']
        return receipt

    def admit(self, phase):
        self.check()
        ticket = str(uuid4())
        job = self.hub.state()['jobs'][self.job_id]
        if ADMISSIONS[job['kind']][0] != phase: raise DataError('operation_authority_unknown')
        execution = {**job['execution'], 'admission': {'phase': phase, 'ticket': ticket}}
        receipt = self.hub.update_job(self.job_id, self.revision, expected_states=('running',),
                                      validate=self._validate, state='committing', stage=phase, execution=execution)
        self.revision, self.admission = receipt['revision'], execution['admission']
        return self.admission

    def validate_admission(self, job):
        self._validate(job)
        if job['state'] != 'committing' or job['execution'].get('admission') != self.admission or self.admission is None:
            raise DataError('request_conflict')

    def finish(self, state, stage=None, **changes):
        # 精确执行者持有的revision；从不读取latest revision授成功。
        validate_success(self.hub.state()['jobs'][self.job_id], state)
        receipt = self.hub.update_job(self.job_id, self.revision, expected_states=('committing',),
            validate=self.validate_admission, state=state, stage=stage or state, **changes)
        self.revision = receipt['revision']
        # 成功帧的真实COMMIT返回也在同D内；未确认前GET仅显示实际未确认事实。
        confirmed_ns = time.monotonic_ns()
        self.remaining()
        def confirm(job):
            execution=job.get('execution',{})
            if (execution.get('clock_domain')!=CLOCK_DOMAIN or execution.get('actor_id')!=self.actor
                or execution.get('deadline_ns')!=self.deadline_ns or job['state']!=state):
                raise DataError('operation_authority_unknown')
            self.remaining()
        receipt=self.hub.update_job(self.job_id,self.revision,expected_states=(state,),validate=confirm,
                                   completion_confirmed_ns=confirmed_ns)
        self.revision=receipt['revision']
        return receipt

    def fail(self, error, *, cleanup_complete, state='failed', **facts):
        def decide(job):
            execution = job.get('execution', {})
            if execution.get('actor_id') != self.actor or execution.get('clock_domain') != CLOCK_DOMAIN:
                raise DataError('operation_authority_unknown')
            pending_success=job.get('completion_protocol')==1 and job['state'] in ('published','received','verified','active_readonly','deleted','deleted_pending') and job.get('completion_confirmed_ns') is None
            if job['state'] in TERMINAL and not pending_success: return None
            if job['state'] == 'cancel_requested':
                outcome = 'cancelled' if cleanup_complete and execution.get('admission') is None else 'cleanup_unconfirmed'
            elif pending_success:
                outcome={'portable_export':'published_unconfirmed','restore_checkpoint':'published_unconfirmed','upload':'upload_unconfirmed',
                         'restore':'restore_unconfirmed','activate':'activation_unconfirmed','source_delete':'deletion_unconfirmed'}[job['kind']]
            else: outcome = state
            return {**facts, 'state': outcome, 'stage': outcome,
                    'error_code': error.code if isinstance(error, DataError) else 'storage_unavailable'}
        return self.hub.change_job(self.job_id, decide)

    def connect_seconds(self, cap=3):
        remaining = self.remaining(cap)
        # libpq只接受整数秒；不足1秒不能用0变成无限等待。
        if remaining < 1: raise DataError('operation_timeout', 504)
        return max(1, int(remaining))

    @contextmanager
    def connection(self, dsn, **kwargs):
        import psycopg
        self.check()
        ms = max(1, int(self.remaining(30) * 1000))
        kwargs['options'] = f"-c statement_timeout={ms} -c lock_timeout={min(ms, 3000)} " + kwargs.get('options', '')
        with psycopg.connect(dsn, connect_timeout=self.connect_seconds(), **kwargs) as raw:
            connection = BoundedConnection(raw, self)
            yield connection
            self.check()  # 事务COMMIT也是同D下的新阶段。
        self.check()


class BoundedConnection:
    def __init__(self, raw, operation): self.raw, self.operation = raw, operation
    def __getattr__(self, name): return getattr(self.raw, name)
    def bound(self):
        self.operation.check()
        ms = int(self.operation.remaining(30) * 1000)
        if ms < 1: raise DataError('operation_timeout', 504)
        prefix = 'SET' if self.raw.autocommit else 'SET LOCAL'
        self.raw.execute(f"{prefix} statement_timeout='{ms}ms'")
        self.raw.execute(f"{prefix} lock_timeout='{min(ms, 3000)}ms'")
    def execute(self, *args, **kwargs):
        # BEGIN须是快照事务第一条语句，不能先用SET LOCAL开启普通事务。
        if args and isinstance(args[0], str) and args[0].lstrip().upper().startswith('BEGIN') and self.raw.info.transaction_status == 0:
            self.operation.check()
            value = self.raw.execute(*args, **kwargs)
            self.operation.check()
            return value
        self.bound()
        value = self.raw.execute(*args, **kwargs)
        self.operation.check()
        return value
    def cursor(self, *args, **kwargs): return BoundedCursor(self.raw.cursor(*args, **kwargs), self)


class BoundedCursor:
    def __init__(self, raw, connection): self.raw, self.connection = raw, connection
    def __getattr__(self, name): return getattr(self.raw, name)
    def __enter__(self): self.raw.__enter__(); return self
    def __exit__(self, *args): return self.raw.__exit__(*args)
    def execute(self, *args, **kwargs):
        self.connection.bound()
        result = self.raw.execute(*args, **kwargs)
        self.connection.operation.check()
        return result
    def fetchmany(self, *args, **kwargs):
        self.connection.bound()
        result = self.raw.fetchmany(*args, **kwargs)
        self.connection.operation.check()
        return result
