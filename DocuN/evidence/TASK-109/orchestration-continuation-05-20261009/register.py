"""核证C04原件并登记最后一根导航尾段；不执行产品或浏览器。"""
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AREA = ROOT / "DocuN/evidence/TASK-109/orchestration-continuation-05-20261009"
RECEIPT = ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-06"
EXEC = ROOT / "DocuN/evidence/TASK-109/execution/continuation-04"
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()
ACTION = "TASK-109-G11-C05-20261009"
IMAGE = "sha256:2b547fc88487d15e80bb7f169f6e4f09ad2fa7c2b944f0b8f47c878a8dc5437b"
CONFIG = "sha256:d9333d9612e86c23b8133ab4149fc2527d2743728608bd556f17a135d0e0b46d"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def identity(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": sha(data)}


def save_json(path, data):
    path.resolve().relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def docker_read(args):
    return subprocess.run(["docker", *args], capture_output=True, encoding="utf-8", text=True, timeout=15, check=True).stdout.strip()


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not RECEIPT.exists() and not (AREA / "verification-budget.json").exists()
result_path = ROOT / "DocuN/results/TASK-109-result.md"
report = result_path.read_bytes()
assert len(report) == 72843 and sha(report) == "4c9e1299de54e0d4bebab8c26f794a628b66806269fba50131304537fbe95835"
prior = (ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-05/TASK-109-C03-resume01-as-returned.md").read_bytes()
assert len(prior) == 52303 and report.endswith(prior)
baseline = read_json(ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-05/current-baseline.json")
expected_changes = {"deploy/preview/host.cjs": "30d9c49f290e9968a1ad48b6fcdb0d2d66e4ec2ff82c5215875c6847b65b01bf", "backend/tests/fixtures/task109/h0-counter.cjs": "457de6cfef6fccc03f782b028b1ab9047441e32b24c70b2e7a91cc49358eaeec"}
actual_changes = {}
for relative, expected in baseline.items():
    actual = sha((ROOT / relative).read_bytes())
    if expected != actual:
        actual_changes[relative] = actual
assert actual_changes == expected_changes
baseline.update(actual_changes)
final_controller = ROOT / "backend/tests/fixtures/task109/h0-final.py"
assert sha(final_controller.read_bytes()) == "8aaaed42a2d90003db4cc2ac0376013a22f5ebce20b1899a35938d5f44a7a982"
baseline[final_controller.relative_to(ROOT).as_posix()] = sha(final_controller.read_bytes())
index = read_json(EXEC / "evidence-file-index.json")
for row in index:
    path = Path(row["path"])
    path.resolve().relative_to(ROOT)
    data = path.read_bytes()
    assert len(data) == row["bytes"] and sha(data) == row["sha256"], f"原件漂移：{path}"
session = read_json(EXEC / "session.json")
assert session["global_roots"] == 77 and session["task_roots"] == 7 and session["H0_roots"] == 7
assert session["cumulative_imagebuilds"] == 4 and session["cumulative_controllers"] == 3 and session["cumulative_preview_starts"] == 3
assert [row["state"] for row in session["roots"]] == ["ERROR", "ERROR"]
observations = read_json(EXEC / "root-07/preview/observations.json")
browser_version = next(row["data"] for row in observations if row["kind"] == "browser_version")
browser_identity = next(row["data"] for row in observations if row["kind"] == "browser_identity")
assert browser_version["version"]["product"] == "Chrome/151.0.7922.34"
assert "--enable-automation" in browser_identity["arguments"] and "--no-sandbox" not in browser_identity["arguments"]
positive = [row for row in observations if row["kind"] == "H0_B01_CONTROL"]
restricted = [row for row in observations if row["kind"] == "H0_B01_RESTRICTED"]
assert len(positive) == 1 and positive[0]["data"]["verdict"] == "PASS_SUBFACT"
assert len(restricted) == 4 and all(row["data"]["verdict"] == "PASS_SUBFACT" for row in restricted)
assert not any(row["kind"] == "H0_NAVIGATION" for row in observations)
stdout = (EXEC / "root-07/preview/container-stdout.bin").read_bytes()
assert len(stdout) == 22364 and sha(stdout) == "592c4247a1017e241ecf873d0b8423b531acf5df966fe81090a98994b8707ac7"
stderr = (EXEC / "root-07/preview/container-stderr.log").read_bytes()
assert len(stderr) == 9619 and b"origin.GetTupleOrPrecursorTupleIfOpaque().IsValid()" in stderr and b"Zygote could not fork" in stderr
loaded = read_json(EXEC / "root-07/loaded-image.json")
assert loaded["id"] == IMAGE and loaded["config"] == CONFIG
old_sessions = read_json(ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-05/receipt.json")["old_sessions"]
assert all(sha(Path(path).read_bytes()) == expected for path, expected in old_sessions.items())
old_sessions[(EXEC / "session.json").as_posix()] = sha((EXEC / "session.json").read_bytes())
images = json.loads(docker_read(["image", "inspect", "--format", '{"id":{{json .Id}},"descriptor":{{json .Descriptor}},"user":{{json .Config.User}},"entrypoint":{{json .Config.Entrypoint}},"labels":{{json .Config.Labels}}}', IMAGE]))
assert images["id"] == images["descriptor"]["digest"] == IMAGE and images["descriptor"]["annotations"]["config.digest"] == CONFIG
assert images["user"] == "10001:10001" and images["entrypoint"] == ["node", "/opt/preview/h0-counter.cjs"]
resources = []
for cid in ["5bd9e24d2a8ba06403f4daf4120aedcd7fe0ef4f0e3ae5f162b723918f189059", "0a449f648fc66020b937cdefa2f2cea4cc6ad305d42a9275cc96a76e77a4ccd0", "3215e8f81ce6ff9b465e1d4be14d7d681a6dc7fdd6058ec881cfa0862bd77392"]:
    data = json.loads(docker_read(["inspect", "--format", '{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"state":{{json .State}},"labels":{{json .Config.Labels}}}', cid]))
    assert data["id"] == cid and data["labels"]["retrolume.task"] == "TASK-109" and not data["state"]["Running"] and not data["state"]["Restarting"] and data["state"]["Pid"] == 0
    resources.append(data)
names = docker_read(["ps", "-a", "--filter", "name=^retrolume-task-109-g11-preview-", "--format", "{{.Names}}"])
assert set(names.splitlines()) == {"retrolume-task-109-g11-preview-01", "retrolume-task-109-g11-preview-02", "retrolume-task-109-g11-preview-04"}
ps_script = r"$p=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18109,55449) } | Select-Object LocalAddress,LocalPort,OwningProcess); $r=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|pythonw|node)(\.exe)?$' -and $_.CommandLine -match 'task109|h0-final|h0-run|preview[\\/]reaper\.py' } | Select-Object ProcessId,Name,CreationDate); @{ports=$p;matching_processes=$r} | ConvertTo-Json -Depth 4 -Compress"
live = json.loads(subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script], capture_output=True, encoding="utf-8", text=True, timeout=25, check=True).stdout)
assert live["ports"] == live["matching_processes"] == []
rules = read_json(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
assert all(sha(Path(row["absolute_path"]).read_bytes()) == row["sha256"] for row in rules)
managed = ["DocuN/tasks/TASK-109.md", "DocuN/results/TASK-109-work-decision.md", "DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD"]
old = {relative: (ROOT / relative).read_bytes() for relative in managed}
assert "文档 v2.29" in old[managed[2]].decode("utf-8-sig").splitlines()[2] and "文档 v1.07" in old[managed[3]].decode("utf-8-sig").splitlines()[2]
assert "CHG-1110" in old[managed[4]].decode("utf-8-sig")[-1000:]
RECEIPT.mkdir()
for relative, data in old.items():
    target = RECEIPT / "before" / relative
    target.resolve().relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
(RECEIPT / "TASK-109-C04-as-returned.md").write_bytes(report)
save_json(RECEIPT / "current-baseline.json", baseline)
save_json(RECEIPT / "resources-readonly.json", {"at": STAMP, "containers": resources, "image": images, "live": live, "preview_names": names.splitlines(), "new_start": 0})
receipt = {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "report": identity(result_path), "old52303_suffix_exact": True, "tracked_source_count": len(baseline), "approved_source_changes": actual_changes, "C04_evidence_index_count": len(index), "C04_evidence_index_all_match": True, "old_sessions": old_sessions, "subfacts_accepted": ["实际Node/包/binary与Browser版本/argv", "真实chrome://sandbox状态原件", "真实手势正对照", "四条受限新页路径的固定2秒子事实", "同CID外部停止及EOF"], "not_accepted": ["完整B01/SEC003/G11通过", "data提交或拒绝", "完整OOPIF观测", "唯一origin或pids根因", "直接cgroup空"], "structural_budget_error": {"original_scenarios": 9, "each_seconds": 2, "minimum_seconds": 18, "old_diagnostic_seconds": 15, "attribution": "编排子限与执行前核对均遗漏，不解释全部浏览器异常"}, "counters": {"global_roots": 77, "task_roots": 7, "H0_roots": 7, "builds": 4, "preview": 3, "controllers": 3}, "real_seconds": 128.828, "build_seconds_subpart": 30.658, "new_active_upper_seconds": 3045.680832, "new_metadata_upper_seconds": 300, "new_offline_upper_seconds": 1, "new_cleanup_upper_seconds": 20, "old_failures_fees_and_overlapping_time_preserved": True, "main_product_runs": 0}
save_json(RECEIPT / "receipt.json", receipt)
inputs = {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "baseline": (RECEIPT / "current-baseline.json").as_posix(), "image": loaded, "C04_report": identity(result_path), "C04_raw_observations": identity(EXEC / "root-07/preview/observations.json"), "C04_stdout": identity(EXEC / "root-07/preview/container-stdout.bin"), "C04_stderr": identity(EXEC / "root-07/preview/container-stderr.log"), "frame_CDP_primary_reference": "https://playwright.dev/docs/api/class-browsercontext#browser-context-new-cdp-session", "local_exact_signature": "deploy/preview/task109-h0-context/vendor/playwright-core/types/types.d.ts:10160-10166，newCDPSession接受Page或Frame；实际OOPIF绑定仍须实证", "source_inputs": [identity(ROOT / path) for path in ["deploy/preview/host.cjs", "backend/tests/fixtures/task109/h0-counter.cjs", "deploy/preview/runtime-bootstrap.cjs", "deploy/preview/wrapper.html", "backend/tests/fixtures/task109/h0-final.py", "backend/app/preview/contracts.py", "backend/app/preview/supervisor.py", "backend/app/preview/reaper.py"]], "remaining_case_order": ["h0_hash", "h0_child", "h0_blob", "h0_data"], "order_basis": "先检查不依赖data异常的同文档路径以尽早形成可裁反证，原场景/2秒标准不删；首次反证或引擎异常停余项"}
save_json(AREA / "continuation-input.json", inputs)
budget = {"TASK": "TASK-109", "R": "R-103", "action_permit": ACTION, "parent_permit": "TASK-109-G11-20261009", "authority": "原批准G11内依据新OOPIF与时间缺口作不同方法/范围的有限尾段；分配原剩余第8根", "window_seconds": 3600, "start_policy": "原109执行者首次读C05即固定同机monotonic起点/3600秒截止，旧全部时间保历史", "effective_start_ns": None, "effective_deadline_ns": None, "seconds": {"metadata": 600, "offline": 300, "root_real": 600, "preview": 60, "tail_diagnostic": 20, "cleanup": 300}, "offline_batches_max": 2, "offline_each_max_seconds": 150, "new_counts": {"root_R08": 1, "preview_create": 1, "preview_start": 1, "controller": 1, "build": 0}, "used_counts": receipt["counters"], "cumulative_caps": {"task_roots": 8, "H0_roots": 8, "builds": 4, "preview": 16, "controllers": 4}, "budget_revision": "H0子限7到8，仅分配原剩余第8根；原taskroot8不增加，build4/4封存；尾段4乘2至少8秒，新诊断20明确取代旧整批15，原18大于15及15.015偏差仍保留", "root": {"id": "H0-R08", "global": 78}, "no_second_root_or_rebuild": True, "after_root": "这条诊断路线结束，若反证或仍不确定转技术方案裁定，不再自动发相同环境小批续验", "image": IMAGE, "config": CONFIG, "business_frozen": True, "zero_new": ["build", "save", "load", "tag", "install", "research_by_worker", "new_engine", "flags_or_resource_relaxation", "PG", "SQL", "role", "profile_model", "API_UI", "main_browser", "provider_fee", "Git", "delete"], "old_failures_spend_and_time_not_reset": True, "new_used": 0}
save_json(AREA / "verification-budget.json", budget)
save_json(AREA / "window-assignment.json", {"TASK": "TASK-109", "R": "R-103", "round": "C05最后导航尾段", "resource": "A+强推理", "window": "原109执行窗口", "dispatch": "待转交", "received": False, "started": False, "new_used": 0, "original107": "隔离保持", "TASK110": "未占未派"})

card = f'''# TASK-109 / R-103 续作05 — 最后一根导航尾段与方案裁定输入

## 目标与交付

继续原109 A+，复用C04成立的元数据/sandbox/正对照及四限制子事实，只对未完成导航补齐真实子frame观察和有限异常取证。以现成c04-02镜像，不构建、不重跑旧整批。先测同文档hash，再dynamic child、blob、data；每项仍真实手势/2秒。首次可证导航或新frame反证即停；引擎异常或观察不足也停止剩余项，不把崩溃当拒绝成功。

这是原总预算最后第8根。正常终点为可裁反证或四项有限样本结果及精确停止；异常终点为绑定明确的错误/资源/观察缺口和最小后续差异。用完这条诊断路线即结束，不能建议再重复相同小批；未关闭同步NavigationGate仍NOT_FULL_H0，业务冻结，不能靠用尽额度宣称完成。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md，task_model/V4.0/AGENTS CHG-0003，需求v1.1、架构v1.08、唯一执行动态v2.30、阶段07。公共根/七锁定指纹同原卡不变，同窗已读未变规则/背景复用。接收A+强推理，继续原109窗口，实际客户端/模型如实登记；原107独立、110未占未派。

原G11-P已批准，本次在原授权内依据新OOPIF观察缺口/时窗矛盾改变诊断方法与范围，明确分配原剩余R08。许可{ACTION}，不改变Must/HTML语义/页面权限/主要模型/引擎或费用，不重复采用。原77入口不是77PASS、R06/R07 ERROR、build4/4和旧13元/UNKNOWN/失败/所有投入完整保留。

## 背景与最小充分上下文

C04实际Chrome151.0.7922.34/原binary、完整argv及真实浏览器sandbox取得；正对照和h0_open/blank/named/form有限子事实成立，表单仅未授allow-forms/CSP层事实。data开始附近有site_info origin CHECK和zygote could not fork，尚无gesture/handler完整ACK或导航结果；唯一资源/引擎因果未确认。根Page快照只有根文档，不能代签OOPIF自身导航。另原9项每项2秒至少18秒大于整批15秒，属于编排与前置核对错误；不把全部引擎异常归于时窗，不抹掉15.015秒原计点偏差。

只补读本卡、DocuN/results/TASK-109-work-decision.md本轮、DocuN/evidence/TASK-109/orchestration-continuation-05-20261009/continuation-input.json和verification-budget.json、现host/固定counter中fixture常量与必要公开Frame接口/控制协议。C04原始observations/stdout/stderr、frozen-run-02/loaded-image、修后记账差异及已存真实镜像投影可复用；不要先读完整执行者自评再重复整仓核证。新helper的controller可参照末次h0-final，但该末版8aaaed42…只有syntax，不能继承完整运行通过。

固定host SHA30d9c49f290e9968a1ad48b6fcdb0d2d66e4ec2ff82c5215875c6847b65b01bf、counter457de6cfef6fccc03f782b028b1ab9047441e32b24c70b2e7a91cc49358eaeec、原bootstrap de20956e3c7cdb631bdb149fee034b95ae8adcad9c07a504beb746f3fc96eeca。准确对象清单及原件在continuation-input。当前报告72843字节/SHA4c9e1299de54e0d4bebab8c26f794a628b66806269fba50131304537fbe95835，末尾52303及嵌套原件完整。

## 执行边界与资源

允许新增backend/tests/fixtures/task109/navigation-tail.cjs、h0-tail.py及必要test_h0_tail_control.py；只实现有限尾段及真实采集，不修改host/counter/bootstrap/wrapper/协议/旧controller/context/vendor/seccomp和全部业务。fixture的pageHtml完整复制原冻结常量并保存字节/hash对应，不能改变其中脚本、sandbox/CSP、按钮/handler或防护来制造拒绝或反证。顺序仅hash→child→blob→data，首反证/异常停止。必须保持原可信鼠标/isTrusted/active与准确handler信号。

明确允许固定受信Node-e组合入口：以原bootstrap源作模板，仅将唯一require旧全counter的诊断调用点替换为被冻结的navigation-tail.cjs正文，采用局部函数作用域，并更新实际执行fixture的描述。组合源/argv/pre-diff-post/as-run/hash均落盘，与原image/原模板分别绑定。新helper只require镜像既有host，使用其真实launch/context/loadFrame能力，不require全counter.main；不改Module缓存/私有API，不伪造CDP返回或version，不读HTTP/页面/model可执行参数，不开放通用exec，不host bind或复制文件进运行容器。完整Windows原生argv长度须离线核清后再入根，不能实际超长才发现。

对子frame直接用冻结1.62.1公开BrowserContext.newCDPSession(frame)，本地types/types.d.ts:10160—10166及[官方接口](https://playwright.dev/docs/api/class-browsercontext#browser-context-new-cdp-session)均支持Page或Frame。实际仍要以Frame/Target、直属#h0_frame、父关系及frame/loader/document元数据绑定，Page.enable及必要Runtime事件观察就绪后才点击；保存子target真实Page/DOMSnapshot投影与导航/创建/销毁事件，根Page并列保存，不用空URL或数组序号代替身份。若确证同进程frame位于根tree，可用根session对准确frameId过滤；没有准确绑定不触发导航。

用子session及固定fixture console原件尽早保留gesture/handler/执行上下文关联，不能只保存发起click就判触发。每case前后记录确切frame、URL、loader、document/backend及目标集，hash的同文档URL变更也是原禁止导航，不能只看loader是否变化。捕获到实际提交/URL变更或新frame/目标创建，保原before/after/events及时终止后续。

可信Node允许限量只读容器自身/proc和/sys/fs/cgroup必要pids、Threads、memory状态：每case前后及诊断期每500ms最多40组，记录失败errno/缺失而非默认0。资源事实、origin CHECK、fork/退出与导航事件分开，不把OOMKilled=false当资源充分。不加ptrace/cap、宿主挂载或资源容量，不为取证另起容器/exec。stdout协议/字节/队列上界继承；只采字段和哈希，不输出所有Env、私配、目录内容或任意文件。

image唯一sha256:2b547fc88487d15e80bb7f169f6e4f09ad2fa7c2b944f0b8f47c878a8dc5437b/config sha256:d9333d9612e86c23b8133ab4149fc2527d2743728608bd556f17a135d0e0b46d。其构建出处C04/R07与新容器执行出处C05/R08分开核，不能要求旧image的build label等于新action。不build/save/load/tag/pull/install，不改image或现有flags。保持UID10001、真sandbox、networknone、readonly、capdropALL/NNP/seccomp、privateIPC、SHM64MiB、CPU1、768MiB等swap、pids128/init/restartno及tmpfs128+32MiB/nosuid-nodev-noexec/原uidgid模式和HOME/XDG/TMPDIR；无bind/socket/port/secret，旧资源不启不删。

首次读卡即单调固化新3600秒窗，原全部截止/active/失败/费用/分类重叠保历史；不是runner启动再起算，不复活C04根。新metadata600/offline300最多2批各150/realroot600/cleanup300/preview60；尾段诊断20秒从诊断begin固定，不后移。仅4项每项2秒至少8秒，预留采集余量12；这是明确新20秒子限，旧18大于15和15.015偏差不改。先完成Frame绑定/真实脚本就绪再开始导航诊断，但全部准备仍计新3600秒与preview60。新测越限如实单列，不能改时间原件造绿。

只H0-R08/global78/TASK109第8根，真实预检前计，总root8不增加、H0子cap7到8明确修订。新preview-05一次create/start、controller一次；原preview/controller各3不返，累计preview最多4/16、controller4/4；build4/4封存新0。C05没有第二根，preflight失败也消耗本根，不借不存在的旧preview03或名义其它余额。新原件/session仅DocuN/evidence/TASK-109/execution/continuation-05/，六旧sessions和旧报告/原件只读。

## 验证、证据与审计关系

一次完整准备后集中offline：新增JS/控制器语法、原HTML字节复制与组合源准确落点、Frame公开接口/事件schema、从R07真实saved image投影验证元数据解析及不同build/run归属、总根序号8但单attempt列表仅1的记账回归、20秒/60秒/根/总期/清理截止一致性。可以针对这两类既有控制缺陷做有意义的纯离线检查；不以mock CDP签Frame或导航行为。字段和下标这种可静态修正问题在入根前解决，不额外Dockers试错。

冻结完整新source/组合argv和读取证明后在一根一次启动内完成尾段；新资源仍需实际版本/binary/argv及目录就绪身份，旧sandbox/B01无需整组重跑。每个正常case满足真实ACK且完整2秒后再判定有限样本；无完整ACK/观察、CDP目标丢失或origin/fork/崩溃等异常立即记UNCONFIRMED/ERROR并停止，不能强行继续刷其它case。首可裁反证停止余项，保权限制失败与引擎故障两轴。四项无反证仍NOT_FULL_H0，当前没有原生同步否决锚，不能签完整安全通过。

外部同CID/image/nonce/出生身份核后kill/wait/events/EOF/Reaper收尾；Stopped子事实与尚未直接cgroup空推断分层，日志、raw packets/Frame返回/时序/截断/错误与资源事实完整存。原real128.828秒含build30.658子段、C04 active3045.680832/metadata300/cleanup20/offline1保守及旧账保持，不重复加子段。PG/SQL/role/profile/model/API/UI/main-browser/provider/费用/新研究/Git/删除均0。G11稳定后的必需独立终审保留，此刻不泛审已过的元数据/B01或占110。

## 停止与回传

一根完成或任何前置/子限/风险/权限反证到达即停止，保存结果。原最后第8根用完后，这条重复受限运行路线终止；若仍异常或缺证，给必要技术裁定输入，不自动提出再加一根/同样参数小批。若取得反证，明确原Native NavigationGate缺口及最小待采用增量，不能改Must/返回值/CSP或页面权限来规避；原生组件/新引擎/主要合同改变须先给具体影响另裁，本卡不实施或系列研究。

置顶保存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-109-result.md，标题续作05，原72843字节完整保后缀。交回最终scope与因果、真实source/argv/hash、旧新累计账、每case证据/未运行、精确收尾与唯一最小下一步；不宣告B01/SEC003/G11/STEP/M-1或项目通过。只回一句结论和结果绝对路径，不接管编排或共享DocuS。

## 以下为C04及更早完整原字节合同

'''
work = f'''# TASK-109 / R-103 C04有限子事实回收与最后导航尾段裁定

{STAMP}，Codex编排Agent。72843字节报告/52303原后缀、原496两批准source差异加h0-final共497映射身份、C04原件索引全部核证，六旧session保持。真实版本151/argv/sandbox原件和正对照/四限制2秒子事实可复用，表单仅自身限制层；data缺完整ACK及导航packet，origin CHECK/fork具体根因不确认，根CDP缺OOPIF自身document。不能判data拒绝或权限反例。原R06/R07 ERROR/构建字段及记账错误/15.015计点偏差保留。

原9项至少18秒却给15秒是编排子限不自洽及前置核对遗漏，主控承担该编排差错；它不解释全部引擎异常。下一步不重跑前半段、不build，改变方法为准确Frame CDP绑定、hash优先的四项未完成尾段及资源取证。原剩余最后R08分配给同109 A+，一次3600秒新窗/根600/preview60/尾诊20，4项至少8秒加采集余量，明确新子限而不改旧记录。

许可{ACTION}仅原剩余总第8根/H0cap7到8，发生后global78/task8/8，controller3到4/4、preview3到最多4/16，build4/4封存新0。复用immutable c04-02镜像，固定Node-e受信组合仅把旧全counter调用改为新冻结尾fixture并更新描述；不改image/host/counter/flags/资源或开任意exec。公开Frame接口本地与官方定义已核，实际绑定仍须证据，资源只可信容器内限量读。首反证或异常即停，不继续同因刷probe。

原77不是77PASS、real128.828含build30.658子段、active3045.680832上界/metadata300/cleanup20/offline1保守/旧失败费13元及重叠原账不返。精确旧01/02/04均Stopped/Pid0，05不存在，当前无相关控制/监听。本C05已保存回读待转交原109，新实际0，原107隔离/110未占未派。最后一根后若仍不足就转技术方案裁定，不自动重复同环境小批；完整NavigationGate/G11/审计/STEP/M1/项目未验收。主控本批只核证/文档，无实现/测试/启动。

'''
state = '''# 执行动态文档

文档 v2.30，2026-10-09，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.08、task_model/阶段07；以下v2.29及原历史保字节。

## C04元数据/sandbox/B01子事实成立，导航尾段用最后原根

109/R103 C04已返回，报告72843/4c9e1299…保52303原后缀；原496映射host/counter两批准变化加h0-final当前497。原件索引匹配，六旧sessions保持。实际版本/argv/binary和真实sandbox、手势正对照/四受限新页有限子事实采纳；data附近origin CHECK/fork、无完整ACK或导航结果、OOPIF自身观察不足，导航不签拒绝或反证。原控制字段/下标错误与15.015偏差不抹；9项各2秒至少18秒大于15秒的编排/前置核对错误明确登记，不把全部失败只归时限。

累计global77、TASK1097/8、H0用7、build4/4、preview/controller各3；R06ERROR7.093/R07ERROR22.719，新增real29.812含build3.641，累计real128.828含build30.658子段不重加。C04active3045.680832上界/metadata300/cleanup20/offline1保守与所有旧失败/费13元/重叠/时窗保留。旧01/02/04当前停止/Pid0，新05不存在、相关控制/18109-55449监听为空。

C05同109/R103原A+待转交，仅固定尾fixture+Frame/OOPIF观察+资源取证，先hash→child→blob→data，四项各2秒且首反证/异常停余项。直接用c04-02实际immutable镜像，Node-e受信组合源分别绑定，不build/不改host、counter、包、flags、权限、资源或业务。新首读3600秒窗，根600/preview60/尾诊20/offline300最多2批/metadata600/cleanup300；明确新诊20只四项8秒加余量，旧18大于15及偏差仍保历史。

只原剩余第8根R08/global78，H0子cap7到8而taskroot8不增加，controller最多4/4/preview4/16，build4/4封存。最后一根之后这条重复运行路线终止，反证或不足转必要技术方案裁定，不自动发相同小批；无反证仍NOT_FULL_H0，原Native NavigationGate未实现，全业务/PG/API/model/付费/Git/删除0。原107独立/110未占未派，完整G11/安全/STEP/M1/项目仍未过，旧G10等充分未变证据继承。

本批CHG1111—1118，下一CHG1119；证据orchestration-receipt-06及orchestration-continuation-05-20261009，报告原109路径。C05未真实接收/起算/开始，新实际0；主控只普通核证和共享文档维护，产品/compile/test/build/启动0。

## 以下为v2.29及更早历史

'''
arch = '''# 架构动态文档

文档 v1.08，2026-10-09，Asia/Shanghai。需求v1.1、执行动态v2.30；以下v1.07及原历史保字节。

## 固定浏览器可运行，导航与OOPIF证据仍有缺口

C04取得固定Chrome151/原binary/argv与浏览器自身sandbox、正对照和有限新页拒绝子事实，元数据兼容已真实生效；data附近引擎origin CHECK/fork没有导航结果，根Page不足观察子OOPIF，不能签安全成功或唯一故障根因。现host仍无生产全协议同步NavigationGate。

C05不改组件/权限/flags/资源或重构建，直接复用c04-02，以独立固定可信尾fixture和公开Frame CDP观察补四项剩余路径；已过前半段继承，改变顺序先检查同文档导航，受信源/镜像分别绑定。整批18秒下限大于旧15秒作为明确编排错误保留，新尾诊20只对应四项8秒加观察余量。最后原根完成后结束该诊断路线，反证或证据不足转技术方案裁定，不能以调返回值或放宽Must结束项目；业务继续冻结。

## 以下为v1.07及更早历史

'''
prefixes = {managed[0]: card, managed[1]: work, managed[2]: state, managed[3]: arch}
for relative, prefix in prefixes.items():
    assert "*" not in prefix and "|" not in prefix
    assert (ROOT / relative).read_bytes() == old[relative]
    (ROOT / relative).write_bytes(prefix.encode("utf-8") + old[relative])
changes = [(1111, "DocuN/evidence/TASK-109/orchestration-receipt-06/receipt.json", "核C04子事实、原件/源及77累计，data/OOPIF未证与时限矛盾分级。"), (1112, managed[1], "最后原根尾段裁定，原受限路线此后终止，不再盲加同样小批。"), (1113, managed[3], "v1.08同步浏览器可运行与导航证据缺口，方案权限不扩大。"), (1114, managed[2], "v2.30登记C04返回和C05待转交、77原账不返、新使用0。"), (1115, managed[0], "完整七节C05直接复用镜像和前半证据，准确Frame观察/四尾段/最后一根/收尾。"), (1116, "DocuN/evidence/TASK-109/orchestration-continuation-05-20261009/continuation-input.json", "497源、C04原件、Frame公开接口来源与重排依据。"), (1117, "DocuN/evidence/TASK-109/orchestration-continuation-05-20261009/verification-budget.json及window-assignment.json", "分配剩余第8根，明示新尾诊20/3600窗，build0，旧失败与秒数保留。"), (1118, "DocuN/evidence/TASK-109/orchestration-continuation-05-20261009/delivery-proof.json", "一次静态文档回读/后缀与源原件保护，主控产品运行0。")]
addition = "\n" + "\n\n".join(f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{relative}。{reason}" for number, relative, reason in changes) + "\n"
assert "*" not in addition and (ROOT / managed[4]).read_bytes() == old[managed[4]]
(ROOT / managed[4]).write_bytes(old[managed[4]] + addition.encode("utf-8"))
checks = {}
for relative, prefix in prefixes.items():
    assert (ROOT / relative).read_bytes() == prefix.encode("utf-8") + old[relative]
    checks[relative] = {"identity": identity(ROOT / relative), "old_suffix_exact": True, "new_prefix_bytes": len(prefix.encode("utf-8"))}
assert result_path.read_bytes() == report
assert all(sha((ROOT / relative).read_bytes()) == expected for relative, expected in baseline.items())
assert all(sha(Path(path).read_bytes()) == expected for path, expected in old_sessions.items())
save_json(AREA / "delivery-proof.json", {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "action_permit": ACTION, "checks": checks, "old72843_report_and_six_sessions_unchanged": True, "497_mapped_sources_unchanged": True, "old_errors_time_fees_preserved": True, "new_used": 0, "dispatch": "待转交", "main_product_execution": 0, "document_readback": "一次通过，不是产品测试或独立审计"})
print(json.dumps({"saved": True, "card": str(ROOT / managed[0]), "action_permit": ACTION, "versions": {"state": "2.30", "architecture": "1.08", "last_CHG": "1118"}, "last_existing_root": "H0-R08", "new_build": 0, "new_used": 0, "main_product_runs": 0}, ensure_ascii=False))
