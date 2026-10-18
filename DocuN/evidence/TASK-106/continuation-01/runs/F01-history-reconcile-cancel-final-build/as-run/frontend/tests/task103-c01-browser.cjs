const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const base=path.resolve(__dirname,'../../DocuN/evidence/TASK-103/continuation-01');
const attempt=process.env.RETROLUME_TASK103_C01_BROWSER||'01';
const out=path.join(base,'browser-'+attempt);fs.mkdirSync(out,{recursive:true});
const resumeTail=process.env.RETROLUME_TASK103_C01_RESUME_TAIL==='true';
const resumeTeaching=process.env.RETROLUME_TASK103_C01_RESUME_TEACHING==='true';
const cases=resumeTail?JSON.parse(fs.readFileSync(path.join(base,'browser-01/result.json'))).cases:[],network=[],loaded=[];let context;const pages=[];
const write=(name,data)=>fs.writeFileSync(path.join(out,name),JSON.stringify(data,null,2));
const assert=(v,m)=>{if(!v)throw Error(m);};
const ok=(name,data={})=>{cases.push({name,status:'PASS',executed:true,...data});write('checkpoint.json',{cases,network,loaded});};
const ws=p=>p.getByRole('region',{name:'学习记忆工作区',exact:true});
const button=(p,name)=>p.getByRole('button',{name,exact:true});
async function until(p,fn,arg){await p.waitForFunction(fn,arg,{timeout:10000});}
async function pageFacts(p,name){
  const values=await p.evaluate(()=>({url:location.pathname,owner:sessionStorage.getItem('retrolume.teaching-editor-owner.v1'),
   details:[...document.querySelectorAll('.memory-detail')].map(x=>({id:x.dataset.memoryId,version:x.dataset.memoryVersion,revision:x.dataset.memoryRevision,sha:x.dataset.memorySha,busy:x.getAttribute('aria-busy'),
    title:x.querySelector('input[aria-label="记忆标题"]')?.value,text:x.querySelector('textarea')?.value,buttons:[...x.querySelectorAll('button')].map(b=>({text:b.textContent,disabled:b.disabled}))}))}));
  write(name+'-values.json',values);fs.writeFileSync(path.join(out,name+'-dom.txt'),await p.locator('body').innerText());await p.screenshot({path:path.join(out,name+'.png'),fullPage:true});
}
async function activity(p){
 await p.getByRole('button',{name:'学习活动',exact:false}).click();await ws(p).locator('.memory-item').first().waitFor();
 await until(p,()=>Boolean(document.querySelector('.memory-detail')?.dataset.editorOwner));
}
async function idle(p){await until(p,()=>document.querySelector('.memory-detail')?.getAttribute('aria-busy')==='false'&&!document.querySelector('.memory-list>button')?.disabled);}
async function find(p,title){
 const region=ws(p);await region.locator('.memory-item').first().waitFor();
 for(let n=0;n<12;n++){
  if(await button(region,title).count())return;
  const more=button(region,'读取更早记忆');if(!await more.count())throw Error('有限分页没有目标 '+title);
  const response=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/memories'&&new URL(r.url()).searchParams.has('cursor'));
  const count=await region.locator('.memory-item').count();await more.click();assert((await response).status()===200,'分页资格变化');
  await until(p,n=>document.querySelectorAll('.memory-item').length>n,count);
 }
 throw Error('有限分页到达边界');
}
async function selected(p,id,title,revision){
 await find(p,title);await button(ws(p),title).click();
 await until(p,({id,revision})=>{const x=document.querySelector('.memory-detail');return x?.dataset.memoryId===id&&Number(x.dataset.memoryRevision)===revision&&x.getAttribute('aria-busy')==='false';},{id,revision});
 assert(await ws(p).getByLabel('记忆标题',{exact:true}).inputValue()===title,'标题尚未随完整绑定载入');
}
async function memorySave(p,title,text){
 await button(ws(p),'新建用户记忆').click();await ws(p).getByLabel('记忆标题',{exact:true}).fill(title);await ws(p).getByLabel('用户正文或注记',{exact:true}).fill(text);
 const response=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/memories/commands'&&r.request().method()==='POST');await button(ws(p),'保存用户记忆').click();
 const r=await response;const receipt=await r.json();assert(r.status()===200&&receipt.status==='committed','保存未确认 '+JSON.stringify(receipt));
 await until(p,id=>document.querySelector('.memory-detail')?.dataset.memoryId===id&&document.querySelector('.memory-detail')?.dataset.memoryRevision==='1'&&document.querySelector('.memory-detail')?.getAttribute('aria-busy')==='false',receipt.memory_id);
 await idle(p);return receipt;
}
async function teachAction(p,name){
 const region=p.getByRole('region',{name:'教学工作区',exact:true});const b=button(region,name);
 await until(p,name=>{const b=[...document.querySelectorAll('.ws-teaching button')].find(x=>x.textContent===name);return b&&!b.disabled;},name);
 const wait=p.waitForResponse(r=>new URL(r.url()).pathname.endsWith('/teaching/commands')&&r.request().method()==='POST',{timeout:55000});await b.click();
 const response=await wait;const receipt=await response.json();assert(response.status()===200&&receipt.status==='committed','教学动作未提交 '+JSON.stringify(receipt));
 await until(p,rev=>document.querySelector('.ws-teaching .section-title .quiet')?.textContent.includes('修订 '+rev),receipt.head_revision_now);return receipt;
}
async function actor(kind,mid){
 const id=crypto.randomUUID(),folder=path.join(base,'workspace/browser-control');fs.mkdirSync(folder,{recursive:true});
 fs.writeFileSync(path.join(folder,id+'.request.json'),JSON.stringify({id,kind,memory_id:mid}));
 const end=Date.now()+10000;while(!fs.existsSync(path.join(folder,id+'.done.json'))){if(Date.now()>end)throw Error('本轮actor没有确认');await new Promise(r=>setTimeout(r,20));}
 const r=JSON.parse(fs.readFileSync(path.join(folder,id+'.done.json')));assert(r.status==='PASS','actor失败 '+JSON.stringify(r));return r;
}
(async()=>{
 try{
  context=await chromium.launchPersistentContext(path.join(base,'workspace/browser-profile-'+attempt),{headless:true});context.setDefaultTimeout(10000);
  context.on('request',r=>{const u=new URL(r.url());if(u.pathname.startsWith('/api/'))network.push({event:'request',at:Date.now(),method:r.method(),path:u.pathname,page:pages.indexOf(r.frame().page())});});
  const capture=[];context.on('response',r=>{const u=new URL(r.url());if(u.pathname.startsWith('/api/'))network.push({event:'response',at:Date.now(),status:r.status(),method:r.request().method(),path:u.pathname});
   if(u.pathname.startsWith('/assets/')&&/\.(js|css)$/.test(u.pathname))capture.push(r.body().then(data=>{loaded.push({path:u.pathname,bytes:data.length,sha256:crypto.createHash('sha256').update(data).digest('hex')});fs.writeFileSync(path.join(out,path.basename(u.pathname)),data);}));});
  const p=await context.newPage();pages.push(p);await p.goto('http://127.0.0.1:18103');await activity(p);
  if(!resumeTail){
  const title='C01浏览器单位笔记 '+attempt;const saved=await memorySave(p,title,'我仍需练习秒的换算');await pageFacts(p,'01-loaded');
  ok('实际最终bundle保存与完整版本绑定',{memory_id:saved.memory_id});
  await ws(p).getByLabel('用户正文或注记',{exact:true}).fill('主标签保留的新草稿');
  const [q]=await Promise.all([context.waitForEvent('page'),p.evaluate(()=>window.open('/','_blank'))]);pages.push(q);await q.waitForLoadState();await activity(q);await selected(q,saved.memory_id,title,1);
  const oa=await p.evaluate(()=>sessionStorage.getItem('retrolume.teaching-editor-owner.v1')),ob=await q.evaluate(()=>sessionStorage.getItem('retrolume.teaching-editor-owner.v1'));assert(oa&&ob&&oa!==ob,'owner复用了live身份');
  await ws(q).getByLabel('用户正文或注记',{exact:true}).fill('第二标签自己的旧版草稿');await pageFacts(q,'02-second-ready');
  await button(ws(p),'预览记忆修正影响').click();await p.getByRole('dialog',{name:'记忆变动确认',exact:true}).waitFor();
  const revised=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/memories/commands'&&r.request().method()==='POST');await button(ws(p),'确认追加修订版本').click();assert((await revised).status()===200,'修订未确认');
  await until(p,()=>document.querySelector('.memory-detail')?.dataset.memoryRevision==='2'&&document.querySelector('.memory-detail')?.getAttribute('aria-busy')==='false');
  await button(ws(q),'预览记忆修正影响').click();await ws(q).getByRole('alert').filter({hasText:'记忆已有新版本'}).waitFor();assert(await ws(q).getByLabel('用户正文或注记',{exact:true}).inputValue()==='第二标签自己的旧版草稿','CAS丢了旧输入');
  ok('双页真实CAS/owner/正文身份',{memory_id:saved.memory_id,distinct_owner:true});
  const beforeRefresh=network.length;await p.reload();await activity(p);await selected(p,saved.memory_id,title,2);assert(network.slice(beforeRefresh).filter(x=>x.event==='request').every(x=>x.method==='GET'),'刷新产生POST');
  ok('刷新与载入草稿只有GET');
  // 延迟真实GET；读取期间输入必须留在旧绑定，明确后才采用新身份。
  const other=await memorySave(p,'C01慢读取目标 '+attempt,'目标原正文');await button(ws(p),'新建用户记忆').click();
  let ready,release;const hit=new Promise(r=>ready=r),hold=new Promise(r=>release=r);
  const target='**/api/memories/'+other.memory_id;
  await p.route(target,async route=>{const real=await route.fetch();ready();await hold;await route.fulfill({response:real}).catch(()=>{});});
  await find(p,'C01慢读取目标 '+attempt);await button(ws(p),'C01慢读取目标 '+attempt).click();await hit;
  await ws(p).getByLabel('记忆标题',{exact:true}).fill('读取中的新输入');await ws(p).getByLabel('用户正文或注记',{exact:true}).fill('不得静默改绑');
  const bound=await ws(p).locator('.memory-detail').getAttribute('data-memory-id');release();await button(ws(p),'明确载入新版').waitFor();
  assert(await ws(p).locator('.memory-detail').getAttribute('data-memory-id')===bound&&await ws(p).getByLabel('用户正文或注记',{exact:true}).inputValue()==='不得静默改绑','慢读覆盖输入或提前改绑');
  await p.unroute(target);await button(ws(p),'明确载入新版').click();await until(p,id=>document.querySelector('.memory-detail')?.dataset.memoryId===id&&document.querySelector('.memory-detail')?.getAttribute('aria-busy')==='false',other.memory_id);
  assert(await ws(p).getByLabel('用户正文或注记',{exact:true}).inputValue()==='目标原正文','明确载入未恢复原正文');ok('慢真实读取保留输入/旧绑定，明确载入后原子切换');
  // COMMIT后丢响应，保留原key/hash，刷新和核对不能重发。
  await button(ws(p),'新建用户记忆').click();await ws(p).getByLabel('记忆标题',{exact:true}).fill('C01丢响应 '+attempt);await ws(p).getByLabel('用户正文或注记',{exact:true}).fill('原意图保持');
  let lost=true;await p.route('**/api/memories/commands',async route=>{if(lost&&route.request().method()==='POST'){lost=false;const r=await route.fetch();assert(r.status()===200,'后台COMMIT失败');await route.abort('failed');}else await route.continue();});
  const posts=network.filter(x=>x.event==='request'&&x.method==='POST').length;await button(ws(p),'保存用户记忆').click();await ws(p).getByRole('alert').filter({hasText:'未确认'}).waitFor();
  const pending=await p.evaluate(()=>JSON.parse(localStorage.getItem('retrolume.memory-intents.v1')||'[]').find(x=>x.action==='save'&&x.state==='unconfirmed'));assert(pending,'原意图丢失');
  await p.unroute('**/api/memories/commands');const from=network.length;await p.reload();await activity(p);await button(ws(p),'只读核对记忆动作').click();await ws(p).getByText('已只读核对，未重发动作',{exact:true}).waitFor();
  assert(network.slice(from).filter(x=>x.event==='request').every(x=>x.method==='GET')&&network.filter(x=>x.event==='request'&&x.method==='POST').length===posts+1,'丢响应自动重发');ok('真实COMMIT丢响应，原键保留，GET核对零重发',{key:pending.key,request_sha:pending.request_sha});
  }
  const backgroundTitle='C01固定背景 '+(resumeTail?'01':attempt);
  const background=resumeTail?{memory_id:JSON.parse(fs.readFileSync(path.join(base,'browser-01/failure-page-0-values.json'))).details[0].id}:await memorySave(p,backgroundTitle,'<script>window.__c01_xss=1</script>我是自报');
  let aid;const teach=p.getByRole('region',{name:'教学工作区',exact:true});
  if(resumeTeaching){
    await p.locator('button.material').filter({hasText:'task103-c01-browser.md'}).first().click();
    await until(p,()=>document.querySelector('.ws-teaching .section-title .quiet')?.textContent.includes('修订 6'));
    const old=JSON.parse(fs.readFileSync(path.join(base,'browser-02/result.json')));
    aid=old.network.find(x=>x.event==='request'&&x.path.endsWith('/teaching/workspace')).path.split('/')[3];
  }else{
  await find(p,backgroundTitle);const pick=ws(p).getByRole('checkbox',{name:'选用记忆 '+backgroundTitle,exact:true});await pick.click();await until(p,title=>Boolean(document.querySelector('input[aria-label="选用记忆 '+title+'"]')?.checked),backgroundTitle);
  assert(await p.evaluate(()=>window.__c01_xss)===undefined,'XSS执行');
  await p.locator('.ws-pick-row').filter({hasText:'task103-c01-browser.md'}).first().getByRole('checkbox').check();
  const created=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/activities'&&r.request().method()==='POST');await button(p,'创建活动').click();const cr=await created;assert(cr.status()===200,'固定选择创建失败');aid=(await cr.json()).activity.activity_id;
  await teach.locator('#teaching-goal').fill('平均速度米秒换算');await teachAction(p,'保存目标（不调用模型）');await teachAction(p,'生成/重订路径（1 次模型）');await teachAction(p,'接受当前路径（零费）');await teachAction(p,'获取练习（1 次模型）');
  await teach.locator('#teaching-answer').fill('我不知道结果');await teachAction(p,'保存作答（零费，不调用模型）');await teachAction(p,'请求评价（1 次模型）');
  }
  const citation=teach.getByRole('button',{name:/查看依据/}).first();await citation.click();await teach.locator('[aria-label="教学引用原文"]').waitFor();
  ok('固定选择、实际API/PG/SUP教学闭环及原文引用',{activity_id:aid,memory_id:background.memory_id});
  // 合成第二阶段不可执行，使本条墓碑pending；随后只明确原清单清理。
  await selected(p,background.memory_id,backgroundTitle,1);await actor('cleanup_disable',background.memory_id);
  await button(ws(p),'预览撤销并清理').click();const revoke=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/memories/commands'&&r.request().method()==='POST');await button(ws(p),'确认撤销并清理本条记忆').click();const rev=await (await revoke).json();assert(rev.purge_state_now==='pending','应为墓碑待清理');
  await idle(p);await actor('cleanup_enable',background.memory_id);const cleanup=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/memories/commands'&&r.request().method()==='POST');await button(ws(p),'明确重试原清单清理').click();assert((await (await cleanup).json()).purge_state_now==='done','原清单重试未完成');
  await button(teach,'刷新教学工作区（只读）').click();await teach.getByRole('alert').filter({hasText:'所选背景已更新或撤销'}).waitFor();assert(await teach.locator('[aria-label="教学引用原文"]').count()===0,'失效引用残留');assert(await ws(p).getByLabel('用户正文或注记',{exact:true}).count()===0,'撤销正文仍显示');ok('撤销pending/明确原清单重试/失效派生与引用清除',{revocation_key:rev.business_key});
  await actor('memory_config_disable',background.memory_id);await p.reload();await activity(p);
  const slowTitle='C01慢读取目标 '+(resumeTail?'01':attempt);await find(p,slowTitle);await ws(p).getByRole('checkbox',{name:'选用记忆 '+slowTitle,exact:true}).click();await until(p,title=>Boolean(document.querySelector('input[aria-label="选用记忆 '+title+'"]')?.checked),slowTitle);
  await p.locator('.ws-pick-row').filter({hasText:'task103-c01-browser.md'}).first().getByRole('checkbox').check();
  const closed=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/activities'&&r.request().method()==='POST');await button(p,'创建活动').click();assert((await closed).status()===200,'无配置的新选择不能持久确定');
  await p.getByRole('status').filter({hasText:'学习背景使用尚未配置，模型动作暂不可用'}).waitFor();assert(await button(teach,'生成/重订路径（1 次模型）').isDisabled(),'配置关闭仍能生成');
  ok('真实配置关闭后的背景模型门，不产生模型请求');await pageFacts(p,'03-final');if(pages[1])await pageFacts(pages[1],'04-second-final');await Promise.all(capture);
  write('result.json',{status:'PASS',cases,network,loaded});
 }catch(error){for(let i=0;i<pages.length;i++)await pageFacts(pages[i],'failure-page-'+i).catch(()=>{});write('result.json',{status:'FAIL',cases,network,loaded,error:String(error.stack||error)});process.exitCode=1;}
 finally{if(context)await context.close();}
})();
