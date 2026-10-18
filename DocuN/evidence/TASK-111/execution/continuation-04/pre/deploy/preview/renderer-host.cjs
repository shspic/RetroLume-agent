"use strict";
// 生产v2宿主，只有有限匿名管道数据；不复用已封存h0 runner。
const fs=require('node:fs'),crypto=require('node:crypto'),os=require('node:os');
const runtime=require('./runtime.cjs'),pw=require('./vendor/playwright-core');
const {compiledHTML:assembleHTML}=require('./renderer-assembly.cjs');
const {exact,boundedJSON,decodeHeader,validateInit}=require('./renderer-protocol.cjs');
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const MAX_BODY=65536,MAX_HEAD=2048;
let buffer=Buffer.alloc(0),identity=null,initPromise=null,browser=null,page=null,frame=null,context=null;
let inputSeq=0,frameSeq=0,statusSeq=0,lastAck=null,stopping=false,frameBusy=false;
let lastState=null,lastCommittedPNG=null;const engineEvents=[];let baseline=null,browserCdp=null,baselineTargets=null;
let lastFrameAt=0n,pendingFrameTimer=null;
const capabilityEvents={requests:[],downloads:0,filechoosers:0,dialogs:0};
let initStage='load';
function reportHostError(error){
 const value={stage:initStage,error_type:String(error?.name??'Error').slice(0,64),message:String(error?.message??'host_failed').slice(0,1024)};
 process.stderr.write(JSON.stringify(value)+'\n');
}
const manifestBytes=fs.readFileSync('/opt/preview/load-manifest.json'),manifest=JSON.parse(manifestBytes);
for(const [name,hash] of Object.entries(manifest.files))if(sha(fs.readFileSync('/opt/preview/'+name))!==hash)throw new Error('load_manifest_mismatch');
function emit(type,seq,value,binary=null){
 const body=binary??Buffer.from(runtime.canonical(value),'utf8');
 const maximum=type==='frame'?524288:type==='ready'?16384:4096;
 if(body.length>maximum)throw new Error('protocol_output_size');
 const head={protocol:'retrolume.preview.v2',type,preview_id:identity.preview_id,generation:identity.generation,
   artifact_sha256:identity.artifact_sha256,channel_nonce:identity.channel_nonce,seq,body_bytes:body.length,body_sha256:sha(body)};
 if(type==='frame'){head.format='png';head.width=640;head.height=480;}
 const header=Buffer.from(runtime.canonical(head),'utf8');if(header.length>MAX_HEAD)throw new Error('protocol_head_size');
 const prefix=Buffer.alloc(4);prefix.writeUInt32BE(header.length);process.stdout.write(Buffer.concat([prefix,header,body]));
}
function processFacts(){
 const rows=[],errors=[];const own=fs.readlinkSync('/proc/self/ns/pid'),init=fs.readlinkSync('/proc/1/ns/pid');
 const ids=fs.readdirSync('/proc').filter(name=>/^[0-9]+$/.test(name));if(ids.length>256)throw new Error('process_observation_limit');
 for(const id of ids){
  try{
   const text=fs.readFileSync('/proc/'+id+'/status','utf8'),stat=fs.readFileSync('/proc/'+id+'/stat','utf8');
   const row={pid:Number(id),birth_ticks:stat.slice(stat.lastIndexOf(')')+2).trim().split(/\s+/)[19],pid_namespace:fs.readlinkSync('/proc/'+id+'/ns/pid')};
   for(const field of ['Name','PPid','Uid','NoNewPrivs','Seccomp','NSpid','CapEff','CapBnd','Threads']){
    const line=text.split('\n').find(s=>s.startsWith(field+':'));if(!line)throw new Error('missing_process_field');row[field]=line.slice(field.length+1).trim();
   }
   rows.push(row);
  }catch(error){errors.push({pid:Number(id),code:error.code??'read_unconfirmed'});}
 }
 return {kernel:os.release(),own_pid:process.pid,own_uid:process.getuid(),own_gid:process.getgid(),own_namespace:own,
   init_namespace:init,rows,errors,complete:errors.length===0,source:'proc_private_pid_namespace'};
}
function compiledHTML(){
 const script=fs.readFileSync('/opt/preview/runtime.cjs','utf8'),style=fs.readFileSync('/opt/preview/runtime.css','utf8');
 return assembleHTML(fs.readFileSync('/opt/preview/runtime.html','utf8'),script,style);
}
async function engineSnapshot(){
 const result=[];
 for(const f of page.frames()){
  const session=await context.newCDPSession(f);try{
   const tree=await session.send('Page.getFrameTree');const dom=await session.send('DOMSnapshot.captureSnapshot',{computedStyles:[]});
   const documents=dom.documents.map(d=>({frameId:dom.strings[d.frameId],url:dom.strings[d.documentURL],backendNodeId:d.nodes.backendNodeId[0]}));
   result.push({playwright_url:f.url(),frame:tree.frameTree.frame,documents});
  }finally{await session.detach();}
 }
 return result;
}
async function installFrameObservers(){
 for(const f of page.frames()){
  const session=await context.newCDPSession(f);await session.send('Page.enable');
  for(const name of ['Page.frameAttached','Page.frameNavigated','Page.navigatedWithinDocument','Page.frameDetached'])session.on(name,event=>{
   if(engineEvents.length>=64){stop('observer_limit');return;}
   engineEvents.push({name,frameId:event.frameId??event.frame?.id,url:event.url??event.frame?.url??'',urlFragment:event.frame?.urlFragment??''});
   if(baseline)stop('unexpected_navigation_or_frame');
  });
 }
}
async function fixedObservation(){
 const dom=await frame.evaluate(()=>({runtime_type:typeof globalThis.RetroLumeRuntime?.start,
  script:document.scripts.length===1?document.scripts[0].textContent:null,script_count:document.scripts.length,
  style_count:document.querySelectorAll('style').length,title:document.querySelector('h1')?.textContent??'',
  concept:document.querySelector('main > p')?.textContent??'',canvas_count:document.querySelectorAll('canvas').length,
  forbidden_nodes:document.querySelectorAll('a,form,iframe,img,svg,link,object,embed,video,audio,input[type=file]').length}));
 const script=dom.script;delete dom.script;dom.script_sha256=typeof script==='string'?sha(Buffer.from(script,'utf8')):null;
 const targets=(await browserCdp.send('Target.getTargets')).targetInfos.filter(t=>['page','iframe'].includes(t.type)).map(t=>({id:t.targetId,type:t.type,url:t.url}));
 return {frames:await engineSnapshot(),targets,dom,capability_events:capabilityEvents};
}
async function initialize(body){
 initStage='init_fields';
 emit('status',++statusSeq,{state:'initializing',reason_code:'bootstrap_identity',last_input_seq:0,processes:processFacts(),load_manifest_sha256:sha(manifestBytes)});
 validateInit(body,manifest.renderer_sha256);
 const executable=pw.chromium.executablePath();if(sha(fs.readFileSync(executable))!==manifest.browser_sha256)throw new Error('browser_identity');
 initStage='sandbox_browser_launch';browser=await pw.chromium.launch({executablePath:executable,headless:true,chromiumSandbox:true,args:['--enable-automation'],ignoreDefaultArgs:['--disable-popup-blocking'],timeout:8000});
 const cdp=await browser.newBrowserCDPSession(),version=await cdp.send('Browser.getVersion'),command=await cdp.send('Browser.getBrowserCommandLine');browserCdp=cdp;
 await cdp.send('Target.setDiscoverTargets',{discover:true});
 cdp.on('Target.targetCreated',event=>{if(baselineTargets&&['page','iframe'].includes(event.targetInfo.type)&&!baselineTargets.some(t=>t.id===event.targetInfo.targetId))stop('unexpected_target');});
 if(version.product!=='Chrome/151.0.7922.34'||command.arguments.includes('--no-sandbox')||process.getuid()!==10001)throw new Error('sandbox_identity');
 context=await browser.newContext({viewport:{width:640,height:480},deviceScaleFactor:1,serviceWorkers:'block',acceptDownloads:false});
 context.on('request',request=>{if(capabilityEvents.requests.length<8)capabilityEvents.requests.push({url:request.url().slice(0,256),type:request.resourceType()});});
 await context.route(()=>true,route=>route.abort());await context.routeWebSocket(()=>true,socket=>socket.close());
 initStage='sandbox_attestation';const sandboxPage=await context.newPage();await sandboxPage.goto('chrome://sandbox');const sandbox=await sandboxPage.locator('body').innerText();await sandboxPage.close();
 page=await context.newPage();page.on('dialog',dialog=>{capabilityEvents.dialogs++;dialog.dismiss();});
 page.on('download',()=>{capabilityEvents.downloads++;stop('unexpected_download');});
 page.on('filechooser',()=>{capabilityEvents.filechoosers++;stop('unexpected_filechooser');});
 const style='html,body{margin:0;width:640px;height:480px}iframe{border:0;width:640px;height:480px}';
 const scriptHash=crypto.createHash('sha256').update(fs.readFileSync('/opt/preview/runtime.cjs')).digest('base64');
 const cssHash=crypto.createHash('sha256').update(fs.readFileSync('/opt/preview/runtime.css')).digest('base64');
 const rootStyleHash=crypto.createHash('sha256').update(style).digest('base64');
 const rootPolicy="default-src 'none'; script-src 'sha256-"+scriptHash+"'; style-src 'sha256-"+cssHash+"' 'sha256-"+rootStyleHash+"'; frame-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'; worker-src 'none'";
 initStage='trusted_root';await page.setContent('<!doctype html><html><head><meta http-equiv="Content-Security-Policy" content="'+rootPolicy+'"><style>'+style+'</style></head><body></body></html>');
 // srcdoc只接镜像固定程序，模型数据从不参与其字符串构造。
 await page.evaluate(html=>{const f=document.createElement('iframe');f.id='render-frame';f.setAttribute('sandbox','allow-scripts');f.srcdoc=html;document.body.appendChild(f);},compiledHTML());
 initStage='trusted_frame';frame=await (await page.$('#render-frame')).contentFrame();if(!frame||frame.parentFrame()!==page.mainFrame())throw new Error('frame_identity');
 // srcdoc提交与固定脚本执行是异步的；握手前等精确受信API，不延外层ready8。
 await frame.waitForFunction(()=>typeof globalThis.RetroLumeRuntime?.start==='function',null,{timeout:3000});
 lastState=await frame.evaluate(data=>globalThis.RetroLumeRuntime.start(data),body.description);
 if(page.frames().length!==2)throw new Error('frame_count');
 await installFrameObservers();baseline=await engineSnapshot();
 baselineTargets=(await cdp.send('Target.getTargets')).targetInfos.filter(t=>['page','iframe'].includes(t.type)).map(t=>({id:t.targetId,type:t.type,url:t.url}));
 emit('ready',0,{load_manifest_sha256:sha(manifestBytes),renderer_sha256:manifest.renderer_sha256,description_sha256:body.description_sha256,
   node:process.version,playwright:require('./vendor/playwright-core/package.json').version,version,arguments:command.arguments,
   sandbox,processes:processFacts(),baseline,targets:baselineTargets,readouts:readouts(lastState),observation:await fixedObservation()});
 await emitFrame();
 const timer=setInterval(()=>{if(stopping){clearInterval(timer);return;}if(!frameBusy)emitFrame().catch(()=>stop('frame_failed'));},334);
}
function readouts(value){return (value.views??[]).filter(v=>v.kind==='readout').map(v=>({id:v.id,value:String(v.value),unit:v.unit}));}
async function emitFrame(){
 if(stopping||frameBusy||!page)return;
 const remaining=334-Number(process.hrtime.bigint()-lastFrameAt)/1000000;
 if(remaining>0){
  if(pendingFrameTimer===null)pendingFrameTimer=setTimeout(()=>{pendingFrameTimer=null;emitFrame().catch(()=>stop('frame_failed'));},Math.ceil(remaining));
  return;
 }
 frameBusy=true;
 try{
  // 拒绝更新只回报ACK错误，画面继续使用上一张完整有效快照。
  const snapshot=lastState;let png=snapshot?.accepted===false?lastCommittedPNG:await page.screenshot({type:'png',timeout:2000});
  // 截图期间有新快照或拒绝发生，不把跨快照捕获写成有效画面。
  if(lastState!==snapshot)png=lastCommittedPNG;
  if(!png)throw new Error('committed_frame_missing');lastCommittedPNG=png;emit('frame',++frameSeq,null,png);lastFrameAt=process.hrtime.bigint();
 }finally{frameBusy=false;}
}
async function input(body,seq){
 if(seq===inputSeq){if(lastAck?.hash!==sha(Buffer.from(runtime.canonical(body),'utf8')))throw new Error('input_seq_conflict');emit('input_ack',seq,lastAck.value);return;}
 if(seq!==inputSeq+1||seq>1200)throw new Error('input_seq');
 const result=await frame.evaluate(event=>globalThis.RetroLumeRuntime.dispatch(event),body);
 const value={accepted:result.accepted,error_code:result.error_code,readouts:readouts(result),steps:result.steps,
   figures:result.views.filter(v=>v.kind!=='readout').map(v=>({id:v.id,count:v.points.length,
      points:v.points.slice(0,21).map(p=>[p.x,p.y]),points_sha256:sha(Buffer.from(runtime.canonical(v.points),'utf8'))})),input_values:result.inputs};
 inputSeq=seq;lastState=result;lastAck={hash:sha(Buffer.from(runtime.canonical(body),'utf8')),value};emit('input_ack',seq,value);await emitFrame();
 emit('status',++statusSeq,{state:'observation',reason_code:'fixed_input_observation',last_input_seq:seq,observation:await fixedObservation()});
}
function stop(reason){
 if(stopping)return;stopping=true;
 try{if(identity)emit('status',++statusSeq,{state:'stopping',reason_code:reason,last_input_seq:inputSeq,engine_events:engineEvents.slice(-16)});}catch{}
 Promise.resolve(browser?.close()).finally(()=>process.exit(0));setTimeout(()=>process.exit(1),1900);
}
let chain=Promise.resolve();
process.stdin.on('data',chunk=>{
 try{
  if(buffer.length+chunk.length>MAX_BODY+MAX_HEAD+4)throw new Error('protocol_buffer');buffer=Buffer.concat([buffer,chunk]);
  while(buffer.length>=4){
   const length=buffer.readUInt32BE(0);if(length<1||length>MAX_HEAD)throw new Error('protocol_header');if(buffer.length<4+length)return;
   const h=decodeHeader(buffer.subarray(4,4+length));
   if(buffer.length<4+length+h.body_bytes)return;
   const bytes=buffer.subarray(4+length,4+length+h.body_bytes);buffer=buffer.subarray(4+length+h.body_bytes);
   if(sha(bytes)!==h.body_sha256)throw new Error('protocol_hash');const body=boundedJSON(bytes,MAX_BODY);
   if(!identity){if(h.type!=='init'||h.seq!==0)throw new Error('init_required');identity=h;initPromise=initialize(body);chain=initPromise;}
   else{
    for(const field of ['preview_id','generation','artifact_sha256','channel_nonce'])if(h[field]!==identity[field])throw new Error('protocol_session');
    if(h.type==='stop'){exact(body,['reason']);stop('user');}
    else if(h.type==='input')chain=chain.then(()=>input(body,h.seq));else throw new Error('protocol_type');
   }
   chain.catch(error=>{reportHostError(error);stop('host_failed');});
  }
 }catch{stop('protocol_failed');}
});
process.stdin.on('end',()=>stop('pipe_closed'));process.on('SIGTERM',()=>stop('external_stop'));
process.on('uncaughtException',()=>stop('host_failed'));process.on('unhandledRejection',()=>stop('host_failed'));
