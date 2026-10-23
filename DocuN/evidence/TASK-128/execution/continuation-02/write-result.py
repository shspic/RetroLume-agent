import hashlib,json
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[4]
old=(E/'pre/DocuN/results/TASK-128-result.md').read_bytes()
assert len(old)==25623 and hashlib.sha256(old).hexdigest()=='472882152a5283bf0ff36d72ff1b73b7a9822e1cfff4dda5c0afa942950efc55'
state=json.loads((E/'checkpoint.json').read_bytes())
assert all(state['checks'][str(i)]['status']=='passed' for i in range(1,7))
full=Path(state['slots']['source']['successful_receipt']).read_bytes()
assert hashlib.sha256(full).hexdigest()=='a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06'
partial=(R/'.runtime/normal-first-install/interrupted/receipts/task128-c02-expected-unknown.jsonl').read_bytes()
assert partial==(E/'entry-07/interrupted-expected-unknown-receipt.jsonl').read_bytes()
lines=[json.loads(line) for line in partial.splitlines()]
assert lines[-1]['unknown_stage']=='002' and lines[-1]['confirmed_stages']==['001']
assert [r['stage'] for r in lines if r['event']=='submitted']==['001','002']
assert not any(r['event']=='complete' for r in lines)
api=[]
for i in (1,2):
    before=json.loads((E/'entry-08'/f'api-{i}-database-before.json').read_bytes());after=json.loads((E/'entry-08'/f'api-{i}-database-after.json').read_bytes());assert before==after
    o=json.loads((E/'entry-08'/f'api-{i}-output.json').read_bytes());assert o['interval']['exit_code']==0 and all(r['exited'] for r in o['stop_proof']) and not o['listener_after']
    api.append(json.loads((E/'entry-08'/f'api-{i}-observations.json').read_bytes()))
assert api[0]['control_id']==api[1]['control_id']
with (E/'functional-crosscheck.json').open('x',encoding='utf-8') as out:json.dump({'six_checks_passed':True,'source_receipt_unchanged_sha256':hashlib.sha256(full).hexdigest(),'partial_receipt_sha256':hashlib.sha256(partial).hexdigest(),'partial_lines':len(lines),'submitted':['001','002'],'confirmed':['001'],'unknown':'002','api_same_control_id':api[0]['control_id'],'both_database_before_after_identical':True,'both_parent_exit0_tree_ended_port_released':True},out,indent=2)
body='''# TASK-128 / R-122 续作02 当前工程回传

剩余第4/5/6项真实验证已完成，连同已独审采纳的代码修复和前三项，六项工程证据齐全；两库及自有API树已停止，成功/部分库、原收据与全部历史保留，提交主控核新增动态原件及最终验收，Q继续关闭。

本置顶为当前事实。下方续作01及首轮共25623字节完整原文作为历史后缀保留，旧失败/未跑没有被抹除。本轮未改产品代码或P3注释、未重装源库、未重跑旧19/22/23或18/9方法、未新开独审。

## 4/5/6实际结果及原件

| 项 | 实际结果 | 关键证据 |
| --- | --- | --- |
| 5 独立002提交未知 | 通过，唯一注入一次 | 正式001确认，原002由真实驱动执行、全部结果耗尽且COMMIT/IDLE后唯一隐藏确认；收据001 confirmed、002 submitted/unknown，无003/complete/重放。独立只读查询已见activities等002表、003表与控制行不存在，业务计数均0。原部分收据再次apply/verify本地0连接拒绝，新收据对部分库真实零写拒绝，库/卷/收据保留。[check5](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-07/check5.json)、[真实提交trace](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-07/interrupted-expected-unknown-trace.jsonl)、[原部分收据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-07/interrupted-expected-unknown-receipt.jsonl)。 |
| 6 成功收据只读verify | 通过，一次实际verify | 原source/CID/OID/systemid/三UUID和37行完整收据一致，正式CLI仅注入管理员密码引用，其他三秘密/业务与快照DSN未传。真实READ ONLY、原schema/roles与身份核验通过，写请求0、完整收据原字节不变；坏绑定receipt_mismatch且连接数0。[check6](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-07/check6.json)、[正常verify trace](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-07/source-readonly-verify-trace.jsonl)、[坏绑定trace](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-07/source-wrong-binding-trace.jsonl)。 |
| 4 原生API跨PG重开 | 通过，entry08两个完整周期 | 原start_local.py/--shutdown-stdin，固定18122；两个周期之间真实停止并重开同一source PG。会话/capabilities均本地storage_ready=true、normal/R03、source_observation_status=configured，Q real_outbound_authorized=false、模型与integration/preview原生关闭；不是把任意200/503算通过。实际pg_stat_activity观察到retrolume_normal_app，未交管理员凭据。控制身份、三UUID、根实体及DB事实跨PG重开不变，两周期各自before/after表OID/计数相同，原生正常退出0、全部自有树结束、端口释放。[周期1事实](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-08/api-1-observations.json)、[周期2事实](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-08/api-2-observations.json)、[周期1退出](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-08/api-1-output.json)、[周期2退出](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/entry-08/api-2-output.json)。 |

第5项开始前以原preflight真实核interrupted身份/空态且关闭诊断连接，没有用旧trace零写推断恒为空。预定确认隐藏只在本轮entry07实际发生一次，原127和128旧失败都没有注入；entry08没有再次调用它。部分原收据6行，SHA256=f9a30db481b0849c352c759350e86fd71c6c4ded41b65d2cd76e2a76bd9d0e17；私有原件与证据副本相同。两次本地拒绝分别output_exists/receipt_incomplete，新收据实际预检target_not_empty_or_exclusive、安装写请求0，随后库对象/计数未变。没有继续003、清空、补签、退款或新建槽位。

源完整37行成功收据仍SHA256=a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06。verify真实观察仍172.19.0.2/32:5432、PG170011/UTF8及原systemid；没有修改收据以迎合新观察。源apply在本轮控制器和观察CLI均硬拒绝，因此没有重放已成功001—015或原控制行。

两个通过API周期的ControlHub control_id均4010e6be-3a8c-4a01-8c67-2bc99a22d3d7，selection_generation=0/current_mode=normal/read_only=false，binding_kind=original_control_hub，restore_executor_configured=false；没有切只读副本/旧目标/TESTONLY。两原生周期分布在source累计第6和第7次启动，中间有实际Running=false/Pid=0与start区间。完整对象身份和表计数对照保存于相邻api-1/2-database-before/after.json及checkpoint.source_after_first_api；不是两个GET或同一PG内重复开API冒充PG重开。[收据/生命周期交叉核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/functional-crosscheck.json)。

## 容量恢复及一次辅助修正

新合同允许90秒等待但512门不降低。entry07先完成独立中断保护，停库后source启动门从490.6171875MiB等待52.235秒到525.78515625MiB再启动；首API从438.09765625MiB等6.047秒到512.8515625MiB后启动。interrupted启动2007.88671875MiB立即通过。entry08两个source启动门分别947.61328125/934.1328125MiB，两个API门937.37890625/927.01171875MiB均立即通过。每次等待/实际值在entry07 capacity-1—3及entry08 capacity-4—7；等待计入控制器工具时间，PG活跃时也计持有。未改宿主服务、开第二PG或要求用户释放内存。

entry07第5/6项已通过，首API实际就绪、正常源/Q关闭事实完整，但辅助在parent返回0后立即检查全部后代句柄，得到api_tree_stop_unconfirmed。按记录PID+birth只读复核，六个原PID均已不存在，端口无占用，没有强杀。原失败、as-run、capabilities和诊断保留；首次API stdout因旧辅助在写日志前断言失败未保存，不补造，其停止缺口由独立只读诊断说明。该周期计入启动/持有，但未计为最终通过的跨PG周期对。

仅修本轮helper：发送原生stop后关闭自有输入，保留原生170秒收尾上界等待后代信号，分别保存即时/最终状态并在两周期就地保存数据库before/after。不改原启动器、不削弱退出0/树结束/端口释放断言。[原失败诊断](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/api-stop-diagnosis.json)、[helper差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/helper-repair.diff)、[修正依据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/helper-repair-decision.json)。

entry08只续未通过的API对，不重跑前三项、唯一注入或verify。两次即时快照均还有一个后代未信号，随后分别自然等待约0.063/0.047秒即全部结束，直接支持这次辅助时序修正；没有等待到170秒、没有强杀或新产品缺陷。普通预备读错scope文件名、可选依赖路径不存在以及一次build脚本未闭合字符串均在资源启动前定位/纠正，未虚算实际start，见[failure-ledger](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/failure-ledger.json)。

## 连续账、实际身份与停止

接收原A+工程窗口，TASK128/R122，关联129/R123、127/125/126及STEP018/019/020。实际客户端Codex desktop，Codex/GPT-6家族，具体后端变体不可读取，A+不是型号；无并行Agent。需求v1.4、架构v1.74、执行动态v3.02、task_model V4.0/AGENTS CHG-0003；补读本轮卡面、scope/permit/input-manifest、129适用结论和共享顶部，同窗未变公共执行/停止条款复用，公共/DocuS/原始需求只读。

129已独审采纳两函数增量及原前三项；本轮产品源码冻结，不修P3、不运行19/22/23或18/9，不重复全审。59项接收输入全部匹配，当前源码安装器29865字节/hash7cd62b4f3526510c6f38de2a033a01d6ae36bcd661e90dbaca6b551db8141ba8，测试35468字节/hash2357a7031d2da858224d75b56ee0173a3166b0ca68c6905994009b7e64e6b3c3未变。源码/SQL/manifest/角色/profile/业务/启动器/Compose/依赖锁均冻结，只有README和normal-install说明按实证最小更新；动态工程完成交主控核原件，不自签最终验收或阶段放行。

| 连续项目 | 当前事实 |
| --- | --- |
| 入口 | entry07主批+entry08有据续API，累计8/8。成功即停，无下一入口。 |
| source PG start | 原4，本轮+3（第5次verify/首API、第6/7次通过API对），累计7/7。 |
| interrupted PG start | 原1，本轮+1，累计2/3；唯一次注入已消费，剩start不授权重复注入。 |
| API start | 原0，本轮3/3；第1次辅助停止确认失败，第2/3次完整通过。固定18122，无端口轮换。 |
| PG持有 | 原34.1386296749115 + 新32.687373638153076 = 累计66.82600331306458/1800秒，均按start请求到stop确认；最多一PG。 |
| API持有 | 精确完整树退出时刻unknown；保守累计99.34058094024658/900秒，含首次失败的延迟停止确认上界。 |
| 工具wall | 精确unknown；工程原保守8400，本轮保守1500/恢复2400，累计9900/10800。包含准备、52.235+6.047秒等待、两入口、辅助修正、读写与保存，900保存/清场预留仍在管理，余量交回封存。 |
| 新工具可证下界 | 两不重叠真实控制器77.672与12.313秒合计89.985秒，其他筹备/保存不据此写成0；父子不重复累加。 |
| 容量/压力 | entry07采样39次最低378.40234375MiB，entry08采样6次最低834.44140625MiB，均未触发两次<256门；新增启动门保持>=512。 |
| 新资源/费用 | 新create/卷/网络0，原2/2/2保留；真实provider/费用0。129审计900/2400及封存余1500未挪用。 |
| 日历 | 签发2026-10-23 10:40:54.041088+08，原截止16:14:03.021104+08不延长；两入口10:45:57—10:47:14及10:51:48—10:52:00+08已结束。 |

首次API父返回约4.012秒时树尚未全部确认，不能漏计到只有父wait。当前连续账将其保守持有延至api-stop-diagnosis.json写入时点10:48:42.128905+08，首周期上界92.53031301498413秒；另两个完整周期3.416531801223755和3.3937361240386963秒。原4.012418031692505秒仍在原诊断及当前parent_exit_observation_seconds保留，真实子进程最终退出精确秒数不编造。[持有纠正](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/holding-adjustment.json)。旧127/128首轮/续作01、125/126/120/117失败/unknown均连续保留，不因换续作清零。

source仍CID db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d，127.0.0.1:55482，库retrolume_q_first_normal/OID16384/systemid7699647093882925094；interrupted仍CID549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8，127.0.0.1:55483，库retrolume_install_interrupted/OID16384/systemid7699647123872251942。CPU1/512MiB/pids128/restart=no/loopback/无host bind、缓存固定image Id sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f及PG17/vector0.8.6不变，未拉取/构建。

四根/originals、SID/device/file-id、卷/网络创建身份及三UUID全沿原checkpoint复核，不新建替代根或重置身份/密码。实际API用户仅retrolume_normal_app；快照/maintenance按原native结构各司用途，安装管理员环境不交应用。DPAPI秘密仅当前用户内存解密复用，证据不含密文/明文/DSN/完整Env/展开Compose，日志先脱敏后保存。

最终[post-snapshot](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/post-snapshot.json)核两个精确CID均Running=false/Pid=0、卷/网络/根及成功/部分库保留、PG和固定API端口无LISTEN。[自有进程最终核验](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/final-api-process-check.json)按18个已记录PID/birth核原实体不存在或已退出，不碰其他进程；两个通过周期已有原生退出0/树结束/端口释放原件。没有prune、down-v、DROP DATABASE、删卷/网络、递归清理、旧scratch/私配读取或全局环境/驱动改写。

## 交付边界

当前六项功能证据齐全，保留前三项及代码门的129独审结论，本轮只补动态事实；无新产品代码或安全模型变化，不提出新一轮全量测试/审计、P3清单或设计卡。两份用户说明仅同步已验证事实，[说明diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/changes.diff)和pre/post可核。原25623字节历史后缀及此前所有成果完整保留，正式DocuS/编号/最终验收由主控维护。

Q维持FROZEN，T0/72h空；provider/Embedding/计量/付费、索引/查询/生成、三活动/grant/QAuthority.bind/InstanceBinding、浏览器/renderer/预览/业务Job、依赖安装和Git写均0（限本卡动作，不冒称整机零流量）。原100/25及分额、账号/token/模板/容量外部门不变；不宣STEP、Q、M1或NO3/发布已通过。没有新的必要用户手工操作。

---

以下为续作01及首轮完整历史原文（25623字节，SHA256=472882152a5283bf0ff36d72ff1b73b7a9822e1cfff4dda5c0afa942950efc55）：

'''
target=R/'DocuN/results/TASK-128-result.md';assert target.read_bytes()==old
with target.open('wb') as out:out.write(body.encode('utf-8')+old)
assert target.read_bytes().endswith(old)
print(json.dumps({'saved':str(target),'bytes':target.stat().st_size,'old_suffix_bytes':len(old),'six_checks_passed':True}))
