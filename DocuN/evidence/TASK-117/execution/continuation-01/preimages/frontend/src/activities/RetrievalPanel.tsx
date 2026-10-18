import {useEffect,useRef,useState} from 'react';
import {retrievalRequest,retrievalChains,retrieveForCommand,storeRetrievalChain,type RetrievalChain,type RetrievalReceipt,type RetrievalStatus} from './retrieval-api';

export function RetrievalPanel({token,activityId,scopeRevision,domainRevision,owner,mode,onMode,onContinue}:{token:string;activityId:string;scopeRevision:number;domainRevision:number;owner:string|null;mode:'hybrid'|'terms';onMode:(mode:'hybrid'|'terms')=>void;onContinue?:(chain:RetrievalChain)=>void}){
  const [status,setStatus]=useState<RetrievalStatus|null>(null),[chains,setChains]=useState<RetrievalChain[]>([]),[error,setError]=useState(''),[busy,setBusy]=useState(false);
  const current=useRef('');current.current=`${activityId}:${scopeRevision}:${domainRevision}:${owner}`;
  const mounted=useRef(false);useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;};},[]);
  async function refresh(){const identity=current.current;const live=()=>mounted.current&&identity===current.current;try{const s=await retrievalRequest<RetrievalStatus>(token,activityId,'/status',undefined,live);const c=await retrievalChains(activityId);if(live()){setStatus(s);setChains(c);}}catch(e){if(live())setError((e as Error).message);}}
  useEffect(()=>{setStatus(null);setChains([]);void refresh();},[activityId,scopeRevision,domainRevision,owner,token]);
  async function index(){if(!owner||busy)return;const identity=current.current;setBusy(true);setError('');try{await retrieveForCommand(token,activityId,owner,'index',{},scopeRevision,domainRevision,'',()=>mounted.current&&identity===current.current);await refresh();}catch(e){if(identity===current.current)setError((e as Error).message);}finally{if(identity===current.current)setBusy(false);}}
  async function reconcile(row:RetrievalChain){const identity=current.current;setBusy(true);setError('');try{const receipt=await retrievalRequest<RetrievalReceipt>(token,activityId,`/commands/${row.query.business_key}`,undefined,()=>mounted.current&&identity===current.current);if(receipt.business_key!==row.query.business_key)throw new Error('原操作身份不同');await storeRetrievalChain({...row,receipt});await refresh();}catch(e){if(identity===current.current)setError((e as Error).message);}finally{if(identity===current.current)setBusy(false);}}
  return <section aria-label="资料检索与恢复"><h4>资料检索</h4><p>只使用当前确认的资料片段与本轮必要问题；回答和学习记忆不发送给向量服务。</p>
    <p>选择混合检索后，每次生成或评价先查询一次，向量请求费用预留至多 ¥0.25；合格后才调用一次模型，另预留至多 ¥0.25。未确认时保留原键，不自动重发。</p>
    <label><input type="radio" checked={mode==='hybrid'} onChange={()=>onMode('hybrid')}/>结合原文词项与向量检索</label> <label><input type="radio" checked={mode==='terms'} onChange={()=>onMode('terms')}/>明确使用词项降级（不算混合检索通过）</label>
    <p>{status?.available?`已核对 ${status.fragments??0} 个片段，缓存 ${status.cached_fragments??0} 个。${status.ready?'当前索引就绪。':`本次至多 ${status.index_batches??0} 批，单批费用预留 ¥0.25。`}`:'混合检索尚未就绪，请检查本机服务配置。'}</p>
    <button disabled={busy} onClick={()=>void refresh()}>只读核对索引与原意图</button> <button disabled={busy||!owner||!status?.available||status.ready} onClick={()=>void index()}>确认用途、费用与索引当前资料</button>
    {chains.filter(c=>c.owner===owner).map(c=><div key={c.key}><p>{c.domain==='index'?'资料索引':'本轮查询'} · {c.receipt?.terminal_disposition??'未确认'}{c.domain_sent?' · 后续动作已交付，请核对领域原意图':''}</p><button disabled={busy} onClick={()=>void reconcile(c)}>按原键只读核对</button>{c.domain!=='index'&&!c.domain_sent&&c.receipt?.current&&c.receipt.terminal_disposition==='received'&&onContinue&&<button disabled={busy||c.query.expected_scope_revision!==scopeRevision||c.query.expected_domain_revision!==domainRevision} onClick={()=>onContinue(c)}>明确继续尚未发送的原动作</button>}</div>)}
    {error&&<p role="alert">{error}</p>}</section>;
}
