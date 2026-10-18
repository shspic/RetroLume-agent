"""保存C04限定验收与C05合同，保全原文，不改产品。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re,math
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):b=p.read_bytes();return dict(bytes=len(b),sha256=sha(b))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
received=load(OUT/'received.json');b=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
if b['counts']!=received['counts'] or b['active_batch'] is not None:raise RuntimeError('运行账改变')
if info(ROOT/'DocuN/results/TASK-111-result.md')['sha256']!=received['result']['result_sha256']:raise RuntimeError('返回结果改变')
for r in received['sources']:
 if info(ROOT/r['path'])['sha256']!=r['actual_sha256']:raise RuntimeError('源漂移 '+r['path'])
C04=ROOT/'DocuN/evidence/TASK-111/execution/continuation-04'
normal=load(C04/'final/Native-and-normal-UI.json');effects_path=Path(normal['normal_effects_file']);effects=load(effects_path)
frames=[]
for r in effects['frames']:
 p=effects_path.parent/r['file'];v=info(p)
 if v['sha256']!=r['sha256'] or v['bytes']!=r['bytes']:raise RuntimeError('原UI帧字节不符')
 frames.append(dict(file=str(p),**v))
inputs=[]
for r in effects['records']:
 if r.get('kind')!='input':continue
 response=r['response'];body=response['body'];refuse=r['refuse']
 ok=(response['status']==422) if refuse else response['status']==200 and body['accepted'] is True and math.isclose(float(body['readouts'][0]['value']),r['oracle'],rel_tol=0,abs_tol=1e-9)
 if not ok:raise RuntimeError('正常原件数值/拒绝不符')
 inputs.append(dict(label=r['label'],value=r['value'],expected=r['oracle'],refused=refuse,status=response['status']))
save('normal-byte-check.json',dict(effects=info(effects_path),PNG_count=len(frames),PNGs=frames,input_checks=inputs,scope='现成正常UI原件核读，非新运行/全G11'))
caps=dict(b['continuation_caps']);caps.update(real_batches=16,preview_creates=43,preview_starts=41,PG_container_starts=12,API_listener_starts=10,main_browser_starts=9)
budget=dict(TASK='TASK-111',R='R-105',permit='TASK-111-G11-C05-20261011',at=at,
 prior_used=received['counts'],prior_time_seconds=received['time_seconds'],cumulative_caps=caps,
 kickoff='收到C05后首个有真实UTC/monotonic采样的许可接收操作，未采准备段单列unknown，不倒推精确首读',
 work_seconds=10800,prior_authorized_work_seconds=108000,cumulative_authorized_work_seconds=118800,
 new_real_limit_seconds=1800,cumulative_real_limit_seconds=14400,per_root_seconds=1500,cleanup_reserved_seconds=600,cleanup_cumulative_limit_seconds=1800,
 new_preview_names=[f'retrolume-task-111-g11-preview-{i:02d}' for i in range(40,54)],
 planned_base=dict(client_lifecycles=5,stop_scenarios=6),related_repair_slots=3,
 no_new_model_or_OneCall_planned=True,no_new_image_build=True,same_control_root=str(ROOT/'DocuN/evidence/TASK-111/execution/continuation-04/synthetic/control'),new_actual_use=0)
if caps['preview_creates']-received['counts']['preview_creates']!=14 or caps['preview_starts']-received['counts']['preview_starts']!=14:raise RuntimeError('preview额度不符')
if received['time_seconds']['real']+1800>14400:raise RuntimeError('真实总预算不足')
save('continuation-budget.json',budget)
rels=('DocuN/tasks/TASK-111.md','DocuN/results/TASK-111-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD')
before={r:(ROOT/r).read_bytes() for r in rels}
if sha(before[rels[0]])!='ece10a24492aa96b68a4d7424a34b5ac8a85756770214c301911bc07716654c2':raise RuntimeError('C04旧卡改变')
if b'CHG-1203' in before[rels[-1]]:raise RuntimeError('CHG已有归属')
pre=OUT/'before-documents';pre.mkdir(exist_ok=False)
for r,data in before.items():(pre/r.replace('/','__')).write_bytes(data)
(OUT/'prior-TASK-111.md').write_bytes(before[rels[0]])
prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK-111 / R-105 C04部分验收与C05尾链接续

{at}，Codex编排Agent。收到C04 117106字节/4cd4497a…，89源/七规则匹配，97401原历史后缀保存。调度已返回，验收部分通过，完整G11仍未关闭；没有泛审或复跑正常两Native。

DEF-029六列资格闭包和DEF-030挂起登记拒绝/释放后启动/ready后日志拒绝完整清场定向关闭，父终审仍待。主控已核两正常完整绑定、两个Native归属/settled、21ACK、43PNG字节与输入oracle/拒绝记录；XSS、资料与原键/回父等适用原件接受，正常Native/UI不再重发。memory/cancel精确barrier与Node/Reaper限域通过接受，source/parent、核心/预算/权限/rollback/许可充分未变部分继承。

最后首因保留修复仅生产解码器四例过；owner真实case已止但reason FAIL保留，最终生命周期待复验。迟到stop的路由重复处理夹具错误未闭bitmap/最后DOM，隐藏/卸载/活跃刷新未过；另外五个停止场景not_run。根13预检失败/root14已结束、API/browser到限，普通失败前预排stop是执行控制错误，非核心方案再次失败，不能只重开原根。

本次只读源码还核C04 Witness额外持Job且finish主动Terminate；其Node/Reaper原件按披露边界继承，未来死亡场景须先去除或分层此干预。微软Job官方规范支持最后句柄关闭终止并销毁；新私有proof可接受实际Query零或有事前绑定/flags、owner子实例结束与准确Job不存在的严格已销毁证据，不能直接缺对象填0或拿验收者主动kill签自主结束。属于实现既有实际停止要求，不加权限/平台/数据模型或放宽物理证明。

签TASK-111-G11-C05-20261011沿原C04 A+窗口，只做客户端尾链和六项停止。卡中明确真实已解析响应迟到与取消Route分开、实际bitmap释放、真实visibility/活跃刷新；在现有私有恢复完善非干预证明，正常两链和六列ACL不重跑。原C04控制根继续，旧25仍UNKNOWN/R60/旧根blocked，不又换根。

新综合3小时以实际许可接收工具UTC/mono固定，不再事后减300秒冒精确首读；旧准备unknown/历史失守保留。当前real12382.158，新real1800、累计14400，根14→16各1500；client五+停止六+修正三共14名字40—53，create上限43/start41。PG/API/browser上限12/10/9各新可用2，其余model/Windows9/10、image7/7、frontend3/5、原HTTP/输入/PNG等不增。本卡不计划新模型/Native/image，旧92入口/13元/实际与失败不清。

合同与预算已保存待人工转交，旧C04卡原字节保留同receipt/prior-TASK-111.md。主控只读26精确对象均停及维护文档，未执行产品/SQL/build/业务。卡内普通修正连续，完整候选稳定后一次隔离增强终审仍未派，TASK112未占。

## 以下为C04及更早裁定原字节

''',
'DocuS/架构动态文档.MD':f'''# 架构动态文档

文档v1.17，2026-10-11，Asia/Shanghai。需求v1.2、执行动态v2.39、task_model/07。以下v1.16及历史保留；G11多数功能已证，客户端和停止尾链待收口。

## 正常业务与资格启动修复已证，停止观察边界须完善

固定v2-07最终frontend两Native/正常计算图形、源回查、原键竞争/丢回包GET与停止回父有原件，89源一致、21ACK/43PNG核证成立。六列只读资格及记忆/cancel精确屏障、挂起前登记拒绝/释放后真实启动和ready后日志拒绝完整结束使DEF-029/030定向关闭。原物理停止/预算/四账/ACL/角色域不变，真实provider质量与全G11不因此通过。

最后SUP首因保留的生产解码器修复只有协议回归；最终owner失联实际行为还需一次。客户端取消Route与已解析响应迟到须正确分开，bitmap实际释放、真实hidden/unload/活跃刷新未闭。无新正常模型或镜像必要。

C04 Witness预持Job且finish主动Terminate不是纯观察，后续SUP/双死亡/硬D必须先移除 critical窗口的额外Job持有与主动清理，外部救援另层记。私有恢复可基于实际查询0或严格已销毁/owner实例结束/原flags与assignment及完整Linux/EOF证据判结束；非不存在错误/错误名/从未绑定不通过，不拿缺对象填0。原StopProof物理门不降，无新数据库/公共API。

C05仅针对两个尾链集，原controller测试根继续，旧25UNKNOWN不改。工程窗口与精准名字/余量由执行动态/卡管理。生产HTML默认关闭，高风险完整稳定后集中独审；用户库、真实provider/发布、Linux/Nginx无新授权。

## 以下为v1.16及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.39，2026-10-11，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.17、task_model/07。以下v2.38历史保留。

## 111续作04部分返回，续作05只补客户端与停止尾链

C04原A+窗口实际返回117106字节/4cd4497a2cf35813247a56723d6c257ca558269c3097fca10d07b74e7e5b6c2f，89源/七规则一致。验收部分通过，DEF-029/030定向关闭，正常两Native/UI、21公开ACK/43PNG、六列权、memory/cancel精确资格与挂起启动/后ready日志异常真实通过；旧source/parent和充分原件继承。完整G11/M1/项目仍未过，不派全面终审。

剩余为客户端迟到/bitmap/真实hidden/unload/活跃refresh、最终首因owner失联、pipe_corrupt/SUP死亡/双死亡/控制失联/hardD。Node/Reaper现有限域原件保留。新的观察器必须避免额外Job handle延后kill-on-close及finish主动Terminate污染自主结论，准确Job已销毁可在严格事前与实例结束证据下作为私有结束证明，不能伪Query0。

原根13预检失败2.297、根14含PG尾区间1657.703；实际real12382.158/offline204.905/cleanup55.0657405、根14/global92、PG start10/11、API8/8、browser7/7、preview create29/34/start27/32、model/Windows9/10、frontend3/5、image7/7、HTTP882/5000/PNG149/3000/public input57/300/internal26/500。提前排stop和first clock/pre缺口、旧13元/失败/UNKNOWN继续保留；unused名额不复活旧根或许可。

签C05同TASK111/R105沿原C04 A+窗口，现待人工转交，未自动派发/开始。新综合10800秒从首个实际UTC/mono许可接收操作固定，准备段unknown不倒推；旧108000授权窗口账前向增为118800，末600清场。新real≤1800且累计14400，根累计16已14、每根1500；preview create43/start41已29/27，新name40—53共14，client5+停止6+修正3，不重做正常两链。PG/API/browser分别12/10/9，各实际最多新增2；不增model/Windows/image/并发或用户数据费用，frontend仍余2。现26登记对象Stopped/Pid0，active_batch null，新实际0。

先精确修迟到和取证准备，再一个PG/API组合读完每方法结果后决定终止，不预排stop，不因metadata/已知物理结果的普通失败自动掐断余项。所有新场景仍C04唯一control根，旧25UNKNOWN/R60和原根blocked封存，不再换root；新未知完整本对象恢复否则停。核心/许可/ACL/Native等现成部分按字节直接继承，完整稳定后一次隔离增强终审仍未发。

本批CHG1203—1215，下一1216。核证/预算/合同在DocuN/evidence/TASK-111/orchestration-receipt-05/，任务DocuN/tasks/TASK-111.md为唯一新入口，旧C04原字节保存同receipt/prior-TASK-111.md。主控产品写/运行0，公共库和原始需求未动，TASK112未占。

## 以下为v2.38及更早历史

'''
}
draft=(OUT/'effective-contract.md').read_bytes();t=draft.decode('utf-8')
if '*' in t:raise RuntimeError('新合同禁止格式')
reg=f'# 执行动态文档\r\n\r\n{at}，TASK111/R105 C05已登记保存中，非实际派发。\r\n\r\n'.encode()
(ROOT/'DocuS/执行动态文档.MD').write_bytes(reg+before['DocuS/执行动态文档.MD'])
(ROOT/'DocuN/tasks/TASK-111.md').write_bytes(draft)
for r,prefix in prefixes.items():(ROOT/r).write_bytes(prefix.replace('\n','\r\n').encode()+before[r])
save('window-assignment.json',dict(TASK='TASK-111',R='R-105',resource='A+原C04工程窗口',contract=str(ROOT/'DocuN/tasks/TASK-111.md'),contract_sha256=sha(draft),status='待人工转交',parallel=False,audit=False,actual_dispatch=False))
entries=[
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/receive.py','只读结果89源/七规则/26对象及范围核证，publish.py维护合同。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/received.json','C04真实部分返回与方法/余量，非完整验收。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/resource-recheck.json','26精确已登记容器当前停止metadata，非旧25完整树空。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/accepted-and-pending.json','DEF-029/030定向关闭、两组真实剩余方法与Job观察风险。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/normal-byte-check.json','43PNG字节与真实input oracle核证，不重跑正常链。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/continuation-budget.json','client5/stop6/修正3的14名额及3小时、root/real余量成套核算。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/effective-contract.md','两个尾链目标，非干预取证、真实迟到/visibility、无新模型镜像。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/prior-TASK-111.md','旧C04完整原字节历史；window-assignment.json登记同窗待转交。'),
 ('DocuN/results/TASK-111-work-decision.md','C04部分验收与C05限域具体许可，保旧失败/UNKNOWN。'),
 ('DocuN/tasks/TASK-111.md','唯一现行C05完整合同。'),
 ('DocuS/架构动态文档.MD','v1.17已证正常/资格/启动及剩余停止证明边界。'),
 ('DocuS/执行动态文档.MD','v2.39唯一状态账，C04返回/C05待转交，预算与失败不清。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-05/delivery-proof.json','一次历史/路径/预算/源不变的交付检查，主控无产品执行。')]
ledger=ROOT/'DocuS/文档变更记录.MD'
if ledger.read_bytes()!=before[rels[-1]]:raise RuntimeError('变更账并行变化')
append='\r\n'+''.join(f'\r\n- CHG-{1203+i:04d}，{at}，Codex编排Agent，{p}。{note}\r\n' for i,(p,note) in enumerate(entries))
ledger.write_bytes(before[rels[-1]]+append.encode())
if not all((ROOT/p).read_bytes().endswith(before[p]) for p in prefixes):raise RuntimeError('历史后缀改变')
if (OUT/'prior-TASK-111.md').read_bytes()!=before[rels[0]]:raise RuntimeError('旧卡原件改变')
if not all(info(ROOT/r['path'])['sha256']==r['actual_sha256'] for r in received['sources']):raise RuntimeError('发布时产品源改变')
if info(ROOT/'DocuN/results/TASK-111-result.md')['sha256']!=received['result']['result_sha256']:raise RuntimeError('执行者报告改变')
refs=list(dict.fromkeys(re.findall(r'D:/shspic/project_NO3_RetroLume-agent/[A-Za-z0-9_./-]+\.(?:md|json)',t)))
if any(not Path(p).is_file() for p in refs):raise RuntimeError('合同必要路径不存在')
proof=dict(at=at,contract=info(ROOT/'DocuN/tasks/TASK-111.md'),old_contract=info(OUT/'prior-TASK-111.md'),history_exact=True,sources_unchanged=89,report_unchanged=True,
 accepted_normal_PNGs=43,normal_input_checks=len(inputs),new_names=14,baseline=11,repair_slots=3,
 projected_real=received['time_seconds']['real']+1800,total_real_cap=14400,
 new_model_plan=0,new_image_plan=0,checked_local_refs=len(refs),status='待人工转交',actual_new_execution=0,product_writes=0,CHG_first=1203,CHG_last=1215,next_CHG=1216)
save('delivery-proof.json',proof)
print(json.dumps(proof,ensure_ascii=False))
