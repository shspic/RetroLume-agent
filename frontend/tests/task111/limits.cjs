"use strict";
// 新增上界覆盖采用独立有限算术期望，不替代真实browser/DOM/停止验证。
const fs=require('node:fs'),assert=require('node:assert/strict');
const rt=require('../../../deploy/preview/runtime.cjs');
const data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const binomial=data.binomial,values=new Map(binomial.inputs.map(c=>[c.id,c.default]));
values.set('hctl_n','20');values.set('hctl_k','20');values.set('hctl_p','0.5');
let result=rt.evaluate(binomial,values);
assert.ok(Math.abs(result.values.hcalc_pmf-1/1048576)<=1e-9);
assert.equal(result.views[1].points.length,21);
assert.ok(Math.abs(result.views[1].points.reduce((sum,p)=>sum+p.y,0)-1)<=1e-9);
for(const p of ['0','1']){
  values.set('hctl_n','0');values.set('hctl_k','0');values.set('hctl_p',p);
  result=rt.evaluate(binomial,values);assert.equal(result.values.hcalc_pmf,1);
  assert.deepEqual(result.views[1].points.map(p=>p.y),[1]);
}
const upper=data.upper;rt.validate(upper,upper.citations);
assert.throws(()=>rt.evaluate(upper,new Map(upper.inputs.map(c=>[c.id,c.default]))),/calculation_limit/);
console.log(JSON.stringify({classification:'OFFLINE_NUMERIC_ONLY',bars:21,n0_endpoints:true,independent_tail:'1/1048576',step_limit:'finite legal description rejected at 50000'}));
