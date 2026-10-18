"use strict";
// 只核尾链；所有Response/PNG/已解码ImageBitmap均来自真实API，暂停在读取完成后。
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
module.exports=async function tail({browser,input,token}){
 const context=await browser.newContext();const page=await context.newPage();const records=[],requests=[];
 const save=()=>fs.writeFileSync(path.join(input.out,'tail-effects.json'),JSON.stringify({records,requests},null,2));
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
  document.addEventListener('visibilitychange',()=>{t.visibility.push({hidden:document.hidden,state:document.visibilityState,at:performance.now()});});
  setInterval(()=>{if(t.heartbeat&&t.owner&&!document.hidden)void realFetch(t.owner.url,{headers:t.owner.headers}).catch(()=>{});},200);
 });
 page.on('request',r=>{const u=new URL(r.url());if(u.pathname.includes('/html/'))requests.push({path:u.pathname,method:r.method(),owner_present:Boolean(r.headers()['x-retrolume-preview-owner'])});});
 const until=async(fn,ms=7000)=>{const end=Date.now()+ms;while(Date.now()<end){if(await fn())return;await page.waitForTimeout(30);}throw Error('C05 bounded actual observation timeout');};
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
 async function status(live){const r=await context.request.get(input.base+'/api/activities/'+live.item.activity_id+'/html/previews/'+live.row.preview_id,{headers:{'X-RetroLume-Session':token}});assert.equal(r.status(),200);return r.json();}
 async function stopped(live){let row;await until(async()=>{row=await status(live);return row.state==='stopped';},18000);records.push({label:'actual_persistent_stopped',preview_id:live.row.preview_id,row});save();return row;}
 async function clearHolds(){await page.evaluate(()=>{__c5.holds={};__c5.arms={};});}
 const a=input.items[0],b=input.items[1],c=input.items[2];let last=null;
 try{
  await page.goto(input.base,{waitUntil:'domcontentloaded'});
  let fresh;const priorFiles=fs.readdirSync(path.dirname(input.out)).filter(n=>n.startsWith('tail-attempt-')&&n!==path.basename(input.out));let completedCombo=null;
  for(const n of priorFiles){const p=path.join(path.dirname(input.out),n,'tail-effects.json');if(!fs.existsSync(p))continue;const data=JSON.parse(fs.readFileSync(p,'utf8'));const found=data.records.find(r=>r.label==='old_actual_values_released_new_identity_intact');if(found&&found.images.every(i=>i.released&&i.closed&&i.closed_width===0&&i.closed_height===0))completedCombo={path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),record:found};}
  if(!completedCombo){
  // 生命周期1：真实旧响应完成读取和解码后暂停。
  const old=last=await open(a);await inputValue(old.panel,'3',58.8);await until(async()=> (await hashCanvas()).nonzero);
  await arm('bitmap');await inputValue(old.panel,'0',0);await waitHeld('bitmap');await arm('frame');await waitHeld('frame');
  await arm('citation');await old.panel.getByRole('button',{name:/回查资料/}).first().click();await waitHeld('citation');
  await arm('input');await inputValue(old.panel,'1',19.6);await waitHeld('input');await arm('stop');
  await old.panel.getByRole('button',{name:'停止并回到学习',exact:true}).click();await waitHeld('stop');await observe('old_completed_responses_held');
  await page.evaluate(()=>{__c5.heartbeat=false;});await stopped(old);
  await select(b);await page.getByRole('region',{name:'交互解释',exact:true}).getByRole('button',{name:'停止并回到学习',exact:true}).click();
  // 生命周期2：同活动真实新owner/generation，在旧await之后释放实际值/bitmap。
  fresh=last=await open(b);assert.notEqual(fresh.row.owner_id,old.row.owner_id);assert.notEqual(fresh.row.generation,old.row.generation);
  await inputValue(fresh.panel,'4',78.4);await until(async()=> (await fresh.panel.innerText()).includes('78.4'));await page.waitForTimeout(500);const before=await hashCanvas();
  await release(['frame','citation','input','stop','bitmap']);await until(()=>page.evaluate(()=>__c5.images.every(i=>i.closed)));
  await page.waitForTimeout(500);const after=await hashCanvas();assert.deepEqual(after,before);assert.ok((await fresh.panel.innerText()).includes('78.4'));
  assert.equal(await fresh.panel.getByLabel('交互解释引用原文').count(),0);assert.equal(await fresh.panel.count(),1);
  const released=await observe('old_actual_values_released_new_identity_intact');assert.ok(released.images.every(i=>i.released&&i.closed&&i.closed_width===0&&i.closed_height===0));
  for(const image of released.images)assert.ok(!released.draws.includes(image.id));
  await page.screenshot({path:path.join(input.out,'tail-new-owner-preserved.png'),fullPage:true});await clearHolds();
  }else{records.push({label:'inherited_actual_completed_combo',...completedCombo});save();fresh=last=await open(b);}
  // 同生命周期2真实最小化：先完成新PNG解码及JSON读取，再hidden撤销身份。
  await arm('bitmap');await inputValue(fresh.panel,'5',98);await waitHeld('bitmap');await arm('frame');await waitHeld('frame');await arm('citation');await fresh.panel.getByRole('button',{name:/回查资料/}).first().click();await waitHeld('citation');
  assert.equal(await page.evaluate(()=>document.hidden),false);const other=await context.newPage();await other.goto('about:blank');await other.bringToFront();await until(()=>page.evaluate(()=>document.hidden));
  await observe('actual_own_browser_tab_document_hidden');assert.equal(await fresh.panel.getByLabel('交互解释引用原文').count(),0);
  await stopped(fresh);await page.bringToFront();await until(()=>page.evaluate(()=>!document.hidden));await other.close();
  await release(['frame','citation','bitmap']);await until(()=>page.evaluate(()=>__c5.images.every(i=>i.closed)));const hiddenCanvas=await hashCanvas();assert.equal(hiddenCanvas.nonzero,false);
  assert.ok(!(await fresh.panel.innerText()).includes('能量：98'));const hidden=await observe('hidden_actual_bytes_and_bitmap_discarded');for(const image of hidden.images)assert.ok(!hidden.draws.includes(image.id));
  await page.screenshot({path:path.join(input.out,'tail-hidden-cleared.png'),fullPage:true});await clearHolds();
  // 生命周期3：READY组件卸载时释放已解码旧bitmap，原父不复活。
  const unloaded=last=await open(b);await arm('bitmap');await inputValue(unloaded.panel,'2',39.2);await waitHeld('bitmap');
  await page.evaluate(()=>{__c5.heartbeat=false;});await page.locator('[data-activity-id="'+a.activity_id+'"]').click();await release(['bitmap']);await until(()=>page.evaluate(()=>__c5.images.every(i=>i.closed)));
  const unmount=await observe('actual_component_unmount_and_bitmap_close');for(const image of unmount.images)assert.ok(!unmount.draws.includes(image.id));assert.equal(await page.getByRole('region',{name:'交互解释',exact:true}).count(),0);await stopped(unloaded);await clearHolds();
  // 生命周期4：READY页面卸载，只ownerless读取，实际失联清场。
  const departed=last=await open(c);const departure=await status(departed);await page.evaluate(()=>{__c5.heartbeat=false;});await page.goto('about:blank');const departAfter=await stopped(departed);
  assert.equal(departAfter.deadline_at,departure.deadline_at);records.push({label:'actual_READY_page_unload',before:departure,after:departAfter});save();
  // 生命周期5：READY且owner活着时真实reload，没有自动POST或续D。
  await page.goto(input.base,{waitUntil:'domcontentloaded'});const refresh=last=await open(c);const pre=await status(refresh);assert.ok(['ready','running'].includes(pre.state));const requestIndex=requests.length;
  await page.reload({waitUntil:'domcontentloaded'});const post=await stopped(refresh);const following=requests.slice(requestIndex);
  assert.equal(post.deadline_at,pre.deadline_at);assert.equal(post.starts_used,pre.starts_used);assert.equal(following.filter(r=>r.method==='POST').length,0);
  assert.equal(await page.evaluate(()=>__c5.owner),null);records.push({label:'actual_active_refresh_GET_only_owner_lost',before:pre,after:post,requests:following});save();
  fs.writeFileSync(path.join(input.out,'tail-result.json'),JSON.stringify({status:'PASS_REAL_CLIENT_TAIL_FIVE_LIFECYCLES',normal_Native_rerun:false,new_model_calls:0,actual_visibility_control:'own headed Chromium tab selection; minimize unavailable recorded',records},null,2));
 }catch(error){await observe('failure_actual_state').catch(()=>{});await page.screenshot({path:path.join(input.out,'tail-failure.png'),fullPage:true}).catch(()=>{});throw error;}
 finally{
  if(last)await context.request.post(input.base+'/api/activities/'+last.item.activity_id+'/html/previews/'+last.row.preview_id+'/stop',{headers:{'X-RetroLume-Session':token,'Origin':input.base},data:{generation:last.row.generation,stop_key:crypto.randomUUID(),reason:'user'}}).catch(()=>{});
  await context.close();save();
 }
};
