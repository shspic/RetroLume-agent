"""从本卡已验证CID/本地014冻结精确catalog常量，不采用用户库或包内schema。"""
import ast
import json
import re
import sys
from control import ROOT,HERE,event,write,sha,guard,state
from runtime_control import dsn,metadata,PG_IMAGE
sys.path.insert(0,str(ROOT/'backend'))
import psycopg
from psycopg.rows import dict_row
from app.data_exit.schema_profiles import extra_shape_queries,normalized_extra_shape
from app.data_exit.contracts import canonical,digest
guard()
resource=next(r for r in state()['resources'] if r['id']=='pg-source')
actual=metadata(resource['cid'])
if actual['image']!=PG_IMAGE or not actual['running'] or actual['labels'].get('retrolume.task')!='TASK-117':raise RuntimeError('not_own_trusted_migration_source')
with psycopg.connect(dsn('source'),row_factory=dict_row) as connection:
    shape={key:connection.execute(query).fetchall() for key,query in extra_shape_queries().items()}
    forward_constraints=connection.execute("SELECT conname,pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conname='interview_command_execution'").fetchall()
source=(ROOT/'backend/migrations/014_step018_retrieval.sql').read_text(encoding='utf-8')
functions={}
for match in re.finditer(r'CREATE(?: OR REPLACE)? FUNCTION public\.([a-z_]+)\(.*?\bAS\s*\$([a-z_]+)\$(.*?)\$\2\$;',source,re.S):
    functions[match[1]]=digest(re.sub(r'\s+','',match[3]))
for row in shape['functions']:
    if digest(re.sub(r'\s+','',row['prosrc']))!=functions[row['proname']]:raise RuntimeError('actual_function_not_local014:'+row['proname'])
if len(shape['extensions'])!=1 or shape['extensions'][0]['extname']!='vector':raise RuntimeError('extension_missing')
before=json.loads((HERE/'compat-catalog-before014.json').read_text(encoding='utf-8'))
values={'MIGRATION_014':sha((ROOT/'backend/migrations/014_step018_retrieval.sql').read_bytes()),
 'VECTOR_EXTENSION_VERSION':shape['extensions'][0]['extversion'],'R02_EXTRA_SHAPE_SHA':digest(canonical(normalized_extra_shape(shape))),
 'FORWARD_FUNCTIONS':{k:functions[k] for k in ('interview_head_guard','interview_record_insert_guard','interview_result_eligible')},
 'ORIGINAL_FUNCTIONS_013':{r['proname']:r['prosrc'] for r in before['functions']},
 'ORIGINAL_CONSTRAINTS_013':{r['conname']:r['definition'] for r in before['constraints'] if r['conname']=='interview_command_execution'},
 'FORWARD_CONSTRAINTS_014':{r['conname']:r['definition'] for r in forward_constraints},
 'EXTRA_FUNCTIONS':{r['proname']:functions[r['proname']] for r in shape['functions']}}
path=ROOT/'backend/app/data_exit/schema_profiles.py';raw=path.read_text(encoding='utf-8');tree=ast.parse(raw);lines=raw.splitlines(keepends=True)
edits=[]
for node in tree.body:
    if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in values:
        name=node.targets[0].id;edits.append((node.lineno-1,node.end_lineno,name+'='+repr(values[name])+'\n'))
if len(edits)!=len(values):raise RuntimeError('registry_assignment_missing')
for start,end,replacement in sorted(edits,reverse=True):lines[start:end]=[replacement]
path.write_text(''.join(lines),encoding='utf-8',newline='\n')
write(HERE/'r02-frozen-catalog.json',{'source_cid':resource['cid'],'image':PG_IMAGE,'extension':shape['extensions'],'shape':shape,'shape_sha256':values['R02_EXTRA_SHAPE_SHA'],'migration_014_sha256':values['MIGRATION_014'],'function_bodies_match_local014':True,'ordinary_read_role':True})
event('r02_profile_frozen',extension=shape['extensions'],migration014=values['MIGRATION_014'],shape_sha=values['R02_EXTRA_SHAPE_SHA'])
print('R02 exact local014/function/catalog identity frozen; extension '+values['VECTOR_EXTENSION_VERSION'])
