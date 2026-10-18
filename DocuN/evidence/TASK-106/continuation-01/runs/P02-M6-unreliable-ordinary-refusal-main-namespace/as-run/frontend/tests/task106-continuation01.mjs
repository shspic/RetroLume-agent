import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const out=process.env.C01_BROWSER_OUTPUT,seed=JSON.parse(await fs.readFile(process.env.C01_BROWSER_SEED,'utf8'));
const context=await chromium.launchPersistentContext(path.join(out,'chrome-profile'),{headless:true,viewport:{width:1440,height:1100},serviceWorkers:'block'});
const page=context.pages()[0]??await context.newPage(),network=[],errors=[],posts=new Map();
page.on('request',r=>{let key=null,action=null;if(r.method()==='POST'&&r.url().includes('/interview/commands')){const v=JSON.parse(r.postData()??'{}');key=v.business_key;action=v.action;posts.set(key,(posts.get(key)??0)+1);}network.push({kind:'request',at:Date.now(),url:r.url(),method:r.method(),key,action});});
page.on('response',r=>network.push({kind:'response',at:Date.now(),url:r.url(),status:r.status()}));page.on('pageerror',e=>errors.push(e.message));
const area=()=>page.locator('[aria-label="文字模拟面试工作区"]');
const button=name=>area().getByRole('button',{name,exact:true});
const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?`[${v.map(canonical).join(',')}]`:`{${Object.keys(v).sort().map(k=>`${JSON.stringify(k)}:${canonical(v[k])}`).join(',')}}`;
const api=async(method,url,body)=>{
  const r=await page.evaluate(async({method,url,body})=>{const s=await (await fetch('/api/session',{credentials:'omit'})).json();const r=await fetch(url,{method,credentials:'omit',headers:{'X-RetroLume-Session':s.token,...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})});return {status:r.status,body:await r.json()};},{method,url,body});
  assert.ok([200,201,202].includes(r.status),JSON.stringify(r));return r.body;
};
const view=aid=>api('GET',`/api/activities/${aid}/interview/workspace`);
const select=async aid=>{
  for(let n=0;n<8&&!await page.locator(`[data-activity-id="${aid}"]`).count();n++){await page.getByRole('button',{name:'加载更多',exact:true}).click();await page.waitForTimeout(100);}
  await page.locator(`[data-activity-id="${aid}"]`).click();await page.locator(`[data-interview-activity-id="${aid}"]`).waitFor();await page.getByLabel('面试目标',{exact:true}).waitFor();
};
const store=async(aid,command,hash=null)=>{
  const owner=await page.evaluate(()=>sessionStorage.getItem('retrolume.teaching-editor-owner.v1'));assert.ok(owner);
  const {business_key:_,...body}=command;const text=canonical({...body,activity_id:aid});
  const actual=hash??await page.evaluate(async text=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(b=>b.toString(16).padStart(2,'0')).join(''),text);
  await page.evaluate(async({aid,command,hash,owner})=>{
    const draft={key:command.business_key,activity_id:aid,owner,hash,command};
    const db=await new Promise((resolve,reject)=>{const r=indexedDB.open('retrolume-interview-drafts',1);r.onupgradeneeded=()=>r.result.createObjectStore('drafts',{keyPath:'key'});r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
    await new Promise((resolve,reject)=>{const tx=db.transaction('drafts','readwrite');tx.objectStore('drafts').put(draft);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);});db.close();
    const rows=JSON.parse(localStorage.getItem('retrolume.interview.intents.v1')??'[]').filter(x=>x.key!==command.business_key);
    rows.push({key:command.business_key,activity_id:aid,owner,hash,action:command.action,head_revision:command.expected_head_revision,goal_version:command.expected_goal_version,scope_revision:command.expected_scope_revision,state:'saved_not_confirmed'});localStorage.setItem('retrolume.interview.intents.v1',JSON.stringify(rows));
  },{aid,command,hash:actual,owner});return {owner,hash:actual,text,key:command.business_key};
};
const original=key=>area().locator(`[data-interview-intent-key="${key}"]`);
const explicitGoal=async(aid,target)=>{
  const v=await view(aid);return api('POST',`/api/activities/${aid}/interview/commands`,{schema:'interview.command.v1',business_key:crypto.randomUUID(),action:'goal',expected_head_revision:v.head.revision,expected_goal_version:v.head.goal_version,expected_scope_revision:v.head.scope_revision,body:{goal:{target,focus:null,clarifications:[],material_roles:[{source_id:seed.materials[seed.technicalTitle]?.id??Object.values(seed.materials).find(x=>x.title===seed.technicalTitle).id,role:'reference'}]}}});
};

try{
  await context.route('**/*',async route=>{if(!route.request().url().startsWith('http://127.0.0.1:18106/'))return route.abort();return route.continue();});
  await page.goto('http://127.0.0.1:18106');await page.getByRole('button',{name:'模拟面试',exact:true}).click();await select(seed.technical);
  await button('开始提问').click();await page.getByLabel('面试回答',{exact:true}).waitFor();await page.getByLabel('面试回答',{exact:true}).fill(seed.Tanswer);
  await button('保存回答（不调用模型）').click();await button('获取必要追问或反馈').waitFor();const firstAnswer=(await view(seed.technical)).head.current_answer_id;
  await button('获取必要追问或反馈').click();await button('继续下一题（显式调用）').waitFor({timeout:60000});const firstFeedback=(await view(seed.technical)).head.current_feedback_id;
  await button('继续下一题（显式调用）').click();await page.getByLabel('面试回答',{exact:true}).waitFor();const successor=(await view(seed.technical)).head.current_question_id;
  await area().locator(`[data-interview-record-id="${firstAnswer}"]`).getByRole('button',{name:'只读查看该版本',exact:true}).click();
  await page.getByLabel('历史回答修订正文',{exact:true}).fill(seed.Tanswer+' 这是UI显式另存的早期回答v2。');await button('另存历史回答修订').click();await button('获取必要追问或反馈').waitFor();
  let v=await view(seed.technical);assert.equal(v.head.round_index,1);assert.notEqual(v.head.current_answer_id,firstAnswer);
  const oldAnswer=await api('GET',`/api/activities/${seed.technical}/interview/records/${firstAnswer}`),oldFeedback=await api('GET',`/api/activities/${seed.technical}/interview/records/${firstFeedback}`),oldSuccessor=await api('GET',`/api/activities/${seed.technical}/interview/records/${successor}`);
  assert.ok(oldAnswer.body);assert.equal(oldAnswer.record.can_correct_answer,false);assert.equal(oldFeedback.body,null);assert.equal(oldSuccessor.body,null);
  await button('获取必要追问或反馈').click();await button('继续下一题（显式调用）').waitFor({timeout:60000});
  await page.screenshot({path:path.join(out,'historical-answer-corrected-real-feedback.png'),fullPage:true});
  await button('结束本场次').click();await page.getByText('本场次已结束，只读历史',{exact:true}).waitFor();v=await view(seed.technical);assert.equal(v.budget.requests_reserved,4);
  // Actual accepted/unclaimed SQL intent, client draft prepared by this declared fixture.
  await select(seed.accepted);await store(seed.accepted,seed.acceptedCommand,seed.acceptedReceipt.request_sha256);await button('只读刷新／恢复场次').click();
  await original(seed.acceptedCommand.business_key).getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).click();
  await page.getByLabel('面试回答',{exact:true}).waitFor({timeout:60000});const accepted=await view(seed.accepted);assert.equal(accepted.budget.requests_reserved,1);
  const acceptedBefore=posts.get(seed.acceptedCommand.business_key);await original(seed.acceptedCommand.business_key).getByRole('button',{name:'只读核对原提交',exact:true}).click();await area().getByRole('status').filter({hasText:'原提交状态：committed'}).waitFor();assert.equal(posts.get(seed.acceptedCommand.business_key),acceptedBefore);
  // Real native model COMMIT then browser route loses the original response.
  await select(seed.lost);let dropped=null;
  await page.route(`**/api/activities/${seed.lost}/interview/commands`,async route=>{
    const body=JSON.parse(route.request().postData());if(body.action==='ask'&&!dropped){const response=await route.fetch({maxRetries:0});const actual=await response.json();assert.equal(actual.status,'committed');dropped={key:body.business_key,receipt:actual};await route.abort('failed');}else await route.continue();
  });
  await button('开始提问').click();await area().getByRole('alert').waitFor({timeout:60000});assert.ok(dropped);const afterDrop=await view(seed.lost);assert.equal(afterDrop.budget.requests_reserved,1);
  await page.unroute(`**/api/activities/${seed.lost}/interview/commands`);
  const postBeforeReload=posts.get(dropped.key);await page.reload();await page.getByRole('button',{name:'模拟面试',exact:true}).click();await select(seed.lost);assert.equal(posts.get(dropped.key),postBeforeReload);
  await original(dropped.key).getByRole('button',{name:'只读核对原提交',exact:true}).click();await area().getByRole('status').filter({hasText:'原提交状态：committed'}).waitFor();assert.equal(posts.get(dropped.key),postBeforeReload);
  // Hold actual summary-lock completion after owner check. Same-activity new view
  // must not revive old notice; this key's durable receipt may still be confirmed.
  await page.evaluate(()=>{window.c01OriginalLock=navigator.locks.request.bind(navigator.locks);window.c01LockDone=false;navigator.locks.request=async function(name,...args){const r=await window.c01OriginalLock(name,...args);if(name==='retrolume.interview.intents.v1'&&window.c01HoldOwner){window.c01LockDone=true;await new Promise(resolve=>window.c01ReleaseOwner=resolve);}return r;};window.c01HoldOwner=true;});
  await original(dropped.key).getByRole('button',{name:'只读核对原提交',exact:true}).click();await page.waitForFunction(()=>window.c01LockDone);
  await explicitGoal(seed.lost,'余额算法新视图目标');await button('只读刷新／恢复场次').click();await page.waitForFunction(()=>document.querySelector('[aria-label="面试目标"]')?.value==='余额算法新视图目标');
  await page.evaluate(()=>{window.c01HoldOwner=false;window.c01ReleaseOwner();navigator.locks.request=window.c01OriginalLock;});await page.waitForTimeout(150);
  assert.equal(posts.get(dropped.key),postBeforeReload);assert.equal(await area().getByRole('status').filter({hasText:'原提交状态：'}).count(),0);
  // Unsent exact original key. Hold the completed real digest, then new view.
  const current=await view(seed.lost);const guardCmd={schema:'interview.command.v1',business_key:crypto.randomUUID(),action:'goal',expected_head_revision:current.head.revision,expected_goal_version:current.head.goal_version,expected_scope_revision:current.head.scope_revision,body:{goal:{target:'余额算法旧待确认目标',focus:null,clarifications:[],material_roles:[{source_id:Object.values(seed.materials).find(x=>x.title===seed.technicalTitle).id,role:'reference'}]}}};
  const guard=await store(seed.lost,guardCmd);await button('只读刷新／恢复场次').click();
  await page.evaluate(()=>{window.c01OriginalDigest=crypto.subtle.digest.bind(crypto.subtle);window.c01HashDone=false;crypto.subtle.digest=async function(algorithm,data){const value=await window.c01OriginalDigest(algorithm,data);if(window.c01HoldHash&&new TextDecoder().decode(data).includes('旧待确认目标')){window.c01HashDone=true;await new Promise(resolve=>window.c01ReleaseHash=resolve);}return value;};window.c01HoldHash=true;});
  await original(guard.key).getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).click();await page.waitForFunction(()=>window.c01HashDone);
  await explicitGoal(seed.lost,'余额算法再次变更的新视图');await button('只读刷新／恢复场次').click();await page.waitForFunction(()=>document.querySelector('[aria-label="面试目标"]')?.value==='余额算法再次变更的新视图');
  await page.evaluate(()=>{window.c01HoldHash=false;window.c01ReleaseHash();crypto.subtle.digest=window.c01OriginalDigest;});await page.waitForTimeout(150);assert.equal(posts.get(guard.key)??0,0);
  const stored=await page.evaluate(key=>JSON.parse(localStorage.getItem('retrolume.interview.intents.v1')).find(x=>x.key===key),guard.key);assert.equal(stored.hash,guard.hash);
  await page.screenshot({path:path.join(out,'same-activity-view-change-no-old-reconcile.png'),fullPage:true});
  assert.deepEqual(errors,[]);
  await fs.writeFile(path.join(out,'browser-result.json'),JSON.stringify({passed:true,technical:seed.technical,historyCorrection:{firstAnswer,oldAnswer,oldFeedback,oldSuccessor,final:v},acceptedOriginalExplicit:{key:seed.acceptedCommand.business_key,requests:1,GETnoPOST:true},
    actualLostModelResponse:dropped,refreshOnlyGET:true,normalReceiptConfirmation:true,sameActivityOwnerCheckThenChangedView:{oldNoticeRevived:false,oldPOST:0},sameActivityHashDoneThenChangedView:{key:guard.key,oldPOST:0,originalSummaryPreserved:true},finalLost:await view(seed.lost),errors},null,2));
  await fs.writeFile(path.join(out,'network.json'),JSON.stringify(network,null,2));console.log('C01 real browser historical revision, receipt recovery and same-view guards passed');
}catch(error){await fs.writeFile(path.join(out,'failure-dom.html'),await page.content());await page.screenshot({path:path.join(out,'failure.png'),fullPage:true}).catch(()=>{});await fs.writeFile(path.join(out,'network.json'),JSON.stringify(network,null,2));throw error;}
finally{await context.close();}
