'use strict';
// PAK中的普通版权文字只解压复制，不执行其中的HTML/JavaScript。
const fs=require('node:fs'),zlib=require('node:zlib'),crypto=require('node:crypto');
const raw=fs.readFileSync(0),limit=32*1024*1024;
if(raw.length>limit||raw.length<12||raw.readUInt32LE(0)!==5)throw Error('fixed_pak_input');
const count=raw.readUInt16LE(8),aliases=raw.readUInt16LE(10);
if(count>20000||aliases>20000||12+6*(count+1)+4*aliases>raw.length)throw Error('pak_table_bound');
const found=[];
for(let i=0;i<count;i++){
 const id=raw.readUInt16LE(12+6*i),start=raw.readUInt32LE(14+6*i),end=raw.readUInt32LE(20+6*i);
 if(start>end||end>raw.length)throw Error('pak_offset');
 const data=raw.subarray(start,end);let text=data,codec='plain';
 try{
  if(data[0]===0x1f&&data[1]===0x8b){text=zlib.gunzipSync(data,{maxOutputLength:limit});codec='gzip';}
  else if(data[0]===0x1e&&data[1]===0x9b){text=zlib.brotliDecompressSync(data.subarray(8),{maxOutputLength:limit});codec='brotli';}
  if(text.length>limit)continue;
  const value=new TextDecoder('utf-8',{fatal:true}).decode(text);
  if(/<title>Credits<\/title>/i.test(value)&&(value.match(/<pre\b/gi)||[]).length>0){
   found.push({id,start,end,codec,bytes:text.length,sha256:crypto.createHash('sha256').update(text).digest('hex'),copyright_mentions:(value.match(/copyright/gi)||[]).length,pre_count:(value.match(/<pre\b/gi)||[]).length,data:text});
  }
 }catch(error){if(String(error).includes('pak_'))throw error;}
}
if(found.length!==1)throw Error('main_chrome_credits_not_unique');
const result=found[0];fs.writeFileSync(process.argv[2],result.data,{flag:'wx'});delete result.data;
result.pak_sha256=crypto.createHash('sha256').update(raw).digest('hex');process.stdout.write(JSON.stringify(result));
