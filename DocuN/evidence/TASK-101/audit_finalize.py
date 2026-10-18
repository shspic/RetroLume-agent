"""TASK-101结束只读冻结核对与自有交付一致性检查，无产品导入或运行。"""
import hashlib
import json
import pathlib
import re
import time
from collections import Counter
from datetime import datetime, timezone

ROOT = pathlib.Path('D:/shspic/project_NO3_RetroLume-agent')
OWN = ROOT / 'DocuN/evidence/TASK-101'
REPORT = ROOT / 'DocuN/results/TASK-101-result.md'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

started = time.perf_counter()
snapshot = load(OWN / 'input-snapshot.json')
origin = load(OWN / 'audit-start.json')
objects = []
for group in ('contracts','source_files','protected_product_files','rule_files','raw_files'):
    for item in snapshot[group]:
        path = ROOT / item['path']
        digest = sha(path) if path.is_file() else None
        objects.append({'group': group, 'path': item['path'], 'expected': item['sha256'],
                        'actual': digest, 'match': digest == item['sha256']})
target = OWN / 'final-freeze-and-usage.json'
if target.exists():
    raise ValueError('不覆盖结束记录')
text = REPORT.read_text(encoding='utf-8')
links = re.findall(r'\]\((D:/[^)]+)\)', text)
link_checks = []
for link in links:
    base = re.sub(r':\d+$','',link)
    path = pathlib.Path(base)
    link_checks.append({'target': link, 'exists': path.is_file() or path == target})
all_methods = load(OWN / 'original-method-logs.json')
pg = set();http = set()
for row in all_methods:
    if row['stage'] in ('repository-raw','http-raw'):
        bag = pg if row['stage'] == 'repository-raw' else http
        bag.update(m['identity'] for m in row['methods'] if m['verdict']=='ok')
aux = [json.loads(line) for line in (OWN/'auxiliary-times.jsonl').read_text(encoding='utf-8').splitlines()]
elapsed = time.perf_counter()-started
result = {
    'utc': datetime.now(timezone.utc).isoformat(),
    'monotonic_elapsed_after_identity_seconds': time.perf_counter()-origin['monotonic'],
    'pre_identity_reading_seconds': None,
    'pre_identity_reading_note': '约06:59 UTC开始只读规则/卡；未独立计时，不并入精确单调累计。',
    'active_limit_seconds': 14400,
    'metadata_limit_seconds': 600,
    'known_metadata_helper_elapsed_seconds': origin['metadata_elapsed_seconds']+sum(a['elapsed_seconds'] for a in aux)+elapsed,
    'shell_read_total_elapsed_seconds': None,
    'metadata_note': '常规shell读取时间未独立聚合；已保存工具返回耗时，不能把辅助小计当全部元数据精确守恒。',
    'new_resource_counts': origin['counters'],
    'new_business_tests': 0,
    'new_network_or_git_writes': 0,
    'new_process_cleanup_required': False,
    'snapshot_sha256': sha(OWN/'input-snapshot.json'),
    'task_card_sha256': sha(ROOT/'DocuN/tasks/TASK-101.md'),
    'groups': dict(Counter(o['group'] for o in objects)),
    'objects': objects,
    'mismatch_count': sum(not o['match'] for o in objects),
    'report_sha256': sha(REPORT),
    'report_bytes': REPORT.stat().st_size,
    'report_lines': len(text.splitlines()),
    'report_has_asterisk': '*' in text,
    'links': link_checks,
    'different_pg_ok_methods': len(pg),
    'different_http_ok_methods': len(http),
    'auxiliary_errors_preserved': ['windows-outcome-links.json','reconstructed-version-bindings.json'],
    'scope_note': '仅保存自有审计报告/证据；无产品、原证据或DocuS写入。'
}
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('utc','monotonic_elapsed_after_identity_seconds','known_metadata_helper_elapsed_seconds','mismatch_count','report_bytes','report_lines','report_has_asterisk','different_pg_ok_methods','different_http_ok_methods')},ensure_ascii=False))
print('失效链接',[r for r in link_checks if not r['exists']])
print('运行资源',result['new_resource_counts'])
if result['mismatch_count'] or result['report_has_asterisk'] or any(not r['exists'] for r in link_checks):
    raise SystemExit(1)
