"use strict";
// 只核尾链；所有Response/PNG/已解码ImageBitmap均来自真实API，暂停在读取完成后。
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
module.exports=async function tail({browser,input,token}){
 const context=await browser.newContext();const page=await context.newPage();const records=[],requests=[];
 const actualCDP=await context.newCDPSession(page);await actualCDP.send('Emulation.setFocusEmulationEnabled',{enabled:false});
 // PW的原连接仍有独立focus override；对实际原生主session关闭，辅助CDP不足以撤销它。
 async function disableNativeFocusOverride(target){
  const implementation=target._connection.toImpl(target),native=implementation.delegate._mainFrameSession._client;
  await native.send('Emulation.setFocusEmulationEnabled',{enabled:false});
  records.push({label:'actual_Playwright_primary_CDP_focus_emulation_disabled',target_id:implementation.delegate._targetId,session_id:native._sessionId,method:'Emulation.setFocusEmulationEnabled',enabled:false});
 }
 await disableNativeFocusOverride(page);
 let phase="preflight";const save=()=>fs.writeFileSync(path.join(input.out,'tail-effects.json'),JSON.stringify({records,requests},null,2));
 await page.addInitScript(()=>{
  const realFetch=globalThis.fetch.bind(globalThis),realBitmap=globalThis.createImageBitmap.bind(globalThis);
  const t=globalThis.__c5={arms:{},holds:{},images:[],draws:[],visibility:[],workspaces:{},next:0,heartbeat:false,owner:null};
  const kind=url=>url.includes('/citations/')?'citation':url.endsWith('/stop')?'stop':url.endsWith('/inputs')?'input':url.includes('/frames?')?'frame':null;
  const digest=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
  globalThis.fetch=async(...args)=>{
   const url=String(args[0] instanceof Request?args[0].url:args[0]);const opt=args[1]??{};const headers=new Headers(opt.headers??{});
   if(/\/html\/previews\/[^/]+$/.test(url)&&headers.has('x-retrolume-preview-owner'))t.owner={url,headers};
   const response=await realFetch(...args);const k=kind(new URL(url,location.href).pathname+new URL(url,location.href).search);
   if(new URL(url,location.href).pathname.endsWith('/teaching/workspace')){
    const original=response.json.bind(response);Object.defineProperty(response,'json',{value:async()=>{const value=await original();t.workspaces[value.activity_id]={exercise_record_id:value.head?.exercise_record_id};return value;}});
   }
   if(k&&t.arms[k]){
    delete t.arms[k];const method=k==='frame'?'arrayBuffer':'json';const original=response[method].bind(response);
    Object.defineProperty(response,method,{value:async()=>{
     const value=await original();const id=++t.next;const row={id,kind:k,url:new URL(url,location.href).pathname,status:response.status,read_completed:true,released:false,
      data:k==='frame'?{bytes:value.byteLength,sha256:await digest(value),preview_id:response.headers.get('X-Preview-Id'),generation:response.headers.get('X-Preview-Generation')}:value};
     t.holds[k]={row};return await new Promise(resolve=>{t.holds[k].release=()=>{row.released=true;resolve(value);};});
    }});
   }
   return response;
  };
  const draw=CanvasRenderingContext2D.prototype.drawImage;
  CanvasRenderingContext2D.prototype.drawImage=function(image,...args){if(image&&image.__c5_id)t.draws.push(image.__c5_id);return draw.call(this,image,...args);};
  globalThis.createImageBitmap=async(...args)=>{
   const image=await realBitmap(...args);if(!t.arms.bitmap)return image;
   delete t.arms.bitmap;const id=++t.next;const row={id,width:image.width,height:image.height,decoded:true,released:false,closed:false};t.images.push(row);
   Object.defineProperty(image,'__c5_id',{value:id});const close=image.close.bind(image);
   Object.defineProperty(image,'close',{value:()=>{close();row.closed=true;row.closed_width=image.width;row.closed_height=image.height;}});
   t.holds.bitmap={row};return await new Promise(resolve=>{t.holds.bitmap.release=()=>{row.released=true;resolve(image);};});
  };
  document.addEventListener('visibilitychange',()=>{t.visibility.push({hidden:document.hidden,state:document.visibilityState,at:performance.now()});if(document.hidden)t.heartbeat=false;});
  setInterval(()=>{if(t.heartbeat&&t.owner&&!document.hidden)void realFetch(t.owner.url,{headers:t.owner.headers}).catch(()=>{});},200);
 });
 page.on('request',r=>{const u=new URL(r.url());if(u.pathname.includes('/html/'))requests.push({path:u.pathname,method:r.method(),owner_present:Boolean(r.headers()['x-retrolume-preview-owner']),at_ms:Date.now(),phase,source:'page'});});
 const until=async(fn,ms=7000)=>{const end=Date.now()+ms;while(Date.now()<end){if(await fn())return;await page.waitForTimeout(30);}throw Error('C06 bounded actual observation timeout');};
 async function observe(label){const row=await page.evaluate(()=>({holds:Object.fromEntries(Object.entries(__c5.holds).map(([k,v])=>[k,v.row])),images:__c5.images,draws:__c5.draws,visibility:__c5.visibility,hidden:document.hidden,visibilityState:document.visibilityState}));records.push({label,...row});save();return row;}
 async function arm(...names){await page.evaluate(names=>{for(const k of names)__c5.arms[k]=true;},names);}
 async function waitHeld(kind){await until(()=>page.evaluate(kind=>!!__c5.holds[kind]?.release,kind));}
 async function release(names){await page.evaluate(names=>{for(const k of names){if(!__c5.holds[k]?.release)throw Error('missing actual completed response '+k);__c5.holds[k].release();}},names);}
 async function select(item){
  await page.getByRole('button',{name:/学习活动/}).first().click();await page.locator('[data-activity-id="'+item.activity_id+'"]').click();
  await until(()=>page.evaluate(item=>__c5.workspaces[item.activity_id]?.exercise_record_id===item.parent.record_id,item));
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const explain=page.getByRole('button',{name:'交互解释当前练习',exact:true});await explain.waitFor();await explain.click();
  const panel=page.getByRole('region',{name:'交互解释',exact:true});await panel.getByRole('button',{name:'读取已保存解释'}).first().waitFor();await panel.getByRole('button',{name:'读取已保存解释'}).first().click();
  await panel.getByRole('button',{name:'显式打开预览',exact:true}).waitFor();return panel;
 }
 async function open(item){
  const panel=await select(item);const pending=page.waitForResponse(r=>new URL(r.url()).pathname.endsWith('/previews')&&r.request().method()==='POST');
  await panel.getByRole('button',{name:'显式打开预览',exact:true}).click();const response=await pending;assert.equal(response.status(),200);const row=await response.json();
  await panel.getByText(/预览 ready/).waitFor({timeout:10000});await page.evaluate(()=>{__c5.heartbeat=true;});
  records.push({label:'actual_READY_open',activity_id:item.activity_id,parent:item.parent,preview:row});save();return {panel,row,item};
 }
 async function inputValue(panel,value,expected){
  const response=page.waitForResponse(r=>new URL(r.url()).pathname.endsWith('/inputs'));
  await panel.getByRole('spinbutton',{name:'高度 h',exact:true}).fill(value);await panel.getByRole('button',{name:'应用高度 h',exact:true}).click();const r=await response;const ack=await r.json();
  assert.equal(r.status(),200);assert.equal(ack.accepted,true);assert.ok(Math.abs(Number(ack.readouts[0].value)-expected)<1e-9);
  return ack;
 }
 async function hashCanvas(){return page.getByLabel('受信程序计算和图形画面',{exact:true}).evaluate(canvas=>{const bytes=canvas.getContext('2d').getImageData(0,0,640,480).data;let value=2166136261;for(const byte of bytes)value=Math.imul(value^byte,16777619);return {hash:value>>>0,nonzero:bytes.some(x=>x!==0)};});}
 async function status(live){requests.push({path:'/api/activities/'+live.item.activity_id+'/html/previews/'+live.row.preview_id,method:'GET',owner_present:false,at_ms:Date.now(),phase,source:'ownerless_oracle'});const r=await context.request.get(input.base+'/api/activities/'+live.item.activity_id+'/html/previews/'+live.row.preview_id,{headers:{'X-RetroLume-Session':token}});assert.equal(r.status(),200);return r.json();}
 async function stopped(live){let row;await until(async()=>{row=await status(live);return row.state==='stopped';},18000);records.push({label:'actual_persistent_stopped',preview_id:live.row.preview_id,row});save();return row;}
 async function clearHolds(){await page.evaluate(()=>{__c5.holds={};__c5.arms={};});}
 const completed=[],methods=input.methods??['real_hidden','READY_unload','READY_active_refresh'];let last=null;
 const mark=(method,row)=>{const value={method,status:'PASS_REAL_CLIENT_METHOD',...row};completed.push(value);fs.writeFileSync(path.join(input.out,'method-'+method+'.json'),JSON.stringify(value,null,2));save();};
 try{
  const inherited=fs.readFileSync(input.inherited_combo.path);
  assert.equal(crypto.createHash('sha256').update(inherited).digest('hex'),input.inherited_combo.sha256);
  records.push({label:'explicit_inherited_C05_combo_no_replay',path:input.inherited_combo.path,sha256:input.inherited_combo.sha256});save();
  await page.goto(input.base,{waitUntil:'domcontentloaded'});await page.bringToFront();await until(()=>page.evaluate(()=>!document.hidden));
  const initial=await observe('native_visibility_initial_visible_without_preview');assert.equal(initial.visibilityState,'visible');
  const probe=await context.newPage();await probe.goto('about:blank');
  const probeCDP=await context.newCDPSession(probe);await probeCDP.send('Emulation.setFocusEmulationEnabled',{enabled:false});
  await disableNativeFocusOverride(probe);
  const ownTarget=(await actualCDP.send('Target.getTargetInfo')).targetInfo,probeTarget=(await probeCDP.send('Target.getTargetInfo')).targetInfo;
  const ownWindow=await actualCDP.send('Browser.getWindowForTarget',{targetId:ownTarget.targetId}),probeWindow=await probeCDP.send('Browser.getWindowForTarget',{targetId:probeTarget.targetId});
  records.push({label:'native_window_target_bindings',ownTarget,probeTarget,ownWindow,probeWindow});save();
  await probe.bringToFront();await until(()=>page.evaluate(()=>document.hidden));
  const hiddenProbe=await observe('native_visibility_hidden_without_preview');assert.ok(hiddenProbe.visibility.some(r=>r.hidden&&r.state==='hidden'));
  await page.bringToFront();await until(()=>page.evaluate(()=>!document.hidden));const visibleProbe=await observe('native_visibility_restored_without_preview');
  assert.ok(visibleProbe.visibility.some(r=>!r.hidden&&r.state==='visible'));await probe.close();
  assert.equal(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/previews')).length,0);
  fs.writeFileSync(path.join(input.out,'visibility-probe.json'),JSON.stringify({status:'PASS_NATIVE_VISIBLE_HIDDEN_VISIBLE',focus_emulation_disabled:true,cdp_method:'Emulation.setFocusEmulationEnabled',initial,hidden:hiddenProbe,restored:visibleProbe,preview_count:0},null,2));
  if(methods.includes('real_hidden')){
   phase='real_hidden';const live=last=await open(input.items[0]);const before=await status(live);assert.ok(['ready','running'].includes(before.state));
   await arm('bitmap');await inputValue(live.panel,'5',98);await waitHeld('bitmap');await arm('frame');await waitHeld('frame');
   await arm('citation');await live.panel.getByRole('button',{name:/回查资料/}).first().click();await waitHeld('citation');
   const held=await observe('hidden_READY_real_decoded_bitmap_and_read_values_held');assert.ok(held.images.some(i=>i.decoded&&!i.closed));assert.ok(held.holds.frame.read_completed&&held.holds.citation.read_completed);
   const other=await context.newPage();await other.goto('about:blank');await disableNativeFocusOverride(other);await other.bringToFront();await until(()=>page.evaluate(()=>document.hidden));
   await observe('actual_document_hidden_with_READY_owner');await until(()=>live.panel.getByRole('spinbutton',{name:'高度 h',exact:true}).isDisabled());
   assert.equal(await live.panel.getByLabel('交互解释引用原文').count(),0);const stop=await stopped(live);
   await page.bringToFront();await until(()=>page.evaluate(()=>!document.hidden));await other.close();
   await release(['frame','citation','bitmap']);await until(()=>page.evaluate(()=>__c5.images.every(i=>i.closed)));await page.waitForTimeout(250);
   const canvas=await hashCanvas();assert.equal(canvas.nonzero,false);assert.equal(await live.panel.getByLabel('交互解释引用原文').count(),0);
   assert.ok(!(await live.panel.innerText()).includes('能量：98'));assert.equal(await live.panel.getByRole('spinbutton',{name:'高度 h',exact:true}).isDisabled(),true);
   const discarded=await observe('hidden_actual_values_released_bitmap_closed_no_draw_no_resurrection');
   assert.ok(discarded.images.every(i=>i.released&&i.closed&&i.closed_width===0&&i.closed_height===0));for(const image of discarded.images)assert.ok(!discarded.draws.includes(image.id));
   await page.screenshot({path:path.join(input.out,'hidden-cleared.png'),fullPage:true});mark('real_hidden',{preview_id:live.row.preview_id,activity_id:live.item.activity_id,parent:live.item.parent,before,stop,held,discarded,canvas});await clearHolds();
   await live.panel.getByRole('button',{name:'停止并回到学习',exact:true}).click();
  }
  if(methods.includes('READY_unload')){
   phase='READY_unload';const live=last=await open(input.items[1]);const before=await status(live);assert.ok(['ready','running'].includes(before.state));
   await arm('bitmap');await inputValue(live.panel,'2',39.2);await waitHeld('bitmap');const held=await observe('unload_READY_actual_decoded_bitmap_held');
   const begin=requests.length;await page.evaluate(()=>{__c5.heartbeat=false;});await page.locator('[data-activity-id="'+input.items[0].activity_id+'"]').click();
   await until(()=>page.getByRole('region',{name:'交互解释',exact:true}).count().then(n=>n===0));await release(['bitmap']);await until(()=>page.evaluate(()=>__c5.images.every(i=>i.closed)));
   const discarded=await observe('READY_component_actually_unmounted_bitmap_close_no_draw');assert.ok(discarded.images.every(i=>i.released&&i.closed&&i.closed_width===0&&i.closed_height===0));
   for(const image of discarded.images)assert.ok(!discarded.draws.includes(image.id));const stop=await stopped(live);await page.waitForTimeout(250);
   const following=requests.slice(begin);assert.equal(following.filter(r=>r.method==='POST'&&r.path.endsWith('/previews')).length,0);assert.equal(await page.getByRole('region',{name:'交互解释',exact:true}).count(),0);
   mark('READY_unload',{preview_id:live.row.preview_id,activity_id:live.item.activity_id,parent:live.item.parent,before,stop,held,discarded,requests:following});await clearHolds();
  }
  if(methods.includes('READY_active_refresh')){
   phase='READY_active_refresh';await page.goto(input.base,{waitUntil:'domcontentloaded'});const live=last=await open(input.items[2]);
   const before=await status(live);assert.ok(['ready','running'].includes(before.state));assert.ok(await page.evaluate(()=>!!__c5.owner&&__c5.heartbeat));
   await until(()=>Promise.resolve(requests.some(r=>r.phase===phase&&r.method==='GET'&&r.owner_present)));const begin=requests.length;
   await page.reload({waitUntil:'domcontentloaded'});assert.equal(await page.evaluate(()=>__c5.owner),null);const after=await stopped(live);
   const following=requests.slice(begin);assert.equal(after.deadline_at,before.deadline_at);assert.equal(after.starts_used,before.starts_used);
   assert.ok(following.some(r=>r.method==='GET'));assert.equal(following.filter(r=>r.method!=='GET'||r.owner_present).length,0);assert.equal(await page.evaluate(()=>__c5.owner),null);
   mark('READY_active_refresh',{preview_id:live.row.preview_id,activity_id:live.item.activity_id,parent:live.item.parent,before,after,owner_after_reload:null,requests:following,cleanup_POST_outside_this_timeline:true});
  }
  fs.writeFileSync(path.join(input.out,'tail-result.json'),JSON.stringify({status:'PASS_SELECTED_C06_CLIENT_METHODS',methods,completed,normal_Native_rerun:false,new_model_calls:0,inherited_combo:input.inherited_combo},null,2));
 }catch(error){await observe('failure_actual_state').catch(()=>{});await page.screenshot({path:path.join(input.out,'failure.png'),fullPage:true}).catch(()=>{});throw error;}
 finally{
  phase='external_cleanup_after_validation';records.push({label:phase,at_ms:Date.now()});save();
  if(last)await context.request.post(input.base+'/api/activities/'+last.item.activity_id+'/html/previews/'+last.row.preview_id+'/stop',{headers:{'X-RetroLume-Session':token,'Origin':input.base},data:{generation:last.row.generation,stop_key:crypto.randomUUID(),reason:'user'}}).catch(()=>{});
  await actualCDP.detach().catch(()=>{});await context.close();save();
 }
};
