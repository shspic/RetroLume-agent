// 097真实产品主链与隔离UI反例；仅097应用同源HTTP可通行。
import { chromium } from "playwright";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";

const OUT=process.env.RETROLUME_TASK097_OUT;
const APP="http://127.0.0.1:18097";
const KEY="retrolume.pending-intents.v1";
const report={ok:false,checks:[],blocked:[],assets:[],page_errors:[],posts:[],contexts:[]};
const contexts=[],pendingAssets=[];
if(process.env.RETROLUME_TASK097_PREFLIGHT==="1"){
  assert.equal(typeof chromium.launch,"function");assert.equal(pendingAssets.length,0);
  console.log("097 browser module preflight PASS; no browser launched");process.exit(0);
}
let browser;
const save=()=>fs.writeFileSync(path.join(OUT,"browser-report.json"),JSON.stringify(report,null,2));
const check=(name,actual,level="real_product")=>{report.checks.push({name,level,actual});save();};
const html=value=>({status:200,contentType:"application/json",body:JSON.stringify(value)});
async function guardedContext(name){
  const context=await browser.newContext({viewport:{width:1440,height:1080},serviceWorkers:"block"});
  contexts.push(context);report.contexts.push(name);
  await context.route("**/*",async route=>{
    const url=new URL(route.request().url());
    if(url.origin!==APP){report.blocked.push({context:name,url:url.origin+url.pathname,method:route.request().method()});save();return route.abort("blockedbyclient");}
    return route.continue();
  });
  context.on("page",page=>page.on("pageerror",error=>report.page_errors.push({context:name,error:String(error)})));
  context.on("response",response=>{
    const url=new URL(response.url());
    if(url.origin===APP&&(url.pathname==="/"||/\.(js|css|mjs)$/.test(url.pathname))&&response.status()===200){
      pendingAssets.push(response.body().then(body=>{
        const relative=url.pathname==="/"?"index.html":url.pathname.slice(1);
        const served=createHash("sha256").update(body).digest("hex");
        const local=createHash("sha256").update(fs.readFileSync(path.resolve("frontend/dist",relative))).digest("hex");
        assert.equal(served,local);report.assets.push({context:name,path:relative,served_sha256:served,dist_sha256:local});
      }));
    }
  });
  return context;
}
async function workspace(page){
  await page.goto(APP,{waitUntil:"domcontentloaded"});
  await page.locator("nav div",{hasText:"学习活动"}).click();
  await page.getByText("读取与取消：可用").waitFor();
}
async function shot(page,name){await page.screenshot({path:path.join(OUT,name+".png"),fullPage:true});}
async function pick(page,title){await page.locator(".ws-pick-row",{hasText:title}).first().locator("input").check();}
async function selectActivity(page){await page.locator(".ws .library button.material",{hasText:"TASK097 atomicity.pdf"}).first().click();}

try{
  fs.writeFileSync(path.join(OUT,"browser-actual-start.json"),JSON.stringify({at:new Date().toISOString(),attempted:true}));
  browser=await chromium.launch({headless:true});
  const main=await guardedContext("real_main");const page=await main.newPage();
  await page.route("**/api/activities/*/learning/*",async route=>{
    if(route.request().method()==="POST"){
      const body=route.request().postDataJSON();
      const items=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)||"[]"),KEY);
      const stored=items.find(item=>item.business_key===body.business_key);
      assert.ok(stored&&stored.state==="submitted","业务意图必须在POST之前落位");
      assert.ok(!JSON.stringify(items).includes("payload")&&!JSON.stringify(items).includes("session_token"));
      report.posts.push({path:new URL(route.request().url()).pathname,body,stored_before_post:true});save();
    }
    return route.continue();
  });
  await workspace(page);
  await page.getByText("开始学习：可用 · 有限词项").waitFor();
  let activity,first,follow,persisted;
  const reuse=process.env.RETROLUME_TASK097_REUSE?JSON.parse(process.env.RETROLUME_TASK097_REUSE):null;
  if(reuse){
    activity=reuse.activity;first={operation_id:reuse.first};follow={operation_id:reuse.followup};
    persisted=await page.evaluate(async ({activity,operation})=>{
      const token=(await (await fetch("/api/session")).json()).token;
      const response=await fetch(`/api/activities/${activity}/operations/${operation}`,{headers:{"X-RetroLume-Session":token}});
      if(!response.ok)throw new Error("真实持久成果不可用");return (await response.json()).operation;
    },{activity,operation:first.operation_id});
    assert.equal(persisted.read_status,"committed_current");
    await selectActivity(page);await page.locator("button.ws-op",{hasText:follow.operation_id}).click();
    await page.locator(".ws-learning-result").filter({hasText:"本次续问：atomicity 事务 examples"}).waitFor();
    await page.getByRole("button",{name:/查看引用.*atomicity\.pdf.*原文.*物理页/}).first().click();
    await page.locator(".ws-citation-reader canvas").waitFor();
    check("reuse_real_first_followup_no_new_call",{activity,first:first.operation_id,followup:follow.operation_id,learning_posts:0});
  }else{
  await pick(page,"TASK097 atomicity.md");await pick(page,"TASK097 atomicity.pdf");
  const createdResponse=page.waitForResponse(response=>new URL(response.url()).pathname==="/api/activities"&&response.request().method()==="POST");
  await page.getByRole("button",{name:"创建活动",exact:true}).click();
  const created=await (await createdResponse).json();activity=created.activity.activity_id;
  await page.getByLabel("学习目标或具体问题").waitFor();
  assert.equal(created.activity.requests_reserved,0);assert.equal(created.activity.cost_reserved_microunits,0);
  assert.equal(report.posts.length,0);check("select_create_zero_fee",{activity,model_posts:0});
  await page.getByLabel("学习目标或具体问题").fill("Explain atomicity 事务原子性");
  await page.getByLabel("我确认目标、所选资料范围、服务用途和上方有限额度；本次将耗用一次请求及一次费用预留").check();
  const firstResponse=page.waitForResponse(response=>response.url().endsWith("/learning/first")&&response.request().method()==="POST");
  const firstRead=page.waitForResponse(response=>response.url().includes("/operations/learn-first-v1.")&&response.request().method()==="GET");
  await page.getByRole("button",{name:"确认并开始学习"}).click();
  first=await (await firstResponse).json();assert.equal(first.business.read_status,"committed_current");
  persisted=(await (await firstRead).json()).operation;
  fs.writeFileSync(path.join(OUT,"browser-persistent-first.json"),JSON.stringify(persisted,null,2));
  await page.locator(".ws-learning-result").waitFor();
  assert.equal(report.posts.length,1);check("explicit_first_one_post",{operation:first.operation_id,posts:1});
  await shot(page,"browser-first-result");
  const injection=page.locator(".ws-answer-segment",{hasText:"<img"});
  await injection.first().waitFor();
  assert.equal(await page.locator(".ws-learning-result img").count(),0);
  assert.equal(await page.evaluate(()=>window.learningXss),undefined);
  const citationResponse=page.waitForResponse(response=>response.url().includes("/citations/")&&response.request().method()==="GET");
  await injection.first().getByRole("button").click();
  const textCitation=await (await citationResponse).json();
  await page.locator(".ws-citation-reader pre").filter({hasText:"<img"}).waitFor();
  const allowed=persisted.payload.value.catalog.find(e=>e.citation_id===textCitation.citation.citation_id);
  assert.equal(textCitation.citation.version_id,allowed.version_id);
  assert.equal(textCitation.citation.source_id,allowed.source_id);
  assert.equal(textCitation.citation.fragment_sha256,allowed.fragment_sha256);
  check("text_citation_utf8_lines_and_xss",{version:textCitation.citation.version_id,
    start_line:textCitation.citation.start_line,end_line:textCitation.citation.end_line,text:textCitation.citation.text,xss_executed:false});
  await shot(page,"browser-text-citation");
  const pdfButton=page.getByRole("button",{name:/查看引用.*atomicity\.pdf.*原文.*物理页/}).first();
  const pdfResponse=page.waitForResponse(response=>response.url().includes("/citations/"));
  await pdfButton.click();const pdfCitation=await (await pdfResponse).json();
  await page.locator(".ws-citation-reader canvas").waitFor();
  await page.waitForFunction(()=>{
    const canvas=document.querySelector(".ws-citation-reader canvas");if(!canvas||canvas.width<=300)return false;
    const pixels=canvas.getContext("2d").getImageData(0,0,canvas.width,200).data;
    let dark=0;for(let i=0;i<pixels.length;i+=4)if(pixels[i+3]>0&&pixels[i]<128)dark++;
    return dark>20;
  });
  check("pdf_physical_page_original",{page:pdfCitation.citation.physical_page,origin:pdfCitation.citation.origin_kind});
  await shot(page,"browser-pdf-original");
  const supplementResponse=page.waitForResponse(response=>response.url().includes("/citations/"));
  await page.getByRole("button",{name:/查看引用.*用户补充.*物理页/}).first().click();
  const supplement=await (await supplementResponse).json();
  await page.locator(".ws-citation-reader pre").filter({hasText:"用户补充"}).waitFor();
  assert.equal(supplement.citation.origin_kind,"user_supplement");check("pdf_user_supplement_identity",supplement.citation);
  await page.getByRole("button",{name:"从该学习成果续问…"}).click();
  await page.getByLabel("续问内容").fill("atomicity 事务 examples");
  const followResponse=page.waitForResponse(response=>response.url().endsWith("/learning/followups")&&response.request().method()==="POST");
  await page.getByRole("button",{name:"发出并等待"}).click();follow=await (await followResponse).json();
  await page.locator(".ws-learning-result").filter({hasText:"本次续问：atomicity 事务 examples"}).waitFor();
  assert.equal(follow.business.read_status,"committed_current");assert.equal(report.posts.length,2);
  check("explicit_followup_one_post",{operation:follow.operation_id,total_learning_posts:2});
  }
  const count=report.posts.length;
  await page.reload({waitUntil:"domcontentloaded"});await page.locator("nav div",{hasText:"学习活动"}).click();
  await selectActivity(page);
  await page.locator("button.ws-op",{hasText:follow.operation_id}).click();
  await page.locator(".ws-learning-result").filter({hasText:"本次续问：atomicity 事务 examples"}).waitFor();
  assert.equal(report.posts.length,count);assert.equal(await page.evaluate(key=>JSON.parse(localStorage.getItem(key)||"[]").length,KEY),0);
  check("refresh_persistent_restore_get_only",{activity,operation:follow.operation_id,additional_posts:0,local_body_cache:false});
  await shot(page,"browser-refresh-restored");
  // 对已提交首次槽位显式重试后实际丢HTTP响应：核对不得再次调用模型。
  await page.evaluate(({key,activity,goal})=>localStorage.setItem(key,JSON.stringify([{
    intent_id:crypto.randomUUID(),kind:"learning_first",state:"unconfirmed",created_at:new Date().toISOString(),
    activity_id:activity,business_key:crypto.randomUUID(),goal
  }])),{key:KEY,activity,goal:"Explain atomicity 事务原子性"});
  await page.reload({waitUntil:"domcontentloaded"});await page.locator("nav div",{hasText:"学习活动"}).click();
  let releaseLost;let reachedLost;
  const heldLost=new Promise(resolve=>releaseLost=resolve);
  const seenLost=new Promise(resolve=>reachedLost=resolve);
  await page.route("**/learning/first",async route=>{
    const actual=await route.fetch();const value=await actual.json();
    assert.equal(value.business.read_status,"committed_current");reachedLost();await heldLost;
    try{await route.fulfill({response:actual});}catch{}
  });
  await page.getByRole("button",{name:"重新提交同一意图"}).click();await seenLost;
  await page.reload({waitUntil:"domcontentloaded"});releaseLost();await page.unroute("**/learning/first");
  await page.locator("nav div",{hasText:"学习活动"}).click();
  const afterLostPosts=report.posts.length;
  await page.getByRole("button",{name:"核对（只读）"}).click();
  await page.getByText("已只读核对学习动作").first().waitFor();
  assert.equal(report.posts.length,afterLostPosts);
  check("committed_lost_response_reconciliation",{explicit_slot_retry_posts:afterLostPosts-count,additional_reconcile_posts:0});
  // 慢引用在成果切换后释放，迟到回包不得串入新成果。
  let release;let seen;
  const released=new Promise(resolve=>release=resolve);const arriving=new Promise(resolve=>seen=resolve);
  await selectActivity(page);
  await page.locator("button.ws-op",{hasText:follow.operation_id}).click();
  await page.locator(".ws-learning-result").waitFor();
  await page.route("**/citations/*",async route=>{const actual=await route.fetch();seen();await released;try{await route.fulfill({response:actual});}catch{}});
  await page.getByRole("button",{name:/查看引用/}).first().click();await arriving;
  await page.locator("button.ws-op",{hasText:first.operation_id}).click();
  await page.locator(".ws-learning-result").filter({hasText:"确认目标：Explain atomicity"}).waitFor();
  release();await page.unroute("**/citations/*");
  await page.getByRole("button",{name:/查看引用/}).first().click();
  await page.locator(".ws-citation-reader pre").waitFor();
  assert.ok(!(await page.locator(".ws-learning-result").innerText()).includes("本次续问："));
  check("slow_citation_operation_switch_no_stale_content",{parent_selected:first.operation_id});
  // 与真实权限边界分开标注的UI失效提示，只替换本次只读响应。
  await page.route("**/citations/*",route=>route.fulfill({status:409,contentType:"application/json",body:JSON.stringify({detail:{code:"citation_unavailable",message:"引用版本已替换，旧引用不可用"}})}));
  await page.getByRole("button",{name:/查看引用/}).first().click();
  await page.getByText("引用版本已替换，旧引用不可用").waitFor();
  check("invalidated_citation_reason",{status:409},"ui_synthetic_response");await shot(page,"browser-invalidated-citation");
  await page.unroute("**/citations/*");
  await page.evaluate(async()=>{try{await fetch("https://outside.invalid/probe");}catch{}});
  assert.ok(report.blocked.some(item=>item.url==="https://outside.invalid/probe"));
  check("browser_external_request_guard",{explicit_blocked_probe:true});
  // 独立context保留旧G6层级与本地意图纪律，不另启动浏览器。
  const ui=await guardedContext("ui_recovery");const recovery=await ui.newPage();
  let uiPosts=0;let mode="missing";let sourceCaps;
  await recovery.route("**/api/activities/capabilities",async route=>{
    const response=await route.fetch();sourceCaps=await response.json();
    if(mode==="missing")sourceCaps.learning={...sourceCaps.learning,available:false,reason:"learning_not_configured"};
    return route.fulfill(html(sourceCaps));
  });
  await recovery.route("**/api/activities/*/learning/*",async route=>{
    const req=route.request();
    if(req.method()==="POST"){
      uiPosts++;report.posts.push({level:"ui_synthetic_response",path:new URL(req.url()).pathname,body:req.postDataJSON()});
      return route.fulfill(html({status:"supervision_unknown",operation_id:"learn-first-v1."+"b".repeat(64),business:{read_status:"unresolved",payload_available:false},supervision:null}));
    }
    if(req.url().includes("/intents/"))return route.fulfill(html({operation:null}));
    return route.continue();
  });
  await recovery.route(`**/api/activities/*/operations/learn-first-v1.${"b".repeat(64)}`,route=>route.fulfill(html({operation:{
    operation_id:"learn-first-v1."+"b".repeat(64),kind:"model",state:"admitted",disposition:"unknown",
    read_status:"unresolved",payload_available:false,payload:null
  }})));
  await workspace(recovery);await recovery.getByText(/开始学习：未开放/).waitFor();
  await recovery.getByText("新建活动：可用").waitFor();
  await selectActivity(recovery);
  await recovery.getByRole("button",{name:"取消活动",exact:true}).waitFor();
  await recovery.locator("button.ws-op",{hasText:follow.operation_id}).click();
  await recovery.locator(".ws-learning-result").waitFor();
  assert.equal(await recovery.getByRole("button",{name:"从该学习成果续问…"}).isDisabled(),true);
  check("learning_missing_read_create_cancel_retained",{l0:true,l1:true,learning:false},"ui_synthetic_capability");
  mode="normal";
  await recovery.evaluate(key=>localStorage.setItem(key,"{{{"),KEY);
  await recovery.reload({waitUntil:"domcontentloaded"});await recovery.locator("nav div",{hasText:"学习活动"}).click();
  await recovery.getByText(/本机恢复记录不可用或已损坏/).waitFor();
  await selectActivity(recovery);
  await recovery.getByRole("button",{name:"取消活动",exact:true}).waitFor();
  await recovery.locator("button.ws-op",{hasText:follow.operation_id}).click();
  await recovery.locator(".ws-learning-result").waitFor();
  assert.equal(await recovery.getByRole("button",{name:"从该学习成果续问…"}).isDisabled(),true);
  await shot(recovery,"browser-corrupt-intent");
  assert.equal(uiPosts,0);check("corrupt_intent_read_cancel_available_new_writes_closed",{learning_posts:0},"real_client_ui");
  await recovery.getByRole("button",{name:"清除恢复记录"}).click();
  const legacyKey="ui-old-continue";
  await recovery.evaluate(({key,activity,operation})=>localStorage.setItem(key,JSON.stringify([{
    intent_id:crypto.randomUUID(),kind:"continue",state:"unconfirmed",created_at:new Date().toISOString(),activity_id:activity,
    operation_id:operation,parent_operation_id:"old-parent",followup:"old question"
  }])),{key:KEY,activity,operation:legacyKey});
  await recovery.reload({waitUntil:"domcontentloaded"});await recovery.locator("nav div",{hasText:"学习活动"}).click();
  await recovery.getByText(/显式继续 · 结果未确认/).waitFor();
  await recovery.getByRole("button",{name:/放弃/}).click();
  assert.equal(uiPosts,0);check("old_intent_format_and_abandon_zero_post",{posts:0},"real_client_ui");
  const unknownKey=crypto.randomUUID();
  await recovery.evaluate(({key,activity,business})=>localStorage.setItem(key,JSON.stringify([{
    intent_id:crypto.randomUUID(),kind:"learning_first",state:"unconfirmed",created_at:new Date().toISOString(),activity_id:activity,
    business_key:business,goal:"atomicity unknown"
  }])),{key:KEY,activity,business:unknownKey});
  await recovery.reload({waitUntil:"domcontentloaded"});await recovery.locator("nav div",{hasText:"学习活动"}).click();
  await recovery.getByRole("button",{name:"核对（只读）"}).click();await recovery.getByText(/尚无持久操作记录/).waitFor();
  assert.equal(uiPosts,0);
  await recovery.getByRole("button",{name:"重新提交同一意图"}).click();
  await recovery.getByText(/学习结果未确认，可能已执行/).first().waitFor();
  assert.equal(uiPosts,1);assert.equal(report.posts.at(-1).body.business_key,unknownKey);
  await recovery.reload({waitUntil:"domcontentloaded"});await recovery.locator("nav div",{hasText:"学习活动"}).click();
  await recovery.getByRole("button",{name:"核对（只读）"}).waitFor();assert.equal(uiPosts,1);
  await recovery.getByRole("button",{name:/放弃/}).click();assert.equal(uiPosts,1);
  check("unknown_explicit_same_key_retry_and_refresh_abandon",{explicit_posts:1,automatic_posts:0,business_key:unknownKey},"ui_synthetic_response");
  await shot(recovery,"browser-unknown-recovery");
  // 假时钟仅推进UI节拍；HTTP仍到真实097应用。列表running标记是UI夹具。
  const pollContext=await guardedContext("ui_polling");const polling=await pollContext.newPage();
  await polling.clock.install();let pollReads=0;let holdPoll=false;let seenPoll;let releasePoll;
  const pollArrived=new Promise(resolve=>seenPoll=resolve);const pollHeld=new Promise(resolve=>releasePoll=resolve);
  await polling.route("**/api/activities?*",async route=>{
    if(route.request().method()!=="GET")return route.continue();
    pollReads++;const response=await route.fetch();const actual=await response.json();
    if(actual.items.length)actual.items[0].status="running";
    if(holdPoll){seenPoll();await pollHeld;}
    return route.fulfill(html(actual));
  });
  await workspace(polling);await polling.locator("button.material").first().waitFor();
  const initialReads=pollReads;holdPoll=true;
  await polling.evaluate(()=>document.dispatchEvent(new Event("visibilitychange")));await pollArrived;
  await polling.clock.fastForward(12000);assert.equal(pollReads,initialReads+1);
  await polling.evaluate(()=>{Object.defineProperty(document,"hidden",{configurable:true,value:true});document.dispatchEvent(new Event("visibilitychange"));});
  holdPoll=false;const finishedPoll=polling.waitForResponse(response=>new URL(response.url()).pathname==="/api/activities");
  releasePoll();await finishedPoll;
  await polling.clock.fastForward(12000);assert.equal(pollReads,initialReads+1);
  const visibleRead=polling.waitForResponse(response=>new URL(response.url()).pathname==="/api/activities");
  await polling.evaluate(()=>{Object.defineProperty(document,"hidden",{configurable:true,value:false});document.dispatchEvent(new Event("visibilitychange"));});
  await visibleRead;assert.equal(pollReads,initialReads+2);
  await polling.locator("nav div",{hasText:"我的资料"}).click();
  await polling.clock.fastForward(12000);assert.equal(pollReads,initialReads+2);
  check("polling_no_overlap_hidden_pause_resume_unmount",{held_reads:1,visible_reads:1,hidden_and_unmounted_reads:0},"ui_controlled_clock_visibility");
  await Promise.all(pendingAssets);
  assert.equal(report.page_errors.length,0);
  assert.ok(report.assets.some(a=>a.path.endsWith(".js"))&&report.assets.some(a=>a.path.endsWith(".css"))&&report.assets.some(a=>a.path.endsWith(".mjs")));
  report.ok=true;save();
}catch(error){
  report.error=String(error.stack||error);save();console.error(report.error);process.exitCode=1;
  for(let i=0;i<contexts.length;i++)for(const page of contexts[i].pages()){
    try{await shot(page,`browser-failure-context-${i}`);fs.writeFileSync(path.join(OUT,`browser-failure-context-${i}.html`),await page.content());}catch{}
  }
}
finally{for(const context of contexts)await context.close();if(browser)await browser.close();save();}
console.log(JSON.stringify({ok:report.ok,checks:report.checks.length,blocked:report.blocked.length,posts:report.posts.length}));
