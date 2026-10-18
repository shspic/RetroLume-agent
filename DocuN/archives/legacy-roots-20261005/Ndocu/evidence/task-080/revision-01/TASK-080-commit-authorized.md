# TASK-080 / R-074 — 续作02：已授权本地首提交（当前执行指令）

你是本卡执行Agent，沿已完成080续作01的Work Buddy工程窗口，常规执行；记录实际模型。完成本地首提交与核验后统一回传，不接管编排。
项目根D:/shspic/project_NO3_RetroLume-agent；关联STEP-002补项、CON-002、SEC-001；需求v1.1、架构v0.33、执行状态v1.34（提交前冻结）。
授权：用户2026-09-23对“冻结清单599文件提交到本地main，不设置远端、不推送”明确回复“确认”。授权包含该范围的暂存和一次本地首提交，不再索取重复批准，不扩大文件集合或内容版本。

## 合同位置与最小上下文
读取根D:/shspic/project_NO3_RetroLume-agent/AGENTS.md及公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（已读未变则复用）。读取本卡、Ndocu/evidence/task-080/revision-01/manifest.json、pathspec-first-commit.txt、excluded.json、first-commit-playbook.md及原verify_revision01.py。
本卡取代TASK-080.md中“未授权提交”的当前执行限制，仅本轮优先；根任务卡及docu/CHANGE均在已获批599文件中，暂不改动，避免编排自行打破批准快照。此完整续作卡放在本轮已排除目录，不新增TASK或第二状态账本；本地提交验收后由编排同步共享文档/CHANGE。不得将本卡或本轮结果顺手并入首提交。

## 精确批准范围
仅manifest.records的599路径及其逐条SHA256，不接纳清单之外的新增文件或漂移内容。
- manifest.json SHA256：938dbfbdc3fc13413ff22613b6c032b1e93aa9269ea0a28df5bbf62bc8e01b32
- pathspec-first-commit.txt SHA256：06f0d263b33d87d73a43becd05e3708ec0e2934f36979a46f4784655db9e2699
- .gitignore SHA256：7b56964c67acb3b39a2e2e7c01280e984d0ce726558ecab4db8e265b7fe030db
两份073/074含凭据原证据、全部079证据、29项排除材料、revision-01全目录及TASK-080-result.md本轮结果均不入首提交；原件保留不删。manifest/指令/日志本身不入首提交，授权不包含动态产物的随后补交。

## 卡内连续执行
1. 冻结本窗口产品/文档写入；读取Git实际根/分支，要求根正确、main、无现有提交、暂存区为空、无远端。核对上述两个清单hash、599文件hash与literal pathspec精确对应；沿用规则与敏感检查的有效证据，不重扫无变内容。发现已存在提交或暂存、外部写入、漂移、未知hooks/过滤器时停止交回，不reset/clean/覆盖用户工作。
2. 沿用现有可用Git身份，不修改global/system/local身份，不打印用户身份或凭据。缺少必要身份或有效签名配置导致无法提交则报告具体缺口，禁止虚构作者或关闭用户安全设置。
3. 使用卡面literal NUL清单执行一次精确暂存：
   git add --pathspec-from-file=Ndocu/evidence/task-080/revision-01/pathspec-first-commit.txt --pathspec-file-nul
   禁止git add -A、git add .、强制纳入忽略文件或其他目录。暂存后使用NUL分隔输出核对路径集合恰为599，逐个读取暂存blob原字节并以SHA256对照manifest，避免只核工作树而遗漏过滤器/换行变换。工作树也需保持清单hash，任何不符不提交、不静默修改索引/规则。
4. 原verify_revision01.py可作参考，但末尾不以非零码表达all_passed=False，且原staged路径读取需注意中文quotepath。不得只凭进程exit0判通过；如复用必须确认JSON all_passed=true。允许在已排除revision-01目录新增本轮有限核验脚本/日志，使用git -z字节路径避免显示转义；不改旧证据，不建通用框架。
5. 全部前置达标后在main执行一次本地提交，提交信息：
   chore: initial import of RetroLume-agent working tree (TASK-080/R-074 rev01 snapshot)
   不设远端、不push、不amend、不补第二次提交。若命令超时/返回不明，先只读查HEAD确定有无提交，不盲目重试。如果失败则保存证据交回，不清空用户环境、不重复尝试。
6. 提交后核对HEAD提交hash、仅一个根提交、main、无远端，HEAD树路径恰为599，树blob原字节SHA256逐项对应manifest；暂存为空、已跟踪工作树无变化。未跟踪的排除/动态产物允许存在，逐项有理由即可，不能为“干净”删文件。记录提交ID、tree ID、路径数量和核验摘要，不输出身份和文件内容。

## 边界、预算与回传
只允许Git本地暂存/本次首提交所需.git写入、revision-01内本轮证据、Ndocu/results/TASK-080-result.md置顶续作02并保留历史。禁止修改599文件或其他原件、公共库、正式docu；无Docker/PG/模型/网络/安装/产品测试。不能启动079；提交期间不得与写入599文件的其他任务并行。
状态/内容检查每个必要时点一次；单命令≤60秒，只有明确核验脚本缺陷允许一次修正复检，不重跑旧13项全套或新增业务测试。完成即停；范围漂移/安全边界未知/运行失败保留现场交回，未提交可保留暂存并如实说明，不自行撤销。
回报D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-080-result.md：TASK/R、授权范围、实际命令退出码、提交及树ID、599项匹配/排除验证、未跟踪材料、身份仅可用性、失败或偏差、正式文档待编排同步。完成不等于产品验收，不填写编排最终验收。回复一句话结论与结果绝对路径。
