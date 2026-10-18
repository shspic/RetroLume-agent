# TASK-084 有限差异与证据适用性

- Git基线 `45951501d2741630a229762d6b2d3f4b34d7f702`；`git status --short --untracked-files=all` 显示七个 `backend/app/worker/*.py`、005、`backend/tests/fixtures/task083/*.py`、`test_activity_dispatch_close.py`、`test_worker_session.py` 均是未跟踪新文件，已按实际文件逐个阅读；不能以 `git diff` 未列出当作不存在。既有 `repository.py`、`activities/__init__.py`、`test_activity_time_budget.py` 有改动。无审计方Git写入。
- `offline-repair-01/pre-hashes.txt` 至 `final-hashes.txt`：`session.py` 8E99…→D317…、`windows_job.py` 3D0B…→D05C…、`gate.py` 2186…→7E75…、`worker/__init__.py` 70B1…→E2E3…、`test_worker_session.py` 010D…→0AC7…、`fixture.py` B3FC…→D511…；新增`command.py`、`launcher.py`、`job_control.py`、`offline_unit.py`、`run_offline.py`和PG夹具。有限 `git diff --no-index` 已对照补足前 `session.py`、`windows_job.py`、`test_worker_session.py`，确认旧Job结果字段、命令接口、收尾与04控制器均改变。
- `offline-repair-01/static.log` 中静态检查时 `command.py=8763…`、`launcher.py=5A19…`、`session.py=B510…`、`test_worker_session.py=1F9C…`、`fixture.py=A42E…`、`job_control.py=5BC8…`、`offline_unit.py=2C59…`，与最终16文件清单对应值均不同；该日志只证当时快照，不能证最终快照AST或行为。`unit-recheck.log`只复检当时的纯单元05；最后源码改动后未见最终快照纯单元运行证据。
- 原Job初批5场景/2失败，`job-initial.log` 的01结果为 `failed_closed`、04未取得worker句柄且单命令141.328秒；`cleanup-process-check.txt` 的`owned_python_process_count=0`只能说明当时筛选结果。02、03、05仅保留旧代码局部行为观察，不能扩展为最终快照身份/归属/截止证明。

完整冻结哈希与现场匹配见 `hashes.txt`；本文件只记录影响本次审计的有限差异。
