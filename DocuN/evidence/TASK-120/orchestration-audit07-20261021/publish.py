"""仅保存主控裁定和待批准合同，不导入产品、不启动服务、不更改工程账。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def put(p, data):
    p = p.resolve()
    assert p.is_relative_to(ROOT)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_name(p.name + '.main07.tmp')
    with temp.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, p)
    assert p.read_bytes() == data

def js(p, value):
    put(p, (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))

def prefix(text, old):
    return (text.strip()+'\n\n').replace('\n','\r\n').encode('utf-8') + old

assert not (OUT/'save-proof.json').exists()
closing = load(ROOT/'DocuN/evidence/TASK-121/audit/identity-check-closing.json')
rows = closing['rows']
for row in rows:
    p = Path(row['path'])
    assert (digest(p.read_bytes()) if p.is_file() else None) == row['actual'], row['path']
report = ROOT/'DocuN/results/TASK-121-result.md'
assert len(report.read_bytes()) == 33054
assert digest(report.read_bytes()) == 'c4c30439cd6a2d7b63b12254a76550013ae8da93b50c9cf2d6836451588314d8'
receipt = load(ROOT/'DocuN/evidence/TASK-121/audit/audit-session-receipt.json')
assert receipt['finding_counts'] == {'P1':4,'P2':1}
budget_path = ROOT/'DocuN/evidence/TASK-120/execution/budget.json'
budget = load(budget_path)
assert budget['active_root'] is None and budget['active_command'] is None
assert budget['counts']['roots'] == 51 and len(budget['failures']) == 125
assert abs(budget['command_wall_conservative_upper_seconds']-50243.003003) < .001

draft = OUT/'repair-contract-proposed.md'
draft_text = draft.read_text(encoding='utf-8')
for required in ('F01','F02','F03','F04','F05','待采用','72000','retrolume_task120_audit07_main','TASK-121','原字节'):
    assert required in draft_text
assert '〈' not in draft_text and '*' not in draft_text
shared = ['DocuN/results/TASK-120-work-decision.md','DocuS/架构动态文档.MD',
          'DocuS/执行动态文档.MD','DocuN/tasks/TASK-120.md','DocuS/文档变更记录.MD']
old = {x:(ROOT/x).read_bytes() for x in shared}
assert '文档v2.82' in old[shared[2]].decode('utf-8-sig')[:200]
assert '文档v1.54' in old[shared[1]].decode('utf-8-sig')[:200]
assert max(map(int,re.findall(r'CHG-(\d{4})',old[shared[4]].decode('utf-8-sig')))) == 1562
for name, raw in old.items():
    put(OUT/'before'/name, raw)

proposal = f'''# AP-120-07 五项审计修复与定向验证合并采用包

{STAMP}。状态为待用户采用，未签发执行许可。工程、真实Q均保持冻结。

## 已核证和下一完整成果

TASK-121/R-115集中独审交付已回收，报告及收尾322条身份逐项吻合。主控采纳四P1与一P2，当前TASK-120技术验收失败，不能关闭。历史执行控制不通过继续留账；原C12共同100门、ACK、列明业务及迟到UI等有效证据不重跑。

下一完整成果为同TASK-120/R-114续作07一次修完F01迁移缺权、F02实际继承/SET能力、F03正文清理、F04时间回退、F05已领取续批投影，并完成五项定向验证后交原TASK-121增量复核。接收为刚完成06的原A独占最强工程窗口。完整可审阅草案见[修复与验证合同](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-audit07-20261021/repair-contract-proposed.md)。

## 请求一次采用的精确增量

1. 在现有合成源容器 b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f 内新增两个空测试库 retrolume_task120_audit07_r02、retrolume_task120_audit07_main，各最多一次创建。沿原镜像、卷、512MiB/1CPU/pids128及55480/18120，无新容器/卷，旧六实例与旧批准不改。新库最终保留不drop。
2. 仅在未提交测试事务内制造必需权限缺失和角色继承/SET负例，可临时使用两个NOLOGIN桥接组 retrolume_task120_audit07_bridge1/bridge2；无新登录/密码/超级用户/CREATEROLE调整，禁止把危险成员关系提交。负例结束回滚并新连接核原角色图，期间停其他使用同集群的本任务客户。实际负例只证明拒绝不合格配置，不授产品新能力。
3. 修订015仅在本轮新库验证。旧已应用015及旧包原件永久保留；旧R03只按原精确hash作历史读取兼容，新安装必须校验修订hash。不是重写已部署事实，不改001—014，不增加业务表/列。
4. 新测试私有根限定 D:/shspic/project_NO3_RetroLume-agent/.runtime/task120-audit07。准许产品正常源删除/记忆purge入口清除本轮新造并先登记精确清单的最多16份合成正文文件，包括对应Q prepared副本；不得删目录、旧Q根、旧证据或个人数据。原冻结八文本只复制使用，删除对象可重建；保留摘要、事件、007记录和费用，清理失败须关闭相关Q资格。
5. 原剩余根/PG/API/Browser/build等次数继续使用，累计上限不重置，最多16笔新合成admission；只有工具wall前向从57600增至72000秒，已用50243.003003及未知预留全结转。续作窗至多12小时且不晚原96h截止2026-10-22T08:41:08.5687758Z，末1800秒仅清场保存。Q、真实外发/费用、预览和Git仍0。首次接收bootstrap可读卡采时登记，计入wall，不再要求在尚未读卡前伪称完成登记。

以上边界采用后主控将同一草案签发为续作07正式卡，无需为每个测试再询问。未采用时不启动工程或测试。主控没有更改产品/迁移/工程账或启动任何资源，也没有替代独审运行。

## 原因、代价和恢复

原AP-120-06只覆盖单表DELETE、一个新源和既定恢复目标，未覆盖新增逻辑库、负例成员关系及上述正文删除；公共AGENTS第2节要求权限调整和不可逆删除具有覆盖对象与范围的明确授权，所以不能由主控把原许可自动扩成这些动作。

代价是增加两个很小的合成库和受限验证时间；没有真实付费。原源已frozen不能为了省建库而解冻；迁移与角色语义不能靠mock替代。只做代码而不做这些验证可继续保留候选，但不能关闭对应P1，故推荐一次采用本完整包。

恢复为角色/权限负例事务回滚并核证、合成正文由冻结输入重新生成、测试数据库及旧数据全部保留、精确停止源容器/API/子进程。旧实例权限/金融事实/原失败记录不变。不删除本轮失败或超限；历史控制不通过不会因新许可变成通过。
'''
put(OUT/'adoption-proposal.md', proposal.encode('utf-8'))
review = {'observed_at':STAMP,'audit_report':{'path':str(report),'bytes':33054,'sha256':digest(report.read_bytes())},
          'audit_task_delivery':'accepted_complete','engineering_acceptance':'failed',
          'code_axis':'不通过','evidence_axis':'证据不足','control_axis':'不通过',
          'checked_identity_rows':len(rows),'mismatches':[],
          'findings':receipt['result']['findings'],'budget_counts':budget['counts'],
          'budget_caps':budget['caps'],'failures_retained':len(budget['failures']),
          'conservative_wall_seconds':budget['command_wall_conservative_upper_seconds'],
          'holding_seconds':budget['runtime_holding_union_seconds'],
          'active_root':None,'active_command':None,
          'resource_fact':'仅核原停止证据与账末态，未探测当前Docker/进程/端口',
          'main_runtime':0,'product_writes':0,'engineering_ledger_writes':0,
          'proposal_state':'PENDING_USER_ADOPTION_NO_EXECUTION_PERMIT',
          'proposal_sha256':digest((OUT/'adoption-proposal.md').read_bytes()),
          'draft_sha256':digest(draft.read_bytes()),
          'audit_logging_limits':'首批计时未知/保守预留及历史控制失败按报告保留，不篡改'}
js(OUT/'bounded-review.json',review)

put(ROOT/shared[0],prefix(f'''# TASK-120 / R-114 主控回收TASK-121集中独审（当前有效）

{STAMP}。独审已真实返回；主控读报告、收尾身份和投入回执，复算322条身份零漂移、报告33054字节hash吻合，必要源码定位与原119清理/时限合同相符。只作有限核证，不运行产品或重做审计。

TASK-121/R-115审计任务交付通过，其被审对象TASK-120技术验收失败。采纳F01/F02/F03/F04四P1与F05一P2作为唯一合并修复清单，分别为015必需权限漏验、实际成员能力漏验、Q正文清理未接、UTC回退恢复批准、PG已领取投影/续批误开放。报告代码不通过、证据不足、控制不通过分别保留，不以控制记录问题抹掉有效技术证据。

C12、三ACK、列明有限正常链、K2及两迟到UI/只读读取的已有子事实按独审范围继承，不重刷99笔或全业务。原memory即时before不足、旧R01仅包读取、原未知预留和计时限制保持。工程账根51、125失败/旧117的81、wall50243.003003、holding2667.078295、active空未改。停止只核原时点，非本轮实时服务证明。

五项修复合成同TASK120续作07完整草案与AP-120-07具体采用包，位于DocuN/evidence/TASK-120/orchestration-audit07-20261021。原A增强能力独占续作，原121后续增量复核；无新TASK/R。新增合成库、事务内权限反例及新造正文精确删除尚缺用户覆盖授权，实际permit未签发、工程仍冻结，草案不可执行。待用户一并采用后前向签发，不逐小项拆卡。Q继续冻结，STEP018整体/019/020/M1/项目不关闭。

以下为原06收存与更早裁定，原字节保留。
''',old[shared[0]]))
put(ROOT/shared[1],prefix(f'''# 架构动态文档

文档v1.55，2026-10-21，Asia/Shanghai。需求v1.4、执行动态v2.83、task_model/07。以下v1.54原字节保留。

## Q候选集中独审发现权限、清理、时限及领取状态缺口

{STAMP}。TASK121四P1与一P2已核证采纳，TASK120候选未通过。015的SELECT/INSERT/UPDATE前提未保证全部必需权限；严格ACL未检查实际继承/SET角色能力；Q prepared完整正文未纳入资料/记忆清理；仅UTC比较可能恢复过期批准；PG已领取未Q claim仍可能批准/续批。现有有效账本/正常业务/UI证据不因此全作废，修复只覆盖发现与真实影响。

待采用AP-120-07限定完善原合同，不另造权限平台或费用账。拟修015新安装前提并保留旧精确包识别、检查实际角色链、接入原精确清理与失败关闭、补可解释时钟域/不可逆过期、PG领取单独投影。新增测试库/事务权限反例/新合成副本删除未获本轮许可，未实施。原Q启用门与集中独审修正确认保持；原S有限结论及历史控制不通过保留。

## 以下为v1.54及更早历史
''',old[shared[1]]))
put(ROOT/shared[2],prefix(f'''# 执行动态文档

文档v2.83，2026-10-21，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.55、task_model/07。以下v2.82原字节保留。

## TASK121已返回并完成主控回收；TASK120五项合并修复包待采用

{STAMP}。TASK121/R115调度已返回，审计交付验收通过；审计对象TASK120/R114工程验收失败，代码不通过、证据不足、历史执行控制不通过。四P1及一P2为TASK121 F01—F05，沿原工程单一路线合并修复，不重开原S或新占TASK/R。

已保存AP-120-07具体采用包和同号续作07完整合同草案，可审阅但不可执行。位置DocuN/evidence/TASK-120/orchestration-audit07-20261021。接收拟为刚完成06的原A最强工程窗口；原A+停止，原121审计已结束待以后增量复核，不存在新派发/在途记录。待用户明确批准新增两个精确合成库、事务内角色权限负例、新造正文清理及前向wall增量，才签发执行permit；当前工程停止通知保持有效。

322条收尾身份实时重算无漂移；主控未测试、未改工程源码/结果/预算。根51/64、PG52/64、API55/96、Browser14/16、build5/8、Native64/128、HTTP1459/10000，PG/卷创建及对象各2/2，125失败/旧117的81保留，wall50243.003003/57600、holding2667.078295/21600、active空。原停止证据有效时点沿用，不称当前Docker实时核查。

有效共同100门/三ACK/列明正常链/K2/UI证据复用；新五风险要求定向补证。审计接收计时未知、保守预留及工程历史控制失败都保留，不靠新卡追认。Q/provider/实际费用/preview/Git仍冻结或0，STEP018整体/019/020/M1/项目未通过。CHG1563—1568，下一1569。

## 以下为v2.82及更早历史
''',old[shared[2]]))
put(ROOT/shared[3],prefix(f'''# TASK-120 当前停止通知——TASK121集中独审未通过，07采用待决

{STAMP}。四P1与一P2合并回原工程。AP-120-07与完整修复草案已保存于 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-audit07-20261021/。

当前未批准本轮新增数据库、权限反例和精确正文删除，未签发07执行permit。原A工程窗保持停止；不能按下方旧06合同或剩余额度重启。主控待一个合并采用决定后再置顶可执行完整卡。Q继续冻结。旧合同、已用预算及失败历史原字节保留。

以下为原冻结通知及更早合同。
''',old[shared[3]]))
changes = [
 ('DocuN/results/TASK-120-work-decision.md','回收121审计，采纳四P1一P2，120验收失败，五项合并修复待采用。'),
 ('DocuS/架构动态文档.MD','v1.55登记真实权限/清理/时限/领取缺陷及待采用修复边界。'),
 ('DocuS/执行动态文档.MD','v2.83登记121已返回/审计交付通过、120失败、无在途、AP12007待决与预算不重置。'),
 ('DocuN/tasks/TASK-120.md','置顶本轮待采用停止通知，旧合同及旧冻结原字节保留。'),
 ('DocuN/evidence/TASK-120/orchestration-audit07-20261021/adoption-proposal.md','保存具体新资源、负例权限、合成正文删除与wall前向增量的一项批准包，尚未采用。'),
 ('DocuN/evidence/TASK-120/orchestration-audit07-20261021/repair-contract-proposed.md','保存五项修复与定向验证完整草案，不是执行permit；核证/快照/读回同步留证。')]
entries='\n\n'+ '\n\n'.join(f'- CHG-{1563+i:04d}，{STAMP}，Codex编排Agent，{name}。{why}' for i,(name,why) in enumerate(changes))+'\n'
put(ROOT/shared[4],old[shared[4]]+entries.encode('utf-8'))
for row in rows:
    p=Path(row['path'])
    assert (digest(p.read_bytes()) if p.is_file() else None)==row['actual'],str(p)
assert digest(report.read_bytes())==review['audit_report']['sha256']
assert load(budget_path)==budget
for name in shared[:4]:
    assert (ROOT/name).read_bytes().endswith(old[name])
assert (ROOT/shared[4]).read_bytes().startswith(old[shared[4]])
js(OUT/'save-proof.json',{'state':'PROPOSAL_AND_COMPLETE_DRAFT_SAVED_READABLE_NOT_AUTHORIZED',
   'created_at':STAMP,'identity_rows_rechecked':len(rows),'product_or_runtime_changes':0,
   'versions':['2.83','1.55'],'next_CHG':1569,'task_R_numbers_unchanged':True,
   'user_adoption':False,'execution_permit_issued':False,
   'files':[{'path':str(p),'sha256':digest(p.read_bytes()),'bytes':len(p.read_bytes())}
            for p in [OUT/'adoption-proposal.md',draft]+[ROOT/x for x in shared]]})
print(json.dumps({'state':'SAVED_READABLE_PENDING_ONE_ADOPTION','audit_received':True,
                  'findings':5,'runtime':0,'identity_rows':len(rows),'next_CHG':1569},ensure_ascii=False))
