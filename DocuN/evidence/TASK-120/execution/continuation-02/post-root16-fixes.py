"""Filesystem-only repairs after both roots stopped; do not run business."""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
base=ROOT/'backend/tests/fixtures/task120'
for name in ('setup.py','pg_boundaries.py','integrated.py','recovery.py','recovery_races.py','flow.py','api_runtime.py'):
    path=base/name;pre=HERE/'post-root16-preimage'/name;pre.parent.mkdir(exist_ok=True);assert not pre.exists();shutil.copy2(path,pre)
    body=path.read_text(encoding='utf-8-sig').replace('.read_text()',".read_text(encoding='utf-8')")
    if name=='flow.py':
        old="            value=c.request('POST',path,command)\n            assert value['outbound_approval']"
        new="""            # Reconcile the immutable original key first. A fully cached index
            # is a real terminal receipt and needs no new approval or send.
            value=c.request('GET',path+'/'+command['business_key'],expect=(200,202,404))
            if not value.get('status'):value=c.request('POST',path,command)
            if value.get('status')=='terminal':
                if value.get('terminal_disposition')!='received':raise RuntimeError('retained_retrieval_terminal_not_received')
                state[name+'.done']=value;r.write(state_file,state,private=True);return value
            if value.get('launch_claimed') or value.get('launch_claimed_at') or value.get('status')=='launch_claimed':raise RuntimeError('retained_retrieval_claim_never_resent')
            if not value.get('outbound_approval'):value=c.request('POST',path,command)
            assert value['outbound_approval']"""
        assert old in body;body=body.replace(old,new)
    if name=='api_runtime.py':
        body=body.replace("('status','error_code','operation_id','retry_policy','model_called')","('status','error_code','terminal_disposition','operation_id','retry_policy','model_called')")
        body=body.replace("detail=value.get('detail',value);code=detail.get('code') if isinstance(detail,dict) else 'http_rejected'","detail=value.get('detail',value.get('error',value));code=detail.get('code') if isinstance(detail,dict) else 'http_rejected'")
    path.write_text(body,encoding='utf-8',newline='\n')
body=(HERE/'check-stop.py').read_text(encoding='utf-8').replace("HERE/'entry-stop-proof.json'","HERE/'final-stop-proof.json'")
(HERE/'final-stop-check.py').write_text(body,encoding='utf-8')
body=(HERE/'preflight-040.py').read_text(encoding='utf-8').replace('check-stop-16.py','final-stop-check.py').replace('preflight-040-result.json','preflight-041-result.json')
body=body.replace("proof={'syntax':'PASS'", """from app.memory.contracts import MemoryCommandInput
memory_input=ROOT/'.runtime/TASK-120/budget-02/creation-memory.json'
parsed=MemoryCommandInput.model_validate(json.loads(memory_input.read_text(encoding='utf-8')))
assert parsed.body['text']==__import__('tests.fixtures.task120.setup',fromlist=['SAMPLES']).SAMPLES['inputs']['memory_body']
proof={'UTF8_original_memory_input_schema':'PASS_NO_PG_WRITE','syntax':'PASS'""")
(HERE/'preflight-041.py').write_text(body,encoding='utf-8')
import json
(HERE/'command-041.json').write_text(json.dumps({'label':'scope02-final-offline-syntax-UTF8-and-stop-proof','seconds':60,'cwd':'backend','argv':[str(ROOT/'backend/.venv/Scripts/python.exe'),str(HERE/'preflight-041.py')]}),encoding='utf-8')
print('Saved UTF8/cached-index/diagnostic fixes and final readonly checks; business unexecuted.')
