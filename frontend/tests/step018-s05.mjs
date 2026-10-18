// Actual final bundle and PG. Delay only real responses; never fabricate business data.
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const dir=path.join(process.env.RETROLUME_TASK117_EVIDENCE,`browser-${process.env.RETROLUME_TASK117_BROWSER_ATTEMPT}`);
fs.mkdirSync(dir);
const intent=JSON.parse(fs.readFileSync(path.join(process.env.RETROLUME_TASK117_EVIDENCE,'ui-boundaries-intent.json')));
const proof={status:'running',real_backend:true,final_bundle:true,posts:[],assets:[],observed_requests:0};
const save=()=>fs.writeFileSync(path.join(dir,'proof.json'),JSON.stringify(proof,null,2));
let browser,context,page,held=null,release=null,holdAid=null,capture=null,closing=false;
const observations=new Set();
function observe(work){const p=Promise.resolve().then(work).catch(e=>{if(!closing){proof.observation_errors??=[];proof.observation_errors.push(String(e));}}).finally(()=>observations.delete(p));observations.add(p);}
try{
 browser=await chromium.launch({headless:true});
 process.stdin.on('data',()=>void browser.close());process.stdin.on('end',()=>void browser.close());process.stdin.resume();
 context=await browser.newContext({viewport:{width:1440,height:1000}});page=await context.newPage();page.setDefaultTimeout(18000);
 context.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/'))proof.observed_requests++;});
 context.on('response',r=>{if(/\/assets\/.*\.js$/.test(new URL(r.url()).pathname))observe(async()=>proof.assets.push({url:r.url(),sha256:createHash('sha256').update(await r.body()).digest('hex')}));});
 await context.route('**/api/**',async route=>{
  const req=route.request(),u=new URL(req.url());
  if(req.method()==='GET'&&holdAid&&u.pathname===`/api/activities/${holdAid}/teaching/workspace`){
   holdAid=null;const actual=await route.fetch();held={url:u.pathname,status:actual.status(),body_sha256:createHash('sha256').update(await actual.body()).digest('hex')};save();
   await new Promise(resolve=>{release=resolve;});try{await route.fulfill({response:actual});}catch{}return;
  }
  if(req.method()==='POST'&&u.pathname.endsWith('/teaching/commands')){
   const body=req.postDataJSON();proof.posts.push({path:u.pathname,body});
   if(!capture){capture={url:req.url(),body,headers:await req.allHeaders()};const actual=await route.fetch();proof.first={http:actual.status(),receipt:await actual.json()};save();await new Promise(resolve=>setTimeout(resolve,800));return route.fulfill({response:actual});}
  }
  return route.continue();
 });
 await page.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});
 await page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();
 const open=async aid=>{await page.locator(`[data-activity-id="${aid}"]`).click();await page.locator('section.ws-teaching').waitFor();};
 await open(intent.a);await page.locator('#teaching-goal').fill('S05同键目标：只核对当前单位换算。');
 const saveGoal=page.getByRole('button',{name:'保存目标（不调用模型）',exact:true});await saveGoal.click();
 await page.waitForFunction(()=>document.querySelector('section.ws-teaching button.primary')?.disabled===true);
 proof.double_submit_gate_disabled=await saveGoal.isDisabled();
 await page.waitForTimeout(1400);if(proof.first?.http!==200||proof.first?.receipt.status!=='committed')throw new Error('real_goal_not_committed');
 // Replays through actual local-session and DataContext middleware, same real PG key.
 proof.same_key=await page.evaluate(async command=>{
  const call=async body=>{const r=await fetch(command.url,{method:'POST',headers:command.headers,body:JSON.stringify(body)});return {http:r.status,body:await r.json()};};
  const same=await Promise.all([call(command.body),call(command.body)]);
  const different=await call({...command.body,body:{...command.body.body,goal:'S05异文冲突，不覆盖原目标'}});return {same,different};
 },capture);
 if(proof.same_key.same.some(x=>x.http!==200||x.body.request_sha256!==proof.first.receipt.request_sha256)||proof.same_key.different.http!==409)throw new Error('same_key_identity_failed');
 holdAid=intent.b;await open(intent.b);
 const end=Date.now()+15000;while(!held){if(Date.now()>end)throw new Error('late_read_not_started');await page.waitForTimeout(50);}
 await open(intent.a);await page.locator('#teaching-goal').waitFor();release();release=null;
 await page.waitForTimeout(1100);
 const text=await page.locator('#teaching-goal').inputValue();if(!text.includes('S05同键目标')||text.includes('S05另一个'))throw new Error('late_view_polluted_current');
 proof.late_view={held,current_a:intent.a,current_goal:text,old_response_released:true,old_body_not_shown:true};
 // A copied sessionStorage owner must receive a distinct live Web Lock identity.
 const stored=await page.evaluate(()=>Object.fromEntries(Object.entries(sessionStorage)));
 const second=await context.newPage();await second.addInitScript(saved=>{if(location.origin==='http://127.0.0.1:18118')for(const [k,v]of Object.entries(saved))sessionStorage.setItem(k,v);},stored);
 await second.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});await second.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();await second.locator(`[data-activity-id="${intent.a}"]`).click();await second.locator('#teaching-goal').waitFor();await second.waitForTimeout(700);
 const owners=await Promise.all([page,second].map(p=>p.evaluate(()=>Object.fromEntries(Object.entries(sessionStorage).filter(([k])=>k.includes('teaching-editor-owner'))))));
 const own=owners.map(x=>Object.values(x)[0]);if(!own[0]||!own[1]||own[0]===own[1])throw new Error('copied_owner_not_isolated');proof.owner_isolation={copied_session:true,distinct_live_owners:true,owners};await second.close();
 const body=await page.locator('body').innerText();for(const label of ['模型请求：已预扣','费用：已预扣','时间：上限','工具次数：'])if(!body.includes(label))throw new Error('missing_ledger_display:'+label);
 proof.four_ledgers_visible=true;await page.screenshot({path:path.join(dir,'same-key-late-view-four-ledgers.png'),fullPage:true});
 const before=proof.posts.length;await page.reload({waitUntil:'networkidle'});await page.waitForTimeout(600);if(proof.posts.length!==before)throw new Error('reload_reposted');proof.reload_get_only=true;
 if(!proof.assets.some(x=>x.sha256===intent.bundle_sha256))throw new Error('wrong_bundle');proof.status='passed';save();
}catch(e){proof.status='failed';proof.error=String(e);save();throw e;}
finally{
 release?.();closing=true;
 await Promise.race([Promise.allSettled([...observations]),new Promise(r=>setTimeout(r,3000))]);
 if(context)await context.close();if(browser)await browser.close();proof.browser_closed=true;save();
 process.stdin.removeAllListeners();process.stdin.pause();process.stdin.unref?.();
}
