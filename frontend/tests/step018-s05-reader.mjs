import {chromium} from 'playwright';
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';
const evidence=process.env.RETROLUME_TASK117_EVIDENCE;
const dir=path.join(evidence,`browser-${process.env.RETROLUME_TASK117_BROWSER_ATTEMPT}`);fs.mkdirSync(dir);
const proof={status:'running',observed_requests:0,posts:[],records:[],assets:[],real_backend:true};
const save=()=>fs.writeFileSync(path.join(dir,'proof.json'),JSON.stringify(proof,null,2));
let browser,context;const pending=new Set();let closing=false;
try{
 browser=await chromium.launch({headless:true});process.stdin.on('data',()=>void browser.close());process.stdin.on('end',()=>void browser.close());process.stdin.resume();
 context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();page.setDefaultTimeout(18000);
 context.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/')){proof.observed_requests++;if(r.method()==='POST')proof.posts.push(new URL(r.url()).pathname);}});
 context.on('response',r=>{const url=new URL(r.url());if(url.pathname.includes('saved-records')||/\/assets\/.*\.js$/.test(url.pathname)){
  const work=(async()=>{if(url.pathname.includes('saved-records'))proof.records.push({category:url.searchParams.get('category'),http:r.status(),value:await r.json()});else proof.assets.push({path:url.pathname,sha256:createHash('sha256').update(await r.body()).digest('hex')});})().catch(e=>{if(!closing)proof.error=String(e);}).finally(()=>pending.delete(work));pending.add(work);
 }});
 await page.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});await page.getByRole('button',{name:'数据与备份',exact:true}).click();
 await page.getByText('当前仅供只读查看',{exact:false}).waitFor();await page.getByRole('heading',{name:'已保存记录',exact:true}).waitFor();
 const types=page.getByLabel('记录类型');
 for(const category of ['activities','learning','teaching','interview','memories','preview_history','versions']){
  if(category!=='activities')await types.selectOption(category);
  const until=Date.now()+15000;while(!proof.records.some(x=>x.category===category&&x.http===200)){if(Date.now()>until)throw new Error('records_not_read:'+category);await page.waitForTimeout(60);}
 }
 proof.export_disabled=await page.getByRole('button',{name:'导出这些已保存内容',exact:true}).isDisabled();
 proof.backup_disabled=await page.getByRole('button',{name:'保存当前时点的恢复备份',exact:true}).isDisabled();
 proof.restore_disabled=await page.locator('input[type=file]').isDisabled();
 if(!proof.export_disabled||!proof.backup_disabled||!proof.restore_disabled||proof.posts.length)throw new Error('readonly_gate_open');
 await page.screenshot({path:path.join(dir,'R01-real-readonly-records.png'),fullPage:true});
 if(!proof.assets.some(x=>x.sha256==='58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8'))throw new Error('wrong_bundle');proof.status='passed';
}catch(e){proof.status='failed';proof.error=String(e);save();throw e;}
finally{closing=true;await Promise.race([Promise.allSettled([...pending]),new Promise(r=>setTimeout(r,3000))]);if(context)await context.close();if(browser)await browser.close();proof.browser_closed=true;save();process.stdin.removeAllListeners();process.stdin.pause();process.stdin.unref?.();}
