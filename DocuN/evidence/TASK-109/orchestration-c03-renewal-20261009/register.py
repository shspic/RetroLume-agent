"""核证C03过期断点并登记一次续窗；不执行产品或容器启动。"""
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AREA = ROOT / "DocuN/evidence/TASK-109/orchestration-c03-renewal-20261009"
RECEIPT = ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-04"
EXEC = ROOT / "DocuN/evidence/TASK-109/execution/continuation-03"
AMENDMENT = "TASK-109-G11-C03-RESUME01-20261009"
IMAGE = "sha256:aa824fa25eb0aae09cee50c10372fb218a7d86ffb10124b46074a5c1e977cc66"
CONFIG = "sha256:e881d12c9e682de7e535386b9db353bfc95838c3bcea04332bcdffd9cc30e6ea"
CID = "5bd9e24d2a8ba06403f4daf4120aedcd7fe0ef4f0e3ae5f162b723918f189059"
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def identity(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": digest(data)}


def write_json(path, value):
    path.resolve().relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def docker_read(args):
    result = subprocess.run(["docker", *args], capture_output=True, text=True, encoding="utf-8", timeout=15, check=True)
    return result.stdout.strip()


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not RECEIPT.exists(), "不能覆盖已登记的回收证据"
assert not (AREA / "renewal-permit.json").exists(), "不能重复签发同一续窗"
report_path = ROOT / "DocuN/results/TASK-109-result.md"
report = report_path.read_bytes()
proof = read_json(EXEC / "expiry-delivery-proof.json")
assert len(report) == proof["bytes"] == 40900
assert digest(report) == proof["sha256"] == "e45a7317e3be89f3487a2a9a909a1190a8149ddc0449860067003ce06b1fe004"
old_report = (ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-03/TASK-109-C02-as-returned.md").read_bytes()
assert len(old_report) == 37685 and report.endswith(old_report)
session = read_json(EXEC / "session.json")
expiry = read_json(EXEC / "interruption-expiry-check.json")
assert session["roots"] == session["attempts"] == session["preview_creates"] == session["preview_starts"] == session["controllers"] == []
assert session["root_used"] == session["new_preview_create_start"] == 0
assert expiry["roots"] == expiry["attempts"] == expiry["new_runtime"] == 0
assert expiry["C03_window_expired"] and expiry["original_window_expired"]
assert session["original_deadline_ns"] == 795901594189000
baseline = read_json(ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-03/current-baseline.json")
assert len(baseline) == 494
assert all(digest((ROOT / rel).read_bytes()) == expected for rel, expected in baseline.items()), "已有494项冻结对象漂移"
prepared = read_json(EXEC / "prepared-source-manifest.json")
assert len(prepared) == 2
for row in prepared:
    source = Path(row["path"])
    source.resolve().relative_to(ROOT)
    actual = identity(source)
    assert actual["bytes"] == row["bytes"] and actual["sha256"] == row["sha256"]
    rel = source.relative_to(ROOT).as_posix()
    assert rel not in baseline
    baseline[rel] = actual["sha256"]
rules = read_json(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
assert len(rules) == 7
assert all(digest(Path(row["absolute_path"]).read_bytes()) == row["sha256"] for row in rules), "锁定公共规则漂移"
old_sessions = {}
for relative in ["session.json", "continuation-01/session.json", "continuation-02/session.json", "continuation-03/session.json"]:
    path = ROOT / "DocuN/evidence/TASK-109/execution" / relative
    old_sessions[path.relative_to(ROOT).as_posix()] = identity(path)
reception = read_json(EXEC / "reception.json")
for absolute, expected in reception["old_sessions"].items():
    assert digest(Path(absolute).read_bytes()) == expected
names_raw = docker_read(["ps", "-a", "--filter", "name=^retrolume-task-109-g11-preview-", "--format", "{{json .}}"])
names = [json.loads(row) for row in names_raw.splitlines() if row]
assert len(names) == 1 and names[0]["Names"] == "retrolume-task-109-g11-preview-01"
container = json.loads(docker_read(["inspect", "--format", '{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"state":{{json .State}},"restart":{{json .HostConfig.RestartPolicy}},"labels":{{json .Config.Labels}}}', CID]))
assert container["id"] == CID and container["image"] == IMAGE
assert container["state"]["Running"] is False and container["state"]["Restarting"] is False and container["state"]["Pid"] == 0
assert container["restart"]["Name"] == "no" and container["labels"]["retrolume.task"] == "TASK-109"
image = json.loads(docker_read(["image", "inspect", "--format", '{"id":{{json .Id}},"descriptor":{{json .Descriptor}},"user":{{json .Config.User}},"entrypoint":{{json .Config.Entrypoint}},"os":{{json .Os}},"architecture":{{json .Architecture}}}', IMAGE]))
assert image["id"] == image["descriptor"]["digest"] == IMAGE
assert image["descriptor"]["annotations"]["config.digest"] == CONFIG
assert image["user"] == "10001:10001" and image["entrypoint"] == ["node", "/opt/preview/h0-counter.cjs"]
assert image["os"] == "linux" and image["architecture"] == "amd64"
ps_script = r"$p=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18109,55449) } | Select-Object LocalAddress,LocalPort,OwningProcess); $r=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|pythonw|node)(\.exe)?$' -and $_.CommandLine -match 'task109|h0-run-environment|preview[\\/]reaper\.py' } | Select-Object ProcessId,Name,CreationDate); @{ports=$p;matching_processes=$r} | ConvertTo-Json -Depth 4 -Compress"
ps_result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script], capture_output=True, text=True, encoding="utf-8", timeout=25, check=True)
live = json.loads(ps_result.stdout)
assert live["ports"] == live["matching_processes"] == [], "相关监听或控制进程仍在途"

managed = ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/tasks/TASK-109.md", "DocuN/results/TASK-109-work-decision.md"]
old = {relative: (ROOT / relative).read_bytes() for relative in managed}
assert "文档 v2.27" in old[managed[0]].decode("utf-8-sig").splitlines()[2]
assert "文档 v1.05" in old[managed[1]].decode("utf-8-sig").splitlines()[2]
assert "CHG-1094" in old[managed[2]].decode("utf-8-sig")[-1500:]
RECEIPT.mkdir()
for relative, data in old.items():
    path = RECEIPT / "before" / relative
    path.resolve().relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
(RECEIPT / "TASK-109-C03-expired-as-returned.md").write_bytes(report)
write_json(RECEIPT / "current-baseline.json", baseline)
write_json(RECEIPT / "resources-readonly.json", {"at": STAMP, "container": container, "image": image, "preview_names": names, "live": live, "commands_readonly": True, "new_container_start": 0, "product_execution": 0})
receipt = {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "operator": "Codex编排Agent", "report": identity(report_path), "old37685_suffix_exact": True, "old494_match": True, "current_identity_count": len(baseline), "prepared": prepared, "old_sessions": old_sessions, "expiry_check": expiry, "C03_real_used": {"root": 0, "preview_create": 0, "preview_start": 0, "controller": 0}, "old_global_roots": 74, "old_task_roots": 4, "old_active_preparation_seconds": "未单列，不以暂停墙钟当active，也不伪写零投入", "old_C03_wall_elapsed_seconds": expiry["elapsed_C03_seconds"], "adopted": "只采纳准备与过期未运行事实，不签Browser或G11", "independent_audit": False, "main_product_runs": 0}
write_json(RECEIPT / "receipt.json", receipt)
permit = {"TASK": "TASK-109", "R": "R-103", "action_permit": "TASK-109-G11-C03-20261009", "window_amendment_permit": AMENDMENT, "issued_at": STAMP, "authority": "用户2026-10-09明确请求确认新的30分钟C03时窗，编排确认签发", "status": "待人工转交原109窗口", "activation": "原109执行者首次读入本次置顶补充卡时记录同机monotonic_ns并固定一次；不是runner启动时才起算", "effective_start_ns": None, "effective_deadline_ns": None, "window_seconds": 1800, "window_is_additional_time_authorization_not_reset": True, "expired_original_deadline_ns": 795901594189000, "expired_C03_start_ns": 785559428007000, "expired_C03_deadline_ns": 787359428007000, "historical_deadlines_preserved": True, "overrides_expired_deadline_only_for_this_C03_remaining_work": True, "execution_sidecar": (EXEC / "resume-01/session.json").as_posix(), "old_sessions": old_sessions, "old_input_identities": prepared, "seconds_for_recovery_window": {"active": 1800, "metadata": 500, "real_root": 600, "offline": 120, "cleanup": 300, "preview_each": 60, "preview_total": 120, "diagnostic_each": 15}, "old_time_and_unknowns_preserved": True, "offline_batches_remaining_max": 2, "offline_each_seconds_max": 60, "remaining_existing_C03_counts": {"root_R05": 1, "preview_create": 2, "preview_start": 2, "controller": 2}, "new_root_allowance_added": 0, "count_caps": {"task_roots": 8, "H0_roots": 5, "preview": 16, "controller": 3}, "used_counts": {"global_roots": 74, "task_roots": 4, "H0_roots": 4, "preview": 1, "controller": 1, "imagebuild": 2}, "imagebuild_cap": 2, "second_attempt_condition": "仅第一容器确认停止且完整新stderr给原白名单父目录ENOENT依据；成功或无新依据不启第二个", "image": IMAGE, "config": CONFIG, "business_frozen": True, "new_used": 0, "zero_new": ["save", "build", "load", "tag", "install", "research", "PG", "SQL", "role", "profile_model", "API_UI", "main_browser", "native_model", "provider_fee", "Git"]}
write_json(AREA / "renewal-permit.json", permit)
assignment = {"TASK": "TASK-109", "R": "R-103", "round": "C03恢复续窗01", "window_amendment_permit": AMENDMENT, "resource": "A+强推理", "window": "原109执行窗口", "dispatch": "待转交", "sent": False, "received": False, "started": False, "original_C03_received_at_utc": session["first_read_utc"], "original_C03_preparation_received": True, "renewal_used": 0, "independent107": "原隔离窗口保留，不泛审未齐业务", "TASK110": "未占号、未派发"}
write_json(AREA / "window-assignment.json", assignment)

card = f'''# TASK-109 / R-103 C03恢复续窗01 — 新30分钟时窗已确认

## 目标与交付

沿原C03完整成果继续，直接复用已保存bootstrap和控制器准备，完成获准启动环境诊断、能运行时同容器probe及精确停止。不是重新准备或构建。下方原C03七节除本次明确修订的时窗、账目和证据落点外全部有效。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md，task_model/V4.0/AGENTS CHG-0003，需求v1.1、架构v1.06、唯一执行动态v2.28、阶段07。公共源与七锁定指纹未变，同窗有效材料复用。继续原109 A+强推理窗口，登记实际模型；原107独立、110未派。用户2026-10-09明确请求新的30分钟C03时窗，编排于{STAMP}确认签发；无需再次请求时窗确认。

## 背景与最小充分上下文

C03原首读2026-10-09 10:48:17+08:00、子截止11:18:17，原总截止约13:40:44均已过。原C03真实root/create/start/controller均0，准备尚未compile/Node运行。当前report40900字节/SHA e45a7317e3be89f3487a2a9a909a1190a8149ddc0449860067003ce06b1fe004，37685字节及嵌套旧历史完整；原494项一致，两份新增准备核证后共496项。preview01仍Exited137/Pid0，preview02/03不存在，相关控制进程及18109/55449监听为空。这里只采纳断点事实，未宣告产品验证。

只补读本置顶合同、DocuN/evidence/TASK-109/orchestration-c03-renewal-20261009/renewal-permit.json和两份准备源；原合同已读段及有效证据直接继承。bootstrap输入hash de20956e3c7cdb631bdb149fee034b95ae8adcad9c07a504beb746f3fc96eeca，h0-run-environment.py输入hash 4eea4c82a1a4f1fcba7747904f6d22d4521808d3df2b38d941b413c0257b9151；路径分别deploy/preview/runtime-bootstrap.cjs和backend/tests/fixtures/task109/h0-run-environment.py。不同则先查明，不覆盖他人成果。

## 执行边界与资源

本次续窗许可{AMENDMENT}附属于原action TASK-109-G11-C03-20261009。你首次读入本置顶合同即记录monotonic_ns为effective_start_ns，effective_deadline_ns=effective_start_ns+1800000000000，一次固化。首读和准备也在新30分钟内，禁止等runner启动再起算。仅本次剩余C03工作以新有效截止取代已过期的原总截止及旧C03截止；其他旧阶段不恢复执行权。新30分钟是明确新增时间许可，所有旧时窗、投入、失败和UNKNOWN原样累计，不伪称旧active或metadata归零，也不将暂停墙钟24574.306秒冒充active。新窗到期禁止新启动，保存事实交回，不自动续窗。

原四份session.json均只读；新session在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-109/execution/continuation-03/resume-01/session.json，保留原时间键和历史摘要，另存有效起点/截止/本许可及累计账。只允许对准备控制器作必要新session/证据目录、许可核对和统一有效截止接线，留pre/diff/post/as-run。现main和call/finally仍取过期original_deadline_ns，不能直接照跑；全部执行与救援截止须一致使用新的有效硬截止，同时保持root/preview各自较早截止和清理预留。不得重写旧deadline或借此放宽独立子限。原镜像内程序、安全/协议/包/源缓存和旧controller不改；bootstrap复用，普通有据目录修正仍按原C03合同。

真实次数仍原C03未用的一根R05，预检前计；发生后TASK109为5/8、H0为5/5、global75，不是另加第六根。preview02/03最多各一次create/start，controller≤2，累计preview16/controller3保留，旧已用各1。第二个只完整新错误支持原白名单父目录ENOENT且首CID确认停；成功即在同容器完成probe，不启第二个。新时窗内metadata≤500、realroot≤600、offline≤120且最多2批各60、cleanup≤300，各preview60/诊断15，累计runtime≤120，全操作仍在1800秒内。旧准备时间和原类别账保留；这些限制只约束本次明确新增时间许可内动作，不返还旧用量。

image manifest aa824fa25eb0aae09cee50c10372fb218a7d86ffb10124b46074a5c1e977cc66/config e881d12c9e682de7e535386b9db353bfc95838c3bcea04332bcdffd9cc30e6ea复用。build2/2封存，新save/build/load/tag/install/research/Git/PG/SQL/role/profile/model/API/UI/main-browser/provider/fee均0。原UID10001、networknone、readonly、capdrop、NNP、seccomp、privateIPC、CPU1/768MiB/pids128、tmpfs128+32MiB及无bind/socket/port/secret全部保持；不禁Crashpad/sandbox，不换引擎，不复活preview01或删除原资源。

## 验证、证据与审计关系

必要时只对本轮控制接线及尚未检查的准备作原允许离线核对，不重复旧build/probe。冻结实跑源与argv，再在同一R05连续完成目录写probe/完整有界stderr、Browser可用时原counter和精确停止。执行原2秒/手势/frame辨别标准及首反证即停；无反证仍NOT_FULL_H0，不能解冻业务。未知或越权限错误不猜第二环境，明确错误层和最少缺口交回。

新原始证据仅追加到 DocuN/evidence/TASK-109/execution/continuation-03/resume-01/，旧C03目录和四session原字节保留。原failed roots与旧85.797秒真实量含27.017 build子段保留，不重复加子段。完整H0和G11未验收，当前不派泛审或声称必需审计通过。

## 停止与回传

同root内获准普通步骤连续完成；时窗/子限到达、无新因果、第二次失败、越域或首权限反证则精确停止、保留全部尝试交回。报告续写 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-109-result.md，原40900字节作为完整后缀，不改旧失败。回传实际结果、源diff/hash、窗口起止和旧新累计账、原件、精确收尾、未验证与最少下一项；不自签B01/SEC003/STEP/M-1/项目。只带回一句结论与结果绝对路径。

## 以下为原C03完整合同和更早原字节历史

'''
work = f'''# TASK-109 / R-103 C03过期断点核证与一次30分钟续窗

{STAMP}，Codex编排Agent。用户明确请求新30分钟C03，确认签发{AMENDMENT}，不再询问同一授权。核证40900字节报告/37685字节原后缀、494项旧源和2项准备共496对象、四历史session；原C03root/preview/controller均0。preview01仍Exited137/Pid0，新02/03不存在、无相关控制进程/监听。两份准备仅文本/AST事实，compile/Node/真实启动尚未运行，不签Browser或G11。

时窗从原109执行者首次读本补充卡起单调固定1800秒，明确只对剩余C03以新有效截止替代已过期总截止/C03截止；原时间键及过期墙钟24574.306秒只读保留，旧准备active未单列不编零，不把暂停墙钟当工作。新时窗内时间子限仍500/600/120/300、两preview各60/诊断15；旧投入、费用、失败、UNKNOWN累计，真实计数和资源上限不增加。

只用原未启动R05一根/最多两有依据preview02/03/两controller，发生后global75、TASK109 5/8、H0 5/5；build2/2封存、原preview/controller各1不返。新session和证据落resume-01，旧session不改；准备控制器仅允许接新有效deadline/sidecar/许可的必要差异，不覆盖历史或重准备。原image/bootstrap、所有安全边界和业务冻结继承；正式卡已经保存回读后待人工转交原A+，新窗口尚未接收/起算/真实开始，107独立，110未占未派。

本轮主控仅只读原件/hash/元数据与共享文档，产品/compile/build/container-start/业务运行0。G11-P不重新采用，完整H0/G11/STEP/M1/项目未过。下方原裁定原字节保留。

'''
state = f'''# 执行动态文档

文档 v2.28，2026-10-09，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.06、task_model/阶段07。下面v2.27及全部历史原字节保留。

## C03已返回过期断点，确认新30分钟续窗待转交

109/R103 C03实际已接收并保存两份准备，但旧总截止和旧30分钟子窗均过，真实root/create/start/controller为0；40900字节报告与37685字节旧历史完整，原494项未变加两准备共496。preview01仍停止/Pid0、新02/03不存在、相关控制进程和18109/55449无监听；未有新Browser/目录/权限/页面原件。仅准备和过期未运行事实完成核证，不标G11通过。

用户2026-10-09要求确认新30分钟C03，编排签发{AMENDMENT}并保存原TASK109置顶补充。原109 A+首次读新补充卡起单调固定1800秒，专属剩余C03的有效截止替代过期总deadline/旧C03子窗。原start/deadline/session/旧费用失败投入保留，新30分钟是明确新增时间许可，旧active未知不伪零、24574.306秒暂停墙钟不冒工作。续窗许可待人工转交，尚未接收/起算/执行。

累计root74、TASK109 4/8、H0 4/5、preview/controller各1不返；仍仅R05一根/至多两有据preview02/03/两controller，发生后global75与task5/H0到5，不追加root次数。原build2/2封存，旧真实85.797含27.017 build子段与所有FAIL/ERROR/UNKNOWN/13元/重叠时间账保持。本新时窗metadata500/realroot600/offline120最多2批60/cleanup300、preview各60/诊断15且累计120，无新研究或业务额度。

两准备复用，仅控制器新session/证据落点和有效deadline必要接线留差异；原四session只读，新证据execution/continuation-03/resume-01。image/内程序/包/seccomp/CPU-PIDs-mem/UID/readonly/networknone不改，新save/build/load/tag/install/PG/SQL/API/UI/model/provider/fee/Git0；成功同容器续probe，无依据或越域停止，NOT_FULL_H0不解冻业务。原107独立/110未占未派，G10等旧有限验收继承，无重测。

本批CHG1095—1102，下一CHG1103。核证与续窗证据 DocuN/evidence/TASK-109/orchestration-receipt-04/ 及 orchestration-c03-renewal-20261009/。用户只需把当前109置顶续窗合同交原109窗口，结果仍原路径；主控产品/测试/启动运行0。HTML/G11/完整Must/后续交付仍按原路线未签。

## 以下为v2.27及更早历史

'''
arch = '''# 架构动态文档

文档 v1.06，2026-10-09，Asia/Shanghai。需求v1.1、唯一执行动态v2.28。只同步C03已保存准备和续窗事实，架构、资源及信任边界没有新变更；下面v1.05及原历史保字节。

## 有界启动诊断准备未运行，恢复时窗已确认

两份runtime-bootstrap/环境控制准备已核身份，旧494对象未改；旧总期和C03期过后未启动root或容器，Browser/目录权限与导航证据仍缺。新的30分钟仅许可原C03剩余动作，旧时间键和投入原样保留，不恢复其他已完结runner；控制接线需将历史截止与新有效截止明确分开并单次固化。

当前镜像和安全边界复用，禁止禁Crashpad/sandbox、换引擎或扩大权限；准备不等于动态通过，业务仍冻结，完整H0/G11仍未验收。若Browser就绪在同容器完成原探针与收尾，不把启动和网页另拆任务。新许可待人工转交，真实新运行仍0。

## 以下为v1.05及更早历史

'''
prefixes = {"DocuN/tasks/TASK-109.md": card, "DocuN/results/TASK-109-work-decision.md": work, "DocuS/执行动态文档.MD": state, "DocuS/架构动态文档.MD": arch}
for relative, prefix in prefixes.items():
    assert "*" not in prefix and "|" not in prefix
    assert (ROOT / relative).read_bytes() == old[relative]
    (ROOT / relative).write_bytes(prefix.encode("utf-8") + old[relative])
entries = [
    (1095, "DocuN/evidence/TASK-109/orchestration-receipt-04/receipt.json", "核证C03准备、过期未运行、四历史session及496对象；原失败和计数不返。"),
    (1096, "DocuN/results/TASK-109-work-decision.md", "明确确认一次30分钟恢复时窗，只覆盖剩余C03；旧时窗、投入和业务冻结保留。"),
    (1097, "DocuS/架构动态文档.MD", "v1.06同步准备未运行和续窗，不改变架构权限、不签Browser或G11。"),
    (1098, "DocuS/执行动态文档.MD", "v2.28登记旧C03已返回、续窗待转交、新使用0及原次数保留。"),
    (1099, "DocuN/tasks/TASK-109.md", "置顶C03恢复续窗01，原七节和所有历史完整保留；复用准备及必要有效截止接线。"),
    (1100, "DocuN/evidence/TASK-109/orchestration-c03-renewal-20261009/renewal-permit.json", "新1800秒明确时间许可与旧累计账分开，root/preview/controller次数不新增。"),
    (1101, "DocuN/evidence/TASK-109/orchestration-c03-renewal-20261009/window-assignment.json", "原109 A+待人工转交，107仍独立，110未派，新窗口未起算。"),
    (1102, "DocuN/evidence/TASK-109/orchestration-c03-renewal-20261009/delivery-proof.json", "一次静态文档回读核对路径、续窗、原后缀、冻结指纹及资源状态，主控产品运行0。"),
]
addition = "\n" + "\n\n".join(f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{relative}。{reason}" for number, relative, reason in entries) + "\n"
assert "*" not in addition
assert (ROOT / "DocuS/文档变更记录.MD").read_bytes() == old["DocuS/文档变更记录.MD"]
(ROOT / "DocuS/文档变更记录.MD").write_bytes(old["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))

checks = {}
for relative, prefix in prefixes.items():
    data = (ROOT / relative).read_bytes()
    assert data == prefix.encode("utf-8") + old[relative]
    checks[relative] = {"identity": identity(ROOT / relative), "old_suffix_exact": True, "new_prefix_bytes": len(prefix.encode("utf-8")), "new_prefix_no_asterisk_or_table": True}
assert (ROOT / "DocuS/文档变更记录.MD").read_bytes().startswith(old["DocuS/文档变更记录.MD"])
assert report_path.read_bytes() == report
assert all(digest((ROOT / rel).read_bytes()) == expected for rel, expected in baseline.items())
assert all(identity(ROOT / rel) == expected for rel, expected in old_sessions.items())
assert AMENDMENT in (ROOT / "DocuN/tasks/TASK-109.md").read_text(encoding="utf-8")[:8000]
delivery = {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "window_amendment_permit": AMENDMENT, "checks": checks, "change_ledger": identity(ROOT / "DocuS/文档变更记录.MD"), "report_unmodified": identity(report_path), "prepared_and_old496_unchanged": True, "four_sessions_unmodified": True, "old_failed_counters_and_deadlines_preserved": True, "new_used": 0, "dispatched": False, "product_code_modified_by_main": 0, "compile_test_build_container_model_runs_by_main": 0, "readback": "通过一次文件与文档一致性检查，不是产品行为验收"}
write_json(AREA / "delivery-proof.json", delivery)
print(json.dumps({"registered": True, "at": STAMP, "card": str(ROOT / "DocuN/tasks/TASK-109.md"), "amendment": AMENDMENT, "new_window_seconds": 1800, "counters_unchanged": True, "old496_unchanged": True, "versions": {"state": "2.28", "architecture": "1.06", "last_CHG": "1102"}, "main_product_runs": 0}, ensure_ascii=False))
