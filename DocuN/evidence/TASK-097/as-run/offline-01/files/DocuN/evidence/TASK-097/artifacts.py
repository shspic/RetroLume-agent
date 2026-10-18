"""本卡证据工具；产品不导入，快照不含私有配置或运行凭据。"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
E = ROOT / "DocuN/evidence/TASK-097"
PY = ROOT / "backend/.venv/Scripts/python.exe"


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def files():
    selected = []
    for directory, pattern in [("backend/app", "*.py"), ("backend/tests/fixtures/task097", "*"),
        ("frontend/src", "*"), ("frontend/dist", "*"), ("DocuN/evidence/TASK-097", "*.py")]:
        selected += [p for p in (ROOT / directory).rglob(pattern) if p.is_file()
            and "__pycache__" not in p.parts and not p.name.endswith(".pyc") and "as-run" not in p.parts
            and "pre" not in p.parts and "final" not in p.parts]
    selected += list((ROOT / "backend/tests").glob("test_learning_*.py"))
    selected += list((ROOT / "frontend/tests").glob("task097-*.mjs"))
    selected += [ROOT / f for f in ["README.md", "config/activity.example.json", "backend/requirements.lock", "frontend/package.json",
        "frontend/package-lock.json", "DocuN/evidence/TASK-097/implementation-contract.md",
        "backend/tests/test_retrieval.py", "backend/tests/test_worker_one_call.py", "backend/tests/test_worker_one_tool.py",
        "backend/tests/test_activity_workspace_config.py"]]
    selected += list((ROOT / "backend/migrations").glob("00[1-8]_*.sql"))
    return sorted(set(p for p in selected if p.is_file()))


def freeze(label, command, expected):
    target = E / "as-run" / label
    if target.exists():
        raise ValueError("快照标签已存在，不能覆盖历史")
    manifest = []
    for src in files():
        relative = src.relative_to(ROOT)
        dst = target / "files" / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        manifest.append({"path": relative.as_posix(), "sha256": digest(src), "bytes": src.stat().st_size})
    write(target / "manifest.json", {"at": stamp(), "command": command, "expected": expected, "files": manifest})
    return target


def append_event(value):
    path = E / "attempt-ledger.json"
    history = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else []
    history.append({"at": stamp(), **value})
    write(path, history)


def imported_modules():
    result = []
    for name, module in sorted(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename and name.startswith(("app.", "tests.test_learning", "tests.fixtures.task097")):
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT) and path.is_file():
                result.append({"module": name, "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)})
    return result


def offline(label, command, expected, timeout=60, cwd=None):
    snapshot = freeze(label, command, expected)
    start = time.monotonic()
    result = subprocess.run(command, cwd=cwd or ROOT, capture_output=True, timeout=timeout)
    elapsed = time.monotonic() - start
    (snapshot / "stdout.bin").write_bytes(result.stdout)
    (snapshot / "stderr.bin").write_bytes(result.stderr)
    write(snapshot / "run.json", {"start": stamp(), "exit_code": result.returncode, "elapsed_seconds": elapsed,
        "post_hashes": {p.relative_to(ROOT).as_posix(): digest(p) for p in files()}})
    append_event({"category": "offline", "label": label, "command": command, "seconds": elapsed, "exit_code": result.returncode})
    print(result.stdout.decode("utf-8", "replace"))
    print(result.stderr.decode("utf-8", "replace"))
    print(json.dumps({"label": label, "elapsed_seconds": elapsed, "exit_code": result.returncode}))
    return result.returncode


if __name__ == "__main__":
    label = sys.argv[1]
    command = sys.argv[2:]
    raise SystemExit(offline(label, command, "本卡定向离线检查，无PG/模型/业务监督/浏览器启动"))
