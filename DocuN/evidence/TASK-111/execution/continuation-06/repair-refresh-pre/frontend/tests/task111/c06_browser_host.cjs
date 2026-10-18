"use strict";
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),pw=require('../../node_modules/playwright');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),token=process.env.RETROLUME_TASK111_BROWSER_SESSION;
const save=(name,row)=>fs.writeFileSync(path.join(input.out,name),JSON.stringify(row,null,2));
(async()=>{
 const browser=await pw.chromium.launch({headless:false,args:['--window-position=-20000,-20000','--window-size=1280,900','--disable-features=CalculateNativeWinOcclusion']});
 const deadline=Date.now()+input.remaining_ms,timer=setTimeout(()=>void browser.close(),Math.max(1,input.remaining_ms));let attempt=0,passed=false,methods=['real_hidden','READY_unload','READY_active_refresh'];const accepted={};
 save('browser-host-owner.json',{node_pid:process.pid,launches:1,headless:false,dedicated_window:true,deadline_ms:deadline,only_C06_methods:methods});
 try{
  while(Date.now()<deadline){
   attempt++;const out=path.join(input.out,'tail-attempt-'+attempt);fs.mkdirSync(out);const modulePath=require.resolve('./c06_tail.cjs');delete require.cache[modulePath];save('browser-attempt-'+attempt+'.json',{source_sha256:crypto.createHash('sha256').update(fs.readFileSync(modulePath)).digest('hex'),out,methods});
   try{await require(modulePath)({browser,input:{...input,out,methods},token});passed=true;}
   catch(error){save('browser-paused.json',{attempt,out,error:String(error.stack),context_closed:true,same_browser_alive:true});}
   for(const method of methods){const file=path.join(out,'method-'+method+'.json');if(fs.existsSync(file)){const raw=fs.readFileSync(file),row=JSON.parse(raw);if(row.status==='PASS_REAL_CLIENT_METHOD')accepted[method]={path:file,sha256:crypto.createHash('sha256').update(raw).digest('hex'),row};}}
   save('client-methods-accepted.json',accepted);methods=['real_hidden','READY_unload','READY_active_refresh'].filter(m=>!accepted[m]);
   if(passed&&methods.length===0)break;
   const command=path.join(input.out,'browser-control-'+attempt+'.json');while(Date.now()<deadline&&!fs.existsSync(command))await new Promise(r=>setTimeout(r,100));
   if(!fs.existsSync(command)||JSON.parse(fs.readFileSync(command)).action!=='retry')break;
   passed=false;
  }
 }finally{clearTimeout(timer);await browser.close();save('browser-host-final.json',{attempts:attempt,closed:true,passed:methods.length===0});}
 if(methods.length)process.exitCode=1;else save('tail-result.json',{status:'PASS_ALL_THREE_C06_CLIENT_METHODS',accepted,new_model_calls:0,normal_Native_rerun:false});
})().catch(error=>{process.stderr.write(String(error.stack));process.exitCode=1;});
