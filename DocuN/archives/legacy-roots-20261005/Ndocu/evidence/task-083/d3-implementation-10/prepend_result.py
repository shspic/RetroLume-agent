from pathlib import Path
p=Path("Ndocu/results/TASK-083-result.md")
old=p.read_bytes()
bom=b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
body=old[len(bom):]
prefix="""# TASK-083 / R-077 — D3实施10接续结果（置顶；历史原文保留）

**结论：006一列、可信SUP会话号、Job Open错误分类和受部署声明约束的旧G恢复候选代码已写入；离线定向检查通过。真实PG/Windows恢复未执行，D3完整验收条件未达到，原084独立增量审计未启动，M-1/STEP008及产品one_call接线均不能据此宣布完成。** 实际执行者为Codex desktop / GPT-6（可见标签，未核实更细后缀）；本执行者未承担独立审计。基线45951501d2741630a229762d6b2d3f4b34d7f702与已有差异均保护，未提交/推送、未改正式docu/公共规则/旧证据。

## 实际改动

- 新backend/migrations/006_activities_running_owner_session.sql：仅增加running_owner_session_id BIGINT，NULL默认，非NULL CHECK为0..4294967295；旧行不回填，DDL在BEGIN/COMMIT内。001—005字节未改；006真实PG未执行。
- backend/app/activities/repository.py：claim_lease增加可选会话号和旧代次核对；拒bool/非整数/负/超DWORD；新G与会话号同一UPDATE并在ActivityLease回传。耗尽时全额R→S、清空会话并返回None。inspect_window扩展旧会话、数据库时间租约/截止及来源有效性；最终claim也用数据库CURRENT_TIMESTAMP判租约，避免主机时钟偏差造成先杀有效旧树。结算/取消清空非运行态会话号。低层缺省NULL仅为合成兼容，不授予自动恢复资格。
- backend/app/worker/windows_job.py：JobOpenError.code保留OpenJobObjectW原始错误码；仅ERROR_FILE_NOT_FOUND=2可成为旧树不存在候选。可信SUP用自身PID调用ProcessIdToSessionId，失败在认领前拒绝。
- backend/app/worker/session.py：SessionConfig.single_host_single_session_recovery默认False；旧running恢复要求显式True、旧会话非NULL且同号、来源有效、数据库租约已过期、旧精确Job结果可确认。活动互斥覆盖旧Job核查到claim事务响应；仅全额折叠，响应丢失不spawn。结果携带可信会话号及持句柄取得的worker创建时间。该True配置是“同一账本仅一台主机、单交互会话”的运维声明，numeric ID不能技术证明跨机或数据库迁移安全；未知/不满足时保持False。
- 只适配直接受影响的backend/tests/test_worker_session.py与backend/tests/fixtures/task083/offline_unit.py替身接口；新增backend/tests/test_d3_recovery.py与backend/tests/fixtures/task083/d3_pg_windows.py。未改真实gateway/transport/HTTP/PDF/runtime、依赖锁或生产服务。

## 验证、资源与停止原因

证据入口：Ndocu/evidence/task-083/d3-implementation-10/manifest.md、pre-hashes.txt、pre-real-hashes.txt、offline-01/、runner-log.txt、runner-state.json、container-created.json、cleanup-after-identity-check.txt、attempt-00-resource-check/runner-as-run.py、runner-correction-hashes.txt。runner进程退出0仅说明已收尾，不能当测试通过。

- 离线共3命令批，累计远小于5分钟。第1批系统Python编译退出0、单元因缺pydantic退出1（环境选择错误）；第2批现有项目venv的D3定向6项、旧Protocol 2项、旧offline 3项全部退出0；第3批最终语法、D3 6项、受worker创建时间影响的旧offline05及精确diff检查均退出0。原命令、时间、退出码、stdout/stderr见offline-01对应meta与日志；首失败未伪报通过。
- 真实资源一次预检通过：Docker server 29.7.2、固定本地镜像、127.0.0.1:55439空闲。只创建一个授权容器1086a37d40c34841d373487c10b278c5cfb771b81af7d70251fcb260c69421f0，run=20260925-191110，1CPU/512MiB/pids128/restart=no/bridge、无宿主绑定。首版runner将镜像自带匿名PG volume误判为违反“无宿主挂载”，在资源核验阶段停止，单调计时7.859秒；PG测试进程0、Windows场景启动0、真实首验批0、修正复验0。这是runner缺陷，不是已观察到的产品失败。
- 原runner进程已退出，随机合成口令仅在该进程内存中。遵守任务卡，不从容器取回口令、不创建第二容器、不重启接管。原runner曾记录cleanup_incomplete=true；随后只读核准精确ID及retrolume-task=083/phase=d3-10/run=20260925-191110标签，docker stop同ID退出0，复查Running=false；容器及匿名卷保留。首版runner原字节/hash保存在attempt-00-resource-check；当前runner仅修正匿名卷检查和stop参数，尚未再运行。
- 006空/旧行迁移、CHECK及失败事务、claim真实账面提交/耗尽、旧Job消失后的固定SUP恢复、可信Windows SID读取及新G真实PID/创建时间均**未获真实PG/Windows证据**。d3_pg_windows.py仅为预列、语法通过的夹具，不是运行结果。跨机、会话切换、系统重启也未运行；未登录/注销会话。原084须在完整真实证据之后由隔离窗口审最终增量；本窗口没有自审。

## 最终文件SHA-256

| 文件 | SHA-256 |
|---|---|
| backend/migrations/006_activities_running_owner_session.sql | f791f22dcfccf204f6fda369470978452b3b23cca0fc40d2057bd08ea47f6428 |
| backend/app/activities/repository.py | d8a8ba184a84c6427e6c91e88b290c30aac43c355da708f4e09c26fd7cf996e6 |
| backend/app/worker/session.py | dfd3423e3e5c367cae3cafe24d857dcbb9a9375c1ff4513cfa0499d052989bbb |
| backend/app/worker/windows_job.py | d04ed8f249106328d81147707451e6092c2d650c9199bd6c4989931d5249c596 |
| backend/tests/test_d3_recovery.py | 5e7328437f23659bdbe0f944b85b2c59c4446a61f2e0840ac063f4c31d12bccd |
| backend/tests/test_worker_session.py | 4027f5cd72b17d826626704e118b0a194b0a7aef48c4ee4c8de4ac3ef48c |
| backend/tests/fixtures/task083/offline_unit.py | bb30163891de46ef97350b90c1988df5c5e0f80189dd13cdccb9e9c3c8264b6d |
| backend/tests/fixtures/task083/d3_pg_windows.py | a2c8fad08fc324879f40eb1348e00930be016fa00e068c16bd4509ef9ecdfc0e |

下一步由编排按“原runner已退出、口令不可复用、单容器额度已用”裁定新的真实资源授权；授权前不重启/接管该容器，也不把离线替身升级为真实恢复通过。以下是旧结果原文，完整保留。

---

"""
p.write_bytes(bom+prefix.encode("utf-8")+body)
