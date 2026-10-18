"""只保存已有事实、差异和交接；硬门后不导入或运行产品。"""
from control import ROOT,HERE,write,sha,event,sample,state
from pathlib import Path
import ast,difflib,json,subprocess,time

stamp=sample();index=json.loads((HERE/'changes.json').read_text(encoding='utf-8'))
new_paths=['backend/app/capabilities/embedding.py','backend/app/retrieval/contracts.py','backend/app/retrieval/repository.py','backend/app/retrieval/service.py','backend/app/retrieval/api.py','backend/app/data_exit/schema_profiles.py','backend/migrations/014_step018_retrieval.sql','frontend/src/activities/retrieval-api.ts','frontend/src/activities/RetrievalPanel.tsx','config/integration.example.json',*[f'backend/tests/test_step018_{name}.py' for name in ('embedding_contracts','retrieval_pg','profiles_pg','flows')],'frontend/tests/step018-flow.mjs']
new_paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'backend/tests/fixtures/step018').rglob('*.py')]
paths=set(index)|set(new_paths)
for p in (ROOT/'frontend/dist').rglob('*'):
    if p.is_file():paths.add(p.relative_to(ROOT).as_posix())
entries=[];patch=[]
for relative in sorted(paths):
    path=ROOT/relative;pre=index.get(relative);exists=path.is_file();raw=path.read_bytes() if exists else b''
    row={'path':relative,'pre':pre,'post':{'exists':exists,'bytes':len(raw),'sha256':sha(raw) if exists else None},'new_path_allowed_by_card':relative in new_paths}
    row['changed_from_registered_pre']=None if pre is None else pre['exists']!=exists or pre.get('sha256')!=row['post']['sha256']
    if pre is None:row['pre_registration_limit']='未在changes.json记录首建前条目；保留此前首次创建事实，不追造pre'
    entries.append(row)
    if pre and row['changed_from_registered_pre'] and '/dist/' not in relative:
        before=(HERE/'preimages'/relative).read_bytes() if pre['exists'] else b''
        try:lines=list(difflib.unified_diff(before.decode('utf-8-sig').splitlines(True),raw.decode('utf-8-sig').splitlines(True),fromfile='pre/'+relative,tofile='post/'+relative))
        except UnicodeDecodeError:continue
        patch.extend(lines[:100]);
        if len(lines)>100:patch.append(f'\n[limited diff: {len(lines)-100} further lines omitted; exact pre/post hashes in final-source-manifest.json]\n')
write(HERE/'final-source-manifest.json',{'sample':stamp,'scope':'registered preimages and explicit new product/test paths only; not entire preexisting dirty checkout','entries':entries,'note':'final bytes do not upgrade earlier as-run test identities to final-version acceptance'})
(HERE/'final-changes-limited.diff').write_text(''.join(patch),encoding='utf-8')
bundle=json.loads((HERE/'bundle-3.json').read_text(encoding='utf-8'))
for relative,identity in bundle.items():
    if sha((ROOT/relative).read_bytes())!=identity['sha256']:raise RuntimeError('saved_final_bundle_drift')
schema=ast.parse((ROOT/'backend/app/data_exit/schema_profiles.py').read_text(encoding='utf-8'));constants={}
for node in schema.body:
    if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('MIGRATION_014','VECTOR_EXTENSION_VERSION','R02_EXTRA_SHAPE_SHA'):
        constants[node.targets[0].id]=ast.literal_eval(node.value)
write(HERE/'final-binding.json',{'sample':stamp,'source_manifest_sha256':sha((HERE/'final-source-manifest.json').read_bytes()),'bundle_manifest_sha256':sha((HERE/'bundle-3.json').read_bytes()),'bundle':bundle,'profile_constants':constants,'migration_014_actual_sha256':sha((ROOT/'backend/migrations/014_step018_retrieval.sql').read_bytes()),'source_database_final_profile_basis':'r02-frozen-catalog.json; source ordinary API fifth-start accepted normal loader','compat_database_limit':'final additional SELECT teaching_commands grant not applied to compat; earlier nonempty upgrade proof remains as-run only','new_audit':'NOT_RUN','S_complete':False})

def case(cid,scope,links=(),gap='',status='NOT_RUN'):
    return {'id':cid,'S_status':status,'scope':scope,'new_evidence':list(links),'remaining':gap,'Q_status':'NOT_ENABLED_NOT_RUN','frozen_scenario_passed':False}
unit='root-01/unit-result.json';pg='root02-retrieval-proof.json';flows='root04-flow-proof.json';browser='browser-2/proof.json'
cases=[
case('L01','N学习状态链的合成结构/真实PG/Native/HTTP；浏览器至接受路径',[flows,browser],'未覆盖冻结wrong_answer、targeted变体、新实例、最终bundle完整链或L10；Q语义未跑','PARTIAL'),
case('L02','三种速度等价正例',gap='冻结三答及各自真实服务认可未跑'),
case('L03','三种单位/数量级反例',gap='冻结反例未跑'),
case('L04','否定/不确定',gap='冻结否定及不确定传播未跑'),
case('L05','保守反馈及保留理由的一个HTTP路径',[flows],'两份未暴露不同实例推进、同键不重复计分、assisted分支未跑','PARTIAL'),
case('L06','概念/逻辑三答',gap='C未导入，三答未跑'),
case('L07','程序推理二答',gap='P未导入，二答未跑'),
case('L08','同名Java歧义与范围修订',gap='两份Java未导入；澄清与失效矩阵未跑'),
case('L09','不足/冲突双源',gap='N-CONFLICT未导入，冻结不足/冲突未跑'),
case('L10','固定预览正常operator入口',['synthetic/operator/api-proof.json','root04-preview-host.json'],'验签与配置就绪已证明；未生成产物/创建宿主/控件ACK/PNG/停止链','PARTIAL'),
case('I01','用N的v2面试状态链，含一次probe及finish',[flows],'冻结R+M目标、incomplete/supported回答和选用记忆未跑；不是I01通过','PARTIAL'),
case('I02','R缺证/自报',gap='R分支和测量缺口未跑'),
case('I03','虚构收益/范围错引',gap='冻结范围外M及利润50%错引未跑'),
case('X01','N文本导入事实',[pg],'批次坏UTF8、PDF两页/补充、替换成功失败未跑','PARTIAL'),
case('X02','新profile记忆引用实现',gap='选择记忆的真实两域链、修订/撤销/删除晚到未跑'),
case('X03','索引/query重复只读与缓存零调用的串行路径',[pg],'两同键并发、异正文、域semantic slot及batch竞争未跑','PARTIAL'),
case('X04','新增无效结果UNKNOWN规则与UI身份围栏实现',gap='冻结scope/goal/source/cancel晚到与最终bundle切换矩阵未跑'),
case('X05','合同结构与自然暴露的发送前拒绝',[unit,'root02-index-attempt3.json'],'缺配置/预算/owner等完整定向矩阵未跑；旧模型值约束错误已修','PARTIAL'),
case('X06','收到但记录失败后UNKNOWN保留的真实故障',[pg,'root02-index-attempt4.json','root02-index-attempt5.json'],'超时/响应失联/取消晚到全组未跑；不能将初版误判not_sent当正确证据','PARTIAL'),
case('X07','持久账及UNKNOWN预留',[pg,flows],'整步query+model预算预览不足门、四账耗尽/重开未证明；执行资源硬预算已超额','PARTIAL'),
case('X08','面试ask COMMIT后回读失败503，修复权限后GET复用已提交问题',[flows,'source-interview-before-read-acl.json'],'不是三类显式丢HTTP回包注入；索引/answer/feedback最终bundle恢复未跑','PARTIAL'),
case('X09','同source多次API启动，保留目标/路径/已提交ask和预算',[flows,'events.jsonl'],'未完成规定停止同CID/volume再启动后新的合格feedback和UNKNOWN完整核销；最终bundle重开未跑','PARTIAL'),
case('X10','新增派生向量/007删除传播实现',gap='实际删源、跨活动cache/引用抑制、snapshot/overlay恢复未跑'),
case('X11','Docker唤醒内存门拒启后复核；固定端口独占检查',['events.jsonl','final-resource-stop.json'],'端口三型、未知DDL/迁移回滚完整矩阵未跑；本卡持有清场超时另列偏差','PARTIAL'),
case('X12','独立kind/512维/typed凭证/真实默认关闭合同',[unit,'root03-flow-contracts.txt'],'恶意源/伪字段/embedding各父消费/readonly写拒完整PG与bundle矩阵未跑','PARTIAL'),
case('P01','compat非空model/tool/unknown/domain升级、R01预升级包',['compat-catalog-before014.json','compat-catalog-after014.json','compat-r01-package-receipt.json'],'旧数据样本没有完整记忆/面试/HTML；compat未补最终invoker读取授权，不能签最终014全兼容','PARTIAL'),
case('P02','R01包已生成，reader/registry设计实现',['compat-r01-package-receipt.json'],'全新r01目标尚未创建/恢复/seal/应用查看，root05草案未运行','PARTIAL'),
case('P03','R02 registry/codec/loader及float32在source可回读',[pg,'r02-frozen-catalog.json'],'R02 checkpoint未生成；r02/fault目标未创建；往返/删源overlay/坏维度或hash前检未跑','PARTIAL')]
if len(cases)!=28 or len({x['id'] for x in cases})!=28:raise RuntimeError('case_index_incomplete')
for c in cases:
    c['new_evidence']=[str(HERE/p) for p in c['new_evidence'] if (HERE/p).exists()]
inheritance={
'G11':'TASK-112-result.md / TASK-111-G11-final-acceptance.md及TASK-112-work-decision.md；仅既有已关闭边界，不代替L10本轮集成',
'STEP017':'TASK-115-result.md及TASK114续作03有效原件；仅旧R01/围栏/只读边界，不代替R02/正常重开',
'STEP018设计':'TASK-116 design/acceptance-contract.md冻结预期；设计NOT_RUN不转为当前验证通过'}
write(HERE/'case-index.json',{'schema':'TASK117.case-index.v1','sample':stamp,'frozen_contract':'DocuN/evidence/TASK-116/design/acceptance-contract.md','S_candidate':'INCOMPLETE_HARD_BUDGET_STOP','Q':'NOT_ENABLED','passed_frozen_scenarios':0,'cases':cases,'inherited_scope':inheritance,'master_final_acceptance':'NOT_REQUESTED_NOT_SIGNED'})

git_head=subprocess.run(['git','--no-optional-locks','rev-parse','HEAD'],cwd=ROOT,capture_output=True,check=True).stdout.decode().strip()
status=subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false','status','--porcelain=v1','--untracked-files=normal'],cwd=ROOT,capture_output=True,check=True).stdout
(HERE/'git-status-final.txt').write_bytes(status)
write(HERE/'git-final.json',{'sample':stamp,'head':git_head,'status_sha256':sha(status),'lines':len(status.splitlines()),'git_writes':0,'preexisting_dirty_changes_not_reset':True})
rules=json.loads((HERE/'receipt.json').read_text(encoding='utf-8'))['rules']
write(HERE/'final-rules-identity.json',{'sample':stamp,'rules':[{'path':r['absolute_path'],'frozen_sha256':r['sha256'],'current_sha256':sha(Path(r['absolute_path']).read_bytes()),'unchanged':sha(Path(r['absolute_path']).read_bytes())==r['sha256']} for r in rules]})
resources=state()['resources'];intervals=[]
for r in resources:
    for x in r.get('holding_intervals',[]):intervals.append((x['start']['mono_ns'],x['end']['mono_ns']))
merged=[]
for a,b in sorted(intervals):
    if merged and a<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],b)
    else:merged.append([a,b])
write(HERE/'final-holding-union.json',{'sample':stamp,'basis':'两CID已登记start attempt至精确stop/Pid0的全部持有区间并集；不扣除无人操作等待','merged_mono_ns':merged,'seconds':sum((b-a)/1e9 for a,b in merged),'cap_seconds':14400,'over_cap':sum((b-a)/1e9 for a,b in merged)>14400,'original_conservative_root_intervals_retained':True})
event('saved_partial_delivery',case_index_count=28,source_entries=len(entries),final_bundle=3,frozen_scenarios_passed=0,S_complete=False)
print(json.dumps({'case_count':len(cases),'source_entries':len(entries),'source_manifest_sha':sha((HERE/'final-source-manifest.json').read_bytes()),'binding_sha':sha((HERE/'final-binding.json').read_bytes())}))
