import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {createHash} from 'node:crypto';
const {chromium}=createRequire(path.join(process.cwd(),'package.json'))('playwright');
const dir=path.join(process.env.RETROLUME_TASK117_EVIDENCE,`browser-${process.env.RETROLUME_TASK117_BROWSER_ATTEMPT}`);fs.mkdirSync(dir);
const proof={status:'running',observed_requests:0,posts:[],records:[],assets:[],real_backend:true};const save=()=>fs.writeFileSync(path.join(dir,'proof.json'),JSON.stringify(proof,null,2));
const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
let browser,context;const pending=new Set();let closing=false;
try{
 browser=await chromium.launch({headless:true});process.stdin.on('data',()=>void browser.close());process.stdin.on('end',()=>void browser.close());process.stdin.resume();context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();page.setDefaultTimeout(20000);
 context.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/')){proof.observed_requests++;if(r.method()==='POST')proof.posts.push(new URL(r.url()).pathname);}});
 context.on('response',r=>{const u=new URL(r.url());if(u.pathname.includes('saved-records')||/\/assets\/.*\.js$/.test(u.pathname)){const work=(async()=>{if(u.pathname.includes('saved-records'))proof.records.push({category:u.searchParams.get('category'),http:r.status(),value:await r.json()});else proof.assets.push({path:u.pathname,sha256:createHash('sha256').update(await r.body()).digest('hex')});})().catch(e=>{if(!closing)proof.observer_error=String(e);}).finally(()=>pending.delete(work));pending.add(work);}});
 await page.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});await page.getByRole('button',{name:'数据与备份',exact:true}).click();await page.getByText('当前仅供只读查看',{exact:false}).waitFor();await page.getByRole('heading',{name:'已保存记录',exact:true}).waitFor();
 const sessionResponse=await context.request.get('http://127.0.0.1:18118/api/session');proof.observed_requests++;const session=await sessionResponse.json();proof.data_context=session.data_context;
 const headers={'X-RetroLume-Session':session.token,'X-RetroLume-Data-Context':canonical(session.data_context)};
 proof.observed_requests++;const denied=await context.request.post('http://127.0.0.1:18118/api/activities',{headers,data:{}});proof.write_refusal={http:denied.status(),value:await denied.json()};if(denied.status()!==409||!JSON.stringify(proof.write_refusal.value).includes('data_readonly'))throw new Error('write_not_refused_by_readonly_gate');
 await page.getByLabel('记录类型').selectOption('memories');const until=Date.now()+12000;while(!proof.records.some(x=>x.category==='memories'&&x.http===200)){if(Date.now()>until)throw new Error('readonly_history_not_received');await page.waitForTimeout(40);}
 if(!proof.data_context.read_only||proof.data_context.selection_generation!==1||proof.posts.length)throw new Error('current_readonly_UI_granted_mutation');
 if(!proof.assets.some(x=>x.sha256==='58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8'))throw new Error('wrong_bundle');
 await page.screenshot({path:path.join(dir,'R02-normal-reopen-readonly-history.png'),fullPage:true});proof.status='passed';
}catch(e){proof.status='failed';proof.error=String(e);save();throw e;}
finally{closing=true;await Promise.race([Promise.allSettled([...pending]),new Promise(r=>setTimeout(r,3000))]);if(context)await context.close();if(browser)await browser.close();proof.browser_closed=true;save();process.stdin.removeAllListeners();process.stdin.pause();process.stdin.unref?.();}
