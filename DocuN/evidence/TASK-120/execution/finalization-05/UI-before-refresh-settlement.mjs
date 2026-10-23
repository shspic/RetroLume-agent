import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const spec=JSON.parse(fs.readFileSync(process.env.RETROLUME_TASK120_UI_SPEC,'utf8'));
const sha=x=>createHash('sha256').update(x).digest('hex');
const proof={status:'RUNNING',execution_class:'TESTONLY',real_PG:true,formal_bundle:true,cases:[],assets:[],requests:[],actions:[],errors:[]};
const save=()=>fs.writeFileSync(spec.proof,JSON.stringify(proof,null,2));
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(f,ms=14000){const end=Date.now()+ms;while(!f()){assert(Date.now()<end,'bounded observation timeout');await sleep(25);}}
let ordinal=0,context;
const observations=new Set(),approved=new Set(),counted=new Set();
const observe=f=>{const p=Promise.resolve().then(f).catch(e=>proof.errors.push(String(e))).finally(()=>observations.delete(p));observations.add(p);};
async function driver(kind,key){
 ordinal++;fs.writeFileSync(path.join(spec.handshake,`request-${ordinal}.json`),JSON.stringify({ordinal,kind,activity_id:spec.activity_id,business_key:key}));
 const file=path.join(spec.handshake,`reply-${ordinal}.json`);await until(()=>fs.existsSync(file));const got=JSON.parse(fs.readFileSync(file));
 assert.equal(got.status,kind==='approve'?'APPROVED':'COMPLETED');proof.actions.push({at:Date.now(),kind,business_key:key,reply:got});save();
 if(kind==='approve')approved.add(key);return got;
}
const domain=`/api/activities/${spec.activity_id}/interview/commands`,retrieval=`/api/activities/${spec.activity_id}/retrieval/commands`;
const posts=key=>proof.requests.filter(x=>x.method==='POST'&&x.path===domain&&x.body?.business_key===key).length;
async function action(page,route,name,click){
 proof.actions.push({at:Date.now(),name});save();
 const [response]=await Promise.all([page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname===route),click()]);
 assert(response.ok(),`${name}: ${response.status()}`);const got={body:response.request().postDataJSON(),receipt:await response.json()};save();return got;
}
async function storage(page){return await page.evaluate(()=>Object.fromEntries(Object.entries(localStorage).filter(([k])=>k.includes('retrolume.interview.intents')||k.includes('retrolume.retrieval'))));}
try{
 assert(fs.existsSync(chromium.executablePath()),'only cached Chromium');
 context=await chromium.launchPersistentContext(spec.profile,{headless:true,viewport:{width:1440,height:1050},serviceWorkers:'block',args:['--disable-background-networking']});
 await context.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url());if(url.origin!==spec.origin){proof.errors.push(`blocked external origin ${url.origin}`);await route.abort();return;}
  if(req.method()==='POST'){
   const key=req.postDataJSON()?.business_key;
   if(approved.has(key)&&!counted.has(key)){await driver('native_attempt',key);counted.add(key);}
  }
  await route.continue();
 });
 context.on('request',req=>{const u=new URL(req.url());proof.requests.push({at:Date.now(),method:req.method(),path:u.pathname,...(req.method()==='POST'?{body:req.postDataJSON()}: {})});});
 context.on('response',response=>{if(new URL(response.url()).pathname.startsWith('/assets/'))observe(async()=>{const rel=new URL(response.url()).pathname.slice(1),actual=sha(await response.body()),expected=sha(fs.readFileSync(path.join(spec.project,'frontend/dist',rel)));assert.equal(actual,expected);proof.assets.push({path:rel,response_sha256:actual,file_sha256:expected});});});
 const page=context.pages()[0]??await context.newPage();page.setDefaultTimeout(15000);page.on('pageerror',e=>proof.errors.push(String(e)));
 await page.goto(spec.origin,{waitUntil:'networkidle'});
 for(const kind of ['head','scope']){
  await page.reload({waitUntil:'networkidle'});await page.getByRole('navigation').getByRole('button',{name:/模拟面试/}).click();await page.locator(`[data-activity-id="${spec.activity_id}"]`).click();
  const area=page.locator('.interview-workspace');await area.getByLabel('面试目标',{exact:true}).fill(spec.goal);
  await action(page,domain,`${kind}-new-goal`,()=>area.getByRole('button',{name:'保存修正目标（另存版本）',exact:true}).click());
  const query=await action(page,retrieval,`${kind}-prepare-query`,()=>area.getByRole('button',{name:'开始提问',exact:true}).click());
  await driver('approve',query.body.business_key);
  const panel=area.locator('section[aria-label="资料检索与恢复"]');
  await panel.getByRole('button',{name:'只读核对索引与原意图',exact:true}).click();
  const reconcile=panel.getByRole('button',{name:'按原键只读核对',exact:true}).last();await reconcile.waitFor();await reconcile.click();
  await action(page,retrieval,`${kind}-continue-query`,()=>panel.getByRole('button',{name:'明确继续已批准的原检索请求',exact:true}).last().click());
  const model=await action(page,domain,`${kind}-prepare-model`,()=>panel.getByRole('button',{name:'明确继续尚未发送的原动作',exact:true}).last().click());
  await driver('approve',model.body.business_key);
  const intent=area.locator(`[data-interview-intent-key="${model.body.business_key}"]`);await intent.getByRole('button',{name:'只读核对原提交',exact:true}).click();
  const pattern=`**${domain}/${model.body.business_key}`;let hit=false,release;
  const barrier=new Promise(resolve=>release=resolve);
  await page.route(pattern,async route=>{const response=await route.fetch();proof.delayed_response={path:new URL(route.request().url()).pathname,body:await response.json()};hit=true;await barrier;await route.fulfill({response});});
  const beforePosts=posts(model.body.business_key);
  try{
   await intent.getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).click();await until(()=>hit);
   const mutation=await driver(kind,model.body.business_key);
   const refreshed=page.waitForResponse(r=>r.request().method()==='GET'&&new URL(r.url()).pathname===`/api/activities/${spec.activity_id}/interview/workspace`);
   await area.getByRole('button',{name:'只读刷新／恢复场次',exact:true}).click();await refreshed;
   await sleep(400);
   const before={target:await area.getByLabel('面试目标',{exact:true}).inputValue(),text:await area.innerText(),storage:await storage(page)};
   release();await sleep(600);
   const after={target:await area.getByLabel('面试目标',{exact:true}).inputValue(),text:await area.innerText(),storage:await storage(page)};
   assert.equal(posts(model.body.business_key),beforePosts,'late approved GET must never POST original key');
   assert.equal(after.target,before.target,'late response changed current input');
   const newRows=Object.entries(after.storage).map(([key,value])=>[key,JSON.parse(value)]);
   const beforeRows=Object.entries(before.storage).map(([key,value])=>[key,JSON.parse(value)]);
   // 旧键可记原持久事实，其他意图与当前输入必须保持。
   const withoutOld=rows=>rows.map(([key,value])=>[key,Array.isArray(value)?value.filter(x=>x.key!==model.body.business_key):value]);
   assert.deepEqual(withoutOld(newRows),withoutOld(beforeRows),'late response changed another intent');
   assert.equal(after.text,before.text,'late response changed current content/continuation');
   proof.cases.push({name:`actual-${kind}-late-approved-GET`,status:'PASS',business_key:model.body.business_key,route:new URL(spec.origin+domain+'/'+model.body.business_key).pathname,mutation,before,after,old_key_POSTs:beforePosts,no_late_POST:true});save();
  }finally{release();await page.unroute(pattern);}
 }
 await page.screenshot({path:spec.screenshot,fullPage:true});await Promise.allSettled([...observations]);assert(proof.assets.some(x=>x.path.endsWith('.js'))&&proof.assets.some(x=>x.path.endsWith('.css')));assert.equal(proof.errors.length,0);
 proof.status='PASS';save();
}catch(error){proof.status='FAIL';proof.error=String(error);proof.stack=error.stack;save();process.exitCode=1;}
finally{if(context)await context.close();}
