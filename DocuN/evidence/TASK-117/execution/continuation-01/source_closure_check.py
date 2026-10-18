"""停机后的必要源码/可信DDL一致性检查；不执行SQL，不创建资源。"""
from pathlib import Path
import sys,json,re,ast,io,unittest,time
C01=Path(__file__).resolve().parent;EXEC=C01.parent;ROOT=EXEC.parents[3]
sys.path[:0]=[str(EXEC),str(ROOT/'backend'),str(ROOT/'backend/tests/fixtures/step018')]
import control as c
from app.data_exit.schema_profiles import get_profile,check_extra_shape,EXTRA_FUNCTIONS,MIGRATION_014,R02
from app.data_exit.contracts import PROFILE,DataError,canonical,digest

def main():
    start=c.sample();c.guard();assert c.state()['active_root'] is None
    folder=C01/'ordinary-db-fixes';adopted=json.loads((folder/'adoption.json').read_text());derived=json.loads((folder/'derived-shape.json').read_text())
    sql=(ROOT/'backend/migrations/014_step018_retrieval.sql').read_text()
    assert MIGRATION_014==c.sha((ROOT/'backend/migrations/014_step018_retrieval.sql').read_bytes())==adopted['new_migration_014_sha256']
    check_extra_shape(derived['shape'])
    old=json.loads((EXEC/'r02-frozen-catalog.json').read_text())
    try:check_extra_shape(old['shape'])
    except DataError as exc:assert exc.code=='data_schema_not_ready'
    else:raise AssertionError('old uncorrected DB silently accepted')
    body=re.search(r'CREATE FUNCTION public\.retrieval_chunk_guard\(\).*?AS\s+(\$\w*\$)(.*?)\1;',sql,re.S).group(2)
    assert digest(re.sub(r'\s+','',body))==EXTRA_FUNCTIONS['retrieval_chunk_guard']
    legacy=get_profile(PROFILE).migration_chain
    for name,sha in legacy.items():assert c.sha((ROOT/'backend/migrations'/name).read_bytes())==sha
    from synthetic_replies import reply
    from app.learning.teaching_contracts import parse_teaching_output
    samples=json.loads((ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json').read_text());mapping={x['alias']:x for x in samples['sources']}
    evidence=[{'id':'lc_'+str(i)*24,'text':mapping[name]['text'],'source':mapping[name]['filename']} for i,name in [(1,'N'),(2,'N-CONFLICT')]]
    output=reply({'messages':[{'role':'user','content':json.dumps({'goal':samples['inputs']['conflict_query'],'evidence':evidence,'task':{'kind':'plan'}},ensure_ascii=False)}]})
    parsed=parse_teaching_output(json.dumps(output,ensure_ascii=False),'plan');assert parsed['result_type']=='conflict'
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(['test_lifecycle.CleanupTests.test_deadline_cleans_every_resource_without_new_command']))
    (C01/'source-closure-deadline.txt').write_text(stream.getvalue(),encoding='utf-8');assert result.wasSuccessful()
    for path in list((ROOT/'backend/app').rglob('*.py')):
        # Parse only registered task edits, not the whole repo's unrelated working files.
        if path.relative_to(ROOT).as_posix() in json.loads((C01/'changes.json').read_text()):ast.parse(path.read_text(encoding='utf-8-sig'))
    end=c.sample();c.write(C01/'source-closure-check.json',{'start':start,'end':end,'passed':['corrected 014 file digest','controlled derived R02 shape','old DB shape rejected','corrected function identity','001..013 exact bytes unchanged','frozen conflict protocol shape','final controller deadline test','registered Python edit AST'],'SQL_executed':False,'PG_APIs_started':0,'DDL_runtime_verification':'NOT_RUN','old_as_run_evidence_not_upgraded':True})
    value=c.state();value['offline_intervals'].append({'root':None,'segment':value['active_segment'],'start_mono_ns':start['mono_ns'],'end_mono_ns':end['mono_ns'],'seconds':(end['mono_ns']-start['mono_ns'])/1e9,'basis':'最终源码/可信DDL推导一致性与现有截止方法必要复检；没有PG/SQL/Browser/Native'})
    c.write(EXEC/'budget.json',value);print('Source/DDL identity and final deadline checks passed; SQL execution NOT_RUN')

if __name__=='__main__':main()
