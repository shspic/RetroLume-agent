"""真实只读 handler 的删除依赖反例；查询结果受控，不冒 PG 运行。"""
import asyncio
from contextlib import contextmanager
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID,uuid4
import zipfile
from bootstrap import ROOT,AUDIT,save
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.api import saved_records
from app.data_exit.contracts import DataContext,canonical,digest
from app.data_exit.repository import DataRepository
from app.data_exit.schema import COLUMNS
from offline_cases import request

def main():
    package=ROOT/'DocuN/evidence/TASK-114/synthetic/backup-root/packages/737bf7ba-18c2-436c-a011-3aabbc1a8b2b.rldata'
    package_sha=digest(package.read_bytes())
    assert package_sha=='45177d58ea58fcaa704bfdd48641aceade7ca6e6f4fe5d6759b3a46bf2671665'
    with zipfile.ZipFile(package) as archive:
        def rows(table):return [json.loads(x) for x in archive.read('records/'+table+'.jsonl').splitlines()]
        head=next(r for r in rows('learning_memories') if r['state']=='active')
        row=next(r for r in rows('learning_memory_revisions') if r['memory_id']==head['memory_id'] and r['version']==head['current_version'])
        body=next(r['body'] for r in rows('learning_memory_bodies') if r['memory_id']==head['memory_id'] and r['version']==row['version'])
        dependency=next(r for r in rows('learning_memory_dependencies') if r['memory_id']==head['memory_id'] and r['version']==row['version'] and r['dependency_kind']=='source')
    memory_id,source_id,version_id=head['memory_id'],dependency['source_id'],dependency['source_version_id']
    save('offline/readonly-projection-input-02.json',{'package_sha256':package_sha,'memory_id':memory_id,'version':row['version'],'source_id':source_id,'body_sha256':digest(body)})
    queries=[]
    class Result:
        def __init__(self,value):self.value=value
        def fetchall(self):return self.value
        def fetchone(self):return self.value
    class Connection:
        def execute(self,query,*args):
            queries.append(query)
            if 'FROM public.learning_memory_revisions' in query:return Result([row])
            if 'SELECT state FROM public.learning_memories' in query:return Result({'state':'active'})
            if 'SELECT body FROM public.learning_memory_bodies' in query:return Result({'body':body})
            if "entity_kind='memory'" in query:return Result({'revoked':False})
            raise AssertionError(query)
    @contextmanager
    def connection(self,**kwargs):yield Connection()
    context=DataContext(str(uuid4()),1,str(uuid4()),str(uuid4()),'restored_readonly')
    value=SimpleNamespace(context=lambda:context)
    req=request(value);req.app.state.activities_ledger=SimpleNamespace(_dsn='task115_controlled_query_fixture')
    async def direct_read(function,*args,**kwargs):
        # 前一异步线程转移方法在沙箱超时；本次只同步执行其原 read 闭包。
        return function(*args,**kwargs)
    with patch.object(DataRepository,'connection',connection),patch('app.data_exit.api.run_in_threadpool',direct_read):
        result=asyncio.run(saved_records(req,'memories',0))
    observed=result['items'][0]
    evidence={'layer':'真实 saved_records handler 内原 read 闭包/codec 同步执行；DB 查询受控，未连 PG，未证线程池运行',
      'sample_identity':{'package_sha256':package_sha,'row_and_body':'原已成功真实恢复的合法 active memory 当前版本，字节不改'},
      'premise':{'memory_head_state':'active','memory_body_present':True,'memory_tombstone':False,
         'source_dependency':dependency,
         'source_tombstone_present':True,'source_current_version':None,
         'premise_reason':'source deletion retains memory head/body/history and makes material pointer unavailable; no automatic revoke'},
      'expected_current_availability':'source_deleted_or_dependency_invalid','expected_body':None,
      'observed':observed,'queries':queries,'dependency_or_source_qualification_queried':False,
      'defect_observed':observed['availability']=='present' and observed['record']['body']==body}
    save('offline/readonly-projection-counterexample-02.json',evidence)
    assert evidence['defect_observed']
    print(json.dumps({'defect_observed':True,'queries':len(queries),'real_pg':False}))

if __name__=='__main__':main()
