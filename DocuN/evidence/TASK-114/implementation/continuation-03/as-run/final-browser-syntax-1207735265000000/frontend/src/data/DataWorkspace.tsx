import React,{useEffect,useRef,useState} from 'react';
import {dataRequest as fetchData,downloadPackage,exportDrafts,jobKeys,rememberJob,type Job,type Plan} from './dataApi';
import {dataFetch,useDataContext,setDataContext} from './context';
import './data.css';
import {fileHash} from './fileHash';
import {ReadonlyRecords} from './ReadonlyRecords';
type Material={id:string;title:string;revision:number};
type InputKind='restore'|'scope';
type InputBinding={kind:InputKind;epoch:number;revision:number};
type BoundPlan={value:Plan;binding:InputBinding};
type BoundScope={value:any;binding:InputBinding};
const stages:Record<string,string>={prepared:'准备中',reading:'读取已保存记录',copying:'复制原件',verifying:'核对完整性',published:'已保存',published_unconfirmed:'文件已保存，收据待核对',allocating:'建立隔离验证副本',loaded:'内容已加载，尚未封存',verified:'副本已验证，当前应用仍使用原数据',active_readonly:'当前读取恢复副本',selector_committed:'选择已提交，操作收据待核对',failed:'本次未完成，已有数据和旧备份保留',cancel_requested:'已请求取消，等待收尾确认',cancelled:'已取消并确认收尾',cleanup_unconfirmed:'收尾结果待核对',restore_unconfirmed:'恢复结果待核对',activation_unconfirmed:'切换结果待核对',deleted:'本条资料回查内容已删除',cleanup_pending:'墓碑已生效，原件清理待确认',deletion_unconfirmed:'删除结果待核对'};
export function DataWorkspace({token,onSelection}:{token:string;onSelection:()=>Promise<void>}){
  const context=useDataContext(),[caps,setCaps]=useState<any>(null),[jobs,setJobs]=useState<Job[]>([]),[materials,setMaterials]=useState<Material[]>([]);
  const [error,setError]=useState(''),[busy,setBusy]=useState(false),[selected,setSelected]=useState<string[]>([]),[mode,setMode]=useState('all');
  const [boundPlan,setBoundPlan]=useState<BoundPlan|null>(null),[policy,setPolicy]=useState('respect_current_deletions'),[confirmSnapshot,setConfirmSnapshot]=useState(false),[unknown,setUnknown]=useState(false);
  const [restoreJob,setRestoreJob]=useState<Job|null>(null),[lookup,setLookup]=useState(''),[impact,setImpact]=useState<any>(null),[deleteConfirm,setDeleteConfirm]=useState(false);
  const [boundScope,setBoundScope]=useState<BoundScope|null>(null),[activities,setActivities]=useState<any[]>([]),[selectedActivities,setSelectedActivities]=useState<string[]>([]);
  const lifetime=useRef(0),mounted=useRef(false),refreshSequence=useRef(0),refreshAbort=useRef<AbortController|null>(null);
  const revisions=useRef({restore:0,scope:0}),planRef=useRef<BoundPlan|null>(null),restoreRef=useRef<Job|null>(null),policyRef=useRef(policy);
  const plan=boundPlan?.value??null,scopePreview=boundScope?.value??null;
  function checkpoint(epoch=lifetime.current){if(!mounted.current||epoch!==lifetime.current)throw new DOMException('Aborted','AbortError');}
  function bind(kind:InputKind):InputBinding{checkpoint();return {kind,epoch:lifetime.current,revision:revisions.current[kind]};}
  function current(binding:InputBinding){return mounted.current&&binding.epoch===lifetime.current&&binding.revision===revisions.current[binding.kind];}
  function checkInput(binding:InputBinding){checkpoint(binding.epoch);if(!current(binding))throw new DOMException('Aborted','AbortError');}
  function invalidate(kind:InputKind){
    ++revisions.current[kind];
    if(kind==='scope')setBoundScope(null);
    else{planRef.current=null;restoreRef.current=null;setBoundPlan(null);setRestoreJob(null);setUnknown(false);}
  }
  function installPlan(value:Plan,binding:InputBinding,expectedPolicy:string){
    checkInput(binding);
    if(value.deletion_policy!==expectedPolicy||policyRef.current!==expectedPolicy)throw new Error('删除处理已改变，请重新核对备份。');
    const next={value,binding};planRef.current=next;setBoundPlan(next);
  }
  const planCurrent=!!boundPlan&&current(boundPlan.binding)&&plan?.deletion_policy===policy;
  const planConfirmed=planCurrent&&(policy!=='snapshot_only_readonly'||confirmSnapshot)&&(plan?.latest_status==='known'||unknown);
  function actionPlan(){
    const next=planRef.current;
    if(!next||!planConfirmed||!next.value.executor_configured||next.value.deletion_policy!==policyRef.current)throw new Error('请按当前文件和删除处理重新核对并确认备份。');
    checkInput(next.binding);return next;
  }
  async function request(path:string,body?:unknown,options:{signal?:AbortSignal;capabilityRefresh?:boolean}={}){
    checkpoint();const epoch=lifetime.current;const value=await fetchData(token,path,body,options);checkpoint(epoch);return value;
  }
  async function run(work:()=>Promise<void>){const epoch=lifetime.current;setBusy(true);setError('');try{await work();}catch(reason){if(mounted.current&&epoch===lifetime.current&&!(reason instanceof DOMException&&reason.name==='AbortError'))setError(reason instanceof Error?reason.message:'本次操作未完成');}finally{if(mounted.current&&epoch===lifetime.current)setBusy(false);}}
  async function refresh(){
    checkpoint();const epoch=lifetime.current,sequence=++refreshSequence.current;
    const expectedPlan=planRef.current,expectedJob=restoreRef.current;
    refreshAbort.current?.abort();const controller=new AbortController();refreshAbort.current=controller;
    const valid=()=>{checkpoint(epoch);if(controller.signal.aborted||sequence!==refreshSequence.current)throw new DOMException('Aborted','AbortError');};
    const value=await request('/capabilities',undefined,{signal:controller.signal,capabilityRefresh:true});valid();
    if(value.dataset_id&&!setDataContext(value))throw new Error('能力响应已过期，请重新刷新。');
    valid();setCaps(value);
    const list:Job[]=[];for(const key of jobKeys()){try{list.push(await request(`/jobs/by-key/${encodeURIComponent(key)}`,undefined,{signal:controller.signal}));}catch{valid();}}
    valid();
    setJobs(list);
    const restored=expectedJob&&list.find(j=>j.job_id===expectedJob.job_id&&j.plan_id===expectedPlan?.value.plan_id);
    if(restored&&expectedPlan&&expectedJob){
      const nextPlan:Plan=await request(`/restore-plans/${restored.plan_id}`,undefined,{signal:controller.signal});valid();
      if(current(expectedPlan.binding)&&planRef.current===expectedPlan&&restoreRef.current?.job_id===expectedJob.job_id){
        if(nextPlan.plan_id!==expectedPlan.value.plan_id||nextPlan.plan_sha256!==expectedPlan.value.plan_sha256||nextPlan.package_root_sha256!==expectedPlan.value.package_root_sha256)throw new Error('原计划身份不一致，请重新核对备份。');
        installPlan(nextPlan,expectedPlan.binding,expectedPlan.value.deletion_policy);restoreRef.current=restored;setRestoreJob(restored);
      }
    }
    if(value.current_mode!=='unavailable'){const response=await dataFetch('/api/materials',{headers:{'X-RetroLume-Session':token},signal:controller.signal});if(response.ok){const body=await response.json();valid();setMaterials(body.items);}}
    if(value.current_mode!=='unavailable'){const response=await dataFetch('/api/activities?limit=20',{headers:{'X-RetroLume-Session':token},signal:controller.signal});if(response.ok){const body=await response.json();valid();setActivities(body.items??[]);}}
  }
  useEffect(()=>{
    mounted.current=true;const epoch=++lifetime.current;
    invalidate('restore');invalidate('scope');setConfirmSnapshot(false);setBusy(false);
    setMaterials([]);setActivities([]);setSelected([]);setSelectedActivities([]);setImpact(null);
    void refresh().catch(reason=>{if(mounted.current&&epoch===lifetime.current&&reason.name!=='AbortError')setError(reason.message);});
    return()=>{mounted.current=false;++lifetime.current;++refreshSequence.current;refreshAbort.current?.abort();};
  },[token,context?.control_id,context?.instance_id,context?.selection_generation]);
  async function create(kind:string){
    const binding=bind('scope');
    if(mode==='selected'&&(!boundScope||!current(boundScope.binding)||!scopePreview?.closure_sha256))throw new Error('范围已改变，请重新核对证据依赖。');
    if(kind==='restore_checkpoint'&&mode!=='all')throw new Error('恢复备份需要全部已保存内容。');
    const key=crypto.randomUUID();rememberJob(key);
    const receipt=await request('/jobs',{kind,business_key:key,scope:{mode,...(mode==='selected'?{source_ids:selected,activity_ids:selectedActivities,expected_closure_sha256:scopePreview.closure_sha256}:{})},confirm:true});
    checkInput(binding);
    setJobs(old=>[...old.filter(j=>j.job_id!==receipt.job_id),receipt]);
  }
  async function upload(file:File){
    const binding=bind('restore'),expectedPolicy=policyRef.current;
    const key=crypto.randomUUID(),id=crypto.randomUUID();rememberJob(key);
    const sha=await fileHash(file);checkInput(binding);
    const query=new URLSearchParams({business_key:key,upload_id:id,expected_sha256:sha,expected_bytes:String(file.size)});
    const response=await dataFetch('/api/data/uploads?'+query,{method:'POST',headers:{'X-RetroLume-Session':token},body:file});
    const value=await response.json();if(!response.ok)throw new Error(value.detail??'备份未接收');
    checkInput(binding);
    const nextPlan:Plan=await request('/restore-plans',{upload_id:value.upload_id,deletion_policy:expectedPolicy});checkInput(binding);
    installPlan(nextPlan,binding,expectedPolicy);restoreRef.current=null;setRestoreJob(null);
  }
  async function verify(){const next=actionPlan();const key=crypto.randomUUID();rememberJob(key);const value:Job=await request('/restore-jobs',{plan_id:next.value.plan_id,expected_plan_sha256:next.value.plan_sha256,business_key:key,confirm:true,acknowledge_unknown_deletions:unknown});checkInput(next.binding);if(value.plan_id!==next.value.plan_id)throw new Error('验证收据与当前计划不一致。');restoreRef.current=value;setRestoreJob(value);setJobs(old=>[...old,value]);}
  async function activate(){const next=actionPlan(),job=restoreRef.current;if(!job||job.plan_id!==next.value.plan_id||job.state!=='verified'||context?.current_mode==='restored_readonly')throw new Error('当前计划尚无已验证副本。');const key=crypto.randomUUID();rememberJob(key);await request(`/restore-jobs/${job.job_id}/activate-readonly`,{expected_plan_sha256:next.value.plan_sha256,business_key:key,expected_selection_generation:context?.selection_generation??0,confirm:true});checkInput(next.binding);await onSelection();}
  async function checkScope(){const binding=bind('scope');const value=await request('/scope-preview',{scope:{mode,source_ids:selected,activity_ids:selectedActivities}});checkInput(binding);setBoundScope({value,binding});}
  async function preview(material:Material){setImpact(await request(`/materials/${material.id}/deletion-preview`,{expected_revision:material.revision}));setDeleteConfirm(false);}
  async function remove(){if(!impact)return;const key=crypto.randomUUID();rememberJob(key);const value=await request(`/materials/${impact.source_id}/deletions`,{expected_revision:impact.expected_revision,impact_sha256:impact.impact_sha256,business_key:key,confirm:true});setJobs(old=>[...old,value]);setImpact(null);await onSelection();}
  return <main className="data-workspace"><h1>数据与备份</h1><p>导出可独立阅读的已保存内容，保存一致备份，并在隔离副本中核对。浏览器未提交草稿不在服务器备份。</p>
    {error&&<p role="alert">{error}</p>}{caps?.current_mode==='unavailable'&&<p>{caps.control_id?'当前资料库暂不可读取，已保存的操作仍可核对；写入已关闭。':'数据与备份尚未配置；本机已有资料不会自动迁移。'}</p>}
    {context?.read_only&&<p role="status">当前仅供只读查看，旧调用、工具和预览的执行资格未恢复。原数据保留，持续使用需后续验收。</p>}
    <section><h2>导出与保存</h2><label>范围<select value={mode} onChange={event=>{invalidate('scope');setMode(event.target.value);}}><option value="all">全部已保存内容</option><option value="selected">选择资料及活动</option></select></label>
      {mode==='selected'&&materials.map(material=><label key={material.id}><input type="checkbox" checked={selected.includes(material.id)} onChange={event=>{invalidate('scope');setSelected(old=>event.target.checked?[...old,material.id]:old.filter(id=>id!==material.id));}}/>{material.title}</label>)}
      {mode==='selected'&&activities.map(activity=><label key={activity.activity_id??activity.id}><input type="checkbox" checked={selectedActivities.includes(activity.activity_id??activity.id)} onChange={event=>{invalidate('scope');const id=activity.activity_id??activity.id;setSelectedActivities(old=>event.target.checked?[...old,id]:old.filter(value=>value!==id));}}/>活动 {activity.activity_id??activity.id}</label>)}
      {mode==='selected'&&<button disabled={busy||!selected.length&&!selectedActivities.length} onClick={()=>run(checkScope)}>核对自动加入的证据依赖</button>}
      {scopePreview&&<p>将保存 {scopePreview.materials.map((m:any)=>m.title).join('、')}，共 {scopePreview.activity_count} 个活动。核对后范围若改变，本次导出会停止。</p>}
      <p>导出会加入所需的历史版本和证据关系。已撤销记忆正文排除；在途调用和未知预留如实保留，不能获得新的可消费额度。</p>
      <button disabled={busy||!caps?.backup_available||mode==='selected'&&(!boundScope||!current(boundScope.binding))} onClick={()=>run(()=>create('portable_export'))}>导出这些已保存内容</button>
      <button disabled={busy||!caps?.backup_available||mode!=='all'} onClick={()=>run(()=>create('restore_checkpoint'))}>保存当前时点的恢复备份</button>
      <button onClick={()=>run(exportDrafts)}>单独下载未提交浏览器草稿</button></section>
    <section><h2>核对与恢复备份</h2>{caps?.target_observation_status==='unknown'&&<p>已选择的只读副本暂不可读取；已保存操作仍可核对，写入保持关闭。</p>}<label>删除处理<select value={policy} onChange={event=>{invalidate('restore');policyRef.current=event.target.value;setPolicy(event.target.value);setConfirmSnapshot(false);}}><option value="respect_current_deletions">尊重当前已删除内容</option><option value="snapshot_only_readonly">按备份时点只读查看</option></select></label>
      {policy==='snapshot_only_readonly'&&<label><input type="checkbox" checked={confirmSnapshot} onChange={e=>{if(!e.target.checked)invalidate('restore');setConfirmSnapshot(e.target.checked);}}/>确认旧备份可能重新显示已删除内容，仅限隔离只读副本；源墓碑保留</label>}
      <label>选择备份文件<input type="file" accept=".rldata" disabled={busy||!caps?.restore_executor_configured||policy==='snapshot_only_readonly'&&!confirmSnapshot} onChange={event=>{invalidate('restore');const file=event.target.files?.[0];if(file)void run(()=>upload(file));}}/></label>
      {planCurrent&&plan&&<div><p>范围与完整性已核对，删除覆盖 {plan.overlay_count} 项。{plan.latest_status==='known'?'最新删除历史已取得。':'删除历史无法核对。'}</p>
        {plan.latest_status!=='known'&&<label><input type="checkbox" checked={unknown} onChange={e=>setUnknown(e.target.checked)}/>确认仅按已取得的备份时点核对，不视为最新删除或账</label>}
        <button disabled={busy||!plan.executor_configured||!planConfirmed} onClick={()=>run(verify)}>确认验证这个备份</button>
        <button disabled={busy||!plan.executor_configured||!planConfirmed||restoreJob?.plan_id!==plan.plan_id||restoreJob?.state!=='verified'||context?.current_mode==='restored_readonly'} onClick={()=>run(activate)}>切换为当前只读数据</button></div>}</section>
    <section><h2>操作记录</h2><button onClick={()=>run(refresh)}>只读刷新进度</button>
      <label>原操作编号<input value={lookup} onChange={e=>setLookup(e.target.value)}/></label><button onClick={()=>run(async()=>{const job=await request(`/jobs/by-key/${encodeURIComponent(lookup)}`);setJobs(old=>[...old.filter(j=>j.job_id!==job.job_id),job]);})}>核对原操作</button>
      {jobs.map(job=><article key={job.job_id}><p>{stages[job.stage]??'按原操作核对进度'} · {job.business_key}</p>{job.package_id&&<button onClick={()=>run(()=>downloadPackage(token,job))}>下载已保存文件</button>}{['prepared','running'].includes(job.state)&&<button onClick={()=>run(async()=>{await request(`/jobs/${job.job_id}/cancel`,{});await refresh();})}>取消本次操作</button>}{job.kind==='source_delete'&&['deleted_pending','deletion_unconfirmed'].includes(job.state)&&<button disabled={busy||context?.read_only} onClick={()=>run(async()=>{await request(`/jobs/${job.job_id}/retry-cleanup`,{confirm:true});await refresh();})}>按原清单重试清理</button>}</article>)}</section>
    <section><h2>删除影响</h2><p>删除本条资料及全部版本的回查内容，历史关系和旧备份保留。其他资料共享的原件会保留；清理未确认时不会显示已物理完成。</p>
      {materials.map(material=><p key={material.id}>{material.title} <button disabled={busy||context?.read_only||!caps?.source_delete_available} onClick={()=>run(()=>preview(material))}>核对删除影响</button></p>)}
      {impact&&<div><p>{impact.title}，全部版本 {impact.versions.length} 个，影响活动 {impact.activities.length} 个、记忆依赖 {impact.memories.length} 项。</p><label><input type="checkbox" checked={deleteConfirm} onChange={e=>setDeleteConfirm(e.target.checked)}/>确认删除本条资料及全部版本回查内容，保留历史关系和旧备份</label><button disabled={!deleteConfirm||busy} onClick={()=>run(remove)}>确认删除这条资料</button></div>}</section>
    {context?.read_only&&<ReadonlyRecords token={token}/>}
  </main>;
}
