// 正式bundle真实页面；仅请求计数/观察，无响应替换、无Vite。
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const evidence=process.env.RETROLUME_TASK117_EVIDENCE;
if(!evidence)throw new Error('evidence_missing');
const control=process.env.RETROLUME_TASK117_CONTROL??evidence;
const root=path.resolve(control,'../../../..');
const attempt=process.env.RETROLUME_TASK117_BROWSER_ATTEMPT??'1';
const requestedPhase=process.env.RETROLUME_TASK117_BROWSER_PHASE??'complete';
const phase=requestedPhase.replace(/^s03-/,'');
const resumeProof=process.env.RETROLUME_TASK117_RESUME_PROOF;
const resume=['resume','continue-root09','interview-only','recover-before'].includes(phase)&&resumeProof?JSON.parse(fs.readFileSync(resumeProof,'utf8')):null;
const dir=path.join(evidence,`browser-${attempt}`);
const intent=JSON.parse(fs.readFileSync(path.join(evidence,'normal-intent.json'),'utf8'));
let fault=null;let delayGoal=true;fs.mkdirSync(dir,{recursive:false});
const browser=await chromium.launch({headless:true});
process.stdin.on('data',()=>{void browser.close();});process.stdin.on('end',()=>{void browser.close();});process.stdin.resume();
const context=await browser.newContext({viewport:{width:1440,height:1000},...(resumeProof?{storageState:path.join(path.dirname(resumeProof),'storage.json')}:{})});
if(resumeProof&&fs.existsSync(path.join(path.dirname(resumeProof),'session-storage.json'))){
  const previous=JSON.parse(fs.readFileSync(path.join(path.dirname(resumeProof),'session-storage.json'),'utf8'));
  await context.addInitScript(saved=>{if(location.origin==='http://127.0.0.1:18118')for(const [key,value] of Object.entries(saved))sessionStorage.setItem(key,value);},previous);
}
const page=await context.newPage();
const indexBatches=new Map();
const proof={attempt,origin:'http://127.0.0.1:18118',official_bundle:true,vite:false,errors:[],receipts:[],requests:0,screenshots:[],semantic_quality:'NOT_RUN_SYNTHETIC_TRANSPORT'};
if(resumeProof){const previous=JSON.parse(fs.readFileSync(resumeProof,'utf8'));proof.dropped=(previous.dropped??[]).map(row=>({...row,inherited_from:resumeProof}));}
proof.phase=phase;proof.assets=[];
const observations=new Set();let closing=false;
function observe(kind,work){const pending=Promise.resolve().then(work).catch(error=>{proof.observation_errors??=[];proof.observation_errors.push({kind,closing,error:String(error)});if(!closing)proof.errors.push('observation:'+kind+':'+String(error));save();}).finally(()=>observations.delete(pending));observations.add(pending);}
const priorPath=path.join(control,'browser-2','proof.json');
const prior=null;
proof.scenario='S04定向场景；复用本轮已合法持久的同一活动，旧S03表现仅按原证据继承';
if(prior?.teaching_activity_id){proof.teaching_activity_id=prior.teaching_activity_id;proof.inherited_receipts=prior.receipts;proof.inherited_from='browser-2/proof.json';}
function count(name,n=1){if(!n)return;const script="import sys;sys.path.insert(0,sys.argv[1]);from control import count;count(sys.argv[2],int(sys.argv[3]))";const r=spawnSync('python',['-X','utf8','-c',script,control,name,String(n)],{cwd:root,encoding:'utf8'});if(r.status)throw new Error('counter_failed:'+name+':'+r.stderr);}
function save(){fs.writeFileSync(path.join(dir,'proof.json'),JSON.stringify(proof,null,2));}
page.on('pageerror',e=>{proof.errors.push(e.message);save();});
page.on('response',r=>{if(new URL(r.url()).pathname.startsWith('/assets/'))observe('asset',async()=>{const body=await r.body();proof.assets.push({url:r.url(),sha256:createHash('sha256').update(body).digest('hex')});save();});});
page.on('response',r=>{const m=new URL(r.url()).pathname.match(/^\/api\/activities\/([^/]+)\/retrieval\/status$/);if(m&&r.ok())observe('retrieval-status',async()=>{const v=await r.json();indexBatches.set(m[1],v.index_batches??0);});});
page.on('response',r=>{if(r.request().method()==='POST'&&new URL(r.url()).pathname.endsWith('/retrieval/commands'))observe('retrieval-receipt',async()=>{proof.retrieval_receipts??=[];proof.retrieval_receipts.push({request:r.request().postDataJSON(),http:r.status(),response:await r.json()});save();});});
await page.route('**/*',async route=>{
  const r=route.request(),u=new URL(r.url());
  if(!['http:','https:'].includes(u.protocol))return route.continue();
  if(u.origin!=='http://127.0.0.1:18118')throw new Error('unexpected_external_request');
  if(u.pathname.startsWith('/api/')){
    count('http');proof.requests++;
    if(r.method()==='POST'){
      let body;try{body=r.postDataJSON();}catch{}
      if(/\/retrieval\/commands$/.test(u.pathname)&&body?.action==='query')count('native_windows');
      if(/\/retrieval\/commands$/.test(u.pathname)&&body?.action==='source_index')count('native_windows',indexBatches.get(u.pathname.split('/')[3])??8);
      if(/\/teaching\/commands$/.test(u.pathname)&&['plan','exercise','evaluate','calculate'].includes(body?.action))count('native_windows');
      if(/\/interview\/commands$/.test(u.pathname)&&['ask','review'].includes(body?.action))count('native_windows');
      if(/\/html\/commands$/.test(u.pathname))count('native_windows');
    }
  }
  if(r.method()==='GET'&&delayGoal&&u.pathname===`/api/activities/${intent.interview_activity_id}/interview/records/${intent.interview_goal_record_id}`){
    proof.goal_delay_started=true;save();await new Promise(resolve=>setTimeout(resolve,1800));delayGoal=false;return route.continue();
  }
  if(r.method()==='POST'&&fault){let b;try{b=r.postDataJSON();}catch{};const yes=(fault==='answer'&&u.pathname.endsWith('/teaching/commands')&&b?.action==='answer')||(fault==='query'&&u.pathname.endsWith('/retrieval/commands')&&b?.action==='query')||(fault==='feedback'&&u.pathname.endsWith('/teaching/commands')&&b?.action==='evaluate');
    if(yes){const kind=fault;fault=null;const actual=await route.fetch();const result=await actual.json();if(!actual.ok())throw new Error('fault_requires_real_success:'+JSON.stringify(result));proof.dropped??=[];proof.dropped.push({kind,path:u.pathname,request:b,HTTP:actual.status(),actual_result:result});save();return route.abort('failed');}
  }
  return route.continue();
});
let snapshotNumber=0;
async function snapshot(label){const name=`${++snapshotNumber}-${label}`;fs.writeFileSync(path.join(dir,name+'.yml'),await page.locator('body').ariaSnapshot());await page.screenshot({path:path.join(dir,name+'.png'),fullPage:true});proof.screenshots.push(name);save();}
async function command(scope,action,button){
  await snapshot(scope+'-'+action+'-before');
  let responseError;
  const response=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith(`/${scope}/commands`)&&r.request().postDataJSON()?.action===action,{timeout:100000}).catch(e=>{responseError=e;return null;});
  await button.click();const r=await response;if(!r)throw responseError??new Error('原回执未确认');const value=await r.json();proof.receipts.push({scope,action,http:r.status(),value});save();
  if(!r.ok()||value.status!=='committed')throw new Error(scope+'_'+action+'_not_committed:'+JSON.stringify(value));
  await page.waitForTimeout(350);return value;
}

async function waitUntil(predicate,label){const end=Date.now()+100000;while(!predicate()){if(Date.now()>end)throw new Error(label);await page.waitForTimeout(100);}}
async function openActivity(domain,aid){await page.getByRole('navigation').getByRole('button',{name:domain==='teaching'?/学习活动/:/模拟面试/}).click();await page.locator(`[data-activity-id="${aid}"]`).click();const work=page.locator(domain==='teaching'?'section.ws-teaching':'.interview-workspace');await work.waitFor();return work;}
try{
  await page.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});await snapshot('final-bundle-materials');
  let work=await openActivity('teaching',intent.teaching_activity_id);
  if(!proof.dropped?.some(row=>row.kind==='answer')){
  await work.locator('#teaching-answer').fill('1米每秒；2分钟为120秒，120米除以120秒。');
  fault='answer';await work.getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}).click();
  await waitUntil(()=>proof.dropped?.some(x=>x.kind==='answer'),'answer_commit_not_observed');await snapshot('answer-committed-body-lost');
  const answerKey=proof.dropped.find(x=>x.kind==='answer').request.business_key;
  await work.getByRole('button',{name:'核对（只读）',exact:true}).click();
  await work.getByText('已只读核对：匹配同一持久命令（未产生第二次动作）。').waitFor();
  await snapshot('answer-recovered-original-key');
  }else{await snapshot('inherited-committed-answer-original-key-GET-confirmed');}
  if(await work.getByRole('button',{name:'载入当前作答（保留旧草稿）',exact:true}).count())await work.getByRole('button',{name:'载入当前作答（保留旧草稿）',exact:true}).click();
  const answerKey=proof.dropped.find(x=>x.kind==='answer').request.business_key;
  fault='query';await work.getByRole('button',{name:'请求评价（1 次模型）',exact:true}).click();
  await waitUntil(()=>proof.dropped?.some(x=>x.kind==='query'),'query_commit_not_observed');await snapshot('query-received-body-lost');
  const panel=work.getByRole('region',{name:'资料检索与恢复'});
  await panel.getByRole('button',{name:'按原键只读核对',exact:true}).last().click();
  const continued=panel.getByRole('button',{name:'明确继续尚未发送的原动作',exact:true});await continued.waitFor();
  fault='feedback';await continued.click();await waitUntil(()=>proof.dropped?.some(x=>x.kind==='feedback'),'feedback_commit_not_observed');
  await snapshot('feedback-committed-body-lost');
  await work.getByRole('button',{name:'核对（只读）',exact:true}).click();
  await work.getByText('已只读核对：匹配同一持久命令（未产生第二次动作）。').waitFor();await snapshot('feedback-recovered-original-key');
  proof.X08={answer_key:answerKey,classes:['query','answer','feedback'],actual_server_success_then_body_discarded:true,response_fabricated:false,model_replayed:false};save();
  work=await openActivity('interview',intent.interview_activity_id);
  await waitUntil(()=>proof.goal_delay_started,'goal_read_not_started');
  const ask=work.getByRole('button',{name:'开始提问',exact:true});await ask.waitFor();
  proof.goal_gate_disabled_before_persisted_goal=!(await ask.isEnabled());if(!proof.goal_gate_disabled_before_persisted_goal)throw new Error('goal_gate_open_before_goal');
  await waitUntil(()=>!delayGoal,'goal_response_not_released');
  const until=Date.now()+15000;while(!await ask.isEnabled()){if(Date.now()>until)throw new Error('ask_never_ready');await page.waitForTimeout(100);}
  await command('interview','ask',ask);await snapshot('persisted-goal-query-and-question');
  const query=proof.retrieval_receipts?.filter(x=>x.request.action==='query').at(-1);if(!query?.request.query?.trim())throw new Error('empty_reopened_goal_query');
  proof.goal_gate_after_ready={query:query.request.query,current:true};
  const postsBefore=proof.receipts.length;await page.reload({waitUntil:'networkidle'});await snapshot('reload-get-only');if(proof.receipts.length!==postsBefore)throw new Error('reload_posted_domain');
  for(const x of proof.dropped){const posts=proof.dropped.filter(y=>y.request.business_key===x.request.business_key);if(posts.length!==1)throw new Error('duplicate_fault_key');}
  if(!proof.assets.some(x=>x.sha256===intent.final_bundle_sha256))throw new Error('current_official_bundle_not_loaded');
  proof.teaching_activity_id=intent.teaching_activity_id;proof.interview_activity_id=intent.interview_activity_id;proof.status='passed';save();
}catch(error){proof.status='failed';proof.failure=String(error);try{await snapshot('failure');}catch(e){proof.snapshot_failure=String(e);}save();throw error;}
finally{
  closing=true;page.removeAllListeners('response');
  let drainTimer;proof.observations_drained_before_close=await Promise.race([Promise.allSettled([...observations]).then(()=>true),new Promise(resolve=>{drainTimer=setTimeout(()=>resolve(false),5000);})]);clearTimeout(drainTimer);
  try{await context.storageState({path:path.join(dir,'storage.json'),indexedDB:true});fs.writeFileSync(path.join(dir,'session-storage.json'),JSON.stringify(await page.evaluate(()=>Object.fromEntries(Object.entries(sessionStorage)))));}catch(e){proof.storage_failure=String(e);}
  try{await context.close();await browser.close();proof.browser_closed=true;}finally{save();process.stdin.removeAllListeners();process.stdin.pause();process.stdin.unref?.();}
}
