"""最后许可根：无API/Browser/Native，仅单PG定向门、删源与R02隔离恢复。"""
from batch_runtime import *
from pg_remaining import *
from http_remaining import case
from final_restore import final_restore

def read_r02(run):
    receipt=json.loads((C01/'final-r02-verified.json').read_text())['receipt']
    from app.data_exit.control import ControlHub
    from app.data_exit.restore import TargetFactory
    hub=ControlHub(EXEC/'synthetic/source-control');factory=TargetFactory(hub,EXEC/'synthetic/source-restore',factory_profile())
    target=factory.target(receipt['target_id']);hooks=Hooks(run,factory);factory.hooks=hooks;hooks.targets['r02']=target
    slot=next(s for s in factory.profile['slots'] if s['id']=='r02');run.register('verified-r02-readback',lambda:hooks.close_slot(slot),priority=0)
    factory.start(target)
    try:
        credentials=factory.readonly_credentials(target.target_id)
        with psycopg.connect(credentials['readonly_dsn'],row_factory=dict_row) as db:
            proof=verify_readonly_target(db,R02);proof['retrieval']=verify_persistent_retrieval(db)
            try:db.execute('UPDATE activities SET requests_reserved=requests_reserved')
            except psycopg.Error as exc:assert exc.sqlstate=='42501';db.rollback();proof['write_refused_SQLSTATE']=exc.sqlstate
            else:raise AssertionError('sealed target write accepted')
        return {**proof,'target_id':target.target_id,'cid':target.cid,'application_view':'NOT_RUN','source_selection':hub.state()['selection']}
    finally:factory.stop(target)

def main():
    preflight('root13')
    with Batch(13,'ROOT13-PG-only-boundary-and-isolated-R02') as batch:
        c.write(C01/('root13-as-run-'+batch.id+'.json'),{'sample':c.sample(),'files':{p:c.sha((ROOT/p).read_bytes()) for p in json.loads((C01/'changes.json').read_text()) if (ROOT/p).is_file()},'helpers':{p.name:c.sha(p.read_bytes()) for p in C01.glob('*.py')},'HTTP_API_browser_Native_starts':0})
        rc.start_pg('source');runtime=runtime_config(batch.run)
        mapping=json.loads((C01/'frozen-source-bindings.json').read_text())
        for name,operation in [('X03-X07-real-PG-only',lambda:run_async(budget_keys(runtime,mapping))),('X02-real-PG-local-memory',lambda:run_async(memory_changes(runtime,mapping))),('X10-real-PG-delete-source',lambda:run_async(delete_source(runtime)))]:
            batch.run.check();case(name,operation,layer='real PG and original product services; no HTTP/Browser/Native')
        batch.run.check();restored=case('P03-final-R02-and-failed-hash-target',lambda:final_restore(batch.run),layer='real PG/Docker isolated restore; no application viewer')
        if restored:
            batch.run.check();case('P03-R02-real-readonly-readback',lambda:read_r02(batch.run),layer='real sealed PG readonly SQL; application viewer NOT_RUN')
    print('ROOT13 PG-only work saved; every owned PG stopped; no API/browser/Native started')

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        c.failure('S02-ROOT13',type(exc).__name__+':'+str(exc)[:300],effect='最后S根原有界清场；不再新开S根，不降内存/权限/验收')
        (C01/('root13-error-'+str(time.time_ns())+'.txt')).write_text(traceback.format_exc(),encoding='utf-8');raise
