"""只封装本卡最终字节与只读资源身份，不新增业务入口或恢复许可。"""
from __future__ import annotations
import ast,difflib,hashlib,json,subprocess,time
from pathlib import Path
from .control import Control,EVIDENCE,ROOT,atomic_json,freeze,utc
from .resources import OwnedDocker,port_available
from .processes import process_state

def digest(value):return hashlib.sha256(value).hexdigest()
def run():
 start=time.monotonic();control=Control()
 if control.load()['used_seconds']['metadata']==0:
  control.charge('metadata',360,{'name':'prior-readonly-control-conservative','exact':False,'unknown_retained':True,
   'scope':'首读至封装前文件/身份/端口/控制辅助的保守合并登记，既有未逐项计量不冒0；运行外壳已在其分项内收费。'})
 before=json.loads((EVIDENCE/'input-snapshot.json').read_text(encoding='utf-8'))
 final=EVIDENCE/'final';final.mkdir(exist_ok=True)
 rows=freeze(final/'post');mapping={row['path']:row for row in rows}
 for extra in ['README.md','config/activity.example.json','.gitignore']:
  path=ROOT/extra
  if path.exists():
   target=final/'post'/extra;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes());mapping[extra]={'path':extra,'sha256':digest(path.read_bytes())}
 for path in (ROOT/'frontend/dist').rglob('*'):
  if path.is_file():
   name=path.relative_to(ROOT).as_posix();mapping[name]={'path':name,'sha256':digest(path.read_bytes())}
 changed=[];protected=[];diff=[];base_paths=set()
 for row in before['product_before']:
  name=row['path'].replace('\\','/');base_paths.add(name);path=ROOT/name;pre=EVIDENCE/'pre'/name
  current=path.read_bytes() if path.exists() else None
  assert pre.is_file() and digest(pre.read_bytes())==row['sha256'],name
  post=digest(current) if current is not None else None
  value={'path':name,'pre_sha256':row['sha256'],'post_sha256':post,'pre_bytes':len(pre.read_bytes()),'post_bytes':len(current) if current is not None else None}
  if post==row['sha256']:protected.append(value)
  else:
   changed.append(value)
   diff.extend(difflib.unified_diff(pre.read_text(encoding='utf-8-sig').splitlines(True),current.decode('utf-8-sig').splitlines(True) if current is not None else [],fromfile='pre/'+name,tofile='post/'+name))
 new=[];additional=[]
 for name,row in sorted(mapping.items()):
  if name not in base_paths:
   if name=='frontend/src/pdf/THIRD_PARTY_LICENSES/pdfjs-dist-6.3.289-LICENSE.txt':
    additional.append({'path':name,'classification':'初始业务枚举未覆盖的既有版权原件，未写入，不冒新建','post_sha256':row['sha256']});continue
   new.append({'path':name,'pre_exists':False,'post_sha256':row['sha256'],'post_bytes':(ROOT/name).stat().st_size})
   diff.extend(difflib.unified_diff([], (ROOT/name).read_text(encoding='utf-8-sig').splitlines(True),fromfile='pre/absent/'+name,tofile='post/'+name))
 (final/'product.patch').write_bytes(''.join(diff).encode())
 atomic_json(final/'pre-diff-post.json',{'base_files':len(base_paths),'changed':changed,'unchanged_protected':protected,'additional_observed':additional,'new':new,
  'generated_removed_preserved_in_pre':[x for x in changed if x['post_sha256'] is None and x['path'].startswith('frontend/dist/')],
  'missing_product_sources':[x for x in changed if x['post_sha256'] is None and not x['path'].startswith('frontend/dist/')]})
 inputs=[]
 for row in [*before['contracts'],*before['rules']]:
  path=Path(row.get('absolute_path') or row.get('path'));actual=digest(path.read_bytes())
  inputs.append({'path':str(path),'expected_sha256':row['sha256'],'actual_sha256':actual,'match':actual==row['sha256']})
 inputs.append({'path':str(ROOT/'DocuN/tasks/TASK-103.md'),'expected_sha256':before['task_card_sha256'],'actual_sha256':digest((ROOT/'DocuN/tasks/TASK-103.md').read_bytes())})
 inputs[-1]['match']=inputs[-1]['actual_sha256']==inputs[-1]['expected_sha256'];assert all(x['match'] for x in inputs)
 atomic_json(final/'inputs-after.json',inputs)
 # 整文件语法/函数AST对照，未改函数可沿用原证据，但不称新运行通过。
 functions=[]
 for item in changed:
  name=item['path']
  if name.endswith('.py') and name.startswith('backend/app/'):
   def defs(path):
    source=path.read_text(encoding='utf-8-sig');tree=ast.parse(source)
    return {n.name:hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest() for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
   a=defs(EVIDENCE/'pre'/name);b=defs(ROOT/name)
   functions.append({'path':name,'unchanged_functions':sorted(k for k in a if a.get(k)==b.get(k)),'changed_or_new_functions':sorted(k for k in b if a.get(k)!=b[k]),'removed_functions':sorted(k for k in a if k not in b)})
 atomic_json(final/'function-diff.json',functions)
 # 最终dist原字节与本卡Chromium磁盘缓存的确切字节区间相比较，不输出缓存头。
 bundle=[];loaded=[];assets=list((ROOT/'frontend/dist').rglob('*'))
 for path in assets:
  if not path.is_file():continue
  body=path.read_bytes();name=path.relative_to(ROOT).as_posix();target=final/'post'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
  record={'path':name,'bytes':len(body),'sha256':digest(body)};bundle.append(record)
  if path.suffix not in ('.js','.css'):continue
  for attempt in ['02','03']:
   cache=EVIDENCE/('workspace/browser-profile-'+attempt+'/Default/Cache/Cache_Data')
   if not cache.exists():continue
   for entry in cache.iterdir():
    if not entry.is_file():continue
    data=entry.read_bytes();offset=data.find(body)
    if offset>=0:
     saved=final/('browser-loaded-'+attempt+'-'+path.name);saved.write_bytes(data[offset:offset+len(body)])
     loaded.append({**record,'attempt':attempt,'cache_file':entry.relative_to(ROOT).as_posix(),'cache_sha256':digest(data),
      'offset':offset,'length':len(body),'loaded_sha256':digest(saved.read_bytes()),'equal_final_dist':saved.read_bytes()==body})
     break
 build=json.loads((EVIDENCE/'runs/build-03-final-memory-fixes/execution.json').read_text(encoding='utf-8'))
 front=[r for r in build['before'] if r['path'].startswith('frontend/src/')]
 equal=all(digest((ROOT/r['path']).read_bytes())==r['sha256'] for r in front);assert equal
 atomic_json(final/'bundle-chain.json',{'bundle':bundle,'loaded_cache_proofs':loaded,'src_equal_build3':equal,'src_files_compared':len(front),
  'reason':'build3/as-run源hash与最终src一致；缓存区间是实际完整静态资源原字节，不保存auth或API缓存头。'})
 docker=OwnedDocker(control);resources=[]
 for resource in control.load()['resources']:
  state=docker.inspect(resource);assert state['running'] is False and state['pid']==0
  raw=json.loads(docker.cli(['container','inspect',resource['cid']]).stdout)[0];host=raw['HostConfig']
  state.update(cpus=host['NanoCpus'],memory=host['Memory'],pids_limit=host['PidsLimit'],restart=host['RestartPolicy']['Name'],privileged=host['Privileged'])
  assert state['cpus']==1000000000 and state['memory']==536870912 and state['pids_limit']==128 and state['restart']=='no' and state['privileged'] is False
  volume=json.loads(docker.cli(['volume','inspect',resource['volume']]).stdout)[0]
  labels=volume.get('Labels') or {};assert labels.get('retrolume.task')=='TASK-103' and labels.get('retrolume.permit')==control.load()['permit']
  state['volume']={'name':volume['Name'],'created_at':volume.get('CreatedAt'),'driver':volume['Driver'],'labels':labels};resources.append(state)
 witnesses=[]
 for path in (EVIDENCE/'observations').glob('*-session.json'):
  value=json.loads(path.read_text(encoding='utf-8'))['value']
  for pid_key,birth_key in [('manager_pid','manager_created_100ns'),('pid','worker_created_100ns')]:
   pid=value.get(pid_key);birth=value.get(birth_key)
   if not pid or not birth:continue
   now=process_state(pid);same=now.get('exists',False) and now.get('created_100ns')==birth
   witnesses.append({'activity_id':value['activity_id'],'pid':pid,'birth_100ns':birth,'current':now,'original_running':bool(same and now.get('running')),
    'tree_active_at_return':value.get('active_processes_at_end'),'cleanup_incomplete':value.get('cleanup_incomplete')})
 assert not any(x['original_running'] for x in witnesses)
 ports={str(port):port_available(port) for port in [55443,55444,55445,18103,18104]};assert all(ports.values())
 atomic_json(final/'resources-after.json',{'at':utc(),'containers':resources,'known_process_witnesses':witnesses,'ports_available':ports,'data_retained':True,'business_restart':False})
 observations=[]
 for path in (EVIDENCE/'observations').glob('*-sql.json'):
  value=json.loads(path.read_text(encoding='utf-8'))['value'];observations.append({'file':path.relative_to(ROOT).as_posix(),**value})
 grouped={}
 for value in observations:grouped.setdefault(value['tag'],[]).append(value)
 summary={}
 for tag,values in grouped.items():
  semantic=[v for v in values if v['sql'].lstrip().startswith(('WITH q AS','WITH a AS')) or 'SELECT b.selection_sha256' in v['sql']]
  summary[tag]={'all_execute':len(values),'data_snapshot_execute':len(semantic),'semantic_files':[x['file'] for x in semantic]}
 atomic_json(final/'sql-snapshot-evidence.json',{'counts':summary,'note':'一次业务数据SELECT；其余为BEGIN后本地超时配置与schema元数据，不冒称总SQL仅一次。新末尾守卫未PG复跑。'})
 control.charge('metadata',time.monotonic()-start,{'name':'final-package-and-readonly-resource-witnesses','exact':True})
 atomic_json(final/'budget-at-package.json',{**{k:v for k,v in control.load().items() if k!='actions'},'active_used_seconds':(time.monotonic_ns()-control.load()['start_ns'])/1e9,'metadata_prior_exact':False})
 print(json.dumps({'changed':len(changed),'new':len(new),'protected':len(protected),'bundle_cache_proofs':len(loaded),'resources_stopped':len(resources),'process_witnesses':len(witnesses)},ensure_ascii=False))
if __name__=='__main__':run()
