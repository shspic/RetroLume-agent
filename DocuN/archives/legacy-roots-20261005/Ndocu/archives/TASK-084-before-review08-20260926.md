# TASK-084 / R-078 — review-07 D3候选实现及完整验证链独立审计
接收原084独立增强审计窗口，继续原隔离上下文；未参与083实现/夹具/runner编写。原窗口不可用才新独立增强窗口接续，不交实现者自审。不按历史模型标签重做已完成审查。本卡待用户转交，尚未派发。
TASK084/R078；STEP008局部，父083，关联082、NFR002/003、SEC002、FLOW005、DATA007。
项目根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.42、执行状态v1.60；Git基础45951501d2741630a229762d6b2d3f4b34d7f702，保护全部现有差异。用户已批准D3一列恢复范围，未撤回。

## 完整成果与调整原因
一次完成已批准D3的独立代码审计，同时审完本次真实验证所依赖的夹具、runner及剩余运行方案，给出完整且最小的修复/续跑清单。不是仅追查已知两行错误，也不重审整个项目。
原定真实验证后审计；现两容器已消费、真实恢复尚未到达，将必需代码审计前移，避免继续新建容器逐个发现静态可见错误。后续原窗口只对实际修正增量和新动态证据补判，不重复本次已完成代码审查。083暂停，审计期间被审文件冻结；旧Job07/PG08/09/review06有效结论按实际方法依赖复用。
本卡零动态运行，不能把静态放行写成D3完成，也不能自行批准重启/重置口令或第三容器。

## 独立读取顺序与范围
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；
公共规则D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD。
同窗已读未变复用；不读公共WORK或完整阶段提示词。
1. TASK-083-D3-work-decision.md已批准合同、Ndocu/tasks/TASK-083.md完整10合同和当前停止前缀、自己review06三项D3条件。不要加载实现聊天或以实现者自评作证明。
2. 原始产品006、activities/repository.py、worker/session.py、worker/windows_job.py及直接涉及的launcher/supervisor入口/接口；对应本轮pre副本、差异与必要调用方。独立形成代码判断留证。
3. backend/tests/test_d3_recovery.py、test_worker_session.py、fixtures/task083/offline_unit.py、d3_pg_windows.py；Ndocu/evidence/task-083/d3-implementation-10/runner_replacement.py，首版/替补as-run副本以及本轮修正差异。审完整可达路径，不只看异常类及选项白名单。
4. 再读原始offline-01证据、本轮manifest与replacement-20260925-195448/attempt-01/{stdout.log,stderr.log,meta.json,as-run.py}、runner-state.json、runner-log.txt、container-final.json、attempt-02.go及fix记录；最后TASK-083-result.md置顶两轮作为待核声明，披露顺序。
读取仅上述及必要直接依赖，不扫全仓历史。旧证明复用记方法/依赖及hash关系，文件hash变化不自动推翻未变行为；未知额外漂移停止对应结论并报告。
原始证据可能含连接环境，禁止读取/输出任何密码、完整DSN、容器Env或私有配置；只使用脱敏身份与结果。

## 当前冻结（SHA256）
backend/migrations/006_activities_running_owner_session.sql = f791f22dcfccf204f6fda369470978452b3b23cca0fc40d2057bd08ea47f6428
backend/app/activities/repository.py = d8a8ba184a84c6427e6c91e88b290c30aac43c355da708f4e09c26fd7cf996e6
backend/app/worker/session.py = dfd3423e3e5c367cae3cafe24d857dcbb9a9375c1ff4513cfa0499d052989bbb
backend/app/worker/windows_job.py = d04ed8f249106328d81147707451e6092c2d650c9199bd6c4989931d5249c596
backend/tests/test_d3_recovery.py = 5e7328437f23659bdbe0f944b85b2c59c4446a61f2e0840ac063f4c31d12bccd
backend/tests/test_worker_session.py = 4027f5cd72b17d826626704e118b0a194b0a7aef48c4ee4c8de4ac3efae69cf5
backend/tests/fixtures/task083/offline_unit.py = bb30163891de46ef97350b90c1988df5c5e0f80189dd13cdccb9e9c3c8264b6d
backend/tests/fixtures/task083/d3_pg_windows.py = 5f256503807b8945fbe4381466f22fb6be735d5ebcaa3d8d99bdfc69b0289651
Ndocu/evidence/task-083/d3-implementation-10/runner_replacement.py = 39e5917e0173aced0391f9729a4a3ce2f492ed41b8bb2c41e7cd205cc735a27f
末两项已改未运行。替补as-run runner=56e698a7f98b2732596153c26247a41e017420fc4c7e2af9d8d06ac80435ce8e。其他直接依赖按pre/既有证据核对适用性，不无限采hash。

## 必须一次回答的审查内容
A. D3产品合同：
- 006确为一列、域0..DWORD/NULL、旧行保留、事务回滚；Python拒bool/非法整数，0不等于缺值。claim身份与G同事务原子写入，耗尽None提交关闭，settle/cancel清理，最近G/C重试不得污染新窗。
- SUP可信自身会话号读取和失败出口；默认关闭的单主机单交互会话部署声明是否每条恢复路径实际执行，不把numeric SID当主机/boot身份。
- 旧running的有效租约/来源/代次在终止旧树之前校验；同号/NULL/异号及精确Job ERROR_FILE_NOT_FOUND、ACCESS_DENIED/其他错误、存在但未知/树空各分支，保守全额折叠，无部分退款。
- 活动互斥覆盖查询→可能终止/树空→claim提交→释放；响应丢失不spawn、不二次认领，异常收尾；新旧SUP迟到及并发取消/来源变化等直接传导按原合同分析，不凭函数文本没改认定没影响。
- claim租约时钟从主机时间改为DB CURRENT_TIMESTAMP是实际控制变化：与inspect/事务时间采样/等待锁后判断是否一致，有无先误杀再冲突/意外抢占；区分确定缺陷与需动态证明。合同曾禁止顺便换时钟，应明确这是必要修正、范围偏差或需更窄处理，不能略过。
B. 夹具与runner完整路径：
- 迁移空表/旧行/合法0和上界/负与超界/事务回滚的隔离、预期异常、rollback恢复、断言；ledger新G/耗尽/有效租约/幂等与可信SID。
- 真实Windows恢复是否实际调用生产路径，精确旧Job销毁/错误码、互斥提交顺序、旧新G/R/S/SID、PID+创建时间是否取真实对象；注入只制造前提、不替换被证明行为。逐个列将执行场景标识及证据缺口，不新增无关全套。
- 从参数入口→环境/匿名卷/端口/就绪→场景选择→失败等待与同runner定向复验→退出判定→finally逐步审完整链。核异常类真实定义/调用签名、合法选项、stdout+stderr与exit/逐项结果、超时共享deadline/收尾余量、failfast、attempt不可覆盖、有限等待、口令生命周期。
- 已知两修正是否闭合其整个同类路径；若同链还有静态确定错误，统一列出最小完整修正而非每发现一项即回传。禁止用跑脚本代替本次审查。
C. 原始事实与剩余资源：
- 首资源匿名卷误判无测试；替补首批006空表执行/负SID数据库拒绝后捕获路径AttributeError；second go被runner拒绝，第二测试进程未启动。限定已证明项，不能称迁移全通过。
- 两精确容器已消费：1086a37d40c34841d373487c10b278c5cfb771b81af7d70251fcb260c69421f0；
85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7。已有stop/Running=false仅日志时点证据，本卡不Docker查询。
- 已用离线3批、PG进程/真实批1、Windows0；原上限3/3/12，账面尚余2批/2PG/12Windows并不自动解除容器/凭据停止门。7.859s+另行收尾+81.765s保留，不重置30min总额度。
D. 给编排一个具体续跑建议：
优先评估精确已停替补合成容器能否在另行明确授权下安全复用，例如不读取旧secret的测试账号凭据轮换；这是方案评估，不授权执行。须说明必要身份/卷/端口/账号前提、凭据进入/退出与失败恢复、不可泄露方式、是否依赖尚未知认证条件、一次连续runner如何覆盖剩余测试和精确收尾。不能假设本地认证必成功或建议关认证/开放端口/删除旧库。
若无可据当前证据成立的复用路径，写明最窄缺口及唯一备选资源方案成本，让编排一次裁决；不要泛泛建议再建一只容器或把旧secret读取当默认解法。无须为方案搭建通用凭据平台。现有资源上限仍2，所有方案待编排具体授权；本卡不要求找理由放宽安全边界。

## 权限、额度及统一交付
只读上述代码/证据，可生成有限diff/hash；只写Ndocu/evidence/task-084/review-07/及Ndocu/results/TASK-084-result.md置顶review07，历史全文保留。禁止修改产品/测试/runner/正式docu/公共规则/记忆/旧证据/Git；不import/AST/compile/unittest、Docker/PG/Job/进程探针、联网安装或模型调用。现有官方论据复用，本卡不扩研究。动态额度0，不启动任何资源，也不执行实现者脚本。
完成本范围一次审查即停。发现高危问题留证；其余范围仍可只读完成后统一回传。结果必须区分确定代码缺陷、运行控制缺陷、证据限制和非阻塞观察；每个阻断项给触发、位置、影响和完整最小修正。
输出：代码层结论、夹具/runner静态准备结论、独立性/快照、证据复用、完整修正清单、剩余精确动态清单及推荐资源续接条件。代码可通过而动态未完成应分开写，不以缺动态无限否定已完成静态。以后只审实际变更和新动态证据，不重复本轮未变审查。M-1/STEP008/产品接线仍不得宣告完成，不填写编排最终验收。
结果保存确认可读后仅回复一句结论与绝对路径，用户转回编排。