"""Read-only combination of committed DB purge and exact Q body cleanup.

Lock order: shared Q policy -> PG read transaction -> short journal read.
Writers already use exclusive Q policy before PG and cleanup. No QAuthority,
approval observation, journal append, body read or deletion is performed here.
"""
import asyncio
import json
import os
from contextlib import asynccontextmanager

from app.data_exit.contracts import DataError
from app.data_exit.files import RootLease,regular,safe_root
from app.data_exit.q_store import POLICY


def _state(hub):
    safe_root(hub.root)
    with hub.lock.acquire(timeout=1):
        snapshot=hub._validated_locked()
        if snapshot[3]:raise DataError('control_tail_unconfirmed',503)
        return json.loads(snapshot[1])


@asynccontextmanager
async def _policy(ledger):
    gate=getattr(ledger,'mutation_gate',None)
    if gate is None:
        yield None
        return
    hub=gate.hub;state=_state(hub)
    # The sealed target has no normal Q-body store. An old source index
    # cannot stand in for body copies belonging to the selected target.
    if 'q' not in state or getattr(ledger,'data_readonly',False):
        yield None
        return
    inherited=POLICY.get()
    if inherited is not None:
        if inherited[0]!=hub.control_id:raise DataError('q_policy_upgrade_forbidden')
        yield hub
        return
    lock=getattr(gate,'_memory_cleanup_read_lease',None)
    if lock is None:
        # A Q-enabled root must already have its policy lock. GET must not
        # initialize a missing normal-authority store or lock file.
        regular(hub.root/'.q-policy.lock')
        lock=RootLease(hub.root,'.q-policy.lock');gate._memory_cleanup_read_lease=lock
    until=asyncio.get_running_loop().time()+3
    while True:
        try:lease=lock.acquire(False,timeout=0);break
        except (TimeoutError,DataError):
            if asyncio.get_running_loop().time()>=until:raise DataError('q_policy_busy',503)
            await asyncio.sleep(.01)
    token=POLICY.set((hub.control_id,True))
    try:yield hub
    finally:POLICY.reset(token);lease.close()


def _unconfirmed(hub,state,memory_ids):
    ids=set(memory_ids)
    for pid,row in state['q']['requests'].items():
        deps=row.get('dependencies')
        if (not isinstance(deps,dict) or set(deps)!={'sources','memories'}
            or not isinstance(deps['memories'],list) or not isinstance(deps['sources'],list)):
            raise DataError('q_cleanup_dependencies_unknown',503)
        if not ids.intersection(deps['memories']):continue
        cleanup=row.get('cleanup') or {}
        if cleanup.get('state')!='done':return True
        try:os.lstat(hub.artifact_path('q-prepared',pid))
        except FileNotFoundError:continue
        # Any existing/recreated path or inaccessible filesystem is unknown;
        # never substitute lexists(False) for a confirmed absent file.
        return True
    return False


async def read_projected(ledger,operation):
    async with _policy(ledger) as hub:
        result=await operation()
        if hub is None or result is None:return result
        rows=result.get('items') if 'items' in result else [result]
        for row in rows:
            if row.get('state')!='revoked' and row.get('qualification_now')!='revoked':continue
            ids=await ledger.q_snapshot_memory_cleanup_ids(str(row['memory_id']))
            if not ids or str(row['memory_id']) not in ids:raise DataError('q_cleanup_dependencies_unknown',503)
            if _unconfirmed(hub,_state(hub),ids):
                # These are the existing combined-status fields. DB done is
                # never rewritten; committed receipt/effect facts are kept.
                row['cleanup_status_unconfirmed']=True
                row['purge_state_now' if 'purge_state_now' in row else 'purge_state']='pending'
        return result
