"""TASK-071 C 档语法检查：用 backend/.venv 解释器 compile 两个修改文件，不写 pyc。"""
import time

start = time.monotonic()
paths = (
    r"D:\shspic\project_NO3_RetroLume-agent\backend\app\activities\repository.py",
    r"D:\shspic\project_NO3_RetroLume-agent\backend\tests\test_activity_recovery.py",
)
for path in paths:
    with open(path, encoding="utf-8") as handle:
        compile(handle.read(), path, "exec")
    print("compile OK:", path)
print(f"elapsed_seconds={time.monotonic() - start:.2f}")
