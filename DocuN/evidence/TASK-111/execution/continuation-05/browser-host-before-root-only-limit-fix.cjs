"use strict";
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),pw=require('../../node_modules/playwright');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),token=process.env.RETROLUME_TASK111_BROWSER_SESSION;
const save=(name,row)=>fs.writeFileSync(path.join(input.out,name),JSON.stringify(row,null,2));
(async()=>{
 const browser=await pw.chromium.launch({headless:false,args:['--window-position=-20000,-20000','--window-size=1280,900','--disable-features=CalculateNativeWinOcclusion']});
 const deadline=Date.now()+Math.min(input.remaining_ms,600000);const timer=setTimeout(()=>void browser.close(),Math.max(1,deadline-Date.now()));let passed=false,attempt=0;
 save('browser-host-owner.json',{node_pid:process.pid,launches:1,headless:false,dedicated_window:true,deadline_ms:deadline});
 try{
  while(Date.now()<deadline){
   attempt++;const out=path.join(input.out,'tail-attempt-'+attempt);fs.mkdirSync(out);const modulePath=require.resolve('./c05_tail.cjs');delete require.cache[modulePath];save('browser-attempt-'+attempt+'.json',{source_sha256:crypto.createHash('sha256').update(fs.readFileSync(modulePath)).digest('hex'),out});
   try{await require(modulePath)({browser,input:{...input,out},token});fs.copyFileSync(path.join(out,'tail-result.json'),path.join(input.out,'tail-result.json'));passed=true;break;}
   catch(error){save('browser-paused.json',{attempt,out,error:String(error.stack),context_closed:true,same_browser_alive:true});
    const command=path.join(input.out,'browser-control-'+attempt+'.json');while(Date.now()<deadline&&!fs.existsSync(command))await new Promise(r=>setTimeout(r,100));
    if(!fs.existsSync(command)||JSON.parse(fs.readFileSync(command)).action!=='retry')break;
   }
  }
 }finally{clearTimeout(timer);await browser.close();save('browser-host-final.json',{attempts:attempt,closed:true,passed});}
 if(!passed)process.exitCode=1;
})().catch(error=>{process.stderr.write(String(error.stack));process.exitCode=1;});
