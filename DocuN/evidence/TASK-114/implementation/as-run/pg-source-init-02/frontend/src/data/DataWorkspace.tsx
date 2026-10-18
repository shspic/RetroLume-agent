import React,{useEffect,useState} from 'react';
import {dataRequest,downloadPackage,exportDrafts,jobKeys,rememberJob,type Job,type Plan} from './dataApi';
import {dataFetch,useDataContext,setDataContext} from './context';
import './data.css';
import {fileHash} from './fileHash';
import {ReadonlyRecords} from './ReadonlyRecords';
type Material={id:string;title:string;revision:number};
const stages:Record<string,string>={prepared:'准备中',reading:'读取已保存记录',copying:'复制原件',verifying:'核对完整性',published:'已保存',published_unconfirmed:'文件已保存，收据待核对',allocating:'建立隔离验证副本',verified:'副本已验证，当前应用仍使用原数据',active_readonly:'当前读取恢复副本',selector_committed:'已选择只读副本',failed:'本次未完成，已有数据和旧备份保留',cancelled:'已请求取消',deleted:'本条资料回查内容已删除',cleanup_pending:'墓碑已生效，原件清理待确认',deletion_unconfirmed:'删除结果待核对'};
export function DataWorkspace({token,onSelection}:{token:string;onSelection:()=>Promise<void>}){
  const context=useDataContext(),[caps,setCaps]=useState<any>(null),[jobs,setJobs]=useState<Job[]>([]),[materials,setMaterials]=useState<Material[]>([]);
  const [error,setError]=useState(''),[busy,setBusy]=useState(false),[selected,setSelected]=useState<string[]>([]),[mode,setMode]=useState('all');
  const [plan,setPlan]=useState<Plan|null>(null),[policy,setPolicy]=useState('respect_current_deletions'),[confirmSnapshot,setConfirmSnapshot]=useState(false),[unknown,setUnknown]=useState(false);
  const [restoreJob,setRestoreJob]=useState<Job|null>(null),[lookup,setLookup]=useState(''),[impact,setImpact]=useState<any>(null),[deleteConfirm,setDeleteConfirm]=useState(false);
  const [scopePreview,setScopePreview]=useState<any>(null),[activities,setActivities]=useState<any[]>([]),[selectedActivities,setSelectedActivities]=useState<string[]>([]);
  async function run(work:()=>Promise<void>){setBusy(true);setError('');try{await work();}catch(reason){setError(reason instanceof Error?reason.message:'本次操作未完成');}finally{setBusy(false);}}
  async function refresh(){
    const value=await dataRequest(token,'/capabilities');setCaps(value);
    if(value.dataset_id)setDataContext(value);
    const list:Job[]=[];for(const key of jobKeys()){try{list.push(await dataRequest(token,`/jobs/by-key/${encodeURIComponent(key)}`));}catch{}}
    setJobs(list);
    const restored=list.filter(j=>j.kind==='restore').at(-1);
    if(restored?.plan_id){setRestoreJob(restored);setPlan(await dataRequest(token,`/restore-plans/${restored.plan_id}`));}
    if(value.current_mode!=='unavailable'){const response=await dataFetch('/api/materials',{headers:{'X-RetroLume-Session':token}});if(response.ok)setMaterials((await response.json()).items);}
    if(value.current_mode!=='unavailable'){const response=await dataFetch('/api/activities?limit=20',{headers:{'X-RetroLume-Session':token}});if(response.ok)setActivities((await response.json()).items??[]);}
  }
  useEffect(()=>{let alive=true;void refresh().catch(reason=>{if(alive)setError(reason.message);});return()=>{alive=false;};},[token,context?.instance_id]);
  async function create(kind:string){
    const key=crypto.randomUUID();rememberJob(key);
    const receipt=await dataRequest(token,'/jobs',{kind,business_key:key,scope:{mode,...(mode==='selected'?{source_ids:selected,activity_ids:selectedActivities,expected_closure_sha256:scopePreview.closure_sha256}:{})},confirm:true});
    setJobs(old=>[...old.filter(j=>j.job_id!==receipt.job_id),receipt]);
  }
  async function upload(file:File){
    const key=crypto.randomUUID(),id=crypto.randomUUID();rememberJob(key);
    const query=new URLSearchParams({business_key:key,upload_id:id,expected_sha256:await fileHash(file),expected_bytes:String(file.size)});
    const response=await dataFetch('/api/data/uploads?'+query,{method:'POST',headers:{'X-RetroLume-Session':token},body:file});
    const value=await response.json();if(!response.ok)throw new Error(value.detail??'备份未接收');
    setPlan(await dataRequest(token,'/restore-plans',{upload_id:value.upload_id,deletion_policy:policy}));setRestoreJob(null);
  }
  async function verify(){if(!plan)return;const key=crypto.randomUUID();rememberJob(key);const value=await dataRequest(token,'/restore-jobs',{plan_id:plan.plan_id,expected_plan_sha256:plan.plan_sha256,business_key:key,confirm:true,acknowledge_unknown_deletions:unknown});setRestoreJob(value);setJobs(old=>[...old,value]);}
  async function activate(){if(!plan||!restoreJob)return;const key=crypto.randomUUID();rememberJob(key);await dataRequest(token,`/restore-jobs/${restoreJob.job_id}/activate-readonly`,{expected_plan_sha256:plan.plan_sha256,business_key:key,expected_selection_generation:context?.selection_generation??0,confirm:true});await onSelection();}
  async function preview(material:Material){setImpact(await dataRequest(token,`/materials/${material.id}/deletion-preview`,{expected_revision:material.revision}));setDeleteConfirm(false);}
  async function remove(){if(!impact)return;const key=crypto.randomUUID();rememberJob(key);const value=await dataRequest(token,`/materials/${impact.source_id}/deletions`,{expected_revision:impact.expected_revision,impact_sha256:impact.impact_sha256,business_key:key,confirm:true});setJobs(old=>[...old,value]);setImpact(null);await onSelection();}
  return <main className="data-workspace"><h1>数据与备份</h1><p>导出可独立阅读的已保存内容，保存一致备份，并在隔离副本中核对。浏览器未提交草稿不在服务器备份。</p>
    {error&&<p role="alert">{error}</p>}{caps?.current_mode==='unavailable'&&<p>数据与备份尚未配置；本机已有资料不会自动迁移。</p>}
    {context?.read_only&&<p role="status">当前仅供只读查看，旧调用、工具和预览的执行资格未恢复。原数据保留，持续使用需后续验收。</p>}
    <section><h2>导出与保存</h2><label>范围<select value={mode} onChange={event=>{setMode(event.target.value);setScopePreview(null);}}><option value="all">全部已保存内容</option><option value="selected">选择资料及活动</option></select></label>
      {mode==='selected'&&materials.map(material=><label key={material.id}><input type="checkbox" checked={selected.includes(material.id)} onChange={event=>{setSelected(old=>event.target.checked?[...old,material.id]:old.filter(id=>id!==material.id));setScopePreview(null);}}/>{material.title}</label>)}
      {mode==='selected'&&activities.map(activity=><label key={activity.activity_id??activity.id}><input type="checkbox" checked={selectedActivities.includes(activity.activity_id??activity.id)} onChange={event=>{const id=activity.activity_id??activity.id;setSelectedActivities(old=>event.target.checked?[...old,id]:old.filter(value=>value!==id));setScopePreview(null);}}/>活动 {activity.activity_id??activity.id}</label>)}
      {mode==='selected'&&<button disabled={busy||!selected.length&&!selectedActivities.length} onClick={()=>run(async()=>setScopePreview(await dataRequest(token,'/scope-preview',{scope:{mode,source_ids:selected,activity_ids:selectedActivities}})))}>核对自动加入的证据依赖</button>}
      {scopePreview&&<p>将保存 {scopePreview.materials.map((m:any)=>m.title).join('、')}，共 {scopePreview.activity_count} 个活动。核对后范围若改变，本次导出会停止。</p>}
      <p>导出会加入所需的历史版本和证据关系。已撤销记忆正文排除；在途调用和未知预留如实保留，不能获得新的可消费额度。</p>
      <button disabled={busy||!caps?.backup_available||mode==='selected'&&!scopePreview} onClick={()=>run(()=>create('portable_export'))}>导出这些已保存内容</button>
      <button disabled={busy||!caps?.backup_available||mode!=='all'} onClick={()=>run(()=>create('restore_checkpoint'))}>保存当前时点的恢复备份</button>
      <button onClick={()=>run(exportDrafts)}>单独下载未提交浏览器草稿</button></section>
    <section><h2>核对与恢复备份</h2><label>删除处理<select value={policy} onChange={event=>{setPolicy(event.target.value);setPlan(null);}}><option value="respect_current_deletions">尊重当前已删除内容</option><option value="snapshot_only_readonly">按备份时点只读查看</option></select></label>
      {policy==='snapshot_only_readonly'&&<label><input type="checkbox" checked={confirmSnapshot} onChange={e=>setConfirmSnapshot(e.target.checked)}/>确认旧备份可能重新显示已删除内容，仅限隔离只读副本；源墓碑保留</label>}
      <label>选择备份文件<input type="file" accept=".rldata" disabled={busy||!caps?.restore_executor_configured||policy==='snapshot_only_readonly'&&!confirmSnapshot} onChange={event=>{const file=event.target.files?.[0];if(file)void run(()=>upload(file));}}/></label>
      {plan&&<div><p>范围与完整性已核对，删除覆盖 {plan.overlay_count} 项。{plan.latest_status==='known'?'最新删除历史已取得。':'删除历史无法核对。'}</p>
        {plan.latest_status!=='known'&&<label><input type="checkbox" checked={unknown} onChange={e=>setUnknown(e.target.checked)}/>确认仅按已取得的备份时点核对，不视为最新删除或账</label>}
        <button disabled={busy||!plan.executor_configured||plan.latest_status!=='known'&&!unknown} onClick={()=>run(verify)}>确认验证这个备份</button>
        <button disabled={busy||restoreJob?.state!=='verified'||context?.current_mode==='restored_readonly'} onClick={()=>run(activate)}>切换为当前只读数据</button></div>}</section>
    <section><h2>操作记录</h2><button onClick={()=>run(async()=>{await refresh();if(restoreJob)setRestoreJob(await dataRequest(token,`/jobs/${restoreJob.job_id}`));})}>只读刷新进度</button>
      <label>原操作编号<input value={lookup} onChange={e=>setLookup(e.target.value)}/></label><button onClick={()=>run(async()=>{const job=await dataRequest(token,`/jobs/by-key/${encodeURIComponent(lookup)}`);setJobs(old=>[...old.filter(j=>j.job_id!==job.job_id),job]);})}>核对原操作</button>
      {jobs.map(job=><article key={job.job_id}><p>{stages[job.stage]??'按原操作核对进度'} · {job.business_key}</p>{job.package_id&&<button onClick={()=>run(()=>downloadPackage(token,job))}>下载已保存文件</button>}{['prepared','running'].includes(job.state)&&<button onClick={()=>run(async()=>{await dataRequest(token,`/jobs/${job.job_id}/cancel`,{});await refresh();})}>取消本次操作</button>}{job.kind==='source_delete'&&['deleted_pending','deletion_unconfirmed'].includes(job.state)&&<button disabled={busy||context?.read_only} onClick={()=>run(async()=>{await dataRequest(token,`/jobs/${job.job_id}/retry-cleanup`,{confirm:true});await refresh();})}>按原清单重试清理</button>}</article>)}</section>
    <section><h2>删除影响</h2><p>删除本条资料及全部版本的回查内容，历史关系和旧备份保留。其他资料共享的原件会保留；清理未确认时不会显示已物理完成。</p>
      {materials.map(material=><p key={material.id}>{material.title} <button disabled={busy||context?.read_only||!caps?.source_delete_available} onClick={()=>run(()=>preview(material))}>核对删除影响</button></p>)}
      {impact&&<div><p>{impact.title}，全部版本 {impact.versions.length} 个，影响活动 {impact.activities.length} 个、记忆依赖 {impact.memories.length} 项。</p><label><input type="checkbox" checked={deleteConfirm} onChange={e=>setDeleteConfirm(e.target.checked)}/>确认删除本条资料及全部版本回查内容，保留历史关系和旧备份</label><button disabled={!deleteConfirm||busy} onClick={()=>run(remove)}>确认删除这条资料</button></div>}</section>
    {context?.read_only&&<ReadonlyRecords token={token}/>}
  </main>;
}
