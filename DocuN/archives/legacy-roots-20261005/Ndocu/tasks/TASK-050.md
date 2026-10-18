# TASK-050 PDF资源监督独立审计

类型独立审计；STEP-005；R-044；关联TASK-047、FR-001/SEC-001；强档内部Sol隔离新Session，无执行聊天。原始任务目标见TASK-047.md，不以执行者自评为依据。
根D:/shspic/project_NO3_RetroLume-agent；先读AGENTS与docu/AGENTS.MD。本卡只审冻结pdf_import组件、对应test_pdf_import及原始TASK-047-unittest.log、TASK-047-unittest-pass.log，必要依赖固定pypdf6.17.0许可证/锁。不得以TASK-047-result自评替代原始代码和日志，不读其他执行聊天。
目标：独立判断Windows Job挂起创建/分配/恢复/有界等待/kill-on-close是否实际覆盖解释器与子进程，源/临时路径及协议处理是否与范围吻合；确保默认pending_human_review、不执行PDF脚本链接、故障失败关闭。资源监督不等于文件/网络权限沙箱；明确暴露边界是否符合原任务，禁止误称全面恶意文档安全。
只读所有实现，不修改代码/锁/数据/共享docu，不安装/Docker/API/重跑测试。代码/原始局部测试足够则引用；发现决定性缺口列具体函数、影响、反例和最小补证，不为没有全面恶意样本机械阻塞所有开发。若需要额外真实验证另给具体卡建议，不自行扩大。
只写Ndocu/results/TASK-050-result.md：独立性、检查版本hash、可复用原始证据、发现及严重度、已验证与未验证边界、阻塞/放行建议；不能将没有独立重跑写成已执行。结果由Astra裁定。一次定向审计，不扩到整库或模型预算，不重复048的工作。
