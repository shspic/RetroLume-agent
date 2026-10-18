import type {InterviewAction,InterviewCommand,InterviewHead,InterviewGoal} from "./interviewApi";

export function canonicalInterview(value:unknown):string{
  if(value===null||typeof value!=="object")return JSON.stringify(value);
  if(Array.isArray(value))return `[${value.map(canonicalInterview).join(",")}]`;
  const obj=value as Record<string,unknown>;
  return `{${Object.keys(obj).sort().map(k=>`${JSON.stringify(k)}:${canonicalInterview(obj[k])}`).join(",")}}`;
}
export async function interviewSha(text:string):Promise<string>{
  const bytes=new TextEncoder().encode(text);
  const hash=await crypto.subtle.digest("SHA-256",bytes);
  return [...new Uint8Array(hash)].map(b=>b.toString(16).padStart(2,"0")).join("");
}
function goal(value:unknown):InterviewGoal|null{
  if(value===null)return null;
  const g=value as InterviewGoal;
  return {target:g.target,focus:g.focus??null,clarifications:g.clarifications??[],material_roles:(g.material_roles??[]).map(r=>({source_id:r.source_id,role:r.role??"unspecified"}))};
}
export function makeInterviewCommand(action:InterviewAction,head:InterviewHead|null,scope:number,body:Record<string,unknown>,key=crypto.randomUUID()):InterviewCommand{
  const normalized={...body};
  if(action==="start"||action==="goal")normalized.goal=goal(normalized.goal);
  if(action==="ask"){normalized.parent_feedback_id??=null;normalized.retry_of??=null;}
  if(action==="review")normalized.retry_of??=null;
  if(action==="bind_scope")normalized.material_roles??=[];
  return {schema:"interview.command.v1",business_key:key,action,expected_head_revision:head?.revision??0,expected_goal_version:head?.goal_version??0,expected_scope_revision:scope,body:normalized};
}
export function requestText(aid:string,command:InterviewCommand):string{
  const {business_key:_,...value}=command;
  return canonicalInterview({...value,activity_id:aid});
}
