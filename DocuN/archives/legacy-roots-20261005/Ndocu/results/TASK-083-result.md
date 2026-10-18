# TASK-083 / R-077 — review-09 独立验收结果已接收：批准的单机 D3 切片可由编排验收关闭

**当前结论：实现、八场景真实验证及资源/执行控制已通过 TASK-084 review-09 最终独立验收，无阻断性补项；批准的单机、单交互会话 D3 切片达到交付条件，可由编排验收关闭。** 本窗已核对独立结果、assessment及hash记录，仅同步验收事实，不代签独立结论或修改正式执行状态。

独立结论：[TASK-084-result.md](D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-084-result.md)；完整分层裁定：[review-09/assessment.md](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-084/review-09/assessment.md)。单机/单会话、单一成功路径、未覆盖全部崩溃分支和最近G/C幂等未新增实跑等边界保持，不扩大为M-1、STEP008、one_call或整个项目完成。

review-09非阻断观察按原报告保留，不为本次已通过验收追加修复/测试循环；未来若重新授权使用attempt-02复验通道，须先将backend/tests依赖（至少fixture.py）纳入复用指纹。场景exit为批级投影、连续清理错误消息覆盖、整理命令未存脚本及pg_isready有界重试的分层说明，以独立报告为准。

本次仅更新本结果并新增验收接收记录；代码、原始运行证据、历史预算及资源均未操作，新增动态运行0。正式状态及CHANGE登记由编排维护。下方完整收尾14和更早历史字节原样保留，其中“待独立验收”为当时状态，现由本段更新；原evidence-hashes/delivery-check/review-09记录的结果SHA-256 `2d246fc8a1897ca3d637efc398f0a6bab06f291afd5a3006e03ca2869028b0f9`对应下方被审正文，未倒改旧哈希证据。接收时间UTC：2026-09-27T10:32:19.842521+00:00

---

# TASK-083 / R-077 — D3完整收尾14：实现与八场景真实验证完成，待原084最终独立证据验收

2026-09-27（Asia/Shanghai）。本窗唯一主执行；父082，关联084/R078、STEP008局部、NFR002/003、SEC002、FLOW005、DATA007。需求v1.1、架构v0.45、执行状态v1.65。Git基础仍为`45951501d2741630a229762d6b2d3f4b34d7f702`，全部既有工作树差异保留，无提交/推送。

**结论：已修复完整14字段inspect缺键失败并合并运行控制、证据记录的必要修正；本轮唯一真实批次按migration→ledger→windows执行，八个精确ID全部完成，唯一complete的all_pass=true、parts完整，测试进程与runner均exit0。旧Windows Job树0/关闭/Open2→生产固定SUP新G认领→真实PG结算成立；外层树0、控制句柄完成，唯一授权容器按完整CID stop exit0并复核Running=false，卷与schema保留。无需第二批。当前交付状态为“实现/真实验证完成，待最后独立证据验收”；不自签独立审计，不扩大为D3全部崩溃分支、M-1、STEP008、项目或one_call完成。**

实际模型可确认信息是本窗口系统说明的 **Codex / GPT-6**；客户端未向本窗提供可调用的型号/推理档选择或核验接口，不能确认具体后缀或宣称已操作最高档切换。没有以模型名追加审批、没有改用户配置或再开执行窗口。本窗未派子代理。原窗口在途核查为空，13未发现执行成果，沿12断点接续；没有复跑有效旧成果或清零预算。读取索引与公共规则版本见[read-index.md](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/read-index.md)。本结果以前各轮原文完整保留在本段之后，旧限制不覆盖用户完整14授权。

## 1. 最后一次独立验收导航

所有本轮材料集中于`D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/`。真实运行目录为`continuation-20260927-095506-73c4c3e3/`；以下文件均已保存可读，不需从执行聊天取证。

| 顺序 | 材料 | 用途 |
| --- | --- | --- |
| 1 | [incremental.diff](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/incremental.diff)、`pre/`、`review08-current-hashes.json` | 仅本轮3个既有文件差异；修前真实字节与review08哈希匹配，其他10项不变 |
| 2 | [final-hashes.txt](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/final-hashes.txt) | 产品、runner/controller/contracts、fixture、离线入口及真实依赖快照的SHA-256；最终与as-run一致 |
| 3 | [state.json](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/continuation-20260927-095506-73c4c3e3/state.json)、[meta.json](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/continuation-20260927-095506-73c4c3e3/attempt-01/meta.json) | 八ID、parts、complete、真实exit、绝对期限、精确PID/创建时间、控制事件、树0和句柄收尾 |
| 4 | [stdout.log](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/continuation-20260927-095506-73c4c3e3/attempt-01/stdout.log)、同目录`stderr.log` | 各start/result/complete原始记录；stderr为空。时间与逐项结果另索引于`scenario-index.json` |
| 5 | 运行目录`runner-as-run.py`、`controlled_child-as-run.py`、`contracts-as-run.py`、`attempt-01/as-run.py`及`attempt-01/sources/` | 当次执行字节与产品/迁移/旧worker夹具快照；不借最终版本倒签中间版本 |
| 6 | 运行目录[resource-commands.jsonl](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/continuation-20260927-095506-73c4c3e3/resource-commands.jsonl)、根目录`preflight-resource-commands.jsonl`/`preflight.json` | 每次Docker完整argv、UTC、耗时、exit、stdout/stderr；stdin明确省略以保护新口令，未读取Env/旧secret |
| 7 | `offline-01.json`、`offline-01.stdout.log`、`offline-01.stderr.log`、`offline_checks.py`、`bounded_check.py` | 10项本卡定向离线检查、60秒命令上限、耗时1.938秒、exit0；不代替真实PG/Windows |
| 8 | [budget-final.json](D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/d3-completion-14/budget-final.json)、`runner-process.json`、`inflight-pre.json`/`inflight-before-start.json`/`inflight-post.json` | 历史与本轮资源总账、外层runner真实退出、接续前后进程核查 |

供原084的唯一最终审查范围：本轮实际3文件diff、review08未变依赖的哈希适用性、本轮10项离线与8场景原始动态证据、期限/控制/收尾/预算；无需机械重跑006理论、Job07、PG08或09。这里提供可独立审查成果，未操作原084窗口或签署其结论。

## 2. 根因、实际最小差异及对应验证

1. **完整投影缺键**：repair11的第14字段直接访问`.HostConfig.Mounts`，12已实证本机完整模板报缺键。现改为`{{json (index .HostConfig "Mounts")}}`，仍在原完整14字段内读取真实configured mounts；缺键/null→None，非空挂载仍拒绝，顶层Mounts仍单独严格核唯一匿名卷。新增严格running字面值、JSON形状、字段数和唯一端口集合校验；错误类型/解析异常失败关闭。离线验证null/[]合法、非空拒绝、错类型/字段缺失拒绝，随后本机完整投影一次实测exit0；没有复跑12探针矩阵，没有采用诊断抄错的镜像行，也不推断Docker内部机制。
2. **就绪与认证混淆风险**：原路径start后立即以一次psql判断认证；现在同一30秒就绪期限内只对pg_isready返回1/2有界等待，确定其他失败停止；就绪成功后才以容器OS postgres、本地socket、指定测试角色/库验证身份，再stdin轮换一次并以新凭据核loopback用户/库/5432。实际就绪首检exit0、认证/轮换/loopback全部成功；“先未就绪后成功”和确定认证失败不继续由离线替身验证，不冒称该异常分支真实触发。
3. **控制与证据完整性**：controller只增加实际悬停身份→外层归属ActiveProcesses=1→Resume→句柄关闭事件，不变已审安全顺序、Job归属或最后句柄语义。runner补异常收尾后的真实exit与管道EOF确认、全部运行依赖快照、资源命令审计、场景事件排空后的Windows启动判定、最终句柄状态。窗口/runner/fixture均保留原绝对期限，默认/允许总限收紧为≤600秒；没有延长30秒场景/60秒测试命令期限。
4. **局部复验汇总缺口**：原runner第二批任意parts通过即可顶层PASS，可能遗漏未跑后继。现第二批必须覆盖所有缺失/变更分部及后继；只允许复用前一失败批次在失败点之前完整结束、树/句柄清楚的分部，并以该分部AST+公共代码/生产依赖指纹核适用性。原失败exit/缺complete不改写为PASS。等待状态及时落盘，唯一`attempt-02.go`选择协议保持。本轮第一批完整通过，此复验通道只获得静态和定向离线证据，未消费第二批、未写go。
5. **夹具补证**：为每个事件记录UTC/单调时间；旧Job关闭成功后才记handles_closed；Windows结果额外断言业务树0、无cleanup错误；旧G/C三次拒绝明确标注真实触达的claim旧G不匹配、close当前G不匹配、settle当前窗口不匹配分支，明确未触达最近已结算G/C幂等分支。没有修改断言求通过、延长原期限、替换真实仓储或SUP。产品`repository.py`、`session.py`、`windows_job.py`和001—006本轮均未修改。

新增`offline_checks.py`/`bounded_check.py`/`resource_preflight.py`为本卡必要测试与计时辅助；`finalize_evidence.py`只整理既有文件，不启资源。文档整理曾因Windows默认GBK读UTF-8在生成diff时失败，随后明确UTF-8完成；失败发生在证据整理，13项hash与并发核查已经成立，不影响真实运行字节/结果，不隐去该过程。

## 3. 八场景真实验收事实

本轮`attempt-01`对应历史总第2真实批/PG夹具命令，parts=`migration,ledger,windows`；八项各有唯一start/result，唯一complete的all_pass=true且parts吻合，contract.errors=[]。共同判据：真实exit0、timeout=false、outer_tree_zero=true、handles_closed=true、cleanup_error=null；容器停止确认后runner退出0。没有第九个测试，也没有两批拼接。

| 精确ID | 动态事实 | 场景主动耗时 |
| --- | --- | ---: |
| migration_empty | 001—005后006仅增running_owner_session_id；默认NULL、0、4294967295合法；-1/4294967296真实CHECK拒绝，旧有效值保留 | 0.110秒 |
| migration_old | 真实旧running/R=6行经过006后仍为running/6/NULL，无回填 | 0.109秒 |
| migration_rollback | 006事务内故意无效约束失败，ROLLBACK后新增列计数0，无部分006DDL | 0.110秒 |
| ledger_active_lease_rejected | SID=0/G1/R6/S0有效租约拒绝认领，真实行不变；非法Python SID也被拒绝 | 0.250秒 |
| ledger_new_g | 同SID0、过期旧G1/R6全额入S；新G2/R6/S6/SID0/dispatch_closed=false；独立pending活动以DWORD上界认领持久成功；异SID与三次旧G/C调用拒绝且新账不变 | 0.281秒 |
| ledger_exhausted | 旧R6全额折叠已提交，返回None；pending/G2/R0/S6/SID NULL/dispatch_closed=true | 0.250秒 |
| ledger_lock_barrier | pg_stat_activity真实观察来源行锁等待；claim等待09:55:09.815874Z早于deadline09:55:11.084425Z，释放后拒绝且行不变；inspect等待09:55:11.524253Z早于lease expiry09:55:12.832620Z，释放后recoverable=true。未改系统/DB时钟 | 3.515秒 |
| windows_recovery | 真实旧G1/SID1 Job/PID/创建时间→树0→关闭→Open错误2；固定生产launcher/SUP以自身SID1认领G2并结算；最终pending/G3/R0/S7/SID NULL/last_settled G2,C1 | 1.610秒 |

各场景起止UTC、完整活动UUID、schema名称与哈希见`scenario-index.json`和原始stdout。锁屏障跨边界后读取有辨别力，不能把其简化为“资源就绪”。旧G1是折叠的未结算残留，因此三次旧G/C触达的是上述不匹配拒绝分支；**本轮没有重跑或新增证明最近已结算G/C的ALREADY_SETTLED动态路径**，未变部分按既有证据范围复用。

## 4. 精确Windows树与资源终态

- 外层夹具主进程PID **4936**，创建时间 **134349765079104187**（Windows 100ns）。真实控制事件有序为`suspended_identity`→`assigned_outer_job(active=1)`→`resumed`→`control_handles_closed(tree_zero_confirmed=true)`；队列完整读完、进程exit0、外层ActiveProcesses=0后关闭全部线程/进程/Job句柄。无按裸PID、进程名或端口杀进程。
- 旧Job `Local\RetroLume.Activity.63bdd29688b9471a8955d5e779712a67.G1`，SID1，worker PID **17752**，创建时间 **134349765131727313**；整树0、close成功、Open错误2。观察者没有持有旧业务Job最后句柄干扰被测消失。
- 新生产SUP PID **32896**，创建时间 **134349765135467746**；G2 worker PID **37356**，创建时间 **134349765140558339**；outcome=settled、active_processes_at_end=0、cleanup_incomplete=false、cleanup_errors=[]。本次新窗实际0.469秒，向上结算C=1；PG最终S=旧折叠6+新结算1=7、R=0。生产互斥覆盖顺序按未变源码和旧离线事件证据解释，未伪造动态mutex_release事件。
- 容器完整CID `85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7`；name/三标签/固定镜像/唯一匿名卷/CPU/内存/pids/restart/bridge/loopback端口全部逐项相符。启动前Running=false，唯一start成功；OS postgres仅使用角色task083_d3、库retrolume_task083_d3本地socket自改密，新凭据仅进程内存与子环境。未读取完整Config.Env、旧口令、管理员替代身份，也未建第三容器、改认证或端口。
- 精确`docker stop --timeout 10 <完整CID>`于09:55:14.903681Z开始，exit0；09:55:15.676179Z最终inspect身份仍符且**Running=false**。不需kill；container_stopped=true、cleanup_incomplete=false。容器/卷/7个新schema保留，无DROP/删除；旧首容器未触碰。随后仅本地进程只读核对为空，未追加Docker探针或重启。

## 5. 命令、时间、哈希与累计账

工作目录均为`D:/shspic/project_NO3_RetroLume-agent`；Python为项目既有`backend/.venv/Scripts/python.exe`，未安装或拉取依赖。

| 操作 | 精确入口/参数 | 结果与扣账 |
| --- | --- | --- |
| 定向离线 | `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-completion-14/bounded_check.py offline-01` | 包装器实际执行同目录offline_checks.py；10项exit0，2026-09-27 09:53:53.469633Z起，墙钟1.938秒；新增离线累计1.938/600秒，每命令≤60秒 |
| 只读完整预检 | `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-completion-14/resource_preflight.py` | 09:54:06.976765Z至09:54:12.595589Z，5.609秒全扣；完整14字段与ps/端口一次通过 |
| 唯一真实runner | `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/runner.py --authorized-reuse --total-seconds 600` | 进程09:55:05.5862502Z至09:55:15.7277434Z，exit0；保守按外层进程墙钟10.133438秒扣，内部资源墙钟9.390秒不重复相加 |
| 唯一PG/Windows夹具命令 | `backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/d3_pg_windows.py` | cwd=`backend/tests`；D3_PARTS在环境中为migration,ledger,windows，PYTHONOPTIMIZE=0；09:55:07.906043Z至09:55:14.751802Z，6.844秒，已含于runner墙钟；exit0 |

按卡历史保守900秒+第12轮保守240秒（均非历史实耗声明），本轮预检5.609秒+完整runner进程10.133438秒，累计保守占账 **1155.742438/1800秒**，余 **644.257562秒**。启动前余654.391秒，runner设600秒，内部预留60秒收尾；未把阅读/文档整理/用户转交计入资源时间，也未排除任何实际Docker探针。逐命令时间见两份resource-commands日志。定向测试开始到收尾6.844秒，各场景均≤30秒，测试命令≤60秒。

累计次数：容器总2（本轮新增0）；真实批/PG夹具命令历史1+本轮1=**2/3**，剩余1未用；Windows历史0+本轮1=**1/12**，仅本卡恢复场景；start1、轮换1、stop1，第二批0。PG“进程”账按既定一次夹具命令口径，Windows Python重定向器及其后代归外层整树控制，不据此额外启动另一个测试命令。runner已退出且新凭据仅在内存，未用次数不构成重新start/读回secret的授权。

| 最终实际文件 | SHA-256 |
| --- | --- |
| runner.py | `7137664e7cff010089c58600de6f9dae96f82a274cad8968bd6600f70be2c436` |
| controlled_child.py | `0494af00387ba5f1c45062b9cd892e5af22822e95d72b619134f6bd694c8a664` |
| contracts.py（未变） | `a344ac5fbdf7c838c08c18fc1816d5d8e823c3ff67b1a98976cf11129257cbcd` |
| d3_pg_windows.py | `19b6f78cacc88c299a94b78b7e3f2c569621f020d337178163680269100ca1f8` |
| repository.py（未变） | `bca8283316f62216f5ba94959f5c36f8c3395301aeb9dc7f21a9b376f92e29a3` |
| session.py（未变） | `eb514b5f76b0dc8b43ed8dfe116d2dc7be5a181011e1516faaa4d8005461d71c` |
| 006（未变） | `f791f22dcfccf204f6fda369470978452b3b23cca0fc40d2057bd08ea47f6428` |

修前字节/哈希与有限diff、旧12与11原始证据保持；本轮离线检查、完整模板实测和真实批均对应同一最终runner/controller/contracts/fixture版本，真实之后无再改。review08中间版离线分级未被倒签；新增10项是本次实际独立方法数，不与历史测试求和冒充覆盖。

## 6. 未验边界、剩余风险与编排文档建议

- 本次真实证明批准的单机、单交互会话前提下合成D3成功路径；numeric SID不证明跨主机/boot唯一性。跨主机、迁库、注销/重启等仍在自动恢复契约之外。006仍唯一新增列，NULL旧行不回填。
- Windows真实只跑一个恢复成功场景，没有追加猝死/异常实验；Assign前崩溃可能留下悬停孤儿，不能据本次成功树0推成所有崩溃出口已清理。权限拒绝、Open未知、句柄失败等仍按原静态/替身证据范围失败关闭；真实second-attempt、认证失败收尾及stop失败后的kill分支本轮均未触发。
- 旧Job清理、PG折叠/新claim、固定SUP结算与外层收尾本次均有证据，但不能据一条成功链推出所有响应丢失/并发交错/退款异常动态通过；最近G/C幂等未新增实跑，产品one_call仍未验证。
- 原084最后一次独立差异/动态证据验收尚待完成，本实现者不代签，不调用新的前置审计循环。没有实质执行阻塞遗留；剩余交付门是该独立验收。
- 编排可在正式执行状态建议登记：“TASK083完成14实现与真实验证8/8、资源停止保留，待TASK084最后独立验收；STEP008/M-1/one_call不据此关闭”。正式架构/CHANGE/执行状态由编排维护，本窗没有写入。需要逐文件登记的本批文档是本结果与`d3-completion-14/read-index.md`；代码/日志不作为正式文档逐个记账。公共规则只读，未改记忆、用户库/配置、HTTP/gateway/真实模型接口、依赖锁。

---

# TASK-083 / R-077 — D3同容器受控真实验证12：runner预检确定性失败BLOCKED（2026-09-26，当前置顶）

**结论：按卡唯一一次启动已审 runner（`backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/runner.py --authorized-reuse --total-seconds 900`，工作目录项目根），在资源预检第一步 `docker inspect` 即确定性失败退出：verdict=BLOCKED、error=`RuntimeError: inspect exit=1`、进程墙钟约4.4秒、stdout/stderr为空（runner 全部状态写 state.json）。根因已定界为 repair-11 runner 与本机 Docker 29.7.2 的确定性不兼容——runner 的14字段 `--format` 身份投影含 `{{json .HostConfig.Mounts}}`，而模板同时引用 `{{.Id}}` 时本机 CLI 必报 `map has no entry for key "Mounts"`（该路径下 HostConfig JSON 有 Binds 键、无 Mounts 键；12个只读探针交叉定界，跨容器通用）。该投影从未实际运行过：review-08 动态额度为0、implementation-10 走全量JSON解析故免疫，本卡首跑即首次执行。容器全程零接触：未启动、未认证、未轮换、无任何批次（attempts=[]、touched 未置位），8场景全部 not_run，剩余额度2批/2PG/12Windows 与两容器上限均未消耗；55439 空闲、目标容器仍 Exited(0) 保留、13字段只读快照与卡面精确资源许可逐项一致；13项冻结hash运行前后各核一次全 MATCH，零漂移零写入。按卡"若修复需改…runner…停止本卡测试并收尾，带具体差异交回"停止本卡，未改 runner/contracts/controlled_child/夹具/产品任何文件，附已实测可行的最小修复建议交回编排；本地认证/口令轮换/loopback核验/PG事务/Windows恢复全部仍未验证。执行窗口实际身份 GLM-5.3-Flash（接续原083实现窗口，非独立审计，如实登记）。**

## 执行与停止点

- 唯一一次启动，无重试：runner hash 26ECB423…731（与卡冻结一致，运行后未变）。
- 运行证据目录（runner 自建）：`Ndocu/evidence/task-083/d3-repair-11/continuation-20260926-064735-85cbc7d0/`（runner-as-run.py、controlled_child-as-run.py、contracts-as-run.py 及各自 .sha256、state.json；执行窗补充 preflight-blocked-diagnostics.md 探针全录）。
- state.json：verdict=BLOCKED、attempts=[]、cleanup_incomplete=false、container_stopped=false、error="RuntimeError: inspect exit=1"。失败点在 main() 首步 inspect 预检（touched 置位之前），finally 停止分支因无可停对象未执行；容器保持既有停止态，由执行窗只读独立复核。

## 根因定界（12探针 A—L + 5项预检，全部只读）

关键事实链：①守护进程可达（29.7.2）；②完整14字段投影**确定性**复现 exit1（推翻"守护进程冷启动"瞬时假设）；③单字段 `{{json .HostConfig.Mounts}}` 成功返回 null；④HostConfig JSON 顶层有 Binds 键、无 Mounts 键（omitempty）；⑤同一 Mounts 访问与 `{{.Id}}` 共存于模板即必错（B/I/E，含首容器1086a37d 交叉验证），不含 `.Id` 即成功（A/C/G/H/K）；⑥纯13字段（含 .Id）成功、字段齐全（D）；⑦第14字段改顶层 `{{json .Mounts}}` 后14字段成功且数据=同一匿名卷（L）。经验规则：模板引用 `{{.Id}}` 时本机 CLI 29.7.2 走通用 map 渲染（missingkey=error），HostConfig 无 Mounts 键即报错；不含 `.Id` 走类型化结构体路径，Mounts 零值 null。CLI 内部机制未查源码定论，以探针记录为准。

为何此前未暴露：implementation-10 runner 全量 JSON 解析（runner_replacement.py:62），2026-09-25 同机实测通过；repair-11 为排除 Config.Env 改 --format 投影，review-08 纯静态审计未运行，本卡首跑为该投影首次执行。

## 资源现状（只读核准，与卡面精确资源许可逐项一致）

- 全部9个 task-083 容器 Exited(0)，无活动 083 容器；目标容器 85242648b70d…f6a7 十三字段快照（Id/Name/Image/标签{083,d3-10,20260925-195448}/Running=false/唯一匿名卷11140b6c…→/var/lib/postgresql/data/1CPU/512MiB/pids128/restart=no/bridge/127.0.0.1:55439→5432/Binds=null）与卡面完全一致，保留未动。
- 端口 55439 bind 预检空闲（与 runner 同口径）。
- 13项冻结hash运行前后各一次 13/13 ALL MATCH；本置顶段追加按卡不计代码漂移。

## 预算账

- 本卡实际消耗：0批、0 PG测试进程、0 Windows场景、0次容器启动/认证/轮换；剩余额度仍为2批/2PG/12Windows，容器总数仍2（无新增）。
- 墙钟另记约4.4秒（BLOCKED、无资源接触）；历史保守占账900秒与既往 7.859s+81.765s+未知首收尾口径不变，是否并入30分钟总账由编排裁定。

## 最小修复建议（均未实施；runner 属卡面禁改文件，须编排授权另行走查）

| 候选 | 内容 | 已实测 |
| --- | --- | --- |
| A | 投影删第14字段 `{{json .HostConfig.Mounts}}` 保留13字段 | 探针D exit0；valid_identity 的 configured_mounts 检查需另定（固定 None 或由顶层 Mounts 承担） |
| B | 第14字段改顶层 `{{json .Mounts}}` | 探针L 14字段 exit0；顶层为"已实现挂载"，valid_identity 语义需相应调整 |
| C | 回 implementation-10 式全量 JSON 解析+python 侧排除 Env 字段选取 | 2026-09-25 同机实测通过 |

任一方案使 runner hash 轮换，按惯例交原084增量复核并经编排重新授权后，方可再按同卡参数一次启动。

## 边界与未验证（全部保持 not_run）

migration_empty/old/rollback、ledger_active_lease_rejected/new_g/exhausted/lock_barrier、windows_recovery 八场景未启动；本地socket认证、stdin口令轮换、loopback新凭据三重核验、PG锁屏障、旧G恢复链、ControlledChild 真实进程行为、嵌套Job实跑均未验证；不签 D3 动态验收、M-1/STEP008、产品 one_call 或独立安全通过；单机单会话部署前提声明不变。诊断过程全部只读（docker version/ps/inspect/format 探针、端口bind测试、hash复算），无状态变更命令，无凭据/Env读取。

---

# TASK-083 / R-077 — D3审计问题合并修复11（2026-09-25，当前置顶）

**结论：review07 的 P1/P2/F1 与 R1—R3 已按本卡范围合并修正并形成可复核代码、夹具及离线证据；新增离线三批均退出0。真实PG锁屏障、完整006/claim账本及Windows旧G恢复仍未运行，运行控制尚待原084独立增量审查，真实资源重启/认证/轮换另需明确授权；D3动态验收、M-1/STEP008及产品one_call接线均未完成。** 原083增强实现窗口接续；实际客户端Codex desktop、可见模型标签GPT-6（未核更细后缀）；本执行者没有自担独立审计。Git基础45951501d2741630a229762d6b2d3f4b34d7f702及既有差异保护，未提交/推送，未改正式docu、公共规则或旧证据。

## 修复与直接接口

- **P1** `repository.py`：claim取得来源行和活动行锁、fetch活动后才采`datetime.now(timezone.utc)`，以同一主机UTC墙钟判活动截止和旧租约，并据此形成新lease；`inspect_window`也按来源→活动行锁序取得`FOR UPDATE`活动快照后采钟。未改updated_at、预算、G/SID CAS、None提交/关门和其他时间路径。纯替身仅验证采样顺序与逻辑结果；跨来源锁后的实际事务边界由待运行`ledger_lock_barrier`证明，不能把替身当PG通过。
- **P2** `session.py`：旧`running`在未确认新claim/折叠后账目三字段均为`None`；仅明确Open错误2或旧Job terminate、整树0查询、close全成功，才把旧树记为已确认。终止/查询/wait false/close/Open不明、SID缺失或异号、部署声明缺失、来源或有效租约拒接，均不claim、不spawn、不退款，并返回`cleanup_incomplete=true`；旧树清理确定但claim回执未知，账目仍为None。旧running耗尽返回None不把快照R冒作本结果已结算秒数。已提交新窗的结算真值保持，现有`launcher.py`使用`SessionOutcome`及`replace`透传None/cleanup，无需消费者代码改动；`supervisor_main.py`亦无数值强制转换。
- **F1** 合法旧G接续保留SID=0，单独新pending活动以4294967295初领并查持久值；旧G/C重试核新SID、R/S及`dispatch_closed`未被污染。**F2/F3** 保留已修的`psycopg.errors.CheckViolation`与全部合法parts选择，未把此前未运行修正称为历史PASS。迁移空/旧行/回滚、账本、锁屏障与真实Windows场景的开始/结果ID及断言均已预列；原固定`mutex_release`文案已从真实样本移除。
- **R1** 新的测试专用`controlled_child.py`用悬停CreateProcess、精确进程句柄/PID/创建时间、独立外层Windows Job的`KILL_ON_JOB_CLOSE`、Assign和ActiveProcesses核验之后才Resume；失败按精确句柄或外层Job收尾，正证整树0。外层控制器不持业务Job句柄。runner死亡后已纳入外层Job的树由OS最后句柄关闭规则收尾；创建后尚未Assign即异常死亡时只能留下无法运行SUP的悬停进程，此极窄崩溃出口未获真实收尾正证，未来出现须记unknown停批，不能据本轮替身称全路径实测安全。
- **R2/R3** `contracts.py`要求所选各场景逐一唯一完成、单个完整`all_pass=true`/parts一致、子进程exit0且外层树0和句柄收尾确认；缺项、重复、未知、超时和清理不明均失败。stdout/stderr分存、secret在内存扫描脱敏，attempt及脚本字节/hash独立；原错误与清理错误分栏，runner失败退出1。单一绝对总期限约束资源与测试，批≤600秒含60秒收尾，单命令≤60秒含清理，每场景主动30秒截止；无耗尽后`max(1,...)`续时。子进程`-B`、`PYTHONOPTIMIZE=0`且夹具检查`sys.flags.optimize`。具体入口至收尾及未证边界见`runner-walkthrough.md`。

## 本轮离线事实与冻结

变更前review07九项哈希全部一致，五项目标pre字节/hash保存在`d3-repair-11/pre/`和`pre-hashes.txt`。最终有限差异为`incremental.diff`，旧runner→新runner另见`runner-old-to-new.diff`，完整终值见`final-hashes.txt`：repository=`bca8283316f62216f5ba94959f5c36f8c3395301aeb9dc7f21a9b376f92e29a3`，session=`eb514b5f76b0dc8b43ed8dfe116d2dc7be5a181011e1516faaa4d8005461d71c`，夹具=`a1e419f34c6464fc588b5812a9ae95545e4074c8732130cc85d2251af57ce3a1`，新runner=`26ecb423df5524ec834ffb96366ecc599f62764d648eda63f30fb6ec73d3f731`。006、windows_job、test_worker_session、offline_unit与旧runner均核对为review07原hash，001—006无改动。未覆盖其他既有仓库差异。

| 新离线批 | 原始Python命令（项目venv，`-B`） | 原始结果 | 单调计时 |
| --- | --- | --- | --- |
| 01 | `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/offline_check.py` | exit0；受影响D3/Protocol/控制替身16例OK，内存编译OK | 2.7286574s |
| 02 | `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/offline_check_02.py` | exit0；具体runner/夹具修正相关5例OK，内存编译OK | 0.7178588s |
| 03 | `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/offline_check_03.py` | exit0；两相关例OK、F1/F2/锁等待结构核对、最终diff/hash冻结 | 0.9456941s |

三批合计4.3922103秒，均低于各60秒与累计180秒限；每批stdout、stderr、meta独立保存于`Ndocu/evidence/task-083/d3-repair-11/`，无覆盖。纯替身未调用真实Docker/PG/Job或受测SUP/worker进程；静态AST只证准备结构，不证SQL事务或Windows语义。旧Job07/PG08/09未机械重跑；本轮新差异影响的旧Protocol两项在批01通过。

## 真实运行停止门与交接

本卡真实资源额度0；没有执行容器inspect/start/stop、数据库连接、认证轮换、Windows Job或真实spawn。旧记录中的两个专用容器在各自记录时点为停止并保留，**本轮未复核当前状态**；替补精确CID为`85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7`。原真实账1批/1PG测试进程/0 Windows场景，两个容器额度已用；原30分钟总账不重置，已知7.859秒+首次另行收尾（精确时长未知）+81.765秒，不能补造剩余额度。新runner只准备复用该已停CID的未来路径：严核CID/标签/镜像/唯一卷/loopback/限制、无其他任务→明确授权后启动→尝试本地测试角色认证→stdin改密→loopback新凭据核身份→完整剩余场景→精确停止复核；本地认证及改密权限**尚未证明**，失败即同CID收尾，不读旧secret、不开第三容器。单个runner须持续持有新凭据，未来编排按真实剩余总额设更小期限；不能以`--authorized-reuse`旗标代替人的授权。

待运行ID与证据标准见`runner-walkthrough.md`：`migration_empty/old/rollback`、`ledger_active_lease_rejected/new_g/exhausted/lock_barrier`、`windows_recovery`，包括旧G/C不污染新门、Job销毁/Open2/新G真实账本；既有真实局部事实只覆盖空迁移执行与负SID拒绝，不足以通过任一完整part。部署单主机单交互会话仍是受信配置声明，不是数字SID能证明的跨机保证；迁库、共享库多机或不同会话禁自动恢复。现将实际增量与离线证据交**原084独立审计**；真实控制门经审查和资源授权后方可打开。本执行者不签安全最终验收、M-1/STEP008或产品接线。

证据入口：`Ndocu/evidence/task-083/d3-repair-11/`。以下为旧结果原文字节完整保留。

---
# TASK-083 / R-077 — D3实施10替补资源接续结果（2026-09-25，当前置顶）

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

# TASK-083 / R-077 — D3实施10接续结果（置顶；历史原文保留）

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

# TASK-083 / R-077 / STEP008 执行结果：固定launcher组合真实验证09与D3恢复决策（当前有效）

**状态：卡面三项成果全部交付——①新增 launcher_control.py/launcher_scenario.py 夹具并经真实 run_supervised_window→固定SUP→worker 组合在专用真实PG上完成四场景验证：A正常完整入口 settled（真实PG认领/关门/结算，G1→G2、S=1/R=0/closed=true、SUP与worker进程复核消亡、在飞观察记录worker双进程PID+创建时间）；B父级管理截止经wait真实调用边界确定性注入（claim已提交+业务Job在管两真实前提）——SUP有界终止、结果R/S/pending全None、cleanup_incomplete=true，**SUP死亡后业务Job内2个worker进程仍存活**（控制者持精确句柄实测，"SUP退出≠树空"正证据），控制者终止后归零，DB保留R=6/S=0/closed=false不退款；C1父在Resume前被精确终止——悬停SUP不迟到Resume/不迟到认领（DB恒pending、Job对象G0/G1均不存在、2秒有界负观察无变化），控制者精确收尾悬停SUP、映射销毁核验通过；C2父在Resume后（claim完成+worker在飞时）被精确终止——已运行SUP独立完成自身截止与映射生命周期（self_exit=true、DB收敛pending/G2/S=1/closed=true、Job对象与SUP映射均销毁、两个worker PID复核消亡）。②批内尝试账2真实批/8场景启动（≤3批/≤12），前置runner缺陷两轮（预算算术、loop factory）如实留档；最终批 exit=0、8.80s、all_pass=true、19文件hash零漂移、产品源码零改动。③D3给出有原始依据的最小恢复方案：claim事务随G原子新增一列 running_owner_session_id（SUP经ProcessIdToSessionId自证），同号⇒同Local命名空间（官方S1）⇒互斥+FILE_NOT_FOUND严格区分+租约过期后全额保守折叠W；异号/缺值失败关闭；跨boot同号情形下旧进程必然全灭故折叠同样安全——**无需官方并不存在的用户态boot GUID**；不新增常驻见证、不追溯部分退款；新增持久字段须用户批准门，本卡未实施。未验证/不宣告：真实one_call业务链、旧G实际恢复执行、D3方案实施均not_run/not_done；不签独立安全验收，不宣告M-1/STEP008。执行窗口实际身份GLM-5.3-Flash（接续原083实现窗口，非独立审计）。**

## 交付1：夹具与四场景事实（最终批 20260925-1658，results.json 为准）

| 场景 | 结果 | 关键正证据 |
| --- | --- | --- |
| A 正常完整入口 | 通过 | state=settled、G1、Job名精确匹配、worker主PID 28612（venv launcher）+从PID 31580 在飞记录创建时间、active_end=0、S=1（elapsed 0.75s）、R=0/pending=0、cleanup_incomplete=false、timing(t1>t0,observed=1,W=6)、SUP PID 31612+创建时间且事后Open失败(87)；DB：pending/G2/R0/S1/closed=true/last_settled G1。 |
| B 父级管理截止 | 通过 | 注入在wait真实边界触发（G1已认领）；outcome：manager_timeout_unconfirmed、R/S/pending=None、cleanup_incomplete=true、SUP PID 13284有终止；**SUP死后Job内active=2（PID 18212/32940+创建时间在案）→控制者terminate→0**；DB：running/G1/**R=6**/S=0/closed=false/租约在——保守预扣保留、零退款。 |
| C1 父死前退出 | 通过 | P屏障证据（SUP PID 31660+创建时间+映射名）；P两进程精确终止确认；SUP悬停 alive+创建时间匹配；DB恒pending、G0/G1对象均不存在；2s负观察无变化；控制者精确终止SUP；映射open失败（销毁证实）。 |
| C2 父死后退出 | 通过 | pre_resume+at_wait双屏障；父死时DB running/G1、Job内active=2（PID 11060/6388在飞在案）；P精确终止；SUP alive→**25s内自退出（self_exit=true，未用兜底终止）**；DB收敛pending/G2/R0/S1/closed=true/last_settled G1；Job对象与SUP映射查询如实失败（销毁）；worker残留复核两PID均消亡。 |

场景D（映射交接）判定不适用：A/B/C1/C2 已覆盖映射创建/打开/写入/销毁全生命周期（C1 未打开即销毁、C2 双方句柄关闭后销毁），半帧/校验路径沿既有纯单元证据复用，无新增未覆盖风险。

## 交付2：尝试账与复用范围

- 资源预检1次（Docker/镜像/端口/venv 全OK）+ 静态检查批3次（前两次为检查脚本自身缺陷，第3次ALL PASS）。runner/批尝试4次：1652 拦截轮（runner预算算术，0启动）→ 1653 预备轮（ProactorEventLoop，0启动）→ 1655 首验批（A/B/C1通过、C2时序缺陷失败，控制者安全网精确收尾无泄漏）→ 1658 复验批（**四场景全通过**）。真实批计数2/≤3，场景启动8/≤12。
- 修复均属卡内授权范围且零产品改动：①runner TOTAL_WINDOW=660/批前检查口径；②build_activity 用 psycopg_compatible_loop_factory；③c2 触发改为"claim已提交+Job含worker"真实事实的有界轮询；④results.json 序列化 default=str。
- 复用（未重跑）：Job07五场景、PG08六例、084已审静态结论、005/repository冻结、official-facts.md 六页。本卡改动文件仅 launcher_control.py/launcher_scenario.py（新增），19文件冻结（Job07参照13+PG08四文件+新2）pre/post零漂移；attempt-1655 的批级原始日志被 1658 同名覆盖（runner固定文件名缺陷，如实登记），attempt 级 p-evidence/p-stderr 全留存。
- 资源：4个专用容器（每runner一次）全部 Exited(0) stop保留、标签 task=083/phase=d1-09/run=<runTag>、旧PG08三容器未触碰、55438释放；**卡面"一个容器"与实际的4个偏差如实登记，处置权留编排**。DSN口令仅批内环境、输出全脱敏、未打印。

## 交付3：D3 恢复决策（详见 evidence d3-sources-and-decision.md）

- 新增官方事实5项（≤6）：S1 Kernel Object Namespaces（Local\=会话命名空间；会话号按登录顺序分配）、S2 Object Names（job与互斥同空间）、S3 Job Objects/KILL_ON_JOB_CLOSE（最后句柄关闭→杀树→销毁；本批C2真实实证）、S4 ProcessIdToSessionId（SUP可自证会话号，无需特权）、S5 logoff（注销终止会话全部进程）。
- **推荐方案（须用户批准，未实施）**：claim事务随G原子写 `running_owner_session_id`；恢复时同号⇒持活动互斥（无迟到创建屏障）→严格区分ERROR_FILE_NOT_FOUND→租约过期→**全额保守折叠W**（同号跨boot情形旧进程必然全灭，折叠亦安全，故无需不可得的boot GUID）；异号/缺值（含迁移旧行NULL）⇒失败关闭。不部分退款、不新增常驻见证。替代解（不批字段）：单交互会话部署+异号全人工runbook折叠。
- **唯一必要决定**：是否批准该一列持久扩展与"同号自动折叠/异号失败关闭"语义（或选择纯人工替代解）。

## 后续（沿卡）

- 本结果与最终diff一次交原084窗口独立增量终审（B/C的注入边界与安全网语义为终审重点）；docu/CHANGE.MD与执行状态沿惯例由编排补记。
- 若D3方案获批：另卡实施（006迁移+claim接口+定向PG三例+恢复纯单元），不混入本卡。

证据目录：Ndocu/evidence/task-083/launcher-complete-09/（manifest.md、results.json、d3-sources-and-decision.md、post-run-check.json、precheck、runner、static_check_09、两轮P证据、容器inspect、批输出）。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：005及关闭门六例真实PG验证08（当前有效）

**状态：卡面精确六例在专用真实PG上一次全部通过——`Ran 6 tests in 1.897s / OK`、unittest exit=0、0失败/0错误/0skip、failfast未触发（stderr原始输出在案）；005空表迁移仅增dispatch_closed、非空表005整体回滚、关门后拒绝admit/mark且合法outcome收敛、关门先提交先于并发admit/mark（真实来源锁+屏障交错）、取消关门+旧dispatched UNKNOWN收敛、旧G/C幂等ALREADY_SETTLED不碰新窗，全部实际事务验证成立。三容器（批次一/二/三）均stop后Running=false、cleanup_ok=true，容器/卷/库/6个schema全保留，冻结四文件hash运行前后零漂移，源码/测试/迁移/正式docu/公共库/Git零写入。仅确认这六个当前真实PG用例：不扩成新D1真实launcher、不覆盖run_supervised_window固定SUP入口、不解决D3旧G恢复、不签M-1/STEP008或独立安全通过。执行窗口实际身份GLM-5.3-Flash（接续原083实现窗口，非独立审计，如实登记）。**

## 批次史与例外授权（如实登记）

| 批次 | runTag/容器 | 结果 | 根因与处置 |
| --- | --- | --- | --- |
| 一 | 20260925-1455 / 8b2b6349… | 就绪核对30s超时停批，六例not_run | 本卡自备runner就绪检查SQL将PG裸关键字`current_user`误写`current_user()`，服务器持续报语法错误；连接/认证/库全程正常。非环境/夹具/被测对象缺陷。 |
| 二 | 20260925-1509 / 10faef60… | 身份核对停批（连接1.62s即成功），六例not_run | runner将`inet_server_port()`（返回容器内监听端口5432）误预期为宿主映射端口55437；db/user核对全对。 |
| 三（最终） | 20260925-1515 / b8b7982f… | **六例全部通过** | 修正01—03后：标签+宿主端口绑定核对OK、PG就绪身份三核对一致（1.64s）、unittest exit=0、finally干净（5.49s总）。 |

两次停批均由用户明确授权例外后继续（15:10"授权例外重跑"、15:15"授权批次三"）；三次运行的runner/输出/inspect全部留档，批次三实际运行脚本字节副本runner-batch3-as-run.py（sha256=52ba7c44…74933）与误标verdict的runner-state.json原样保留不覆盖。runner共有三处检查/解析缺陷（current_user括号、inet_server_port语义、Ran/OK摘要解析只查stdout），均属本轮证据目录内自备脚本问题，不影响夹具/被测对象证据；verdict以原始stderr输出+退出码为准。

## 六例逐项事实（unittest-stderr.txt原始行+stdout schema行）

| 用例 | 实际 | 保留schema（全保留，无失败保留行） |
| --- | --- | --- |
| pg_migration_01_empty_table_adds_only_closed_column | ok：001—004后空activities执行005，仅新增列dispatch_closed(boolean,NO,default false) | task083_migration_91f93dae… |
| pg_migration_02_nonempty_table_rolls_back_whole_005 | ok：非空表005抛psycopg.Error、ROLLBACK后数据仍在且无dispatch_closed列，合成行FK清理 | task083_migration_b0bae76d… |
| pg01_close_settle_and_old_gc_does_not_touch_new_window | ok：关门→关门幂等→settle SETTLED→新代次claim开门→旧G settle ALREADY_SETTLED不碰新窗→过代次close拒绝 | task083_close_cdef47ba… |
| pg02_closed_gate_rejects_admit_mark_but_records_outcomes | ok：关门后admit/mark均AdmissionDenied，reserved/dispatched记UNKNOWN、received保留，not_sent=0/unknown=2/received=1 | task083_close_8fed9a16… |
| pg03_close_commits_before_concurrent_admit_and_mark | ok：真实来源锁持有+请求屏障控制交错，close先提交，并发admit/mark均拒绝 | task083_close_6d1cda74… |
| pg04_cancel_closes_gate_and_old_dispatched_unknown_converges | ok：cancel关门（closed=true、R=0、S=90整树结算），旧dispatched记UNKNOWN收敛 | task083_close_97643930… |

## 版本、资源与零写入证明

- venv Python 3.12.10、psycopg 3.3.5、PostgreSQL 17.11 (Debian 17.11-1.pgdg12+2)、Docker server 29.7.2、固定镜像pgvector/pgvector:0.8.6-pg17-bookworm（sha256:cf134a767f47…，在位未拉取）；容器1CPU/512MiB/pids128/restart=no/bridge/无宿主bind挂载/仅127.0.0.1:55437→5432；合成账号task083_pg08+随机口令仅注入本次子进程环境，全部输出经口令过滤，未记录完整含口令DSN。
- 运行前后核验：四冻结文件（pg_migration.py/pg_close.py/repository.py/005.sql）hash全MATCH零漂移（precheck两次+post-run-hash-check.txt）；git status backend/仅含083既有实现差异，与卡面"既有差异保护"一致；本卡写入仅限Ndocu/evidence/task-083/pg-run-08/与本置顶段。
- 三个容器均保留（Running=false），含各自匿名卷与库实例；未删除任何容器/卷/schema/database，未执行用户库迁移，未接管073/074/079旧资源。

## 边界与后续（沿卡，不扩）

- 本批只确认上述六个当前真实PG用例；不构成新D1固定launcher真实入口、不覆盖run_supervised_window固定SUP入口、不解决D3旧G恢复（化身来源决策仍开放）、不签M-1/STEP008完成。Job07已验局部行为未重测。
- runner三缺陷修正（01裸关键字、02 proc初始化、03端口语义、04摘要解析）已留档于runner.py供后续卡复用；错误经验应记入D:\shspic\错误记录（编排裁定）。
- docu/CHANGE.MD与执行状态沿惯例由编排补记（本卡禁改正式docu）。证据目录：Ndocu/evidence/task-083/pg-run-08/（manifest.md含批次史与授权记录、precheck、runner及批次三字节副本、container-inspect-created/final、unittest-stdout/stderr/meta、schemas.txt、runner-log/state、post-run-hash-check.txt）。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：受控真实Windows Job验证07（当前有效）

**状态：编排一次解冻的现有Job01—05真实Windows合成批，五场景全部实际启动并按已审控制器裁定通过——01正常早停（settled、事件序[inspect,claim,close_db,settle]、C=1≤W=6、整树0后关门/结算）、02挂死（stopped_at_deadline、全窗6s保留不结算、真实树空0）、03主进程先退后代存（descendants_after_primary=2、确切终止至整树0）、05同名Job碰撞拒绝（collision_rejected=true、原Job精确身份在案）、04最后句柄（Start生命周期+身份回执、PID/创建时间精确核验、SUP退出前Job计数1、释放观察句柄后worker signaled、对象销毁后查询如实null）。批命令exit=0、墙钟14.122011s（单一计时源run_batch_07.py perf_counter）≤60s，未超时、无cleanup_incomplete、无归属/树未知、无句柄错配；运行前后15项冻结hash零漂移（卡面运行链4文件+9直接依赖+信息项2），精确PID残留核验与补充只读扫描均无遗留，本批对源码/夹具/迁移/正式docu/公共库/旧证据零写入。即使五例全过，也只确认这五个已审合成Job行为：不覆盖新run_supervised_window固定SUP入口（01/02直接run_once、03/05直接Job）、不覆盖真实PG/005（02账本为合成FakeLedger，不得声称PG真实退款）、不解决D3旧G恢复，不宣告M-1/STEP008完成。执行者不签独立安全结论，回传由编排裁定。执行窗口实际身份：GLM-5.3-Flash（接续原083增强实现窗口，非独立审计，如实登记）。**

## 场景逐项事实（依据实际控制器输出裁定；原始JSON逐行存证据，不事后编造）

| 场景 | 实际 | 身份正证据（runTag / UUID+G / Job名 / PID） | 关键观察与清理 |
| --- | --- | --- | --- |
| 01 正常早停 | 已启动，通过 | job-01-e815efbd；活动 81455924-4f7c-49b6-8292-6b79693b2a94，G1；Local\RetroLume.Activity.814559244f7c49b682926b79693b2a94.G1；worker PID 30240（outcome.pid） | state=settled、events=[inspect,claim,close_db,settle]（=已审预期次序）、timing_diagnostic t1>t0（Δ=750000000ns）→C=1、W=6，1≤C≤W；active_processes_before_resume=1、active_processes_at_end=0（Job整树0后关门/结算）；settled=1/reserved=0/pending_fold=0、elapsed=0.75s、cleanup_incomplete=false。账本为合成FakeLedger，不构成PG真实退款证据。 |
| 02 挂死 | 已启动，通过 | job-02-1b31fce6；活动 dc717c60-c767-4272-b069-93297ea56a8c，G1；…dc717c60c7674272b06993297ea56a8c.G1；worker PID 25304 | state=stopped_at_deadline、reserved_seconds=6、settled_seconds=0、events=[inspect,claim]（无settle）、elapsed=5.0s、pending_fold_seconds=6（交原规则保守折叠）；真实树空观察 active_processes_at_end=0、cleanup_incomplete=false——全窗保守账面、不部分退款。 |
| 03 主退后代存 | 已启动，通过 | job-03-29a56b7e；活动 4a5afcc6-6c40-4f70-a735-7f68a9f3f723，G1；…4a5afcc66c404f70a7357f68a9f3f723.G1 | 主进程退出后Job查询 descendants_after_primary=2（>0，主退不当树空；查询值如实记录，不作进一步推断）；随后确切终止/等待至 active_processes_at_end=0、cleanup_incomplete=false。控制器输出不含本场景worker PID（悬停期已由控制器以精确句柄+创建时间+active_before=1核验），如实记录、不补造。 |
| 05 同名碰撞 | 已启动，通过 | job-05-2c58bbb9；活动 a8a1440a-27ea-4a86-8462-044caba2db60，G1；…a8a1440a27ea4a868462044caba2db60.G1 | collision_rejected=true：同名 NamedJob.create 被拒（JobUnknown），原Job身份精确在案、不按模糊名字查杀；active_processes_at_end=0、cleanup_incomplete=false。控制器输出同样不含worker PID（口径同03）。 |
| 04 最后句柄 | 已启动，通过 | job-death-5cdecc24；活动 15b1838f-48aa-4415-93fb-cce26d058597，G7；…15b1838f48aa441593fbcce26d058597.G7；worker PID 27856、created_100ns=134347917200933325 | Start生命周期与身份回执：子端Open消费Start并回执悬停身份后父才释放唯一Start句柄；PID+创建时间经OpenProcess/GetProcessTimes核验；active_processes=1（悬停）与active_processes_before_supervisor_exit=1（Resume前Job计数1）；观察Job句柄先关、SUP退出码0；释放观察句柄后最后Job句柄关闭使worker_signaled_after_last_job_handle_closed=true；对象销毁后无法查询ActiveProcesses时active_processes_at_end=null如实写入（tree_evidence原文在案），不把单进程夹具推成任意整树通用证明。 |

## 命令、退出码与单一计时来源

- 唯一命令（无第二次运行）：`D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe -B -m fixtures.task083.job_batch`，工作目录 `backend/tests`；run_batch_07.py 包装（Popen在OS层直录stdout/stderr，退出码取自Popen.wait()，不以工具yield当进程已结束）。
- exit_code=0；墙钟14.122011s（单一计时源 run_batch_07.py time.perf_counter；起2026-09-25T14:35:06.067+08:00，止14:35:20.189+08:00）；timed_out_at_60s=false；批内55s自身deadline与场景30s上限均未触及；stderr为空。
- 实际启动5/5，通过5/5，失败0，跳过0；场景次序01→02→03→05→04按已审脚本内置次序执行，未重排、未补跑。

## 清理确认与零写入证明

- 逐场景控制器 cleanup_incomplete=false；01/02/03/05 active_processes_at_end=0（确切整树0）；04 worker signaled（最后句柄关闭致worker退出）。
- 运行后只读精确核验（post-run-check.json）：控制器打印的 01 PID 30240、02 PID 25304、04 PID 27856 OpenProcess 均error 87（进程已不存在），无"同PID同创建时间"残留；03/05 控制器不打印PID，以整树0为清理证据；补充只读名称扫描（task083相关命令行）0条，仅作旁证、不充当树空证明。未知对象/遗留：无；旧不明进程未触碰。
- 运行前（pre-run-check.json）与运行后（post-run-check.json）各15项hash一致：卡面运行链4文件（job_batch 648e419c…、job_control 5bc35bf1…、scenario_child 98f132f2…、fixture c9970b8d…）+9直接依赖（windows_job/session/command/worker_main/launcher/supervisor_ipc/supervisor_main/gate/test_worker_session，沿stub-fix-05与084 review-02冻结记录）+信息项repository/005——本批零写入证明。

## 边界、复用与后续（沿卡，不扩）

- 本批只确认上述五个已审合成Job行为；不覆盖新 run_supervised_window 固定SUP真实入口、不覆盖真实PG/005、不解决D3旧G恢复，不宣告M-1/STEP008完成。剩余已登记路线：专用PG六例、新D1受控入口准备、D3化身事实决策，均不在本批。
- 旧5场景尝试、超时偏差与费用不重置；本批为独立一次授权运行，未复用旧04 count0筛选替代观察。
- 执行者不签独立安全结论；需要独立解释的新风险沿084窗口增量审，不默认再审全仓。docu/CHANGE.MD与正式执行状态沿惯例由编排补记（本卡禁改正式docu）。
- 证据目录 Ndocu/evidence/task-083/job-run-07/：manifest.md（运行前冻结值/命令/次序/预算/停止与精确清理办法）、prep_run07.py、pre-run-check.json、run_batch_07.py、run-batch-stdout.log（逐场景原始JSON）、run-batch-stderr.log、run-batch-meta.json、post_check_07.py、post-run-check.json。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：生命周期夹具完整修正06（当前有效）

**状态：review-04定位的三处同链替身缺陷（①硬编码身份回执 ②open_existing断言硬编码身份 ③starter/kernel句柄基址撞号）已一次合并修复，静态核对34项ALL_PASS，最终定向批三例全部通过——生命周期两例首次经真实verify_last_handle完整控制流验证通过（此前三轮分别停在argtypes赋值、身份校验），05确定时钟例首次通过（t1>t0、ceil=1/W=6、树0后关门、同G结算重试）。本卡只修替身不修控制器，job_control.py语义零改动；真实Job与PG仍冻结，静态/替身通过不构成真实OS证据，不宣告M-1/STEP008完成，不填写编排最终验收。执行窗口实际身份：GLM-5.3-Flash（接续原083增强实现任务，非独立审计，如实登记）。**

## 本轮改动（唯一允许文件，三项一次完成）

backend/tests/fixtures/task083/focused_unit.py：pre_sha256=4a633aff…7a1ca（=卡冻结值，改前真实字节副本+hash见 pre/、pre-hashes.txt）→ new_sha256=dfaaf814bb6abeea0a7f82d8499b1e03915c87bad50aa4a50295fcfde3995259。全部改动限于StartLifecycleTests区段（区段外head/tail字节级不变，static-check证明；incremental.diff存档）：

1. **身份派生（修正①）**：删除硬编码`_identity_lines`（旧activity="11111111-…"、run_tag="lifecycle-unit"）；fake_spawn从真实spawn实参派生身份——args[4]=activity_id、args[5]=int(str(generation))、args[6]=run_tag，索引经job_control.py:82-84实际调用文本逐项核对（sys._base_executable, "-B", str(fixture), "controller", activity_id, str(generation), run_tag, start_name），非机械照抄报告数字；按真实job_name函数构造created/resumed回执；pid=123、created_100ns=0、active_processes=1及resumed pid=123等协议字段保持不变。不patch控制器uuid4、不固定控制器内部随机身份、不取消任何身份校验（patch面仍仅三处OS边界：job_control.ctypes.WinDLL、job_control.asyncio.create_subprocess_exec、job_control.NamedJob）。
2. **派生身份回传与断言（修正②）**：_run签名改为`(*, receipt="identity", spawn_error=None)`，返回(次序log, kernels, 派生身份, result, 异常)；三分支定义清晰——"identity"=按派生身份回执两行、"empty"=spawn成功但空回执、spawn异常=不产生身份（保持空dict）；成功例与失败分支B的open_existing正反断言改用派生身份+字面量7（job_control.py:36固定int 7与FakeNamedJob记录类型一致）；分支A新增显式断言`identity == {}`（spawn未成功不产生派生身份，防未定义身份变量）。断言能发现任何不应发生的open_existing调用：控制器内部随机activity经spawn实参派生同源，不以硬编码元组掩盖行为。
3. **句柄基址分离（修正③）**：Kernel.__init__接收base，fake_windll按实例序号分配互不相交基址（starter=100起、kernel=100100起）；Start父句柄与worker/事件句柄不再共用编号空间，`count(("close_handle", start_handle))==1`等断言按原语义成立；每类API的返回、指针输出（byref _FILETIME全0与created_100ns=0匹配）与调用记录语义不变；Start回执后关闭、恰一次释放、观察Job先释放再Exit、失败清理等次序断言原样保留，不改断言迎合错误次序。

## 静态核对（一次执行额度，34项ALL_PASS）

static_check_06.py（托管3.13.12执行，文本/AST/hash三层，不import不写pyc，0.036秒≤60秒，单次执行无重试）：① 三文件冻结复算MATCH（focused_unit pre=4a633aff…、job_control=5bc35bf1…3980d2、offline_unit=3029a709…4c5c），零漂移；② 区段限制：pre/post的head（模块docstring/导入/EventControlTests）与tail（FrameTests/ConfigFactory/LauncherTests/main）字节级相等，diff仅落StartLifecycleTests区段——碰撞两例与D1期限用例方法体未变；③ AST：_identity_lines已删、_run唯一5元组return、三方法齐备；④ 全流程文本一致性：派生索引与job_control.py:82-84实参顺序跨文件核对、open_existing传int generation、身份校验tuple原文未动（无契约弱化）、无uuid4 patch、回执字段与协议一致；⑤ 有限diff写入incremental.diff。

## 运行账（新增且仅一次定向批；先冻结后运行）

| 命令 | 退出码 | 耗时（单一计时源run_batch_06.py perf_counter） | 结果 |
| --- | --- | --- | --- |
| 1：`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/focused_unit.py --failfast StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt StartLifecycleTests.test_04_start_handle_release_exactly_once_on_failure`（工作目录=项目根） | 0 | 2.478099秒（≤60秒） | **2 tests OK**：成功例与失败例均实际运行，failfast未触发任何跳过 |
| 2：`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry`（命令1通过后才启动） | 0 | 0.883秒（≤60秒） | **1 test OK** |

- 成功例：真实verify_last_handle控制流全路径——fake spawn→SetEvent(100)→首次readline收到派生身份回执→job_control.py:97-100身份校验通过→CloseHandle(100)恰一次→OpenProcess/GetProcessTimes→open_existing（派生身份,int 7）→Arm→resumed回执校验→job_close先于Exit→returncode 0→最后句柄等待通过。
- 05例诊断行：t0_ns=1000000000000、t1_ns=1000400000000（t1>t0）、delta_ns=400000000、observed=1、window=6、state=settled、job_events=[spawn_suspended, resume, query, close_job]；导入hash session=502a3743…f16c、offline_unit=3029a709…4c5c与冻结一致（日志offline-05-06.log）。
- 累计3.361秒≤120秒；PASS仅绑定最终快照dfaaf814…5259；无真实事件/Job/spawn/子进程/PG/Docker/网络调用。

## PASS适用范围、复用与风险

- 保留PASS（局部不变性延续，不重跑）：EventControlTests碰撞两例、LauncherTests D1期限一例——区段外字节级不变+直接依赖冻结复算MATCH；第12项及其余9项沿084口径复用。
- 未运行/缺口（如实登记）：真实Job与PG仍冻结；生命周期两例验证的是真实verify_last_handle控制流+全替身OS边界，不构成真实Start/Arm/Exit事件、真实Job对象、真实子进程证据；旧05根因仍未证（本轮按要求不研究）；D3不研究不实现，旧G未知保持失败关闭；新D1固定launcher真实入口OS证据缺口保留。
- 后续（沿卡）：三例及差异经原084增量确认后，由编排分别安排受控真实验证；本卡未追加任何运行。docu/CHANGE.MD登记沿前几轮惯例由编排补记（卡面禁改正式docu）。
- 证据目录Ndocu/evidence/task-083/fixture-completion-06/：prep_evidence.py、pre/（三文件字节副本）、pre-hashes.txt、static_check_06.py、static-check.txt、incremental.diff、final-hashes.txt、manifest-final.txt、run_batch_06.py、unit-lifecycle-06.log、unit-lifecycle-06-meta.txt、offline-05-06.log、offline-05-06-meta.txt。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# 历史：TASK-083 / R-077 / STEP008 执行结果：夹具替身修正05与剩余三例验证（stub-fix-05轮原文）

**状态：04轮替身兼容缺陷已修——partial包装使argtypes/restype赋值合法，静态核对ALL_PASS；但新增定向批首命令 1/2 FAIL 即停：生命周期成功例在真实verify_last_handle内推进到身份回执校验后，因夹具回执身份与控制器内部随机身份结构性不匹配（"Job/G/runTag身份不匹配"）而失败；第二例因failfast未运行，命令2（offline 05）not_run。按卡"失败即停、不再修正复跑、不开启无限修正批"，本轮到此交回原084独立窗口审视夹具与具体失败。Job/PG仍冻结；不宣告真实Job/PG通过、D3恢复解决或M-1/STEP008完成。执行窗口实际身份：GLM-5.3-Flash（接续原083增强实现任务，非独立审计）。**

## 本轮改动（唯一允许文件）

backend/tests/fixtures/task083/focused_unit.py：pre_sha256=1e58eb03…8ce08（=卡冻结值，改前真实字节副本+hash见 pre/、pre-hashes.txt）→ new_sha256=4a633aff536f833cdbf3a266be2d44de70b8e01105a204b68d7947995627a1ca。仅三处hunk（incremental.diff共40行）：① 新增标准库导入 `from functools import partial`；② StartLifecycleTests docstring追加partial包装说明（纯追加）；③ StartLifecycleTests._run局部Kernel.__init__将8个API（CreateEventW/SetEvent/CloseHandle/OpenProcess/GetProcessTimes/OpenEventW/WaitForSingleObject/TerminateProcess）以partial包装的实例闭包占位，使verify_last_handle（job_control.py:49-71）对替身API的argtypes/restype赋值合法。API调用语义、参数、返回值、事件记录与故障注入行为零改动。job_control.py（5bc35bf1…3980d2）、offline_unit.py（3029a709…4c5c）及13个冻结文件逐一复算零漂移（final-hashes.txt）。其余全部顶层节点AST与改前副本逐项一致：碰撞两例、D1期限用例的测试方法与直接依赖均未受影响，其旧PASS按"局部不变性"延续证据（不重跑）；functools导入不改变全局初始化行为。

## 静态核对（3次尝试，最终一次ALL_PASS）

stub_fix_05.py（AST/hash/diff，不import、不写pyc，以backend/.venv/Scripts/python.exe -B执行——本卡默认项目解释器，无解释器偏差）：job_control内verify_last_handle/_new_event_or_reject对starter/kernel的argtypes/restype赋值面与调用面各8个API，与Kernel partial包装集和方法集逐一闭合；15个冻结hash全FROZEN_OK。attempt-01/02失败均为检查脚本自身缺陷（ast.AsyncFunctionDef漏扫async的verify_last_handle；docstring前缀判定未先归一缩进，并由此暴露首次docstring编辑曾使62-66行降为0缩进，已恢复统一4空格缩进），非目标文件问题；两次失败日志与meta原样存档（static-attempt-01-fail.log、static-attempt-02-fail.log及对应meta），最终静态static.log+static-meta.txt（1.12秒内，≤60秒达标）。上一轮（04）静态用托管3.13.12而非卡定venv的偏差如实保留于04轮历史记录，本轮不冒称按原命令执行。

## 运行账（新增定向批，失败即停）

- **Command 1**（`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/focused_unit.py --failfast -v StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt StartLifecycleTests.test_04_start_handle_release_exactly_once_on_failure`，工作目录=项目根D:/shspic/project_NO3_RetroLume-agent）：**exit=1，1.1161450秒**（run_cmd.py单一计时源perf_counter；unit-lifecycle-01.log/meta）。
  - FAIL（failfast，第二例未运行）：`test_04_start_handle_closes_after_identity_receipt`——`assertIsNone(exc)`失败，exc=AssertionError('Job/G/runTag身份不匹配')。**精确定位（未修）**：修正04的AttributeError已消除，流程真实推进：fake spawn→SetEvent(100)→首次readline收到_identity_lines回执→json解析→job_control.py:97-100身份校验失败。verify_last_handle内部自生成activity_id=str(uuid4())（:34）与run_tag="job-death-"+uuid4().hex[:8]（:35），而_identity_lines回执硬编码activity="11111111-1111-1111-1111-111111111111"、run_tag="lifecycle-unit"，phase/generation/pid/created_100ns匹配但activity_id/run_tag/job_name三字段必不匹配——夹具回执身份与控制器内部随机身份结构性不相容，是partial修复点之后新暴露的第二个夹具缺陷（修正04运行从未到达此路径）。修复需patch job_control.uuid4为确定性值并同步_identity_lines常量（或等价方案），属语义性替身扩展，超出本卡"只改Kernel API替身+必须标准库导入"授权，按停机纪律不修、不复跑，交原084窗口裁定。
  - `test_04_start_handle_release_exactly_once_on_failure`：**not_run**（failfast首例失败即停；其分支A spawn异常与分支B空回执路径均不触及身份校验，但本轮无运行证据）。
- **Command 2**（offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry）：**not_run**（首命令失败即停）。05确定时钟注入运行验证仍为零。

## PASS适用范围、复用与风险

- 保留PASS（局部不变性延续，不重跑）：EventControlTests碰撞两例、LauncherTests.test_d1_deadline_before_resume_terminates_exact_owner（AST逐项一致+直接依赖FROZEN_OK+导入增量functools唯一）；第12项及其余9项沿084口径复用。
- 风险/未闭合：① job_control.py生命周期修改至今无一次完整通过运行（本轮推进至身份校验即失败，04轮失败点在argtypes赋值）；② D1期限PASS原绑定focused_unit.py旧hash 1e58eb03…，本文件已轮换为4a633aff…，其PASS按"测试方法与依赖未变的局部不变性"主张，适用性由084认定；③ 05仍未运行验证；④ 新暴露夹具身份缺陷的最小修法待084审定，本卡未实施；⑤ 真实Job/PG/事件/子进程本轮零启动，D3恢复未闭合、新D1固定入口OS证据缺口保留；⑥ docu/CHANGE.MD仍未登记（卡面禁改正式docu，建议由编排补记）。
- 证据目录Ndocu/evidence/task-083/stub-fix-05/：prep_evidence.py、pre/、pre-hashes.txt、stub_fix_05.py、static.log、static-meta.txt、static-attempt-01-fail.log、static-attempt-02-fail.log及两个对应attempt meta、incremental.diff、final-hashes.txt、manifest-final.txt、run_cmd.py、unit-lifecycle-01.log、unit-lifecycle-01-meta.txt。本轮结果以上方置顶段为准，历史各轮原文字节保留于下方分隔线之后。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：定向夹具修正04（当前有效）

**状态：三项夹具修正候选已写入（AST/静态一次通过、13个未改文件零漂移），最终离线批首命令 2/5 FAIL 即停：新增生命周期两例因测试替身自身 AttributeError 未执行到被测路径，D1 Resume 前截止用例修改后首次 PASS；第二命令 not_run，05 时钟注入未运行验证。按卡"失败即停、不追加修正复检"，本轮未修替身、未复跑。Job/PG 仍冻结；不宣告真实 Job/PG 通过、D3 恢复解决或 M-1/STEP008 完成。**

## 三项改动（原→新）

| 文件 | pre_sha256（与卡冻结值一致） | new_sha256 | 改动 |
| --- | --- | --- | --- |
| backend/tests/fixtures/task083/job_control.py | f76f0a4e…dcb95 | 5bc35bf1…3980d2 | `verify_last_handle` 合并为单一大 try：create_subprocess/SetEvent→readline→身份校验通过后才 `starter.CloseHandle(start_event)`（start_released 标记防重）；finally 统一精确收尾含 start_event 恰好一次释放与 proc None 防护。原"SetEvent 后立即关闭唯一父句柄"的竞态出口删除；kernel 配置段前移至 try 前（纯 argtypes 赋值，行为不变）；deadline/remaining 与观察 Job 释放时点不变，不延长总期限、不跨越最后句柄死亡测试。 |
| backend/tests/fixtures/task083/focused_unit.py | 0887adee…cff6d4 | 1e58eb03…8ce08 | D1 期限用例 `_remaining` 序列 (5,5,5,0,0)→(5,5,0,5,5)（第三次 Resume 前检查归零，finally 清理保有 5s），断言增强为精确事件序列+账字段未知+不读结果；新增 StartLifecycleTests（2 方法，调用真实 verify_last_handle，patch job_control.ctypes.WinDLL / asyncio.create_subprocess_exec / NamedJob；成功分支断言回执先于关闭、失败分支覆盖提前异常与空回执）。 |
| backend/tests/fixtures/task083/offline_unit.py | 3e79ce97…5cb04 | 3029a709…4c5c | 新增 _TestClock（读取返回固定值、仅显式 advance 0.4s）；FakeJob.wait_empty_until 注入 clock 时以确定性推进代替 2ms 真实睡眠（clock=None 旧路径保留不变，其他用例零影响）；test_05 以 patch("app.worker.session.time") 与本模块 time（脚本直跑为 __main__）注入，断言 t1>t0、Δ=400000000ns、ceil=1、W=6、job_closed 先于 close_db、settle×2 同 G、(settled,reserved,pending)=(1,0,0)。生产 session.py 未触碰，C0 拒退与 C>W 拒绝语义不变（hash 零漂移）。 |

完整有限 diff：`incremental.diff`；逐文件新旧 hash 与未改文件防漂移：`final-hashes.txt`（launcher/session/supervisor_ipc/supervisor_main/command/worker_main/gate/repository/005/fixture.py/scenario_child.py/job_batch.py 全部 FROZEN_OK；windows_job.py 登记 d05ca259…f6f6，job_name 纯字符串构造已核实）。改前真实字节副本与卡冻结值核对一致：`pre-hashes.txt`、`pre/`。上一轮卡已由编排归档 `Ndocu/archives/TASK-083-before-fixture-repair04-20260924.md`。

## 验证账与失败定位

证据目录 `Ndocu/evidence/task-083/fixture-repair-04/`：

- 静态检查一次通过（AST parse，不 import、不写 pyc）：`static_check.py` → AST_OK 3 路径 + FROZEN_OK 12 路径，0.047345 秒（托管 3.13.12 解释器执行，仅静态解析）。
- 最终离线批 manifest（6 方法限额、OS 替身覆盖确认清单）：`manifest-final.txt`；runner `run_batch.py`，单一计时来源 time.perf_counter。
- **Command 1**（`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/focused_unit.py` + 5 个精确 ID）：**exit=1，1.0503720 秒**（`unit-final-01.log`、`unit-final-meta.txt`）。
  - ok×3：`EventControlTests.test_04_start_collision_closes_only_returned_handle`、`test_04_start_creation_error_and_new_handle`（原碰撞两例未改）、`LauncherTests.test_d1_deadline_before_resume_terminates_exact_owner`（修改后 PASS：state=manager_startup_deadline_unconfirmed、精确序列 ["create_suspended","identity",("wait",0),"terminate",("wait",5.0),"process_close"]、无 resume、账字段 (None,None,None)、无 read_result——**Resume 前截止分支首次有效替身验证**；claim 结构上不可能发生，因 SUP 从未 resume 且 claim 仅存在于 SUP 内的 session.run_once）。
  - FAIL×2：`StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt`、`test_04_start_handle_release_exactly_once_on_failure`，原因均为 `AttributeError("'method' object has no attribute 'argtypes'")`。定位：verify_last_handle 对 starter/kernel 的 API 设置 argtypes/restype（job_control.py:49-71），替身 Kernel 以普通绑定方法模拟 API 不可设属性；异常发生在任何生命周期断言与 job_control 新代码路径执行之前。**job_control.py 生命周期修改的运行验证为零。**
- **Command 2**（offline_unit.py test_05）：**not_run**（首命令失败即停）。05 确定时钟注入运行验证为零，`__main__.time` patch 方案亦未经运行检验。

## 已明确的下一步（供编排裁定，未执行）

最小修正只涉 focused_unit.py 的 StartLifecycleTests 替身：Kernel 各 API 用 functools.partial（或可设属性的可调用包装）绑定实例闭包，使 argtypes/restype 赋值合法；job_control.py 与 offline_unit.py 不动。修正后 focused_unit.py hash 轮换，本轮 command 1 的 5 例（含已 PASS 的碰撞两例与 D1）须按同一 manifest 复跑，再跑 command 2；按卡"后补代码对应测试 not_run，不能沿用通过"。生命周期两例通过后，04 生命周期修改才存在首个替身运行证据；随后由原 084 窗口只复核本三处差异与日志，受控 Job 真实验证仍另卡（新 D1 固定 launcher 真实入口仍无运行证据，Job01—05 不能替代）。

## 复用与风险

- 复用：第 12 项不重跑（command/worker_main/gate 未变，本轮 FROZEN_OK 再证）；其余 9 项按未受影响依赖沿用；旧 05 诊断不重复取证；D3 本轮不再调查，旧 G 未知继续失败关闭。
- 风险：① job_control.py 修改与 offline_unit.py 时钟注入当前只有静态证据，行为验证 not_run；② 生命周期替身修复未实施，其 PASS 行为未知；③ D1 本轮 PASS 绑定 focused_unit.py hash 1e58eb03…8ce08，同文件再改即失效；④ 真实 Start/Arm/Exit 事件、子进程、Job、最后句柄行为仍未运行（Job 冻结）；⑤ 旧 05 失败原因仍未唯一确定（如实保留），2ms 跨时钟刻度依赖已在源码层消除但待运行证明；⑥ docu/CHANGE.MD 未登记（卡面禁改正式 docu，建议由编排补记）。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：review-02 后定向接续（当前有效）

**状态：部分完成，按本卡最终批次失败即停。Job/PG 运行门仍冻结，D1、D3 未闭合，05 旧失败未查明；不得接线或宣告 STEP008/M-1 完成。** 执行身份为原 083 实现窗口 GPT-6，本窗口自本卡起是实现者而非独立审计者。原 5 个 Job、旧 04 缺证与全部历史修正/失败不清零；本轮真实 Job/PG 启动数均为 0，005 未执行。

## 四项结论

| 项 | 本轮结果 | 定位及限制 |
| --- | --- | --- |
| 04 Start 事件 | **代码候选已修。** `CreateEventW` 返回已有对象（183）或失败即关闭本次句柄并拒绝；01—05 控制链 Start/Arm 共用检查，不触发外来事件。纯替身碰撞/失败/新建 2 项显示 ok。 | `backend/tests/fixtures/task083/job_control.py:21,56`；`unit-final-01.log`。无真实事件/Job 验证，旧 04 证据无法追补。改前真实 `fixture.py` 字节副本已保存在 `focused-repair-03/pre/`，本轮未改它。 |
| 05 计时 | **根因未证，未改 1≤C≤W。** 按预列 ID 仅诊断一次，退出 0；本次 `t0=1172500000000ns`、`t1=1172515000000ns`、`delta=15000000ns`、`C=1`、`W=6`，sleep 前后读数分别等于这两个时间，Job 替身事件为 `spawn_suspended,resume,query,close_job`，状态 settled。导入的 session/test 哈希随原始 JSON 记录。 | `05-diagnostic.log`、`05-diagnostic-meta.txt`；诊断时 session 哈希 9956e442…，最终版本另有 D1 输出字段。单次 PASS 未复现 review-02 的 `elapsed_violation_full_reservation`，不能解释旧失败，也不能据此关闭。05 不在最终批次重复。 |
| D1 父 launcher/SUP | **固定悬停控制候选已写，验证未通过。** `run_supervised_window` 仅接真实仓储、受限 `SessionConfig`、`WorkerCommand`；请求经限长 16 KiB 命名映射提交，父以显式 base Python 与固定 `app.worker.supervisor_main` 创建悬停进程，禁句柄继承，取得精确进程/主线程句柄与创建时间后才 Resume。子端固定入口验证请求，执行 `SingleWindowSupervisor.run_once`，结果只在确切 SUP 退出后读取并校验帧、身份和形状。启动、运行、终止等待共享绝对 `deadline` 与预留清理窗；无 SUP 结果时 S/R/待折叠均 None、`cleanup_incomplete=True`。 | `launcher.py:93,170,196,215`；`supervisor_ipc.py:41,50,88`；`supervisor_main.py:23,58`；`session.py:66`。最终批次 10 项中 9 ok、1 fail，整批退出 1；失败项的替身把第四次检查设为截止，此时实现已 Resume，故实际 `manager_timeout_unconfirmed`，期待的 Resume 前状态不成立。该分支无有效验证；旧第12项因停批 not_run。Win32 固定入口/venv 转发、父死亡悬停对象及真实超时/句柄收尾均 not_run。CreateProcessW 内核永久阻塞不在硬墙钟承诺内；同权限恶意旁路未证明排除。 |
| D3 旧 G 恢复 | **事实调查完成，提案待裁决。** 只讨论旧 W 全额折叠，不追溯部分退款，不改模型。Microsoft Learn 支持 Local 命名空间按登录会话分隔，`ProcessIdToSessionId` 只给 numeric ID，`GetTickCount64` 是 uptime 而非唯一启动 ID；快速启动属于 S4，不能以墙钟或数值相同证明命名空间化身。六页官方取证链接、适用范围和未证部分见 `official-facts.md`。 | 两列 `running_owner_boot_id/session_id` 只有在先获得可信且持久的启动/登录会话化身来源后才可能充分；本轮未获得该唯一决定性事实，不能提交具体迁移为安全方案。现行旧 Job Open 失败保持拒新工，不放行恢复。 |

## D1 控制时序与故障出口

父在创建 SUP 前写入受限映射请求及绝对截止；`CreateProcessW(CREATE_SUSPENDED)` 成功后先取 PID、创建时间和主线程句柄，再检查剩余运行窗，才 Resume。子仅读固定映射、按固定模块进入单窗监督；本地业务 Job 的 claim→Job→worker Resume→整树确认→关门/结算仍由未变 `session.py` 协议管理。父等确切 SUP 退出，再读一次完整结果帧；半帧/校验错、子失败、父取消、启动部分失败或总期限到期均走精确句柄有限终止/等待，未知时字段保持 None。父在 Resume 前死亡时，本代码没有后台线程或迟到回调去 Resume；该结论限受信本地进程模型，未把任意外部同权限操纵视为已排除。父取得的非继承句柄与映射关闭、实际 Windows 父死后悬停生命周期须由后续 Job 运行和独立审查核实。

D1 最终替身失败的具体调用次序是：检查 1 映射前、检查 2 写请求后、检查 3 取得精确身份后、检查 4 Resume 后进入 wait。夹具给前三次 5 秒、第四次 0 秒，因此失败反映夹具场景排程不符其断言，不说明 Resume 前截止被验证。按“失败即停”未修夹具、未复检；实现也未签通过。`unit-stop-analysis.md` 保留原始定位。

## D3 最窄批准边界

候选仅需旧 G 满租后按原 W 全额折叠：若将来有可信启动/登录会话化身标识，可由受信 SUP 在 claim 的活动锁事务随 G 原子写入并读回；claim 响应丢失不得造 Job。持同一活动互斥时，同化身同会话须对确切 Job 得到零进程，或得到明确 `ERROR_FILE_NOT_FOUND` 且能排除迟到创建/错误命名空间，才能全额折叠；不同可信启动化身还须证明旧受控进程全灭；不同会话、旧行无字段、标识异常、权限/其他 Open 错误、提交不明均失败关闭。旧 SUP 迟到提交仍由原 status/G/C/CAS 裁决。拟由 running 行增加 `running_owner_boot_id`、`running_owner_session_id` 两列并改 claim/恢复接口，超出已批准 005 单列及本卡权限；**当前这两列仍不充分**，因官方支持的唯一命名空间化身事实未取得，不能请求仅按列名实施。未运行系统身份探针，也未把 `GetTickCount64` 或 session ID 复用风险猜成已解决。

## 验证、差异与后续门

- 改前所有相关文件（含实际已有 fixture.py）的字节副本/哈希见 `focused-repair-03/pre/`、`pre-hashes.txt`。最终 7 文件 AST、仓储/005 冻结哈希、逐文件旧新 SHA256 见 `static-final.log`、`final-hashes.txt`，增量正文见 `incremental.diff`。最终静态命令 `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/focused-repair-03/static-final.py`，退出 0、0.1614772 秒；AST 不等于运行通过。仓储 `929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20` 与 005 `26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb` 未漂移。
- 05 唯一诊断命令：`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry`，退出 0、1.5256558 秒。最终批次精确 ID/源码 hash 见 `manifest-final.txt`、`manifest-source-hashes.txt`；首命令 10 例退出 1、0.6060814 秒，原日志 `unit-final-01.log`；第二命令 `FixedEntryTests.test_12_fixed_command_and_injected_gateway_pass_through_gate` **not_run**。无第二次修正或复检。两项实际测试时长未超各自 60 秒，批次总窗未超 180 秒。
- D2/D5/D6 复用前轮静态/离线证据，未重新验证；D7 PG 隔离准备和 D8 未知结果仍仅为原条件结论，D1 变化不使它们自动升级。未改 repository、001—005、HTTP/gateway/PDF/runtime/锁/配置；未联网业务、安装、模型、应用、Docker、PG、真实 Job/事件/子进程。官方页面只读不算本机动态验证。
- 后续先由原 084 独立窗口增量复核本轮源码、D1 失败与 D3 证据边界；不得以本实现者自评代替审计。经编排另定额度后，最小 Job 仍含 01 正常早停、02 挂死、03 主退后代存、04 最后句柄/碰撞、05 同名碰撞，并补固定 SUP 的创建/父死亡/IPC 异常/期限受影响事实；任一归属或清理未知即停。PG 仍仅 review-02 定向 005 两例与 close 四例，真实连接 not_run；若 D3 获得审批，另列迁移/claim/恢复实际事务验证，不复用原 PG 证据。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：审计修复轮02（当前有效）

**状态：部分完成并停止本轮。不得进入 Job/PG 运行门或产品接线。** 本窗口实际标签 GPT-6，是原083实现者，不承担独立安全审计。084的D1管理启动上界、D3恢复证明仍未闭合；本轮最终命令路径修正后的定向复检3项中1项失败，原因未证实，修正/复检额度已用尽。原5个Job、旧04缺证及历史失败预算不清零；005未执行，PG/Job本轮启动数均为0；不宣告STEP008或M-1完成。

## D1—D8 增量结论

| 审计项 | 本轮变更与最终定位 | 状态和限制 |
| --- | --- | --- |
| D1 启动/IPC/期限 | launcher.py:46 将管理截止分出清理预留，所有已返回的Process对象使用同一绝对截止有限join/terminate/kill；start异常后按精确对象尝试收尾，poll/recv/close异常保留未知结果。纯替身09—11覆盖这些分支。 | **未闭合、运行阻断。** multiprocessing.Process.start返回前没有独立可终止的SUP句柄；子pipe.send和父recv仍可能卡在无独立取消的调用，有限故障模型下不能证明整体期限。不得以替身通过冒充生产启动/IPC上界。最小控制结构变更见下文。 |
| D2 固定入口/门 | command.py:15,28 固定项目venv解释器与唯一 app.worker.worker_main 模块，只接受 idle/one_call受限任务数据，不能由生产参数提供exe、-c或脚本；worker_main.py:27,46 的真实模块入口调用run_internal_task→run_controlled_worker→ClosingCallGate。one_call在无供应商接线的产品入口会明确失败；假gateway纯单元12证受控调用。 | **代码候选，Job与真实供应商未验。** venv转发器可能增加Job内进程，未来控制器按确切Job整树检查；不得把初始PID当最终解释器。 |
| D3 失败后恢复 | session.py未改；旧Job打不开时仍失败关闭，claim已提交但Job已消失可永久挂R。 | **提案待编排裁定。** 不能把Open失败或单纯主进程退出当整树空；下述持久证明/所有权扩展超出已批准005单列。 |
| D4 合成Job控制 | test_worker_session.py已移除可直接执行的旧WindowsJobTests；job_control.py:18,165、scenario_child.py、job_batch.py:20准备01/02/03/05统一Start→悬停身份→精确Job/进程句柄/创建时间核验→Arm→Resume；04的fixture.py:20加入Start门和单进程Job限额，04观察句柄在Exit前释放。单场景25/20秒，批入口55秒且失败停批。 | **仅准备，全部not_run。** 04最后句柄关闭后不能再查询该Job的ActiveProcesses，结果诚实写null，仅报告关闭前count=1及该单进程夹具的精确进程退出；此证据强度须独立审计。初批04旧count0仍不足。 |
| D5 PG02 | pg_close.py:122 将预留凭证按原合法UNKNOWN收敛，统计期望unknown=2；repository.py未改。 | **静态修复，PG not_run。** |
| D6 取消 | offline_unit.py:145 对claim响应未知的取消断言改为R/S=(None,None)，保留取消重抛与收尾断言。 | **纯单元初批通过，最终此路径源码未再改。** |
| D7 PG隔离 | pg_close.py:38每例随机schema，001—005在其内准备；仓储、行查询、并发、定向FK清理均使用同一search_path DSN；pg_close.py:140以实际来源锁持有/请求屏障控制close先提交和mark先提交的正反序。pg_migration.py:26失败保留schema，本轮不DROP；仅专用环境变量RETROLUME_TASK_083_DATABASE_URL，缺失skip。 | **可执行候选，PG not_run。** 锁与迁移实际事务效果、失败保留和清理仍待定向PG验证；新schema最终删除须另卡授权。 |
| D8 未知树结果 | launcher.py:46后所有外层超时、SUP丢失、start/recv失败均返回R/S/待折叠=None和cleanup_incomplete=True，即使SUP已退出亦不声称Job树空；有SUP结果但外层清理异常时标记不完整。 | **纯替身08—11通过；真实Job未证。** D1未闭合，不能进入运行。 |

## D1与D3的具体决定边界

D1的决定性缺口是CPython Process.start和Connection.recv的调用中没有可在调用尚未返回时由当前父方握持并取消的精确SUP对象。现有代码已在返回后的故障路径保守收尾，但无法证明启动前后整体deadline。最小后续实现是替换该父级Process/Pipe控制段：父方创建悬停SUP并在Resume前握精确进程/管理Job句柄，使用有界、可取消或可由终止SUP保证结束的结果协议，所有等待共享同一截止；CreateProcess自身内核不返回的情形仍在有限故障模型之外。此项需要先核对相应Windows API事实并经084独立复核，不能继续用新线程包装阻塞start。没有请求本轮额外运行或新增服务。

D3的最小恢复闭环**提案，不是本轮实现或已获批准**：新增按(activity UUID,G)唯一的持久window witness记录及持久owner epoch/CAS接口，记录命名空间/登录会话/boot身份、Job名、worker PID与创建时间、阶段CLAIMED→ASSIGNED→ARMED→TREE_EMPTY及可信主体。claim同事务写CLAIMED；单一持有活动互斥的所有者创建悬停Job/Assign，ASSIGNED提交或同代次读回确认后才可写ARMED并Resume；Job外可信持句柄者查询确切ActiveProcesses=0后写TREE_EMPTY，再允许close/settle。旧SUP晚到须受互斥和epoch CAS拒绝；提交响应丢失只读回同G/owner阶段，不盲目再领或Resume。整应用重启由独立于应用SUP的持句柄见证者按持久记录找回；见证者或证明丢失、命名空间/权限/boot不符时失败关闭，绝不凭Job不存在退款。仅用DB标记和易失Job无法原子地区分“从未创建”与“创建后在标记前崩溃”；该空隙归UNKNOWN，未ARMED者不得曾执行受控工作，仍需互斥/进程归属证明排除迟到创建。见证者自身死亡后的正常恢复仍需经官方Job销毁语义与同命名空间实证判定，否则保持保守预扣，不把新的看门责任递归假定为永不失败。

原批准边界只有005的dispatch_closed；上述持久表/接口及独立见证者均是**需编排取得具体批准的模型/职责扩展**。现合同的失败关闭代价是旧R可能长期不能折叠、无新窗，不能作为满足恢复目标的解法；不能擅自改折叠/结算或添加字段来掩盖。

## 最终文件、差异与验证账

所有改前已保存副本在 Ndocu/evidence/task-083/audit-fix-02/pre；逐文件旧/新SHA256、AST及冻结仓储/005匹配在 static-final.log，增量文本在 incremental.diff。例外：原有 fixture.py 的改前**字节副本遗漏**，其084基线hash为D511DCEA4E7E22F5E01D91B2845479FB8DB4CF5D33405C18E0E1C6ABA7F5636E，最终hash见静态日志；diff将其误列为全新文件，不能据此声称精确增量。其余重要最终hash：command b0e91c3a…、worker_main 5d065b5e…、launcher f650d2b8…、job_control 62396193…、pg_close 00b58fe7…、pg_migration 85d27efd…。repository 929320BA…、005 26B71A83…与084冻结值相同，001—004未改；没有改正式docu、公共库、gateway主体、HTTP/runtime、PDF、配置或Git。

| 验证 | 真实命令/证据 | 结果 |
| --- | --- | --- |
| 初始纯单元 | backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/run_audit_fix_02.py；unit-initial.log、unit-initial-meta.txt | exit 0，14/14，约0.89秒；属于修正解释器路径**之前**快照。 |
| 唯一修正复检 | backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/run_audit_fix_02_recheck.py；unit-recheck.log、unit-recheck-meta.txt | exit 1，3项中2过；test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry返回elapsed_violation_full_reservation而断言期望settled。原因未证实，最终快照**不能称通过**。约0.62秒。 |
| 最终静态 | backend/.venv/Scripts/python.exe -B - 执行一次限定AST/差异/hash脚本；static-final.log、incremental.diff | exit 0，13个改动/新增Python文件AST通过，冻结仓储/005匹配；局部无明文凭证或真实外发URL模式。它不验证行为、OS或PG。 |
| Job/PG/迁移 | 本轮未执行 | not_run；Job启动数0，PG连接数0，005未执行。 |

复检失败后没有再改源码或追加测试。初批14项只有不受最终命令argv改动的条目可作局部证据；05最终失败，不将旧PASS沿用为最终PASS。历史Job 5例及旧04缺证原样保留。没有真实出站或旧进程调查/操作。任务预算未按新脚本或中断重置。

后续最小门：先由原084独立增强窗口只读复核D1/D2/D4/D8最终控制链、D3权限提案和本次复检失败；不对未改仓储全量重审。D1/D3和05单元失败未关闭前不进入Job运行。若编排修复并另给预算，Job最小清单为01正常退款、02挂死全额预扣、03主退后代、04最后句柄/旧失败、05因统一控制器和身份入口变化需核验同名碰撞；每例按job_batch的精确对象与停止条件复审后才可执行，不承诺按当前脚本直接放行。PG定向ID为 PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column、test_pg_migration_02_nonempty_table_rolls_back_whole_005、PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window、test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes、test_pg03_close_commits_before_concurrent_admit_and_mark、test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges；专用DSN缺失skip，另卡授权运行/清理。文档建议由编排把083保持“部分/运行冻结”，登记D1/D3与本轮复检失败；本实现者不签安全通过。

---

## 历史：离线补足轮01原文


# TASK-083 / R-077 / STEP008 执行结果：离线补足轮01（当前有效）

**结论：内部监督候选实现与受控验证准备已补足；真实 Job、005/PG、产品供应商路径及独立安全审计均未通过或未运行，不可接线放行。** 本窗口实际标签 GPT-6，仍是 083 实现者而非独立审计。原初批 5 个 Job、一次修正、第04场景超时与归属缺证及旧原始日志不清零；下方保留初批结果原文。没有宣告 M-1 或 STEP008 完成。

## A—E 完成映射与接口

| 项 | 本轮可审查实现 | 限制 |
| --- | --- | --- |
| A 命令与 SUP 边界 | 新 `WorkerCommand` 只接受本地绝对可执行文件、不可变有界参数及工作目录；SUP 不再调用 `command_for_lease` 任意同步函数。新 `run_supervised_window` 是阻塞的内部入口，拒绝在运行中的应用事件循环调用；Windows `multiprocessing.spawn` 专用子进程持 Job/活动所有权，父启动器在创建前固定总管理 deadline，凭精确 `Process` 对象有限 join→terminate→kill，未知结果失败关闭。子进程使用现有 `psycopg_compatible_loop_factory`。默认 W90、启动5、请求10、停止预留5、管理额外30秒，关系由 `SessionConfig` 检查；partial W 不开工。 | 真实进程/PG组合 not_run；父启动器自身死亡时由旧树未知恢复规则失败关闭，未宣称任意系统挂死下硬实时。 |
| B 收尾与账本语义 | `SingleWindowSupervisor.run_once` 所有路径在 Job 终止/查询/close、互斥释放之后构造结果；首个异常类型保留，后续清理异常逐项记录。取消重抛并附 `session_outcome`。结果分 `settled_seconds`（本窗确认进入 S）、`reserved_seconds`（确认仍占 R）与 `pending_fold_seconds`（待原规则折叠）；claim 或 settle 提交响应不明时字段为 `None`，不再谎称 0 或已收费。只有 Job 树 0、主进程成功、C≥1且 C≤W 后才关 DB 门并按原 G/W/C 有限重试结算。 | claim 未知语义、子进程兼容循环属于纯单元之后的定向源码补正，最终动态验证 **not_run**；整树事实仍须真实 Job 验证。 |
| C 内部发送门 | `run_controlled_worker` 将唯一 `ClosingCallGate` 交给注入 work；门先原子 closed 再等活跃调用归零，令牌包住假 gateway 的 admit→mark→send→record，全链纯单元观察了已 mark 未 send 时新令牌被拒、在途收尾后退出。未来 Job01 的 `controlled_fast` 合成 worker 入口也调用真实 `run_controlled_worker`，不接供应商。 | `WorkerCommand` 是内部命令数据，不证明未来产品 worker 必然调用受控入口；产品接线需独立审查该约束，未授权修改 gateway 主体。 |
| D 可控 Job 准备 | 第04场景改成 base Python 稳定进程句柄，并按本机 Python 3.12 Windows spawn 源码设置 `__PYVENV_LAUNCHER__` 保留 venv 依赖。父测试在 Resume 前有20秒独立截止、UUID/G/runTag/Job名/PID/进程创建时间、精确 Job/进程句柄及 ActiveProcesses>0；两个唯一命名事件各限5秒握手，父控制器有限管道读/等待，最终只用自身句柄收尾并输出身份与停止事实。Job01/02/03/05 也准备身份日志。 | 这些新场景 **not_run**；旧04进程列表 count0 仍不能补成旧Job整树正证据。01 合成 venv 转发器及子进程在同Job内，<=原4进程上限；04直接 base 解释器。 |
| E PG 可执行准备 | 新 `pg_close.py` 含当前代次 close/首次 settle 前置/最近旧 G/C 不改新窗、关闭后 admit/mark 拒绝而 RECEIVED/UNKNOWN/NOT_SENT 可收敛、真实来源锁→活动锁并发次序及 cancel 残留；新 `pg_migration.py` 在随机自建 schema 上准备 001—005 空表成功/非空事务回滚。仓储用例仅以本例 UUID 和 FK 顺序清理；仅 `RETROLUME_TASK_083_DATABASE_URL`，缺失明确 skip，无应用/用户 DSN 回退。 | 005 未执行，全部 PG **not_run**；旧001—004未改。精确测试ID及既有受影响ID见本轮 `manifest.md`。 |

内部接口清单：`WorkerCommand`（纯数据）、`run_supervised_window`（产品未来唯一应接的阻塞 launcher）、`SingleWindowSupervisor.run_once`（仅子进程/替身调用）、`SessionConfig`、`SessionOutcome`、`run_controlled_worker`、`ClosingCallGate`、`NamedJob`/`ActivityMutex`。产品 HTTP/真实供应商入口仍未接线。SUP 时序是活动本地/Win32排他→旧Job确切身份与 ActiveProcesses 0→t0→claim 明确返回→唯一 Job/悬停 worker→固定 stop/deadline→Resume→整树0→关闭 Job 句柄→DB close→settle→释放所有权；kill/超窗/未知不退款且不开新工。默认 q≤50ms 轮询、g=5秒；调度和内核终止误差不作硬实时保证。`repository.py`、005 hash 未变。

## 差异、hash 与验证

改前版本与 SHA256 在 `Ndocu/evidence/task-083/offline-repair-01/pre/`、`pre-hashes.txt`；最终全部逐文件 SHA256 在同目录 `final-hashes.txt`。关键旧→新：`session.py` `8E99B12B...→D317DB76...`，`windows_job.py` `3D0B5DAB...→D05CA259...`，`gate.py` `2186C7C8...→7E7588A5...`，`test_worker_session.py` `010DD38A...→0AC732AC...`；新增 `command.py`、`launcher.py`、`job_control.py`、`offline_unit.py`、`run_offline.py`、`pg_close.py`、`pg_migration.py`。冻结 repository `929320BAF55D625E897324AA76EBE543BDA86E73A4BF1C4766C7E552721C5B20`、005 `26B71A836355FA9620401F6BBB76E9A42668A1CE52077AA91ECB2F61EBEB50EB` 均保持。所有本轮新增/改动都在原083允许源码/测试或本轮证据与结果路径；不改正式 docu/公共库/旧证据/HTTP/gateway主体/PDF/依赖锁/Git，不安装/外发。

| 验证 | 真实命令与退出码 | 事实 |
| --- | --- | --- |
| 静态一次 | 项目根 `backend\.venv\Scripts\python.exe -B Ndocu\evidence\task-083\offline-repair-01\static_check.py`，exit 0；限定 `git diff --check -- backend/app/worker/__init__.py backend/app/worker/gate.py backend/app/worker/session.py backend/app/worker/windows_job.py backend/tests/test_worker_session.py backend/tests/fixtures/task083/fixture.py`，exit 0 | `static.log`；核对当时 AST、004/005/repository hash、显式测试选择。静态后又有定向源码/夹具修正，**不能把旧静态日志称为最终版本的 AST 通过**。 |
| 纯单元初批 | backend 根 `.venv\Scripts\python.exe -B tests\fixtures\task083\run_offline.py`，exit 1 | `unit-initial.log`；10项中9过，唯一失败是即刻返回 FakeJob 使合成 C=0，生产 SUP 按合同拒绝部分退款。 |
| 唯一修正复检 | backend 根 `.venv\Scripts\python.exe -B tests\fixtures\task083\offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry`，exit 0 | `unit-recheck.log`；只修该替身正耗时与 Job close→DB close→settle 的事件观察，1/1过。没有第二批 Job、没有 PG/OS 子进程。 |

真实纯单元命令耗时分别约0.35s、0.05s，单命令均小于60s。首次静态检查约11:23、单元初批约13:43，**整段墙钟跨越180秒上限**：中间 `exec_command` 自动审批因用量限制未完成审核，明确拒绝动作是纯单元命令，理由是审批用量限制而非认定不安全；该次命令未执行、无日志或遗留进程。用户随后明确要求继续，断点核对后才执行；未借此重置083 Job预算。上述超时偏差保留。离线补足的修正次数为一次单元失败修正及仅失败项复检；其后发现 claim 响应丢失不能报 R=0、子进程事件循环兼容性和合成入口问题，已作定向源码补正，**没有追加测试额度或声称这些补正动态通过**。

## 后续审查与运行门

先由新窗口独立增强**只读审查最终源码**与 `job-initial.log`、本轮原始单元日志及 `final-hashes.txt`，重点核对 DB 门与本地发送门、退款/取消/未知交错、SUP/Job 精确归属和最后句柄、重启预算不重置、late claim/settle 响应以及本轮后补代码。实现者不签安全通过。审查后由编排另定真实 Job 预算；最小受影响场景为原失败01正常早停退款、原失败04 SUP死亡/最后句柄，以及 session 终止/清理改变牵动的02挂死全额预扣、Job身份与创建时间/主退子存牵动的03。原05同名碰撞旧局部行为通过但身份记录不足，由独立审查决定是否占新预算复检，不能把旧PASS说成身份验收。专用PG按本轮 manifest 的两个 migration 与四个仓储确切ID定向运行，随后只挑受影响旧 time-budget 01/02/06/08、ledger 01/05/06/07、recovery 01/03/05；均须编排另定预算，当前 not_run。

文档建议：编排在正式执行状态记录“083离线候选已补、Job/PG/独立审计仍阻塞产品接线”，登记静态后代码修正未复核和离线整段墙钟偏差；本执行者不改正式 docu。无需用户逐项确认工程参数。当前无新增持久字段、公共接口或服务批准请求。

---

## 历史：083 初批结果（原文保留）

# TASK-083 / R-077 / STEP008 执行结果

**状态：部分完成，停止本卡运行并交回编排。** 本窗口实际模型标签为 GPT-6；沿 TASK-082 独立诊断窗口转为本卡实现者，082 历史诊断独立性不变，本窗口不担任 083 后续独立安全审计。未宣告 M-1、STEP008 或项目完成。根目录 `D:\shspic\project_NO3_RetroLume-agent`。基线 `45951501d2741630a229762d6b2d3f4b34d7f702`；既有正式文档和其他未提交差异原样保护。

## 输入与边界

按本卡读取根 `AGENTS.md`、公共 `docu/AGENTS.MD`（本窗口已读未变，复用）、`TASK-083.md`、`TASK-082-work-decision.md` 全部批准条款、`TASK-082-result.md`、需求 NFR002/003、SEC002、第13节、架构 FLOW005/DATA007，必要的 activities/repository、001—004、gateway/transport、PDF Windows Job 与直接相关测试。没有加载全部历史执行聊天或重做 077—079 PG。082 的官方依据仅用于本卡既定设计；本卡未新增联网取证。

用户 2026-09-24 批准的是内部单窗监督切片与合成验证。005 **未执行**；未运行 PG、Docker、模型、应用服务或真实外发。未改 gateway/transport 主体、PDF 监督器、HTTP/runtime/前端、001—004、锁文件、正式 docu/公共库或旧证据；未 Git 提交/推送/reset/clean。

## 已写入的增量与职责

| 路径 | 增量与职责 | 状态 |
| --- | --- | --- |
| `backend/migrations/005_activities_dispatch_closed.sql` | 事务内 ACCESS EXCLUSIVE 锁 activities，非空抛错回滚，仅增加 `dispatch_closed BOOLEAN NOT NULL DEFAULT FALSE`。 | 静态核对，not_run |
| `backend/app/activities/repository.py`、`__init__.py` | claim 同事务只给新代次开门；折叠耗尽/cancel/settle 关门；`begin_window_close` 同来源→活动锁序、当前 G/执行者匹配、仅 false→true 幂等；admit/mark 检查门；record 仍允许关门后合法收敛；settle 首次需已关门，最近 G/C 幂等先行；`inspect_window` 供恢复只读核对。 | 离线替身局部通过，PG not_run |
| `backend/app/worker/gate.py`、`worker_main.py` | 不可重开的本地共享调用令牌，覆盖包装器 `gateway.call` 的全程；关闭先设 closed 再等活跃调用退出。只向注入工作函数提供包装器。 | 离线 2 项通过；未接真实 gateway |
| `backend/app/worker/windows_job.py` | 活动命名互斥、UUID+G 精确命名 Job，默认当前用户 DACL、非继承句柄、无 breakaway，4 进程/256 MiB 限额、KILL_ON_JOB_CLOSE；悬停创建→Assign→Resume；查询 BasicAccounting.ActiveProcesses，有限终止等待。 | 合成初批部分通过；归属测试未闭合 |
| `backend/app/worker/session.py`、`__init__.py` | 活动互斥覆盖恢复核对、claim、Job 创建及交接；t0 在 claim 前，响应丢失不 spawn；partial W 拒绝启动；整树 0 且主进程成功才取 t1/关 DB 门/按真实 C 结算；失败保留全额预扣并失败关闭。 | 内部骨架，尚不能签完整监督协议 |
| `backend/tests/test_activity_time_budget.py` | 原 PG 合成 helper 在当前合法代次 settle 前调用 close；保留旧业务断言；未运行 PG。 | not_run |
| `backend/tests/test_activity_dispatch_close.py`、`test_worker_session.py`、`fixtures/task083/fixture.py` | 限定离线替身与 Windows 合成场景；初批发现夹具缺陷后作唯一一次精确修正，未再次运行 Job。 | 7 离线通过、Job 3/5 初批通过 |

原件 hash 及副本：`Ndocu/evidence/task-083/pre/`。冻结 repository `045A3CF8B1C81D7A1336C3BD2E90E891E4E53934027C9FEA9727FAFDE7202534`、004 `8F04F57C743C260F5081E0C6F232860301B30C7B03FEF69498D7C0704C0A97CC` 均与预期相同。最终 repository `929320BAF55D625E897324AA76EBE543BDA86E73A4BF1C4766C7E552721C5B20`，activities `__init__` `0C5EA723C270EFAE0BAC9F5AA9517628D1EBC88844A3C4E41829188B52F2BE78`，time-budget test `CB5A51960B830825350F5E30F9430DE6B04C939489D8FE8CAC0C76172C2E1245`，005 `26B71A836355FA9620401F6BBB76E9A42668A1CE52077AA91ECB2F61EBEB50EB`。全部新 Python 文件最终 hash 见 `Ndocu/evidence/task-083/static-final.log`；前副本 hash 在同文件。已跟踪源码增量 `+92/-1` 行；新增文件不在 Git numstat 中，审计须直接查看。

## 合同与当前实现限制

默认工程参数 W=90s、启动上限 s=5s、请求超时=10s、停止预留 g=5s、Job 查询步长 q≤0.05s；要求 `W > s + request_timeout + g`，实际 `W_eff` 不满足也拒绝开工，截止固定为 t0+W_eff，终止开始不晚于 t0+W_eff-g。SUP 的 claim、旧树核对、DB 及清理均有有限代码等待；不声称 Windows 硬实时。C0 只保留仓储原合同，真实 SUP 仅在 `1≤ceil(t1-t0)≤W_eff` 路径请求退款；越界/失败不伪造 C0 或钳制 C，残留由原过期认领规则保守折叠，不擅自取消活动。提交响应丢失只用同 G/W/C 有限重试；整机重启不比较旧 t0，旧 Job 打不开或身份未知就拒绝新 claim。

**仍有实现级缺口**：`command_for_lease` 是同步注入回调，代码没有对其执行时长的独立强制上限；当前 SUP 用阻塞 Win32 轮询，必须专用线程/进程运行，但外部启动器的有限管理生命周期未形成可验证产品接口。内部 worker 门仅由注入回调路径使用，尚未与真实供应商 gateway 连接，不能证明未来业务代码不会持原始 gateway 绕开门。真实 Job 身份/恢复与 SUP 死亡场景未通过本批验证。因此这不是可供产品接线的完整已验收监督协议。

## 有限验证与真实预算账

首次运行前清单：`Ndocu/evidence/task-083/manifest.md`。静态命令（项目根）`backend\.venv\Scripts\python.exe -B Ndocu\evidence\task-083\static_check.py`：初次及修正后各 exit 0；最终原始输出 `static-final.log`。本卡限定 `git diff --check -- backend/app/activities/repository.py backend/app/activities/__init__.py backend/tests/test_activity_time_budget.py` exit 0。全仓 `git diff --check` exit 1，只报本卡开始前已存在的正式 docu 尾随空白，不触碰这些文件。静态检查是 AST、hash 与明显真实外发标记检查，不是动态无外发证明。

| 批次 | 真实命令（工作目录 backend） | exit | 原始事实 |
| --- | --- | ---: | --- |
| 离线仓储替身 | `.venv\Scripts\python.exe -B tests\test_activity_dispatch_close.py CloseGateRepositoryTests` | 0 | 3/3 通过，`unit-close.log`；仅调用序/内存替身，不证明 PG 锁或约束。 |
| 离线 worker | `.venv\Scripts\python.exe -B tests\test_worker_session.py GateTests ProtocolUnitTests` | 0 | 4/4 通过，`unit-worker.log`；claim 响应丢失、partial W、旧 Job 未知均不 spawn。 |
| 初始 Job 批次 | `.venv\Scripts\python.exe -B tests\test_worker_session.py WindowsJobTests` | 1 | 5 个场景，3 通过、2 失败，`job-initial.log`。日志 10:32:19—10:34:40，本批总墙钟约141.3秒；第4场景和整条命令突破单场景30秒/命令60秒上限。没有第二 Job 批次，修正后 Job 结果 **not_run**。 |

Job 初批逐项：01 正常早停在 Job 查询 0 后未结算，合成 FakeLedger 错把真实 0.313 秒当作必须≥1，SUP 返回 `failed_closed`；日志保留活动 `d0876c04-4b37-4247-bbd4-60c5d181acdd`、G1、精确 Job 名、PID 35116、`ActiveProcesses=0`。02 挂死路径在约5秒停止并观测 0，全窗收费，未调用 settle。03 主进程先退时 ActiveProcesses 仍>0，随后查询为 0。04 SUP 死亡路径未取得稳定 worker 句柄：虚拟环境解释器为转发器，读取到的 PID 随转发退出，`OpenProcess` 返回空；测试控制器/管道等待突破期限，不能主张“最后句柄关闭后整树退出”已验证。05 同名 Job 创建拒绝，原 Job 查询 0。第02/03/05 的精确 UUID/PID 未写入原始日志，因此只作为局部行为证据，不作完整归属审计证据。

初批曾以精确命令行与父链定位测试进程 13512/32900、夹具控制者 7300/35500，活动 UUID `11dd3767-7f74-41eb-baa4-aba83a852dfc`；对仍存活且归属已核对的 PID 35500 作有限应急停止，随后批次进程收束。`cleanup-process-check.txt` 的只读筛选为本卡 Python 夹具/测试控制者 count=0；这**不是**该 Job 的 ActiveProcesses=0 正证据，04 仍按归属/整树证据不足记录。未按进程名/端口批量杀进程，没有继续启动 Job。启动 Job 场景数为 5，少于8；初批总窗少于10分钟，但场景/命令子上限违反，作为执行偏差保留。

一次范围内修正由 `edit_after_initial.py` 精确修改 FakeLedger 的 `ceil(C)` 断言，并使合成场景使用 `sys._base_executable` 绕开已确认的虚拟环境转发器，未扩大进程数。修正后仅 AST/hash 通过；因 04 的归属正证据和时间边界失守，按本卡停止规则**未启动复检**，不可称修复已通过。无第二次修正或第二 Job 批次。测试输出中的 unittest `FAIL` 原样保留，不以文字 PASS 代替。

## 后续矩阵与交接

| 层级 | 下一步具体范围 | 当前证据 |
| --- | --- | --- |
| 实现补足 | 为生成 worker 命令及 SUP/启动器建立有限上限；让测试控制者在 Resume 前取得稳定精确进程/Job 身份和截止，并为每场景记录 runTag、UUID/G/Job/PID/查询结果；修正 04 的管道等待期限；只在获新卡预算后重测失败/受影响场景。 | 缺口未闭合；本卡不再运行。 |
| 独立增强审计（新窗口） | 审查关闭门与 admit/mark/send/退款交错、DB 锁序与旧 G/C 幂等、Job 归属/跨进程重启/未知退出、t0/W/失败预算不重置；审计最终源码与本卡原始失败日志。 | 本实现者不签安全通过。 |
| 专用真实 PG 与组合验证（另卡） | `Ndocu/evidence/task-083/pg-plan.md` 的 PG-01—06，专用 DSN 缺失 skip；仅选择真正受影响的既有 ledger/recovery/time-budget 用例。 | **not_run**；079 旧证据不覆盖 005/新门。 |
| 产品外接 | 在审计与专用 PG 后明确 gateway 注入和 worker 生命周期；若需改 gateway 主体或持久字段，先提交具体差异再审批。 | 本卡未接线。 |

原始导航：`Ndocu/evidence/task-083/manifest.md`、`static-final.log`、`unit-close.log`、`unit-worker.log`、`job-initial.log`、`cleanup-process-check.txt`、`pg-plan.md`、`pre/`。源码/测试原件均在上述允许路径；旧文档差异保持。建议编排将 083 标记“部分/停止”，围绕确定缺口派下一张有限修正与验证卡，再交独立增强审计；不要把本结果登记为最终验收。
补充实现风险：`run_once` 多个提前返回在 `finally` 清理前构造 `SessionOutcome`，若清理随后失败，返回值的 `cleanup_incomplete` 可能失真；下一卡须先修正并以故障注入验证，不能依赖该字段判定安全收尾。
