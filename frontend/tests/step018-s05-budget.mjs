import {chromium} from 'playwright';import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';
const evidence=process.env.RETROLUME_TASK117_EVIDENCE,attempt=process.env.RETROLUME_TASK117_BROWSER_ATTEMPT;
const dir=path.join(evidence,`browser-${attempt}`);fs.mkdirSync(dir);const intent=JSON.parse(fs.readFileSync(path.join(evidence,'one-request-intent.json')));
const proof={status:'running',observed_requests:0,posts:[],assets:[],actual_budget:1,real_backend:true};const save=()=>fs.writeFileSync(path.join(dir,'proof.json'),JSON.stringify(proof,null,2));
let browser,context;const pending=new Set();let closing=false;
try{
 browser=await chromium.launch({headless:true});process.stdin.on('data',()=>void browser.close());process.stdin.on('end',()=>void browser.close());process.stdin.resume();context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();page.setDefaultTimeout(18000);
 context.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/')){proof.observed_requests++;if(r.method()==='POST')proof.posts.push({path:new URL(r.url()).pathname,body:r.postDataJSON()});}});
 context.on('response',r=>{if(/\/assets\/.*\.js$/.test(new URL(r.url()).pathname)){const work=r.body().then(bytes=>proof.assets.push({sha256:createHash('sha256').update(bytes).digest('hex')})).catch(e=>{if(!closing)proof.error=String(e);}).finally(()=>pending.delete(work));pending.add(work);}});
 await page.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});await page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();await page.locator(`[data-activity-id="${intent.activity_id}"]`).click();const work=page.locator('section.ws-teaching');await work.waitFor();
 const plan=work.getByRole('button',{name:'生成/重订路径（1 次模型）',exact:true});await plan.waitFor();
 const until=Date.now()+10000;while(!await plan.isEnabled()){if(Date.now()>until)throw new Error('plan_gate_never_ready');await page.waitForTimeout(80);}await plan.click();
 await work.getByText('剩余额度不足以完成本步，查询和后续动作均未发送。',{exact:false}).waitFor();await page.waitForTimeout(500);
 if(proof.posts.length)throw new Error('partial_query_or_model_sent');proof.whole_query_plus_model_refused_before_POST=true;
 await page.screenshot({path:path.join(dir,'one-request-cannot-start-two-call-step.png'),fullPage:true});
 await page.reload({waitUntil:'networkidle'});await page.waitForTimeout(600);if(proof.posts.length)throw new Error('reload_resubmitted');proof.reload_get_only=true;
 if(!proof.assets.some(x=>x.sha256==='58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8'))throw new Error('wrong_bundle');proof.status='passed';
}catch(e){proof.status='failed';proof.error=String(e);save();throw e;}
finally{closing=true;await Promise.race([Promise.allSettled([...pending]),new Promise(r=>setTimeout(r,3000))]);if(context)await context.close();if(browser)await browser.close();proof.browser_closed=true;save();process.stdin.removeAllListeners();process.stdin.pause();process.stdin.unref?.();}
