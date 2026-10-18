"""原封存包、保护身份和as-run的标准库只读核对。"""
import ast
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import sys
import time
import zipfile
sys.stdout.reconfigure(encoding='utf-8')
started=time.perf_counter()
root=Path('D:/shspic/project_NO3_RetroLume-agent')
e=root/'DocuN/evidence/TASK-117/execution';c=e/'continuation-05';out=root/'DocuN/evidence/TASK-118/audit'
access=[]
def raw(p):
    p=Path(p);p=p if p.is_absolute() else root/p
    b=p.read_bytes();access.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(v):return hashlib.sha256(v.encode('utf-8') if isinstance(v,str) else v).hexdigest()
protected=load(c/'rules-and-protected-readback.json')['unchanged'];pc=[]
for row in protected:
    p=Path(row['path']);actual=sha(raw(p)) if p.is_file() else None
    pc.append({'path':str(p),'expected':row['sha256'],'actual':actual,'match':actual==row['sha256']})
asruns=[]
for number in range(29,34):
    value=load(c/f'api-{number}-as-run.json');checks=[]
    for item in value['files']:
        p=Path(item['path']);p=p if p.is_absolute() else root/p
        actual=sha(raw(p)) if p.is_file() else None
        checks.append({'path':item['path'],'as_run':item.get('sha256'),'current':actual,'same':actual==item.get('sha256')})
    asruns.append({'api':number,'sample':value['sample'],'source_slot':value.get('source_slot'),'count':len(checks),'differences':[x for x in checks if not x['same']]})
package=e/'synthetic/source-backup/packages/7a10f64c-26bc-4c89-a409-4417ddc1a6dc.rldata'
b=raw(package)
with zipfile.ZipFile(io.BytesIO(b)) as archive:
    manifest=json.loads(archive.read('manifest.json'));body=dict(manifest);expected=body.pop('root_sha256')
    checks=[]
    for member in manifest['contents']:
        data=archive.read(member['path'])
        checks.append({'path':member['path'],'match':sha(data)==member['sha256'] and len(data)==int(member['bytes'])})
    tables={info.filename.split('/')[1][:-6]:[json.loads(line) for line in archive.read(info.filename).splitlines() if line] for info in archive.infolist() if info.filename.startswith('checkpoint/') and info.filename.endswith('.jsonl')}
    vf=[]
    for row in tables['retrieval_chunks']:
        vec=row['vector_value']
        if vec is not None:
            actual=sha(struct.pack('<512f',*vec)) if len(vec)==512 and all(type(x) in (int,float) and math.isfinite(x) for x in vec) else None
            vf.append({'evidence_id':row['evidence_id'],'match':actual==row['vector_sha256']})
    emb=[row for row in tables['activity_operation_results'] if json.loads(row['payload']).get('value',{}).__class__ is dict and json.loads(row['payload'])['value'].get('profile')=='embedding.v1']
    op={(r['activity_id'],r['operation_id']):r for r in tables['activity_operations']}
    triples=[]
    for row in tables['activity_operation_results']:
        operation=op.get((row['activity_id'],row['operation_id']))
        triples.append({'operation_id':row['operation_id'],'match':sha(row['payload'])==row['payload_sha256'] and operation is not None and row['admission_id']==operation['admission_id'] and row['scope_revision']==operation['scope_revision'] and row['execution_generation']==operation['execution_generation']})
    pkg={'path':str(package),'bytes':len(b),'sha256':sha(b),'root_sha256':expected,'root_matches':sha(canon(body))==expected,'contents':len(checks),'contents_mismatches':[x for x in checks if not x['match']],
      'profile':manifest['codec_profile'],'table_count':len(tables),'rows':sum(map(len,tables.values())),'table_rows':{k:len(v) for k,v in tables.items()},'spaces':tables['retrieval_spaces'],
      'vectors':len(vf),'vector_hash_mismatches':[x for x in vf if not x['match']], 'embedding_007_count':len(emb),'all_007_mismatches':[x for x in triples if not x['match']],
      'unknown_operations':[{'activity_id':r['activity_id'],'operation_id':r['operation_id'],'reserved_cost_microunits':r['reserved_cost_microunits'],'state':r['state']} for r in op.values() if r['state']=='unknown']}
png=raw(c/'L10/actual-frame.png');acks=load(c/'L10/input-acks.json')
deletion=load(c/'X02-current-physical-deletion.json');manifest_text=next(r[-1] for r in deletion['SQL']['commands'] if r[0]=='revoke');revoke=next(r for r in deletion['SQL']['commands'] if r[0]=='revoke')
pdf=load(c/'PDF-two-page-confirmed.json');confirm=raw(pdf['confirmation_receipt'])
result={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'protected_count':len(pc),'protected_mismatches':[x for x in pc if not x['match']],
 'as_runs':asruns,'package':pkg,'PNG_hash_matches':sha(png)==acks['PNG_sha256'],'X02_manifest_hash_matches':sha(manifest_text)==revoke[-2],
 'PDF_confirmation_original_hash_matches':sha(confirm)==pdf['confirmation_sha256'],'elapsed_seconds':time.perf_counter()-started,'accesses':access}
(out/'artifact-facts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='accesses'},ensure_ascii=False,indent=2))
