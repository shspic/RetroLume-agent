"""不消费旧 runner，只核原件、as-run 和冻结产品的逐字节身份。"""
import collections
import hashlib
import json
from pathlib import Path
import stat
from bootstrap import ROOT, AUDIT, digest, save

def check_entry(row, base):
    p = base / row['path']
    exists = p.is_file()
    actual = digest(p) if exists else None
    return {'path':str(p), 'sha256':actual, 'expected':row.get('sha256'),
            'match':actual==row.get('sha256') if row.get('sha256') else not exists}

def protected():
    paths = [ROOT/'DocuN/evidence/TASK-114/implementation/control/receipt.json',
             ROOT/'DocuN/evidence/TASK-114/implementation/control/events.jsonl']
    old = ROOT/'DocuN/evidence/TASK-114/synthetic'
    for directory in ('source-root','backup-root','control-root','restore-root'):
        for p in sorted((old/directory).rglob('*')):
            info=p.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                raise RuntimeError('受保护输入存在重解析点，停止自动扫描')
            if p.is_file():paths.append(p)
    return [{'path':str(p), 'bytes':p.stat().st_size,'sha256':digest(p)} for p in paths]

def main():
    baseline=AUDIT/'protected-before.json'
    if not baseline.exists():save('protected-before.json',protected())
    c01 = ROOT/'DocuN/evidence/TASK-114/implementation/continuation-01'
    final = json.loads((c01/'final/manifest.json').read_text(encoding='utf-8-sig'))
    source_check=[check_entry(r,c01/'final/source') for r in final if r.get('sha256')]
    current_check=[check_entry(r,ROOT) for r in final if r.get('sha256')]
    outputs={}
    for name in ('batch-result-index.json','failure-index.json'):
        index=json.loads((c01/'final'/name).read_text(encoding='utf-8-sig'))
        outputs[name]=[check_entry(r,ROOT) for r in index]
    deltas={}
    asrun_checks={}
    missing_asrun=[]
    direct=('backend/app/data_exit/','backend/migrations/013_','backend/app/main.py','frontend/src/data/',
            'backend/app/materials/','backend/app/storage/','backend/app/worker/','backend/app/preview/',
            'backend/app/activities/','backend/app/memory/','frontend/dist/')
    for folder in sorted((c01/'as-run').iterdir()):
        if not (folder/'manifest.json').is_file():
            missing_asrun.append(folder.name)
            continue
        value=json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
        rows=value['files'] if isinstance(value,dict) else value
        asrun_checks[folder.name]=[check_entry(r,folder) for r in rows]
        deltas[folder.name]=[r['path'] for r in rows if r['path'].startswith(direct)
                             and (not (ROOT/r['path']).is_file() or digest(ROOT/r['path'])!=r['sha256'])]
    save('frozen-and-as-run.json',{'final_source':source_check,'current':current_check,'indexes':outputs,
                                  'as_run':asrun_checks,'direct_deltas':deltas,'missing_as_run_manifests':missing_asrun})
    old_control=json.loads((ROOT/'DocuN/evidence/TASK-114/implementation/control/receipt.json').read_text(encoding='utf-8-sig'))
    events=[json.loads(line) for line in (ROOT/'DocuN/evidence/TASK-114/implementation/control/events.jsonl').read_text(encoding='utf-8-sig').splitlines()]
    save('control/original-control-structure.json',{'receipt_keys':list(old_control),
         'event_count':len(events),'event_keys':list(events[0]),
         'event_kind_counts':dict(collections.Counter(e.get('event',e.get('kind')) for e in events))})
    print(json.dumps({'final_entries':len(final),'final_copy_matches':sum(r['match'] for r in source_check),
          'current_matches':sum(r['match'] for r in current_check),
          'index_matches':{k:sum(r['match'] for r in v) for k,v in outputs.items()},
          'as_run_mismatches':{k:[r['path'] for r in v if not r['match']] for k,v in asrun_checks.items() if any(not r['match'] for r in v)},
          'direct_deltas':deltas,'missing_as_run':missing_asrun,'old_receipt_keys':list(old_control),'first_event_keys':list(events[0]),
          'event_kinds':dict(collections.Counter(e.get('event',e.get('kind')) for e in events))},ensure_ascii=False))

if __name__=='__main__':main()
