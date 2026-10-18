"""原CID上仅更新本卡已注册014函数；保留初版as-run与失败，不重建资源。"""
import json,re,sys
from control import HERE,ROOT,guard,event,write,sha,state
from runtime_control import dsn,metadata,PG_IMAGE
sys.path.insert(0,str(ROOT/'backend'))
import psycopg
from psycopg.rows import dict_row
from app.data_exit.contracts import digest
guard()
source=(ROOT/'backend/migrations/014_step018_retrieval.sql').read_text(encoding='utf-8')
statements={}
for match in re.finditer(r'CREATE(?: OR REPLACE)? FUNCTION public\.([a-z_]+)\(.*?\bAS\s*\$([a-z_]+)\$(.*?)\$\2\$;',source,re.S):
    statements[match[1]]=(match.group(0).replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1),digest(re.sub(r'\s+','',match[3])))
frozen=json.loads((HERE/'r02-frozen-catalog.json').read_text(encoding='utf-8'))
before={r['proname']:digest(re.sub(r'\s+','',r['prosrc'])) for r in frozen['shape']['functions']}
for slot in ('source','compat'):
    row=next(r for r in state()['resources'] if r['id']=='pg-'+slot);actual=metadata(row['cid'])
    if actual['image']!=PG_IMAGE or not actual['running'] or actual['labels'].get('retrolume.task')!='TASK-117':raise RuntimeError('exact_cid_not_live')
    with psycopg.connect(dsn(slot,'admin'),row_factory=dict_row) as connection:
        if connection.execute("SELECT EXISTS(SELECT 1 FROM activities WHERE running_reserved_seconds>0 OR lease_expires_at>CURRENT_TIMESTAMP) AS busy").fetchone()['busy']:raise RuntimeError('must_stop_native_before_function_repair')
        for name,(statement,expected) in statements.items():
            raw=connection.execute("SELECT p.prosrc FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname=%s",(name,)).fetchone()
            current=digest(re.sub(r'\s+','',raw['prosrc']))
            if current==expected:continue
            if current!=before.get(name):raise RuntimeError('function_drift:'+name)
            event('014_function_forward_repair',slot=slot,cid=row['cid'],function=name,pre_sha=current,post_sha=expected)
            connection.execute(statement)
print('Only changed014 function updated transactionally on two exact CIDs')
