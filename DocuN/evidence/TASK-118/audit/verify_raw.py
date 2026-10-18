"""只以JSON/原始字节/AST核证，避免执行产品和原runner。"""
import ast
from copy import deepcopy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')
root=Path('D:/shspic/project_NO3_RetroLume-agent')
e=root/'DocuN/evidence/TASK-117/execution'
out=root/'DocuN/evidence/TASK-118/audit'
started=time.perf_counter()
access=[]
def raw(p):
    p=p if isinstance(p,Path) else root/p
    b=p.read_bytes();access.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)});return b
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(v):return hashlib.sha256(v.encode('utf-8') if isinstance(v,str) else v).hexdigest()
def normalize(shape):
    value=deepcopy(shape)
    for row in value.get('columns',[]):
        if row['relname']=='activities' and row['attname']=='outbound_grant_sha256' and row.get('owner_super') is True:row['owner']='bootstrap_owner'
    for section in ('columns','table_acl','functions'):
        for row in value.get(section,[]):
            if row.get('acl'):row['acl']=re.sub(r'/[^,}]+','/trusted_owner',row['acl'])
    return value
mode=sys.argv[1]
result={}
if mode=='sql':
    tree=ast.parse(raw(root/'backend/app/data_exit/schema_profiles.py').decode('utf-8-sig'))
    constants={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            try:constants[node.targets[0].id]=ast.literal_eval(node.value)
            except (ValueError,TypeError):pass
    sql=raw(root/'backend/migrations/014_step018_retrieval.sql').decode('utf-8-sig')
    extracted={m.group(1):m.group(3) for m in re.finditer(r'CREATE(?: OR REPLACE)? FUNCTION public\.(\w+)\(.*?\).*? AS (\$\w*\$)(.*?)\2;',sql,re.S)}
    fnchecks=[]
    for name,expected in constants['EXTRA_FUNCTIONS'].items():
        actual=sha(re.sub(r'\s+','',extracted.get(name,'')))
        fnchecks.append({'function':name,'expected_registry':expected,'actual_014':actual,'match':actual==expected})
    result={'migration_registry_matches':sha(sql)==constants['MIGRATION_014'],'functions_from_trusted_014':fnchecks,'catalogs':[]}
    for rel in ['r02-frozen-catalog.json','continuation-02/compat-SQL-after.json','continuation-02/compat-actual-after-first-commit.json']:
        v=load(e/rel);shape=v['shape']
        result['catalogs'].append({'path':rel,'raw_shape_hash':sha(canon(shape)),'normalized_shape_hash':sha(canon(normalize(shape))),'current_expected':constants['R02_EXTRA_SHAPE_SHA'],
          'current_match':sha(canon(normalize(shape)))==constants['R02_EXTRA_SHAPE_SHA'],
          'function_actual_vs_014':[{'name':r['proname'],'match':r['proname'] in extracted and re.sub(r'\s+','',r['prosrc'])==re.sub(r'\s+','',extracted[r['proname']])} for r in shape.get('functions',[])],
          'roles':shape.get('roles'),'table_acl':shape.get('table_acl'),'extensions':shape.get('extensions'),
          'interview_read_acl_count':len(shape.get('interview_read_acl',[])),
          'migration_recorded':v.get('migration_014_sha256',v.get('migration_014'))})
    old=load(e/'compat-catalog-before014.json');new=load(e/'compat-catalog-after014.json')
    result['legacy_before_after_equal']=canon(old['legacy'])==canon(new['legacy'])
    result['legacy_rows_before']=old['legacy'];result['legacy_rows_after']=new['legacy']
    legacy=load(e/'compat-legacy-fixture.json')
    result['compat_fixture_keys']=list(legacy)
elif mode=='bindings':
    c=e/'continuation-05'
    checks=[]
    for filename in ('final-source-manifest.json','final-binding.json','final-bundle-7-binding.json','final-fixture-manifest.json'):
        v=load(c/filename)
        entries=v.get('entries',v.get('files',v.get('assets',[])))
        if isinstance(entries,dict):entries=[{'path':k,**val} for k,val in entries.items()]
        for row in entries:
            p=row.get('path')
            if not p:continue
            expected=row.get('post',row)
            file=Path(p) if Path(p).is_absolute() else root/p
            b=raw(file) if file.is_file() else None
            actual=None if b is None else sha(b)
            checks.append({'binding':filename,'path':p,'expected_sha256':expected.get('sha256'),'actual_sha256':actual,'match':actual==expected.get('sha256')})
    result={'checks':checks,'count':len(checks),'mismatches':[v for v in checks if not v['match']]}
elif mode=='readback':
    v=load(e/'continuation-05/rules-and-protected-readback.json');result={'sections':{}}
    for key in ('unchanged','authorized_changes'):
        rows=v[key];result['sections'][key]={'count':len(rows),'first':rows[:1],'last':rows[-1:]}
else:raise ValueError('mode')
record={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'mode':mode,'result':result,'accesses':access,'elapsed_seconds':time.perf_counter()-started}
(out/('raw-'+mode+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result if mode!='bindings' else {k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2))
print('metadata_seconds='+str(record['elapsed_seconds']))
