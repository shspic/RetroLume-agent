TASK-071 实际执行命令记录（PowerShell 5.1，工作目录 D:\shspic\project_NO3_RetroLume-agent）

说明：本机 Windows bash shim 存在 PATH 缺陷（mkdir/cat 等内建命令不可用，
见 2026-09-20 备忘），故全部命令改用 PowerShell 工具执行；PowerShell stdout
可能不回显，统一落盘到本目录文件后用 Read 回读。

[1] 冻结哈希核对 + 原文件备份（成功，输出见 pre-hashes.txt）
    New-Item -ItemType Directory -Force -Path Ndocu/evidence/task-071
    Get-FileHash -Algorithm SHA256 backend/app/activities/repository.py, backend/tests/test_activity_recovery.py | Format-List Path,Hash | Out-File pre-hashes.txt
    Copy-Item repository.py -> Ndocu/evidence/task-071/repository.py.pre-task071
    Copy-Item test_activity_recovery.py -> Ndocu/evidence/task-071/test_activity_recovery.py.pre-task071
    结果：
      repository.py            CC7FDDD4E685E1D3AF859C7B402D0734354CEF5675ED72F2F8ACB83C92E6DCC7（与卡内冻结值一致）
      test_activity_recovery.py 7BF924CDED794B94BDC213D255177253AF2B3948AD844F302D7BD987AE6804F4（与卡内冻结值一致）

[2] 第一次语法检查尝试（失败——工具链问题，非源码问题）
    & backend/.venv/Scripts/python.exe -c "<多行 here-string 检查代码>" | Out-File compile-check.txt
    失败原因：PowerShell 5.1 向原生命令传递多行字符串参数时换行被吞掉，
    Python 收到的 -c 代码只剩第 1 行 `for path in (`，报
    `SyntaxError: '(' was never closed`（File "<string>", line 1）。
    该报错与被检查的两个源文件无关。按卡内"有据修正后复检一次"改用脚本文件方式。

[3] 第二次语法检查（成功，输出见 compile-check.txt）
    编写 Ndocu/evidence/task-071/compile_check.py（compile(f.read(), path, "exec")，不写 pyc）
    & backend/.venv/Scripts/python.exe Ndocu/evidence/task-071/compile_check.py | Out-File compile-check.txt
    结果：
      compile OK: backend/app/activities/repository.py
      compile OK: backend/tests/test_activity_recovery.py
      elapsed_seconds=0.02（限时 60 秒内）

[4] 空行风格修正后复跑 [3]（成功，compile-check.txt 为该次最终输出）并重新生成哈希与差异
    & backend/.venv/Scripts/python.exe Ndocu/evidence/task-071/make_diffs.py | Out-File make-diffs-run.txt
    make_diffs.py 用 hashlib + difflib 生成（未使用 Git，卡内禁止）。

[5] 未执行的操作（按卡内禁令）
    未运行 Docker/PostgreSQL/uvicorn/应用/模型；未运行 unittest；未联网安装；
    未读凭据；未做 DDL/索引/依赖变更；未改正式 docu、旧证据；未用 Git。

修改后最终哈希（见 hashes-and-diffs.txt）：
  backend/app/activities/repository.py     50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6（removed=6 added=24）
  backend/tests/test_activity_recovery.py  ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246（removed=0 added=100）
