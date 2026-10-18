"""只核现成C05文件和精确资源元数据，不导入或运行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, subprocess, shutil

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
C05 = ROOT / 'DocuN/evidence/TASK-111/execution/continuation-05'

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):
    data = p.read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

at = datetime.now(timezone(timedelta(hours=8))).isoformat()
delivery = load(C05 / 'final/result-delivery-receipt.json')
report = ROOT / 'DocuN/results/TASK-111-result.md'
assert info(report) == dict(bytes=delivery['result_bytes'], sha256=delivery['result_sha256'])
old = (C05 / 'prior-TASK-111-result.md').read_bytes()
assert report.read_bytes().endswith(old) and len(old) == delivery['old_suffix_bytes']
sources = []
for row in load(C05 / 'final/source-identity.json'):
    actual = info(ROOT / row['path'])
    assert actual['sha256'] == row['sha256'] and actual['bytes'] == row['bytes'], row['path']
    sources.append(dict(**row, match=True))
rules = []
for row in load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    actual = info(Path(row['absolute_path']))
    assert actual['sha256'] == row['sha256']
    rules.append(dict(path=row['absolute_path'], sha256=actual['sha256'], match=True))
receipt = load(C05 / 'final/execution-receipt.json')
budget = load(ROOT / 'DocuN/evidence/TASK-111/execution/budget.json')
assert budget['active_batch'] is None and budget['counts'] == receipt['counts']
assert budget['time_seconds'] == receipt['time_seconds']
effects_path = C05 / 'root-15/step-03-tail/tail-attempt-2/tail-effects.json'
effects = load(effects_path)
completed = next(r for r in effects['records'] if r['label'] == 'old_actual_values_released_new_identity_intact')
assert completed['images'] and all(r['decoded'] and r['released'] and r['closed'] and r['closed_width'] == 0 and r['closed_height'] == 0 for r in completed['images'])
assert all(r['id'] not in completed['draws'] for r in completed['images'])
fault_dir = C05 / 'root-15/step-04-faults'
faults = load(fault_dir / 'fault-results.json')
assert {r['scenario'] for r in faults} == {'owner_control_lost','pipe_corrupt','supervisor_death','both_supervisors_death'}
assert all(r['status'] == 'PASS_REAL_REMAINING_SCENARIO' and r['extra_job_handles_held'] is False and r['source_image'] == 'sha256:c23c7489d56fa2cc955dc15e86e0b710b476589997d57ee33c9eb9f3949e826f' for r in faults)
evidence = []
for rel in ['final/matrix-actual.json','final/session-proof-index.json','final/execution-receipt.json','final/delivery-boundaries.json','root-15/step-03-tail/tail-attempt-2/tail-effects.json','root-15/step-04-faults/fault-results.json','root-15/step-04-faults/supervisor_death/same-root-persistent-recovery.json','root-15/step-04-faults/both_supervisors_death/same-root-persistent-recovery.json','cleanup-only/never-created-full-R-recovery.json']:
    evidence.append(dict(path=str(C05 / rel), **info(C05 / rel)))
save('received.json', dict(at=at, result=delivery, old_report_suffix_preserved=True, sources=sources, source_count=len(sources), rules=rules, counts=receipt['counts'], time_seconds=receipt['time_seconds'], evidence=evidence, accepted_faults=faults, bitmap_checks=dict(actual_decoded=True, actual_close_zero=True, old_not_drawn=True), report_or_source_product_executions=0))
actual_objects = []
for row in load(C05 / 'final/exact-resources-final.json')['objects']:
    p = subprocess.run([shutil.which('docker'),'container','inspect',row['id']], capture_output=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode == 0, '精确对象元数据不可读取'
    item = json.loads(p.stdout)[0]
    state = item['State']
    assert item['Id'] == row['id'] and item['Image'] == row['image'] and item['Name'] == row['name']
    assert not state['Running'] and state['Pid'] == 0 and item['RestartCount'] == 0
    actual_objects.append(dict(id=item['Id'], name=item['Name'], image=item['Image'], running=False, pid=0, restart_count=0))
save('resource-recheck.json', dict(at=at, objects=actual_objects, read_only=True, only_registered=True, metadata_not_substitute_for_old_UNKNOWN_full_stop=True))
print(json.dumps(dict(at=at, source_count=len(sources), rules_count=len(rules), result_match=True, old_suffix_preserved=True, resources_stopped=len(actual_objects), bitmap_actual_close=True, fault_passes=[r['scenario'] for r in faults], active_batch=None), ensure_ascii=False))
