import fs from 'node:fs';
import path from 'node:path';
import cp from 'node:child_process';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const [root,out,profile]=process.argv.slice(2);
const save=(name,value)=>fs.writeFileSync(path.join(out,name+'.json'),JSON.stringify(value,null,2),{flag:'wx'});
const old={control_id:'33300000-0000-4000-8000-000000000001',selection_generation:0,dataset_id:'33300000-0000-4000-8000-000000000002',instance_id:'33300000-0000-4000-8000-000000000003',current_mode:'normal',read_only:false};
const next={...old,selection_generation:1,dataset_id:'33300000-0000-4000-8000-000000000004',instance_id:'33300000-0000-4000-8000-000000000005',current_mode:'restored_readonly',read_only:true};
const uuid=n=>'33300000-0000-4000-8000-'+String(n).padStart(12,'0');
const hash=value=>createHash('sha256').update(value).digest('hex');
const respect='respect_current_deletions',snapshot='snapshot_only_readonly';
const spawn=cp.spawn;cp.spawn=function(command,args,options){const child=spawn(command,args,options);if(/chrome|chromium/i.test(command))process.stdout.write(JSON.stringify({event:'browser_spawn',pid:child.pid})+'\n');return child;};
const {chromium}=await import(pathToFileURL(path.join(root,'frontend/node_modules/playwright/index.mjs')).href);
const browser=await chromium.launchPersistentContext(profile,{headless:true,viewport:{width:1365,height:1050},serviceWorkers:'block',acceptDownloads:true});
const requests=[],errors=[],cases=[],pending=[],sequence=[];let active=old,phase='initial',hold=null,serial=100,overlay=1,latest='known';
const jobs=new Map(),plans=new Map();
const assets=fs.readdirSync(path.join(root,'frontend/dist/assets')).map(name=>'assets/'+name);
const finalIdentity=['frontend/src/data/DataWorkspace.tsx','frontend/tests/task114-c03-inputs.mjs','frontend/dist/index.html',...assets.map(name=>'frontend/dist/'+name)].map(name=>({path:name,sha256:hash(fs.readFileSync(path.join(root,name)))}));
const cap=()=>({...active,backup_available:true,restore_executor_configured:true,source_delete_available:!active.read_only});
async function release(route,body,ctx=active){try{await route.fulfill({json:body,headers:{'X-RetroLume-Data-Context':JSON.stringify(ctx,Object.keys(ctx).sort())}});return 'fulfilled';}catch{return 'already_aborted';}}
async function holdOrRelease(kind,route,body){if(hold===kind){hold=null;pending.push({kind,route,body,context:{...active}});sequence.push({event:'held',kind,phase,body});return;}return release(route,body);}
async function awaitHeld(kind){for(let n=0;n<200&&!pending.some(item=>item.kind===kind);n++)await new Promise(resolve=>setTimeout(resolve,5));assert.ok(pending.some(item=>item.kind===kind),'未到达精确挂起点 '+kind);}
async function finishHeld(kind){const index=pending.findIndex(item=>item.kind===kind);assert.notEqual(index,-1);const [item]=pending.splice(index,1);const result=await release(item.route,item.body,item.context);sequence.push({event:'released',kind,phase,result,body:item.body});return item.body;}
try{
 const page=browser.pages()[0];page.setDefaultTimeout(5000);page.on('pageerror',e=>errors.push(e.message));
 await browser.route('**/*',async route=>{
  const request=route.request(),url=new URL(request.url()),name=url.pathname,method=request.method();
  let body=null;if(method==='POST'&&name!=='/api/data/uploads')body=request.postDataJSON();
  const entry={seq:requests.length+1,method,path:name,query:url.search,body,phase,context:JSON.parse(request.headers()['x-retrolume-data-context']??'null')};requests.push(entry);
  if(url.protocol!=='http:'||url.hostname!=='127.0.0.1'||url.port!=='18114'){
    errors.push('禁止URL '+request.url());return route.abort('blockedbyclient');
  }
  if(method==='GET'&&(name==='/'||assets.includes(name.slice(1)))){
    const file=path.join(root,'frontend/dist',name==='/'?'index.html':name.slice(1));
    return route.fulfill({body:fs.readFileSync(file),contentType:name==='/'?'text/html':name.endsWith('.css')?'text/css':'application/javascript'});
  }
  if(method==='GET'&&name==='/api/session')return route.fulfill({json:{token:'c03-route-session',storage_configured:true,max_bytes:5242880,data_context:old}});
  if(method==='GET'&&name==='/api/data/capabilities')return release(route,cap());
  if(method==='GET'&&name==='/api/materials')return release(route,{items:[{id:uuid(20),title:'C03 source A',revision:1,version_id:uuid(21),format:'md',size:12,created_at:'2026-10-14T00:00:00Z'},{id:uuid(22),title:'C03 source B',revision:1,version_id:uuid(23),format:'md',size:12,created_at:'2026-10-14T00:00:00Z'}],next_offset:null});
  if(method==='GET'&&name==='/api/activities')return release(route,{items:[{id:uuid(30),activity_id:uuid(30)},{id:uuid(31),activity_id:uuid(31)}],next_offset:null});
  if(method==='GET'&&name==='/api/pdf-candidates')return release(route,{items:[],next_offset:null});
  if(method==='GET'&&name==='/api/activities/capabilities')return release(route,{enabled:false});
  if(method==='POST'&&name==='/api/data/uploads'){
    entry.bytes=request.postDataBuffer()?.length;const expected=url.searchParams.get('expected_sha256');assert.equal(expected,hash(request.postDataBuffer()));
    const upload_id=url.searchParams.get('upload_id'),business_key=url.searchParams.get('business_key');
    jobs.set(business_key,{job_id:uuid(serial++),business_key,kind:'upload',state:'received',stage:'received',revision:3});
    return holdOrRelease('upload',route,{upload_id});
  }
  if(method==='POST'&&name==='/api/data/restore-plans'){
    assert.ok([respect,snapshot].includes(body.deletion_policy));
    const plan_id=uuid(serial++),value={plan_id,deletion_policy:body.deletion_policy,plan_sha256:hash(plan_id+'plan'),package_root_sha256:hash(body.upload_id+'root'),latest_status:latest,overlay_count:overlay,executor_configured:true,permanent_readonly:true};
    plans.set(plan_id,value);return holdOrRelease('plan',route,value);
  }
  if(method==='POST'&&name==='/api/data/restore-jobs'){
    const plan=plans.get(body.plan_id);assert.ok(plan);assert.equal(body.expected_plan_sha256,plan.plan_sha256);assert.equal(body.confirm,true);
    const value={job_id:uuid(serial++),business_key:body.business_key,kind:'restore',state:'verified',stage:'verified',revision:4,plan_id:plan.plan_id,target_id:uuid(serial++)};jobs.set(body.business_key,value);
    return holdOrRelease('verify',route,value);
  }
  if(method==='POST'&&/^\/api\/data\/restore-jobs\/[^/]+\/activate-readonly$/.test(name))return release(route,{state:'active_readonly'});
  if(method==='POST'&&name==='/api/data/scope-preview'){
    const markers=[...(body.scope.source_ids??[]),...(body.scope.activity_ids??[])].join(',');
    return holdOrRelease('scope',route,{closure_sha256:hash(markers),materials:[{title:'SCOPE '+markers}],activity_count:(body.scope.activity_ids??[]).length});
  }
  if(method==='POST'&&name==='/api/data/jobs'){
    assert.equal(body.kind,'portable_export');assert.equal(body.confirm,true);
    const expected=hash([...(body.scope.source_ids??[]),...(body.scope.activity_ids??[])].join(','));assert.equal(body.scope.expected_closure_sha256,expected);
    const value={job_id:uuid(serial++),business_key:body.business_key,kind:body.kind,state:'published',stage:'published',revision:3};jobs.set(body.business_key,value);return release(route,value);
  }
  if(method==='GET'&&name.startsWith('/api/data/jobs/by-key/'))return release(route,jobs.get(decodeURIComponent(name.split('/').at(-1)))??{state:'failed',stage:'failed'});
  if(method==='GET'&&name.startsWith('/api/data/restore-plans/'))return holdOrRelease('get_plan',route,plans.get(name.split('/').at(-1)));
  if(method==='GET'&&name==='/api/data/saved-records')return release(route,{items:[],next_offset:null});
  errors.push('非白名单请求 '+method+' '+name);return route.abort('blockedbyclient');
 });
 await page.goto('http://127.0.0.1:18114/',{waitUntil:'networkidle'});
 const policy=page.getByLabel('删除处理',{exact:true}),file=page.getByLabel('选择备份文件',{exact:true}),verify=page.getByRole('button',{name:'确认验证这个备份',exact:true}),activate=page.getByRole('button',{name:'切换为当前只读数据',exact:true});
 const confirm=page.getByLabel('确认旧备份可能重新显示已删除内容，仅限隔离只读副本；源墓碑保留',{exact:true});
 const preview=page.getByRole('button',{name:'核对自动加入的证据依赖',exact:true}),exportButton=page.getByRole('button',{name:'导出这些已保存内容',exact:true});
 const workspace=async()=>{await page.getByRole('button',{name:'数据与备份',exact:true}).click();await policy.waitFor();await file.waitFor({state:'visible'});await page.getByRole('button',{name:'核对删除影响',exact:true}).first().waitFor();};
 const settle=async()=>{await page.waitForTimeout(80);};
 const noPlan=async()=>{await settle();assert.equal(await verify.count(),0);assert.equal(await activate.count(),0);};
 const uploadFile=async name=>{assert.equal(await file.isEnabled(),true);await file.setInputFiles({name:name+'.rldata',mimeType:'application/octet-stream',buffer:Buffer.from('C03-'+name)});};
 const snap=async()=>{await policy.selectOption(snapshot);assert.equal(await file.isDisabled(),true);await confirm.check();assert.equal(await file.isEnabled(),true);};
 const observe=async name=>{fs.writeFileSync(path.join(out,name+'-dom.txt'),await page.locator('body').innerText());await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});save(name,{phase,policy:await policy.inputValue(),verify_count:await verify.count(),verify_enabled:await verify.count()?await verify.isEnabled():false,export_enabled:await exportButton.isEnabled(),post_counts:requests.filter(r=>r.method==='POST').length});};
 const count=pathName=>requests.filter(r=>r.method==='POST'&&r.path===pathName).length;
 await workspace();
 phase='upload-pending-policy-change';await snap();hold='upload';await uploadFile('snapshot-upload-late');await awaitHeld('upload');const planCount=count('/api/data/restore-plans');await policy.selectOption(respect);await finishHeld('upload');await noPlan();assert.equal(count('/api/data/restore-plans'),planCount);assert.equal(count('/api/data/restore-jobs'),0);await observe('01-upload-policy');cases.push({case:phase,old_upload_fact:true,stale_plan_POST:0,restore_POST:0});
 phase='plan-pending-policy-change';await snap();overlay=7199;hold='plan';await uploadFile('snapshot-plan-late');await awaitHeld('plan');await policy.selectOption(respect);const stalePlan=await finishHeld('plan');await noPlan();assert.equal(count('/api/data/restore-jobs'),0);assert.ok(!(await page.locator('body').innerText()).includes('删除覆盖 7199'));await observe('02-plan-policy');cases.push({case:phase,stale_policy:stalePlan.deletion_policy,current_policy:respect,not_eligible:true});
 phase='fresh-respect-positive';overlay=31;await uploadFile('respect-current');await page.getByText('删除覆盖 31 项',{exact:false}).waitFor();assert.equal(await verify.isEnabled(),true);const freshPlan=plans.get(requests.filter(r=>r.path==='/api/data/restore-plans').at(-1).body?Array.from(plans.keys()).at(-1):'');const beforeVerify=count('/api/data/restore-jobs');await verify.click();await activate.waitFor();await settle();assert.equal(await activate.isEnabled(),true);assert.equal(count('/api/data/restore-jobs'),beforeVerify+1);const actualVerify=requests.filter(r=>r.path==='/api/data/restore-jobs').at(-1).body;assert.equal(actualVerify.plan_id,freshPlan.plan_id);assert.equal(actualVerify.expected_plan_sha256,freshPlan.plan_sha256);assert.equal(actualVerify.acknowledge_unknown_deletions,false);await observe('03-fresh-respect');cases.push({case:phase,plan:freshPlan,verify_body:actualVerify,explicit_once:true});
 phase='refresh-plan-late-policy-change';hold='get_plan';await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();await awaitHeld('get_plan');await policy.selectOption(snapshot);await finishHeld('get_plan');await noPlan();assert.equal(await file.isDisabled(),true);cases.push({case:phase,old_GET_plan_not_requalified:true,snapshot_confirmation_reset:true});
 phase='snapshot-unknown-positive';await confirm.check();latest='unknown';overlay=41;await uploadFile('snapshot-unknown');await page.getByText('删除覆盖 41 项',{exact:false}).waitFor();assert.equal(await verify.isDisabled(),true);await page.getByLabel('确认仅按已取得的备份时点核对，不视为最新删除或账',{exact:true}).check();assert.equal(await verify.isEnabled(),true);await verify.click();await settle();assert.equal(await activate.isEnabled(),true);const snapshotPlan=Array.from(plans.values()).at(-1),snapshotVerify=requests.filter(r=>r.path==='/api/data/restore-jobs').at(-1).body;assert.equal(snapshotVerify.plan_id,snapshotPlan.plan_id);assert.equal(snapshotVerify.acknowledge_unknown_deletions,true);
 const activatePath='/api/data/restore-jobs/'+jobs.get(snapshotVerify.business_key).job_id+'/activate-readonly';await activate.click();await settle();const activation=requests.filter(r=>r.path===activatePath);assert.equal(activation.length,1);assert.equal(activation[0].body.expected_plan_sha256,snapshotPlan.plan_sha256);assert.equal(activation[0].body.expected_selection_generation,0);assert.equal(activation[0].body.confirm,true);await confirm.uncheck();await noPlan();await observe('04-snapshot-confirmation');cases.push({case:phase,verify_body:snapshotVerify,activation:activation[0],confirmation_revoked_plan:true,layer:'route action only, no real selector'});
 phase='same-context-file-replacement';latest='known';await policy.selectOption(respect);overlay=51;await uploadFile('old-file');await page.getByText('删除覆盖 51 项',{exact:false}).waitFor();const restoreCount=count('/api/data/restore-jobs');hold='upload';await uploadFile('replacement-file');await awaitHeld('upload');await noPlan();assert.equal(await file.isDisabled(),true);overlay=52;await finishHeld('upload');await page.getByText('删除覆盖 52 项',{exact:false}).waitFor();assert.equal(count('/api/data/restore-jobs'),restoreCount);assert.ok(!(await page.locator('body').innerText()).includes('删除覆盖 51'));cases.push({case:phase,file_replacement_invalidates_previous:true,no_automatic_verify:true});
 phase='verify-late-input-change';hold='verify';await verify.click();await awaitHeld('verify');await policy.selectOption(snapshot);await finishHeld('verify');await noPlan();cases.push({case:phase,old_verification_fact_preserved_but_not_activation_eligible:true});
 phase='source-A-to-B';await page.getByLabel('范围',{exact:true}).selectOption('selected');await page.getByLabel('C03 source A',{exact:true}).check();hold='scope';await preview.click();await awaitHeld('scope');await page.getByLabel('C03 source A',{exact:true}).uncheck();await page.getByLabel('C03 source B',{exact:true}).check();const staleSourceScope=await finishHeld('scope');await settle();assert.equal(await exportButton.isDisabled(),true);assert.ok(!(await page.locator('body').innerText()).includes('SCOPE '+uuid(20)));await preview.click();await page.getByText('SCOPE '+uuid(22),{exact:false}).waitFor();assert.equal(await exportButton.isEnabled(),true);const beforeExport=count('/api/data/jobs');await exportButton.click();await settle();assert.equal(count('/api/data/jobs'),beforeExport+1);const sourceExport=requests.filter(r=>r.path==='/api/data/jobs').at(-1).body;assert.deepEqual(sourceExport.scope.source_ids,[uuid(22)]);assert.deepEqual(sourceExport.scope.activity_ids,[]);await observe('05-source-scope');cases.push({case:phase,stale:staleSourceScope,export_body:sourceExport,explicit_once:true});
 phase='activity-A-to-B';await page.getByLabel('C03 source B',{exact:true}).uncheck();await page.getByLabel('活动 '+uuid(30),{exact:true}).check();hold='scope';await preview.click();await awaitHeld('scope');await page.getByLabel('活动 '+uuid(30),{exact:true}).uncheck();await page.getByLabel('活动 '+uuid(31),{exact:true}).check();await finishHeld('scope');await settle();assert.equal(await exportButton.isDisabled(),true);await preview.click();await page.getByText('SCOPE '+uuid(31),{exact:false}).waitFor();await exportButton.click();await settle();const activityExport=requests.filter(r=>r.path==='/api/data/jobs').at(-1).body;assert.deepEqual(activityExport.scope.activity_ids,[uuid(31)]);assert.deepEqual(activityExport.scope.source_ids,[]);cases.push({case:phase,export_body:activityExport,explicit_once:true});
 phase='mode-change';hold='scope';await preview.click();await awaitHeld('scope');await page.getByLabel('范围',{exact:true}).selectOption('all');await finishHeld('scope');await settle();assert.ok(!(await page.locator('body').innerText()).includes('SCOPE '+uuid(31)));await page.getByLabel('范围',{exact:true}).selectOption('selected');assert.equal(await exportButton.isDisabled(),true);cases.push({case:phase,late_scope_absent:true,selected_requires_fresh_preview:true});
 phase='unmount-plan-late';await policy.selectOption(respect);hold='plan';overlay=8899;await uploadFile('unmount-late');await awaitHeld('plan');await page.getByRole('button',{name:'我的资料',exact:false}).click();await finishHeld('plan');await workspace();await noPlan();assert.ok(!(await page.locator('body').innerText()).includes('删除覆盖 8899'));await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();await noPlan();cases.push({case:phase,late_result_not_committed:true,history_GET_did_not_adopt_old_plan:true});
 phase='context-plan-late';hold='plan';overlay=9999;await uploadFile('context-late');await awaitHeld('plan');active=next;await page.getByRole('button',{name:'只读刷新进度',exact:true}).click();await page.getByText('当前仅供只读查看',{exact:false}).waitFor();await finishHeld('plan');await noPlan();assert.ok(!(await page.locator('body').innerText()).includes('删除覆盖 9999'));await observe('06-context-late');cases.push({case:phase,late_result_not_committed:true,current_identity:next});
 assert.equal(pending.length,0);assert.deepEqual(errors,[]);assert.equal(count('/api/data/jobs'),2);assert.equal(count('/api/data/restore-jobs'),3);assert.equal(requests.filter(r=>r.path.endsWith('/activate-readonly')).length,1);
 save('result',{state:'passed',layer:'真实Chromium/最终dist；全部routes/合成DTO，零监听/API/PG；切换响应不代表真实selector',cases,requests,sequence,errors,finalIdentity,explicit_restore_POST:3,explicit_export_POST:2,explicit_activate_POST:1,automatic_action_POST:0});
}catch(error){save('failure',{type:error.name,message:error.message,stack:error.stack,requests,sequence,errors,cases,finalIdentity});throw error;}
finally{for(const item of pending)try{await item.route.abort();}catch{}await browser.close();process.stdout.write(JSON.stringify({event:'browser_closed',confirmed:true})+'\n');}
