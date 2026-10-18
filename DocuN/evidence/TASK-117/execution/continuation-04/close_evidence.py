"""S05 forward evidence and result closure. Does not start resources or alter shared status."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,subprocess,difflib,copy,time,re
N=Path(__file__).resolve().parent;E=N.parent;ROOT=E.parents[3]
sys.path.insert(0,str(E));import control as c

def get(name):return json.loads((N/name).read_text(encoding='utf-8'))
def identity(path):
    path=Path(path);raw=path.read_bytes()
    return {'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':c.sha(raw)}

def main():
    c.reserve_offline(900)
    assert c.state()['active_root'] is None
    stop=get('final-resource-stop-binding.json');assert stop['all_stopped']
    assert get('final-old-preview-stop.json')['all_current_owned_preview_instances_stopped']
    assert get('browser-12/proof.json')['status']=='passed' and get('browser-13/proof.json')['status']=='passed'
    # Every original record and failure stays available; these are forward projections only.
    updates={
      'L01':('S_PG_HTTP_NATIVE_COMPLETE_FINAL_U_SUBSET','原S03业务闭包，S04/S05正式bundle7真实装载及作答/评价/当前视图子集；不再写bundle6未验。','完整L01最终U全程与Q未整体验收。',['browser-12/proof.json'],['final-UI-passed.json']),
      'L05':('S_PERSISTENT_COUNTS_AND_REASON_DISTINCTION_PASS','S04三种reason分支与两份独立实例/无后继持久证据继承。','不将未发生的自动推进或全部冻结场景记PASS。',[],['reason-sufficient-no-successor-persistent.json']),
      'L08':('S_SINGLE_JCODE_SCOPE_HTTP_NATIVE_PASS','继承两Java澄清；新活动真实只选J-CODE并取得清楚Java路径。','L08专门最终U及Q语义仍未闭。',['L08-JCODE-only-after-clarification.json'],[]),
      'L10':('S_ARTIFACT_EXISTS_OLD_PRECREATE_RECOVERED_NEW_HOST_MEMORY_BLOCKED','原artifact合法；原预览真实恢复never_started、60秒全额结算及owned结束；新预览未启动。','新宿主ready、ACK/PNG、实际阶段成本及正常StopProof仍缺。',['old-preview-recovery.json','final-old-preview-stop.json','preview-stage-cost-final.json','L10-current-memory-gate.json'],['preview-parent-and-artifact.json']),
      'I01':('S_HTTP_NATIVE_FINISHED_FINAL_U_ASK_GATE_PASS','S03完整面试业务继承；S04 bundle7持久目标就绪后真实query/ask继承。','最终U完整面试反馈/追问全程及Q未整体通过。',[],['final-UI-passed.json']),
      'X01':('S_MD_INHERITED_PDF_HTTP_FROZEN','原MD/坏UTF8及孤立PDF成功继承；有限诊断无新可区分因果。','PDF两页HTTP/人工确认未补；未裸重试第三次。',['PDF-bounded-diagnosis.json'],[]),
      'X02':('S_REVISE_REVOKE_INHERITED_DELETE_CONTRACT_HELD_BY_USER','原修订/撤销/晚到失效保留；独立delete不以revoke重复代替。','用户确认由主控补删除持久合同；R02正式切换随依赖保留。',['X02-independent-delete-gap.json','user-X02-hold.json'],[]),
      'X03':('S_SAME_KEY_CONCURRENCY_AND_DIFFERENT_BODY_FINAL_U_PASS_SUBSET','最终bundle真实UI一次提交，两个同键真实HTTP并发重放同一事实，异文409。','新域/index semantic slot完整矩阵仅继承原PG子集，不冒全场景通过。',['browser-12/proof.json'],[]),
      'X04':('S_FINAL_U_LATE_VIEW_AND_COPIED_OWNER_PASS_SUBSET','真实后端200仅延迟传递；换视图后旧响应不污染；复制sessionStorage的标签页获得不同活跃owner。','scope/goal/source在query/model执行中变化及selector晚到最终U未新增完整矩阵。',['browser-12/proof.json'],[]),
      'X07':('S_FINAL_U_WHOLE_STEP_BUDGET_AND_FOUR_LEDGERS_PASS_SUBSET','真实1请求活动，正式bundle在query前拒整步两次调用；零POST、零预扣；四账可见、刷新不重发。','运行/工具/预览耗尽的完整最终U组合未整体认领。',['browser-12/proof.json','browser-13/proof.json','X07-one-request-actual-budget.json'],[]),
      'X08':('S_THREE_COMMIT_BODY_LOSS_ORIGINAL_KEY_GET_INHERITED','S04实际query/answer/feedback三类COMMIT丢回包后原键GET已通过；不再写三类均未完成。','继承S04实际U，不再重交旧业务键；Q关闭。',[],['final-UI-passed.json']),
      'X09':('S_NORMAL_APP_REOPEN_INHERITED_FINAL_U_GET_ONLY_SUBSET','S03同库正常应用重开业务继承；S04/S05 bundle7刷新只读。','不把新活动或普通GET冒充旧全部场景重新执行。',['browser-12/proof.json','browser-13/proof.json'],[]),
      'X10':('S_DELETE_PACKAGE_AND_R02_LOAD_SEAL_PASS_ACTIVATION_HELD','S04同617行原包22.454秒装载/封印/float32/31表证据继承；当前六墓碑均在原overlay。','独立删除尚缺，用户保留R02正式activate；无success02条件创建。',['R02-overlay-dependency-preflight.json','user-X02-hold.json'],['P03-S04-verified.json']),
      'X11':('S_CURRENT_EXACT_STOP_PASS_OLD_FAILURES_PRESERVED','本轮根19—21均已精确停止；原预览新恢复与首次UNCONFIRMED分开。','历史漏采/未知/失败不回填；新预览正常停止链尚未实测。',['final-resource-stop-binding.json','final-old-preview-stop.json'],[]),
      'P02':('S_R01_REAL_SEALED_READER_HTTP_READ_AND_WRITE_REFUSAL_PASS_U_BLOCKED','独立normal产品reader构造，无source写/loader/维护/执行配置；R01真实七类历史HTTP及四种POST只读拒绝。','R01浏览器实测未启动（内存门）；API27 reader证据与API28最终缓存增量分别绑定。',['R01-reader-verified.json','reader-host-proof.json','R01-UI-memory-gate.json','api-27-as-run.json'],[]),
      'P03':('S_R02_FIXED_PACKAGE_LOAD_AND_SEAL_PASS_FORMAL_ACTIVATION_HELD','原有效装载超时已由S04成功目标封印闭合；两个失败CID永久停止保留，成功目标未激活。','独立delete与R02正式只读HTTP/U依赖用户补合同；不再列load未成功。',['R02-overlay-dependency-preflight.json','user-X02-hold.json'],['P03-S04-verified.json'])
    }
    matrix=json.loads((E/'case-index.json').read_text(encoding='utf-8'))
    for row in matrix['cases']:
        if row['id'] in updates:
            status,scope,remaining,now,old=updates[row['id']]
            row['S05_previous_projection']={k:row.get(k) for k in ('S_status','scope','remaining')}
            row.update(S_status=status,scope=scope,remaining=remaining)
            row['S05_evidence']=[str(N/p) for p in now]+[str(E/'continuation-03'/p) for p in old if (E/'continuation-03'/p).exists()]
        row['Q_status']='NOT_ENABLED_NOT_RUN'
    matrix['sample']=c.sample();matrix['S_candidate']='PARTIAL_NOT_STABLE_NO_OVERALL_PASS';matrix['passed_frozen_scenarios']=0
    matrix['full_pass_count_meaning']='No whole T/U/Q frozen scenario accepted as a package; assess each evidence layer, not true/false totals.'
    matrix['S05']={'sample':c.sample(),'Q':'NOT_ENABLED','stable_S':False,'final_bundle':'7, unchanged four asset bytes; Browser12/13 verified',
        'closed_incremental':['old preview recovery/owned','measured writable snapshot hotspot','L08 JCODE HTTP','same-key/view/owner/four-ledger U','one-request whole-step U','R01 readonly HTTP','origin local association'],
        'remaining':['X02 independent delete contract and dependent R02 activation held by user','PDF HTTP causal gap','new fixed preview ready/ACK/PNG/StopProof blocked before launch by memory','R01 final U blocked before browser launch by memory','remaining scope/model/selector and full exhaustion U matrices','Q closed'],
        'S04_stale_projections_corrected':['P03 load sealed success','L10 artifact exists but never ready','X08 three original key GET classes'],
        'full_28_scenario_pass':False,'new_success02_created':False}
    c.write(E/'case-index.json',matrix);c.write(N/'final-case-index.json',matrix)
    concise=[{'id':r['id'],'current_S':r['S_status'],'scope':r.get('scope'),'remaining':r.get('remaining'),'S05_evidence':r.get('S05_evidence',[]),'Q':'NOT_ENABLED'} for r in matrix['cases']]
    c.write(N/'S-case-closure.json',{'sample':c.sample(),'layers':'T/PG/HTTP/Native/U and Q kept separate in scope/remaining, no 28-case overall pass','cases':concise})
    lines=['|例|当前层与结论|未闭范围|','|---|---|---|']
    for row in concise:lines.append('|'+row['id']+'|'+row['current_S']+'：'+str(row['scope']).replace('|','/')+'|'+str(row['remaining']).replace('|','/')+'|')
    (N/'S-case-closure.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # Product/evidence source bytes and pre/diff/post. All prior manifests remain untouched.
    changes=get('changes.json');diff=[];entries={r['path']:r for r in json.loads((E/'continuation-03/final-source-manifest.json').read_text())['entries']}
    for relative,pre in changes.items():
        p=ROOT/relative;raw=p.read_bytes();before=(ROOT/pre['backup']).read_bytes() if pre['exists'] else b''
        diff.extend(difflib.unified_diff(before.decode('utf-8-sig').splitlines(),raw.decode('utf-8-sig').splitlines(),fromfile='pre/'+relative,tofile='post/'+relative,lineterm=''))
        entries[relative]={'path':relative,'pre':pre,'post':{'exists':True,'bytes':len(raw),'sha256':c.sha(raw)}}
    # Refresh every inherited identity, recording actual changes rather than pretending old hashes still match.
    for relative,row in entries.items():
        p=ROOT/relative
        if p.exists():row['post']={'exists':True,'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())}
    (N/'source-changes.diff').write_text('\n'.join(diff)+'\n',encoding='utf-8')
    c.write(N/'final-source-manifest.json',{'sample':c.sample(),'entries':list(entries.values()),'scope':'All prior155 source identities plus S05 registered changes; actual post bytes, not old hashes.'})
    assets=json.loads((E/'continuation-03/bundle-7.json').read_text())['files']
    for item in assets:assert c.sha((ROOT/item['path']).read_bytes())==item['sha256']
    c.write(N/'final-bundle-7-binding.json',{'sample':c.sample(),'files':assets,'unchanged':True,'actual_U':['browser-12/proof.json','browser-13/proof.json'],'builds_added':0})
    # Strict, explicit public candidates: source, trusted migrations/locks/examples, generic tests only.
    rawpaths=subprocess.run(['rg','--files','backend','frontend','deploy','config'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    public=[];suffixes={'.py','.ts','.tsx','.mjs','.cjs','.json','.sql','.ps1','.sh','.cmd','.md','.txt','.lock','.css','.html','.svg','.png','.ico','.toml'}
    for relative in rawpaths+['README.md','.gitignore','start-local.cmd']:
        p=ROOT/relative;rel=p.relative_to(ROOT).as_posix()
        if not p.is_file() or (p.suffix not in suffixes and p.name!='.gitignore'):continue
        if rel.startswith('config/') and '.example' not in p.name:continue
        if rel.startswith('backend/tests/fixtures/') and not rel.startswith('backend/tests/fixtures/step018/'):continue
        if any(x in p.parts for x in ('private','synthetic-runtime','storage-state','profile','__pycache__')) or '.local.' in p.name:continue
        public.append(identity(p))
    c.write(N/'version-sync-manifest.json',{'sample':c.sample(),'candidate_files':public,'publication_approval':False,
        'local_only':['DocuN/** raw evidence, results, archives, reports, runtime/operator configurations and credentials','DocuS/** user requirements/project planning not automatically public','config private/local/env files except reviewed examples','data/backups/restore/control roots, browser storage/profile, logs and captured responses','.venv/node_modules/dist/cache binaries','historical task-specific fixture runtimes'],
        'next_release':'select exact files and review secrets/paths before a separately approved commit/push; never directory-wide git add','uploaded_files':0})
    run=lambda *a:subprocess.run(['git','--no-optional-locks',*a],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    head=run('rev-parse','HEAD');assert head=='45951501d2741630a229762d6b2d3f4b34d7f702'
    assert run('config','--get','remote.origin.url')=='https://github.com/shspic/RetroLume-agent.git'
    original=get('receipt.json')['verified_inputs'];gitproof=[]
    for name in ('HEAD','index'):
        p=ROOT/'.git'/name;old=next(x for x in original if x['path']==str(p));assert c.sha(p.read_bytes())==old['sha256'];gitproof.append({'file':name,'sha256':old['sha256'],'unchanged':True})
    config=(ROOT/'.git/config').read_bytes();prefix=config.split(b'[remote "origin"]',1)[0]
    old_config=next(x for x in original if x['path']==str(ROOT/'.git/config'))
    assert c.sha(prefix)==old_config['sha256'],'preexisting config bytes changed'
    status=run('-c','core.fsmonitor=false','status','--porcelain=v1');counts={}
    for line in status.splitlines():counts[line[:2]]=counts.get(line[:2],0)+1
    c.write(N/'repository-final.json',{'sample':c.sample(),'HEAD':head,'branch':run('branch','--show-current'),'origin':run('remote','-v'),
        'protected':gitproof,'preexisting_config_bytes_unchanged':True,'config_sha256':c.sha(config),'porcelain_summary_entries':len(status.splitlines()),'porcelain_status_counts':counts,
        'read_only_remote_refs_query':{'executed':True,'exit_code':1,'error':'Recv failure: Connection was reset','live_refs':'UNVERIFIED','prior_controller_metadata':'repository-state.json: public/default main/empty branches at dispatch; not asserted current'},
        'commits_pushes_uploads':0,'public_candidates':len(public),'global_git_config_changed':False})
    rules=json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    for row in rules:assert c.sha(Path(row['absolute_path']).read_bytes())==row['sha256']
    c.write(N/'rules-and-protected-readback.json',{'sample':c.sample(),'seven_locked_rules_match':True,'shared_files_written':False,
        'unchanged_protected_inputs':[r for r in original if Path(r['path']).is_file() and c.sha(Path(r['path']).read_bytes())==r['sha256']],
        'changed_inputs':[{'path':r['path'],'before':r['sha256'],'after':c.sha(Path(r['path']).read_bytes())} for r in original if Path(r['path']).is_file() and c.sha(Path(r['path']).read_bytes())!=r['sha256']],
        'note':'Changes classified by preimages, authorized remote exception and real recovery writes; result still old exact suffix until final save.'})
    c.event('S05_case_and_source_closure_saved',cases=len(concise),public_candidates=len(public),stable_S=False)
    c.settle_offline();b=c.state();seg=c.active_segment(b);seg['offline_cursor_mono_ns']=time.monotonic_ns();c.write(E/'budget.json',b)
    print(json.dumps({'case_closure':len(concise),'source_entries':len(entries),'public_candidates':len(public),'counts':b['counts']},ensure_ascii=False))

if __name__=='__main__':main()
