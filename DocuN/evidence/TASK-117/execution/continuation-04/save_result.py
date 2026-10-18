"""Save-only S05 return after hard offline gate; preserve every earlier report byte."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,sys,time,subprocess
N=Path(__file__).resolve().parent;E=N.parent;ROOT=E.parents[3]
sys.path.insert(0,str(E));import control as c

def read(name):return json.loads((N/name).read_text(encoding='utf-8'))
def usage(b,s,stamp):
    offline=sum(x['seconds'] for x in b['offline_intervals'] if x.get('segment')==s['permit'])
    if s.get('offline_cursor_mono_ns') is not None:offline+=(stamp['mono_ns']-s['offline_cursor_mono_ns'])/1e9
    runtime=sum(x['seconds'] for x in b['runtime_intervals'] if x.get('segment')==s['permit'])
    activity=(stamp['mono_ns']-s['start_mono_ns'])/1e9
    return {'sample':stamp,'S05':{'activity_seconds':activity,'runtime_seconds':runtime,'offline_seconds':offline,
        'caps':{'activity':21600,'runtime':7200,'offline':10800},'offline_overrun_seconds':max(0,offline-10800),'new_roots':[19,20,21]},
        'cumulative':{'activity_seconds':90806.1720744+activity,'runtime_seconds':24821.501+runtime,'offline_seconds':9011.637117+offline,
                      'offline_forward_cap':19812,'offline_forward_overrun_seconds':max(0,9011.637117+offline-19812)},
        'counts':b['counts'],'offline_gap':'unobserved interruption conservatively charged; not asserted actual CPU or active work for every second',
        'old_caps_overruns_failures_preserved':True,'all_current_resources_stopped':True}

def main():
    result=ROOT/'DocuN/results/TASK-117-result.md';old=(N/'before-result.md').read_bytes()
    assert len(old)==48950 and c.sha(old)=='67f3656fb1f0a602957ac0a8274205d1c51127e1028d9925c05ea8af31f15bc4'
    assert result.read_bytes()==old,'preserve an already-saved S05 result instead of replacing it'
    assert read('final-resource-stop-binding.json')['all_stopped'] and read('final-old-preview-stop.json')['all_current_owned_preview_instances_stopped']
    b=c.state();s=c.active_segment(b);assert b['active_root'] is None and b['counts']['api_starts']==28
    manifest=read('final-source-manifest.json')
    for row in manifest['entries']:
        path=ROOT/row['path']
        if row['post'].get('exists') is False:
            assert not path.exists(),row['path']
        else:assert c.sha(path.read_bytes())==row['post']['sha256'],row['path']
    assets=read('final-bundle-7-binding.json')['files']
    for row in assets:assert c.sha((ROOT/row['path']).read_bytes())==row['sha256']
    rules=json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    for row in rules:assert c.sha(Path(row['absolute_path']).read_bytes())==row['sha256']
    git=lambda *args:subprocess.run(['git','--no-optional-locks',*args],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    repository=read('repository-final.json');assert git('rev-parse','HEAD')==repository['HEAD']
    assert git('config','--get','remote.origin.url')=='https://github.com/shspic/RetroLume-agent.git'
    for row in repository['protected']:assert c.sha((ROOT/'.git'/row['file']).read_bytes())==row['sha256']
    for label,reason in [
        ('S05_default_CIM_read_denied','initial default-sandbox CIM stop check failed; same authorized read-only check succeeded with escalation'),
        ('S05_offline_manifest_enumerations_cancelled','two own enumerations cancelled before candidate inventory; scoped rg inventory succeeded, current creation-window CIM found no residual helper'),
        ('S05_reader_config_test_sandbox_temp_denied','first3 config tests could not write temporary files in sandbox; same3 passed in normal Windows environment'),
        ('S05_final_preview_lookup_timeout','first final exact lookup product2s CLI timed out; original error retained; later unchanged product lookup succeeded'),
        ('S05_GitHub_refs_connection_reset','approved read-only ls-remote exited1 connection reset; local origin/HEAD/index readback passed, live refs unverified')]:
        if not any(x.get('label')==label for x in b['failures']):c.failure(label,reason,effect='preserve original failure; no limits or historical results rewritten');b=c.state();s=c.active_segment(b)
    stamp=c.sample();u=usage(b,s,stamp);local=datetime.fromisoformat(stamp['utc']).astimezone(timezone(timedelta(hours=8))).isoformat()
    gate=read('L10-current-memory-gate.json');reader_gate=read('R01-UI-memory-gate.json')
    root_lines='\n'.join(f"| {key} | {b['counts'][key]-s['baseline_counts'][key]} | {b['counts'][key]} | {s['cumulative_caps'][key]} |" for key in ('roots','pg_create_attempts','pg_objects','volumes','pg_starts','api_starts','browser_starts','frontend_builds','native_windows','http','preview_creates','preview_starts','provider_calls','actual_fee_microunits'))
    link=lambda name:f'[{name}]({(N/name).as_posix()})'
    text=f'''# TASK-117 / R-111 — S05 增量结果（部分交付，已停止）

保存采样：{local}。执行许可 `TASK-117-STEP018-INTEGRATION-S05-20261016`；原 A+ 工程窗口，资源标签不冒充具体模型。未形成稳定 S 候选，未启动独立终审，Q 未启用，未声明28例整体通过；STEP019/020、M-1及全项目仍未完成。

本轮完成旧预览正常恢复及 owned 闭包、实测控制日志热点修补、J-CODE 单范围消歧、正式 bundle7 的同键/晚到视图/复制owner/四账与整步预算 U 验证、R01 隔离只读 reader 的真实 HTTP 查看/写拒绝，以及 README、证据投影和本地 GitHub origin 关联。独立 delete 和依赖的 R02 正式切换由用户明确保留，交主控补合同；PDF、新固定预览与 R01 最终 U 保留未闭。

## 已完成及证据层

| 项目 | 实际结论 | 主要证据 |
|---|---|---|
| 原预览恢复 | 原5c508dc7…沿正常启动恢复取得新的 never_started：原parent/launcher/晚到reaper出生身份结束，精确name+nonce无CID且未请求create/start/attach；原60秒保守全额结算、预留归零；原owned 3a251940…从unknown经正常接口结束。首次StopProof仍为UNCONFIRMED，未改写。 | {link('old-preview-recovery.json')}、{link('final-old-preview-stop.json')} |
| 控制日志热点 | 真实只读gate的相同有限profile从0.891s到0.125s；assert_writable复用已验完整当前字节投影，仍持真实文件锁、逐次完整字节/身份/摘要检查、尾帧拒绝、不可变返回、跨进程当前状态与原持久写入/CAS/时钟。增加固定阶段时钟观察，不移动t0或任何3/4.5/8/D门。 | {link('preview-stage-cost-final.json')}、{link('source-changes.diff')} |
| L08 | 继承两Java中性澄清，只新增正常明确选择J-CODE的活动并取得清楚的Java编程路径，旧范围未改。HTTP/PG/Native层通过；不是Q语义验收。 | {link('L08-JCODE-only-after-clarification.json')} |
| X03/X04/X07 最终 U | Browser12实际载入bundle7：UI一次提交后两个同键真实HTTP并发只读重放同一持久事实，异文409；延迟真实200后换view不污染当前；复制sessionStorage的第二标签页取得不同活跃owner；四账可见；刷新无POST。没有伪造业务响应。 | {link('browser-12/proof.json')} |
| 整步预算 U | Browser13对正常配置产生的真实1请求活动操作，query+model所需2次不足，在任何query/model POST之前拒绝；刷新不重发，真实服务端请求/费用预扣保持0。 | {link('browser-13/proof.json')}、{link('X07-one-request-actual-budget.json')} |
| R01 只读 reader | 新独立reader配置走正常产品构造、核对真实sealed旧R01身份/读权限/写拒绝；宿主不持source写、loader、维护、provider或预览执行配置，不写原selector/fence。七类历史真实HTTP可读，activities/materials/memory/data-job四种POST拒data_readonly。无R01正式activate。 | {link('R01-reader-verified.json')}、{link('reader-host-proof.json')}、{link('api-27-as-run.json')} |
| 旧证据继承 | S04同617行包22.454s恢复/封印、31表/float32/007/unknown/删除覆盖不重跑；S03两域业务/重开、S04无后继reason及X08三类COMMIT丢回包后原键GET不重交。 | 原continuation-03/P03-S04-verified.json、final-UI-passed.json及旧原件 |

R01 HTTP绑定API27源码；其后仅缓存hub身份防替换保护增量另由真实文件检查和正常API28绑定，不冒充R01最终U已跑。正式前端业务源码及4个bundle7资产未变，本轮build新增0；Browser12/13均核对JS SHA `58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8`。

必要定向检查最终为8项当前日志/锁/尾帧/篡改/合法外来hub替换、2项精确owned恢复/重复只读/错误nonce及出生身份、3项reader配置能力隔离，合计13项通过。首次新增围栏检查事件名错误及默认沙箱临时目录权限失败原日志保留，没有当作产品通过。

## 明确保留的缺口

1. **X02独立delete及R02正式切换**：当前010与API仅save/revise/revoke/purge；purge绑定撤销清单且原服务自动清理。不得改001—013/新持久模型，也不得把revoke重做当delete。用户已回复“保留缺口，由主控补合同”。未做新的独立删除、未正式activate、未制造/清理墓碑、未建success02。当前真实六个墓碑tuple均已在原success01 plan.overlay；未来必要新delete出现未覆盖tuple时仍须正常新prepare，并按条件许可判定派生目标。见 {link('user-X02-hold.json')}、{link('R02-overlay-dependency-preflight.json')}。
2. **固定预览 L10**：原artifact当前合法，原失败恢复已闭；新宿主仍无ready/ACK/PNG/正常StopProof。热点诊断总墙钟上界约600s（门900s），只定位了重复日志解析，未测到新的t0→reserve→register/owned→SUP→Popen→ready完整真实分段。本轮两次新preview门均在启动前拒绝，最终可用内存{gate['available']/1024**2:.3f}MiB，门1024MiB；没有新增preview create/start。不能宣称启动超时已全链修复，也不放宽固定门或绕过API次数门。
3. **R01最终U**：HTTP已闭，浏览器启动前内存{reader_gate['available']/1024**2:.3f}MiB，低于768MiB，未启动。只读UI夹具已准备，不作实测通过。
4. **PDF X01**：原两次HTTP422和孤立worker两页成功分别保留。有限身份/启动环境复核没有新的可区分根因，无第三次裸HTTP、未换样本或放宽Job/内存/超时。见 {link('PDF-bounded-diagnosis.json')}。
5. X03其它semantic slot竞争、X04执行中scope/model/selector完整晚到矩阵、X07运行/工具/预览耗尽完整最终U等仍按逐项层证据保留；X05/X06/X12旧边界不因本轮某子集通过而整族认领。Q仍零真实provider/零费用，不外推真实供应商语义。

## 停止、时钟和累计账

断点前证据收口已完成，但报告未保存。恢复入口发现持久offline cursor继续跨越无连续采样的中断空档；未将空档声称全部为实际CPU/人工投入，保守整段入账，不清零或改归类。现已超过offline10800及累计前向19812门，执行只清场/保存，不再业务、修补或新增运行。见 {link('resume-gap-audit.json')}。首入口又漏同步UTC/QPC，后采样根据本聊天首读时戳映射并额外保守扣1秒；原接收失败和漏采保留，不追认合规。

截至报告生成采样：S05活动{u['S05']['activity_seconds']:.3f}s/21600，保守持有{u['S05']['runtime_seconds']:.3f}s/7200，连续离线{u['S05']['offline_seconds']:.3f}s/10800，离线超{u['S05']['offline_overrun_seconds']:.3f}s；累计活动{u['cumulative']['activity_seconds']:.3f}s、持有{u['cumulative']['runtime_seconds']:.3f}s、离线{u['cumulative']['offline_seconds']:.3f}s，累计前向离线超{u['cumulative']['offline_forward_overrun_seconds']:.3f}s。最终保存/复读追加时间以 {link('final-budget-observed.json')} 为准。S04原离线2782.296/2400超382.296、旧累计9011.637117/9000超11.637117及S01—S03旧超额/漏采/失败均原样保留。

| 计数 | S05新增 | 累计 | 当前前向门 |
|---|---:|---:|---:|
{root_lines}

新完整根仅19/20/21三个；根内沿原2100+300s截止恢复，没有失败另改名清零。API累计28已到门，根22、Browser14及其它未用额不消费。本轮6次PG重启全部复用原CID/卷，没有创建新PG/卷，两个failed目标从未启动，sealed success01保留停止。

恢复后的最新精确停止复核确认6个PG非running/Pid0、固定15481—15487/18118无listener、原API/Browser出生实例结束、缓存Chromium及Node后代无残留。旧预览原registry绑定的parent/launcher/reaper结束，精确name+nonce无CID；SUP/REAP现在OpenJob返回error2，仅记当前不存在，不伪填ActiveProcesses=0或回填首次历史成功。原连续采样缺失仍unknown。见 {link('final-resource-stop-binding.json')}、{link('final-old-preview-stop.json')}；期间没有关用户程序或改WSL/全局Docker。

## GitHub、本地交付及审查范围

本地origin已实际关联并复读为 `https://github.com/shspic/RetroLume-agent.git`，main/HEAD `45951501d2741630a229762d6b2d3f4b34d7f702`、index与原有Git配置字节不变（仅追加origin段）。没有commit、push、上传、global config、分支/可见性修改或整目录git add；已批准旧归档删除未reset/stash/clean/恢复。只读远端refs查询连接重置退出1，实时refs未核实；主控派发时public/default main/empty branches只作历史元数据，不冒充当前远端结果。见 {link('repository-final.json')}。

{link('version-sync-manifest.json')}列出产品源码/可信迁移/锁/通用夹具/说明样例的逐文件候选与本地排除范围；候选不是上传批准或敏感检查通过。DocuN原始证据/备份/数据/配置凭据、DocuS用户输入与规划、浏览器storage/profile、运行日志及依赖二进制均不整包公开。README已更新实际启动/配置、低内存分时门、只读reader与正式切换差别、预览限制和公开范围；reader私配可用已忽略的config/data-exit.local.json。新公开样例为config/data-exit-reader.example.json。

采用差异限于data_exit当前字节缓存/完整性检查、正常preview owned恢复与非秘密阶段观察、隔离sealed-reader构造/配置/明确写拒绝、受控夹具和README。001—014迁移本轮未改，fixed renderer/签票器/依赖锁/全局权限/供应商退款语义未改。source pre/diff/post、163项身份、API27/28 as-run与正式bundle绑定均可复核；更早SQL、恢复、业务原件复用。最终稳定候选仍须真正隔离A+集中独审，重点当前缓存/owned/preview/reader边界。本窗口未代改DocuS、任务卡或主控裁定。

## 交接导航

- {link('S-case-closure.md')} / {link('S-case-closure.json')}：28例逐项实际层和缺口，唯一case-index已纠正旧P03 load失败、L10无artifact、X08未完成等陈旧投影。
- {link('changes.json')}、{link('source-changes.diff')}、{link('final-source-manifest.json')}、{link('final-bundle-7-binding.json')}：pre/diff/post与资产身份；新helper另见execution-helpers-manifest.json。
- {link('snapshot-final-tests.log')}、{link('recovery-adapter-tests.log')}、{link('reader-config-tests-02.log')}：最终13项定向检查；首份失败日志不删除。
- {link('result-save-receipt.json')}、{link('final-readback.json')}、{link('final-binding.json')}、{link('final-budget-observed.json')}：保存、复读、停止与预算终态。

建议主控先补独立delete合同；之后针对固定preview真实阶段/StopProof、R01最终U、PDF具体HTTP因果及剩余晚到/预算矩阵补齐受影响证据，保留现有有效成果。不得只以加预算替代这些具体差异或绕过平台审批。

---

以下原S04及更早报告48950字节按原字节完整保留，原SHA `67f3656fb1f0a602957ac0a8274205d1c51127e1028d9925c05ea8af31f15bc4`；包括更早40682字节后缀。

'''
    result.write_bytes(text.encode('utf-8')+old)
    raw=result.read_bytes();assert raw.endswith(old)
    c.write(N/'result-save-receipt.json',{'sample':c.sample(),'path':str(result),'bytes':len(raw),'sha256':c.sha(raw),'old48950_exact_suffix':True,'old_sha256':c.sha(old),'old40682_suffix_inherited':True})
    helpers=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())} for p in sorted(N.glob('*.py'))]
    c.write(N/'execution-helpers-manifest.json',{'sample':c.sample(),'files':helpers,'source_runtime_imported_by_product':False})
    matrix=json.loads((E/'case-index.json').read_text());matrix['S05']['control_status']='OFFLINE_HARD_GATE_EXCEEDED_SAVE_ONLY_RETURN';matrix['S05']['gap_audit']=str(N/'resume-gap-audit.json')
    c.write(E/'case-index.json',matrix);c.write(N/'final-case-index.json',matrix)
    c.event('S05_result_saved',path=str(result),sha256=c.sha(raw),bytes=len(raw),old48950_exact_suffix=True,stable_S=False,Q_enabled=False)
    c.settle_offline();b=c.state();s=c.active_segment(b);stamp=c.sample();u=usage(b,s,stamp)
    s['return_disposition']={'sample':stamp,'status':'partial_returned_after_offline_hard_gate','stable_S':False,'result':str(result),'sha256':c.sha(raw),'bytes':len(raw),
        'old48950_exact_suffix':True,'business_authorization_returned':True,'all_resources_currently_stopped':True,'Q_enabled':False,
        'finalization_cursor_mono_ns':stamp['mono_ns'],'offline_interruption_conservatively_charged':True}
    s['status']='returned_partial';b['phase']='S05_returned_partial_save_only';c.write(E/'budget.json',b)
    c.write(N/'final-budget-observed.json',u)
    c.write(N/'final-readback.json',{'sample':c.sample(),'result_sha256':c.sha(result.read_bytes()),'old48950_exact_suffix':True,'source_entries_verified':len(manifest['entries']),
        'bundle_assets_verified':len(assets),'locked_rules_verified':7,'HEAD_index_origin_verified':True,'all_current_resources_stopped':True,'no_whole_S_acceptance':True})
    names=['receipt.json','final-source-manifest.json','source-changes.diff','final-bundle-7-binding.json','final-case-index.json','S-case-closure.json',
           'final-resource-stop-binding.json','final-old-preview-stop.json','repository-final.json','version-sync-manifest.json','resume-gap-audit.json','user-X02-hold.json',
           'result-save-receipt.json','final-readback.json','final-budget-observed.json','execution-helpers-manifest.json']
    c.write(N/'final-binding.json',{'sample':c.sample(),'result':{'path':str(result),'sha256':c.sha(raw),'bytes':len(raw)},'files':[{'path':str(N/name),'sha256':c.sha((N/name).read_bytes())} for name in names],
        'canonical_budget':str(E/'budget.json'),'canonical_events':str(E/'events.jsonl'),'canonical_case_index':str(E/'case-index.json'),'stable_S':False,'Q':'NOT_ENABLED'})
    print(json.dumps({'saved':str(result),'bytes':len(raw),'sha256':c.sha(raw),'old48950_exact_suffix':True,'status':b['phase'],'offline_seconds':u['S05']['offline_seconds']},ensure_ascii=False))

if __name__=='__main__':main()
