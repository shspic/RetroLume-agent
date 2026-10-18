"""读取现成C04结果和关键证据，查询精确资源停止元数据；不运行产品。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,subprocess,shutil
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
C04=ROOT/'DocuN/evidence/TASK-111/execution/continuation-04'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
delivery=load(C04/'final/result-delivery-receipt.json');report=ROOT/'DocuN/results/TASK-111-result.md'
if info(report)['sha256']!=delivery['result_sha256'] or report.stat().st_size!=delivery['result_bytes']:raise RuntimeError('结果身份不符')
rows=[]
for r in load(C04/'final/source-identity.json'):
 actual=info(ROOT/r['path']);rows.append(dict(**r,actual_sha256=actual['sha256'],match=actual['sha256']==r['sha256']))
if not all(r['match'] for r in rows):raise RuntimeError('交回源漂移')
rules=[]
for r in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
 actual=info(Path(r['absolute_path']))['sha256'];rules.append(dict(path=r['absolute_path'],sha256=actual,match=actual==r['sha256']))
if not all(r['match'] for r in rules):raise RuntimeError('规则漂移')
receipt=load(C04/'final/execution-receipt.json');budget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
if budget['counts']!=receipt['counts'] or budget['active_batch'] is not None:raise RuntimeError('预算或在途改变')
normal=load(C04/'final/Native-and-normal-UI.json')
effects=load(Path(normal['normal_effects_file']))
bindings={k:dict(activity_id=v['activity_id'],artifact_id=v['receipt']['artifact_id'],normal_complete=v['normal_complete']) for k,v in normal['bindings'].items()}
checks={'normal_scope':normal['status']=='PASS_TWO_NORMAL_UI_ONLY','normal_count':len(bindings)==2 and all(v['normal_complete'] for v in bindings.values()),
        'ACK_count':normal['actual_public_input_ACKs']==21,'PNG_count':normal['PNG_samples']==43,
        'Native_count':len(normal['native_OneCall'])==2 and all(r['data']['active_processes_at_end']==0 and r['data']['state']=='settled' for r in normal['native_OneCall']),
        'final_bundle':load(C04/'final/unchanged-rules-runtime-and-front-bundle.json')}
save('received.json',dict(at=at,result=delivery,sources=rows,source_count=len(rows),rules=rules,counts=receipt['counts'],time_seconds=receipt['time_seconds'],
    normal_bindings=bindings,normal_checks=checks,normal_effects=info(Path(normal['normal_effects_file'])),
    matrix=load(C04/'final/matrix-actual.json'),race_results=load(C04/'root-14/step-09-races/race-results.json'),
    faults=load(C04/'root-14/step-10-faults/fault-results.json'),main_product_running_or_writes=0))
recorded=load(C04/'final/exact-resource-final.json')
objects=recorded.get('objects') or recorded.get('containers')
if not isinstance(objects,list):raise RuntimeError('资源对象索引缺失')
actual_rows=[]
for r in objects:
 cid=r.get('id') or r.get('cid');p=subprocess.run([shutil.which('docker'),'container','inspect',cid],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
 if p.returncode:raise RuntimeError('精确对象无法核实')
 v=json.loads(p.stdout)[0];st=v['State']
 if v['Id']!=cid or st['Running'] or st['Pid']:raise RuntimeError('归属对象仍运行或漂移')
 actual_rows.append(dict(id=v['Id'],name=v['Name'],image=v['Image'],running=st['Running'],pid=st['Pid'],status=st['Status'],restart_count=v['RestartCount']))
save('resource-recheck.json',dict(at=at,objects=actual_rows,only_registered=True,read_only=True,not_full_tree_stop_proof=True))
permissions=dict(grantee='retrolume_html_owner',columns={'pdf_review_candidates':['id','version_id','status','page_count'],'pdf_review_pages':['candidate_id'],'pdf_extracted_pages':['version_id']},
    actual_proofs=[str(C04/'root-14/step-01-qualify/qualification-patch.json'),str(C04/'root-14/step-03-pdf_missing/pdf-complete-qualification-cases.json')],
    acceptance='六列资格与相关实际路径可定向关闭DEF-029，父G11终审仍待')
save('accepted-and-pending.json',dict(DEF_027='保持已关闭',DEF_028='保持已关闭',DEF_029=permissions,
    DEF_030='真实挂起登记拒绝与ready后拒绝完整结束定向可关闭，剩余死亡恢复尚未通过',
    accepted_methods=['两Native/正常UI','memory/cancel准确缓存屏障','Node_busy','Reaper_death/fake_console限定范围'],
    pending_methods=['客户端迟到与真实bitmap释放','实际hidden/unload','活跃刷新','owner_control_lost最终原因动态','pipe_corrupt','supervisor_death','both_supervisors_death','control_path_lost','hard_deadline'],
    witness_risk='C04 Witness预持Job且finish主动Terminate；死亡与last-handle自然结束观察必须先移除/分级该干预',
    primary_source='https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects',
    old_preview25_kept_unknown=True,full_task_accepted=False))
print(json.dumps(dict(result_match=True,source_match=len(rows),rules_match=len(rules),resources_stopped=len(actual_rows),normal_checks={k:v for k,v in checks.items() if isinstance(v,bool)},counts=receipt['counts']),ensure_ascii=False))
