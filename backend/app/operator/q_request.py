"""Inspect exact Q requests, approve explicitly, or revoke locally."""
from __future__ import annotations
import argparse
import asyncio
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path

from app.capabilities.q_protocol import canonical, digest, load_json
from app.data_exit.contracts import DataError,DataContext
from app.data_exit.files import regular
from app.data_exit.q_store import QAuthority,authority_for


def principal_id():
    if os.name!='nt':return 'uid:'+str(os.getuid())
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    api=ctypes.WinDLL('advapi32',use_last_error=True)
    kernel.GetCurrentProcess.restype=wintypes.HANDLE
    api.OpenProcessToken.argtypes=[wintypes.HANDLE,wintypes.DWORD,ctypes.POINTER(wintypes.HANDLE)]
    api.GetTokenInformation.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)]
    api.ConvertSidToStringSidW.argtypes=[ctypes.c_void_p,ctypes.POINTER(wintypes.LPWSTR)]
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    kernel.LocalFree.argtypes=[ctypes.c_void_p]
    token=wintypes.HANDLE();size=wintypes.DWORD();text=wintypes.LPWSTR()
    if not api.OpenProcessToken(kernel.GetCurrentProcess(),8,ctypes.byref(token)):raise ctypes.WinError()
    try:
        api.GetTokenInformation(token,1,None,0,ctypes.byref(size))
        storage=ctypes.create_string_buffer(size.value)
        if not api.GetTokenInformation(token,1,storage,size,ctypes.byref(size)):raise ctypes.WinError()
        if not api.ConvertSidToStringSidW(ctypes.c_void_p.from_buffer(storage).value,ctypes.byref(text)):raise ctypes.WinError()
        return text.value
    finally:
        if text:kernel.LocalFree(text)
        kernel.CloseHandle(token)


async def inspect_request(ledger,pid):
    from app.capabilities.q_context import snapshot,check_instance,check_snapshot_sql,command_fact
    authority=authority_for(ledger)
    if authority is None:raise DataError('q_control_missing')
    async with authority.async_policy(shared=True):
        row=authority.request(pid)
        if row.get('cleanup'):
            return {'prepared_id':pid,'state':'invalidated','request_available':False,'cleanup':row['cleanup']['state']}
        state,_,_=await snapshot(ledger,row['prepared']['activity_id'])
        check_instance(authority,ledger,state)
        current=state==row['prepared']['snapshot']
        # No private-body fallback after source, memory, parent or instance invalidation.
        if not current:return {'prepared_id':pid,'state':'invalidated','request_available':False}
        async def q_snapshot(connection):
            await check_snapshot_sql(connection,state,authority)
        await ledger._transaction(q_snapshot)
        artifact=authority.artifact(row)
        fact=await command_fact(ledger,row)
        return {'prepared_id':pid,'prepared_sha256':row['prepared_sha256'],
            'projection':authority.projection(row,pg_consumed=fact['consumed']),'prepared':row['prepared'],'pg_command_fact':fact,
            'request':artifact['request'],'provider_object':artifact['payload'],
            'provider_bytes_utf8':canonical(artifact['payload']),'provenance':artifact['provenance'],
            'request_available':True,'execution_class':authority.bundle['execution_class']}


async def approve_request(ledger,pid,expected_sha256):
    authority=authority_for(ledger)
    if authority is None:raise DataError('q_control_missing')
    async with authority.async_policy():
        inspection=await inspect_request(ledger,pid)
        if not inspection['request_available'] or inspection.get('prepared_sha256')!=expected_sha256:
            raise DataError('q_inspection_changed')
        return authority.approve(pid,principal_id(),current=True,pg_consumed=inspection['pg_command_fact']['consumed'])


def read_config(path):
    regular(path)
    raw=Path(path).read_bytes()
    if len(raw)>262144:raise DataError('q_config_limit')
    value=load_json(raw)
    required={'schema','enabled','control_root','database_url_env','root_file'}
    if set(value)!=required or value['schema']!='retrolume.q-approval-config.v2':raise DataError('q_config_shape')
    if type(value['enabled']) is not bool:raise DataError('q_config_shape')
    if not value['enabled']:return value
    if (not isinstance(value['control_root'],str) or not isinstance(value['root_file'],str)
        or not Path(value['control_root']).is_absolute() or not Path(value['root_file']).is_absolute()
        or not isinstance(value['database_url_env'],str) or not value['database_url_env'].startswith('RETROLUME_')):
        raise DataError('q_config_shape')
    return value


def configure_application(app,path):
    """Explicit deployment path, never supplied by a browser. Does not activate Q."""
    value=read_config(path)
    if not value['enabled']:return {'available':False,'reason':'q_disabled'}
    runtime=app.state.data_exit;ledger=app.state.activities_ledger
    if runtime is None or ledger is None or Path(value['control_root']).resolve()!=runtime.hub.root:
        raise DataError('q_original_control_required')
    regular(value['root_file']);raw=Path(value['root_file']).read_bytes()
    if len(raw)>262144:raise DataError('q_root_limit')
    bundle=load_json(raw)
    if (not isinstance(bundle,dict) or set(bundle)!={'schema','execution_class','grant','manifest','binding','templates','template_atoms','operator_principals'}
        or bundle['execution_class'] not in ('Q','TESTONLY')):raise DataError('q_root_shape')
    from app.capabilities.transport import HttpxModelTransport
    if bundle.get('execution_class')=='TESTONLY' and HttpxModelTransport.is_external:
        raise DataError('q_testonly_external_forbidden')
    service=app.state.activity_config.model_service;embedding=app.state.integration_config.service
    if (service is None or embedding is None or not service.returned_models or not embedding.returned_models
        or service.model!='deepseek-flash' or service.outbound_grant!=bundle['grant']
        or embedding.outbound_grant!=bundle['grant']):raise DataError('q_readiness_unknown')
    if 'q' not in runtime.hub.state():QAuthority.bind(runtime.hub,bundle)
    authority=authority_for(ledger)
    if authority.bundle!=bundle:raise DataError('q_deployment_changed')
    return {'available':True,'reason':None,'execution_class':bundle['execution_class'],
            'real_outbound_authorized':bundle['execution_class']=='Q'}


def operator_ledger(config):
    from app.data_exit.control import ControlHub
    from app.data_exit.maintenance import MutationGate
    from app.activities.repository import PostgresAdmissionLedger
    if not config['enabled']:raise DataError('q_disabled')
    dsn=os.environ.get(config['database_url_env'])
    if not dsn:raise DataError('q_operator_database_missing')
    # Opening another root cannot create approval authority: existing journal required.
    root=Path(config['control_root'])
    if not (root/'journal.bin').is_file():raise DataError('q_control_missing')
    hub=ControlHub(root);authority=QAuthority(hub);b=authority.binding
    context=DataContext(b.hub_control_id,b.selection_generation,b.dataset_id,b.instance_id,'normal')
    ledger=PostgresAdmissionLedger(dsn);ledger.data_enabled=True
    ledger.mutation_gate=MutationGate(hub,lambda:context)
    return ledger


async def run_cli(args):
    ledger=operator_ledger(read_config(args.config))
    if args.action=='inspect':return await inspect_request(ledger,args.prepared_id)
    if args.action=='revoke':return authority_for(ledger).revoke(args.prepared_id,principal_id())
    if not args.expected_prepared_sha256:raise DataError('q_exact_digest_required')
    expected='APPROVE '+args.expected_prepared_sha256
    if input('Type '+expected+' after inspecting the exact full request: ')!=expected:
        raise DataError('q_explicit_approval_required')
    return await approve_request(ledger,args.prepared_id,args.expected_prepared_sha256)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('inspect','approve','revoke'))
    parser.add_argument('--config',required=True)
    parser.add_argument('--prepared-id',required=True)
    parser.add_argument('--expected-prepared-sha256')
    args=parser.parse_args()
    if os.name=='nt':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:print(canonical(asyncio.run(run_cli(args))))
    except (DataError,ValueError,OSError) as exc:
        print(canonical({'state':'denied','code':exc.code if isinstance(exc,DataError) else 'q_operator_unavailable'}))
        return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
