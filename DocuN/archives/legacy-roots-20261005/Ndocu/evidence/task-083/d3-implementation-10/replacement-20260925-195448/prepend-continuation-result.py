from pathlib import Path
p=Path("Ndocu/results/TASK-083-result.md")
old=p.read_bytes()
bom=b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
body=old[len(bom):]
prefix="""# TASK-083 / R-077 — D3实施10替补资源接续结果（2026-09-25，当前置顶）

**结论：产品候选实现与上轮离线证据保持有效；替补真实PG首批只证明006空表迁移执行且负会话号被数据库CHECK拒绝，随后夹具异常类路径错误使该批退出1。已修夹具未能复验：runner遗漏全量复验选项，收到修正信号后在第二测试进程启动前退出。D3累计两容器额度已用，替补容器经精确核对停止保留；真实claim事务和Windows旧G恢复仍未验证，原084独立审计尚未启动。** 本轮为原TASK-083/R-077接续，实际客户端Codex desktop、模型可见标签GPT-6，未自担独立审计；未提交/推送、未动正式docu/公共规则/旧证据。

## 本次新授权与实际资源

用户2026-09-25粘贴的接续裁定在原D3范围内另授权一个替补容器，累计上限2。原容器1086a37d40c34841d373487c10b278c5cfb771b81af7d70251fcb260c69421f0保持停止、不接管。新容器85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7，run=20260925-195448；Docker 29.7.2、固定镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f、127.0.0.1:55439→容器5432、1CPU/512MiB/pids128/restart=no/bridge和标签均经runner核对。镜像声明的唯一匿名PG卷由本次创建，无宿主bind/mount；PG身份查询得retrolume_task083_d3/task083_d3/容器内5432。新资源与全部原始证据只在Ndocu/evidence/task-083/d3-implementation-10/replacement-20260925-195448/；原attempt-00及其日志字节未改。

替补runner单调总计81.765秒，包含一次预检、创建、就绪、首批0.891秒、等待同窗修正信号及收尾；连同前一资源7.859秒和其后精确收尾，未超30分钟，但容器数量已达2。真实PG测试子进程1个，PID31624、创建时间134348108976985801，exit1；Windows场景启动0；attempt-02测试进程0；额外离线命令批0。替补容器stop exit0、末次inspect Running=false、cleanup_incomplete=false，容器及匿名卷保留。runner退出后内存随机口令不可复用，未读取旧/新容器口令、未建第3容器。

## 原始失败、修正和证据边界

attempt-01的stdout先记录空schema task083_d3_empty_0b5945b9；006在该空schema实际执行，PostgreSQL随后对-1返回CheckViolation，证明该单一非法值被CHECK拒绝。夹具写成psycopg.CheckViolation，实际应为psycopg.errors.CheckViolation，捕获阶段触发AttributeError；上界、含旧行、失败事务回滚、claim账面折叠/耗尽和Windows场景均未运行，不能称迁移或D3验证通过。失败schema保留。修正后的夹具hash为5f256503807b8945fbe4381466f22fb6be735d5ebcaa3d8d99bdfc69b0289651，未实测。

同一runner还活着时已提交attempt-02.go=migration,ledger,windows；runner白名单遗漏该合法全量选择，报invalid correction selection并收尾，第二批并未启动。as-run runner hash为56e698a7f98b2732596153c26247a41e017420fc4c7e2af9d8d06ac80435ce8e；白名单补全后的未运行候选hash为39e5917e0173aced0391f9729a4a3ce2f492ed41b8bb2c41e7cd205cc735a27f。原始命令/参数、stdout、stderr、exit、时间、容器inspect/stop、as-run脚本及修正前后字节/hash均见replacement-20260925-195448/；资源总账见d3-implementation-10/manifest.md。runner进程退出0只表示收尾，不是测试通过。

四项产品文件现场最终SHA-256未漂移：006=f791f22dcfccf204f6fda369470978452b3b23cca0fc40d2057bd08ea47f6428；repository=d8a8ba184a84c6427e6c91e88b290c30aac43c355da708f4e09c26fd7cf996e6；session=dfd3423e3e5c367cae3cafe24d857dcbb9a9375c1ff4513cfa0499d052989bbb；windows_job=d04ed8f249106328d81147707451e6092c2d650c9199bd6c4989931d5249c596。仓储claim改用数据库CURRENT_TIMESTAMP判租约是实质控制变化，因首批未到ledger阶段，尚无真实PG回归证据；原定ledger_active_lease_rejected等场景不得标通过。test_worker_session.py真实hash为4027f5cd72b17d826626704e118b0a194b0a7aef48c4ee4c8de4ac3efae69cf5，前段结果中该hash抄写缺项，按真实文件与本轮核验值为准。旧离线3批通过证据复用，未重复运行。

现受“第3容器禁止＋runner退出后口令不得取回或复用”硬门限制，停止本卡真实运行并一次交回。原084只在完整真实证据后独立增量审计；M-1/STEP008和产品one_call接线均未完成。以下为上轮结果原文，字节完整保留。

---

"""
p.write_bytes(bom+prefix.encode("utf-8")+body)
