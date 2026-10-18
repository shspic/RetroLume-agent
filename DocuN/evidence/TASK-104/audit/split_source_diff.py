from metadata import *
import difflib,re
index=load(ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/audit-input.json')
parts={k:[] for k in ('backend','frontend','other')}
for x in index['product_scope_changed_existing']:
    rel=x['relative_path']; group='backend' if rel.startswith('backend/') else 'frontend' if rel.startswith('frontend/') else 'other'
    patch=''.join(difflib.unified_diff(read(x['initial_bytes_path']).splitlines(keepends=True),read(ROOT/rel).splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
    parts[group].append(patch)
for group,items in parts.items():save(group+'-existing-diff.patch',''.join(items))
src=read(ROOT/'backend/app/memory/repository.py');tree=ast.parse(src)
fingerprints={}
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FUNCTION_FINGERPRINTS' for t in n.targets):fingerprints=ast.literal_eval(n.value)
sql=read(ROOT/'backend/migrations/010_learning_memory.sql')
functions={m[1]:m[2] for m in re.finditer(r'CREATE FUNCTION public\.(\w+)\([^;]*? AS \$f\$(.*?)\$f\$;',sql,re.S)}
checks=[{'name':name,'source_hash_without_whitespace':hashlib.sha256(re.sub(r'\s+','',body).encode()).hexdigest(),'app_expected':fingerprints.get(name),'match':hashlib.sha256(re.sub(r'\s+','',body).encode()).hexdigest()==fingerprints.get(name)} for name,body in functions.items()]
assert len(checks)==len(fingerprints)==12 and all(x['match'] for x in checks)
raw=(ROOT/'backend/migrations/010_learning_memory.sql').read_bytes()
save('sql-source-app-function-binding.json',{'at':stamp(),'sql_file_crlf_sha256':hashlib.sha256(raw).hexdigest(),'sql_text_lf_sha256':hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest(),'functions':checks,'actual_catalog_not_yet_adopted':True})
finish('source-diff-groups-and-sql-app-fingerprints',{'backend_diff_lines':len(''.join(parts['backend']).splitlines()),'frontend_diff_lines':len(''.join(parts['frontend']).splitlines()),'other_diff_lines':len(''.join(parts['other']).splitlines()),'12_functions_source_app_match':True,'raw_sha256':hashlib.sha256(raw).hexdigest(),'lf_sha256':hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()})
