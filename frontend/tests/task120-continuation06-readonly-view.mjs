import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
const spec=JSON.parse(fs.readFileSync(process.env.RETROLUME_TASK120_UI_SPEC,'utf8'));
const sha=v=>createHash('sha256').update(v).digest('hex');
const proof={status:'RUNNING',requests:[],responses:[],assets:[],errors:[]};
const save=()=>fs.writeFileSync(spec.proof,JSON.stringify(proof,null,2));let context;
try{
 context=await chromium.launchPersistentContext(spec.profile,{headless:true,viewport:{width:1440,height:1050},serviceWorkers:'block',args:['--disable-background-networking']});
 await context.route('**/*',async route=>{assert.equal(new URL(route.request().url()).origin,spec.origin);await route.continue();});
 context.on('request',r=>proof.requests.push({method:r.method(),path:new URL(r.url()).pathname}));
 const observations=[];context.on('response',r=>{observations.push((async()=>{const p=new URL(r.url()).pathname;if(p==='/api/session'){const j=await r.json();proof.context=j.data_context;}if(p.startsWith('/assets/')){const h=sha(await r.body());assert.equal(h,sha(fs.readFileSync(path.join(spec.project,'frontend/dist',p.slice(1)))));proof.assets.push({path:p,sha256:h});}if(p==='/api/activities'||p==='/api/data/saved-records')proof.responses.push({path:p,status:r.status(),body:await r.json()});})().catch(e=>proof.errors.push(String(e))));});
 const page=context.pages()[0]??await context.newPage();page.setDefaultTimeout(16000);await page.goto(spec.origin,{waitUntil:'networkidle'});
 assert.equal(proof.context.current_mode,'restored_readonly');assert.equal(proof.context.read_only,true);assert.equal(proof.context.instance_id,spec.instance_id);
 const listing=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/activities'&&r.ok());await page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();await listing;await page.locator('[data-activity-id]').nth(2).waitFor();assert.equal(await page.locator('[data-activity-id]').count(),3);assert(!(await page.locator('body').innerText()).includes('活动数据暂不可用'));
 await page.screenshot({path:spec.screenshot});
 const saved=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/data/saved-records'&&r.ok());await page.getByRole('button',{name:'数据与备份',exact:true}).click();await saved;await page.getByRole('heading',{name:'已保存记录',exact:true}).waitFor();
 const records=page.locator('section').filter({has:page.getByRole('heading',{name:'已保存记录',exact:true})});await records.locator('article').nth(2).waitFor();assert.equal(await records.locator('article').count(),3);
 await Promise.all(observations);assert.equal(proof.requests.filter(r=>r.method==='POST').length,0);assert.equal(proof.errors.length,0);proof.status='PASS';proof.activity_rows=3;proof.saved_record_rows=3;proof.no_automatic_POST=true;save();
}catch(e){proof.status='FAIL';proof.error=String(e);proof.stack=e.stack;save();process.exitCode=1;}
finally{if(context)await context.close();}
