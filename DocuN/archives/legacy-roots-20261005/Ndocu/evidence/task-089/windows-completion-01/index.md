# Windows收尾01证据索引

- 授权：用户转交收尾01；TASK-089-work-decision.md。仅指定既有CID/DB/role，口令每批经stdin轮换一次，目标身份/权限/无占用先核。没有新资源、迁移或PG套件。
- 命令（两次相同）：`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task089/windows_completion.py`。总attempt2对应attempt-1，总attempt3对应attempt-2。
- 首批：1发现/1执行/0skip/1通过/0失败，exit0，11.25秒。原始结果有效；父进程trace不覆盖SUP，不作为顺序动态证据。
- 末批：1发现/1执行/0skip/1通过/0失败，exit0，5.11秒。只修采集位置和父进程导入钩子位置，实际SUP trace203条。`derived-session-order.json`由原始bootstrap SUP轨迹映射冻结session.py，line事件表示执行到该行，后续成功推进及settled证明其正常完成；不把单条line事件当提交确认。
- 原始日志：各attempt/stdout.log、stderr.log、manifest.json；bootstrap-sup/worker JSON包含实际编译源码字节hash（测试SourceFileLoader强制从捕获源码编译，避免仅末尾读磁盘）、模块磁盘hash、前后稳定性及发送计数。parent-loaded-source.json末批17项；as-run/post覆盖源码/迁移/相关测试/fixture。
- 自举替换仅测试SUP/worker启动入口及HttpxModelTransport.send合成响应，ToolRegistry禁止；产品固定监督、身份/IPC、gateway、真实PG和安全门保持。调用的是合成transport，不能推出真实provider可用。
- 原27项中仅bootstrap/win_chain有授权增量；产品/测试/001—007一致。pre副本、attempt1副本、final差异、final-baseline-applicability.json留存；旧final-hashes不覆盖。
- 末批hash回执/数据库/read一致；内3无正文，经真实外2校验；账户R0/S1/G2、操作G1、关门true；Job不可重开、外层Job树零/句柄关闭；指定CID Running=false/Pid0。资源/DB/role保留，只有本例登记ID定向删除。
- 账本累计真实3/3启动、Windows2/6（本段2/2）、实测本段16.36秒＋保守启动开销4秒；全卡真实50.594/2400秒。离线8.5055802/1800秒，本段静态保守扣3秒（含UTF8读取失败和清单路径修正开销），没有重跑44离线/18PG。
- 历史real-01失败/088越界及旧报告全部保留。首个工具沙箱helper初始化失败没有启动进程；经工具审批正常权限执行已授权范围，无自动审批拒绝。
- 所有动态运行结束；不再启动资源，待原独立审计最后增量。结果统一引用其结论。
