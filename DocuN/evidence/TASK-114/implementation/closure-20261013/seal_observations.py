"""Stop-boundary evidence sealing only: no product import, test, SQL, or resource start."""
from datetime import datetime, timedelta, timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = ROOT / 'DocuN/evidence/TASK-114/implementation'
CLOSURE = Path(__file__).resolve().parent
CONTROL = EVIDENCE / 'control'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    with (CLOSURE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def command(arguments):
    result = subprocess.run(arguments, capture_output=True, timeout=30, check=False)
    return result.returncode, result.stdout.decode('utf-8-sig').strip()


def main():
    now = datetime.now(timezone.utc)
    mono = time.monotonic_ns()
    receipt_raw = (CONTROL / 'receipt.json').read_bytes()
    receipt = json.loads(receipt_raw)
    start = datetime.fromisoformat(receipt['received_utc'])
    elapsed = (mono - receipt['received_monotonic_ns']) / 1e9
    save('stop-boundary.json', {
        'utc': now.isoformat(), 'monotonic_ns': mono,
        'purpose': 'read_only_resource_observation_and_required_evidence_sealing',
        'new_product_execution': False, 'new_budget_authorization_found': False,
        'original_receipt_sha256': sha(receipt_raw), 'original_anchors_unchanged': True,
        'received_utc': receipt['received_utc'], 'received_monotonic_ns': receipt['received_monotonic_ns'],
        'elapsed_monotonic_seconds': elapsed, 'elapsed_utc_seconds': (now - start).total_seconds(),
        'total_limit_seconds': receipt['limits']['total_seconds'],
        'business_stop_utc': (start + timedelta(seconds=27600)).isoformat(),
        'total_stop_utc': (start + timedelta(seconds=28800)).isoformat(),
        'total_window_expired': elapsed >= 28800,
        'counts_preserved': receipt['counts'], 'offline_seconds_preserved': receipt['offline_seconds'],
        'holding_seconds_preserved': receipt['real_holding_seconds'],
        'resource_counters_reset': False,
    })

    source = next(r for r in receipt['resources'] if r['kind'] == 'pg')
    code, raw = command(['docker', 'inspect', source['identity']])
    if code:
        observation = {'source_inspect_exit_code': code, 'identity_status': 'unavailable'}
    else:
        v = json.loads(raw)[0]
        h = v['HostConfig']
        labels = v['Config'].get('Labels', {})
        observation = {
            'source_inspect_exit_code': 0, 'cid': v['Id'], 'name': v['Name'], 'image_id': v['Image'],
            'running': v['State']['Running'], 'status': v['State']['Status'],
            'started_at': v['State']['StartedAt'], 'finished_at': v['State']['FinishedAt'],
            'labels': {k: labels.get(k) for k in ('retrolume.task', 'retrolume.data.job', 'retrolume.data.profile')},
            'mounts': [{k: m[k] for k in ('Type', 'Name', 'Destination', 'RW')} for m in v['Mounts']],
            'ports': h['PortBindings'], 'memory_bytes': h['Memory'], 'nano_cpus': h['NanoCpus'],
            'pids_limit': h['PidsLimit'], 'restart_policy': h['RestartPolicy']['Name'],
            'privileged': h['Privileged'], 'network_mode': h['NetworkMode'],
            'identity_matches_receipt': (
                v['Id'] == source['identity'] and v['Name'] == '/' + source['metadata']['name']
                and v['Image'] == source['metadata']['image_id']
                and labels.get('retrolume.data.job') == source['metadata']['labels']['retrolume.data.job']
                and len(v['Mounts']) == 1 and v['Mounts'][0].get('Name') == source['metadata']['volume']
            ),
        }
    names = {'retrolume-task-114-data-source'} | {f'retrolume-task-114-data-target{i:02}' for i in range(1, 9)}
    code, listing = command(['docker', 'ps', '-a', '--no-trunc', '--format', '{{json .}}'])
    observation['container_list_exit_code'] = code
    observation['exact_task_pg_objects'] = [
        {k: row.get(k) for k in ('ID', 'Names', 'State', 'Status', 'Ports')}
        for line in listing.splitlines() for row in [json.loads(line)] if row.get('Names') in names
    ] if code == 0 else None
    code, listing = command(['docker', 'volume', 'ls', '--format', '{{.Name}}'])
    observation['volume_list_exit_code'] = code
    observation['exact_task_pg_volumes'] = sorted(set(listing.splitlines()) & {n + '-data' for n in names}) if code == 0 else None
    ps = "ConvertTo-Json -Compress -InputObject @(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object { $_.LocalPort -in @(18114,15114,55461,55462,55463,55464,55465,55466,55467,55468,55469) } | Select-Object LocalAddress,LocalPort,OwningProcess)"
    code, listing = command(['powershell', '-NoProfile', '-Command', ps])
    observation['listener_query_exit_code'] = code
    observation['task_port_listeners'] = json.loads(listing) if code == 0 and listing else None
    save('resources-observed.json', observation)

    before = json.loads((CONTROL / 'before-manifest.json').read_bytes())
    prior = {v['path']: v for v in before}
    files = {ROOT / p for p in prior}
    for directory in ('backend/app/data_exit', 'frontend/src/data', 'backend/tests/fixtures/task114'):
        files.update(p for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for pattern in ('backend/tests/test_data_exit*.py', 'frontend/tests/task114*.mjs'):
        files.update(ROOT.glob(pattern))
    files.update(ROOT / n for n in ('backend/migrations/013_data_exit.sql', 'deploy/data_restore.py', 'config/data-exit.example.json'))
    manifest = []
    diff_root = CLOSURE / 'diff'
    for path in sorted(files):
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        target = CLOSURE / 'final-source' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        entry = {'path': rel, 'bytes': len(raw), 'sha256': sha(raw), 'baseline_registered': rel in prior}
        if rel in prior:
            old = (EVIDENCE / 'before' / rel).read_bytes()
            entry.update(before_bytes=len(old), before_sha256=sha(old), baseline_copy_matches_registered=sha(old) == prior[rel]['sha256'])
            entry['change'] = 'unchanged' if old == raw else 'modified'
        else:
            old = b''
            entry['change'] = 'new_in_this_task'
            entry['before_observation'] = 'not_in_scoped_before_inventory; creation_history_and_batch_manifests_retained'
        if old != raw:
            diff = ''.join(difflib.unified_diff(old.decode('utf-8-sig').splitlines(keepends=True), raw.decode('utf-8-sig').splitlines(keepends=True), fromfile='before/' + rel if rel in prior else '/dev/null', tofile='final/' + rel))
            destination = diff_root / (rel + '.diff')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(diff, encoding='utf-8', newline='\n')
            entry['diff_path'] = destination.relative_to(ROOT).as_posix()
        manifest.append(entry)
    save('final-source-manifest.json', {'utc': now.isoformat(), 'is_tested_snapshot': False, 'reason': 'freeze_at_stop_boundary; execution_coverage_is_defined_by_prior_as_run', 'files': manifest})
    changed = [e['path'] for e in manifest if e['change'] == 'modified']
    added = [e['path'] for e in manifest if e['change'] == 'new_in_this_task']
    save('change-index.json', {'baseline_files': len(before), 'final_files': len(manifest), 'modified': changed, 'added': added, 'unchanged_count': sum(e['change'] == 'unchanged' for e in manifest), 'all_baseline_copies_match': all(e.get('baseline_copy_matches_registered', True) for e in manifest)})
    coverage = []
    for batch in sorted((EVIDENCE / 'as-run').iterdir()):
        p = batch / 'manifest.json'
        if not p.exists():
            continue
        old = {v['path']: v for v in json.loads(p.read_bytes())['files']}
        coverage.append({'batch': batch.name, 'files_different_from_final': [e['path'] for e in manifest if e['path'] in old and e['sha256'] != old[e['path']]['sha256']], 'files_missing_in_batch': [e['path'] for e in manifest if e['path'] not in old]})
    save('as-run-to-final.json', coverage)
    bundle = []
    for path in sorted((ROOT / 'frontend/dist').rglob('*')):
        if path.is_file():
            raw = path.read_bytes()
            rel = path.relative_to(ROOT).as_posix()
            target = CLOSURE / 'final-bundle' / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            bundle.append({'path': rel, 'bytes': len(raw), 'sha256': sha(raw)})
    save('final-bundle-manifest.json', {'files': bundle, 'pre_first_build_bundle_saved': False, 'limitation': 'dist was allowed build output but its pre first-build bytes were not saved; do not infer them from HEAD'})

    received = json.loads((ROOT / 'DocuN/evidence/TASK-114/orchestration-20261012/input-manifest.json').read_bytes())
    verification = []
    for v in received['context']:
        path = Path(v['path'])
        verification.append({'path': str(path), 'expected': v['sha256'], 'actual': sha(path.read_bytes()), 'match': sha(path.read_bytes()) == v['sha256']})
    pins = json.loads((ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    for v in pins:
        path = Path(v['absolute_path'])
        verification.append({'path': str(path), 'expected': v['sha256'], 'actual': sha(path.read_bytes()), 'match': sha(path.read_bytes()) == v['sha256']})
    save('locked-inputs-observed.json', verification)

    journal = ROOT / 'DocuN/evidence/TASK-114/synthetic/control-root/journal.bin'
    raw = journal.read_bytes()
    pos, previous, events, incomplete = 0, '0' * 64, [], False
    canon = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    while pos < len(raw):
        if len(raw) - pos < 4:
            incomplete = True
            break
        length = struct.unpack('!I', raw[pos:pos+4])[0]
        if not 1 <= length <= 65536:
            raise ValueError('journal length not valid')
        end = pos + 4 + length
        tail_end = end + 73
        if tail_end > len(raw):
            incomplete = True
            break
        body = raw[pos+4:end]
        if raw[end:tail_end] != b'\nCOMMIT:' + sha(body).encode('ascii') + b'\n':
            raise ValueError('journal COMMIT/hash not valid')
        event = json.loads(body)
        if event['seq'] != len(events)+1 or event['prev_hash'] != previous or event['body_hash'] != sha(canon(event['payload'])) or body != canon(event):
            raise ValueError('journal sequence or canonical chain not valid')
        events.append(event)
        previous, pos = sha(body), tail_end
    state = {'jobs': {}, 'targets': {}, 'plans': {}, 'selection': None, 'fence': None}
    for event in events:
        kind, payload = event['kind'], event['payload']
        if kind in ('job.create', 'job.update'):
            key = payload['job_id']; state['jobs'][key] = {**state['jobs'].get(key, {}), **payload}
        elif kind in ('target.register', 'target.seal'):
            key = payload['target_id']; state['targets'][key] = {**state['targets'].get(key, {}), **payload}
        elif kind == 'plan.create':
            state['plans'][payload['plan_id']] = payload
        elif kind == 'selector_commit':
            state['selection'] = payload
        elif kind == 'maintenance.fence':
            state['fence'] = payload
    job_keys = ('job_id', 'business_key', 'kind', 'state', 'stage', 'revision', 'package_id', 'root_sha256', 'target_id', 'error_code')
    target_keys = ('target_id', 'job_id', 'slot_id', 'profile_id', 'state', 'cid', 'name', 'port')
    save('hub-readonly-observation.json', {
        'journal_sha256': sha(raw), 'journal_bytes': len(raw), 'committed_frames': len(events), 'unconfirmed_tail': incomplete,
        'read_method': 'standard_library_raw_frame_hash_chain; no_ControlHub_constructor_or_product_import',
        'journal_changed': journal.read_bytes() != raw,
        'jobs': [{k: v[k] for k in job_keys if k in v} for v in state['jobs'].values()],
        'targets': [{k: v[k] for k in target_keys if k in v} for v in state['targets'].values()],
        'plan_ids': list(state['plans']), 'selector_commit_observed': state['selection'] is not None,
        'maintenance_fence_observed': state['fence'] is not None,
        'credentials_decrypted': False,
    })
    packages = []
    for path in sorted((ROOT / 'DocuN/evidence/TASK-114/synthetic/backup-root/packages').glob('*.rldata')):
        with zipfile.ZipFile(path) as archive:
            m = json.loads(archive.read('manifest.json'))
            # Identity inventory only; no repeat of the former product verification method.
            row_counts = {name[8:-6]: len(archive.read(name).splitlines()) for name in archive.namelist() if name.startswith('records/') and name.endswith('.jsonl')}
            control_counts = {name: len(archive.read(name).splitlines()) for name in archive.namelist() if name.startswith('metadata/') and name.endswith('.jsonl')}
            packages.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes()),
                             'package_id': m['package_id'], 'root_sha256': m['root_sha256'], 'codec_profile': m['codec_profile'],
                             'completion': m['completion'], 'package_kind': m['package_kind'], 'snapshot': m['snapshot'],
                             'manifest_contents': len(m['contents']), 'archive_members': len(archive.infolist()),
                             'business_row_counts': row_counts, 'control_row_counts': control_counts,
                             'source_business_table_count': m['source_business_table_count'], 'snapshot_control_domain_count': m['snapshot_control_domain_count'],
                             'manifest_has_unicode_replacement': '\ufffd' in json.dumps(m, ensure_ascii=False)})
    save('package-identities.json', packages)
    events = [json.loads(line) for line in (CONTROL / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
    save('command-and-resource-events.json', events)
    save('sealing-result.json', {'utc': datetime.now(timezone.utc).isoformat(), 'modified_count': len(changed), 'added_count': len(added), 'final_file_count': len(manifest), 'bundle_files': len(bundle), 'locked_inputs_all_match': all(v['match'] for v in verification), 'receipt_unchanged': (CONTROL / 'receipt.json').read_bytes() == receipt_raw, 'product_tests_or_starts': 0})
    print(json.dumps({'closure': str(CLOSURE), 'modified_count': len(changed), 'added_count': len(added), 'final_file_count': len(manifest), 'inputs_all_match': all(v['match'] for v in verification), 'source_running': observation.get('running'), 'source_identity_match': observation.get('identity_matches_receipt'), 'listeners': observation['task_port_listeners'], 'elapsed_seconds': elapsed, 'counts': receipt['counts']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
