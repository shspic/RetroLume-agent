// 无浏览器离线验证真实意图函数与核对匹配，不能替代UI反例证据。
import assert from "node:assert/strict";
import { appendIntent,loadIntents,updateIntent,removeIntent,clearIntents } from "../src/activities/pendingIntents.ts";
import { compareLearningIntent } from "../src/activities/learningIntentMatch.ts";

const values=new Map();let writeFailed=false;
globalThis.localStorage={getItem:key=>values.get(key)??null,setItem:(key,value)=>{if(writeFailed)throw Error("quota");values.set(key,value);},removeItem:key=>values.delete(key)};
const key="retrolume.pending-intents.v1";
const base={intent_id:"intent",state:"unconfirmed",created_at:"2026-10-02",activity_id:crypto.randomUUID()};
const old={...base,kind:"continue",operation_id:"ordinary",parent_operation_id:"parent",followup:"old question"};
values.set(key,JSON.stringify([old]));assert.deepEqual(loadIntents(),{ok:true,items:[old]});
clearIntents();const first={...base,kind:"learning_first",business_key:crypto.randomUUID(),goal:" atomicity "};
assert.ok(appendIntent(first));assert.ok(updateIntent("intent",{state:"submitted"}));
assert.equal(loadIntents().items[0].state,"submitted");
assert.equal(compareLearningIntent(first,{profile:"learning.v1",action:"first",goal:"atomicity"}),"matching");
assert.equal(compareLearningIntent(first,{profile:"learning.v1",action:"first",goal:"other goal"}),"conflict");
assert.equal(compareLearningIntent(first,null),"unconfirmed");
const follow={...base,kind:"learning_followup",business_key:crypto.randomUUID(),parent_operation_id:"parent",followup:" question "};
assert.equal(compareLearningIntent(follow,{profile:"learning.v1",action:"followup",question:"question",parent_operation_id:"parent"}),"matching");
for(const patch of [{question:"other"},{parent_operation_id:"different"}]){
  assert.equal(compareLearningIntent(follow,{profile:"learning.v1",action:"followup",question:"question",parent_operation_id:"parent",...patch}),"conflict");
}
removeIntent("intent");assert.equal(loadIntents().items.length,0);
for(const damaged of ["{{{",JSON.stringify([{...first,business_key:null}]),JSON.stringify([{...follow,parent_operation_id:null}])]){
  values.set(key,damaged);assert.equal(loadIntents().ok,false);assert.equal(appendIntent(first),false);
}
clearIntents();writeFailed=true;assert.equal(appendIntent(first),false);assert.equal(loadIntents().items.length,0);
console.log(JSON.stringify({checks:15,result:"PASS",browser_launched:false,network_calls:0,
  scope:"真实意图纯函数及输入匹配，UI动态核对、迟到恢复仍未复验"}));
