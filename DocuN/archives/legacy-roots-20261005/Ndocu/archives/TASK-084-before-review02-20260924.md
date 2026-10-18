# TASK-084 / R-078 — 内部单窗监督候选独立代码与运行控制审查
你是独立审计Agent，不接管编排、不实现或运行测试。STEP008局部，父083，关联082/076—079、NFR002/003、SEC002、FLOW005/DATA007。
接收增强执行（Codex Sol或同等强推理模型），全新隔离窗口，未参与082诊断转083实现、083离线补足；不得沿该实现窗口签发独立审计。真实身份如实记录，判断以事实/证据为准，不以名称代替能力。安全/并发/Windows归属和退款需增强档。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.37、执行状态v1.42。Git基础45951501d2741630a229762d6b2d3f4b34d7f702，加083实际源码/新文件及既有文档差异；新文件不能因git diff未列入就漏审。

## 唯一目标
一次审查最终候选是否符合批准的先预扣/单窗/不可重开门/整树退出后退款/跨恢复保守处理，是否具备安全进入定向Job/PG验证的运行控制条件；输出确定缺陷与最小受影响验证矩阵。不是整仓审计、产品最终验收或对已有079行为重审。

## 独立输入及顺序
1. 根AGENTS.md、公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD；读Ndocu/results/TASK-082-work-decision.md仅批准合同和末尾用户批准，跳过诊断自评；需求NFR002/003、SEC002原文。
2. 完整合同Ndocu/archives/TASK-083-before-offline-repair-20260924.md与当前Ndocu/tasks/TASK-083.md离线补足，二者分别提供功能原合同及有效停止边界；无需读取实现聊天或TASK-083-result.md自评。
3. 当前worker七Python文件、activities/repository.py与__init__.py、005、test_activity_dispatch_close.py、test_activity_time_budget.py、test_worker_session.py、tests/fixtures/task083/全部实际Python（含launcher控制、offline、PG）；必要直接依赖gateway/transport/runtime、001—004、PDF原Job源码只读最小片段。原修改前副本在Ndocu/evidence/task-083/pre/和offline-repair-01/pre/，可生成有限diff；仓储前hash见083原合同。
4. 初判先留存，再读Ndocu/evidence/task-083/job-initial.log、cleanup-process-check.txt、offline-repair-01/unit-initial.log、unit-recheck.log、static.log、manifest.md及两个时期hash清单。原始失败必须读，不以实现者“已补足”代替审查。若意外读自评或项目记忆披露接触范围，不伪称盲审。
已知事实非预设通过：Job初批5例2失败且04身份/超时缺口，旧count0不能证旧Job空；纯单元10项初批9过，失败项一次复检通过，但之后仍有源码改动，旧静态/动态证据不完整适用最终快照。预算已冻结。

## 快照
Ndocu/evidence/task-083/offline-repair-01/final-hashes.txt为16文件清单，编排本轮已复算全一致。审计独立核对并绑定使用；补充三文件冻结：
- activities/__init__.py 0c5ea723c270efae0bac9f5aa9517628d1ebc88844a3c4e41829188b52f2be78
- tests/test_activity_time_budget.py cb5a51960b830825350f5e30f9430de6b04c939489d8fe8cac0c76172c2e1245
- tests/test_activity_dispatch_close.py ecfbdad21e53183ab6a76b7eda909256ba7f6a38c9327a29216d8f6d399aa130
本批冻结不并行源码写入；哈希漂移停相关结论，报实际文件/hash，不以旧快照签当前通过。

## 必查八项（按实际实现判断，不复述方案）
1. 005先锁后判空原子DDL，非空拒绝；关闭位默认值不授予资格，只有claim新代次可开门。close身份代次校验、幂等、锁序；admit/mark拒绝关门，record/recover合法收敛不被共同helper误阻断。settle初次关闭前拒绝，最近旧G/C确认不伤新窗门/R/S；取消/折叠不误退款。
2. 本地门真正进入Job worker路径，closed先挡新令牌再排空；令牌覆盖admit前至mark/send/底层收尾，取消/异常/已mark未send不能脱离追踪。区分内部可信注入约束与未来未接供应商；不能要求未授权生产接线，但必须审查当前任意命令/回调是否绕过本切片应保证的边界。
3. t0认领前、先确知预扣再spawn/Resume，W_eff实际值及partial/claim响应丢失；t1须整树退出正证据之后。SUP关闭与结算顺序、1≤C≤W、失败/超窗/DB late-response、不把保留R当已入S、不把未知报0；管理开销单独有限、不承诺绝对硬实时。
4. launcher专用进程总deadline在创建前固定；start/join/管道recv/send/terminate/kill/DB/互斥/Job query都不能绕过剩余预算。阻塞Win32与应用事件循环隔离，异常/取消/子进程pickle与解释器环境适配，修复是否仅将无界回调转移到别处。父启动器/SUP死亡故障模型一致，不借无限看门层掩盖。
5. 活动跨线程/跨进程互斥、命名空间/ACL/碰撞、句柄继承/最后句柄、无breakaway、悬停Assign、旧SUP迟到动作及恢复读取竞态。ActiveProcesses0必须对应确切对象；Open失败不能当0。未知旧树拒绝新claim；必要失败关闭是安全限制，但若正常重启永远无法恢复须如实列可用性缺口而非称需求完成。
6. finally之后生成结果；主异常/清理异常、句柄关闭/互斥释放失败均不能逃逸剩余收尾或虚报clean。取消/超时后无悬空能创建Job的主体；无法证明收尾则不退款/不开新工。实际接口字段与语义一致。
7. 测试控制器是否在Resume前掌握精确归属、创建时间、独立deadline；venv转发器场景、事件/管道双向等待、父死/子存/同名碰撞是否可靠取证。检查观察句柄是否改变被测“最后句柄关闭”条件，不能由夹具自身保活Job然后误判产品。原5场景哪些证据可复用、哪些修复使必须再验逐项说明。
8. 可执行PG夹具专用DSN/缺失skip、随机schema与search_path实际传给仓储、001—005顺序/空非空迁移、不回退用户库、并发事务真正控制顺序而非只睡眠、FK定向清理及失败保留。指出静态可确定失败的夹具问题；替身不能冒充数据库/OS验证。最后源码补正未运行项映射具体测试，不机械扩大/删除回归。

## 交付与停止
逐项判定：代码层通过/有条件通过/不通过/证据不足，与Job可运行/PG可运行分别列。缺陷给文件行号、最短触发/交错、影响与最小修复；区分确定缺陷、条件风险、动态未验证及非阻塞观察。必要独立安全审计结论只限当前代码，不替代动态证据。
输出后续最小验证清单：先应修哪些确定缺陷、需补哪些最终快照纯单元、Job01—05分别执行或复用理由、实际PG测试ID及受影响旧测试；明确场景/命令硬截止和收尾可控性是否已足够，由编排另卡给运行额度。不是预授权全部重测。
只写Ndocu/results/TASK-084-result.md及Ndocu/evidence/task-084/有限hash/diff/初判；不改产品/测试/迁移/正式docu/公共库/旧证据/Git，不运行代码（含compile/AST/import/单元）、不spawn/Job/PG/Docker/EXPLAIN/网络/安装/模型，不读真实配置。官方事实沿082原文链接导航，若必须新取证则具体列缺口，不臆测。
达到限定覆盖即停，不扩大为整项目审计。不依实现自评提前下结论，不以安全措辞强造新需求。报告实际读取/身份/独立性及未运行范围；保存指定结果，回复一句话结论与绝对路径，供用户转交编排。
