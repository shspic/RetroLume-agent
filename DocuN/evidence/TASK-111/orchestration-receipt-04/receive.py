"""编排核对现成文件和精确已停对象；不运行产品或SQL。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib,json,subprocess,shutil
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
C03=ROOT/'DocuN/evidence/TASK-111/execution/continuation-03'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
returned=load(C03/'final/result-delivery-receipt.json')
report=ROOT/'DocuN/results/TASK-111-result.md'
if sha(report)!=returned['sha256'] or report.stat().st_size!=returned['bytes']:raise RuntimeError('交回结果身份不符')
sources=[]
for r in load(C03/'final/source-identity.json'):
    actual=sha(ROOT/r['path']);sources.append(dict(**r,actual_sha256=actual,match=actual==r['sha256']))
if not all(r['match'] for r in sources):raise RuntimeError('交回源码漂移')
receipt=load(C03/'final/execution-receipt.json')
budget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
if budget['counts']!=receipt['final_used'] or budget['active_batch'] is not None:raise RuntimeError('账目或在途不符')
core=load(C03/'root-10/step-08-probe/phase-a-result.json')
proof=core['stop_proof'];pngs=core['pngs'];png_checks=[]
for r in pngs:
    if isinstance(r,dict):
        raw=r.get('path') or r.get('file')
        if raw:
            p=Path(raw);p=p if p.is_absolute() else C03/'root-10/step-08-probe'/p
            if p.is_file():png_checks.append(dict(path=str(p),sha256=sha(p),declared=r.get('sha256'),match=r.get('sha256') is None or sha(p)==r['sha256']))
rules=[]
for r in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    actual=sha(Path(r['absolute_path']));rules.append(dict(path=r['absolute_path'],sha256=actual,match=actual==r['sha256']))
if not all(r['match'] for r in rules):raise RuntimeError('锁定规则漂移')
data=dict(at=at,result=returned,sources=sources,rules=rules,source_count=len(sources),
    counts=receipt['final_used'],time_seconds=receipt['final_seconds'],active_batch=None,
    core=dict(status=core['status'],image_id=core['image_id'],load_manifest_sha256=core['load_manifest_sha256'],
              Native_or_main_UI_chain=core.get('Native_or_main_UI_chain'),
              preview_id=core['preview_id'],remote_acks=core['remote_acks'],pngs=pngs,png_file_checks=png_checks,
              proof_kind=proof.get('tree_confirmation'),proof_CID=proof.get('cid'),
              proof_image=proof.get('image_id'),attach_eof=proof.get('attach_eof_confirmed'),
              reaper_job=proof.get('reaper_windows_job'),supervisor_job=proof.get('supervisor_cli_windows_job'),
              kernel_premises_sha256=proof.get('kernel_premises_sha256'),final=core['final']),
    main_product_execution=0,main_product_writes=0)
save('returned-and-core-check.json',data)
oldresources=load(C03/'final-exact-resource-check.json')['objects']
objects=[]
for r in oldresources:
    p=subprocess.run([shutil.which('docker'),'container','inspect',r['id']],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode:raise RuntimeError('精确资源无法核实')
    v=json.loads(p.stdout)[0];s=v['State']
    if v['Id']!=r['id'] or v['Image']!=r['image'] or s['Running'] or s['Pid']:raise RuntimeError('资源漂移或仍运行')
    objects.append(dict(id=v['Id'],name=v['Name'],image=v['Image'],running=s['Running'],pid=s['Pid'],status=s['Status'],restart_count=v['RestartCount'],started=s['StartedAt'],finished=s['FinishedAt']))
save('resource-recheck.json',dict(at=at,objects=objects,read_only=True,not_a_full_stop_proof=True))
unknown=receipt['unknown_CID']
# 读取Docker已保存的本对象日志，仅作为现成原件检索；不exec/start或补造运行样本。
p=subprocess.run([shutil.which('docker'),'container','logs',unknown],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
(OUT/'unknown-log.stdout.bin').write_bytes(p.stdout)
(OUT/'unknown-log.stderr.bin').write_bytes(p.stderr)
packets=[];position=0;parse_error=None
try:
    while position<len(p.stdout):
        if len(p.stdout)-position<4:raise ValueError('short_header')
        n=int.from_bytes(p.stdout[position:position+4],'big');position+=4
        if not 1<=n<=2048 or len(p.stdout)-position<n:raise ValueError('header_limit')
        h=json.loads(p.stdout[position:position+n]);position+=n;m=h['body_bytes']
        if not 1<=m<=524288 or len(p.stdout)-position<m:raise ValueError('body_limit')
        b=p.stdout[position:position+m];position+=m
        if hashlib.sha256(b).hexdigest()!=h['body_sha256']:raise ValueError('body_hash')
        if h['type']!='frame':
            body=json.loads(b);packets.append(dict(type=h['type'],preview_id=h['preview_id'],generation=h['generation'],
               body_sha256=h['body_sha256'],reason_code=body.get('reason_code'),has_processes=isinstance(body.get('processes'),dict)))
except Exception as error:parse_error=type(error).__name__+':'+str(error)[:80]
save('unknown-existing-log-check.json',dict(cid=unknown,returncode=p.returncode,stdout_bytes=len(p.stdout),stderr_bytes=len(p.stderr),
    stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),packets=packets,parse_error=parse_error,
    recovery_kernel_premises_available=any(r['has_processes'] for r in packets),scope='只读取已有日志，空日志不证明未执行/停止'))
print(json.dumps(dict(result_match=True,source_matches=len(sources),rules_matches=len(rules),resource_stopped=len(objects),
    core_status=core['status'],image_id=core['image_id'],proof_kind=proof.get('tree_confirmation'),
    log_bytes=len(p.stdout),kernel_in_log=any(r['has_processes'] for r in packets),counts=receipt['final_used']),ensure_ascii=False))
