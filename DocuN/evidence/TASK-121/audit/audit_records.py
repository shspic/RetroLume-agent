"""仅对已保存记录做标准库对照；不调用业务或原工程runner。"""
import collections
import datetime
import hashlib
import json
from pathlib import Path

ROOT=Path(r'D:\shspic\project_NO3_RetroLume-agent')
E=ROOT/'DocuN/evidence/TASK-120/execution'
OUT=ROOT/'DocuN/evidence/TASK-121/audit'
def get(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def dt(value):return datetime.datetime.fromisoformat(value.replace('Z','+00:00'))

def main():
    b=get(E/'budget.json')
    events=[json.loads(line) for line in (E/'events.jsonl').read_text(encoding='utf-8-sig').splitlines()]
    kind=lambda x:x.get('kind',x.get('event'))
    stages=[('orchestration-20261018',1,8),('orchestration-continuation01-20261019',9,16),
      ('orchestration-repair03-20261019',17,20),('orchestration-validation04-20261019',21,24),
      ('orchestration-final05-20261019',25,40),('orchestration-continuation06-20261020',41,51)]
    permits=[]
    for folder,start,end in stages:
        path=E.parent/folder/'permit.json';p=get(path)
        permit_id=p['id'];caps=p.get('new_cumulative_caps',p.get('new_caps'))
        adopted=next((x for x in b['permit_history'] if x.get('id',x.get('permit_id'))==permit_id),None)
        adopted_time=adopted.get('received_and_adopted_utc',adopted.get('adopted_at_utc',adopted.get('registered_utc'))) if adopted else b['actual_first_tool_utc']
        permit=dict(path=str(path.relative_to(ROOT)),sha256=sha(path),id=permit_id,issued_at=p['issued_at'],adopted_at=adopted_time,
          root_range=[start,end],caps=caps,root_entry_excesses=[],roots_before_adoption=[])
        for root in b['roots']:
            if start<=root['id']<=end:
                excess={key:(value,caps.get(key)) for key,value in root['counts_at_entry'].items() if key in caps and value>caps[key]}
                if excess:permit['root_entry_excesses'].append(dict(root=root['id'],excess=excess))
                if adopted_time and dt(root['start_utc'])<dt(adopted_time):permit['roots_before_adoption'].append(root['id'])
        permits.append(permit)
    components={k:b[k] for k in ('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds',
      'unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds',
      'continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds',
      'validation04_unwrapped_command_wall_upper_seconds','finalization05_unwrapped_command_wall_upper_seconds','continuation06_unwrapped_command_wall_upper_seconds')}
    receipts=[]
    for path in sorted(E.rglob('command-*.receipt.json')):
        d=get(path)
        receipts.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),**{k:d.get(k) for k in ('start_utc','end_utc','limit_seconds','wall_seconds','exit_code','tree_empty','pid','birth_100ns','manifest')}))
    roots=[]
    for r in b['roots']:
        result=r.get('result',{})
        roots.append(dict(id=r['id'],start_utc=r['start_utc'],elapsed=result.get('root_elapsed_seconds'),exit_code=result.get('exit_code'),
          cleanup_confirmed=result.get('cleanup',{}).get('all_confirmed'),counts_at_entry=r['counts_at_entry']))
    control=dict(budget_sha256=sha(E/'budget.json'),events_sha256=sha(E/'events.jsonl'),events_count=len(events),
      event_kinds=dict(collections.Counter(map(kind,events))),permits=permits,roots=roots,command_receipts=receipts,
      wall_components=components,recomputed_wall=sum(components.values()),recorded_wall=b['command_wall_conservative_upper_seconds'],
      holding=b['runtime_holding_union_seconds'],holding_uncertainty=b['holding_uncertainty'],
      retained_failure_entries=b['failures'],retained_TASK117_failures=b['original_TASK117_failures'],
      counts=b['counts'],caps=b['caps'],active_root=b['active_root'],active_command=b['active_command'],
      roots_over_1800=[x['id'] for x in roots if x['elapsed'] is not None and x['elapsed']>1800],
      unconfirmed_root_cleanup=[x['id'] for x in roots if not x['cleanup_confirmed']],
      controlled_commands_over_declared_limit=[r['path'] for r in receipts if r['wall_seconds'] is not None and r['limit_seconds'] is not None and r['wall_seconds']>r['limit_seconds']],
      synthetic_transport_count=sum(kind(x)=='synthetic_provider_transport' for x in events))
    save('engineering-control-reconstruction.json',control)
    race=get(E/'budget-last-slot-race.json');baseline=get(E/'budget-99-baseline.json')
    op_counts=collections.Counter(x.get('operation_id') for x in events if kind(x)=='synthetic_provider_transport')
    budget=dict(waiting_backends=race['waiting_backends'],baseline_requests=baseline['requests'],baseline_cost=baseline['cost'],
      baseline_roster=[x['requests_reserved'] for x in baseline['activities']],baseline_operations=len(baseline['operations']),
      final_requests=race['final']['requests'],final_cost=race['final']['cost'],final_operations=len(race['final']['operations']),
      outcomes=[race['model_status'],race['embedding_status']],post100=race['post100_both_providers'],
      new_operations=[dict(operation=x,synthetic_transport_calls=op_counts[x['operation_id']]) for x in race['final']['operations'] if x not in baseline['operations']],
      duplicate_synthetic_operation_ids={k:v for k,v in op_counts.items() if v>1})
    save('budget-evidence-comparison.json',budget)
    identities=[]
    targets=[E/'budget-99-baseline.json',E/'budget-last-slot-race.json']
    for directory in (E/'finalization-05',E/'continuation-06'):
        for pattern in ('ACK-*.json','permission-*-PASS.json','K2-*.json','race-*-COMMIT*.json','race-*-persistent*.json',
                        'UI-normal-GET-*.json','UI-context-root-46.json','UI-*-PASS-root-46.json','namespace-capabilities-authenticated-barrier.json',
                        'actual-frozen-DataContext-COMMIT.json','normal-*-checkpoint.json','normal-selector-activation-COMMIT.json',
                        'real-profile-ACL-and-guard-PASS.json','scope-exact-actual-ACL.json','scope-negative-*-actual-root-44.json',
                        'final-fresh-financials-separated.json','restore-target-final-financials.json',
                        'retained-original-Q-witness.json','final-protocol-currentness-witness.json','final-stop-proof-after-readonly.json'):
            targets.extend(directory.glob(pattern))
    for path in sorted(set(targets)):
        identities.append(dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=sha(path)))
    save('reviewed-raw-evidence-identities.json',identities)
    print(json.dumps(dict(permit_groups=len(permits),root_count=len(roots),receipt_count=len(receipts),
      root_entry_excesses=[(p['id'],p['root_entry_excesses']) for p in permits if p['root_entry_excesses']],
      roots_before_permit_adoption=[(p['id'],p['roots_before_adoption']) for p in permits if p['roots_before_adoption']],
      roots_over_1800=control['roots_over_1800'],unconfirmed_cleanup=control['unconfirmed_root_cleanup'],
      commands_over_limit=control['controlled_commands_over_declared_limit'],recomputed_wall=control['recomputed_wall'],
      raw_identities=len(identities),budget=budget),ensure_ascii=False))

if __name__=='__main__':main()
