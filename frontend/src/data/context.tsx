import React, {useEffect, useRef, useSyncExternalStore} from "react";

export type DataContext = {control_id:string; selection_generation:number; dataset_id:string; instance_id:string; current_mode:string; read_only:boolean};
let current: DataContext|null = null;
const listeners = new Set<()=>void>();
function sameIdentity(a:DataContext,b:DataContext){return a.control_id===b.control_id&&a.selection_generation===b.selection_generation&&a.dataset_id===b.dataset_id&&a.instance_id===b.instance_id;}
function validContext(value:DataContext){return typeof value.control_id==='string'&&typeof value.dataset_id==='string'&&typeof value.instance_id==='string'&&Number.isSafeInteger(value.selection_generation)&&value.selection_generation>=0&&typeof value.read_only==='boolean';}
function canAdvance(value:DataContext,sessionBootstrap=false){
  if(!validContext(value))return false;
  if(!current)return sessionBootstrap;
  if(value.control_id!==current.control_id)return sessionBootstrap;
  if(value.selection_generation<current.selection_generation)return false;
  if(value.selection_generation===current.selection_generation){
    if(!sameIdentity(value,current)||current.read_only&&!value.read_only)return false;
  }
  return true;
}
export function setDataContext(value:DataContext|null,options:{sessionBootstrap?:boolean}={}) {
  if(value?!canAdvance(value,options.sessionBootstrap):current!==null&&!options.sessionBootstrap)return false;
  if(value&&current&&canonical(value)===canonical(current))return true;
  current=value?{control_id:value.control_id,selection_generation:value.selection_generation,dataset_id:value.dataset_id,
    instance_id:value.instance_id,current_mode:value.current_mode,read_only:value.read_only}:null;
  listeners.forEach(fn=>fn());
  return true;
}
export function getDataContext(){return current;}
export function dataNamespace(){return current ? `${current.dataset_id}.${current.instance_id}.${current.selection_generation}` : "legacy";}
export function dataStorageKey(base:string){return current ? `${base}:${dataNamespace()}` : base;}
export function canonical(value:unknown):string {
  if(value===null||typeof value!=="object") return JSON.stringify(value);
  if(Array.isArray(value))return `[${value.map(canonical).join(",")}]`;
  const object=value as Record<string,unknown>;
  return `{${Object.keys(object).sort().map(key=>`${JSON.stringify(key)}:${canonical(object[key])}`).join(",")}}`;
}
export function useDataContext(){return useSyncExternalStore(fn=>{listeners.add(fn);return()=>{listeners.delete(fn);};},getDataContext);}
export async function dataFetch(path:RequestInfo|URL,init:RequestInit={},policy:{capabilityRefresh?:boolean}={}) {
  const capture=dataNamespace(),context=current,method=(init.method??'GET').toUpperCase();
  const pathname=new URL(String(path),window.location.origin).pathname;
  const hubRead=['GET','HEAD'].includes(method)&&/^\/api\/data\/(jobs(?:\/|$)|packages(?:\/|$)|restore-plans\/)/.test(pathname);
  const hubCancel=method==='POST'&&/^\/api\/data\/jobs\/[^/]+\/cancel$/.test(pathname);
  const artifactWork=method==='POST'&&(/^\/api\/data\/(jobs|uploads|restore-plans|restore-jobs)$/.test(pathname)||/^\/api\/data\/restore-jobs\/[^/]+\/activate-readonly$/.test(pathname));
  const bootstrap=policy.capabilityRefresh&&method==='GET'&&pathname==='/api/data/capabilities';
  if(context?.read_only&&!hubRead&&!hubCancel&&!artifactWork&&!['GET','HEAD'].includes(method))throw new Error("当前数据仅供只读查看，不能修改或继续调用。");
  const headers=new Headers(init.headers);
  if(context)headers.set('X-RetroLume-Data-Context',canonical(context));
  const response=await fetch(path,{...init,headers});
  const check=()=>{
    if(init.signal?.aborted)throw new DOMException('Aborted','AbortError');
    if(current?.control_id!==context?.control_id||!(hubRead||hubCancel||bootstrap)&&(capture!==dataNamespace()||canonical(current)!==canonical(context)))throw new Error("当前数据已切换，旧响应未用于当前页面。");
    const observed=response.headers.get('X-RetroLume-Data-Context');
    if(context&&observed){
      let identity:DataContext;try{identity=JSON.parse(observed);}catch{throw new Error('数据身份无法核对。');}
      if(hubRead||hubCancel){if(identity.control_id!==context.control_id)throw new Error('控制身份已改变。');}
      else if(bootstrap){if(!canAdvance(identity))throw new Error('能力响应已过期，请重新刷新。');}
      else if(observed!==canonical(context))throw new Error("数据身份已改变，请刷新后核对。");
    }
  };
  check();
  const json=response.json.bind(response),blob=response.blob.bind(response),arrayBuffer=response.arrayBuffer.bind(response);
  response.json=async()=>{const value=await json();check();if(bootstrap&&value.dataset_id&&!canAdvance(value))throw new Error('能力响应已过期，请重新刷新。');return value;};
  response.blob=async()=>{const value=await blob();check();return value;};
  response.arrayBuffer=async()=>{const value=await arrayBuffer();check();return value;};
  return response;
}

export function ReadOnlyBusiness({children}:{children:React.ReactNode}) {
  const context=useDataContext(),root=useRef<HTMLDivElement>(null);
  useEffect(()=>{
    if(!context?.read_only||!root.current)return;
    const apply=()=>{
      root.current?.querySelectorAll<HTMLButtonElement>('button').forEach(button=>{
        if(!/刷新|核对|查看|历史|回查|展开|收起|上一页|下一页|返回|关闭|下载|导出|取消选择/.test(button.textContent??''))button.disabled=true;
      });
      root.current?.querySelectorAll<HTMLInputElement|HTMLTextAreaElement>('input,textarea').forEach(input=>{
        if(input.closest('.line-picker'))return;
        if(input instanceof HTMLTextAreaElement||['text','number','search'].includes(input.type))input.readOnly=true;
        else input.disabled=true;
      });
    };
    apply();const observer=new MutationObserver(apply);observer.observe(root.current,{childList:true,subtree:true});
    return()=>observer.disconnect();
  },[context?.read_only,context?.instance_id]);
  return <div ref={root}>{context?.read_only&&<p role="status" className="data-readonly">当前读取恢复副本或维护中的记录。仅恢复记录与只读查看，未恢复继续学习或调用的执行资格；原数据保留，持续使用需后续验收。历史额度是备份时点记录，未知预留保留。</p>}{children}</div>;
}
