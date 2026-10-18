"""正式bundle与冻结两链；两域回答留在同normal库供下一批正常重开后显式反馈。"""
from batch_runtime import *
from frozen_http import FrozenFlow,SAMPLES
import traceback

def build():
    marker=C01/'bundle-4.json'
    if marker.exists():
        manifest=json.loads(marker.read_text())
        if any(not(ROOT/r['path']).is_file() or c.sha((ROOT/r['path']).read_bytes())!=r['sha256'] for r in manifest['files']):raise RuntimeError('saved_bundle_drift')
        return
    for path in (ROOT/'frontend/dist').rglob('*'):
        if path.is_file():c.pre(path.relative_to(ROOT).as_posix())
    c.count('frontend_builds')
    result=subprocess.run(['cmd','/d','/c','npm.cmd','run','build'],cwd=ROOT/'frontend',capture_output=True,timeout=180)
    (C01/'build-4.log').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('formal_build_failed')
    files=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())} for p in sorted((ROOT/'frontend/dist').rglob('*')) if p.is_file()]
    c.write(marker,{'attempt':4,'sample':c.sample(),'files':files,'vite_server':False})

def memory_teaching(flow,mapping,memory):
    marker=C01/'memory-teaching-before-reopen.json'
    if marker.exists():return json.loads(marker.read_text())
    aid=flow.create([mapping['N']],memory);flow.index(aid)
    w=flow.teaching(aid,'goal',{'goal':SAMPLES['inputs']['numeric_goal']})
    w=flow.teaching(aid,'plan',{'confirmed':True})
    w=flow.teaching(aid,'accept_path',{'proposal_record_id':w['proposal']['record_id']})
    w=flow.teaching(aid,'select_node',{'path_record_id':w['head']['path_record_id'],'node_id':'n1'})
    w=flow.teaching(aid,'exercise',{'confirmed':True,'path_record_id':w['head']['path_record_id'],'node_id':'n1','purpose':'initial'})
    w=flow.teaching(aid,'answer',{'exercise_record_id':w['head']['exercise_record_id'],'kind':'initial','text':SAMPLES['inputs']['numeric_positive_answers'][0]})
    value={'activity_id':aid,'workspace':w,'memory_id':memory['memory_id'],'phase':'answer_saved_before_normal_reopen'}
    c.write(marker,value);return value

def unknown_before_reopen(flow,mapping):
    marker=C01/'unknown-before-normal-reopen.json'
    if marker.exists():return
    aid=flow.create([mapping['N-CONFLICT']]);flow.index(aid)
    query='S02合成超时';key=__import__('uuid').uuid4()
    c.write(C01/'unknown-fault-input-before-send.json',{'activity_id':aid,'business_key':str(key),'query_sha256':c.sha(query.encode()),'synthetic_only':True,'actual_fee':0})
    receipt=flow.call('POST',f'/api/activities/{aid}/retrieval/commands',{'business_key':str(key),'action':'query','expected_scope_revision':1,'expected_domain_revision':0,'query':query,'confirmed':True},native=1)
    assert receipt['terminal_disposition']=='unknown',receipt
    c.write(marker,{'activity_id':aid,'source_id':mapping['N-CONFLICT']['id'],'query_key':str(key),'receipt':receipt})

def main():
    preflight('root08',preview=True)
    with Batch(8,'ROOT08-final-bundle-frozen-inputs-two-chains-before-normal-reopen') as batch:
        test_start=c.sample()
        env=dict(os.environ);env['PYTHONPATH']=os.pathsep.join(str(ROOT/p) for p in ('backend','backend/tests','backend/tests/fixtures/step018'))
        methods=['test_step018_flows.IntegrationContractTests.'+x for x in ('test_grant_expiry_after_admission_prevents_dispatch','test_frozen_numeric_variants_and_safe_preview_descriptor','test_frozen_concept_program_and_neutral_output_shapes')]
        prior=list(C01.glob('root08-focused-*.txt'))
        if not any(b'\nOK\n' in p.read_bytes().replace(b'\r\n',b'\n') for p in prior):
            result=subprocess.run([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8','-m','unittest',*methods,'-v'],cwd=ROOT,env=env,capture_output=True,timeout=40)
            (C01/('root08-focused-'+batch.id+'.txt')).write_bytes(result.stdout+result.stderr)
            stamp=c.sample();value=c.state();value['offline_intervals'].append({'root':8,'start_mono_ns':test_start['mono_ns'],'end_mono_ns':stamp['mono_ns'],'seconds':(stamp['mono_ns']-test_start['mono_ns'])/1e9,'segment':value['active_segment'],'basis':'真实资源前3个新增定向方法'});c.write(EXEC/'budget.json',value)
            if result.returncode:raise RuntimeError('focused_final_contracts_failed')
        build()
        binding={p:c.sha((ROOT/p).read_bytes()) for p in json.loads((C01/'changes.json').read_text()) if (ROOT/p).is_file() and not p.startswith('frontend/dist/')}
        c.write(C01/('root08-as-run-'+batch.id+'.json'),{'sample':c.sample(),'files':binding,'node_script':c.sha((ROOT/'frontend/tests/step018-flow.mjs').read_bytes())})
        rc.start_pg('source');batch.start_api()
        flow=FrozenFlow('root08-inputs')
        try:
            mapping,memory=flow.prepare()
            memory_teaching(flow,mapping,memory)
            unknown_before_reopen(flow,mapping)
        finally:flow.close()
        proof=batch.start_browser('before-restart')
        c.write(C01/'before-reopen-browser.json',proof)
        # 原model unknown预留、两域回答/heads与四账的实际同库基线。
        import psycopg
        from psycopg.rows import dict_row
        from app.retrieval.repository import plain
        with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:
            c.write(C01/'before-normal-reopen-pg.json',plain({'activities':db.execute('SELECT id::text,status,execution_generation,requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds,running_settled_seconds FROM public.activities ORDER BY id').fetchall(),
              'unknown':db.execute("SELECT activity_id::text,operation_id,admission_id::text,state,reserved_cost_microunits,disposition FROM public.activity_operations WHERE state='unknown' ORDER BY activity_id,operation_id").fetchall(),
              'teaching_heads':db.execute('SELECT * FROM public.teaching_heads ORDER BY activity_id').fetchall(),
              'interview_heads':db.execute('SELECT * FROM public.interview_heads ORDER BY activity_id').fetchall(),
              'memory_choices':db.execute('SELECT activity_id,memory_id,version,selected_revision,body_sha256 FROM public.activity_memory_choices ORDER BY activity_id,ordinal').fetchall()}))
    print('ROOT08: final bundle and frozen answers saved; own resources stopped before normal reopen')

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        c.failure('S02-ROOT08',type(exc).__name__+':'+str(exc)[:300],effect='精确有界清场；保留COMMIT与新旧业务键，从未完成处继续，不自动再发')
        path=C01/('root08-error-'+str(time.time_ns())+'.txt');path.write_text(traceback.format_exc(),encoding='utf-8');raise
