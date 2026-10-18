"""本次候选的具体字节、继承范围及只读资源收尾；不运行业务或旧许可。"""
from __future__ import annotations
import ast,difflib,hashlib,json,re,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from .control import Control,ROOT,EVIDENCE,atomic_json,freeze
from .resources import OwnedDocker,port_available
from ..processes import process_state

def sha(body):return hashlib.sha256(body).hexdigest()

def qualified_functions(body):
 text=body.decode('utf-8-sig');lines=text.splitlines(keepends=True);result={}
 def walk(nodes,prefix=()):
  for node in nodes:
   if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
    name=prefix+(node.name,)
    if not isinstance(node,ast.ClassDef):
     first=min([node.lineno,*[d.lineno for d in node.decorator_list]])
     result['.'.join(name)]=sha(''.join(lines[first-1:node.end_lineno]).encode())
    walk(node.body,name)
 walk(ast.parse(text).body);return result

class MetadataDocker(OwnedDocker):
 def cli(self,args,env=None,allowed=30,check=True):
  result=subprocess.run(['docker',*args],env=env,capture_output=True,timeout=self.control.remaining('metadata',allowed),creationflags=subprocess.CREATE_NO_WINDOW)
  if check and result.returncode:raise RuntimeError('最终自有资源只读核失败 '+str(result.returncode))
  return result

def run():
 control=Control();start=time.monotonic();out=EVIDENCE/'final';out.mkdir(exist_ok=True)
 try:
  control.remaining('metadata',180)
  original=(EVIDENCE/'original-result.md').read_bytes();assert len(original)==24351 and sha(original)=='b62695f7da2b3b5c65553f7a7ec5f87a979c7029c3e2b33ed5ee9cb06fe21b13'
  base=json.loads((EVIDENCE.parent/'continuation-01-input.json').read_text('utf-8'))['current_files']
  final=freeze(out/'post');by_path={x['path']:x for x in final};changed=[];deleted=[];unchanged=[];functions=[];patch=[]
  for name,expected in base.items():
   pre=(EVIDENCE/'pre'/name).read_bytes();assert sha(pre)==expected
   if name not in by_path:deleted.append({'path':name,'pre_sha256':expected,'pre_bytes':len(pre)});continue
   if by_path[name]['sha256']==expected:unchanged.append(name);continue
   post=(ROOT/name).read_bytes();changed.append({'path':name,'pre_sha256':expected,'post_sha256':sha(post),'pre_bytes':len(pre),'post_bytes':len(post)})
   if name.endswith('.py'):
    left=qualified_functions(pre);right=qualified_functions(post)
    functions.append({'path':name,'unchanged_functions':[n for n in sorted(left.keys()&right.keys()) if left[n]==right[n]],
     'changed_or_new_functions':[n for n in sorted(right) if left.get(n)!=right[n]],'removed_functions':sorted(left.keys()-right.keys()),
     'before':left,'after':right,'meaning':'限定名函数字节辅助，不把依赖/常量改动冒整文件不变'})
   if not name.startswith('frontend/dist/'):
    patch.extend(difflib.unified_diff(pre.decode('utf-8-sig').splitlines(True),post.decode('utf-8-sig').splitlines(True),fromfile='pre/'+name,tofile='post/'+name))
  added=[r for r in final if r['path'] not in base]
  diff={'baseline_existing_files':len(base),'baseline_verified':True,'final_files':len(final),'changed':changed,'added':added,'deleted':deleted,
   'unchanged':unchanged,'historical_deleted_before_c01':'原已有2个删除资产只引用原pre/final，不重标成本轮删除'}
  atomic_json(out/'pre-diff-post.json',diff);atomic_json(out/'function-diff.json',functions);(out/'product.patch').write_bytes(''.join(patch).encode())
  protected=[n for n in base if n.startswith(('backend/app/worker/','backend/native/')) or (n.startswith('backend/migrations/') and not n.endswith('010_learning_memory.sql'))]
  assert all(n in unchanged for n in protected)
  atomic_json(out/'protected-files.json',[by_path[n] for n in protected])
  rules=[]
  for row in json.loads((EVIDENCE/'rules-contracts.json').read_text('utf-8')):
   actual=sha(Path(row['path']).read_bytes());assert actual==row['sha256'];rules.append({**row,'actual':actual,'match':True})
  atomic_json(out/'rules-contracts-final.json',rules)
  runs=[]
  for folder in sorted((EVIDENCE/'runs').iterdir()):
   if not folder.is_dir():continue
   execution=json.loads((folder/'execution.json').read_text('utf-8'));actual_rows=json.loads((folder/'as-run/identities.json').read_text('utf-8'))
   mismatches=[]
   for row in actual_rows:
    p=folder/'as-run'/row['path'];assert p.is_file() and sha(p.read_bytes())==row['sha256']
    if row['path'].startswith(('backend/app/','backend/migrations/','frontend/src/')) and by_path.get(row['path'],{}).get('sha256')!=row['sha256']:mismatches.append(row['path'])
   runs.append({'name':folder.name,'execution_path':str(folder/'execution.json'),'execution_sha256':sha((folder/'execution.json').read_bytes()),
    'exit_code':execution['exit_code'],'passed':execution['passed'],'elapsed_seconds':execution['elapsed_seconds'],
    'bytes_unchanged_during_run':execution['bytes_unchanged'],'as_run_files':len(actual_rows),'source_mismatches_to_final':mismatches,
    'argv':execution['argv'],'cwd':execution['cwd'],'allowed_seconds':execution['allowed_seconds']})
  atomic_json(out/'runs-ledger.json',{'runs':runs,'preflight_import_failure':str(EVIDENCE/'offline-03-preflight-import-failure.json'),
   'previous_runs_immutable':str(EVIDENCE.parent/'final/runs-ledger.json'),'previous_runs_sha256':sha((EVIDENCE.parent/'final/runs-ledger.json').read_bytes())})
  build=EVIDENCE/'runs/build-01-final-ui/as-run';assert build.is_dir()
  frontend=[]
  for name,row in by_path.items():
   if name.startswith('frontend/src/'):
    actual=sha((build/name).read_bytes());assert actual==row['sha256'];frontend.append({'path':name,'source_sha256':actual,'match':True})
  loaded=[]
  for browser in ['browser-01','browser-02','browser-03']:
   result=json.loads((EVIDENCE/browser/'result.json').read_text('utf-8'))
   for row in result['loaded']:
    name=Path(row['path']).name;product=ROOT/'frontend/dist/assets'/name;captured=EVIDENCE/browser/name
    assert product.read_bytes()==captured.read_bytes() and sha(captured.read_bytes())==row['sha256'] and len(captured.read_bytes())==row['bytes']
    loaded.append({**row,'browser':browser,'complete_bytes_match':True})
  atomic_json(out/'bundle-chain.json',{'frontend_source_count':len(frontend),'source_matches_build':frontend,
   'build_execution':str(EVIDENCE/'runs/build-01-final-ui/execution.json'),'dist':[r for r in final if r['path'].startswith('frontend/dist/')],
   'loaded':loaded,'browser_status':{b:json.loads((EVIDENCE/b/'result.json').read_text('utf-8'))['status'] for b in ['browser-01','browser-02','browser-03']}})
  repository=ast.parse((ROOT/'backend/app/memory/repository.py').read_text('utf-8'))
  fingerprints=next(ast.literal_eval(n.value) for n in repository.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='FUNCTION_FINGERPRINTS' for x in n.targets))
  migration=(ROOT/'backend/migrations/010_learning_memory.sql').read_text('utf-8')
  sql_source={m.group(1):sha(re.sub(r'\s+','',m.group(2)).encode()) for m in re.finditer(r'CREATE FUNCTION public\.(\w+)\(.*?\bAS \$f\$(.*?)\$f\$;',migration,re.S)}
  assert sql_source==fingerprints
  sql_proofs=[]
  for label,file in [('pg1','pg1-final-catalog.json'),('pg3','pg3-catalog-after.json')]:
   catalog=json.loads((EVIDENCE/'sql'/file).read_text('utf-8'));actual={r[0]:sha(re.sub(r'\s+','',r[2]).encode()) for r in catalog['functions'] if r[0] in fingerprints}
   assert actual==fingerprints;sql_proofs.append({'slot':label,'catalog':str(EVIDENCE/'sql'/file),'catalog_sha256':sha((EVIDENCE/'sql'/file).read_bytes()),'all_12_match':True,'fingerprints':actual})
  pg2=json.loads((EVIDENCE/'sql/pg2-final-row-summary.json').read_text('utf-8'))
  old_pg2=json.loads((EVIDENCE.parent/'upgrade-old-before.json').read_text('utf-8'))
  from ..migration_cleanup import digest
  assert pg2['rows_sha256']==digest(old_pg2) and len(pg2['tables'])==14 and sum(pg2['tables'].values())==32
  atomic_json(out/'sql-chain.json',{'migration_sha256':sha(migration.encode()),'source_fingerprints':fingerprints,'actual_catalogs':sql_proofs,
   'pg2_original_14_tables_32_rows_match':True,'pg2_row_summary':pg2,'forward_proofs':[str(EVIDENCE/'sql'/(p+'-forward-proof.json')) for p in ['pg1','pg3']],
   'full_table_acl_inheritance':'原root16实际权限证据及未改010权限DDL继承；本轮三函数ACL/owner/search_path/volatility真实前后核。最终catalog含函数ACL和角色，不冒本轮重新测全部表ACL。'})
  cfg=[]
  for p in sorted((EVIDENCE/'workspace').glob('*-config.json')):
   cfg.append({'path':str(p),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size,'non_secret_value':json.loads(p.read_text('utf-8'))})
  atomic_json(out/'runtime-configs.json',{'synthetic_only':True,'configurations':cfg,'session_config':{'window_seconds':20,'request_timeout_seconds':2,'stop_grace_seconds':2,
   'startup_limit_seconds':5,'manager_db_timeout_seconds':5,'cleanup_seconds':5,'mutex_wait_seconds':3,'manager_overhead_seconds':30,
   'manager_total_seconds':50,'single_host_single_session_recovery':False,'actual_sup_lease_seconds':20},'credentials':'只在获准根RAM/子进程Env，不落盘或argv'})
  if '--sources-only' in sys.argv:
   proof=out/'resources-after.json';authority={'entry','container_start','listener_start','sup','browser','driver','container_create','volume_create'}
   proof_time=datetime.fromtimestamp(proof.stat().st_mtime,timezone.utc)
   later=[a for a in control.load()['actions'] if a['kind'] in authority and datetime.fromisoformat(a['at'])>proof_time];assert not later
   atomic_json(out/'resource-proof-reuse.json',{'resources_after_sha256':sha(proof.read_bytes()),'no_resource_launch_actions_since':True,
    'scope':'只追加离线ASGI异常映射与字节封装，已有资源收尾证明复用，不重复47份PID／三实例／端口检查','counts':control.load()['counts']})
   print(json.dumps({'final_files':len(final),'changed':len(changed),'added':len(added),'deleted':len(deleted),'runs':len(runs),
    'bundle_match':True,'sql_12_match':True,'pg2_original_rows_match':True,'resource_proof_reused':True},ensure_ascii=False));return 0
  docker=MetadataDocker(control);containers=[]
  for resource in control.load()['resources']:
   raw=json.loads(docker.cli(['container','inspect',resource['cid']]).stdout)[0];w=docker.inspect(resource)
   assert not w['running'] and w['pid']==0
   host=raw['HostConfig'];assert host['NanoCpus']==1000000000 and host['Memory']==536870912 and host['PidsLimit']==128 and host['RestartPolicy']['Name']=='no'
   containers.append({**w,'limits':{'nanocpus':host['NanoCpus'],'memory':host['Memory'],'pids':host['PidsLimit'],'restart':host['RestartPolicy']['Name']},'old_permit_label':raw['Config']['Labels']['retrolume.permit'],'port_bindings':host['PortBindings']})
  ports={str(p):port_available(p) for p in [18103,18104,55443,55444,55445]};assert all(ports.values())
  processes=[];seen=set()
  for file in (EVIDENCE/'observations').glob('*.json'):
   record=json.loads(file.read_text('utf-8'));v=record['value'];candidates=[]
   if record['kind']=='sup':candidates=[(v['pid'],v['created_100ns'])]
   if record['kind']=='session':candidates=[(v.get('manager_pid'),v.get('manager_created_100ns')),(v.get('pid'),v.get('worker_created_100ns'))]
   for pid,birth in candidates:
    if not pid or not birth or (pid,birth) in seen:continue
    seen.add((pid,birth));actual=process_state(pid);same=actual.get('created_100ns')==birth
    assert not(actual.get('running') and same)
    processes.append({'pid':pid,'expected_created_100ns':birth,'actual':actual,'original_identity_running':False,'evidence':str(file)})
  for file in EVIDENCE.glob('browser-*-root-result.json'):
   report=json.loads(file.read_text('utf-8'));w=report.get('server_witness')
   if w:
    actual=process_state(w['pid']);assert not(actual.get('running') and actual.get('created_100ns')==w['created_100ns'])
    processes.append({'server':w,'actual':actual,'original_identity_running':False,'evidence':str(file)})
  pattern=str(EVIDENCE/'workspace/browser-profile-').replace("'","''")
  command="$p=Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(chrome|chromium|node|python|pythonw)\\.exe$' -and ($_.CommandLine -like '*"+pattern+"*' -or ($_.CommandLine -like '*tests.fixtures.task103.c01.*' -and $_.CommandLine -notlike '*tests.fixtures.task103.c01.package*')) }; @($p | ForEach-Object { [pscustomobject]@{pid=$_.ProcessId;name=$_.Name;created=$_.CreationDate.ToUniversalTime().ToString('o')} }) | ConvertTo-Json -Compress"
  response=subprocess.run(['powershell.exe','-NoProfile','-Command',command],capture_output=True,timeout=control.remaining('metadata',30),creationflags=subprocess.CREATE_NO_WINDOW);assert response.returncode==0
  raw=response.stdout.decode('utf-8-sig').strip();lingering=json.loads(raw) if raw else [];assert not lingering
  atomic_json(out/'resources-after.json',{'containers':containers,'ports_released':ports,'known_pid_births':processes,'exact_fixture_or_browser_profile_processes':lingering,
   'data_and_volumes_preserved':True,'stopped_other_resources':False,'old_resources_after':str(EVIDENCE.parent/'final/resources-after.json')})
  print(json.dumps({'final_files':len(final),'changed':len(changed),'added':len(added),'deleted':len(deleted),'runs':len(runs),
   'bundle_match':True,'sql_12_match':True,'pg2_original_rows_match':True,'known_pid_births':len(processes),'resources_stopped':True},ensure_ascii=False))
 finally:control.charge('metadata',time.monotonic()-start,{'name':'c01-final-byte-and-resource-package','kind':'measured'})
 return 0
if __name__=='__main__':sys.exit(run())
