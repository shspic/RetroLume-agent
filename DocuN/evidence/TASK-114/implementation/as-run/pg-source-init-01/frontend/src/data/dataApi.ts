import {dataFetch,getDataContext,canonical} from './context';
export type Job={job_id:string;business_key:string;kind:string;state:string;stage:string;revision:number;package_id?:string;plan_id?:string;target_id?:string;selection_generation?:number;counts?:{bytes?:string;files?:number;rows?:number}};
export type Plan={plan_id:string;plan_sha256:string;package_root_sha256:string;deletion_policy:string;latest_status:string;overlay_count:number;executor_configured:boolean;permanent_readonly:boolean};
export async function dataRequest(token:string,path:string,body?:unknown):Promise<any>{
  const response=await dataFetch('/api/data'+path,{method:body===undefined?'GET':'POST',headers:{'X-RetroLume-Session':token,...(body===undefined?{}:{'Content-Type':'application/json'})},body:body===undefined?undefined:canonical(body),cache:'no-store'});
  const value=await response.json();if(!response.ok)throw new Error(typeof value.detail==='string'?value.detail:'操作未完成，请核对原操作编号。');return value;
}
const intentKey=()=>`retrolume.data-jobs.v1:${getDataContext()?.control_id??'unconfigured'}`;
export function rememberJob(key:string){const values=jobKeys();if(!values.includes(key))localStorage.setItem(intentKey(),JSON.stringify([...values,key].slice(-256)));}
export function jobKeys():string[]{try{const value=JSON.parse(localStorage.getItem(intentKey())??'[]');return Array.isArray(value)?value.filter(v=>typeof v==='string'):[];}catch{return [];}}
export async function downloadPackage(token:string,job:Job){
  if(Number(job.counts?.bytes??0)>=128*1024*1024)throw new Error('此备份较大，已保存在配置的本机备份目录，请用本机文件管理器取出。');
  const response=await dataFetch(`/api/data/packages/${job.package_id}/content`,{headers:{'X-RetroLume-Session':token},cache:'no-store'});
  if(!response.ok)throw new Error('备份文件尚不可下载，请核对保存收据。');
  downloadBlob(await response.blob(),`${job.package_id}.rldata`);
}
export function downloadBlob(blob:Blob,filename:string){const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);}
export async function exportDrafts(){
  const local:Record<string,unknown>={};
  for(let i=0;i<localStorage.length;i++){const key=localStorage.key(i);if(key&&/^retrolume\.(pending-intents|teaching-intents|interview\.intents|memory-intents|html11\.intents)/.test(key))local[key]=JSON.parse(localStorage.getItem(key)??'null');}
  const indexed:Record<string,unknown[]>={};
  const names=(await indexedDB.databases()).map(v=>v.name).filter((v):v is string=>!!v&&/^retrolume-(teaching|interview-drafts|memory)(:|$)/.test(v));
  for(const name of names){
    const db=await new Promise<IDBDatabase>((resolve,reject)=>{const request=indexedDB.open(name);request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(new Error('本机草稿无法读取'));});
    try{for(const store of Array.from(db.objectStoreNames))indexed[`${name}/${store}`]=await new Promise<unknown[]>((resolve,reject)=>{const request=db.transaction(store).objectStore(store).getAll();request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(new Error('本机草稿无法读取'));});}finally{db.close();}
  }
  downloadBlob(new Blob([JSON.stringify({format:'retrolume.unsubmitted-drafts.v1',submitted:false,restores_execution_authority:false,local,indexed},null,2)],{type:'application/json'}),'retrolume-unsubmitted-drafts.json');
}
