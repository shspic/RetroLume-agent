"use strict";
// 生产宿主直接使用的纯管道校验；页面文字没有调用通路。
const crypto=require('node:crypto'),runtime=require('./runtime.cjs');
const HEX=/^[0-9a-f]{64}$/;
function exact(v,names){if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).length!==names.length||names.some(n=>!Object.hasOwn(v,n)))throw new Error('protocol_fields');}
function boundedJSON(bytes,max){
 if(bytes.length<1||bytes.length>max)throw new Error('protocol_size');
 const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes),value=JSON.parse(text);
 if(!Buffer.from(runtime.canonical(value),'utf8').equals(Buffer.from(bytes)))throw new Error('protocol_noncanonical');return value;
}
function decodeHeader(bytes){
 const h=boundedJSON(bytes,2048);
 exact(h,['protocol','type','preview_id','generation','artifact_sha256','channel_nonce','seq','body_bytes','body_sha256']);
 if(h.protocol!=='retrolume.preview.v2'||!HEX.test(h.artifact_sha256)||!HEX.test(h.channel_nonce)||!HEX.test(h.body_sha256)||
    typeof h.preview_id!=='string'||!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(h.preview_id)||!Number.isSafeInteger(h.generation)||h.generation<1||!Number.isSafeInteger(h.seq)||h.seq<0||
    !Number.isSafeInteger(h.body_bytes)||h.body_bytes<1||h.body_bytes>(h.type==='init'?65536:1024))throw new Error('protocol_identity');
 return h;
}
function validateInit(body,renderer){
 exact(body,['schema','description','description_sha256','renderer_sha256','viewport']);
 if(body.schema!=='retrolume.preview.init.v2'||body.renderer_sha256!==renderer||body.viewport?.width!==640||body.viewport?.height!==480||
    runtime.canonical(body.viewport)!=='{"height":480,"width":640}')throw new Error('init_identity');
 if(body.description&&Object.hasOwn(body.description,'constraints')&&!Array.isArray(body.description.constraints))throw new Error('description_constraints_type');
 runtime.validate(body.description);
 if(crypto.createHash('sha256').update(runtime.canonical(body.description),'utf8').digest('hex')!==body.description_sha256)throw new Error('description_hash');
}
module.exports={exact,boundedJSON,decodeHeader,validateInit};
