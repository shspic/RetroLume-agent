# TASK-080 / R-074 — 续作01：首提交范围冻结准备（当前唯一有效指令）
你是本卡执行Agent，继续已完成080的Work Buddy新工程窗口，常规执行；实际模型如实登记。目标是补齐纳管边界并生成可审批的精确本地首提交清单；不重新初始化仓库、不重做已完成环境核验。
关联STEP-002补项、CON-002、SEC-001、TASK-043。根D:/shspic/project_NO3_RetroLume-agent。需求v1.1、架构v0.33、执行状态v1.34。用户已授权本地版本管理准备；尚无commit/push授权。

上下文：读取根D:/shspic/project_NO3_RetroLume-agent/AGENTS.md及公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（未变已读不重复全文）；本项目Ndocu/results/TASK-080-result.md、本卡、.gitignore、原candidates.json/md和verify-log.json；状态顶部本轮裁定。旧合同保存在Ndocu/archives/TASK-080-before-revision01-20260923.md，只作历史。

编排裁定与连续工作：
1. 初始化、main无提交/无远端、局部autocrlf=false、原规则纯追加证据已采纳；不再运行初始化脚本。两份旧证据含合成凭据，本地原件保留不改、不纳管，不以容器据称销毁作为公开依据。
2. 根.gitignore追加精确的根相对规则：/Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json 与 /Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json。不读取/打印凭据值，不改原件。原29项非候选二进制/生成物维持不纳管，不需要为这些普通材料整目录忽略。079证据首提交全部排除：新增/Ndocu/evidence/task-079/规则，明确仅首提交暂缓追踪，原始文件仍保留，未来选择性纳管须另查敏感信息并调整规则。079任务卡/结果已脱敏文本可以候选纳管，但仍须检查。不得复跑079。
3. 在Ndocu/evidence/task-080/revision-01/生成全量精确首提交manifest（相对路径、字节数、SHA256、类别），保持原候选范围并补新增必要结果/当前文档；排除私有配置、凭据、生成目录、所有079证据与原29项。旧清单598不是固定目标数量。当前manifest及本轮动态日志不能自引用hash，放独立排除列表；全部排除逐条有原因，原清单历史保留。不改产品/原证据，不掩盖缺失源文件。
4. 对候选文本做有限敏感检查，只记录路径/模式/裁定，不回显秘密。新增不确定项排除并回报，不能认为首轮扫描覆盖了后来改动。逐项检查004确在清单（旧结果“001—003系列4份”文字纠正为001—004）。
5. 生成UTF-8 NUL分隔literal pathspec清单及将来暂存/提交的操作说明（只写文件，不执行）；防止Git pathspec魔法匹配扩围。列推荐提交信息、main、只本地无远端、现有身份可用性（只存在性，不打印身份）。提交前必须逐条核验manifest hash，漂移即刷新受影响清单交回；精确比对实际暂存路径，不能git add -A，不能凭候选数量判断范围一致。
6. 本轮一次静态清单/忽略边界检查；允许有明确修正依据最多一次复检。核验两份凭据证据及079证据被忽略、必要源码/锁/004与脱敏样例未被误排除，未暂存/提交。单命令≤60秒，不运行产品测试/PG/Docker/网络/安装。完成即停。

允许写根.gitignore、本轮revision-01证据、Ndocu/results/TASK-080-result.md置顶续作并保留历史。现有.git只读，不改global/system或身份，不add/commit/push，不删除、不改业务及正式docu/公共库。无端口/容器/测试资源预算。正式提交动作须编排在具体清单准备完成后取得用户对应授权，再沿本卡续作。本轮不以缺提交授权阻碍准备工作。
并行：与079无操作冲突；编排本轮文档写完后交卡。清单采集后有别的Agent改动则记录漂移，不覆盖。发现真实秘密风险、范围扩大或两次修正仍失败，完成不受阻项后停止交回；无需新增独立审计。
交付：完整候选/排除清单、规则前后hash/diff、敏感检查摘要、精确pathspec及未来本地提交操作说明、真实检查命令/退出码；结果保存D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-080-result.md，注明未提交/尚未建立版本历史，不填编排最终验收。回复一句话结论与结果绝对路径。
