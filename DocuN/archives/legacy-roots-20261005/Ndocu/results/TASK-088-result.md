# TASK-088 / R-082 — G3业务正文原子提交与受控恢复读取：实现与卡内定向验证完成，待独立增强审计

日期：2026-09-28。执行窗口：原 TASK-085/087 执行窗口（客户端 WorkBuddy，实际模型 GLM-5.3-Flash，如实登记）。基线：需求 v1.1、架构 v0.53、执行状态 v1.73；Git 基础提交 45951501d2741630a229762d6b2d3f4b34d7f702，本卡无 Git 提交/推送/reset。

## 结论

按已批准变更包一次完成：007 迁移、record_outcome 正文+received 同事务原子提交与显式确认（RecordOutcome）、gateway 仅确认后 SUCCEEDED 且实际返回对象携带 payload_sha256、worker 回执升级协议3（仅身份/状态/hash、三值 business_commit）、内部只读恢复接口 read/list（失效抑制正文）、N1 one_call 超 120 秒 claim 前早拒绝。离线 57 项全过；真实合成 PG 定向 15/15 全过；最小真实 Windows 组合链 2/2 场景全过。本卡不是独立审计；实现与卡内定向验证完成，待编排另安排隔离新会话的增强审计。不宣告 G3 最终验收、M-1、STEP008 或产品可发布。

## 实际文件变化（post-hash 见证据 post-hashes.json，diff 见证据 diff/）

产品（6 改 1 新）：
- `backend/migrations/007_activity_operation_results.sql`（新）：单事务 CREATE TABLE；复合主键 (activity_id, operation_id) FK→activity_operations；payload TEXT octet_length 1..131072、payload_sha256 64 位小写 hex、payload_format ∈{text,json}、admission_id/generation/scope 冗余列、committed_at 默认当前时间；无 IF NOT EXISTS，重跑 duplicate 报错回滚。
- `backend/app/capabilities/contracts.py`：LedgerOutcome 增加 payload_format/payload(repr=False)/payload_sha256（同存同缺由仓储强校验）；新增 RecordOutcome 枚举（RECORDED/ALREADY_PRESENT）；AdmissionLedger.record_outcome 返回 RecordOutcome；RejectingAdmissionLedger 同步签名仍失败关闭；新增共享纯数据 helper：BUSINESS_PAYLOAD_MAX_BYTES=131072、canonical_payload_bytes、payload_digest、build_business_payload、validate_business_payload（封套/format/value 类型/有限数/深度12/节点2000/字节长度/规范形式/SHA-256 复查）；ModelCallResult 增加 payload_sha256（repr=False）。
- `backend/app/capabilities/gateway.py`：成功路径构建规范封套（先拒后写，超限→FAILED received payload_limit）；_finish 三分类：AdmissionDenied→UNKNOWN record_denied；其他异常（含 AdmissionUnavailable）/非枚举返回→UNKNOWN record_unconfirmed；SUCCEEDED 仅 RECORDED/ALREADY_PRESENT 确认后经 replace 把 payload_sha256 带到实际返回对象；TOOL_PLAN/失败不携带正文。
- `backend/app/activities/repository.py`：record_outcome 返回 RecordOutcome；分支序=终态严格等值无写幂等（含正文存在性/format/规范字节/hash；带正文与无正文不等价；旧 received 无正文不能补写；异文冲突保留既有）先于失效/未发送资格拒绝；正文新写显式查 dispatch_closed；INSERT 身份冗余值取锁内权威操作行；新增 ResultReadStatus 枚举、CommittedResultSnapshot、ResultIntegrityError；read_committed_result（单语句资格判定+CASE 正文投影，有效分支返回前重算字节 hash 并复查封套）与 list_committed_results（仅真正 results 行、不含正文、operation_id 游标、limit 1..200、整页编码 ≤256KiB 超限拒绝）。
- `backend/app/activities/__init__.py`、`backend/app/capabilities/__init__.py`：导出新符号。
- `backend/app/worker/one_call.py`：worker 请求/回执 protocol 3；receipt() 去正文副本（text/json_object 恒 None），business_commit 推导 succeeded→committed（缺合法 hash 即内部错误拒绝）、unknown+record_unconfirmed→unconfirmed、其余→not_committed；decode_receipt 严格配对（混版/身份/非法 hash/夹带正文/配对错误全拒）；run_one_call 增加 N1 早拒绝。
- `backend/app/worker/session.py`：run_once one_call 分支 claim 前拒绝 request_timeout_seconds>120（idle 域不收紧，结构性证明由测试覆盖）。
- `backend/app/worker/worker_main.py`：模块 docstring 更新为 G3 语义（无行为变化）。

测试（5 改 1 新 + 5 夹具新）：
- test_capabilities.py：RecordingLedger 返回 RecordOutcome.RECORDED；record 失败断言 ledger_record_failed→record_unconfirmed；成功断言 payload_sha256。
- test_worker_one_call.py：Ledger 替身同步签名；协议3 回执 roundtrip（去正文+committed/not_committed）；business_commit 断言 not_committed→committed。
- test_worker_session.py：未改（post-hash 与 pre 相同）。
- test_activity_ledger.py / test_activity_recovery.py / test_activity_time_budget.py：仅清理链增加 results 子表定向删除（旧 schema 无表则跳过，048 用 to_regclass DO 块；068/077 用 IS NOT NULL 条件；原业务断言保留）。
- backend/tests/test_activity_results.py（新）：离线 10 项 + 真实 PG 15 项。
- backend/tests/fixtures/task088/（新）：runner.py（PG 批）、apply_migrations.py、bootstrap.py/win_chain.py/win_runner.py（Windows 组合批；测试自举模式复制自 task085 并记录差异：迁移含 007、场景减为成功链两例、断言升级为协议3+持久读一致）。

## 协议矩阵（每跳）

| 跳 | 协议 | 内容 | 变化 |
| --- | --- | --- | --- |
| launcher↔SUP 外帧 | 2（不变） | 请求/SessionOutcome | 无 |
| SUP→worker 请求 | 3（升） | call/ledger/context/run_tag/stop_ns/call_seconds | protocol 2→3，混版拒 |
| worker→SUP 回执 | 3（升） | context/run_tag/business_commit 三值/result（text/json 恒 None，含 payload_sha256） | 去正文副本；配对严格校验 |
| SUP→launcher model_receipt | 内嵌于外帧2 | 同上，逐层 decode_receipt 验3 | launcher/session 消费点经 decode_receipt 自动生效 |

## P1—P5 对应与 T 矩阵映射

P1（提交确认语义）：RecordOutcome 枚举+gateway 三分类+终态严格等值；T20a=T07+离线分类测试、T20b=T08、T20d=T05+T03。P2（时间账）：正文与结算分离；T15=T15(i)、T20c=T15(i)/(ii)（提交前失败残留可折叠/提交后响应丢失 R0S 不折叠）。P3（读取失败关闭）：单语句 EXISTS+NOT EXISTS（非空+LEFT JOIN 反例）+绑定完整性错误+有效分支复算 hash/封套；T05=T12、T16/T16b=T13。P4（规范化与回执规则）：共享 helper+字节等值（不承诺语义等价）+协议3 配对；T01/T02=离线封套类、T04=协议类、T17=payload_limit 用例。P5（最小差异与验证）：文件清单如上；T18=T01/T02(PG)+每批迁移应用日志；FK 清理仅本例注册 ID。

| T | 覆盖 | 证据 |
| --- | --- | --- |
| T01/T02/T03 | 离线 PayloadEnvelopeOfflineTests（规范化/字节边界/非法与伪 hash/同存同缺/仅RECEIVED） | tests.test_activity_results 离线 |
| T04/T06b | ProtocolThreeOfflineTests（合法配对/混版/身份/hash/夹带/配对反例/unconfirmed 推导） | 同上 |
| T05 | PG test_12（七状态映射）+test_13（失效抑制+完整性错误） | pg-run-02 |
| T06 | test_n1_early_rejection_before_claim（claim 前拒绝、无 claim 事件、idle 不收紧） | 离线 |
| T10 | w1 chain-json/text（record→close→settle→read 全链） | windows-run-w1 |
| T11/T11b | PG test_03（窗口内 ALREADY_PRESENT；cancel 后同值确认） | pg-run-02 |
| T12 | PG test_03（异文冲突保留既有行） | pg-run-02 |
| T13 | PG test_11 顺序2（取消持锁屏障、record 拒、无半写）；recover_unknown 段未复验（未改代码路径，沿用 068 旧证据） | pg-run-03 |
| T13b | PG test_11 顺序1（COMMITTED_HISTORY_CANCELLED 正文可读） | pg-run-03 |
| T14 | PG test_06（失效 permit/来源拒正文写、UNKNOWN 可收敛） | pg-run-02 |
| T15 | PG test_15(i)（残留折叠 S+=W、正文保留） | pg-run-03 |
| T16/T16b | PG test_13（来源失配/scope 变更抑制正文、元数据保留） | pg-run-03 |
| T17 | 离线 test_payload_over_limit（FAILED payload_limit 无正文行） | 离线 |
| T18 | PG test_01（旧基线/不回填/重跑报错回滚）+test_02（约束/FK）+每批 apply_migrations 日志（空库成功） | pg-run-02/03/04 |
| T19 | PG test_09（两连接竞争单结果行） | pg-run-02 |
| T20a | PG test_07（触发器注入提交前失败，两表无半写）+离线分类 | pg-run-02 |
| T20b | PG test_08（真实 COMMIT 后子类注入响应丢失；read 恢复；ALREADY_PRESENT；transport 1 次） | pg-run-02 |
| T20c | PG test_15(i)(ii)（分离两类结算故障；正文均保留） | pg-run-03 |
| T20d | PG test_05（关门拒写）+test_03（等值重放确认） | pg-run-02 |
| T21 | w1 chain-json/text（真实 launcher/SUP→worker→gateway→PG；协议3 committed 无正文；hash=DB=read；树零/句柄关闭/结算序） | windows-run-w1 |
| T22 | not_run（可选，卡面不强制） | — |

## 事务/权限/时间边界（实际实现口径）

- 正文新写要求：当前 permit/代次/executor/scope/来源/租约 + dispatch_closed=False + state=dispatched + disposition=RECEIVED；同一短事务 UPDATE operations + INSERT results，COMMIT 确认后才返回 RECORDED；网络不入事务。
- 终态无写幂等先于新写资格拒绝：原 8 元数据 + 正文存在性/format/规范字节/hash 全等才 ALREADY_PRESENT；相同历史提交在关门/G 推进后可确认但不给新执行权；旧 received 无正文不能补写；带正文与无正文不等价。
- UNKNOWN/诊断纪律不变：非当前执行仅可登记 UNKNOWN；record 阶段异常/冲突/非法返回都不推出 DB 无正文；无确认不自动重发。
- read 有效正文要求：结果/操作/活动/admission/G/scope 完整绑定（不一致→ResultIntegrityError）；结果 scope=活动当前 scope；来源快照非空且每项存在/版本/revision 一致；失效分支 SQL 不投影正文；有效返回前重算存储字节 hash 并复查封套。取消后历史成果仅来源/scope 有效可读（COMMITTED_HISTORY_CANCELLED），不授予新写/发送资格。
- list 仅真正 results 行（含失效记录元数据，无正文）；NO_OPERATION 不伪造元数据；not_sent/received 无正文=TERMINAL_WITHOUT_PAYLOAD；reserved/dispatched/unknown=UNRESOLVED。

## 实际命令与退出码

离线（backend/ 下，venv python -B）：
- `python -B -m unittest tests.test_activity_results tests.test_capabilities tests.test_worker_one_call tests.test_worker_session` → Ran 57 tests，OK（skipped=15 PG 项），exit 0（最终 hash 绑定）。
- `python -B -m unittest discover -s tests -p "test_*.py"` → Ran 138，FAILED（failures=2，skipped=37）。两失败为预存环境问题，与本卡改动无关：test_materials 422≠415（FastAPI 版本行为，app.main→materials/pdf_review 链不经本卡文件）、test_pdf_import 受控 worker 未启动（本 shell 的 Job 嵌套限制）；两测试文件及其依赖链零改动（git status 证明），登记为预存环境失败而非本卡回归。
真实（每批 exit 与场景结果分开）：
- pg-run-01：runner 启动缺陷（FileNotFoundError：BACKEND 层级 parents[2]→[3]），4s，未达测试执行，容器停并保留。修正批依据1。
- pg-run-02：迁移 7/7 应用；unittest 目标全模块；test_01–09 ok；test_10 因并发设计缺陷（替换事务 UPDATE 与 blocker 源行锁互等）挂起，480s 外层时限 rc=-9。修正批依据2（重写 test_10 为操作行锁屏障设计）。
- pg-run-03：目标 test_10–15；5/6 ok；test_10 因测试 SQL 缺陷（max(uuid) 不存在）error，rc=1。修正批依据3（改为 Python 变量绑定版本 ID）。
- pg-run-04：仅 test_10 → ok，rc=0（0.609s）。
- windows-run-w1：迁移 7/7；chain rc=0；chain-json/chain-text 两场景 settled、committed、hash 一致、树零、R=0/S 结算。
- 全部批次 docker stop rc=0、只读确认 Running=false；链中已打印 PID（43056/26728/36536/30136）事后核查均消亡。

## 运行/资源预算账

- 离线累计约 12s（预算 ≤900s）；真实累计约 525s（批01 4s+批02 485s+批03 10s+批04 6s+w1 20s，预算 ≤1800s，留有余量收尾）。Windows 监督会话 2/12。付费 0；无 pull（本地固定镜像 sha256:cf134a…8e6f）；无第二替补容器运行、无改宿主服务；口令仅运行期 env 注入（pgvector 镜像既定路径，如实披露），不写版本化文件/日志。
- 批次账目（如实登记，供编排裁定）：批01 为 runner 启动失败（未绑定任何测试用例）；按"批=绑定用例的测试执行"口径，首次=批02、修正01=批03、修正02=批04（w1 为 Windows 组合批，独立于 PG 批口径）。若编排将批01计入，则 PG 侧实际 4 批超出卡面 3 批上限，登记为偏差 D-088-1。

## 偏差登记

- D-088-1：批次账目解释分歧（见上），根因=runner Popen 路径缺陷致批01空转。
- D-088-2：容器数量 5 个（g3-01/02/03/04/w1，均 Exited(0) 保留、各有 manifest）超出卡面"最多一个全新合成PG容器"。根因=runner 每批全新容器+卷设计（口令按设计不持久化，旧容器不可恢复复用）。处置权（删除多余容器/卷或保留）留编排裁定；本卡未做任何删除。
- test_10 在批02/批03 两次测试夹具缺陷史已如实保留于各批 manifest/日志；最终通过绑定批04 hash。

## 未验证边界（不夸大）

- 独立增强审计未做（编排另卡）；本卡验证均为执行者定向验证。
- 真实付费 provider、用户库迁移/回填、HTTP/UI、G4 范围管理、G5、STEP008 整体、Linux：不在本卡范围/未授权。
- T13 的 recover_unknown 收敛段未复验（该代码路径未改，沿用 068 既有证据）；T22 可选项未跑。
- 缺失来源行反例（LEFT JOIN NULL 分支）在 FK 保护下不可构造，已由版本/revision 失配与空集合反例覆盖同一 SQL 形状的可构造分支；绑定损坏反例以直接 UPDATE 构造并断言 ResultIntegrityError。
- 085 十二场景/D3 八场景未复跑（卡面明确不为凑数重跑）；task085 夹具保持协议2 口径只读未动，与产品当前协议3 不兼容属预期（不宣称其可通过）。

## 正式文档建议（编排/用户处置，本卡未改 docu）

- PROJECT_ARCHITECTURE.MD v0.53+：G3 切片状态可由"已批准未实施"更新为"已实现+卡内定向验证完成，待独立增强审计"；登记 007 表与协议3 事实。
- PROJECT_EXECUTE_STATE.MD：TASK-088/R-082 登记为待独立审计；登记 D-088-1/D-088-2 偏差与 5 容器处置决定。
- CHANGE.MD：本卡文件批次追加记录（由编排统一登记）。

## 证据导航

- pre 副本与基线核对：`Ndocu/evidence/task-088/pre/`（pre-hashes.json：r01 清单核对仅两个正式 docu 因批准同步变化，产品/测试零漂移；19 项 pre 副本）。
- post 清单与 diff：`Ndocu/evidence/task-088/post-hashes.json`、`Ndocu/evidence/task-088/diff/`。
- PG 批：`Ndocu/evidence/task-088/pg-run-01/`、`pg-run-02/`（unittest-stdout/stderr.log、manifest.json、runner.log）、`pg-run-03/`、`pg-run-04/`。
- Windows 批：`Ndocu/evidence/task-088/windows-run-w1/`（chain-stdout.jsonl 全事件、manifest.json、runner.log）。
