import {useEffect,useRef,useState} from "react";
import {getInterviewCitation,type InterviewCatalog} from "./interviewApi";
import {interviewEditorOwner} from "./interviewIntents";

export function InterviewCitations({token,activityId,recordId,viewToken,catalog,owner}:{token:string;activityId:string;recordId:string;viewToken:string;catalog:InterviewCatalog[];owner:string}){
  const [selected,setSelected]=useState<InterviewCatalog|null>(null),[error,setError]=useState("");
  const generation=useRef(0),request=useRef<AbortController|null>(null);
  const identity=useRef({activityId,recordId,viewToken,owner});identity.current={activityId,recordId,viewToken,owner};
  useEffect(()=>{generation.current++;request.current?.abort();setSelected(null);setError("");return()=>{generation.current++;request.current?.abort();};},[activityId,recordId,viewToken,owner]);
  async function open(id:string){
    request.current?.abort();const controller=new AbortController();request.current=controller;const stamp=++generation.current;const expected={activityId,recordId,viewToken};
    const live=()=>!controller.signal.aborted&&generation.current===stamp&&identity.current.owner===owner&&identity.current.activityId===expected.activityId&&identity.current.recordId===expected.recordId&&identity.current.viewToken===expected.viewToken;
    setSelected(null);setError("");
    try{const now=await interviewEditorOwner();if(!live()||now!==owner)return;const result=await getInterviewCitation(token,activityId,recordId,id,viewToken,controller.signal,live);if(live()&&result.view_token===expected.viewToken)setSelected(result.citation);}
    catch(reason){if(live())setError(reason instanceof Error?reason.message:"引用无法核对");}
  }
  return <div className="interview-citations"><p className="quiet">位置已核对与语义支持是两项判断；引用不证明来源真实性或自报业绩。</p>
    {catalog.map(c=><button type="button" key={c.citation_id} onClick={()=>void open(c.citation_id)}>查看依据：{c.title} · 版本{c.source_revision}</button>)}
    {error&&<p role="alert">{error}</p>}{selected&&<article aria-label="面试引用"><strong>{selected.title} · 版本{selected.source_revision}</strong><p>{selected.physical_page?`物理页${selected.physical_page} · `:""}第{selected.start_line}—{selected.end_line}行</p><pre>{selected.text}</pre><p>语义判断仍为模型建议。</p></article>}
  </div>;
}
