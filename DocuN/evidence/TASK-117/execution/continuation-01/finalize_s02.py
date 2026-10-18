"""只结账/保存当前部分交付，不运行旧runner、PG、API或业务。"""
from pathlib import Path
import sys,json,ast,difflib,subprocess,time
from datetime import datetime,timezone,timedelta
C01=Path(__file__).resolve().parent;EXEC=C01.parent;ROOT=EXEC.parents[3]
sys.path.insert(0,str(EXEC));import control as c

def link(name):
    p=C01/name
    return f'[{name}]({p.as_posix()})'

def merge(intervals):
    merged=[]
    for a,b in sorted(intervals):
        if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
        else:merged.append([a,b])
    return {'intervals_mono_ns':merged,'seconds':sum((b-a)/1e9 for a,b in merged)}

def main():
    stamp=c.sample();value=c.state();segment=c.active_segment(value);assert segment and value['active_root'] is None
    final=C01/'finalization';final.mkdir(exist_ok=True)
    stop=json.loads((C01/'final-resource-stop-binding.json').read_text());assert stop['all_stopped']
    assert c.sha(Path(stop['path']).read_bytes())==stop['sha256']
    original_result=ROOT/'DocuN/results/TASK-117-result.md';old=original_result.read_bytes()
    expected='db9dd539274c9b77db237410de31a6c9cc75595bae3b758d6e6c2d5573351b53'
    assert len(old)==21405 and c.sha(old)==expected,'Do not overwrite another delivery; inspect first'
    (final/'S01-result-original.md').write_bytes(old)
    old_manifest=json.loads((EXEC/'final-source-manifest.json').read_text());old_rows={r['path']:r for r in old_manifest['entries']}
    changes=json.loads((C01/'changes.json').read_text())
    paths=set(old_rows)|set(changes)
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'frontend/dist').rglob('*') if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in C01.glob('*.py'))
    paths.update(p.relative_to(ROOT).as_posix() for p in (C01/'quota-recovery').glob('*.py'))
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'backend/tests/fixtures/step018').glob('*.py'))
    rows=[];patch=[];unregistered=[]
    for relative in sorted(paths):
        path=ROOT/relative;exists=path.is_file();raw=path.read_bytes() if exists else b'';pre=changes.get(relative)
        post={'exists':exists,'bytes':len(raw),'sha256':c.sha(raw) if exists else None}
        row={'path':relative,'S02_pre':pre,'post':post,'S01_post':old_rows.get(relative,{}).get('post')}
        if pre is None:row['pre_limit']='no S02 first-edit pre registration; as-run hashes and preserved S01 records remain separate'
        elif pre.get('exists'):
            before=ROOT/pre['backup'];assert before.is_file() and c.sha(before.read_bytes())==pre['sha256']
            if '/dist/' not in relative:
                try:patch.extend(difflib.unified_diff(before.read_text(encoding='utf-8-sig').splitlines(True),raw.decode('utf-8-sig').splitlines(True),fromfile='S02-pre/'+relative,tofile='S02-post/'+relative))
                except UnicodeError:pass
        row['changed_from_S01']=bool(row['S01_post'] and row['S01_post']!=post)
        if row['changed_from_S01'] and pre is None:unregistered.append(relative)
        rows.append(row)
    c.write(C01/'final-source-manifest.json',{'sample':stamp,'scope':'registered TASK117 S02 products/config/tests and own controllers; not whole preexisting dirty checkout','entries':rows,'unregistered_changed_from_S01':unregistered,'old_77_manifest_unchanged':c.sha((EXEC/'final-source-manifest.json').read_bytes()),'as_run_versions_not_upgraded':True})
    (final/'source-changes.diff').write_text(''.join(patch),encoding='utf-8')
    bundle=json.loads((C01/'bundle-5.json').read_text())
    for row in bundle['files']:assert (ROOT/row['path']).is_file() and c.sha((ROOT/row['path']).read_bytes())==row['sha256']
    rules=json.loads((EXEC/'receipt.json').read_text())['rules'];rule_rows=[]
    for row in rules:
        actual=c.sha(Path(row['absolute_path']).read_bytes());assert actual==row['sha256']
        rule_rows.append({'path':row['absolute_path'],'sha256':actual,'same_locked':True})
    c.write(final/'rules.json',{'sample':stamp,'rules':rule_rows,'not_auto_adopting_new_public_versions':True})
    readonly=[]
    fixed=['backend/app/worker/session.py','backend/app/worker/launcher.py','backend/app/preview/host_policy.py','backend/app/preview/pipe.py','backend/app/preview/production_supervisor.py','backend/app/preview/production_reaper.py','backend/app/preview/host_job.py']
    for relative in fixed:
        baseline=old_rows.get(relative,{}).get('post');actual=c.sha((ROOT/relative).read_bytes())
        readonly.append({'path':relative,'current_sha256':actual,'S01_post_sha256':baseline.get('sha256') if baseline else None,'unchanged_from_S01':bool(baseline and actual==baseline['sha256'])})
    c.write(final/'protected-core.json',{'sample':stamp,'entries':readonly,'note':'missing S01 entry stays unproved; no invented historical hash'})
    runtime=sum(r['seconds'] for r in value['runtime_intervals'] if r.get('segment')==segment['permit'])
    offline=sum(r['seconds'] for r in value['offline_intervals'] if r.get('segment')==segment['permit'])
    pg_intervals=[]
    for r in value['resources']:
        for item in r.get('holding_intervals',[]):
            if item.get('segment')==segment['permit']:pg_intervals.append((item['start']['mono_ns'],item['end']['mono_ns']))
    pg_union=merge(pg_intervals)
    c.write(final/'holding.json',{'sample':stamp,'S02_runtime_roots_conservative_seconds':runtime,'S02_PG_CID_union':pg_union,'PG_union_is_not_all_resource_stop_proof':True,'root09_missing_historical_browser_tree_close_charged_until_late_confirmation':value['roots'][8]['end'],'S01_conservative_seconds':16219.360,'S01_CID_union_seconds':16216.391,'clock_domains_not_merged':True})
    gaps={
      'L01':('PARTIAL','bundle4真实错答/针对/曝光/360与240作答已提交；最后240作答revision16评价/完整理由仍未完成。','browser-3/proof.json'),
      'L02':('NOT_RUN','冻结三种等价答案逐答评价未跑；不把模板正确当语义通过。',None),
      'L03':('PARTIAL','真实错答链保留；三项单位/数量级反例完整矩阵未跑。','browser-3/proof.json'),
      'L04':('NOT_RUN','否定/不确定的冻结真实链未跑。',None),
      'L05':('PARTIAL','曝光及不同练习作答已保存；最终240评价与两份独立资格/推进理由未闭。','browser-3/15-teaching-complete.yml'),
      'L06':('PROTOCOL_PARTIAL','C已导入、概念题schema已验；正/反/partial三答未跑。','root08-focused-1792035877082666300.txt'),
      'L07':('PROTOCOL_PARTIAL','P已导入、程序题schema已验；未执行用户代码；两答真实链未跑。',None),
      'L08':('PROTOCOL_PARTIAL','两份Java已导入，澄清schema已验；范围修订/最终bundle未跑。',None),
      'L09':('PROTOCOL_PARTIAL','不足/冲突合成schema有定向检查；真实双源链未跑。','source-closure-check.json'),
      'L10':('PARTIAL','正常operator验签/loader曾就绪，描述schema检查通过；artifact、真实控件ACK/PNG/StopProof集成未跑。','api-proof-8.json'),
      'I01':('BLOCKED_PARTIAL','R+M已导入；checkbox异步fixture及开始前索引门已修。R+M完整ask/probe/review/finish仍未完成。','browser-4/proof.json'),
      'I02':('NOT_RUN','R缺证/自报冻结语义与真实传播未跑。',None),
      'I03':('NOT_RUN','范围外M/利润50%错引冻结矩阵未跑。',None),
      'X01':('PARTIAL_FAILED','8份MD与坏UTF8隔离已有HTTP；PDF两次422保留，不作第三次盲试；逐页/替换矩阵未闭。','pdf-launch-diagnosis.json'),
      'X02':('FAILED','选记忆教学已到保存回答；真实v2面试本地开始报pdf_review_pages权限不足。传递只读源码已修，DB未应用，迟到/修订/撤销/清理未闭。','X02-real-PG-local-memory-error.txt'),
      'X03':('PG_PARTIAL_PASS','真实PG同键并发一份目标、异正文拒绝已验；领域semantic slot/索引batch及最终bundle未闭。','X03-X07-real-PG-only.json'),
      'X04':('IMPLEMENTED_NOT_VERIFIED','源码身份围栏保留；冻结scope/source/view/DataContext迟到矩阵未闭。',None),
      'X05':('PARTIAL','typed/grant/整步门确定检查有实证；完整发送前反例矩阵未闭。','low-memory/focused.txt'),
      'X06':('PARTIAL','合成timeout以及新007监督UNKNOWN均保留；响应失联/非法向量/取消晚到完整组未闭。','unknown-before-normal-reopen.json'),
      'X07':('PG_PARTIAL_PASS','剩1request时query+model整步在INSERT前拒绝，requests/cost均0；运行/工具/预览耗尽和UI重开未闭。','X03-X07-real-PG-only.json'),
      'X08':('PARTIAL','旧COMMIT后GET恢复证据继承；三类显式丢HTTP回包最终bundle未闭。',None),
      'X09':('PARTIAL','同原CID正常start_local启动/就绪/停止已验，原回答GET确认；新feedback与完整面试重开连续性未闭。','root10-original-committed-readback.json'),
      'X10':('FAILED','真实删源事务报PL/pgSQL c.source_refs歧义并回滚；源码alias已修，DB未应用；overlay/恢复未闭。','X10-real-PG-delete-source-error.txt'),
      'X11':('PARTIAL_PASS','分阶段门及真实连续低于256MiB压力自动清场已实证；旧root09停止未确认/晚核偏差保留。','root12-stop-1792045254766060400.json'),
      'X12':('PARTIAL','实际source/version/fragment白名单及grant离线闭包实现；Q固定roster全局PG并发与新父消费完整矩阵未闭。','actual-source-manifest.candidate-receipt.json'),
      'P01':('PARTIAL','compat最小teaching_commands SELECT修复及旧账对账有效；后续记忆传递ACL新修正尚未应用/PG复检。','compat-final-forward-repair.json'),
      'P02':('SQL_PARTIAL_PASS','R01真实恢复/seal/普通readonly UPDATE 42501已验；应用GET/POST查看未跑。','restores-r01.json'),
      'P03':('BLOCKED_PRECONDITION','source实采2space/非空grant元数据/unknown/6向量22个received与007一致；删源失败使overlay前置不成立，R02包/targets未建。','P03-final-R02-and-failed-hash-target-error.txt')}
    prior=json.loads((EXEC/'case-index.json').read_text());(final/'case-index-S01-original.json').write_bytes((EXEC/'case-index.json').read_bytes())
    cases=[]
    for old_case in prior['cases']:
        row=dict(old_case);status,gap,evidence=gaps[row['id']]
        row['history_S01']=old_case;row.update(S_status=status,remaining=gap,Q_status='NOT_ENABLED_NOT_RUN',frozen_scenario_passed=False)
        row['S02_evidence']=[str(C01/evidence)] if evidence and (C01/evidence).exists() else []
        cases.append(row)
    assert len(cases)==28
    c.write(EXEC/'case-index.json',{'schema':'TASK117.case-index.v2','sample':stamp,'S_candidate':'INCOMPLETE_S_ROOT_CAP_AND_UNRESOLVED_RUNTIME','Q':'NOT_ENABLED','passed_frozen_scenarios':0,'cases':cases,'prior_inherited_scope':prior.get('inherited_scope'),'final_source_manifest':str(C01/'final-source-manifest.json'),'new_audit':'NOT_RUN_NOT_READY'})
    fixes=json.loads((C01/'ordinary-db-fixes/adoption.json').read_text())
    constants={}
    for node in ast.parse((ROOT/'backend/app/data_exit/schema_profiles.py').read_text()).body:
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('MIGRATION_014','VECTOR_EXTENSION_VERSION','R02_EXTRA_SHAPE_SHA'):constants[node.targets[0].id]=ast.literal_eval(node.value)
    c.write(C01/'final-binding.json',{'sample':stamp,'source_manifest_sha256':c.sha((C01/'final-source-manifest.json').read_bytes()),'bundle5':bundle,'bundle5_HTTP_browser_binding':'NOT_RUN','bundle4_historical_actual_JS_sha256':'6f3f3b0242c5ab0a746e2c861322132dc03383af6ed3a3519e24541feda8df97','profile_constants':constants,'last_PG_DDL_sha256':'4aa808fd80845e8abb1f09d5547a5c63694fea2f781a69200ec6a992ea8247b0','current_code_DDL_apply':'PENDING, old DB rejected by new trusted shape','pending_forward_SQL':str(C01/'ordinary-db-fixes/pending-forward-repair.sql'),'S_complete':False,'Q_enabled':False})
    head=subprocess.run(['git','--no-optional-locks','rev-parse','HEAD'],cwd=ROOT,capture_output=True,check=True).stdout.decode().strip()
    git_status=subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false','status','--porcelain=v1','--untracked-files=normal'],cwd=ROOT,capture_output=True,check=True).stdout
    (final/'git-status.txt').write_bytes(git_status);c.write(final/'git.json',{'sample':stamp,'HEAD':head,'status_sha256':c.sha(git_status),'git_writes':0})
    auxiliary='辅助只读Node模块定位曾多次失败，最终改用公共executablePath并核证；未启动额外浏览器。一次apply_patch因完整行不匹配原子失败，随后精确修正。原工具回执保留，未追造当时raw日志。四个S02 pre晚恢复条目的原说明保留；没有首建pre的本轮helper仅给当前post/as-run身份。\n'
    (final/'evidence-limits.md').write_text(auxiliary,encoding='utf-8')
    stamp=c.sample();activity=(stamp['mono_ns']-segment['start_mono_ns'])/1e9
    budget={'sample':stamp,'S01':{'activity_seconds':37651.0027854,'original_activity_cap':28800,'activity_overrun_seconds':8851.0027854,'runtime_conservative_seconds':16219.360,'original_runtime_cap':14400,'CID_union_seconds':16216.391,'offline_seconds':1724.875},'S02':{'permit':segment['permit'],'start_utc':segment['start_utc'],'clock_domain':segment['clock_domain'],'activity_seconds':activity,'activity_cap':28800,'runtime_conservative_seconds':runtime,'runtime_cap':10800,'offline_recorded_seconds':offline,'offline_cap':3600,'PG_CID_union':pg_union,'root9_late_confirmation_charged_not_refunded':True},'cumulative':{'activity_seconds':37651.0027854+activity,'activity_cap':66451.0027854,'runtime_conservative_seconds':16219.360+runtime,'runtime_forward_cap':27019.360,'offline_recorded_seconds':1724.875+offline},'counts':value['counts'],'effective_caps':{**segment['cumulative_caps'],'roots':13,'api_starts':14},'TASK_roots_total_cap':14,'Q_root_reserved':1,'S_roots_remaining':0,'old_caps_and_failures_preserved':True,'Native_counter_limit':'预记53含旧S01保守28；ROOT12在HTTP503前预记1但未获Native启动，不退款或冒53成功窗口','all_own_resources_stopped':True}
    c.write(C01/'final-budget-observed.json',budget)
    local=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    report=f'''# TASK-117 / R-111 S02 接续结果：部分交付，S 未完成

保存于 {local}。继续原工程窗口，独占写入；Codex desktop／系统GPT-6，具体后端子型号未披露，A+为资源标签。未派子Agent、未承担独审。

**当前不能提交稳定S采用包。已保留全部有效成果并修正具体源码缺陷，但本卡S运行根13/13已用完；内存压力、007监督未知、尚未应用的DDL修正及冻结矩阵缺口仍在。Q未启用，真实provider调用/实际费用均0，STEP018及项目未验收。**

1. 本轮新增并有效的成果

- 有界控制器在每次启动前登记全部自有PG/API/Browser；按512/768/1024MiB分阶段实时门运行，约2秒采样，两次低于256MiB自动清场。root12真实触发，最低97,435,648 bytes（约93MiB），拒新mutation并确认API/PG/观测线程结束。截止回调最终必要复检也通过。见 {link('source-closure-check.json')}、{link('root12-stop-1792045254766060400.json')}。
- X07整步query+model预算预览及后端门、实际source/version/原件SHA/必要fragment与query白名单、共享grant累计锁及截止前再验签已实现。15个不同定向方法在各自as-run层通过；最后只重检受影响的截止方法。真实普通角色PG确认剩1request时整步在INSERT前拒绝、requests/cost均0，同键并发仅一份目标记录且异正文拒绝。此证据不冒UI完整门或真实Q roster跨活动PG并发。见 {link('X03-X07-real-PG-only.json')}、{link('low-memory/focused.txt')}。
- 8份冻结MD及坏UTF8隔离的真实HTTP有效，实际source/version/原件hash已生成白名单候选；候选未作为Q许可采用。选记忆教学活动 `bbe0617f-0417-4490-8a8f-354ab0e10ae3` 到回答保存，独立于浏览器学习活动。见 {link('actual-source-manifest.candidate-receipt.json')}、{link('memory-teaching-before-reopen.json')}。
- 浏览器学习活动 `b7f32142-b5b3-4a5c-b561-f927bcbe1b6d` 继承原目标/路径，新增错答、针对练习、曝光、360米复测与240米作答等已提交事实；最后answer/revision16未经本轮最终合格评价，截图名称不作完成证明。旧业务键没有整链重放。见 {link('browser-3/proof.json')}。
- compat的最小teaching_commands SELECT与014可信旧定义、旧model/tool/NULL tokens/unknown及预算对账已完成。R01目标 `185cb0ca16203196597ac4c4e00b99b5725fe9806f72e2046d817f913e0f51d4` 已实际恢复、seal、readonly读回，普通角色UPDATE真实拒绝42501；未冒应用查看通过。见 {link('compat-final-forward-repair.json')}、{link('restores-r01.json')}。
- 现有start_local已实际启动、就绪并经原stdin/lifespan与拥有句柄正常停止，同原source CID。夹具已修异步记忆选择等待、关闭期response读体观测收口及导航名称。另修面试开始前索引入口：先开始零费场次，再确认索引；避免消耗预算后被原领域fresh gate拒绝。最后正式build5/typecheck通过，最终bundle尚未HTTP/Browser加载验证。见 {link('bundle-5.json')}。

2. 两个真实SQL错误已改源码，但未应用数据库

- root13面试v2本地开始报 `permission denied for table pdf_review_pages`。静态追查原 `memory_revision_readable → memory_revision_eligible → activity_memory_eligible` 的传递依赖，补SELECT-only的 `material_versions/pdf_review_candidates/pdf_review_pages/pdf_extracted_pages/teaching_records`，不授写权限，不改001—013。
- 真正删源事务报 `c.source_refs is ambiguous`，定位 `retrieval_chunk_guard` 的PL/pgSQL局部row变量c与DELETE查询别名c冲突；仅将该查询别名改为purge_command。原删除事务回滚，最后实采deleted_source=0，原件与历史保留。
- 014当前源码SHA为 `{fixes['new_migration_014_sha256']}`；新R02形状由旧受信a3c9…目录和上述明确增量推导，为 `{fixes['new_shape_sha256']}`。新源码/函数hash/旧001—013精确字节及旧未修shape拒绝检查通过；**这不是PG执行通过**。source/compat仍为原4aa808…DDL，后续获准运行前须原事务前向应用和目录核证，不能跳过schema门。最小可审查事务：{link('ordinary-db-fixes/pending-forward-repair.sql')}；推导：{link('ordinary-db-fixes/adoption.json')}。

3. 未完成与失败事实

- PDF两次真实HTTP422保持；本补充不授权盲目第三次尝试。孤立worker两页诊断成功不代HTTP逐页核验/替换矩阵通过。
- root09在异步勾选记忆时失败，又发生关闭后response.json异常，缺当时browser_closed/整树证。原cleanup/stop的false和Node退出1不改。5:45 UTC完整当前进程/精确CID/端口核证后才前向关root09，保守计至晚核时间；不倒填12:28，不把Sol账号中断冒业务失败唯一原因。
- root10浏览器前余量低于768MiB，未启动；root11 Browser4在图标前缀导航locator失败，关闭期观察器修正已有真实browser_closed=true和整批清场证明。root11新检索键 `95a0b55e-b5fb-45d7-ad6e-310f3bc4b572` 返回UNKNOWN／worker_failed_full_reservation，传输已到而007写阶段CancelledError；原预留和回执留存。关闭诊断trace有约4–5倍只读成本对照，尚不能认定它是该异常的最终根因。
- root12随后遇真实内存压力退出，POST返回controller_stopping 503；预记Native1未获实际启动。没有再换键盲跑。root13只跑PG，不开API/Browser/Native：X03/X07子门成功；记忆开始及删除分别报上述SQL错误。P03因删源overlay前置不成立而停止，未放宽断言、未创建r02/r02-fault或虚构坏包PASS。
- L01最后评价/独立次数与理由、R+M完整I01及I02/I03、L02—L09完整冻结链、L10 artifact/真实ACK/PNG/StopProof、X02/X04/X08/X09全闭包、R01应用GET/POST、R02包/恢复/坏包/应用查看仍有缺口。source最后实采6个512维向量、22个received embedding与22份007一致、2space和1个非执行grant摘要元数据、unknown1，但这些不替代P03往返。完整28场景账：[{(EXEC/'case-index.json').name}]({(EXEC/'case-index.json').as_posix()})，全场景通过数0。

4. 额度、资源与证据边界

| 量 | S01封存 | S02本段 | 当前有效门 |
|---|---:|---:|---:|
| 活动秒 | 37651.0027854（原28800超8851.0027854） | {activity:.3f} | 本段28800；累计66451.0027854 |
| 保守运行/持有秒 | 16219.360（原14400超额保留） | {runtime:.3f} | 本段10800 |
| 已登记offline秒 | 1724.875 | {offline:.3f} | 本段3600／累计5324.875 |

同域计时，S01旧QPC域不与S02直接相减；总活动仍含实现/等待/保存，不以offline或PG并集小计替代。S02 PG CID区间并集 {pg_union['seconds']:.3f} 秒只说明PG，不能抹掉root09浏览器停止未知的保守计时。详细账：{link('final-budget-observed.json')}。

累计根13/13（TASK总14仍保留未来Q1），PGcreate/object/volume3，PGstart16/20，API11/14，Browser4/8，build5/5，Native预记53/160，HTTP304/3000，preview0/12，provider/fee0。未退旧时间/失败/超额/启动；其它数字尚有余额不恢复S新根许可。

最后独立当前核查：3个原CID全部Running=false/Pid0；所有登记API/Node原birth已退出，完整442项进程清单中缓存Chromium及Node后代为0，固定端口无监听。成功R01永久只读保留，source/compat及所有卷/合成行/失败原件保留；无foreign kill、无Git写、无依赖安装/镜像拉取、无真实provider或用户资料。见 {link('final-resource-stop-binding.json')}。

最终源码/pre/diff/post：{link('final-source-manifest.json')}、{link('finalization/source-changes.diff')}；最终bundle/profile绑定：{link('final-binding.json')}；七项锁定规则仍相同。旧77项与root09的84项as-run保持历史身份；build4实际加载JS SHA `6f3f3b0242c5ab0a746e2c861322132dc03383af6ed3a3519e24541feda8df97` 不冒最终build5。晚恢复pre的说明及新helper首建pre缺口不追造，见 {link('finalization/evidence-limits.md')}。

本次交回主控的是部分结果及具体待执行事务/验证缺口，尚不具稳定S集中独审采用条件。Q仍未启用，原80次/20元条件授权未取消也未消费；新执行须按主控有效接续门，禁止直接重跑root09或整批旧runner。

---

以下为原S01报告21405字节全文，SHA `{expected}`，原字节保留；其中状态与路径均为历史时点。

'''
    original_result.write_bytes(report.encode('utf-8')+old)
    raw=original_result.read_bytes();assert raw.endswith(old) and c.sha(raw[-21405:])==expected
    disposition={'sample':c.sample(),'permit':segment['permit'],'S_complete':False,'Q_enabled':False,'reason':'S root cap13 reached; runtime memory/UNKNOWN and unapplied DDL/frozen matrix gaps','result':str(original_result),'result_sha256':c.sha(raw),'all_resources_stopped':True,'new_business_requires_effective_continuation':True}
    value=c.state();value['s02_return_disposition']=disposition;value['phase']='S02_returned_partial';c.active_segment(value)['return_disposition']=disposition;c.write(EXEC/'budget.json',value)
    c.write(C01/'result-save-receipt.json',{'sample':c.sample(),'result_path':str(original_result),'bytes':len(raw),'sha256':c.sha(raw),'S01_suffix_bytes':21405,'S01_suffix_sha256':expected,'S01_original_byte_preserved':True,'source_manifest_sha256':c.sha((C01/'final-source-manifest.json').read_bytes()),'case_index_sha256':c.sha((EXEC/'case-index.json').read_bytes()),'binding_sha256':c.sha((C01/'final-binding.json').read_bytes()),'budget_after_return_sha256':c.sha((EXEC/'budget.json').read_bytes()),'S_complete':False,'Q_enabled':False})
    c.event('S02_partial_result_saved',result_sha256=c.sha(raw),S_complete=False,Q_enabled=False,new_business=False)
    print(json.dumps({'result':str(original_result),'bytes':len(raw),'source_entries':len(rows),'cases':len(cases),'S_complete':False,'Q_enabled':False,'S01_preserved':True,'all_resources_stopped':True},ensure_ascii=False))

if __name__=='__main__':main()
