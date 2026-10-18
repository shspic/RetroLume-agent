import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import cp from 'node:child_process';
import assert from 'node:assert/strict';

const root='D:/shspic/project_NO3_RetroLume-agent';
const evidence=path.join(root,'DocuN/evidence/TASK-107');
const out=process.env.TASK107_BROWSER_OUTPUT;
const plan=JSON.parse(fs.readFileSync(path.join(evidence,'runtime-plan.json'),'utf8'));
const network=[],loaded=[],controllers=[],cases=[];
let context,page,mode=null;
const writes=new Map();
const write=(name,data)=>fs.writeFileSync(path.join(out,name),JSON.stringify(data,null,2));
const canonical=value=>value===null||typeof value!=='object'?JSON.stringify(value):Array.isArray(value)?`[${value.map(canonical).join(',')}]`:`{${Object.keys(value).sort().map(k=>`${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}`;
const requestText=(aid,command)=>{const {business_key,...rest}=command;return canonical({...rest,activity_id:aid});};
const bridge=input=>JSON.parse(cp.execFileSync(path.join(root,'backend/.venv/Scripts/python.exe'),['-X','utf8','-B','-m','tests.fixtures.task107.bridge'],{cwd:path.join(root,'backend'),env:process.env,input:JSON.stringify(input),encoding:'utf8',windowsHide:true,timeout:15000,maxBuffer:8*1024*1024}));
const counts=()=>bridge({action:'counts'}).counts;
const area=()=>page.locator('[data-interview-activity-id]');
const button=name=>area().getByRole('button',{name,exact:true});
const textbox=name=>area().getByRole('textbox',{name,exact:true});
const wait=async(fn,arg)=>page.waitForFunction(fn,arg,{timeout:15000});
const keyPosts=key=>network.filter(x=>x.kind==='request'&&x.method==='POST'&&x.payload?.business_key===key).length;
const noNativeDelta=(before,after)=>assert.deepEqual([after.SUP_attempt,after.transport_send],[before.SUP_attempt,before.transport_send]);

async function api(method,url,body){
  const response=await page.evaluate(async({method,url,body})=>{
    const session=await(await fetch('/api/session',{credentials:'omit',cache:'no-store'})).json();
    const result=await fetch(url,{method,credentials:'omit',cache:'no-store',headers:{'X-RetroLume-Session':session.token,...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})});
    return {status:result.status,body:await result.json()};
  },{method,url,body});
  assert.ok([200,201,202].includes(response.status),JSON.stringify(response));
  return response.body;
}
const view=aid=>api('GET',`/api/activities/${aid}/interview/workspace`);
const record=async(aid,id)=>{const current=await view(aid);return await api('GET',`/api/activities/${aid}/interview/records/${id}?view_token=${current.view_token}`);};
function command(action,current,body,key=crypto.randomUUID()){
  return {schema:'interview.command.v1',business_key:key,action,expected_head_revision:current.head?.revision??0,expected_goal_version:current.head?.goal_version??0,expected_scope_revision:current.head?.scope_revision??1,body};
}
function goalBody(target){return {goal:{target,focus:null,clarifications:[],material_roles:[{source_id:plan.material.id,role:'reference'}]}};}

async function facts(name,aid){
  const current=await view(aid),pg=bridge({action:'snapshot',activity_id:aid});
  const local=await page.evaluate(()=>new Promise((resolve,reject)=>{
    const open=indexedDB.open('retrolume-interview-drafts',1);
    open.onsuccess=()=>{const db=open.result,tx=db.transaction('drafts','readonly'),get=tx.objectStore('drafts').getAll();let drafts=[];get.onsuccess=()=>drafts=get.result;tx.oncomplete=()=>{db.close();resolve({drafts,intents:JSON.parse(localStorage.getItem('retrolume.interview.intents.v1')||'[]'),owner:sessionStorage.getItem('retrolume.teaching-editor-owner.v1')});};tx.onerror=reject;};open.onerror=reject;
  }));
  write(name+'-values.json',{at:Date.now(),workspace:current,pg,local,counts:counts()});
  fs.writeFileSync(path.join(out,name+'-dom.txt'),await page.locator('body').innerText());
  await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});
  write('checkpoint.json',{cases,network,loaded,controllers});
  return {workspace:current,pg,local};
}

async function select(aid){
  const fresh=await api('GET','/api/activities');
  const refreshed=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/activities'&&r.request().method()==='GET'&&!new URL(r.url()).searchParams.has('cursor'));
  await page.getByRole('button',{name:'刷新',exact:true}).click();
  await refreshed;
  if(fresh.items.some(x=>x.activity_id===aid))await page.locator(`[data-activity-id="${aid}"]`).waitFor();
  for(let n=0;n<12&&!(await page.locator(`[data-activity-id="${aid}"]`).count());n++){
    const more=page.getByRole('button',{name:'加载更多',exact:true});
    assert.equal(await more.count(),1,'合法场次不在分页且无下一页');
    const response=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/activities'&&new URL(r.url()).searchParams.has('cursor'));
    await more.click();await response;
  }
  const chosen=page.locator(`[data-activity-id="${aid}"]`);assert.equal(await chosen.count(),1);
  await chosen.click();await page.locator(`[data-interview-activity-id="${aid}"]`).waitFor();
  await textbox('面试目标').waitFor();
  await wait(()=>!!sessionStorage.getItem('retrolume.teaching-editor-owner.v1')&&!!document.querySelector('.interview-workspace'));
}

async function ready(aid,phase,action){
  const expected={ready:'可开始提问',question_ready:'等待你的回答',answer_ready:'回答已保存，可请求追问或反馈',feedback_ready:'本轮反馈已保存',ended:'本场次已结束，只读历史'}[phase];
  await wait(({aid,expected})=>{const p=document.querySelector('[data-interview-activity-id]');return p?.dataset.interviewActivityId===aid&&[...p.querySelectorAll('[role="status"]')].some(x=>x.textContent===expected);},{aid,expected});
  if(action)await button(action).isEnabled().then(ok=>ok||wait(name=>[...document.querySelectorAll('.interview-workspace button')].some(b=>b.textContent===name&&!b.disabled),action));
  const current=await view(aid);assert.equal(current.head.phase,phase);return current;
}

async function completedAction(name,aid,phase,nextAction){
  const response=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname===`/api/activities/${aid}/interview/commands`);
  await button(name).click();const actual=await response;const receipt=await actual.json();
  assert.equal(actual.status(),200,JSON.stringify(receipt));assert.equal(receipt.status,'committed');
  await ready(aid,phase,nextAction);return receipt;
}

async function create(aid){
  const existing=await page.evaluate(async aid=>{const session=await(await fetch('/api/session')).json();const r=await fetch('/api/activities/'+aid,{headers:{'X-RetroLume-Session':session.token}});return {status:r.status,body:await r.json()};},aid);
  if(existing.status===404){const made=await api('POST','/api/activities',{activity_id:aid,source_ids:[plan.material.id]});assert.equal(made.activity.activity_id,aid);}
  else assert.equal(existing.status,200,'复用本卡已创建场次前只读检查失败');
  await select(aid);
  await textbox('面试目标').fill(plan.target);
  await area().getByRole('combobox',{name:`${plan.material.title}的面试用途`,exact:true}).selectOption('reference');
  await completedAction('开始场次',aid,'ready','开始提问');
}

async function waitFile(file){
  const start=Date.now();while(!fs.existsSync(file)){if(Date.now()-start>12000)throw Error('107真实屏障原件未出现：'+path.basename(file));await new Promise(r=>setTimeout(r,25));}
  return JSON.parse(fs.readFileSync(file,'utf8'));
}

async function localDraft(key){return await page.evaluate(key=>new Promise((resolve,reject)=>{const r=indexedDB.open('retrolume-interview-drafts',1);r.onsuccess=()=>{const db=r.result,tx=db.transaction('drafts','readonly'),q=tx.objectStore('drafts').get(key);let value;q.onsuccess=()=>value=q.result;tx.oncomplete=()=>{db.close();resolve(value);};tx.onerror=reject;};r.onerror=reject;}),key);}
async function localSummary(key){return await page.evaluate(key=>JSON.parse(localStorage.getItem('retrolume.interview.intents.v1')||'[]').find(x=>x.key===key),key);}

async function extraDraft(aid,current,label){
  return await page.evaluate(async({aid,current,label,source})=>{
    const key=crypto.randomUUID(),owner=sessionStorage.getItem('retrolume.teaching-editor-owner.v1');
    const command={schema:'interview.command.v1',business_key:key,action:'goal',expected_head_revision:current.head.revision,expected_goal_version:current.head.goal_version,expected_scope_revision:current.head.scope_revision,body:{goal:{target:label,focus:null,clarifications:[],material_roles:[{source_id:source,role:'reference'}]}}};
    const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?`[${v.map(canonical).join(',')}]`:`{${Object.keys(v).sort().map(k=>`${JSON.stringify(k)}:${canonical(v[k])}`).join(',')}}`;
    const {business_key,...value}=command,text=canonical({...value,activity_id:aid});
    const bytes=await window.__task107NativeDigest('SHA-256',new TextEncoder().encode(text));
    const hash=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
    const draft={key,activity_id:aid,owner,hash,command};
    await new Promise((resolve,reject)=>{const r=indexedDB.open('retrolume-interview-drafts',1);r.onsuccess=()=>{const db=r.result,tx=db.transaction('drafts','readwrite');tx.objectStore('drafts').put(draft);tx.oncomplete=()=>{db.close();resolve();};tx.onerror=reject;};r.onerror=reject;});
    return draft;
  },{aid,current,label,source:plan.material.id});
}

async function gate(kind,match){await page.evaluate(({kind,match})=>window.__task107Arm(kind,match),{kind,match});}
async function held(){await wait(()=>window.__task107Barrier?.held===true);return await page.evaluate(()=>({...window.__task107Barrier,release:undefined}));}
async function release(){await page.evaluate(()=>window.__task107Barrier.release());}
async function refreshGoal(aid,target){
  const current=await view(aid),receipt=await api('POST',`/api/activities/${aid}/interview/commands`,command('goal',current,goalBody(target)));
  assert.equal(receipt.status,'committed');await button('只读刷新／恢复场次').click();
  await wait(({target,version})=>{const box=document.querySelector('textarea[aria-label="面试目标"]');return box?.value===target&&[...document.querySelectorAll('.interview-workspace h4')].some(h=>h.textContent===`目标 v${version}与资料用途`);},{target,version:receipt.goal_version});
  return await view(aid);
}
const intentRow=key=>area().locator(`[data-interview-intent-key="${key}"]`);
async function idleIntent(key){await wait(key=>{const p=document.querySelector(`[data-interview-intent-key="${key}"]`);return !!p&&[...p.querySelectorAll('button')].every(b=>!b.disabled);},key);}

try{
  context=await chromium.launchPersistentContext(path.join(out,'chrome-profile'),{headless:true,viewport:{width:1440,height:1100},serviceWorkers:'block'});
  context.setDefaultTimeout(15000);
  await context.addInitScript(()=>{
    const digest=crypto.subtle.digest.bind(crypto.subtle),lock=navigator.locks.request.bind(navigator.locks);
    window.__task107NativeDigest=digest;
    window.__task107Arm=(kind,match)=>{let release;const waiting=new Promise(r=>release=r);window.__task107Barrier={kind,match,armed:true,held:false,release:()=>release(),waiting};};
    crypto.subtle.digest=async function(algorithm,input){
      const actual=await digest(algorithm,input),g=window.__task107Barrier;
      if(g?.armed&&g.kind==='digest'&&new TextDecoder().decode(input)===g.match){g.armed=false;g.native_completed_at=Date.now();g.actual_hash=[...new Uint8Array(actual)].map(x=>x.toString(16).padStart(2,'0')).join('');g.held=true;await g.waiting;g.released_at=Date.now();}
      return actual;
    };
    navigator.locks.request=async function(name,...args){
      const actual=await lock(name,...args),g=window.__task107Barrier;
      if(g?.armed&&g.kind==='summary'&&name===g.match){g.armed=false;g.native_lock_request_resolved_at=Date.now();g.actual_lock_and_owner_callback_completed=true;g.held=true;await g.waiting;g.released_at=Date.now();}
      return actual;
    };
  });
  const captures=[];
  context.on('response',r=>{const u=new URL(r.url());if(u.pathname.startsWith('/assets/')&&/\.(js|css)$/.test(u.pathname))captures.push(r.body().then(data=>{const sha=crypto.createHash('sha256').update(data).digest('hex');loaded.push({path:u.pathname,sha256:sha,bytes:data.length});fs.writeFileSync(path.join(out,path.basename(u.pathname)),data);}));});
  context.on('request',r=>{const u=new URL(r.url());if(!u.pathname.startsWith('/api/'))return;let payload;if(r.method()==='POST')payload=r.postDataJSON();network.push({kind:'request',at:Date.now(),path:u.pathname,query:u.search,method:r.method(),...(payload?{payload}: {})});});
  context.on('response',r=>{const u=new URL(r.url());if(u.pathname.startsWith('/api/'))network.push({kind:'response',at:Date.now(),path:u.pathname,method:r.request().method(),status:r.status()});});
  context.on('requestfailed',r=>network.push({kind:'requestfailed',at:Date.now(),path:new URL(r.url()).pathname,error:r.failure()?.errorText}));
  await context.route('**/*',async route=>{
    const request=route.request(),u=new URL(request.url());
    if(u.protocol!=='http:'||u.hostname!=='127.0.0.1'||u.port!=='18106'){await route.abort('blockedbyclient');return;}
    if(request.method()!=='POST'||!u.pathname.endsWith('/interview/commands')){await route.continue();return;}
    const payload=request.postDataJSON(),hold=mode;
    assert.ok(['start','goal','ask','answer','correct_answer','review','finish'].includes(payload.action),'107未授权动作');
    if(!hold||hold.aid!==u.pathname.split('/')[3]||(hold.key&&hold.key!==payload.business_key)){await route.continue();return;}
    mode=null;hold.request_at=Date.now();hold.payload=payload;
    if(hold.kind==='ghost-goal'){
      hold.server_request_intentionally_not_sent=true;await route.abort('failed');hold.aborted_at=Date.now();controllers.push(hold);hold.done();return;
    }
    try{
      const response=await route.fetch();hold.server_response_at=Date.now();hold.actual_status=response.status();
      if(hold.kind==='drop-committed'){
        hold.actual_receipt=await response.json();assert.equal(response.status(),200);assert.equal(hold.actual_receipt.status,'committed');assert.equal(hold.actual_receipt.effect_applied,true);
        hold.actual_PG_before_browser_drop=bridge({action:'snapshot',activity_id:hold.aid});
      }
      await route.abort('failed');hold.aborted_at=Date.now();
    }catch(error){hold.controller_error=String(error);try{await route.abort('failed');}catch{}}
    controllers.push({...hold,done:undefined});hold.done();
  });
  page=context.pages()[0]??await context.newPage();await page.goto('http://127.0.0.1:18106');await page.getByRole('button',{name:'模拟面试',exact:true}).click();

  // B1：旧seed只读期限不改，本卡必要新场次走真实API与最终UI。
  const a=plan.B1;await create(a);
  await completedAction('开始提问',a,'question_ready','保存回答（不调用模型）');
  let current=await view(a);const firstQuestion=current.head.current_question_id;
  await textbox('面试回答').fill(plan.answer_v1);await completedAction('保存回答（不调用模型）',a,'answer_ready','获取必要追问或反馈');
  current=await view(a);const firstAnswer=current.head.current_answer_id;
  await completedAction('获取必要追问或反馈',a,'feedback_ready','继续下一题（显式调用）');
  current=await view(a);const firstFeedback=current.head.current_feedback_id;
  await completedAction('继续下一题（显式调用）',a,'question_ready','保存回答（不调用模型）');
  current=await view(a);const successor=current.head.current_question_id;await facts('B1-before-history-revision',a);
  await area().locator(`[data-interview-record-id="${firstAnswer}"]`).getByRole('button',{name:'只读查看该版本',exact:true}).click();
  await textbox('历史回答修订正文').waitFor();await textbox('历史回答修订正文').fill(plan.answer_v2);
  const corrected=await completedAction('另存历史回答修订',a,'answer_ready','获取必要追问或反馈');
  current=await view(a);assert.equal(current.head.current_question_id,firstQuestion);const secondAnswer=current.head.current_answer_id;
  const oldAnswer=await record(a,firstAnswer),oldFeedback=await record(a,firstFeedback),oldSuccessor=await record(a,successor),newAnswer=await record(a,secondAnswer);
  assert.equal(oldAnswer.body.value.text,plan.answer_v1);assert.equal(oldAnswer.record.can_correct_answer,false);assert.equal(oldFeedback.body,null);assert.equal(oldSuccessor.body,null);assert.equal(newAnswer.record.answer_version,2);assert.equal(newAnswer.body.value.text,plan.answer_v2);
  await area().locator(`[data-interview-record-id="${firstAnswer}"]`).getByRole('button',{name:'只读查看该版本',exact:true}).click();
  await wait(id=>{const p=document.querySelector('.interview-history article[aria-label="面试回答"]');return !!p&&p.textContent.includes('回答v1');},firstAnswer);
  assert.equal(await button('另存历史回答修订').isDisabled(),true);await facts('B1-old-v1-readonly-successors-suppressed',a);
  await completedAction('获取必要追问或反馈',a,'feedback_ready','继续下一题（显式调用）');
  current=await view(a);const finalFeedback=await record(a,current.head.current_feedback_id);
  assert.ok(finalFeedback.body.value.recognitions.every(r=>r.answer_record_id===secondAnswer));assert.ok((await area().innerText()).includes(plan.answer_v2));
  await facts('B1-new-v2-native-feedback',a);cases.push({method:'B1',status:'PASS',activity:a,firstQuestion,firstAnswer,firstFeedback,successor,secondAnswer,corrected,finalFeedback});

  // B2：真实产品accept已经提交后延迟其回执并取消调用者，制造未claim原意图。
  const b=plan.B2;await create(b);
  fs.writeFileSync(path.join(evidence,'runtime-mode.json'),JSON.stringify({mode:'hold-accepted-receipt',activity_id:b}));
  let resolveAccept;const acceptDone=new Promise(r=>resolveAccept=r);const acceptHold={kind:'accept-before-claim',aid:b,done:resolveAccept};mode=acceptHold;
  const nativeBefore=counts();await button('开始提问').click();
  const acceptance=await waitFile(path.join(evidence,'acceptance-observed.json'));
  assert.equal(acceptance.receipt.launch_claimed,false);const key=acceptance.key;
  const actualAccepted=await api('GET',`/api/activities/${b}/interview/commands/${key}`);assert.equal(actualAccepted.status,'accepted');assert.equal(actualAccepted.launch_claimed,false);noNativeDelta(nativeBefore,counts());
  fs.writeFileSync(path.join(evidence,'cancel-accepted-caller.json'),JSON.stringify({at:Date.now(),key}));await acceptDone;
  fs.writeFileSync(path.join(evidence,'runtime-mode.json'),JSON.stringify({mode:'normal'}));
  await wait(name=>[...document.querySelectorAll('.interview-workspace button')].some(b=>b.textContent===name&&!b.disabled),'开始提问');
  await button('只读刷新／恢复场次').click();await intentRow(key).waitFor();await idleIntent(key);await facts('B2-real-accepted-unclaimed-original',b);
  let resolveDrop;const dropDone=new Promise(r=>resolveDrop=r);const drop={kind:'drop-committed',aid:b,key,done:resolveDrop};mode=drop;
  await intentRow(key).getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).click();await dropDone;assert.ok(drop.actual_receipt);await idleIntent(key);
  const afterCommit=counts();assert.equal(afterCommit.SUP_attempt-nativeBefore.SUP_attempt,1);assert.equal(afterCommit.transport_send-nativeBefore.transport_send,1);
  await button('只读刷新／恢复场次').click();await ready(b,'question_ready','保存回答（不调用模型）');await idleIntent(key);
  const beforeGet=counts(),postBaseline=keyPosts(key);
  await intentRow(key).getByRole('button',{name:'只读核对原提交',exact:true}).click();await idleIntent(key);
  const receipt=await api('GET',`/api/activities/${b}/interview/commands/${key}`);assert.equal(receipt.status,'committed');assert.equal(receipt.business_key,key);assert.equal((await localSummary(key)).state,'committed');assert.equal(keyPosts(key),postBaseline);noNativeDelta(beforeGet,counts());
  await facts('B2-COMMIT-drop-and-original-GET-confirmed',b);cases.push({method:'B2',status:'PASS',activity:b,key,actualAccepted,receipt,postCount:keyPosts(key),nativeBefore,afterCommit,controller:{...drop,done:undefined}});

  // B3-1：真实owner核对和摘要锁完成/释放后，再挂起其完成通知。
  const firstDraft=await localDraft(key),firstSummary=await localSummary(key);const firstPosts=keyPosts(key),beforeB3=counts();
  await gate('summary','retrolume.interview.intents.v1');await intentRow(key).getByRole('button',{name:'只读核对原提交',exact:true}).click();const firstGate=await held();
  assert.equal(firstGate.actual_lock_and_owner_callback_completed,true);
  const changed1=await refreshGoal(b,'TASK107 B3真实摘要完成后显式新目标');
  const kept1=await extraDraft(b,changed1,'TASK107 B3-1保留的新合成本机草稿');await facts('B3-summary-completed-new-view-held',b);
  await release();await idleIntent(key);assert.equal(keyPosts(key),firstPosts);noNativeDelta(beforeB3,counts());assert.deepEqual(await localDraft(key),firstDraft);assert.deepEqual(await localDraft(kept1.key),kept1);assert.deepEqual(await localSummary(key),firstSummary);
  assert.equal((await area().getByRole('status').allTextContents()).some(t=>t.startsWith('原提交状态：')),false);await facts('B3-summary-after-release',b);cases.push({method:'B3-summary',status:'PASS',activity:b,key,gate:firstGate,newView:changed1.view_token,keptDraft:kept1.key,oldPOSTdelta:0});

  // 用真实UI先存正文/摘要，截断本次合成goal发送；真实原键GET404触发显式恢复路径。
  let resolveGhost;const ghostDone=new Promise(r=>resolveGhost=r);const ghost={kind:'ghost-goal',aid:b,done:resolveGhost};mode=ghost;
  await textbox('面试目标').fill('TASK107 B3待核对原目标意图');await button('保存修正目标（另存版本）').click();await ghostDone;
  const ghostKey=ghost.payload.business_key;await idleIntent(ghostKey);const ghostDraft=await localDraft(ghostKey),ghostSummary=await localSummary(ghostKey);assert.ok(ghostDraft&&ghostSummary);const oldText=requestText(b,ghostDraft.command);
  const beforeDigest=counts(),beforeDigestPosts=keyPosts(ghostKey);await gate('digest',oldText);
  await intentRow(ghostKey).getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).click();const digestGate=await held();assert.equal(digestGate.actual_hash,ghostDraft.hash);
  const changed2=await refreshGoal(b,'TASK107 B3真实digest完成后显式新目标');const kept2=await extraDraft(b,changed2,'TASK107 B3-2保留的新合成本机草稿');await facts('B3-digest-completed-new-view-held',b);
  await release();await idleIntent(ghostKey);assert.equal(keyPosts(ghostKey),beforeDigestPosts);noNativeDelta(beforeDigest,counts());assert.deepEqual(await localDraft(ghostKey),ghostDraft);assert.deepEqual(await localSummary(ghostKey),ghostSummary);assert.deepEqual(await localDraft(kept2.key),kept2);await facts('B3-digest-after-release',b);cases.push({method:'B3-digest',status:'PASS',activity:b,key:ghostKey,gate:digestGate,newView:changed2.view_token,oldPOSTdelta:0});

  // B3-3直接代表：真实摘要hash被本卡模拟另一编辑者改变，原回调不得重交。
  await gate('digest',oldText);await intentRow(ghostKey).getByRole('button',{name:'在安全条件下显式重交原意图',exact:true}).click();const identityGate=await held();
  const externallyChanged=await page.evaluate(async key=>{const rows=JSON.parse(localStorage.getItem('retrolume.interview.intents.v1'));const item=rows.find(x=>x.key===key);const result=await window.__task107NativeDigest('SHA-256',new TextEncoder().encode('TASK107明确合成的另一hash身份'));item.hash=[...new Uint8Array(result)].map(x=>x.toString(16).padStart(2,'0')).join('');localStorage.setItem('retrolume.interview.intents.v1',JSON.stringify(rows));return item;},ghostKey);
  const kept3=await extraDraft(b,await view(b),'TASK107 B3-3保留的新合成本机草稿');const beforeIdentity=counts(),identityPosts=keyPosts(ghostKey);await facts('B3-intent-hash-changed-held',b);
  await release();await idleIntent(ghostKey);assert.equal(keyPosts(ghostKey),identityPosts);noNativeDelta(beforeIdentity,counts());assert.deepEqual(await localSummary(ghostKey),externallyChanged);assert.deepEqual(await localDraft(ghostKey),ghostDraft);assert.deepEqual(await localDraft(kept3.key),kept3);await facts('B3-intent-hash-after-release',b);cases.push({method:'B3-identity',status:'PASS',activity:b,key:ghostKey,gate:identityGate,controlledChangedHash:externallyChanged.hash,oldPOSTdelta:0});

  await Promise.all(captures);write('result.json',{status:'PASS',cases,network,loaded,controllers,counts:counts(),fixtureLayers:{rawTransportOnly:true,acceptedReceiptDelayAndActualCallerCancel:true,realWebLocksAndDigestCompletionDelay:true,ghostGoalSendFault:true,syntheticLocalDraftAndHashMutation:true,noReactStateOrServerQualificationMock:true}});
}catch(error){
  if(page)try{fs.writeFileSync(path.join(out,'failure-dom.txt'),await page.locator('body').innerText());await page.screenshot({path:path.join(out,'failure.png'),fullPage:true});}catch{}
  write('result.json',{status:'FAIL',error:String(error.stack||error),cases,network,loaded,controllers});process.exitCode=1;
}finally{
  if(context)await context.close();
}
