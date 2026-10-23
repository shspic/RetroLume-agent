// Normal final-dist UI, original PG/API/SUP. Business responses are never faked.
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash,randomUUID} from 'node:crypto';
import assert from 'node:assert/strict';
assert(process.env.RETROLUME_TASK120_UI_SPEC,'owned finite TASK120 root required');
const spec=JSON.parse(fs.readFileSync(process.env.RETROLUME_TASK120_UI_SPEC,'utf8'));
assert.equal(spec.permit,'TASK-120-Q-PREP-IMPLEMENTATION-20261018');
assert(['teaching','interview','legacy_html','fences'].includes(spec.mode));
const sha=x=>createHash('sha256').update(x).digest('hex');
const proof={execution_class:'TESTONLY',mode:spec.mode,status:'RUNNING',real_PG:true,real_Windows_SUP:true,
 fixture_sha256:sha(fs.readFileSync(fileURLToPath(import.meta.url))),assets:[],requests:[],actions:[],cases:[],external_attempts:[],errors:[]};
const save=()=>fs.writeFileSync(spec.proof,JSON.stringify(proof,null,2));
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(f,seconds=12){const end=Date.now()+seconds*1000;while(!f()){assert(Date.now()<end,'bounded observation timeout');await sleep(25);}}
let context,ordinal=0;
const observations=new Set();
const observe=f=>{const p=Promise.resolve().then(f).catch(e=>proof.errors.push(String(e))).finally(()=>observations.delete(p));observations.add(p);};
const posts=p=>proof.requests.filter(x=>x.method==='POST'&&x.path===p);
async function operator(aid,key){
 ordinal++;fs.writeFileSync(path.join(spec.handshake,`request-${ordinal}.json`),JSON.stringify({ordinal,kind:'approve',activity_id:aid,business_key:key}));
 const reply=path.join(spec.handshake,`reply-${ordinal}.json`);await until(()=>fs.existsSync(reply));assert.equal(JSON.parse(fs.readFileSync(reply)).status,'APPROVED');
 proof.actions.push({at:Date.now(),action:'actual_local_operator_approved',activity_id:aid,business_key:key});save();
}
async function action(page,p,label,click){
 const waiting=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname===p);
 proof.actions.push({at:Date.now(),action:label});await click();const response=await waiting;assert(response.ok(),`${label}: HTTP ${response.status()}`);
 return {body:response.request().postDataJSON(),receipt:await response.json()};
}
async function select(page,aid,interview=false){
 await page.getByRole('navigation').getByRole('button',{name:interview?/模拟面试/:/学习活动/}).click();
 await page.locator(`[data-activity-id="${aid}"]`).click();
 const area=page.locator(interview?'.interview-workspace':'section.ws-teaching');await area.waitFor();return area;
}
async function reopenLegacy(page){
 await select(page,spec.activities[2]);
 const result=page.locator('section[aria-label="学习成果"]');
 if(!await result.count())await page.locator('button.ws-op').filter({hasText:spec.legacy_operation}).first().click();
 await result.waitFor();return result;
}
async function late(page,pattern,click,mutate,postPath){
 const before=posts(postPath).length;let hit=false,release;const barrier=new Promise(resolve=>release=resolve);
 await page.route(pattern,async route=>{const response=await route.fetch();hit=true;await barrier;await route.fulfill({response});});
 try{await click();await until(()=>hit);await mutate();release();await sleep(300);assert.equal(posts(postPath).length,before,'late approved GET must not POST');}
 finally{release();await page.unroute(pattern);}
}
try{
 assert(fs.existsSync(chromium.executablePath()),'cached Chromium only');
 context=await chromium.launchPersistentContext(spec.profile,{headless:true,viewport:{width:1440,height:1050},serviceWorkers:'block',args:['--disable-background-networking']});
 await context.route('**/*',async route=>{const url=new URL(route.request().url());if(url.origin!==spec.origin){proof.external_attempts.push(url.origin);await route.abort();return;}await route.continue();});
 context.on('request',request=>{const url=new URL(request.url());proof.requests.push({at:Date.now(),method:request.method(),path:url.pathname,
  ...(request.method()==='POST'?{body:request.postDataJSON()}: {})});});
 context.on('response',response=>{if(new URL(response.url()).pathname.startsWith('/assets/'))observe(async()=>{
  const rel=new URL(response.url()).pathname.slice(1),bytes=await response.body();assert.equal(sha(bytes),sha(fs.readFileSync(path.join(spec.project,'frontend/dist',rel))));
  proof.assets.push({path:rel,response_sha256:sha(bytes),file_sha256:sha(fs.readFileSync(path.join(spec.project,'frontend/dist',rel)))});
 });});
 const page=context.pages()[0]??await context.newPage();page.setDefaultTimeout(13000);page.on('pageerror',e=>proof.errors.push(String(e)));
 await page.goto(spec.origin,{waitUntil:'networkidle'});
 const [a1,a2,a3]=spec.activities;
 if(spec.mode==='teaching'){
  let area=await select(page,a3);const domain=`/api/activities/${a3}/teaching/commands`,retrieval=`/api/activities/${a3}/retrieval/commands`;
  // A3 has a real unused local-goal slot after the completed normal chain.
  // Both local actions are frozen texts; only the final numeric goal is sent.
  for(const [name,text] of [['concept',spec.concept_goal],['numeric',spec.numeric_goal]]){
   await area.getByLabel('学习目标（零费保存，不调用模型）',{exact:true}).fill(text);
   const goal=await action(page,domain,`explicit_A3_local_goal_${name}`,()=>area.getByRole('button',{name:'保存目标（不调用模型）',exact:true}).click());
   assert.equal(goal.receipt.status,'committed');
  }
  const query=await action(page,retrieval,'explicit_teaching_query',()=>area.getByRole('button',{name:'生成/重订路径（1 次模型）',exact:true}).click());
  assert(query.receipt.outbound_approval&&!query.receipt.outbound_approval.can_continue);
  let before=posts(retrieval).length;await page.reload({waitUntil:'networkidle'});area=await select(page,a3);await sleep(250);assert.equal(posts(retrieval).length,before);
  await operator(a3,query.body.business_key);
  let panel=area.locator('section[aria-label="资料检索与恢复"]');await panel.getByRole('button',{name:'按原键只读核对',exact:true}).last().click();
  const received=await action(page,retrieval,'explicit_original_teaching_query_continue',()=>panel.getByRole('button',{name:'明确继续已批准的原检索请求',exact:true}).last().click());
  assert.equal(received.body.business_key,query.body.business_key);assert.equal(received.receipt.terminal_disposition,'received');
  const model=await action(page,domain,'explicit_original_teaching_model_prepare',()=>panel.getByRole('button',{name:'明确继续尚未发送的原动作',exact:true}).last().click());
  assert.equal(model.receipt.outbound_approval.state,'pending');before=posts(domain).length;
  await page.reload({waitUntil:'networkidle'});area=await select(page,a3);await sleep(250);assert.equal(posts(domain).length,before);
  await operator(a3,model.body.business_key);await area.getByRole('button',{name:'核对（只读）',exact:true}).last().click();
  const resume=()=>area.getByRole('button',{name:'明确恢复原意图（同键）',exact:true}).last().click();
  const owner=await page.evaluate(()=>Object.entries(sessionStorage).find(([k])=>k.includes('teaching-editor-owner')));assert(owner);
  await late(page,`**${domain}/${model.body.business_key}`,resume,()=>page.evaluate(([key])=>sessionStorage.setItem(key,crypto.randomUUID()),owner),domain);
  await page.evaluate(([key,value])=>sessionStorage.setItem(key,value),owner);
  await area.getByRole('button',{name:'核对（只读）',exact:true}).last().click();
  await late(page,`**${domain}/${model.body.business_key}`,resume,()=>page.getByRole('navigation').getByRole('button',{name:/模拟面试/}).click(),domain);
  area=await select(page,a3);await area.getByRole('button',{name:'核对（只读）',exact:true}).last().click();
  const result=await action(page,domain,'explicit_original_teaching_model_COMMIT',resume);
  assert.equal(result.body.business_key,model.body.business_key);assert.equal(result.receipt.status,'committed');
  proof.cases.push({name:'A3-teaching-query-model-wait-reopen-owner-view-late-original-COMMIT',status:'PASS',query_key:query.body.business_key,model_key:model.body.business_key});
  await page.screenshot({path:spec.screenshotTeaching,fullPage:true});
 }else if(spec.mode==='interview'){
  let area=await select(page,a2,true);const domain=`/api/activities/${a2}/interview/commands`,retrieval=`/api/activities/${a2}/retrieval/commands`;
  await area.getByLabel('面试目标',{exact:true}).fill(spec.interview_goal);
  await action(page,domain,'explicit_interview_goal',()=>area.getByRole('button',{name:'保存修正目标（另存版本）',exact:true}).click());
  const query=await action(page,retrieval,'explicit_interview_query',()=>area.getByRole('button',{name:'开始提问',exact:true}).click());
  assert(query.receipt.outbound_approval&&!query.receipt.outbound_approval.can_continue);
  const queryPosts=posts(retrieval).length;await page.reload({waitUntil:'networkidle'});area=await select(page,a2,true);await sleep(250);assert.equal(posts(retrieval).length,queryPosts);
  await operator(a2,query.body.business_key);
  let panel=area.locator('section[aria-label="资料检索与恢复"]');
  await panel.getByRole('button',{name:'按原键只读核对',exact:true}).last().click();
  const continuedQuery=await action(page,retrieval,'explicit_original_query_continue',()=>panel.getByRole('button',{name:'明确继续已批准的原检索请求',exact:true}).last().click());
  assert.equal(continuedQuery.body.business_key,query.body.business_key);assert.equal(continuedQuery.receipt.terminal_disposition,'received');
  const model=await action(page,domain,'explicit_original_domain_continue',()=>panel.getByRole('button',{name:'明确继续尚未发送的原动作',exact:true}).last().click());
  assert.equal(model.receipt.outbound_approval.state,'pending');const count=posts(domain).length;
  await page.reload({waitUntil:'networkidle'});area=await select(page,a2,true);await sleep(250);assert.equal(posts(domain).length,count);
  await operator(a2,model.body.business_key);
  await area.getByRole('button',{name:'只读核对原提交',exact:true}).last().click();
  const resume=()=>area.getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).last().click();
  const owner=await page.evaluate(()=>Object.entries(sessionStorage).find(([k])=>k.includes('teaching-editor-owner')));
  assert(owner,'real interview editor owner');
  await late(page,`**${domain}/${model.body.business_key}`,resume,()=>page.evaluate(([key])=>sessionStorage.setItem(key,crypto.randomUUID()),owner),domain);
  await page.evaluate(([key,value])=>sessionStorage.setItem(key,value),owner);
  await area.getByRole('button',{name:'只读核对原提交',exact:true}).last().click();
  await late(page,`**${domain}/${model.body.business_key}`,resume,()=>page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click(),domain);
  area=await select(page,a2,true);await area.getByRole('button',{name:'只读核对原提交',exact:true}).last().click();
  const result=await action(page,domain,'explicit_approved_model_same_key',resume);
  assert.equal(result.body.business_key,model.body.business_key);assert.equal(result.receipt.status,'committed');
  proof.cases.push({name:'interview-query-and-model-wait-GET-reopen-owner-view-late-explicit-original-commit',status:'PASS',query_key:query.body.business_key,model_key:model.body.business_key});
  await page.screenshot({path:spec.screenshotInterview,fullPage:true});
 }else if(spec.mode==='fences'){
  const domain=`/api/activities/${a2}/interview/commands`,retrieval=`/api/activities/${a2}/retrieval/commands`;
  for(const fence of ['head','scope']){
   await page.reload({waitUntil:'networkidle'});let area=await select(page,a2,true);
   await area.getByLabel('面试目标',{exact:true}).fill(spec.interview_goal);
   await action(page,domain,`fence_${fence}_new_goal`,()=>area.getByRole('button',{name:'保存修正目标（另存版本）',exact:true}).click());
   const query=await action(page,retrieval,`fence_${fence}_query_prepare`,()=>area.getByRole('button',{name:'开始提问',exact:true}).click());
   assert(query.receipt.outbound_approval);await operator(a2,query.body.business_key);
   let panel=area.locator('section[aria-label="资料检索与恢复"]');
   await panel.getByRole('button',{name:'按原键只读核对',exact:true}).last().click();
   await action(page,retrieval,`fence_${fence}_query_continue`,()=>panel.getByRole('button',{name:'明确继续已批准的原检索请求',exact:true}).last().click());
   const model=await action(page,domain,`fence_${fence}_model_prepare`,()=>panel.getByRole('button',{name:'明确继续尚未发送的原动作',exact:true}).last().click());
   await operator(a2,model.body.business_key);
   const intent=area.locator(`[data-interview-intent-key="${model.body.business_key}"]`);
   await intent.getByRole('button',{name:'只读核对原提交',exact:true}).click();
   const other=await context.newPage();other.setDefaultTimeout(13000);await other.goto(spec.origin,{waitUntil:'networkidle'});
   const second=await select(other,a2,true);let hit=false,release;const barrier=new Promise(resolve=>release=resolve);
   const pattern=`**${domain}/${model.body.business_key}`;
   await page.route(pattern,async route=>{const response=await route.fetch();hit=true;await barrier;await route.fulfill({response});});
   const oldKeyPosts=()=>posts(domain).filter(x=>x.body?.business_key===model.body.business_key).length;
   const before=oldKeyPosts();
   try{
    await intent.getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).click();await until(()=>hit);
    if(fence==='head'){
     await second.getByLabel('面试目标',{exact:true}).fill(spec.interview_goal);
     await action(other,domain,'concurrent_actual_local_goal',()=>second.getByRole('button',{name:'保存修正目标（另存版本）',exact:true}).click());
    }else{
     await second.getByRole('button',{name:'读取当前资料，明确更新范围',exact:true}).click();
     await second.locator('label').filter({hasText:spec.scope_remove_title}).filter({has:other.locator('input[type="checkbox"]')}).getByRole('checkbox').uncheck();
     await action(other,domain,'concurrent_actual_scope_binding',()=>second.getByRole('button',{name:'确认新的资料范围',exact:true}).click());
    }
    const refresh=page.waitForResponse(r=>r.request().method()==='GET'&&new URL(r.url()).pathname===`/api/activities/${a2}/interview/workspace`);
    await area.getByRole('button',{name:'只读刷新／恢复场次',exact:true}).click();await refresh;await sleep(300);release();await sleep(350);
    assert.equal(oldKeyPosts(),before,'late original model GET must not POST after observed head/scope change');
    proof.cases.push({name:`actual-${fence}-mutation-during-approved-GET-no-original-model-POST`,status:'PASS',business_key:model.body.business_key});
   }finally{release();await page.unroute(pattern);await other.close();}
  }
  proof.not_run=['namespace-switch','DataContext-switch'];
 }else{
  assert(spec.legacy_operation,'actual committed legacy parent');
  let learning=await reopenLegacy(page);const follow=`/api/activities/${a3}/learning/followups`,html=`/api/activities/${a3}/html/commands`;
  await page.getByRole('button',{name:'从该学习成果续问…',exact:true}).click();await page.getByLabel('续问内容',{exact:true}).fill(spec.numeric_question);
  const first=await action(page,follow,'explicit_legacy_followup',()=>page.getByRole('button',{name:'发出并等待',exact:true}).click());
  assert(first.receipt.outbound_approval&&!first.receipt.outbound_approval.can_continue);
  let before=posts(follow).length;await page.reload({waitUntil:'networkidle'});await select(page,a3);await sleep(250);assert.equal(posts(follow).length,before);
  await operator(a3,first.body.business_key);
  let intent=page.locator('.ws-intent').filter({hasText:'学习续问'});await intent.getByRole('button',{name:'核对（只读）',exact:true}).click();
  const resume=()=>intent.getByRole('button',{name:'重新提交同一意图',exact:true}).click();
  await late(page,`**/api/activities/${a3}/learning/intents/${first.body.business_key}?*`,resume,()=>page.locator(`[data-activity-id="${a1}"]`).click(),follow);
  await select(page,a3);intent=page.locator('.ws-intent').filter({hasText:'学习续问'});
  const continued=await action(page,follow,'explicit_approved_legacy_original_key',resume);
  assert.equal(continued.body.business_key,first.body.business_key);assert.equal(continued.receipt.status,'committed_current');
  proof.cases.push({name:'legacy-followup-wait-reopen-GET-late-same-key',status:'PASS',business_key:first.body.business_key});
  learning=await reopenLegacy(page);await learning.getByRole('button',{name:'交互解释此答案段',exact:true}).first().click();
  let panel=learning.locator('section[aria-label="交互解释"]');await panel.getByLabel('交互解释难点',{exact:true}).fill(spec.numeric_goal);
  await panel.getByLabel('确认父成果、资料与一次模型调用额度',{exact:true}).check();
  const pending=await action(page,html,'explicit_HTML_description_generate',()=>panel.getByRole('button',{name:'确认生成交互解释',exact:true}).click());
  assert.equal(pending.receipt.outbound_approval.state,'pending');before=posts(html).length;
  await page.reload({waitUntil:'networkidle'});learning=await reopenLegacy(page);await learning.getByRole('button',{name:'交互解释此答案段',exact:true}).first().click();
  panel=learning.locator('section[aria-label="交互解释"]');await sleep(250);assert.equal(posts(html).length,before);
  await operator(a3,pending.body.business_key);await panel.getByRole('button',{name:'只读核对原键',exact:true}).last().click();
  const result=await action(page,html,'explicit_approved_original_HTML_generate',()=>panel.getByRole('button',{name:'明确继续已批准的原生成请求',exact:true}).click());
  assert.equal(result.body.business_key,pending.body.business_key);assert.equal(result.receipt.terminal_disposition,'succeeded');assert.equal(result.receipt.read_status,'current');
  assert.equal(proof.requests.filter(x=>x.method==='POST'&&/\/previews(?:\/|$)/.test(x.path)).length,0);
  proof.cases.push({name:'HTML-description-wait-reopen-GET-approved-same-key-preview-zero',status:'PASS',business_key:pending.body.business_key});
  await page.screenshot({path:spec.screenshotTeaching,fullPage:true});
 }
 await Promise.allSettled([...observations]);assert(proof.assets.some(x=>x.path.endsWith('.js'))&&proof.assets.some(x=>x.path.endsWith('.css')));
 assert.equal(proof.external_attempts.length,0);assert.equal(proof.errors.length,0);proof.status='PASS_FOR_LISTED_CHAINS';
}catch(error){proof.status='FAIL';proof.failure={name:error.name,message:String(error.message),stack:error.stack};process.exitCode=1;}
finally{if(context)await context.close();await Promise.allSettled([...observations]);proof.context_closed=true;save();}
