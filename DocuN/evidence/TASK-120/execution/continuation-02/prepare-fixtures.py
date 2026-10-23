"""Filesystem-only narrowly scoped fixture edits, not candidate execution."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
pending={}
def replace(rel,old,new):
    path=ROOT/rel;body=pending.get(path,path.read_text(encoding='utf-8-sig'))
    assert old in body,(rel,old[:80]);pending[path]=body.replace(old,new)
S='backend/tests/fixtures/task120/setup.py';F='backend/tests/fixtures/task120/flow.py'
replace(S,"slot not in ('flow','budget-01')","slot not in ('flow','budget-01','budget-02')")
replace(S,"('flow' if slot=='flow' else 'budget_01')","slot.replace('-','_')")
replace(S,"    if not (base/'activity.json').exists():", "    if slot=='budget-02':\n        activity['memory_context']={'selected_items':1,'max_memory_bytes':4096,'max_memory_chars':2048,'model_context_tokens':131072,'max_input_tokens_estimate':65536,'protocol_reserve_tokens':1024,'reserved_output_tokens':2048,'safety_tokens':1024,'estimate_policy':'utf8_bytes.v1','model_identity':activity['model_identity']}\n    if not (base/'activity.json').exists():")
replace(S,"original=path.read_bytes();body=original.decode('utf-8-sig')","original=path.read_bytes();body=original.decode('utf-8-sig')\n            if slot=='budget-02':body=body.replace('\\r\\n','\\n')")
replace(S,"if slot=='budget-01':","if slot in ('budget-01','budget-02'):")
replace(S,"messages_for(TemplateContext())[0]['content']]","messages_for(TemplateContext())[0]['content'],'仅低信任背景；不作为资料引用、测量、经历核实或本活动新独立表现。']")
replace(S,"    bundle={'schema':'retrolume.q-root.v2'", "    if slot=='budget-02':\n        expiry='2026-10-19T12:19:22.457756+00:00'\n        if now>=datetime.fromisoformat(expiry):raise RuntimeError('memory_TESTONLY_original_deadline_expired')\n        grant['valid_until_utc']=expiry\n    bundle={'schema':'retrolume.q-root.v2'")
replace(S,"        await ledger.create_activity(ActivitySpec(aid,scope,now+timedelta(hours=24)","""        selection=None
        if slot=='budget-02' and index==1:
            from app.memory.contracts import MemoryCommandInput,MemorySelectionInput
            from app.memory.service import MemoryService
            selected=base/'creation-memory.json'
            if not selected.exists():
                r.write(selected,{'business_key':str(uuid4()),'memory_id':str(uuid4()),'expected_revision':0,'action':'save',
                    'body':{'kind':'preference','title':next(s['filename'] for s in SAMPLES['sources'] if s['alias']=='R'),'text':SAMPLES['inputs']['memory_body']}},private=True)
            command=MemoryCommandInput.model_validate(json.loads(selected.read_text()))
            receipt=await MemoryService(ledger).submit_command(command)
            async def memory_row(connection):
                cursor=await connection.execute('SELECT memory_id::text,version,revision,body_sha256 FROM public.learning_memory_revisions WHERE memory_id=%s AND version=1',(command.memory_id,))
                return await cursor.fetchone()
            row=await ledger._transaction(memory_row)
            selection=MemorySelectionInput(confirmed=True,entries=[dict(row)])
            r.write(r.EVIDENCE/'budget-02-creation-memory-proof.json',{'save_receipt':receipt,'selection':selection.model_dump(),'frozen_memory_text_sha256':raw_digest(SAMPLES['inputs']['memory_body']),'bound_before_activity_creation':True})
        await ledger.create_activity(ActivitySpec(aid,scope,datetime.fromisoformat(grant['valid_until_utc'])""")
replace(S,"max_tool_calls=8,outbound_grant_sha256=digest(grant)))","max_tool_calls=8,outbound_grant_sha256=digest(grant)),memory_selection=selection)")
replace(F,'def run_flow(lane=None,client=None):',"def run_flow(lane=None,client=None,slot='flow'):")
replace(F,"state_file=r.PRIVATE/'flow/flow-progress.json'","state_file=r.PRIVATE/slot/'flow-progress.json'")
replace(F,"application('flow') if client", "application(slot) if client")
replace(F,'        a1,a2,a3=ROSTER','        a1,a2,a3=ROSTER\n        if lane==\'teaching_a3\':a1=a3')
replace(F,"financials('flow')","financials(slot)")
replace(F,"view=c.request('GET',f'/api/activities/{a1}/teaching/workspace');h=view['head']","view=c.request('GET',f'/api/activities/{a1}/teaching/workspace');h=view['head'] or {}")
replace(F,"'expected_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':1,'body':body", "'expected_revision':h.get('revision',0),'expected_goal_version':h.get('goal_version',0),'expected_scope_revision':1,'body':body")
replace(F,"before=c.request('GET',f'/api/activities/{a1}/teaching/workspace')['head']", "before=c.request('GET',f'/api/activities/{a1}/teaching/workspace')['head'] or {'revision':0,'goal_version':0,'goal_record_id':None}")
replace(F,"        if lane in (None,'teaching'):","""        if lane=='teaching_a3':
            if 'c02-a3-goal.done' not in state:
                import psycopg
                with psycopg.connect(setup.dsn(slot)) as db:
                    heads=db.execute('SELECT (SELECT count(*) FROM teaching_heads WHERE activity_id=%s),(SELECT count(*) FROM interview_heads WHERE activity_id=%s)',(a1,a1)).fetchone()
                    activity=db.execute('SELECT deadline_at>CURRENT_TIMESTAMP,requests_reserved<max_requests,cost_reserved_microunits+250000<=max_cost_microunits FROM activities WHERE id=%s',(a1,)).fetchone()
                if heads!=(0,0) or not activity or not all(activity):raise RuntimeError('original_A3_not_a_legal_fresh_teaching_start')
                r.write(r.EVIDENCE/'flow-A3-fresh-head-precondition.json',{'activity_id':a1,'heads':list(heads),'deadline_and_funds_valid':True,'old_A1_untouched':True})
            change_goal('c02-a3-goal',setup.SAMPLES['inputs']['numeric_goal'])
            plan=teach('plan',{'confirmed':True},'c02-a3-plan')
            proposal=next(row['record_id'] for row in plan['record_ids'] if row['kind']=='path_proposal')
            teach('accept_path',{'proposal_record_id':proposal},'c02-a3-accept-path')
            head=c.request('GET',f'/api/activities/{a1}/teaching/workspace')['head']
            teach('exercise',{'confirmed':True,'path_record_id':head['path_record_id'],'node_id':head['node_id'],'purpose':'initial'},'c02-a3-exercise')
        if lane in (None,'teaching'):""")
replace(F,"}-{lane or 'all'}-flow-result.json", "}-{slot}-{lane or 'all'}-flow-result.json")
for path,body in pending.items():path.write_text(body,encoding='utf-8',newline='\n')
print('Saved two fixture changes; no product/test/runtime execution.')
