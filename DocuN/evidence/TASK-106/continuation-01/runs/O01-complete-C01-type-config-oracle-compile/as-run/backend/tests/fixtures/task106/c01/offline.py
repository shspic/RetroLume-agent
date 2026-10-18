"""First actual type/config/oracle/compile check; no real root or old runner."""
import inspect,json,os,secrets
from pathlib import Path
from uuid import uuid4
from pydantic import SecretStr
from .control import ROOT,EVIDENCE,batch,atomic_json,reserve,manifest
from .harness import Harness
from .http import config_value
from .model import response_value
from .samples import *
from app.service_config import load_activity_config
from app.interview.contracts import FeedbackOutput,QuestionOutput,InterviewProfile
from app.capabilities.contracts import ModelCallRequest,ModelServiceConfig
from app.worker.one_call import OneCallInput

def main():
    with batch('O01-complete-C01-type-config-oracle-compile',category='offline_build',count='offline_batch',maximum=180) as out:
        reserve('compile_initial',dict(scope='all changed Python and c01 before first native root'))
        paths=[p for p in manifest() if p.endswith('.py') and (p.startswith('backend/app/') or '/task106/c01/' in p)]
        for p in paths:compile((ROOT/p).read_bytes(),str(ROOT/p),'exec')
        os.environ['RETROLUME_C01_MODEL_KEY']=secrets.token_urlsafe(24);configs={}
        for mode in ('normal','illegal_model','onecall_limit'):
            path=out/(mode+'.json');atomic_json(path,config_value(mode));cfg=load_activity_config(path)
            assert cfg.interview_model_layer.available and cfg.model_service is not None,(mode,cfg.interview_model_layer)
            configs[mode]=dict(available=cfg.interview_model_layer.available,model=cfg.model,max_request_bytes=cfg.model_service.max_request_bytes)
        catalog=[dict(citation_id='ic_'+str(n)*24,text=text,source_id=str(n)) for n,text in ((1,'仅声明不背书。'),(2,SERIAL),(3,TRACE))]
        frozen=dict(catalog=catalog,goal_body=dict(target='余额算法'),action='review',parent_record_refs=[dict(kind='answer',record_id=str(uuid4()),body={'value':{'text':T_ANSWER}})])
        value=response_value(frozen);FeedbackOutput.model_validate(value);assert value['recognitions'][0]['reference_ids']==[catalog[1]['citation_id'],catalog[2]['citation_id']]
        try:response_value({**frozen,'catalog':catalog[:1]})
        except ValueError:pass
        else:raise AssertionError('Fixture pretended support without actual catalog sentence')
        hc=[dict(citation_id='ic_'+'4'*24,text=YEAR_A,source_id='a'),dict(citation_id='ic_'+'5'*24,text='只说冲突未知',source_id='b'),dict(citation_id='ic_'+'6'*24,text=YEAR_B,source_id='b')]
        hv=response_value({**frozen,'catalog':hc,'goal_body':dict(target='史料活动X')});FeedbackOutput.model_validate(hv);assert hv['conflicts'][0]['reference_ids']==[hc[0]['citation_id'],hc[2]['citation_id']]
        profile=InterviewProfile(activity_id=str(uuid4()),business_key=str(uuid4()),action='ask',request_sha256='1'*64,context_sha256='2'*64,expected_head_revision=1,goal_version=1,scope_revision=1,round_index=0,probe_depth=0,goal_record_id=str(uuid4()))
        req=ModelCallRequest(interview_profile=profile,messages=[dict(role='system',content='fixed'),dict(role='user',content='bounded')],max_output_tokens=512)
        service=ModelServiceConfig(provider='deepseek_chat_completions',base_url='https://api.deepseek.com',model='task106-c01-synthetic',api_key=SecretStr('DECLARED-SYNTHETIC'),max_request_bytes=65536,max_response_bytes=65536)
        wire=OneCallInput('int10m.'+profile.business_key.replace('-',''),req,service).to_wire();assert OneCallInput.from_wire(wire).request==req
        atomic_json(out/'preflight.json',dict(compiled=paths,configs=configs,oracle_T=value,oracle_H=hv,old_wrong_fragments_negative=True,complete_wire_bytes=len(json.dumps(wire).encode()),frame_roundtrip=True,fixture_source_only_no_DB_or_authority_mock=True,
            signatures=dict(command=str(inspect.signature(Harness.command)),activity=str(inspect.signature(Harness.activity)))))
        print('C01 all Python compiled, real config variants/type signatures and support selection preflight passed')

if __name__=='__main__':main()
