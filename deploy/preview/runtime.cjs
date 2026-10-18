"use strict";
// 固定数据语言和计算图形程序；模型数据没有代码、URL、DOM或工具出口。
(function (root) {
  const SCHEMA = "interactive_description.v1";
  const ARITY = new Map(Object.entries({add:2,sub:2,mul:2,div:2,neg:1,abs:1,min:2,max:2,pow_int:2,sqrt:1,sin:1,cos:1,binomial_pmf:3}));
  const prefixes = new Map([['input','hctl_'],['result','hcalc_'],['view','hview_'],['readout','hout_'],['action','hact_']]);
  const encoder = new TextEncoder();
  class DataError extends Error { constructor(code='invalid_interactive_output') { super(code); this.code=code; } }
  function fail(code) { throw new DataError(code); }
  function plain(v) { return v !== null && typeof v === 'object' && !Array.isArray(v) && Object.getPrototypeOf(v) === Object.prototype; }
  function exact(v, required, optional=[]) {
    if (!plain(v) || required.some(k=>!Object.hasOwn(v,k)) || Object.keys(v).some(k=>!required.includes(k)&&!optional.includes(k))) fail();
  }
  function text(v,maximum,empty=false) {
    if(typeof v!=='string'||(!empty&&!v)||[...v].length>maximum||v.includes('\0'))fail();
    for(const ch of v){const n=ch.codePointAt(0);if(n>=0xd800&&n<=0xdfff)fail();}
    return v;
  }
  function list(v,max,min=0){if(!Array.isArray(v)||v.length<min||v.length>max)fail();return v;}
  function canonical(v) {
    function ordered(x){
      if(Array.isArray(x))return x.map(ordered);
      if(plain(x)){const result=Object.create(null);for(const k of Object.keys(x).sort())result[k]=ordered(x[k]);return result;}
      if(typeof x==='number'&&!Number.isFinite(x))fail();
      if(x!==null&&!['string','number','boolean'].includes(typeof x))fail();
      return x;
    }
    return JSON.stringify(ordered(v));
  }
  function decimal(v) {
    if(typeof v!=='string'||v.length>24||!/^[-]?(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$/.test(v)||v==='-0')fail('invalid_decimal');
    const negative=v.startsWith('-'),unsigned=negative?v.slice(1):v,parts=unsigned.split('.'),scale=parts[1]?.length??0;
    const integer=BigInt(parts.join(''))*(negative?-1n:1n);
    if((integer<0n?-integer:integer)>1000000n*10n**BigInt(scale))fail('invalid_decimal');
    return {integer,scale};
  }
  function scaled(parts,scale){return parts.integer*10n**BigInt(scale-parts.scale);}
  function controlValue(c,v){
    const values=[c.min,c.max,c.step,v].map(decimal),scale=Math.max(...values.map(p=>p.scale));
    const [low,high,step,current]=values.map(p=>scaled(p,scale));
    if(step<=0n||low>high||current<low||current>high||(current-low)%step!==0n)fail('calculation_domain_error');
    if(c.kind==='integer'&&[low,high,step,current].some(n=>n%10n**BigInt(scale)!==0n))fail('calculation_domain_error');
    if(c.kind==='range'&&((high-low)%step!==0n||(high-low)/step>100n))fail('calculation_domain_error');
    return v;
  }
  function validate(value,citationIds=null){
    exact(value,['schema','title','concept','inputs','calculations','views','actions','calculation_notes','limitations','citations'],['constraints']);
    if(value.schema!==SCHEMA||encoder.encode(canonical(value)).length>24576)fail();
    text(value.title,128);text(value.concept,1024);
    const seen=new Set(),inputs=new Map(),results=new Set();let nodes=0;
    function identity(item,kind){const id=item.id;if(typeof id!=='string'||!new RegExp('^'+prefixes.get(kind)+'[A-Za-z0-9_]{1,24}$').test(id)||seen.has(id))fail();seen.add(id);return id;}
    for(const item of list(value.inputs,8,1)){
      exact(item,['id','kind','label','description','min','max','step','default']);
      if(!['number','range','integer'].includes(item.kind))fail();
      const id=identity(item,'input');text(item.label,80);text(item.description,256,true);controlValue(item,item.default);inputs.set(id,item);
    }
    for(const item of list(value.constraints??[],4)){
      exact(item,['kind','left','right']);if(item.kind!=='le'||!inputs.has(item.left)||!inputs.has(item.right))fail();
      const a=decimal(inputs.get(item.left).default),b=decimal(inputs.get(item.right).default),s=Math.max(a.scale,b.scale);
      if(scaled(a,s)>scaled(b,s))fail('calculation_domain_error');
    }
    function expression(node,depth=1,sample=false){
      if(++nodes>256||depth>16||!plain(node)||typeof node.op!=='string')fail();
      if(node.op==='const'){exact(node,['op','value']);decimal(node.value);}
      else if(node.op==='input'||node.op==='result'){exact(node,['op','id']);if(!(node.op==='input'?inputs.has(node.id):results.has(node.id)))fail();}
      else if(node.op==='sample_x'){exact(node,['op']);if(!sample)fail();}
      else if(ARITY.has(node.op)){exact(node,['op','args']);for(const arg of list(node.args,ARITY.get(node.op),ARITY.get(node.op)))expression(arg,depth+1,sample);}
      else fail();
    }
    for(const item of list(value.calculations,32,1)){exact(item,['id','expression']);const id=identity(item,'result');expression(item.expression);results.add(id);}
    let pictures=0,points=0,readouts=0;
    for(const item of list(value.views,4,1)){
      if(item?.kind==='readout'){
        exact(item,['id','kind','label','calculation','unit']);identity(item,'readout');text(item.unit,24,true);if(!results.has(item.calculation))fail();readouts++;
      }else if(['bar','curve','points_lines'].includes(item?.kind)){
        exact(item,['id','kind','label','source']);identity(item,'view');pictures++;const source=item.source;
        if(item.kind==='bar'){
          if(source?.kind==='values'){
            exact(source,['kind','values']);for(const p of list(source.values,21,1)){exact(p,['label','value']);text(p.label,80);expression(p.value);points++;}
          }else if(source?.kind==='binomial_distribution'){exact(source,['kind','n','p']);expression(source.n);expression(source.p);points+=21;}
          else fail();
        }else if(item.kind==='curve'){
          exact(source,['min','max','samples','expression']);const a=decimal(source.min),b=decimal(source.max),s=Math.max(a.scale,b.scale);
          if(scaled(a,s)>=scaled(b,s)||!Number.isSafeInteger(source.samples)||source.samples<2||source.samples>128)fail();
          points+=source.samples;expression(source.expression,1,true);
        }else{
          exact(source,['points','join']);if(typeof source.join!=='boolean')fail();
          for(const p of list(source.points,128,1)){exact(p,['x','y']);expression(p.x);expression(p.y);points++;}
        }
      }else fail();
      text(item.label,80);
    }
    if(pictures>2||points>128||readouts>8)fail();
    for(const item of list(value.actions,4)){exact(item,['id','kind','label']);identity(item,'action');text(item.label,80);if(item.kind!=='reset')fail();}
    for(const item of list(value.calculation_notes,4,1)){
      exact(item,['formula','domain','error','samples','citations']);text(item.formula,512);text(item.domain,256);text(item.error,128);
      for(const s of list(item.samples,4,2)){exact(s,['input','expected']);text(s.input,256);text(s.expected,128);}
      list(item.citations,4,1);
    }
    for(const item of list(value.limitations,8))text(item,256);
    list(value.citations,8,1);if(new Set(value.citations).size!==value.citations.length)fail();
    for(const id of value.citations){text(id,128);if(citationIds&&!citationIds.includes(id))fail('invalid_citation');}
    if(value.calculation_notes.some(note=>note.citations.some(id=>!value.citations.includes(id))))fail('invalid_citation');
    return JSON.parse(canonical(value));
  }
  function evaluate(description,inputValues){
    validate(description);const inputs=new Map();for(const c of description.inputs){const v=inputValues.get(c.id);controlValue(c,v);inputs.set(c.id,Number(v));}
    for(const r of description.constraints??[]){const a=decimal(inputValues.get(r.left)),b=decimal(inputValues.get(r.right)),s=Math.max(a.scale,b.scale);if(scaled(a,s)>scaled(b,s))fail('calculation_domain_error');}
    const results=new Map(),views=[];let steps=0;
    function tick(){if(++steps>50000)fail('calculation_limit');}
    function finite(n){if(!Number.isFinite(n))fail('calculation_domain_error');return n;}
    function pmf(n,k,p){
      if(!Number.isSafeInteger(n)||n<0||n>20||!Number.isSafeInteger(k)||k<0||k>n||p<0||p>1)fail('calculation_domain_error');
      if(p===0)return k===0?1:0;if(p===1)return k===n?1:0;
      let combination=1;for(let i=1;i<=k;i++){tick();combination=finite(combination*(n-i+1)/i);}
      return finite(combination*Math.pow(p,k)*Math.pow(1-p,n-k));
    }
    function run(node,x=null){
      tick();if(node.op==='const')return Number(node.value);if(node.op==='input')return inputs.get(node.id);if(node.op==='result')return results.get(node.id);
      if(node.op==='sample_x'){if(x===null)fail();return x;}
      const a=node.args.map(v=>run(v,x));let result;
      switch(node.op){
        case 'add':result=a[0]+a[1];break;case 'sub':result=a[0]-a[1];break;case 'mul':result=a[0]*a[1];break;
        case 'div':if(a[1]===0)fail('calculation_domain_error');result=a[0]/a[1];break;
        case 'neg':result=-a[0];break;case 'abs':result=Math.abs(a[0]);break;case 'min':result=Math.min(...a);break;case 'max':result=Math.max(...a);break;
        case 'pow_int':if(!Number.isSafeInteger(a[1])||a[1]<0||a[1]>10)fail('calculation_domain_error');result=a[1]===0?1:Math.pow(a[0],a[1]);break;
        case 'sqrt':if(a[0]<0)fail('calculation_domain_error');result=Math.sqrt(a[0]);break;case 'sin':result=Math.sin(a[0]);break;case 'cos':result=Math.cos(a[0]);break;
        case 'binomial_pmf':result=pmf(...a);break;default:fail();
      }
      return finite(result);
    }
    for(const item of description.calculations)results.set(item.id,run(item.expression));
    for(const item of description.views){
      if(item.kind==='readout')views.push({id:item.id,kind:item.kind,label:item.label,unit:item.unit,value:results.get(item.calculation)});
      else{
        const points=[];const s=item.source;
        if(item.kind==='bar'){
          if(s.kind==='values'){for(const p of s.values)points.push({x:points.length,y:run(p.value),label:p.label});}
          else{const n=run(s.n),p=run(s.p);if(!Number.isSafeInteger(n)||n<0||n>20)fail('calculation_domain_error');for(let k=0;k<=n;k++){tick();points.push({x:k,y:pmf(n,k,p),label:String(k)});}}
        }else if(item.kind==='curve'){
          const min=Number(s.min),max=Number(s.max);for(let i=0;i<s.samples;i++){tick();const x=finite(min+(max-min)*i/(s.samples-1));points.push({x,y:run(s.expression,x),label:''});}
        }else for(const p of s.points){tick();points.push({x:run(p.x),y:run(p.y),label:''});}
        for(const p of points){finite(p.x);finite(p.y);}
        finite(Math.max(1,...points.map(p=>p.x))-Math.min(0,...points.map(p=>p.x)));
        finite(Math.max(1,...points.map(p=>p.y))-Math.min(0,...points.map(p=>p.y)));
        views.push({id:item.id,kind:item.kind,label:item.label,join:s.join??item.kind==='curve',points});
      }
    }
    return {values:Object.fromEntries(results),views,steps};
  }
  let descriptor=null,current=null,inputValues=null,rootElement=null;
  const elementById=new Map(),inputElements=new Map();
  function node(tag,content=''){const item=document.createElement(tag);item.textContent=content;return item;}
  function draw(view){
    const canvas=elementById.get(view.id),ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
    const points=view.points,lowX=Math.min(0,...points.map(p=>p.x)),highX=Math.max(1,...points.map(p=>p.x));
    const lowY=Math.min(0,...points.map(p=>p.y)),highY=Math.max(1,...points.map(p=>p.y));
    const x=v=>24+(v-lowX)/(highX-lowX)*550,y=v=>124-(v-lowY)/(highY-lowY)*102;
    ctx.strokeStyle='#425469';ctx.beginPath();ctx.moveTo(24,12);ctx.lineTo(24,124);ctx.lineTo(586,124);ctx.stroke();
    ctx.fillStyle='#267bba';ctx.strokeStyle='#267bba';ctx.font='11px sans-serif';
    if(view.kind==='bar'){
      const width=520/points.length;points.forEach((p,i)=>{const xx=32+i*width,height=124-y(p.y);ctx.fillRect(xx,y(p.y),Math.max(1,width-8),height);ctx.fillText(p.label.slice(0,24),xx,138);});
    }else{
      if(view.join){ctx.beginPath();points.forEach((p,i)=>i===0?ctx.moveTo(x(p.x),y(p.y)):ctx.lineTo(x(p.x),y(p.y)));ctx.stroke();}
      points.forEach(p=>{ctx.beginPath();ctx.arc(x(p.x),y(p.y),3,0,2*Math.PI);ctx.fill();});
    }
    canvas.setAttribute('aria-label',view.label+'，'+points.map(p=>String(p.y)).join('，').slice(0,512));
  }
  function paint(snapshot){
    for(const view of snapshot.views){
      if(view.kind==='readout')elementById.get(view.id).textContent=String(Number(view.value.toPrecision(12)))+' '+view.unit;
      else draw(view);
    }
    for(const [id,value] of inputValues)inputElements.get(id).value=value;
    elementById.get('render-error').textContent='';
  }
  function start(value){
    if(descriptor!==null)fail('duplicate_init');
    const validated=validate(value),initial=new Map(validated.inputs.map(c=>[c.id,c.default])),snapshot=evaluate(validated,initial);
    // 首快照和全部字段校验完成后才创建真实远端DOM。
    descriptor=validated;inputValues=initial;current=snapshot;rootElement=document.getElementById('render-root');
    rootElement.replaceChildren(node('h1',descriptor.title),node('p',descriptor.concept));
    const controls=node('section');
    for(const c of descriptor.inputs){const label=node('label',c.label),input=node('input');input.id=c.id;input.type=c.kind==='range'?'range':'number';input.min=c.min;input.max=c.max;input.step=c.step;input.value=c.default;label.appendChild(input);controls.appendChild(label);inputElements.set(c.id,input);}
    for(const a of descriptor.actions){const button=node('button',a.label);button.type='button';button.id=a.id;controls.appendChild(button);}
    rootElement.appendChild(controls);
    for(const view of descriptor.views){
      const label=node('p',view.label);rootElement.appendChild(label);const item=node(view.kind==='readout'?'output':'canvas');item.id=view.id;
      if(view.kind!=='readout'){item.width=600;item.height=145;}
      elementById.set(view.id,item);rootElement.appendChild(item);
    }
    const error=node('p');error.id='render-error';error.className='error';elementById.set(error.id,error);rootElement.appendChild(error);paint(current);return state();
  }
  function dispatch(event){
    if(descriptor===null)fail('not_initialized');let next=new Map(inputValues);
    try{
      if(event?.type==='set_number'){exact(event,['type','control_id','value']);const c=descriptor.inputs.find(c=>c.id===event.control_id);if(!c)fail();next.set(c.id,controlValue(c,event.value));}
      else if(event?.type==='activate'){exact(event,['type','action_id']);if(!descriptor.actions.some(a=>a.id===event.action_id))fail();next=new Map(descriptor.inputs.map(c=>[c.id,c.default]));}
      else fail();
      const snapshot=evaluate(descriptor,next);inputValues=next;current=snapshot;paint(snapshot);return {accepted:true,error_code:null,...state()};
    }catch(error){if(!(error instanceof DataError))throw error;elementById.get('render-error').textContent=error.code;return {accepted:false,error_code:error.code,...state()};}
  }
  function state(){return {values:current?.values??{},views:current?.views??[],steps:current?.steps??0,inputs:Object.fromEntries(inputValues??[])};}
  const api=Object.freeze({SCHEMA,ARITY:Object.freeze(Object.fromEntries(ARITY)),DataError,canonical,decimal,controlValue,validate,evaluate,start,dispatch,state});
  if(typeof module==='object'&&module.exports)module.exports=api;
  else Object.defineProperty(root,'RetroLumeRuntime',{value:api,writable:false,configurable:false});
})(globalThis);
