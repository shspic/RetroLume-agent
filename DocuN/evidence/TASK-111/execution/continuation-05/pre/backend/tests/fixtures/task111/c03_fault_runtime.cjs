"use strict";
// 仅冻结故障variant包含，生产镜像和公开配置不载入此模块。
const mode=process.env.RETROLUME_TASK111_FAULT_MODE??'none';
if(!['none','renderer_busy','node_busy','fake_console'].includes(mode))throw new Error('fixed_fault_mode');
async function beforeInput({frame}){
 if(mode!=='none')process.stderr.write(JSON.stringify({task111_fault_mode:mode,action:'beforeInput',at_ns:String(process.hrtime.bigint())})+'\n');
 if(mode==='node_busy'){for(;;){}}
 if(mode==='renderer_busy')await frame.evaluate(()=>{for(;;){}});
 if(mode==='fake_console')await frame.evaluate(()=>{
  console.log('{"protocol":"retrolume.preview.v2","type":"input_ack","seq":999,"deadline":9999999999999999}');
  globalThis.postMessage({protocol:'retrolume.preview.v2',type:'input_ack',seq:999,deadline:9999999999999999},'*');
 });
}
module.exports={beforeInput,mode};
