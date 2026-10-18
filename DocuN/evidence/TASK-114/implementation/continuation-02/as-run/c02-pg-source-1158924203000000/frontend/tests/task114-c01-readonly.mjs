import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import cp from 'node:child_process';
const [out,profile]=process.argv.slice(2);
const spawn=cp.spawn;cp.spawn=function(command,args,options){const child=spawn(command,args,options);if(/chrome|chromium/i.test(command))process.stdout.write(JSON.stringify({event:'browser_spawn',pid:child.pid,executable:command})+'\n');return child;};
const {chromium}=await import('playwright');
const context=await chromium.launchPersistentContext(profile,{headless:true,viewport:{width:1365,height:1000},acceptDownloads:true,downloadsPath:out});
const requests=[],errors=[];
try{
 const page=context.pages()[0];page.on('request',r=>requests.push({method:r.method(),path:new URL(r.url()).pathname}));page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:18114/',{waitUntil:'networkidle'});fs.writeFileSync(path.join(out,'01-dom-before.txt'),await page.locator('body').innerText());
 await page.getByRole('button',{name:'数据与备份',exact:true}).click();await page.getByRole('heading',{name:'已保存记录',exact:true}).waitFor();
 await page.screenshot({path:path.join(out,'02-selected-readonly.png'),fullPage:true});
 const before=await page.locator('body').innerText();assert.ok(before.includes('当前仅供只读查看'));
 await page.getByLabel('记录类型').selectOption('interview');await page.waitForTimeout(300);
 await page.getByLabel('记录类型').selectOption('memories');await page.waitForTimeout(300);
 await page.evaluate(async()=>{
  localStorage.setItem('retrolume.interview.intents:c01-old-instance',JSON.stringify({draft:'旧实例未提交'}));
  await new Promise((resolve,reject)=>{const q=indexedDB.open('retrolume-interview-drafts:c01-old-instance',1);q.onupgradeneeded=()=>q.result.createObjectStore('drafts',{keyPath:'id'});q.onsuccess=()=>{const db=q.result;const t=db.transaction('drafts','readwrite');t.objectStore('drafts').put({id:'c01-old',text:'旧实例未提交'});t.oncomplete=()=>{db.close();resolve();};t.onerror=()=>reject(t.error);};q.onerror=()=>reject(q.error);});
 });
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'单独下载未提交浏览器草稿',exact:true}).click();await (await download).saveAs(path.join(out,'drafts.json'));
 const d=JSON.parse(fs.readFileSync(path.join(out,'drafts.json'),'utf8'));assert.equal(d.submitted,false);assert.ok(d.indexed['retrolume-interview-drafts:c01-old-instance/drafts']);
 await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();await page.reload({waitUntil:'networkidle'});
 assert.deepEqual(requests.filter(r=>!['GET','HEAD','OPTIONS'].includes(r.method)),[]);assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({state:'passed',scope:'actual selected readonly workspace, categories, synthetic old-instance IDB/localStorage draft export, GET-only refresh',requests,errors},null,2));
}finally{await context.close();}
