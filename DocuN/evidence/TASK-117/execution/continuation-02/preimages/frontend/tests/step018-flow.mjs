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
const phase=process.env.RETROLUME_TASK117_BROWSER_PHASE??'complete';
const resumeProof=process.env.RETROLUME_TASK117_RESUME_PROOF;
const resume=['resume','continue-root09','interview-only'].includes(phase)&&resumeProof?JSON.parse(fs.readFileSync(resumeProof,'utf8')):null;
const dir=path.join(evidence,`browser-${attempt}`);fs.mkdirSync(dir,{recursive:false});
const browser=await chromium.launch({headless:true});
process.stdin.on('data',()=>{void browser.close();});process.stdin.on('end',()=>{void browser.close();});process.stdin.resume();
const context=await browser.newContext({viewport:{width:1440,height:1000},...(resumeProof?{storageState:path.join(path.dirname(resumeProof),'storage.json')}:{})});
const page=await context.newPage();
const indexBatches=new Map();
const proof={attempt,origin:'http://127.0.0.1:18118',official_bundle:true,vite:false,errors:[],receipts:[],requests:0,screenshots:[],semantic_quality:'NOT_RUN_SYNTHETIC_TRANSPORT'};
proof.phase=phase;proof.assets=[];
const observations=new Set();let closing=false;
function observe(kind,work){const pending=Promise.resolve().then(work).catch(error=>{proof.observation_errors??=[];proof.observation_errors.push({kind,closing,error:String(error)});if(!closing)proof.errors.push('observation:'+kind+':'+String(error));save();}).finally(()=>observations.delete(pending));observations.add(pending);}
const priorPath=path.join(control,'browser-2','proof.json');
const prior=Number(attempt)>2&&fs.existsSync(priorPath)?JSON.parse(fs.readFileSync(priorPath,'utf8')):null;
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
async function create(domain){
  await page.getByRole('button',{name:'我的资料'}).click();
  await page.locator('button.material').filter({hasText:domain==='interview'?'虚构练习经历.md':'速度.md'}).first().click();
  await page.getByRole('button',{name:domain==='teaching'?'用这份资料开始学习':'用这份资料开始面试',exact:true}).click();
  await snapshot(domain+'-scope');
  if(domain==='interview'){
    await page.locator('label.ws-pick-row').filter({hasText:'合成测量.md'}).locator('input').check();
    const memory=page.getByLabel('选用记忆 S02偏好',{exact:true});
    // choose()核对GET当前记忆后才提交受控checked状态；一次真实点击，再核异步结果。
    await memory.click();
    await page.getByText(/新活动已明确选择 1 条/).waitFor();
    if(!await memory.isChecked())throw new Error('memory_selection_not_confirmed');
  }
  const response=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/activities');
  await page.getByRole('button',{name:'创建活动',exact:true}).click();const r=await response,value=await r.json();
  if(!r.ok())throw new Error('create_failed:'+JSON.stringify(value));proof[domain+'_activity_id']=value.activity.activity_id;save();
  return domain==='teaching'?page.locator('section.ws-teaching'):page.getByRole('region',{name:'文字模拟面试工作区'});
}
async function index(work){
  const button=work.getByRole('button',{name:'确认用途、费用与索引当前资料',exact:true});
  await work.getByText(/已核对.*个片段/).waitFor();
  const deadline=Date.now()+10000;
  while(!await button.isEnabled()&&!await work.getByText(/当前索引就绪/).count()&&Date.now()<deadline)await page.waitForTimeout(100);
  if(await button.isEnabled()){
    const response=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/retrieval/commands')&&r.request().postDataJSON()?.action==='source_index',{timeout:100000});
    await button.click();const r=await response,value=await r.json();proof.receipts.push({scope:'retrieval',action:'source_index',http:r.status(),value});save();
    if(!r.ok()||!['received','cache_ready'].includes(value.terminal_disposition))throw new Error('index_not_ready:'+JSON.stringify(value));
    await work.getByText(/当前索引就绪/).waitFor();
  }
}
try{
  await page.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});await snapshot('materials');
  let work;
  if(resume){
    proof.teaching_activity_id=resume.teaching_activity_id;proof.interview_activity_id=resume.interview_activity_id;
    if(phase!=='interview-only'){
    await page.getByRole('navigation').getByRole('button',{name:/学习活动/}).click();
    await page.locator(`[data-activity-id="${proof.teaching_activity_id}"]`).click();work=page.locator('section.ws-teaching');await work.waitFor();
    await command('teaching','evaluate',work.getByRole('button',{name:'请求评价（1 次模型）',exact:true}));await snapshot('normal-reopen-new-feedback-and-reason');
    }
    if(['continue-root09','interview-only'].includes(phase)){
      if(phase!=='interview-only'){
      await work.getByRole('button',{name:'交互解释当前反馈',exact:true}).click();
      const html=page.getByRole('region',{name:'交互解释',exact:true});
      await html.getByLabel('交互解释难点',{exact:true}).fill('核对分钟换秒后的平均速度，d120/t120=1，t240=0.5。');
      await html.getByLabel('确认父成果、资料与一次模型调用额度',{exact:true}).check();
      const response=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/html/commands'),{timeout:100000});
      await html.getByRole('button',{name:'确认生成交互解释',exact:true}).click();const r=await response;const value=await r.json();
      proof.receipts.push({scope:'html',action:'generate',http:r.status(),value});save();
      if(!r.ok()||!value.artifact_id)throw new Error('html_generation_not_saved:'+JSON.stringify(value));
      proof.html_artifact_id=value.artifact_id;await snapshot('current-feedback-html-artifact');
      await html.getByRole('button',{name:'停止并回到学习',exact:true}).click();
      }
      await create('interview');work=page.locator('.interview-workspace');await work.waitFor();
      await work.getByLabel('面试目标',{exact:true}).fill('围绕这份虚构接口项目资料，练习技术面试，重点是个人分工与测量口径。');
      await work.getByLabel('虚构练习经历.md的面试用途',{exact:true}).selectOption('resume');
      await work.getByLabel('合成测量.md的面试用途',{exact:true}).selectOption('measurement');
      await command('interview','start',work.getByRole('button',{name:'开始场次',exact:true}));
      await index(work);
      await command('interview','ask',work.getByRole('button',{name:'开始提问',exact:true}));
      await work.getByLabel('面试回答',{exact:true}).fill('我做了优化，效果很好。');
      await command('interview','answer',work.getByRole('button',{name:'保存回答（不调用模型）',exact:true}));
      await command('interview','review',work.getByRole('button',{name:'获取必要追问或反馈',exact:true}));
      await work.getByLabel('面试回答',{exact:true}).fill('在练习设定中，我参与缓存路径改造。合成测量给的是同环境各1000次，平均耗时100毫秒降到80毫秒，耗时下降20%；不能据此说吞吐或费用提高20%。');
      await command('interview','answer',work.getByRole('button',{name:'保存回答（不调用模型）',exact:true}));await snapshot('interview-answer-before-normal-reopen');
    }else{
    await page.getByRole('button',{name:'模拟面试',exact:true}).click();await page.locator(`[data-activity-id="${proof.interview_activity_id}"]`).click();work=page.locator('.interview-workspace');await work.waitFor();
    await command('interview','review',work.getByRole('button',{name:'获取必要追问或反馈',exact:true}));
    await command('interview','finish',work.getByRole('button',{name:'结束本场次',exact:true}));await snapshot('normal-reopen-interview-finished');
    }
  }else{
  if(prior?.teaching_activity_id){await page.getByRole('button',{name:'学习活动'}).click();await page.locator(`[data-activity-id="${prior.teaching_activity_id}"]`).click();work=page.locator('section.ws-teaching');}
  else work=await create('teaching');
  work=page.locator('section.ws-teaching');await work.waitFor();
  if(!prior?.teaching_activity_id){
  await work.locator('#teaching-goal').fill('根据速度.md，学习平均速度与分钟换秒，说明单位并独立复测。');
  await command('teaching','goal',work.getByRole('button',{name:'保存目标（不调用模型）',exact:true}));
  await command('teaching','plan',work.getByRole('button',{name:'生成/重订路径（1 次模型）',exact:true}));
  await command('teaching','accept_path',work.getByRole('button',{name:'接受当前路径（零费）',exact:true}));
  }
  await command('teaching','select_node',work.getByRole('button',{name:'选择节点 n1（保留当前题为历史）',exact:true}));
  await command('teaching','exercise',work.getByRole('button',{name:'获取练习（1 次模型）',exact:true}));
  await work.locator('#teaching-answer').fill('60米每秒；把120除以2得到60。');
  await command('teaching','answer',work.getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}));
  await command('teaching','evaluate',work.getByRole('button',{name:'请求评价（1 次模型）',exact:true}));
  await command('teaching','exercise',work.getByRole('button',{name:'反馈后续练习（1 次模型）',exact:true}));
  await command('teaching','expose',work.getByRole('button',{name:'查看参考要点（零费）',exact:true}));
  await work.locator('#teaching-answer').fill('2米每秒；1.5分钟=90秒。');
  await command('teaching','answer',work.getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}));
  await command('teaching','evaluate',work.getByRole('button',{name:'请求评价（1 次模型）',exact:true}));
  await command('teaching','exercise',work.getByRole('button',{name:'新实例复测（1 次模型）',exact:true}));
  await work.locator('#teaching-answer').fill('3米每秒；2分钟=120秒。');
  await command('teaching','answer',work.getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}));
  await command('teaching','evaluate',work.getByRole('button',{name:'请求评价（1 次模型）',exact:true}));
  await command('teaching','exercise',work.getByRole('button',{name:'新实例复测（1 次模型）',exact:true}));
  await work.locator('#teaching-answer').fill('4米每秒；1分钟=60秒。');
  await command('teaching','answer',work.getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}));
  if(phase!=='before-restart'){
  await command('teaching','evaluate',work.getByRole('button',{name:'请求评价（1 次模型）',exact:true}));
  }
  await snapshot('teaching-complete');
  await create('interview');work=page.locator('.interview-workspace');await work.waitFor();
  await work.getByLabel('面试目标',{exact:true}).fill('围绕这份虚构接口项目资料，练习技术面试，重点是个人分工与测量口径。');
  await work.getByLabel('虚构练习经历.md的面试用途',{exact:true}).selectOption('resume');
  await work.getByLabel('合成测量.md的面试用途',{exact:true}).selectOption('measurement');
  await command('interview','start',work.getByRole('button',{name:'开始场次',exact:true}));
  await index(work);
  await command('interview','ask',work.getByRole('button',{name:'开始提问',exact:true}));
  await work.getByLabel('面试回答',{exact:true}).fill('我做了优化，效果很好。');
  await command('interview','answer',work.getByRole('button',{name:'保存回答（不调用模型）',exact:true}));
  await command('interview','review',work.getByRole('button',{name:'获取必要追问或反馈',exact:true}));
  await work.getByLabel('面试回答',{exact:true}).fill('在练习设定中，我参与缓存路径改造。合成测量给的是同环境各1000次，平均耗时100毫秒降到80毫秒，耗时下降20%；不能据此说吞吐或费用提高20%。');
  await command('interview','answer',work.getByRole('button',{name:'保存回答（不调用模型）',exact:true}));
  if(phase!=='before-restart'){
  await command('interview','review',work.getByRole('button',{name:'获取必要追问或反馈',exact:true}));
  await command('interview','finish',work.getByRole('button',{name:'结束本场次',exact:true}));
  }
  await snapshot('interview-ended');
  }
  const before=proof.receipts.length;await page.reload({waitUntil:'networkidle'});await snapshot('reloaded-get-only');
  if(proof.receipts.length!==before)throw new Error('reload_auto_submitted');
  if(proof.errors.length)throw new Error('browser_page_errors');proof.status='passed';save();
}catch(error){proof.status='failed';proof.failure=String(error);try{await snapshot('failure');}catch(e){proof.snapshot_failure=String(e);}save();throw error;}
finally{
  closing=true;page.removeAllListeners('response');
  let drainTimer;const drained=await Promise.race([Promise.allSettled([...observations]).then(()=>true),new Promise(resolve=>{drainTimer=setTimeout(()=>resolve(false),5000);})]);clearTimeout(drainTimer);
  proof.observations_drained_before_close=drained;
  try{await context.storageState({path:path.join(dir,'storage.json'),indexedDB:true});}catch(e){proof.storage_save_failure=String(e);}
  try{await browser.close();proof.browser_closed=true;}catch(e){proof.browser_close_failure=String(e);}
  await Promise.allSettled([...observations]);save();process.stdin.removeAllListeners();process.stdin.pause();process.stdin.unref?.();
}
