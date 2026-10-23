"""保存同号独审增量卡与共享状态；不修改工程或运行产品。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib
import json
import os
import re

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
A=ROOT/'DocuN/evidence/TASK-121/orchestration-review01-20261021'
E=ROOT/'DocuN/evidence/TASK-120/execution'
STAMP=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='microseconds')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(p,raw):
    p=p.resolve();assert p.is_relative_to(ROOT)
    p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_name(p.name+'.review01.tmp')
    with temp.open('xb') as s:s.write(raw);s.flush();os.fsync(s.fileno())
    os.replace(temp,p);assert p.read_bytes()==raw
def js(p,x):put(p,(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def prepend(text,old):return (text.strip()+'\n\n').replace('\n','\r\n').encode('utf-8')+old
def absolute(entry):
    p=Path(entry['path']);return p if p.is_absolute() else ROOT/p

assert not (OUT/'save-proof.json').exists()
inputs=load(A/'audit-inputs.json'); scope=load(A/'scope-index.json'); bounded=load(OUT/'bounded-review.json')
protected={}
for entry in inputs['current_frozen_files']+inputs['raw_engineering_evidence']+inputs['unique_latest_engineering_ledger']+[inputs['opaque_engineering_result'],inputs['prior_audit_result'],inputs['prior_audit_receipt']]:
    p=absolute(entry);h=sha(p.read_bytes()) if p.is_file() else None
    assert h==entry['sha256'],str(p)
    if h:protected[p]=h
for entry in inputs['rules']:assert sha(Path(entry['absolute_path']).read_bytes())==entry['sha256']
oldtask=ROOT/'DocuN/tasks/TASK-121.md'
shared=['DocuN/results/TASK-120-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuN/tasks/TASK-120.md','DocuN/tasks/TASK-121.md','DocuS/文档变更记录.MD']
before={n:(ROOT/n).read_bytes() for n in shared}
assert '文档v2.84' in before[shared[2]].decode('utf-8-sig')[:200]
assert '文档v1.56' in before[shared[1]].decode('utf-8-sig')[:200]
assert max(map(int,re.findall(r'CHG-(\d{4})',before[shared[5]].decode('utf-8-sig'))))==1573
for n,raw in before.items():put(OUT/'before'/n,raw)
put(OUT/'returned-ledger/budget.json',(E/'budget.json').read_bytes())
js(OUT/'main-metadata-correction.json',{
 'scope':'主控文件身份核对，不是工程运行',
 'first_command':{'chunk_id':'fbd571','exit_code':1,'wall_seconds':1.851192,'effect':'no output artifact created',
  'cause':'工程final-file-identities在统一报告置顶之前冻结，仍列旧报告hash；当前报告须单独用save-consistency新hash和旧91351字节后缀核验'},
 'corrected_command':{'chunk_id':'94803c','exit_code':0,'wall_seconds':4.4525876,
  'effect':'frozen inputs saved after explicit separate report checks'},
 'engineering_failure_count_unchanged':141,'no_original_input_writes':True})
contract=(A/'contract.md').read_bytes()
ct=contract.decode('utf-8-sig')
for x in ('F01','F02','F03','F04','F05','cleanup attempt','769.9025901','1800','3600','全部0','原TASK-121'):
    assert x in ct,x
assert '*' not in ct and '〈' not in ct
permit={
 'id':'TASK-121-READONLY-INCREMENTAL-REVIEW-01-20261021','issued_at':STAMP,
 'task':'TASK-121','R':'R-115','review':'review-01','parent_task':'TASK-120','STEP':'STEP018',
 'state':'SAVED_READABLE_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED_OR_STARTED',
 'receiver':'A+ independent enhanced; continue actual original TASK121 audit window, isolated from engineering',
 'contract_sha256':sha(contract),'contract_path':str(A/'contract.md'),
 'input_manifest_sha256':sha((A/'audit-inputs.json').read_bytes()),'scope_index_sha256':sha((A/'scope-index.json').read_bytes()),
 'engineering_products_frozen':True,'new_engineering_runtime_authorized':False,
 'runtime_counts':{x:0 for x in ('compile','unittest','product_or_test_import','PG','Docker','API','Windows_Job','browser','build','model','business_network','Git')},
 'metadata_only_stdlib_hash_diff_zip_and_saved_record_comparison':True,
 'previous_conservative_audit_tool_seconds_retained':769.9025901,
 'previous_audit_unknown_reserves_retained':True,'previous_audit_tool_cap':1800,
 'new_cumulative_audit_tool_cap_seconds':3600,'this_round_incremental_tool_cap_seconds':1800,
 'single_metadata_command_seconds':60,'maximum_calendar_seconds_this_increment':28800,
 'deadline_rule':'new reliable receipt + 8h; if actual receipt unknown, issued_at is conservative earlier bound; no interruption reset',
 'expired_original_audit_window_not_retroactively_extended':True,
 'first_bounded_read_clock_receipt_bootstrap_allowed':True,
 'official_primary_pages_cumulative_cap':6,'already_used_official_pages':2,'new_official_pages_cap':4,
 'write_paths':['DocuN/evidence/TASK-121/audit/review-01/','DocuN/results/TASK-121-result.md'],
 'prior_result_sha256_preserve_as_exact_suffix':inputs['prior_audit_result']['sha256'],
 'forbidden_decode':['DocuN/results/TASK-120-result.md','DocuN/results/TASK-120-work-decision.md','engineering chat/thinking/self-evaluation and candidate report archive entries'],
 'runtime_vault_credentials_real_configuration_read':False,
 'real_Q':'FROZEN','main_runtime':0}
js(A/'audit-permit.json',permit)
state=f'''# 执行动态文档

文档v2.85，2026-10-21，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.57、task_model/07。以下v2.84原字节保留。

## TASK120续作07已返回并冻结；原TASK121 review-01增量复核已登记

{STAMP}。收到工程07五项修复与定向验证结果，主控核15产品增量导航、31注册/30实际变化、原322引用及269去重当前身份、249本轮原件身份、015源码、选定权限/清理/时钟/PG已领取记录、原报告91351字节后缀、275条目ZIP、079/080/999及最新唯一账。仅文件/原件有限核对，无业务运行或独审。工程已返回、候选收存，五项关闭及技术验收仍待原121独立结论，原失败和控制不通过不改。

DISPATCH_STATUS

原A和更早A+工程均保持停止，当前源码/测试/dist/结果/唯一账冻结，剩余工程次数不恢复许可。原121同一独立窗口续作，只审F01—F05全修正及直接影响；特别核新cleanup attempt/完成见证是否仅恢复准确清理、新旧015完整迁移链、时钟域与PG消费门，按as-run分层继承证据，不重做整个Q/S。新运行全部0；本轮只读窗口至多8h、工具增量1800s且累计cap前向3600，首轮保守769.9025901/unknown全留，官方累计6页已用2页。旧审计窗不追认、工程96h不延长。

工程累计root60/64、PG61/64、API63/96、Browser14/16、build5/8、Native69/128、HTTP1520/10000，容器/卷创建和对象仍2/2；两新库各attempt/object1，合成准入5/16，main5/1250000、r02零独立分账，旧六实例不写不加总。失败141条/旧117的81另留，active_root/command空。wall最新64525.559426/72000，holding2885.485295/21600；报告64583.418426只将999预留60替换实测2.141，另留post-save60及旧unknown保持。

原079于2026-10-21T08:14:39.838517Z核705组PID/birth、153Job、两CID stopped/Pid0及55480/55481/18120无监听；079/080/999 exit0/tree_empty。主控只核保存时点，未探测当前资源。前端/dist/001—014等未变，原ACK/C12/正常UI/K2充分项按原审计继承。真实Q/provider/费用/preview/Git仍冻结或0，STEP018整体/019/020/M1/项目未放行。CHG1574—1579，下一1580。

## 以下为v2.84及更早历史
'''
registered=prepend(state.replace('DISPATCH_STATUS','TASK121/R115 review-01已登记，增量完整卡正在保存，未声明接收/开始。'),before[shared[2]])
put(ROOT/shared[2],registered);put(OUT/'registration-state.bytes',registered)
put(oldtask,contract+b'\r\n\r\n---\r\n\r\n'+before[shared[4]])
assert oldtask.read_bytes().startswith(contract)
put(ROOT/shared[2],prepend(state.replace('DISPATCH_STATUS','TASK121/R115 review-01完整卡已保存读回，待用户人工转交原121独审窗口，未声明已接收或开始。输入/范围/permit在DocuN/evidence/TASK-121/orchestration-review01-20261021；卡为DocuN/tasks/TASK-121.md当前置顶。'),before[shared[2]]))
put(ROOT/shared[0],prepend(f'''# TASK-120 / R-114 主控续作07回收与同TASK121增量独审安排（当前有效）

{STAMP}。工程07已真实返回。有限核对当前269去重身份/322引用导航、31注册文件/30变化及15产品差异、原始五项记录和as-run映射、原报告91351字节后缀/新hash、1,132,289字节275条目包、预算与079/080/999停止退出。没有运行产品、重做独审或凭工程PASS签关闭。

收存五项修复候选及定向工程证据，当前具备交原121增量复核的对象与原件条件。F01—F05尚不由主控预先关闭，上一工程验收失败待独审后裁定；历史控制不通过保留。新增source-delete跨进程准确清理attempt及完成回执是本轮必须审的直接高风险影响，不能因旧Operation未改而排除；两精确015链/旧包兼容、权限闭包和联合时钟同样按实际diff和被测字节判断。

同TASK121/R115 review-01完整合同已置顶保存待转交原独立A+窗口，运行0、只读工具增量1800s/累计前向3600s、8h新增只读窗，首轮769.9025901及未知预留全结转；不追认旧8h、不借工程余量。未变已充分C12/ACK/UI等复用，不新开全面审计或TASK/R。工程原A/旧A+冻结。

工程最新账root60、PG61、API63、Browser14、build5、Native69、HTTP1520、141失败/旧117的81；wall64525.559426/72000、holding2885.485295/21600及全部旧unknown保留，active空。999原预留与实测差额已据唯一账核，报告数不充当最终账；停止仅核原079时点，不是主控现时Docker探针。新两库合成5/1250000与旧实例分开，真实供应商/费用/preview/Git0，Q冻结。

架构v1.57/执行v2.85同步候选与独审安排，工程结果/证据/唯一账/审计旧结果均未改。独审未返回前不签STEP018整体/019/020/M1/项目或Q启用。以下原裁定完整保留。
''',before[shared[0]]))
put(ROOT/shared[1],prepend(f'''# 架构动态文档

文档v1.57，2026-10-21，Asia/Shanghai。需求v1.4、执行动态v2.85、task_model/07。以下v1.56原字节保留。

## Q五项修复候选已落地，独立增量确认待决

{STAMP}。工程07登记15产品变化。015修订874d2a17…330915逐项核三权限并事务内NOT VALID转换；旧59b2e556…34ef0e和新完整迁移链精确兼容，失败中间版本不接受。q_roles/schema_checks增加真实INHERIT/SET/ADMIN及管理能力用途检查。源/记忆正常链连Q正文准确清理和失败关闭，control/deletions增加source_delete私有有界CAS清理尝试与完成见证，旧Operation执行权不恢复。q_clock/批准证书增加boot域和900s单调/UTC判定及不可逆失效；PG消费事实与不可变snapshot分开，投影/续批与合法worker各守边界。

以上为实现候选与工程定向证据状态，原F01—F05关闭待TASK121 review-01独立确认。新cleanup attempt、兼容链和原55/57与最终60被测字节差异作为直接影响必审；不把前端未变或旧Operation未改当作无传导证明。001—014/前端正式dist未变，充分旧业务/UI/账本证据按适用性继承。Q及STEP018整体保持未放行。

## 以下为v1.56及更早历史
''',before[shared[1]]))
put(ROOT/shared[3],prepend(f'''# TASK-120 当前工程冻结通知——续作07已返回，待原TASK121增量确认

{STAMP}。五项修复和定向工程验证已返回并收存，主控未签其最终关闭。当前产品、fixture、dist、统一工程结果/原证据及唯一预算事件均冻结；原A及旧A+工程窗停止，07剩余次数/时间不能自动重启。原TASK121独审按本卡关联的review-01只读增量合同接续，不运行或修复工程。

当前原TASK121完整卡 D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-121.md，冻结输入 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/orchestration-review01-20261021/。Q继续冻结。以下07和更早合同只作授权/尝试历史，现停止通知优先。
''',before[shared[3]]))
entries=[(shared[0],'收存07五项修复候选及必要原件，安排原121只读增量审查，不预先关闭五项。'),
 (shared[1],'v1.57登记十五产品增量/新cleanup attempt、迁移双身份、权限和时限候选，独审待决。'),
 (shared[2],'v2.85登记工程已返回冻结、原121 review-01已保存待转交及唯一账最新值。'),
 (shared[3],'置顶工程冻结通知，原07合同与旧许可历史原字节保留。'),
 (shared[4],'置顶原121同号review-01完整增量独审卡，限定五项及直接影响、运行0，旧全面审计卡保留。'),
 ('DocuN/evidence/TASK-120/orchestration-return07-20261021及TASK-121/orchestration-review01-20261021','保存有限核证/269当前身份/249原件/范围索引、独审许可、旧共享/返回账和读回；元数据报告快照时点差异单列更正，不改工程账。')]
changes='\n\n'+'\n\n'.join(f'- CHG-{1574+i:04d}，{STAMP}，Codex编排Agent，{p}。{why}' for i,(p,why) in enumerate(entries))+'\n'
put(ROOT/shared[5],before[shared[5]]+changes.encode('utf-8'))
for p,h in protected.items():assert sha(p.read_bytes())==h,str(p)
for n in shared[:5]:assert (ROOT/n).read_bytes().endswith(before[n])
assert (ROOT/shared[5]).read_bytes().startswith(before[shared[5]])
assert (ROOT/shared[4]).read_bytes().startswith(contract)
js(OUT/'save-proof.json',{'state':'REVIEW01_SAVED_READABLE_AWAITING_MANUAL_HANDOFF',
 'issued_at':STAMP,'task':'TASK-121','R':'R-115','review':'review-01','contract_bytes':len(contract),
 'contract_sha256':sha(contract),'current_files_frozen':269,'raw_evidence_frozen':249,
 'main_runtime':0,'engineering_writes':0,'versions':['2.85','1.57'],'next_CHG':1580})
js(A/'dispatch-readback.json',{'state':'SAVED_READABLE_NOT_DISPATCHED','issued_at':STAMP,
 'card_path':str(oldtask),'card_sha256':sha(oldtask.read_bytes()),'current_contract_sha256':sha(contract),
 'permit_sha256':sha((A/'audit-permit.json').read_bytes()),'runtime':0})
print(json.dumps({'state':'REVIEW01_SAVED_READABLE_AWAITING_MANUAL_HANDOFF','task':'TASK-121','R':'R-115',
 'contract_bytes':len(contract),'frozen_current_files':269,'frozen_raw_evidence':249,'next_CHG':1580,'runtime':0},ensure_ascii=False))
