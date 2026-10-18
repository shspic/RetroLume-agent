"""Continue already-COMMIT P02; zero duplicate model effects/calls."""
import asyncio,json,sys
from .control import EVIDENCE,batch,atomic_json
from .resources import start,stop,runtime
from .core import Harness
from .samples import SAMPLES,T_NAME


async def finish(h,prior):
    aid=prior[0]['aid'];receipt=prior[-1]['receipt'];rid=receipt['record_ids'][0]
    before=h.snapshot(aid);detail=await h.ledger.read_interview_record(aid,rid)
    assert detail['body']['value']['recognitions'][0]['verification_kind']=='source_interpretation',detail
    entry=detail['body']['catalog'][0]
    citation=await h.service.read_citation(aid,rid,entry['citation_id'],detail['view_token']);c=citation['citation']
    atomic_json(h.out/'actual-citation-and-failed-oracle.json',dict(citation=citation,prior_wrong_oracle='first fragment must include initial100',
        exact_slice=SAMPLES[T_NAME][c['start_offset']:c['end_offset']],before=before))
    assert citation['position_verified'] and c['text']==SAMPLES[T_NAME][c['start_offset']:c['end_offset']],('citation actual slice',c)
    history=await h.ledger.read_interview_history(aid)
    assert all(not any(k in r for k in ('payload','local_body','catalog','text')) for r in history['records']),history
    end,command=await h.command(aid,'finish',{})
    assert end['status']=='committed' and end['effect_applied'],end
    again=await h.service.submit_command(aid,command,h.config,run_tag='task106-closed-replay')
    assert again['record_ids']==end['record_ids'],again
    after=h.snapshot(aid)
    assert before['activity']['requests_reserved']==after['activity']['requests_reserved']==2 and len(after['results'])==2,after
    view=await h.ledger.read_interview_workspace(aid);assert view['head']['phase']=='ended',view
    atomic_json(h.out/'history.json',history);atomic_json(h.out/'final-state.json',after)
    atomic_json(h.out/'feedback.json',detail)
    print(json.dumps(dict(resumed=True,model_calls_added=0,technical_chain=True,citation_exact=True,history_metadata=True,ended=True)))


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    prior=json.loads((EVIDENCE/'runs/P02-ordinary-core-first-native/effects.json').read_text(encoding='utf-8'))
    with batch('P03-resume-committed-technical-citation-end') as out:
        try:
            admin=start(1);app,denied=runtime(admin);h=Harness(admin,app,out)
            asyncio.run(finish(h,prior))
        finally:stop(1)


if __name__=='__main__':main()
