"""TASK118 有限 JSON/AST 补定位及只读冻结复核；不导入产品。"""
import ast, copy, datetime as dt, hashlib, json, re, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
root=Path('D:/shspic/project_NO3_RetroLume-agent'); out=root/'DocuN/evidence/TASK-118/audit'; e=root/'DocuN/evidence/TASK-117/execution'
start=time.perf_counter(); accesses=[]
def raw(p):
    b=p.read_bytes(); accesses.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}); return b
def load(p): return json.loads(raw(p).decode('utf-8-sig'))
def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
mode=sys.argv[1]
if mode=='cross':
    constants={}
    for n in ast.parse(raw(root/'backend/app/data_exit/schema_profiles.py').decode('utf-8-sig')).body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try: constants[n.targets[0].id]=ast.literal_eval(n.value)
            except (TypeError,ValueError): pass
    v=load(e/'continuation-02/source-SQL-after.json'); shape=copy.deepcopy(v['shape'])
    for row in shape.get('columns',[]):
        if row['relname']=='activities' and row['attname']=='outbound_grant_sha256' and row.get('owner_super') is True: row['owner']='bootstrap_owner'
    for section in ('columns','table_acl','functions'):
        for row in shape.get(section,[]):
            if row.get('acl'): row['acl']=re.sub(r'/[^,}]+','/trusted_owner',row['acl'])
    sh=hashlib.sha256(canon(shape).encode()).hexdigest()
    commands=[]
    for p in sorted((e/'continuation-02/root16-normal').glob('*.json')):
        v=load(p)
        if v.get('method')!='POST': continue
        r=v.get('response',{}); req=v.get('request') or {}
        commands.append({'raw_file':str(p),'path':v.get('path'),'http_status':v.get('status'),'action':req.get('action'), 'business_key':req.get('business_key'),
            'disposition':r.get('terminal_disposition',r.get('state')),'error':r.get('error',r.get('code')), 'record_kinds':[x.get('kind') for x in r.get('records',[])], 'receipt_keys':list(r)})
    before=load(e/'continuation-02/X09-before-normal-reopen.json'); after=load(e/'continuation-02/X09-GET-only-after-reopen.json')
    result={'source_SQL_normalized_shape':sh,'registry_expected':constants['R02_EXTRA_SHAPE_SHA'],'source_SQL_current_match':sh==constants['R02_EXTRA_SHAPE_SHA'],
        'root16_POSTs':commands,'reopen_top_keys_before':list(before),'reopen_top_keys_after':list(after),'reopen_POSTs_before_explicit':after['POSTs_before_explicit_continue'],
        'reopen_unknown_equal':before.get('unknown')==after.get('unknown'),'reopen_budgets_equal':before.get('budgets')==after.get('budgets'),
        'reopen_heads_equal':before.get('heads')==after.get('heads')}
elif mode=='freeze':
    original=load(out/'freeze-initial.json'); checks=[]
    for row in original['checks']:
        p=Path(row['path']); b=raw(p) if p.is_file() else None
        actual={'exists':b is not None,'bytes':0 if b is None else len(b),'sha256':None if b is None else hashlib.sha256(b).hexdigest()}
        checks.append({'path':str(p),'initial':row['actual'],'actual':actual,'match':actual==row['actual']})
    result={'count':len(checks),'checks':checks,'mismatches':[x for x in checks if not x['match']]}
else: raise ValueError(mode)
record={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'mode':mode,'result':result,'accesses':accesses,'elapsed_seconds':time.perf_counter()-start}
(out/('final-'+mode+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks',)},ensure_ascii=False,indent=2))
