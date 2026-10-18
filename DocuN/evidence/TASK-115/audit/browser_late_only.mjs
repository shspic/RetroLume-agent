import fs from 'node:fs';
import path from 'node:path';
import cp from 'node:child_process';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const [root,out,profile]=process.argv.slice(2);
const write=(name,value)=>fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2));
const old={control_id:'11500000-0000-4000-8000-000000000003',selection_generation:0,
  dataset_id:'11500000-0000-4000-8000-000000000004',instance_id:'11500000-0000-4000-8000-000000000005',current_mode:'normal',read_only:false};
const newer={...old,selection_generation:1,dataset_id:'11500000-0000-4000-8000-000000000006',
  instance_id:'11500000-0000-4000-8000-000000000007',current_mode:'restored_readonly',read_only:true};
const cap=ctx=>({...ctx,format:'data_exit.v1.r01',backup_available:true,restore_executor_configured:false,source_delete_available:false});
const spawn=cp.spawn;cp.spawn=function(command,args,options){const child=spawn(command,args,options);if(/chrome|chromium/i.test(command))process.stdout.write(JSON.stringify({event:'browser_spawn',pid:child.pid,executable:command})+'\n');return child;};
const {chromium}=await import(pathToFileURL(path.join(root,'frontend/node_modules/playwright/index.mjs')).href);
const context=await chromium.launchPersistentContext(profile,{headless:true,viewport:{width:1365,height:1050}});
const requests=[],errors=[];let active=false,first=null,count=0,released=false;const held=[];
try{
  const page=context.pages()[0];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async route=>{
    const request=route.request(),url=new URL(request.url()),name=url.pathname;
    requests.push({method:request.method(),path:name,data_context_header:request.headers()['x-retrolume-data-context']??null});
    if(url.hostname!=='127.0.0.1')throw new Error('本卡不允许外部 URL');
    if(name==='/'||name==='/assets/index-CJ8Yp7JQ.js'||name==='/assets/index-Ccc1_Rok.css'){
      const file=path.join(root,'frontend/dist',name==='/'?'index.html':name.slice(1));
      return route.fulfill({body:fs.readFileSync(file),contentType:name==='/'?'text/html':name.endsWith('.js')?'application/javascript':'text/css'});
    }
    if(name==='/api/session')return route.fulfill({json:{token:'task115-frontend-only',storage_configured:true,max_bytes:5242880,data_context:old}});
    if(name==='/api/data/capabilities'){
      if(!active)return route.fulfill({json:cap(old)});
      count++;
      if(count===1){first=route;return;}
      if(released){held.push(route);return;}
      return route.fulfill({json:cap(newer)});
    }
    if(name==='/api/materials'||name==='/api/activities'||name==='/api/pdf-candidates')return route.fulfill({json:{items:[],next_offset:null}});
    if(name==='/api/data/saved-records')return route.fulfill({json:{items:[],next_offset:null}});
    return route.fulfill({status:404,json:{code:'not_found'}});
  });
  await page.goto('http://127.0.0.1:18115/',{waitUntil:'networkidle'});
  await page.getByRole('button',{name:'数据与备份',exact:true}).click();
  await page.getByRole('button',{name:'只读刷新进度',exact:true}).waitFor();
  await page.waitForTimeout(100);active=true;
  await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();
  for(let i=0;i<40&&!first;i++)await page.waitForTimeout(20);
  assert.ok(first);
  await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();
  const notice='当前仅供只读查看，旧调用、工具和预览的执行资格未恢复。原数据保留，持续使用需后续验收。';
  await page.getByText(notice,{exact:true}).waitFor();
  fs.writeFileSync(path.join(out,'01-new-context-dom.txt'),await page.locator('body').innerText());
  await page.screenshot({path:path.join(out,'01-new-context.png'),fullPage:true});
  released=true;await first.fulfill({json:cap(old)});await page.waitForTimeout(250);
  const reverted=await page.getByText(notice,{exact:true}).count()===0;
  fs.writeFileSync(path.join(out,'02-old-context-dom.txt'),await page.locator('body').innerText());
  await page.screenshot({path:path.join(out,'02-old-context.png'),fullPage:true});
  write('result.json',{layer:'真实 Chromium/冻结最终 bundle，所有 HTTP 响应由路由夹具提供；没有 TCP 服务或真实 selector 切换',
    old_context:old,new_context:newer,late_old_response_reverted_context:reverted,requests,errors,
    job_post_count:requests.filter(r=>r.method==='POST').length});
  assert.equal(reverted,true);assert.equal(errors.length,0);
  for(const route of held)await route.abort('aborted');
}catch(error){write('failure.json',{type:error.name,message:error.message,requests,errors});throw error;}
finally{await context.close();process.stdout.write(JSON.stringify({event:'browser_closed',confirmed:true})+'\n');}
