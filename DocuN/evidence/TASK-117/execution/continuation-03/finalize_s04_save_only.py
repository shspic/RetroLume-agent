from pathlib import Path
import sys,json,time,difflib,ast
r=Path.cwd();e=r/'DocuN/evidence/TASK-117/execution';n=e/'continuation-03';sys.path.insert(0,str(e));import control as c
b=c.state(); sg=c.active_segment(b); sg['offline_cursor_mono_ns']=max(x['end_mono_ns'] for x in b['offline_intervals'] if x.get('segment')==sg['permit']); c.write(e/'budget.json',b)
stop=json.loads((n/'final-resource-stop-binding.json').read_text());assert stop['all_stopped'];v=c.state();assert v['active_root'] is None
c.settle_offline();v=c.state();s=c.active_segment(v);stamp=c.sample();runtime=sum(x['seconds'] for x in v['runtime_intervals'] if x.get('segment')==s['permit']);offline=sum(x['seconds'] for x in v['offline_intervals'] if x.get('segment')==s['permit']);elapsed=(stamp['mono_ns']-s['start_mono_ns'])/1e9
verified=json.loads((n/'P03-S04-verified.json').read_text());reason=json.loads((n/'reason-sufficient-no-successor-persistent.json').read_text());browser=json.loads((n/'final-UI-passed.json').read_text());assert browser['proof']['status']=='passed' and browser['proof']['browser_closed']
report=r/'DocuN/results/TASK-117-result.md';old=(n/'before-result.md').read_bytes();assert len(old)==40682 and c.sha(old)=='4347b1e249f2d405ecc7ef39c66c78253ebc5c971266781e1a17c8205e59d473';assert report.read_bytes()==old
# README只补当前真实可用边界，原字节先存。
changes=json.loads((n/'changes.json').read_text());previous=json.loads((e/'continuation-02/final-source-manifest.json').read_text());paths={x['path'] for x in previous['entries']}|set(changes)|{p.relative_to(r).as_posix() for p in n.glob('*.py')}|{p.relative_to(r).as_posix() for p in (r/'frontend/dist').rglob('*') if p.is_file()};rows=[];diff=[]
for path in sorted(paths):
 p=r/path;post={'exists':p.is_file(),'bytes':p.stat().st_size if p.is_file() else 0,'sha256':c.sha(p.read_bytes()) if p.is_file() else None};rows.append({'path':path,'pre':changes.get(path),'post':post})
 pre=changes.get(path)
 if pre and pre.get('exists') and 'frontend/dist/' not in path:
  b=r/pre['backup'];assert c.sha(b.read_bytes())==pre['sha256'];diff.extend(difflib.unified_diff(b.read_text(encoding='utf-8-sig').splitlines(True),p.read_text(encoding='utf-8-sig').splitlines(True) if p.is_file() else [],fromfile='S04-pre/'+path,tofile='S04-post/'+path))
(n/'source-changes.diff').write_text(''.join(diff),encoding='utf-8');c.write(n/'final-source-manifest.json',{'sample':stamp,'entries':rows,'scope':'继承136项并绑定必要增量；新增辅助文件不追造提前pre，原as-run失败保存'})
idx=json.loads((e/'case-index.json').read_text());idx['S04']={'sample':stamp,'stable_S':False,'Q':'NOT_ENABLED','final_bundle':'bundle-7.json','L05':'三分支离线区别通过；新合法两独立实例evidence_sufficient/无后继理由实际持久','X08':'Browser10/11真实answer/query/feedback COMMIT后丢回包及原键GET，未重发原answer','I01_UI_gate':'当前正式bundle7真实载入，目标未就绪按钮禁用，随后非空持久目标查询与question提交','P03_load':'原包/原完整控制日志，真实31表全列codec回读、撤loader及seal通过；新reader应用GET/拒POST未跑','P02':'原seal继承，新应用查看未跑','L10':'真实artifact已生成；首次宿主reaper_not_ready/cleanup_unconfirmed，原StopProof不确认；当前物理资源另证不存在','X01':'一次有限离线核对无新具体依据，未做第三次HTTP重试','remaining':['L08只选J-CODE后的范围澄清','独立记忆正文delete/current/late最终U','X03/X04/X07尚缺的最终U','P02/P03新reader应用GET与拒POST','固定宿主ACK/PNG/可信读值和原StopProof','PDF真实HTTP'],'old_failures_and_matrix_kept':True};c.write(e/'case-index.json',idx);c.write(n/'final-case-index.json',idx)
counts=v['counts'];budget={'sample':stamp,'S04':{'elapsed_seconds':elapsed,'runtime_conservative_seconds':runtime,'offline_seconds':offline,'caps':{'activity':14400,'runtime':7200,'offline':2400},'offline_overrun_seconds':max(0,offline-2400),'new_roots':[17,18],'counts':counts},'cumulative':{'activity_seconds':86678.9850744+elapsed,'runtime_seconds':23476.767+runtime,'offline_seconds':6229.341117+offline,'offline_forward_cap':9000},'S03_old_overruns_preserved':True,'S01_S02_old_overruns_preserved':True,'all_resources_currently_stopped':True};c.write(n/'final-budget-observed.json',budget)
def link(name):return str((n/name).resolve()).replace('\\','/')
prefix=f'''# TASK-117 / R-111 S04 结果，部分交付，完整S未通过

保存于{stamp['utc']}。R02装载超时已完成有据修补和真实同包成功恢复；最终bundle7、三类COMMIT丢回包及派生理由取得新证据。固定预览、PDF、normal余项及R01/R02新reader应用查看仍未闭，不自签完整S、STEP018或项目验收。

## 恢复慢点与实际成功

原日志516450字节与同617行/3938960字节包受控对照。最大依赖组件在未执行SQL时，原逐行全日志验证/重放已耗32.108秒；修补后同组件0.942秒，全部872个检查完成、检查耗3.055秒。读包校验0.824秒、重复图/包扫描1.224秒。不是把静态怀疑当唯一SQL根因。详见[有限计时]({link('restore-cost-final-diagnosis.json')})及[snapshot函数计时]({link('snapshot-profile.txt')})。

ControlHub在真实锁内每次读取当前完整字节，核fd/path身份与大小及摘要，只复用同一身份和摘要的已验证投影；Operation只复制当前job。缓冲按当前size+1有界读取，保留64MiB总门。append、同大小同mtime篡改、截断、文件替换、peer取消、revision/clock authority与返回对象隔离均有真实文件反例，六项检查通过。CAS、取消、总deadline、组件30秒、文件完整性、trigger/CHECK及依赖组件事务闭包均未放宽。未改001—013或重跑两库SQL修补。

根18在原控制根完整日志{json.loads((n/'root18-before-create-as-run.json').read_text())['original_full_control_journal_bytes']}字节上使用相同原包，root SHA仍b040841394dfa82a14c2b180e60393b3b7f0d222b11016b468a81d6f17c3a347；重新prepare当前deletion overlay。新slot为r02-success-01，CID {verified['target']['cid']}，target {verified['target']['target_id']}，job {verified['receipt']['job_id']}，verified并sealed，耗{verified['verify_seconds']:.3f}秒。实际31表codec逐列canonical回读相等，含512维float32、007、unknown/预留及删除覆盖；真实readonly角色拒写、loader撤销与封印通过，非仅counts。详见[实际恢复/封印原件]({link('P03-S04-verified.json')})和[创建前as-run]({link('root18-before-create-as-run.json')})。旧两个failed目标未复用，第二成功slot未创建。

normal余项仍需写资格，且固定宿主的原停止协议未闭，因此未激活R01/R02，源selector和fence均空，不把任一sealed目标改normal或fallbacksource。P02/P03新reader应用GET与拒POST未完成；R01旧seal/UPDATE42501继承。后续先收口normal依赖，再按真实owner/control根安排两种reader，不能清空selector或复制秘密授权。

## 最终界面与新理由

教学编辑身份尚未就绪时输入可被载入过程覆盖，已增加当前活动/题目/本机draft就绪门。正式build7及typecheck通过，JS SHA为58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8。Browser11真实载入该字节，完成三类服务端成功后丢回包：answer继承Browser10真实COMMIT/GET，query和feedback在11实际提交并按原键GET恢复；没有重发原answer。面试目标正文尚未载入时按钮禁用，随后使用非空持久目标查询并提交question。Browser11已确认关闭。详见[最终U实际范围]({link('final-UI-passed.json')})。该定向新场景不替代S03两域完整持久链或同normal应用重开，旧成功证据直接继承；最终矩阵仍按实际层列缺口。

理由分证据不足、证据已足无后继和可推进，三分支离线区别通过。首次新场景的多组数值答被有限parser判unchecked，保留revision10与失败，不改旧答或追造独立资格。明确的新无记忆N场景{reason['activity_id']}取得两份不同独立实例、evidence_sufficient，原样保存无后继理由，advance=false，不宣称长期掌握。详见[新合法持久理由]({link('reason-sufficient-no-successor-persistent.json')})。夹具原mode错误由新入口按current_mode读取，原错误文件和复制说明不改。

## 失败、停止与未闭项

Browser9在首次answer前因过早输入失败，其无界response观察等待由原父控制器有限等待终止，原cleanup未确认保留；后来的精确当前停止另证。补输入门/build7及有限drain/关闭后，Browser10已真实提交并GET恢复answer，因状态容器exact文本定位失败；Browser11继承真实storage/session-storage，修正定位后从未完成处继续。原记录/as-run均留存，没有整体重做两域。中间一次自动审批复核超时，动作未执行，按平台许可原样重试一次成功；没有绕过审批，不把它归为动作不安全。

固定HTML父成果和artifact已真实生成。首次固定宿主在reaper就绪前返回reaper_not_ready，cleanup_unconfirmed，原supervisor-result confirmed=false/proof=null，SUP Job最终ActiveProcesses0。原reaper PID26892及launcher/parent现均退出，精确preview标签无CID，五旧PG及新成功PG、API/Node/Chromium和端口另经当前清场核查。当前不存在不改写原StopProof为通过，未取得ACK/PNG或可信读值。固定宿主/renderer/验签/Job及限制未改，不裸重试。详见[预览当前物理停止与原未确认边界]({link('preview-late-current-absence.json')})和[最终停止绑定]({link('final-resource-stop-binding.json')})。

PDF仅作一次有限离线源码/旧失败核对，没有新的具体HTTP根因，保持原两次422与孤立成功，不做第三次裸重试。L08单J-CODE、记忆独立正文清理/current/late及X03/X04/X07尚缺的最终U未执行完，不冒通过。[唯一case-index]({str((e/'case-index.json').resolve()).replace(chr(92),'/')})保留28例原历史并加S04层。Q始终关闭，真实provider与实际费用0，旧AP2条件许可和旧账不变，独立终审未执行。

## 身份、预算与交回

[最终源码manifest]({link('final-source-manifest.json')})、[pre至post差异]({link('source-changes.diff')})、各根as-run和原始HTTP/Browser/restore已绑定实际对象。README本轮未更新，offline硬门后仅保存结果；既有README保留，本报告明确当前限制。不写共享DocuS、任务卡、裁定、Git或公共库。原40682字节结果全文在后保持不变。

S04 elapsed {elapsed:.3f}秒，保守持有{runtime:.3f}秒，offline {offline:.3f}/2400秒；本次offline超额{max(0,offline-2400):.3f}秒如实列账，进入最终保存清场，不启新业务。原S03活动超10124.280秒、offline超682.780秒及漏首采、S01/S02旧失败/超额均保留。S04首写工具同次直接采UTC/QPC，没有回推签发时间。累计counts {json.dumps(counts,ensure_ascii=False)}。[分段与累计账]({link('final-budget-observed.json')})仍以原budget.json/events.jsonl为唯一主账；未因换根/失败/旧报告继承退款或清零。

最小下一步是固定宿主reaper就绪/原StopProof的有据处置、normal定向U/范围/独立清理余项及PDF的具体原因；这些闭合后补两个profile真实应用只读查看。不是继续原样整批重跑，也不是仅追加入口或额度。物理清场已确认，未开启根19或第二成功slot；工程结果仍部分交付。

## 以下完整保留S03、S02及S01原件

'''
report.write_bytes(prefix.encode('utf-8')+old);assert report.read_bytes().endswith(old)
receipt={'sample':c.sample(),'permit':s['permit'],'status':'partial_returned','stable_S':False,'result':str(report),'sha256':c.sha(report.read_bytes()),'bytes':report.stat().st_size,'old40682_bytes_exact_suffix':True,'all_resources_currently_stopped':True,'original_preview_StopProof':'UNCONFIRMED','business_authorization_returned':True}
v['phase']='S04_returned_partial';v['s04_return_disposition']=receipt
for x in v['segments']:
 if x['permit']==s['permit']:x['return_disposition']=receipt
c.write(e/'budget.json',v);c.event('S04_returned_partial',sha256=receipt['sha256'],all_current_resources_stopped=True,original_preview_StopProof='UNCONFIRMED',stable_S=False);c.write(n/'result-save-receipt.json',receipt)
c.write(n/'final-binding.json',{'sample':c.sample(),'result':receipt,'source_manifest_sha256':c.sha((n/'final-source-manifest.json').read_bytes()),'case_index_sha256':c.sha((e/'case-index.json').read_bytes()),'budget_sha256':c.sha((e/'budget.json').read_bytes()),'stop':stop})
for row in rows:
 p=r/row['path'];assert p.is_file()==row['post']['exists']
 if p.is_file():assert c.sha(p.read_bytes())==row['post']['sha256']
assert report.read_bytes()[-40682:]==old
print(json.dumps({'result':str(report),'sha256':receipt['sha256'],'source_identities_verified':len(rows),'all_stopped':True,'stable_S':False,'S04_offline_seconds':offline},ensure_ascii=False))
