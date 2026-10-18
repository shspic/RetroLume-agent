"""TASK-119 metadata only: hash prescribed public project inputs; no product import."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
manifest_path = ROOT / 'DocuN/evidence/TASK-119/orchestration-20261018/input-manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
expected = list(manifest['sources']) + [manifest['audit_report'], manifest['adoption_receipt'], manifest['contract']]
rows = []
for item in expected:
    path = Path(item['path'])
    raw = path.read_bytes()
    actual = {'path': str(path), 'bytes': len(raw), 'sha256': sha256(raw).hexdigest()}
    actual['matches_orchestration'] = actual['bytes'] == item['bytes'] and actual['sha256'] == item['sha256']
    rows.append(actual)
extra = [
    'AGENTS.md', 'DocuN/tasks/TASK-119.md',
    'DocuN/results/TASK-117-work-decision.md', 'DocuN/results/TASK-118-work-decision.md',
    'backend/app/activities/teaching_repository.py', 'backend/app/activities/interview_repository.py',
    'backend/app/capabilities/contracts.py', 'backend/app/learning/contracts.py',
    'backend/app/learning/teaching_contracts.py', 'backend/app/interview/contracts.py',
    'backend/app/preview/business_service.py', 'backend/app/preview/model_policy.py',
    'backend/app/worker/one_call.py', 'backend/app/retrieval/contracts.py',
    'backend/app/data_exit/schema_profiles.py', 'backend/app/data_exit/schema_checks.py',
    'backend/migrations/014_step018_retrieval.sql',
]
for name in extra:
    path = ROOT / name
    if path.is_file():
        raw = path.read_bytes()
        rows.append({'path': str(path), 'bytes': len(raw), 'sha256': sha256(raw).hexdigest(), 'additional_readonly_input': True})
    else:
        rows.append({'path': str(path), 'exists': False, 'note': 'name lookup only; no execution'})
samples = json.loads((ROOT / 'DocuN/evidence/TASK-116/design/sample-inputs.json').read_text(encoding='utf-8'))
literals = []
for alias, value in samples['inputs'].items():
    for index, text in enumerate(value if isinstance(value, list) else [value]):
        raw = text.encode('utf-8')
        literals.append({'alias': alias, 'ordinal': index, 'utf8_bytes': len(raw),
                         'raw_text_sha256': sha256(raw).hexdigest(),
                         'json_string_sha256': sha256(json.dumps(text, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()})
sources = [{'alias': x['alias'], 'filename': x['filename'], 'utf8_bytes': len(x['text'].encode('utf-8')),
            'raw_text_sha256': sha256(x['text'].encode('utf-8')).hexdigest()} for x in samples['sources']]
payload = {'task': 'TASK-119', 'sampled_utc': datetime.now(timezone.utc).isoformat(),
           'scope': 'metadata identity only; no runtime or secret read', 'inputs': rows,
           'mismatch_count': sum(r.get('matches_orchestration') is False for r in rows),
           'frozen_sample_text_metadata': sources, 'finite_literal_metadata': literals}
(OUT / 'input-identities.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'input_count': len(rows), 'mismatches': payload['mismatch_count'],
                  'finite_literals': len(literals), 'source_text_bytes': sum(x['utf8_bytes'] for x in sources)}, ensure_ascii=False))
