"""回收C03并发布同范围C04；只维护合同/共享文档，不改产品或SQL。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
C03=ROOT/'DocuN/evidence/TASK-111/execution/continuation-03'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):b=p.read_bytes();return dict(bytes=len(b),sha256=sha(b))
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
received=load(OUT/'returned-and-core-check.json');core=load(OUT/'core-acceptance.json')
if not core['all_pass']:raise RuntimeError('核心证据未闭')
report=ROOT/'DocuN/results/TASK-111-result.md'
if info(report)['sha256']!=received['result']['sha256']:raise RuntimeError('结果在回收后改变')
sources=received['sources']
for r in sources:
    if info(ROOT/r['path'])['sha256']!=r['actual_sha256']:raise RuntimeError('源已改变 '+r['path'])
oldbudget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
if oldbudget['counts']!=received['counts'] or oldbudget['active_batch'] is not None:raise RuntimeError('预算或在途变化')
caps=dict(oldbudget['continuation_caps']);caps.update(PG_container_starts=11,API_listener_starts=8,main_browser_starts=7)
budget=dict(TASK='TASK-111',R='R-105',permit='TASK-111-G11-C04-20261011',at=at,
    first_read_work_seconds=14400,prior_authorized_work_seconds=93600,cumulative_authorized_work_seconds=108000,
    prior_used=received['counts'],prior_time_seconds=received['time_seconds'],cumulative_caps=caps,
    new_real_limit_seconds=3000,cumulative_real_limit_seconds=14400,per_root_seconds=1800,
    business_stop_before_final_deadline_seconds=600,cleanup_cumulative_limit_seconds=1800,
    preview_new_names=[f'retrolume-task-111-g11-preview-{i:02d}' for i in range(26,45)],
    no_new_image_build=True,production_image=core['image'],production_load=core['load'],
    old_unknown_kept=True,old_unknown_no_refund=True,new_execution_started=False)
if budget['prior_time_seconds']['real']+3000>14400:raise RuntimeError('真实总预算不够')
if caps['preview_creates']-received['counts']['preview_creates']!=len(budget['preview_new_names']):raise RuntimeError('名字与counter错配')
save('continuation-budget.json',budget)
boundaries=dict(TASK='TASK-111',authority='108 C2已采用的owner资格校验必需SELECT/EXECUTE；110保留记忆闭包',
    columns={'public.pdf_review_candidates':['id','version_id','status','page_count'],'public.pdf_review_pages':['candidate_id'],'public.pdf_extracted_pages':['version_id']},
    grantee='retrolume_html_owner',grant_option=False,table_SELECT=False,new_role=False,DML=False,user_database=False,
    unknown_preview='542b0750-6e02-418a-b216-5dfbd3b93047',unknown_CID='742543c26e0507a62d3797f86f9a88bea3c433bc75d4d681b87f5a6e2dd23944',
    unknown_preserve_state='cleanup_unconfirmed',unknown_reserved_seconds=60,unknown_old_root_blocked=True,
    C04_single_test_root=str(ROOT/'DocuN/evidence/TASK-111/execution/continuation-04/synthetic/control'),
    development_only_isolation=True,not_a_product_unknown_bypass=True,new_unknown_stops_same_root=True,
    no_new_user_adoption_needed='补齐已采用资格只读闭包，主控明确工程测试隔离；不降低产品停止/退款门')
save('scope-and-authority.json',boundaries)

rels=('DocuN/tasks/TASK-111.md','DocuN/results/TASK-111-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD')
before={r:(ROOT/r).read_bytes() for r in rels}
if sha(before[rels[0]])!='cd8220ab8bc8d5a29e59ca1b12cab0c130d9a17bb7119d5a2c0a2cf5fa7e3098':raise RuntimeError('原C03卡改变')
if b'CHG-1190' in before[rels[-1]]:raise RuntimeError('CHG号已占')
pre=OUT/'before-documents';pre.mkdir(exist_ok=True)
for r,b in before.items():
    saved=pre/r.replace('/','__')
    if saved.exists():
        if saved.read_bytes()!=b:raise RuntimeError('已有pre与共享源不符')
    else:saved.write_bytes(b)
prior=OUT/'prior-TASK-111.md'
if prior.exists():
    if prior.read_bytes()!=before[rels[0]]:raise RuntimeError('旧卡原件不符')
else:prior.write_bytes(before[rels[0]])
draft=(OUT/'effective-contract.md').read_bytes();text=draft.decode('utf-8')
if '*' in text:raise RuntimeError('新卡格式不合规则')
prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK-111 / R-105 C03部分验收与C04明确接续

{at}，Codex编排Agent。真实回收97401字节/6cf13c14…、78项当前源和七规则匹配，旧75828后缀原字节保留。原C03窗口已返回，调度已返回；完整实现与矩阵未通过，验收部分通过，不能安排全面终审。

DEF-027在代码/本次定向行为范围关闭。实际生产共用纯组装、完整15586字节脚本与Python compiled_html一致；v2-07核心ACK58.8/零、三PNG内容/nonce/哈希和蓝柱归零已核。core-acceptance.json的21项绑定全成立，private PID/init停止、kernel hash/EOF/wait/die/两Job零任务相符。只是机械能核心和当次停止，不冒最终Native/主UI或整个G11。当前process.py的有界替换等待只有本机边界证据，不能追成该核心使用最终同一文件版。

新预算INSERT/ON CONFLICT触发器问题已修并真实三生命周期通过，作为已解决实际缺陷登记DEF-028/定向闭合；记忆资格缺读列登记DEF-029开放，启动后登记失败失去管道证据登记DEF-030开放/异常路径待修。原PermissionError没有准确WinError/行号，不假称锁持有者根因已证；当前结构确定是启动后必需登记先于读者建立。

权限裁定覆盖完整调用链。108 C2已采用owner资格必需SELECT/EXECUTE，110 C4保留记忆。现012缺pdf三表六列是原域实现缺漏，不是新权限域，明确准许仅html_owner的SELECT(id,version_id,status,page_count)候选表、SELECT(candidate_id)核对页、SELECT(version_id)抽取页，无grant option/table SELECT/正文/DML/成员变更。只改012声明及本合成main精确补丁，不改003/010/011；真实资格与列反例/旧主体权限必须补证。无需用户重批原包。

旧preview25/CID742543c2…保UNKNOWN/R60/一次使用和旧根blocked。主控只读检索旧Docker日志为空，不能补造kernel/EOF，不签停止或node_busy。明确允许下一卡在唯一C04测试控制根做其它独立合成验收，条件为12对象/已登记Windows归属已结束与Global排他；属于开发场景隔离，不在产品加换根/跳过UNKNOWN入口，旧结算不动。C04新未知必须先本对象完整救援/恢复，否则停，不能再次换根。

纠正产物/镜像误绑。110规定artifact排未来image且四runtime未变；C03未打开N1若实际资格/verify_package成立且没有旧config预算，可用v2-07打开，生成v2-05与预览v2-07分别真实记录，不强迫模型重发。真的失效/旧budget不同才新生成，旧键/预算不改。

签TASK-111-G11-C04-20261011，沿原C03 A+工程窗口，无并行和新TASK。新完整卡先离线制齐必要修复/夹具，一次PG/API优先正常两链再补剩余矩阵。新综合四小时；剩根2/14、新real3000且累计14400、preview剩19、model/Windows各剩3、frontend剩2、image无新增。仅PG/API/browser各加一次有据修正余量到11/8/7，不增并发/容器/卷/用户数据或付费；旧real10722.158/offline203.452/cleanup48.5337405、global90、旧13元/超限/迟记/时钟缺口保留。

资料、核心与充分矩阵按版本继承，当前稳定完整终审仍未发。本主控产品写/SQL/构建/业务运行0。卡在DocuN/tasks/TASK-111.md保存待转交，预算/权限边界/核证在orchestration-receipt-04，执行完成带回原结果路径。

## 以下保留C03及此前裁定原字节

''',
'DocuS/架构动态文档.MD':f'''# 架构动态文档

文档v1.16，2026-10-11，Asia/Shanghai。需求v1.2、执行动态v2.38，task_model/07。以下v1.15及历史保留。G11有限核心已证，完整业务尚未闭合。

## 受信renderer已运行，资格读取和启动异常仍待修

DEF-027定向关闭：实际纯组装字面替换/完整脚本/CSP与编译包一致，最终v2-07真实机械能ACK、蓝柱/归零、PNG与完整当次停止组合已核。新纯protocol、描述hash、拒绝保整帧与3fps有对应限定原件。未签完整Native/UI、二项图形/XSS或全安全。process.py收尾后新增100ms有界替换只本机验证，不能当全新startup已过。

012预算guard的INSERT/ON CONFLICT问题已通过精确函数补丁与三真实生命周期收口；owner/ACL原件保留，登记DEF-028定向闭合。DEF-029记忆资格闭包缺PDF三表六列读取待补，NOLOGIN HTML owner只添资格计数/状态列，原角色/数据域与禁止旧表写保持；003/010/011不改。逐列ACL差异、正文拒绝与真实完整资格待验，主控此轮只裁定授权未实施GRANT。

DEF-030的启动后登记写失败使管道reader与kernel取证未建立；下一卡在既有JobChild/HostJob完善开始前登记/读者准备和异常排空，不增加平台、镜像或放宽停止门。旧Node场景未触发，旧CID仍UNKNOWN/R60，不能按当前Stopped改树空。

C04工程测试仅在明确唯一隔离控制根继续独立场景，旧根仍blocked且不退款；产品不加未知绕过。artifact四runtime执行包不自动因宿主image变更失效，preview再按实际config/镜像绑定；正常N1可根据真实资格及无旧budget复用，不改旧不可变事实。角色权和UI剩余动态未通过，正常优先、完整后集中独审。

原已采用有限描述/固定计算图形、原四账/Windows监督、隔离/产品3次180秒/ready8/D-10及生产默认关闭不变。Linux/Nginx、用户库/provider/发布没有新许可。

## 以下为v1.15及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.38，2026-10-11，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.16、task_model/07。以下v2.37与原历史保留。

## 111续作03已返回部分通过，续作04待转交

原C03 A+实际Codex/GPT-6窗口已返回97401字节/6cf13c14…，78源/七规则匹配，旧75828字节后缀不改。调度已返回，验收部分通过；DEF-027与机械能核心定向关闭，未通过完整Native/UI或G11。三PNG/ACK、kernel/EOF/wait/die与两Job零任务21项绑定成立；新renderer/v2-07数学图形不重新前置复验。DEF-028预算guard修正定向闭合，DEF-029资格PDF列权、DEF-030启动登记与管道异常仍开放。

已证限定项包括生产协议22类拒绝、真实域/50000步拒绝保帧、source/parent缓存前准确屏障、三次共享预算、并发同key/create回包丢失、同COMMIT旧证据/越权ROLLBACK，按as-run和当前差异继承。N2/最终Native/UI、记忆完整资格/cancel、客户端迟到、剩余故障未闭。当前process的有界等待只有Windows文件证据，不被主控签成全链运行通过。

旧Node preview25/CID742543c2…确已退出metadata但缺kernel/EOF；旧日志查询空，不能补证。旧UNKNOWN/R60/count1及注册根blocked封存，node_busy未触发不算过。主控具体准许C04唯一新测试控制根独立验收，旧对象不动/不退款，产品recover不绕过；12个旧对象只读核止及Windows/Global排他前置仍必需，新未知必须在本根完整救援否则停，不再换根。

现用根12/14、image7/7、PG start9/10、API6/7、browser5/6、model7/10、Windows7/10、frontend3/5、preview create15/34/start13/32、HTTP240/5000、public input22/300/internal21/500、PNG GET0。global90为入口非通过；real10722.158/offline203.452/cleanup48.5337405及旧13元、第一读时缺失/300秒保守margin、root09超时/迟记3次/源码载入缺口保留。本批当前所有实际资源已停止，active_batch null，不代执行层起服务。

签同TASK111/R105 C04，沿有效原C03 A+窗口，待人工转交，未自动派发/开始，TASK112未占。新四小时从首次读取固化，旧93600窗口账增加为108000；末600清场。只剩两真实根各1800，新real3000且累计14400；不加image/model/Windows/preview额度。PG/API/browser各只加一修正余量到11/8/7（新增可用2/2/2），一个PG/卷/preview并发与全部产品安全门保持。权限三表六列由已采用108 C2/110闭包覆盖，主控明确写入新卡而非执行者自行GRANT，不再问原包批准。

正常优先：先制齐六列权、startup与已定界UI夹具；一次PG/API核权/真实异常边界后完成正常两链，再补剩余矩阵，现成证明继承。N1若未变执行包且无旧budget可实际资格核后复用v2-05生成产物在v2-07预览，不假称生成在v2-07；必要才补合成发送。共享状态与最终裁定由主控维护，完整稳定后一次隔离增强终审仍未派。

本批CHG1190—1202，下一1203，证据DocuN/evidence/TASK-111/orchestration-receipt-04/。合同DocuN/tasks/TASK-111.md单一现行入口，旧C03原字节保存同目录prior-TASK-111.md。无用户库、真实付费、安装/特权/Git/删除/发布增量；主控只有读取现成原件/精确metadata和写文档。

## 以下为v2.37及更早历史

'''
}
paths=['DocuN/tasks/TASK-111.md',*prefixes,'DocuS/文档变更记录.MD']
before={p:(ROOT/p).read_bytes() for p in paths}
if sha(before[paths[0]])!='cd8220ab8bc8d5a29e59ca1b12cab0c130d9a17bb7119d5a2c0a2cf5fa7e3098':raise RuntimeError('旧卡被改')
if b'CHG-1190' in before[paths[-1]]:raise RuntimeError('CHG编号已有归属')
for p,b in before.items():
    if (pre/p.replace('/','__')).read_bytes()!=b:raise RuntimeError('写入前共享文档已改变')
draft=(OUT/'effective-contract.md').read_bytes();text=draft.decode('utf-8')
if '*' in text:raise RuntimeError('新文档格式')
required=['## 目标与交付','## 项目、规则与安排','## 背景与最小输入','## 执行范围与明确裁定','## 精确资源与工程预算','## 验证与完整剩余矩阵','## 停止与回传','## 人工与待同步']
if not all(h in text for h in required):raise RuntimeError('完整卡缺节')
reg=f'# 执行动态文档\r\n\r\n{at}，TASK111/R105 C04登记并保存中；不是派发或执行。\r\n\r\n'.encode()
(ROOT/'DocuS/执行动态文档.MD').write_bytes(reg+before['DocuS/执行动态文档.MD'])
(ROOT/'DocuN/tasks/TASK-111.md').write_bytes(draft)
for p,prefix in prefixes.items():(ROOT/p).write_bytes(prefix.replace('\n','\r\n').encode()+before[p])
save('window-assignment.json',dict(TASK='TASK-111',R='R-105',resource='A+，原续作03工程窗口',reason='当前上下文有效，沿同模块接续',
    contract=str(ROOT/'DocuN/tasks/TASK-111.md'),contract_sha256=sha(draft),status='待人工转交',actual_dispatch=False,
    independent_audit=False,original_earlier_windows='继续停写，不并行'))
entries=[
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/receive.py','只读结果/78源/精确对象和旧日志核证，core_acceptance.py与publish.py为同批工具。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/returned-and-core-check.json','交回身份与分层核心原件核对，未复跑。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/core-acceptance.json','21项实际核心/PNG/停止绑定，全过限域接受DEF-027。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/resource-recheck.json','12精确已停对象与旧日志读取，unknown-existing-log-check.json空日志不造证明。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/continuation-budget.json','真实余量与四小时接续，PG/API/browser各一修正余量；scope-and-authority.json明确六列权与测试隔离。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/effective-contract.md','C04完整目标与必须边界，normal优先，证据继承。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/prior-TASK-111.md','C03原25233字节全文历史，不运行旧时窗。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/window-assignment.json','原有效C03 A+窗口待转交，无新独审/并行。'),
 ('DocuN/results/TASK-111-work-decision.md','部分验收/三缺陷状态、最小资格权与旧未知保留、新工程具体许可。'),
 ('DocuN/tasks/TASK-111.md','单一当前C04完整合同，旧卡原字节保留。'),
 ('DocuS/架构动态文档.MD','v1.16记录核心已证、权限/启动异常待修和产物镜像正确绑定。'),
 ('DocuS/执行动态文档.MD','v2.38唯一状态账，C03已返回/C04待转交，所有旧失败与投入保留。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-04/delivery-proof.json','一次历史/路径/预算/源完整核证，主控无产品执行。')]
ledger=ROOT/'DocuS/文档变更记录.MD'
if ledger.read_bytes()!=before['DocuS/文档变更记录.MD']:raise RuntimeError('变更账并行修改')
append='\r\n'+''.join(f'\r\n- CHG-{1190+i:04d}，{at}，Codex编排Agent，{p}。{note}\r\n' for i,(p,note) in enumerate(entries))
ledger.write_bytes(before['DocuS/文档变更记录.MD']+append.encode())
refs=list(dict.fromkeys(re.findall(r'D:/shspic/project_NO3_RetroLume-agent/[A-Za-z0-9_./-]+\.(?:md|json)',text)))
missing=[p for p in refs if not Path(p).is_file()]
if missing:raise RuntimeError('卡引用缺失 '+str(missing))
hist=all((ROOT/p).read_bytes().endswith(before[p]) for p in prefixes)
unchanged=all(info(ROOT/r['path'])['sha256']==r['actual_sha256'] for r in sources)
if not hist or not unchanged or info(report)['sha256']!=received['result']['sha256']:raise RuntimeError('写文档期对象改变')
proof=dict(at=at,contract=info(ROOT/'DocuN/tasks/TASK-111.md'),old_contract=info(OUT/'prior-TASK-111.md'),
    old_contract_exact=(OUT/'prior-TASK-111.md').read_bytes()==before[paths[0]],history_suffixes_exact=hist,
    source_unchanged=78,result_unchanged=True,core_checks=21,DEF_027_closed_limited=True,
    new_create_slots=caps['preview_creates']-received['counts']['preview_creates'],new_start_slots=caps['preview_starts']-received['counts']['preview_starts'],
    new_image_slots=0,new_PG_slots=2,new_API_slots=2,new_browser_slots=2,new_root_slots=2,
    projected_real=received['time_seconds']['real']+3000,global_real_limit=14400,
    checked_local_references=len(refs),status='待人工转交',new_execution=0,product_writes=0,
    CHG_first=1190,CHG_last=1202,next_CHG=1203)
save('delivery-proof.json',proof)
print(json.dumps(proof,ensure_ascii=False))
