import {useEffect,useRef,useState} from 'react';
import {retrievalRequest,retrievalChains,retrieveForCommand,storeRetrievalChain,retrievalDisclosureKnown,serviceIdentityKnown,type ServiceIdentity,type RetrievalChain,type RetrievalReceipt,type RetrievalStatus} from './retrieval-api';

export function RetrievalPanel({token,activityId,scopeRevision,domainRevision,owner,mode,onMode,onContinue,indexAllowed=true,modelService=null,onDisclosureChange}:{token:string;activityId:string;scopeRevision:number;domainRevision:number;owner:string|null;mode:'hybrid'|'terms';onMode:(mode:'hybrid'|'terms')=>void;onContinue?:(chain:RetrievalChain)=>void;indexAllowed?:boolean;modelService?:ServiceIdentity|null;onDisclosureChange?:(ready:boolean)=>void}){
  const [status,setStatus]=useState<RetrievalStatus|null>(null),[chains,setChains]=useState<RetrievalChain[]>([]),[error,setError]=useState(''),[busy,setBusy]=useState(false);
  const current=useRef('');current.current=`${activityId}:${scopeRevision}:${domainRevision}:${owner}`;
  const mounted=useRef(false);useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;};},[]);
  const vectorKnown=retrievalDisclosureKnown(status),chatKnown=serviceIdentityKnown(modelService);
  const modelNoticeReady=chatKnown&&(mode==='terms'||vectorKnown);
  useEffect(()=>{onDisclosureChange?.(modelNoticeReady);},[modelNoticeReady,onDisclosureChange]);
  async function refresh(){const identity=current.current;const live=()=>mounted.current&&identity===current.current;try{const s=await retrievalRequest<RetrievalStatus>(token,activityId,'/status',undefined,live);const c=await retrievalChains(activityId);if(live()){setStatus(s);setChains(c);}}catch(e){if(live())setError((e as Error).message);}}
  useEffect(()=>{setStatus(null);setChains([]);void refresh();},[activityId,scopeRevision,domainRevision,owner,token]);
  async function index(){if(!owner||busy||!indexAllowed||!vectorKnown)return;const identity=current.current;setBusy(true);setError('');try{await retrieveForCommand(token,activityId,owner,'index',{},scopeRevision,domainRevision,'',()=>mounted.current&&identity===current.current);await refresh();}catch(e){if(identity===current.current)setError((e as Error).message);}finally{if(identity===current.current)setBusy(false);}}
  async function reconcile(row:RetrievalChain){const identity=current.current;setBusy(true);setError('');try{const receipt=await retrievalRequest<RetrievalReceipt>(token,activityId,`/commands/${row.query.business_key}`,undefined,()=>mounted.current&&identity===current.current);if(receipt.business_key!==row.query.business_key)throw new Error('原操作身份不同');await storeRetrievalChain({...row,receipt});await refresh();}catch(e){if(identity===current.current)setError((e as Error).message);}finally{if(identity===current.current)setBusy(false);}}
  return <section aria-label="资料检索与恢复"><h4>资料检索</h4><p>只使用当前确认的资料片段与本轮必要问题；回答和学习记忆不发送给向量服务。</p>
    <p>选择混合检索后，每次生成或评价先查询一次，合格后再调用一次模型，共需2次请求、两笔费用预留及两个运行窗口。未确认时保留原键，不自动重发。</p>
    {vectorKnown&&status?<p data-service-disclosure="vector">向量供应商：{status.provider}；模型：{status.model}。用途：{status.purpose}；索引单批预留 {status.reserve_cost_microunits} 微单位，每批运行窗口 {status.window_reserve_seconds} 秒。</p>:<p role="status">向量供应商、模型、用途或额度无法核对；索引及混合检索动作暂停。</p>}
    {chatKnown?<p data-service-disclosure="chat">聊天供应商：{modelService.provider}；模型：{modelService.model}。用途：后续教学或面试生成与评价，使用本轮目标、回答、必要历史及明确选择的学习记忆。</p>:<p role="status">聊天供应商或模型无法核对；模型动作暂停。本地保存、取消和只读核对仍按原资格可用。</p>}
    <label><input type="radio" checked={mode==='hybrid'} onChange={()=>onMode('hybrid')}/>结合原文词项与向量检索</label> <label><input type="radio" checked={mode==='terms'} onChange={()=>onMode('terms')}/>明确使用词项降级（不算混合检索通过）</label>
    <p>{status?.available?`已核对 ${status.fragments??0} 个片段，缓存 ${status.cached_fragments??0} 个。${status.ready?'当前索引就绪。':`本次至多 ${status.index_batches??0} 批，单批预留 ${status.reserve_cost_microunits} 微单位。`}`:'混合检索尚未就绪，请检查本机服务配置。'}</p>
    {status?.available&&<p>当前剩余 {status.remaining_requests} 次请求、{status.remaining_cost_microunits} 微单位费用额度、{status.remaining_running_seconds} 秒；查询及后续模型需预留 {status.query_then_model_reserve_microunits} 微单位、{2*status.window_reserve_seconds} 秒。预览后服务器仍逐笔核准；不足时整步不发。</p>}
    {!indexAllowed&&<p>请先保存面试目标并开始场次，再确认资料索引。</p>}
    <button disabled={busy} onClick={()=>void refresh()}>只读核对索引与原意图</button> <button disabled={busy||!owner||!vectorKnown||status?.ready||!indexAllowed} onClick={()=>void index()}>确认用途、费用与索引当前资料</button>
    {chains.filter(c=>c.owner===owner).map(c=><div key={c.key}><p>{c.domain==='index'?'资料索引':'本轮查询'} · {c.receipt?.terminal_disposition??'未确认'}{c.domain_sent?' · 后续动作已交付，请核对领域原意图':''}</p><button disabled={busy} onClick={()=>void reconcile(c)}>按原键只读核对</button>{c.domain!=='index'&&!c.domain_sent&&c.receipt?.current&&c.receipt.terminal_disposition==='received'&&onContinue&&<button disabled={busy||!modelNoticeReady||c.query.expected_scope_revision!==scopeRevision||c.query.expected_domain_revision!==domainRevision} onClick={()=>onContinue(c)}>明确继续尚未发送的原动作</button>}</div>)}
    {error&&<p role="alert">{error}</p>}</section>;
}
