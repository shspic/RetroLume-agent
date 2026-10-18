"""续作许可接收和唯一总账升级，保留原账/结果/源码原字节。"""
import argparse
from datetime import datetime, timezone
import ctypes
import hashlib
import json
from pathlib import Path
import shutil
import time

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'DocuN/evidence/TASK-114/implementation'
DEST=BASE/'continuation-01'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('begin_utc');parser.add_argument('begin_ns',type=int);args=parser.parse_args()
    permit=json.loads((ROOT/'DocuN/evidence/TASK-114/orchestration-continuation-01-20261013/continuation-permit.json').read_bytes())
    receipt_path=BASE/'control/receipt.json';receipt=json.loads(receipt_path.read_bytes())
    if receipt.get('continuation') is not None:raise RuntimeError('续作许可已激活，不重复清账')
    result=(ROOT/'DocuN/results/TASK-114-result.md').read_bytes()
    if hashlib.sha256(result).hexdigest()!='c655556d7b783a871e34c5a50c40cb9d477504d0b8d389f028e14f68b091d1af':raise RuntimeError('原结果漂移')
    manifest=json.loads((BASE/'closure-20261013/final-source-manifest.json').read_bytes())['files']
    for e in manifest:
        if hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise RuntimeError('源码漂移: '+e['path'])
    bundle=json.loads((BASE/'closure-20261013/final-bundle-manifest.json').read_bytes())['files']
    for e in bundle:
        if hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise RuntimeError('bundle漂移: '+e['path'])
    DEST.mkdir(parents=True,exist_ok=True)
    for e in manifest+bundle:
        target=DEST/'pre'/e['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/e['path'],target)
    for path in ('DocuN/results/TASK-114-result.md','DocuN/evidence/TASK-114/implementation/control/receipt.json','DocuN/evidence/TASK-114/implementation/control/events.jsonl'):
        target=DEST/'pre'/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,target)
    (DEST/'pre-manifest.json').write_text(json.dumps(manifest+bundle,ensure_ascii=False,indent=2),encoding='utf-8')
    # 第一个工具批里的实采UTC为02:43:31.5316719Z；用同批早31.532s的保守边界。
    received=datetime(2026,10,13,2,43,0,tzinfo=timezone.utc)
    now=datetime.now(timezone.utc);mono=time.monotonic_ns()
    received_ns=mono-int((now-received).total_seconds()*1e9)
    receipt['legacy']={'receipt_sha256':hashlib.sha256(receipt_path.read_bytes()).hexdigest(),'raw_counts':dict(receipt['counts']),'net_active_work':'unknown','old_window_expired':True}
    receipt['counts']['real_roots']=permit['conservative_root_baseline']
    receipt['limits']['real_roots']=permit['cumulative_root_limit']
    receipt['continuation']={'permit':permit['permit'],'received_utc':received.isoformat(),'received_monotonic_ns':received_ns,
        'anchor_basis':'conservative floor 31.532s before first tool batch UTC sample; monotonic derived at bootstrap',
        'active_limit_seconds':permit['new_active_work_seconds'],'calendar_limit_seconds':permit['calendar_horizon_seconds'],
        'active_segments':[{'begin_utc':args.begin_utc,'begin_ns':args.begin_ns,'end_ns':None,'reason':'first non-readonly continuation work'}],
        'real_batches':[],'pause':None}
    pending=receipt_path.with_suffix('.pending');pending.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');pending.replace(receipt_path)
    entry={'utc':now.isoformat(),'monotonic_ns':mono,'kind':'continuation.accepted','permit':permit['permit'],'old_anchor_unchanged':True,'root_baseline':10,'root_limit':18,'activity_begin_ns':args.begin_ns}
    with (BASE/'control/events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(entry,ensure_ascii=False)+'\n');f.flush()
    (DEST/'accepted.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'state':'accepted','source_files':len(manifest),'bundle_files':len(bundle),'old_counts_retained':True,'permit':permit['permit']}))

if __name__=='__main__':main()
