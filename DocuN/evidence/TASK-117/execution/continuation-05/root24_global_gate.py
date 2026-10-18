"""Distinguishing PG lock check with isolated synthetic budget: no Q roster or target writes."""
from batch_runtime import *
from profiles_batch import factory_profile,Hooks
from app.data_exit.control import ControlHub
from app.data_exit.restore import TargetFactory
from app.activities.repository import PostgresAdmissionLedger
from app.capabilities.contracts import AdmissionDenied
from app.runtime import psycopg_compatible_loop_factory
import asyncio,psycopg
sys.path.insert(0,str(ROOT/'backend/tests'))
from test_step018_flows import adopted_fixture
class Cursor:
    def __init__(self,row=None,rows=None):self.row,self.rows=row,rows
    async def fetchone(self):return self.row
    async def fetchall(self):return self.rows
async def check(dsn):
    _,manifest,grant,request=adopted_fixture();budget={'requests':79,'cost':19750000};locks=[]
    ledger=PostgresAdmissionLedger('unused-no-Q-ledger-rows')
    class Proxy:
        def __init__(self,connection,pid):self.connection,self.pid=connection,pid
        async def execute(self,query,args=None):
            if 'pg_advisory_xact_lock' in query:
                begin=time.monotonic_ns();result=await self.connection.execute(query,args);locks.append({'backend_pid':self.pid,'sql':query,'begin_ns':begin,'acquired_ns':time.monotonic_ns()});return result
            if 'source_version_id' in query:return Cursor(rows=list(manifest.sources))
            if 'outbound_grant_sha256,reserve_cost_microunits' in query:return Cursor({'outbound_grant_sha256':grant.sha256,'reserve_cost_microunits':250000})
            if 'sum(requests_reserved)' in query:
                assert args[0]==list(grant.allowed_activity_ids);return Cursor(dict(budget))
            raise AssertionError('unexpected query; no target write permitted')
    ready=asyncio.Event();arrivals=0
    async def transaction(provider,model):
        nonlocal arrivals
        async with await psycopg.AsyncConnection.connect(dsn) as connection:
            async with connection.transaction():
                await connection.execute('SET TRANSACTION READ ONLY')
                cursor=await connection.execute('SELECT pg_backend_pid(),current_setting(\'transaction_read_only\')');pid,readonly=await cursor.fetchone();assert readonly=='on'
                arrivals+=1
                if arrivals==2:ready.set()
                await ready.wait()
                try:
                    await ledger._outbound_lock(Proxy(connection,pid),request.activity_id,grant.model_dump(mode='json'),provider,model,100,0,manifest.model_dump(mode='json'))
                    await asyncio.sleep(.08);budget['requests']+=1;budget['cost']+=250000
                    return {'provider':provider,'admitted':True,'synthetic_transport_calls':1,'backend_pid':pid}
                except AdmissionDenied as error:return {'provider':provider,'admitted':False,'reason':str(error),'synthetic_transport_calls':0,'backend_pid':pid}
    results=await asyncio.wait_for(asyncio.gather(transaction('deepseek_chat_completions','deepseek-chat'),transaction('zhipu_embeddings','embedding-3')),timeout=15)
    assert sum(x['admitted'] for x in results)==1 and budget=={'requests':80,'cost':20000000}
    assert len({x['backend_pid'] for x in locks})==2 and len({x['sql'] for x in locks})==1
    c.write(C01/'shared-global-budget-PG-lock.json',{'sample':c.sample(),'layer':'real PG transaction advisory lock with isolated in-memory S budget/manifest/grant/transport; not real outbound admission or PG business/Q rows','same_unchanged_production_gate':True,'production_sha256':c.sha((ROOT/'backend/app/retrieval/repository.py').read_bytes()),'results':results,'budget':budget,'locks':locks,'real_PG_connections':2,'read_only_transactions':True,'target_SQL_writes':0,'Q_roster_rows_created':0,'real_provider_calls':0,'actual_fee':0})
def main():
    preflight('S06-global-PG-lock-distinction')
    with Batch(24,'S06-R02-formal-selector-and-reopen') as batch:
        hub=ControlHub(EXEC/'synthetic/source-control');selection=hub.state()['selection'];assert selection['target_id']=='634aa034-51f6-4510-b075-38cb005481d8'
        factory=TargetFactory(hub,EXEC/'synthetic/source-restore',factory_profile());factory.hooks=Hooks(batch.run,factory);target=factory.target(selection['target_id'])
        batch.run.register('same-permanent-readonly-R02',lambda:factory.stop(target),priority=0)
        batch.run.register('source-hub-lock',hub.lock.close,priority=1);batch.run.register('source-operation-lock',hub.operation_lock.close,priority=1)
        factory.start(target);credentials=factory.readonly_credentials(target.target_id);factory._wait_pg(credentials['readonly_dsn'])
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(check(credentials['readonly_dsn']))
        credentials.clear();assert hub.state()['selection']==selection
if __name__=='__main__':main()
