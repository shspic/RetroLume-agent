import fs from 'node:fs';
import path from 'node:path';
import cp from 'node:child_process';
import assert from 'node:assert/strict';
const [out,profile,fixturePath]=process.argv.slice(2),fixture=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
const spawn=cp.spawn;cp.spawn=function(command,args,options){const child=spawn(command,args,options);if(/chrome|chromium/i.test(command))process.stdout.write(JSON.stringify({event:'browser_spawn',pid:child.pid})+'\n');return child;};
const {chromium}=await import('playwright');
const browser=await chromium.launchPersistentContext(profile,{headless:true,viewport:{width:1365,height:1050}});
const requests=[],errors=[];
try{
 const page=browser.pages()[0];page.on('pageerror',error=>errors.push(error.message));
 page.on('request',request=>{let context=null;try{context=JSON.parse(request.headers()['x-retrolume-data-context']??'null');}catch{}requests.push({method:request.method(),path:new URL(request.url()).pathname,context});});
 await page.route('**/*',route=>new URL(route.request().url()).hostname==='127.0.0.1'?route.continue():route.abort());
 await page.goto('http://127.0.0.1:18114/',{waitUntil:'networkidle'});
 await page.getByRole('button',{name:'数据与备份',exact:true}).click();await page.getByRole('heading',{name:'已保存记录',exact:true}).waitFor();
 await page.getByLabel('记录类型').selectOption('memories');
 const deleted=page.locator('article').filter({hasText:fixture.memories.delete.memory_id});await deleted.waitFor();
 assert.ok((await deleted.innerText()).includes('"body": null'));
 assert.ok((await page.locator('body').innerText()).includes('C02-valid'));
 await page.getByLabel('原操作编号').fill(fixture.package_key);await page.getByRole('button',{name:'核对原操作',exact:true}).click();
 await page.getByText(fixture.package_key,{exact:false}).waitFor();await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();
 await page.getByRole('heading',{name:'已保存记录',exact:true}).waitFor();
 assert.deepEqual(requests.filter(request=>request.method==='POST'),[]);assert.deepEqual(errors,[]);
 const latest=requests.filter(request=>request.context).at(-1).context;assert.equal(latest.selection_generation,1);assert.equal(latest.read_only,true);
 await page.screenshot({path:path.join(out,'actual-selected.png'),fullPage:true});fs.writeFileSync(path.join(out,'actual-selected-dom.txt'),await page.locator('body').innerText());
 fs.writeFileSync(path.join(out,'browser-result.json'),JSON.stringify({state:'passed',layer:'actual Chromium/final dist/18114 TCP/new sealed PG; no route response fixtures',requests,errors,deleted_memory_body_null:true,valid_memory_readable:true,old_Hub_key_reachable:true,final_context:latest},null,2));
}catch(error){fs.writeFileSync(path.join(out,'browser-failure.json'),JSON.stringify({type:error.name,message:error.message,requests,errors},null,2));throw error;}
finally{await browser.close();process.stdout.write(JSON.stringify({event:'browser_closed',confirmed:true})+'\n');}
