"""续作01新命名空间冻结/导航/结果置顶，初轮原件和旧行保留。"""
from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[4];E=ROOT/'DocuN/evidence/TASK-097';C=E/'continuation-01'
sys.path.insert(0,str(E));sys.path.insert(0,str(C))
from artifacts import files,digest,write,stamp
from control import event,permit,ledger,added,events,freeze
START=time.monotonic()

def main():
    p=permit();assert not (C/'post-manifest.json').exists(),'不可覆盖本轮最终冻结'
    freeze('c01-final-artifact-assembly-02',[sys.executable,'-B',str(Path(__file__).resolve())],'仅新命名空间最终冻结、证据适用性、结果保存/readback；无资源启动')
    initial=json.loads((E/'post-manifest.json').read_text(encoding='utf-8'))
    basemap={r['path']:r for r in initial};selected=files();rows=[];changes=[];diff=[]
    for src in selected:
        rel=src.relative_to(ROOT).as_posix();raw=src.read_bytes();sha=digest(src)
        dst=C/'final/files'/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
        rows.append({'path':rel,'sha256':sha,'bytes':len(raw)})
        before=basemap.get(rel)
        if before is None or before['sha256']!=sha:
            old=(C/'pre/files'/rel).read_bytes() if before else b''
            changes.append({'path':rel,'pre':before,'post':rows[-1],'status':'added' if before is None else 'modified'})
            try:
                diff.extend(difflib.unified_diff(old.decode('utf-8-sig').splitlines(True),raw.decode('utf-8-sig').splitlines(True),fromfile='continuation-pre/'+rel,tofile='continuation-post/'+rel))
            except UnicodeDecodeError:diff.append(f'Binary differs: {rel}\n')
    product=lambda rel: rel.startswith(('backend/app/','frontend/src/','frontend/dist/')) or rel in ['README.md','config/activity.example.json']
    drift=[r for r in changes if product(r['path'])];assert not drift,drift
    write(C/'post-manifest.json',rows);write(C/'changes.json',changes);(C/'limited.diff').write_text(''.join(diff),encoding='utf-8')
    build=json.loads((E/'build-binding.json').read_text(encoding='utf-8'))['builds'][-1]
    assert build['label']=='build-05-complete-inputs' and build['exit_code']==0
    inputs=[{**r,'current_sha256':digest(ROOT/r['path'])} for r in build['source_inputs']]
    assert all(r['sha256']==r['current_sha256'] for r in inputs)
    served=json.loads((E/'integration-09-combined/served-bundle.json').read_text(encoding='utf-8'))
    assert len(served)==4 and all(digest(ROOT/'frontend/dist'/r['path'])==r['sha256'] for r in served)
    write(C/'build-binding.json',{'no_new_build':True,'origin_build':build,'current_inputs':inputs,'current_dist':served,
        'actual_browser_served':'DocuN/evidence/TASK-097/integration-09-combined/served-bundle.json','all_origin_inputs_and_served_output_match':True})
    current={r['path']:r['sha256'] for r in rows};bindings=[]
    for folder in [E/'as-run',C/'as-run']:
        for mf in sorted(folder.glob('*/manifest.json')):
            m=json.loads(mf.read_text(encoding='utf-8'))
            if 'files' not in m:
                assert 'inputs' in m
                bindings.append({'batch':mf.parent.name,'manifest':str(mf.relative_to(ROOT)),
                    'scope':'historical document readback only; not a product as-run test snapshot','inputs':m['inputs'],
                    'source_sha256':m.get('source_sha256'),'product_different':[],'scope_note':'旧原字节回读已成立，当前结果保留旧尾部；不作为产品动态验证'})
                continue
            observed={r['path']:r['sha256'] for r in m['files']}
            changed=[r for r,s in observed.items() if r in current and current[r]!=s]
            bindings.append({'batch':mf.parent.name,'manifest':str(mf.relative_to(ROOT)),'current_equal':sum(current.get(r)==s for r,s in observed.items()),
                'different_current':changed,'product_different':[r for r in changed if product(r)],'scope_note':'字节身份只是复用必要条件，实际已通过场景与增量影响见current-matrix；旧FAIL保留'})
    imports=[]
    for name in ['integration-09-combined','integration-10-repair','integration-11-ui-only']:
        observed=json.loads((C/'as-run'/name/'manifest.json').read_text(encoding='utf-8'))
        h={r['path']:r['sha256'] for r in observed['files']}
        for f in sorted((E/name).glob('imports-*.json')):
            loaded=json.loads(f.read_text(encoding='utf-8'))
            for mod,row in loaded.items():
                assert h.get(row['path'])==row['sha256'],(name,mod,row)
            imports.append({'batch':name,'path':str(f.relative_to(ROOT)),'sha256':digest(f),'module_count':len(loaded),'all_match_as_run':True})
    write(C/'evidence-applicability.json',{'bindings':bindings,'actual_imports':imports,'product_unchanged_from_initial_final':True,
        'fixture_after_10_modified':['bootstrap.py','publication.py','processes.py','continuation_ui.py'],
        'final_publication_full_supervisor_business_revalidation':'not_run: SUP quota exhausted; Windows files stress only'})
    launches=[];outcomes=[];supplements=[]
    for f in sorted(E.glob('integration-*/sup-launch-*.json')):
        value=json.loads(f.read_text(encoding='utf-8'));row={'origin':str(f.relative_to(ROOT)),**value}
        created=[x for x in f.parent.glob(f.name+'.*.tmp') if json.loads(x.read_text(encoding='utf-8')).get('created')]
        if created:
            extra=json.loads(created[0].read_text(encoding='utf-8'));row['created_identity_evidence']={'origin':str(created[0].relative_to(ROOT)),**extra};supplements.append(row['created_identity_evidence'])
        launches.append(row)
    for f in sorted(E.glob('integration-*/session-*.json')):outcomes.append({'origin':str(f.relative_to(ROOT)),**json.loads(f.read_text(encoding='utf-8'))})
    newlaunch=[r for r in launches if r.get('permit')=='continuation-01'];assert len(launches)==23 and len(newlaunch)==8
    write(C/'supervision-ledger.json',{'actual_launch_attempts':len(launches),'new_launch_attempts':len(newlaunch),'launches':launches,'session_receipts':outcomes,
        'old_missing_outcome_count':1,'new_pre_CreateProcess_guard_failure_outcome_count':1,'new_created_pre_Resume_failure_count':1,
        'created_identity_supplements':supplements,'created_pending_counted_not_omitted':True,'job_close_count':len(list(E.glob('integration-*/job-close-*.json')))})
    oldattempt=json.loads((C/'pre/files/DocuN/evidence/TASK-097/attempt-ledger.json').read_text(encoding='utf-8'));assert ledger()[:len(oldattempt)]==oldattempt
    # 命令相对路径/工作目录失配在Python启动前失败：原始tool输出及墙钟纳账，非资源入口。
    launch_failure={'category':'offline','label':'c01-command-resolution-failure','seconds':1.342,'exit_code':1,'not_started':True,'reason':'backend工作目录下误用backend/.venv相对路径，PowerShell不能解析；Python及测试均未启动'}
    if not any(x.get('label')==launch_failure['label'] for x in added('offline')):event(launch_failure)
    (C/'command-resolution-failure.txt').write_text("Command cwd: D:/shspic/project_NO3_RetroLume-agent/backend\nCommand: & 'backend/.venv/Scripts/python.exe' -B 'DocuN/evidence/TASK-097/continuation-01/control.py' c01-offline-03-publication ...\nExit: 1; wall_seconds: 1.3414831999999999\nThe term 'backend/.venv/Scripts/python.exe' is not recognized as a name of a cmdlet, function, script file, or executable program.\nNo Python/test/resource process launched. Corrected absolute command captured in c01-offline-03-publication manifest.\n",encoding='utf-8')
    measured=time.monotonic()-START
    event({'category':'offline','label':'c01-final-artifact-assembly-02','seconds':30,'measured_before_report_seconds':measured,
        'timing_basis':'30秒保守额度包含冻结/最终JSON、结果和readback；非声称实际运行30秒','exit_code':0})
    newends=added('integration_end');old=p['baseline']
    newactual=len([f for f in E.glob('integration-*/browser-actual-start.json') if json.loads(f.read_text(encoding='utf-8')).get('permit')=='continuation-01'])
    newdriver=len([f for f in E.glob('integration-*/browser-launch.json') if json.loads(f.read_text(encoding='utf-8')).get('permit')=='continuation-01'])
    incremental={'entries':len(added('integration_entry')),'starts':len(added('container_start')),'sup':len(newlaunch),'browser_actual':newactual,'browser_driver':newdriver,
        'business_seconds':sum(r['business_seconds'] for r in newends),'cleanup_seconds':sum(r['cleanup_seconds'] for r in newends),
        'offline_seconds':sum(r['seconds'] for r in added('offline')),'active_seconds':time.time()-p['active_started_epoch']}
    total={k:old[k]+incremental[k] for k in old};remaining={k:p['added_limits'][k]-incremental[k] for k in incremental}
    assert all(v>=0 for v in remaining.values()),remaining
    budget={'at':stamp(),'initial_preserved':old,'incremental':incremental,'total':total,'added_limits':p['added_limits'],'remaining_added':remaining,
        'active_basis':'原初轮保守上界12681.232110738754 + 续作06:55:06.880Z起至冻结真实墙钟；人工交回等待间隔不计入续作；非精确键盘秒',
        'stop':'新增SUP8/实际browser3/driver3达上限；有剩余入口/秒数不授权更多这些启动','runs':newends}
    write(C/'budget-final.json',budget);write(C/'attempt-ledger-current.json',ledger())
    metadata={'finalized_at':datetime.now(timezone.utc).astimezone().isoformat(),'files':len(rows),'changed_files':len(changes),'product_drift':drift,
        'new_pass_browser_cases':sum(c['status']=='PASS' for n in ['integration-09-combined','integration-10-repair','integration-11-ui-only'] for c in json.loads((E/n/'browser-report.json').read_text(encoding='utf-8'))['cases']),
        'old_result_sha256':digest(C/'pre/files/DocuN/results/TASK-097-result.md'),'build':'build-05-complete-inputs'}
    table='|口径|初轮|续作01|累计|续作剩余|\n|---|---:|---:|---:|---:|\n'
    for key,label in [('entries','runner入口'),('starts','精确容器start'),('sup','实际SUP启动尝试'),('browser_actual','实际浏览器启动尝试'),('browser_driver','浏览器driver'),('business_seconds','业务秒'),('cleanup_seconds','清理秒'),('offline_seconds','离线计费秒'),('active_seconds','主动墙钟上界秒')]:
        table+=f"|{label}|{old[key]:.3f}|{incremental[key]:.3f}|{total[key]:.3f}|{remaining[key]:.3f}|\n"
    prefix=(C/'result-prefix.md').read_text(encoding='utf-8').replace('@@BUDGET@@',table).replace('@@FROZEN_AT@@',metadata['finalized_at']).replace('@@FILES@@',str(len(rows))).replace('@@CHANGES@@',str(len(changes)))
    oldpath=C/'pre/files/DocuN/results/TASK-097-result.md';oldraw=oldpath.read_bytes();resultpath=ROOT/'DocuN/results/TASK-097-result.md';assert resultpath.read_bytes()==oldraw,'结果被其他窗口修改，不能覆盖'
    mark=b'\n\n<!-- TASK-097 initial result preserved byte-for-byte below -->\n\n'
    raw=prefix.encode('utf-8')+mark+oldraw;resultpath.write_bytes(raw)
    assert resultpath.read_bytes()==raw and resultpath.read_bytes().endswith(oldraw);raw.decode('utf-8')
    resultdst=C/'final/documents/TASK-097-result.md';resultdst.parent.mkdir(parents=True,exist_ok=True);resultdst.write_bytes(raw)
    documents=[]
    for name in ['verification-plan.md','ui-supplement-plan.md','repair-01.md','repair-02-stop.md','current-matrix.md','evidence-navigation.md','result-prefix.md','permit.json']:
        src=C/name;dst=C/'final/documents'/name;dst.write_bytes(src.read_bytes());documents.append({'path':str(src.relative_to(ROOT)),'sha256':digest(src),'bytes':src.stat().st_size})
    write(C/'documents-manifest.json',documents)
    write(C/'delivery-proof.json',{'at':stamp(),'result_path':str(resultpath),'sha256':digest(resultpath),'bytes':len(raw),'utf8_readable':True,
        'initial_tail_exact':True,'initial_tail_sha256':hashlib.sha256(oldraw).hexdigest(),'source_files_snapshot':len(rows),'product_unchanged':True,
        'whole_card_state':'部分完成：主链/UI闭合；观察器修正02完整SUP动态not_run','not_independent_audit':True})
    write(C/'artifact-assembly.run.json',{'exit_code':0,'measured_seconds':time.monotonic()-START,'charged_seconds':30,'within_single_offline_60_seconds':time.monotonic()-START<=60,'metadata':metadata})
    print(json.dumps({'saved':str(resultpath),'sha256':digest(resultpath),'product_drift':0,'files':len(rows),'changes':len(changes),'increments':incremental,'state':'partial; main flow and UI complete, final SUP observer dynamic validation not_run'},ensure_ascii=False))

if __name__=='__main__':main()
