"""C02已证反例改为正确断言；真实Hub/文件，load与故障点明确受控。"""
import asyncio
import faulthandler
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import uuid4
import zipfile
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'fixtures/task114'))
from app.data_exit.contracts import DataContext, DataJobCommand, DataError, Limits, TABLES, canonical, digest
from app.data_exit.control import ControlHub
from app.data_exit.operations import Operation, request_cancel, acknowledge_unstarted, CLOCK_DOMAIN
from app.data_exit.packages import DataPackageService, PackageReader
from app.data_exit.snapshot import SnapshotResult
from app.data_exit.restore import RestoreController
from app.data_exit.codec import load_json
from app.data_exit.api import upload
from app.runtime import psycopg_compatible_loop_factory
from starlette.requests import Request
from test_data_exit_package import sample
from budget import EVIDENCE

BASE = EVIDENCE / 'synthetic/scratch/c02-offline'
OUT = EVIDENCE / 'offline/cases' / os.environ.get('C02_CASE_ATTEMPT', 'initial')


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / (name + '.json')).open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2))


def setup(name):
    root = BASE / (name + '-' + str(uuid4())); root.mkdir(parents=True)
    hub = ControlHub(root)
    return hub, DataContext(hub.control_id, 0, str(uuid4()), str(uuid4()), 'normal'), root


def package(path, identity=None):
    members, manifest = sample()
    if identity:
        manifest['package_id'] = identity; manifest.pop('root_sha256'); manifest['root_sha256'] = digest(canonical(manifest))
        members['manifest.json'] = canonical(manifest).encode()
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED, allowZip64=False) as z:
        for name, raw in members.items(): z.writestr(name, raw)
    return members, manifest


def publisher(name, seconds=1800):
    hub, ctx, root = setup(name)
    backup = root / 'backup'; backup.mkdir()
    job = hub.create_or_get_job(DataJobCommand('restore_checkpoint', name, {'mode': 'all'}), ctx)
    members, manifest = package(root / 'input.rldata', job['job_id'])
    captured_root = root / 'capture'; captured_root.mkdir()
    for member, raw in members.items():
        if member == 'manifest.json': continue
        path = captured_root / member; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    control = json.loads(members['metadata/source_control.json'])
    captured = SnapshotResult(captured_root, {'logical_time_utc':'2026-10-12T00:00:00+00:00','database_snapshot':'1:2:'},
        control, manifest['contents'], [], {t: [] for t in TABLES}, {'mode':'all'})
    calls = []
    def capture(*args, **kwargs): calls.append('capture'); kwargs['on_stage']('reading'); return captured
    service = DataPackageService(hub, SimpleNamespace(capture=capture), backup, Limits(operation_seconds=seconds))
    return hub, job, service, calls


def request(value, receive):
    scope={'type':'http','method':'POST','scheme':'http','path':'/api/data/uploads','root_path':'','query_string':b'',
      'server':('127.0.0.1',18114),'client':('127.0.0.1',30001),'headers':[(b'x-retrolume-session',b'c02-synthetic-session')],
      'app':SimpleNamespace(state=SimpleNamespace(session_token='c02-synthetic-session',data_exit=value))}
    return Request(scope, receive=receive)


class Boundaries(unittest.TestCase):
    def test_01_every_kind_cancel_first_and_admission_first(self):
        results=[]
        phases={'portable_export':('file_publish','published'),'restore_checkpoint':('file_publish','published'),
                'upload':('upload_publish','received'),'restore':('readonly_seal','verified'),
                'source_delete':('source_tombstone_commit','deleted'),'activate':('readonly_maintenance_selector','active_readonly')}
        for kind,(phase,terminal) in phases.items():
            hub,ctx,root=setup(kind)
            scope={'plan_id':str(uuid4()),'plan_sha256':'a'*64} if kind=='restore' else {}
            job=hub.create_or_get_job(DataJobCommand(kind,'cancel-first',scope),ctx)
            op=Operation(hub,job['job_id'],10,'reading')
            accepted=request_cancel(hub,job['job_id']);self.assertEqual(accepted['state'],'cancel_requested')
            with self.assertRaises(DataError):op.admit(phase)
            self.assertEqual(op.fail(DataError('operation_cancelled'),cleanup_complete=True)['state'],'cancelled')
            with self.assertRaises(DataError):hub.update_job(job['job_id'],hub.get(job['job_id'])['revision'],state=terminal)
            job=hub.create_or_get_job(DataJobCommand(kind,'admit-first',scope),ctx);op=Operation(hub,job['job_id'],10,'reading');op.admit(phase)
            with self.assertRaises(DataError) as e:request_cancel(hub,job['job_id'])
            self.assertEqual(e.exception.code,'operation_not_cancelable')
            self.assertEqual(op.finish(terminal)['state'],terminal)
            results.append({'kind':kind,'cancel_first':'cancel_requested then executor cancelled','admit_first':'cancel rejected; success CAS permitted'})
        save('01-cas-all-kinds',{'layer':'real private journal; no business PG','results':results})

    def test_02_publish_cancel_before_admission_and_after_admission(self):
        from app.data_exit import packages
        hub,job,service,calls=publisher('publish-cancel-first')
        original=packages.PackageReader
        def reader(*args,**kwargs):request_cancel(hub,job['job_id']);return original(*args,**kwargs)
        with patch.object(packages,'PackageReader',reader):
            with self.assertRaises(DataError):service.capture_and_publish(job['job_id'],{'mode':'all'})
        self.assertFalse(service.path(job['job_id']).exists());self.assertEqual(hub.get(job['job_id'])['state'],'cancelled')
        hub2,job2,service2,calls2=publisher('publish-admit-first');link=packages.publish;cancel_results=[]
        def admitted(*args,**kwargs):
            try:request_cancel(hub2,job2['job_id'])
            except DataError as e:cancel_results.append(e.code)
            return link(*args,**kwargs)
        with patch.object(packages,'publish',admitted):final=service2.capture_and_publish(job2['job_id'],{'mode':'all'})
        self.assertEqual(cancel_results,['operation_not_cancelable']);self.assertEqual(final['state'],'published')
        save('02-real-file-cancel',{'layer':'real ZIP/no-replace/Hub; captured input controlled','cancel_first':hub.get(job['job_id']),
            'file_after_cancel':False,'admission_first':final,'cancel_result':cancel_results})

    def test_03_last_load_cancel_no_seal_after_cleanup(self):
        hub,ctx,root=setup('restore-cancel');incoming=root/'incoming';incoming.mkdir();uid=str(uuid4())
        _,m=package(incoming/(uid+'.rldata'));pid=str(uuid4());plan={'plan_id':pid,'upload_id':uid,'package_sha256':digest((incoming/(uid+'.rldata')).read_bytes()),
          'package_root_sha256':m['root_sha256'],'resource_profile_id':'controlled-c02','latest_status':'unknown'}
        sha=hub.save_artifact('plans',pid,canonical(plan).encode());hub.commit('plan.create',{'plan_id':pid,'plan_sha256':sha,'public':{}})
        job=hub.create_or_get_job(DataJobCommand('restore','cancel-load',{'plan_id':pid,'plan_sha256':sha}),ctx);calls=[]
        target=SimpleNamespace(target_id=str(uuid4()),job_id=job['job_id'])
        hub.commit('target.register',{'target_id':target.target_id,'job_id':job['job_id'],'state':'allocated'})
        factory=SimpleNamespace(allocate=lambda *args:target,seal_readonly=lambda *a:calls.append('seal'),
            abandon=lambda *a:(calls.append('abandon') or True),stop=lambda *a:calls.append('stop'))
        controller=RestoreController(hub,incoming,factory,None,None)
        def load(*args):request_cancel(hub,job['job_id']);return {'counts':{'rows':0}}
        controller._load=load
        with self.assertRaises(DataError):controller.verify(job['job_id'],sha)
        self.assertEqual(calls,['abandon','stop']);self.assertEqual(hub.get(job['job_id'])['state'],'cancelled')
        save('03-last-load-cancel',{'layer':'real controller/ZIP/Hub; factory/load controlled, not PG','final':hub.get(job['job_id']),'calls':calls})

    def test_04_upload_eof_cancel_and_disconnect(self):
        observations=[]
        for mode in ('cancel','disconnect'):
            hub,ctx,root=setup('upload-'+mode);incoming=root/'incoming';incoming.mkdir();uid=str(uuid4());path=root/'input.rldata';package(path);raw=path.read_bytes()
            value=SimpleNamespace(hub=hub,context=lambda:ctx,incoming=incoming,limits=Limits());n=0
            async def receive():
                nonlocal n
                n+=1
                if n==1:return {'type':'http.request','body':raw,'more_body':True}
                if mode=='disconnect':return {'type':'http.disconnect'}
                request_cancel(hub,hub.get_by_key('upload')['job_id']);return {'type':'http.request','body':b'','more_body':False}
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
                with self.assertRaises(Exception):runner.run(upload(request(value,receive),'upload',uid,digest(raw),len(raw)))
            final=hub.get_by_key('upload');self.assertNotEqual(final['state'],'received');self.assertFalse((incoming/(uid+'.rldata')).exists())
            if mode=='cancel':self.assertEqual(final['state'],'cancelled')
            observations.append({'mode':mode,'final':final,'published':False})
        save('04-asgi-upload',{'layer':'actual ASGI handler and files; receive controlled; not TCP','results':observations})

    def test_05_whole_deadline_and_receipt_loss(self):
        from app.data_exit import packages
        hub,job,service,calls=publisher('publish-deadline',1);link=packages.publish;start=time.monotonic()
        def delayed(*args,**kwargs):time.sleep(1.1);return link(*args,**kwargs)
        with patch.object(packages,'publish',delayed):
            with self.assertRaises(DataError) as e:service.capture_and_publish(job['job_id'],{'mode':'all'})
        self.assertEqual(e.exception.code,'operation_timeout');self.assertFalse(service.path(job['job_id']).exists())
        jobfacts=hub.state()['jobs'][job['job_id']];self.assertEqual(jobfacts['execution']['deadline_ns']-jobfacts['execution']['started_ns'],1000000000)
        save('05-one-deadline',{'layer':'actual post-capture file method, controlled 1.1s delay','seconds':time.monotonic()-start,
            'operation_seconds':1,'final':hub.get(job['job_id']),'file':False,'deadline_not_reset':True})
        hub,job,service,calls=publisher('receipt-loss');update=hub.update_job
        def lost(*args,**kwargs):
            if kwargs.get('state')=='published':raise OSError('controlled receipt failure')
            return update(*args,**kwargs)
        with patch.object(hub,'update_job',lost):
            with self.assertRaises(OSError):service.capture_and_publish(job['job_id'],{'mode':'all'})
        raw=service.path(job['job_id']).read_bytes();before=hub.path.read_bytes();again=service.capture_and_publish(job['job_id'],{'mode':'all'})
        self.assertEqual(again['state'],'published_unconfirmed');self.assertEqual(again['file_publication'],'confirmed')
        self.assertEqual(calls,['capture']);self.assertEqual(hub.path.read_bytes(),before);self.assertEqual(service.path(job['job_id']).read_bytes(),raw)
        save('06-receipt-loss',{'layer':'real publication; controlled receipt failure','reconciled':again,'capture_count':1,'GET_unchanged':True})

    def test_06_clock_unknown_and_depth(self):
        hub,ctx,root=setup('unknown-clock');job=hub.create_or_get_job(DataJobCommand('source_delete','old-clock',{}),ctx);op=Operation(hub,job['job_id'],10,'reading');op.admit('source_tombstone_commit')
        op.fail(DataError('storage_unavailable'),cleanup_complete=False,state='deletion_unconfirmed')
        before=hub.path.read_bytes()
        with patch('app.data_exit.operations.CLOCK_DOMAIN',str(uuid4())):
            with self.assertRaises(DataError) as e:Operation.resume_cleanup(hub,job['job_id'])
            self.assertEqual(e.exception.code,'operation_authority_unknown')
        self.assertEqual(before,hub.path.read_bytes())
        self.assertEqual(load_json(b'[[0]]',Limits(json_depth=2)),[[0]])
        with self.assertRaises(DataError):load_json(b'[[[0]]]',Limits(json_depth=2))
        save('07-clock-and-depth',{'unknown_clock_grants':0,'journal_unchanged':True,'JSON_depth_exact_and_over':'passed'})

    def test_07_spool_copy_and_fsync_faults(self):
        from app.data_exit import packages
        from app.data_exit.snapshot import SnapshotCoordinator
        from app.data_exit.files import RootLease
        from app.storage.originals import OriginalStore
        from test_data_exit_incremental import Connection
        from contextlib import contextmanager
        cases=[]
        for mode in ('spool','copy','fsync'):
            hub,job,service,calls=publisher('fault-'+mode)
            old = service.path(job['job_id']).parent/'retained-prior.rldata';old.write_bytes(b'PRIOR RETAINED FILE')
            if mode=='spool':
                source=service.root/'source';source.mkdir();store=OriginalStore(source);lease=RootLease(source)
                raw=b'C02 copy input';original=store.put(io.BytesIO(raw),max_bytes=4096);sid,vid=str(uuid4()),str(uuid4())
                rows={t:[] for t in TABLES};rows['material_sources']=[dict(id=sid,title='source',current_version=vid,revision=1)]
                rows['material_versions']=[dict(id=vid,source_id=sid,filename='input.md',format='md',sha256=original.sha256,size=len(raw),created_at=datetime.now(timezone.utc))]
                control=dict(dataset_id=str(uuid4()),schema_profile='data_exit.v1.r01',created_at=datetime.now(timezone.utc),source_instance_observed=str(uuid4()),mode_observed='normal',source_snapshot_id=None,source_root_sha256=None)
                @contextmanager
                def connection(**kwargs):yield Connection(rows,control)
                snap=SnapshotCoordinator('controlled-db',store,lease,service.root);snap.repository=SimpleNamespace(connection=connection);service.snapshot=snap
            original_open=Path.open;original_fsync=os.fsync;injected=[]
            def opening(path,mode_arg='r',*args,**kwargs):
                if mode=='spool' and path.name=='material_sources.jsonl' and '.raw' in path.parts and mode_arg=='xb' and not injected:
                    injected.append('spool-open');raise OSError('controlled spool write failure')
                stream=original_open(path,mode_arg,*args,**kwargs)
                if mode=='copy' and path.name=='README.txt' and 'capture' in path.parts and mode_arg=='rb' and not injected:
                    class BrokenRead:
                        def __enter__(self):return self
                        def __exit__(self,*args):stream.close()
                        def read(self,*args):injected.append('copy-read');raise OSError('controlled copy read failure')
                    return BrokenRead()
                return stream
            pending=service.packages/(job['job_id']+'.pending')
            def syncing(fd):
                if mode=='fsync' and pending.exists() and os.fstat(fd).st_ino==pending.stat().st_ino and not injected:
                    injected.append('pending-fsync');raise OSError('controlled fsync failure')
                return original_fsync(fd)
            with patch.object(Path,'open',opening),patch.object(os,'fsync',syncing):
                with self.assertRaises(OSError):service.capture_and_publish(job['job_id'],{'mode':'all'})
            self.assertEqual(len(injected),1);self.assertFalse(service.path(job['job_id']).exists());self.assertFalse(pending.exists())
            self.assertEqual(hub.get(job['job_id'])['state'],'failed');self.assertEqual(old.read_bytes(),b'PRIOR RETAINED FILE')
            self.assertEqual(service.capture_and_publish(job['job_id'],{'mode':'all'})['state'],'failed')
            if mode=='spool':lease.close()
            cases.append({'case':mode,'injected':injected,'final':hub.get(job['job_id']),'old_file_unchanged':True,'new_publication':False})
        save('08-spool-copy-fsync',{'layer':'real snapshot file spool/ZIP/fsync/Hub; database rows controlled; no kernel hang','cases':cases})

    def test_08_allocation_seal_and_deadline_rejections(self):
        cases=[]
        for mode in ('half_register','seal_reject','allocate_deadline'):
            hub,ctx,root=setup(mode);incoming=root/'incoming';incoming.mkdir();uid=str(uuid4());_,m=package(incoming/(uid+'.rldata'));pid=str(uuid4())
            plan={'plan_id':pid,'upload_id':uid,'package_sha256':digest((incoming/(uid+'.rldata')).read_bytes()),'package_root_sha256':m['root_sha256'],'resource_profile_id':'controlled-c02','latest_status':'unknown'}
            sha=hub.save_artifact('plans',pid,canonical(plan).encode());hub.commit('plan.create',{'plan_id':pid,'plan_sha256':sha,'public':{}})
            job=hub.create_or_get_job(DataJobCommand('restore',mode,{'plan_id':pid,'plan_sha256':sha}),ctx);calls=[];target=SimpleNamespace(target_id=str(uuid4()),job_id=job['job_id'])
            def allocate(*args):
                hub.commit('target.register',{'target_id':target.target_id,'job_id':job['job_id'],'state':'allocating' if mode=='half_register' else 'allocated'})
                if mode=='half_register':raise OSError('controlled half register')
                if mode=='allocate_deadline':time.sleep(1.1)
                return target
            def seal(*args):
                calls.append('seal');hub.commit('target.seal',{'target_id':target.target_id,'state':'sealed'})
                raise OSError('controlled seal receipt loss')
            factory=SimpleNamespace(allocate=allocate,seal_readonly=seal,abandon=lambda *a:(calls.append('abandon') or True),stop=lambda *a:calls.append('stop'))
            controller=RestoreController(hub,incoming,factory,None,None,limits=Limits(operation_seconds=1 if mode=='allocate_deadline' else 10))
            def load(*args):calls.append('load');return {'counts':{'rows':0}}
            controller._load=load
            with self.assertRaises(Exception):controller.verify(job['job_id'],sha)
            final=hub.get(job['job_id']);self.assertNotEqual(final['state'],'verified')
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
                with self.assertRaises(DataError) as e:runner.run(controller.activate_readonly(job['job_id'],sha,'activate-denied',0))
                self.assertEqual(e.exception.code,'target_not_verified')
            if mode=='allocate_deadline':self.assertNotIn('load',calls);self.assertNotIn('seal',calls)
            cases.append({'case':mode,'final':final,'calls':calls,'activation_authority':False})
        save('09-half-register-seal-deadline',{'layer':'real controller/Hub/ZIP; factory boundaries controlled, not actual PG faults','cases':cases})

    def test_09_actual_reparse_and_external_sentinel(self):
        from app.data_exit.files import safe_root, RootLease
        sentinel=EVIDENCE/'synthetic/sentinel-root'/('outside-'+str(uuid4()));sentinel.mkdir(parents=True)
        link=BASE/('redirect-'+str(uuid4()));package(sentinel/'valid.rldata');(sentinel/'sentinel.bin').write_bytes(b'C02 OUTSIDE SENTINEL\x00\r\n')
        def observed():return {p.name:{'bytes':len(p.read_bytes()),'sha256':digest(p.read_bytes())} for p in sentinel.iterdir() if p.is_file()}
        before=observed();save('10a-external-before',{'directory':str(sentinel),'files':before})
        quote=lambda p:"'"+str(p).replace("'","''")+"'"
        result=subprocess.run(['powershell','-NoProfile','-Command',"$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path "+quote(link)+" -Target "+quote(sentinel)+" | Out-Null"],capture_output=True,timeout=10)
        self.assertEqual(result.returncode,0)
        self.assertTrue(link.lstat().st_file_attributes&0x400)
        codes=[]
        for function in (lambda:safe_root(link),lambda:RootLease(link),lambda:PackageReader(link/'valid.rldata').__enter__()):
            with self.assertRaises(DataError) as error:function()
            codes.append(error.exception.code)
        after=observed();save('10b-external-after',{'directory':str(sentinel),'files':after});self.assertEqual(after,before)
        save('10-real-reparse',{'layer':'actual Windows junction/reparse directory and valid ZIP through redirected parent','link':str(link),
            'reparse_attribute':True,'rejected_codes':codes,'external_sentinel_bytes_and_file_set_unchanged':True,'retained_for_review':True})


if __name__ == '__main__':
    faulthandler.dump_traceback_later(10)
    unittest.main(verbosity=2)
