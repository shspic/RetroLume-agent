from pathlib import Path
import ast, datetime, hashlib, json, sys, time
ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OWN = ROOT / 'DocuN/evidence/TASK-101/review-03'
STARTED = time.perf_counter()
def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    return Path(path).read_text(encoding='utf-8-sig')
def load(path):
    return json.loads(read(path))
def save(name, value):
    path = (OWN / name).resolve()
    if not path.is_relative_to(OWN.resolve()):
        raise ValueError('own evidence only')
    if isinstance(value, str):
        path.write_text(value, encoding='utf-8')
    else:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path
def finish(label, data=None):
    item = {'at': stamp(), 'label': label, 'elapsed_seconds': time.perf_counter()-STARTED}
    if data is not None:
        item['data'] = data
    with (OWN / 'metadata-actions.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False)+'\n')
    print(json.dumps(item, ensure_ascii=False))
if __name__ == '__main__':
    card = ROOT / 'DocuN/tasks/TASK-101.md'
    index = ROOT / 'DocuN/evidence/TASK-101/review-03-input.json'
    baseline = ROOT / 'DocuN/results/TASK-101-result.md'
    frozen = ROOT / 'DocuN/evidence/TASK-100/orchestration-receipt-07/TASK-101-review-02-report-as-frozen.md'
    baseline_bytes = baseline.read_bytes()
    if len(baseline_bytes) != 70370 or hashlib.sha256(baseline_bytes).hexdigest() != 'b75f00d8a9a1e3c564d221dc70ca591cb0fa0a23ddf276a691cd1d323ba1dbb2':
        raise ValueError('prior report differs')
    if baseline_bytes != frozen.read_bytes():
        raise ValueError('frozen/current prior report mismatch')
    (OWN / 'prior-report-preserved.md').write_bytes(baseline_bytes)
    receipt = {'at':stamp(), 'scope':'F01 / review-03 only; no product execution', 'card_sha256':sha(card), 'input_sha256':sha(index), 'prior_report_bytes':len(baseline_bytes), 'prior_report_sha256':sha(baseline), 'prior_frozen_sha256':sha(frozen), 'pre_receipt_first_reads_seconds':'not individually measured', 'pre_receipt_conservative_charge_seconds':600, 'active_deadline_utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=3000)).isoformat(), 'permit_active_seconds':3600, 'permit_pure_metadata_seconds':300, 'new_business_resources':0}
    if receipt['input_sha256'] != 'f5febafa84ace45f2a77783873a641ea414ec165ee7d55224f570bfd5d15959f':
        raise ValueError('neutral input drift')
    save('audit-receipt.json', receipt)
    obj = load(index)
    summary = {}
    for key, value in obj.items():
        if isinstance(value, list):
            summary[key] = {'count':len(value), 'first':value[0] if value else None}
        else:
            summary[key] = value
    finish('initialize-and-index-shape', summary)
