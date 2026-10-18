"""S06 final local result, forward accounts and exact original suffix; no runtime or shared verdict."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,copy,difflib,re
N=Path(__file__).resolve().parent;E=N.parent;ROOT=E.parents[3]
sys.path.insert(0,str(E));import control as c
def get(name):return json.loads((N/name).read_text(encoding='utf-8'))
def ident(path):
    p=Path(path);raw=p.read_bytes();return {'path':str(p),'bytes':len(raw),'sha256':c.sha(raw)}
def link(name):return '['+name+']('+str((N/name).resolve()).replace('\\','/')+')'
def usage(b,s,stamp):
    runtime=sum(x['seconds'] for x in b['runtime_intervals'] if x.get('segment')==s['permit'])
    offline=sum(x['seconds'] for x in b['offline_intervals'] if x.get('segment')==s['permit'])
    if s.get('offline_cursor_mono_ns') is not None:offline+=(stamp['mono_ns']-s['offline_cursor_mono_ns'])/1e9
    activity=c.segment_activity_seconds(s,stamp['mono_ns'])
    return {'sample':stamp,'S06':{'activity_seconds':activity,'runtime_holding_seconds':runtime,'continuous_offresource_seconds':offline,'paused_seconds':s.get('paused_seconds',0),'offline_process_conservative_debit_seconds':s['offline_process_run_seconds'],'caps':{'activity':14400,'no_new_issues_after':10800,'save_only_after':13200,'runtime_holding':5400,'offline_process':1800,'rolling_offline':None}},'cumulative':{'activity_seconds':s['baseline_cumulative_activity_seconds']+activity,'runtime_seconds':s['baseline_cumulative_runtime_seconds']+runtime,'continuous_offresource_seconds':s['baseline_cumulative_offline_seconds']+offline,'S06_new_rolling_offline_cap':None},'counts':b['counts'],'baseline_counts':s['baseline_counts'],'old_debt_and_unknowns_preserved':True}
def tool_receipts_debit():
    # Read only this original chat. Charge measured short-tool receipts conservatively,
    # including overlap with already charged bounded children; never refund earlier time.
    rollout=Path('C:/Users/28432/.codex/sessions/2026/10/12/rollout-2026-10-12T01-41-26-01a12c0e-22b8-7e71-849b-0163931d12c7.jsonl')
    rows=[]
    with rollout.open('rb') as stream:
        start=max(0,rollout.stat().st_size-4*1024**2);stream.seek(start)
        if start:stream.readline()
        for line in stream:
            try:value=json.loads(line)
            except (ValueError,UnicodeError):continue
            if value.get('timestamp','')<'2026-10-16T13:00:19' or value.get('type')!='response_item':continue
            p=value.get('payload',{});output=p.get('output')
            if p.get('type')!='custom_tool_call_output' or not isinstance(output,list):continue
            def visit(obj):
                if isinstance(obj,dict):
                    if 'wall_time_seconds' in obj and ('exit_code' in obj or 'session_id' in obj):rows.append({'call_id':p.get('call_id'),'receipt_utc':value['timestamp'],'wall_time_seconds':obj['wall_time_seconds']})
                    for key,item in obj.items():
                        if key!='output':visit(item)
                elif isinstance(obj,list):
                    for item in obj:visit(item)
            for block in output:
                try:visit(json.loads(block.get('text','')))
                except (ValueError,TypeError):pass
    seconds=sum(x['wall_time_seconds'] for x in rows)
    c.write(N/'offline-process-tool-receipts.json',{'sample':c.sample(),'scope':'this original chat S06 measured tool receipts only; no content or secrets copied','receipts':rows,'additional_conservative_debit_seconds':seconds,'classification':'includes overlap with already charged child wall time and receipts during runtime; deliberately no subtraction/refund, not asserted CPU or exact unique process time','unexpected_gap':'not counted as CPU; retained separately in activity and off-resource upper bound'})
    return seconds
def refresh_final_identities():
    changes=get('changes.json');manifest=get('final-source-manifest.json');entries={r['path']:r for r in manifest['entries']};diff=[]
    for relative,pre in changes.items():
        p=ROOT/relative;raw=p.read_bytes();before=(ROOT/pre['backup']).read_bytes() if pre['exists'] else b''
        if pre['exists']:assert c.sha(before)==pre['sha256']
        diff.extend(difflib.unified_diff(before.decode('utf-8-sig').splitlines(),raw.decode('utf-8-sig').splitlines(),fromfile='S06-pre/'+relative,tofile='S06-final/'+relative,lineterm=''))
        entries[relative]={'path':relative,'pre':pre,'post':{'exists':True,'bytes':len(raw),'sha256':c.sha(raw)}}
    for relative,row in entries.items():
        p=ROOT/relative
        if row['post'].get('exists') is False:assert not p.exists(),relative
        else:assert c.sha(p.read_bytes())==row['post']['sha256'],relative
    manifest.update(sample=c.sample(),entries=list(entries.values()));c.write(N/'final-source-manifest.json',manifest)
    (N/'source-changes.diff').write_text('\n'.join(diff)+'\n',encoding='utf-8')
    fixtures=get('final-fixture-manifest.json');fixtures.update(sample=c.sample(),files=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())} for p in [*N.glob('*.py'),*N.glob('*.mjs')]])
    c.write(N/'final-fixture-manifest.json',fixtures)
    assert get('controller-boundaries.json')['source_sha256']==c.sha((E/'control.py').read_bytes())
    assert len(get('controller-boundaries.json')['checks'])==16
    for path in [E/'control.py',ROOT/'backend/app/data_exit/config.py',*N.glob('*.py')]:compile(path.read_text(encoding='utf-8-sig'),str(path),'exec')
    public=get('version-sync-manifest.json')
    for row in public['candidate_files']:
        p=ROOT/row['path'];raw=p.read_bytes();row.update(bytes=len(raw),sha256=c.sha(raw))
    public['sample']=c.sample();c.write(N/'version-sync-manifest.json',public)
def main():
    started=time.monotonic_ns();c.reserve_offline(60);b=c.guard();s=c.active_segment(b)
    assert s['stage']=='S06' and b['active_root'] is None and s['offline_process_run_active'] is None
    assert get('final-resource-stop-binding.json')['all_stopped'] and get('final-new-preview-and-selector-stop.json')['all_current_resources_stopped']
    assert b['counts']['provider_calls']==b['counts']['actual_fee_microunits']==0
    old=(N/'before-result.md').read_bytes();result=ROOT/'DocuN/results/TASK-117-result.md'
    assert len(old)==63687 and c.sha(old)=='4ba3402549f8d7a9c5a9cb4c6e26825ae174aae5bbdcd5740294e95ed73bbe00'
    assert result.read_bytes()==old,'preserve already-saved final result instead of regenerating it'
    refresh_final_identities();debit=tool_receipts_debit();b=c.state();s=c.active_segment(b)
    observed_before=s['offline_process_run_seconds'];s['offline_process_run_seconds']+=debit
    s['offline_process_receipt_reconciliation']={'path':str(N/'offline-process-tool-receipts.json'),'prior_bounded_and_initial_observed_seconds':observed_before,'additional_conservative_debit_seconds':debit,'overlap_not_refunded':True}
    c.write(E/'budget.json',b)
    stamp=c.sample();u=usage(b,s,stamp);assert u['S06']['activity_seconds']<13200 and u['S06']['runtime_holding_seconds']<5400 and s['offline_process_run_seconds']<1800
    counts=b['counts'];caps=s['cumulative_caps'];rows=[]
    for key in ('roots','pg_create_attempts','pg_objects','volumes','pg_starts','api_starts','browser_starts','frontend_builds','native_windows','http','preview_creates','preview_starts','provider_calls','actual_fee_microunits'):
        limit=6 if key in ('pg_create_attempts','pg_objects','volumes') else caps[key]
        rows.append(f"|{key}|{counts[key]-s['baseline_counts'][key]}|{counts[key]}|{limit}|")
    stage=get('L10/stage-times.json');t0=stage['t0_ns'];stages='；'.join(x['stage']+' '+f"{(x['at_ns']-t0)/1e9:.3f}s" for x in stage['stages'])
    ready=get('L10/supervisor-result.json');ready_s=(ready['ready_accepted_ns']-t0)/1e9
    selected=get('R02-formal-readonly-reopen.json')['selector'];configsha=c.sha((ROOT/'backend/app/data_exit/config.py').read_bytes())
    text=f'''# TASK-117 / R-111 — S06 工程增量结果

**结论：本卡剩余工程证据已收口，形成供主控集中独立复核的 S 候选。未自签独审、Q、STEP018 或项目通过；真实供应商与费用仍为0。**

许可 `TASK-117-STEP018-INTEGRATION-S06-20261016`；沿原工程窗口，实际为 Codex desktop / GPT-6，A+仅是资源标签，具体服务端子型号未披露。本轮无子Agent、无新窗口、无Git写入。S06首工具同步 UTC/QPC，原接收、失败、超额和累计账不清零。此前全部63687字节报告作为本文件完整后缀保留。

## 本轮实际完成

|范围|实际结果与边界|原件|
|---|---|---|
|X02 合同纠正与删除实效|沿save/revise/revoke/purge既有协议证明三个效果。修订/撤销晚到失效继承S03；本轮只读核实撤销清单SHA `f15b4a4aa0da44dbfebd01051c57183854e329ee7e9a902f5fbf9faa4c723576`、版本1/2各自hash/bytes与清单精确相等、正文行0、GET body=null、两个版本和6个旧选择身份保留。没有新建记忆/墓碑或独立delete。历史用户保留决定原件照留，S06纠正解除此前R02前置。|{link('X02-current-physical-deletion.json')}|
|L10 固定预览|复用原activity/artifact及SHA。真实ACK：d120/t120=1、t240=.5，t0/未知控件422，reset=1；真实PNG对应已接受seq2的.5，未将该帧冒充reset后的1。精确CID/image/nonce、private PID/init结束、双EOF、原SUP/REAP Job ActiveProcesses0及owned结束，原正常StopProof confirmed=true。|{link('L10/input-acks.json')}、{link('L10/actual-frame.png')}、{link('L10/supervisor-result.json')}|
|预览阶段及账|{stages}；ready接受在t0后{ready_s:.3f}s，原t0/3/4.5/8/D门未改。新窗reserve60、实际正常耗11、reserved0，包含旧失败60后的累计settled71、starts_used2。仅新增一次preview create/start。|{link('L10/stage-times.json')}、{link('L10/settled-status.json')}|
|X01 同一冻结PDF|942字节、SHA `ca68cb54cfdb651e6a2d4048128a1aa5d3613a83a3192bb1321df5f2ddb8fcc4`。唯一新区别诊断真实HTTP到parse，Job创建/assign/resume/exit全部实测成功，worker exit0、0.422s、输出341字节、ok=true、两物理页、无global trace，原10s/256MiB/进程上限未改。逐页确认后GET/content回查页1/2及独立补充身份。|{link('PDF-diagnostic-admission.json')}、{link('PDF-HTTP-bounded-probe.json')}、{link('PDF-two-page-confirmed.json')}|
|X03/X04 最小代表|两个不同业务键竞争同父goal槽，一项真实提交、一项409；真实query已dispatch后改变goal，晚到received回包current=false。原source真实200响应在selector/正常reload后释放，无新POST或下一动作。其余同资格函数族沿原G3/G5/G8/G9/G11有效证据映射，不扩排列。|{link('semantic-slot-race.json')}、{link('inflight-goal-invalidation.json')}、{link('R02-selector-increment.json')}|
|共享总预算|两个真实PG只读事务执行同一生产全许可advisory锁；配隔离合成预算/manifest/grant/传输，79→80请求、19750000→20000000，至多一项获准。第二事务真实等待同锁约109ms。目标SQL写入、Q名册行和真实外发均0。范围是“真实PG锁+合成预算”，不是实际外发账的端到端准入或真实条款验证。|{link('shared-global-budget-concurrency.json')}、{link('shared-global-budget-PG-lock.json')}|
|R01 当前只读应用|复用已封存R01及S05七类HTTP/四种拒写；最终bundle7真实浏览器七类历史可查看，export/backup/upload禁用，无页面POST。reader子进程没有source写、loader、维护、provider或preview执行配置，原source selector/fence未改。|{link('R01-final-browser-verified.json')}、{link('reader-host-proof.json')}、{link('browser-14/proof.json')}|
|R02 正式切换及重开|原success01/617行包与原overlay复用，当前墓碑tuple缺项[]、未知owned[]。真实原source控制根drain→freeze→latest→停止source→启动原封存target→selector提交，仅一次activate。generation1、target `{selected['target_id']}`，激活job `{selected['activation_job_id']}`。最终配置正常只读重开、GET有历史、POST409 data_readonly，source停止，无fallback/换目标/回normal。无success02或新装载。|{link('R02-current-overlay-and-owned.json')}、{link('R02-one-PG-switch-stage.json')}、{link('R02-formal-readonly-reopen.json')}、{link('browser-16/proof.json')}|

## 代码、版本与继承

产品普通修补仅使成功绑定的target schema_profile用于caps.format，避免正常R02只读重开在source_state=None时显示R01。最终 `backend/app/data_exit/config.py` SHA `{configsha}`，由API33及真实重开/拒写绑定。未改001—014、依赖锁、权限/退款/停止语义、固定renderer/验签器、原始需求、公共库、DocuS、任务卡或主控裁定。

工程控制器显式采用S06 activity/runtime/离线进程门，null表示没有第二个跨中断滚动offline门；旧amendments不遮蔽API34等新额。默认PGcreate/对象/卷仍各6；第7个仅接受原包、success02、真实新增删除差异的hash绑定证据，本轮不存在该条件。16项有限无资源边界检查通过；保存首次13项原件，后续只补控制器新增分支。reader配置3项通过，新/变Python编译与两个新浏览器夹具语法检查通过。未重跑已通过业务/恢复或G11完整停止矩阵。

正式bundle7四资产原字节未变，新增build0，JS SHA `58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8` 由Browser14/15/16实际装载。L01/I01的S03持久全链、S04/S05针对变化的真实U合并继承，不新增“同一最终Browser从头重做”前置。28项逐层映射见 {link('S-case-closure.md')}、{link('S-case-closure.json')}，唯一工程case-index已追加S06并保留旧投影；全28 T/U/Q整体验收计数仍0，Q关闭。

163项产品/既有源身份见 {link('final-source-manifest.json')}；5项pre/diff/post见 {link('changes.json')}、{link('source-changes.diff')}。最终夹具与API29—33原as-run收据分列于 {link('final-fixture-manifest.json')}，最终文件hash不冒充之前夹具修订的启动时观测。PDF探针在诊断准入时已有hash。R01 U在profile显示补丁前运行，补丁对R01仍同profile；公共绑定的最终增量由R02实际重开验证。前端代码和资产不变。

213项受保护输入目前205项原字节一致，其余8项为5个授权源码/说明变化及budget/events/case-index；最终报告新增前缀另有明确授权。旧阶段/根1—21/失败前缀/事件前缀核销见 {link('historical-ledger-preservation.json')}；最终保护复读见 {link('rules-and-protected-readback.json')}。

## 保留的真实失败与验收边界

1. 原两次PDF HTTP422及旧孤立worker成功分别保留，确切旧因未追溯确认。S06有界新HTTP直接成功，因此不再解析重试，也不宣称发现了旧因。PDF本轮观察/实现/确认在恢复后15:11至15:23的保守上界内，小于1800s；该界包含其他准备，不称CPU时间。新脚本末回查曾误用不存在的`/materials/{{id}}`得404，真实解析/确认已提交，随后仅正确GET/content补证，未重解析/重确认。
2. Browser15原整体FAIL保留：真实selector和旧响应抑制已成功；测试脚本对业务POST用了非canonical身份头，被409 selection_changed提前拒绝。该子集按原件提取；Browser16在同一永久只读目标、正常重开后以canonical头得到409 data_readonly，不重复切换。原失败夹具未改写为PASS。
3. 首次隔离合成全局门离线检查45s超时保留，完整CIM未发现对应Python遗留。加入有界阶段观察和8s内部截止后通过；未猜测首次超时原因。随后真实PG锁区别检查亦通过，仍不创建Q行。
4. 旧预览首次UNCONFIRMED、S01—S05漏采/失败/超额、旧unknown和预留不回填。新正常StopProof不能替旧首次作成功。真实供应商语义、真实价格/条款采用、隔离集中独审、STEP及项目验收由主控后续安排，本报告不自签。

## 停止与每段累计账

本轮实际新根仅22/23/24三个，根内继续均保留首次2100+300s截止与原计数。最终6个精确PG全部非running/Pid0，固定15481—15487/18118无监听，登记API/Browser原出生实例结束、缓存Chromium/Node后代无残留。PID复用按birth区别，用户/其他进程未动。旧预览现有Job不存在仅记录error2，不冒历史ActiveProcesses0；新预览的原Job结尾确有0与双EOF。永久R02选择器及frozen围栏保留，owned在途0。见 {link('final-resource-stop-binding.json')}、{link('final-old-preview-stop.json')}、{link('final-new-preview-and-selector-stop.json')}。

计数截至当前：

|计数|S06新增|累计|本段有效累计门|
|---|---:|---:|---:|
{chr(10).join(rows)}

第7对象的条件额未启用，PG create/object/volume新增0；真实provider、费用、Q运行、Git写入均0。Browser累计16已到门，不再启动；保留未用根/PG/API额度，不挪作重试池。

报告生成采样：S06活动 {u['S06']['activity_seconds']:.3f}s /14400，保守真实持有 {u['S06']['runtime_holding_seconds']:.3f}s /5400，连续无资源区间 {u['S06']['continuous_offresource_seconds']:.3f}s（没有第二个滚动offline硬门）；明确暂停0。离线进程先有观测 {observed_before:.3f}s，另将本聊天工具墙钟收据 {debit:.3f}s保守追加扣账，含嵌套/持有期间重叠不退款，合计 {s['offline_process_run_seconds']:.3f}s /1800；不称精确唯一CPU或人工时间。最终脚本运行与保存/复读追加以 {link('final-budget-observed.json')} 为准。工具收据明细见 {link('offline-process-tool-receipts.json')}。

S06本轮恢复入口15:11:25与首工具13:00:19之间未预登记暂停，中断空档保留在活动及连续无资源上界，不私自退款，见 {link('resume-gap-audit.json')}。累计活动 {u['cumulative']['activity_seconds']:.3f}s、持有 {u['cumulative']['runtime_seconds']:.3f}s、连续无资源记录 {u['cumulative']['continuous_offresource_seconds']:.3f}s。原S05活动16611.729874/持有159.953/offline16451.527874，超offline5651.527874；旧累计offline25463.164991/19812超5651.164991，以及S01—S04原失败/超额均保持。S06不将null当0，也不追改旧门。

## 本地交付与独立复核入口

README已同步实际删除合同和验证限制。Git HEAD `45951501d2741630a229762d6b2d3f4b34d7f702`、index、config原字节未变；沿S05既有origin `https://github.com/shspic/RetroLume-agent.git`，S06无commit/push/upload/远端refs重试。旧远端连接重置与派发时元数据仍按历史记录，不冒当前远端结果。见 {link('repository-final.json')}、{link('version-sync-manifest.json')}。清单是待另行批准的精确文件候选，原始证据/数据/配置凭据/备份/用户文档不整包公开。

交主控安排一次隔离A+集中独立复核，重点审：原日志缓存的完整字节/身份与尾帧保护；owned恢复和新预览原StopProof、阶段钟/结算；PDF探针覆盖与正常确认/引用；R01最小能力reader；R02唯一原source selector及最终只读重开；最终profile显示修补；跨provider总门真实锁与合成预算适用边界。独立审查原件入口为 {link('final-binding.json')}、{link('final-readback.json')}。

---

以下为此前63687字节完整原报告，S06不改写其历史结论、失败或数字。

'''
    prefix=text.encode('utf-8');result.write_bytes(prefix+old);actual=result.read_bytes();assert actual==prefix+old and actual[-63687:]==old
    c.write(N/'result-save-receipt.json',{'sample':c.sample(),'result':ident(result),'prefix_bytes':len(prefix),'old_suffix_bytes':63687,'old_suffix_sha256':c.sha(actual[-63687:]),'exact_suffix_preserved':True,'UTF8_readback':bool(actual.decode('utf-8'))})
    # Final protection readback includes the newly authorized report prefix.
    protected=get('rules-and-protected-readback.json');protected['final_sample']=c.sample();protected['report_prefix_authorized']=True;protected['result_exact_old_suffix']=True
    for row in protected['authorized_changes']:row['current_sha256']=c.sha(Path(row['path']).read_bytes())
    for row in protected['unchanged']:
        p=Path(row['path'])
        if p==result:continue
        assert (c.sha(p.read_bytes()) if p.exists() else None)==row['sha256'],str(p)
    protected['result_after_save']=ident(result);c.write(N/'rules-and-protected-readback.json',protected)
    c.settle_offline();b=c.state();s=c.active_segment(b);ended=c.sample();own=(ended['mono_ns']-started)/1e9
    s['offline_process_run_seconds']+=own;s.update(status='returned_engineering_candidate',end=ended,activity_seconds_at_return=c.segment_activity_seconds(s,ended['mono_ns']),offline_cursor_mono_ns=None,return_disposition='engineering S candidate; independent audit/Q/STEP not self-signed; all exact resources stopped')
    assert s['activity_seconds_at_return']<13200 and s['offline_process_run_seconds']<1800
    b['phase']='S06_returned_engineering_candidate';b['s06_return_disposition']={'sample':ended,'result_path':str(result),'resources_stopped':True,'old_failures_and_overruns_preserved':True};c.write(E/'budget.json',b)
    c.event('S06_returned_engineering_candidate',result_sha256=c.sha(actual),old_suffix_sha256=c.sha(old),real_provider_calls=0,Q='NOT_ENABLED',independent_review='NOT_SELF_SIGNED')
    final=usage(b,s,ended);final['status']=s['status'];final['all_current_resources_stopped']=True;final['final_script_observed_seconds']=own;c.write(N/'final-budget-observed.json',final)
    files=[result,E/'budget.json',E/'events.jsonl',E/'case-index.json']+[N/x for x in ('receipt.json','final-budget-observed.json','final-source-manifest.json','final-fixture-manifest.json','source-changes.diff','rules-and-protected-readback.json','historical-ledger-preservation.json','controller-boundaries.json','S-case-closure.json','final-bundle-7-binding.json','final-resource-stop-binding.json','final-old-preview-stop.json','final-new-preview-and-selector-stop.json','X02-current-physical-deletion.json','PDF-HTTP-bounded-probe.json','PDF-two-page-confirmed.json','R01-final-browser-verified.json','R02-selector-increment.json','R02-formal-readonly-reopen.json','shared-global-budget-PG-lock.json','result-save-receipt.json','repository-final.json','version-sync-manifest.json')]
    binding={'sample':c.sample(),'entries':[ident(p) for p in files],'engineering_candidate_ready':True,'independent_review':False,'Q':'NOT_ENABLED','no_runtime_resources':True};c.write(N/'final-binding.json',binding)
    for row in binding['entries']:assert c.sha(Path(row['path']).read_bytes())==row['sha256'],row['path']
    assert result.read_bytes()==actual and c.sha(result.read_bytes()[-63687:])=='4ba3402549f8d7a9c5a9cb4c6e26825ae174aae5bbdcd5740294e95ed73bbe00'
    c.write(N/'final-readback.json',{'sample':c.sample(),'result':ident(result),'binding_sha256':c.sha((N/'final-binding.json').read_bytes()),'bindings_read_back':len(files),'old63687_suffix_exact':True,'saved_and_readable':True,'budget_status':s['status'],'active_root':b['active_root'],'all_current_resources_stopped':True,'final_counters':b['counts'],'actual_Q_or_independent_acceptance':False})
    print(json.dumps({'saved':str(result),'bytes':len(actual),'sha256':c.sha(actual),'old63687_suffix_exact':True,'binding_files':len(files),'status':s['status'],'activity_seconds':final['S06']['activity_seconds'],'offline_process_conservative_debit_seconds':s['offline_process_run_seconds'],'all_resources_stopped':True},ensure_ascii=False))
if __name__=='__main__':main()
