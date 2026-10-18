import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {randomUUID,createHash} from 'node:crypto';
const require=createRequire(path.join(process.cwd(),'package.json'));const {chromium}=require('playwright');
const dir=path.join(process.env.RETROLUME_TASK117_EVIDENCE,`browser-${process.env.RETROLUME_TASK117_BROWSER_ATTEMPT}`);fs.mkdirSync(dir);
const proof={status:'running',observed_requests:0,posts:[],responses:[],assets:[],real_backend:true,provider_calls:0};
const save=()=>fs.writeFileSync(path.join(dir,'proof.json'),JSON.stringify(proof,null,2));
let browser,context,release;let armed=false,held=false,closing=false;const pending=new Set();
try{
 browser=await chromium.launch({headless:true});process.stdin.on('data',()=>void browser.close());process.stdin.on('end',()=>void browser.close());process.stdin.resume();
 context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();page.setDefaultTimeout(20000);
 context.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/')){proof.observed_requests++;if(r.method()==='POST')proof.posts.push(new URL(r.url()).pathname);}});
 context.on('response',r=>{const u=new URL(r.url());if(u.pathname.includes('saved-records')||/\/assets\/.*\.js$/.test(u.pathname)){
  const work=(async()=>{if(u.pathname.includes('saved-records'))proof.responses.push({path:u.pathname,category:u.searchParams.get('category'),http:r.status(),value:await r.json()});else proof.assets.push({path:u.pathname,sha256:createHash('sha256').update(await r.body()).digest('hex')});})().catch(e=>{if(!closing)proof.observer_error=String(e);}).finally(()=>pending.delete(work));pending.add(work);
 }});
 await page.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});
 const originalSession=await context.request.get('http://127.0.0.1:18118/api/session');proof.observed_requests++;const oldSession=await originalSession.json();
 proof.origin_context=oldSession.data_context;if(proof.origin_context.read_only)throw new Error('origin_not_normal');
 const barrier=new Promise(r=>release=r);
 await page.route('**/api/materials',async route=>{
  if(!armed||held||route.request().method()!=='GET')return route.continue();
  const actual=await route.fetch();const body=await actual.body();held=true;
  proof.held_actual_response={http:actual.status(),sha256:createHash('sha256').update(body).digest('hex'),context:actual.headers()['x-retrolume-data-context'],source_ids:JSON.parse(body).items.map(x=>x.id),actual_backend_bytes:true};save();
  await barrier;
  try{await route.fulfill({response:actual,body});proof.old_delivery='actual original bytes released to the original request';}catch(e){proof.old_delivery='original request aborted by normal document transition';proof.old_delivery_error=String(e).slice(0,180);}
 });
 armed=true;await page.getByRole('button',{name:'数据与备份',exact:true}).click();
 const until=Date.now()+15000;while(!held){if(Date.now()>until)throw new Error('old_material_response_not_held');await page.waitForTimeout(40);}
 const body={expected_plan_sha256:'06926cbd4ee118f4d41a14497ad97c19aad8cf38c5f36dd40fd5edef690d0ec3',business_key:randomUUID(),expected_selection_generation:0,confirm:true};
 proof.observed_requests++;const activated=await context.request.post('http://127.0.0.1:18118/api/data/restore-jobs/55957ddd-20dc-498b-972f-66f3805679cb/activate-readonly',{headers:{'X-RetroLume-Session':oldSession.token,'X-RetroLume-Data-Context':JSON.stringify(oldSession.data_context)},data:body,timeout:60000});
 proof.activation={request:body,http:activated.status(),receipt:await activated.json()};save();
 if(activated.status()!==200||proof.activation.receipt.state!=='active_readonly')throw new Error('formal_activation_not_confirmed');
 await page.reload({waitUntil:'domcontentloaded'});await page.getByRole('button',{name:'数据与备份',exact:true}).click();
 await page.getByText('当前仅供只读查看',{exact:false}).waitFor();await page.getByRole('heading',{name:'已保存记录',exact:true}).waitFor();
 const nextSessionResponse=await context.request.get('http://127.0.0.1:18118/api/session');proof.observed_requests++;const next=await nextSessionResponse.json();proof.selected_context=next.data_context;
 if(!next.data_context.read_only||next.data_context.selection_generation!==1||next.data_context.instance_id===oldSession.data_context.instance_id)throw new Error('selector_identity_not_advanced');
 const headers={'X-RetroLume-Session':next.token,'X-RetroLume-Data-Context':JSON.stringify(next.data_context)};
 proof.observed_requests++;const caps=await context.request.get('http://127.0.0.1:18118/api/data/capabilities',{headers});proof.selected_caps=await caps.json();
 if(proof.selected_caps.format!=='data_exit.v1.r02'||!proof.selected_caps.read_only)throw new Error('selected_caps_profile');
 const postsBefore=proof.posts.length;release();await page.waitForTimeout(400);
 if(proof.posts.length!==postsBefore)throw new Error('old_response_triggered_new_mutation');
 proof.old_response_granted_no_next_action=true;
 proof.observed_requests++;const denied=await context.request.post('http://127.0.0.1:18118/api/activities',{headers,data:{}});proof.write_refusal={http:denied.status(),value:await denied.json()};
 if(denied.status()!==409||!JSON.stringify(proof.write_refusal.value).includes('data_readonly'))throw new Error('readonly_write_gate');
 await page.getByLabel('记录类型').selectOption('memories');await page.waitForTimeout(350);
 await page.screenshot({path:path.join(dir,'R02-selected-readonly-history.png'),fullPage:true});
 if(!proof.assets.some(x=>x.sha256==='58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8'))throw new Error('wrong_bundle');
 proof.status='passed';
}catch(e){proof.status='failed';proof.error=String(e);save();throw e;}
finally{release?.();closing=true;await Promise.race([Promise.allSettled([...pending]),new Promise(r=>setTimeout(r,3000))]);if(context)await context.close();if(browser)await browser.close();proof.browser_closed=true;save();process.stdin.removeAllListeners();process.stdin.pause();process.stdin.unref?.();}
