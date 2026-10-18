// Final dist + native Chromium/IDB/Web Locks. All API responses are labelled
// readonly snapshots; no HTTP server/listener, POST, model/tool or business write.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const assert=require('node:assert/strict');const {chromium}=require('playwright');
const batch=process.env.RETROLUME_TASK100_BATCH_DIR,base='http://127.0.0.1:18100';
const input=JSON.parse(fs.readFileSync(path.join(batch,'readonly-browser-input.json'),'utf8'));
const output=path.join(batch,'readonly-browser'),dist=path.resolve(__dirname,'../dist');fs.mkdirSync(output,{recursive:true});
const OWNER='retrolume.teaching-editor-owner.v1',aid=input.ui.activity_id;
const timeline=[],checks=[],assets=[],requests=[],pendingAssets=[];let browser,context,page,state='A1';
const write=(name,value)=>fs.writeFileSync(path.join(output,name),JSON.stringify(value,null,2));
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function capture(name){await page.screenshot({path:path.join(output,name+'.png'),fullPage:true});}
async function drafts(where=page){return where.evaluate(()=>new Promise((resolve,reject)=>{
 const request=indexedDB.open('retrolume-teaching');request.onerror=()=>reject(request.error);
 request.onsuccess=()=>{const db=request.result,tx=db.transaction('drafts','readonly'),read=tx.objectStore('drafts').getAll();
 read.onsuccess=()=>{resolve(read.result);db.close();};read.onerror=()=>{reject(read.error);db.close();};};
}));}
async function stored(predicate,where=page){
 for(let i=0;i<60;i++){const rows=await drafts(where);if(predicate(rows))return rows;await pause(50);}
 throw new Error('bounded native IndexedDB assertion timed out');
}
function bodyFor(url){
 const pathname=url.pathname;
 if(pathname==='/api/session')return {token:'task100-labelled-readonly-snapshot-context',storage_configured:true,max_bytes:5242880};
 if(pathname===`/api/activities/${aid}/teaching/workspace`)return input[`workspace_${state}`];
 if(pathname===`/api/activities/${aid}/teaching/history`)return input.history_pages[state];
 return input.routes[pathname];
}
async function readonlyRoute(route){
 const request=route.request(),url=new URL(request.url());
 if(url.origin!==base){requests.push({url:request.url(),method:request.method(),grade:'blocked_outside_virtual_origin'});return route.abort();}
 requests.push({path:url.pathname+url.search,method:request.method(),state,grade:'labelled_readonly_route_replay'});
 if(request.method()!=='GET')return route.fulfill({status:405,json:{detail:{code:'readonly_fixture',message:'只读验证不允许写入'}}});
 if(url.pathname.startsWith('/api/')){
  const value=bodyFor(url);if(value===undefined)return route.fulfill({status:404,json:{detail:{code:'unmapped_snapshot',message:url.pathname}}});
  return route.fulfill({status:200,contentType:'application/json',headers:{'Cache-Control':'no-store'},body:JSON.stringify(value)});
 }
 const relative=url.pathname==='/'?'index.html':url.pathname.slice(1),file=path.resolve(dist,relative);
 assert.ok(file===dist||file.startsWith(dist+path.sep),'dist traversal refused');
 if(!fs.existsSync(file))return route.fulfill({status:url.pathname==='/favicon.ico'?204:404,body:''});
 const type={'.html':'text/html','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2'}[path.extname(file)]||'application/octet-stream';
 return route.fulfill({status:200,contentType:type,body:fs.readFileSync(file)});
}
async function openActivity(target,where=page){
 if(!where.url().startsWith(base))await where.goto(base,{waitUntil:'domcontentloaded'});
 await where.getByRole('button',{name:/学习活动/}).click();
 const button=where.locator('button.material').filter({hasText:target.title});await button.first().waitFor();await button.first().click();
 await where.locator('.ws-teaching #teaching-goal').waitFor();
 await where.waitForFunction(()=>document.querySelector('.ws-teaching .section-title')?.textContent?.includes('修订'));
 await where.waitForFunction(()=>!!document.querySelector('#teaching-goal')&&!document.querySelector('#teaching-goal').disabled);
}
const refresh=where=>where.getByRole('button',{name:'刷新教学工作区（只读）',exact:true}).click();
const bindingOf=snap=>({activity_id:aid,goal_record_id:snap.head.goal_record_id,path_record_id:snap.head.path_record_id,
 node_id:snap.head.node_id,exercise_record_id:snap.head.exercise_record_id,answer_record_id:snap.head.answer_record_id,head_revision:snap.head.revision});
function checkBinding(row,snapshot,owner){for(const [key,value] of Object.entries(bindingOf(snapshot)))assert.equal(row[key],value,key);assert.equal(row.editor_owner_id,owner);}
async function seedAndCitations(){
 await openActivity({title:input.seed.source.title});
 await page.locator('.ws-op').filter({hasText:input.seed.operation_id}).click();
 await page.getByRole('button',{name:'沿用此目标',exact:true}).click();
 await page.waitForFunction(goal=>document.querySelector('#teaching-goal')?.value===goal,input.seed.goal);
 await capture('01-readonly-explicit-seed');
 checks.push({name:'explicit_seed_selection_no_automatic_POST',status:'pass',grade:'labelled_readonly_snapshot_UI'});
 await openActivity(input.ui);
 for(const label of ['路径 n1','参考 p1','正确部分 1']){
  const area=page.getByLabel(label+'依据',{exact:true});await area.getByRole('button').first().click();
  const text=area.getByLabel('教学引用原文',{exact:true});await text.waitFor();assert.match(await text.innerText(),/平均速度/);
 }
 await capture('02-own-record-native-PG-citation-snapshots');
 checks.push({name:'final_bundle_own_record_path_reference_feedback_citations',status:'pass',grade:'native_PG_projection_readonly_UI_replay'});
}
async function twoTabDrafts(){
 const a1=input.workspace_A1,a2=input.workspace_A2;
 const owner1=await page.evaluate(key=>sessionStorage.getItem(key),OWNER);assert.match(owner1,/^[0-9a-f-]{36}$/);
 const first='第一页 A1 未保存文字：120米 / 2分钟，保留这个编辑身份';
 await page.locator('#teaching-answer').fill(first);
 let rows=await stored(items=>items.some(d=>d.content===first&&d.editor_owner_id===owner1));
 const firstDraft=rows.find(d=>d.content===first&&d.editor_owner_id===owner1);checkBinding(firstDraft,a1,owner1);
 const second=await context.newPage();second.setDefaultTimeout(20000);await second.goto(base,{waitUntil:'domcontentloaded'});
 // Reproduce sessionStorage cloning, which a duplicated/opener tab may perform.
 await second.evaluate(({key,value})=>sessionStorage.setItem(key,value),{key:OWNER,value:owner1});
 await openActivity(input.ui,second);
 const owner2=await second.evaluate(key=>sessionStorage.getItem(key),OWNER);assert.notEqual(owner2,owner1,'live owner lock must separate cloned tabs');
 const other='第二页独立 A1 草稿：不覆盖第一页';await second.locator('#teaching-answer').fill(other);
 rows=await stored(items=>items.some(d=>d.content===other&&d.editor_owner_id===owner2));
 const secondDraft=rows.find(d=>d.content===other&&d.editor_owner_id===owner2);checkBinding(secondDraft,a1,owner2);
 assert.equal(rows.find(d=>d.draft_id===firstDraft.draft_id).content,first);
 assert.notEqual(firstDraft.draft_id,secondDraft.draft_id);
 checks.push({name:'cloned_sessionStorage_owner_collision_and_two_native_IDB_slots',status:'pass',grade:'actual_Chromium_WebLocks_sessionStorage_IDB',firstDraft,secondDraft});
 state='A2';await refresh(second);await refresh(page);
 for(const [where,text] of [[page,first],[second,other]]){
  await where.getByRole('alert',{name:'作答身份变化',exact:true}).waitFor();assert.equal(await where.locator('#teaching-answer').inputValue(),text);
  assert.equal(await where.getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}).isDisabled(),true);
  assert.equal(await where.getByRole('button',{name:'提交修正版（零费）',exact:true}).isDisabled(),true);
 }
 rows=await drafts();assert.equal(rows.find(d=>d.draft_id===firstDraft.draft_id).content,first);assert.equal(rows.find(d=>d.draft_id===secondDraft.draft_id).content,other);
 await capture('03-A1-A2-two-tab-warning-disabled-retained');
 await page.getByRole('button',{name:'载入当前作答（保留旧草稿）',exact:true}).click();
 assert.equal(await page.locator('#teaching-answer').inputValue(),String(a2.answer.text));
 assert.equal((await drafts()).find(d=>d.draft_id===firstDraft.draft_id).content,first);
 await second.getByRole('button',{name:'明确沿用草稿到当前作答',exact:true}).click();assert.equal(await second.locator('#teaching-answer').inputValue(),other);
 assert.equal(await second.getByRole('alert',{name:'作答身份变化',exact:true}).count(),0);
 // Typing after explicit rebinding persists under A2 without rewriting A1 slots.
 const latest='第一页 A2 新草稿：重新载入仍属于本标签页';await page.locator('#teaching-answer').fill(latest);
 rows=await stored(items=>items.some(d=>d.content===latest&&d.editor_owner_id===owner1));
 const currentDraft=rows.find(d=>d.content===latest);checkBinding(currentDraft,a2,owner1);
 await page.reload({waitUntil:'domcontentloaded'});await openActivity(input.ui);
 assert.equal(await page.evaluate(key=>sessionStorage.getItem(key),OWNER),owner1,'reload keeps released owner identity');
 await page.waitForFunction(value=>document.querySelector('#teaching-answer')?.value===value,latest);
 rows=await drafts();assert.equal(rows.find(d=>d.draft_id===firstDraft.draft_id).content,first);assert.equal(rows.find(d=>d.draft_id===secondDraft.draft_id).content,other);
 await capture('04-owner-and-A2-draft-reload-restored');
 checks.push({name:'same_exercise_A1_A2_conflict_explicit_rebind_old_drafts_reload',status:'pass',grade:'actual_native_storage_UI_recorded_actual_HTTP_snapshots',a1_head:a1.head,a2_head:a2.head,currentDraft});
 write('drafts.json',rows);await second.close();
}
async function historyAndUnmount(){
 await page.getByRole('button',{name:'查看更早历史（只读）',exact:true}).click();
 await page.waitForFunction(()=>document.querySelectorAll('.ws-history li').length>20);
 const r1=input.records.find(r=>r.kind==='path_accept'),r2=input.records.find(r=>r.kind==='feedback');assert.ok(r1&&r2);
 const target=`**/api/activities/${aid}/teaching/records/${r1.record_id}`;
 let release,startedResolve;let started=new Promise(resolve=>startedResolve=resolve),gate=new Promise(resolve=>release=resolve);
 await page.route(target,async route=>{startedResolve();await gate;
  try{await route.fulfill({status:200,json:input.routes[new URL(route.request().url()).pathname]});}catch(error){timeline.push({kind:'cancelled_readonly_delivery',message:String(error)});}});
 await page.getByRole('button',{name:`查看记录 · ${r1.seq}`,exact:true}).click();await started;
 await page.getByRole('button',{name:`查看记录 · ${r2.seq}`,exact:true}).click();
 const detail=page.getByLabel('历史记录正文',{exact:true});await detail.waitFor();assert.equal(await detail.getAttribute('data-record-id'),r2.record_id);
 release();await pause(650);assert.equal(await detail.getAttribute('data-record-id'),r2.record_id);await page.unroute(target);
 await page.locator('#teaching-correction').fill('明确选择 R2，迟到 R1 仍不更换所选正文');
 await capture('05-late-R1-cannot-replace-R2');
 checks.push({name:'history_over20_and_R1_R2_late_selection',status:'pass',grade:'native_browser_controlled_readonly_deliveries',r1,r2,
  real_correction_target_write_proof_reused_from:input.source_batch+'/repair-browser/facts.json'});
 started=new Promise(resolve=>startedResolve=resolve);gate=new Promise(resolve=>release=resolve);
 await page.route(target,async route=>{startedResolve();await gate;
  try{await route.fulfill({status:200,json:input.routes[new URL(route.request().url()).pathname]});}catch(error){timeline.push({kind:'cancelled_unmounted_record',message:String(error)});}});
 await page.getByRole('button',{name:`查看记录 · ${r1.seq}`,exact:true}).click();await started;
 await openActivity({title:input.seed.source.title});release();await pause(650);await page.unroute(target);
 assert.equal(await page.locator('[data-record-id]').count(),0);assert.equal(await page.locator('#teaching-answer').inputValue(),'');
 assert.equal(await page.locator('#teaching-goal').inputValue(),input.seed.goal);
 checks.push({name:'unmounted_history_reply_cannot_pollute_next_activity',status:'pass',grade:'native_browser_controlled_readonly_deliveries'});
 await openActivity(input.ui);
 const workspaceTarget=`**/api/activities/${aid}/teaching/workspace`;
 started=new Promise(resolve=>startedResolve=resolve);gate=new Promise(resolve=>release=resolve);
 await page.route(workspaceTarget,async route=>{startedResolve();await gate;
  try{await route.fulfill({status:200,json:input.workspace_A2});}catch(error){timeline.push({kind:'cancelled_unmounted_workspace',message:String(error)});}});
 await refresh(page);await started;await openActivity({title:input.seed.source.title});release();await pause(650);await page.unroute(workspaceTarget);
 assert.equal(await page.locator('#teaching-answer').inputValue(),'');assert.equal(await page.getByLabel('已保存作答',{exact:true}).count(),0);
 await capture('06-switch-aborts-old-workspace-and-record');
 checks.push({name:'unmounted_workspace_reply_cannot_pollute_next_activity',status:'pass',grade:'native_browser_controlled_readonly_deliveries'});
}
(async()=>{
 let result={status:'fail'};
 try{
  assert.equal(process.env.RETROLUME_TASK100_FIXTURE,'TASK-100-audit-repair-03-20261005');assert.equal(input.status,'pass');assert.ok(fs.existsSync(chromium.executablePath()));
  const python=path.resolve(__dirname,'../../backend/.venv/Scripts/python.exe');
  const counter=cp.spawnSync(python,['-B','-m','tests.fixtures.task100.browser_budget'],{cwd:path.resolve(__dirname,'../../backend'),env:process.env,encoding:'utf8',timeout:10000});assert.equal(counter.status,0,counter.stderr);
  browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1']});
  context=await browser.newContext({viewport:{width:1366,height:950}});await context.route('**/*',readonlyRoute);page=await context.newPage();page.setDefaultTimeout(20000);
  const listen=p=>p.on('pageerror',e=>timeline.push({kind:'pageerror',message:e.message}));listen(page);context.on('page',listen);
  context.on('response',r=>{if(r.url().includes('/assets/')&&r.status()===200)pendingAssets.push((async()=>{
   const bytes=await r.body();assets.push({url:r.url(),sha256:crypto.createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length,
    grade:'final_dist_bytes_intercepted_without_application_server'});
  })().catch(error=>timeline.push({kind:'asset_capture_error',message:String(error)})));});
  await seedAndCitations();await twoTabDrafts();await historyAndUnmount();
  assert.equal(requests.filter(r=>r.method!=='GET').length,0,'all UI actions in this session must stay readonly');
  assert.equal(requests.filter(r=>r.grade==='blocked_outside_virtual_origin').length,0);
  assert.equal(timeline.filter(r=>r.kind==='pageerror'||r.kind==='asset_capture_error').length,0);
  await Promise.all(pendingAssets);
  for(const asset of assets){const file=path.join(dist,new URL(asset.url).pathname.slice(1));assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),asset.sha256);}
  assert.ok(assets.some(a=>a.url.endsWith('.js')),'final bundle bytes missing');
  result={status:'pass',checks,assets,requests:requests.length,POSTs:0,application_starts:0,SUP_calls:0,business_writes:0,
   grade:input.browser_grade,snapshot_controls:input.snapshot_controls,no_new_HTTP_auth_proof:true};
 }catch(error){result={status:'fail',error:error.stack,checks};console.error(error.stack);
  if(page&&!page.isClosed()){try{fs.writeFileSync(path.join(output,'failure-dom.html'),await page.content());await capture('failure');}catch(e){result.capture_error=String(e);}}
 }finally{
  try{if(context)await context.close();}finally{if(browser)await browser.close();}
  write('requests.json',requests);write('timeline.json',timeline);write('served-assets.json',assets);write('facts.json',result);console.log(JSON.stringify(result));
 }
 process.exitCode=result.status==='pass'?0:1;
})();
