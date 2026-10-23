import datetime,difflib,hashlib,importlib.util,json,os,subprocess
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[4]
sha=lambda b:hashlib.sha256(b).hexdigest()
s=importlib.util.spec_from_file_location('w128',E/'win-support.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
state=json.loads((E/'checkpoint.json').read_bytes())
# 首次停止断言失败，持有上界延长到随后全部PID不存在的证据写入时刻。
first=state['api_intervals'][0]
confirmed_epoch=(E/'api-stop-diagnosis.json').stat().st_mtime
original_seconds=first['seconds']
first['parent_exit_observation_seconds']=original_seconds
first['seconds']=max(original_seconds,confirmed_epoch-first['start_epoch'])
first['stop_confirmation_basis']='api-stop-diagnosis.json filesystem write time; conservative upper bound, exact child exit time unknown'
first['stopped']=datetime.datetime.fromtimestamp(confirmed_epoch,datetime.timezone.utc).isoformat()
(E/'holding-adjustment.json').write_text(json.dumps({'original_parent_interval_seconds':original_seconds,'conservative_first_api_holding_seconds':first['seconds'],'cumulative_api_upper_bound_seconds':sum(v['seconds'] for v in state['api_intervals']),'raw_diagnosis_preserved':True},indent=2),encoding='utf-8')
(E/'checkpoint.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
pid_rows=[]
for interval in state['api_intervals']:
    for old in interval.get('processes',[]):
        try:
            ref=w.ProcessRef(old['pid']);same=ref.birth==old['birth'];alive=ref.alive()
            assert not same or not alive
            pid_rows.append({'pid':old['pid'],'expected_birth':old['birth'],'same_birth':same,'alive':alive});ref.close()
        except OSError as error:
            assert error.errno==87
            pid_rows.append({'pid':old['pid'],'expected_birth':old['birth'],'already_absent':True})
(E/'final-api-process-check.json').write_text(json.dumps(pid_rows,indent=2),encoding='utf-8')
docker=Path(os.environ['LOCALAPPDATA'])/'Programs/DockerDesktop/resources/bin/docker.exe'
env={k:os.environ[k] for k in ('SystemRoot','WINDIR','TEMP','TMP','ComSpec','USERPROFILE','APPDATA','LOCALAPPDATA') if k in os.environ}
env['PATH']=str(docker.parent)+os.pathsep+str(Path(env['SystemRoot'])/'System32')
objects={};secrets=[]
for slot,v in state['slots'].items():
    res=subprocess.run([str(docker),'inspect',v['cid']],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20);assert res.returncode==0
    raw=json.loads(res.stdout)[0];assert raw['Id']==v['cid'] and raw['Image']==v['created_projection']['image_id']
    assert not raw['State']['Running'] and raw['State']['Pid']==0
    assert raw['Mounts']==v['created_projection']['mounts']
    roots=[w.file_identity(Path(row['path'])) for row in v['roots']];assert roots==v['roots']
    for kind,identity,expected,keys in [('volume',v['volume']['Name'],v['volume'],('Name','CreatedAt','Driver','Labels')),('network',v['network_id'],v['network'],('Name','Id','Created','Driver','Labels'))]:
        check=subprocess.run([str(docker),kind,'inspect',identity],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20);assert check.returncode==0
        actual=json.loads(check.stdout)[0];assert all(actual.get(k)==expected.get(k) for k in keys)
    objects[slot]={'cid':v['cid'],'state':raw['State'],'roots':roots,'volume':v['volume']['Name'],'network_id':v['network_id'],'starts':v['starts']}
    secrets.extend(w.protect_secret((Path(v['home'])/'credentials.dpapi').read_bytes(),decrypt=True).split(b'\0'))
allowed=['deploy/normal-install.md','README.md']
changes=[];diff=[]
for name in allowed:
    before=(E/'pre'/name).read_bytes();after=(R/name).read_bytes()
    dst=E/'post'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(after)
    changes.append({'path':name,'before_sha256':sha(before),'after_sha256':sha(after),'bytes':len(after)})
    diff.extend(difflib.unified_diff(before.decode('utf-8').splitlines(True),after.decode('utf-8').splitlines(True),fromfile='pre/'+name,tofile=name))
(E/'changes.diff').write_text(''.join(diff),encoding='utf-8')
pre=json.loads((E/'pre-snapshot.json').read_bytes());post=[]
for row in pre['inputs']:
    p=Path(row['path']);changed=sha(p.read_bytes())!=row['sha256']
    assert not changed or p.relative_to(R).as_posix() in allowed,str(p)
    post.append({'path':str(p),'sha256':sha(p.read_bytes()),'changed':changed})
oldpre=json.loads((R/'DocuN/evidence/TASK-127/execution/pre-snapshot.json').read_bytes())
public=Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
assert all(sha((public/r['path']).read_bytes())==r['sha256'] for r in oldpre['rules'])
ports=w.port_owners({55482,55483,18122,18124,18126});assert not any(r['state']==2 for r in ports)
scanned=0
for directory in [E,E/'entry-07',E/'entry-08']:
    for p in directory.iterdir():
        if p.is_file():
            assert not any(v in p.read_bytes() for v in secrets),str(p)
            scanned+=1
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'objects':objects,'inputs':post,'changes':changes,'rules_unchanged':7,'ports':ports,'no_listeners':True,'secret_matches':0,'scanned_files':scanned,'entries_cumulative':state['entries'],'pg_holding_cumulative_seconds':sum(i['seconds'] for i in state['pg_intervals']),'api_starts':state['api_starts'],'api_holding_seconds':sum(v['seconds'] for v in state['api_intervals']),'Q':'FROZEN','T0':None,'provider':0,'fees_cny':0,'source_apply_replayed':False,'planned_interrupted_apply_performed':True}
(E/'post-snapshot.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'stopped':True,'inputs':len(post),'changed':sum(r['changed'] for r in post),'cumulative_pg_seconds':record['pg_holding_cumulative_seconds'],'cumulative_starts':{k:v['starts'] for k,v in state['slots'].items()},'entries':state['entries']}))
