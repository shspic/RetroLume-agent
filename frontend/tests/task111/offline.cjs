"use strict";
// 独立手算期望与跨语言边界，不用同一实现计算自己的oracle。
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const rt=require('../../../deploy/preview/runtime.cjs'),data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
for(const value of data.valid)rt.validate(value,value.citations);
for(const [name,value] of data.invalid)assert.throws(()=>rt.validate(value,['lc_synthetic_energy']),undefined,name);
function values(desc){return new Map(desc.inputs.map(c=>[c.id,c.default]));}
const energy=data.valid[0],input=values(energy);
assert.ok(Math.abs(rt.evaluate(energy,input).values.hcalc_energy-58.8)<=1e-9);input.set('hctl_h','0');assert.equal(rt.evaluate(energy,input).values.hcalc_energy,0);
input.set('hctl_m','0');input.set('hctl_h','3');assert.equal(rt.evaluate(energy,input).values.hcalc_energy,0);input.set('hctl_h','-1');assert.throws(()=>rt.evaluate(energy,input));
const probability=data.valid[1],p=values(probability);
let snapshot=rt.evaluate(probability,p);assert.ok(Math.abs(snapshot.values.hcalc_pmf-.375)<=1e-9);
assert.deepEqual(snapshot.views[1].points.map(x=>x.y),[.125,.375,.375,.125]);
p.set('hctl_p','0');p.set('hctl_k','0');assert.equal(rt.evaluate(probability,p).values.hcalc_pmf,1);
p.set('hctl_p','1');p.set('hctl_k','3');assert.equal(rt.evaluate(probability,p).values.hcalc_pmf,1);
p.set('hctl_k','2');assert.equal(rt.evaluate(probability,p).values.hcalc_pmf,0);
p.set('hctl_k','4');assert.throws(()=>rt.evaluate(probability,p));
rt.controlValue(probability.inputs[2],'0.3');for(const bad of ['0.30','NaN','-0','1.1'])assert.throws(()=>rt.controlValue(probability.inputs[2],bad));
console.log(JSON.stringify({status:'PASS',invalid:data.invalid.length,normal_oracle:'independent arithmetic constants',syntax:'closed data language'}));
