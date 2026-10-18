// 续作01：一个真实浏览器，独立场景；正常链使用真实HTTP/PG/Windows，额外UI替身明确标层。
import { chromium } from 'playwright';
import { createHash, randomUUID } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const OUT=process.env.RETROLUME_TASK097_OUT, APP='http://127.0.0.1:18097', KEY='retrolume.pending-intents.v1';
if(process.env.RETROLUME_TASK097_PREFLIGHT==='1'){
  assert.equal(typeof chromium.launch,'function'); console.log('continuation browser module preflight: no Chromium start');process.exit(0);
}
assert.equal(process.env.RETROLUME_TASK097_PERMIT,'continuation-01');
const cold=JSON.parse(process.env.RETROLUME_TASK097_REUSE);
const filter=new Set((process.env.RETROLUME_TASK097_CASES||'').split(',').filter(Boolean));
const report={ok:false,cases:[],requests:[],assets:[],asset_interruptions:[],asset_errors:[],blocked:[],page_errors:[],fresh:null};
const observers=[];let browser,serial=0;
const save=()=>fs.writeFileSync(path.join(OUT,'browser-report.json'),JSON.stringify(report,null,2));
const json=v=>({status:200,contentType:'application/json',body:JSON.stringify(v)});
const sha=v=>createHash('sha256').update(v).digest('hex');
async function context(name){
  const c=await browser.newContext({viewport:{width:1440,height:1080},serviceWorkers:'block'});
  await c.route('**/*',r=>{
    const u=new URL(r.request().url());
    if(u.origin!==APP){report.blocked.push({case:name,url:u.origin+u.pathname,method:r.request().method()});save();return r.abort('blockedbyclient');}
    return r.continue();
  });
  c.on('request',r=>{report.requests.push({case:name,at:Date.now(),method:r.method(),path:new URL(r.url()).pathname});save();});
  c.on('page',p=>{
    let navigation=0;p.on('framenavigated',f=>{if(f===p.mainFrame())navigation++;});
    p.on('pageerror',e=>{report.page_errors.push({case:name,error:String(e)});save();});
    p.on('response',r=>{
      const u=new URL(r.url());if(u.origin!==APP||r.status()!==200||!(u.pathname==='/'||/\.(js|css|mjs)$/.test(u.pathname)))return;
      const startedNavigation=navigation;
      const task=r.body().then(raw=>{
        const rel=u.pathname==='/'?'index.html':u.pathname.slice(1),actual=sha(raw),expected=sha(fs.readFileSync(path.resolve('frontend/dist',rel)));
        assert.equal(actual,expected,`served bytes differ: ${rel}`);report.assets.push({case:name,path:rel,served_sha256:actual,dist_sha256:expected,bytes:raw.length});
      }).catch(e=>{
        const fact={case:name,path:u.pathname,error:String(e),navigation_changed:navigation!==startedNavigation};
        if(/Target page, context or browser has been closed/.test(String(e))||
          (fact.navigation_changed&&/No resource with given identifier found/.test(String(e))))report.asset_interruptions.push(fact);
        else report.asset_errors.push(fact);
      });observers.push(task);
    });
  });return c;
}
async function workspace(p){await p.goto(APP,{waitUntil:'domcontentloaded'});await p.locator('nav div',{hasText:'学习活动'}).click();await p.getByText('读取与取消：可用').waitFor();}
async function reopen(p){await p.reload({waitUntil:'domcontentloaded'});await p.locator('nav div',{hasText:'学习活动'}).click();await p.getByText('读取与取消：可用').waitFor();}
async function select(p,title='TASK097 atomicity.pdf'){await p.locator('.ws .library button.material',{hasText:title}).first().click();await p.getByRole('button',{name:'取消活动',exact:true}).waitFor();}
async function open(p,op){await p.locator('button.ws-op',{hasText:op}).click();await p.locator('.ws-learning-result').waitFor();}
async function shot(p,name){await p.screenshot({path:path.join(OUT,name+'.png'),fullPage:true});}
async function storage(p,items){await p.evaluate(({key,items})=>localStorage.setItem(key,JSON.stringify(items)),{key:KEY,items});}
const intent=(goal,extra={})=>({intent_id:randomUUID(),kind:'learning_first',state:'unconfirmed',created_at:new Date().toISOString(),activity_id:cold.activity,business_key:randomUUID(),goal,...extra});
const postCount=name=>report.requests.filter(r=>r.case===name&&r.method==='POST').length;
async function scenario(name,level,fn,dependency=true){
  if(filter.size&&!filter.has(name))return;
  if(!dependency){report.cases.push({name,level,status:'not_run',reason:'真实首续前提未成立'});save();return;}
  const c=await context(name),p=await c.newPage();p.setDefaultTimeout(12000);p.setDefaultNavigationTimeout(12000);
  const item={name,level,status:'FAIL',started_at:new Date().toISOString()};report.cases.push(item);save();
  try{item.actual=await fn(p,c);item.status='PASS';await shot(p,`${++serial}-${name}`);}
  catch(e){item.error=String(e.stack||e);console.error(name,item.error);try{await shot(p,`${++serial}-${name}-FAIL`);fs.writeFileSync(path.join(OUT,name+'-FAIL.html'),await p.content());}catch{}}
  finally{item.ended_at=new Date().toISOString();await c.close();save();}
}
async function api(p,url){return p.evaluate(async url=>{const token=(await(await fetch('/api/session')).json()).token;const r=await fetch(url,{headers:{'X-RetroLume-Session':token}});if(!r.ok)throw new Error(`read ${r.status}`);return r.json();},url);}

try{
  fs.writeFileSync(path.join(OUT,'browser-actual-start.json'),JSON.stringify({permit:'continuation-01',at:new Date().toISOString(),attempted:true}));
  browser=await chromium.launch({headless:true});
  await scenario('cold_refresh_get_only','real_product',async p=>{
    await workspace(p);await select(p);await open(p,cold.followup);
    await p.getByText('本次续问：atomicity 事务 examples',{exact:false}).waitFor();
    await p.getByRole('button',{name:/查看引用.*atomicity\.pdf.*原文.*物理页/}).first().click();await p.locator('.ws-citation-reader canvas').waitFor();
    await reopen(p);await select(p);await open(p,cold.first);
    await p.getByText('确认目标：Explain atomicity 事务原子性',{exact:false}).waitFor();
    const stored=await api(p,`/api/activities/${cold.activity}/operations/${cold.first}`);
    assert.equal(stored.operation.read_status,'committed_current');assert.equal(postCount('cold_refresh_get_only'),0);
    return {activity:cold.activity,first:cold.first,followup:cold.followup,posts:0,payload_sha256:stored.operation.payload_sha256};
  });
  await scenario('final_first_followup_citations','real_product',async p=>{
    await p.route('**/api/activities/*/learning/*',async r=>{
      if(r.request().method()==='POST'){
        const body=r.request().postDataJSON(),items=await p.evaluate(k=>JSON.parse(localStorage.getItem(k)||'[]'),KEY);
        const saved=items.find(i=>i.business_key===body.business_key);assert.ok(saved&&saved.state==='submitted');
        assert.ok(!JSON.stringify(items).includes('payload')&&!JSON.stringify(items).includes('token'));
        report.intent_before_post=(report.intent_before_post||[]).concat([{body,stored:saved}]);save();
      }return r.continue();
    });
    await workspace(p);await p.getByText('开始学习：可用 · 有限词项').waitFor();
    for(const title of ['TASK097 C01 atomicity.md','TASK097 C01 事务原子性.txt','TASK097 C01 atomicity.pdf'])await p.locator('.ws-pick-row',{hasText:title}).first().locator('input').check();
    const creating=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/activities'&&r.request().method()==='POST');
    await p.getByRole('button',{name:'创建活动',exact:true}).click();const created=await(await creating).json();
    report.fresh={activity:created.activity.activity_id};save();
    assert.equal(created.activity.requests_reserved,0);assert.equal(created.activity.cost_reserved_microunits,0);
    await p.getByLabel('学习目标或具体问题').fill('Explain atomicity 事务原子性');
    await p.getByLabel('我确认目标、所选资料范围、服务用途和上方有限额度；本次将耗用一次请求及一次费用预留').check();
    const firstResponse=p.waitForResponse(r=>r.url().endsWith('/learning/first')&&r.request().method()==='POST');
    await p.getByRole('button',{name:'确认并开始学习'}).click();const first=await(await firstResponse).json();
    report.fresh.first=first.operation_id;save();assert.equal(first.business.read_status,'committed_current');
    await p.locator('.ws-learning-result').waitFor();
    const persisted=(await api(p,`/api/activities/${report.fresh.activity}/operations/${first.operation_id}`)).operation;
    fs.writeFileSync(path.join(OUT,'browser-persistent-first.json'),JSON.stringify(persisted,null,2));
    const injection=p.locator('.ws-answer-segment',{hasText:'<img'}).first();await injection.waitFor();
    assert.equal(await p.locator('.ws-learning-result img').count(),0);assert.equal(await p.evaluate(()=>window.learningXss),undefined);
    const citation=p.waitForResponse(r=>r.url().includes('/citations/'));
    await injection.getByRole('button').click();const text=(await(await citation).json()).citation;
    await p.locator('.ws-citation-reader pre').filter({hasText:'<img'}).waitFor();
    const allowed=persisted.payload.value.catalog.find(e=>e.citation_id===text.citation_id);
    for(const k of ['source_id','version_id','fragment_sha256','start_line','end_line'])assert.equal(text[k],allowed[k]);
    for(const kind of ['原文','用户补充']){
      const reply=p.waitForResponse(r=>r.url().includes('/citations/'));
      await p.getByRole('button',{name:new RegExp(`查看引用.*atomicity\\.pdf.*${kind}.*物理页`)}).first().click();
      const quote=(await(await reply).json()).citation;assert.equal(quote.origin_kind,kind==='原文'?'original':'user_supplement');
      await p.locator('.ws-citation-reader canvas').waitFor();assert.equal(quote.physical_page,kind==='原文'?1:2);
    }
    await p.getByRole('button',{name:'从该学习成果续问…'}).click();await p.getByLabel('续问内容').fill('atomicity 事务 examples');
    const followResponse=p.waitForResponse(r=>r.url().endsWith('/learning/followups')&&r.request().method()==='POST');
    await p.getByRole('button',{name:'发出并等待'}).click();const follow=await(await followResponse).json();
    report.fresh.followup=follow.operation_id;save();assert.equal(follow.business.read_status,'committed_current');
    await p.getByText('本次续问：atomicity 事务 examples',{exact:false}).waitFor();
    assert.equal(report.requests.filter(r=>r.case==='final_first_followup_citations'&&r.method==='POST'&&r.path.includes('/learning/')).length,2);
    const before=postCount('final_first_followup_citations');await reopen(p);await select(p,'TASK097 C01 atomicity.pdf');await open(p,follow.operation_id);
    await p.getByText('本次续问：atomicity 事务 examples',{exact:false}).waitFor();assert.equal(postCount('final_first_followup_citations'),before);
    return {...report.fresh,learning_posts:2,refresh_posts:0,xss_executed:false,text_citation:text};
  });
  await scenario('served_final_bundle','real_product',async p=>{
    await workspace(p);
    const names=fs.readdirSync('frontend/dist/assets'),files=['index.html',...names.filter(x=>/\.(js|css|mjs)$/.test(x)).map(x=>'assets/'+x)];
    const rows=[];for(const rel of files){const r=await p.request.get(APP+'/'+(rel==='index.html'?'':rel));assert.equal(r.status(),200);const raw=await r.body();const expected=sha(fs.readFileSync(path.resolve('frontend/dist',rel)));assert.equal(sha(raw),expected);rows.push({path:rel,sha256:expected,bytes:raw.length});}
    assert.equal(rows.length,4);fs.writeFileSync(path.join(OUT,'served-bundle.json'),JSON.stringify(rows,null,2));return rows;
  });
  await scenario('lost_response_matching_conflict','real_client_with_real_persisted_facts',async p=>{
    await workspace(p);const initial=intent('Explain atomicity 事务原子性');await storage(p,[initial]);await reopen(p);
    // 明确请求同槽位：服务器返回原事实，浏览器收不到回执；真实库和send计数另核。
    let lost=null;
    await p.route('**/learning/first',async r=>{const response=await r.fetch();lost={status:response.status(),body:await response.json()};return r.abort('failed');});
    await p.getByRole('button',{name:'重新提交同一意图'}).click();await p.locator('.error').waitFor();await p.getByText(/首次学习 · 结果未确认/).waitFor();
    assert.equal(lost.status,200);assert.equal(lost.body.operation_id,cold.first);assert.equal(postCount('lost_response_matching_conflict'),1);
    await reopen(p);await p.getByRole('button',{name:'核对（只读）'}).click();await p.getByText(/匹配持久输入/).waitFor();
    assert.equal((await p.evaluate(k=>JSON.parse(localStorage.getItem(k)||'[]'),KEY)).length,0);
    const before=postCount('lost_response_matching_conflict');const other=intent('Different atomicity goal');await storage(p,[other]);await reopen(p);
    await p.getByRole('button',{name:'核对（只读）'}).click();await p.getByText(/发现不同输入/).waitFor();
    const kept=await p.evaluate(k=>JSON.parse(localStorage.getItem(k)||'[]'),KEY);assert.equal(kept.length,1);assert.equal(kept[0].goal,other.goal);assert.equal(kept[0].state,'refused');
    await p.getByRole('button',{name:'放弃',exact:true}).click();assert.equal(postCount('lost_response_matching_conflict'),before);
    return {response_deliberately_lost:lost,matched_removed:true,different_retained:true,explicit_posts:1,automatic_posts:0,abandon_posts:0};
  });
  await scenario('unknown_same_key_retry_abandon','ui_synthetic_response',async p=>{
    let posts=0,seenKey;const unknown=intent('atomicity unknown');
    await p.route('**/learning/intents/*',r=>r.fulfill(json({operation:null})));
    await p.route('**/learning/first',r=>{posts++;seenKey=r.request().postDataJSON().business_key;return r.fulfill(json({status:'supervision_unknown',operation_id:'learn-first-v1.'+'b'.repeat(64),business:{read_status:'unresolved',payload_available:false},supervision:null}));});
    await p.route('**/operations/learn-first-v1.*',r=>r.fulfill(json({operation:{operation_id:'learn-first-v1.'+'b'.repeat(64),kind:'model',state:'admitted',disposition:'unknown',read_status:'unresolved',payload_available:false,payload:null}})));
    await workspace(p);await storage(p,[unknown]);await reopen(p);await p.getByRole('button',{name:'核对（只读）'}).click();await p.getByText(/尚无持久操作记录/).waitFor();assert.equal(posts,0);
    await p.getByRole('button',{name:'重新提交同一意图'}).click();await p.getByText(/学习结果未确认，可能已执行/).first().waitFor();assert.equal(posts,1);assert.equal(seenKey,unknown.business_key);
    await reopen(p);await p.getByRole('button',{name:'核对（只读）'}).waitFor();assert.equal(posts,1);await p.getByRole('button',{name:'放弃',exact:true}).click();assert.equal(posts,1);
    return {explicit_posts:1,automatic_posts:0,business_key:seenKey,abandon_posts:0};
  });
  await scenario('corrupt_and_legacy_intents','real_client_ui_with_synthetic_cancel',async p=>{
    let cancelPosts=0;await p.route('**/api/activities/*/cancel',async r=>{cancelPosts++;const actual=await api(p,`/api/activities/${cold.activity}`);return r.fulfill(json(actual));});
    await workspace(p);await p.evaluate(k=>localStorage.setItem(k,'{{{'),KEY);await reopen(p);await p.getByText(/本机恢复记录不可用或已损坏/).waitFor();
    await select(p);await open(p,cold.followup);assert.equal(await p.getByRole('button',{name:'创建活动',exact:true}).isDisabled(),true);
    assert.equal(await p.getByRole('button',{name:'从该学习成果续问…'}).isDisabled(),true);
    await p.getByRole('button',{name:'取消活动',exact:true}).click();assert.equal(cancelPosts,0);await p.getByRole('button',{name:'确认取消',exact:true}).click();await p.getByText(/已取消：/).waitFor();assert.equal(cancelPosts,1);
    await p.getByRole('button',{name:'清除恢复记录'}).click();
    await storage(p,[{intent_id:randomUUID(),kind:'continue',state:'unconfirmed',created_at:new Date().toISOString(),activity_id:cold.activity,operation_id:'ui-old-continue',parent_operation_id:'old-parent',followup:'old question'}]);
    await reopen(p);await p.getByText(/显式继续 · 结果未确认/).waitFor();const before=postCount('corrupt_and_legacy_intents');await p.getByRole('button',{name:'放弃',exact:true}).click();assert.equal(postCount('corrupt_and_legacy_intents'),before);
    return {new_writes_disabled:true,cancel_explicit_posts:1,legacy_restored:true,abandon_posts:0};
  });
  await scenario('missing_learning_config','ui_synthetic_capability',async p=>{
    await p.route('**/api/activities/capabilities',async r=>{const response=await r.fetch(),v=await response.json();v.learning={...v.learning,available:false,reason:'learning_not_configured'};return r.fulfill(json(v));});
    await workspace(p);await p.getByText(/开始学习：未开放/).waitFor();await p.getByText('新建活动：可用').waitFor();await select(p);await open(p,cold.followup);
    assert.equal(await p.getByRole('button',{name:'从该学习成果续问…'}).isDisabled(),true);await p.getByRole('button',{name:'取消活动',exact:true}).waitFor();assert.equal(postCount('missing_learning_config'),0);
    return {read_cancel:true,create:true,learning:false,posts:0};
  });
  await scenario('bad_invalid_citation_and_network','real_browser_ui_synthetic_409_and_active_guard',async p=>{
    await workspace(p);await select(p);await open(p,cold.first);
    await p.route('**/citations/*',r=>r.fulfill({status:409,contentType:'application/json',body:JSON.stringify({detail:{code:'citation_unavailable',message:'引用版本已替换，旧引用不可用'}})}));
    await p.getByRole('button',{name:/查看引用/}).first().click();await p.getByText('引用版本已替换，旧引用不可用').waitFor();
    await p.evaluate(async()=>{try{await fetch('https://outside.invalid/probe');}catch{}});assert.ok(report.blocked.some(b=>b.case==='bad_invalid_citation_and_network'&&b.url==='https://outside.invalid/probe'));
    return {citation_unavailable:409,active_probe_blocked:true};
  });
  await scenario('slow_learning_contexts','real_browser_controlled_read_delay',async p=>{
    await workspace(p);await select(p);
    let release,seen;const held=new Promise(r=>release=r),arrived=new Promise(r=>seen=r);let delivered;
    try{
      await p.route(`**/operations/${cold.followup}`,async r=>{const actual=await r.fetch();seen();await held;try{await r.fulfill({response:actual});}catch{}});
      await p.locator('button.ws-op',{hasText:cold.followup}).click();await arrived;
      delivered=p.waitForResponse(r=>r.url().endsWith('/operations/'+cold.first));await p.locator('button.ws-op',{hasText:cold.first}).click();await delivered;
      await p.getByText('确认目标：Explain atomicity 事务原子性',{exact:false}).waitFor();release();await p.unroute(`**/operations/${cold.followup}`);
      await api(p,'/api/activities/capabilities');assert.ok(!(await p.locator('.ws-learning-result').innerText()).includes('本次续问：'));
      let releaseQuote,seenQuote;const heldQuote=new Promise(r=>releaseQuote=r),arrivedQuote=new Promise(r=>seenQuote=r);
      try{
        await p.route('**/citations/*',async r=>{const actual=await r.fetch();seenQuote();await heldQuote;try{await r.fulfill({response:actual});}catch{}});
        await p.getByRole('button',{name:/查看引用/}).first().click();await arrivedQuote;
        await p.locator('nav div',{hasText:'我的资料'}).click();releaseQuote();await p.unroute('**/citations/*');await api(p,'/api/activities/capabilities');assert.equal(await p.locator('.ws-citation-reader').count(),0);
      }finally{releaseQuote?.();}
      await p.locator('nav div',{hasText:'学习活动'}).click();await select(p);
      const i=intent('Different atomicity goal');await storage(p,[i]);await reopen(p);await select(p);
      let releaseIntent,seenIntent;const heldIntent=new Promise(r=>releaseIntent=r),arrivedIntent=new Promise(r=>seenIntent=r);
      try{
        await p.route('**/learning/intents/*',async r=>{const actual=await r.fetch();seenIntent();await heldIntent;try{await r.fulfill({response:actual});}catch{}});
        await p.getByRole('button',{name:'核对（只读）'}).click();await arrivedIntent;
        await select(p,'TASK097 C01 atomicity.pdf');releaseIntent();await p.unroute('**/learning/intents/*');
        // 操作按钮重新可点意味着核对finally完成；活动不得被迟到核对选回。
        await p.getByRole('button',{name:'核对（只读）'}).waitFor({state:'visible'});
        await p.waitForFunction(()=>!document.querySelector('.ws-intent-actions button')?.disabled);
        assert.ok((await p.locator('.reader-title').innerText()).includes('TASK097 C01'));assert.equal(await p.locator('.ws-learning-result').count(),0);
      }finally{releaseIntent?.();}
      return {slow_operation_ignored:true,citation_unmount_aborted:true,late_reconcile_activity_preserved:true};
    }finally{release?.();}
  },Boolean(report.fresh?.followup||process.env.RETROLUME_TASK097_FRESH));
  await scenario('poll_no_overlap_hidden_unmount','ui_controlled_clock_visibility_real_http',async p=>{
    await p.clock.install();let reads=0,hold=false,seen,release;
    const arrived=new Promise(r=>seen=r),held=new Promise(r=>release=r);
    await p.route('**/api/activities?*',async r=>{reads++;const response=await r.fetch(),v=await response.json();if(v.items.length)v.items[0].status='running';if(hold){seen();await held;}try{await r.fulfill(json(v));}catch{}});
    try{
      await workspace(p);await p.locator('.ws .library button.material').first().waitFor();const initial=reads;hold=true;
      await p.evaluate(()=>document.dispatchEvent(new Event('visibilitychange')));await arrived;await p.clock.fastForward(12000);assert.equal(reads,initial+1);
      await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));});
      hold=false;const ended=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/activities');release();await ended;
      await p.clock.fastForward(12000);assert.equal(reads,initial+1);
      const visible=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/activities');await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'));});await visible;
      assert.equal(reads,initial+2);await p.locator('nav div',{hasText:'我的资料'}).click();await p.clock.fastForward(12000);assert.equal(reads,initial+2);
      return {held_reads:1,hidden_reads:0,resume_reads:1,unmounted_reads:0};
    }finally{release?.();}
  });
  await Promise.all(observers);assert.equal(report.asset_errors.length,0,JSON.stringify(report.asset_errors));assert.equal(report.page_errors.length,0,JSON.stringify(report.page_errors));
  report.ok=report.cases.every(c=>c.status==='PASS');save();
}catch(e){report.error=String(e.stack||e);console.error(report.error);}
finally{await browser?.close();save();}
console.log(JSON.stringify({ok:report.ok,cases:report.cases.map(c=>[c.name,c.status]),assets:report.assets.length,blocked:report.blocked.length}));
process.exitCode=report.ok?0:1;
