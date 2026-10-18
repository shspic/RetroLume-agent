# TASK-083 / R-077 — 受控真实Windows Job验证07
接收原083增强实现窗口继续执行既有冻结测试，不担任独立审计。STEP008，父082、关联084/R078、NFR002/003、SEC002。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.38、执行状态v1.52；Git基础45951501d2741630a229762d6b2d3f4b34d7f702和全部差异保护。
授权：用户2026-09-24批准082内部单窗监督与合成验证；084 review-05已关闭现有Job夹具确定阻断。编排本卡仅解冻现有Job01—05一次真实Windows合成批，不解冻PG/新D1入口/旧G恢复，不重置旧5场景尝试、超时偏差或费用。

## 唯一成果与输入
取得当前已审控制器下五场景真实对象归属、退出/清理及限定协议行为证据；正常完成或首次失败/未知时统一交回。不是实现卡，不修码，不追加测试设计。
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，已读未变复用。读TASK-084-result.md review-05分项运行门及review-03最小Job矩阵、TASK-082-work-decision.md批准边界、原Job失败/归属缺口记录（只读相关段），当前job_batch/job_control/scenario_child/fixture和必要直接依赖。原卡存Ndocu/archives/TASK-083-before-job-run07-20260925.md。
只读hash核对运行链：
backend/tests/fixtures/task083/job_batch.py 648e419cea693aa10630326cb28176e010a82b9f2c3380c33b42169c19bdef5b
backend/tests/fixtures/task083/job_control.py 5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2
backend/tests/fixtures/task083/scenario_child.py 98f132f272b952c22ac887efbf8026c5b00ec618838b6d484a3deec3c73f3f36
backend/tests/fixtures/task083/fixture.py c9970b8ddc718da1a4e83c6d206a67f6bd000d715578e028c0a0964d9f53dc7f
其余worker/仓储等直接依赖沿fixture-completion-06/final-hashes及084冻结。漂移停对应运行，不覆盖。纯单元三例、D1期限/碰撞等证据复用，不再AST/compile/重跑纯单元。

## 场景、精确入口与可观察事实
在D:/shspic/project_NO3_RetroLume-agent/backend/tests工作目录，运行绝对解释器D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe -B -m fixtures.task083.job_batch。模块入口可定位fixtures且既有脚本将backend加到路径；先文本核对环境/路径，禁止用额外import探针试跑。按已审脚本次序01→02→03→05→04，不能擅自重排或单独补跑失败/跳过场景。
01正常早停：干净合成活动、Job整树0后关门/结算，1≤C≤W；账本为合成替身，不能声称PG真实退款。
02挂死：有限截止终止确切Job，全窗保守账面结果、不部分退款；真实树空须观察。
03主进程先退出仍有后代：主退不当树空，终止/等待确切整树0。
05同名Job碰撞：拒接管现有对象、记录其精确身份与收尾，不按模糊名字查杀。
04最后句柄：Start生命周期与身份回执、准确worker PID/创建时间、关闭前Job计数1、释放观察句柄后SUP退出导致worker句柄signaled；对象销毁后无法查询ActiveProcesses时写null，不把单进程夹具推成任意整树通用证明。
每例保留runTag、UUID/G、Job名、PID/创建时间、事件/句柄交接、退出码/查询值与原始JSON。依据实际控制器输出裁定；缺关键归属数据即证据不足，不事后编造。旧04进程筛选count0不是树空证明，本轮不复用它替代观察。

## 资源、边界和新增额度
本批仅本机Windows、专用随机合成活动/命名对象/自有进程树，无真实模型/网络/HTTP/用户数据/PG/Docker；不读私有配置或凭据，不安装、不Git提交/推送。不改任何源码/夹具/迁移/正式docu/公共库或旧证据。本批串行独占本Job夹具进程，无并行测试、服务操作或代码修改；不需要端口数据库。
一次命令、最多五个场景启动；场景上限30秒（原控制器更短限制保持），脚本55秒批deadline，命令≤60秒；总体准备/执行/精确收尾≤10分钟，收尾预留≤60秒。原脚本有限等待/独立身份控制不得撤掉。启动前将冻结值、命令、顺序、预算与停止/精确清理办法写manifest，确认执行工具能记录原始stdout/stderr、退出码及墙钟超时，不以工具yield返回为进程已结束。
首次断言失败、timeout、cleanup_incomplete、归属/树未知、句柄错配或总截止到达，立即停止整批，不启动余项、不修复复跑。不要新加通用runner/看门服务；现有控制器不足以保障本卡界限的具体问题若启动前发现，停并报告，不临时绕开。清理仅本次runTag/精确PID+创建时间/已握句柄且归属已证的对象；不按python名/端口批量杀，不处理旧不明进程。无法确认精确归属则不猜杀，保留未知对象与最少人工处置需求。不能用只杀批入口掩盖未收束子树。
结果目录Ndocu/evidence/task-083/job-run-07/，仅可在该目录写manifest、原始日志/meta/hash/必要只读记录；结果Ndocu/results/TASK-083-result.md置顶保留历史。不得复制环境变量/DSN等敏感信息入日志。

## 交付及结论边界
逐场景实际已启动/通过/失败/跳过、身份正证据、命令/退出码/单一计时来源、清理确认或未知及原始证据路径；完成即停。失败保持真实原文，静态/替身PASS不能替代本批结果。即使五例全过，也只确认这五个已审合成Job行为：不覆盖新run_supervised_window固定SUP入口（现有01/02直接run_once，03/05直接Job）、不覆盖真实PG/005、不解决D3旧G恢复，不宣告M-1/STEP008完成。
执行者不签独立安全结论，回传由编排裁定；需要独立解释的新风险沿084窗口增量审，不默认再审全仓。剩余已登记路线为专用PG六例、新D1受控入口准备、D3化身事实决策，均不塞入本批。保存完整结果并确认可读后只回一句结论与绝对路径。
