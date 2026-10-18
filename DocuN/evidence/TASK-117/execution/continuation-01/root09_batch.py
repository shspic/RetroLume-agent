"""低内存串行原目标：实际冻结文本、两链、下一批同库重开的基线。"""
from batch_runtime import *
from root08_batch import build,memory_teaching,unknown_before_reopen
from frozen_http import FrozenFlow
import traceback,unittest,io

def focused():
    sys.path.insert(0,str(ROOT/'backend/tests'))
    start=c.sample();stream=io.StringIO()
    methods=['test_lifecycle.CleanupTests.'+x for x in ('test_memory_pressure_closes_consumers_before_pg_without_new_command','test_unknown_memory_fails_closed_and_still_cleans')]
    methods+=['test_step018_flows.IntegrationContractTests.'+x for x in ('test_workflow_budget_refuses_before_retrieval_insert','test_both_provider_prefixes_share_fixed_global_request_and_cost_gate')]
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(methods))
    (C01/'low-memory/focused.txt').write_text(stream.getvalue(),encoding='utf-8')
    value=c.state();end=c.sample();value['offline_intervals'].append({'root':9,'segment':value['active_segment'],'start_mono_ns':start['mono_ns'],'end_mono_ns':end['mono_ns'],'seconds':(end['mono_ns']-start['mono_ns'])/1e9,'basis':'两项新增压力闭包与两项纯合同负例；资源启动前'})
    c.write(EXEC/'budget.json',value)
    if not result.wasSuccessful():raise RuntimeError('new_focused_methods_failed_read_log')
    from offline_finish import manifest_candidate
    manifest_candidate()

def baseline(filename='before-normal-reopen-pg.json'):
    import psycopg
    from psycopg.rows import dict_row
    from app.retrieval.repository import plain
    with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:
        data={name:db.execute(query).fetchall() for name,query in {
          'activities':'SELECT id::text,status,execution_generation,requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds,running_settled_seconds FROM public.activities ORDER BY id',
          'unknown':"SELECT activity_id::text,operation_id,admission_id::text,state,reserved_cost_microunits,disposition FROM public.activity_operations WHERE state='unknown' ORDER BY activity_id,operation_id",
          'teaching_heads':'SELECT * FROM public.teaching_heads ORDER BY activity_id',
          'interview_heads':'SELECT * FROM public.interview_heads ORDER BY activity_id',
          'memory_choices':'SELECT activity_id,memory_id,version,selected_revision,body_sha256 FROM public.activity_memory_choices ORDER BY activity_id,ordinal'}.items()}
        c.write(C01/filename,plain(data))

def main():
    preflight('root09',preview=True)
    with Batch(9,'ROOT09-low-memory-frozen-chains') as batch:
        focused();build()
        c.write(C01/('root09-as-run-'+batch.id+'.json'),{'sample':c.sample(),'files':{p:c.sha((ROOT/p).read_bytes()) for p in json.loads((C01/'changes.json').read_text()) if (ROOT/p).is_file()},'node_script_sha256':c.sha((ROOT/'frontend/tests/step018-flow.mjs').read_bytes())})
        rc.start_pg('source');batch.start_api()
        flow=FrozenFlow('root09-inputs')
        try:
            mapping,memory=flow.prepare(pdf=False)
            for name,action in [('memory_teaching',lambda:memory_teaching(flow,mapping,memory)),('unknown',lambda:unknown_before_reopen(flow,mapping))]:
                try:action()
                except Exception as exc:
                    c.failure('S02-ROOT09-'+name,type(exc).__name__+':'+str(exc)[:300],effect='原回执保存；不自动重发；继续独立浏览器目标')
                    (C01/(name+'-failure.txt')).write_text(traceback.format_exc(),encoding='utf-8')
        finally:flow.close()
        try:
            proof=batch.start_browser('before-restart')
            c.write(C01/'before-reopen-browser.json',proof)
        finally:baseline()
    print('ROOT09 finished; all owned resources stopped; exact receipts saved')

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        c.failure('S02-ROOT09',type(exc).__name__+':'+str(exc)[:300],effect='低内存原闭包清场；原失败与累计预算保留')
        (C01/('root09-error-'+str(time.time_ns())+'.txt')).write_text(traceback.format_exc(),encoding='utf-8');raise
