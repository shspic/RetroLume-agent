"""TASK-077 / R-071 修正轮02：N1 最小验证——真实 ActivityLease 构造检查。

约束（按任务卡）：
- 导入实际产品数据类 app.activities.repository.ActivityLease，不复制、不 mock；
- 不实例化仓储、不连接数据库、不读配置或环境密钥、不写 pyc；
- 用合成 activity_id / executor_id / generation / scope_revision / datetime
  及 79 作为第六位置参数构造一次，断言 window_seconds==79 且其余字段按位置保留。
"""

import dataclasses
import hashlib
import os
import sys
import time
from datetime import datetime, timezone

sys.dont_write_bytecode = True

REPO_REL = os.path.join("app", "activities", "repository.py")


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


started = time.perf_counter()
repo_path = os.path.abspath(REPO_REL)
tested_hash = sha256(repo_path)
print("[hash_under_test] %s  %s" % (REPO_REL, tested_hash))

# 直接导入链静态检查结论已在卡内登记：app/__init__.py 为空；repository.py 仅在
# _transaction 内惰性导入 psycopg；顶层无 connect / getenv / environ / open 调用。
from app.activities.repository import ActivityLease  # noqa: E402

# --- 1. 字段存在性、类型注解与顺序（返回契约） ---
fields = [f.name for f in dataclasses.fields(ActivityLease)]
annotations = {f.name: f.type for f in dataclasses.fields(ActivityLease)}
expected_order = [
    "activity_id",
    "executor_id",
    "execution_generation",
    "scope_revision",
    "lease_expires_at",
    "window_seconds",
]
assert fields == expected_order, "字段顺序不符: %r" % (fields,)
print("[fields] %s" % (fields,))
# repository.py 使用 from __future__ import annotations，注解可能以字符串形式暴露。
window_annotation = annotations["window_seconds"]
print("[annotation] window_seconds -> %r" % (window_annotation,))
assert window_annotation in ("int", int), "window_seconds 注解必须是 int"

# --- 2. frozen=True 保留，且为必填（无默认值） ---
params = ActivityLease.__dataclass_params__
assert params.frozen is True, "frozen=True 未保留"
missing = object()
default = getattr(ActivityLease, "window_seconds", missing)
assert default is missing, "window_seconds 不应有类属性默认值"
print("[frozen] %s" % (params.frozen,))

# --- 3. 六位置参数真实构造 ---
activity_id = "11111111-1111-4111-8111-111111111111"
executor_id = "revision02-synthetic-executor"
generation = 7
scope_revision = 3
lease_expires_at = datetime(2026, 9, 23, 1, 0, 0, tzinfo=timezone.utc)
window_seconds_arg = 79

lease = ActivityLease(
    activity_id,
    executor_id,
    generation,
    scope_revision,
    lease_expires_at,
    window_seconds_arg,
)

assert lease.activity_id == activity_id
assert lease.executor_id == executor_id
assert lease.execution_generation == generation
assert lease.scope_revision == scope_revision
assert lease.lease_expires_at == lease_expires_at
assert lease.window_seconds == 79, "window_seconds 取值错误: %r" % (lease.window_seconds,)
print("[constructed] %r" % (lease,))

# --- 4. frozen 语义：赋值必须失败 ---
try:
    lease.window_seconds = 1
except dataclasses.FrozenInstanceError:
    print("[frozen_enforced] FrozenInstanceError raised as expected")
else:
    raise AssertionError("frozen 数据类可被赋值，契约破坏")

# --- 5. 调用点位置一致性：claim 成功路径第六实参必须与第六字段同序 ---
with open(repo_path, encoding="utf-8") as fh:
    source_lines = fh.read().splitlines()

call_index = None
for index, line in enumerate(source_lines):
    if line.strip() == "return ActivityLease(":
        call_index = index
        break
assert call_index is not None, "未找到 ActivityLease 构造点"

call_block = []
for line in source_lines[call_index + 1 :]:
    stripped = line.strip()
    if stripped == ")":
        break
    call_block.append(stripped)
call_args = [arg.rstrip(",") for arg in call_block]
print("[call_site_line] %d" % (call_index + 1,))
print("[call_args] %s" % (call_args,))
assert len(call_args) == 6, "构造点实参个数应为 6，实际 %d" % (len(call_args),)
assert call_args[-1] == "effective_window", "第六实参应为 effective_window"
assert call_args[4] == "lease_expires_at", "第五实参应为 lease_expires_at"

elapsed_ms = (time.perf_counter() - started) * 1000.0
print("[RESULT] PASS window_seconds==79 positional_contract_ok")
print("[hash_under_test_after] %s" % (sha256(repo_path),))
print("[elapsed_ms] %.1f" % (elapsed_ms,))
