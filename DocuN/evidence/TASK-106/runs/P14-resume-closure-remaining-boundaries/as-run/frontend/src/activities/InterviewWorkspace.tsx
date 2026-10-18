import {useEffect,useRef,useState} from "react";
import {getInterviewWorkspace,getInterviewRecord,getInterviewHistory,getInterviewReceipt,postInterview,interviewRequest,
  InterviewApiError,type InterviewWorkspaceView,type InterviewDetail,type InterviewHistory,type InterviewReceipt,type InterviewAction,type InterviewGoal,type MaterialRole} from "./interviewApi";
import {makeInterviewCommand,interviewSha,requestText} from "./interviewDrafts";
import {interviewEditorOwner,loadInterviewIntents,readInterviewDraft,saveInterviewIntent,noteInterviewReceipt,type InterviewIntent} from "./interviewIntents";
import {InterviewCitations} from "./InterviewCitations";
import "./interview-workspace.css";

const PHASE:Record<string,string>={needs_goal:"请补充具体目标",ready:"可开始提问",question_ready:"等待你的回答",answer_ready:"回答已保存，可请求追问或反馈",feedback_ready:"本轮反馈已保存",ended:"本场次已结束，只读历史"};
const ROLES:Record<MaterialRole,string>={unspecified:"用途未定（按自报）",reference:"概念对照资料",resume:"简历（自报）",experience:"经历（自报）",measurement:"测量／收益（自报）"};
const LABEL:Record<string,string>={start:"开始场次",goal:"目标版本",scope:"范围确认",question:"问题",probe:"必要追问",answer:"回答",feedback:"反馈建议",finish:"结束场次",abandon:"显式放弃未确认意图"};
type Material={id:string;title:string;version_id:string;revision:number;sha256:string};

export function InterviewWorkspace({activityId,token,scopeRevision,onChanged}:{activityId:string;token:string;scopeRevision:number;onChanged?:()=>void}){
  const [view,setView]=useState<InterviewWorkspaceView|null>(null),[details,setDetails]=useState<Record<string,InterviewDetail>>({}),[history,setHistory]=useState<InterviewHistory|null>(null);
  const [target,setTarget]=useState(""),[focus,setFocus]=useState(""),[answer,setAnswer]=useState(""),[roles,setRoles]=useState<Record<string,MaterialRole>>({});
  const [error,setError]=useState(""),[notice,setNotice]=useState(""),[busy,setBusy]=useState(false),[owner,setOwner]=useState<string|null>(null),[intents,setIntents]=useState<InterviewIntent[]>([]);
  const [chosenHistory,setChosenHistory]=useState<InterviewDetail|null>(null),[materials,setMaterials]=useState<Material[]>([]),[rangeIds,setRangeIds]=useState<string[]>([]);
  const panel=useRef(0),active=useRef({activityId,token,owner:null as string|null,viewToken:""}),controllers=useRef(new Set<AbortController>());
  const draftIdentity=useRef<{key:string;hash:string;text:string}|null>(null),viewRef=useRef<InterviewWorkspaceView|null>(null);
  active.current={activityId,token,owner,viewToken:view?.view_token??""};viewRef.current=view;
  const alive=(stamp:number,aid=activityId)=>panel.current===stamp&&active.current.activityId===aid;
  function controller(){const c=new AbortController();controllers.current.add(c);return c;}
  function localIntents(currentOwner:string|null){const state=loadInterviewIntents();if(!state.ok)throw new Error("本机待确认意图无法读取；请保留草稿，不会提交");return state.items.filter(x=>x.activity_id===activityId&&x.owner===currentOwner);}

  async function refresh(){
    const stamp=panel.current,aid=activityId,c=controller();setError("");
    try{
      const next=await getInterviewWorkspace(token,aid,c.signal,()=>alive(stamp,aid));if(!alive(stamp,aid))return;
      setView(next);viewRef.current=next;active.current.viewToken=next.view_token;
      const loaded:Record<string,InterviewDetail>={};
      for(const row of next.records){
        const detail=await getInterviewRecord(token,aid,row.record_id,next.view_token,c.signal,()=>alive(stamp,aid)&&active.current.viewToken===next.view_token);
        if(!alive(stamp,aid)||active.current.viewToken!==next.view_token)return;
        loaded[row.record_id]=detail;
      }
      if(!alive(stamp,aid)||active.current.viewToken!==next.view_token)return;
      setDetails(loaded);setChosenHistory(null);
      const goal=next.head?.goal_record_id?loaded[next.head.goal_record_id]?.body?.value.goal:null;
      if(goal){setTarget(goal.target);setFocus(goal.focus??"");setRoles(Object.fromEntries(goal.material_roles.map(r=>[r.source_id,r.role])));}
      setRangeIds(next.sources.map(s=>s.source_id));
      const h=await getInterviewHistory(token,aid,next.view_token,undefined,c.signal,()=>alive(stamp,aid)&&active.current.viewToken===next.view_token);
      if(!alive(stamp,aid)||active.current.viewToken!==next.view_token)return;
      setHistory(h);setIntents(localIntents(active.current.owner));
    }catch(reason){if(alive(stamp,aid)&&!c.signal.aborted)setError(reason instanceof Error?reason.message:"面试读取未确认");}
    finally{controllers.current.delete(c);}
  }
  useEffect(()=>{
    const stamp=++panel.current;setView(null);setDetails({});setHistory(null);setChosenHistory(null);setTarget("");setFocus("");setAnswer("");setError("");setNotice("");setBusy(false);draftIdentity.current=null;
    void interviewEditorOwner().then(o=>{if(alive(stamp)){setOwner(o);active.current.owner=o;setIntents(localIntents(o));}}).catch(()=>{if(alive(stamp))setError("编辑身份不可用；保持只读");});
    void refresh();
    return()=>{panel.current++;draftIdentity.current=null;for(const c of controllers.current)c.abort();controllers.current.clear();};
  },[activityId,token]);

  function goal():InterviewGoal{return {target,focus:focus.trim()?focus:null,clarifications:[],material_roles:(view?.sources??[]).map(s=>({source_id:s.source_id,role:roles[s.source_id]??"unspecified"}))};}
  async function submit(action:InterviewAction,body:Record<string,unknown>){
    if(busy||!owner||!view)return;
    const expectedOwner=owner,stamp=panel.current,aid=activityId,expectedView=view.view_token;
    const command=makeInterviewCommand(action,view.head,view.head?.scope_revision??scopeRevision,body);
    const text=requestText(aid,command);draftIdentity.current={key:command.business_key,hash:"",text};setBusy(true);setError("");setNotice("");
    const synchronous=()=>alive(stamp,aid)&&active.current.owner===expectedOwner&&active.current.viewToken===expectedView&&draftIdentity.current?.key===command.business_key&&draftIdentity.current.text===text;
    try{
      const hash=await interviewSha(text);if(!synchronous())return;draftIdentity.current!.hash=hash;
      const stillCurrent=()=>synchronous()&&draftIdentity.current?.hash===hash;
      const actualOwner=await interviewEditorOwner();if(!stillCurrent()||actualOwner!==expectedOwner)return;
      await saveInterviewIntent({key:command.business_key,activity_id:aid,owner:expectedOwner,hash,command},stillCurrent);
      if(!stillCurrent())return;
      const afterSaveOwner=await interviewEditorOwner();if(!stillCurrent()||afterSaveOwner!==expectedOwner)return;
      // No await between this last identity check and POST.
      if(!stillCurrent())return;
      const c=controller();let receipt:InterviewReceipt;
      try{receipt=await postInterview(token,aid,command,c.signal,stillCurrent);}finally{controllers.current.delete(c);}
      if(!stillCurrent()||receipt.business_key!==command.business_key||receipt.activity_id!==aid||receipt.request_sha256!==hash)return;
      await noteInterviewReceipt(receipt,expectedOwner);if(!stillCurrent())return;
      setNotice(receipt.status==="unknown"?"尚未确认是否完成，请查看原提交结果；不会自动重发。":receipt.effect_applied?"已持久保存。继续与下一题都需要你的明确选择。":"已核对原回执；没有第二次业务效果。");
      if(action==="answer"||action==="correct_answer")setAnswer("");
      await refresh();if(alive(stamp,aid))onChanged?.();
    }catch(reason){if(alive(stamp,aid))setError(reason instanceof Error?reason.message:"请求未确认，请按原键只读核对，不会自动提交");}
    finally{if(alive(stamp,aid)){setBusy(false);setIntents(localIntents(active.current.owner));}}
  }
  async function reconcile(intent:InterviewIntent,resubmit=false){
    if(busy||!owner||intent.owner!==owner)return;
    const stamp=panel.current,aid=activityId,expectedOwner=owner;setBusy(true);setError("");
    const live=()=>alive(stamp,aid)&&active.current.owner===expectedOwner;
    try{
      let receipt:InterviewReceipt|null=null;
      try{receipt=await getInterviewReceipt(token,aid,intent.key,undefined,live);}catch(reason){if(!(reason instanceof InterviewApiError&&reason.status===404))throw reason;}
      if(!live())return;
      if(receipt&&receipt.request_sha256!==intent.hash)throw new Error("服务器原意图正文hash不同，拒绝重交");
      if(resubmit){
        if(receipt&&!(receipt.status==="accepted"&&!receipt.launch_claimed&&!receipt.duplicate_of)){setNotice("原提交已进入处理或已有终态，只读核对；不会再启动。");}
        else{
          const draft=await readInterviewDraft(intent.key);if(!live())return;
          const now=await interviewEditorOwner();if(!live()||now!==expectedOwner)return;
          if(!draft||draft.owner!==expectedOwner||draft.activity_id!==aid||draft.hash!==intent.hash||draft.command.business_key!==intent.key)throw new Error("原键正文或编辑身份缺失，不能重交");
          const hash=await interviewSha(requestText(aid,draft.command));if(!live()||hash!==intent.hash)throw new Error("本机正文hash无法核对，不能重交");
          const freshOwner=await interviewEditorOwner();if(!live()||freshOwner!==expectedOwner)return;
          if(!live())return;
          receipt=await postInterview(token,aid,draft.command,undefined,live);if(!live())return;
        }
      }
      if(receipt){await noteInterviewReceipt(receipt,expectedOwner);if(!live())return;setNotice(`原提交状态：${receipt.status}。未重新生成业务键。`);}
      else setNotice("服务器未找到原提交；请保留本机正文，可显式重交原意图。");
      await refresh();
    }catch(reason){if(live())setError(reason instanceof Error?reason.message:"原提交无法核对");}
    finally{if(live()){setBusy(false);setIntents(localIntents(expectedOwner));}}
  }
  async function loadRange(){
    const stamp=panel.current,c=controller();try{const list=await interviewRequest<{items:Material[];next_offset:number|null}>(token,"/api/materials",{signal:c.signal});if(alive(stamp))setMaterials(list.items);}
    catch(reason){if(alive(stamp)&&!c.signal.aborted)setError(reason instanceof Error?reason.message:"资料列表无法读取");}finally{controllers.current.delete(c);}
  }
  async function bindRange(){
    if(!materials.length||!rangeIds.length||rangeIds.length>10){setError("请明确选择1—10份当前资料");return;}
    const selected=rangeIds.map(id=>materials.find(m=>m.id===id));if(selected.some(m=>!m)){setError("当前资料版本未全部加载，请先读取当前资料");return;}
    await submit("bind_scope",{sources:selected.map(m=>({source_id:m!.id,version_id:m!.version_id,source_revision:m!.revision,original_sha256:m!.sha256})).sort((a,b)=>a.source_id.localeCompare(b.source_id)),material_roles:rangeIds.map(id=>({source_id:id,role:roles[id]??"unspecified"})).sort((a,b)=>a.source_id.localeCompare(b.source_id))});
  }
  async function showRecord(id:string){const stamp=panel.current,c=controller(),expected=view?.view_token;if(!expected)return;try{const result=await getInterviewRecord(token,activityId,id,expected,c.signal,()=>alive(stamp)&&active.current.viewToken===expected);if(alive(stamp)&&active.current.viewToken===expected)setChosenHistory(result);}catch(reason){if(alive(stamp)&&!c.signal.aborted)setError(reason instanceof Error?reason.message:"历史详情无法读取");}finally{controllers.current.delete(c);}}
  async function moreHistory(){if(!history?.next_before_seq||!view)return;const stamp=panel.current,expected=view.view_token,c=controller();try{const next=await getInterviewHistory(token,activityId,expected,history.next_before_seq,c.signal,()=>alive(stamp)&&active.current.viewToken===expected);if(alive(stamp)&&active.current.viewToken===expected)setHistory({...next,records:[...history.records,...next.records]});}catch(reason){if(alive(stamp)&&!c.signal.aborted)setError(reason instanceof Error?reason.message:"历史游标已变化，请重新读取");}finally{controllers.current.delete(c);}}

  const head=view?.head,question=head?.current_question_id?details[head.current_question_id]:null,savedAnswer=head?.current_answer_id?details[head.current_answer_id]:null,feedback=head?.current_feedback_id?details[head.current_feedback_id]:null;
  const finished=head?.phase==="ended",pending=Boolean(view?.pending),writeDisabled=busy||!owner||finished;
  function detailCard(item:InterviewDetail|null|undefined){
    if(!item)return null;const value=item.body?.value;
    return <article key={item.record.record_id} aria-label={`面试${LABEL[item.record.kind]??item.record.kind}`}><h4>{LABEL[item.record.kind]??item.record.kind} · 目标v{item.record.goal_version}{item.record.answer_version?` · 回答v${item.record.answer_version}`:""}</h4>
      {!value?<p>该记录仍保留，当前正文已抑制：{item.suppression_reason}</p>:<><pre>{value.text??value.summary??(value.goal?value.goal.target:"")}</pre>
        {value.recognitions?.map((r,i)=><div key={i} className={r.verification_kind==="source_interpretation"?"interview-supported":"interview-gap"}><strong>{r.verification_kind==="source_interpretation"?"有依据的部分 · 资料对照建议":"用户已说明 · 未独立核实"}</strong><p>“{r.answer_excerpt}”</p><p>{r.explanation}</p></div>)}
        {value.gaps?.length? <div className="interview-gap"><h4>尚缺依据或不确定</h4>{value.gaps.map((g,i)=><p key={i}>{g.text}</p>)}</div>:null}
        {value.conflicts?.length?<div><h4>冲突资料</h4>{value.conflicts.map((g,i)=><p key={i}>{g.text}</p>)}</div>:null}
        {value.next_steps?.map((s,i)=><p key={i}>建议：{s}</p>)}
        {item.body?.catalog?.length&&owner?<InterviewCitations key={`${activityId}:${item.record.record_id}:${owner}:${view?.view_token}`} token={token} activityId={activityId} recordId={item.record.record_id} viewToken={view?.view_token??""} catalog={item.body.catalog} owner={owner}/>:null}</>}
    </article>;
  }
  return <div className="interview-workspace" aria-label="文字模拟面试工作区" data-interview-activity-id={activityId}><h3>文字模拟面试</h3><p>首版只在未选择记忆的全新活动开始；不固定学科、岗位或总题数。模型反馈是建议，经历与收益保留自报身份。</p>
    {error&&<p role="alert" className="failure">{error}</p>}{notice&&<p role="status">{notice}</p>}<button type="button" disabled={busy} onClick={()=>void refresh()}>只读刷新／恢复场次</button>
    {!owner&&<p>本机编辑身份或锁不可用，保持只读。可以复制自己的草稿。</p>}
    {view&&<><section><h4>本次资料范围与预算</h4>{view.sources.map(s=><p key={s.source_id}>{s.title} · 版本{s.source_revision} · {s.valid?"当前可用":"已更新，须重新确认范围"}</p>)}
      <p>次数：{view.budget.requests_reserved} / {view.budget.max_requests}；费用预留：{view.budget.cost_reserved_microunits} / {view.budget.max_cost_microunits}微单位，单次最多{view.budget.reserve_cost_microunits}微单位。</p><p>时间：已结算{view.budget.running_settled_seconds}秒，预留{view.budget.running_reserved_seconds}秒，上限{view.budget.max_running_seconds}秒；工具已用{view.budget.tools_reserved}，本面试不使用工具。</p>
      <p>本场次不使用已保存记忆。外发仅含当前目标、必要回答版本与有界资料片段。</p>
      <button type="button" disabled={busy||finished} onClick={()=>void loadRange()}>读取当前资料，明确更新范围</button>{materials.length>0&&<div>{materials.map(m=><label key={m.id}><span><input type="checkbox" disabled={busy||finished} checked={rangeIds.includes(m.id)} onChange={e=>setRangeIds(ids=>e.target.checked?[...ids,m.id]:ids.filter(id=>id!==m.id))}/>{m.title} · 当前版本{m.revision}</span></label>)}<button type="button" disabled={writeDisabled} onClick={()=>void bindRange()}>确认新的资料范围</button></div>}
    </section><section><h4>目标{head?` v${head.goal_version}`:""}与资料用途</h4><label>希望针对哪个主题、角色或场景练习？<textarea aria-label="面试目标" value={target} disabled={writeDisabled} maxLength={1024} onChange={e=>setTarget(e.target.value)}/></label><label>具体重点或同名澄清<textarea aria-label="面试重点" value={focus} disabled={writeDisabled} maxLength={1024} onChange={e=>setFocus(e.target.value)}/></label>
      {view.sources.map(s=><label key={s.source_id}>{s.title}的用途<select aria-label={`${s.title}的面试用途`} disabled={writeDisabled} value={roles[s.source_id]??"unspecified"} onChange={e=>setRoles(r=>({...r,[s.source_id]:e.target.value as MaterialRole}))}>{(Object.keys(ROLES) as MaterialRole[]).map(r=><option key={r} value={r}>{ROLES[r]}</option>)}</select></label>)}
      {head?<button type="button" disabled={writeDisabled||!target.trim()} onClick={()=>void submit("goal",{goal:goal()})}>保存修正目标（另存版本）</button>:<button type="button" disabled={writeDisabled||view.domain!=="none"} onClick={()=>void submit("start",{goal:target.trim()?goal():null})}>开始场次</button>}
      {view.domain==="existing"&&<p>已有学习／教学／运行事实的活动不能转成面试，请新建未选择记忆的活动。</p>}
    </section>{head&&<><p role="status">{pending?`原动作${view.pending?.status==="unknown"?"未确认":"处理中"}，请核对原提交`:PHASE[head.phase]??head.phase}</p>
      {!view.capabilities.model&&<p>模型动作未开放：{view.capabilities.model_reason}；本地答案与只读核对仍按当前资格可用。</p>}
      {detailCard(question)}{detailCard(savedAnswer)}{(head.phase==="question_ready"||head.phase==="answer_ready"||head.phase==="feedback_ready")&&<section><label>{head.phase==="question_ready"?"你的回答":"修改当前回答（另存新版本）"}<textarea aria-label="面试回答" value={answer} maxLength={4096} disabled={writeDisabled} onChange={e=>setAnswer(e.target.value)}/></label><button type="button" disabled={writeDisabled||!answer.trim()||(!head.current_question_id)} onClick={()=>void submit(head.current_answer_id?"correct_answer":"answer",head.current_answer_id?{answer_record_id:head.current_answer_id,expected_answer_version:savedAnswer?.record.answer_version??1,text:answer}:{question_record_id:head.current_question_id,text:answer})}>保存回答{head.current_answer_id?"新版本":""}（不调用模型）</button></section>}
      {detailCard(feedback)}<div className="interview-actions">
        {head.phase==="ready"&&<button type="button" disabled={writeDisabled||pending} onClick={()=>void submit("ask",{mode:"first"})}>开始提问</button>}
        {head.phase==="answer_ready"&&<button type="button" disabled={writeDisabled||pending} onClick={()=>void submit("review",{question_record_id:head.current_question_id,answer_record_id:head.current_answer_id})}>获取必要追问或反馈</button>}
        {head.phase==="feedback_ready"&&<button type="button" disabled={writeDisabled||pending} onClick={()=>void submit("ask",{mode:"next",parent_feedback_id:head.current_feedback_id})}>继续下一题（显式调用）</button>}
        {pending&&<button type="button" disabled={writeDisabled} onClick={()=>void submit("abandon",{pending_key:head.pending_key})}>显式放弃原意图（不退款／不重发）</button>}
        {!finished&&<button type="button" disabled={writeDisabled||pending} onClick={()=>void submit("finish",{})}>结束本场次</button>}
      </div></>}
    <section className="interview-history"><h4>持久历史 · 元数据</h4><p>读取历史不提交或调用；旧评价可失去当前资格，事实与用户回答版本仍保留。</p><ol>{history?.records.map(r=><li key={r.record_id}>{LABEL[r.kind]??r.kind} · 目标v{r.goal_version} · 范围v{r.scope_revision}{r.answer_version?` · 回答v${r.answer_version}`:""} · {r.eligible?"可读取":"正文已抑制"}<button type="button" onClick={()=>void showRecord(r.record_id)}>只读查看该版本</button></li>)}</ol>{history?.next_before_seq&&<button type="button" onClick={()=>void moreHistory()}>读取更早历史</button>}{detailCard(chosenHistory)}</section>
    <section><h4>本机原意图</h4><p>正文先保存在本机，再提交；刷新只按原键读取。已开始或未知不得重发。</p>{intents.map(i=><div key={i.key}>{LABEL[i.action]??i.action} · {i.state}<button type="button" disabled={busy} onClick={()=>void reconcile(i)}>只读核对原提交</button><button type="button" disabled={writeDisabled} onClick={()=>void reconcile(i,true)}>在安全条件下显式重交原意图</button></div>)}</section>
    </>}
  </div>;
}
