"use strict";
// 校验调用生产纯函数；实际生命周期反例另由PG/host夹具完成。
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const runtime=require(path.join(root,'deploy/preview/runtime.cjs')),protocol=require(path.join(root,'deploy/preview/renderer-protocol.cjs'));
const bytes=v=>Buffer.from(runtime.canonical(v)),sha=v=>crypto.createHash('sha256').update(bytes(v)).digest('hex');
const records=[];
const valid={protocol:'retrolume.preview.v2',type:'init',preview_id:'11111111-1111-4111-8111-111111111111',generation:1,artifact_sha256:'a'.repeat(64),channel_nonce:'b'.repeat(64),seq:0,body_bytes:100,body_sha256:'c'.repeat(64)};
assert.deepEqual(protocol.decodeHeader(bytes(valid)),valid);
for(const [name,mutate] of [['v1',h=>h.protocol='retrolume.preview.v1'],['unknown',h=>h.unknown=true],['bad_nonce',h=>h.channel_nonce='x'],['bad_hash',h=>h.body_sha256='x'],['generation_bool',h=>h.generation=true],['seq_negative',h=>h.seq=-1],['size',h=>h.body_bytes=65537]]){
 const value={...valid};mutate(value);assert.throws(()=>protocol.decodeHeader(bytes(value)));records.push({name,status:'REJECTED_REAL_HEADER_FUNCTION'});
}
for(const raw of [Buffer.from('{"a":1,"a":1}'),Buffer.from([0xff]),Buffer.from('x'.repeat(2049))])assert.throws(()=>protocol.boundedJSON(raw,2048));
const init={schema:'retrolume.preview.init.v2',description:input.energy,description_sha256:sha(input.energy),renderer_sha256:input.renderer,viewport:{width:640,height:480}};
protocol.validateInit(init,input.renderer);
for(const [name,mutate] of [['rawHTML',v=>v.html='<script>1</script>'],['v1_init',v=>v.schema='retrolume.preview.init.v1'],['renderer',v=>v.renderer_sha256='0'.repeat(64)],['description_hash',v=>v.description_sha256='0'.repeat(64)],['viewport',v=>v.viewport={width:1,height:480}]]){
 const value=structuredClone(init);mutate(value);assert.throws(()=>protocol.validateInit(value,input.renderer));records.push({name,status:'REJECTED_REAL_INIT_FUNCTION'});
}
const entries=['#hash','history','data:text/html,x','blob:x','file:///etc/passwd','http://127.0.0.1:1','https://example.invalid','popup','newframe','download','chooser','fetch','xhr','ws','system','model_tool','markup','parent','top','blank','named','form'];
for(const capability of entries){const v=structuredClone(init);v.description.actions.push({id:'hact_bad',kind:capability,url:capability});v.description_sha256=sha(v.description);assert.throws(()=>protocol.validateInit(v,input.renderer));records.push({capability,status:'REJECTED_REAL_HOST_INIT'});}
runtime.validate(input.limited);const values=new Map(input.limited.inputs.map(c=>[c.id,c.default]));const baseline=runtime.evaluate(input.limited,values);
assert.equal(baseline.values.hcalc_root,1);values.set('hctl_x','-1');assert.throws(()=>runtime.evaluate(input.limited,values),/calculation_domain_error/);
values.set('hctl_x','1');values.set('hctl_p','0.5');assert.throws(()=>runtime.evaluate(input.limited,values),/calculation_limit/);
fs.writeFileSync(path.join(input.out,'host-boundary-result.json'),JSON.stringify({status:'PASS_ACTUAL_PRODUCTION_BOUNDARIES',records,finite_limit_sample:{initial_steps:baseline.steps,curve_points:baseline.views[1].points.length,at_nonzero_probability:'calculation_limit'},real_browser_execution:false},null,2));
