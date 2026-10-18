import {dataFetch} from "../data/context";
import type { HtmlAck,HtmlArtifact,HtmlCapabilities,HtmlCommand,HtmlEvent,HtmlPreview,HtmlReceipt } from "./contracts";

export class HtmlApiError extends Error {constructor(readonly code:string,message:string){super(message);}}
export function canonical(value:unknown):string {
  const ordered=(v:unknown):unknown=>Array.isArray(v)?v.map(ordered):v!==null&&typeof v==="object"?
    Object.fromEntries(Object.entries(v).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,x])=>[k,ordered(x)])):v;
  // 协议字段只有固定ASCII键，排序不依赖用户文本或模型键。
  return JSON.stringify(ordered(value));
}
export async function digest(bytes:Uint8Array|string):Promise<string>{
  const data=typeof bytes==="string"?new TextEncoder().encode(bytes):bytes;
  const result=await crypto.subtle.digest("SHA-256",data as BufferSource);
  return Array.from(new Uint8Array(result),b=>b.toString(16).padStart(2,"0")).join("");
}
export function randomKey():string{const bytes=crypto.getRandomValues(new Uint8Array(32));return Array.from(bytes,b=>b.toString(16).padStart(2,"0")).join("");}
export async function request<T>(url:string,token:string,body?:unknown,signal?:AbortSignal,owner?:string):Promise<T>{
  const headers:Record<string,string>={"X-RetroLume-Session":token};if(owner)headers["X-RetroLume-Preview-Owner"]=owner;
  if(body!==undefined)headers["Content-Type"]="application/json";
  const response=await dataFetch(url,{method:body===undefined?"GET":"POST",headers,body:body===undefined?undefined:canonical(body),signal,cache:"no-store"});
  const value=await response.json();if(!response.ok)throw new HtmlApiError(value.code??"html_unavailable",value.message??"交互服务未确认");return value as T;
}
const base=(aid:string)=>`/api/activities/${encodeURIComponent(aid)}/html`;
export const capabilities=(aid:string,token:string,signal?:AbortSignal)=>request<HtmlCapabilities>(base(aid)+"/capabilities",token,undefined,signal);
export const generate=(aid:string,token:string,command:HtmlCommand,signal?:AbortSignal)=>request<HtmlReceipt>(base(aid)+"/commands",token,command,signal);
export const reconcile=(aid:string,token:string,key:string,signal?:AbortSignal)=>request<HtmlReceipt>(base(aid)+"/commands/"+key,token,undefined,signal);
export const artifact=(aid:string,token:string,id:string,signal?:AbortSignal)=>request<HtmlArtifact>(base(aid)+"/artifacts/"+id,token,undefined,signal);
export const history=(aid:string,token:string,signal?:AbortSignal)=>request<{items:{artifact_id:string;artifact_sha256:string;eligible:boolean}[]}>(base(aid)+"/artifacts",token,undefined,signal);
export const openPreview=(aid:string,token:string,item:HtmlArtifact,startKey:string,owner:string,signal?:AbortSignal)=>request<HtmlPreview>(base(aid)+`/artifacts/${item.artifact_id}/previews`,token,
  {start_key:startKey,expected_artifact_sha256:item.artifact_sha256,input_owner_key:owner,confirmed:true},signal);
export const preview=(aid:string,token:string,id:string,signal?:AbortSignal,owner?:string)=>request<HtmlPreview>(base(aid)+"/previews/"+id,token,undefined,signal,owner);
export async function input(aid:string,token:string,item:HtmlPreview,seq:number,event:HtmlEvent,owner:string,signal?:AbortSignal){
  const payload_sha256=await digest(canonical(event));
  return request<HtmlAck>(base(aid)+`/previews/${item.preview_id}/inputs`,token,{preview_generation:item.generation,seq,payload_sha256,event},signal,owner);
}
export const stop=(aid:string,token:string,item:HtmlPreview,reason:"user"|"back_to_learning"="user")=>request<HtmlPreview>(base(aid)+`/previews/${item.preview_id}/stop`,token,
  {generation:item.generation,stop_key:crypto.randomUUID(),reason});
export async function frame(aid:string,token:string,item:HtmlPreview,afterSeq:number,owner:string,signal?:AbortSignal){
  const response=await dataFetch(base(aid)+`/previews/${item.preview_id}/frames?generation=${item.generation}&after_seq=${afterSeq}`,
    {headers:{"X-RetroLume-Session":token,"X-RetroLume-Preview-Owner":owner},signal,cache:"no-store"});
  if(response.status===204)return null;
  if(!response.ok){const error=await response.json();throw new HtmlApiError(error.code??"frame_unavailable",error.message??"画面已失效");}
  const length=Number(response.headers.get("content-length")??0);if(length>524288)throw new Error("画面过大");
  const bytes=new Uint8Array(await response.arrayBuffer());const seq=Number(response.headers.get("x-frame-seq"));
  if(bytes.length>524288||bytes.length<24||response.headers.get("x-preview-id")!==item.preview_id||
    response.headers.get("x-preview-generation")!==String(item.generation)||response.headers.get("x-artifact-sha256")!==item.artifact_sha256||
    !Number.isSafeInteger(seq)||seq<=afterSeq||!bytes.slice(0,8).every((b,i)=>b===[137,80,78,71,13,10,26,10][i])||
    new DataView(bytes.buffer).getUint32(16)!==640||new DataView(bytes.buffer).getUint32(20)!==480||await digest(bytes)!==response.headers.get("x-frame-sha256"))throw new Error("画面身份或编码不匹配");
  return {bytes,seq};
}
