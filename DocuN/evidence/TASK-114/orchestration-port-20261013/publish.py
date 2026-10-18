"""保存当前端口阻塞事实和共享状态；不改系统服务、产品或执行账。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
STATE = ROOT / 'DocuS/执行动态文档.MD'
WORK = ROOT / 'DocuN/results/TASK-114-work-decision.md'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'


def info(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


at = datetime.now(timezone(timedelta(hours=8))).isoformat()
old = {path: path.read_bytes() for path in (STATE, WORK, CHANGES)}
assert '文档v2.48' in old[STATE].decode('utf-8-sig').splitlines()[2]
assert 'CHG-1317' in old[CHANGES].decode('utf-8-sig') and 'CHG-1318' not in old[CHANGES].decode('utf-8-sig')
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items():
    (backup / path.name).write_bytes(raw)
receipt = ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json'
receipt_before = info(receipt)

diagnosis = f'''# TASK114续作01 source端口阻塞事实

{at}，Codex编排Agent。用户截图说明原114窗口已实际继续，source 127.0.0.1:55461绑定报WinError10013；本轮对系统和容器元数据及端口作检查，没有停止服务、改变防火墙/排除范围、Docker启动或产品执行。

## 已观察事实

- netsh interface ipv4/ipv6 show excludedportrange protocol=tcp均未列出覆盖55461的排除区间；不据错误码假称系统保留。
- Get-NetTCPConnection -LocalPort 55461显示LocalAddress=0.0.0.0、RemotePort=0、State=Bound、OwningProcess=7912。只筛Listen会漏此记录。
- 临时IPv4 TCP Socket ExclusiveAddressUse绑定Loopback:55461复现NativeErrorCode10013，2026-10-13T11:12:04.3195014+08:00；finally立即Dispose，无持久端口或设置改变。
- PID7912为gdphost.exe，创建于2026-09-30，父PID6328为gdpsvc.exe；父对应服务gdpsvc，Running/Auto，PathName为C:/Program Files (x86)/Common Files/Glodon Shared/GDP/4.0.0.123/x86/gdpsvc.exe。来源为本机CIM，不根据文件名猜软件或解密私配。
- source CID2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22仍Running=false/Pid0，原image/卷/127.0.0.1:55461不变。当前task namespace只见source、target04、target05均exited；不是停止证明或完整目标验收。
- current receipt此刻counts为real_roots12、PG create/success3、start12、Windows1、build2，累计次数只是账观察，不签合规/业务通过。主控不修改该执行账。

## 裁定与最小操作

source当前端口由项目外广联达后台进程绑定，是可证的当前占用事实；未监听不等于空闲。10013可由其他应用独占绑定产生，微软说明：https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2 。不据此推断该进程的所有网络策略或恶意性。

本任务仅授权准确停止自有工作，主控未获停广联达软件/服务的对应许可，不自行kill PID7912/父服务，也不重启HNS/Winnat/Docker或清Windows端口排除。若用户当前不使用广联达，先保存退出其软件，再在services.msc临时停止gdpsvc；后续可以启动恢复，启动类型不改。服务正在被使用则先保留，需另决定连接安排，不能执行Agent自行改原CID/卷/端口。

服务释放后由主控或原执行窗口先重查所有TCP状态、临时bind并立即释放、内存及准确source身份；真正通过才在现行C01计数/预算内一次启动原source。未知/仍失败不反复重试，继续不依赖source的独立目标和HTTP工作。现行许可允许所有自有资源准确停妥且外部等待有UTC/mono/原因/断点时暂停活动工时；真实资源持有永远不暂停，不能清零失败或宣source已验证。

无需新技术采用、预算或另派任务；当前TASK114在途，TASK115仍待稳定，不以截图代验收。
'''
(OUT / 'port-conflict.md').write_text(diagnosis, encoding='utf-8')
work_prefix = f'''# TASK114续作01端口阻塞处理（当前附加事实）

{at}。原114窗口已实际接续，source依赖路径现被55461端口占用阻塞。主控查全部TCP状态，0.0.0.0:55461为Bound，owner PID7912 gdphost.exe、父gdpsvc服务，路径指向广联达Glodon Shared；IPv4/IPv6排除范围未涵盖该口，临时bind复现10013后立即释放。source/当前target04/05均Stopped，原CID/卷/端口不改，主控未动执行账或系统服务。

证据在DocuN/evidence/TASK-114/orchestration-port-20261013/port-conflict.md。项目外广联达服务不属于准确自有停止授权，不自行kill或改系统网络。用户当前不使用时保存退出后可临时停止gdpsvc，再核全TCP状态/bind/内存/身份，确认释放才在C01原额度内重试一次source；未释放继续独立target/HTTP并据真实外部等待暂停活动段，不清真实持有/失败/计数。当前实现/真实成果尚在途，不重出卡或提前审计。

## 以下为原续作许可历史原字节

'''
WORK.write_bytes(work_prefix.replace('\n', '\r\n').encode('utf-8') + old[WORK])
state_prefix = f'''# 执行动态文档

文档v2.49，2026-10-13，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.26、task_model/07。以下v2.48历史原字节保留；本次为执行环境事实，架构方案不变。

## TASK114续作01已实际接续，source端口占用待处理

{at}。用户提供执行窗口实际继续截图，C01调度由待转交更新为实际接收/执行中；当前source依赖操作blocked，原窗口继续独立目标/HTTP，尚无新统一完成结果可验收。current执行账观察roots12/18、PG create/success3、start12/32、Windows1、build2，主控不改该账、不凭此签额度或方法全部合规。

主控实查0.0.0.0:55461为Bound，PID7912 gdphost.exe，父6328 gdpsvc.exe/服务gdpsvc，路径C:/Program Files (x86)/Common Files/Glodon Shared/GDP/4.0.0.123/x86/gdpsvc.exe。IPv4/IPv6端口排除未涵盖55461；11:12:04临时独占bind复现10013后立即释放。只查监听漏Bound是本次环境判据不足，不能说无监听便可用。

原source CID2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22仍Stopped/Pid0/原55461与卷不变；当前source/target04/05都exited。广联达服务是项目外工作，未获对应停线许可，不自行kill/停服务/网络重置或换CID。用户闲置广联达时可保存退出、临时停止gdpsvc后复核端口再通知原执行窗口。现行C01外部等待可在全部自有资源准确停妥/无消费者/断点与暂停记录齐备时暂停活动工时，持有与旧失败/费用账不暂停/清零。

此次不追加预算/容器或技术包，不重出实施卡，不派TASK115。原有效验证、G11关闭、旧25/unknown/R60/13元/626.566/所有历史保留；永久只读切片和剩余Must仍原约束。主控仅作元数据/临时bind诊断与共享记录，产品运行0、系统持久改动0。

证据与最小处理在DocuN/evidence/TASK-114/orchestration-port-20261013/port-conflict.md，旧共享原字节同目录before-documents；CHG1318—1321，下一1322。

## 以下为v2.48及更早历史

'''
STATE.write_bytes(state_prefix.replace('\n', '\r\n').encode('utf-8') + old[STATE])
entries = [
    (1318, 'DocuN/evidence/TASK-114/orchestration-port-20261013/port-conflict.md', '全TCP Bound/10013/广联达服务路径及精确原资源事实，未改系统。'),
    (1319, 'DocuN/results/TASK-114-work-decision.md', '在途source依赖阻塞/项目外服务权限/释放后有界原source复核与当前续作许可关系。'),
    (1320, 'DocuS/执行动态文档.MD', 'v2.49真实调度已接续，环境端口阻塞及等待条件，不伪签业务验收。'),
    (1321, 'DocuN/evidence/TASK-114/orchestration-port-20261013/delivery-proof.json', '共享旧字节/执行账保护与保存证据，无系统服务或产品执行。'),
]
addition = ''.join(f'\r\n- CHG-{n}，{at}，Codex编排Agent，{path}。{note}\r\n' for n, path, note in entries)
CHANGES.write_bytes(old[CHANGES] + addition.encode('utf-8'))
assert STATE.read_bytes().endswith(old[STATE]) and WORK.read_bytes().endswith(old[WORK])
assert CHANGES.read_bytes().startswith(old[CHANGES])
receipt_after = info(receipt)
# 执行窗口可能继续独立操作，记录前后实际身份，不因其合法更新声称主控改账。
proof = {'at': at, 'TASK': 'TASK-114', 'continuation': '01', 'facts': str(OUT / 'port-conflict.md'), 'shared_history_preserved': True, 'receipt_identity_before': receipt_before, 'receipt_identity_after': receipt_after, 'receipt_written_by_main': False, 'system_services_stopped_by_main': 0, 'persistent_network_changes': 0, 'temporary_bind_probes': 1, 'product_runs': 0, 'CHG': [1318,1321], 'next_CHG': 1322}
(OUT / 'delivery-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'state': 'v2.49', 'diagnosis_saved': str(OUT / 'port-conflict.md'), 'blocked_port_owner': 'gdphost.exe / gdpsvc (Glodon Shared)', 'service_stopped': False, 'network_changed': False, 'product_runs': 0},ensure_ascii=False))
