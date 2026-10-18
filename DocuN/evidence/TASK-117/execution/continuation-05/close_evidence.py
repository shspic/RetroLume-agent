"""S06 forward engineering closure, exact pre/post and inherited evidence; no shared-state verdict."""
from pathlib import Path
import sys,json,copy,difflib,subprocess
N=Path(__file__).resolve().parent;E=N.parent;ROOT=E.parents[3]
sys.path.insert(0,str(E));import control as c
def read(name):return json.loads((N/name).read_text(encoding='utf-8'))
def identity(path):
    p=Path(path);raw=p.read_bytes();return {'path':p.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':c.sha(raw)}
def main():
    c.guard();assert c.state()['active_root'] is None
    assert read('final-resource-stop-binding.json')['all_stopped'] and read('final-new-preview-and-selector-stop.json')['all_current_resources_stopped']
    assert read('R02-formal-readonly-reopen.json')['caps']['format']=='data_exit.v1.r02'
    assert read('browser-14/proof.json')['status']==read('browser-16/proof.json')['status']=='passed'
    assert read('browser-15/proof.json')['status']=='failed' and read('R02-selector-increment.json')['normal_API_activation_calls']==1
    assert read('PDF-HTTP-bounded-probe.json')['result']=='success' and read('shared-global-budget-PG-lock.json')['target_SQL_writes']==0
    inherited=json.loads((E/'case-index.json').read_text());matrix=copy.deepcopy(inherited)
    matrix['S06_previous_summary']={k:inherited[k] for k in ('S_candidate','Q','passed_frozen_scenarios','full_pass_count_meaning')}
    updates={
     'L01':('S_BUSINESS_PG_NATIVE_AND_CHANGED_U_ADOPTED','S03持久业务全链、S04/S05 bundle7针对变化的真实U合并继承；前端及教学业务源码本轮未变。','无须同一Browser从头重做；Q开放语义与独立复核待主控。',[]),
     'I01':('S_BUSINESS_PG_NATIVE_AND_CHANGED_U_ADOPTED','继承S03完整面试持久链及S04最终bundle7目标就绪query/ask；本轮相关业务代码未变。','Q开放语义与独立复核待主控；不制造完整U重跑前置。',[]),
     'L08':('S_CLARIFICATION_SCOPE_ADOPTED','S05 J-CODE单源真实HTTP/Native及既有共享澄清/范围UI继承，未改澄清与选择函数。','本轮无新增专属UI分支；真实语义留Q。',[]),
     'L10':('S_FIXED_PREVIEW_ACK_PNG_NORMAL_STOP_PROVED','原artifact复用；真实d120/t120=1、t240=.5、t0/未知字段422、reset1；PNG与受信观察、原private-init/双EOF/Jobs StopProof及持久结算。','固定合成解释结构通过；开放生成解释语义属于Q。',['L10/input-acks.json','L10/stage-times.json','L10/supervisor-result.json','L10/settled-status.json','L10/actual-frame.png']),
     'X01':('S_ORIGINAL_PDF_HTTP_REVIEW_AND_PHYSICAL_PAGES_PROVED','同942字节冻结PDF真实HTTP到parse/受限Job成功；逐页确认后GET/content返回两物理页与补充来源。','原两次422确切原因未追溯，原失败保留；新诊断直接成功，不再解析重试。',['PDF-HTTP-bounded-probe.json','PDF-two-page-confirmed.json','PDF-diagnostic-admission.json']),
     'X02':('S_THREE_DELETION_EFFECTS_PROVED_UNCHANGED_PROTOCOL','继承修订/撤销晚到invalidated；本轮只读核清单hash及两个版本集合、body行0、GET无正文，保留修订与6个旧选择身份。','按S06纠正验收三个效果；不要求独立delete，不新建记忆/墓碑。',['X02-current-physical-deletion.json']),
     'X03':('S_KEY_AND_SEMANTIC_SLOT_REPRESENTATIVES_PROVED','S05同键/异文真实U继承；本轮不同键同父教学goal并发，一项提交一项409。检索claim CAS、共享索引唯一性及向量事实沿未变PG约束证据继承。','未扩domain×kind故障全排列；非本轮所有slot动态重跑。',['semantic-slot-race.json']),
     'X04':('S_INFLIGHT_GOAL_AND_REAL_SELECTOR_LATE_SUPPRESSION_PROVED','真实query dispatch后改变goal，原收到回包current=false；原source实际200响应暂存至正式selector及正常reload后释放，不授新动作；最终只读重开拒写。','scope/source/memory等同资格函数族沿原G3/G5/G8/G9及S03有效证据；不冒每族都新跑。',['inflight-goal-invalidation.json','R02-selector-increment.json','browser-16/proof.json']),
     'X05':('S_UNCHANGED_CAPABILITY_PROTOCOL_AND_PG_ADOPTED','容量/维度/provider映射/发送前拒绝协议与PG事实未改；继承原证明及S05整步门。','Q真实供应商条件仍未启用；不扩全Windows故障集合。',[]),
     'X06':('S_UNKNOWN_ACCOUNTING_PRESERVED_ADOPTED','原unknown、费用/预留和同键只读恢复证据保留；新读取/恢复不恢复执行权，不重发未知。','不以所有kind故障全排列作为S06新前置。',[]),
     'X07':('S_BUDGET_WORKFLOW_AND_REAL_PREVIEW_LEDGER_ADOPTED','S05四账/整步拒绝及原G5/G8/G11运行/工具/预览上限继承；本轮真实预览reserve60、正常耗11、reserved0、含旧60累计settled71。','Q关闭；未把账面预留当真实费用或声称所有耗尽UI重跑。',['L10/settled-status.json','shared-global-budget-PG-lock.json']),
     'X09':('S_NORMAL_REOPEN_INHERITED_AND_PERMANENT_R02_REOPEN_PROVED','S03正常业务应用重开沿用；新增最终配置下R02正常只读重开，source PG保持停止，无fallback。','旧业务及旧键不重复执行。',['R02-formal-readonly-reopen.json']),
     'X10':('S_OLD_PACKAGE_DELETION_OVERLAY_AND_FORMAL_SELECTOR_PROVED','原617行包装载/封印继承；当前墓碑tuple全部在success01 plan，沿原source hub drain/freeze/selector正式切换一次。','无新墓碑、无success02、无重新装载；原失败目标保留。',['R02-current-overlay-and-owned.json','R02-selector-increment.json','R02-formal-readonly-reopen.json']),
     'X11':('S_CURRENT_EXACT_STOP_AND_NEW_NORMAL_STOP_PROVED','根22/23/24各attempt均结束；六原PG与所有登记API/Browser实例停止；新预览正常StopProof与旧首次UNCONFIRMED分层。','历史漏采/超额/未知不回填。',['final-resource-stop-binding.json','final-old-preview-stop.json','final-new-preview-and-selector-stop.json']),
     'X12':('S_SHARED_GLOBAL_GATE_TWO_SYNTHETIC_OPS_PROVED_Q_OFF','同一生产全许可锁和总门：两个真实PG只读事务配隔离合成预算/传输，仅一项获准；无Q名册行、目标写入或外发。','范围为真实PG锁+合成预算，不冒实际外发账/付费Q准入；Q仍须独立采用。',['shared-global-budget-concurrency.json','shared-global-budget-PG-lock.json']),
     'P02':('S_R01_REAL_SEALED_READER_HTTP_AND_FINAL_U_PROVED','S05七类HTTP/四种拒写继承；S06最终bundle7浏览器七类历史和export/backup/upload禁用，原source selector/fence未改。','R01实测在R02绑定profile显示补丁前；该补丁对R01仍同profile，最终R02真实重开验证公共绑定增量。',['R01-final-browser-verified.json','reader-host-proof.json','browser-14/proof.json']),
     'P03':('S_R02_SEALED_TARGET_FORMAL_SELECTION_HTTP_U_REOPEN_PROVED','复用原封存success01；一次真实activate-readonly，旧回包抑制、实际GET/POST readonly及正常只读重开，原source不回退。','原失败装载、Browser15夹具头格式失败保留；不新建或换目标。',['R02-selector-increment.json','R02-one-PG-switch-stage.json','R02-formal-readonly-reopen.json','browser-16/proof.json'])}
    for row in matrix['cases']:
        if row['id'] in updates:
            status,scope,remaining,paths=updates[row['id']];row['history_S05_projection']=copy.deepcopy(row)
            row.update(S_status=status,scope=scope,remaining=remaining,S06_evidence=[str(N/p) for p in paths])
        row['Q_status']='NOT_ENABLED_NOT_RUN'
        # Keep the historical whole-scenario acceptance flags; engineering candidate is not final acceptance.
    matrix.update(sample=c.sample(),S_candidate='ENGINEERING_S_CANDIDATE_READY_FOR_INDEPENDENT_REVIEW',Q='NOT_ENABLED',passed_frozen_scenarios=0)
    matrix['S06']={'sample':c.sample(),'permit':c.state()['active_segment'],'engineering_candidate_ready':True,'independent_review':'NOT_SELF_SIGNED; controller arranges one isolated A+ review','whole_28_T_U_Q_acceptance':False,'new_roots':[22,23,24],'new_success02_created':False,'current_selector':'original source hub -> permanent success01 read-only','business_chains_repeated':False,'real_provider_calls':0,'fee':0}
    c.write(E/'case-index.json',matrix);c.write(N/'final-case-index.json',matrix)
    concise=[{'id':r['id'],'current_S':r['S_status'],'scope':r.get('scope'),'remaining':r.get('remaining'),'S06_evidence':r.get('S06_evidence',[]),'S05_evidence':r.get('S05_evidence',[]),'Q':'NOT_ENABLED'} for r in matrix['cases']]
    c.write(N/'S-case-closure.json',{'sample':c.sample(),'engineering_candidate_ready':True,'layers':'T/real PG lock+synthetic budget/PG/HTTP/Native/U each scoped; no Q or overall acceptance','cases':concise})
    lines=['|例|工程证据与适用层|保留边界|','|---|---|---|']
    for row in concise:lines.append('|'+row['id']+'|'+row['current_S']+'：'+row['scope'].replace('|','/')+'|'+row['remaining'].replace('|','/')+'|')
    (N/'S-case-closure.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    changes=read('changes.json');entries={r['path']:copy.deepcopy(r) for r in json.loads((E/'continuation-04/final-source-manifest.json').read_text())['entries']};diff=[]
    for relative,pre in changes.items():
        path=ROOT/relative;raw=path.read_bytes();before=(ROOT/pre['backup']).read_bytes() if pre['exists'] else b''
        if pre['exists']:assert c.sha(before)==pre['sha256']
        diff.extend(difflib.unified_diff(before.decode('utf-8-sig').splitlines(),raw.decode('utf-8-sig').splitlines(),fromfile='S06-pre/'+relative,tofile='S06-post/'+relative,lineterm=''))
        entries[relative]={'path':relative,'pre':pre,'post':{'exists':True,'bytes':len(raw),'sha256':c.sha(raw)}}
    for relative,row in entries.items():
        p=ROOT/relative
        if p.exists():row['post']={'exists':True,'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())}
        else:assert row['post'].get('exists') is False,relative
    (N/'source-changes.diff').write_text('\n'.join(diff)+'\n',encoding='utf-8')
    c.write(N/'final-source-manifest.json',{'sample':c.sample(),'entries':list(entries.values()),'scope':'inherited163 plus S06 pre/post changes; missing entries remain explicit; not blanket as-run assertion'})
    helpers=[identity(p) for p in [*N.glob('*.py'),*N.glob('*.mjs')]]
    c.write(N/'final-fixture-manifest.json',{'sample':c.sample(),'files':helpers,'scope':'final helper bytes, not retroactive as-run hashes for previously executed helper revisions','actual_product_as_run':[identity(N/f'api-{i}-as-run.json') for i in range(29,34)],'PDF_probe_admission_sha':read('PDF-diagnostic-admission.json')['probe_sha256']})
    assets=json.loads((E/'continuation-04/final-bundle-7-binding.json').read_text())['files']
    for row in assets:assert c.sha((ROOT/row['path']).read_bytes())==row['sha256']
    c.write(N/'final-bundle-7-binding.json',{'sample':c.sample(),'files':assets,'unchanged':True,'actual_U':['browser-14/proof.json','browser-15/proof.json (scoped FAIL preserved)','browser-16/proof.json'],'builds_added':0})
    oldpublic=json.loads((E/'continuation-04/version-sync-manifest.json').read_text());public=[]
    for row in oldpublic['candidate_files']:
        p=ROOT/row['path'];assert p.is_file();public.append(identity(p))
    oldpublic.update(sample=c.sample(),candidate_files=public,publication_approval=False,uploaded_files=0)
    oldpublic['S06']='only exact current identities refreshed; raw DocuN/runtime configs/credentials/backup and user docs remain local; no Git writes'
    c.write(N/'version-sync-manifest.json',oldpublic)
    receipt=read('receipt.json');allowed={str((ROOT/p).resolve()).lower() for p in changes}|{str((E/p).resolve()).lower() for p in ('budget.json','events.jsonl','case-index.json')}
    checked=[];changed=[]
    for row in receipt['verified']:
        p=Path(row['path']);exists=p.exists();actual=c.sha(p.read_bytes()) if exists else None
        same=exists==row.get('exists',True) and actual==row.get('sha256');item={**row,'current_exists':exists,'current_sha256':actual,'same_now':same}
        if not same:assert str(p.resolve()).lower() in allowed,row['path'];changed.append(item)
        else:checked.append(item)
    c.write(N/'rules-and-protected-readback.json',{'sample':c.sample(),'total':len(receipt['verified']),'unchanged':checked,'authorized_changes':changed,'unexpected_changes':[],'DocuS_rules_task_card_Git_old_evidence_written':False,'result_still_exact_old_suffix_before_save':(ROOT/'DocuN/results/TASK-117-result.md').read_bytes()==(N/'before-result.md').read_bytes()})
    previous=json.loads((N/'before-budget.json').read_text());now=c.state()
    assert now['segments'][:-1]==previous['segments'] and now['roots'][:len(previous['roots'])]==previous['roots'] and now['failures'][:len(previous['failures'])]==previous['failures']
    ei=read('before-events.jsonl-identity.json');oldbytes=(E/'events.jsonl').read_bytes()[:ei['bytes']];assert c.sha(oldbytes)==ei['sha256']
    c.write(N/'historical-ledger-preservation.json',{'sample':c.sample(),'all_old_segments_exact':True,'roots_1_to_21_exact':True,'old_failures_exact_prefix':True,'old_events_exact_prefix_sha256':ei['sha256'],'old_S05_overruns_unchanged':True,'old_report63687_sha256':c.sha((N/'before-result.md').read_bytes())})
    priorrepo=json.loads((E/'continuation-04/repository-final.json').read_text());git=[]
    for name in ('HEAD','index','config'):
        p=ROOT/'.git'/name;before=next(x for x in receipt['verified'] if Path(x['path'])==p);assert c.sha(p.read_bytes())==before['sha256'];git.append({'name':name,'sha256':before['sha256'],'unchanged':True})
    def command(*args):return subprocess.run(['git','--no-optional-locks',*args],cwd=ROOT,capture_output=True,text=True,timeout=20,check=True).stdout.strip()
    head=command('rev-parse','HEAD');origin=command('config','--get','remote.origin.url');assert head==priorrepo['HEAD'] and origin=='https://github.com/shspic/RetroLume-agent.git'
    c.write(N/'repository-final.json',{'sample':c.sample(),'HEAD':head,'origin':origin,'protected':git,'S06_Git_writes_commit_push_upload':0,'remote_live_refs':'not retried; prior reset and stale dispatch metadata preserved','actual_prior_association':'continuation-04/repository-final.json','public_candidates':len(public)})
    c.write(N/'visual-readback.json',{'sample':c.sample(),'visually_inspected':['browser-14/R01-real-readonly-records.png','browser-16/R02-normal-reopen-readonly-history.png','L10/actual-frame.png'],'observations':['R01 readonly banner, disabled export/backup/upload and saved records','R02 readonly banner and revoked memory version identities with body null','actual preview PNG shows d120/t240 and .5, corresponding to accepted seq2; reset1 proven by ACK seq3, not claimed same PNG'],'browser13_old_evidence_unchanged':True})
    c.event('S06_engineering_evidence_closure',cases=len(concise),engineering_candidate_ready=True,independent_review=False,Q_enabled=False)
    print(json.dumps({'cases_mapped':len(concise),'source_entries':len(entries),'helper_files':len(helpers),'protected_unchanged':len(checked),'authorized_changed':len(changed),'unexpected':0,'all_old_segments_preserved':True,'new_builds':0,'Git_writes':0},ensure_ascii=False))
if __name__=='__main__':main()
