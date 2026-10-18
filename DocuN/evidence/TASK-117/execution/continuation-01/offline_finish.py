"""ROOT08原截止内的最后两项纯合同检查与实际导入原件白名单候选；无资源启动。"""
from batch_runtime import *
from types import SimpleNamespace
from uuid import UUID
import sysconfig
from app.capabilities.embedding import OutboundSourceManifest,FROZEN_SAMPLE_SHA
from app.retrieval.evidence import SourceTextUnit,build_fragments
from app.retrieval.service import fragment_manifest

def manifest_candidate():
    samples=json.loads((ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json').read_text(encoding='utf-8'))
    assert c.sha((ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json').read_bytes())==FROZEN_SAMPLE_SHA
    rows={};receipts=[]
    for path in sorted((C01/'root08-inputs').glob('*.json')):
        value=json.loads(path.read_text(encoding='utf-8'));response=value.get('response',{})
        found=response.get('items',[]) if isinstance(response,dict) else []
        if isinstance(response,dict) and isinstance(response.get('material'),dict):found=[*found,response['material']]
        for row in found:
            if isinstance(row,dict) and all(k in row for k in ('id','version_id','revision','sha256','title')):
                rows[row['id']]=row;receipts.append({'receipt':str(path.relative_to(ROOT)),'sha256':c.sha(path.read_bytes())})
    sources=[];fragments=[];bindings=[]
    for sample in samples['sources']:
        row=next((r for r in rows.values() if r['title']==sample['filename'] and r['sha256']==c.sha(sample['text'].encode())),None)
        if row is None:raise RuntimeError('actual_committed_source_mapping_missing:'+sample['alias'])
        sources.append({'source_id':row['id'],'source_version_id':row['version_id'],'source_revision':row['revision'],'original_sha256':row['sha256']})
        unit=SourceTextUnit(row['id'],row['version_id'],row['revision'],None,'original',sample['text'],True)
        wrapper=SimpleNamespace(supplement_id=None,unit=unit,source={'sha256':row['sha256']})
        for fragment in build_fragments(unit):
            item=fragment_manifest(fragment,wrapper);fragments.append({k:item[k] for k in ('identity_sha256','input_sha256')})
        bindings.append({'alias':sample['alias'],**sources[-1]})
    keys=('numeric_goal','concept_goal','ambiguous_goal','ambiguous_clarification','no_evidence_query','conflict_query','interview_goal','numeric_initial_question','targeted_question','retest_question')
    queries=[samples['inputs'][key] for key in keys]+['平均速度 分钟换秒 米每秒','虚构接口 缓存路径 个人分工 合成测量 耗时']
    from app.retrieval.contracts import digest
    manifest=OutboundSourceManifest.model_validate_json(json.dumps({'frozen_samples_sha256':FROZEN_SAMPLE_SHA,'sources':sources,'fragments':fragments,'query_input_sha256':sorted({digest(q) for q in queries})}))
    c.write(C01/'actual-source-manifest.candidate.json',manifest.model_dump(mode='json'))
    c.write(C01/'actual-source-manifest.candidate-receipt.json',{'sample':c.sample(),'status':'PROPOSED_NOT_ADOPTED_Q_NOT_ENABLED','manifest_canonical_sha256':manifest.sha256,'actual_committed_text_sources':bindings,'receipt_bindings':receipts,'PDF':'excluded until real HTTP review succeeds','query_scope':'仅已列必要问题；最终Q实际query须再采用，未放行任意输入','provider_calls':0,'actual_fee':0,'grant_signed_or_activated':False})

def main():
    root=next(r for r in c.state()['roots'] if r['id']==8)
    if time.monotonic_ns()>=root['business_deadline_mono_ns']:raise RuntimeError('ROOT08_original_deadline_closed')
    start=c.sample();env=dict(os.environ);env['PYTHONPATH']=os.pathsep.join([str(ROOT/'backend'),str(ROOT/'backend/tests'),str(ROOT/'backend/tests/fixtures/step018'),sysconfig.get_paths()['purelib']])
    methods=['test_step018_flows.IntegrationContractTests.'+x for x in ('test_workflow_budget_refuses_before_retrieval_insert','test_both_provider_prefixes_share_fixed_global_request_and_cost_gate')]
    result=subprocess.run([sys._base_executable,'-X','utf8','-m','unittest',*methods,'-v'],env=env,cwd=ROOT,capture_output=True,timeout=30)
    path=C01/('offline-final-'+str(start['mono_ns'])+'.txt');path.write_bytes(result.stdout+result.stderr)
    value=c.state();end=c.sample();value['offline_intervals'].append({'root':8,'segment':value['active_segment'],'start_mono_ns':start['mono_ns'],'end_mono_ns':end['mono_ns'],'seconds':(end['mono_ns']-start['mono_ns'])/1e9,'basis':'原ROOT08内两项新增协议门反例，未启动PG/API/browser/preview，不冒真实PG并发'})
    c.write(EXEC/'budget.json',value)
    if result.returncode:raise RuntimeError('offline_final_failed_read_exact_log')
    manifest_candidate()
    c.write(C01/'offline-final-receipt.json',{'sample':c.sample(),'methods':2,'result':'passed','layer':'pure_contract_with_connection_double','PG_concurrency':'NOT_RUN','Q_roster_activities_created':0,'resources_started':0,'as_run':{p:c.sha((ROOT/p).read_bytes()) for p in ('backend/app/retrieval/repository.py','backend/app/capabilities/embedding.py','backend/tests/test_step018_flows.py')}})
    print('Two new pure gates passed; actual committed eight-source manifest candidate saved; Q remains disabled')

if __name__=='__main__':main()
