"""核证C03返回并登记完整诊断收口合同；不执行产品实现或验证。"""
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AREA = ROOT / "DocuN/evidence/TASK-109/orchestration-continuation-04-20261009"
RECEIPT = ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-05"
EXEC = ROOT / "DocuN/evidence/TASK-109/execution/continuation-03/resume-01"
ACTION = "TASK-109-G11-C04-20261009"
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()
IMAGE = "sha256:aa824fa25eb0aae09cee50c10372fb218a7d86ffb10124b46074a5c1e977cc66"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def identity(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": sha(data)}


def save_json(path, value):
    path.resolve().relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def docker_read(args):
    result = subprocess.run(["docker", *args], capture_output=True, encoding="utf-8", text=True, timeout=15, check=True)
    return result.stdout.strip()


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not RECEIPT.exists() and not (AREA / "verification-budget.json").exists(), "不覆盖旧回收或重复签发"
result_path = ROOT / "DocuN/results/TASK-109-result.md"
result_bytes = result_path.read_bytes()
delivery = read_json(EXEC / "delivery-proof.json")
assert len(result_bytes) == delivery["result"]["bytes"] == 52303
assert sha(result_bytes) == delivery["result"]["sha256"] == "485dc033390ba08a98989bafc2e3a6cdf6feb1a9b0b970d950d702af7ab04580"
prior_report = (ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-04/TASK-109-C03-expired-as-returned.md").read_bytes()
assert len(prior_report) == 40900 and result_bytes.endswith(prior_report)
baseline = read_json(ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-04/current-baseline.json")
differences = []
for relative, expected in baseline.items():
    actual = sha((ROOT / relative).read_bytes())
    if actual != expected:
        differences.append({"path": relative, "pre": expected, "post": actual})
assert differences == [{"path": "backend/tests/fixtures/task109/h0-run-environment.py", "pre": "4eea4c82a1a4f1fcba7747904f6d22d4521808d3df2b38d941b413c0257b9151", "post": "72eddbbefe0d31da625ad970180bef7484ec63f60b521ecb2e605502c506152a"}]
baseline[differences[0]["path"]] = differences[0]["post"]
assert len(baseline) == 496
manifest = read_json(EXEC / "as-run-source-manifest.json")
assert all(identity(Path(row["path"])) == row for row in manifest["files"])
old_sessions = {row["path"]: row["sha256"] for row in delivery["old_sessions"]}
old_sessions[(EXEC / "session.json").as_posix()] = sha((EXEC / "session.json").read_bytes())
assert all(sha(Path(path).read_bytes()) == expected for path, expected in old_sessions.items())
session = read_json(EXEC / "session.json")
assert session["task_roots"] == 5 and session["global_roots"] == 75
assert len(session["roots"]) == len(session["attempts"]) == len(session["preview_creates"]) == len(session["controllers"]) == 1
assert session["roots"][0]["state"] == "ERROR" and session["roots"][0]["elapsed_seconds"] == 13.219
observations = read_json(EXEC / "root-05/attempt-01/observations.json")
directories = [row["data"] for row in observations if row["kind"] == "runtime_directory"]
assert len(directories) == 6 and all(row["uid"] == row["gid"] == 10001 and row["write_probe"]["exclusive_success"] for row in directories)
terminal = next(row for row in observations if row["kind"] == "terminal")
assert "Browser.getBrowserCommandLine" in terminal["data"]["message"] and "--enable-automation not set" in terminal["data"]["message"]
capture = read_json(EXEC / "root-05/attempt-01/stderr-capture.json")
assert capture["total_bytes_seen"] == 6811 and capture["prefix_truncated"] is False
stderr = (EXEC / "root-05/attempt-01/container-stderr.log").read_bytes()
assert len(stderr) == 6811 and b"chrome_crashpad_handler: --database is required" not in stderr
cleanup = read_json(EXEC / "root-05/attempt-01/cleanup.json")
assert cleanup["docker_stopped"] and cleanup["attach_exit"] == 137 and cleanup["protocol_thread_closed"] and cleanup["stderr_thread_closed"]
current_containers = []
for cid in ["5bd9e24d2a8ba06403f4daf4120aedcd7fe0ef4f0e3ae5f162b723918f189059", "0a449f648fc66020b937cdefa2f2cea4cc6ad305d42a9275cc96a76e77a4ccd0"]:
    data = json.loads(docker_read(["inspect", "--format", '{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"state":{{json .State}},"labels":{{json .Config.Labels}}}', cid]))
    assert data["id"] == cid and data["image"] == IMAGE and data["labels"]["retrolume.task"] == "TASK-109"
    assert not data["state"]["Running"] and not data["state"]["Restarting"] and data["state"]["Pid"] == 0
    current_containers.append(data)
names = docker_read(["ps", "-a", "--filter", "name=^retrolume-task-109-g11-preview-", "--format", "{{.Names}}"])
assert set(names.splitlines()) == {"retrolume-task-109-g11-preview-01", "retrolume-task-109-g11-preview-02"}
ps_script = r"$p=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18109,55449) } | Select-Object LocalAddress,LocalPort,OwningProcess); $r=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|pythonw|node)(\.exe)?$' -and $_.CommandLine -match 'task109|h0-run-environment|preview[\\/]reaper\.py' } | Select-Object ProcessId,Name,CreationDate); @{ports=$p;matching_processes=$r} | ConvertTo-Json -Depth 4 -Compress"
live = json.loads(subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script], capture_output=True, encoding="utf-8", text=True, timeout=25, check=True).stdout)
assert live["ports"] == live["matching_processes"] == []
rules = read_json(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
assert all(sha(Path(row["absolute_path"]).read_bytes()) == row["sha256"] for row in rules)
paths = ["DocuN/tasks/TASK-109.md", "DocuN/results/TASK-109-work-decision.md", "DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD"]
old = {relative: (ROOT / relative).read_bytes() for relative in paths}
assert "文档 v2.28" in old[paths[2]].decode("utf-8-sig").splitlines()[2]
assert "文档 v1.06" in old[paths[3]].decode("utf-8-sig").splitlines()[2]
assert "CHG-1102" in old[paths[4]].decode("utf-8-sig")[-1000:]
RECEIPT.mkdir()
for relative, data in old.items():
    target = RECEIPT / "before" / relative
    target.resolve().relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
(RECEIPT / "TASK-109-C03-resume01-as-returned.md").write_bytes(result_bytes)
save_json(RECEIPT / "current-baseline.json", baseline)
save_json(RECEIPT / "resources-readonly.json", {"at": STAMP, "containers": current_containers, "names": names.splitlines(), "live": live, "read_only": True})
source_paths = ["deploy/preview/host.cjs", "deploy/preview/runtime-bootstrap.cjs", "deploy/preview/wrapper.html", "deploy/preview/Dockerfile", "backend/tests/fixtures/task109/h0-counter.cjs", "backend/tests/fixtures/task109/h0-run-environment.py", "backend/app/preview/contracts.py", "backend/app/preview/supervisor.py", "backend/app/preview/reaper.py"]
source_ids = [identity(ROOT / relative) for relative in source_paths]
receipt = {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "result": identity(result_path), "old40900_suffix_exact": True, "current496_identities": True, "expected_only_control_wiring_difference": differences, "old_sessions": old_sessions, "source_inputs": source_ids, "directory_write_subfact": "六目录UID/GID/mode与实际独占写42字节成立", "browser_connection_subfact": "调用顺序与远端getBrowserCommandLine错误共同支持Browser及浏览器级CDP已建立；实际版本值未落盘", "blocked_by": terminal["data"]["message"], "no_new_directory_retry_basis": True, "current_original_root": "H0-R05 ERROR原样保留", "counters": {"global_roots": 75, "task_roots": 5, "H0_roots": 5, "imagebuild": 2, "preview": 2, "controllers": 2}, "real_seconds_cumulative": 99.016, "real_seconds_build_subpart": 27.017, "new_active_upper_seconds": 1092.0, "new_metadata_reserved_upper_seconds": 500, "new_offline_seconds": 0.281, "new_cleanup_upper_seconds": 30, "legacy_zero_session_keys_not_used_as_current_counters": True, "physical_namespace_termination": "推断待审，不签直接cgroup空", "main_product_runs": 0, "adopted": "只接受启动环境/连接及精确停止子事实，G11仍未验收"}
save_json(RECEIPT / "receipt.json", receipt)
save_json(AREA / "continuation-input.json", {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "baseline": (RECEIPT / "current-baseline.json").as_posix(), "sources": source_ids, "report": identity(result_path), "original_C03_delivery": (EXEC / "delivery-proof.json").as_posix(), "previous_successful_build_command": (ROOT / "DocuN/evidence/TASK-109/execution/continuation-01/root-03/build-command.json").as_posix(), "official_api_source": "https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/browser_protocol.json", "official_api_scope": "getBrowserCommandLine声明依赖启动命令行中的enable-automation；与本次真实错误相符，不能当当前实际Browser版本证明", "old_source_and_history_unchanged": True})
budget = {"TASK": "TASK-109", "R": "R-103", "action_permit": ACTION, "parent_permit": "TASK-109-G11-20261009", "authority": "已批准G11执行范围内的普通诊断兼容修正和编排子额明确修订", "window_seconds": 5400, "start_policy": "原109执行者首次读本C04合同即记录同机monotonic_ns并一次固定，不等runner启动再起算", "old_deadlines_retained_as_history": True, "effective_start_ns": None, "effective_deadline_ns": None, "seconds": {"metadata": 900, "offline": 600, "build_each": 300, "build_total": 600, "real_roots_total": 1800, "root_each": 900, "preview_each": 60, "preview_total": 120, "diagnostic_each": 15, "cleanup_total": 600}, "limits": {"new_roots": 2, "new_imagebuilds": 2, "new_preview_create_start": 2, "new_controllers": 2, "offline_batches": 3}, "used": receipt["counters"], "cumulative_caps": {"task_roots": 8, "H0_roots": 7, "imagebuilds": 4, "preview_create_start": 16, "controllers": 4}, "root_ordinals": [{"id": "H0-R06", "global": 76}, {"id": "H0-R07", "global": 77}], "budget_revision_explicit": "H0子限5到7；imagebuild子限2到4且旧2/2封存不返；controller子限3到4；原总root8/preview16不变", "second_root": "只因首轮原始错误支持本卡普通代码/观测/启动元数据修正；第一资源确认停止、源码有新修正、还有预算才启用；成功或真实权限反证不重跑", "business_frozen": True, "zero_new": ["image_save", "install", "new_engine", "research_by_worker", "PG", "SQL", "role", "profile_model", "API_UI", "main_browser", "provider_fee", "Git", "user_data_delete"], "old_failures_fees_and_time_not_reset": True, "new_used": 0}
save_json(AREA / "verification-budget.json", budget)
save_json(AREA / "window-assignment.json", {"TASK": "TASK-109", "R": "R-103", "round": "C04完整诊断收口", "resource": "A+强推理", "window": "原109执行窗口", "dispatch": "待转交", "received": False, "started": False, "new_used": 0, "original107": "保持隔离", "TASK110": "未占未派"})

card = f'''# TASK-109 / R-103 续作04 — 元数据兼容与整条关口诊断收口

## 目标与交付

继续原109执行窗口，合并完成启动元数据兼容、后续接口及观察器前置核对、原真实关口probe和精确收尾。有依据的普通诊断代码修正在本卡内连续完成，不再只交启动子事实。本次终点是完整、可裁定的诊断结果；当前诊断器没有生产同步NavigationGate，即使无反证仍NOT_FULL_H0，业务继续冻结。

正常出口为准确版本/真实argv/浏览器自身sandbox证据与有效正对照、原限制场景和停止原件；关键异常出口为真实权限反证或明确环境不足、完整因果和唯一最小后续差异。不得为结束任务伪造通过，也不能把未经修正的普通API前置错误包装成安全方案失败。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md，task_model/V4.0/AGENTS CHG-0003，需求v1.1、架构v1.07、唯一执行动态v2.29、阶段07。公共根与七锁定指纹沿原卡；同窗未变材料复用。A+强推理，继续原109窗口，如实登记实际模型，不派子Agent或接管编排。原107保持独立，110未占未派。

原G11-P已获用户采用。本次是该已授权执行范围内的普通诊断兼容与编排子额明确修订，不改变Must/主要模型/页面权限或费用。许可{ACTION}，原75入口不是75PASS、原R01—05及全部FAIL/ERROR/UNKNOWN/旧13元保持。C03实际目录与Browser/CDP连接成立；根R05 ERROR不改色，未保存实际版本值、不签sandbox或导航。

## 背景与最小充分上下文

本次真实错误是Browser.getBrowserCommandLine要求enable-automation，但固定host启动未明确满足。官方协议[原始定义](https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/browser_protocol.json)也声明该前置；仅机制依据，不替代当前版本实证。此前卡面只授目录修正造成普通兼容交回，本轮明确覆盖整条诊断的普通前置，不能再按每个API拆转。

唯一推荐修正是在deploy/preview/host.cjs的既有chromium.launch中显式加入标准启动参数--enable-automation，保留headless/实际executable/chromiumSandbox:true/原popup-blocking配置；真实Browser.getVersion先独立emit，再取真实getBrowserCommandLine并记录采集来源与实际参数。原固定版本、UID及禁no-sandbox检查保留，不改变version()或CDP返回值，不截取有利flags。必须说明该标准启动配置对观察的影响，重新取得浏览器自身sandbox原件，不能用加标志替代安全证明。不引入proc复杂兼容器、私有CDP改写或通用exec。

按最少顺序补读本置顶合同、DocuN/results/TASK-109-work-decision.md本轮段、DocuN/evidence/TASK-109/orchestration-continuation-04-20261009/continuation-input.json及verification-budget.json、host全文、backend/tests/fixtures/task109/h0-counter.cjs全文、wrapper和必要controller/协议直接依赖。只围绕从launch到最后probe的真实调用查前置、字段结构、观察器就绪、可信手势/目标frame与超时；不重读整仓或做新官方研究。C01成功构建命令、OCI链/111文件包、C03目录组合与完整stderr直接复用。

当前报告52303字节/SHA 485dc033390ba08a98989bafc2e3a6cdf6feb1a9b0b970d950d702af7ab04580，40900及更早嵌套历史完整。基线496对象仅C03控制接线已变为72eddbbefe0d31da625ad970180bef7484ec63f60b521ecb2e605502c506152a，余项吻合；本轮输入清单给准确host/counter/其他hash。runtime-bootstrap.cjs仍de20956e3c7cdb631bdb149fee034b95ae8adcad9c07a504beb746f3fc96eeca，原目录初始化和stderr配置复用，不重做原因研究。

## 执行边界与资源

允许host元数据启动配置/分阶段emit的最小修正，counter和新Python控制fixture中确由源码或原始错误支持的纯采集、schema、观察器就绪/目标frame引用及有界超时修正；场景、真实手势、2秒观察、判断标准与首反证即停不删不弱化。wrapper、包/binary/seccomp、业务源和全部既有持久模型不改，不添加生产守卫或新引擎。既有h0-root/C01/C02/C03 controller与全部旧sessions/as-run/context/cache只读；新控制器可在backend/tests/fixtures/task109/新增h0-final.py，新构建context仅deploy/preview/task109-c04-context/。

本卡明确允许最多2次本地增量build/load和各自新tag retrolume-task-109-g11-h0:c04-01、c04-02；旧build2/2封存不返，累计build子限2到4。只用原已成功OCI context及同一c091 manifest，沿原build-command.json实际命令、desktop-linux/networknone/pullfalse/本地输入/metadata映射；不save/export/拉取/安装，不改builder/daemon/store，不覆盖旧context、tag或image。新context仅复制既有依赖与本轮修正source，更新输入清单；build后绑定新manifest/config/源码/同一binary/实际标签，不能把新image写成旧aa824。旧镜像与两个停止容器保留。

首次读卡即单调固化新有效5400秒窗口，原全部起点/截止和投入原样保历史；只有本次C04动作可使用新有效截止，不恢复已结束根，不等runner起算。新metadata≤900、offline≤600且最多3批、build每次300总600、realroots合计1800且每根900、独立cleanup≤600；所有操作在新5400内。原task roots5/8，仅余分配R06和有据R07，预检前各计、发生后global76/77及TASK109最多7/8；H0子cap5到7明确修订。每根最多一个新preview，runtime60/诊断15，累计新runtime120；新controller≤2，原已用2不返、累计controllercap3到4。原preview2/16保持，本轮最多增2。剩余原第8根没有本卡执行权。

预览名固定preview-03/preview-04，前缀retrolume-task-109-g11-；每根不同nonce与action/root归属，最多一次create/start，不复用或重启旧01/02。第一成功或有真实权限反证即停，不为更放心用第二根。首轮只要是本卡有明确依据的普通诊断错误，可在确认首资源停止后集中修正，以不同as-run/hash/image进入第二根；仅“再试试”不能启动。两次有据修正仍败、根因不稳、任何权限/架构扩大就带最终因果和最小差异交回，不自动再建议同样第三批。

原UID10001、真sandbox、readonly、capdropALL/NNP/原seccomp、networknone/privateIPC/SHM64MiB/CPU1/768MiB等swap/pids128/init/restartno、tmpfs128+32MiB/nosuid-nodev-noexec、无bind/socket/port/secret全部保持。C03显式HOME/XDG/TMPDIR和目录uid/gid模式继承。禁止禁Crashpad/sandbox、root/SYS_ADMIN/ptrace、换包/binary或无因果加flag，唯一新增启动标志仅enable-automation。PG/SQL/role/四表/profile/model/API/UI/main-browser/provider/fee/install/Git、用户资料与删除操作均0。主控不亲自实现或运行。

## 验证、证据与审计关系

一次完整准备后集中离线核对真实改动和后续调用契约，再冻结本轮source/context/argv/版本声明。不能用mock的CDP成功冒真实连接。准备阶段发现普通诊断缺陷直接一并修正，不按每个field返回；真实根发生前写本轮预算和唯一输出目录。新session与原件仅 DocuN/evidence/TASK-109/execution/continuation-04/，原五sessions只读，原计数与实际99.016秒包含27.017 build子段不返、不重复加。

单根直接串行构建绑定、同C03目录启动、版本/命令行/浏览器自身sandbox、正对照、原B01/导航probe与外部精确停止。缺mandatory身份或有效正对照不判权限拒绝成功；表单分层与未触发/观察器不足如实分开。真实新页/导航反证立即停后续；无反证仍NOT_FULL_H0，不签B01/SEC003/G11/STEP/M-1或项目，也不进入后端业务。counter纯观测修正保留原所有有效断言与影响对照，不能改返回枚举造绿。

保全stdout封包/全stderr及截断标记、真实版本与argv、输入清单/包/binary/新image/config、namespace/进程出生、目标/loader/document/可信手势证据和每根失败；外部同CID/nonce/image核后kill/wait/events/EOF/归属进程结束，Stopped子事实与未直接cgroup空的推断分层。全部资源停后保留，不rm/prune/DELETE/DROP或全局kill。集中独立审计仍归稳定完整G11成果，目前不泛派110审普通元数据修正。

## 停止与回传

达到本卡终点即停；scope/高风险/同因两次修正仍败/任一上限或首反证触发则精确停止并交回，旧失败原文不改。成果置顶 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-109-result.md，原标题续作04，当前52303字节完整保后缀。给最终修正/真实diff/hash、新旧累计账、完整诊断进展与有效证据、未完成/风险/权限边界、唯一最小后续差异。普通诊断错误仍阻断时必须给已核根因及本卡为何不能闭合，不再只报元数据未运行。无需用户开Docker或执行命令；回一句结论和结果完整路径，由编排最终裁定。

## 以下为C03及更早完整原字节合同

'''
work = f'''# TASK-109 / R-103 C03启动子事实回收与C04完整诊断收口裁定

{STAMP}，Codex编排Agent。52303字节报告与40900原后缀、496源/唯一controller接线差异、五sessions及真实封包/6811字节完整stderr已核；六目录实际写42字节成功，Browser/CDP连接由真实顺序和协议错误支持，实际版本值未保存/sandbox与probe仍未运行。R05 ERROR13.219秒含cleanup1.719保持，旧99.016秒含build27.017子段；global75、task5/8、H0用5、preview/controller各2、build2/2、active1092上界/metadata500保守/offline0.281/cleanup30及旧未知费用均不返。两个精确CID当前Stopped/Pid0，新03/04不存在、相关控制进程/端口为空。

明确责任为诊断host未满足getBrowserCommandLine的启动前置，原只允许目录修正的合同不覆盖该普通兼容，造成可避免回传；不再重测C03目录或签导航反证。官方原协议与真实错误相符，推荐唯一最小标准启动配置enable-automation，并先持久emit版本再采集真实命令行。原真sandbox/版本/实际参数检查保留，没有模型/页面系统权限或费用扩大。

依据已批准G11执行范围，编排明确修订原子额，C04将元数据配置、后续前置/观察器核对、有据普通诊断修正、最多两根真实probe与收尾合并一合同。新首读固定5400秒，仅本C04取代过期时间门，所有历史时间与已用投入保留。沿原OCI成功来源本地最多2增量build/load；原build2/2封存、累计buildcap2到4，H0cap5到7/controllercap3到4，原taskroot8/preview16不变。R06/有据R07来自原剩余根，不复用R05或无因果启第二；任何权限反证、安全/主要方案变化直接停，仍NOT_FULL_H0/业务冻结。

当前C04已保存回读待转交原109 A+，未真实接收/运行，不再按metadata/启动/网页逐小项出卡。主控只普通核证、维护共享文档，源码与真实测试/build/container启动0。原107独立/110未派；完整G11、必需审计、M-1/项目未验收。以下原裁定原字节保留。

'''
state = '''# 执行动态文档

文档 v2.29，2026-10-09，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.07、task_model/阶段07；以下v2.28及旧历史原字节保留。

## C03目录与Browser连接成立，C04合并普通兼容及整条真实诊断

109/R103 C03恢复续窗01实际已返回，report52303字节/485dc033…保40900旧后缀；当前496项只有h0-run-environment接线变72eddbbe…，其余匹配。六目录uid/gid/mode和独占写42字节成立，6811 stderr完整且无旧Crashpad签名，Browser/CDP连接成立；host的getBrowserCommandLine缺enable-automation前置导致ERROR，版本值尚未落盘/sandbox/probe均未完成。采纳目录/连接/精确停止子事实，不宣告G11。

实际global75、TASK1095/8、H0用5、build2/2、preview/controller各2；R05ERROR13.219含stop1.719、累计real99.016含build27.017子段；本轮active1092上界/metadata500保守/offline0.281/cleanup30及全部旧FAIL/ERROR/UNKNOWN/13元/时窗/重叠原账保留。精确preview01/02当前停止/Pid0、03/04未创建、相关控制进程和18109/55449监听为空。原五session不写。

普通诊断兼容与前卡范围过窄导致再次回传，C04改完整收口，同原109/R103/A+，唯一推荐标准enable-automation启动配置和先存版本后取真实argv；在卡内完成后续API/观察器前置、有据普通修正、完整probe及收尾，不按小步骤交回。新许可TASK-109-G11-C04-20261009，首读固定5400秒专属新窗；明确增量build≤2、原build2/2封存/累计cap4，H0cap5到7/controllercap3到4，原taskroot8/preview16不变；只R06/global76和有新因果R07/global77，无第8根许可。preview各60/诊断15总120，原安全边界不松、新业务/安装/外网/费用/Git0。

C04已保存回读待人工转交，未接收/起算/运行。原目录/OCI/包/业务保护证据复用，主控不接管执行；首权限反证立即停、无反证仍NOT_FULL_H0，原107独立/110未占未派。完整Must/HTML/G11/STEP/M1/最终交付仍原路线未签。本批CHG1103—1110，下一CHG1111；证据orchestration-receipt-05及orchestration-continuation-04-20261009，报告仍原109路径。

## 以下为v2.28及更早历史

'''
arch = '''# 架构动态文档

文档 v1.07，2026-10-09，Asia/Shanghai。需求v1.1、执行动态v2.29；以下v1.06及原历史保字节。

## 目录组合生效，Browser连接后受元数据前置阻断

六目录真实同UID/模式/独占写和完整stderr成立，Browser/CDP已连接，实际版本值未保存；原host调用命令行元数据的enable-automation前置遗漏，属于诊断实现兼容缺陷。旧Crashpad错误本次不再出现是组合生效子事实，不唯一归因HOME，不签浏览器自身sandbox或权限探针。

C04采用标准自动化元数据配置的最小host修正和先保存版本/真实参数，保原sandbox/权限/依赖；因host在镜像内，明确新本地增量build绑定新image/config与源字节，原image/旧context/失败不覆盖。后续普通诊断修正与真实probe/停止集中同卡，不新增生产NavigationGate或新引擎。无反证仍NOT_FULL_H0，四表/PG/profile/model/API/UI业务继续冻结，当前只待转交，不宣称新运行或G11放行。

## 以下为v1.06及更早历史

'''
prefixes = {paths[0]: card, paths[1]: work, paths[2]: state, paths[3]: arch}
for relative, prefix in prefixes.items():
    assert "*" not in prefix and "|" not in prefix
    assert (ROOT / relative).read_bytes() == old[relative]
    (ROOT / relative).write_bytes(prefix.encode("utf-8") + old[relative])
changes = [
    (1103, "DocuN/evidence/TASK-109/orchestration-receipt-05/receipt.json", "核证52303报告、启动子事实与API前置失败、五session和累计75，原失败不返。"),
    (1104, paths[1], "裁定普通兼容责任与完整诊断收口，明确预算子额修订，原边界保留。"),
    (1105, paths[3], "v1.07记录目录/连接实际层与元数据兼容候选，不签sandbox/探针或新image已运行。"),
    (1106, paths[2], "v2.29登记C03返回与C04待转交，所有旧次数/投入保持。"),
    (1107, paths[0], "七节C04完整合同，元数据/后续普通前置/真实probe/收尾合并；原卡原字节保留。"),
    (1108, "DocuN/evidence/TASK-109/orchestration-continuation-04-20261009/continuation-input.json", "最终496源与原件/官方协议前置及原成功构建输入绑定。"),
    (1109, "DocuN/evidence/TASK-109/orchestration-continuation-04-20261009/verification-budget.json及window-assignment.json", "原109 A+待转交，新90分钟/最多2有据根，明确build/H0/controller子限修订不清旧账。"),
    (1110, "DocuN/evidence/TASK-109/orchestration-continuation-04-20261009/delivery-proof.json", "一次静态回读核对历史后缀、路径、预算、源与报告未改；主控产品运行0。"),
]
addition = "\n" + "\n\n".join(f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{relative}。{reason}" for number, relative, reason in changes) + "\n"
assert "*" not in addition
assert (ROOT / paths[4]).read_bytes() == old[paths[4]]
(ROOT / paths[4]).write_bytes(old[paths[4]] + addition.encode("utf-8"))
checks = {}
for relative, prefix in prefixes.items():
    assert (ROOT / relative).read_bytes() == prefix.encode("utf-8") + old[relative]
    checks[relative] = {"identity": identity(ROOT / relative), "old_suffix_exact": True, "new_prefix_bytes": len(prefix.encode("utf-8")), "new_prefix_no_stars_tables": True}
assert result_path.read_bytes() == result_bytes
assert all(sha((ROOT / relative).read_bytes()) == expected for relative, expected in baseline.items())
assert all(sha(Path(path).read_bytes()) == expected for path, expected in old_sessions.items())
proof = {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "action_permit": ACTION, "checks": checks, "old_52303_report_unchanged": True, "old496_and_five_sessions_unchanged": True, "original_errors_deadlines_counts_not_reset": True, "new_used": 0, "dispatch": "待转交", "main_product_execution": 0, "static_document_readback_pass": True, "not_a_product_test_or_independent_audit": True}
save_json(AREA / "delivery-proof.json", proof)
print(json.dumps({"saved": True, "card": str(ROOT / paths[0]), "permit": ACTION, "versions": {"state": "2.29", "architecture": "1.07", "last_CHG": "1110"}, "old_counts_preserved": True, "new_used": 0, "main_product_runs": 0}, ensure_ascii=False))
