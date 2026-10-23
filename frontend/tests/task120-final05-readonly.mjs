import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const spec=JSON.parse(fs.readFileSync(process.env.RETROLUME_TASK120_UI_SPEC,'utf8'));
const sha=x=>createHash('sha256').update(x).digest('hex');
const proof={status:'RUNNING',execution_class:'TESTONLY',fixture_sha256:sha(fs.readFileSync(fileURLToPath(import.meta.url))),assets:[],requests:[],cases:[],contexts:[],errors:[]};
const save=()=>fs.writeFileSync(spec.proof,JSON.stringify(proof,null,2));
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(f){const end=Date.now()+20000;while(!f()){assert(Date.now()<end,'bounded handshake timeout');await sleep(25);}}
let context,ordinal=0;const observations=new Set();
const observe=f=>{const p=Promise.resolve().then(f).catch(e=>proof.errors.push(String(e))).finally(()=>observations.delete(p));observations.add(p);};
async function driver(kind,key){ordinal++;fs.writeFileSync(path.join(spec.handshake,`request-${ordinal}.json`),JSON.stringify({ordinal,kind,activity_id:spec.activity_id,business_key:key}));const file=path.join(spec.handshake,`reply-${ordinal}.json`);await until(()=>fs.existsSync(file));const got=JSON.parse(fs.readFileSync(file));assert.equal(got.status,kind==='approve'?'APPROVED':'COMPLETED');save();return got;}
try{
 assert(fs.existsSync(chromium.executablePath()));context=await chromium.launchPersistentContext(spec.profile,{headless:true,viewport:{width:1440,height:1050},serviceWorkers:'block',args:['--disable-background-networking']});
 await context.route('**/*',async route=>{if(new URL(route.request().url()).origin!==spec.origin){proof.errors.push('external attempt denied');await route.abort();return;}await route.continue();});
 context.on('request',req=>{const u=new URL(req.url());proof.requests.push({at:Date.now(),method:req.method(),path:u.pathname,...(req.method()==='POST'?{body:req.postDataJSON()}: {})});});
 context.on('response',response=>observe(async()=>{const u=new URL(response.url());if(u.pathname.startsWith('/assets/')){const rel=u.pathname.slice(1),hash=sha(await response.body()),expected=sha(fs.readFileSync(path.join(spec.project,'frontend/dist',rel)));assert.equal(hash,expected);proof.assets.push({path:rel,response_sha256:hash,file_sha256:expected});}if(u.pathname==='/api/session'){const v=await response.json();proof.contexts.push(v.data_context);}if(u.pathname==='/api/data/capabilities'){const h=response.headers()['x-retrolume-data-context'];if(h)proof.contexts.push(JSON.parse(h));}}));
 const page=context.pages()[0]??await context.newPage();page.setDefaultTimeout(16000);page.on('pageerror',e=>proof.errors.push(String(e)));
 await page.goto(spec.origin,{waitUntil:'networkidle'});await page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();await page.locator(`[data-activity-id="${spec.activity_id}"]`).click();
 await page.locator('button.ws-op').filter({hasText:spec.parent_operation}).first().click();await page.locator('section[aria-label="学习成果"]').waitFor();
 await page.getByRole('button',{name:'从该学习成果续问…',exact:true}).click();await page.getByLabel('续问内容',{exact:true}).fill(spec.question);
 const follow=`/api/activities/${spec.activity_id}/learning/followups`;
 const [pending]=await Promise.all([page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname===follow),page.getByRole('button',{name:'发出并等待',exact:true}).click()]);assert(pending.ok());const cmd=pending.request().postDataJSON(),receipt=await pending.json();assert(receipt.outbound_approval&&!receipt.outbound_approval.can_continue);
 await driver('approve',cmd.business_key);const intent=page.locator('.ws-intent').filter({hasText:'学习续问'});await intent.getByRole('button',{name:'核对（只读）',exact:true}).click();
 const pattern=`**/api/activities/${spec.activity_id}/learning/intents/${cmd.business_key}?*`;let hit=false,release;const barrier=new Promise(resolve=>release=resolve);
 await page.route(pattern,async route=>{const response=await route.fetch();proof.delayed={path:new URL(route.request().url()).pathname,receipt:await response.json()};hit=true;await barrier;await route.fulfill({response});});
 const posts=()=>proof.requests.filter(r=>r.method==='POST'&&r.path===follow&&r.body?.business_key===cmd.business_key).length,beforePosts=posts();
 try{
  await intent.getByRole('button',{name:'重新提交同一意图',exact:true}).click();await until(()=>hit);assert(proof.delayed.receipt.outbound_approval.can_continue);
  proof.freeze=await driver('freeze',cmd.business_key);
  await page.getByRole('button',{name:'数据与备份',exact:true}).click();await page.getByRole('heading',{name:'数据与备份',exact:true}).waitFor();await page.getByRole('status').filter({hasText:'当前仅供只读查看'}).waitFor();
  await sleep(500);const before={text:await page.locator('.data-workspace').innerText(),storage:await page.evaluate(()=>Object.fromEntries(Object.entries(localStorage)))};
  release();await sleep(600);const after={text:await page.locator('.data-workspace').innerText(),storage:await page.evaluate(()=>Object.fromEntries(Object.entries(localStorage)))};
  assert.equal(posts(),beforePosts);assert.equal(before.text,after.text);assert.deepEqual(before.storage,after.storage);
  proof.cases.push({name:'actual-frozen-DataContext-plus-view-late-approved-GET',status:'PASS',business_key:cmd.business_key,before,after,old_key_POSTs:beforePosts,isolated_DataContext_guard:false,namespace_change:false});save();
 }finally{release();await page.unroute(pattern);}
 await Promise.allSettled([...observations]);assert(proof.contexts.some(x=>x?.read_only));assert(proof.assets.some(x=>x.path.endsWith('.js'))&&proof.assets.some(x=>x.path.endsWith('.css')));assert.equal(proof.errors.length,0);proof.status='PASS_FOR_COMBINED_CONTEXT_AND_VIEW';save();
}catch(error){proof.status='FAIL';proof.error=String(error);proof.stack=error.stack;save();process.exitCode=1;}
finally{if(context)await context.close();}
