"""接收独审四P1、维护共享账并保存原工程合并修复卡；不执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
CARD=ROOT/'DocuN/tasks/TASK-114.md'
WORK114=ROOT/'DocuN/results/TASK-114-work-decision.md'
WORK115=ROOT/'DocuN/results/TASK-115-work-decision.md'
ARCH=ROOT/'DocuS/架构动态文档.MD'
STATE=ROOT/'DocuS/执行动态文档.MD'
CHANGES=ROOT/'DocuS/文档变更记录.MD'
AUDIT=ROOT/'DocuN/evidence/TASK-115/audit'


def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def info(path):
    raw=path.read_bytes()
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


at=datetime.now(timezone(timedelta(hours=8))).isoformat()
received=load(ROOT/'DocuN/evidence/TASK-115/orchestration-receipt-20261013/received.json')
result115=ROOT/'DocuN/results/TASK-115-result.md'
assert info(result115)=={k:received['report'][k] for k in ('bytes','sha256')}
frozen=load(ROOT/'DocuN/evidence/TASK-114/implementation/continuation-01/final/manifest.json')
for row in frozen:
    if row['change']=='deleted_build_output':assert not (ROOT/row['path']).exists()
    else:assert info(ROOT/row['path'])=={k:row[k] for k in ('bytes','sha256')},row['path']
old={path:path.read_bytes() for path in (CARD,WORK114,WORK115,ARCH,STATE,CHANGES)}
assert '文档v1.27' in old[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.51' in old[STATE].decode('utf-8-sig').splitlines()[2]
assert 'CHG-1335' in old[CHANGES].decode('utf-8-sig') and 'CHG-1336' not in old[CHANGES].decode('utf-8-sig')
assert not re.search(r'DEF-03[4-7]',old[STATE].decode('utf-8-sig'))
backup=OUT/'before-documents';backup.mkdir(exist_ok=False)
for path,raw in old.items():
    target=backup/path.name
    assert not target.exists()
    target.write_bytes(raw)
result114=ROOT/'DocuN/results/TASK-114-result.md'
result114_before=info(result114)
assert result114_before=={'bytes':53842,'sha256':'c0f970d48ac57d1081e79afa90bcab5822d4c6058e60ed7f9fb6f9b0cd770e2e'}
control=ROOT/'DocuN/evidence/TASK-114/implementation/control'
control_before={name:info(control/name) for name in ('receipt.json','events.jsonl')}

permit={
 'TASK':'TASK-114','R':'R-108','continuation':'02','permit':'TASK-114-STEP017-C02-20261013','created_at':at,'dispatch_confirmed':False,'execution_started':False,
 'authorization':'用户已采用STEP017-P1并要求继续原任务；本轮修复原Must四P1及明确必要补证，不重批方案',
 'defects':{'DEF-034':'115/F01取消与不可逆成功准入','DEF-035':'115/F02完整消费链同一绝对截止','DEF-036':'115/F03晚到caps回退当前身份','DEF-037':'115/F04删除依赖记忆正文投影'},
 'frozen_old_state':'旧source frozen、selected target07 generation1、旧八logical slot占用、旧六容器Stopped，原控制/数据/包不写或启动',
 'new_activity_seconds':21600,'calendar_seconds':172800,'cleanup_activity_reserved_seconds':1200,
 'task114_old_counts':{'roots':18,'pg_create':6,'pg_success':6,'pg_start':27,'windows':11,'api':5,'browser':3,'build':3,'holding_seconds':377.280,'offline_seconds':51.238,'c01_active_final_seconds':9739.953,'old_calendar_seconds':55525.796,'old_net_active':'unknown'},
 'task115_usage_preserved':load(AUDIT/'delivery.json')['new_counts'],
 'new_cumulative_task114_limits':{'real_roots':24,'pg_create':12,'pg_success':9,'pg_start':37,'api_start':11,'browser_start':9,'frontend_build':6,'windows_start':12,'holding_seconds':10800,'holding_business_seconds':9600,'cleanup_reserved_seconds':1200,'offline_seconds':7200,'provider_calls':0,'fees':0},
 'current_c02_remaining':{'real_roots':6,'pg_create':6,'pg_success':3,'pg_start':10,'api_start':6,'browser_start':6,'build':3,'holding_seconds':10422.720,'holding_business_seconds':9222.720,'offline_seconds':7148.762,'new_windows_work':0,'preview':0},
 'image':'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
 'profile':'TASK-114-C02-PG17','maximum_running_containers':2,
 'new_objects':[
  {'slot':'source','name':'retrolume-task-114-c02-source','volume':'retrolume-task-114-c02-source-data','host_ip':'127.0.0.1','port':15452,'database':'retrolume_task114_c02_source'},
  {'slot':'target01','name':'retrolume-task-114-c02-target01','volume':'retrolume-task-114-c02-target01-data','host_ip':'127.0.0.1','port':15453,'database':'retrolume_task114_c02_target'},
  {'slot':'target02','name':'retrolume-task-114-c02-target02','volume':'retrolume-task-114-c02-target02-data','host_ip':'127.0.0.1','port':15454,'database':'retrolume_task114_c02_target'}],
 'object_limits':{'cpus':1,'memory_bytes':536870912,'pids':128,'restart':'no','host_binds':0,'privileged':False,'docker_socket':False},
 'api_port':18114,'vite_port':15114,
 'new_business_root':str(ROOT/'DocuN/evidence/TASK-114/implementation/continuation-02/synthetic'),
 'same_execution_budget_control':str(control),'old_product_control_unchanged':True,
 'observation':{'at':'2026-10-13T16:39:39.6478345+08:00','source_and_selected_target07_running':False,'source_and_selected_target07_pid':0,'new_namespace':[],'planned_port_states':[],'available_memory_gib':1.25,'gate_gib':2,'real_start_requires_recheck':True,'auto_review':'已允许精确只读元数据，无拒绝'},
 'independent_review':'修后原TASK115窗口review-01只核四P1、必要余门和实际影响，不提前发卡/不重审G11',
 'persistent_model_changes':'私有job协议/字段细化允许；不新业务表列/服务，013仅已有最小读取权限或身份必要定向修正',
}
save('continuation-permit.json',permit)

work114_prefix=f'''# TASK114续作02／四项P1合并修复许可（当前有效）

{at}，Codex编排Agent。独审115/R109报告37767字节/7d34ec7e7f433effe3bf51367c68229a566dc525361a30c4b2c496702f4ca67a及358审计原件/216冻结current/七规则实核。审计交付接受，产品不通过；原合法主要链保留，DEF034=F01取消、DEF035=F02完整deadline、DEF036=F03晚到身份、DEF037=F04依赖正文四P1开放。前三为明确受控真实层反例，F04为合法状态代码反例，两60秒夹具超时未知不称PG或产品延迟。

用户已采用完整包并要求继续，不重复批方案。TASK114/R108原A+窗口续作02，一张完整四修/实际影响/115明确余门补证卡；旧源码pre和所有反例保留。私有job状态/准入/唯一D可细化，不新增业务表/列、服务或旧执行权；source old frozen/target07 generation1/原所有包和控制全不写，不借旧slot。正向验证用新C02 source及两独立target，固定15452—15454及原本地PG17/1CPU512MiBpids128，旧原物理成功6加3到原9上限，create总12不加。

前向许可TASK-114-STEP017-C02-20261013，活动21600/48h日历/最后1200清场，旧锚点和C01最终活动9739.953/旧55525.796与unknown保历史。原root18追加6至24；PG start32加5至37（已27），API8加3至11（已5），Browser6加3至9（已3）；成功9/create12/build6（已3）/offline7200（已51.238）/hold10800（已377.280）不加，Windows/preview本轮无新真实消费，费用/provider0。115的3root/14.874hold/125.610offline等单独保留不挪回开发账。

16:39:39主控只读实核原source/07Stopped，新names/端口无占，RAM1.25GiB，先源码和离线，真实开跑前达原2GiB门，不停用户服务或盲占slot。执行controller按C02追加唯一旧control账，原产品ControlHub完全独立新业务根，不能替换旧received_monotonic锚点/删事件。源source_delete/capture/upload/restore/activate不可逆点须共享正确短CAS；源码限时和当前资格不因前向工时暂停改变。

修后稳定回原115窗口独立review-01，仅四P1/余证和实际传播，主控另给复核许可，不预派TASK116。所有共享文档/DEF最后关闭主控负责；审计已done未产品通过、原G11/UNKNOWN/费用/全部Must不外推。

## 以下为旧工程许可历史原字节

'''
WORK114.write_bytes(work114_prefix.replace('\n','\r\n').encode('utf-8')+old[WORK114])
work115_prefix=f'''# TASK115审计交付已回收，产品不通过，增量复核待修后

{at}，Codex编排Agent。报告37767字节/7d34ec7e…ca67a、358审计原件与216冻结源码/4bundle及七规则匹配，独立性披露主控摘要意外接触/无实现聊天和未读114自评接受；明确找出四P1，独审成果验收通过，不等工程或STEP017通过。

F01/F02/F03分别真实控制/文件或上传收尾、受控deadline边界、真实Browser路由反序；F04直接源码和合法依赖输入成立，两个异步方法超时根因unknown、动态未成。报告合并最小修复和必要余门作为原114 C02执行合同依据，不要求全仓重测，不用时间和原件偏差掩产品缺陷。

115新roots3/4、API3/3、Browser2/2、PG0、offline125.610、保守hold14.874、活动上界5490.683454与计时/根标签补账偏差全部保留，资源已结束。旧许可任何余额不自动续；待114真实修后主控给本原独立窗口review-01，只复核问题/实际影响和新证据，不自行回产品修改或占新TASK。原结果/原反例/FAIL原字节不动。

## 以下为原集中独审许可历史原字节

'''
WORK115.write_bytes(work115_prefix.replace('\n','\r\n').encode('utf-8')+old[WORK115])

arch_prefix=f'''# 架构动态文档

文档v1.28，2026-10-13，Asia/Shanghai。需求v1.2、执行动态v2.52、task_model/07；以下v1.27历史原字节保留。

## STEP017独审四P1开放，主要实证保留，闭环暂不通过

{at}。TASK115集中三轴审计已返回，候选不通过。DEF034：cancel把请求当已取消，publish/upload/verify可读latestrev覆盖成功；source删除/激活存在同机制传播。DEF035：operation_seconds未覆盖capture后的ZIP/校验/发布及恢复allocate/init/seal，子started不能替完整D。DEF036：capabilities反序回包可回退全局dataset/instance/generation，整个/api/data免namespace过宽。DEF037：active memory只查自身状态/body/墓碑，遗漏source/event/upstream资格，已删依赖正文仍present。

四修目标仍已采用合同：短CAS取消请求/安全确认/不可逆成功准入、整个消费链唯一受信deadline及未知事实、当前上下文新鲜性/生命周期/稳定Hub与数据视图分工、相同只读快照下完整正文依赖资格与overlay。不得持journal锁等IO，不把已发布/墓碑/selector事实抹除、不减旧数据/预算，不用改memory头或purge状态修DTO。

正常独立恢复/94行4原件31域/加载guard/两FK、同T/两序/迟到COMMIT、原SUP/四账/冻结选择/正常TCP和Browser原证据按实际不变机制继承；它们不关闭取消/超时/晚到/依赖正文门。C02新独立修复测试域不写原frozen源或旧selector，旧八slot保留，不新增业务模型/服务或恢复旧工作权；必要原十三版只读ACL/身份定向变化须实证。

修后原115增量复核才可能建议有限STEP017关闭；永久只读不代完整NFR005持续执行恢复，原G11关闭/25/UNKNOWN/费用和STEP018—020全部Must保留。用户库/真实资料迁移删改切换/模型费用不许可。

## 以下为v1.27及更早历史

'''
ARCH.write_bytes(arch_prefix.replace('\n','\r\n').encode('utf-8')+old[ARCH])
CARD.write_bytes((OUT/'effective-contract.md').read_bytes())

state_prefix=f'''# 执行动态文档

文档v2.52，2026-10-13，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.28、task_model/07。以下v2.51历史原字节保留。

## TASK115审计已回，四P1阻断；TASK114 C02合并修复待人工转交

{at}。审计115/R109实际已接收/执行/返回，交付报告37767字节/7d34ec7e7f433effe3bf51367c68229a566dc525361a30c4b2c496702f4ca67a，358审计原件/216当前frozen+1移除和七规则匹配。独立性带意外主控摘要披露接受，未参与工程/未读实现聊天和114自评；审计交付验收通过，产品代码不通过/证据部分/控制部分合规，STEP017暂不关闭。

新DEF034/P1（F01）取消确认可被成功覆盖，DEF035/P1（F02）后段总deadline漏门，DEF036/P1（F03）capabilities迟到回退身份，DEF037/P1（F04）已删依赖记忆正文仍可present。前三有明确分层反例；F04为源码/合法状态反例，两个60秒异步诊断未得结果、原因unknown，不称真实PG或产品超时。四问题全部开放，修完候选由原115增量独立复核后主控裁定，原已经充分主要方法不作废或整仓重审。

115实际计root3/API3/Browser2、PG/Native/preview/build/provider/费用0、offline125.610、保守hold14.874、活动上界5490.683454/余16109.316546。首工具UTC/mono缺精确配对、保守早起点、reader根误标补扣、夹具FAIL与两个超时、原firstdist/PGargv等限制保留；全部消费者ended，旧六容器Stopped，原控制/资料/源码未修改。旧审计余额不自动复活。

原114 root18/18/PG create-success6/start27/Windows11/API5/Browser3/build3、offline51.238/hold377.280、C01最终活动9739.953（9185.438为中间封存）、旧55525.796/净活动unknown和raw7→保守10+8全部保历史。source frozen、target07 selected generation1、所有old slot占，C02不启动写这些旧对象/控制。

用户已采用技术包并继续指示，前向修复许可TASK-114-STEP017-C02-20261013保持同TASK114/R108和原A+工程窗。完整卡DocuN/tasks/TASK-114.md已保存复读待人工转交，旧卡原字节保存本轮before-documents；C02真实派发/接收/新量0。新增21600活动/48h日历/最后1200清场，原root18加6至24，start32加5至37、API8加3至11、Browser6加3至9，其余create12/成功9/build6/offline7200/hold10800/业务门9600不扩。所有新预算按原唯一control追加，原锚点/旧事件不清，不借115余量。

精确C02新source+target01/02共最多3对象，固定profile TASK-114-C02-PG17、本地cf134a76镜像/1CPU512MiBpids128、新名字卷和15452—15454，各新合法ID/数据/独立业务control根；原实体6加3正好原物理成功9，不能failed复用/改名。原API18114、Browser本轮独立profile；Native/preview/真实provider/public/费用0。16:39:39实际新names/端口无占、原source/07Stopped，RAM1.25GiB，先代码/离线，启动时复核≥2GiB，不停用户服务/降门；主控只读升级由自动审查允许，无拒绝。

一张四修+115最小剩余门定向验证卡，旧F04停止路线不机械第三跑，使用明确新PG/TCP/受信loop；F01各成功点短CAS，F02完整D，F03最终bundle新鲜性，F04完整依赖mask不改历史头/purge。正常链/RootLease/原SUP/G11不变依原件继承。修后原115窗口review-01另给许可，只问题和传播，不自行全审；TASK116未占号。

主控此轮文件/原件/元数据核证及共享维护，产品运行0。核证/许可/旧文档/card/输入和窗口在TASK115/orchestration-receipt-20261013与TASK114/orchestration-repair-c02-20261013。原始/最终需求/公共库/旧结果/所有FAIL不写，G11/25/UNKNOWN/R60/count1/13元/626.566和永久只读限定不外推完整恢复或项目。CHG1336—1344，下一1345。

## 以下为v2.51及更早历史

'''
STATE.write_bytes(state_prefix.replace('\n','\r\n').encode('utf-8')+old[STATE])
save('window-assignment.json',{'TASK':'TASK-114','R':'R-108','continuation':'02','execution':'A+','window':'原TASK114工程窗口，不能使用原115审计窗','dispatch_confirmed':False,'execution_started':False,'fallback':'原窗确实不可用才同等A+新窗恢复','parallel':False,'subagent':False,'independent_review':'原TASK115窗口修后review-01尚未派发'})
context=[ROOT/'AGENTS.md',WORK114,WORK115,ARCH,STATE,result115,ROOT/'DocuN/evidence/TASK-113/design/revision-01/current-contract.md']
save('input-manifest.json',{'at':at,'TASK':'TASK-114','R':'R-108','continuation':'02','context':[{'path':str(p),**info(p)} for p in context],'product_pre':frozen,'old_task114_report':{'path':str(result114),**result114_before},'old_control':control_before,'audit_report_and_evidence_verified':str(ROOT/'DocuN/evidence/TASK-115/orchestration-receipt-20261013/received.json'),'old_state_and_roles_not_execution_permission':True})
entries=[
 (1336,'DocuN/evidence/TASK-115/orchestration-receipt-20261013/received.json','报告及358审计原件/冻结源码/反例分层核证，审计交付接受产品不通过。'),
 (1337,'DocuN/results/TASK-115-work-decision.md','原审计已交付、控制与独立性披露保留、四P1修后增量复核待。'),
 (1338,'DocuN/results/TASK-114-work-decision.md','DEF034—037合并修复C02、明牌前向额度和新测试域，不重批技术。'),
 (1339,'DocuN/evidence/TASK-114/orchestration-repair-c02-20261013/effective-contract.md；DocuN/tasks/TASK-114.md','完整四P1修复/定向余证卡，旧卡原字节保留，待人工转交。'),
 (1340,'DocuN/evidence/TASK-114/orchestration-repair-c02-20261013/continuation-permit.json；input-manifest.json；window-assignment.json','新精确源+两目标/累计根和余量/源冻结保护/原A+工程窗，旧预算不清零。'),
 (1341,'DocuS/架构动态文档.MD','v1.28四确定P1及原合同正确修复目标，主要实证有效、闭环不通过。'),
 (1342,'DocuS/执行动态文档.MD','v2.52唯一实际账：审计已回/产品四DEF开放/C02待派及真实资源门。'),
 (1343,'DocuN/evidence/TASK-114/orchestration-repair-c02-20261013/before-documents/TASK-114.md','C01完整旧任务卡原字节保留，历史停止许可不恢复。'),
 (1344,'DocuN/evidence/TASK-114/orchestration-repair-c02-20261013/delivery-proof.json','完整卡/许可/预算/报告源码旧账与共享历史/CHG保存复读一致性。'),
]
addition=''.join(f'\r\n- CHG-{n}，{at}，Codex编排Agent，{p}。{why}\r\n' for n,p,why in entries)
CHANGES.write_bytes(old[CHANGES]+addition.encode('utf-8'))
for p in (WORK114,WORK115,ARCH,STATE):assert p.read_bytes().endswith(old[p])
assert CHANGES.read_bytes().startswith(old[CHANGES])
assert info(result114)==result114_before and info(result115)=={k:received['report'][k] for k in ('bytes','sha256')}
for row in frozen:
    if row['change']!='deleted_build_output':assert info(ROOT/row['path'])=={k:row[k] for k in ('bytes','sha256')},row['path']
for name,expected in control_before.items():assert info(control/name)==expected
text=CARD.read_text(encoding='utf-8-sig')
assert len(re.findall(r'^## ',text,re.MULTILINE))==9
assert '*' not in text and '|' not in text
assert not re.search(r'〈[^〉]+〉|<[^>]+>',text)
assert CARD.read_bytes()==(OUT/'effective-contract.md').read_bytes()
assert permit['new_cumulative_task114_limits']['pg_success']-permit['task114_old_counts']['pg_success']==len(permit['new_objects'])
assert not (ROOT/'DocuN/tasks/TASK-116.md').exists()
for n,_,_ in entries:assert CHANGES.read_text(encoding='utf-8-sig').count(f'CHG-{n}，')==1
save('delivery-proof.json',{'at':at,'TASK':'TASK-114','R':'R-108','continuation':'02','task':{'path':str(CARD),**info(CARD)},'status':'完整卡已保存复读待人工转交，非已派发','current_product_and_old_reports_unchanged':True,'old_control_unchanged':True,'prior_shared_byte_exact':True,'four_defects_open':['DEF-034','DEF-035','DEF-036','DEF-037'],'audit_delivery_accepted_product_not_passed':True,'CHG':[1336,1344],'next_CHG':1345,'product_runs':0,'resources_started':0,'check':'一次完整合同/许可/预算/物理对象/状态版本/历史及源保护核对，非产品测试'})
print(json.dumps({'task':str(CARD),**info(CARD),'status':'待人工转交','execution':'A+原TASK114工程窗','architecture':'v1.28','state':'v2.52','CHG':[1336,1344],'four_defects_open':True,'product_runs':0,'old_products_and_reports_preserved':True},ensure_ascii=False))
