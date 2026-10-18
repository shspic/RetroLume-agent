"""Two in-memory S transactions exercise the unchanged production global gate, no PG/Q/provider."""
import asyncio,json,sys
print('S06 shared gate: interpreter entered',flush=True)
from pathlib import Path
N=Path(__file__).resolve().parent;ROOT=N.parents[4]
sys.path[:0]=[str(N.parent),str(ROOT/'backend'),str(ROOT/'backend/tests')]
import control as c
print('S06 shared gate: controller imported',flush=True)
from test_step018_flows import adopted_fixture
from app.activities.repository import PostgresAdmissionLedger
from app.capabilities.contracts import AdmissionDenied
entry,manifest,grant,request=adopted_fixture()
print('S06 shared gate: synthetic grant and manifest constructed',flush=True)
class Cursor:
    def __init__(self,row=None,rows=None):self.row,self.rows=row,rows
    async def fetchone(self):return self.row
    async def fetchall(self):return self.rows
async def run():
    lock=asyncio.Lock();budget={'requests':79,'cost':19750000};locks=[]
    class Connection:
        held=False
        async def execute(self,sql,args=None):
            if 'pg_advisory_xact_lock' in sql:
                print('S06 shared gate: waiting shared lock',flush=True)
                await lock.acquire();self.held=True;locks.append(sql);return Cursor()
            if 'source_version_id' in sql:return Cursor(rows=list(manifest.sources))
            if 'outbound_grant_sha256,reserve_cost_microunits' in sql:return Cursor({'outbound_grant_sha256':grant.sha256,'reserve_cost_microunits':250000})
            if 'sum(requests_reserved)' in sql:
                assert args[0]==list(grant.allowed_activity_ids);return Cursor(dict(budget))
            raise AssertionError('unexpected production query')
    ledger=PostgresAdmissionLedger('unused-synthetic-contract-only')
    async def transaction(provider,model):
        connection=Connection()
        try:
            await ledger._outbound_lock(connection,request.activity_id,grant.model_dump(mode='json'),provider,model,100,0,manifest.model_dump(mode='json'))
            await asyncio.sleep(0);budget['requests']+=1;budget['cost']+=250000
            return {'provider':provider,'admitted':True,'synthetic_transport_calls':1}
        except AdmissionDenied as error:return {'provider':provider,'admitted':False,'refusal':str(error),'synthetic_transport_calls':0}
        finally:
            if connection.held:lock.release()
    results=await asyncio.gather(transaction('deepseek_chat_completions','deepseek-chat'),transaction('zhipu_embeddings','embedding-3'))
    assert sum(x['admitted'] for x in results)==1 and budget=={'requests':80,'cost':20000000} and len(set(locks))==1
    c.write(N/'shared-global-budget-concurrency.json',{'sample':c.sample(),'layer':'T: production gate with isolated in-memory transaction/transport; not a real PG race','concurrent_S_operations':2,'results':results,'final_synthetic_budget':budget,'same_production_gate_and_lock':True,'production_gate_sha256':c.sha((ROOT/'backend/app/retrieval/repository.py').read_bytes()),'real_PG_Q_roster_created':0,'real_provider_calls':0,'actual_fee':0,'Q':'NOT_ENABLED','prior_applicable_PG_lock_evidence':'existing G3/G5 and S05 X07 unchanged activity transaction gate'})
    print(json.dumps({'global_gate_two_S_operations':True,'admitted':1,'real_provider':0,'Q_roster_created':0}))
asyncio.run(asyncio.wait_for(run(),timeout=8))
