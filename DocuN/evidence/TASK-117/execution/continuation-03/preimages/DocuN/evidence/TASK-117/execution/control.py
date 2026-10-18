"""本卡单一接收、时间、运行根、资源和差异账。只运行明确调用的本卡动作。"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PERMIT='TASK-117-STEP018-INTEGRATION-S01-20261014'
CAPS={'roots':7,'pg_create_attempts':8,'pg_objects':5,'volumes':5,'pg_starts':20,'api_starts':8,
      'browser_starts':8,'frontend_builds':3,'native_windows':160,'preview_creates':12,'preview_starts':12,
      'http':3000,'provider_calls':0,'actual_fee_microunits':0}


def sample():return {'utc':datetime.now(timezone.utc).isoformat(),'mono_ns':time.monotonic_ns()}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def event(kind,**fields):
    value={'kind':kind,**sample(),**fields}
    with (HERE/'events.jsonl').open('a',encoding='utf-8') as stream:
        stream.write(json.dumps(value,ensure_ascii=False)+'\n')
    return value


def state():return json.loads((HERE/'budget.json').read_text(encoding='utf-8'))


def active_segment(value):
    permit=value.get('active_segment')
    return next((s for s in value.get('segments',[]) if s['permit']==permit and s['status']=='active'),None)


def guard():
    value=state();segment=active_segment(value)
    if segment is not None:
        elapsed=(time.monotonic_ns()-segment['start_mono_ns'])/1e9
        if elapsed<0:raise RuntimeError('active_segment_host_clock_domain_changed')
        if elapsed>=segment['save_only_after_seconds']:raise RuntimeError('S02仅保存清场')
        if datetime.now(timezone.utc)>=datetime.fromisoformat(segment['calendar_deadline_utc']):raise RuntimeError('S02日历门已到')
        for kind,cap in (('runtime',segment['runtime_holding_cap_seconds']),('offline',segment['offline_cap_seconds'])):
            used=sum(x['seconds'] for x in value[kind+'_intervals'] if x.get('segment')==segment['permit'])
            if value['active_root'] is not None:
                root=next(x for x in value['roots'] if x['id']==value['active_root'])
                if root.get('segment')!=segment['permit']:raise RuntimeError('旧根不能借新许可执行')
                if root['category']==kind:used+=(time.monotonic_ns()-root['start']['mono_ns'])/1e9
                if time.monotonic_ns()>=root['business_deadline_mono_ns']:raise RuntimeError('本根仅允许清场')
            if used>=cap:raise RuntimeError('S02_'+kind+'_time_cap')
        if sum(x['seconds'] for x in value['offline_intervals'])>=7200:raise RuntimeError('all_task_offline_time_cap')
        return value
    elapsed=(time.monotonic_ns()-value['start_mono_ns'])/1e9
    if elapsed>=27000:raise RuntimeError('本卡已进入1800秒保存清场段，不再开业务动作')
    if datetime.now(timezone.utc)>=datetime.fromisoformat(value['calendar_deadline_utc']):raise RuntimeError('日历门已到')
    for kind,cap in (('runtime',14400),('offline',7200)):
        used=sum(x['seconds'] for x in value[kind+'_intervals'])
        if value['active_root'] is not None:
            root=next(x for x in value['roots'] if x['id']==value['active_root'])
            if root['category']==kind:used+=(time.monotonic_ns()-root['start']['mono_ns'])/1e9
        if used>=cap:raise RuntimeError(kind+'_time_cap')
    return value


def count(name,number=1):
    value=guard()
    segment=active_segment(value);limits=segment['cumulative_caps'] if segment else CAPS
    amendments=segment.get('scheduling_amendments',[]) if segment else []
    root_cap=amendments[-1]['S_root_cap'] if amendments else limits.get('roots')
    effective_cap=root_cap if name=='roots' else amendments[-1].get('API_cumulative_cap',limits.get(name)) if name=='api_starts' and amendments else limits.get(name)
    if name not in limits or number<1 or value['counts'][name]+number>effective_cap:raise RuntimeError('次数门关闭：'+name)
    scheduling_override=bool(amendments and (name=='roots' or name=='api_starts' and 'API_cumulative_cap' in amendments[-1]))
    if segment and name in segment['segment_caps'] and (not scheduling_override or 'S03' in segment['permit']) and value['counts'][name]+number-segment['baseline_counts'][name]>segment['segment_caps'][name]:raise RuntimeError('当前段次数门关闭：'+name)
    value['counts'][name]+=number;write(HERE/'budget.json',value);event('attempt_reserved',counter=name,number=number,total=value['counts'][name])


def pre(relative):
    guard();path=(ROOT/relative).resolve();path.relative_to(ROOT)
    if any(part in ('.git','private') for part in path.parts) or '.local.' in path.name:
        raise RuntimeError('不读取旧私配或Git内部')
    segment=active_segment(state());base=Path(segment.get('evidence_directory',str(HERE/'continuation-01'))) if segment else HERE
    index_path=base/'changes.json';index=json.loads(index_path.read_text(encoding='utf-8')) if index_path.exists() else {}
    relative=path.relative_to(ROOT).as_posix()
    if relative in index:return index[relative]
    if path.exists():
        raw=path.read_bytes();backup=base/'preimages'/relative;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(raw)
        identity={'exists':True,'bytes':len(raw),'sha256':sha(raw),'backup':backup.relative_to(ROOT).as_posix()}
    else:identity={'exists':False,'bytes':0,'sha256':None}
    identity['recorded']=sample();index[relative]=identity;write(index_path,index);event('preimage_registered',path=relative,identity=identity)
    return identity


def begin_root(label,category='offline'):
    value=guard()
    if value['active_root'] is not None:raise RuntimeError('上一运行根未精确结束')
    count('roots');value=state();stamp=sample()
    root={'id':value['counts']['roots'],'label':label,'category':category,'start':stamp,'end':None,'attempts':[]}
    segment=active_segment(value)
    if segment:root.update(segment=segment['permit'],business_deadline_mono_ns=stamp['mono_ns']+int(segment['root_business_seconds']*1e9),cleanup_deadline_mono_ns=stamp['mono_ns']+int((segment['root_business_seconds']+segment['root_cleanup_seconds'])*1e9))
    value['roots'].append(root);value['active_root']=root['id'];value['phase']=label;write(HERE/'budget.json',value)
    event('root_begin',root=root);return root['id']


def end_root(*,result,resources_confirmed_stopped=True):
    value=state();number=value['active_root']
    if number is None:raise RuntimeError('没有在途运行根')
    if not resources_confirmed_stopped:raise RuntimeError('未确认自有资源结束，不能结束运行根')
    root=next(x for x in value['roots'] if x['id']==number);root['end']=sample();root['result']=result
    interval_start=root.get('resumed_interval_start_mono_ns',root['start']['mono_ns'])
    seconds=(root['end']['mono_ns']-interval_start)/1e9
    key='offline_intervals' if root['category']=='offline' else 'runtime_intervals'
    interval={'root':number,'start_mono_ns':interval_start,'end_mono_ns':root['end']['mono_ns'],'seconds':seconds}
    if root.get('segment'):interval['segment']=root['segment']
    value[key].append(interval)
    value['active_root']=None;value['phase']='implementation';write(HERE/'budget.json',value);event('root_end',root=number,seconds=seconds,result=result)


def resume_root(number,*,stop_evidence):
    """只继续最新同一目标的原截止窗；保存先前attempt结束点，不复位根时钟或计数。"""
    value=guard();segment=active_segment(value)
    if segment is None or value['active_root'] is not None or value['counts']['roots']!=number:raise RuntimeError('root_resume_identity')
    root=next(r for r in value['roots'] if r['id']==number)
    if root.get('segment')!=segment['permit'] or root['end'] is None or time.monotonic_ns()>=root['business_deadline_mono_ns']:raise RuntimeError('root_original_deadline_closed')
    proof=json.loads(Path(stop_evidence).read_text(encoding='utf-8'))
    if proof.get('all_stopped') is not True:raise RuntimeError('root_resume_stop_unconfirmed')
    stamp=sample();root.setdefault('completed_attempts',[]).append({'end':root['end'],'result':root['result'],'resume':stamp,'stop_evidence':str(stop_evidence),'stop_evidence_sha256':sha(Path(stop_evidence).read_bytes())})
    root['resumed_interval_start_mono_ns']=stamp['mono_ns'];root['end']=None
    value['active_root']=number;value['phase']=root['label'];write(HERE/'budget.json',value)
    event('root_resumed_with_original_deadline',root=number,original_start=root['start'],business_deadline_mono_ns=root['business_deadline_mono_ns'],stamp=stamp)


def failure(label,reason,*,effect='保留失败，不改变原输入或预算'):
    value=state();row={'label':label,'reason':reason,'effect':effect,**sample()};value['failures'].append(row);write(HERE/'budget.json',value);event('failure',**row)


def initialize():
    if (HERE/'budget.json').exists():raise RuntimeError('已有预算，不能重复初始化或清零')
    anchor_utc=datetime.fromisoformat('2026-10-14T05:21:53.590792+00:00')
    anchor_mono=1226774590214600
    start_utc=anchor_utc-timedelta(seconds=5);start_mono=anchor_mono-5000000000
    rules=json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    verified=[]
    for row in rules:
        actual=sha(Path(row['absolute_path']).read_bytes())
        if actual!=row['sha256']:raise RuntimeError('锁定规则变化：'+row['relative_path'])
        verified.append({**row,'same_locked':True})
    used=['AGENTS.md','DocuN/tasks/TASK-117.md','DocuN/results/TASK-117-work-decision.md',
          'DocuN/results/TASK-116-work-decision.md','DocuN/results/TASK-116-result.md',
          'DocuN/evidence/TASK-116/design/integration-contract.md','DocuN/evidence/TASK-116/design/acceptance-contract.md',
          'DocuN/evidence/TASK-116/design/sample-inputs.json','DocuN/evidence/TASK-116/design/adoption-package.md',
          'DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json',
          'DocuN/evidence/TASK-117/orchestration-20261014/input-manifest.json']
    identities=[{'path':relative,'bytes':(ROOT/relative).stat().st_size,'sha256':sha((ROOT/relative).read_bytes())} for relative in used]
    receipt={'TASK':'TASK-117','R':'R-111','permit':PERMIT,'stage':'S01','model':'Codex desktop / 系统GPT-6；具体后端子型号未披露；A+为资源标签',
             'first_tool_pair':{'utc':anchor_utc.isoformat(),'mono_ns':anchor_mono},
             'anchor_basis':'首工具内同步采UTC/QPC；同次并行文件读取可能先于采钟，额外保守扣5秒，不冒精确首入口',
             'start_utc_conservative':start_utc.isoformat(),'start_mono_ns_conservative':start_mono,
             'recorded':sample(),'rules':verified,'input_identities':identities,
             'AP1':'已采用','AP2':'已条件性批准，Q未启用；当前真实供应商请求/费用0',
             'previous_execution_directory_existed':False,'old_permissions':'已结束，仅继承原件，不执行旧runner或启旧对象',
             'subagents':0,'status':'S01_in_progress'}
    write(HERE/'receipt.json',receipt)
    budget={'permit':PERMIT,'start_utc':start_utc.isoformat(),'start_mono_ns':start_mono,
            'calendar_deadline_utc':(start_utc+timedelta(hours=72)).isoformat(),'activity_cap_seconds':28800,
            'save_reserve_seconds':1800,'runtime_holding_cap_seconds':14400,'offline_cap_seconds':7200,
            'counts':{key:0 for key in CAPS},'caps':CAPS,'runtime_intervals':[],'offline_intervals':[],
            'roots':[],'resources':[],'failures':[],'official_pages':[],'active_root':None,
            'phase':'preflight_and_implementation','old_task_counters_unchanged':True}
    write(HERE/'budget.json',budget)
    event('received',permit=PERMIT,phase=budget['phase'])
    result=subprocess.run(['git','--no-optional-locks','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True)
    git_status=subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false','status','--porcelain=v1','--untracked-files=normal'],cwd=ROOT,capture_output=True,check=True)
    (HERE/'git-status-before.txt').write_bytes(git_status.stdout)
    write(HERE/'git-baseline.json',{'head':result.stdout.strip(),'porcelain_sha256':sha(git_status.stdout),
                                 'lines':len(git_status.stdout.splitlines()),'existing_changes_protected':True,'git_writes':0})
    print(json.dumps({'received':PERMIT,'rules_locked':len(verified),'root_running':None,'runtime':0,'S_real_provider_calls':0,'S_fee':0},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['init','pre','status']);parser.add_argument('paths',nargs='*');args=parser.parse_args()
    if args.command=='init':initialize()
    elif args.command=='pre':
        for path in args.paths:pre(path)
        print(json.dumps({'preimages_registered':len(args.paths)},ensure_ascii=False))
    else:
        value=state();segment=active_segment(value);elapsed=(time.monotonic_ns()-(segment or value)['start_mono_ns'])/1e9
        print(json.dumps({'elapsed_seconds':elapsed,'active_permit':segment['permit'] if segment else value['permit'],'cumulative_activity_seconds':(segment['baseline_s01_activity_seconds'] if segment else 0)+elapsed,'phase':value['phase'],'counts':value['counts'],'root':value['active_root']},ensure_ascii=False))
