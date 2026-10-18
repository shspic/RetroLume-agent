"""纯元数据封存与逐文件pre/diff/post；不测试、启资源或重算旧账。"""
from datetime import datetime,timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'DocuN/evidence/TASK-114/implementation/continuation-01'
DEST=E/'final'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,value):(DEST/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    DEST.mkdir()
    before=json.loads((E/'pre-manifest.json').read_bytes());prior={e['path']:e for e in before}
    files={ROOT/p for p in prior}
    for directory in ('backend/app/data_exit','frontend/src/data','backend/tests/fixtures/task114','frontend/dist'):
        files.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for pattern in ('backend/tests/test_data_exit*.py','frontend/tests/task114*.mjs'):files.update(ROOT.glob(pattern))
    entries=[]
    for p in sorted(files):
        rel=p.relative_to(ROOT).as_posix();old=(E/'pre'/rel).read_bytes() if rel in prior else b''
        if not p.exists():entries.append({'path':rel,'change':'deleted_build_output','before_sha256':sha(old),'exists':False});continue
        raw=p.read_bytes();destination=DEST/'source'/rel;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,destination)
        kind=('unchanged' if old==raw else 'modified') if rel in prior else 'added'
        item={'path':rel,'bytes':len(raw),'sha256':sha(raw),'change':kind,'before_exists':rel in prior,'before_sha256':sha(old) if rel in prior else None}
        if kind!='unchanged':
            d=DEST/'diff'/(rel+'.diff');d.parent.mkdir(parents=True,exist_ok=True)
            try:d.write_text(''.join(difflib.unified_diff(old.decode('utf-8-sig').splitlines(keepends=True),raw.decode('utf-8-sig').splitlines(keepends=True),fromfile='pre/'+rel if rel in prior else '/dev/null',tofile='final/'+rel)),encoding='utf-8',newline='\n')
            except UnicodeError:item['binary_diff']='exact bytes and hash only'
        entries.append(item)
    save('manifest.json',entries)
    save('changes.json',{'counts':{k:sum(e['change']==k for e in entries) for k in ('modified','added','unchanged','deleted_build_output')},'files':[{k:e[k] for k in ('path','change')} for e in entries if e['change']!='unchanged']})
    receipt_path=ROOT/'DocuN/evidence/TASK-114/implementation/control/receipt.json';receipt=json.loads(receipt_path.read_bytes())
    identities=[]
    for r in receipt['resources']:
        if r['kind']!='pg':continue
        result=subprocess.run(['docker','inspect',r['identity']],capture_output=True,check=False,timeout=20)
        if result.returncode:raise RuntimeError('准确Docker观察不可用，不能冒清场完成')
        v=json.loads(result.stdout)[0]
        if v['Id']!=r['identity'] or v['Image']!='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f':raise RuntimeError('资源身份漂移')
        identities.append({'cid':v['Id'],'name':v['Name'],'image_id':v['Image'],'status':v['State']['Status'],'running':v['State']['Running'],'pid':v['State']['Pid'],
            'labels':{k:x for k,x in v['Config']['Labels'].items() if k.startswith('retrolume.')},
            'mounts':[{k:m[k] for k in ('Type','Name','Destination','RW')} for m in v['Mounts']]})
    if any(v['running'] or v['pid'] for v in identities) or any(r['state']=='running' for r in receipt['resources']):raise RuntimeError('仍有在途资源')
    save('resources.json',identities)
    portquery="ConvertTo-Json -Compress -InputObject @(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object { $_.LocalPort -in @(18114,15114,55461,55462,55463,55464,55465,55466,55467,55468,55469) } | Select-Object LocalAddress,LocalPort,OwningProcess)"
    p=subprocess.run(['powershell','-NoProfile','-Command',portquery],capture_output=True,check=False,timeout=30)
    if p.returncode:raise RuntimeError('端口观察不可用')
    listeners=json.loads(p.stdout.decode('utf-8-sig'));save('listeners.json',listeners)
    if listeners:raise RuntimeError('本卡端口仍有监听')
    active=sum(((s['end_ns'] if s['end_ns'] is not None else time.monotonic_ns())-s['begin_ns'])/1e9 for s in receipt['continuation']['active_segments'])
    save('budget-at-freeze.json',{'utc':datetime.now(timezone.utc).isoformat(),'counts':receipt['counts'],'limits':receipt['limits'],'holding_seconds':receipt['real_holding_seconds'],
        'offline_seconds':receipt['offline_seconds'],'active_seconds':active,'original_anchor_preserved':receipt['received_monotonic_ns'],'all_consumers_stopped':True,
        'root_quota_reached':receipt['counts']['real_roots']==receipt['limits']['real_roots'],'original_result_suffix_sha256':sha((E/'pre/DocuN/results/TASK-114-result.md').read_bytes())})
    proof=[]
    for p in sorted((E/'batches').glob('*/result.json')):proof.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes()),'result':json.loads(p.read_bytes())})
    save('batch-result-index.json',proof)
    failed=[]
    for p in sorted((E/'batches').glob('*/failure.json')):failed.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes()),'result':json.loads(p.read_bytes())})
    save('failure-index.json',failed)
    save('bundle.json',[e for e in entries if e['path'].startswith('frontend/dist/') and e.get('exists') is not False])
    pins=json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    checks=[{'path':p['absolute_path'],'expected':p['sha256'],'actual':sha(Path(p['absolute_path']).read_bytes())} for p in pins]
    if any(c['expected']!=c['actual'] for c in checks):raise RuntimeError('锁定规则漂移')
    save('locked-rules.json',checks)
    print(json.dumps({'final':str(DEST),'files':len(entries),'counts':receipt['counts'],'holding':receipt['real_holding_seconds'],'active_seconds':active,'all_stopped':True}))

if __name__=='__main__':main()
