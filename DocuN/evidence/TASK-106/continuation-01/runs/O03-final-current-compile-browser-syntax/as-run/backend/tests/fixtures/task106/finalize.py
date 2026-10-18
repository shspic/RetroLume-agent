"""Read-only identities and exact ownership cleanup; no new real runner root."""
import ctypes,difflib,hashlib,json,shutil,subprocess,time
from pathlib import Path
from .control import ROOT,EVIDENCE,atomic_json,source_manifest,locked,charge
from .resources import inspect,freeze
from .http_group import process_birth

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def cleanup():
    begun=time.perf_counter();out=EVIDENCE/'final';out.mkdir(parents=True,exist_ok=True)
    with locked() as state:resources=state['resources'].copy()
    containers=[]
    for n in (1,2,3):
        actual=freeze(inspect(resources[f'pg{n}']['cid']),n)
        assert not actual['state']['Running'] and actual['state']['Pid']==0
        containers.append(actual)
    query="Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18106,18107,55446,55447,55448) } | Select-Object LocalAddress,LocalPort,OwningProcess | ConvertTo-Json -Compress"
    result=subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    listeners=json.loads(result.stdout or '[]');assert not listeners,listeners
    # New106 profile namespaces only; never capture unrelated command lines.
    prefix=str(EVIDENCE/'runs').replace("'","''")
    query="Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' -and $_.CommandLine.Contains('"+prefix+"') -and $_.CommandLine.Contains('chrome-profile') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"
    result=subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    chrome=json.loads(result.stdout or '[]');assert not chrome, 'Owned profile still has a Chrome process; do not broad kill'
    checks=[];known=[]
    for p in (EVIDENCE/'runs').glob('*/owned-*.json'):
        item=json.loads(p.read_text(encoding='utf-8'));items=item if isinstance(item,list) else [item]
        for x in items:
            pid=x.get('pid',x.get('ProcessId'));birth=x.get('birth_100ns')
            if pid and birth:known.append((pid,birth,p.relative_to(ROOT).as_posix()))
    for p in (EVIDENCE/'observations').glob('*.json'):
        item=json.loads(p.read_text(encoding='utf-8'))
        if item.get('kind')=='native-sup':
            x=item['value'];known.append((x['pid'],x['created_100ns'],p.relative_to(ROOT).as_posix()))
    for pid,birth,proof in sorted(set(known)):
        try:live_birth=process_birth(pid)
        except RuntimeError:live_birth=None
        same=live_birth==birth
        checks.append(dict(pid=pid,expected_birth_100ns=birth,live_birth_100ns=live_birth,original_alive=same,proof=proof))
        assert not same, 'An exact owned process remains; no PID-only termination authorized'
    sessions=[]
    for p in (EVIDENCE/'observations').glob('*.json'):
        item=json.loads(p.read_text(encoding='utf-8'))
        if item.get('kind')=='native-session':
            x=item['value'];sessions.append(dict(proof=p.relative_to(ROOT).as_posix(),**x))
            if x.get('active_processes_at_end') is not None:assert x['active_processes_at_end']==0
            assert not x.get('cleanup_incomplete')
    runs=[json.loads(p.read_text(encoding='utf-8')) for p in (EVIDENCE/'runs').glob('*/run.json')]
    assert all(x['status']!='running' for x in runs)
    atomic_json(out/'resource-stop-proof.json',dict(containers=containers,listeners=listeners,owned_profile_processes=chrome,process_identities=checks,
        native_sessions=sessions,all_runs_closed=True,preserved='all new data, roles, volumes, containers, profiles, failed originals; no DROP/DELETE/removal',no_termination_needed=True))
    charge('cleanup',time.perf_counter()-begun,'final exact resource/port/PID birth/Job observations verification')

def package():
    out=EVIDENCE/'final';out.mkdir(parents=True,exist_ok=True)
    spec=json.loads((EVIDENCE/'implementation-map.json').read_text(encoding='utf-8'))
    baseline=json.loads((EVIDENCE/'orchestration-setup-20261008/baseline-input.json').read_text(encoding='utf-8'))['current_files']
    allowed=set(spec['modified']);changed=[];protected=[];bad=[]
    for name,before in baseline.items():
        path=ROOT/name;after=digest(path) if path.is_file() else None
        item=dict(path=name,before=before,after=after,equal=before==after)
        if name in allowed or name.startswith('frontend/dist/'):
            if before!=after:changed.append(item)
        else:
            protected.append(item)
            if before!=after:bad.append(item)
    assert not bad,'Protected baseline drift; exact items saved only on a diagnosed exception'
    rules=json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8'))
    rulechecks=[dict(path=x['absolute_path'],before=x['sha256'],after=digest(x['absolute_path'])) for x in rules]
    assert all(x['before']==x['after'] for x in rulechecks)
    assert digest(ROOT/'DocuN/results/TASK-105-result.md')=='c1b192aa05cdab6384b9c3114269c7396ec44022685f1ac7d48edcd03f37483d'
    diffdir=out/'diff';diffdir.mkdir(exist_ok=True)
    for name in spec['modified']:
        before=EVIDENCE/'pre'/name;after=ROOT/name
        assert before.is_file() and after.is_file()
        target=diffdir/(name.replace('/','__')+'.patch')
        target.write_text(''.join(difflib.unified_diff(before.read_text(encoding='utf-8-sig').splitlines(keepends=True),after.read_text(encoding='utf-8-sig').splitlines(keepends=True),fromfile='pre/'+name,tofile='post/'+name)),encoding='utf-8')
    files=source_manifest()
    for name in files:
        target=out/'post'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    atomic_json(out/'post-source.json',files)
    identity=json.loads((EVIDENCE/'runs/F03-final-immediate-panel-invalidation-build/build-identity.json').read_text(encoding='utf-8'))
    assert all(digest(ROOT/p)==v for p,v in identity['dist'].items())
    for run in ('P12-resume-committed-browser-repair','P16-final-late-record-owner-draft'):
        pre=json.loads((EVIDENCE/'runs'/run/'pre-source.json').read_text(encoding='utf-8'))
        assert all(pre.get(p)==v for p,v in identity['dist'].items())
        assert json.loads((EVIDENCE/'runs'/run/'browser-result.json').read_text(encoding='utf-8'))['passed']
    atomic_json(out/'baseline-post-and-build-identity.json',dict(baseline_objects=len(baseline),authorized_changes=changed,protected_checked=len(protected),protected_drift=bad,
        protected=protected,locked_rules=rulechecks,new_production=[dict(path=p,sha256=digest(ROOT/p)) for p in spec['new_backend']+spec['new_frontend']],
        final_build=identity,source_build_HTTP_browser_match=True,old_contract_sha256=digest(ROOT/'DocuN/results/TASK-105-result.md')))
    print('Protected sources, contract, final dist/browser identity and exact resource stop verified')

if __name__=='__main__':cleanup();package()
