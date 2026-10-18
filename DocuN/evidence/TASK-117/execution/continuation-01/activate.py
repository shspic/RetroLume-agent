"""只前向追加S02段，封存S01原账与成果；不启动产品或资源。"""
from pathlib import Path
import datetime as dt,hashlib,json,time,sys
HERE=Path(__file__).resolve().parent;EXEC=HERE.parent;ROOT=EXEC.parents[3]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
path=EXEC/'budget.json';raw=path.read_bytes();budget=json.loads(raw)
permit='TASK-117-STEP018-INTEGRATION-S02-20261015'
if any(x.get('permit')==permit for x in budget.get('segments',[])):raise RuntimeError('已有S02段，不能重复激活')
if budget['active_root'] is not None:raise RuntimeError('旧运行根仍在途')
result=ROOT/'DocuN/results/TASK-117-result.md'
if sha(result.read_bytes())!='db9dd539274c9b77db237410de31a6c9cc75595bae3b758d6e6c2d5573351b53':raise RuntimeError('原结果漂移')
manifest=json.loads((EXEC/'final-source-manifest.json').read_text(encoding='utf-8'))
drift=[]
for item in manifest['entries']:
    source=ROOT/item['path'];post=item['post'];exists=source.is_file()
    if exists!=post['exists'] or exists and sha(source.read_bytes())!=post['sha256']:drift.append(item['path'])
if drift:raise RuntimeError('S01源码漂移:'+repr(drift))
rules=json.loads((EXEC/'receipt.json').read_text(encoding='utf-8'))['rules']
if not all(sha(Path(x['absolute_path']).read_bytes())==x['sha256'] for x in rules):raise RuntimeError('锁定规则变化')
now=dt.datetime.now(dt.timezone.utc);mono=time.monotonic_ns()
# 首工具只采到Get-Date，未同时采mono。按本次host时钟保守回推并提前5秒，明确不是首点精确采样。
start=dt.datetime.fromisoformat('2026-10-15T02:24:05.722344+00:00')-dt.timedelta(seconds=5)
start_mono=mono-int((now-start).total_seconds()*1e9)
snapshot=HERE/'s01-frozen';snapshot.mkdir(exist_ok=False)
for name in ('budget.json','events.jsonl','case-index.json','final-source-manifest.json','final-binding.json','result-save-receipt.json'):
    (snapshot/name).write_bytes((EXEC/name).read_bytes())
(snapshot/'TASK-117-result.md').write_bytes(result.read_bytes())
for name in ('control.py','runtime_control.py','root04_http.py','root04_start.py','root05_profiles.py'):
    p=HERE/'preimages'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((EXEC/name).read_bytes())
segment={'permit':permit,'stage':'S02','start_utc':start.isoformat(),'start_mono_ns':start_mono,'clock_domain':'S02-host-restart-new-QPC','calendar_deadline_utc':(start+dt.timedelta(hours=48)).isoformat(),'activity_cap_seconds':28800,'no_expansion_after_seconds':25200,'save_only_after_seconds':27000,'save_reserve_seconds':1800,'runtime_holding_cap_seconds':10800,'offline_cap_seconds':3600,'baseline_s01_activity_seconds':37651.0027854,'baseline_s01_runtime_conservative_seconds':16219.360,'baseline_s01_runtime_actual_seconds':16216.391,'baseline_s01_offline_seconds':1724.875,'baseline_counts':dict(budget['counts']),'cumulative_caps':{**budget['caps'],'roots':9,'frontend_builds':5,'api_starts':10},'segment_caps':{'roots':5,'frontend_builds':2,'api_starts':5,'browser_starts':6,'pg_starts':17},'root_business_seconds':2100,'root_cleanup_seconds':300,'official_page_targets_added_cap':8,'official_page_targets_prior':10,'status':'active','original_budget_sha256':sha(raw)}
budget.setdefault('segments',[]).append(segment);budget['active_segment']=permit;budget['phase']='S02-先修自动清场';budget['s01_frozen_budget_sha256']=sha(raw)
write(path,budget)
receipt={'TASK':'TASK-117','R':'R-111','permit':permit,'sample':{'utc':now.isoformat(),'mono_ns':mono},'start':{'utc':start.isoformat(),'mono_ns':start_mono},'first_point_limit':'首工具未同步采mono；Get-Date后本次成对采样回推并保守前扣5秒；不冒精确首点','clock_discontinuity':'当前host mono约4e12，旧S01约1e15；不同host启动域不作跨域差值，只将封存S01秒数与S02段秒数相加','s01_77_source_entries_unchanged':True,'seven_rules_unchanged':True,'model':'Codex desktop / 系统GPT-6，具体后端子型号未披露','new_resources_started':0,'task_card_sha256':sha((ROOT/'DocuN/tasks/TASK-117.md').read_bytes()),'segment':segment}
write(HERE/'receipt.json',receipt)
with (EXEC/'events.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'kind':'S02_activated',**receipt},ensure_ascii=False)+'\n')
print(json.dumps({'activated':permit,'source_entries_verified':len(manifest['entries']),'s01_fields_preserved':True,'new_resources':0,'segment_elapsed_seconds':(mono-start_mono)/1e9}))
