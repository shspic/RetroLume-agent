import fs from 'node:fs';
import path from 'node:path';
import cp from 'node:child_process';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const [root,out,profile]=process.argv.slice(2);
const write=(name,value)=>fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2));
const original=cp.spawn;
cp.spawn=function(command,args,options){
  const child=original(command,args,options);
  if(/chrome|chromium/i.test(command))process.stdout.write(JSON.stringify({event:'browser_spawn',pid:child.pid,executable:command})+'\n');
  return child;
};
const {chromium}=await import(pathToFileURL(path.join(root,'frontend/node_modules/playwright/index.mjs')).href);
const context=await chromium.launchPersistentContext(profile,{headless:true,viewport:{width:1365,height:1050},acceptDownloads:true,downloadsPath:out});
const requests=[],errors=[];
let browserClosed=false;
try{
  const page=context.pages()[0];
  page.on('request',r=>requests.push({method:r.method(),path:new URL(r.url()).pathname}));
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto('http://127.0.0.1:18115/',{waitUntil:'networkidle'});
  await page.getByRole('button',{name:'数据与备份',exact:true}).click();
  await page.getByRole('button',{name:'保存当前时点的恢复备份',exact:true}).waitFor();
  const session=await page.evaluate(async()=>await (await fetch('/api/session')).json());
  const oldContext=session.data_context;
  // 实际 POST 在服务端确认后，仅在浏览器网络边界受控丢回应。
  let dropped=null;
  await page.route('**/api/data/jobs',async route=>{
    if(route.request().method()!=='POST')return route.continue();
    const body=route.request().postDataJSON();const response=await route.fetch();
    dropped={business_key:body.business_key,status:response.status(),receipt:await response.json()};
    await route.abort('failed');
  });
  await page.getByRole('button',{name:'保存当前时点的恢复备份',exact:true}).click();
  await page.getByRole('alert').waitFor();
  assert.ok(dropped && dropped.status===202);
  write('01-drop-response.json',{layer:'actual TCP POST/Hub; controlled browser response abort; capture input fixture',...dropped});
  await page.unroute('**/api/data/jobs');
  await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();
  await page.getByText(dropped.business_key,{exact:false}).waitFor();
  const persisted=await page.evaluate(async({token,key})=>await (await fetch('/api/data/jobs/by-key/'+key,{headers:{'X-RetroLume-Session':token}})).json(),{token:session.token,key:dropped.business_key});
  assert.equal(persisted.job_id,dropped.receipt.job_id);
  assert.equal(requests.filter(r=>r.method==='POST'&&r.path==='/api/data/jobs').length,1);
  write('02-get-original-key.json',{same_job:true,receipt:persisted,job_post_count:1});
  const conflict=await page.evaluate(async({token,key})=>{
    const r=await fetch('/api/data/jobs',{method:'POST',headers:{'X-RetroLume-Session':token,'Content-Type':'application/json'},
      body:JSON.stringify({kind:'portable_export',business_key:key,scope:{mode:'all'},confirm:true})});
    return {status:r.status(),body:await r.json()};
  },{token:session.token,key:dropped.business_key});
  assert.equal(conflict.status,409);assert.equal(conflict.body.code,'request_conflict');write('03-key-hash-conflict.json',conflict);
  // 真实取消 handler + 刷新 UI，不运行受影响的实际发布消费者。
  const pending=await page.evaluate(async({token})=>{
    const r=await fetch('/api/data/jobs',{method:'POST',headers:{'X-RetroLume-Session':token,'Content-Type':'application/json'},
      body:JSON.stringify({kind:'restore_checkpoint',business_key:'task115-browser-cancel',scope:{mode:'all'},confirm:true})});
    return await r.json();
  },{token:session.token});
  // 只读核对并保留已发布终态，取消 UI 的 prepared 分支用受控响应定位。
  await page.route('**/api/data/jobs/by-key/task115-browser-cancel',route=>route.fulfill({json:{...pending,state:'prepared',stage:'prepared'}}));
  await page.evaluate(()=>{const k=Object.keys(localStorage).find(k=>k.startsWith('retrolume.data-jobs.v1:'));const list=JSON.parse(localStorage.getItem(k)??'[]');list.push('task115-browser-cancel');localStorage.setItem(k,JSON.stringify(list));});
  await page.route(`**/api/data/jobs/${pending.job_id}/cancel`,route=>route.fulfill({json:{...pending,state:'cancelled',stage:'cancel_requested'}}));
  await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();
  const article=page.locator('article').filter({hasText:'task115-browser-cancel'});
  await article.getByRole('button',{name:'取消本次操作',exact:true}).click();
  await page.waitForTimeout(250);
  assert.equal(requests.filter(r=>r.method==='POST'&&r.path===`/api/data/jobs/${pending.job_id}/cancel`).length,1);
  write('04-cancel-ui.json',{layer:'actual final bundle; prepared/cancel responses controlled, actual background package already terminal',cancel_post_count:1,
     automatic_new_job_posts:requests.filter(r=>r.method==='POST'&&r.path==='/api/data/jobs').length-3});
  await page.unroute('**/api/data/jobs/by-key/task115-browser-cancel');
  await page.unroute(`**/api/data/jobs/${pending.job_id}/cancel`);
  // 两个能力 GET 反序到达，证明最终 bundle 将旧上下文重新写为当前。
  const newer={...oldContext,selection_generation:1,dataset_id:'11500000-0000-4000-8000-000000000001',
                instance_id:'11500000-0000-4000-8000-000000000002',current_mode:'restored_readonly',read_only:true};
  let first=null,count=0,oldReleased=false;
  const held=[];
  await page.route('**/api/data/saved-records*',route=>route.fulfill({json:{items:[],next_offset:null}}));
  await page.route('**/api/data/capabilities',async route=>{
    count++;
    if(count===1){first=route;return;}
    if(oldReleased){held.push(route);return;}
    await route.fulfill({json:{...newer,format:'data_exit.v1.r01',backup_available:true,restore_executor_configured:false,source_delete_available:false}});
  });
  await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();
  for(let i=0;i<30&&!first;i++)await page.waitForTimeout(20);
  assert.ok(first);
  await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();
  await page.getByText('当前仅供只读查看，旧调用、工具和预览的执行资格未恢复。原数据保留，持续使用需后续验收。',{exact:true}).waitFor();
  fs.writeFileSync(path.join(out,'05-new-context-dom.txt'),await page.locator('body').innerText());
  await page.screenshot({path:path.join(out,'05-new-context.png'),fullPage:true});
  oldReleased=true;
  await first.fulfill({json:{...oldContext,format:'data_exit.v1.r01',backup_available:true,restore_executor_configured:false,source_delete_available:false}});
  await page.waitForTimeout(300);
  const reverted=await page.getByText('当前仅供只读查看，旧调用、工具和预览的执行资格未恢复。原数据保留，持续使用需后续验收。',{exact:true}).count()===0;
  fs.writeFileSync(path.join(out,'06-old-context-reverted-dom.txt'),await page.locator('body').innerText());
  await page.screenshot({path:path.join(out,'06-old-context-reverted.png'),fullPage:true});
  write('06-late-capabilities.json',{layer:'actual final bundle, reordered controlled capability responses; no actual backend selector change',
       old_context:oldContext,new_context:newer,late_old_response_reverted_current_context:reverted,requests,errors});
  assert.equal(reverted,true);
  for(const route of held)await route.abort('aborted');
  write('result.json',{late_context_defect_observed:true,requests,errors,post_count:requests.filter(r=>r.method==='POST').length});
}catch(error){write('failure.json',{type:error.name,message:error.message,requests,errors});throw error;}
finally{await context.close();browserClosed=true;process.stdout.write(JSON.stringify({event:'browser_closed',confirmed:browserClosed})+'\n');}
