from pathlib import Path
import ast, datetime, hashlib, json, sys, time
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OWN=ROOT/'DocuN/evidence/TASK-104/audit'
BOOT=time.monotonic()
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return Path(p).read_text(encoding='utf-8-sig')
def load(p): return json.loads(read(p))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):
    p=(OWN/name).resolve()
    if not p.is_relative_to(OWN.resolve()): raise ValueError('audit own directory only')
    p.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return p
def finish(label,data=None):
    v={'at':stamp(),'label':label,'metadata_measured_seconds':time.monotonic()-BOOT,'data':data}
    with (OWN/'metadata-actions.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(v,ensure_ascii=False)+'\n')
    print(json.dumps(v,ensure_ascii=False))
if __name__=='__main__':
    path=ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/audit-input.json'
    v=load(path)
    initial={'at':stamp(),'task':'TASK-104/R-098','permit':'TASK-104-G9-AUDIT-20261007','client':'Codex desktop','system_model':'GPT-6','actual_deployment':'not exposed','role':'A+','first_card_reading_not_individually_timed':True,'pre_receipt_conservative_charge_seconds':360,'fixed_active_monotonic_origin':BOOT-360,'fixed_active_deadline':BOOT-360+21600,'limits_seconds':{'active':21600,'metadata':1800,'real_read_only':600,'cleanup':300,'fixture_offline':300},'limits_counts':{'real_roots':3,'pg1_starts':3,'api_starts':3,'browser':3,'driver':3,'offline_batches':3},'counts':{'real_roots':0,'pg1_starts':0,'api_starts':0,'browser':0,'driver':0,'offline_batches':0},'new_business_writes':0,'prior_task101_audit_history':True,'participated_TASK102_or_TASK103':False,'isolation_exception':'This chat has earlier independent TASK-101 history; no TASK102/103 implementation context, chat or self-evaluation inherited. It is not a literally empty conversation.','card_sha256':sha(ROOT/'DocuN/tasks/TASK-104.md'),'input_sha256':sha(path)}
    save('audit-receipt.json',initial)
    out={}
    for k,x in v.items():
        out[k]={'kind':'list','count':len(x),'first':x[0] if x else None} if isinstance(x,list) else {'keys':list(x)} if isinstance(x,dict) else x
    nav=load(ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/raw-evidence-navigation.json')
    navshape={k:({'count':len(x),'first':x[0] if x else None} if isinstance(x,list) else {'keys':list(x)} if isinstance(x,dict) else x) for k,x in nav.items()} if isinstance(nav,dict) else {'count':len(nav),'first':nav[0]}
    save('input-shape.json',{'input':out,'navigation':navshape})
    finish('receive-fix-deadline-and-input-shape',{'input':out,'navigation':navshape})
