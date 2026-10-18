import type { HtmlCommand } from "./contracts";
const KEY="retrolume.html11.intents.v2";
export type HtmlIntent={activity_id:string;command:HtmlCommand;state:"pending"|"unconfirmed"};
export function readIntents():HtmlIntent[]{
  const raw=localStorage.getItem(KEY);if(!raw)return [];
  if(raw.length>65536)throw new Error("交互意图台账过大，保持只读");const values:unknown=JSON.parse(raw);
  if(!Array.isArray(values)||values.length>32)throw new Error("交互意图台账不可核对");
  for(const v of values){if(!v||typeof v!=="object"||Object.keys(v).sort().join(",")!=="activity_id,command,state"||
    typeof v.activity_id!=="string"||!["pending","unconfirmed"].includes(v.state)||typeof v.command?.business_key!=="string"||
    typeof v.command?.focus!=="string"||!v.command.parent||typeof v.command.expected_config_sha256!=="string"||v.command.confirmed!==true)throw new Error("交互意图台账不可核对");}
  return values as HtmlIntent[];
}
export function saveIntent(activity_id:string,command:HtmlCommand){
  const values=readIntents();if(values.some(v=>v.activity_id===activity_id&&v.command.business_key===command.business_key))return;
  if(values.length>=32)throw new Error("待核对交互意图已达上限");
  const raw=JSON.stringify([...values,{activity_id,command,state:"pending"}]);if(raw.length>65536)throw new Error("交互意图无法保存");localStorage.setItem(KEY,raw);
}
export function resolveIntent(activity_id:string,key:string){localStorage.setItem(KEY,JSON.stringify(readIntents().filter(v=>v.activity_id!==activity_id||v.command.business_key!==key)));}
