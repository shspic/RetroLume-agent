"""S03前向接收，保留旧段原件及真实计时边界。"""
from pathlib import Path
from datetime import datetime,timedelta,timezone
import sys,json,time,hashlib,shutil
N=Path(__file__).resolve().parent;E=N.parent;R=E.parents[3]
sys.path.insert(0,str(E))
import control as c

def main():
    assert not (N/'receipt.json').exists(),'已经接收，禁止重新立账'
    stamp=c.sample();anchor=json.loads((N/'first-reliable-clock.json').read_text(encoding='utf-8-sig'))
    permit=json.loads((R/'DocuN/evidence/TASK-117/orchestration-s03-20261015/continuation-permit.json').read_text(encoding='utf-8'))
    # 前几次只读未同次采钟，使用许可发出时刻作为更早的保守下界，不冒充首工具精确点。
    lower=datetime.fromisoformat(permit['at']).astimezone(timezone.utc)
    start_mono=stamp['mono_ns']-int((datetime.fromisoformat(stamp['utc'])-lower).total_seconds()*1e9)
    before={}
    for name in ('budget.json','events.jsonl','case-index.json'):
        raw=(E/name).read_bytes();(N/('before-'+name)).write_bytes(raw)
        before[name]={'bytes':len(raw),'sha256':c.sha(raw)}
    report=R/'DocuN/results/TASK-117-result.md';raw=report.read_bytes()
    assert len(raw)==31949 and c.sha(raw)=='5f2e0a19f893dcd6634345b86149d9a35de41354cb50f2694f76a024ba1c0c8d'
    (N/'before-result.md').write_bytes(raw)
    entries=json.loads((E/'continuation-01/final-source-manifest.json').read_text())['entries']
    for row in entries:
        p=R/row['path'];post=row['post'];assert p.exists()==post['exists'],row['path']
        if p.exists():assert c.sha(p.read_bytes())==post['sha256'],row['path']
    rules=json.loads((R/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    for row in rules:assert c.sha(Path(row['absolute_path']).read_bytes())==row['sha256']
    v=c.state();assert v['active_root'] is None and v['counts']==permit['counts_baseline_at_issuance']
    stop=json.loads((N/'entry-stop.json').read_text());assert stop['all_stopped']
    assert all(not r.get('running') for r in v['resources'] if r.get('kind')=='pg')
    inputs={}
    for rel in ('DocuN/tasks/TASK-117.md','DocuN/results/TASK-117-work-decision.md',
      'DocuN/evidence/TASK-117/orchestration-s03-20261015/received.json',
      'DocuN/evidence/TASK-117/orchestration-s03-20261015/continuation-permit.json',
      'DocuN/evidence/TASK-117/orchestration-s03-20261015/input-manifest.json'):
        p=R/rel;inputs[rel]={'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())}
    segment={'permit':permit['permit'],'status':'active','start_utc':lower.isoformat(),'start_mono_ns':start_mono,
      'clock_domain':'S03-current-host-QPC','start_basis':'首工具漏采钟；以许可发出时刻作保守更早下界，首个可靠同步点单独保存',
      'calendar_deadline_utc':(lower+timedelta(hours=48)).isoformat(),'activity_cap_seconds':21600,
      'no_expansion_after_seconds':18000,'save_only_after_seconds':19800,'runtime_holding_cap_seconds':10800,
      'offline_cap_seconds':3000,'root_business_seconds':2100,'root_cleanup_seconds':300,
      'baseline_counts':dict(v['counts']),'baseline_cumulative_activity_seconds':54954.7049314,
      'baseline_cumulative_runtime_seconds':21921.454,'baseline_cumulative_offline_seconds':2546.561,
      'segment_caps':permit['new_counts_caps'],'cumulative_caps':permit['cumulative_counts_caps'],
      'evidence_directory':str(N),'scheduling_amendments':[{'profile':'S03-staged-low-memory',
        'S_root_cap':17,'API_cumulative_cap':19,'stages_MiB':{'base':512,'pg':512,'api':512,'browser':768,'second_pg':768,'preview':1024}}]}
    v['segments'].append(segment);v['active_segment']=segment['permit'];v['phase']='S03_preparation'
    c.write(E/'budget.json',v)
    c.write(N/'receipt.json',{'sample':stamp,'first_reliable_pair':anchor,'segment':segment,'before':before,'inputs':inputs,
      '113_current_identities_checked':len(entries),'rules_unchanged':len(rules),'actual_client':'Codex desktop / GPT-6，A+为资源标签',
      'single_writer':'原工程窗口；未创建接续窗或子Agent','prior_gap':'S02交回至S03接收间无本窗口业务，当前完整停机证明；不计作运行',
      'first_tool_clock_deviation':'最初只读工具未同步采钟，已保守扣许可发出至可靠点全部间隔；未追造精确首点'})
    c.event('S03_received',permit=segment['permit'],start_basis=segment['start_basis'],receipt=str(N/'receipt.json'))
    print(json.dumps({'permit':segment['permit'],'identities':len(entries),'all_stopped':True,'activity_elapsed':(time.monotonic_ns()-start_mono)/1e9}))
if __name__=='__main__':main()
