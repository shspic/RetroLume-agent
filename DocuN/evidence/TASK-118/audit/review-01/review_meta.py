"""TASK118 review-01: bounded standard-library reads only, no product imports."""
import argparse,datetime as dt,hashlib,json,sys,time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent'); OUT=ROOT/'DocuN/evidence/TASK-118/audit/review-01'
START=time.perf_counter(); ACC=[]
def pathof(x):
    p=Path(x);return p if p.is_absolute() else ROOT/p
def raw(x):
    p=pathof(x);b=p.read_bytes();ACC.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    if time.perf_counter()-START>55:raise TimeoutError('metadata 55-second guard')
    return b
def decoded(x):
    p=pathof(x)
    if 'task-117-result' in p.name.lower() or 'before-result' in p.name.lower() or p.name.lower()=='received-candidate.json':raise PermissionError('implementation assessment is not an independent input')
    return raw(x).decode('utf-8-sig')
def load(x):return json.loads(decoded(x))
def save(n,v):
    p=(OUT/n).resolve()
    if OUT.resolve() not in p.parents:raise PermissionError('outside review-01')
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def compact(v):
    if isinstance(v,dict):return {k:compact(x) for k,x in v.items()}
    if isinstance(v,list):return [compact(x) for x in v] if len(v)<=12 else {'length':len(v),'first':[compact(x) for x in v[:4]],'last':[compact(x) for x in v[-2:]]}
    if isinstance(v,str) and len(v)>1400:return {'chars':len(v),'prefix':v[:250],'sha256_utf8':hashlib.sha256(v.encode()).hexdigest()}
    return v
p=argparse.ArgumentParser();p.add_argument('mode',choices=['read','json','shape','hash','freeze','init']);p.add_argument('paths',nargs='*');p.add_argument('--select',default='');p.add_argument('--name',default='freeze-initial.json');a=p.parse_args();parts=[];status='ok'
try:
    if a.mode=='read':
        for spec in a.paths:
            path,sep,span=spec.partition('@');lines=decoded(path).splitlines();first,last=(1,len(lines)) if not sep else map(int,span.split(':'))
            parts.append(path+'\n'+'\n'.join(f'{i}: {lines[i-1]}' for i in range(first,min(last,len(lines))+1)))
    elif a.mode in ('json','shape'):
        for x in a.paths:
            v=load(x)
            for k in filter(None,a.select.split('/')):v=v[int(k)] if isinstance(v,list) else v[k]
            if a.mode=='shape':v={k:{'type':type(x).__name__,'length':len(x) if hasattr(x,'__len__') else None} for k,x in v.items()} if isinstance(v,dict) else {'length':len(v),'first':v[:1]}
            parts.append(x+'\n'+json.dumps(compact(v),ensure_ascii=False,indent=2))
    elif a.mode=='hash':
        for x in a.paths:raw(x)
        parts.append(json.dumps(ACC,ensure_ascii=False,indent=2))
    elif a.mode=='init':
        b=raw('DocuN/results/TASK-118-result.md')
        if len(b)!=41590 or hashlib.sha256(b).hexdigest()!='dd0a5f1d2ddb2ffcd9a168496e4cca5b8292b7221977c76b8ff417f9ff0f21f1':raise ValueError('original audit result drift')
        backup=OUT/'original-TASK118-result.bytes'
        if backup.exists() and backup.read_bytes()!=b:raise ValueError('original backup already differs')
        if not backup.exists():backup.write_bytes(b)
        save('start-clock.json',{'utc':'2026-10-18T02:25:42.1180680Z','utc_unix_ms':1792290342118,'host_monotonic_ticks':840019757189,'frequency':10000000,'basis':'actual first tool direct sample; route clock is separate; no cross-domain subtraction'})
        parts.append('original audit byte identity verified and preserved; first direct sample recorded')
    elif a.mode=='freeze':
        checks=[];seen=set()
        def check(path,exp):
            p=pathof(path);key=(str(p),exp.get('sha256'),exp.get('exists',True))
            if key in seen:return
            seen.add(key);b=raw(p) if p.is_file() else None;got={'exists':b is not None,'bytes':0 if b is None else len(b),'sha256':None if b is None else hashlib.sha256(b).hexdigest()}
            checks.append({'path':str(p),'expected':exp,'actual':got,'match':all(got[k]==v for k,v in exp.items() if k in got)})
        def walk(v):
            if isinstance(v,dict):
                if isinstance(v.get('path'),str):
                    if isinstance(v.get('post'),dict):check(v['path'],v['post'])
                    elif 'sha256' in v:check(v['path'],v)
                if isinstance(v.get('absolute_path'),str) and 'sha256' in v:check(v['absolute_path'],v)
                for k,x in v.items():
                    if k not in ('pre','post','audit_pre','S08_pre','original_audit_result'):walk(x)
            elif isinstance(v,list):
                for x in v:walk(x)
        for x in a.paths:walk(load(x))
        result={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'checks':checks,'count':len(checks),'mismatches':[x for x in checks if not x['match']]};save(a.name,result)
        parts.append(json.dumps({'count':result['count'],'mismatches':result['mismatches']},ensure_ascii=False,indent=2))
except BaseException as ex:
    status='error';parts.append(type(ex).__name__+': '+str(ex));raise
finally:
    record={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'argv':sys.argv[1:],'status':status,'elapsed_seconds':time.perf_counter()-START,'accesses':ACC}
    with (OUT/'commands.jsonl').open('a',encoding='utf-8') as s:s.write(json.dumps(record,ensure_ascii=False)+'\n')
    result='\n\n'.join(parts);(OUT/('read-'+str(time.time_ns())+'.txt')).write_text(result,encoding='utf-8');print(result);print('metadata_seconds='+str(record['elapsed_seconds']))
