"""Read-only exact07 Docker/port probe; never prints Docker Env."""
from pathlib import Path
import json,socket,subprocess
HERE=Path(__file__).resolve().parent
ids=['b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f','4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332']
p=subprocess.run(['docker','container','inspect',*ids],capture_output=True,timeout=20)
if p.returncode:raise RuntimeError('exact_docker_readonly_probe_failed_'+str(p.returncode))
rows=json.loads(p.stdout);safe=[]
for item in rows:
    safe.append({'Id':item['Id'],'Name':item['Name'],'Image':item['Image'],'labels':item['Config']['Labels'],
      'Running':item['State']['Running'],'Pid':item['State']['Pid'],'ports':item['HostConfig']['PortBindings'],
      'limits':{k:item['HostConfig'][k] for k in ('Memory','NanoCpus','PidsLimit','RestartPolicy')},
      'mounts':[{k:m.get(k) for k in ('Type','Name','Destination')} for m in item['Mounts']]})
assert [x['Id'] for x in safe]==ids and all(not x['Running'] and x['Pid']==0 for x in safe)
ports=[]
for port in (55480,55481,18120):
    with socket.socket() as s:s.settimeout(.3);ports.append({'port':port,'listening':s.connect_ex(('127.0.0.1',port))==0})
assert not any(x['listening'] for x in ports)
value={'status':'PASS','objects':safe,'ports':ports,'read_only':True}
(HERE/'resource-readonly-probe-PASS.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
print(json.dumps(value))
