"""只读核证回传、保存编排调整与文档，不运行产品或测试。"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import subprocess
import time

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = Path(__file__).resolve().parent
EXEC = ROOT / "DocuN/evidence/TASK-111/execution"
C01 = EXEC / "continuation-01"
OUT.mkdir(parents=True, exist_ok=True)

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def identity(path):
    body = path.read_bytes()
    return {"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def metadata(args):
    try:
        proc = subprocess.run(args, capture_output=True, timeout=25)
        if proc.returncode:
            return {"exit_code": proc.returncode, "readable": False}
        return {"exit_code": 0, "data": json.loads(proc.stdout.decode("utf-8-sig"))}
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        return {"readable": False, "error_type": type(exc).__name__}

stamp = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
receipt = read(C01 / "delivery/returned-receipt.json")
report_path = ROOT / "DocuN/results/TASK-111-result.md"
report = {"path": str(report_path), **identity(report_path)}
assert all(report[key] == receipt[key] for key in ("bytes", "sha256"))
(OUT / "returned-result.md").write_bytes(report_path.read_bytes())

rules = []
for row in read(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json"):
    item = {"path": row["absolute_path"], **identity(Path(row["absolute_path"]))}
    item["matches"] = item["sha256"] == row["sha256"]
    rules.append(item)
save("rules-check.json", rules)
assert all(row["matches"] for row in rules)

sources = {}
for manifest in (EXEC / "delivery/final-source-identity.json", EXEC / "delivery/supplemental-source-identity.json", C01 / "delivery/final-source-identity.json"):
    for item in read(manifest):
        sources[item["path"]] = {"manifest": str(manifest.relative_to(ROOT)), **item}
checked = []
for relative, row in sources.items():
    path = ROOT / relative
    assert path.resolve().is_relative_to(ROOT.resolve())
    actual = identity(path)
    checked.append({"path": relative, "manifest": row["manifest"], **actual,
                    "expected_sha256": row["sha256"], "matches": actual["sha256"] == row["sha256"]})
save("source-check.json", checked)
assert all(row["matches"] for row in checked)

inputs = []
for relative in ("AGENTS.md", "DocuS/最终需求文档.MD", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD", "DocuS/文档变更记录.MD",
                 "DocuN/tasks/TASK-111.md", "DocuN/results/TASK-111-work-decision.md", "DocuN/results/TASK-111-result.md",
                 "DocuN/evidence/TASK-111/execution/budget.json", "DocuN/evidence/TASK-111/execution/continuation-01/timing.json",
                 "DocuN/evidence/TASK-111/execution/continuation-01/phase-events.jsonl",
                 "DocuN/evidence/TASK-111/execution/continuation-01/stop-receipt.json",
                 "backend/tests/fixtures/task111/control.py", "backend/tests/fixtures/task111/c01_coordinator.py", "backend/tests/fixtures/task111/c01_faults.py"):
    inputs.append({"path": relative, **identity(ROOT / relative)})
save("input-receipt.json", inputs)
budget = read(EXEC / "budget.json")
timing = read(C01 / "timing.json")
assert budget["active_batch"] is None
assert budget["counts"] == receipt["counts"]

cid = "1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51"
pg = metadata(["docker", "container", "inspect", cid])
if "data" not in pg:
    raise SystemExit("精确PG元数据不可核，停止签发")
obj = pg.pop("data")[0]
pg.update({"id": obj.get("Id"), "image": obj.get("Image"), "name": obj.get("Name"),
           "running": obj.get("State", {}).get("Running"), "pid": obj.get("State", {}).get("Pid"),
           "mounts": [{key: row.get(key) for key in ("Type", "Name", "Destination", "RW")} for row in obj.get("Mounts", [])]})
assert pg["id"] == cid and pg["running"] is False and pg["pid"] == 0
proc = subprocess.run(["docker", "container", "ls", "-a", "--filter", "name=retrolume-task-111-g11-preview-", "--format", "{{.ID}}"], capture_output=True, timeout=25)
assert proc.returncode == 0
preview_ids = proc.stdout.decode("utf-8", errors="replace").split()
assert not preview_ids
ps = r"$ErrorActionPreference='Stop'; $taskProbePid=$PID; $taskListeners=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18111,55451) } | Select-Object LocalAddress,LocalPort,OwningProcess); $taskProcesses=@(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $taskProbePid -and $_.Name -match 'python|node|docker|powershell' -and $_.CommandLine -and $_.CommandLine -match 'task111[\\/](workloop|c01_coordinator)\.py|app\.preview\.production_reaper|app\.preview\.production_supervisor|uvicorn.*18111' } | Select-Object ProcessId,ParentProcessId,Name,CreationDate); [PSCustomObject]@{metadata_probe_pid=$taskProbePid;listeners=$taskListeners;possible_owned_processes=$taskProcesses} | ConvertTo-Json -Depth 8 -Compress"
host = metadata(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps])
assert "data" in host
host = host["data"]
assert not host["listeners"] and not host["possible_owned_processes"]
save("resource-recheck.json", {"at_local": stamp, "read_only": True, "pg": pg, "previews": preview_ids, "host": host,
                              "scope": "精确对象只读元数据，不读取Env/秘密，不声明动态TreeProof或预算退款"})
save("returned-receipt.json", {"TASK": "TASK-111", "R": "R-105", "at_local": stamp, "report": report,
                              "rules_matches": len(rules), "source_matches": len(checked), "budget": budget,
                              "C01_timing": timing, "new_real": 0, "renderer_cumulative_start": 0,
                              "implementation": "候选增量/夹具未完成", "evidence": "仅新增静态，动态全链仍未齐",
                              "execution_control": "C01分类7530.953>3600，超限3930.953，历史FAIL不追认",
                              "diagnosis": ["分类硬门与复杂收口不匹配", "全部故障前置拖延首次正常运行", "分类计时未持续监控", "协调清场仍走业务门，准确故障仍占位"],
                              "main_runtime": False})

caps = dict(timing["caps_after"])
used = dict(budget["counts"])
cleanup_remaining = 1800 - budget["time_seconds"]["cleanup"]
assert abs(budget["time_seconds"]["cleanup"] - 17.5570978) < 0.01
grant = {"TASK": "TASK-111", "R": "R-105", "permit": "TASK-111-G11-C02-20261010", "base_permit": "TASK-111-G11-P110-20261010",
         "issued_local": stamp, "source_result": report, "used_counts": used, "hard_count_caps": {key: val for key, val in caps.items() if key != "offline_related_batches"},
         "offline_batches": {"previous_used": 7, "previous_cap": 8, "C02_rule": "记录实际检查与普通修正，不再设次数硬门，统一总窗和问题两修停止"},
         "old_implementation_breach_preserved": True, "old_category_unknown_preserved": True,
         "class_time_policy": "metadata/实施/离线记实际分段，不再各自硬截止；非资源准备由完整综合窗约束",
         "seconds": {"new_comprehensive_window": 21600, "original_total_window": 43200, "authorized_total_after": 64800,
                     "original_deadline_ns": 902913370092600, "aggregate_deadline_ns_after": 924513370092600,
                     "aggregate_deadline_local_after": "2026-10-11T01:24:07+08:00",
                     "effective_deadline_rule": "C02首读单调加21600与旧固定总截止加21600取更早；不回填首次读取",
                     "business_stop_before_total": 600, "real_used": 3630.157, "real_total_cap": 14400, "real_remaining": 10769.843,
                     "real_roots_remaining": 3, "real_root_each": 3500, "reaper_combination_remaining": 1, "reaper_combination_seconds": 1200,
                     "cleanup_used": budget["time_seconds"]["cleanup"], "cleanup_remaining": cleanup_remaining},
         "scope_change": "仅执行时窗/低影响分类门/首正常顺序，不变用户目标、产品安全/限额、对象、模型次数或付费",
         "first_normal_requires_all_faults": False, "all_faults_still_required_for_full_delivery": True,
         "PG_start_remaining": 1, "PG_shared_lifecycle": True, "root_cumulative_before": 84, "root_cumulative_after_max": 87,
         "independent_audit_required_after_stable": True, "state": "待人工转交", "new_runtime_started": False}
save("continuation-budget.json", grant)
save("window-assignment.json", {"TASK": "TASK-111", "R": "R-105", "level": "A+", "window": "原110→111窗口",
                               "reason": "复用当前控制增量与证据，在完整时窗内连续收口，不换窗清账",
                               "state": "待人工转交，未派发/开始", "parallel": False, "audit_dispatched": False})

before = OUT / "before"
before.mkdir(exist_ok=True)
shared = ("DocuN/tasks/TASK-111.md", "DocuN/results/TASK-111-work-decision.md", "DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD")
for relative in shared:
    expected = next(row for row in inputs if row["path"] == relative)
    assert identity(ROOT / relative)["sha256"] == expected["sha256"]
    (before / relative.replace("/", "__")).write_bytes((ROOT / relative).read_bytes())
ledger_old = (ROOT / "DocuS/文档变更记录.MD").read_text(encoding="utf-8")
assert int(re.findall(r"CHG-(\d+)", ledger_old)[-1]) == 1159

def prefix(relative, text):
    assert "*" not in text and not any(line.startswith("|") for line in text.splitlines())
    old = (before / relative.replace("/", "__")).read_bytes()
    (ROOT / relative).write_bytes(text.encode("utf-8") + old)
    return {"path": relative, **identity(ROOT / relative), "old_suffix_sha256": hashlib.sha256(old).hexdigest()}

state_head = f"""# 执行动态文档

文档v2.35，2026-10-10，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.13、task_model/07。以下v2.34及原历史保字节。

## 111续作01部分返回，纠正分类停线与前置顺序，续作02待转交

原111A+已返回42608字节，当前报告与交回receipt匹配，合成覆盖源清单及七规则匹配；C01实现PARTIAL、证据PARTIAL/NOT_RUN、执行控制FAIL分类超限。新增Global owner/非空namespace/HostJob/监督归属和夹具候选，一次静态批，新增真实根/model/PG/API/browser/renderer均0。M01—M12完整未闭，不能提交稳定完整终审或签G11/B01/SEC003/STEP/M1/项目。

前向实施/离线经过7530.953超过3600达3930.953秒，最后源修改14:51:58早于15:09:03子截止，16:11:59才重新核时发现。包含等待/推理，旧unknown保持；不补造计时或追认合规。编排一小时分类硬门及全部故障前置不适配复杂收口，执行计时监测缺失；更有实际协调清场仍走业务门、Path拼接、准确屏障/create丢回包占位等未完成项，不能只是加次数或说纯审批阻断。

真实计数仍根6/9、Reaper2/3、离线7/旧8，renderer create1/start0、PG start5/6、API1/4、browser1/3、model4/6、Windows4/8、build1/3、frontend2/3。旧78加新6累计84根；real3630.157/offline64.234/cleanup17.5570978，C01新real0，旧费用13元/失败/UNKNOWN不清。精确PG目前Stopped/Pid0，preview对象空，18111/55451无监听及限定本卡进程空，只读元数据不签运行后TreeProof或退款。

主控签TASK-111-G11-C02-20261010，同TASK/R及原A+窗口，未验收同成果。新增综合窗21600，原总43200明确增加为64800，C02首读加6小时和旧固定总截止加6小时取更早，最晚本地2026-10-11 01:24:07。分类metadata/实施/离线和关联离线次数继续实记但不各设中间停线门，旧超限FAIL原样保留，不拿C02追认C01。根9/各3500、real14400剩10769.843、Reaper只余一次1200、PG只余一次及其它硬资源/产品限额完全不变，无第二份C01余额。

正常链只要求其必需控制/清场前置，立即取得两正常真实交互和树证明，再在同协调者补其余M矩阵；全故障夹具不挡首次正常，实际故障前须制齐。完整安全标准/终审不降。PG跨根托管，不在普通失败就stop耗完start；清场独立于业务/分类state，业务总截止前600秒收线。旧image/runtime及充分阶段证据复用，生产HTML默认关闭，用户库/私配/provider/付费/特权/Git/删除/发布0。主控未接管产品实现与运行。

续作02合同与Work/预算/窗口已完整保存待人工转交，未派发/开始；本批CHG1160—1169，下一1170，回收在DocuN/evidence/TASK-111/orchestration-receipt-02/。稳定完整G11后一次新隔离增强终审仍计划未发。旧G3—G10、107隔离与109反证/封存许可保持。

## 以下为v2.34及更早历史

"""
arch_head = """# 架构动态文档

文档v1.13，2026-10-10，Asia/Shanghai。需求v1.2、执行动态v2.35；以下v1.12及原历史保字节。G11-P110采用保持，111仍未完成完整候选。

## G11控制增量是候选，真实链尚未跑

C01增加Global部署owner与实际kernel对象查询候选、严格非空pid namespace前提、Windows CLI HostJob挂起创建/Assign/Resume及SUP/Reaper归属。源码增量和一批静态检查已保存，实际Windows互斥/Job/管道、Linux init与任务树、remote和PNG、停止恢复均没有新运行证据；renderer累计start0。不能凭Global字符串、ast或当前Stopped/Pid0签跨会话/树空。

description/compiler/有限模型边界、012四表/角色、runtime/image和原四账未变的阶段原件按实际字节继承。现夹具协调者只有root07，cleanup仍受业务门，故障路径拼接和准确竞争/丢回包占位等未完成，不能冒完整组合已就绪。教学父/边界产物未实际生成，升级fault/同COMMIT反例/最终浏览器未知，许可证缺项保持。

续作02只改执行控制和收口顺序，先正常所需安全前提与实际remote/止树，再同卡补完整故障/权限/竞争矩阵；完整安全必须项与一次新隔离终审不减。产品3次/180秒、reserve30—60/ready8/D-10、UNKNOWN保R、固定隔离、有限数据无代码出口与生产默认关闭都保持。新综合窗/旧超限属于执行账，不能拿时间授权反向豁免产品安全。

精确新PG/renderer资源继续原对象，不启动用户/旧库或公开部署。Compose本地依赖/构建候选、Linux/Nginx交付阶段和许可证/自包含放行原边界不变，G11/STEP/M1/项目未通过。

## 以下为v1.12及更早历史

"""
decision_head = f"""# TASK-111 / R-105 续作02编排纠正与明确许可

{stamp}，Codex编排Agent。已核原报告42608字节、当前合成源与必要控制源码/原件。回收C01为部分完成，新增静态/真实0，执行分类超限FAIL保持，不签稳定候选或G11最终通过。

编排承担一小时分类硬门及全部故障前置安排不匹配的责任；执行未连续监测计时，且完整runner/故障还未实现。调整依据不是泛称额度少，而是实际根6/9仍有3未用、renderer start0，C01清场和Path错误与占位直接源码已定界。原类别超限3930.953秒和历史unknown不抹去。

明确签发C02同范围完整续作，综合工作最多6小时，原总12小时增加6小时为18小时，实际截止C02首读加6小时与旧固定截止加6小时取更早，最晚本地2026-10-11 01:24:07。分类和关联离线检查实记、不再中间停线，旧C01规则当时失守仍FAIL。真实根/总14400、Reaper/所有硬资源/模型次数/产品限额及禁止权限保持，不新添一份C01未用额度。

先修正常运行必需的控制/独立清场/已知路径问题，立即取得两个真实正常remote和TreeProof；其余故障进入前制齐，而非全部前置再首次运行。保持全部M01—M12/安全/独审终点；代码消费者停后记录as-run再普通修正并新加载，PG唯一剩余启动由协调者跨根托管，普通错误不耗尽restart。没有新体系/引擎/用户数据/provider/付费/特权/Git/删除或发布许可。

原任务与证据仍同窗口优先，当前仅待人工转交。完整卡的新有效部分覆盖旧C01分类及截止，原文全保留；执行不得读到旧timing就又用旧门拦新许可。主控只维护文档与核证，没有自己修产品或运行验证。稳定完整成果后一次新隔离增强审计依然必需。

## 以下保留续作01及原授权历史

"""
changes = []
changes.append(prefix("DocuS/执行动态文档.MD", state_head))
contract = (OUT / "continuation-contract.md").read_text(encoding="utf-8")
changes.append(prefix("DocuN/tasks/TASK-111.md", contract))
changes.append(prefix("DocuN/results/TASK-111-work-decision.md", decision_head))
changes.append(prefix("DocuS/架构动态文档.MD", arch_head))
log_items = [
    ("DocuN/evidence/TASK-111/orchestration-receipt-02/returned-receipt.json", "回收C01，候选/静态/执行超限三轴保持，原件及失败不改"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-02/source-check.json", "合并最终源覆盖核匹配，当前动态不冒已验证"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-02/resource-recheck.json", "精确只读停止核查，非运行后TreeProof或退款"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-02/continuation-budget.json", "明确新增综合6小时和分类门纠正，旧超限不追认，所有真实资源/产品硬门原样"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-02/window-assignment.json", "原111 A+窗口待转交，无并行与审计派发"),
    ("DocuN/results/TASK-111-work-decision.md", "编排纠正因果与C02明确许可，旧失败/历史保持"),
    ("DocuN/tasks/TASK-111.md", "续作02完整七节，先正常真实链后按风险补完整矩阵，不再分类停线反复交回"),
    ("DocuS/架构动态文档.MD", "v1.13候选控制增量及真实未完成，不变产品安全/默认关闭"),
    ("DocuS/执行动态文档.MD", "v2.35唯一账更新真实C01部分返回与C02待转交，旧账不清"),
    ("DocuN/evidence/TASK-111/orchestration-receipt-02/delivery-proof.json", "一次文档/路径/历史/预算一致性检查，主控产品运行0")
]
ledger = ROOT / "DocuS/文档变更记录.MD"
old_ledger = (before / "DocuS__文档变更记录.MD").read_bytes()
add = "\n\n## 2026-10-10 TASK111续作01回收与C02编排纠正\n\n"
add += "\n\n".join(f"- CHG-{1160+index:04d}，{stamp}，Codex编排Agent，{path}。{why}。" for index,(path,why) in enumerate(log_items)) + "\n"
assert "*" not in add
ledger.write_bytes(old_ledger + add.encode("utf-8"))
changes.append({"path": "DocuS/文档变更记录.MD", **identity(ledger)})

for item in changes[:4]:
    assert (ROOT / item["path"]).read_bytes().endswith((before / item["path"].replace("/", "__")).read_bytes())
assert ledger.read_bytes().startswith(old_ledger)
assert identity(report_path)["sha256"] == report["sha256"]
req = next(row for row in inputs if row["path"] == "DocuS/最终需求文档.MD")
assert identity(ROOT / req["path"])["sha256"] == req["sha256"]
for title in ("目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源", "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"):
    assert contract.count("## " + title + "\n") == 1
assert 902913370092600 + 21600 * 1000000000 == grant["seconds"]["aggregate_deadline_ns_after"]
assert sum((grant["seconds"]["real_used"], grant["seconds"]["real_remaining"])) == grant["seconds"]["real_total_cap"]
assert caps["real_batches"] - used["real_batches"] == 3
assert all((ROOT / relative).is_file() for relative in shared)
proof = {"verified_local": dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(), "TASK": "TASK-111", "R": "R-105",
         "permit": grant["permit"], "state": "待人工转交", "complete_seven_sections": True, "one_document_consistency_check": True,
         "rules_matches": len(rules), "source_matches": len(checked), "report_and_requirements_unchanged": True,
         "history_original_bytes_preserved": True, "C01_breach_not_retroapproved": True,
         "hard_counts_unchanged": True, "original_plus_delta_time_arithmetic": True, "changed_documents": changes,
         "CHG": [1160,1169], "next_CHG": 1170, "orchestrator_product_runtime": False, "new_audit_dispatched": False}
save("delivery-proof.json", proof)
print(json.dumps({"saved": True, "report": report, "source_matches": len(checked), "rules_matches": len(rules),
                  "card": str(ROOT / "DocuN/tasks/TASK-111.md"), "card_identity": identity(ROOT / "DocuN/tasks/TASK-111.md"),
                  "state": "v2.35 待转交", "architecture": "v1.13 候选", "C01_breach_preserved": True,
                  "runtime_executed": False, "CHG": [1160,1169]}, ensure_ascii=False))
