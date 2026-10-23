"""Publish the bounded orchestration review; stdlib metadata only, no product imports."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
from datetime import datetime, timedelta, timezone


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "DocuN/evidence/TASK-120/execution/finalization-05"
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
STAMP = NOW.isoformat(timespec="microseconds")
DATE = NOW.date().isoformat()


def raw(path: Path) -> bytes:
    return path.read_bytes()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def owned(path: Path) -> Path:
    path = path.resolve()
    assert path.is_relative_to(ROOT), str(path)
    return path


def write(path: Path, data: bytes) -> None:
    path = owned(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".adoption06.tmp")
    assert not temporary.exists(), str(temporary)
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    assert path.read_bytes() == data


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def prefix(text: str, previous: bytes) -> bytes:
    return (text.strip() + "\n\n").replace("\n", "\r\n").encode("utf-8") + previous


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not (OUT / "save-proof.json").exists(), "Already published; inspect saved proof instead of republishing."
shared_names = [
    "DocuN/results/TASK-120-work-decision.md",
    "DocuS/架构动态文档.MD",
    "DocuS/执行动态文档.MD",
    "DocuN/tasks/TASK-120.md",
    "DocuS/文档变更记录.MD",
]
before = {name: raw(ROOT / name) for name in shared_names}
assert "文档v2.79" in before[shared_names[2]].decode("utf-8-sig")[:250]
assert "文档v1.51" in before[shared_names[1]].decode("utf-8-sig")[:250]
assert max(map(int, re.findall(r"CHG-(\d{4})", before[shared_names[4]].decode("utf-8-sig")))) == 1546

# The pinned seven files are checked, not silently upgraded to another rule version.
rules = load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
rule_checks = []
for item in rules:
    actual = sha(raw(Path(item["absolute_path"])))
    assert actual == item["sha256"], item["relative_path"]
    rule_checks.append({"path": item["absolute_path"], "sha256": actual, "match": True})
assert len(rule_checks) == 7

# Verify the returned snapshot without running the implementation or its tests.
identity = load(EVIDENCE / "final-file-identities.json")
assert len(identity["all_current_paths"]) == 202
identity_checks = []
for item in identity["all_current_paths"]:
    path = owned(ROOT / item["path"])
    actual = sha(raw(path)) if path.is_file() else None
    assert actual == item["sha256"], item["path"]
    identity_checks.append({"path": item["path"], "sha256": actual, "match": True})

report_path = ROOT / "DocuN/results/TASK-120-result.md"
report_raw = raw(report_path)
old_marker = "# TASK-120 / R-114 — 续验04结果（有限正常链通过；仍未完整，Q冻结）".encode("utf-8")
old_report = report_raw[report_raw.index(old_marker):]
assert len(old_report) == 65338
assert sha(old_report) == "85ed46c94bd38c8382a66112f9462e0e00e186715d364ec6790c24bc40d6430a"

ledger_path = ROOT / "DocuN/evidence/TASK-120/execution/budget.json"
events_path = ROOT / "DocuN/evidence/TASK-120/execution/events.jsonl"
ledger_raw, events_raw = raw(ledger_path), raw(events_path)
ledger = json.loads(ledger_raw.decode("utf-8-sig"))
assert ledger["active_root"] is None and ledger.get("active_command") is None
assert ledger["counts"]["roots"] == 40 and ledger["caps"]["roots"] == 64
assert ledger["counts"]["pg_starts"] == 39 and ledger["counts"]["browser_starts"] == 11
assert ledger["engineering_status"] == "FINALIZATION_05_PARTIAL_STOPPED_PERMISSION_AND_UI_GAPS"
assert len(ledger["failures"]) == 111
assert ledger["current_permit_id"] == "TASK-120-Q-PREP-FINALIZATION-05-20261019"
for key in ("provider_calls", "actual_fee_microunits", "preview_creates", "preview_starts", "Git_writes"):
    assert ledger["counts"][key] == 0

blocker = load(EVIDENCE / "scope-removal-blocker.json")
assert blocker["sqlstate"] == "42501" and blocker["application_role"]["delete_allowed"] is False
assert blocker["persistent_command"] is None and blocker["before_scope"] == blocker["after_scope"]
assert blocker["head_unchanged"] and blocker["fees_unchanged"] and blocker["grant_or_DDL_not_changed"]
ack = load(EVIDENCE / "ACK-matrix-PASS.json")
assert ack["status"] == "PASS" and ack["facts"]["three_separate_checkpoints"] is True
old503 = load(EVIDENCE / "old-scope-503-reconciliation.json")
assert old503["conclusion"] == "NOT_COMMITTED" and old503["no_resend"] is True
assert old503["mutation_command"] is None and old503["007"]["state"] == "received"
assert old503["007"]["payload_sha256"] == old503["007"]["actual_sha256"]
index = load(EVIDENCE / "final-review-index.json")
assert index["engineering_complete"] is False and index["stable_for_independent_audit"] is False
gaps = load(EVIDENCE / "remaining-gaps.json")
assert {entry["id"] for entry in gaps["gaps"]} == {"scope-removal", "late-namespace-DataContext"}

stop = load(EVIDENCE / "final-stop-proof.json")
r58, r59 = (load(EVIDENCE / f"command-{number}.receipt.json") for number in ("058", "059"))
assert stop["processes_jobs_ports_stopped"] and stop["all_fresh_stop_dimensions_confirmed"]
assert stop["metadata_read_problems"] == []
assert stop["docker_realtime"]["state"]["Running"] is False and stop["docker_realtime"]["state"]["Pid"] == 0
assert all(not value["listening"] for value in stop["ports"].values())
assert all(not value["same_identity_running"] for value in stop["registered_processes"])
for receipt in (r58, r59):
    assert receipt["tree_empty"] is True and receipt["exit_code"] == 0
wall = ledger["command_wall_conservative_upper_seconds"]
assert math.isclose(wall, 43972.006199 - 60 + r59["wall_seconds"], abs_tol=0.000001)
expired05 = datetime.fromisoformat("2026-10-20T20:04:46.848938+08:00")
assert NOW > expired05

evidence_names = [
    "final-review-index.json", "remaining-gaps.json", "acceptance-matrix.json",
    "source.diff", "fixture.diff", "final-file-identities.json", "financial-summary.json",
    "financial-final-separated.json", "scope-removal-blocker.json", "scope-diagnostic-PASS.json",
    "old-scope-503-reconciliation.json", "ACK-matrix-PASS.json", "ACK-accepted-COMMIT-PASS.json",
    "ACK-launch-claim-COMMIT-PASS.json", "ACK-result-COMMIT-PASS.json", "K2-head-PASS.json",
    "K2-revoke-PASS.json", "K2-scope-PASS.json", "K2-source-PASS.json",
    "K2-memory-persistent-reconciled.json", "UI-head-scope-root-33.json", "UI-head-scope-root-34.json",
    "UI-readonly-root-36.json", "readonly-actual-PG-body-closed-reconciled.json",
    "retained-original-Q-witness.json", "final-stop-proof.json", "command-058.receipt.json",
    "command-059.receipt.json", "candidate-package-identity.json", "old-packages-preserved.json",
]
protected = {report_path: sha(report_raw), ledger_path: sha(ledger_raw), events_path: sha(events_raw)}
evidence_checks = []
for name in evidence_names:
    path = EVIDENCE / name
    digest = sha(raw(path))
    protected[path] = digest
    evidence_checks.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest})
for item in identity_checks:
    if item["sha256"] is not None:
        protected[ROOT / item["path"]] = item["sha256"]
for name in ("AGENTS.md", "DocuS/原始需求文档.MD", "DocuS/最终需求文档.MD"):
    protected[ROOT / name] = sha(raw(ROOT / name))

proposal_path = OUT / "adoption-proposal.md"
proposal_sha = sha(raw(proposal_path))
sql_path = OUT / "015-permission-core.proposed.sql"
assert "待用户" in proposal_path.read_text(encoding="utf-8-sig")
assert not any((ROOT / "backend/migrations").glob("015*.sql")), "Unexpected migration015 exists."
protected[proposal_path] = proposal_sha
protected[sql_path] = sha(raw(sql_path))

verification = {
    "timestamp": STAMP, "role": "task_model orchestration; bounded read-only evidence review",
    "task": "TASK-120", "R": "R-114", "decision": "PARTIAL_ACCEPTANCE_ADOPTION_PENDING",
    "rules": rule_checks, "returned_identity_checks": identity_checks,
    "selected_evidence_hashes": evidence_checks,
    "returned_report": {"sha256": sha(report_raw), "bytes": len(report_raw),
                        "prior_suffix_bytes": len(old_report), "prior_suffix_sha256": sha(old_report)},
    "ledger_at_return": {"counts": ledger["counts"], "caps": ledger["caps"],
                         "failure_entries": len(ledger["failures"]),
                         "conservative_wall_after059_seconds": wall,
                         "report_wall_including059_reserve_seconds": 43972.006199,
                         "reconciliation": "Replace only the explicitly reserved final60s with actual059=5.203s; all earlier unknown reserves remain.",
                         "resource_holding_union_seconds": ledger["runtime_holding_union_seconds"],
                         "active_root": None, "active_command": None,
                         "business_window05_expired": True},
    "stop_proof_scope": {"original_stop_time": stop["utc"],
                         "process_identity_count": len(stop["registered_processes"]),
                         "job_identity_count": len(stop["registered_jobs"]),
                         "all_fresh_stop_dimensions_confirmed_at_that_time": True,
                         "filesystem059_exit0_tree_empty": True,
                         "main_did_not_query_current_Docker_or_retest_runtime": True},
    "proposal": {"id": "AP-120-06", "sha256": proposal_sha, "status": "PENDING_USER_ADOPTION",
                 "runtime_permit_issued": False, "permissions_modified": False},
    "scope_limitations": ["Not independent audit", "memory branch lacks immediately persisted pre-financial snapshot",
                          "Original FAIL/UNKNOWN retained", "Scope removal and namespace/fullDataContext UI remain incomplete"],
}
write(OUT / "input-verification.json", json_bytes(verification))
for name, data in before.items():
    write(OUT / "before" / name, data)
for name, data in (("TASK-120-result.md", report_raw), ("budget.json", ledger_raw), ("events.jsonl", events_raw)):
    write(OUT / "returned-snapshot" / name, data)

work = f"""
# TASK-120 / R-114 主控收尾05核证与AP-120-06采用裁定（当前有效：待用户决定）

{STAMP}。完整收尾05已返回；主控核对7锁定规则、202当前文件身份、本轮唯一产品diff、ACK/K2/UI逐项证据、旧503持久事实、四库分账、058停止与059文件保存回执、65338字节旧结果后缀。只作有限核证，不重跑业务，不冒充原118独审。

总验收部分通过，完整工程与稳定集中独审前置仍未满足。11项完整请求权限反例/重复批准、三种COMMIT丢确认、head/revoke/scope新增/source竞态及head/scope两项迟到UI按列明对象收存；memory按原trace和PG核证继承，缺即时before-financial快照的限制照留。旧scope503命令不存在且scope_revision1保持，判NOT_COMMITTED；对应模型committed/007 received和费用保留，未重发。根33整根FAIL不改绿，其独立head checkpoint与根34scope成功分开采纳。

本轮repository._apply_scope_locked只移除实际差集并upsert保留项，新增/版本更新实际PG通过。真正减去来源仍在应用角色命中42501，命令不存在、scope/head/费用不变；公共角色无该表DELETE是确定权限缺口，不能靠夹具改期望关闭。namespace/完整DataContext UI缺口也照留：根36先冻结后取得旧正常响应的次序错误，正确q_root_changed拒绝不等于迟到UI通过；matrix-final永久frozen，不解冻、不重建或续旧grant。

已保存唯一合并采用包AP-120-06：DocuN/evidence/TASK-120/orchestration-adoption06-20261020/adoption-proposal.md，SHA256 {proposal_sha}。推荐新增015，只给既有NOLOGIN retrolume_data_app在public.activity_scope_sources的DELETE，匹配精确版本指纹/旧R01-R02兼容；单表权限不是行级CAS，风险和回退已列。仅新隔离源库及真实正常恢复目标使用，旧001—014/四库/用户库不改。恢复工厂实际要求新容器+命名卷、verified job和restored_readonly，故包内明确一源逻辑库和至多一恢复目标，不再用frozen源冒充目标。先取两个真实正常批准响应再执行生产冻结/切换，分开验证完整mode/read_only与namespace，禁止伪造响应/selector。

采用状态待决，尚未发06许可、未GRANT/建库/创建资源/修改产品。锁定公共AGENTS第2节明确权限调整须有覆盖动作及范围的授权；原05禁止schema/profile/权限变化，“继续”不具体覆盖这项新增DELETE。采用后同TASK120/R114交刚完成05的原A窗口，原A+停止；最终完整稳定后由原118独立归属集中终审，不加逐小项审计。

原05业务窗已在2026-10-20T20:04:46.848938+08到期；原96h至2026-10-22T08:41:08.5687758Z及末1800保存期不变。账上root40/64、PG39/64、API44/96、Browser11/16、build4/8、Native59/128、HTTP1303/10000、111条失败记录，active_root/command空。059退出后唯一账wall={wall:.6f}/57600秒；报告43972.006199包含该次60秒预留，以实测5.203秒替换此项，不动早前未知预留。持有2443.530295/21600秒。次数未耗尽不恢复已过期时窗，不重置任何原账。

058原时点核511 PID/birth、113 Job、原CID stopped/Pid0和两端口；059只是文件保存且exit0/tree_empty。主控未做现时Docker/进程查询，未声称本次实时清场。Q/真实provider/实际费用/preview/Git继续冻结或0，旧S有限关闭保持；STEP018整体/019/020/M1/项目未放行。证据、旧共享和返回账快照已存本次orchestration-adoption06目录。

---

# 以下旧裁定原字节保留
"""
architecture = f"""
# 架构动态文档

文档v1.52，{DATE}，Asia/Shanghai。需求v1.4、执行动态v2.80、task_model/07；以下v1.51原字节保留。

## Q安全矩阵多数补足；范围移除缺权限、完整上下文UI缺证，采用包未生效

{STAMP}。TASK120完整收尾05的唯一产品增量为activities/repository.py::_apply_scope_locked：读取旧scope、只DELETE实际移除项、保留项ON CONFLICT更新版本/来源修订，事务/锁/CAS未扩展。新增与版本更新已在真实PG通过，实际移除仍42501、命令/scope/head/费用不变；当前013的应用角色仅有该表SELECT/INSERT/UPDATE，没有DELETE。001—014及schema/profile本轮未改。

11项全请求权限反例、三类COMMIT响应丢失及head/revoke/scope新增/source发送释放窗口已有证据；memory按原trace/后续持久核证收存但缺即时before-financial快照。head与scope迟到UI有独立PASS，namespace/完整DataContext仍未通过。根36真实frozen提交与UI失败分开，正确旧root拒绝不作为UI通过；原matrix-final永久冻结，不借缓存/旧批准恢复正常权利。

AP-120-06为待用户采用的最小方案，尚未实现：新增015仅补scope绑定表DELETE并维护精确指纹/兼容，不加业务表列/外部接口/费用/备份格式；风险是表级删除权，CAS由原受信仓储和guard承担。最后UI需先获取真实正常批准响应，再生产冻结及选择verified恢复只读目标；TargetFactory的正常独立容器/命名卷/restore job前置已源级核对并列入采用资源。当前无新增权限或资源，最终独立增强终审仍待，Q未启用。

## 以下为v1.51及更早历史
"""
state = f"""
# 执行动态文档

文档v2.80，{DATE}，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.52、task_model/07。以下v2.79原字节保留。

## TASK120完整收尾05已返回；部分验收，AP-120-06权限/最后UI采用待决

{STAMP}。主控只读核7锁定规则、202当前身份、本轮产品diff、ACK/K2/UI/503/金融原件和058—059回执，旧结果65338字节SHA256匹配。TASK120调度已返回、验收部分通过，完整工程及稳定独审前置未满足；没有重测或自签独审。11项完整请求权限反例、三类COMMIT丢确认、head/revoke/scope新增/source竞态与head/scope迟到UI收存；memory缺即时before-financial快照限制、全部旧FAIL/UNKNOWN照留，正常五入口/C12等充分旧项不重跑。

余项明确为两组：真实scope移除SQLSTATE42501，现应用角色缺activity_scope_sources DELETE，原许可禁扩权；namespace与完整DataContext迟到UI未通过，原matrix-final已永久frozen。已完成具体AP-120-06采用包与015权限核心审阅草案，仅放DocuN/evidence/TASK-120/orchestration-adoption06-20261020，未生成可执行06卡/permit。推荐单表DELETE及对应精确版本兼容、一个新隔离源库和至多一个正常恢复目标容器/卷，最后两UI先取正常响应再冻结/真实切换。用户尚未采用，权限/schema/profile/资源/运行时窗都未变；当前禁止新增业务运行。

实际账root40/64、PGstart39/64、API44/96、Browser11/16、build4/8、Native59/128、HTTP1303/10000、PG对象/卷各1/1，失败111条（不是111个独立缺陷），active_root/command空；旧117的81条另留。059回执退出后唯一预算wall保守{wall:.6f}/57600，持有2443.530295/21600秒约40.726分钟。报告43972.006199含059预留60，退出实测5.203替换后核账，所有更早unknown预留保持，不把calendar空档叫CPU工作。

旧scope503已核NOT_COMMITTED（原命令缺失/原scope_revision1），原模型committed/007 received/费用保留，不重发。四库分账保持：flow25/6250000、budget01 100/25000000、budget02 8/2000000、matrix-final23/5750000；不可合并作单实例额度。原三UNKNOWN事件序列不变，不退款不释放旧slot。

原05业务窗已到2026-10-20T20:04:46.848938+08，原96h截止2026-10-22T08:41:08.5687758Z/末1800保存门不变；剩余次数不恢复旧窗。058于2026-10-20T15:41:23.916100+08核511 PID/birth、113 Job、精确CID Running=false/Pid0、55480/18120无监听；059仅文件保存exit0/tree_empty。主控核证的是原停机时点，未执行现时Docker/资源查询。

下一动作只缺用户对AP-120-06的一个合并采用决定，原因是公共AGENTS第2节要求具体权限调整授权。采用后交刚完成05的原A工程窗口同号续作06，原A+停止；稳定包再集中独审。当前无在途任务，不占新TASK121/R115，不提前派独审。Q/真实provider/费用/preview/Git仍冻结或0；旧S不重开，STEP018整体/019/020/M1/项目未放行。主控未改产品/执行结果/唯一工程账。CHG1547—1551，下一1552。

## 以下为v2.79及更早历史
"""
task_notice = f"""
# TASK-120 / R-114 — 当前停止通知：完整收尾05已返回，AP-120-06待采用

{STAMP}。**本置顶通知优先于下面历史卡的“当前有效”字样。当前无新增运行许可，不是06执行卡。**

05已回传并有限核证，原业务时窗已在2026-10-20T20:04:46.848938+08到期。原A工程窗口保持停止，原A+同样停止；次数余量不重开旧时窗，不GRANT/建库/解冻/重绑旧批准。多数安全矩阵、ACK和head/scope UI按原证据收存；尚欠真实scope移除权限、namespace/完整DataContext迟到UI，Q继续冻结。

具体待采用包：D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-adoption06-20261020/adoption-proposal.md（SHA256 {proposal_sha}）。权限核心审阅草案同目录015-permission-core.proposed.sql，不是正式迁移，不可执行。待一个合并采用决定，主控才签同号06完整合同与精确前向许可给刚完成05的原A窗口；本通知不冒称已转交/开始。

完整核证：DocuN/results/TASK-120-work-decision.md置顶；唯一当前状态：DocuS/执行动态文档.MD v2.80。原首点/预算/失败/UNKNOWN/冻结状态和有效证据全保留；旧05及更早合同仅作为历史，不赋予过期运行权。

---

# 以下为原05及更早合同原字节
"""
new_values = {
    shared_names[0]: prefix(work, before[shared_names[0]]),
    shared_names[1]: prefix(architecture, before[shared_names[1]]),
    shared_names[2]: prefix(state, before[shared_names[2]]),
    shared_names[3]: prefix(task_notice, before[shared_names[3]]),
}
changes = [
    (1547, shared_names[0], "收尾05部分验收，核证旧503/ACK/K2与两组缺口；AP-120-06待采用，未扩权或签续验许可。"),
    (1548, shared_names[1], "v1.52记录scope差集/upsert唯一产品修补、实际移除权限缺口及最后UI未闭合；015/profile方案待决。"),
    (1549, shared_names[2], "v2.80登记05已返回/部分通过、059实际补账/旧窗到期，待一个权限资源合并采用决定。"),
    (1550, shared_names[3], "置顶停止通知及采用包导航；旧卡原字节保留为历史，未生成可执行06合同。"),
    (1551, "DocuN/evidence/TASK-120/orchestration-adoption06-20261020", "保存具体权限/资源/UI顺序采用包、审阅SQL、有限核证/旧共享/返回账快照及读回复核；主控未运行产品。"),
]
addition = "\r\n\r\n" + "\r\n\r\n".join(
    f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{name}。{description}"
    for number, name, description in changes
) + "\r\n"
new_values[shared_names[4]] = before[shared_names[4]] + addition.encode("utf-8")

# Do not overwrite concurrent shared work or changed engineering inputs.
for name, data in before.items():
    assert raw(ROOT / name) == data, f"Shared state drift: {name}"
for path, digest in protected.items():
    assert sha(raw(path)) == digest, f"Input drift: {path}"
for name in shared_names:
    write(ROOT / name, new_values[name])
for name in shared_names[:4]:
    assert raw(ROOT / name).endswith(before[name]), f"History suffix changed: {name}"
assert raw(ROOT / shared_names[4]).startswith(before[shared_names[4]])
for path, digest in protected.items():
    assert sha(raw(path)) == digest, f"Protected input changed: {path}"

proof = {
    "timestamp": STAMP, "status": "SAVED_AND_READ_BACK",
    "task": "TASK-120", "R": "R-114", "adoption": "AP-120-06_PENDING_USER_DECISION",
    "runtime_permit_issued": False, "product_or_runtime_operations": False,
    "proposal_sha256": proposal_sha, "rule_matches": 7, "returned_identity_matches": 202,
    "engineering_report_budget_events_evidence_unchanged": True,
    "prior_report_suffix_sha256": sha(old_report),
    "shared_history_byte_preservation": True,
    "writes": [{"path": name, "sha256": sha(raw(ROOT / name)), "bytes": len(raw(ROOT / name))}
               for name in shared_names],
    "CHG": [1547, 1548, 1549, 1550, 1551], "next_CHG": 1552,
}
write(OUT / "save-proof.json", json_bytes(proof))
print(json.dumps({"status": proof["status"], "rules": 7, "identities": 202,
                  "adoption": proof["adoption"], "runtime_permit_issued": False,
                  "shared_versions": ["2.80", "1.52"], "CHG": [1547, 1551],
                  "next_CHG": 1552, "proposal_sha256": proposal_sha}, ensure_ascii=False))
