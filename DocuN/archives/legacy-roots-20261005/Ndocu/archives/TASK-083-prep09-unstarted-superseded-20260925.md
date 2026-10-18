# TASK-083 / R-077 — 新D1固定launcher受控验证准备09
接收原083增强实现窗口，沿原任务，不担任独立审计。STEP008，父082，关联084/R078、NFR002/003、SEC002、FLOW005/DATA007。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.39、执行状态v1.54；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及全部差异保护。用户082内部实现/合成验证授权有效，本卡仅补已明确未覆盖的固定launcher受控场景与审查包，不扩生产功能或持久模型。

## 完整成果
交付可以直接独立审查的最小真实入口验证夹具、精确运行清单及资源/收尾方案，不只交泛泛设计，不实际启动OS/PG。Job07五例和PG08六例证据按既有范围复用，不重测。新入口必须实际调用生产run_supervised_window→固定SUP→worker链，不能再以run_once/直接Job冒充覆盖。
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，已读未变复用。最小输入：082-work-decision批准合同；084结果review-03 D1安全边界/review-05分项门；launcher.py/supervisor_ipc.py/supervisor_main.py/session.py/command.py/worker_main.py/windows_job.py的必要路径；现有job_control/fixture协议及PG08隔离/收尾经验。旧卡归档Ndocu/archives/TASK-083-before-launcher-prep09-20260925.md。
运行链当前冻结沿job-run-07/pre-run-check.json、post-run-check.json及pg-run-08/post-run-hash-check.txt；只读核对将用的直接依赖，不全仓重采。不读取或输出含合成口令的配置/旧runner环境。首次写目标先保存已有字节/hash，新文件如实NEW；未知漂移停影响项。

## 最小可审查夹具与场景
允许新增backend/tests/fixtures/task083/launcher_control.py、launcher_scenario.py（必要合成配套限同目录新文件），以及本卡证据目录中的运行计划/runner准备。原则是利用既有机制、窄增量，而不是新通用测试平台。生产backend/app及现有Job/PG测试文件全部只读；若确需生产观测钩子，先给具体最小diff和必要性，不能自行实施。
完整覆盖D1新行为的最少场景，合理合并，不机械每条另建一批：
A. 干净新活动、固定入口正常启动与真实账本关闭/结算：专用合成PG，固定允许的idle任务即可，无供应商/模型/外网；记录精确父/SUP/worker身份与实际创建时间、Job归属、同deadline传递、树退出及DB S/R/G/closed。不能用FakeLedger声称真实固定子入口已跑通。
B. 新父launcher管理超时/主动终止或子端无有效结果：验证有界收尾、无可信结果字段保持None、cleanup_incomplete以及批次停机纪律；精确SUP退出不等于Job树空/退款证明。结果观察与收尾事实分开，不迁就预期把未知改clean。
C. 父在Resume前死亡与Resume后死亡/映射交接窗口：列出如何确定控制点、独立持有精确对象身份、阻止迟到Resume及终止本次悬停遗留；不能凭随机sleep碰撞当确定注入。父死后子继续其自身deadline与父主动杀SUP是不同情况，说明哪些可合并覆盖，哪些仍待验证。资源遗留和执行资格风险区分，不把不运行的悬停对象记成已清理。
D. 映射碰撞/半帧/错误结果：已有纯单元可复用的解析分支不全部重跑，只有真实OS映射生命周期/固定入口交接确实新增的风险才列实际场景；不向生产入口增加任意exe/-c开关。
每个场景明确实际调用入口、故障注入机制、前置身份/握句柄的时点、成功/保守未知判定、确切清理与记录字段。为上次03/05落盘缺项补本新夹具的结构化身份字段，而不重跑旧场景追补。独立外层必须在被测对象失控前有可用身份/期限，不以失控后的宽泛进程搜索兜底；不得为观察最后句柄而无意保持Job存活。若当前无钩子无法确定C场景，交单一决定性缺口与最小变更提案，不写假可运行方案、不叠第三常驻服务。

## 资源与安全计划（只准备）
新真实批次日后另卡解冻/定预算。本卡不得启动旧PG08任一容器、不得读取旧口令。计划优先全新专用合成容器/库/schema并用固定已在本机镜像，正常模式需PG则列其依赖；所有身份/端口/版本/标签/敏感脱敏及stop保留规则承接PG08，具体值在未来卡冻结。仅本机loopback，无用户库。每场景建议≤30秒、命令≤60秒、批总≤10分钟并预留收尾；超出合理最小需求则提前指出，不能伪写期限。
预期只有本次自有精确句柄/PID+创建时间、runTag可用于终止；不能按名称/端口杀进程。容器标签ID、进程身份、原始stdout/stderr+exit三者独立记录。runner按真实服务端5432核对连接、按docker映射核对宿主端口；PG current_user为裸关键字；unittest摘要通常stderr，原始流/退出码优先于summary解析。不要复制PG08含凭据状态文件。任何归属/清理未知即停，不重新领窗或自动恢复。

## 权限、验证和停止
本轮不运行Job/事件/spawn/子进程/PG/Docker/应用/联网/模型/安装，不读私有配置，不改生产/迁移/锁/正式docu/公共库/Git/旧证据。源码冻结，不与其他写入并行。只新增授权夹具与Ndocu/evidence/task-083/launcher-prep-09/（设计、manifest准备、hash/diff）和TASK-083-result.md置顶历史保留。
先完成全链文本一致性检查；一次项目backend/.venv/Scripts/python.exe读取新Python执行compile或AST不import、不写pyc，单命令≤60秒，不跑测试。若失败停并交回，不进行工具脚本循环修正。验证仅准备文件语法/接口一致性，不冒称动态通过；动态额度0。实际身份如实记录，完成/范围扩展/决定性控制点缺失则一次交回，不能停在只有计划的半成品；不受阻夹具与清单仍完成。
交付：新增文件用途与hash、真实入口覆盖矩阵、精确命令草案/注入与身份方案、已复用证据、资源与停止条件、独立审查重点和唯一未决变更。保存结果后仅回一句结论及绝对路径。原084随后只审新增控制/运行安全，再由编排授权实跑；D3旧G恢复事实路线另列，不在本卡叠字段或解决。不得宣告M-1/STEP008完成。
