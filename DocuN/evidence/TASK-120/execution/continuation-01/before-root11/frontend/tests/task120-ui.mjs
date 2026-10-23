// Final dist, actual loopback API/PG/SUP. No HTTP business response stubs.
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';

assert(process.env.RETROLUME_TASK120_UI_SPEC,'owned TASK120 root required');
const spec=JSON.parse(fs.readFileSync(process.env.RETROLUME_TASK120_UI_SPEC,'utf8'));
assert.equal(spec.permit,'TASK-120-Q-PREP-IMPLEMENTATION-20261018');
const sha=x=>createHash('sha256').update(x).digest('hex');
const proof={execution_class:'TESTONLY',status:'RUNNING',real_PG:true,real_Windows_SUP:true,external_attempts:[],assets:[],requests:[],actions:[],cases:[],errors:[]};
const save=()=>fs.writeFileSync(spec.proof,JSON.stringify(proof,null,2));
const observations=new Set();
const observe=f=>{const p=Promise.resolve().then(f).catch(e=>proof.errors.push(String(e))).finally(()=>observations.delete(p));observations.add(p);};
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(f,seconds=15){const end=Date.now()+seconds*1000;while(!f()){assert(Date.now()<end,'bounded observation timeout');await sleep(25);}}
let ordinal=0,context;
async function operator(aid,key){
 ordinal++;const message={ordinal,kind:'approve',activity_id:aid,business_key:key};
 fs.writeFileSync(path.join(spec.handshake,`request-${ordinal}.json`),JSON.stringify(message));
 const reply=path.join(spec.handshake,`reply-${ordinal}.json`);await until(()=>fs.existsSync(reply));
 assert.equal(JSON.parse(fs.readFileSync(reply,'utf8')).status,'APPROVED');
 proof.actions.push({at:Date.now(),action:'actual_local_operator_approved',activity_id:aid,business_key:key});save();
}
const posts=(aid,domain)=>proof.requests.filter(x=>x.method==='POST'&&x.path===`/api/activities/${aid}/${domain}/commands`);
async function navigate(page,aid,interview=false){
 await page.getByRole('navigation').getByRole('button',{name:interview?/模拟面试/:/学习活动/}).click();
 await page.locator(`[data-activity-id="${aid}"]`).click();
 const area=page.locator(interview?'.interview-workspace':'section.ws-teaching');await area.waitFor();
 if(!interview)await area.getByLabel('明确使用词项降级（不算混合检索通过）',{exact:true}).check();
 return area;
}
async function command(page,aid,domain,action,click){
 const response=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname===`/api/activities/${aid}/${domain}/commands`&&r.request().postDataJSON().action===action);
 proof.actions.push({at:Date.now(),action:'explicit_UI_'+action,activity_id:aid,domain});await click();
 const actual=await response;assert(actual.ok(),`actual ${domain} HTTP ${actual.status()}`);return {body:actual.request().postDataJSON(),receipt:await actual.json()};
}
try{
 assert(fs.existsSync(chromium.executablePath()),'cached browser required; no download');
 context=await chromium.launchPersistentContext(spec.profile,{headless:true,viewport:{width:1440,height:1050},serviceWorkers:'block',args:['--disable-background-networking']});
 await context.route('**/*',async route=>{
  const url=new URL(route.request().url());
  if(url.origin!==spec.origin){proof.external_attempts.push({origin:url.origin});await route.abort();return;}
  await route.continue();
 });
 context.on('request',request=>{const url=new URL(request.url());proof.requests.push({at:Date.now(),method:request.method(),path:url.pathname,body_sha256:request.postData()?sha(request.postData()):null,
  ...(request.method()==='POST'&&url.pathname.endsWith('/commands')?{body:request.postDataJSON()}: {})});});
 context.on('response',response=>{if(new URL(response.url()).pathname.startsWith('/assets/'))observe(async()=>{
  const rel=new URL(response.url()).pathname.slice(1),bytes=await response.body(),file=path.join(spec.project,'frontend/dist',rel);
  assert.equal(sha(bytes),sha(fs.readFileSync(file)));proof.assets.push({path:rel,response_sha256:sha(bytes),file_sha256:sha(fs.readFileSync(file))});});});
 const page=context.pages()[0]??await context.newPage();page.setDefaultTimeout(18000);
 page.on('pageerror',e=>proof.errors.push(String(e)));
 await page.goto(spec.origin,{waitUntil:'networkidle'});
 const [a1,a2,a3]=spec.activities;
 let area=await navigate(page,a1);
 const first=await command(page,a1,'teaching','plan',()=>area.getByRole('button',{name:'生成/重订路径（1 次模型）',exact:true}).click());
 assert.equal(first.receipt.outbound_approval.state,'pending');assert.equal(posts(a1,'teaching').length,1);
 await page.reload({waitUntil:'networkidle'});area=await navigate(page,a1);await sleep(250);
 assert.equal(posts(a1,'teaching').length,1,'reload and navigation only GET');
 await operator(a1,first.body.business_key);
 let intent=area.locator('.ws-intent').filter({hasText:'路径'});
 if(await intent.count()!==1)intent=area.locator('[data-teaching-intent-key]');
 // The exact existing intent row, whose explicit recovery button appears only
 // after the real command GET reports approved and unclaimed.
 const readonly=area.getByRole('button',{name:'核对（只读）',exact:true});await readonly.last().click();
 const resume=area.getByRole('button',{name:'明确恢复原意图（同键）',exact:true});await resume.waitFor();
 let hit=false,release;const barrier=new Promise(resolve=>release=resolve);
 const routePattern=`**/api/activities/${a1}/teaching/commands/${first.body.business_key}`;
 await page.route(routePattern,async route=>{const actual=await route.fetch();hit=true;await barrier;await route.fulfill({response:actual});});
 await resume.click();await until(()=>hit);await page.locator(`[data-activity-id="${a3}"]`).click();release();await sleep(400);await page.unroute(routePattern);
 assert.equal(posts(a1,'teaching').length,1,'late approved GET after activity switch must not POST');
 const drafts=await page.evaluate(async()=>{
  const result=[];for(const item of await indexedDB.databases())if(item.name?.includes('teaching')&&!item.name.includes('retrieval')){
   const db=await new Promise((resolve,reject)=>{const r=indexedDB.open(item.name);r.onsuccess=()=>resolve(r.result);r.onerror=reject;});
   for(const store of db.objectStoreNames)result.push(...await new Promise((resolve,reject)=>{const r=db.transaction(store).objectStore(store).getAll();r.onsuccess=()=>resolve(r.result);r.onerror=reject;}));db.close();
  }return result;
 });
 assert(drafts.some(x=>typeof x.content==='string'&&JSON.parse(x.content).action==='plan'),'full original draft retained');
 proof.cases.push({name:'teaching-reopen-and-late-approved-GET',status:'PASS',business_key:first.body.business_key,posts_before_explicit_resume:1,draft_retained:true});
 area=await navigate(page,a1);await area.getByRole('button',{name:'核对（只读）',exact:true}).last().click();
 const continued=await command(page,a1,'teaching','plan',()=>area.getByRole('button',{name:'明确恢复原意图（同键）',exact:true}).click());
 assert.equal(continued.body.business_key,first.body.business_key);assert.equal(continued.receipt.status,'committed');
 proof.cases.push({name:'teaching-approved-explicit-same-key',status:'PASS',business_key:first.body.business_key});await page.screenshot({path:spec.screenshotTeaching,fullPage:true});save();
 area=await navigate(page,a2,true);
 await area.getByLabel('面试目标',{exact:true}).fill(spec.interview_goal);
 await command(page,a2,'interview','goal',()=>area.getByRole('button',{name:'保存修正目标（另存版本）',exact:true}).click());
 const panel=area.locator('section[aria-label="资料检索与恢复"]');
 const queryResponse=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname===`/api/activities/${a2}/retrieval/commands`&&r.request().postDataJSON().action==='query');
 proof.actions.push({at:Date.now(),action:'explicit_UI_interview_query',activity_id:a2});
 await area.getByRole('button',{name:'开始提问',exact:true}).click();
 const query=await queryResponse;assert(query.ok());const queryBody=query.request().postDataJSON(),queryReceipt=await query.json();assert(queryReceipt.outbound_approval);
 await operator(a2,queryBody.business_key);
 await panel.getByRole('button',{name:'按原键只读核对',exact:true}).last().click();
 const queryContinued=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname===`/api/activities/${a2}/retrieval/commands`&&r.request().postDataJSON().business_key===queryBody.business_key);
 await panel.getByRole('button',{name:'明确继续已批准的原检索请求',exact:true}).last().click();assert.equal((await (await queryContinued).json()).terminal_disposition,'received');
 const asked=await command(page,a2,'interview','ask',()=>panel.getByRole('button',{name:'明确继续尚未发送的原动作',exact:true}).last().click());
 assert.equal(asked.receipt.outbound_approval.state,'pending');
 const before=posts(a2,'interview').length;
 await page.reload({waitUntil:'networkidle'});area=await navigate(page,a2,true);await sleep(250);assert.equal(posts(a2,'interview').length,before);
 await operator(a2,asked.body.business_key);
 await area.getByRole('button',{name:'只读核对原提交',exact:true}).last().click();
 const resumed=await command(page,a2,'interview','ask',()=>area.getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).last().click());
 assert.equal(resumed.body.business_key,asked.body.business_key);assert.equal(resumed.receipt.status,'committed');
 proof.cases.push({name:'interview-wait-reopen-approve-explicit-same-key',status:'PASS',business_key:asked.body.business_key});
 await page.screenshot({path:spec.screenshotInterview,fullPage:true});
 await Promise.allSettled([...observations]);assert(proof.assets.some(x=>x.path.endsWith('.js'))&&proof.assets.some(x=>x.path.endsWith('.css')));
 assert.equal(proof.external_attempts.length,0);assert.equal(proof.errors.length,0);proof.status='PASS';
}catch(error){proof.status='FAIL';proof.failure={name:error.name,message:String(error.message),stack:error.stack};process.exitCode=1;}
finally{if(context)await context.close();await Promise.allSettled([...observations]);proof.context_closed=true;save();}
