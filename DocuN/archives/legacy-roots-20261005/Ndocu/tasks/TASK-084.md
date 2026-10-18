# 已关闭：编排最终验收通过（2026-09-27）
本卡授权成果已交付并通过review09及编排验收，不再执行下方历史命令。运行许可结束，未用预算不得自行续跑。裁定见Ndocu/results/TASK-083-084-final-acceptance.md；STEP008/M-1/one_call不据此完成，新成果另建关联任务。

---
以下保留原完整合同供追溯。
# TASK-084 / R-078 — review-09 D3完整成果最终独立验收
接收原084独立增强审计窗口，沿review08上下文，未参与083实现或运行；原窗不可用才新独立增强窗口接续。实际型号如实登记，不按名称追溯重审。TASK084/R078，STEP008局部，父083，关联082、NFR002/003、SEC002、FLOW005、DATA007。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.46、执行状态v1.66；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及全部现有差异保护。本卡待转交。

## 唯一目标
对083完整收尾14的实际三文件增量和八场景真实证据完成最后一次独立验收，明确批准的单机D3切片是否已达到实现/验证交付条件。review08已关闭的问题与未变产品不全量重审；不运行任何测试，不为日志美观再要求复跑。
这是成果终审，不是再做一轮准备或泛化安全研究。仅确定缺陷、关键证据缺失或实际契约违反可阻断；条件风险/有限覆盖/未触发异常分支按已有验收范围分层记录，不自动扩成新测试或新平台。不能因用户催进度降低标准，也不能无限追加未批准的覆盖目标。
083已结束运行，被审源码/证据冻结；资源只有停止日志，本卡不实时查询Docker。未用预算不是重启许可。

## 规则与独立输入顺序
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；
公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，同窗未变已读复用。
1. 当前Ndocu/tasks/TASK-083.md完整14合同和已批准TASK-083-D3-work-decision.md必要边界；自己的review08结论/方法级证据分级。
2. Ndocu/evidence/task-083/d3-completion-14/pre/、incremental.diff、review08-current-hashes.json及实际runner/controller/fixture，先独立判断实际差异是否守住旧控制合同；仅必要直接依赖。审新增离线入口offline_checks.py/bounded_check.py和resource_preflight.py的实际作用；finalize_evidence.py只在确认整理是否改变原始证据时读，不执行。
3. 真实目录Ndocu/evidence/task-083/d3-completion-14/continuation-20260927-095506-73c4c3e3/：
runner/controller/contracts as-run及hash，attempt-01/as-run.py及sources/真实依赖快照；state.json、attempt-01/meta.json、stdout.log/stderr.log、resource-commands.jsonl。
4. 根证据目录final-hashes.txt、offline-01.json/stdout/stderr、preflight-resource-commands.jsonl/preflight.json、budget-final.json、runner-process.json、scenario-index.json、inflight前后快照。先原始证据后索引；最后读TASK-083-result.md置顶14作为待核声明，披露顺序。
不读实现聊天/模型推理；不读容器Env、完整DSN、secret或用户配置，stdin省略不可被要求补齐口令。不得把自报all_pass替代真实断言/原始控制事实。

## 当前快照与复用
本轮实际既有文件仅三项变化：
Ndocu/evidence/task-083/d3-repair-11/runner.py = 7137664E7CFF010089C58600DE6F9DAE96F82A274CAD8968BD6600F70BE2C436
Ndocu/evidence/task-083/d3-repair-11/controlled_child.py = 0494AF00387BA5F1C45062B9CD892E5AF22822E95D72B619134F6BD694C8A664
backend/tests/fixtures/task083/d3_pg_windows.py = 19B6F78CACC88C299A94B78B7E3F2C569621F020D337178163680269100CA1F8
未变关键：
repository.py = BCA8283316F62216F5BA94959F5C36F8C3395301AEB9DC7F21A9B376F92E29A3
session.py = EB514B5F76B0DC8B43ED8DFE116D2DC7BE5A181011E1516FAAA4D8005461D71C
contracts.py = A344AC5FBDF7C838C08C18FC1816D5D8E823C3FF67B1A98976CF11129257CBCD
006 = F791F22DCFCCF204F6FDA369470978452B3B23CCA0FC40D2057BD08EA47F6428
其他未变项及辅助新文件查final-hashes和review08-current-hashes；独立核最终/as-run/pre链，不把本轮pre/post相等当历史未变证明。未知漂移停止相关结论、其他只读审查可继续。Job07/PG08/09、review08按方法与依赖复用，不再重述全部理论。

## 一次审查五块
A. 三文件实际增量
inspect index缺键访问仍完整14字段、configured_mounts非空拒绝、类型/字段/端口集合严格且不读Env；就绪只对pg_isready临时不可用有界等待，确定认证失败不绕过；一次本地角色自改密和loopback核验。
控制器新增真实身份/归属/Resume/收尾事件是否观察实际调用顺序、不弱化句柄或最后Job语义；异常管道/EOF/exit处理是否保留原错与unknown；场景排空后windows_started判定是否准确。
复验聚合修复是否不把首批非零/缺complete倒写PASS、复用指纹是否覆盖依赖、是否漏未运行后继；本轮未走复验通道，结论只能静态/离线，不强制为未触发分支新建一轮真实失败实验。
所有改动是否在14普通完整修复授权内，产品零改/迁移未改及边界不扩核实。若只是证据记录修正不虚构生产变化。

B. 八场景真实链（按原ID逐项）
migration_empty/old/rollback：断言真正触及006新增列/域、旧NULL和失败事务无部分DDL，区分合成故障位置，不夸所有迁移故障。
ledger_active_lease_rejected/new_g/exhausted：同SID0与上界、有效租约拒绝、全额旧R入S、新G/SID/关闭门、None提交事实。
ledger_lock_barrier：真实pg_stat_activity锁等待先于deadline/lease边界，释放后claim拒绝/inspect可恢复，与实际锁后UTC代码因果对应；不把单纯sleep当屏障正证。
windows_recovery：确切旧Job G1/SID/worker PID+创建时间、树0/close/Open2→生产固定launcher/SUP自读SID→G2真实claim和结算→PG最终G3/S7/R0/SID NULL/last_settled G2,C1；观察句柄不保活业务Job。原始payload/调用点/执行hash一致，不靠硬编码结果或mock。
逐个记录确实证明和未证明。旧G/C此次实际仅三种不匹配拒绝，不是ALREADY_SETTLED重测；最近已结算重试按旧未变方法证据范围复用，不因未重测自动新门。八场景完整成功不扩大到跨机/注销/重启/全部响应丢失或退款异常。

C. 进程与资源证据
外层PID4936/创建时间134349765079104187，真实suspended_identity→assigned_outer_job(active=1)→resumed→control_handles_closed(tree_zero_confirmed=true)，实际exit0/管道EOF/树0/句柄完成是否支持。
旧worker17752、SUP32896、新worker37356均按原始创建时间和Job名对应，不能只凭裸PID认归属。互斥释放顺序沿未变源码/旧单元事件，不伪造本轮动态事件；Assign前猝死悬停孤儿限制不由成功链消除。
容器完整CID85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7，各字段/固定卷/127.0.0.1:55439逐项核；仅start1/轮换1/stop1、无新容器、无旧secret读取或提权绕过。末次stop exit0/Running=false及身份确认支持记录时点停止；不要要求本卡重启或实时inspect才能接受已有收尾。

D. 版本、期限与纪律
当批实际执行字节与最终hash/真实sources链成立，三批旧离线分级保留，本轮10项新离线不混算历史覆盖。
真实唯一批的8唯一start/result、唯一complete、parts完整、exit与cleanup共同成立；报告与raw JSON的真实字段名核准，不将投影出来的null误认为原字段false/缺失证据。
资源预检5.609秒+外层runner10.133438秒=15.742438秒；内部9.390秒已包含不重复计；原保守900+240继续为占账而非精确实耗，总1155.742438/1800，8场景及命令各自期限未超；原真实总2/3批/PG命令、Windows1/12、容器2，本轮无第二批。若发现实际偏差单列影响，不因非实质文案误差废全部实证。
在途核查与公共规则/文档只读、Git未提交等按已有证据限定；不要求再全仓扫描或重跑核验。文件整理GBK失败说明是否仅整理过程、不改真实证据，有限核查即可。

E. 最终判定
分别给“实际增量代码”“八场景动态”“资源/执行控制”“批准的D3切片整体”结论；如全部条件满足，明确D3该批准切片可由编排验收关闭，并列适用单机/单会话与未触发异常边界，不把未承诺的全部场景当新阻断。
若关键项确有确定缺陷/证据不足，给最短触发/定位/影响/最小完整补项；其他已证部分保留，不能泛泛要求再一轮审计/全测。不是预设必须通过，也不为完成卡制造非必要新门。

## 权限与交付
只写Ndocu/evidence/task-084/review-09/与Ndocu/results/TASK-084-result.md置顶review09，全部历史保留。其余产品/夹具/runner/正式docu/公共库/记忆/Git/旧证据只读；不执行实现者脚本、不import/AST/compile/测试、Docker/PG/Job/进程探针，不联网安装或模型调用。动态0，有限只读hash/diff允许。
完成本范围一次即停。独立结论先于自评形成留证，已知接触自评则披露，不伪称无接触。输出事实定位、问题分级、有效证据/限制、D3可验收与否、最少必要后续和文档建议。你提供独立验收意见，不替编排改正式状态；不宣布M-1/STEP008/one_call或整个项目完成。
确认结果可读后只回复一句最终结论与绝对路径，由用户带回编排。