"""主控回收C01部分成果并发布独立审计/必要取证卡；不执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
CARD = ROOT / 'DocuN/tasks/TASK-115.md'
AUDIT_WORK = ROOT / 'DocuN/results/TASK-115-work-decision.md'
WORK114 = ROOT / 'DocuN/results/TASK-114-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'
RECEIVED = ROOT / 'DocuN/evidence/TASK-114/orchestration-receipt-c01-20261013/received.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def info(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


at = datetime.now(timezone(timedelta(hours=8))).isoformat()
received = load(RECEIVED)
result114 = Path(received['result']['path'])
assert info(result114) == {k: received['result'][k] for k in ('bytes','sha256')}
for row in received['current_and_saved_files']:
    assert info(ROOT / row['path']) == {k: row[k] for k in ('bytes','sha256')}, row['path']
assert not CARD.exists() and not AUDIT_WORK.exists() and not (ROOT / 'DocuN/results/TASK-115-result.md').exists()
old = {path: path.read_bytes() for path in (WORK114, ARCH, STATE, CHANGES)}
assert '文档v1.26' in old[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.50' in old[STATE].decode('utf-8-sig').splitlines()[2]
assert 'CHG-1325' in old[CHANGES].decode('utf-8-sig') and 'CHG-1326' not in old[CHANGES].decode('utf-8-sig')
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items():
    (backup / path.name).write_bytes(raw)
control = ROOT / 'DocuN/evidence/TASK-114/implementation/control'
control_before = {name: info(control / name) for name in ('receipt.json','events.jsonl')}

allocation = {
    'TASK':'TASK-115','R':'R-109','permit':'TASK-115-STEP017-AUDIT-20261013','at':at,
    'kind':'独立集中审计与必要余项验收取证，不修产品',
    'dispatch_confirmed':False,'execution_started':False,
    'window':'全新A+隔离会话，未参与113/114工程，不接收实现聊天/自评',
    'frozen_case':{'source_files':212,'bundle_files':4,'removed_build_output':1,'original_task114_roots':18,'task114_current_context':'source frozen，target07 selected generation1；原许可不恢复'},
    'audit_source':{'name':'retrolume-task-115-data-audit','volume':'retrolume-task-115-data-audit-data','port':15451,'host_ip':'127.0.0.1','database':'retrolume_task115_audit','login_prefix':'retrolume_task115_','image':'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f','cpu':1,'memory_bytes':536870912,'pids':128,'restart':'no','maximum_successful_objects':1},
    'readonly_target07':{'cid':'c4adab7d59fd43a399a2f5c0dd2ba40efdf7623a674342850eef9d931a8850f9','name':'retrolume-task-114-data-target07','volume':'retrolume-task-114-data-target07-data','port':55468,'image':'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f','job_label':'48d96040-e0f6-4b47-857f-8547c7eec141','profile_label':'TASK-114-PG17','scope':'真实readonly LOGIN读/拒写无持久变化；不解围/DDL/admin/loader/改变selector'},
    'api_port':18115,'maximum_running_containers':2,
    'private_test_roots':['source-root','backup-root','restore-root','control-root','readonly-control-copy','scratch','sentinel-root','browser-root'],
    'base_root':str(ROOT / 'DocuN/evidence/TASK-115/audit/synthetic'),
    'limits':{'active_work_seconds':21600,'calendar_seconds':172800,'real_roots':4,'audit_pg_create_attempts':2,'audit_pg_success':1,'audit_pg_start':3,'readonly_target07_start':2,'api_start':3,'browser_start':2,'real_holding_seconds':2400,'real_business_holding_seconds':2100,'cleanup_reserved_seconds':300,'offline_process_seconds':3600,'real_windows_work':0,'preview':0,'build':0,'model_provider':0,'fees':0,'public_network':0},
    'observations':{'at':'2026-10-13T13:53:20.8395642+08:00','audit_names_found':[],'new_port_states':[],'available_memory_gib':1.82,'memory_gate_gib':2,'must_recheck_before_real_start':True,'source_and_selected_target07':{'running':False,'pid':0},'default_sandbox_metadata_denied':'Docker/CIM access denied，非实际0内存','auto_review_read_only_upgrade':'两个确切对象/端口/内存只读核查已获自动审查允许，无拒绝'},
    'permissions':'只改本卡证据/结果及本卡新测试对象；当前产品/旧对象/控制源/旧账冻结',
    'normal_source_not_restoration_target':'新审计源用于权限/取消/包/并发测试，不宣跨集群恢复重验；完整恢复原件按字节继承',
}
save('resource-allocation.json',allocation)

work114_prefix=f'''# TASK114续作01回收与集中审计安排（当前有效）

{at}，Codex编排Agent。续作01结果53842字节/c0f970d48ac57d1081e79afa90bcab5822d4c6058e60ed7f9fb6f9b0cd770e2e已实际返回；原34931字节后缀保留。主控212源码/4bundle及原件副本、1移除输出、八批结果/13FAIL索引与七规则匹配；当前产品冻结，主体及主要真实恢复/删除/锁序/冻结选择/HTTP/Browser有实证，余异常分支未全闭。验收为部分候选，不能签完整V01—29或STEP017。

C01真实根18/18已停止，活动9185.438为封存观测、offline51.238/hold377.280、PG create/success6/start27、Windows11/API5/Browser3/build3保留；全部逻辑slot01—08占，不解围source frozen、不回退target07/generation1或重用failed目标。主控只读实核准确source和target07仍Stopped/Pid0；其他四对象的封存Stopped事实保留，不冒新的完整停止证明。

下一为TASK115/R109集中独立审计与必要余项补证，强档全新隔离窗、产品禁止修复。目标是读实际代码/原证据判断充分性、只补关闭所需权限/取消/半发布/迟到等具体门，不为每个未枚举变量组合重跑主要链；必要门不能降。允许一个独立新审计合成source和target07准确readonly短启，原source/失败/旧控制与budget只读冻结。新许可/资源/预算单列，旧18不清零。确定产品问题统一回主控，再合并交原工程修复，不自签或重派所有历史阶段。

原技术采用/永久只读范围/G11/UNKNOWN/费用/Must均不改，不新增用户库/真实数据/费用/原执行恢复许可；共享总账v2.51/架构v1.27记录实际候选，不采用实现者自评替独立判断。

## 以下为环境接续及原许可历史原字节

'''
WORK114.write_bytes(work114_prefix.replace('\n','\r\n').encode('utf-8')+old[WORK114])

work115=f'''# TASK115/R109集中独立审计与必要余项取证许可

{at}，Codex编排Agent。原STEP017-P1已采用且完整实施/验证/集中审计在授权路线；TASK114当前主要链真实原件充分、产品稳定冻结，尚有异常子分支缺口，现以前置满足的集中审查与关闭所需取证作为一个完整成果，占TASK115/R109。尚未实际派发/接收，不接管开发。

接收全新A+隔离审计窗，未参与113/114，不传工程完整聊天或实现结果自评；输入仅目标/采用合同/源码/真实差异和原始证据。审计三轴独立形成判定，非代码修复卡；确定缺陷给严重度/触发/最小修正/实际影响，主控统一交工程。必要补证允许自写本卡夹具、实际新合成PG/文件/HTTP/Browser，旧已验证不变主链直接继承，原明确Must子门不漏签。

精确新资源为一个retrolume-task-115-data-audit/同名-data卷/loopback15451，新库和LOGIN前缀task115，原固定PG17镜像/1CPU512MiBpids128；可准确短启只读target07 CID c4adab7d59fd43a399a2f5c0dd2ba40efdf7623a674342850eef9d931a8850f9/55468只用readonly，旧source/failed targets绝不启写，selector/原control不改。API18115/既有最终bundle和Browser，Native/preview/build/model/fee/public全0。真实根4、source create尝试2/成功1/start3、target07 start2、API3/Browser2，真实持有2400含最后300清场、offline3600/活动21600/接受后48h日历，旧114全部用量不借/清。详细见资源JSON和完整卡。

当前metadata只读源/target07 stopped、新名字/端口无占；RAM1.82GiB未满足2GiB，先充分代码/文件证据审查，真实开跑前再核，未满足不循环开对象/降门/停用户软件。当前sandbox默认Docker/CIM访问拒绝，经自动审查升级两个只读核查已允许，无审批拒绝，不把空结果转0GB。执行者需要平台权限时按精确低风险授权申请，不绕过审批，依赖被拒才给真实阻塞，其余读审持续完成。

产品/迁移/源码/原tests/旧账/控制/原结果/DocuS/公共库都冻结，只写本卡测试证据与结果，合成新库按真实冻结实现生成新ID/明确限额，不复制旧执行权。不为取证登录旧admin/loader、回源normal或回收slot。新审计卡是新独立验收单元和明确新许可，不恢复已结束C01；主要链候选未关闭，最终由主控据三轴与必要门裁定。

结果DocuN/results/TASK-115-result.md。共享版本为架构v1.27/执行v2.51，最终需求v1.2不变；原始需求只读。人工仅把当前完整卡转新A+审计窗，完成后带回结果路径，不重复批STEP017-P1。
'''
AUDIT_WORK.write_text(work115,encoding='utf-8')

register=f'''# 执行动态文档

文档v2.51，2026-10-13，Asia/Shanghai。需求v1.2、架构v1.27、task_model/07。

{at} TASK114 C01已返回部分候选，根18/18停线。TASK115/R109独立集中审计及必要取证已占号登记准备，完整卡待保存复读；未派发/运行。

## 以下为v2.50历史原字节

'''
STATE.write_bytes(register.replace('\n','\r\n').encode('utf-8')+old[STATE])
CARD.write_bytes((OUT/'effective-contract.md').read_bytes())
assert CARD.read_bytes()==(OUT/'effective-contract.md').read_bytes()

arch_prefix=f'''# 架构动态文档

文档v1.27，2026-10-13，Asia/Shanghai。需求v1.2、执行动态v2.51、task_model/07。以下v1.26历史原字节保留。

## STEP017主体和主要真实链已形成，必要异常门及集中独审待闭合

{at}。TASK114 C01候选完成独立target05全001—013/28域94行4原件/14组件与31域只读撤权、target07默认删除覆盖和target08快照时点对照、实际同T/两序/迟到COMMIT与共享删除、真实SUP有限工具收尾、source frozen/Hub选择target07代次1、最后TCP和Browser只读回查/草稿/刷新及目标不可用不回源。仅上述具体方法有真实原件，不称全部29项或父Must通过。

loading memory_body_guard的普通SELECT分支、failed目标部分初始化admin清理、精确约束/指纹、删除changed态/readonly错误码/目标不可用绑定及UI修正已形成最终字节；212源码/4bundle/原件匹配。013/角色/普通在线纪律、三域控制权威/快照与旧账保真必须集中独立再核，不能以成功加载遮蔽ACL/取消/半发布/迟到分支缺口。

原source持久frozen、selected target07/generation1、6容器封存Stopped，全部logical slot占用；原C01根18/18已停止，不以余时解围或重新建source。下一TASK115在隔离新窗一次审查和必要补证，独立新审计source与现有sealed目标readonly核查，产品和原控制/预算不改，验证/审计权限不等生产能力开放。

可携退出/隔离永久只读范围与原采用包维持，全部NFR005持续执行恢复、STEP018整链/Embedding/Compose/真实服务、019总验、020自用运维仍有门。G11有限关闭/旧UNKNOWN/预算/所有历史不改，原需求Must不减，用户库/真实删除覆盖切换/付费不许可。

## 以下为v1.26及更早历史

'''
ARCH.write_bytes(arch_prefix.replace('\n','\r\n').encode('utf-8')+old[ARCH])
state_prefix=f'''# 执行动态文档

文档v2.51，2026-10-13，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.27、task_model/07。以下v2.50历史原字节保留。

## TASK114 C01部分回收，TASK115集中独审与必要余项补证待转交

{at}。C01真实回传53842字节/c0f970d48ac57d1081e79afa90bcab5822d4c6058e60ed7f9fb6f9b0cd770e2e、原34931字节后缀完整；主控212当前源码/4bundle及封存原件、1移除输出、八结果/13FAIL索引和七规则相符。主要恢复/删除/准确竞态/只读选择/TCP/最后Browser有实证，原V01—29多数仍部分、取消/半发布/权限细分/迟到等必要异常待判定或补证。工程验收为部分稳定候选，TASK114/STEP017未关闭，未自签独审。

C01根18/18结束全部新真实消费；封存active9185.438/21600（最终保存另记）、offline51.238/7200、hold377.280/10800/业务门9600，PG create/success6/start27、Windows11/API5/Browser3/build3、Vite/preview0、model/fee0。原目录根错计7/前向保守10/八新根、55525.796旧日历/净活动unknown全部保留，不能把子余余额变旧许可。source=frozen、selected target07/generation1；6精确容器封存Stopped，主控另实核source/07当前Stopped/Pid0，未探SQL或复演业务。

下一TASK115/R109已先占号再保存完整卡复读，待人工转交：A+全新独立窗未参与113/114，无实现聊天/自评，无子Agent/并行，原114窗封存。把集中三轴审查与必要余项验收取证作为一个完整成果；严格继承已充分不变方法，不要求无界组合穷举，明确原Must必要门不漏。产品/013/原测试/原控制/原预算只读，确定缺陷由主控之后统一交工程，审计不自行修。

新审计许可TASK-115-STEP017-AUDIT-20261013：活动21600/48h日历、offline3600、真实持有2400含最后300清场/业务门2100、根4；唯一新审计source retrolume-task-115-data-audit/15451/固定本地PG17/1CPU512MiBpids128/create2成功1/start3；可精确readonly短启旧target07/55468最多2，API18115最多3/Browser2，Native/preview/build/provider/public/费用全0，旧source/failed不启动写。旧114根18等不改，所有新实用量当前0，不冒已派发/接收。资源profile/输入/独立安排在TASK115/orchestration-20261013。

主控只读source/07及新namespace/端口/内存先遭当前sandbox权限限制，申请两个只读升级自动审查均允许；不是审批拒绝或0内存。13:53:20实际新名字/15451/18115无占，RAM1.82GiB低于2GiB，读审和文件准备可进行，真实启动时核门，不关闭用户软件/服务或盲占slot。

原STEP017-P1/只读范围/G11关闭/25/R60/count1/13元/626.566/全部失败Must维持，不签完整恢复并继续/NFR005/STEP018—020/M1/项目。主控仅文件/metadata核证及共享维护，产品运行0。TASK116未占号；只有审计具体缺陷/缺口才安排原卡定向接续，不预派无限补测。CHG1326—1335，下一1336。

## 以下为v2.50及更早历史

'''
STATE.write_bytes(state_prefix.replace('\n','\r\n').encode('utf-8')+old[STATE])

context=[ROOT/'AGENTS.md',ROOT/'DocuS/最终需求文档.MD',ARCH,STATE,AUDIT_WORK,ROOT/'DocuN/evidence/TASK-113/design/revision-01/current-contract.md',ROOT/'DocuN/evidence/TASK-113/design/revision-01/b5-permissions.md',ROOT/'DocuN/evidence/TASK-113/design/revision-01/format-example.json',ROOT/'DocuN/evidence/TASK-113/design/revision-01/control-format-example.json',ROOT/'DocuN/evidence/TASK-113/design/revision-01/relationships.mmd',ROOT/'DocuN/tasks/TASK-114.md']
save('input-manifest.json',{'at':at,'TASK':'TASK-115','R':'R-109','context':[{'path':str(p),**info(p)} for p in context],'frozen_files':received['current_and_saved_files'],'removed':received['deleted_build_outputs'],'evidence_index_checks':received['index_checks'],'rules':load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'),'auditor_must_not_read':['TASK-114-result.md','implementation conversations/self-review','main product acceptance conclusions'],'C01_identity_record_for_main_only':str(RECEIVED),'old_runtime_control_identity':control_before})
save('window-assignment.json',{'TASK':'TASK-115','R':'R-109','execution':'A+','window':'全新独立隔离审计会话，未参与113/114实现','client_and_model':'由真实接收者如实登记，主控未核','manual_transfer':True,'dispatch_confirmed':False,'execution_started':False,'subagent':False,'product_frozen':True,'audit_and_bounded_required_evidence_one_result':True})
entries=[
 (1326,'DocuN/evidence/TASK-114/orchestration-receipt-c01-20261013/received.json','C01原字节/212源4bundle/八结果13FAIL/原报告后缀与规则核证，部分候选。'),
 (1327,'DocuN/results/TASK-114-work-decision.md','C01主要实链部分回收，原18/18停线/被冻结源和只读选择保护，转集中独审与必要补证。'),
 (1328,'DocuN/results/TASK-115-work-decision.md','独立集中三轴审计和精确有限取证许可，不允许修产品或借旧预算。'),
 (1329,'DocuN/evidence/TASK-115/orchestration-20261013/effective-contract.md；DocuN/tasks/TASK-115.md','完整一张审计/余项证据成果卡，新独立窗，先占号后保存待转交。'),
 (1330,'DocuS/架构动态文档.MD','v1.27主要闭环候选/真实方法与异常门未闭，三表/角色/只读范围不外推。'),
 (1331,'DocuS/执行动态文档.MD','v2.51唯一状态：114部分返回/18根结束，115待派/新许可零用量及权限/内存事实。'),
 (1332,'DocuN/evidence/TASK-115/orchestration-20261013/resource-allocation.json','一个新隔离审计源及目标07只读精确复用，有限工时/根/资源与零费用。'),
 (1333,'DocuN/evidence/TASK-115/orchestration-20261013/input-manifest.json','冻结实际源码/原件/授权目标和独立不读自评的输入边界。'),
 (1334,'DocuN/evidence/TASK-115/orchestration-20261013/window-assignment.json','全新A+独立会话，人工转卡，原工程封存。'),
 (1335,'DocuN/evidence/TASK-115/orchestration-20261013/delivery-proof.json','完整卡/预算/原数据源码账保护/共享历史及CHG连续保存复读。'),
]
addition=''.join(f'\r\n- CHG-{n}，{at}，Codex编排Agent，{p}。{why}\r\n' for n,p,why in entries)
CHANGES.write_bytes(old[CHANGES]+addition.encode('utf-8'))
for path in (WORK114,ARCH,STATE):assert path.read_bytes().endswith(old[path])
assert CHANGES.read_bytes().startswith(old[CHANGES])
assert info(result114)=={k:received['result'][k] for k in ('bytes','sha256')}
for row in received['current_and_saved_files']:assert info(ROOT/row['path'])=={k:row[k] for k in ('bytes','sha256')},row['path']
for name,identity in control_before.items():assert info(control/name)==identity
text=CARD.read_text(encoding='utf-8-sig')
assert len(re.findall(r'^## ',text,re.MULTILINE))==9
assert '*' not in text and '|' not in text
assert not re.search(r'〈[^〉]+〉|<[^>]+>',text)
assert CARD.read_bytes()==(OUT/'effective-contract.md').read_bytes()
assert allocation['limits']['real_holding_seconds']==allocation['limits']['real_business_holding_seconds']+allocation['limits']['cleanup_reserved_seconds']
assert not (ROOT/'DocuN/tasks/TASK-116.md').exists()
for n,_,_ in entries:assert CHANGES.read_text(encoding='utf-8-sig').count(f'CHG-{n}，')==1
save('delivery-proof.json',{'at':at,'TASK':'TASK-115','R':'R-109','task':{'path':str(CARD),**info(CARD)},'status':'完整卡已保存复读待人工转交，非已派发','prior_shared_byte_exact':True,'frozen_products_result_and_old_control_unchanged':True,'new_test_permissions_reviewable':True,'independent_window_required':True,'input_files':212,'bundle_files':4,'removed':1,'CHG':[1326,1335],'next_CHG':1336,'product_runs':0,'resources_started':0,'platform_read_metadata_upgrade':'auto_review允许，无审批拒绝','check':'一次完整合同/授权/参数/独立性/源保护/旧历史/文档版本/CHG与保存复读核对，非产品测试'})
print(json.dumps({'task':str(CARD),**info(CARD),'status':'待人工转交','execution':'A+新独立审计会话','state':'v2.51','architecture':'v1.27','CHG':[1326,1335],'product_runs':0,'prior_product_and_control_preserved':True},ensure_ascii=False))
