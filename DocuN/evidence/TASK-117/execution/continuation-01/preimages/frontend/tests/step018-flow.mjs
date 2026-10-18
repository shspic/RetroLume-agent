// 正式bundle真实页面；仅请求计数/观察，无响应替换、无Vite。
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const evidence=process.env.RETROLUME_TASK117_EVIDENCE;
if(!evidence)throw new Error('evidence_missing');
const root=path.resolve(evidence,'../../../..');
const attempt=process.env.RETROLUME_TASK117_BROWSER_ATTEMPT??'1';
const dir=path.join(evidence,`browser-${attempt}`);fs.mkdirSync(dir,{recursive:false});
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const proof={attempt,origin:'http://127.0.0.1:18118',official_bundle:true,vite:false,errors:[],receipts:[],requests:0,screenshots:[],semantic_quality:'NOT_RUN_SYNTHETIC_TRANSPORT'};
const priorPath=path.join(evidence,'browser-2','proof.json');
const prior=Number(attempt)>2&&fs.existsSync(priorPath)?JSON.parse(fs.readFileSync(priorPath,'utf8')):null;
if(prior?.teaching_activity_id){proof.teaching_activity_id=prior.teaching_activity_id;proof.inherited_receipts=prior.receipts;proof.inherited_from='browser-2/proof.json';}
function count(name,n=1){if(!n)return;const script="import sys;sys.path.insert(0,sys.argv[1]);from control import count;count(sys.argv[2],int(sys.argv[3]))";const r=spawnSync('python',['-X','utf8','-c',script,evidence,name,String(n)],{cwd:root,encoding:'utf8'});if(r.status)throw new Error('counter_failed:'+name+':'+r.stderr);}
function save(){fs.writeFileSync(path.join(dir,'proof.json'),JSON.stringify(proof,null,2));}
page.on('pageerror',e=>{proof.errors.push(e.message);save();});
await page.route('**/*',async route=>{
  const r=route.request(),u=new URL(r.url());
  if(!['http:','https:'].includes(u.protocol))return route.continue();
  if(u.origin!=='http://127.0.0.1:18118')throw new Error('unexpected_external_request');
  if(u.pathname.startsWith('/api/')){
    count('http');proof.requests++;
    if(r.method()==='POST'){
      let body;try{body=r.postDataJSON();}catch{}
      if(/\/retrieval\/commands$/.test(u.pathname)&&body?.action==='query')count('native_windows');
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
  await button.click();const r=await response;const value=await r.json();proof.receipts.push({scope,action,http:r.status(),value});save();
  if(!r.ok()||value.status!=='committed')throw new Error(scope+'_'+action+'_not_committed:'+JSON.stringify(value));
  await page.waitForTimeout(350);return value;
}
async function create(domain){
  await page.getByRole('button',{name:'我的资料'}).click();
  await page.locator('button.material').filter({hasText:'速度.md'}).first().click();
  await page.getByRole('button',{name:domain==='teaching'?'用这份资料开始学习':'用这份资料开始面试',exact:true}).click();
  await snapshot(domain+'-scope');
  const response=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/activities');
  await page.getByRole('button',{name:'创建活动',exact:true}).click();const r=await response,value=await r.json();
  if(!r.ok())throw new Error('create_failed:'+JSON.stringify(value));proof[domain+'_activity_id']=value.activity.activity_id;save();
  return domain==='teaching'?page.locator('section.ws-teaching'):page.getByRole('region',{name:'文字模拟面试工作区'});
}
try{
  await page.goto('http://127.0.0.1:18118',{waitUntil:'networkidle'});await snapshot('materials');
  let work;
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
  await work.locator('#teaching-answer').fill('2分钟为120秒，120米除以120秒等于1米每秒。');
  await command('teaching','answer',work.getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}));
  await command('teaching','evaluate',work.getByRole('button',{name:'请求评价（1 次模型）',exact:true}));
  await command('teaching','exercise',work.getByRole('button',{name:'新实例复测（1 次模型）',exact:true}));
  await work.locator('#teaching-answer').fill('先把2分钟换成120秒，再计算120/120，平均速度为1米每秒。');
  await command('teaching','answer',work.getByRole('button',{name:'保存作答（零费，不调用模型）',exact:true}));
  await command('teaching','evaluate',work.getByRole('button',{name:'请求评价（1 次模型）',exact:true}));
  await snapshot('teaching-complete');
  await create('interview');work=page.locator('.interview-workspace');await work.waitFor();
  await work.getByLabel('面试目标',{exact:true}).fill('说明平均速度和分钟换秒，区分资料与自报。');
  await work.getByLabel('速度.md的面试用途',{exact:true}).selectOption('reference');
  await command('interview','start',work.getByRole('button',{name:'开始场次',exact:true}));
  await command('interview','ask',work.getByRole('button',{name:'开始提问',exact:true}));
  await work.getByLabel('面试回答',{exact:true}).fill('2分钟是120秒，120米除以120秒等于1米每秒。');
  await command('interview','answer',work.getByRole('button',{name:'保存回答（不调用模型）',exact:true}));
  await command('interview','review',work.getByRole('button',{name:'获取必要追问或反馈',exact:true}));
  await work.getByLabel('面试回答',{exact:true}).fill('1分钟等于60秒，这是资料依据；没有核实的经历仍是自报。');
  await command('interview','answer',work.getByRole('button',{name:'保存回答（不调用模型）',exact:true}));
  await command('interview','review',work.getByRole('button',{name:'获取必要追问或反馈',exact:true}));
  await command('interview','finish',work.getByRole('button',{name:'结束本场次',exact:true}));
  await snapshot('interview-ended');
  const before=proof.receipts.length;await page.reload({waitUntil:'networkidle'});await snapshot('reloaded-get-only');
  if(proof.receipts.length!==before)throw new Error('reload_auto_submitted');
  if(proof.errors.length)throw new Error('browser_page_errors');proof.status='passed';save();
}catch(error){proof.status='failed';proof.failure=String(error);await snapshot('failure');save();throw error;}
finally{await browser.close();}
