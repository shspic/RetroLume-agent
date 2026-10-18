'use strict';
// 只解析固定本地PAK的数据表和许可文字，数据不作为JavaScript执行。
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),crypto=require('node:crypto');
const root=__dirname,input=path.join(root,'license-logical-probe/selected/ms-playwright/chromium-1234/chrome-linux64/resources.pak');
const data=fs.readFileSync(input),version=data.readUInt32LE(0),count=data.readUInt16LE(8),aliases=data.readUInt16LE(10);
if(version!==5||count>20000||aliases>20000)throw Error('fixed_pak_header');
const found=[],limits=32*1024*1024;let gzip=0,brotli=0;
for(let i=0;i<count;i++){
 const id=data.readUInt16LE(12+i*6),start=data.readUInt32LE(14+i*6),end=data.readUInt32LE(20+i*6);
 if(start>end||end>data.length)throw Error('pak_offset');
 const payload=data.subarray(start,end);let plain=payload,codec='plain';
 try{
  if(payload[0]===0x1f&&payload[1]===0x8b){plain=zlib.gunzipSync(payload,{maxOutputLength:limits});codec='gzip';gzip++;}
  else if(payload[0]===0x1e&&payload[1]===0x9b){plain=zlib.brotliDecompressSync(payload.subarray(8),{maxOutputLength:limits});codec='brotli';brotli++;}
  if(plain.length>limits)continue;
  const text=new TextDecoder('utf-8',{fatal:true}).decode(plain);
  const mentions=(text.match(/copyright/gi)||[]).length,title=text.match(/<title[^>]*>([^<]*)<\/title>/i)?.[1]??'';
  if(mentions>10&&/<!doctype|<html/i.test(text)){
   const output=path.join(root,'license-logical-probe','pak-html-'+id+'.txt');fs.writeFileSync(output,plain);
   found.push({id,start,end,codec,bytes:plain.length,copyright_mentions:mentions,title,pre_count:(text.match(/<pre\b/gi)||[]).length,sha256:crypto.createHash('sha256').update(plain).digest('hex'),path:output});
  }
 }catch(error){if(error.code!=='ERR_BUFFER_TOO_LARGE'&&!(error instanceof TypeError)&&!String(error).includes('decompress'))continue;}
}
const result={source_sha256:crypto.createHash('sha256').update(data).digest('hex'),version,count,aliases,gzip,brotli,found};
fs.writeFileSync(path.join(root,'license-logical-probe/pak-html-probe.json'),JSON.stringify(result,null,2));
process.stdout.write(JSON.stringify(result));
