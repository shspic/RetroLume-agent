"""发布单一现行人工任务合同，保存旧卡原字节并维护唯一共享账。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, re

ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(b):return hashlib.sha256(b).hexdigest()
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=digest(b))
timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat()
budget=read(OUT/'continuation-budget.json')
check=read(OUT/'input-and-resource-check.json')
draft=(OUT/'effective-contract.md').read_bytes()
text=draft.decode('utf-8')
if not all(heading in text for heading in ('## 目标与交付','## 项目、规则与接收安排','## 背景与最小充分上下文','## 执行边界与资源','## 验证、证据与审计关系','## 停止与回传','## 必要人工与待同步信息')):
    raise RuntimeError('完整卡七节缺失')
if '*' in text:raise RuntimeError('新卡含禁止格式')
for r in check['sources']:
    if digest(Path(r['path']).read_bytes())!=r['actual']:raise RuntimeError('源漂移 '+r['path'])
result=ROOT/'DocuN/results/TASK-111-result.md'
if info(result)['sha256']!=check['result_sha256']:raise RuntimeError('结果已改变')
if budget['prior_used']!=read(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')['counts']:raise RuntimeError('运行账已改变')

paths=('DocuN/tasks/TASK-111.md','DocuN/results/TASK-111-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD')
old={rel:(ROOT/rel).read_bytes() for rel in paths}
if digest(old[paths[0]])!='513d4fb39daa7e72362e778ef5a3ee2961c08acee6388f37de09f82d0b68022d':raise RuntimeError('旧卡漂移')
if b'CHG-1179' in old[paths[-1]]:raise RuntimeError('编号已占')
pre=OUT/'before-documents';pre.mkdir(exist_ok=False)
for rel,b in old.items():(pre/rel.replace('/','__')).write_bytes(b)
(OUT/'prior-TASK-111.md').write_bytes(old[paths[0]])

prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK-111 / R-105 续作03完整工程许可

{timestamp}，Codex编排Agent。用户在根因复盘后询问下一步，按已采用G11-P110同范围继续工程编排。DEF-027确定根因、66项源/七规则/结果身份及精确资源停止条件已核；前置是针对已知缺陷修复，不是当前实现已通过。签发TASK-111-G11-C03-20261011，待人工转交新A+工程窗口，原111窗口停写；不重批110，不派审计或TASK112。

现行完整合同统一在DocuN/tasks/TASK-111.md，旧62036字节/SHA513d4fb3…保存在DocuN/evidence/TASK-111/orchestration-continuation-03/prior-TASK-111.md，仅历史。新卡不嵌套旧过期入口，旧预算/失败/原件和结果75828字节仍保持。关联七规则版本不变。

本次具体增量是8小时综合窗与一套足够覆盖实际缺口及普通修正的工程名额。真实根累计14（已8，新增6）/每根1800/新增真实7200且累计real14400，build7（已3，新增4），PG start10（已7，新增3），API7（已3，新增4），主browser6（已3，新增3），frontend5（已2，新增3），合成发送与Windows各10（已各6，新增各4），preview create34/start32（已4/2，新增各30，新name15—44）。计划基线至多22加8有据修正，全部不必消费。Reaper分组与离线次数在C03为记录项；实际preview60/停止诊断15、根/总窗与隔离硬门保持。C03只增加前向许可，不返旧失败/次数/unknown/13元，旧deadline已经历史。

顺序为实际字面组装/脚本字节/CSP等价核证→不发模型/不启主UI的生产控制最小真实renderer闭环→最终镜像下正确新活动和Native两正常UI链→同卡完成剩余M矩阵/有据修正/清场。任何旧config不改budget造通过，未实现的故障入口先制齐再触发。PG可跨根托管或在已证阶段后有意结束等待长离线准备，不在普通错误或自行300秒门就消耗start。

资源仍一个现成PG/卷、一时一个preview、原固定镜像来源/权限与无用户库/付费/网络安装/Git/删除/发布。产品3次/180秒、reserve30—60、ready8/D-10、UNKNOWN保R与完整止树不降。候选仍默认关闭；完整稳定后集中隔离终审。本主控产品改写/测试/SQL/启动全部0。

预算与核证在DocuN/evidence/TASK-111/orchestration-continuation-03/。卡内完成或真正停止才回结果路径，普通修正连续完成；执行者不能自签最终验收。以下复盘及原裁定完整保留原字节，只有本C03为新的实际入口许可。

## 以下为此前裁定历史

''',
'DocuS/架构动态文档.MD':f'''# 架构动态文档

文档v1.15，2026-10-11，Asia/Shanghai。需求v1.2、执行动态v2.37、task_model/07。以下v1.14及原历史保留；产品仍候选，DEF-027开放。

## G11按已证根因恢复工程，不改变采用方案

续作03先修实际宿主字面组装并核固定脚本/style/CSP与Python产物字节一致，再取得真实renderer计算/ACK/PNG/停止，之后才主UI和剩余故障。生产镜像冻结后安排正确新合成活动；旧budget的image/load绑定不能reset或绕过。窗口与工程预算变化不构成产品已修或通过证据。

已有有限数据/固定程序、四表/角色/短事务和原G3—G10主权、安全/隔离/停止及产品预算保持。原已证生成/事务/权限/限定升级按字节继承，故障占位仍待执行层补齐，不增加平台或换引擎。原111实现窗口停写，新A+唯一工程窗口承接单一现行合同；稳定完整候选再一次隔离终审。

精确资源仍本卡PG/卷与独占preview，新工程名额及正确入口详见DocuN/tasks/TASK-111.md和同卡continuation-budget.json。生产默认HTML关闭，发布、Linux/Nginx、用户库和真实provider仍未放行，主控没有接管实现。

## 以下为v1.14及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.37，2026-10-11，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.15、task_model/07。以下v2.36及原历史保留。

## 111续作03已登记待转交，原卡历史封存

根因复盘已完成并核DEF-027开放，用户询问下一步后按已采用范围组织完整工程续作。同TASK111/R105，A+最强且胜任工程的执行Agent，全新会话；原111窗口停写，无并行产品执行或审计。新卡已保存待人工转交，没有自动派发、接收、开始或新运行事实。TASK112未占。

现行唯一合同DocuN/tasks/TASK-111.md，旧62036字节/513d4fb3…保存同卡orchestration-continuation-03/prior-TASK-111.md，不照旧截止/root运行。源66/66、规则7/7、结果75828字节/31a88d3f…仍匹配；PG与preview03/14只读核实停止。当前代码/证据仍部分，DEF-027修后动态及完整M01—M12未通过，旧正常remote/PNG/input0不改。

C03工程许可TASK-111-G11-C03-20261011，一体8小时从实际首次读卡固化，原总体64800明确增加28800为93600，业务末600秒清场；原时窗、未知与超限保持历史。新增真实≤7200、累计real≤14400，根累计14已8，每根1800；build7已3、PG start10已7、API7已3、主browser6已3、frontend5已2、model合成10已6、Windows10已6、preview create34/start32已4/2，新名字15—44仅一次各30名额。22基线加8相关修正上界核算，达到成果即停。Reaper分组2及offline批18继续记录，本C03不另作重复硬门；单preview安全时间、工程根/总窗/一时一个与物理停止要求仍硬门。

当前累计global86根、real6541.282/offline200.828/cleanup44.4247405及旧13元/失败/UNKNOWN保留，原PG/卷各1、HTTP156/5000、PNG0/3000、公开input0/300、内部input0/500不清。新工程上限不是用量，实际新使用0。低风险预检/离线准备不占真实根，真正build/start/SQL/业务按入口记真实；旧预检失败根不追返。

执行顺序为修真实组装根因与字节绑定→最小生产控制真实renderer闭环→最终部署新合成活动与两正常Native/UI→完整剩余矩阵及普通修正→清场→新隔离集中终审。现成未变证明继承，正确活动config/allocator/控制门一次核清，不再靠加等待或逐次加一次PG。新许可不增加用户库、付费、安装、特权、Git、删除或公开发布，产品3次180秒/ready8/D-10/UNKNOWN保R不变。

本批CHG1179—1189，下一1190。证据DocuN/evidence/TASK-111/orchestration-continuation-03/，状态待人工转交。主控只编排核证与写文档，没有产品写入或产品验证；执行完成带回原结果路径即可，不要求用户再次批准110。

## 以下为v2.36及更早历史

'''
}

# 先登记已有TASK的当前准备，再保存完整合同，随后状态改成真实待转交。
registration=f'''# 执行动态文档

文档v2.37准备记录，{timestamp}。TASK111/R105续作03已登记，当前保存现行合同；拟安排新A+工程窗口。不是实际派发或运行。

## 以下为v2.36历史

'''.replace('\n','\r\n').encode('utf-8')
(ROOT/'DocuS/执行动态文档.MD').write_bytes(registration+old['DocuS/执行动态文档.MD'])
if digest((ROOT/'DocuN/tasks/TASK-111.md').read_bytes())!=digest(old['DocuN/tasks/TASK-111.md']):raise RuntimeError('写卡前旧卡改变')
(ROOT/'DocuN/tasks/TASK-111.md').write_bytes(draft)
if (ROOT/'DocuN/tasks/TASK-111.md').read_bytes()!=draft:raise RuntimeError('完整卡保存失败')
for rel,prefix in prefixes.items():
    if rel=='DocuS/执行动态文档.MD':
        if not (ROOT/rel).read_bytes().endswith(old[rel]):raise RuntimeError('登记后历史改变')
    elif (ROOT/rel).read_bytes()!=old[rel]:raise RuntimeError('共享文件并行改变')
    (ROOT/rel).write_bytes(prefix.replace('\n','\r\n').encode('utf-8')+old[rel])
assignment=read(OUT/'window-assignment.json')
assignment.update(status='待人工转交',contract=str(ROOT/'DocuN/tasks/TASK-111.md'),contract_sha256=digest(draft),old_window_write_access='本C03原窗口停写，不并行')
(OUT/'window-assignment.json').write_text(json.dumps(assignment,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

entries=[
('DocuN/evidence/TASK-111/orchestration-continuation-03/prepare_card.py','只读断点与预算脚本；publish_card.py完成串行合同保存及历史保全。'),
('DocuN/evidence/TASK-111/orchestration-continuation-03/input-and-resource-check.json','66源/七规则/结果与三个精确资源停止核证，新运行0。'),
('DocuN/evidence/TASK-111/orchestration-continuation-03/continuation-budget.json','完整前向工程增量、基线与普通修正余量，旧账不返。'),
('DocuN/evidence/TASK-111/orchestration-continuation-03/window-assignment.json','新A+工程会话待转交，原窗口停写，不冒独立审计。'),
('DocuN/evidence/TASK-111/orchestration-continuation-03/effective-contract.md','单一现行完整合同，修根因→最小真实闭环→完整矩阵。'),
('DocuN/evidence/TASK-111/orchestration-continuation-03/prior-TASK-111.md','原62036字节任务卡及冻结通知原字节历史，不执行旧入口。'),
('DocuN/results/TASK-111-work-decision.md','签发C03具体合成许可，不重批采用；全成果稳定后集中终审。'),
('DocuN/tasks/TASK-111.md','替换为唯一当前完整七节，旧卡已原字节封存，新实际0。'),
('DocuS/架构动态文档.MD','v1.15描述正确组装与部署绑定、阶段顺序，产品仍候选。'),
('DocuS/执行动态文档.MD','v2.37唯一状态账，新C03待转交、预算新旧分清、失败/费用保留。'),
('DocuN/evidence/TASK-111/orchestration-continuation-03/delivery-proof.json','卡/预算/路径/历史和源未改的一次一致性核证。')]
append='\r\n'+''.join(f'\r\n- CHG-{1179+i:04d}，{timestamp}，Codex编排Agent，{rel}。{reason}\r\n' for i,(rel,reason) in enumerate(entries))
if (ROOT/paths[-1]).read_bytes()!=old[paths[-1]]:raise RuntimeError('变更账并行改变')
(ROOT/paths[-1]).write_bytes(old[paths[-1]]+append.encode('utf-8'))

references=re.findall(r'D:/shspic/project_NO3_RetroLume-agent/[A-Za-z0-9_./-]+\.(?:md|json)',text)
references=list(dict.fromkeys(references))
missing=[p for p in references if not Path(p).is_file()]
if missing:raise RuntimeError('任务卡必要文件不可达 '+str(missing))
history=[dict(path=rel,old_suffix_unchanged=(ROOT/rel).read_bytes().endswith(old[rel])) for rel in prefixes]
if not all(r['old_suffix_unchanged'] for r in history):raise RuntimeError('正式文档历史未保全')
if (OUT/'prior-TASK-111.md').read_bytes()!=old[paths[0]]:raise RuntimeError('旧合同未保全')
if info(result)['sha256']!=check['result_sha256']:raise RuntimeError('执行者结果改变')
source_ok=all(digest(Path(r['path']).read_bytes())==r['actual'] for r in check['sources'])
if not source_ok:raise RuntimeError('产品源在文档写入期改变')
caps=budget['cumulative_caps'];used=budget['prior_used']
proof=dict(at=timestamp,contract=dict(path=str(ROOT/'DocuN/tasks/TASK-111.md'),**info(ROOT/'DocuN/tasks/TASK-111.md')),
    old_contract=dict(**info(OUT/'prior-TASK-111.md'),original_bytes_exact=True),
    historical_suffixes=history,source_files_unchanged=66,result_unchanged=True,rules_matched=7,
    new_preview_available=caps['preview_creates']-used['preview_creates'],new_start_available=caps['preview_starts']-used['preview_starts'],
    baseline_plus_repairs=budget['planned_baseline_ceiling']+budget['related_repair_reserve'],
    projected_real=budget['prior_time_seconds']['real']+budget['new_real_limit_seconds'],cumulative_real_limit=budget['cumulative_real_limit_seconds'],
    local_references_checked=len(references),single_current_contract=True,status='待人工转交',
    actual_new_execution=0,product_writes=0,product_tests=0,CHG_first=1179,CHG_last=1189,next_CHG=1190)
if proof['projected_real']>proof['cumulative_real_limit'] or proof['new_preview_available']!=proof['baseline_plus_repairs']:raise RuntimeError('预算算术错误')
(OUT/'delivery-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False))
