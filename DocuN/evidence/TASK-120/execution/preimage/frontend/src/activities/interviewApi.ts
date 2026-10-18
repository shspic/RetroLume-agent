import {dataFetch} from "../data/context";
export type InterviewAction = "start"|"goal"|"ask"|"answer"|"correct_answer"|"review"|"bind_scope"|"abandon"|"finish";
export type MaterialRole = "resume"|"experience"|"measurement"|"reference"|"unspecified";
export type SourceRole = {source_id:string;role:MaterialRole};
export type InterviewGoal = {target:string;focus:string|null;clarifications:string[];material_roles:SourceRole[]};
export type InterviewCommand = {schema:"interview.command.v1"|"interview.command.v2";business_key:string;action:InterviewAction;expected_head_revision:number;expected_goal_version:number;expected_scope_revision:number;body:Record<string,unknown>;retrieval_ref?:import('./retrieval-api').RetrievalRef|null};
export type InterviewHead = {revision:number;goal_version:number;scope_revision:number;phase:string;round_index:number;probe_depth:number;last_seq:number;goal_record_id:string|null;root_question_id:string|null;current_question_id:string|null;current_answer_id:string|null;current_feedback_id:string|null;pending_key:string|null};
export type InterviewRecordMeta = {record_id:string;seq:number;kind:string;origin:string;goal_version:number;scope_revision:number;round_index:number;probe_depth:number;answer_version:number|null;question_record_id:string|null;body_sha256:string;operation_id:string|null;eligible:boolean;can_correct_answer:boolean};
export type InterviewSource = {source_id:string;version_id:string;source_revision:number;original_sha256:string;title:string;format:string;valid:boolean};
export type InterviewWorkspaceView = {schema:"interview.view.v1";profile?:"interview.v1"|"interview.v2";activity_id:string;domain:string;head:InterviewHead|null;sources:InterviewSource[];budget:Record<string,number|string|null>;pending:{business_key:string;status:string}|null;records:InterviewRecordMeta[];view_token:string;qualification:string;suppression_reason:string|null;capabilities:{local:boolean;model:boolean;model_reason:string|null;max_followups_per_round:number|null;max_output_tokens:number|null}};
export type InterviewReceipt = {schema:"interview.receipt.v1";activity_id:string;business_key:string;request_sha256:string;status:string;action:InterviewAction;effect_applied:boolean;duplicate_of:string|null;record_ids:string[];qualification:string;error_code:string|null;view_token:string;launch_claimed:boolean};
export type Recognition = {answer_record_id:string;answer_excerpt:string;explanation:string;verification_kind:"source_interpretation"|"user_statement";semantic_support:string;position_verified:boolean;reference_ids:string[]};
export type InterviewValue = {type?:string;text?:string;summary?:string;recognitions?:Recognition[];gaps?:{text:string;reference_ids:string[]}[];conflicts?:{text:string;reference_ids:string[]}[];next_steps?:string[];goal?:InterviewGoal;answer_version?:number};
export type InterviewCatalog = {citation_id:string;source_id:string;version_id:string;source_revision:number;title:string;text:string;start_line:number;end_line:number;start_offset:number;end_offset:number;physical_page:number|null};
export type InterviewDetail = {schema:"interview.record.v1";activity_id:string;record:InterviewRecordMeta;body:{value:InterviewValue;catalog?:InterviewCatalog[]}|null;view_token:string;qualification:string;suppression_reason:string|null};
export type InterviewHistory = {records:InterviewRecordMeta[];view_token:string;next_before_seq:number|null;last_seq:number};

export class InterviewApiError extends Error {
  constructor(public code:string,public status:number,message:string){super(message);}
}

export async function interviewRequest<T>(token:string,path:string,init:RequestInit={},guard?:()=>boolean):Promise<T>{
  const response=await dataFetch(path,{...init,headers:{"X-Retrolume-Session":token,...init.headers},credentials:"omit",cache:"no-store"});
  if(guard&&!guard())throw new DOMException("面板身份已变化","AbortError");
  const data=await response.json();
  if(guard&&!guard())throw new DOMException("面板身份已变化","AbortError");
  if(!response.ok){const error=data.detail??data;throw new InterviewApiError(error.code??"unavailable",response.status,error.message??"请求未确认，请只读核对原提交结果");}
  return data as T;
}

const base=(aid:string)=>`/api/activities/${encodeURIComponent(aid)}/interview`;
export const getInterviewWorkspace=(token:string,aid:string,signal?:AbortSignal,guard?:()=>boolean)=>interviewRequest<InterviewWorkspaceView>(token,`${base(aid)}/workspace`,{signal},guard);
export const getInterviewReceipt=(token:string,aid:string,key:string,signal?:AbortSignal,guard?:()=>boolean)=>interviewRequest<InterviewReceipt>(token,`${base(aid)}/commands/${encodeURIComponent(key)}`,{signal},guard);
export const getInterviewRecord=(token:string,aid:string,rid:string,view:string,signal?:AbortSignal,guard?:()=>boolean)=>interviewRequest<InterviewDetail>(token,`${base(aid)}/records/${encodeURIComponent(rid)}?view_token=${encodeURIComponent(view)}`,{signal},guard);
export const getInterviewHistory=(token:string,aid:string,view:string,before?:number,signal?:AbortSignal,guard?:()=>boolean)=>interviewRequest<InterviewHistory>(token,`${base(aid)}/history?limit=20&view_token=${encodeURIComponent(view)}${before?`&before_seq=${before}`:""}`,{signal},guard);
export const postInterview=(token:string,aid:string,command:InterviewCommand,signal?:AbortSignal,guard?:()=>boolean)=>interviewRequest<InterviewReceipt>(token,`${base(aid)}/commands`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(command),signal},guard);
export const getInterviewCitation=(token:string,aid:string,rid:string,cid:string,view:string,signal?:AbortSignal,guard?:()=>boolean)=>interviewRequest<{citation:InterviewCatalog;position_verified:boolean;semantic_verification:string;view_token:string}>(token,`${base(aid)}/records/${encodeURIComponent(rid)}/citations/${encodeURIComponent(cid)}?view_token=${encodeURIComponent(view)}`,{signal},guard);
