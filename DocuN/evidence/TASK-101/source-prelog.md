# TASK-101 / R-095 独立源码初判

本文件在读取 TASK-100 原始运行日志前保存。身份索引 90977b25905c3af72eacc27210f32bd64ec95c86d8d52ebaaf88cb41ed74110e 已独立核对 797 个对象，全部匹配。对象分组为 112 最终源码及夹具和 dist、18 保护产品、7 规则、3 合同、657 运行原件。hash 仅表示字节身份。

已读取原批准合同 A—D、DDL、S1—S3、H1—H4、V01—V20，核心教学仓储、DTO、service、policy、progress、views、HTTP、前端及准入和原子提交直接依赖。具体范围与读取时间见 reads.jsonl，首次身份核对见 independent-hashes.json。没有导入或执行产品，没有运行旧测试、PG、Docker、SUP、构建、浏览器或 provider。

独立性披露。当前为新的 Codex desktop 审计对话，系统说明身份 GPT-6，无法验证具体部署型号，也没有证据声称不同模型家族。未读取 TASK-100 结果、自评、work-decision、receipt.json、实现聊天或实现记忆。读取唯一状态账顶部及一次过宽定向搜索时意外看到编排的部分通过/计数摘要，不能声称从未见过任何编排评价；这些摘要不用于判断。客户端记忆只读到用户避免重复前置测试的规划偏好，无 TASK-100 实现资料，不作为技术证据。

## 已定位代码缺口

- 候选 F01，P1，确定代码缺陷。teaching_policy.py 的 derive_support_checks 80—135 行不使用 answer_text，只比较参考的 left/right 与参考 value_decimal。teaching_progress.py 46—61 行随后以这个 matched 加模型 met 判合格独立观察。错答如 S1 的 60 m/s、0.01 m/s 若模型误判 met，确定算术屏障没有比较实际答案，两个实例可能进入 evidence_sufficient。合同 099 第 5.2 节及 V04/V06 要求确定数值/单位冲突收紧模型判断。需要在有限可核查答案域中比较答案；无法可靠解析则 unchecked/unknown，不能称 matched。此判断为 B 级静态调用链，不声称已执行反例。
- 候选 F02，P1，确定代码缺陷。teaching_views.py public_record 71—96 行只以当前活动 sources 判断 derived 资格，不核 row.source_refs。用户通过原 revise_scope 更新活动至新的有效范围后，旧记录虽 scope_revision 不同仍返回 history 正文；原来源失效不会再触发当前 source_invalid。历史练习参考暴露的 T-local 637—667 行同样只核活动当前来源和原正文。应逐记录核绑定来源/旧 scope，来源失效只保留身份并抑制派生正文，不能因新范围有效恢复旧资料。合同 V11、A5，资料版本不变更或 source_invalid 覆盖层的正常证据不能覆盖此竞争条件。
- 候选 F03，P1/P2 待按完整影响定级，确定代码缺陷。teaching_api.py _read_bounded_body 53—63 行先 request.body() 全量缓冲，再计 32768 字节，未按 stream 提前中止，也使用默认 json.loads，重复字段覆盖后再 DTO 校验。模型输出的重复键拒绝不能证明 HTTP 命令输入已拒重复。main.py 没有更外层正文流量限制。合同第 5.3 节及 V14 要求解析前流量限制和恶意重复键拒绝。
- 候选 F04，P2，确定恢复合同缺口。TeachingService.submit_command 53—59 行对既有 accepted 命令直接只读返回，_submit_model 中获取唯一 claim 的分支不再可达，accepted 尚未 claim 的同键显式再试无法继续；claim 后 no-operation 保守不重发是另一种正确状态。放弃未 claim 显示后新键可替代，但同键恢复未实现。合同第 6.3 节及 V09。
- 候选 F05，P2，确定上限遗漏。MAX_PATHS=32 已定义，但 counts/accept_path 与结果写入没有接受路径数检查，反复 plan/accept 能超过活动 32 条路径。有限命令/总记录上限不能替代独立已批准路径上限。合同第 4.2 节与 A1。

## 具备源码支持的边界

- 009 三表、同活动 FK、首答/修正版/反馈效果唯一性、records 无 UPDATE/DELETE、command 身份和非空 launch 不可重置具备明确实现。新 records 的 applied_revision/state_after 在 INSERT 前成型，当前 feedback 的效果只由 progress 承担。
- 来源→活动→operation 排序→head→command 锁序、T-intent/launch/admit/mark 版本与冻结 hash 复核、当前/历史结果分支、缺 command 导致原正文同事务回滚具有源码支持，动态适用性尚待原件。
- 原关门、G/scope/租约资格及 ALREADY_PRESENT 优先级保留。正常结算后 pending/dispatch_closed 允许教学下一窗口进入原 claim_lease，不把关门放开当准入。
- workspace/command/history/record 共用一条 CTE 业务快照；set_config 两条只设置事务超时。通用 operation GET 不回教学正文，教学未暴露参考仅由专门 public 投影提供。来源历史逐记录资格缺口见 F02。
- IDB 完整正文与 localStorage 摘要先成功再 POST、Web Locks 跨标签摘要及 IDB 同事务容量、只 GET 重开、unknown 有界单快照、React 字面渲染具备源码支持。最终 reason 的读取确为 reason.body，需要结合原 DOM/截图判断尾断言失败与当前 bundle 显示；暂不申请或启动补证。

## 待原始证据核对

下一步只读 033911/041623 运行原件、最终离线与构建，逐方法建立源码版本绑定，核 29 PG/4 HTTP、六迁移/非空旧操作、八 Windows 场景与 17 窗及重开四窗、10 浏览器控制、纠错事实和脚本完整 diff。保留各原批 FAIL、未执行尾项及缺少独立 as-loaded/Chromium 后代出生时间的边界。随后完成八组、V01—V20/H1—H4、执行控制及最终报告，不以发现单个问题中止其他可读审查。
