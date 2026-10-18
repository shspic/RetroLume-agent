"""TASK-071 证据生成：pre 副本与当前文件的 SHA-256 与 unified diff。"""
import difflib
import hashlib

PAIRS = (
    (
        r"D:\shspic\project_NO3_RetroLume-agent\Ndocu\evidence\task-071\repository.py.pre-task071",
        r"D:\shspic\project_NO3_RetroLume-agent\backend\app\activities\repository.py",
        "backend/app/activities/repository.py",
        "Ndocu/evidence/task-071/repository.py.pre-task071",
    ),
    (
        r"D:\shspic\project_NO3_RetroLume-agent\Ndocu\evidence\task-071\test_activity_recovery.py.pre-task071",
        r"D:\shspic\project_NO3_RetroLume-agent\backend\tests\test_activity_recovery.py",
        "backend/tests/test_activity_recovery.py",
        "Ndocu/evidence/task-071/test_activity_recovery.py.pre-task071",
    ),
)


def sha256(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


with open(
    r"D:\shspic\project_NO3_RetroLume-agent\Ndocu\evidence\task-071\hashes-and-diffs.txt",
    "w",
    encoding="utf-8",
    newline="\n",
) as out:
    for pre, current, label, pre_label in PAIRS:
        out.write(f"== {label} ==\n")
        out.write(f"pre  sha256: {sha256(pre)}  ({pre_label})\n")
        out.write(f"post sha256: {sha256(current)}\n")
        with open(pre, encoding="utf-8") as handle:
            pre_lines = handle.readlines()
        with open(current, encoding="utf-8") as handle:
            current_lines = handle.readlines()
        diff = list(
            difflib.unified_diff(
                pre_lines,
                current_lines,
                fromfile=f"a/{label}",
                tofile=f"b/{label}",
            )
        )
        removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
        added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
        out.write(f"diff stat: removed={removed} added={added}\n\n")
        out.writelines(diff)
        out.write("\n\n")
print("written: Ndocu/evidence/task-071/hashes-and-diffs.txt")
