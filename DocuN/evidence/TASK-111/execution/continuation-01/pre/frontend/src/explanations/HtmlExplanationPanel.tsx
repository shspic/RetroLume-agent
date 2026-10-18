import {useEffect,useRef,useState} from "react";
import type {HtmlAck,HtmlArtifact,HtmlCapabilities,HtmlEvent,HtmlParent,HtmlPreview,HtmlReceipt} from "./contracts";
import * as api from "./htmlApi";
import {readIntents,resolveIntent,saveIntent,type HtmlIntent} from "./htmlIntents";
import {PreviewCanvas} from "./PreviewCanvas";

const TERMINAL=new Set(["stopped","failed_unstarted","cleanup_unconfirmed"]);
function decimal(value:string){
  if(!/^[+-]?(?:[0-9]+)(?:\.[0-9]+)?$/.test(value))throw new Error("请输入有限十进制数值");
  const negative=value.startsWith("-"),unsigned=value.replace(/^[+-]/,"");let [whole,fraction=""]=unsigned.split(".");
  whole=whole.replace(/^0+(?=\d)/,"");fraction=fraction.replace(/0+$/,"");
  const normalized=whole+(fraction?"."+fraction:"");return (negative&&normalized!=="0"?"-":"")+normalized;
}
export function HtmlExplanationPanel({activityId,parent,token,onClose}:{activityId:string;parent:HtmlParent;token:string;onClose:()=>void}){
  const [caps,setCaps]=useState<HtmlCapabilities|null>(null),[focus,setFocus]=useState(""),[confirmed,setConfirmed]=useState(false);
  const [receipt,setReceipt]=useState<HtmlReceipt|null>(null),[item,setItem]=useState<HtmlArtifact|null>(null),[running,setRunning]=useState<HtmlPreview|null>(null);
  const [picture,setPicture]=useState<Uint8Array|null>(null),[ack,setAck]=useState<HtmlAck|null>(null),[values,setValues]=useState<Record<string,string>>({});
  const [pending,setPending]=useState<HtmlIntent[]>([]),[saved,setSaved]=useState<{artifact_id:string;eligible:boolean}[]>([]);
  const [busy,setBusy]=useState(false),[error,setError]=useState(""),[notice,setNotice]=useState(""),[citation,setCitation]=useState<unknown>(null);
  const [pollEpoch,setPollEpoch]=useState(0);
  const generation=useRef(0),owner=useRef<string|null>(null),current=useRef<HtmlPreview|null>(null),seq=useRef(0),frameSeq=useRef(0),control=useRef<AbortController|null>(null);
  const artifactVersion=useRef(0),citationVersion=useRef(0);
  const parentKey=api.canonical(parent);
  useEffect(()=>{
    const version=++generation.current;control.current?.abort();const abort=new AbortController();control.current=abort;
    owner.current=null;seq.current=0;frameSeq.current=0;current.current=null;
    artifactVersion.current++;citationVersion.current++;setCaps(null);setSaved([]);setPending([]);setValues({});setNotice("");
    setReceipt(null);setItem(null);setRunning(null);setPicture(null);setAck(null);setCitation(null);setError("");setBusy(false);
    try{setPending(readIntents().filter(x=>x.activity_id===activityId));}catch(reason){setError(String(reason));}
    void api.capabilities(activityId,token,abort.signal).then(data=>{if(version===generation.current&&!abort.signal.aborted)setCaps(data);}).catch(reason=>{if(version===generation.current&&!abort.signal.aborted)setError(String(reason));});
    void api.history(activityId,token,abort.signal).then(data=>{if(version===generation.current&&!abort.signal.aborted)setSaved(data.items);}).catch(()=>{});
    const visibility=()=>{if(document.hidden){generation.current++;citationVersion.current++;abort.abort();control.current=new AbortController();setPicture(null);setAck(null);setCitation(null);owner.current=null;setBusy(false);setPollEpoch(old=>old+1);
      setRunning(old=>old&&!TERMINAL.has(old.state)?{...old,state:"stopping"}:old);
      const live=current.current;if(live&&!TERMINAL.has(live.state))void api.stop(activityId,token,live).catch(()=>{});}};
    document.addEventListener("visibilitychange",visibility);
    return()=>{generation.current++;abort.abort();document.removeEventListener("visibilitychange",visibility);owner.current=null;
      const live=current.current;if(live&&!TERMINAL.has(live.state))void api.stop(activityId,token,live,"back_to_learning").catch(()=>{});current.current=null;};
  },[activityId,parentKey,token]);

  useEffect(()=>{
    if(!running||TERMINAL.has(running.state))return;
    const active=running,version=generation.current,abort=new AbortController();let closed=false;
    async function observe(){
      try{
        const status=await api.preview(activityId,token,active.preview_id,abort.signal,owner.current??undefined);
        if(closed||version!==generation.current||status.preview_id!==active.preview_id||status.generation!==active.generation||status.owner_id!==active.owner_id||status.artifact_sha256!==active.artifact_sha256)return;
        current.current=status;setRunning(status);
        if(!status.eligible||TERMINAL.has(status.state)){
          setPicture(null);setAck(null);owner.current=null;
          if(!status.eligible){artifactVersion.current++;citationVersion.current++;setItem(null);setCitation(null);}
          return;
        }
        if(["ready","running"].includes(status.state)&&owner.current){
          const packet=await api.frame(activityId,token,status,frameSeq.current,owner.current,abort.signal);
          if(closed||version!==generation.current||current.current?.preview_id!==active.preview_id||current.current?.generation!==active.generation)return;
          if(packet){frameSeq.current=packet.seq;setPicture(packet.bytes);}
        }
      }catch(reason){if(!closed&&version===generation.current&&!abort.signal.aborted){
        setError(String(reason));setPicture(null);setAck(null);setItem(null);setCitation(null);artifactVersion.current++;citationVersion.current++;
        owner.current=null;void api.stop(activityId,token,active).catch(()=>{});
      }}
      if(!closed)timer=window.setTimeout(()=>void observe(),300);
    }
    let timer=window.setTimeout(()=>void observe(),0);
    return()=>{closed=true;abort.abort();window.clearTimeout(timer);};
  },[running?.preview_id,running?.generation,running?.state,activityId,token,pollEpoch]);

  async function loadArtifact(id:string,version:number){
    const selection=++artifactVersion.current;citationVersion.current++;setItem(null);setCitation(null);setPicture(null);setAck(null);setBusy(true);
    try{
      const value=await api.artifact(activityId,token,id,control.current?.signal);
      if(version!==generation.current||selection!==artifactVersion.current||value.artifact_id!==id)return;
      setItem(value);setValues(Object.fromEntries(value.description.inputs.map(input=>[input.id,input.default])));
    }catch(reason){if(version===generation.current&&selection===artifactVersion.current)setError(String(reason));}
    finally{if(version===generation.current&&selection===artifactVersion.current)setBusy(false);}
  }
  async function generate(){
    if(!caps?.available||!caps.config_sha256||!confirmed||busy)return;const version=generation.current;
    const command={business_key:crypto.randomUUID(),parent,focus:focus.trim(),expected_config_sha256:caps.config_sha256,confirmed:true as const};
    try{saveIntent(activityId,command);setPending(readIntents().filter(x=>x.activity_id===activityId));}
    catch(reason){setError(String(reason));return;}
    setBusy(true);setError("");
    try{
      const response=await api.generate(activityId,token,command,control.current?.signal);
      if(version!==generation.current)return;
      if(api.canonical(response.accepted_input)!==api.canonical(command))throw new Error("生成意图与原键不一致");
      setReceipt(response);
      if(response.status==="terminal"){resolveIntent(activityId,command.business_key);setPending(readIntents().filter(x=>x.activity_id===activityId));}
      if(response.artifact_id&&response.read_status==="current"){await loadArtifact(response.artifact_id,version);setNotice("已保存，尚未打开预览");}
      else setNotice("生成未形成可用产物，已保留原学习成果与调用事实");
    }catch(reason){if(version===generation.current)setError(String(reason));}
    finally{if(version===generation.current)setBusy(false);}
  }
  async function reconcile(intent:HtmlIntent){
    const version=generation.current;setError("");
    try{const value=await api.reconcile(activityId,token,intent.command.business_key,control.current?.signal);
      if(version!==generation.current)return;if(api.canonical(value.accepted_input)!==api.canonical(intent.command))throw new Error("原键绑定不同输入，保持只读");
      setReceipt(value);if(value.status==="terminal"){resolveIntent(activityId,value.business_key);setPending(readIntents().filter(x=>x.activity_id===activityId));}
      if(value.artifact_id&&value.read_status==="current")await loadArtifact(value.artifact_id,version);
    }catch(reason){if(version===generation.current)setError(String(reason));}
  }
  async function open(){
    if(!item||busy||running&&!TERMINAL.has(running.state))return;const version=generation.current;const key=api.randomKey();setBusy(true);setError("");
    try{const value=await api.openPreview(activityId,token,item,crypto.randomUUID(),key,control.current?.signal);
      if(version!==generation.current){void api.stop(activityId,token,value).catch(()=>{});return;}
      owner.current=key;current.current=value;seq.current=0;frameSeq.current=0;setRunning(value);setPicture(null);setAck(null);
    }catch(reason){if(version===generation.current)setError(String(reason));}
    finally{if(version===generation.current)setBusy(false);}
  }
  async function send(event:HtmlEvent){
    const live=current.current,key=owner.current;if(!live||!key||busy||!item)return;const version=generation.current;setBusy(true);setError("");
    const next=seq.current+1;
    try{const value=await api.input(activityId,token,live,next,event,key,control.current?.signal);
      if(version!==generation.current||current.current?.preview_id!==live.preview_id||current.current?.generation!==live.generation||owner.current!==key||
        value.preview_id!==live.preview_id||value.generation!==live.generation||value.artifact_sha256!==live.artifact_sha256)return;
      seq.current=next;setAck(value);setValues(value.input_values);if(!value.accepted)setError(value.error_code??"计算输入不在定义域，已保留上次画面");
    }catch(reason){if(version===generation.current){setError(String(reason));owner.current=null;setPicture(null);setAck(null);void api.stop(activityId,token,live).catch(()=>{});}}
    finally{if(version===generation.current)setBusy(false);}
  }
  async function stop(back=false){
    generation.current++;citationVersion.current++;control.current?.abort();control.current=new AbortController();setPicture(null);setAck(null);setCitation(null);owner.current=null;setBusy(false);setPollEpoch(old=>old+1);
    const live=current.current;
    if(live&&!TERMINAL.has(live.state)){
      setNotice("停止中，尚未确认资源树结束");
      try{const result=await api.stop(activityId,token,live,back?"back_to_learning":"user");current.current=result;setRunning(result);}
      catch(reason){setError(String(reason));}
    }
    if(back)onClose();
  }
  async function showCitation(id:string){
    const version=generation.current,selection=artifactVersion.current,request=++citationVersion.current;const source=item?.parent??parent;setCitation(null);
    const url=source.kind==="learning"?`/api/activities/${activityId}/learning/operations/${encodeURIComponent(source.operation_id)}/citations/${encodeURIComponent(id)}`:
      `/api/activities/${activityId}/teaching/records/${source.record_id}/citations/${encodeURIComponent(id)}`;
    try{const value=await api.request<unknown>(url,token,undefined,control.current?.signal);
      if(version===generation.current&&selection===artifactVersion.current&&request===citationVersion.current)setCitation(value);}
    catch(reason){if(version===generation.current&&selection===artifactVersion.current&&request===citationVersion.current)setError(String(reason));}
  }
  const ready=running&&["ready","running"].includes(running.state)&&running.eligible&&owner.current!==null;
  return <section aria-label="交互解释" className="ws-block">
    <h3>交互解释</h3><button onClick={()=>void stop(true)}>停止并回到学习</button>
    <p>固定程序在独立预览中计算和绘图；参数、公式、资料与限制可核对。</p>
    {!caps?.available&&<p role="status">交互解释未开放：{caps?.reason??"正在核对配置"}</p>}
    <label>需要解释的难点<textarea aria-label="交互解释难点" value={focus} maxLength={1024} onChange={event=>setFocus(event.target.value)}/></label>
    <label><input type="checkbox" checked={confirmed} onChange={event=>setConfirmed(event.target.checked)}/>确认父成果、资料与一次模型调用额度</label>
    <button disabled={!caps?.available||!confirmed||!focus.trim()||busy||Boolean(running&&!TERMINAL.has(running.state))} onClick={()=>void generate()}>确认生成交互解释</button>
    {pending.map(intent=><p key={intent.command.business_key}>未确认的生成意图：{intent.command.focus} <button onClick={()=>void reconcile(intent)}>只读核对原键</button></p>)}
    {saved.map(value=><button key={value.artifact_id} disabled={busy||!value.eligible||Boolean(running&&!TERMINAL.has(running.state))} onClick={()=>void loadArtifact(value.artifact_id,generation.current)}>读取已保存解释</button>)}
    {receipt&&<p role="status">生成状态：{receipt.status} / {receipt.terminal_disposition??"未确认"}</p>}
    {notice&&<p role="status">{notice}</p>}{error&&<p role="alert">{error}</p>}
    {item&&<><h4>{item.description.title}</h4><p>{item.description.concept}</p>
      <button disabled={!caps?.available||busy||Boolean(running&&!TERMINAL.has(running.state))} onClick={()=>void open()}>显式打开预览</button>
      <button disabled={!running||TERMINAL.has(running.state)} onClick={()=>void stop()}>停止预览</button>
      {running&&<p role="status">预览 {running.state} · 已用 {running.starts_used}/3 次 · 已结算 {running.settled_seconds} 秒 / 预留 {running.reserved_seconds} 秒</p>}
      <PreviewCanvas bytes={picture} identity={`${activityId}:${parentKey}:${running?.owner_id}:${running?.preview_id}:${running?.generation}:${item.artifact_sha256}:${generation.current}`}/>
      {item.description.inputs.map(control=><label key={control.id}>{control.label}
        <input aria-label={control.label} type={control.kind==="range"?"range":"number"} min={control.min} max={control.max} step={control.step} value={values[control.id]??control.default}
          disabled={!ready||busy} onChange={event=>{const value=event.target.value;setValues(old=>({...old,[control.id]:value}));}}/>
        <button disabled={!ready||busy} onClick={()=>{try{void send({type:"set_number",control_id:control.id,value:decimal(values[control.id]??control.default)});}catch(reason){setError(String(reason));}}}>应用{control.label}</button>
      </label>)}
      {item.description.actions.map(action=><button key={action.id} disabled={!ready||busy} onClick={()=>void send({type:"activate",action_id:action.id})}>{action.label}</button>)}
      <div aria-live="polite">{ack?.readouts.map(value=><p key={value.id}>{item.description.views.find(view=>view.id===value.id)?.label??value.id}：{value.value} {value.unit}</p>)}</div>
      {item.description.calculation_notes.map((note,index)=><div key={index}><p>公式：{note.formula}</p><p>适用域：{note.domain} · 误差：{note.error}</p>
        {note.samples.map((sample,i)=><p key={i}>{sample.input} → {sample.expected}</p>)}</div>)}
      <p>{item.description.limitations.join("；")}</p>
      {item.citations.map(value=><button key={value.citation_id} onClick={()=>void showCitation(value.citation_id)}>回查资料 · {value.title}</button>)}
      {citation!==null&&<pre aria-label="交互解释引用原文">{JSON.stringify(citation,null,2)}</pre>}
    </>}
  </section>;
}
