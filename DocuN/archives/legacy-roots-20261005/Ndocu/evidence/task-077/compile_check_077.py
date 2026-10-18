import sys

files = [
    r"D:\shspic\project_NO3_RetroLume-agent\backend\app\activities\repository.py",
    r"D:\shspic\project_NO3_RetroLume-agent\backend\app\activities\__init__.py",
    r"D:\shspic\project_NO3_RetroLume-agent\backend\tests\test_activity_ledger.py",
    r"D:\shspic\project_NO3_RetroLume-agent\backend\tests\test_activity_recovery.py",
    r"D:\shspic\project_NO3_RetroLume-agent\backend\tests\test_activity_time_budget.py",
]
for path in files:
    with open(path, encoding="utf-8") as handle:
        compile(handle.read(), path, "exec")
print("COMPILE_OK", len(files))
sys.exit(0)
