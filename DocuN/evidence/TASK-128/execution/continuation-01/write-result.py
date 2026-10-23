import hashlib,json
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[4]
old=(E/'pre/DocuN/results/TASK-128-result.md').read_bytes()
assert len(old)==13923 and hashlib.sha256(old).hexdigest()=='fd9445acbca5abe2d3b1daa8bfb8f0793d6be24ba9e70a08b7628de09b4e0558'
state=json.loads((E/'checkpoint.json').read_bytes())
receipt=Path(state['slots']['source']['successful_receipt']).read_bytes()
assert receipt==(E/'entry-06/source-success-receipt.jsonl').read_bytes()
assert hashlib.sha256(receipt).hexdigest()==state['slots']['source']['successful_receipt_sha256']
rows=[json.loads(line) for line in receipt.splitlines()]
assert len(rows)==37 and rows[-1]['event']=='complete'
assert len([r for r in rows if r['event']=='confirmed'])==17
roles=json.loads((E/'entry-06/check3.json').read_bytes())
assert all(r['actual_login']['current_user']==r['actual_login']['session_user'] for r in roles)
pack={'receipt_private_matches_evidence':True,'receipt_sha256':hashlib.sha256(receipt).hexdigest(),'receipt_lines':len(rows),'confirmed':17,'actual_logins':[r['actual_login'] for r in roles],'actual_permission_refusals':sum(len(r['actual_refusals']) for r in roles)}
(E/'receipt-role-crosscheck.json').write_text(json.dumps(pack,indent=2),encoding='utf-8')
body='''# TASK-128 / R-122 续作01 当前工程回传

地址格式修复及三项定向方法通过，前三项真实验收已通过；API和独立中断槽位均被可用内存低于512MiB的启动门拦截，六项整体未完成，成功安装及全部资源/证据已保留，两库已精确停止。

本置顶为当前结果；下方首轮13923字节完整原文保留为历史后缀，不把旧失败改写为通过，也不以工程自查代签集中独审或主控验收。

## 当前变化及实证

仅在observe_identity解析server_address时用ip_interface兼容裸IPv4/IPv6与完整主机掩码/32、/128，并要求prefixlen等于该地址max_prefixlen；短前缀/非法地址仍拒绝。IDENTITY_QUERY、其他身份等式/类型/端口限制及事务未改，返回值保持真实172.19.0.2/32，不替换为裸地址或客户端loopback。保留首轮connect对PGSERVICE/PGSERVICEFILE存在即拒绝、显式host/hostaddr=127.0.0.1、精确目标/凭据和options的修复，不再复现坏service连接。

新增test23涵盖实际IPv4 /32、bare IPv4、bare IPv6及IPv6 /128；非法/短前缀拒绝；在合法/32输入下错误OID/systemid/installer/session login、superuser、版本、编码、端口仍拒绝，正例观察值不改。与受影响19/22一次集中运行，3/3通过，0.549秒；运行前后实际安装器/测试hash相同，记录器不证明PG/ACL。[名单/时间/字节](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/targeted-tests.json)。旧18/9方法及未变SQL/角色/目录独审不重跑。

实际source正确preflight已通过，包含原空库/排他性/版本/身份门，真实服务端文本原样保留。[正确空库预检](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/correct-empty-preflight.json)。随后原SQL001—015、normal控制行与登录创建全部真实提交、原schema_checks/q_roles通过，完整成功收据37行/17阶段submitted+confirmed/complete；观察到013后控制行由空到normal/R01，014/R02、015/R03。未改原SQL、guard、事务或用Recorder替代真实驱动。[完整安装](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/check2.json)、[原37行收据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/source-success-receipt.jsonl)、[实际提交trace](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/source-success-trace.jsonl)。私有原件与证据副本原字节/hash一致，SHA256=a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06，后续禁止重放成功安装。

## 六项状态

| 项 | 实际状态 | 原件与边界 |
| --- | --- | --- |
| 1 四类空库拒绝 | 通过 | 错误OID/systemid分别target_identity_mismatch，非空表target_not_empty_or_exclusive，职责组碰撞global_role_collision；各真实连接、安装器写请求0，不是统一other_clients。仅两精确临时对象事先证不存在、记OID后创建，按同名同OID撤销，源恢复已核空态才安装。[四反例](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/check1.json)，相邻独立trace/收据保存全部请求和拒绝。 |
| 2 完整真实安装 | 通过 | 17真实阶段、37行成功收据及R01/R02/R03和原后置核验均成立。源dataset/instance/originals_root三UUID沿用，normal控制行真实写入，不产生Q身份。 |
| 3 业务/快照登录权限 | 通过 | 实际retrolume_normal_app、retrolume_normal_snapshot分别认证，current_user=session_user，原ROLE_CAPABILITIES/MEMBERSHIPS闭包检查；读取实际最小控制视图。维护秘密列不可读、快照无业务写；业务SET owner及快照SET owner/业务、读秘密/INSERT反例共5次均42501并ROLLBACK。原角色管理标志、owner、SET/INHERIT/ADMIN实际事实在[角色原件](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/check3.json)。无持久业务记录夹具。 |
| 4 两次原生API跨PG重开 | 未执行 | api_once(1)在实际Popen前触发startup_memory_below512，API累计0，未选API端口、未建立ControlHub/正常源运行绑定。首次API尚无，不能用PG一次安装启停冒充两个API周期；C未执行。 |
| 5 独立002真实提交后未知 | 未执行 | 停source后独立尝试进入check5，但start_pg的512门也拒绝；interrupted未启动、未apply、注入次数0，旧失败收据仍不是002提交未知。 |
| 6 完整成功收据verify | 未执行 | 已有真实完整源收据，但本轮没有运行verify CLI或坏绑定拒绝；apply内部后置READ ONLY核验不冒充独立verify。 |

前三项为新实际通过，不从127/128旧六项无PASS记录中继承。旧空service根因、真实同秘密连接与19/22历史证据按范围复用。没有全项目、阶段、发布或Q通过声明。

## 真实容量停止，不使用条件备用

entry06正确执行A前半段至权限通过。首次API在startup guard实时可用内存<512MiB时拒绝，尚未启动进程、选端口或消耗API次数。控制器停source，再安排独立B；interrupted的启动前guard同样拒绝，未消耗其启动次数。不是产品API启动失败，也不虚称已试出正常源不可用。

内存约2秒采样8次，从1297.87890625到最低105.33203125MiB，低于256仅一次，下一次336.08203125，未达到连续两次<256的运行压力退出门；但新增启动的512门确实两次不满足。没有降低门、改用2GiB、要求用户反复释放内存、启动浏览器/renderer或结束他人程序。实际拒绝和采样均保留。[失败账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/failure-ledger.json)、[memory.jsonl](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/memory.jsonl)。

本轮没有普通夹具缺陷；entry07只在“明确普通夹具缺陷”等条件成立时可用，容量门不满足该条件，因此未启备用。source已累计4/5且本轮首次API尚未开始，余一次source启动不足以再做“首API→停源→B→同源重开第二API/verify”；不消耗最后一次启动制造不能收口的半段。停在实际容量与生命周期可行性门，不重放已完成安装/前三项，也不新建替代槽位。后续由主控处理容量可用时的明确续作范围、条件入口及source额外一次启停余量，不能凭本文件自动恢复；当前不向用户索取密钥/截图/手工清库或恢复Docker。

## 身份、冻结与停止

续作01按用户人工转卡接收，TASK128/R122、A+工程安排；实际客户端Codex桌面/Codex GPT-6家族，具体后端变体不可读取，不以A+冒型号。无并行Agent或新独审。需求v1.4、架构v1.72、执行动态v3.00、task_model V4.0/CHG-0003；同窗未变规则/原接口复用，补读新卡置顶、scope/permit/input-manifest、work-decision和共享顶部。公共库/DocuS/原始需求只读，阶段关联STEP018/019/020等保持，工程不代签其验收。

73项接收输入pre全部匹配；最终只变允许的安装器、测试、README、安装说明四文件，原SQL/manifest/roles/profile/业务/原生启动器/Compose/依赖锁未动，七规则hash一致。final-run-inputs以原73冻结指纹为基础，只允许本轮安装器/测试已明确两变化绑定最终测试字节，未把全输入无约束地改成“当前即基线”。entry06/as-run保留三辅助实际副本及输入；完整pre/post/hash和[changes.diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/changes.diff)供集中增量独审。README/说明只更新实际前三项通过和其余未验证，不再保留已修缺陷为当前结论。

source CID=db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d，127.0.0.1:55482，库retrolume_q_first_normal/OID16384/systemid7699647093882925094；interrupted CID=549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8，127.0.0.1:55483，原systemid7699647123872251942/OID16384，本轮未重新连接。镜像Id仍sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，PG170011/vector默认0.8.6，CPU1/512MiB/pids128/restart=no/loopback/无host bind。

原专有卷/bridge Id、创建时刻/标签、四根和originals的SID/device/file-id在复用前与最终逐项核同。三UUID沿用：dataset6f283260-33d0-4465-bbcd-b29e50f57aab、instance4236ae70-6718-4141-9b6d-694c95b0fae4、originals_rootacde4327-a170-4a8d-97e9-1bcafbf28efc；实际控制行normal/R03，尚无ControlHub控制身份。秘密仅复用现有DPAPI内存解密，没有生成新密码、ALTER旧角色或复制密文/DSN/Env到证据。新正常登录由原正式login_roles阶段首次创建；没有把bootstrap交应用。

最终[post-snapshot.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/post-snapshot.json)核两CID Running=false/Pid=0，卷/网络/根及完整成功库保留，所选PG/API候选无LISTEN。API树未创建，未宣称关闭过原生API。没有prune、down-v、DROP DATABASE、删卷/网络、递归清理旧scratch、换槽位或重置账号。原127和128首轮原件/检查点/许可未改。

## 连续账与交接

| 项 | 当前连续值 |
| --- | --- |
| 工具wall | 精确unknown；127保守4800、128首轮2400，本轮保守1200/恢复3600，连续保守8400/10800。包含全部筹备/定向测试/真实段/文档/核验保存；900保存/清场储备在本轮管理，未用余量交回封存。 |
| 可证不重叠下界 | 实际controller14.875秒及定向测试工具1.9951606秒，至少16.87秒；其余筹备/工具读写不写成0，不用测试秒数冒全部投入。父子计时不重复相加。 |
| 入口 | entry06新增1，累计6/前向7；entry07条件不成立未用。顶层exit0代表收集实际失败并收尾，不能当六项绿。 |
| PG start | source累计4/5（本轮+1），interrupted累计1/2（本轮+0）。两次512门拒绝未执行启动。 |
| PG持有 | 原21.66196846961975 + 本轮12.476661205291748 = 累计34.1386296749115/1800秒；按start请求至stop确认。 |
| 本轮PG区间 | 2026-10-23 09:39:57.935398—09:40:10.412059+08，未同时运行两PG。 |
| API | start0/3、持有0/900，端口未选定。 |
| 新资源/费用 | 本轮create/卷/网络0，仍原2/2/2保留；provider/费用0。 |
| 日历 | 签发09:33:10.819748+08，截止保持16:14:03.021104+08，无跨时窗恢复或新24h。 |

原125/126unknown与封存批次、120根64/64及149失败、117旧81等历史账不清零。原128首轮13923字节完整保留在下方，旧缺陷/失败仍可核；当前以上述置顶实证为准。

稳定候选现在包括connect服务隔离及observe_identity主机格式两处产品增量，供主控集中独立审其直接影响及真实原件，未变SQL/角色/目录不重开全审；工程只自查，不签审计关闭。主控需同步前三项实证、容量阻断、成功收据/不可重放约束及连续账，正式DocuS未由本窗口维护。

Q继续FROZEN，T0/72h空；本卡无provider/Embedding/计量/付费、索引/查询/生成、三活动、grant/QAuthority.bind/InstanceBinding、浏览器/预览/业务Job或Git写。原100/25及分额、账号/token/模板/容量外部门未变，不放行Q、STEP、M1、项目或发布。

---

以下为首轮完整原文（13923字节，SHA256=fd9445acbca5abe2d3b1daa8bfb8f0793d6be24ba9e70a08b7628de09b4e0558）：

'''
target=R/'DocuN/results/TASK-128-result.md'
assert target.read_bytes()==old
raw=body.encode('utf-8')+old
with target.open('wb') as out:out.write(raw)
assert target.read_bytes().endswith(old)
print(json.dumps({'saved':str(target),'bytes':len(raw),'historical_suffix_bytes':len(old),'receipt_crosschecked':True}))
