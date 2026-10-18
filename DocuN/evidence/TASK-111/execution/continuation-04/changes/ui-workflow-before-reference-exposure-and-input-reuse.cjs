"use strict";
// 正常UI、原键竞争和真实迟到字节共用一个主浏览器；期望值独立计算。
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
module.exports=async function workflow({browser,input,token}){
const records=[],requests=[],acks=[],frames=[],bindings={},pending=[];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const canonical=v=>JSON.stringify(Array.isArray(v)?v.map(x=>JSON.parse(canonical(x))):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,JSON.parse(canonical(v[k]))])):v);
const save=()=>fs.writeFileSync(path.join(input.out,'ui-effects.json'),JSON.stringify({records,requests,acks,frames,bindings},null,2));
function pmf(n,k,p){if(p===0)return k===0?1:0;if(p===1)return k===n?1:0;let c=1;for(let i=1;i<=k;i++)c=c*(n-i+1)/i;return c*p**k*(1-p)**(n-k);}
 const context=await browser.newContext();const page=await context.newPage();const dialogs=[];
 page.on('dialog',async dialog=>{dialogs.push(dialog.type());await dialog.dismiss();});
 await page.addInitScript(()=>{
  const original=globalThis.createImageBitmap;
  globalThis.createImageBitmap=async(...args)=>{const image=await original(...args);if(!globalThis.__t111_hold_bitmap)return image;
   globalThis.__t111_hold_bitmap=false;globalThis.__t111_bitmap={width:image.width,height:image.height};
   return await new Promise(resolve=>{globalThis.__t111_release_bitmap=()=>resolve(image);});};
 });
 page.on('request',r=>{const u=new URL(r.url());if(u.pathname.includes('/html/'))requests.push({path:u.pathname,method:r.method()});});
 page.on('response',r=>{
  const u=new URL(r.url());
  if(u.pathname.endsWith('/inputs'))pending.push(r.json().then(body=>{acks.push({status:r.status(),body});save();}).catch(()=>{}));
  if(u.pathname.endsWith('/frames')&&r.status()===200)pending.push(r.body().then(bytes=>{const file='ui-remote-'+frames.length+'.png';fs.writeFileSync(path.join(input.out,file),bytes);
   frames.push({file,path:u.pathname,sha256:sha(bytes),bytes:bytes.length,preview_id:r.headers()['x-preview-id'],generation:r.headers()['x-preview-generation']});save();}).catch(()=>{}));
 });
 async function until(fn,ms=6000){const end=Date.now()+ms;while(Date.now()<end){if(await fn())return;await page.waitForTimeout(40);}throw Error('bounded observation timeout');}
 async function select(item){
  await page.getByRole('button',{name:/学习活动/}).first().click();
  await page.locator('[data-activity-id="'+item.activity_id+'"]').click();
  await page.getByRole('region',{name:'教学工作区',exact:true}).waitFor();
  await page.getByRole('button',{name:item.kind==='energy'?'交互解释当前练习':'交互解释当前反馈',exact:true}).click();
  return page.getByRole('region',{name:'交互解释',exact:true});
 }
 async function step(panel,label,value,oracle,{refuse=false}={}){
  const before=acks.length;
  const spin=panel.getByRole('spinbutton',{name:label,exact:true});
  if(await spin.count())await spin.fill(value);else{
   const slider=panel.getByRole('slider',{name:label,exact:true});await slider.focus();await slider.press('Home');
   const min=Number(await slider.getAttribute('min')),increment=Number(await slider.getAttribute('step'));
   for(let n=0;n<Math.round((Number(value)-min)/increment);n++)await slider.press('ArrowRight');
  }
  await panel.getByRole('button',{name:'应用'+label,exact:true}).press('Enter');
  await until(()=>acks.length>before);const response=acks.at(-1);
  if(refuse){assert.equal(response.status,422);await panel.getByRole('alert').filter({hasText:'已保留上次画面'}).waitFor();}
  else{assert.equal(response.status,200);assert.equal(response.body.accepted,true);assert.ok(Math.abs(Number(response.body.readouts[0].value)-oracle)<=1e-9);
   const figure=response.body.figures?.[0];if(figure?.count<=21&&label!=='高度 h'&&label!=='质量 m')assert.ok(Math.abs(figure.points.reduce((s,p)=>s+p[1],0)-1)<=1e-9);}
  await until(()=>panel.getByRole('button',{name:'应用'+label,exact:true}).isEnabled());await page.waitForTimeout(800);
  records.push({kind:'input',label,value,oracle,refuse,response});save();return response.body;
 }
 async function stopAndWait(panel,preview){
  await panel.getByRole('button',{name:'停止预览',exact:true}).click();
  await panel.getByText(/预览 stopped/).waitFor({timeout:15000});
  const result=await context.request.get(input.base+'/api/activities/'+preview.activity_id+'/html/previews/'+preview.preview_id,{headers:{'X-RetroLume-Session':token}});
  assert.equal((await result.json()).state,'stopped');records.push({kind:'stop',preview_id:preview.preview_id});save();
 }
 try{
  await page.goto(input.base,{waitUntil:'domcontentloaded'});
  for(const item of input.parents){
   const previous=input.resume_bindings?.[item.kind];
   if(previous?.normal_complete&&previous.activity_id===item.activity_id){bindings[item.kind]=previous;records.push({kind:'inherited_complete_normal',activity_id:item.activity_id});save();continue;}
   const panel=await select(item);let command=null,receipt=null,duplicate=null;
   if(previous?.receipt?.artifact_id&&previous.activity_id===item.activity_id){
    command=previous.command;receipt=previous.receipt;bindings[item.kind]=previous;
    await panel.getByRole('button',{name:'读取已保存解释'}).first().waitFor();await panel.getByRole('button',{name:'读取已保存解释'}).first().click();
    await panel.getByRole('button',{name:'显式打开预览',exact:true}).waitFor();
   }else{
    await page.route('**/html/commands',async route=>{
     const req=route.request();command=req.postDataJSON();const original=route.fetch();
     if(item.kind==='energy'){
      await page.waitForTimeout(50);duplicate=await context.request.post(req.url(),{headers:{'X-RetroLume-Session':token,'Origin':input.base},data:command});
      assert.equal(duplicate.status(),200);
     }
     const real=await original;receipt=await real.json();
     if(item.kind==='binomial')await route.abort('failed');else await route.fulfill({response:real});
    },{times:1});
    await panel.getByLabel('交互解释难点').fill(item.kind==='energy'?'C04 机械能参数与图形':'C03 边界 二项概率 n0到20 C04');
    await panel.getByRole('checkbox',{name:'确认父成果、资料与一次模型调用额度'}).check();
    await panel.getByRole('button',{name:'确认生成交互解释',exact:true}).click();await until(()=>receipt!==null,20000);
    assert.equal(receipt.terminal_disposition,'succeeded');assert.ok(receipt.artifact_id);bindings[item.kind]={...item,command,receipt};save();
    await until(async()=>await panel.getByRole('button',{name:'显式打开预览',exact:true}).count()>0||await panel.getByRole('button',{name:'只读核对原键',exact:true}).count()>0,10000);
    if(!await panel.getByRole('button',{name:'显式打开预览',exact:true}).count()){
     await panel.getByRole('button',{name:'只读核对原键',exact:true}).click();
    }
    await panel.getByRole('button',{name:'显式打开预览',exact:true}).waitFor();
   }
   const changed=await context.request.post(input.base+'/api/activities/'+item.activity_id+'/html/commands',{headers:{'X-RetroLume-Session':token,'Origin':input.base},data:{...command,focus:command.focus+' 不同输入'}});
   assert.equal(changed.status(),409);
   const reconciled=await context.request.get(input.base+'/api/activities/'+item.activity_id+'/html/commands/'+command.business_key,{headers:{'X-RetroLume-Session':token}});
   assert.equal((await reconciled.json()).artifact_id,receipt.artifact_id);
   bindings[item.kind]={...item,command,receipt,concurrent_same_key:item.kind==='energy',lost_HTTP_response:item.kind==='binomial',different_input_status:changed.status()};save();
   const opening=page.waitForResponse(r=>new URL(r.url()).pathname.endsWith('/previews')&&r.request().method()==='POST');
   await panel.getByRole('button',{name:'显式打开预览',exact:true}).click();const preview=await (await opening).json();bindings[item.kind].preview=preview;save();
   await panel.getByText(/预览 ready/).waitFor({timeout:10000});await page.screenshot({path:path.join(input.out,'ui-'+item.kind+'-ready.png'),fullPage:true});
   if(item.kind==='energy'){
    await step(panel,'高度 h','3',58.8);await step(panel,'高度 h','0',0);await step(panel,'质量 m','0',0);await step(panel,'高度 h','3',0);
    const before=frames.at(-1)?.sha256;await step(panel,'高度 h','-1',null,{refuse:true});assert.equal(frames.at(-1)?.sha256,before);
    assert.equal(await panel.getByRole('spinbutton',{name:'高度 h',exact:true}).inputValue(),'3');
    const ackBefore=acks.length;await panel.getByRole('button',{name:'恢复默认参数',exact:true}).click();await until(()=>acks.length>ackBefore);assert.equal(acks.at(-1).body.accepted,true);assert.ok(Math.abs(Number(acks.at(-1).body.readouts[0].value)-58.8)<=1e-9);
    records.push({kind:'trusted_number_range_reset',range_control:'质量 m',number_control:'高度 h',reset_ack:acks.at(-1)});save();
   }else{
    assert.ok((await panel.innerText()).includes('<script>alert(1)</script>'));assert.ok((await panel.innerText()).includes('</script><img src=x onerror=alert(1)>'));
    assert.equal(await panel.locator('script,img,svg,iframe').count(),0);
    let b=await step(panel,'成功概率 p','0.5',.375);assert.deepEqual(b.figures[0].points.map(p=>p[1]),[.125,.375,.375,.125]);
    await step(panel,'成功次数 k','0',.125);await step(panel,'成功概率 p','0',1);await step(panel,'成功概率 p','1',0);
    await step(panel,'成功次数 k','3',1);await step(panel,'成功次数 k','2',0);await step(panel,'成功次数 k','0',0);
    await step(panel,'试验次数 n','0',1);await step(panel,'试验次数 n','1',0);await step(panel,'成功概率 p','0.25',.75);
    await step(panel,'成功次数 k','1',.25);b=await step(panel,'试验次数 n','20',pmf(20,1,.25));assert.equal(b.figures[0].count,21);
    await step(panel,'成功次数 k','21',null,{refuse:true});await step(panel,'试验次数 n','1.5',null,{refuse:true});
    await page.route('**/inputs',async route=>{const body=route.request().postDataJSON();body.event.value='1.05';body.payload_sha256=sha(canonical(body.event));await route.continue({postData:canonical(body)});},{times:1});
    await step(panel,'成功概率 p','0.25',null,{refuse:true});
   }
   await panel.getByRole('button',{name:/回查资料/}).first().click();await panel.getByLabel('交互解释引用原文').waitFor();
   records.push({kind:'source_lookup',activity_id:item.activity_id,parent:item.parent,body:await panel.getByLabel('交互解释引用原文').innerText()});
   await page.screenshot({path:path.join(input.out,'ui-'+item.kind+'-complete.png'),fullPage:true});
   await stopAndWait(panel,{activity_id:item.activity_id,...preview});bindings[item.kind].normal_complete=true;save();
   await panel.getByRole('button',{name:'停止并回到学习',exact:true}).click();await until(async()=>await page.getByRole('region',{name:'交互解释',exact:true}).count()===0);
   records.push({kind:'return_to_parent',activity_id:item.activity_id,parent:item.parent});save();
   const before=requests.length;await page.reload({waitUntil:'domcontentloaded'});await page.waitForTimeout(500);
   assert.equal(requests.slice(before).filter(r=>r.method==='POST').length,0);records.push({kind:'refresh_only_GET',activity_id:item.activity_id});save();
  }
  // 两个额外生命周期，真实迟到HTTP/已解码PNG/引用/stop回包横跨旧owner与新代次。
  const energy=bindings.energy;let panel=await select(energy);await panel.getByRole('button',{name:'读取已保存解释'}).first().click();
  let opening=page.waitForResponse(r=>new URL(r.url()).pathname.endsWith('/previews')&&r.request().method()==='POST');await panel.getByRole('button',{name:'显式打开预览',exact:true}).click();
  const old=await (await opening).json();await panel.getByText(/预览 ready/).waitFor({timeout:10000});await step(panel,'高度 h','0',0);
  await page.evaluate(()=>{globalThis.__t111_hold_bitmap=true;});await until(()=>page.evaluate(()=>!!globalThis.__t111_bitmap));
  let lateFrame=null,lateReference=null,lateStop=null;
  await page.route('**/frames?**',async route=>{const r=await route.fetch();lateFrame={route,response:r,bytes:await r.body()};},{times:1});
  await page.route('**/citations/*',async route=>{const r=await route.fetch();lateReference={route,response:r};},{times:1});
  await panel.getByRole('button',{name:/回查资料/}).first().click();await until(()=>!!lateReference&&!!lateFrame);
  await page.route('**/stop',async route=>{const r=await route.fetch();lateStop={route,response:r};},{times:1});
  await panel.getByRole('button',{name:'停止并回到学习',exact:true}).click();await until(()=>!!lateStop);
  // 在停止回包待处理时换父视图，再建立新owner和新generation。
  await page.locator('[data-activity-id="'+bindings.binomial.activity_id+'"]').click();
  const freshItem=bindings.binomial;panel=await select(freshItem);await panel.getByRole('button',{name:'读取已保存解释'}).first().click();
  const lastPid=old.preview_id,deadline=Date.now()+15000;
  while(Date.now()<deadline){const r=await context.request.get(input.base+'/api/activities/'+energy.activity_id+'/html/previews/'+lastPid,{headers:{'X-RetroLume-Session':token}});if((await r.json()).state==='stopped')break;await page.waitForTimeout(60);}
  opening=page.waitForResponse(r=>new URL(r.url()).pathname.endsWith('/previews')&&r.request().method()==='POST');await panel.getByRole('button',{name:'显式打开预览',exact:true}).click();
  const fresh=await (await opening).json();assert.notEqual(fresh.preview_id,old.preview_id);assert.notEqual(fresh.owner_id,old.owner_id);assert.notEqual(fresh.generation,old.generation);
  await panel.getByText(/预览 ready/).waitFor({timeout:10000});await step(panel,'成功概率 p','0.5',.375);
  await lateFrame.route.fulfill({response:lateFrame.response});await lateReference.route.fulfill({response:lateReference.response});await lateStop.route.fulfill({response:lateStop.response});
  await page.evaluate(()=>globalThis.__t111_release_bitmap());await page.waitForTimeout(700);
  assert.equal(await panel.count(),1);assert.ok((await panel.innerText()).includes('0.375'));assert.equal(await panel.getByLabel('交互解释引用原文').count(),0);
  records.push({kind:'late_actual_bytes_guard',old_preview_id:old.preview_id,new_preview_id:fresh.preview_id,old_owner_id:old.owner_id,new_owner_id:fresh.owner_id,
    old_activity_id:energy.activity_id,new_activity_id:freshItem.activity_id,old_parent:energy.parent,new_parent:freshItem.parent,
    old_generation:old.generation,new_generation:fresh.generation,late_HTTP_png_sha256:sha(lateFrame.bytes),decoded_png:await page.evaluate(()=>globalThis.__t111_bitmap),late_reference:true,late_stop:true,old_view_not_revived:true});save();
  // 查询真实浏览器可见性；若平台不支持切后台，保留明确范围，不用属性伪造。
  const other=await context.newPage();await other.goto('about:blank');await other.bringToFront();await page.waitForTimeout(400);
  let hidden=await page.evaluate(()=>document.hidden);await other.close();
  if(!hidden){
   const cdp=await context.newCDPSession(page);
   try{const actual=await cdp.send('Browser.getWindowForTarget');await cdp.send('Browser.setWindowBounds',{windowId:actual.windowId,bounds:{windowState:'minimized'}});
    await page.waitForTimeout(400);hidden=await page.evaluate(()=>document.hidden);records.push({kind:'actual_browser_window_minimize',windowId:actual.windowId,hidden});
    await cdp.send('Browser.setWindowBounds',{windowId:actual.windowId,bounds:{windowState:'normal'}});
   }catch(error){records.push({kind:'actual_window_visibility_unavailable',error:String(error)});}finally{await cdp.detach();}
  }
  records.push({kind:'actual_visibility',hidden});save();
  if(!hidden)await panel.getByRole('button',{name:'停止并回到学习',exact:true}).click();
  await page.goto('about:blank');await page.waitForTimeout(3000);records.push({kind:'unload_and_owner_loss',preview_id:fresh.preview_id});save();
  assert.equal(dialogs.length,0);
  fs.writeFileSync(path.join(input.out,'ui-result.json'),JSON.stringify({status:'PASS_NORMAL_UI_AND_LATE_GUARDS',bindings,actual_hidden_supported:hidden,dialogs},null,2));
 }catch(error){save();await page.screenshot({path:path.join(input.out,'ui-failure.png'),fullPage:true}).catch(()=>{});throw error;}
 finally{await context.close();await Promise.allSettled(pending);save();}
};
