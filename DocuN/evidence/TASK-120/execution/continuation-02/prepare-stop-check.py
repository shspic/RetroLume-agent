"""Filesystem-only adapt original readonly collector; never executes it."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
body=(HERE.parent/'continuation-01/readonly-stop-inspection.py').read_text(encoding='utf-8-sig')
body=body.replace("*HERE.glob('command-*.receipt.json')","*(EX/'continuation-01').glob('command-*.receipt.json'),*HERE.glob('command-*.receipt.json')")
body=body.replace("for slot in ('flow','budget-01'):","for slot in ('flow','budget-01','budget-02'):")
body=body.replace("    previous='0'*64;seq=0","    if not path.exists():continue\n    previous='0'*64;seq=0")
start=body.index('proof={\'utc\'')
body=body[:start]+'''from tests.fixtures.task120 import resources as r
actual=r.owned(r.container(),budget['pg_registry'])
assert actual['Id']=='b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f'
assert actual['Image']=='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
assert actual['limits']['Memory']==536870912 and actual['limits']['NanoCpus']==1000000000 and actual['limits']['PidsLimit']==128
assert actual['limits']['RestartPolicy']['Name']=='no' and len(actual['mounts'])==1
assert actual['ports']=={'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':'55480'}]}
stopped=not problems and not any(x['same_identity_running'] for x in pids) and not any(x.get('unknown') or x.get('active_processes',0) for x in jobs) and not any(x['listening'] for x in ports.values())
complete=stopped and not actual['state']['Running'] and actual['state']['Pid']==0
proof={'utc':datetime.now(timezone.utc).isoformat(),'kind':'normal_channel_readonly_exact_stop_inspection','registered_processes':pids,'registered_jobs':jobs,'ports':ports,'metadata_read_problems':problems,'processes_jobs_ports_stopped':stopped,'docker_realtime':actual,'all_fresh_stop_dimensions_confirmed':complete,'root_count':budget['counts']['roots'],'old_command038_not_executed':not (EX/'continuation-01/command-038.receipt.json').exists()}
(HERE/'entry-stop-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
if not complete:raise RuntimeError('exact_stop_or_identity_not_confirmed')
print(json.dumps({'PID_births':len(pids),'Jobs':len(jobs),'all_fresh_stop_dimensions_confirmed':complete}))
'''
(HERE/'check-stop.py').write_text(body,encoding='utf-8')
print('Saved readonly collector; not executed.')
