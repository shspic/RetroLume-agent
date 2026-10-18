"""TASK-083 fixture-completion-06 one-shot static check (single execution quota).

Text/AST/hash only: no fixture import, no test run, no pyc.
Covers per card: whole-flow text consistency, bounded diff, one AST+hash pass,
freeze drift check on card-named files.
"""
import ast
import difflib
import hashlib
import time
from pathlib import Path

T0 = time.perf_counter()
ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
SRC = ROOT / "backend/tests/fixtures/task083"
EV = ROOT / "Ndocu/evidence/task-083/fixture-completion-06"
PRE_COPY = EV / "pre" / "pre__focused_unit.py"

pre_bytes = PRE_COPY.read_bytes()
post_bytes = (SRC / "focused_unit.py").read_bytes()
pre_text = pre_bytes.decode("utf-8")
post_text = post_bytes.decode("utf-8")

checks = []
def check(name, cond):
    checks.append(name)
    if not cond:
        raise SystemExit(f"STATIC CHECK FAIL: {name}")

# --- hashes & freeze drift ---
pre_hash = hashlib.sha256(pre_bytes).hexdigest()
post_hash = hashlib.sha256(post_bytes).hexdigest()
check("pre copy hash == card freeze 4a633aff...7a1ca",
      pre_hash == "4a633aff536f833cdbf3a266be2d44de70b8e01105a204b68d7947995627a1ca")
check("post hash != pre hash (file actually changed)", post_hash != pre_hash)
for name, expect in {
    "job_control.py": "5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2",
    "offline_unit.py": "3029a709f615ab068d65004d1083568d0a96e577417380b26109defaf0a64c5c",
}.items():
    check(f"freeze unchanged: {name}",
          hashlib.sha256((SRC / name).read_bytes()).hexdigest() == expect)

# --- scope containment: only StartLifecycleTests section changed ---
def split_section(text):
    head, rest = text.split("class StartLifecycleTests", 1)
    mid, tail = rest.split("class FrameTests", 1)
    return head, "class StartLifecycleTests" + mid, "class FrameTests" + tail

pre_head, pre_mid, pre_tail = split_section(pre_text)
post_head, post_mid, post_tail = split_section(post_text)
check("outside section unchanged: head (module docstring/imports/EventControlTests)", pre_head == post_head)
check("outside section unchanged: tail (FrameTests/ConfigFactory/LauncherTests/main)", pre_tail == post_tail)
check("inside section actually changed", pre_mid != post_mid)

# --- AST: parse only, no import ---
tree = ast.parse(post_text)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "StartLifecycleTests")
methods = {n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
check("hardcoded _identity_lines removed", "_identity_lines" not in methods)
check("three methods present",
      {"_run", "test_04_start_handle_closes_after_identity_receipt",
       "test_04_start_handle_release_exactly_once_on_failure"} <= methods)
run_fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_run")
rets = [n for n in ast.walk(run_fn) if isinstance(n, ast.Return) and isinstance(n.value, ast.Tuple)]
check("_run has exactly one 5-tuple return", len(rets) == 1 and len(rets[0].value.elts) == 5)

# --- fix 1: derived identity from real spawn args + real job_name receipt ---
check("derive activity from args[4]", 'identity["activity_id"] = args[4]' in post_mid)
check("derive generation from args[5] as int", 'identity["generation"] = int(args[5])' in post_mid)
check("derive run_tag from args[6]", 'identity["run_tag"] = args[6]' in post_mid)
check("receipt built with real job_name(activity, generation)",
      '"job_name": job_name(identity["activity_id"], identity["generation"])' in post_mid)
check("protocol fields preserved (pid/created_100ns/active_processes)",
      '"pid": 123, "created_100ns": 0, "active_processes": 1' in post_mid)
check("resumed receipt preserved", '{"phase": "resumed", "pid": 123}' in post_mid)
check("no hardcoded activity UUID left", "11111111" not in post_mid)
check("no hardcoded run_tag left", "lifecycle-unit" not in post_mid)

# cross-file: derivation indexes match the real job_control.py call site
jc = (SRC / "job_control.py").read_text(encoding="utf-8")
check("job_control spawn argv order matches derivation indexes (args[4..6])",
      'sys._base_executable, "-B", str(fixture), "controller", activity_id, str(generation), run_tag, start_name,' in jc)
check("job_control open_existing passes int generation",
      "parent_job = NamedJob.open_existing(activity_id, generation)" in jc)
check("job_control identity tuple unchanged (no contract weakening)",
      'expected = ("suspended", activity_id, generation, run_tag, job_name(activity_id, generation))' in jc)

# patch targets: exactly the three OS boundaries; no uuid4 patch, no controller identity pinning
check("no job_control.uuid4 patch", "job_control.uuid4" not in post_mid)
for target in ("job_control.ctypes.WinDLL", "job_control.asyncio.create_subprocess_exec", "job_control.NamedJob"):
    check(f"patch target kept: {target}", f'"{target}"' in post_mid)

# --- fix 2: _run returns identity; open_existing assertions use derived identity ---
check("success-case assertion uses derived identity",
      'log.index(("open_existing", identity["activity_id"], 7))' in post_mid)
check("failure-case negative assertion uses derived identity",
      'assertNotIn(("open_existing", identity["activity_id"], 7), log)' in post_mid)
check("old hardcoded activity assertions gone", '("open_existing", activity, 7)' not in post_mid)
check("spawn-error branch defines empty derived identity explicitly",
      'self.assertEqual(identity, {})' in post_mid)

# --- fix 3: disjoint handle base addresses ---
check("Kernel takes base parameter", "def __init__(self, base):" in post_mid)
check("base split per WinDLL instance (100 / 100100)",
      "Kernel(base=100 + 100000 * len(kernels))" in post_mid)
check("old shared base literal gone", "self._next = 100" not in post_mid)

# --- receipt mode definitions ---
check("receipt modes defined", 'def _run(self, *, receipt="identity", spawn_error=None):' in post_mid)
check("identity-mode receipt gating", 'if receipt == "identity":' in post_mid)

# --- artifacts: bounded unified diff + final hashes + check report ---
diff_lines = list(difflib.unified_diff(
    pre_text.splitlines(keepends=True), post_text.splitlines(keepends=True),
    fromfile="pre__focused_unit.py (4a633aff...)", tofile="focused_unit.py post-fix-06", n=3))
(EV / "incremental.diff").write_text("".join(diff_lines), encoding="utf-8")
(EV / "final-hashes.txt").write_text(
    "# fixture-completion-06 final hashes (managed Python 3.13.12 hashlib)\n"
    f"{post_hash}  backend/tests/fixtures/task083/focused_unit.py  (pre=4a633aff...7a1ca, StartLifecycleTests section only)\n"
    f"{hashlib.sha256((SRC / 'job_control.py').read_bytes()).hexdigest()}  backend/tests/fixtures/task083/job_control.py  == frozen unchanged\n"
    f"{hashlib.sha256((SRC / 'offline_unit.py').read_bytes()).hexdigest()}  backend/tests/fixtures/task083/offline_unit.py  == frozen unchanged\n",
    encoding="utf-8")
elapsed = time.perf_counter() - T0
report = ([f"fixture-completion-06 static check: ALL_PASS ({len(checks)} checks, {elapsed:.3f}s, single execution)"]
          + [f"PASS  {n}" for n in checks] + [f"post_sha256={post_hash}"])
(EV / "static-check.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
