"""编排只读断点核对并保存C03精确资源与预算；不导入产品。"""
from pathlib import Path
import datetime, hashlib, json, shutil, subprocess

ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
OLD=ROOT/'DocuN/evidence/TASK-111/orchestration-review-03/review-evidence.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,v):(OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
old=read(OLD)
rows=[dict(path=r['path'],expected=r['sha256'],actual=digest(Path(r['path']))) for r in old['returned_sources']]
if any(r['expected']!=r['actual'] for r in rows):raise RuntimeError('冻结源发生未说明变化')
rules=[]
for r in read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    rules.append(dict(path=r['absolute_path'],expected=r['sha256'],actual=digest(Path(r['absolute_path']))))
if any(r['expected']!=r['actual'] for r in rules):raise RuntimeError('规则漂移')
if digest(ROOT/'DocuN/results/TASK-111-result.md')!=old['report']['sha256']:raise RuntimeError('111结果改变')
budget=read(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
if budget.get('active_batch') is not None:raise RuntimeError('真实批仍在途')
objects=[]
for ref in ('1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51',
            'retrolume-task-111-g11-preview-03','retrolume-task-111-g11-preview-14'):
    p=subprocess.run([shutil.which('docker'),'container','inspect',ref],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode:raise RuntimeError('精确资源无法核实 '+ref)
    item=json.loads(p.stdout)[0]
    row=dict(id=item['Id'],name=item['Name'],image=item['Image'],running=item['State']['Running'],pid=item['State']['Pid'],restart_count=item['RestartCount'])
    if row['running'] or row['pid']:raise RuntimeError('归属对象仍在运行 '+ref)
    objects.append(row)
write('input-and-resource-check.json',dict(at=at,source_count=len(rows),sources=rows,rules=rules,
    result_sha256=digest(ROOT/'DocuN/results/TASK-111-result.md'),result_bytes=(ROOT/'DocuN/results/TASK-111-result.md').stat().st_size,
    review_sha256=digest(ROOT/'DocuN/results/TASK-111-root-cause-review.md'),objects=objects,active_batch=None,
    scope='只读文件和精确Docker元数据，没有SQL/启动/产品运行'))
caps=dict(budget['continuation_caps'])
caps.update(real_batches=14,image_builds=7,PG_container_starts=10,API_listener_starts=7,main_browser_starts=6,
            model_synthetic_requests=10,Windows_OneCall_sessions=10,frontend_typecheck_build_batches=5,
            preview_creates=34,preview_starts=32)
caps.pop('preview_reaper_validation_batches',None)
new=dict(TASK='TASK-111',R='R-105',permit='TASK-111-G11-C03-20261011',at=at,
         authorization='用户要求完成根因复盘后继续编排已采用G11-P110；主控在同范围签具体合成工程许可',
         first_read_integrated_window_seconds=28800,prior_authorized_overall_seconds=64800,new_authorized_overall_seconds=93600,
         new_real_limit_seconds=7200,cumulative_real_limit_seconds=14400,
         prior_used=budget['counts'],prior_time_seconds=budget['time_seconds'],cumulative_caps=caps,
         per_real_root_seconds=1800,cleanup_reserved_seconds=600,cleanup_cumulative_limit_seconds=1800,
         reaper_group_batches='本C03记录项；逐preview物理安全和真实根/总时间硬门保持',
         offline_batch_count='记录项，无独立中途停线门',
         preview_new_names=[f'retrolume-task-111-g11-preview-{n:02d}' for n in range(15,45)],
         preview_added_available=30,planned_baseline_ceiling=22,related_repair_reserve=8,
         PG_containers=1,PG_volumes=1,preview_simultaneous=1,real_provider_cost=0,
         no_previous_failure_refunded=True,old_C02_deadline_historical_only=True,new_execution_started=False)
if caps['preview_creates']-budget['counts']['preview_creates']!=len(new['preview_new_names']):raise RuntimeError('create预算映射错误')
if caps['preview_starts']-budget['counts']['preview_starts']!=len(new['preview_new_names']):raise RuntimeError('start预算映射错误')
if new['planned_baseline_ceiling']+new['related_repair_reserve']!=new['preview_added_available']:raise RuntimeError('基线余量错误')
write('continuation-budget.json',new)
write('window-assignment.json',dict(TASK='TASK-111',R='R-105',resource='A+，用户最强且胜任该工程的执行Agent',
    arrangement='全新工程会话，原111实现窗口停止写入',reason='原窗口多轮旧许可/上下文混杂，本轮使用单份有效合同恢复',
    independent_auditor=False,automatic_dispatch=False,status='拟登记，尚未保存任务卡或转交',
    expected_result=str(ROOT/'DocuN/results/TASK-111-result.md')))
print(json.dumps(dict(source_match=len(rows),rules_match=len(rules),resources_stopped=len(objects),
    current_counts=budget['counts'],new_cumulative_caps=caps,new_permit=new['permit']),ensure_ascii=False))
