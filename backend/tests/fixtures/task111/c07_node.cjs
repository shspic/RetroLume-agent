"use strict";
// 离线实际宿主入口；只把浏览器启动截在固定标志，产品JSON/init/runtime链原样执行。
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{EventEmitter}=require('node:events');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),root=path.resolve(__dirname,'../../../..');
const product=path.join(root,'deploy/preview'),protocol=require(path.join(product,'renderer-protocol.cjs'));
const runtime=require(path.join(product,'runtime.cjs')),source=fs.readFileSync(path.join(product,'renderer-host.cjs'),'utf8');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
async function actualHost(header,body){
 const events=[],errors=[],stdin=new EventEmitter();let browserReached=false;
 const fakeProcess={pid:100,getuid:()=>10001,getgid:()=>10001,stdin,stdout:{write:b=>events.push(Buffer.from(b))},stderr:{write:s=>errors.push(s)},on:()=>{},exit:code=>events.push({exit:code})};
 const manifest=Buffer.from(JSON.stringify({files:{},renderer_sha256:input.renderer,browser_sha256:'0'.repeat(64)}));
 const hostFs={...fs,readFileSync:p=>p==='/opt/preview/load-manifest.json'?manifest:fs.readFileSync(p),readlinkSync:()=> 'pid:[100]',readdirSync:()=>[]};
 const pw={chromium:{executablePath(){browserReached=true;throw new Error('OFFLINE_BROWSER_BOUNDARY');}}};
 const sandbox={Buffer,TextDecoder,Promise,setTimeout:()=>0,setInterval:()=>0,clearInterval:()=>{},process:fakeProcess,
  require:name=>name==='node:fs'?hostFs:name==='./vendor/playwright-core'?pw:name.startsWith('./')?require(path.join(product,name)):require(name)};
 const entry=new Function('require','process','Buffer','TextDecoder','setTimeout','setInterval','clearInterval',source);
 entry(sandbox.require,fakeProcess,Buffer,TextDecoder,sandbox.setTimeout,sandbox.setInterval,sandbox.clearInterval);
 const prefix=Buffer.alloc(4);prefix.writeUInt32BE(header.length);stdin.emit('data',Buffer.concat([prefix,header,body]));
 await new Promise(resolve=>setImmediate(resolve));
 return {browserReached,errors:errors.join(''),output_packets:events.filter(x=>Buffer.isBuffer(x)).length};
}
(async()=>{
 const rows=[];
 for(const sample of input.cases){
  const raw=Buffer.from(sample.body_hex,'hex'),header=Buffer.from(sample.header_hex,'hex');let parsed=null,gate=null;
  try{const h=protocol.decodeHeader(header);if(h.body_bytes!==raw.length||h.body_sha256!==hash(raw))throw new Error('wire_identity');
   parsed=protocol.boundedJSON(raw,65536);protocol.validateInit(parsed,input.renderer);gate='accept';
  }catch(e){gate=e.message;}
  const host=await actualHost(header,raw),accepted=host.browserReached;
  if(accepted!==sample.expected||(gate==='accept')!==sample.expected)throw new Error('实际Node入口与预期不符 '+sample.name+' '+JSON.stringify({gate,host}));
  if(sample.name==='internal_BOM'&&parsed.description.title!==sample.internal_title)throw new Error('内部U+FEFF被修改');
  rows.push({name:sample.name,expected:sample.expected,actual:accepted,gate,host,header_bytes:header.length,header_sha256:hash(header),body_bytes:raw.length,body_sha256:hash(raw)});
 }
 fs.writeFileSync(input.out,JSON.stringify({status:'PASS_ACTUAL_NODE_HOST_INGRESS_OFFLINE',renderer:input.renderer,rows,browser_started:false},null,2));
 console.log(JSON.stringify({status:'PASS_ACTUAL_NODE_HOST_INGRESS_OFFLINE',cases:rows.length}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
