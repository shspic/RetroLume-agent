import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const folder=process.env.RETROLUME_TASK106_BROWSER_OUTPUT;
const seed=JSON.parse(await fs.readFile(process.env.RETROLUME_TASK106_BROWSER_SEED,'utf8'));
const base='http://127.0.0.1:18106';
const profile=path.join(folder,'chrome-profile');
const context=await chromium.launchPersistentContext(profile,{headless:true,viewport:{width:1440,height:1100}});
const page=context.pages()[0]??await context.newPage();
const network=[],consoleErrors=[];let postCount=0;
page.on('request',r=>{if(r.url().includes('/interview/commands')&&r.method()==='POST')postCount++;network.push({kind:'request',at:Date.now(),url:r.url(),method:r.method()});});
page.on('response',r=>network.push({kind:'response',at:Date.now(),url:r.url(),status:r.status()}));
page.on('pageerror',e=>consoleErrors.push(e.message));
const api=async(method,url,body)=>{
  const result=await page.evaluate(async({method,url,body})=>{
    const session=await (await fetch('/api/session',{credentials:'omit'})).json();
    const r=await fetch(url,{method,headers:{'X-RetroLume-Session':session.token,...(body?{'Content-Type':'application/json'}:{})},credentials:'omit',...(body?{body:JSON.stringify(body)}:{})});
    return {status:r.status,data:await r.json()};
  },{method,url,body});
  assert.ok([200,201,202].includes(result.status),JSON.stringify(result));return result.data;
};
const select=async aid=>{
  await page.locator(`[data-activity-id="${aid}"]`).click();
  await page.locator(`[data-interview-activity-id="${aid}"]`).waitFor();
  await page.getByLabel('面试目标',{exact:true}).waitFor();
};
const area=()=>page.locator('[aria-label="文字模拟面试工作区"]');
const button=(name)=>area().getByRole('button',{name,exact:true});

async function finalBoundaries(){
  await page.goto(base);await page.getByRole('button',{name:'模拟面试',exact:true}).click();await select(seed.technical);
  const state=await api('GET',`/api/activities/${seed.technical}/interview/workspace`);assert.equal(state.head.phase,'ended');
  const late=[];
  for(const [kind,rid] of [['question',state.head.current_question_id],['feedback',state.head.current_feedback_id]]){
    for(const afterParse of [false,true]){
      await select(seed.technical);await page.getByText('本场次已结束，只读历史',{exact:true}).waitFor();
      await page.evaluate(({rid,afterParse})=>{
        const original=Response.prototype.json;window.__task106OriginalJSON=original;window.__task106RecordHeld=false;
        Response.prototype.json=async function(){
          const match=this.url.includes(`/interview/records/${rid}`);let data;
          if(afterParse)data=await original.call(this);
          if(match){window.__task106RecordHeld=true;window.__task106HeldRecord={url:this.url,afterParse,hasBody:Boolean(data?.body)};await new Promise(resolve=>window.__task106ReleaseRecord=resolve);}
          return afterParse?data:await original.call(this);
        };
      },{rid,afterParse});
      const posts=postCount;await button('只读刷新／恢复场次').click();await page.waitForFunction(()=>window.__task106RecordHeld);
      const actual=await page.evaluate(()=>window.__task106HeldRecord);if(afterParse)assert.equal(actual.hasBody,true);
      await select(seed.other);await page.evaluate(()=>window.__task106ReleaseRecord());await page.waitForTimeout(100);
      assert.equal(await area().locator('article').count(),0);assert.equal(postCount,posts);
      late.push({kind,rid,afterParse,actual,activity:seed.other,oldProjectionRevived:false,postDelta:0});
      await page.evaluate(()=>{Response.prototype.json=window.__task106OriginalJSON;});
    }
  }
  // A denied real summary lock rejects before POST, after body persisted locally.
  await page.getByLabel('面试目标',{exact:true}).fill('史料活动X迟到与锁验证');
  await page.evaluate(()=>{window.__task106NativeLock=navigator.locks.request.bind(navigator.locks);navigator.locks.request=function(name,...args){if(name==='retrolume.interview.intents.v1')return Promise.reject(new DOMException('TASK106 declared summary lock failure','AbortError'));return window.__task106NativeLock(name,...args);};});
  const lockPosts=postCount;await button('开始场次').click();await area().getByRole('alert').waitFor();assert.equal(postCount,lockPosts);
  await page.evaluate(()=>{navigator.locks.request=window.__task106NativeLock;});
  // Save a genuine unsent summary, then switch before the final POST check.
  await page.evaluate(()=>{window.__task106SummaryComplete=false;window.__task106HoldSummary=true;navigator.locks.request=async function(name,...args){
    const result=await window.__task106NativeLock(name,...args);if(name==='retrolume.interview.intents.v1'&&window.__task106HoldSummary){window.__task106SummaryComplete=true;await new Promise(resolve=>window.__task106SummaryRelease=resolve);}return result;
  };});
  await button('开始场次').click();await page.waitForFunction(()=>window.__task106SummaryComplete);
  await select(seed.technical);await page.evaluate(()=>{window.__task106HoldSummary=false;window.__task106SummaryRelease();navigator.locks.request=window.__task106NativeLock;});
  await page.waitForTimeout(100);assert.equal(postCount,lockPosts);
  // Actual IDB read completion is held; changing activity stops original-key retry.
  await select(seed.other);
  await page.evaluate(()=>{const d=Object.getOwnPropertyDescriptor(IDBTransaction.prototype,'oncomplete');window.__task106ReadDescriptor=d;window.__task106ReadDone=false;
    Object.defineProperty(IDBTransaction.prototype,'oncomplete',{...d,set(fn){d.set.call(this,function(event){if(this.db.name==='retrolume-interview-drafts'&&this.mode==='readonly'){
      window.__task106ReadDone=true;window.__task106ReleaseRead=()=>fn.call(this,event);
    }else fn.call(this,event);});}});
  });
  const readPosts=postCount;await button('在安全条件下显式重交原意图').first().click();await page.waitForFunction(()=>window.__task106ReadDone);
  await select(seed.technical);await page.evaluate(()=>{window.__task106ReleaseRead();Object.defineProperty(IDBTransaction.prototype,'oncomplete',window.__task106ReadDescriptor);});
  await page.waitForTimeout(100);assert.equal(postCount,readPosts);
  // A second document inheriting the live owner id obtains a distinct real Web Lock.
  const firstOwner=await page.evaluate(()=>sessionStorage.getItem('retrolume.teaching-editor-owner.v1'));assert.ok(firstOwner);
  const second=await context.newPage();await second.addInitScript(owner=>sessionStorage.setItem('retrolume.teaching-editor-owner.v1',owner),firstOwner);
  await second.goto(base);await second.getByRole('button',{name:'模拟面试',exact:true}).click();await second.locator(`[data-activity-id="${seed.other}"]`).click();
  await second.getByRole('button',{name:'开始场次',exact:true}).waitFor();
  await second.waitForFunction(expected=>{const id=sessionStorage.getItem('retrolume.teaching-editor-owner.v1');return id&&id!==expected;},firstOwner);
  const secondOwner=await second.evaluate(()=>sessionStorage.getItem('retrolume.teaching-editor-owner.v1'));assert.ok(secondOwner&&secondOwner!==firstOwner);
  await second.screenshot({path:path.join(folder,'distinct-owner-document.png'),fullPage:true});await second.close();
  const blocked=await context.newPage();let blockedPosts=0;blocked.on('request',r=>{if(r.url().includes('/interview/commands')&&r.method()==='POST')blockedPosts++;});
  await blocked.addInitScript(()=>Object.defineProperty(navigator,'locks',{value:undefined,configurable:true}));await blocked.goto(base);await blocked.getByRole('button',{name:'模拟面试',exact:true}).click();await blocked.locator(`[data-activity-id="${seed.other}"]`).click();
  await blocked.getByText('本机编辑身份或锁不可用，保持只读。可以复制自己的草稿。',{exact:true}).waitFor();assert.equal(await blocked.getByRole('button',{name:'开始场次',exact:true}).isDisabled(),true);assert.equal(blockedPosts,0);
  await blocked.screenshot({path:path.join(folder,'owner-lock-unavailable-readonly.png'),fullPage:true});await blocked.close();
  assert.deepEqual(consoleErrors,[]);assert.equal(postCount,0);
  await page.screenshot({path:path.join(folder,'ended-technical-no-late-revival.png'),fullPage:true});
  await fs.writeFile(path.join(folder,'browser-result.json'),JSON.stringify({passed:true,closure:true,technical:seed.technical,other:seed.other,lateRecords:late,summaryLockFailurePostDelta:0,
    savedSummarySwitchPostDelta:0,draftReadSwitchPostDelta:0,firstOwner,secondOwner,ownerCollisionProtected:true,ownerLockFailurePOST:blockedPosts,totalBusinessPOST:postCount,final:state,consoleErrors},null,2));
  await fs.writeFile(path.join(folder,'network.json'),JSON.stringify(network,null,2));
}

try{
  if(seed.closureOnly){await finalBoundaries();}
  else{
  await page.goto(base);await page.getByRole('button',{name:'模拟面试',exact:true}).click();
  await select(seed.technical);
  if(!seed.resumeOnly){
  await page.getByLabel('面试目标',{exact:true}).fill('余额算法串行结果与覆盖风险');
  await page.getByLabel(`${seed.technicalTitle}的面试用途`,{exact:true}).selectOption('reference');
  await button('开始场次').click();await button('开始提问').waitFor();
  await button('开始提问').click();await page.getByLabel('面试回答',{exact:true}).waitFor();
  await page.getByLabel('面试回答',{exact:true}).fill('🧭串行100加20减10为110；两个都先读100时，后写90可能覆盖先写120。这只针对给定算法。');
  await button('保存回答（不调用模型）').click();await button('获取必要追问或反馈').waitFor();
  await button('获取必要追问或反馈').click();await button('继续下一题（显式调用）').waitFor({timeout:60000});
  }
  await button('继续下一题（显式调用）').waitFor();
  await area().getByText('有依据的部分 · 资料对照建议',{exact:true}).waitFor();
  await page.screenshot({path:path.join(folder,'technical-feedback.png'),fullPage:true});
  let state=await api('GET',`/api/activities/${seed.technical}/interview/workspace`);
  assert.equal(state.budget.requests_reserved,2);assert.equal(state.head.phase,'feedback_ready');
  const metadata=await api('GET',`/api/activities/${seed.technical}/interview/history`);
  assert.ok(metadata.records.every(r=>!('payload' in r)&&!('local_body' in r)&&!('text' in r)));
  // Refresh/reopen restores owner and facts but causes no business POST.
  const beforeReload=postCount;await page.reload();await page.getByRole('button',{name:'模拟面试',exact:true}).click();await select(seed.technical);
  await button('继续下一题（显式调用）').waitFor();assert.equal(postCount,beforeReload);
  // Real parsed old citation waits after Response.json, then switches to another panel.
  await page.evaluate(()=>{
    const original=Response.prototype.json;
    window.__task106HoldCitation=true;window.__task106ParsedCitation=false;
    Response.prototype.json=async function(){const data=await original.call(this);if(window.__task106HoldCitation&&this.url.includes('/citations/')){
      window.__task106ParsedCitation=true;window.__task106ParsedBody=data;await new Promise(resolve=>window.__task106ReleaseCitation=resolve);
    }return data;};
  });
  await area().getByRole('button',{name:new RegExp(`查看依据：${seed.technicalTitle}`)}).first().click();
  await page.waitForFunction(()=>window.__task106ParsedCitation===true);
  const parsed=await page.evaluate(()=>({status:window.__task106ParsedBody?.position_verified,source:window.__task106ParsedBody?.citation?.source_id}));
  assert.equal(parsed.status,true);
  await select(seed.other);
  await page.evaluate(()=>{window.__task106HoldCitation=false;window.__task106ReleaseCitation();});
  await page.waitForTimeout(100);
  assert.equal(await page.locator('[aria-label="面试引用"]').count(),0);
  await page.screenshot({path:path.join(folder,'late-parsed-citation-other-panel.png'),fullPage:true});
  // IndexedDB fails before first body save: no POST, real visible error.
  await page.getByLabel('面试目标',{exact:true}).fill('史料活动X策展');
  await page.evaluate(()=>{window.__task106OriginalOpen=IDBFactory.prototype.open;IDBFactory.prototype.open=function(name,...args){if(name==='retrolume-interview-drafts')throw new DOMException('TASK106 declared storage failure','QuotaExceededError');return window.__task106OriginalOpen.call(this,name,...args);};});
  const beforeStorage=postCount;await button('开始场次').click();await area().getByRole('alert').waitFor();assert.equal(postCount,beforeStorage);
  await page.evaluate(()=>{IDBFactory.prototype.open=window.__task106OriginalOpen;});
  // Successful body save completes but caller continuation is held; activity change forbids POST.
  await page.evaluate(()=>{
    const d=Object.getOwnPropertyDescriptor(IDBTransaction.prototype,'oncomplete');window.__task106CompleteDescriptor=d;
    window.__task106HoldSave=true;window.__task106SaveCompleted=false;
    Object.defineProperty(IDBTransaction.prototype,'oncomplete',{...d,set(fn){d.set.call(this,function(e){
      if(window.__task106HoldSave&&this.db.name==='retrolume-interview-drafts'&&this.mode==='readwrite'){
        window.__task106SaveCompleted=true;window.__task106ReleaseSave=()=>fn.call(this,e);
      }else fn.call(this,e);
    });}});
  });
  const beforeSave=postCount;await button('开始场次').click();await page.waitForFunction(()=>window.__task106SaveCompleted===true);
  await select(seed.technical);await page.evaluate(()=>{window.__task106HoldSave=false;window.__task106ReleaseSave();});
  await page.waitForTimeout(100);assert.equal(postCount,beforeSave);
  await page.evaluate(()=>{Object.defineProperty(IDBTransaction.prototype,'oncomplete',window.__task106CompleteDescriptor);});
  // Persist the actual summary, hold its lock completion and switch before POST.
  await select(seed.other);await page.getByLabel('面试目标',{exact:true}).fill('史料活动X策展');
  await page.evaluate(()=>{
    window.__task106OriginalLock=navigator.locks.request.bind(navigator.locks);
    navigator.locks.request=async function(name,...args){
      const value=await window.__task106OriginalLock(name,...args);
      if(window.__task106HoldSummary&&name==='retrolume.interview.intents.v1'){
        window.__task106SummarySaved=true;await new Promise(resolve=>window.__task106ReleaseSummary=resolve);
      }return value;
    };window.__task106HoldSummary=true;window.__task106SummarySaved=false;
  });
  const beforeSummary=postCount;await button('开始场次').click();await page.waitForFunction(()=>window.__task106SummarySaved===true);
  await select(seed.technical);await page.evaluate(()=>{window.__task106HoldSummary=false;window.__task106ReleaseSummary();});
  await page.waitForTimeout(100);assert.equal(postCount,beforeSummary);
  await page.evaluate(()=>{navigator.locks.request=window.__task106OriginalLock;});
  // An unsent original key returns real 404, so draft hash validation is exercised.
  const summary=await page.evaluate(()=>JSON.parse(localStorage.getItem('retrolume.interview.intents.v1')??'[]'));
  assert.ok(summary.length>=1);assert.ok(summary.every(x=>!('text' in x)&&!('body' in x)));
  const selected=summary.find(x=>x.activity_id===seed.other);assert.ok(selected);
  await page.evaluate(async key=>{const db=await new Promise((resolve,reject)=>{const r=indexedDB.open('retrolume-interview-drafts',1);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
    await new Promise((resolve,reject)=>{const tx=db.transaction('drafts','readwrite'),s=tx.objectStore('drafts'),g=s.get(key);g.onsuccess=()=>{const d=g.result;d.hash='0'.repeat(64);s.put(d);};tx.oncomplete=resolve;tx.onerror=reject;});db.close();},selected.key);
  await select(seed.other);const beforeTamper=postCount;await button('在安全条件下显式重交原意图').first().click();
  await area().getByRole('alert').filter({hasText:'原键正文或编辑身份缺失'}).waitFor();assert.equal(postCount,beforeTamper);
  await select(seed.technical);
  // A real response is received but blocked before JSON parsing, then the panel changes.
  await page.evaluate(()=>{window.__task106BeforeJSON=false;window.__task106HoldBeforeJSON=true;
    const original=Response.prototype.json;Response.prototype.json=async function(){
      if(window.__task106HoldBeforeJSON&&this.url.includes('/citations/')){
        window.__task106BeforeJSON=true;await new Promise(resolve=>window.__task106ReleaseBeforeJSON=resolve);
      }return original.call(this);
    };
  });
  await area().getByRole('button',{name:new RegExp(`查看依据：${seed.technicalTitle}`)}).first().click();
  await page.waitForFunction(()=>window.__task106BeforeJSON===true);await select(seed.other);
  await page.evaluate(()=>{window.__task106HoldBeforeJSON=false;window.__task106ReleaseBeforeJSON();});
  await page.waitForTimeout(100);assert.equal(await page.locator('[aria-label="面试引用"]').count(),0);
  await select(seed.technical);
  await button('结束本场次').click();await area().getByText('本场次已结束，只读历史',{exact:true}).waitFor();
  state=await api('GET',`/api/activities/${seed.technical}/interview/workspace`);assert.equal(state.head.phase,'ended');assert.equal(state.budget.requests_reserved,2);
  assert.deepEqual(consoleErrors,[]);
  await fs.writeFile(path.join(folder,'browser-result.json'),JSON.stringify({passed:true,technical:seed.technical,other:seed.other,postCount,
    resumedCommittedChain:seed.resumeOnly,refreshPostDelta:0,storageFailurePostDelta:0,savedThenSwitchedPostDelta:0,summarySavedThenSwitchedPostDelta:0,
    lateParsedCitation:parsed,lateBeforeParsedCitation:true,latePanelRevived:false,summaryHasNoBody:true,unsentHashMismatch:true,tamperPostDelta:0,final:state,consoleErrors},null,2));
  await fs.writeFile(path.join(folder,'network.json'),JSON.stringify(network,null,2));
  console.log(JSON.stringify({browser:true,realHTTP:true,realPG:true,parsedLateCitationRejected:true,successfulSavedDraftSwitchNoPOST:true,storageFailureNoPOST:true,refreshOnlyGET:true}));
  }
}catch(error){
  await fs.writeFile(path.join(folder,'failure-dom.html'),await page.content());
  await page.screenshot({path:path.join(folder,'failure.png'),fullPage:true}).catch(()=>{});
  await fs.writeFile(path.join(folder,'network.json'),JSON.stringify(network,null,2));
  throw error;
}finally{await context.close();}
