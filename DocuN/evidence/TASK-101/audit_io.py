"""TASK-101 只读身份核对与逐行读取，不导入产品，不运行测试。"""
import hashlib
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path('D:/shspic/project_NO3_RetroLume-agent')
OWN = ROOT / 'DocuN/evidence/TASK-101'
SNAP = OWN / 'input-snapshot.json'
EXCLUDED = ('DocuN/results/TASK-100-result.md', 'DocuN/results/TASK-100-work-decision.md', 'DocuN/evidence/TASK-100/orchestration-receipt-03/receipt.json')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def emit(name, data):
    path = OWN / name
    if path.exists():
        raise RuntimeError('拒绝覆盖已有审计产物 ' + str(path))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def read(path, first, last):
    relative = path.replace('\\', '/')
    if relative in EXCLUDED:
        raise RuntimeError('禁止的审计输入')
    full = ROOT / path
    lines = full.read_text(encoding='utf-8-sig').splitlines()
    with (OWN / 'reads.jsonl').open('a', encoding='utf-8') as log:
        log.write(json.dumps({'utc':datetime.now(timezone.utc).isoformat(), 'path':relative, 'first':first, 'last':min(last,len(lines)), 'sha256':digest(full)}, ensure_ascii=False) + '\n')
    print(relative)
    for n in range(first, min(last, len(lines)) + 1):
        print(f'{n:5d} {lines[n-1]}')

if sys.argv[1] == 'verify':
    started = time.perf_counter()
    snapshot = json.loads(SNAP.read_text(encoding='utf-8-sig'))
    results = []
    for group in ('contracts','source_files','protected_product_files','rule_files','raw_files'):
        for item in snapshot[group]:
            p = ROOT / item['path']
            actual = digest(p) if p.is_file() else None
            results.append({'group':group,'path':item['path'],'expected':item['sha256'],'actual':actual,'match':actual==item['sha256'],'bytes':p.stat().st_size if p.exists() else None})
    emit('independent-hashes.json', {'utc':datetime.now(timezone.utc).isoformat(),'snapshot_sha256':digest(SNAP),'elapsed_seconds':time.perf_counter()-started,'objects':results})
    emit('audit-start.json', {'utc':datetime.now(timezone.utc).isoformat(),'monotonic':time.perf_counter(),'identity':'Codex desktop；系统身份 GPT-6；无可核实的具体部署型号或家族证明','role':'TASK-101/R-095 独立审计执行者','isolation':'新审计对话；未读取TASK-100实现聊天、结果、自评或work-decision','prelude':'身份核对前只读规则、卡和索引；唯一状态账顶部及定向搜索意外看到编排评价，须披露且不作为证据','counters':{'entry':0,'driver':0,'browser':0,'static_service_start':0,'db':0,'docker':0,'backend':0,'SUP':0,'build':0,'provider':0},'limits':{'active_seconds':14400,'metadata_seconds':600,'probe_seconds':180,'cleanup_seconds':120},'metadata_elapsed_seconds':time.perf_counter()-started})
    print(json.dumps({'objects':len(results),'mismatches':[r for r in results if not r['match']],'elapsed_seconds':time.perf_counter()-started},ensure_ascii=False))
    for item in snapshot['source_files']:
        p=ROOT/item['path']
        print(f"{len(p.read_bytes().splitlines()):5d} {item['path']}")
elif sys.argv[1] == 'read':
    for spec in sys.argv[2:]:
        path, first, last = spec.rsplit(':',2)
        read(path,int(first),int(last))
