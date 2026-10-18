// TASK-100：最终 dist + 真实 API/PG 的 H1 浏览器链与重开；局部显示控制单列。
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const cp=require('node:child_process');
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base='http://127.0.0.1:18100';
const batch=process.env.RETROLUME_TASK100_BATCH_DIR;
const input=JSON.parse(fs.readFileSync(path.join(batch,'browser-input.json'),'utf8'));
const main=process.argv.includes('--main');
const controlsOnly=process.argv.includes('--controls-only');
assert.ok(!(main&&controlsOnly),'browser mode conflict');
const output=path.join(batch,main?'browser-main':controlsOnly?'browser-controls':'browser-reopen');
fs.mkdirSync(output,{recursive:true});
const timeline=[];const controls=[];
let browser,context,page;
const write=(name,value)=>fs.writeFileSync(path.join(output,name),JSON.stringify(value,null,2));
async function snapshot(name){await page.screenshot({path:path.join(output,name+'.png'),fullPage:true});}
async function api(url,body){
 const session=await context.request.get(base+'/api/session');const token=(await session.json()).token;
 const r=body?await context.request.post(base+url,{headers:{'X-RetroLume-Session':token},data:body}):await context.request.get(base+url,{headers:{'X-RetroLume-Session':token}});
 assert.equal(r.status(),200,await r.text());return r.json();
}
async function openActivity(){
 await page.goto(base,{waitUntil:'domcontentloaded'});
 await page.getByRole('button',{name:/学习活动/}).click();
 const target=page.getByRole('button').filter({hasText:input.title});
 await target.first().waitFor({state:'visible'});await target.first().click();
 await page.locator('.ws-teaching #teaching-goal').waitFor({state:'visible'});
 await page.locator('.ws-teaching').getByRole('button',{name:'刷新教学工作区（只读）',exact:true}).waitFor({state:'visible'}).catch(()=>{});
 await page.waitForFunction(()=>document.querySelector('.ws-teaching .section-title')?.textContent?.includes('修订'));
}
async function action(name){
 const button=page.locator('.ws-teaching').getByRole('button',{name,exact:true});
 await button.waitFor({state:'visible'});
 await page.waitForFunction(label=>[...document.querySelectorAll('.ws-teaching button')].some(b=>b.textContent===label&&!b.disabled),name);
 const waiting=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().includes(`/api/activities/${input.activity_id}/teaching/commands`),{timeout:110000});
 await button.click();const response=await waiting;const value=await response.json();
 assert.equal(response.status(),200,JSON.stringify(value));assert.equal(value.status,'committed',JSON.stringify(value));
 timeline.push({kind:'actual_command_receipt',name,body:response.request().postDataJSON(),receipt:value});
 await page.waitForFunction(()=>[...document.querySelectorAll('.ws-teaching textarea')].every(e=>!e.disabled));
 return value;
}
async function answer(text){await page.locator('#teaching-answer').fill(text);return action('保存作答（零费，不调用模型）');}
async function normal(){
 await openActivity();await page.locator('#teaching-goal').fill(input.goal);
 await action('保存目标（不调用模型）');await snapshot('01-goal');
 await action('生成/重订路径（1 次模型）');await snapshot('02-path-proposal');
 assert.match(await page.locator('[aria-label="学习路径"]').innerText(),/依据与理由/);
 await action('接受当前路径（零费）');await action('获取练习（1 次模型）');
 assert.match(await page.locator('[aria-label="当前练习"]').innerText(),/120/);
 assert.equal(await page.locator('[aria-label="参考要点"]').count(),0);await snapshot('03-unexposed-exercise');
 await answer('120÷2=60m/s');await snapshot('04-saved-answer');
 await action('请求评价（1 次模型）');
 for(const text of ['正确部分','实际错误','证据不足','原因假设'])assert.match(await page.locator('[aria-label="评价结果"]').innerText(),new RegExp(text));
 await snapshot('05-four-feedback-and-exposure');await action('核算参考要点（1 次有限计算）');
 await answer('120÷120=1m/s，2分钟乘60等于120秒，单位m/s，数量级合理');await action('请求评价（1 次模型）');
 let view=await api(`/api/activities/${input.activity_id}/teaching/workspace`);
 assert.equal(view.nodes.n1.independent_answers.length,0);assert.ok(view.nodes.n1.assisted.length>=1);
 await snapshot('06-assisted-continuation');
 await action('新实例复测（1 次模型）');await answer('180÷180=1m/s，3分钟=180秒，单位m/s，数量级合理');await action('请求评价（1 次模型）');
 view=await api(`/api/activities/${input.activity_id}/teaching/workspace`);assert.equal(view.nodes.n1.independent_answers.length,1);assert.equal(view.head.node_id,'n1');
 await snapshot('07-one-independent-retest');
 await action('新实例复测（1 次模型）');await answer('240÷240=1m/s，4分钟=240秒，单位m/s，数量级合理');await action('请求评价（1 次模型）');
 view=await api(`/api/activities/${input.activity_id}/teaching/workspace`);assert.equal(view.nodes.n1.independent_answers.length,2);assert.equal(view.head.node_id,'n2');
 await snapshot('08-update-reason');
 const kinds=timeline.filter(x=>x.kind==='actual_command_receipt').map(x=>x.receipt.action);
 assert.equal(kinds.filter(k=>['plan','exercise','evaluate'].includes(k)).length,8);assert.equal(kinds.filter(k=>k==='calculate').length,1);
 return {status:'pass',actual_model_actions:8,actual_tool_actions:1,workspace:view,real_chain:true};
}
async function displayControls(){
 const actual=await api(`/api/activities/${input.activity_id}/teaching/workspace`);
 const countPosts=()=>timeline.filter(x=>x.kind==='request'&&x.method==='POST'&&x.url.includes('/teaching/commands')).length;
 // 实际原生 IDB 被拒绝：输入保留且 0 POST。只拦存储，不替代服务结果。
 const before=countPosts();await page.locator('#teaching-answer').fill('浏览器保留输入');
 await page.evaluate(()=>{window.__task100Open=indexedDB.open.bind(indexedDB);indexedDB.open=()=>{throw new Error('task100 blocked native storage');};});
 await page.locator('.ws-teaching').getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}).click();
 await page.getByRole('alert').filter({hasText:'本机草稿写入失败，输入已保留，未发出任何请求'}).waitFor();
 assert.equal(countPosts(),before);assert.equal(await page.locator('#teaching-answer').inputValue(),'浏览器保留输入');
 await snapshot('13-storage-failure-zero-post');
 await page.evaluate(()=>{indexedDB.open=window.__task100Open;});
 controls.push({name:'native_idb_failure',status:'pass',zero_post:true,layer:'browser_storage'});
 // 以下仅控制显示响应：不据此签数据库 UNKNOWN/取消/源失效。
 let reads=0,active=0,maxActive=0;
 await page.route(`**/api/activities/${input.activity_id}/teaching/workspace`,async route=>{
   reads++;active++;maxActive=Math.max(maxActive,active);
   const value=structuredClone(actual);value.overlay.unknown=true;value.head.pending_business_key='display-unknown';
   try {await route.fulfill({json:value});} finally {active--;}
 });
 await page.clock.install();await page.reload();await page.getByRole('button',{name:/学习活动/}).click();
 await page.getByRole('button').filter({hasText:input.title}).first().click();
 await page.locator('#teaching-answer').waitFor();
 await page.waitForFunction(()=>document.querySelector('.ws-teaching .section-title')?.textContent?.includes('修订'));
 await page.evaluate(()=>{Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'));});
 const hiddenStart=reads;await page.clock.runFor(9000);assert.equal(reads,hiddenStart);
 await page.evaluate(()=>{Object.defineProperty(document,'hidden',{value:false,configurable:true});document.dispatchEvent(new Event('visibilitychange'));});
 await page.clock.runFor(125000);assert.ok(reads<=42);assert.equal(maxActive,1);
 const atStop=reads;await page.clock.runFor(20000);assert.equal(reads,atStop);
 assert.equal(countPosts(),before);
 controls.push({name:'unknown_bounded_single_snapshot_poll',status:'pass',reads,maximum_overlap:maxActive,zero_post:true,layer:'display_control'});
 controls.push({name:'hidden_pauses_poll',status:'pass',layer:'display_control'});
 await snapshot('14-unknown-read-only');
 await page.goto('about:blank');const unmounted=reads;await page.clock.runFor(9000);assert.equal(reads,unmounted);
 controls.push({name:'unmounted_stops_poll',status:'pass',layer:'actual_browser'});
 await page.unroute(`**/api/activities/${input.activity_id}/teaching/workspace`);await page.clock.resume();
 await page.goto(base,{waitUntil:'domcontentloaded'});await page.getByRole('button',{name:/学习活动/}).click();await page.getByRole('button').filter({hasText:input.title}).first().click();
 await page.locator('#teaching-answer').waitFor();
 const activityView=await api(`/api/activities/${input.activity_id}/teaching/workspace`);
 assert.equal(activityView.head.goal_record_id,actual.head.goal_record_id);
 controls.push({name:'reopen_only_get',status:'pass',layer:'actual_api_pg'});
 // 两个读取重叠：旧响应晚到不能覆盖正在编辑的文本或焦点。
 let release,heldReady;const held=new Promise(resolve=>heldReady=resolve);let index=0;
 await page.route(`**/api/activities/${input.activity_id}/teaching/workspace`,async route=>{
   index++;if(index===1){await new Promise(resolve=>{release=resolve;heldReady();});}
   try{await route.fulfill({json:actual});}catch{};
 });
 const refresh=page.locator('.ws-teaching').getByRole('button',{name:'刷新教学工作区（只读）',exact:true});
 await refresh.click();await held;await page.locator('#teaching-answer').fill('新编辑文本仍在');
 await refresh.click();await page.locator('#teaching-answer').focus();release();
 await page.waitForFunction(()=>document.querySelector('#teaching-answer')?.value==='新编辑文本仍在');
 assert.equal(await page.locator('#teaching-answer').inputValue(),'新编辑文本仍在');
 assert.equal(await page.evaluate(()=>document.activeElement?.id),'teaching-answer');
 await page.unroute(`**/api/activities/${input.activity_id}/teaching/workspace`);
 controls.push({name:'late_snapshot_does_not_replace_edit_or_focus',status:'pass',layer:'display_control'});
 // 同一原生存储的另一个标签页改变摘要容量，原页不得挤掉旧意图后发送。
 const second=await context.newPage();await second.goto(base);
 const old=await second.evaluate(()=>localStorage.getItem('retrolume.teaching-intents.v1'));
 await second.evaluate(aid=>localStorage.setItem('retrolume.teaching-intents.v1',JSON.stringify(Array.from({length:16},(_,i)=>({
   key:'capacity-'+i,action:'answer',activity_id:aid,head_revision:1,goal_version:1,scope_revision:1,created_at:new Date().toISOString(),state:'unconfirmed'})))),input.activity_id);
 const capacityBefore=countPosts();await page.locator('.ws-teaching').getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}).click();
 await page.getByRole('alert').filter({hasText:'本机恢复台账写入失败，未发出任何请求'}).waitFor();assert.equal(countPosts(),capacityBefore);
 assert.equal(await page.locator('#teaching-answer').inputValue(),'新编辑文本仍在');
 await second.evaluate(value=>{if(value===null)localStorage.removeItem('retrolume.teaching-intents.v1');else localStorage.setItem('retrolume.teaching-intents.v1',value);},old);
 await second.close();controls.push({name:'cross_tab_summary_capacity_preserves_input_zero_post',status:'pass',layer:'native_storage'});
 // 局部资格显示替身：真实服务端资格已由 PG/Windows 原件验证。
 let displayed=actual;
 await page.route(`**/api/activities/${input.activity_id}/teaching/workspace`,route=>route.fulfill({json:displayed}));
 for(const condition of ['source_invalid','cancelled','budget_exhausted']){
  displayed=structuredClone(actual);
  if(condition==='budget_exhausted')displayed.budgets.requests_reserved=displayed.budgets.max_requests;
  else displayed.overlay[condition]=true;
  const received=page.waitForResponse(r=>r.url().includes(`/api/activities/${input.activity_id}/teaching/workspace`));
  await refresh.click();await received;
  const evaluate=page.locator('.ws-teaching').getByRole('button',{name:'请求评价（1 次模型）',exact:true});
  await page.waitForFunction(cancelled=>{
   const buttons=[...document.querySelectorAll('.ws-teaching button')];
   return buttons.some(b=>b.textContent==='请求评价（1 次模型）'&&b.disabled)
    &&buttons.some(b=>b.textContent==='保存作答（零费，不调用模型）'&&b.disabled===cancelled);
  },condition==='cancelled');
  assert.equal(await evaluate.isDisabled(),true);
  const save=page.locator('.ws-teaching').getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true});
  assert.equal(await save.isDisabled(),condition==='cancelled');
  assert.equal(countPosts(),capacityBefore);
  controls.push({name:condition+'_action_disabled',status:'pass',zero_post:true,zero_fee_save_allowed:condition!=='cancelled',layer:'display_control'});
 }
 await page.unroute(`**/api/activities/${input.activity_id}/teaching/workspace`);
 await refresh.click();await page.waitForFunction(()=>[...document.querySelectorAll('.ws-teaching button')].some(b=>b.textContent==='请求评价（1 次模型）'&&!b.disabled));
 await snapshot('15-restored-actual-workspace');
}
async function remainingControls(){
 assert.ok(input.inherited_windows_batch,'validated Windows inheritance missing');
 await openActivity();const before=await api(`/api/activities/${input.activity_id}/teaching/workspace`);
 assert.equal(before.budgets.requests_reserved,12);assert.match(before.answer.text,/提交响应丢失/);
 await displayControls();
 const after=await api(`/api/activities/${input.activity_id}/teaching/workspace`);
 assert.deepEqual(after.budgets,before.budgets);assert.deepEqual(after.head,before.head);
 // 原生键盘、UTF-8与HTML文本显示；唯一新增服务器动作是零费用户纠错。
 const correction='用户补充：单位解释待核对。中文🙂 <script>window.__task100Executed=true</script>';
 await page.locator('#teaching-correction').fill(correction);await page.locator('#teaching-correction').focus();
 await page.keyboard.press('Tab');
 assert.match(await page.evaluate(()=>document.activeElement?.textContent??''),/提交纠错/);
 const receipt=await action('提交纠错（零费）');
 const corrected=await api(`/api/activities/${input.activity_id}/teaching/workspace`);
 assert.equal(receipt.action,'correct');assert.deepEqual(corrected.budgets,before.budgets);
 assert.equal(corrected.reason.kind,'correction');assert.equal(corrected.reason.text,correction);
 assert.equal(await page.evaluate(()=>window.__task100Executed),undefined);
 assert.match(await page.getByLabel('更新或保留理由').innerText(),/用户补充/);
 await snapshot('16-zero-fee-correction-literal-text');
 controls.push({name:'actual_zero_fee_correction_keyboard_utf8_and_literal_html',status:'pass',record_ids:receipt.record_ids,layer:'actual_api_pg'});
 return {status:'pass',actual_model_actions:0,actual_tool_actions:0,actual_local_actions:1,workspace:corrected,controls,
   inherited_windows_batch:input.inherited_windows_batch,real_chain:true};
}
async function reopen(){
 await openActivity();let before=await api(`/api/activities/${input.activity_id}/teaching/workspace`);
 assert.equal(before.head.node_id,'n2');assert.equal(before.budgets.requests_reserved,8);await snapshot('09-reopened-h1');
 // 原 H1 已建立 n1 的前置证据，真实 UI 获取另外两类练习及反馈。
 await action('获取练习（1 次模型）');assert.match(await page.locator('[aria-label="当前练习"]').innerText(),/concept/);
 await answer('A100/B50，全部成功或全部不生效，原子性不能单独保证隔离，资料未给级别');await action('请求评价（1 次模型）');
 await snapshot('10-concept-feedback');
 await action('选择节点 n3（保留当前题为历史）');await action('获取练习（1 次模型）');
 assert.match(await page.locator('[aria-label="当前练习"]').innerText(),/program/);
 await answer('返回2，0也满足value>0并被计数');await action('请求评价（1 次模型）');await snapshot('11-program-partial-correct');
 let after=await api(`/api/activities/${input.activity_id}/teaching/workspace`);assert.equal(after.budgets.requests_reserved,12);
 assert.equal(after.nodes.n3.status,'needs_repair');
 await page.reload();await openActivity();
 assert.match(await page.getByLabel('已保存作答').innerText(),/0也满足/);
 await snapshot('12-reopened-saved-answer');
 const detailButtons=page.locator('.ws-history').getByRole('button',{name:'查看记录',exact:true});
 await detailButtons.first().click();await page.getByLabel('历史记录正文').waitFor();
 assert.ok(await page.getByLabel('历史记录正文').innerText());
 // 真正服务端已提交、仅浏览器响应丢失：重开只 GET 恢复已保存作答。
 const commands=`**/api/activities/${input.activity_id}/teaching/commands`;let committed;
 await page.route(commands,async route=>{const response=await route.fetch();assert.equal(response.status(),200);committed=await response.json();await route.abort('failed');});
 await page.locator('#teaching-answer').fill('提交响应丢失后的已保存作答');
 await page.locator('.ws-teaching').getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}).click();
 await page.getByText(/结果未确认（连接中断）；输入已保留/).waitFor();assert.equal(committed.status,'committed');
 await page.unroute(commands);await page.reload();await openActivity();
 assert.match(await page.getByLabel('已保存作答').innerText(),/提交响应丢失/);
 const posts=timeline.filter(x=>x.kind==='request'&&x.method==='POST'&&x.url.includes('/teaching/commands')).length;
 await page.locator('.ws-intent').getByRole('button',{name:'核对（只读）',exact:true}).first().click();
 await page.getByText(/已只读核对：匹配同一持久命令/).waitFor();
 assert.equal(timeline.filter(x=>x.kind==='request'&&x.method==='POST'&&x.url.includes('/teaching/commands')).length,posts);
 controls.push({name:'actual_commit_response_loss_reopen_and_read_only_reconcile',status:'pass',record_ids:committed.record_ids,layer:'actual_api_pg_response_loss'});
 await displayControls();
 return {status:'pass',actual_model_actions:4,actual_tool_actions:0,workspace:after,controls,real_chain:true};
}
(async()=>{
 let result={status:'fail'};
 try{
  assert.equal(process.env.RETROLUME_TASK100_FIXTURE,'TASK-100-continuation-02-20261004');
  assert.ok(fs.existsSync(chromium.executablePath()),'existing chromium runtime missing');
  const python=path.resolve(__dirname,'../../backend/.venv/Scripts/python.exe');
  const counter=cp.spawnSync(python,['-B','-m','tests.fixtures.task100.browser_budget'],{cwd:path.resolve(__dirname,'../../backend'),env:process.env,encoding:'utf8',timeout:10000});
  assert.equal(counter.status,0,counter.stderr);
  browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1']});
  context=await browser.newContext({viewport:{width:1366,height:900}});page=await context.newPage();page.setDefaultTimeout(30000);
  await context.route('**/*',route=>{const url=new URL(route.request().url());return url.hostname==='127.0.0.1'||url.protocol==='data:'?route.continue():route.abort();});
  page.on('request',r=>{if(r.url().startsWith(base))timeline.push({kind:'request',method:r.method(),url:r.url(),at:Date.now(),body:r.method()==='POST'?r.postData():null});});
  page.on('pageerror',e=>timeline.push({kind:'pageerror',message:e.message}));
  result=main?await normal():controlsOnly?await remainingControls():await reopen();
  assert.equal(timeline.filter(x=>x.kind==='pageerror').length,0);
 }catch(error){
  result={status:'fail',error:error.stack,controls};console.error(error.stack);
  if(page&&!page.isClosed()){
   try{fs.writeFileSync(path.join(output,'failure-dom.html'),await page.content());await snapshot('failure');}
   catch(captureError){result.failure_capture_error=String(captureError);}
  }
 }
 finally{
  try{if(context)await context.close();}finally{if(browser)await browser.close();}
  write('timeline.json',timeline);write('facts.json',result);console.log(JSON.stringify(result));
 }
 process.exitCode=result.status==='pass'?0:1;
})();
