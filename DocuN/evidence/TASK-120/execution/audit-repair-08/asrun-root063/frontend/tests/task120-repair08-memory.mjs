import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';

const spec=JSON.parse(fs.readFileSync(process.env.RETROLUME_TASK120_UI_SPEC,'utf8'));
const sha=value=>createHash('sha256').update(value).digest('hex');
const proof={status:'RUNNING',requests:[],assets:[],steps:[],errors:[]};
const save=()=>fs.writeFileSync(spec.proof,JSON.stringify(proof,null,2));
const mark=(name,value)=>fs.writeFileSync(path.join(spec.handshake,name+'.json'),JSON.stringify(value));
let context,page,latestList=[];
const pendingResponses=[];
async function openMemory(){
 const workspace=page.getByRole('region',{name:'学习记忆工作区'});
 if(!await workspace.isVisible())await page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();
 await workspace.getByRole('heading',{name:'学习记忆',exact:true}).waitFor();
 await page.waitForFunction(()=>document.querySelectorAll('.memory-list .memory-item').length>0);
 await Promise.all(pendingResponses);
 const index=latestList.findIndex(x=>x.memory_id===spec.memory_id);assert(index>=0);
 await workspace.locator('.memory-list .memory-item').nth(index).getByRole('button').click();
 await workspace.locator(`.memory-detail[data-memory-id="${spec.memory_id}"]`).waitFor();
 return workspace;
}
async function snapshot(label,expected){
 const workspace=await openMemory();const detail=workspace.locator('.memory-detail');
 if(expected==='pending'){
  await detail.getByText(/内容清理待核对/).waitFor();
  assert.equal(await detail.getByRole('button',{name:'明确重试原清单清理',exact:true}).count(),1);
  assert(!await detail.getByText(/本条在线正文已清理/).count());
 }else{
  await detail.getByText(/本条在线正文已清理/).waitFor();
  assert.equal(await detail.getByRole('button',{name:'明确重试原清单清理',exact:true}).count(),0);
 }
 proof.steps.push({label,state:expected,detail_text:await detail.innerText(),posts:proof.requests.filter(x=>x.method==='POST').length});save();
 await workspace.screenshot({path:path.join(spec.screenshots,`memory08-${label}.png`)});
 return detail;
}
try{
 context=await chromium.launchPersistentContext(spec.profile,{headless:true,viewport:{width:1360,height:960},
  serviceWorkers:'block',args:['--disable-background-networking']});
 await context.route('**/*',async route=>{assert.equal(new URL(route.request().url()).origin,spec.origin);await route.continue();});
 context.on('request',request=>proof.requests.push({method:request.method(),path:new URL(request.url()).pathname}));
 context.on('response',response=>pendingResponses.push((async()=>{
  const p=new URL(response.url()).pathname;
  if(p==='/api/memories'&&response.ok())latestList=(await response.json()).items;
  if(p.startsWith('/assets/')){
   const hash=sha(await response.body());assert.equal(hash,sha(fs.readFileSync(path.join(spec.project,'frontend/dist',p.slice(1)))));
   proof.assets.push({path:p,sha256:hash});
  }
 })().catch(error=>proof.errors.push(String(error)))));
 page=context.pages()[0]??await context.newPage();page.setDefaultTimeout(18000);
 await page.goto(spec.origin,{waitUntil:'networkidle'});
 await snapshot('API-reopened-pending','pending');
 await page.reload({waitUntil:'networkidle'});await snapshot('page-reopened-pending','pending');
 assert.equal(proof.requests.filter(x=>x.method==='POST').length,0);
 mark('pending',{state:'pending',explicit_retry_visible:true,no_automatic_POST:true});
 const receipt=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/memories/commands'&&response.request().method()==='POST');
 await page.locator('.memory-detail').getByRole('button',{name:'明确重试原清单清理',exact:true}).click();
 const result=await receipt;assert.equal(result.status(),200);
 const body=await result.json();assert.equal(body.action,'purge');assert.equal(body.purge_state_now,'done');
 assert(!body.cleanup_status_unconfirmed);proof.explicit_retry_receipt=body;
 await page.waitForLoadState('networkidle');await snapshot('explicit-retry-done','done');
 assert.equal(proof.requests.filter(x=>x.method==='POST').length,1);mark('done',{state:'done',explicit_POSTs:1});
 const until=Date.now()+60000;
 while(!fs.existsSync(path.join(spec.handshake,'api-reopened.json'))){assert(Date.now()<until);await new Promise(resolve=>setTimeout(resolve,50));}
 await page.reload({waitUntil:'networkidle'});await snapshot('second-API-reopened-done','done');
 await Promise.all(pendingResponses);assert.equal(proof.errors.length,0);assert.equal(proof.requests.filter(x=>x.method==='POST').length,1);
 proof.status='PASS';proof.one_headless_context_one_page=true;proof.no_model_or_embedding_POST=true;proof.formal_dist_hashes_bound=true;save();
}catch(error){proof.status='FAIL';proof.error=String(error);proof.stack=error.stack;save();process.exitCode=1;}
finally{if(context)await context.close();}
