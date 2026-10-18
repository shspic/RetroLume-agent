import {canonical,dataFetch,dataNamespace} from '../data/context';

export type RetrievalRef={business_key:string;query_sha256:string;space_id:string;result_sha256:string};
export type RetrievalCommand={business_key:string;action:'source_index'|'query';expected_scope_revision:number;expected_domain_revision:number;query:string|null;confirmed:true};
export type RetrievalReceipt={business_key:string;action:string;status:string;current:boolean;terminal_disposition:string|null;error_code:string|null;retrieval_ref?:RetrievalRef};
export type ServiceIdentity={provider:string;model:string};
export type RetrievalStatus={available:boolean;reason:string|null;provider:string|null;model:string|null;ready?:boolean;fragments?:number;cached_fragments?:number;index_batches?:number;domain_revision?:number;purpose:string;reserve_cost_microunits:number;remaining_requests:number;remaining_cost_microunits:number;remaining_running_seconds:number;query_then_model_requests:number;query_then_model_reserve_microunits:number;window_reserve_seconds:number};
// D04：只认可只读配置给出的有限服务身份，不能从服务类型猜模型。
export function serviceIdentityKnown(value:unknown):value is ServiceIdentity{
  if(!value||typeof value!=='object')return false;
  const row=value as Record<string,unknown>;
  return ['provider','model'].every(key=>typeof row[key]==='string'&&/^[A-Za-z0-9._:/-]{1,128}$/.test(row[key] as string));
}
export function retrievalDisclosureKnown(status:RetrievalStatus|null):boolean{
  return Boolean(status?.available&&serviceIdentityKnown(status)&&typeof status.purpose==='string'&&status.purpose.trim().length>0&&status.purpose.length<=300
    &&[status.reserve_cost_microunits,status.window_reserve_seconds,status.query_then_model_reserve_microunits].every(n=>Number.isSafeInteger(n)&&n>0)
    &&status.query_then_model_requests===2&&status.query_then_model_reserve_microunits>=2*status.reserve_cost_microunits
    &&[status.remaining_requests,status.remaining_cost_microunits,status.remaining_running_seconds].every(n=>Number.isFinite(n)&&n>=0));
}
export type RetrievalChain={key:string;namespace:string;activity_id:string;owner:string;domain:'teaching'|'interview'|'index';domain_input:Record<string,unknown>;query:RetrievalCommand;domain_sent:boolean;receipt?:RetrievalReceipt;created_at:string};
const base=(aid:string)=>`/api/activities/${encodeURIComponent(aid)}/retrieval`;
export async function retrievalRequest<T>(token:string,aid:string,suffix:string,body?:unknown,guard=()=>true):Promise<T>{
  if(!guard())throw new Error('页面身份已变化，未提交');
  const response=await dataFetch(base(aid)+suffix,{method:body===undefined?'GET':'POST',headers:{'X-RetroLume-Session':token,...(body===undefined?{}:{'Content-Type':'application/json'})},body:body===undefined?undefined:canonical(body),cache:'no-store'});
  if(!guard())throw new Error('页面身份已变化，保留原意图');
  const value=await response.json();if(!guard())throw new Error('页面身份已变化，保留原意图');
  if(!response.ok)throw new Error(value.detail?.message??'资料检索未完成，请核对原操作');return value;
}
async function database(){return new Promise<IDBDatabase>((resolve,reject)=>{const r=indexedDB.open(`retrolume-teaching:retrieval:${dataNamespace()}`,1);r.onupgradeneeded=()=>r.result.createObjectStore('chains',{keyPath:'key'});r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(new Error('本机意图不可写，未提交'));});}
export async function storeRetrievalChain(row:RetrievalChain){
  if(row.namespace!==dataNamespace())throw new Error('数据已切换，原意图保留');
  const db=await database();try{await new Promise<void>((resolve,reject)=>{const tx=db.transaction('chains','readwrite');tx.objectStore('chains').put(row);tx.oncomplete=()=>resolve();tx.onabort=tx.onerror=()=>reject(new Error('本机意图不可写，未提交'));});}finally{db.close();}
}
export async function retrievalChains(aid:string){const db=await database();try{return await new Promise<RetrievalChain[]>((resolve,reject)=>{const r=db.transaction('chains').objectStore('chains').getAll();r.onsuccess=()=>resolve((r.result as RetrievalChain[]).filter(x=>x.activity_id===aid&&x.namespace===dataNamespace()));r.onerror=()=>reject(new Error('本机检索意图无法读取'));});}finally{db.close();}}
export async function retrieveForCommand(token:string,aid:string,owner:string,domain:RetrievalChain['domain'],input:Record<string,unknown>,scope:number,revision:number,query:string,guard:()=>boolean,recovered?:RetrievalChain,modelService?:ServiceIdentity|null){
  const row:RetrievalChain=recovered??{key:crypto.randomUUID(),namespace:dataNamespace(),activity_id:aid,owner,domain,domain_input:input,query:{business_key:crypto.randomUUID(),action:domain==='index'?'source_index':'query',expected_scope_revision:scope,expected_domain_revision:revision,query:domain==='index'?null:query.trim(),confirmed:true},domain_sent:false,created_at:new Date().toISOString()};
  const live=()=>guard()&&row.namespace===dataNamespace();
  if(!live()||row.owner!==owner||row.domain!==domain||row.domain_sent||row.query.expected_scope_revision!==scope||row.query.expected_domain_revision!==revision)throw new Error('原动作资格已变化，请只读核对');
  await storeRetrievalChain(row);if(!live())throw new Error('页面身份已变化，未提交');
  const preview=await retrievalRequest<RetrievalStatus>(token,aid,'/status',undefined,live);
  if(!retrievalDisclosureKnown(preview)||(domain!=='index'&&!serviceIdentityKnown(modelService)))throw new Error('本步供应商、模型、用途或额度尚不可核对，未发送。');
  if(!recovered){
    const needed=domain==='index'?(preview.index_batches??0):2;
    if(preview.remaining_requests<needed||preview.remaining_cost_microunits<needed*preview.reserve_cost_microunits||preview.remaining_running_seconds<needed*preview.window_reserve_seconds)throw new Error('剩余额度不足以完成本步，查询和后续动作均未发送。');
  }
  const receipt=await retrievalRequest<RetrievalReceipt>(token,aid,recovered?`/commands/${row.query.business_key}`:'/commands',recovered?undefined:row.query,live);
  if(receipt.business_key!==row.query.business_key)throw new Error('检索回执身份不同');row.receipt=receipt;await storeRetrievalChain(row);
  if(!live()||(domain==='index'?!['received','cache_ready'].includes(receipt.terminal_disposition??''):receipt.terminal_disposition!=='received'||!receipt.current||!receipt.retrieval_ref))throw new Error('检索尚无当前合格结果，后续动作未发送；请按原键核对');
  return {row,ref:receipt.retrieval_ref};
}
