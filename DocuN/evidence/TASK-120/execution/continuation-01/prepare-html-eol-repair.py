"""Prepare only. Exact nine trusted function bodies; no PG connection."""
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
old=json.loads((HERE.parent/'root-12-html-shape-difference.json').read_text(encoding='utf-8'))
path=ROOT/'backend/migrations/012_html_explanations.sql'
source=path.read_text(encoding='utf-8-sig')
commands=[];identities=[]
for delta in old['differences']:
    before=delta['before'];after=delta['after'];normalized=dict(after,prosrc=after['prosrc'].replace('\r\n','\n'))
    if delta['section']!='functions' or before!=normalized or '\r' in normalized['prosrc']:raise RuntimeError('not_exact_EOL_only')
    name=before['proname']
    found=re.search(r'CREATE FUNCTION public\.'+re.escape(name)+r'\(.*?\bAS\s+(\$[A-Za-z_0-9]*\$)(.*?)\1\s*;',source,re.S)
    if not found or found.group(2)!=before['prosrc']:raise RuntimeError('trusted_migration_body_not_identical_'+name)
    commands.append(found.group(0).replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1))
    identities.append({'function':name,'before_body_sha256':hashlib.sha256(after['prosrc'].encode()).hexdigest(),'after_body_sha256':hashlib.sha256(before['prosrc'].encode()).hexdigest()})
if len(commands)!=9:raise RuntimeError('closed_nine_function_set')
sql='-- REVIEW ONLY until explicit TASK120 supplemental DDL permission.\nBEGIN;\n'+'\n\n'.join(commands)+'\nCOMMIT;\n'
(HERE/'proposed-html-eol-repair.sql').write_text(sql,encoding='utf-8',newline='\n')
manifest={'status':'PREPARED_NOT_EXECUTED','database':'retrolume_task120_flow','migration_source':path.relative_to(ROOT).as_posix(),'migration_original_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256(sql.encode()).hexdigest(),'functions':identities,'financial_rows_changed':0,'schema_profile_or_source_files_changed':False}
(HERE/'proposed-html-eol-repair.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest))
