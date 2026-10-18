"""Reuse every committed core subcase; continue from the fixture barrier miss."""
import asyncio,json,os,sys
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from .control import EVIDENCE,atomic_json
from .harness import Harness
from .http import HTTP,Server
from .core import cancellation_cases
from .samples import T_NAME,T_ANSWER,H_ANSWER

async def run(h):
    original=EVIDENCE/'runs/P01-core-remaining-PG-HTTP-native'
    saved=json.loads((original/'samples-oracle.json').read_text(encoding='utf-8'))['materials'];h.saved=saved
    effects=json.loads((original/'effects.json').read_text(encoding='utf-8'))
    def find(target):return next(x['activity'] for x in effects if x['command']['action']=='start' and x['command']['body']['goal']['target']==target)
    ui=find('余额算法UI历史修订');accepted=find('余额算法accepted原意图');lost=find('余额算法浏览器丢响应')
    for aid,target in ((ui,'余额算法串行覆盖，UI历史修订'),(accepted,'余额算法串行覆盖，accepted原意图'),(lost,'余额算法串行覆盖，浏览器丢响应')):
        await h.command(aid,'goal',{'goal':{'target':target,'material_roles':[dict(source_id=saved[T_NAME]['id'],role='reference')]}})
    oldfailure=effects[-1]['activity']
    with psycopg.connect(h.dsn,row_factory=dict_row) as conn:
        old=conn.execute("SELECT business_key::text,status,context_body::jsonb AS context FROM interview_commands WHERE activity_id=%s AND action='ask' ORDER BY created_at DESC LIMIT 1",(oldfailure,)).fetchone()
    assert old and old['status']=='unknown'
    atomic_json(h.out/'first-fixture-miss-preserved.json',dict(activity=oldfailure,old=old,snapshot=h.snapshot(oldfailure),cause='Cancellation-test target omitted serial/overwrite retrieval terms; actual catalog missed declared support, lowest fixture raised; no payload before_result barrier',no_repeat=True))
    c=await h.make(accepted,'ask',{'mode':'first'});frozen=await h.service._frozen(accepted,c,h.config)
    receipt=await h.ledger.accept_interview_command(accepted,c,frozen);assert not receipt['launch_claimed']
    with Server(h.dsn,h.out):
        http=HTTP(h.out);await cancellation_cases(h,http);http.client.close()
    negative=await h.start([T_NAME],'余额算法串行覆盖，配置反例');before=h.snapshot(negative)
    for mode,code in (('illegal_model','interview_binding_invalid'),('onecall_limit','interview_model_unavailable')):
        with Server(h.dsn,h.out,mode):
            http=HTTP(h.out);command=await h.make(negative,'ask',{'mode':'first'});r=http.request('POST',f'/api/activities/{negative}/interview/commands',json=command.model_dump())
            assert r.status_code in (409,422,503) and r.json()['code']==code,dict(mode=mode,status=r.status_code,body=r.json());http.client.close()
        assert h.snapshot(negative)==before
    seed=dict(technical=ui,lost=lost,accepted=accepted,acceptedCommand=c.model_dump(),acceptedReceipt=receipt,technicalTitle=saved[T_NAME]['title'],materials=saved,Tanswer=T_ANSWER,Hanswer=H_ANSWER)
    atomic_json(h.out/'browser-seed.json',seed);atomic_json(h.out/'resumed-summary.json',dict(all_remaining=True,inherited_root=str(original),no_positive_model_replay=True,source_fingerprint_unchanged=True))

if __name__=='__main__':
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run(Harness(os.environ['C01_ADMIN_DSN'],os.environ['C01_APP_DSN'],Path(os.environ['C01_OUT']))));print('C01 checkpoint continuation completed')
