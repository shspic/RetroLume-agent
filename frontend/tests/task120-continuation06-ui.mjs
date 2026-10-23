import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
const spec=JSON.parse(fs.readFileSync(process.env.RETROLUME_TASK120_UI_SPEC,'utf8'));
const sha=x=>createHash('sha256').update(x).digest('hex');
const proof={status:'RUNNING',fixture_sha256:sha(fs.readFileSync(fileURLToPath(import.meta.url))),cases:[],captures:[],assets:[],requests:[],native:[],contexts:[],storageAccess:[],errors:[]};
const save=()=>fs.writeFileSync(spec.proof,JSON.stringify(proof,null,2));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn,seconds=22){const end=Date.now()+seconds*1000;while(!await fn()){assert(Date.now()<end,'bounded condition timeout');await sleep(25);}}
let context,page,ordinal=0;const held=[],pending=new Map(),work=new Set();
function observe(fn){const p=Promise.resolve().then(fn).catch(e=>proof.errors.push(String(e))).finally(()=>work.delete(p));work.add(p);}
async function driver(kind,extra={}){++ordinal;fs.writeFileSync(path.join(spec.handshake,`request-${ordinal}.json`),JSON.stringify({ordinal,kind,...extra}));const target=path.join(spec.handshake,`reply-${ordinal}.json`);await until(()=>fs.existsSync(target),85);const result=JSON.parse(fs.readFileSync(target));assert.equal(result.status,'COMPLETED',JSON.stringify(result));return result.facts;}
const namespace=c=>`${c.dataset_id}.${c.instance_id}.${c.selection_generation}`;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function currentContext(){return proof.contexts.at(-1)?.value;}
async function settled(){
 await until(()=>{const ended=new Set(proof.native.filter(e=>e.kind==='fetch-resolved'||e.kind==='fetch-rejected').map(e=>e.id));return proof.native.filter(e=>e.kind==='fetch-start'&&!ended.has(e.id)).every(e=>held.some(h=>e.url.includes(h.key)));});
 await sleep(150);
 proof.settlement={actual_native_fetches_settled_except_explicit_held_GETs:true,context_transport_pending:[...pending.values()]};
}
async function snapshot(){return {text:await page.locator('.data-workspace').innerText(),input:await page.locator('.data-workspace input').evaluateAll(nodes=>nodes.filter(n=>n.type==='text').map(n=>n.value)),storage:await page.evaluate(()=>Object.fromEntries(Object.entries(localStorage))),databases:await page.evaluate(async()=>(await indexedDB.databases()).map(d=>d.name).sort())};}
async function goLearning(){await page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();await page.locator(`[data-activity-id="${spec.activity_id}"]`).click();await page.locator('button.ws-op').filter({hasText:spec.parent_operation}).first().click();await page.locator('section[aria-label="学习成果"]').waitFor();}
async function capture(index){
 await goLearning();await page.getByRole('button',{name:'从该学习成果续问…',exact:true}).click();await page.getByLabel('续问内容',{exact:true}).fill(spec.questions[index]);
 const follow=`/api/activities/${spec.activity_id}/learning/followups`;
 const [prepared]=await Promise.all([page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname===follow),page.getByRole('button',{name:'发出并等待',exact:true}).click()]);
 assert(prepared.ok());const key=prepared.request().postDataJSON().business_key;const initial=await prepared.json();assert(initial.outbound_approval&&!initial.outbound_approval.can_continue);
 await driver('approve',{business_key:key});
 const pattern=`**/api/activities/${spec.activity_id}/learning/intents/${key}?*`;let release;const barrier=new Promise(r=>release=r);const h={key,pattern,release,fulfilled:false};held.push(h);
 await page.route(pattern,async route=>{
   try{const response=await route.fetch();const body=await response.body();const json=JSON.parse(body);assert.equal(response.status(),200);assert(json.outbound_approval.can_continue);
     h.capture={index,key,path:new URL(route.request().url()).pathname,request_context:JSON.parse(route.request().headers()['x-retrolume-data-context']),status:response.status(),headers:response.headers(),body:json,body_sha256:sha(body)};
     proof.captures.push(h.capture);fs.writeFileSync(path.join(spec.evidence,`UI-normal-GET-${index+1}-root-${spec.root}.json`),JSON.stringify(h.capture,null,2));save();
     await barrier;await route.fulfill({response});h.fulfilled=true;
   }catch(e){h.transport_error=String(e);proof.errors.push(String(e));}
 });
 const intent=page.locator('.ws-intent').filter({hasText:spec.questions[index].slice(0,35)});assert.equal(await intent.count(),1);
 await intent.getByRole('button',{name:'核对（只读）',exact:true}).click();await until(()=>!!h.capture);return h;
}
try{
 assert(fs.existsSync(chromium.executablePath()));context=await chromium.launchPersistentContext(spec.profile,{headless:true,viewport:{width:1440,height:1050},serviceWorkers:'block',args:['--disable-background-networking']});
 await context.exposeBinding('__task120Observe',(_source,event)=>{if(event.kind==='storage')proof.storageAccess.push(event);else proof.native.push(event);});
 await context.addInitScript(()=>{
  const emit=value=>void window.__task120Observe(value).catch(()=>{});let seq=0;
  const original=window.fetch.bind(window);window.fetch=(input,init)=>{const url=String(input),id=++seq;emit({kind:'fetch-start',id,url});return original(input,init).then(response=>{emit({kind:'fetch-resolved',id,url,status:response.status});const json=response.json.bind(response);response.json=async()=>{emit({kind:'business-json',id,url});return json();};return response;},error=>{emit({kind:'fetch-rejected',id,url,error:String(error)});throw error;});};
  const get=Storage.prototype.getItem;Storage.prototype.getItem=function(key){if(String(key).startsWith('retrolume.'))emit({kind:'storage',key:String(key)});return get.call(this,key);};
 });
 await context.route('**/*',async route=>{if(new URL(route.request().url()).origin!==spec.origin){proof.errors.push('external request denied');await route.abort();}else await route.continue();});
 context.on('request',r=>{const p=new URL(r.url()).pathname;pending.set(r,p);const extra={};if(r.method()==='POST'){if((r.headers()['content-type']??'').includes('application/json'))extra.body=r.postDataJSON();else{const raw=r.postDataBuffer()??Buffer.alloc(0);extra.body_sha256=sha(raw);extra.bytes=raw.length;}}proof.requests.push({method:r.method(),path:p,context:r.headers()['x-retrolume-data-context'],...extra});});
 context.on('requestfinished',r=>pending.delete(r));context.on('requestfailed',r=>{pending.delete(r);proof.native.push({kind:'actual-requestfailed',url:r.url(),failure:r.failure()});});
 context.on('response',r=>observe(async()=>{const p=new URL(r.url()).pathname;if(p.startsWith('/assets/')){const file=path.join(spec.project,'frontend/dist',p.slice(1)),hash=sha(await r.body());assert.equal(hash,sha(fs.readFileSync(file)));proof.assets.push({path:p,response_sha256:hash,file_sha256:hash});}if(p==='/api/session'&&r.ok()){proof.contexts.push({kind:'session',value:(await r.json()).data_context});save();}if(p==='/api/data/capabilities'&&r.ok()){const value=await r.json();proof.contexts.push({kind:'production-capabilities',value:Object.fromEntries(['control_id','selection_generation','dataset_id','instance_id','current_mode','read_only'].map(k=>[k,value[k]])),response_header:r.headers()['x-retrolume-data-context']});save();}}));
 page=context.pages()[0]??await context.newPage();page.setDefaultTimeout(16000);page.on('pageerror',e=>proof.errors.push(String(e)));await page.goto(spec.origin,{waitUntil:'networkidle'});
 const original=currentContext();assert(original&&!original.read_only&&original.current_mode==='normal');proof.original_context=original;save();
 const first=await capture(0);await page.getByRole('button',{name:'数据与备份',exact:true}).click();await page.getByRole('heading',{name:'数据与备份',exact:true}).waitFor();await settled();
 const second=await capture(1);assert.equal(first.capture.request_context.current_mode,'normal');assert.equal(second.capture.request_context.current_mode,'normal');
 const backup=await driver('backup');assert.equal(backup.context.current_mode,'normal');proof.backup={receipt:backup.receipt,context:backup.context};save();
 proof.freeze=await driver('freeze');await page.getByRole('button',{name:'数据与备份',exact:true}).click();await page.getByRole('heading',{name:'数据与备份',exact:true}).waitFor();
 await page.getByRole('status').filter({hasText:'当前仅供只读查看'}).waitFor();await settled();
 const frozen=currentContext();assert.equal(frozen.current_mode,'frozen');assert.equal(frozen.read_only,true);assert.equal(namespace(frozen),namespace(original));assert.equal(frozen.control_id,original.control_id);
 const before=await snapshot(),postCount=proof.requests.filter(r=>r.method==='POST').length;
 first.release();await until(()=>first.fulfilled);await until(()=>proof.native.some(e=>e.kind==='fetch-resolved'&&e.url.includes(first.key)));await settled();const after=await snapshot();assert.deepEqual(after,before);
 assert(!proof.native.some(e=>e.kind==='business-json'&&e.url.includes(first.key)));assert.equal(proof.requests.filter(r=>r.method==='POST').length,postCount);
 proof.cases.push({name:'actual-complete-DataContext-late-normal-approved-GET',status:'PASS',business_key:first.key,original,frozen,namespace_unchanged:true,mode_and_read_only_changed:true,native_fetch_fulfilled:true,business_body_consumed:false,before,after,zero_automatic_POST:true});save();
 fs.writeFileSync(path.join(spec.evidence,`UI-complete-DataContext-PASS-root-${spec.root}.json`),JSON.stringify(proof.cases[0],null,2));
 const planPromise=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/data/restore-plans'&&r.request().method()==='POST');await page.getByLabel('选择备份文件',{exact:false}).setInputFiles(backup.path);const planResponse=await planPromise;assert(planResponse.ok());const plan=await planResponse.json();
 const restorePromise=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/data/restore-jobs'&&r.request().method()==='POST');await page.getByRole('button',{name:'确认验证这个备份',exact:true}).click();const restoreResponse=await restorePromise;assert(restoreResponse.ok());const job=await restoreResponse.json();proof.verified=await driver('verified',{job_id:job.job_id});
 await driver('arm_namespace');await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();proof.activation=await driver('activate',{job_id:job.job_id,plan_sha256:plan.plan_sha256});
 await until(()=>proof.contexts.some(c=>c.value?.current_mode==='restored_readonly'&&c.value.instance_id!==original.instance_id));await settled();const selected=currentContext();
 assert.equal(selected.current_mode,'restored_readonly');assert.equal(selected.read_only,true);assert.equal(selected.control_id,original.control_id);assert.notEqual(namespace(selected),namespace(original));assert.notEqual(selected.instance_id,original.instance_id);assert.notEqual(selected.dataset_id,original.dataset_id);assert(selected.selection_generation>original.selection_generation);
 assert(proof.requests.some(r=>r.context&&JSON.parse(r.context).instance_id===selected.instance_id));
 const before2=await snapshot(),postCount2=proof.requests.filter(r=>r.method==='POST').length;
 second.release();await until(()=>second.fulfilled);await until(()=>proof.native.some(e=>e.kind==='fetch-resolved'&&e.url.includes(second.key)));await settled();const after2=await snapshot();assert.deepEqual(after2,before2);
 assert(!proof.native.some(e=>e.kind==='business-json'&&e.url.includes(second.key)));assert.equal(proof.requests.filter(r=>r.method==='POST').length,postCount2);
 proof.cases.push({name:'actual-verified-restore-namespace-late-normal-approved-GET',status:'PASS',business_key:second.key,original,selected,namespace_before:namespace(original),namespace_after:namespace(selected),native_fetch_fulfilled:true,business_body_consumed:false,before:before2,after:after2,zero_automatic_POST:true,normal_selector_and_verified_target:true});save();
 fs.writeFileSync(path.join(spec.evidence,`UI-namespace-PASS-root-${spec.root}.json`),JSON.stringify(proof.cases[1],null,2));
 await page.reload({waitUntil:'networkidle'});await page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();await settled();proof.final_bootstrap_context=currentContext();assert.equal(proof.final_bootstrap_context.instance_id,selected.instance_id);
 proof.actual_storage_namespace_reads=proof.storageAccess.filter(e=>e.key.includes(namespace(selected)));assert(proof.actual_storage_namespace_reads.length>0,'new storage namespace was not read by production UI');
 await page.screenshot({path:path.join(spec.evidence,`UI-context-root-${spec.root}.png`)});await Promise.allSettled([...work]);assert(proof.assets.some(a=>a.path.endsWith('.js'))&&proof.assets.some(a=>a.path.endsWith('.css')));assert.equal(proof.errors.length,0,JSON.stringify(proof.errors));proof.status='PASS';save();
}catch(e){proof.status='FAIL';proof.error=String(e);proof.stack=e.stack;proof.context_transport_pending=[...pending.values()];save();process.exitCode=1;}
finally{for(const h of held)h.release();if(context)await context.close();}
