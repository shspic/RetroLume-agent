# TASK099一次文档一致性检查

本记录属于TASK-099/R-093的设计证据，不是实现验证、独立审计或共享任务状态。唯一合同为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-099-result.md。2026-10-02当前Codex桌面会话按本卡做一个连续文档对应检查过程，发现的普通矛盾在初次交付前修正；最终字节和可读性另记delivery-proof.json。

## 检查范围及限制

检查A动作、B DTO/事实/锁/事务、C界面/意图/样例、D验收/资源/批准包的对应。只用了文件阅读、定向hash、普通文档JSON/UTF-8计量和文档写入；没有导入产品代码，没有compile、测试、PG、Docker、浏览器、应用、Windows Job、模型、网络安装或Git写操作。手工轨迹及SQL草案没有被执行，不能因此签并发、迁移、协议行为或真实质量通过。

输入索引38项、七份锁定规则的实际hash相符，详见read-manifest.json记录的2026-10-02T22:18:37.8892241+08:00读入时点；此后修改只涉及本结果和TASK099证据。没有全仓指纹或重复读取大量旧日志。版本仍为需求v1.1/架构v0.76/执行v1.98、task_model V4.0/公共AGENTS CHG-0003；00只核指纹，当前阶段07。

## 动作到DTO、事务、事实、界面及验收的对应

1. O01 → action=goal → T-local → goal不可变新版本/唯一state_after → needs_plan、旧下游历史 → “修正目标并保存” → V01/V05/V10。commands保存原CAS版本，goal事实版本加1，旧first不重入，G/R/S和预算不动。
2. O02 → plan → T-intent/T-launch/T-admit/T-mark/T-result → path_proposal指007、候选及reason → 正常path_review、用户未接受无当前新路径 → “重新提出路径·1次模型” → V01/V02/V09/V10/V14。中性输出仅理由，不建立可出题的路径。
3. O03 → accept_path → T-local → path_accept/唯一效果 → ready、新图空观察、旧题答反馈归历史 → “接受此路径” → V02/V06/V18。proposal必须当前且result_type=path，不能接受澄清正文或旧目标。
4. O04 → exercise及purpose/父反馈 → 同O02受控边界 → 一条exercise指007 → exercise_ready，参考不进普通GET → “获取练习/新复测题·1次模型” → V03/V06/V10/V14。initial/continuation/retest的阶段和独立性不同；中性结果保留旧题/答案。
5. O05 → expose及hint/reference → T-local → exposure COMMIT后才exposed_part → 当前或历史显示参考，暴露不能撤回 → “查看提示/参考·会记录暴露” → V03/V06/V09/V11。纯GET无写暴露权限，历史事实仍绑定原题版本。
6. O06 → answer及initial/continuation/revision/supersedes → T-local → answer/首答与继承链唯一性/暴露快照 → answer_saved或history_only → “保存作答·不调用模型” → V04/V05/V08/V10/V11/V15。评价在途可保存新版本，来源失效的窄留稿不推进head，取消/到期只能本机草稿。
7. O07 → calculate及reference_point_id → T-intent/T-launch/原G5 admit/mark/result → calculation指真实工具007 → support_check、无节点评分 → “核算这一步·1次有限计算” → V04/V13/V14。须先有参考exposure和有限工具许可；不接自然语言算式、任意工具或代码。
8. O08 → evaluate及answer/correction → 受控模型边界、原record_outcome同事务hook → 正常feedback/exposure/progress共最多3事实、仅progress承担一次效果 → feedback_ready或下一节点ready → “请求评价·1次模型” → V04—V14。旧资格仅历史反馈及历史exposure，无progress；原G3资格失效仍拒正文，中性结果不计观察。
9. O09 → correct及target/disputed_dimensions → T-local → correction不可变/当前争议投影或history_only → 依据题答指针决定ready/exercise_ready/answer_saved/feedback_ready → “纠正这条判断” → V07/V10/V17。回旧节点清不同节点的题答；历史答案不冒充当前，用户声明不是能力事实。
10. O10 → abandon及target_business_key → T-local/启动状态锁内判断 → command元数据收据，无伪造model/tool或record → 只放弃显示；claimed/UNKNOWN槽不释放 → “放弃这个显示意图” → V09/V12/V15。零教学revision的元数据整理不要求虚构state_after，不代表远端取消或预算退款。
11. O11 → select_node及archive_current → T-local → node_selection/唯一效果 → ready并清题答反馈/候选 → 路径节点按钮及归档确认 → V02/V06/V16。前置重新核验，放弃显示后仍须等待原窗口收尾。
12. X01 → 既有cancel，不新增DTO/教学operation kind → 原G/关门/R折叠 → 读页cancelled覆盖 → “取消活动” → V12/V13。R01—03对应workspace/history/records/citations/answers references纯GET → 单请求快照/受限历史 → V11/V15—V17，刷新0POST、0新SUP。

11个command action与SQL action集合一致，records有11种kind；O10只改收据，O08可产生三种事实，故动作与事实不应被误做机械一对一。record ordinal至4覆盖同事务最大批次。三表没有第三种operation kind，007只保留模型/工具正文，零费事实和命令完整输入不伪造费用行。

## 同一检查过程中补齐的口径

1. 原草稿对迟到历史feedback说不写新暴露，却允许历史反馈读取。已改为仍在原门禁允许时同事务写history_only exposure；纯GET须核对应暴露存在，后存同题答案纳入它，先存答案快照不被追改。来源/取消失效分支仍禁止新正文，未被此修正放宽。
2. 接受新图、选择节点、纠错回节点统一清不同节点的当前题/答/反馈；同节点保留合法当前作答。下一动作按实际阶段判断，不能拿历史答案或旧代码当当前版本。当前path与待接受proposal分开，O03/O11都清候选指针。
3. 明确command原CAS版本和新goal事实版本、历史事实原题版本；state_after带revision/goal_version及严格投影，history_only只增last_seq不增教学revision。
4. TeachingFrozenContext写成严格model/tool联合，不能在extra=forbid对象上临时追加未声明工具字段；固定模型输出额度冻结其中，旧protocol3/4不增加字段。exposed_part与retry_policy并入完整Receipt DTO，未知called用null。
5. clarification/no_evidence/conflict可有已提交规范正文，但不形成正常路径/题/观察，不触发自动重试；按原阶段保留输入及理由。受信phase/version/目录/进度不来自模型。

这些是初次交付前同一设计检查中的修正，没有生成第二套推荐合同，没有修改生产DDL、产品行为或正式状态。

## 样例、轨迹和大小对应

S1的参考由M1:L1—L4和手算导出：120米/2分钟为1m/s，150米/5分钟为0.5m/s，360米/3分钟为2m/s。单位错造成60倍差；K01/K02同时保留等价单位表达及数量级反例。S2原子性与隔离性依据M2，否定/等价/半句缺失分开；S3逐行手推正数计数和循环内return，正确结果与错误理由不能全答通过。三者未运行程序或模型，K01—K16覆盖题型、证据/逻辑、暴露、重复、版本与越权。

H1手工账相符：8次模型/0工具/8个窗口、Q8/C8000、h14、seq22、S16/R0是本轨迹假设值。feedback正常批次各3条，两个不同未暴露复测A2/A3才形成有限前进；重开只读不增任何账。原n1题答与反馈由reason/history展示，新n2当前指针已清。

H2同父同规范请求跨key以duplicate_of复用胜者，异文冲突；同key重放及响应丢失无第二answer/launch/progress，supersedes不分叉。H3目标/答案更新不动G/租约，旧feedback可历史加暴露但不推进，新来源失效遵原门禁拒正文；旧题新答案在迟到暴露前保存的快照不追改。H4预算尽仍可合法零费保存，确定失败才retry_of；UNKNOWN不解槽不退款，取消后只读，已保存答不因评价失败而丢失。

model-output-examples.json是三种代表性文档结构，不是provider返回。普通JSON紧凑序列化UTF-8长度记录于document-sizes.json：S1-plan为1335字节/881序列化字符，S1-exercise为1662字节/1312字符，S2-feedback为1784字节/1226字符，均低于16384字节。这只支持有界文档大小的建议；没有跑产品序列化、tokenizer或通道验证，也不能证明2048 token足够或模型正确。

## D范围、资源和交付核对

V01—V20覆盖全部动作、版本/源/UNKNOWN/四账/新迁移/旧兼容/客户端/内容/独立审计。每项说明最适层、复用与新增、预期正常及拒绝、最终字节；V19真实provider质量仍需单独授权和实际核查，V20保留稳定成果的独立审计，不把本文作者自检称独立审计。

下一实施范围为一个完整成果。17个建议业务窗口由H1的8、G5的1、目标/答/来源/取消的4、UNKNOWN/无效/显式retry的3、硬停的1相加；建议SUP创建尝试总20。管理窗120秒乘20为2400秒，加PG/API/UI至1200秒为业务总3600；清理独立360，离线/构建1800，主动实施上限12小时均仅建议，不是本卡运行许可。一个PG启动/两个合成数据库/一个应用/一个浏览器会话为首选资源合并；097旧bootstrap及依赖runner禁用、同根因两次失败重评、已用额度不清零、all-pass即停。

唯一主要决定G8-P包含完整三表/同事务接线/profile/接口/显式教学配置方案，未包含用户库、真实key/资料、付费或部署。原有Must无需反复确认；完整STEP013—020及向量/质量剩余Must保留。正式DocuS、共享TASK/R/CHG和经验库由编排维护，本轮未改。

最终保存回读只验证本结果和允许证据的实际存在、UTF-8可读、hash/大小、标识与Markdown围栏完整性。结果中F01—F13、O01—O11、S1—S3、H1—H4、V01—V20齐全；Markdown不用星号或表格。本文只结论为文档合同已收敛，不结论为实现/测试/迁移/模型质量通过。
