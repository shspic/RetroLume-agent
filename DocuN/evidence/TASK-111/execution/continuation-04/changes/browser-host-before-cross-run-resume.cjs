"use strict";
// 本卡最后一个主browser实例持续承担有据修正；不新增launch或公开控制接口。
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),pw=require('../../node_modules/playwright');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),token=process.env.RETROLUME_TASK111_BROWSER_SESSION;
const save=(name,data)=>fs.writeFileSync(path.join(input.out,name),JSON.stringify(data,null,2));
(async()=>{
 const browser=await pw.chromium.launch({headless:true});let success=false,attempt=0,resume={};
 const until=Date.now()+Math.min(input.remaining_ms??500000,500000);
 const cutoff=setTimeout(()=>void browser.close(),Math.max(1,until-Date.now()));
 save('browser-host-owner.json',{node_pid:process.pid,launches:1,deadline_ms:until});
 try{
  while(Date.now()<until){
   attempt++;const folder=path.join(input.out,'ui-attempt-'+String(attempt).padStart(2,'0'));fs.mkdirSync(folder);
   const modulePath=require.resolve('./c04_ui_workflow.cjs');delete require.cache[modulePath];
   const workflow=require(modulePath);save('browser-attempt-'+attempt+'.json',{folder,source_sha256:crypto.createHash('sha256').update(fs.readFileSync(modulePath)).digest('hex')});
   try{
    await workflow({browser,input:{...input,out:folder,resume_bindings:resume},token});
    for(const name of ['ui-result.json','ui-effects.json'])fs.copyFileSync(path.join(folder,name),path.join(input.out,name));
    success=true;break;
   }catch(error){
    save('browser-paused.json',{attempt,folder,error:String(error.stack),same_browser_remains_open:true});
    const effects=JSON.parse(fs.readFileSync(path.join(folder,'ui-effects.json'),'utf8'));resume={...resume,...effects.bindings};
    // 只停止本实例实际保存的会话，不重置任何budget或生成键。
    for(const item of Object.values(resume)){
     if(!item.preview)continue;const base=input.base+'/api/activities/'+item.activity_id+'/html/previews/'+item.preview.preview_id;
     await fetch(base+'/stop',{method:'POST',headers:{'X-RetroLume-Session':token,'Origin':input.base,'Content-Type':'application/json'},body:JSON.stringify({generation:item.preview.generation,stop_key:crypto.randomUUID(),reason:'user'})}).catch(()=>{});
     const bound=Date.now()+15000;
     while(Date.now()<bound){const response=await fetch(base,{headers:{'X-RetroLume-Session':token}}).catch(()=>null);if(!response)break;
      const row=await response.json();if(['stopped','cleanup_unconfirmed'].includes(row.state))break;await new Promise(r=>setTimeout(r,100));}
    }
    const command=path.join(input.out,'browser-control-'+attempt+'.json');
    while(Date.now()<until&&!fs.existsSync(command))await new Promise(r=>setTimeout(r,100));
    if(!fs.existsSync(command)||JSON.parse(fs.readFileSync(command,'utf8')).action!=='retry')break;
   }
  }
 }finally{clearTimeout(cutoff);await browser.close();save('browser-host-final.json',{launches:1,attempts:attempt,closed:true,success});}
 if(!success)process.exitCode=1;
})().catch(error=>{process.stderr.write(String(error.stack));process.exitCode=1;});
