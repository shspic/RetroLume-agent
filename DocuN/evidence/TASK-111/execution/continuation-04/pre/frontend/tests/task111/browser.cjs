"use strict";
// 使用真实主应用、可信控件和远端PNG；不将组件mock签为完整链。
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const pw=require('../../node_modules/playwright');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),token=process.env.RETROLUME_TASK111_BROWSER_SESSION;
(async()=>{
 const browser=await pw.chromium.launch({headless:true});const context=await browser.newContext();const page=await context.newPage();
 const records=[],acks=[],frames=[],pending=[];
 page.on('response',response=>{
  const pathname=new URL(response.url()).pathname;
  if(pathname.endsWith('/inputs'))pending.push(response.json().then(body=>{acks.push(body);fs.writeFileSync(path.join(input.out,'actual-remote-acks.json'),JSON.stringify(acks,null,2));}).catch(()=>{}));
  if(pathname.endsWith('/frames')&&response.status()===200)pending.push(response.body().then(body=>{
    if(body.length>524288)throw Error('frame output bound');
    const name='remote-frame-'+frames.length+'.png';fs.writeFileSync(path.join(input.out,name),body);frames.push({path:name,bytes:body.length,url_path:pathname});
    fs.writeFileSync(path.join(input.out,'actual-remote-frames.json'),JSON.stringify(frames,null,2));
  }).catch(()=>{}));
 });
 try{
  for(const item of input.cases){
   await page.goto(input.base,{waitUntil:'domcontentloaded'});
   await page.getByRole('button',{name:/学习活动/}).first().click().catch(()=>{});
   await page.locator('[data-activity-id="'+item.activity_id+'"]').click();
   if(item.parent?.kind==='teaching'){
     await page.getByRole('region',{name:'教学工作区',exact:true}).waitFor();
     await page.getByRole('button',{name:item.kind==='energy'?'交互解释当前练习':'交互解释当前反馈'}).click();
   }else{
     await page.locator('.ws-op').filter({hasText:item.operation_id}).first().click();
     await page.getByRole('button',{name:'交互解释此答案段'}).first().click();
   }
   const panel=page.getByRole('region',{name:'交互解释',exact:true});
   // 打开已有真实生成成果，刷新不触发POST模型或容器。
   await panel.getByRole('button',{name:'读取已保存解释'}).first().click();
   await panel.getByRole('button',{name:'显式打开预览'}).click();
   await panel.getByText(/预览 ready/).waitFor({timeout:10000});
   await page.screenshot({path:path.join(input.out,'ui-'+item.kind+'-ready.png'),fullPage:true});
   for(const step of item.steps){
    const field=panel.getByRole('spinbutton',{name:step.label});
    if(await field.count())await field.fill(step.value);else {
      const slider=panel.getByRole('slider',{name:step.label});await slider.focus();await slider.press('Home');
      const minimum=Number(await slider.getAttribute('min')),increment=Number(await slider.getAttribute('step'));
      for(let i=0;i<Math.round((Number(step.value)-minimum)/increment);i++)await slider.press('ArrowRight');
    }
    const before=acks.length;await panel.getByRole('button',{name:'应用'+step.label,exact:true}).press('Enter');
    const until=Date.now()+5000;while(acks.length===before&&Date.now()<until)await page.waitForTimeout(50);
    assert.ok(acks.length>before,'real remote ACK missing');const last=acks.at(-1);
    assert.equal(last.accepted,true);assert.ok(Math.abs(Number(last.readouts[0].value)-Number(step.expect.match(/[-+]?\d*\.?\d+/)[0]))<=1e-9,'independent ACK numerical oracle');
    await panel.getByText(new RegExp(step.expect.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))).first().waitFor({timeout:5000});
    await page.waitForTimeout(2000);
    await page.screenshot({path:path.join(input.out,'ui-'+item.kind+'-'+records.length+'.png'),fullPage:true});
    records.push({kind:item.kind,input:step,visible:await panel.innerText()});
   }
   await panel.getByRole('button',{name:/回查资料/}).first().click();
   await panel.getByLabel('交互解释引用原文').waitFor();
   await panel.getByRole('button',{name:'停止预览',exact:true}).click();
   await panel.getByText(/预览 stopped/).waitFor({timeout:15000});
   assert.equal(await panel.getByRole('spinbutton').first().isEnabled().catch(()=>false),false);
   await page.reload({waitUntil:'domcontentloaded'});
   records.push({kind:item.kind,refresh:'readonly',html:await page.locator('body').innerText()});
  }
  fs.writeFileSync(path.join(input.out,'browser-effects.json'),JSON.stringify(records,null,2));
 }catch(error){await page.screenshot({path:path.join(input.out,'ui-failure.png'),fullPage:true}).catch(()=>{});throw error;}
 finally{await Promise.allSettled(pending);fs.writeFileSync(path.join(input.out,'browser-effects.json'),JSON.stringify(records,null,2));await browser.close();}
})().catch(error=>{process.stderr.write(String(error.stack));process.exitCode=1;});
