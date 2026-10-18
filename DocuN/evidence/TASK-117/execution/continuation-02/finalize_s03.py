"""S03时间门关闭后只保存成果与真实未闭项，不启动业务或改旧证据。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,json,time,hashlib,difflib,copy
N=Path(__file__).resolve().parent;E=N.parent;R=E.parents[3]
sys.path[:0]=[str(E),str(R/'backend')]
import control as c
from app.data_exit.control import ControlHub

def identity(p):
    return {'exists':p.is_file(),'bytes':p.stat().st_size if p.is_file() else 0,'sha256':c.sha(p.read_bytes()) if p.is_file() else None}
def link(name):return str((N/name).resolve())
def union(intervals):
    result=[]
    for a,b in sorted(intervals):
        if result and a<=result[-1][1]:result[-1][1]=max(result[-1][1],b)
        else:result.append([a,b])
    return {'intervals_mono_ns':result,'seconds':sum(b-a for a,b in result)/1e9}

def main():
    assert not (N/'result-save-receipt.json').exists(),'不可覆盖已交回结果'
    stamp=c.sample();v=c.state();s=c.active_segment(v);assert s and 'S03' in s['permit'] and v['active_root'] is None
    stop_binding=json.loads((N/'final-resource-stop-binding.json').read_text());stop_path=Path(stop_binding['path'])
    assert c.sha(stop_path.read_bytes())==stop_binding['sha256'];stop=json.loads(stop_path.read_text());assert stop['all_stopped']
    raw=(N/'before-result.md').read_bytes();report=R/'DocuN/results/TASK-117-result.md'
    assert len(raw)==31949 and c.sha(raw)=='5f2e0a19f893dcd6634345b86149d9a35de41354cb50f2694f76a024ba1c0c8d'
    assert report.read_bytes()==raw,'结果已被其他写者修改，停止覆盖'
    rules=json.loads((R/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    assert all(c.sha(Path(x['absolute_path']).read_bytes())==x['sha256'] for x in rules)
    receipt=json.loads((N/'receipt.json').read_text());assert c.sha((R/'DocuN/tasks/TASK-117.md').read_bytes())==receipt['inputs']['DocuN/tasks/TASK-117.md']['sha256']
    before=json.loads((N/'before-budget.json').read_text());old_manifest=json.loads((E/'continuation-01/final-source-manifest.json').read_text())
    changes=json.loads((N/'changes.json').read_text());paths={x['path'] for x in old_manifest['entries']}|set(changes)
    paths.update(p.relative_to(R).as_posix() for p in N.glob('*.py'))
    paths.update(p.relative_to(R).as_posix() for p in (N/'as-run').glob('*.py'))
    paths.update(p.relative_to(R).as_posix() for p in (R/'frontend/dist').rglob('*') if p.is_file())
    paths.add('backend/tests/test_step018_term_prefix.py')
    old_rows={x['path']:x['post'] for x in old_manifest['entries']};rows=[];diff=[]
    for relative in sorted(paths):
        p=R/relative;post=identity(p);pre=changes.get(relative)
        row={'path':relative,'S03_pre':pre,'S02_post':old_rows.get(relative),'post':post,'changed_from_S02':old_rows.get(relative)!=post}
        if pre and pre.get('exists'):
            backup=R/pre['backup'];assert identity(backup)['sha256']==pre['sha256']
            if 'frontend/dist/' not in relative:
                try:diff.extend(difflib.unified_diff(backup.read_text(encoding='utf-8-sig').splitlines(True),p.read_text(encoding='utf-8-sig').splitlines(True) if p.is_file() else [],fromfile='S03-pre/'+relative,tofile='S03-post/'+relative))
                except UnicodeError:pass
        elif relative not in old_rows:
            row['new_file_basis']='本轮新增辅助入口或build6产物；没有旧S02对象，不追造首次pre时间'
            if p.suffix=='.py' and p.is_file():diff.extend(difflib.unified_diff([],p.read_text(encoding='utf-8').splitlines(True),fromfile='/dev/null',tofile='S03-new/'+relative))
        rows.append(row)
    (N/'source-changes.diff').write_text(''.join(diff),encoding='utf-8')
    c.write(N/'final-source-manifest.json',{'sample':stamp,'scope':'继承113项及S03必要产品/夹具/控制器/正式build6；非整仓验收','entries':rows,'source_pre_limit':'新增辅助文件没有伪造提前pre；源码和as-run以各原始回执及上轮manifest分别绑定'})
    bundle=json.loads((N/'bundle-6.json').read_text());assert all(identity(R/x['path'])['sha256']==x['sha256'] for x in bundle['files'])
    # 从已保存真实HTTP投影核对中性结果；原错误保留，不重发plan。
    neutral_ids={'c430ffb3-c9de-4ff0-aa32-8ac76b95cd86':('L08','clarification'),'23e836e1-682b-4a65-8e25-c0f8166602a2':('L09-insufficient','no_evidence'),'0ed0b088-c535-48fc-83f6-d2ca82435c3e':('L09-conflict','conflict')}
    found={}
    for p in (N/'root16-normal').glob('*.json'):
        if p.name=='proof.json':continue
        obj=json.loads(p.read_text());w=obj.get('response')
        if not isinstance(w,dict) or w.get('activity_id') not in neutral_ids or not obj.get('path','').endswith('/teaching/workspace'):continue
        reason=w.get('reason');aid=w['activity_id']
        if reason and reason.get('body',{}).get('result_type')==neutral_ids[aid][1]:
            assert reason['qualification']=='current' and w['head']['path_record_id'] is None
            found[aid]={'case':neutral_ids[aid][0],'expected':neutral_ids[aid][1],'actual_reason':reason,'head':w['head'],'original_HTTP':str(p),'sha256':c.sha(p.read_bytes()),'original_status':obj['status'],'reissued_POST':False}
    assert len(found)==3;c.write(N/'neutral-results-readback.json',{'sample':stamp,'status':'真实原HTTP事实核对通过；原夹具错误不删除','results':list(found.values()),'L08_scope_clarification_followup':'NOT_RUN','Q':'NOT_ENABLED'})
    hub=ControlHub(E/'synthetic/source-control');hs=hub.state()
    assert hs['selection'] is None and hs['fence'] is None
    targets=[{k:t.get(k) for k in ('target_id','slot_id','cid','state','temporary_credentials_revoked','job_id','schema_profile')} for t in hs['targets'].values()]
    assert {t['slot_id']:t['state'] for t in targets}=={'r01':'sealed','r02-fault':'failed','r02':'failed'}
    jobs=[{k:j.get(k) for k in ('job_id','kind','state','stage','error_code')} for j in hs['jobs'].values()]
    c.write(N/'restore-final-disposition.json',{'sample':stamp,'targets':targets,'jobs':jobs,'selection':None,'fence':None,'failed_targets_never_reused':True,'source_activation_attempted':False,'R01_application_GET':'NOT_RUN','R02_success_roundtrip':'FAILED_component_timeout_30s','diagnostic_limit':'准确失败位置为restore._load组件内逐行INSERT后30秒检查；617行包，不推断某个SQL或根因已确定'})
    c.write(N/'metadata-corrections.json',{'sample':stamp,'items':[{'path':link('preview-recheck-intent.json'),'original_sha256':c.sha((N/'preview-recheck-intent.json').read_bytes()),'error':'复制入口时reason残留已选R02/compat文案','correct':'本次实际启动source原CID；R02此前装载失败，selector/fence均空；没有启动compat或激活R01/R02。原文件保留。'},{'paths':['preview_source_and_r01.py','remaining.py'],'error':'夹具将公开DataContext.current_mode误读为mode，API18首个会话检查KeyError','correct':'该动作未创建父成果/预览或激活；后续代码未执行。源码未冒动态通过。'},{'paths':['L08-ambiguity-error.txt','L09-insufficient-error.txt','L09-conflict-error.txt'],'error':'中性plan保存在reason投影；夹具误读proposal=None','correct':'只从原HTTP回执核对reason.body.result_type及current；不重新POST，不抹去原失败。'},{'paths':['root14','root15','root16'],'error':'S03复制夹具的部分事件名/schema仍含S02','correct':'实际执行段由主budget、原根ID、S03receipt及continuation-02路径唯一绑定；不追改事件。'}]})
    c.write(N/'PDF-unclosed.json',{'sample':stamp,'status':'BLOCKED_NO_NEW_CAUSE_NOT_RETRIED','original_HTTP_failures':2,'third_HTTP_attempt':False,'prior_isolated_probe':link('../continuation-01/pdf-launch-diagnosis.json'),'observation':'原API环境TRACE_PG=1；孤立worker成功不等同HTTP。现夹具排除PDFworker自动安装，仍无足够证据把超时唯一归因trace，按卡冻结PDF依赖。','security_limits_unchanged':True})
    # 只记录可证的离线工作，明确排除资源全停的用户中断间隔。
    rollout=Path('C:/Users/28432/.codex/sessions/2026/10/12/rollout-2026-10-12T01-41-26-01a12c0e-22b8-7e71-849b-0163931d12c7.jsonl')
    prior_last=None
    for line in rollout.open(encoding='utf-8'):
        item=json.loads(line);pay=item.get('payload',{})
        ts=item.get('timestamp','')
        if '2026-10-15T14:19:00'<=ts<'2026-10-15T20:00:00' and item.get('type')=='response_item' and pay.get('type') in ('function_call','custom_tool_call'):
            prior_last=ts
    assert prior_last is not None
    plan_stamp=json.loads((N/'root16-plan-and-as-run.json').read_text())['sample']
    utc_stamp=datetime.fromisoformat(stamp['utc'])
    old_end=stamp['mono_ns']-int((utc_stamp-datetime.fromisoformat(prior_last)).total_seconds()*1e9)
    spans=sorted((max(plan_stamp['mono_ns'],x['start_mono_ns']),min(old_end,x['end_mono_ns'])) for key in ('runtime_intervals','offline_intervals') for x in v[key] if x.get('segment')==s['permit'] and x['end_mono_ns']>=plan_stamp['mono_ns'] and x['start_mono_ns']<=old_end)
    point=plan_stamp['mono_ns'];new_offline=[]
    for a,b in spans+[(old_end,old_end)]:
        if a>point:new_offline.append({'root':None,'segment':s['permit'],'start_mono_ns':point,'end_mono_ns':a,'seconds':(a-point)/1e9,'basis':'上一段可证的非运行准备/保存空档保守计入；排除之后等待用户接续间隔'})
        point=max(point,b)
    resume_pair={'utc':'2026-10-15T21:44:34.188106+00:00','mono_ns':33574156000000}
    new_offline.append({'root':None,'segment':s['permit'],'start_mono_ns':resume_pair['mono_ns'],'end_mono_ns':stamp['mono_ns'],'seconds':(stamp['mono_ns']-resume_pair['mono_ns'])/1e9,'basis':'新用户接续后只读断点/清场/保存；业务门早已关闭，超额如实登记'})
    v['offline_intervals'].extend(new_offline)
    runtime=sum(x['seconds'] for x in v['runtime_intervals'] if x.get('segment')==s['permit'])
    offline=sum(x['seconds'] for x in v['offline_intervals'] if x.get('segment')==s['permit'])
    elapsed=(stamp['mono_ns']-s['start_mono_ns'])/1e9
    pg=[]
    for resource in v['resources']:
        for span in resource.get('holding_intervals',[]):
            if span.get('segment')==s['permit']:pg.append((span['start']['mono_ns'],span['end']['mono_ns']))
    budget={'sample':stamp,'S01':{'activity_seconds':37651.0027854,'runtime_conservative_seconds':16219.360,'offline_seconds':1724.875,'old_overruns_preserved':True},'S02':{'activity_seconds_at_return':17303.702146,'runtime_conservative_seconds':5702.094,'offline_seconds':821.686},'S03':{'permit':s['permit'],'activity_clock_elapsed_seconds':elapsed,'activity_cap_seconds':21600,'activity_clock_overrun_seconds':max(0,elapsed-21600),'runtime_conservative_seconds':runtime,'runtime_cap_seconds':10800,'offline_recorded_seconds':offline,'offline_cap_seconds':3000,'offline_overrun_seconds':max(0,offline-3000),'PG_CID_union':union(pg),'new_roots':[14,15,16],'new_root_cap':4,'original_start_and_deadlines_preserved':True,'counts':v['counts'],'counts_added':{k:v['counts'][k]-s['baseline_counts'][k] for k in v['counts']},'caps':s['cumulative_caps']},'cumulative':{'activity_clock_seconds':54954.7049314+elapsed,'runtime_conservative_seconds':21921.454+runtime,'offline_seconds':2546.561+offline,'offline_all_task_cap':7200},'interruption':{'last_prior_tool_utc':prior_last,'resume_pair':resume_pair,'resources_were_stopped':True,'gap_is_not_runtime_or_offline':True,'activity_guard':'原S03 elapsed门未重置，因此接续时已关闭；未把等待间隔冒PG持有'},'provider_calls_actual':0,'fee_actual':0,'Q':'NOT_ENABLED'}
    c.write(N/'final-budget-observed.json',budget)
    old_index=json.loads((N/'before-case-index.json').read_text());cases=[]
    facts={
      'L01':('S_PG_HTTP_NATIVE_COMPLETE_U_PARTIAL','新N两域教学错答/针对/曝光/360与240新实例、末评价/理由已持久；旧过期活动不追续','最终bundle6 U缺；进度最后节点理由需区分无后继与不足',['L01-L05-I01-X09-final.json','browser-5/proof.json','browser-8/proof.json']),
      'L02':('S_DETERMINISTIC_INHERITED_Q_OPEN','复用未变确定换算与v3有限输入协议；当前主链有1/2/3/4m/s事实','完整等价正例真实供应商语义待Q',[]),
      'L03':('S_DETERMINISTIC_INHERITED_Q_OPEN','主链真实单位错答及既有反例/量纲检查有效','开放解释语义待Q',[]),
      'L04':('S_DETERMINISTIC_INHERITED_Q_OPEN','既有否定/不确定parser保守unchecked及v3合成协议有效','实际供应商语义待Q',[]),
      'L05':('S_COUNTS_VERIFIED_REASON_REVIEW_REQUIRED','实际两个独立实例、一辅助，evidence_sufficient；本次单节点path无后继，保留n1','reason仍沿用不足/辅助文案；不冒实际推进及完整冻结场景PASS',['L01-L05-I01-X09-final.json']),
      'L06':('S_REAL_HTTP_PG_NATIVE_PASS_Q_OPEN','C正/反/部分三答均真实持久，profile/citation/policy层已覆盖','语义质量仍需Q',['L06-concept-three-answers.json']),
      'L07':('S_REAL_HTTP_PG_NATIVE_PASS_Q_OPEN','P正/反两答真实持久，只阅读推理未执行用户代码','语义质量仍需Q',['L07-program-two-answers.json']),
      'L08':('S_CLARIFICATION_PERSISTED_PARTIAL','两Java范围真实中性plan澄清保存在reason投影；夹具失败通过原回执核对','范围再确认仅J-CODE及最终U/Q未完成',['neutral-results-readback.json']),
      'L09':('S_NEUTRAL_RESULTS_PERSISTED_Q_OPEN','火星不足/双源冲突真实中性结果已提交，原夹具错误保留','供应商逐项支持与开放语义待Q',['neutral-results-readback.json']),
      'L10':('BLOCKED_REAL_HOST_NOT_STARTED','HTML资格目录新增ACL投影已修并通过真实普通PG指纹；初始503保留','复检夹具错读current_mode导致API18退出；无真实artifact/ACK/PNG/StopProof，时间门关闭',['L10-current-artifact-error.txt','HTML-catalog-real-PG-check.json','preview-recheck-failure-1792075142549409000.txt']),
      'I01':('S_REAL_HTTP_PG_NATIVE_FINISHED_U_PARTIAL','R+M选记忆场次有问题/必要probe/支持回答/反馈/finish；原ask GET404后精确HTTP同键续交','最终bundle6 U与Q语义仍缺',['I01-after-normal-reopen.json','original-ask-explicit-recovery.json','browser-7/proof.json']),
      'I02':('S_CONTRACT_INHERITED_Q_NOT_RUN','已有范围/用途非证据协议继承','仅R缺M和自报的真实语义待Q，未冒新动态完整通过',[]),
      'I03':('S_CITATION_BOUNDARY_INHERITED_Q_NOT_RUN','既有范围/位置校验继承，记忆不作履历证据','利润/收益无据与位置不等于语义支持仍待Q',[]),
      'X01':('PARTIAL_PDF_BLOCKED','坏UTF8/MD与已有替换部分继承；原两次HTTP PDF422仍失败','孤立worker成功不替代HTTP，未取得稳定新根因，未裸重试第三次',['PDF-unclosed.json']),
      'X02':('S_REAL_HTTP_PG_NATIVE_LATE_INVALIDATION_PASS_U_PARTIAL','学习及v2面试dispatch后分别真实revise/revoke，晚到invalidated/current=false，rev3 purge done','独立第三次delete及最终前端晚到门未完成',['X02-late-memory.json']),
      'X03':('S_REAL_PG_SUBSET_PASS_U_PARTIAL','原X03-X07 PG同键并发/异文拒绝/一次claim证据复用','最终U及其它新域/index语义竞争的完整矩阵未完成',[]),
      'X04':('S_BACKEND_LATE_INVALIDATION_PASS_U_NOT_RUN','真实dispatch之后记忆依赖变更使旧query不当前，持久事实保留','最终bundle6旧view/owner响应抑制未实际浏览器验证',['X02-late-memory.json']),
      'X05':('S_PROTOCOL_AND_PG_INHERITED','既有v4容量/维度/provider映射/发送前失败关闭及workflow预算证明有效','未新增实际Windows故障集合完整通过声明',[]),
      'X06':('S_REAL_UNKNOWN_PRESERVED','旧95a0原键保留不重发；新同库重开前显式合成timeout留unknown/预留','全部新kind故障族与最终U未完成',['actual-checkpoint.json','X09-before-normal-reopen.json','X09-GET-only-after-reopen.json']),
      'X07':('S_REAL_PG_WORKFLOW_GATE_PASS_U_PARTIAL','一request但query+model整步不足在INSERT前拒；旧真实PG四账证明复用','最终bundle6预算前端门未新增U验证',[]),
      'X08':('PARTIAL_REFRESH_GET_ONLY','Browser7实际reload GET不自动POST，原ask key404精确核对后合法同键继续','索引/query、answer、feedback三类COMMIT丢HTTP正文故障未完成',['browser-7/proof.json','original-ask-recovery-before.json']),
      'X09':('S_NORMAL_APP_REOPEN_PASS_U_PARTIAL','保存两域回答与unknown后，原正常stdin/句柄关闭并同CID库重开，GET无POST，后续新反馈已保存','PG由原控制器连续持有，未声称PG重启；最终bundle6完整U缺',['X09-GET-only-after-reopen.json','L01-L05-I01-X09-final.json']),
      'X10':('S_REAL_DELETE_AND_PACKAGE_PASS_ROUNDTRIP_BLOCKED','已索引/query/007的N-CONFLICT经真实服务提交墓碑，chunks/embedding正文删除；53received=42正文+11已删','R02成功往返未完成，非全场景通过',['X10-real-deletion-overlay.json','source-r02-final-package.json']),
      'X11':('S_REAL_ISOLATION_AND_CLEANUP_PASS_WITH_LIMITS','S02低压自动清场继承；S03所有根/attempt精确关闭，无外部进程/端口被处理','S03时间门已到；原8次Browser上限保持',['final-resource-stop-binding.json','final-budget-observed.json']),
      'X12':('S_CONTRACT_BOUNDARY_INHERITED_Q_OFF','既有能力/源白名单/跨kind消费/空间隔离有限断言继承；Q roster未创建','全局外发预算实际PG并发与完整新U覆盖未验证',[]),
      'P01':('S_NONEMPTY_UPGRADE_AND_REPAIR_REAL_PG_PASS','继承非空014升级；source/compat最小SQL后完整受信目录及全业务行不变，选记忆start/实际删源通过','不外推用户库迁移或项目独审',['SQL-repair-summary.json','source-SQL-before.json','source-SQL-after.json','compat-SQL-before.json','compat-SQL-after.json','minimal-memory-interview-start.json','X10-real-deletion-overlay.json']),
      'P02':('S_OLD_R01_SEAL_INHERITED_NEW_APP_NOT_RUN','原R01真实装载/seal/UPDATE42501原件复用，无014改写','新reader应用GET及拒POST未完成，没有激活R01',['restore-final-disposition.json']),
      'P03':('FAILED_VALID_R02_COMPONENT_TIMEOUT','实际R02包617行/101文件/两space/22向量/unknown/删源overlay；hash-fault隔离失败正确','有效目标component30秒超时，已failed/撤凭据/停止；5对象满，两个失败目标不能清空复用',['source-r02-final-package.json','final-r02-hash-failed.json','root16-failure-1792074903576023600.txt','restore-final-disposition.json'])
    }
    for old in old_index['cases']:
        key=old['id'];status,scope,remaining,evidence=facts[key]
        cases.append({'id':key,'S_status':status,'scope':scope,'remaining':remaining,'new_evidence':[link(x) for x in evidence],'inherited_evidence':old.get('new_evidence',[]),'Q_status':'NOT_ENABLED_NOT_RUN','frozen_scenario_passed':False,'history_S02':old})
    assert len(cases)==28;c.write(E/'case-index.json',{'schema':'TASK117.case-index.v3','sample':stamp,'S_candidate':'INCOMPLETE_WITH_LOCATED_PRODUCT_AND_VERIFICATION_BLOCKERS','Q':'NOT_ENABLED','passed_frozen_scenarios':0,'full_pass_count_meaning':'所有冻结层全部满足的计数；不把0解释为各S层无成果，逐例S_status分层','cases':cases})
    c.write(N/'final-case-index.json',json.loads((E/'case-index.json').read_text()))
    c.write(N/'validation-summary.json',{'sample':stamp,'new_tests':{'TermPrefixTests':{'executed':2,'passed':2,'layer':'纯词项范围与容量；未增加24词上限、未改变完整向量查询'},'HTML_catalog':{'layer':'实际普通PG目录指纹及未知ACL拒绝','evidence':'HTML-catalog-real-PG-check.json'}},'build6':{'typecheck_and_build':'passed','HTTP_exact_bytes':'passed','Browser':'NOT_RUN'},'old_tests':'未变算法/协议按原具体证据继承，没有整批重跑','new_rule_hashes_checked':len(rules),'source_identity_count':len(rows)})
    local=datetime.now(timezone(timedelta(hours=8))).isoformat()
    countline='、'.join(f'{k} {val}' for k,val in v['counts'].items())
    prefix=f'''# TASK-117 / R-111 S03 结果：部分交付，完整S未完成

保存于 {local}。两库SQL修补、持久两域及多项传播已完成；R02有效包恢复失败，固定预览、R01新reader应用查看及最终bundle6 U未完成，不能提交为稳定完整S或STEP通过。

## 已完成及证据边界

source和compat原CID串行应用批准的五表SELECT与retrieval_chunk_guard别名修补。完整旧受信目录先核，新shape为5b7dc68a94101307bcbd63a16607c5b2ee79906b5f32669d764853a55172dc12，014字节为3a919b2562ded5765de132519b841c1d1439c65c001795cfbd608cbc03586e78。真实管理员/角色/owner/SECURITY DEFINER/search_path、无写权与全部业务行/预算/原UNKNOWN不变已核。没有重跑001—014，没有改001—013、R01或用户库。首次compat目录拒绝由CRLF存入prosrc造成，原失败保留，按同一批准函数文本LF修正后通过。

新检索诊断对照经正常入口、真实Windows监督/PG获得received；它不是原95a0b55e-b5fb-45d7-ad6e-310f3bc4b572的重试。旧UNKNOWN及预留只读保留。移除高成本诊断trace后本次正常提交成功，仍不把trace认定为旧UNKNOWN唯一根因。

旧教学b7f32142-b5b3-4a5c-b561-f927bcbe1b6d实测已过deadline，保持revision16，不改期限或追造资格。明确新场景93852e50-f648-4cb1-a2e8-5f8283975567完成错答、针对练习/参考曝光、360及240新实例、末评价和理由，最终revision17；实际独立两份、辅助一份、evidence_sufficient。单节点路径无后继仍保留n1，现有理由却沿用“独立实例不足/辅助”文案，该矛盾单列待核，不冒实际推进或长期掌握。

R+M选记忆面试06c8a779-a936-423d-9554-010f9ebcfb8e完成问题、一次probe、支持回答、反馈和finish，revision7/ended。先本地start再确认索引已真实执行。原长中文目标超过24词项令catalog返回500，已使混合词项通道只取既定24词前缀，完整已绑定向量查询不改；严格旧词项入口继续拒超限。原未claim提问按保存正文hash及GET404由真实HTTP显式同键续交，没有冒用旧tab owner。

两域回答/probe及一笔显式合成unknown保存后，按原正常启动器stdin/句柄停止应用，同source CID/卷/profile重新启动，GET原事实未自动POST，后续教学反馈及面试反馈已保存。PG在两次API之间由同一根控制器持续持有；本证据不冒PG进程重启。两域有UI和HTTP混合证据，未签完整最终U。

C三类答案、P两类答案实际经HTTP/PG/Native持久；没有执行用户代码。Java歧义、火星不足和双源冲突实际提交在reason中，夹具误读proposal=None的失败保留，已从原HTTP回执核对，不重新POST。L08后续只选J-CODE的范围修订尚未完成。学习及v2面试真实dispatch后分别修订/撤销记忆，晚到query均invalidated/current=false；revision3正文purge done。独立第三次delete及最终前端晚到门仍缺。N-CONFLICT实际墓碑/清理已提交，chunk/embedding正文删除而调用及unknown费用元数据保留。

## 实际修补与验证范围

前端重开时，持久head先就绪而目标正文尚未载入，曾发空query并被后端400拒绝。现改为使用核过的持久目标，目标未就绪时禁ask/review/next。正式build6及typecheck通过，JS为index-BhHp87aG.js / 7df2e239f2a9f49b00fc25b70e45db678ec765b361af6fafcdf7835fcb98a2b1；真实HTTP核过全部4项字节。Browser5—8实际加载的是bundle5，不能移花到bundle6。Browser累计8已到门，本轮没有第9次。

HTML资格ACL投影漏掉qualification_column_acls，曾导致capabilities503。只补批准SELECT的同一精确投影，真实普通PG HTML指纹及未知ACL拒绝通过；未放宽受信schema。随后正常API18复检在夹具错读DataContext.current_mode前退出，父feedback、artifact和真实宿主均未产生。preview create/start仍0，无本轮ACK/PNG/StopProof，不能写L10通过。

新增两项词项边界断言通过；其它充分且未变的确定算法/旧协议验证直接继承，没有整批重跑。预览renderer、验签器、Job与退款主体及依赖锁未改。源码pre/diff/post、历史as-run差异和最终bundle身份分别见[最终manifest]({link('final-source-manifest.json')})、[差异]({link('source-changes.diff')})及[验证摘要]({link('validation-summary.json')})。新增辅助文件没有追造首次pre时间；复制夹具的旧S02命名、错误预览说明及字段错误在[纠正记录]({link('metadata-corrections.json')})如实分列，未改旧失败。

## 恢复及当前真实阻断

R02包真实发布，3938960字节、617行、101文件；含两个space、22份512维向量、53份received embedding，其中42份当前007与11份已删正文对应，两个unknown、非执行grant元数据和已删源overlay。向量SQL/Python float32摘要一致。这是源包事实，不是往返成功。

hash-fault目标3728af48-e602-4960-a70c-75f315abb2bc按预期integrity_failed；有效目标8e7a206c-54cd-46de-a0ab-bb448f2bb7a1在restore._load组件逐行INSERT后超过30秒，operation_timeout。两者均failed、临时凭据撤销且精确停止，永久保留，不清空复用。实际慢SQL/组件根因未完全定位，不扩大30秒时限或拆事务假通过。PG物理对象/卷各5已满；成功往返还需先定位修正装载阻断，并由主控明确新的独立目标安排。

R01目标05abc665-bbf9-4d41-abf0-7fc607049bf8继续保持旧链封印和原UPDATE42501事实，新reader应用GET/拒POST未完成。当前source的selector与fence均空，未激活R01/R02，源数据没有切成恢复副本。PDF原两次HTTP422及孤立两页成功原件保留；尚无足够新根因，不裸重试第三次，X01仍缺。

28场景的S/PG/Native/HTTP/U及Q边界逐项见[唯一case-index]({str((E/'case-index.json').resolve())})。有真实T层成功及继承层成果，完整冻结场景/最终S仍未通过。Q未启用，本段真实供应商调用和实际费用均0；原AP2条件许可及历史费用账不改变。独立集中审计未执行，本人不自签。

## 资源、时间与累计账

本段新增真实根14、15、16，根内续作保留原首点/截止及每次失败；没有开根17或重跑旧root09/11/12/13。累计 {countline}。Native计数含原保守预记，未退款；当前各段数/上限、PG并集及实际超额见[最终账观察]({link('final-budget-observed.json')})，唯一主账仍原budget.json/events.jsonl。

S01活动37651.0027854/持有16219.360/offline1724.875及原超额保留；S02交回活动17303.702146/持有5702.094/offline821.686保留。S03本次观察elapsed {elapsed:.3f}秒，对21600门超{max(0,elapsed-21600):.3f}秒；保守持有{runtime:.3f}秒，已登记offline {offline:.3f}秒，对3000门超{max(0,offline-3000):.3f}秒。中断时所有资源已停，用户接续间隔不冒真实运行或离线投入；原elapsed门未重置，所以恢复后仅保存/核查，没有再启业务。S03最初首工具漏同步采钟，已从本线程记录恢复首工具UTC，可靠QPC另存；更早许可时刻的保守活动下界不退款，不冒严格满足首采要求。

最新独立只读停止核查核过五只PG均Running=false/Pid0、全部S02/S03注册API/Node原birth已退出、完整{stop['complete_Win32_Process_inventory']['rows']}项进程清单无cached Chromium/子孙、固定15481—15485及18118无监听。所有旧数据、卷、失败、原始报告保留，无在途资源。确切CID/birth/端口及原件sha见[停止绑定]({link('final-resource-stop-binding.json')})。当前没有因平台自动审批额度遭拒的动作，不把未完归为Sol账号问题。

交回主控的最小待决为R02装载阻断与新独立目标、最终bundle6 U与固定宿主/PDF/R01应用补证的定向安排；不建议整批重跑或再单纯增加入口。共享DocuS/任务卡/裁定及Git未写，正式进度/缺陷严重度和最终裁定留主控同步。

## 以下完整保留S02及S01原件

'''
    report.write_bytes(prefix.encode('utf-8')+raw)
    result_id=identity(report);assert report.read_bytes().endswith(raw)
    disposition={'sample':c.sample(),'permit':s['permit'],'result':str(report),'result_identity':result_id,'status':'partial_returned_time_gate_closed','stable_S':False,'all_resources_stopped':True,'business_authorization_returned':True,'old31949_bytes_suffix_preserved':True}
    v['phase']='S03_returned_partial';v['s03_return_disposition']=disposition
    for segment in v['segments']:
        if segment['permit']==s['permit']:segment['return_disposition']=disposition
    c.write(E/'budget.json',v);c.event('S03_returned_partial',result=str(report),sha256=result_id['sha256'],all_stopped=True,business_restarted_after_time_gate=False)
    c.write(N/'result-save-receipt.json',disposition)
    c.write(N/'final-binding.json',{'sample':c.sample(),'result':result_id,'source_manifest':identity(N/'final-source-manifest.json'),'case_index':identity(E/'case-index.json'),'budget':identity(E/'budget.json'),'stop':stop_binding,'Q':'NOT_ENABLED'})
    for row in rows:assert identity(R/row['path'])==row['post'],row['path']
    assert report.read_bytes()[-31949:]==raw
    c.write(N/'final-readback.json',{'sample':c.sample(),'report':str(report),'report_identity':identity(report),'old_result_suffix_exact':True,'source_identities_checked':len(rows),'case_count':28,'bundle6_files':len(bundle['files']),'all_stopped':True,'public_locked_rules':len(rules),'stable_S':False})
    print(json.dumps({'result':str(report),'bytes':result_id['bytes'],'sha256':result_id['sha256'],'source_identities':len(rows),'case_count':28,'all_stopped':True,'stable_S':False,'S03_offline':offline},ensure_ascii=False))
if __name__=='__main__':main()
