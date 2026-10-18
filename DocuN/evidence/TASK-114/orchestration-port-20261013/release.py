"""登记用户释放端口后的检查和同许可接续；不启动source或修改执行账。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
STATE = ROOT / 'DocuS/执行动态文档.MD'
WORK = ROOT / 'DocuN/results/TASK-114-work-decision.md'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'
at = datetime.now(timezone(timedelta(hours=8))).isoformat()
old = {path: path.read_bytes() for path in (STATE, WORK, CHANGES)}
assert '文档v2.49' in old[STATE].decode('utf-8-sig').splitlines()[2]
assert 'CHG-1321' in old[CHANGES].decode('utf-8-sig')
assert 'CHG-1322' not in old[CHANGES].decode('utf-8-sig')
backup = OUT / 'before-release-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items():
    (backup / path.name).write_bytes(raw)

checked = {
    'observed_at': '2026-10-13T11:28:04.0729593+08:00',
    'user_action': '用户明确回复已停，本机Get-Service gdpsvc确认Stopped',
    'tcp_port': 55461, 'all_tcp_states_found': 0,
    'exclusive_ipv4_loopback_bind_succeeded': True,
    'probe_disposed_immediately': True, 'persistent_network_change': False,
    'available_memory_gib': 4.22, 'minimum_memory_gib': 2, 'memory_gate_met': True,
    'source': {'cid': '2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22', 'name': 'retrolume-task-114-data-source', 'running': False, 'pid': 0, 'image': 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f', 'volume': 'retrolume-task-114-data-source-data', 'host_ip': '127.0.0.1', 'host_port': 55461, 'job_label': 'f934ac64-4dce-4f8c-8442-15b283f2d48d', 'profile_label': 'TASK-114-PG17'},
    'main_started_source': False,
    'permission': '现行TASK114/R108/C01许可及剩余预算内恢复原source依赖路径；无新资源或预算',
    'does_not_prove_pg_restore_or_business_passed': True,
}
(OUT / 'release-checked.json').write_text(json.dumps(checked,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
notice = '''# TASK114续作01端口释放后接续通知

主控2026-10-13T11:28:04+08:00复核：gdpsvc已Stopped，55461所有TCP状态无占用，临时独占IPv4 loopback绑定成功并立即释放；可用内存4.22GiB达到原2GiB门。原source CID/image/卷/label/127.0.0.1:55461未变，当前仍Stopped/Pid0。

原TASK114工程窗口可在现行C01许可和真实累计余额内继续source依赖工作。先核当前内存/身份/端口、resume活动段与真实根/pg_start计数，再有界启动原CID一次确认；成功后按完整合同连续完成剩余验证及普通修正，保失败与原件。不重建/换端口/删旧包/重seed，不重置尝试、持有、工时或slot。

若端口再次被占或身份/资格未知，准确收尾并报告，不循环重试或停项目外服务。主控没有启动数据库、修改服务/网络或接管产品执行。此前10013环境阻塞已解除，不等于真实PG/HTTP/业务验证通过。
'''
(OUT / 'resume-notice.md').write_text(notice,encoding='utf-8')
work_prefix = f'''# TASK114续作01端口已释放（当前有效环境事实）

{at}登记。用户回复已停；11:28:04实核gdpsvc Stopped、55461全TCP无占、临时独占IPv4 bind成功并Dispose，可用内存4.22GiB≥原2GiB门。原source CID/image/卷/label/55461不变，source仍Stopped/Pid0。先前项目外广联达绑定造成的source环境阻塞已解除。

原窗口按现行C01累计预算/根/启动计数复核并有界启动原source，继续剩余真实验证；不另发新卡或加额度，不重建/改port/seed/抹失败。采样不替代实际启动前核对，也不签业务通过。主控仅元数据和临时bind，不操作产品/服务；可转交通知在DocuN/evidence/TASK-114/orchestration-port-20261013/resume-notice.md。

## 以下为原端口阻塞及许可历史原字节

'''
WORK.write_bytes(work_prefix.replace('\n','\r\n').encode('utf-8')+old[WORK])
state_prefix = f'''# 执行动态文档

文档v2.50，2026-10-13，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.26、task_model/07，架构方案不变。以下v2.49历史原字节保留。

## TASK114续作01的source环境阻塞已解除，继续原窗口

{at}登记。用户回复已停，11:28:04主控实查gdpsvc Stopped、55461无所有TCP状态记录、临时独占IPv4 loopback bind成功且立即释放；可用内存4.22GiB达到原2GiB门。原source CID2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22、cf134a76…镜像、source-data卷、标签和127.0.0.1:55461不变，仍Stopped/Pid0。

原C01工程窗口可以按现行许可和剩余累计额度恢复source依赖操作，先实时身份/内存/端口/活动段与根/启动计数核对，第一次启动有界确认后连续完成剩余矩阵。无需新预算/技术采用/新卡，不重建/换端口/seed，不停项目外进程/改网络，不清旧失败/工时/持有/slot。通知和检查在DocuN/evidence/TASK-114/orchestration-port-20261013/resume-notice.md、release-checked.json。

此前10013环境阻塞关闭；产品实施/目标恢复/竞态/HTTP/UI的真实结果仍在途待统一回传。服务由用户停止，主控无持久系统改变/数据库启动或产品测试，临时bind检查不是业务通过。TASK115仍待完整稳定后隔离集中独审；原G11/25/UNKNOWN/费用/全部历史保留。CHG1322—1325，下一1326。

## 以下为v2.49及更早历史

'''
STATE.write_bytes(state_prefix.replace('\n','\r\n').encode('utf-8')+old[STATE])
entries=[
    (1322,'DocuN/evidence/TASK-114/orchestration-port-20261013/release-checked.json；resume-notice.md','用户停服务后真实检查/同C01原source接续通知，不冒业务已过。'),
    (1323,'DocuN/results/TASK-114-work-decision.md','环境阻塞解除、原窗口/计数/预算与准确source不变。'),
    (1324,'DocuS/执行动态文档.MD','v2.50在途工程恢复source依赖，未签产品/资源额外许可。'),
    (1325,'DocuN/evidence/TASK-114/orchestration-port-20261013/release-delivery-proof.json','共享历史保留及保存复读；无产品启动/持久系统改动。'),
]
addition=''.join(f'\r\n- CHG-{n}，{at}，Codex编排Agent，{path}。{why}\r\n' for n,path,why in entries)
CHANGES.write_bytes(old[CHANGES]+addition.encode('utf-8'))
assert WORK.read_bytes().endswith(old[WORK]) and STATE.read_bytes().endswith(old[STATE])
assert CHANGES.read_bytes().startswith(old[CHANGES])
proof={'at':at,'TASK':'TASK-114','continuation':'01','check':checked,'shared_history_byte_exact':True,'products_modified_or_started':0,'execution_receipt_written':False,'service_changed_by_main':False,'CHG':[1322,1325],'next_CHG':1326}
(OUT / 'release-delivery-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'端口释放检查通过，原C01接续','state':'v2.50','notice':str(OUT/'resume-notice.md'),'main_source_start':False},ensure_ascii=False))
