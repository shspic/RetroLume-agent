"""最终差异、真实方法索引及原字节后缀保存；不接触PG、旧业务Hub/selector。"""
from datetime import datetime, timezone
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
from c03_support import C03Budget, ROOT, EVIDENCE, CONTROL, save, sample


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def capture():
    before = json.loads((EVIDENCE / 'pre-manifest.json').read_text(encoding='utf-8'))
    previous = {entry['path']: entry for entry in before}
    files = set(previous)
    files.update(path.relative_to(ROOT).as_posix() for path in (ROOT / 'backend/tests/fixtures/task114').glob('c03*.py'))
    files.update(('backend/tests/test_data_exit_c03.py', 'frontend/tests/task114-c03-inputs.mjs'))
    files.update(path.relative_to(ROOT).as_posix() for path in (ROOT / 'frontend/dist').rglob('*') if path.is_file())
    destination = EVIDENCE / 'final'; destination.mkdir()
    manifest = []
    allowed_modified = {'backend/app/data_exit/reference.py', 'backend/app/data_exit/restore.py', 'frontend/src/data/DataWorkspace.tsx'}
    for name in sorted(files):
        path = ROOT / name; pre = previous.get(name)
        current = {'path': name, 'exists': path.is_file()}
        if current['exists']:
            current.update(identity(path)); target = destination / 'source' / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        status = ('added' if current['exists'] else 'absent') if pre is None else (
            'unchanged' if current['exists'] == pre['exists'] and (not current['exists'] or current['sha256'] == pre['sha256'])
            else 'modified' if current['exists'] and pre['exists'] else 'added' if current['exists'] else 'removed')
        current['status'] = status; current['before'] = pre
        if status == 'modified' and name not in allowed_modified and not name.startswith('frontend/dist/'):
            raise RuntimeError('冻结文件发生未授权变更 ' + name)
        if status == 'removed' and not name.startswith('frontend/dist/'):
            raise RuntimeError('非构建原件被移除 ' + name)
        if status in ('added', 'modified', 'removed'):
            old = (EVIDENCE / 'pre' / name).read_bytes() if pre and pre['exists'] else b''
            new = path.read_bytes() if path.is_file() else b''
            diff = ''.join(difflib.unified_diff(old.decode('utf-8').splitlines(keepends=True), new.decode('utf-8').splitlines(keepends=True), fromfile='pre/' + name, tofile='final/' + name))
            target = destination / 'diff' / (name + '.diff'); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(diff, encoding='utf-8')
        manifest.append(current)
    save(destination / 'manifest.json', {'captured': sample(), 'files': manifest})
    methods = [json.loads(path.read_text(encoding='utf-8')) for path in sorted((EVIDENCE / 'methods').glob('*.json')) if not path.name.endswith('-begin.json')]
    for path in sorted((EVIDENCE / 'batches').glob('*/method.json')):
        methods.append(json.loads(path.read_text(encoding='utf-8')))
    assert methods and all(isinstance(method['argv'], list) and method['end'] and 'exit_code' in method for method in methods)
    for method in methods:
        as_run = json.loads((ROOT / method['as_run'] / 'manifest.json').read_text(encoding='utf-8'))
        by_path = {item['path']: item for item in as_run['files']}
        relevant = ['backend/app/data_exit/reference.py', 'backend/app/data_exit/restore.py'] if method['label'].startswith('loading-pin') else ['frontend/src/data/DataWorkspace.tsx']
        if method['label'].startswith('c03-browser'):
            relevant += [item['path'] for item in manifest if item['exists'] and item['path'].startswith('frontend/dist/')]
            relevant.append('frontend/tests/task114-c03-inputs.mjs')
        method['final_binding'] = {name: by_path.get(name, {}).get('sha256') == identity(ROOT / name)['sha256'] for name in relevant}
    save(destination / 'method-index.json', {'methods': methods, 'offline_exact': [method for method in methods if method['root'] == 'c03-check-group'],
          'browser_exact': [method for method in methods if method['root'] == 'c03-browser-group'],
          'no_new_PG_SQL_API_Vite_listener_Native_preview_provider_fees_public_network': True})
    old_rule = json.loads((ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    assert all(identity(Path(rule['absolute_path']))['sha256'] == rule['sha256'] for rule in old_rule)
    input_manifest = json.loads((EVIDENCE / 'input-manifest.json').read_text(encoding='utf-8-sig'))
    for key in ('root_entry', 'adopted_contract', 'audit_report', 'C02_final_manifest'):
        original = input_manifest[key]
        assert identity(Path(original['path'])) == {key: original[key] for key in ('bytes', 'sha256')}
    old_reference = ast.parse((EVIDENCE / 'pre/backend/app/data_exit/reference.py').read_text(encoding='utf-8'))
    new_reference = ast.parse((ROOT / 'backend/app/data_exit/reference.py').read_text(encoding='utf-8'))
    prior_pin = next(node for node in old_reference.body if isinstance(node, ast.ClassDef) and node.name == 'ReferencePin')
    final_pin = next(node for node in new_reference.body if isinstance(node, ast.ClassDef) and node.name == 'ReferencePin')
    assert ast.dump(prior_pin) == ast.dump(final_pin)
    old_receipt = json.loads((EVIDENCE / 'pre/receipt.json').read_text(encoding='utf-8')); current = C03Budget().load()
    assert current['resources'][:len(old_receipt['resources'])] == old_receipt['resources']
    assert current['continuation_history'] == old_receipt['continuation_history'] + [old_receipt['continuation']]
    assert current['received_utc'] == old_receipt['received_utc'] and current['received_monotonic_ns'] == old_receipt['received_monotonic_ns']
    assert (CONTROL / 'events.jsonl').read_bytes().startswith((EVIDENCE / 'pre/events.jsonl').read_bytes())
    save(destination / 'inheritance.json', {'seven_rules_match': True, 'ordinary_ReferencePin_AST_unchanged': True,
        'old_resources_exact_unchanged': True, 'old_continuations_exact_preserved': True, 'old_events_byte_prefix_preserved': True,
        'audit_and_adopted_contract_unchanged': True, 'actual_modified_files': [entry['path'] for entry in manifest if entry['status'] == 'modified'],
        'PG_applicability': '无新增PG；原两秒样本仅继承读取阶段过D拒绝/无发布；新pin传播以受控连接参数/实际_load原件子路径闭合，不称真实PG等待上界或恢复主链复跑'})
    return manifest, methods


def deliver():
    budget = C03Budget(); budget.check(cleanup=True)
    manifest = json.loads((EVIDENCE / 'final/manifest.json').read_text(encoding='utf-8'))['files']
    for entry in manifest:
        path = ROOT / entry['path']; assert path.is_file() == entry['exists']
        if entry['exists']: assert identity(path) == {key: entry[key] for key in ('bytes', 'sha256')}
    current = budget.load()
    assert all(r['state'] == 'stopped' and r['end_ns'] is not None for r in current['resources'])
    new_resources = current['resources'][len(json.loads((EVIDENCE / 'pre/receipt.json').read_text(encoding='utf-8'))['resources']):]
    assert all(r['last_stop']['process_ended'] and r['last_stop']['actual_browser_close'] for r in new_resources)
    result = ROOT / 'DocuN/results/TASK-114-result.md'; prior = (EVIDENCE / 'pre/TASK-114-result.md').read_bytes()
    if result.read_bytes() != prior:
        checkpoint = json.loads((EVIDENCE / 'checkpoint.json').read_text(encoding='utf-8'))
        assert identity(result) == checkpoint['result_identity'] and result.read_bytes().endswith(prior)
    assert len(prior) == 69598 and hashlib.sha256(prior).hexdigest() == 'e457d13159c439da8c56814b4f9c860973c0ff5d8622793ab4663584ffe5ad11'
    prefix = (EVIDENCE / 'report-prefix.md').read_bytes(); result.write_bytes(prefix + prior)
    assert result.read_bytes().endswith(prior)
    end = sample(); continuation = current['continuation']
    for root in continuation['real_batches']:
        if root['end_ns'] is None: root['end_ns'] = end['mono_ns']
    segment = continuation['active_segments'][-1]; segment.update(end_ns=end['mono_ns'], end_utc=end['utc'], end_reason='C03完整结果保存/准确新Browser关闭/旧字节核对完成')
    continuation.update(status='delivered_candidate_for_TASK115_two_defect_incremental_review', result_sha256=identity(result)['sha256'])
    if continuation.get('external_block'):
        continuation['external_block']['resolution'] = {'utc': end['utc'], 'state': 'resolved_before_final_browser', 'basis': '实际Browser方法入口内存达门，正常browser.close和精确PID/birth结束已证'}
    budget.save(current)
    active = sum((s['end_ns'] - s['begin_ns']) / 1e9 for s in continuation['active_segments'])
    delivery = {'saved': end, 'result': str(result), **identity(result), 'old_suffix_identity': identity(EVIDENCE / 'pre/TASK-114-result.md'),
        'old_suffix_exact': True, 'counts': current['counts'], 'active_C03_seconds_conservative': active,
        'active_C02_plus_C03_seconds': active + 9188.720111, 'offline_cumulative_seconds': current['offline_seconds'],
        'offline_C03_seconds': current['offline_seconds'] - continuation['baseline_offline_seconds'],
        'holding_cumulative_seconds': current['real_holding_seconds'], 'holding_C03_seconds': current['real_holding_seconds'] - continuation['baseline_holding_seconds'],
        'roots': continuation['real_batches'], 'new_resource_closure': new_resources, 'status': continuation['status'],
        'current_files': sum(entry['exists'] for entry in manifest), 'prior_stopped_is_inherited_not_live_Docker_observation': True}
    save(EVIDENCE / 'final/delivery.json', delivery); budget.event('c03.delivered', delivery)
    print(json.dumps(delivery, ensure_ascii=False))


if __name__ == '__main__':
    if sys.argv[1] == 'capture':
        files, methods = capture(); print(json.dumps({'files': len(files), 'methods': len(methods)}))
    elif sys.argv[1] == 'deliver': deliver()
    else: raise ValueError('只接受capture/deliver')
