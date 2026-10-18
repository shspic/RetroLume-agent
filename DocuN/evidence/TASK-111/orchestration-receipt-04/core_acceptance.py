"""读取现成核心证据的身份、数值、PNG与收据，非运行验证。"""
from pathlib import Path
import json,hashlib,math
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
CORE=ROOT/'DocuN/evidence/TASK-111/execution/continuation-03/root-10/step-08-probe'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(b):return hashlib.sha256(b).hexdigest()
value=load(CORE/'phase-a-result.json')
wrapper=value['stop_proof'];proof=wrapper['proof'];facts=load(Path(value['runtime_folder'])/'kernel-premises.json')
checks={
 'status':value['status']=='PASS_REAL_RUNTIME_CORE',
 'not_claimed_main_UI':value['Native_or_main_UI_chain'] is False,
 'final_stopped':value['final']['state']=='stopped' and value['final']['reserved_seconds']==0,
 'confirmed_wrapper':wrapper['confirmed'] is True,
 'proof_kind':proof['tree_confirmation']=='private_pid_init_terminated',
 'image_binding':proof['image_id']==value['image_id'],
 'kernel_binding':proof['kernel_premises_sha256']==sha(canonical(facts).encode()),
 'attach_EOF':proof['attach_eof_confirmed'] is True,
 'owned_reaper_ended':proof['owned_reaper_ended'] is True,
 'reaper_zero':proof['reaper_windows_job']['ActiveProcesses']==0,
 'host_zero':proof['supervisor_cli_windows_job']['ActiveProcesses']==0,
 'stopped_after':proof['after']['state']['Running'] is False and proof['after']['state']['Pid']==0,
 'wait':proof['wait']['code']==0,
 'load_binding':facts['load_manifest_sha256']==value['load_manifest_sha256'],
}
dies=[json.loads(s) for s in proof['events']['stdout'].splitlines() if s.strip()]
checks['die_identity']=any(e['Action']=='die' and e['Actor']['ID']==proof['cid'] for e in dies)
for index,r in enumerate(value['remote_acks']):
 a=r['ack'];checks['ack_'+str(index)]=a['accepted'] is True and math.isclose(float(a['readouts'][0]['value']),r['oracle'],rel_tol=0,abs_tol=1e-9) and a['preview_id']==value['preview_id']
for index,r in enumerate(value['pngs']):
 b=(CORE/r['path']).read_bytes();h=r['head'];checks['png_'+str(index)]=sha(b)==r['sha256']==h['body_sha256'] and len(b)==h['body_bytes'] and h['preview_id']==value['preview_id'] and h['channel_nonce']==proof['nonce']
output=dict(checks=checks,all_pass=all(checks.values()),image=value['image_id'],load=value['load_manifest_sha256'],CID=proof['cid'],
            evidence_scope='机械能核心及当次完整停止；不是Native/主UI或整个G11',
            DEF_027='定向修复/验证可关闭，父G11独立终审仍待',
            source='现成文件核读，新产品运行0')
(OUT/'core-acceptance.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(output,ensure_ascii=False))
