"""保存同任务增量合同和共享裁定，只做文档一致性核对。"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess
import time

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = Path(__file__).resolve().parent
BASE = ROOT / "DocuN/evidence/TASK-111/orchestration-20261010"
EXEC = ROOT / "DocuN/evidence/TASK-111/execution"

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def ident(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def put_prefix(relative, prefix):
    data = prefix.encode("utf-8")
    if "*" in prefix or any(line.startswith("|") for line in prefix.splitlines()):
        raise SystemExit("新增文档含禁用格式")
    original = (OUT / "before" / relative.replace("/", "__")).read_bytes()
    (ROOT / relative).write_bytes(data + original)
    return {"path": relative, **ident(ROOT / relative), "prefix_bytes": len(data),
            "old_suffix_sha256": hashlib.sha256(original).hexdigest()}

now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
stamp = now.isoformat()
for item in read(OUT / "input-receipt.json"):
    if item["path"] in ("DocuN/tasks/TASK-111.md", "DocuN/results/TASK-111-work-decision.md", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD", "DocuS/文档变更记录.MD"):
        if ident(ROOT / item["path"])["sha256"] != item["sha256"]:
            raise SystemExit("共享对象已变化，停止覆盖")

budget = read(EXEC / "budget.json")
returned = read(OUT / "returned-receipt.json")
if budget != returned["budget"]:
    raise SystemExit("执行账已变化，先查在途")
remaining = (budget["deadline_ns"] - time.monotonic_ns()) / 1e9
if remaining <= 1800:
    raise SystemExit("原总窗不足保留清场，不签新真实执行")

old_limits = read(BASE / "verification-budget.json")
caps = dict(old_limits["counts"])
caps["real_batches"] = 9
caps["preview_reaper_validation_batches"] = 3
caps["offline_related_batches"] = 8
used = budget["counts"]
grant = {"TASK": "TASK-111", "R": "R-105", "continuation": "续作01", "issued_local": stamp,
         "permit": "TASK-111-G11-C01-20261010", "base_permit": "TASK-111-G11-P110-20261010",
         "source_result": returned["report"], "consumed_at_issue": used, "caps_after": caps,
         "remaining_counts": {key: caps[key] - val for key, val in used.items()},
         "raised_only": {"real_batches": {"old": 6, "new": 9}, "preview_reaper_validation_batches": {"old": 2, "new": 3}, "offline_related_batches": {"old": 6, "new": 8}},
         "seconds": {"original_total_window": 43200, "original_deadline_ns": budget["deadline_ns"],
                     "original_deadline_utc": "2026-10-10T11:24:07Z", "original_deadline_local": "2026-10-10T19:24:07+08:00",
                     "remaining_total_at_issue": remaining, "old_recorded_real": 3630.157,
                     "real_total_cap": 14400, "real_remaining": 10769.843, "new_real_cap": 10500,
                     "new_root_each": 3500, "new_reaper_combination": 1200,
                     "new_metadata_preparation_cap": 1200, "new_implementation_offline_cap": 3600,
                     "cleanup_original_cap": 1800, "cleanup_used": 6.375, "cleanup_remaining": 1793.625},
         "historical_unclassified_time": "unknown，保留原分类缺口；新计时不把旧缺口当0",
         "prospective_timing_gate": "本次有界分类加原总截止替代未可重建旧metadata/offline余额门；累计已知投入不清零",
         "root_cumulative_before": 84, "root_cumulative_after_max": 87,
         "resource_span": "唯一PG协调者一次剩余start，跨根持有全过程计入新增real，独立清场与出生控制，不跨交回保运行",
         "license_text_exception": {"maximum_texts": 6, "seconds": 300, "within_metadata_cap": True,
                                    "scope": "锁定版本的公开官方版权/许可文本只读取回，不发项目资料、不取二进制、不安装或换依赖"},
         "execution_started": False, "delivery_state": "待人工转交", "orchestrator_runtime": False}
assert grant["seconds"]["old_recorded_real"] + grant["seconds"]["new_real_cap"] <= grant["seconds"]["real_total_cap"]
assert all(value >= 0 for value in grant["remaining_counts"].values())
save("continuation-budget.json", grant)

ps = r"$ErrorActionPreference='Stop'; $taskMetadataPid=$PID; $taskProcesses=@(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $taskMetadataPid -and ($_.ProcessId -in @(47588,52420) -or ($_.CommandLine -and ($_.CommandLine -match 'task111[\\/]workloop\.py|app\.preview\.production_reaper|app\.preview\.production_supervisor|uvicorn.*18111'))) } | Select-Object ProcessId,ParentProcessId,Name,CreationDate); [PSCustomObject]@{metadata_probe_pid=$taskMetadataPid;possible_owned_processes=$taskProcesses} | ConvertTo-Json -Depth 8 -Compress"
host_proc = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, timeout=25)
if host_proc.returncode:
    raise SystemExit("宿主只读在途核对失败")
host_check = json.loads(host_proc.stdout.decode("utf-8-sig"))
host_check["note"] = "前次元数据PowerShell因命令内模式串自匹配已披露；此核对明确排除本次只读探针PID，不是产品运行证据"
save("host-process-supplement.json", host_check)
if host_check["possible_owned_processes"]:
    raise SystemExit("仍有可能在途的本卡进程，停止签发")

resources = {"issued_local": stamp, "read_only_recheck": "resource-recheck.json及host-process-supplement.json",
             "pg": {"id": "1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51",
                    "name": "retrolume-task-111-g11-v2-pg1", "volume": "retrolume-task-111-g11-v2-pg1-data",
                    "image": "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f",
                    "port": 55451, "main_exists": True, "upgrade_fault": "原授权范围，本次明确可在同一簇创建；尚未实施"},
             "renderer_image": {"image_index": "sha256:8ec35cf6df9c13eef0c3b15567e72ac0cd7382c19b586469cb4aaca48e8ef015",
                                "image_config": "sha256:24f911d87f7375cf2dc31b8d1431957d7f2fec4a6de531885109e0ad28e9b043",
                                "load_manifest_sha256": "3df2280c8a135f0ac51c1df55c341d269d2439c855ff3a5c8819d6123ac44cf2",
                                "renderer_sha256": "6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597",
                                "reuse": "源码不变不重build；必要修正只剩余v2-02/03"},
             "preview": {"allowed_names": [f"retrolume-task-111-g11-preview-{number:02d}" for number in range(2, 15)],
                         "previous_01": "125失败，无对象无start，60秒R和count1及原失败保留；恢复事实只能追加"},
             "api_port": 18111, "final_audit": "稳定完整候选后新隔离A+，目前未发卡",
             "secret_handling": "仅安全内存/DPAPI/stdin或限定Env，主控不读私配/秘密"}
save("continuation-resources.json", resources)
save("window-assignment.json", {"TASK": "TASK-111", "R": "R-105", "level": "A+", "window": "原110→111执行窗口",
                               "previous_report_identity": "Codex based on GPT-6，精确部署后缀未知",
                               "state": "待人工转交，未派发/接收/开始", "parallel": False,
                               "why": "有限语言、原子权限、浏览器、跨进程停止和恢复的完整高风险成果", "new_audit_dispatched": False})

state_prefix = f"""# 执行动态文档

文档 v2.34，2026-10-10，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.12、task_model/阶段07；以下v2.33及历史原字节保留。

## 111候选部分回收，续作01完整增量待转交

TASK111/R105原A+窗口已真实返回，结果25338字节/72bb21f6…，95项交回源和七锁定规则指纹全匹配。实现候选已保存，不等于完整实现验收通过。代码轴为候选尚待完整终审；证据轴四次Windows OneCall加合成传输/PG与部分HTTP/离线有效，renderer实际start0、M01—M12未闭；执行控制轴原根6/6、Reaper2/2、offline6/6到限，旧分类计时缺口和全部失败保留。没有G11、STEP015/016、SEC003/B01、M1或项目放行。

实际四次原生为机械能/二项成功、非法RECEIVED无artifact、UNKNOWN无artifact；未变descriptor/compiler/model_policy/generation/012及四runtime的相关事实可继承。最终模板/owner/API/进程/PNG/控制与前端改变尚未完整动态验证。唯一preview01因不支持--pid private拒绝125，已离线修正但从未启动，60秒R和一次计数保留。真实工作loop失败后空等截止且清场同闸受阻，独立cleanup已精确收尾；许可两次同因修正失败，旧扫描停止。本次不以更多metadata子事实替代正常链。

主控只读核精确PG CID1791a2d0…、volume、image、1CPU/512MiB/pids128/55451，实际Stopped/Pid0；renderer v2-01 image8ec35cf6…仍可用；本卡preview对象空、18111/55451无监听，宿主探针自匹配经排除自身PID补记。以上是当前清场元数据，不是运行后Linux树空或退款证据。主控产品修改/测试/构建/SQL/资源启动全部0。

在已采用G11-P110同范围内签发TASK-111-G11-C01-20261010：仍沿原TASK111/R105与原A+窗口，未验收补证不新TASK，卡与Work已保存待人工转交，没有派发/开始事实。新根累计6→9各3500，新real最多10500且累计≤14400；Reaper验证2→3仅一1200完整组合；offline6→8仅两有据关联批。其它上限和全部旧已用不变：PG start5/6只剩一次、API1/4、browser1/3、model4/6、Windows4/8、build1/3、frontend2/3、preview create1/14/start0/14，后续仅02—14。真实入口历史累计旧78加新6为84，上限新增后87，不是通过次数。

原首读2026-10-09T23:24:07Z，原固定截止2026-10-10T11:24:07Z/本地19:24:07，mono902913370092600不延。已计real3630.157/offline62.296/cleanup6.375不是全实施投入；旧metadata/实施分类unknown仍保留。本轮前向有界资料准备1200、实现离线3600、新真实10500、原cleanup剩1793.625与原总截止取更早；旧unknown不能当0，取证仅证明实际新分类，不追签旧7200分类已合规。许可原失败后采用逻辑OCI链接到普通文本的新定界方法，必要仅6份同锁定版本官方许可文本/300秒只读例外，不允许二进制/安装/pull/换依赖或发项目资料。

PG唯一剩余启动由资源协调者跨新增根持有，整个持有过程计real且有独立截止、出生、parent-death和cleanup控制，不跨交回保运行。先完成实际M矩阵/故障variant/同COMMIT-ACL/准确cache屏障/upgrade-fault夹具和控制修正；第一组合正常两场景remote/几何/PNG/来源及TreeProof，故障组合随后完成。源码消费者停后留as-run再修，根不延，无工作即收尾，不再次空等。许可证欠证阻塞最终自包含放行，不挡独占合成正常验证；HTML默认关闭，稳定完整G11后一次新隔离增强终审仍计划未发。

本次CHG1150—1159，下一1160；完整回收与增量预算/资源/窗口/回读在DocuN/evidence/TASK-111/orchestration-receipt-01/。用户只需转同卡给原111A+并回传结果路径。所有旧G3—G10通过/107隔离、109反证与13元及历史失败UNKNOWN保持；Linux/Nginx公共交付后续阶段不在此启动，用户库/私配/付费/Git/删除/发布0。

## 以下为v2.33及更早历史

"""

architecture_prefix = """# 架构动态文档

文档 v1.12，2026-10-10，Asia/Shanghai。需求v1.2、执行动态v2.34；以下v1.11及历史原字节保留。G11-P110已采用，111实际为候选且动态链未完成。

## G11有限交互候选已落地，完整安全与功能仍待收口

实际加入description/compiler/model_policy/generation、012四表及有限角色/生产repository、HTTP接口、Supervisor/Reaper/process/pipe/host_policy、固定runtime与host、前端解释面板/控件/typedAPI/意图核对及原允许业务挂载、公开配置和README/本地部署/Compose候选。当前新产物协议interactive_description.v1→html_explanation.v2→compiled_interactive_html.v1/retrolume.preview.v2，不执行模型自由HTML/JS/markup。只按实际交回清单与源码定位登记，不把“实现保存”当运行或独审通过。

四次真实Windows OneCall/合成PG事实及部分HTTP证据可在未变source范围继承；最终模板和控制/前端尚缺相关动态验收。正式renderer v2-01镜像及加载字节已构建，但start0，不能签远端计算/图形、所有导航出口、Linux停止或恢复成立。原非法PID参数已经源码修正，Default private PID适用仍需真实namespace/init和对象身份原件。PNG完整性/身份/迟到、同COMMIT-ACL/非空升级、准确公开资格屏障与输入控制均保持原必须项。

preview产品仍每活动3次/180秒、30—60秒预扣、ready8与D-10关输入，次数/UNKNOWN/旧四账不变；旧01失败保留60秒R及count1，不把精确清场元数据当退款授权。当前HostPolicy的Local互斥范围未证明跨Windows登录会话；续作在现有允许模块内明确受信部署owner排他范围、真实非空namespace身份及Windows CLI归属，未知失败关闭，不新增系统权域或服务。

停止候选仍完整private PID/init机制适用、无逃逸、精确CID/image/nonce、外部kill/wait/events/EOF与拥有控制进程退出、无restart组合；单Stopped/Pid0或数据库状态不足，缺证unconfirmed保R。生成/预览业务只可精确合成许可取证，生产审核票据前默认HTML关闭。许可证OpenSSL解析与主Chrome版权未齐，自包含尚不通过，新的普通文本解析与少量官方许可文本取证不得扩大为安装联网或新引擎。

111续作01同窗口把正常UI、事务权限、升级、竞争与停止恢复作为完整成果，复用未变runtime/image及旧充分证明。Compose候选仅本机PG依赖和renderer构建入口，动态preview不能常驻绕次数；Windows本地app不加Docker socket。Linux/Nginx公共部署仍后续，无用户库或公开发布。完整稳定G11之后一次隔离增强终审必需，目前未派审计。

## 以下为v1.11及更早历史

"""

work_prefix = f"""# TASK-111 / R-105 续作01回收裁定与明确增量许可

{stamp}，Codex编排Agent。原用户采用G11-P110持续有效；本轮不是再次改变核心目标、主要模型、输入安全承诺或固定权限画像。已读结果原件并核95项源、七规则及精确资源，只做编排核证/文档，不接管实现与运行。

裁定原111已返回候选、部分完成，整卡不验收通过。四次原生生成/保存及有效离线、HTTP子事实按字节继承；renderer从未start，最后模板/控制/前端与M01—M12完整动态仍缺，许可两修失败及计时/缺失pre/短暂撤销改动偏差保留。三轴分别登记，不凭报告存在或清场成功通过功能。

现在明确签发TASK-111-G11-C01-20261010，沿原A+执行窗口与原TASK/R，一次完整收口而非逐点拆卡。累计真实根6→9各3500/新增real10500、Reaper2→3一次1200、offline6→8两批；其它已用与上限全保留。原固定总窗截止本地2026-10-10 19:24:07及mono902913370092600不延，新增分类计时由卡明确，历史unknown不补造；原real14400及cleanup剩1793.625继续有效。新版continuation-budget.json为精确额度，不从执行者建议自动授予权限。

现PG一次剩余start由唯一资源协调者跨新根持有并独立清场，整个持有期计真实时间。完整夹具先齐，首次新组合同时拿正常remote与停止组合，普通确定修正停消费者后按as-run复验，不再空等或让finally受业务闸挡住。old 01未知保留/次数不退款；恢复只能按持久事实与完整证据追加。未知Windows owner/namespace身份需失败关闭，在原允许模块内有据落实，不扩服务/特权。

许可证旧方法两次失败停止。新依据为保存OCI清单中的链接/层路径定界与普通版权字节逻辑复制；必要允许最多6份锁定版本官方许可文本/300秒只读例外，不下载新发行包、不安装/pull/换库、不发项目秘密。欠证仍阻最终许可/自包含放行，不能用许可准备挡正常合成链。

全部资源沿已登记111专用对象，禁止用户/旧库、私配、真实provider/付费、001—011/锁文件、第五表/新权域、旧109重启、Git提交、数据删除或发布。生产默认HTML关闭，完整高风险G11稳定后一次新隔离A+终审不取消。本轮没有最终用户放行。

续作合同、预算、精确资源、窗口与核证receipt已保存待人工转交；不是已派发/执行中。保存具体路径及完整历史后由用户转原111窗口，完成或真实停止条件才统一回传。

## 以下为原完整执行授权历史

"""

changes = []
changes.append(put_prefix("DocuS/执行动态文档.MD", state_prefix))
contract = (OUT / "continuation-contract.md").read_text(encoding="utf-8")
changes.append(put_prefix("DocuN/tasks/TASK-111.md", contract))
changes.append(put_prefix("DocuN/results/TASK-111-work-decision.md", work_prefix))
changes.append(put_prefix("DocuS/架构动态文档.MD", architecture_prefix))

log_items = [
    ("DocuN/evidence/TASK-111/orchestration-receipt-01/returned-receipt.json", "真实回收111候选，95源/七规则与原件适用，三轴及历史计时缺口登记，不签整卡"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-01/continuation-budget.json", "明确同范围增量6→9根/2→3Reaper/6→8offline，原总截止及其它消耗不清，前向分类与原unknown区分"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-01/continuation-resources.json", "精确PG剩余一次持有/独立清场、image复用、preview02—14和许可文本小例外，未启动"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-01/window-assignment.json", "沿原111A+待人工转交，无并行，无未来审计派发事实"),
    ("DocuN/results/TASK-111-work-decision.md", "回收三轴与同任务续作明确裁定，原授权全文保留"),
    ("DocuN/tasks/TASK-111.md", "续作01完整七节，首正常remote/停止，事务ACL/升级/准确race/故障/许可一次收口，原卡原字节保留"),
    ("DocuS/架构动态文档.MD", "v1.12真实候选/默认关闭/真实缺口与采用边界，无实现通过或树空冒认"),
    ("DocuS/执行动态文档.MD", "v2.34唯一账回收111并登记同窗续作待转交、累计84/新上限87与原截止"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-01/host-process-supplement.json", "排除只读探针PID自匹配，原观察不改，补记无可能在途本卡进程"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-01/delivery-proof.json", "一次文档/实际路径/预算/历史后缀回读，主控产品运行0")
]
ledger_path = ROOT / "DocuS/文档变更记录.MD"
ledger_before = (OUT / "before/DocuS__文档变更记录.MD").read_bytes()
log_prefix = "\n\n## 2026-10-10 TASK111回收与同任务续作01\n\n"
log_prefix += "\n\n".join(f"- CHG-{1150 + index:04d}，{stamp}，Codex编排Agent，{path}。{reason}。" for index, (path, reason) in enumerate(log_items)) + "\n"
assert "*" not in log_prefix
ledger_path.write_bytes(ledger_before + log_prefix.encode("utf-8"))
changes.append({"path": "DocuS/文档变更记录.MD", **ident(ledger_path), "history_prefix_sha256": hashlib.sha256(ledger_before).hexdigest()})

for item in changes[:4]:
    path = ROOT / item["path"]
    old_bytes = (OUT / "before" / item["path"].replace("/", "__")).read_bytes()
    assert path.read_bytes().endswith(old_bytes)
assert ledger_path.read_bytes().startswith(ledger_before)
assert ident(ROOT / "DocuN/results/TASK-111-result.md")["sha256"] == returned["report"]["sha256"]
req_before = next(item for item in read(OUT / "input-receipt.json") if item["path"] == "DocuS/最终需求文档.MD")
assert ident(ROOT / req_before["path"])["sha256"] == req_before["sha256"]
expected_sections = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源", "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
assert all(contract.count("## " + title + "\n") == 1 for title in expected_sections)
assert (ROOT / "DocuN/tasks/TASK-111.md").read_text(encoding="utf-8").startswith(contract)
required_paths = ["AGENTS.md", "DocuN/tasks/TASK-111.md", "DocuN/results/TASK-111-result.md", "DocuN/results/TASK-111-work-decision.md",
                  "DocuN/evidence/v4-migration-20260930/rules-snapshot.json", "backend/tests/fixtures/task111/workloop.py",
                  "backend/tests/fixtures/task111/complete_matrix.py", "DocuN/evidence/TASK-111/execution/delivery/final-source-identity.json",
                  "DocuN/evidence/TASK-111/execution/delivery/supplemental-source-identity.json"]
assert all((ROOT / path).is_file() for path in required_paths)
proof = {"verified_local": dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(), "TASK": "TASK-111", "R": "R-105",
         "permit": grant["permit"], "state": "待人工转交", "main_product_runtime": False,
         "one_document_consistency_check": True, "complete_seven_sections": True, "rule_matches": 7, "source_matches": 95,
         "report_original_unchanged": True, "requirements_unchanged": True, "history_original_bytes_retained": True,
         "path_checks": required_paths, "changed_documents": changes, "budget_arithmetic_passed": True,
         "original_deadline_preserved": True, "no_new_task_or_audit_dispatch": True, "CHG": [1150,1159], "next_CHG": 1160}
save("delivery-proof.json", proof)
print(json.dumps({"saved": True, "card": str(ROOT / "DocuN/tasks/TASK-111.md"), "card_identity": ident(ROOT / "DocuN/tasks/TASK-111.md"),
                  "remaining_seconds_at_issue": remaining, "state": "v2.34 待人工转交", "architecture": "v1.12 候选未验收",
                  "history_and_budget_check": True, "CHG": [1150,1159]}, ensure_ascii=False))
