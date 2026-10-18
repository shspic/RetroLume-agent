"""TASK-083 stub-fix-05 静态检查（不import项目模块、不写pyc，仅AST/文本/hash）。

核对项：
1. 新focused_unit.py语法可解析（AST parse）。
2. 从冻结的job_control.py AST逐项提取verify_last_handle与_new_event_or_reject
   对WinDLL替身实例（starter/kernel）的属性赋值（argtypes/restype）与调用面，
   证明StartLifecycleTests局部Kernel替身对每个API均以partial包装、方法齐备。
3. 局部不变性：除新增functools导入、StartLifecycleTests docstring附加说明、
   Kernel.__init__ partial包装外，其余顶层节点AST与改前副本逐字节结构一致。
4. 冻结防漂移：job_control.py/offline_unit.py及fixture-repair-04/final-hashes.txt
   的13个未改文件hash逐一复算。
5. 生成incremental.diff与final-hashes.txt。
"""
import ast
import difflib
import hashlib
import sys
import time
from pathlib import Path

T0 = time.perf_counter()

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
PRE_COPY = HERE / "pre" / "backend__tests__fixtures__task083__focused_unit.py"
NEW = ROOT / "backend/tests/fixtures/task083/focused_unit.py"
JOB_CONTROL = ROOT / "backend/tests/fixtures/task083/job_control.py"

EXPECTED_8 = {"CreateEventW", "SetEvent", "CloseHandle", "OpenProcess",
              "GetProcessTimes", "OpenEventW", "WaitForSingleObject", "TerminateProcess"}

FROZEN = {
    "backend/tests/fixtures/task083/job_control.py": "5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2",
    "backend/tests/fixtures/task083/offline_unit.py": "3029a709f615ab068d65004d1083568d0a96e577417380b26109defaf0a64c5c",
    "backend/app/worker/launcher.py": "703ceb0344e21a174f3d70e81b05ede5635d700ed84f53e26e9ae70037d2acea",
    "backend/app/worker/supervisor_ipc.py": "57be00aead15114673b180b1abb436dde10ef426a618d56f30d0031e3201ac96",
    "backend/app/worker/supervisor_main.py": "98c420e75671b3ad1823ea5a72a3866221e7cb0fc1defe032feb0a5822afb145",
    "backend/app/worker/session.py": "502a37436de83fa5e56636d54ae5a4f694639f18c5e474e02749162e4e15f16c",
    "backend/app/worker/command.py": "b0e91c3a2e65de19656b3c902df49a33bdd29dc135bc9c292e7732e300a5e273",
    "backend/app/worker/worker_main.py": "5d065b5e44b678c08dc34c9e611a5dcaaa2d0aa3ed2c6e588fe7a70ca25a1454",
    "backend/app/worker/gate.py": "7e7588a58869038f53d850816c027aab00ecd1270d2c893d1fc4902978d32674",
    "backend/app/worker/windows_job.py": "d05ca259d5c99e6cc8f67c7fcea01667068a2901066b865239e920bd0f5246f6",
    "backend/app/activities/repository.py": "929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20",
    "backend/migrations/005_activities_dispatch_closed.sql": "26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb",
    "backend/tests/fixtures/task083/fixture.py": "c9970b8ddc718da1a4e83c6d206a67f6bd000d715578e028c0a0964d9f53dc7f",
    "backend/tests/fixtures/task083/scenario_child.py": "98f132f272b952c22ac887efbf8026c5b00ec618838b6d484a3deec3c73f3f36",
    "backend/tests/fixtures/task083/job_batch.py": "648e419cea693aa10630326cb28176e010a82b9f2c3380c33b42169c19bdef5b",
}

failures = []


def check(label, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'} {label}{(' :: ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


pre_text = PRE_COPY.read_text(encoding="utf-8")
new_text = NEW.read_text(encoding="utf-8")
pre_tree = ast.parse(pre_text)
new_tree = ast.parse(new_text)
check("AST_OK focused_unit.py (new)", True)

# ---- 1. job_control.py：WinDLL实例上的属性赋值与调用面 ----
jc_tree = ast.parse(JOB_CONTROL.read_text(encoding="utf-8"))
assigned, called = set(), set()
DLL_BASES = {"starter", "kernel"}


def scan_dll_usage(fn_node, bases):
    for node in ast.walk(fn_node):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and t.attr in ("argtypes", "restype"):
                    inner = t.value
                    if isinstance(inner, ast.Attribute) and isinstance(inner.value, ast.Name) and inner.value.id in bases:
                        assigned.add(inner.attr)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            base = node.func.value
            if isinstance(base, ast.Name) and base.id in bases:
                called.add(node.func.attr)


for fn in jc_tree.body:
    if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name in ("verify_last_handle", "_new_event_or_reject"):
        scan_dll_usage(fn, DLL_BASES)
print(f"INFO job_control argtypes/restype assigned on: {sorted(assigned)}")
print(f"INFO job_control calls on starter/kernel: {sorted(called)}")

# ---- 2. 新focused_unit：StartLifecycleTests._run.Kernel替身 ----
sl = next(n for n in new_tree.body if isinstance(n, ast.ClassDef) and n.name == "StartLifecycleTests")
run_fn = next(n for n in sl.body if isinstance(n, ast.FunctionDef) and n.name == "_run")
kernel_cls = next(n for n in run_fn.body if isinstance(n, ast.ClassDef) and n.name == "Kernel")
methods = {n.name for n in kernel_cls.body if isinstance(n, ast.FunctionDef)}
init_fn = next(n for n in kernel_cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__")
wrapped = set()
for stmt in init_fn.body:
    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
        t, v = stmt.targets[0], stmt.value
        if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self"
                and isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "partial"
                and len(v.args) == 1 and isinstance(v.args[0], ast.Attribute)
                and isinstance(v.args[0].value, ast.Name) and v.args[0].value.id == "self"
                and v.args[0].attr == t.attr):
            wrapped.add(t.attr)
check("Kernel partial-wraps exactly the 8 APIs", wrapped == EXPECTED_8 and len(init_fn.body) == 10,
      f"wrapped={sorted(wrapped)}")
check("assigned(argtypes/restype) covered by partial wraps", assigned <= wrapped,
      f"assigned={sorted(assigned)}")
check("called APIs all exist as Kernel methods", called <= methods,
      f"called={sorted(called)} methods={sorted(methods)}")

# ---- 3. 局部不变性：改前副本 vs 新文件 ----
pre_top = {}
for n in pre_tree.body:
    if isinstance(n, ast.ClassDef) or isinstance(n, ast.FunctionDef):
        pre_top[n.name] = n
    elif isinstance(n, ast.If) and isinstance(n.test, ast.Compare):
        pre_top["__main__guard"] = n
new_top = {}
for n in new_tree.body:
    if isinstance(n, ast.ClassDef) or isinstance(n, ast.FunctionDef):
        new_top[n.name] = n
    elif isinstance(n, ast.If) and isinstance(n.test, ast.Compare):
        new_top["__main__guard"] = n

unchanged = ["EventControlTests", "FrameTests", "LauncherTests", "ConfigFactory",
             "request_data", "Mapping", "Process", "__main__guard"]
for name in unchanged:
    check(f"unchanged AST: {name}", ast.dump(pre_top[name]) == ast.dump(new_top[name]))

check("module docstring unchanged",
      ast.get_docstring(pre_tree) == ast.get_docstring(new_tree))


def import_items(tree):
    items = set()
    for n in tree.body:
        if isinstance(n, ast.Import):
            for a in n.names:
                items.add(("import", a.name))
        elif isinstance(n, ast.ImportFrom):
            for a in n.names:
                items.add((n.module or "", a.name))
    return items


pre_imp, new_imp = import_items(pre_tree), import_items(new_tree)
check("import delta exactly functools.partial", new_imp - pre_imp == {("functools", "partial")} and pre_imp - new_imp == set(),
      f"added={sorted(new_imp - pre_imp)} removed={sorted(pre_imp - new_imp)}")

check("StartLifecycleTests method set unchanged",
      {n.name for n in sl.body if isinstance(n, ast.FunctionDef)} ==
      {n.name for n in pre_top["StartLifecycleTests"].body if isinstance(n, ast.FunctionDef)})
for m in ("_identity_lines", "test_04_start_handle_closes_after_identity_receipt",
          "test_04_start_handle_release_exactly_once_on_failure"):
    pre_m = next(n for n in pre_top["StartLifecycleTests"].body if isinstance(n, ast.FunctionDef) and n.name == m)
    new_m = next(n for n in sl.body if isinstance(n, ast.FunctionDef) and n.name == m)
    check(f"unchanged AST: StartLifecycleTests.{m}", ast.dump(pre_m) == ast.dump(new_m))

pre_run = next(n for n in pre_top["StartLifecycleTests"].body if isinstance(n, ast.FunctionDef) and n.name == "_run")
pre_kernel = next(n for n in pre_run.body if isinstance(n, ast.ClassDef) and n.name == "Kernel")
pre_kernel_methods = {n.name for n in pre_kernel.body if isinstance(n, ast.FunctionDef)}
check("Kernel adds no/renames no methods", pre_kernel_methods == methods)
check("StartLifecycleTests docstring only appended",
      ast.get_docstring(sl).rstrip().startswith(ast.get_docstring(pre_top["StartLifecycleTests"]).rstrip()))


def dump_without_kernel(fn):
    body = [s for s in fn.body if not (isinstance(s, ast.ClassDef) and s.name == "Kernel")]
    clone = ast.FunctionDef(name=fn.name, args=fn.args, body=body, decorator_list=fn.decorator_list,
                            returns=fn.returns, type_comment=None, type_params=[])
    return ast.dump(clone)


check("_run body outside Kernel structurally unchanged", dump_without_kernel(pre_run) == dump_without_kernel(run_fn))

# ---- 4. 冻结hash复算 ----
new_hash = sha256(NEW)
pre_hash = sha256(PRE_COPY)
check("pre copy hash == card frozen 1e58eb03…", pre_hash == "1e58eb039eb54e0400a8a730b649fb7e450bb558bb983d27e1db1a24c2a8ce08",
      pre_hash)
for rel, expect in FROZEN.items():
    actual = sha256(ROOT / rel)
    check(f"FROZEN_OK {rel}", actual == expect, actual)
    print(f"  sha256={actual}")

# ---- 5. diff与hash清单落盘 ----
diff_lines = list(difflib.unified_diff(pre_text.splitlines(), new_text.splitlines(),
                                       fromfile="focused_unit.py@pre(1e58eb03…8ce08)",
                                       tofile="focused_unit.py@stub-fix-05(new)", lineterm=""))
(HERE / "incremental.diff").write_text("\n".join(diff_lines) + "\n", encoding="utf-8")
(HERE / "final-hashes.txt").write_text(
    "TASK-083 stub-fix-05 hashes\n"
    f"backend/tests/fixtures/task083/focused_unit.py pre_sha256={pre_hash}\n"
    f"backend/tests/fixtures/task083/focused_unit.py new_sha256={new_hash}\n"
    + "".join(f"FROZEN_OK {rel} {h}\n" for rel, h in FROZEN.items()),
    encoding="utf-8")

print(f"INFO new focused_unit sha256={new_hash}")
print(f"INFO diff_lines={len(diff_lines)}")
duration = time.perf_counter() - T0
result_text = "ALL_PASS" if not failures else "FAILED:" + ",".join(failures)
print(f"RESULT {result_text}")
(HERE / "static-meta.txt").write_text(
    "TASK-083 stub-fix-05 static check (AST/hash/diff, no import, no pyc)\n"
    "command: backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/stub-fix-05/stub_fix_05.py\n"
    f"cwd: {ROOT}\nexit_code: {0 if not failures else 1}\n"
    f"duration_perf_counter_seconds: {duration:.7f}\nresult: {result_text}\n",
    encoding="utf-8")
sys.exit(0 if not failures else 1)
