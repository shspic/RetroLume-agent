"""保存续作07接收及修改前原件；不启动资源，不追造首读时钟。"""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent

def main():
    now = time.monotonic_ns()
    utc = datetime.now(timezone.utc).isoformat()
    prior = OUT / 'pre'
    prior.mkdir(exist_ok=True)
    entries = []
    paths = [
        'DocuN/evidence/TASK-111/execution/budget.json',
        'DocuN/results/TASK-111-result.md',
        'DocuN/tasks/TASK-111.md',
        'backend/app/preview/production_supervisor.py',
        'backend/app/preview/pipe.py',
        'backend/app/preview/process.py',
        'backend/app/preview/contracts.py',
        'deploy/preview/renderer-protocol.cjs',
        'backend/tests/fixtures/task111/control.py',
        'backend/tests/fixtures/task111/core.py',
        'backend/tests/fixtures/task111/c01_seeds.py',
    ]
    for relative in paths:
        src = ROOT / relative
        raw = src.read_bytes()
        target = prior / relative.replace('/', '__')
        if target.exists():
            assert target.read_bytes() == raw, '接收原件不得覆盖'
        else:
            target.write_bytes(raw)
        entries.append(dict(path=str(src), preserved=str(target), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    b = json.loads((ROOT / paths[0]).read_text(encoding='utf-8'))
    assert b['active_batch'] is None
    assert b['counts']['real_batches'] == 18
    assert hashlib.sha256((ROOT / paths[1]).read_bytes()).hexdigest() == 'fcee65ac816c59e364f26c23d0feaec023b28a97b170e78785d16af19d4be5f4'
    public = Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
    rules = json.loads((ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8'))
    checks = []
    for item in rules:
        got = hashlib.sha256((public / item['relative_path']).read_bytes()).hexdigest()
        assert got == item['sha256'], item['relative_path']
        checks.append(dict(path=item['relative_path'], sha256=got))
    value = dict(TASK='TASK-111', R='R-105', permit='TASK-111-G11-C07-20261012', client='Codex desktop', model='系统身份 GPT-6；精确子型号无可核工具',
        role='A+，续作06工程接续，无子Agent', saved_utc=utc, saved_ns=now,
        first_clock_utc='2026-10-11T17:44:05.806977+00:00', first_clock_ns=1012109906000000,
        exact_first_read_clock_missing=True, unsampled_prelude='首两次只读工具未同步采钟；不回填精确首读；无资源启动',
        conservative_window_margin_seconds=300, receipt_script_first_failure='根parents下标6错误，只读FileNotFoundError；改为5后保存，无真实资源动作', entries=entries, seven_rules=checks, prior_counts=b['counts'], prior_time_seconds=b['time_seconds'])
    target = OUT / 'accepted.json'
    assert not target.exists(), '接收仅记录一次'
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(status='C07_ACCEPTED_PRE_PRESERVED', at_utc=utc, at_ns=now, entries=len(entries), rules=len(checks)), ensure_ascii=False))

if __name__ == '__main__':
    main()
