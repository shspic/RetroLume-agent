import {dataStorageKey} from "../data/context";
import {teachingEditorOwner} from "./teachingIntents";
import {canonicalInterview,interviewSha,requestText} from "./interviewDrafts";
import type {InterviewCommand,InterviewReceipt} from "./interviewApi";

export const interviewEditorOwner=teachingEditorOwner;
const KEY = () => dataStorageKey("retrolume.interview.intents.v1"), DB = () => dataStorageKey("retrolume-interview-drafts"), STORE="drafts";
export type InterviewIntent={key:string;activity_id:string;action:string;hash:string;owner:string;head_revision:number;goal_version:number;scope_revision:number;state:string};
export type InterviewDraft={key:string;activity_id:string;owner:string;hash:string;command:InterviewCommand};
function summaries():InterviewIntent[]{
  const raw=localStorage.getItem(KEY());if(!raw)return [];
  if(new TextEncoder().encode(raw).length>32768)throw new Error("本机意图台账超过上限");
  const rows=JSON.parse(raw);
  if(!Array.isArray(rows)||rows.length>16||rows.some(x=>!x||typeof x.key!=="string"||typeof x.owner!=="string"||typeof x.hash!=="string"||typeof x.activity_id!=="string"))throw new Error("本机意图台账无法核对");
  return rows;
}
export function loadInterviewIntents():{ok:boolean;items:InterviewIntent[]}{try{return {ok:true,items:summaries()};}catch{return {ok:false,items:[]};}}
async function database():Promise<IDBDatabase>{
  return await new Promise((resolve,reject)=>{const r=indexedDB.open(DB(),1);r.onupgradeneeded=()=>r.result.createObjectStore(STORE,{keyPath:"key"});r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(new Error("本机正文库无法打开"));r.onblocked=()=>reject(new Error("本机正文库被阻止"));});
}
export async function readInterviewDraft(key:string):Promise<InterviewDraft|null>{
  const db=await database();try{return await new Promise((resolve,reject)=>{const tx=db.transaction(STORE,"readonly");let value:InterviewDraft|null=null;const r=tx.objectStore(STORE).get(key);r.onsuccess=()=>value=(r.result??null) as InterviewDraft|null;tx.oncomplete=()=>resolve(value);tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);});}finally{db.close();}
}
async function writeDraft(draft:InterviewDraft):Promise<void>{
  const db=await database();try{await new Promise<void>((resolve,reject)=>{const tx=db.transaction(STORE,"readwrite"),store=tx.objectStore(STORE);const get=store.getAll();get.onsuccess=()=>{
    const rows=(get.result as InterviewDraft[]).filter(d=>d.key!==draft.key);rows.push(draft);
    if(rows.length>16||new TextEncoder().encode(canonicalInterview(rows)).length>262144){tx.abort();return;}
    store.put(draft);
  };tx.oncomplete=()=>resolve();tx.onerror=()=>reject(new Error("本机正文保存失败"));tx.onabort=()=>reject(new Error("本机正文保存失败或已达上限"));});}finally{db.close();}
}
export async function saveInterviewIntent(draft:InterviewDraft,stillCurrent:()=>boolean):Promise<void>{
  if(!navigator.locks||!stillCurrent())throw new Error("无法取得本机意图锁或编辑身份已变化");
  await navigator.locks.request(`${KEY()}:drafts`,async()=>{
    if(!stillCurrent()||await interviewEditorOwner()!==draft.owner||!stillCurrent())throw new Error("编辑身份已变化");
    const computed=await interviewSha(requestText(draft.activity_id,draft.command));
    if(!stillCurrent()||computed!==draft.hash)throw new Error("正文身份已变化");
    await writeDraft(draft);
    if(!stillCurrent()||await interviewEditorOwner()!==draft.owner||!stillCurrent())throw new Error("正文已保存，编辑身份变化；未发送");
    await navigator.locks.request(KEY(),async()=>{
      if(!stillCurrent())throw new Error("面板已变化，未发送");
      const rows=summaries().filter(x=>x.key!==draft.key);
      if(rows.length>=16)throw new Error("本机待核对意图已达16条，请先核对原提交");
      rows.push({key:draft.key,activity_id:draft.activity_id,action:draft.command.action,hash:draft.hash,owner:draft.owner,head_revision:draft.command.expected_head_revision,
        goal_version:draft.command.expected_goal_version,scope_revision:draft.command.expected_scope_revision,state:"saved_not_confirmed"});
      const raw=canonicalInterview(rows);if(new TextEncoder().encode(raw).length>32768)throw new Error("本机摘要已达上限");
      localStorage.setItem(KEY(),raw);
    });
    if(!stillCurrent())throw new Error("本机保存成功，但发送身份已变化；未发送");
  });
}
export async function noteInterviewReceipt(receipt:InterviewReceipt,owner:string,stillCurrent:()=>boolean=()=>true):Promise<void>{
  if(!navigator.locks)throw new Error("本机锁不可用");
  await navigator.locks.request(KEY(),async()=>{
    if(!stillCurrent())throw new Error("原意图身份已变化");
    const now=await interviewEditorOwner();if(!stillCurrent()||now!==owner)throw new Error("编辑身份已变化");
    const rows=summaries();const item=rows.find(x=>x.key===receipt.business_key&&x.activity_id===receipt.activity_id&&x.owner===owner&&x.hash===receipt.request_sha256);
    if(!item||item.action!==receipt.action||!stillCurrent())throw new Error("原意图身份无法核对");
    item.state=receipt.status;localStorage.setItem(KEY(),canonicalInterview(rows));
  });
}
