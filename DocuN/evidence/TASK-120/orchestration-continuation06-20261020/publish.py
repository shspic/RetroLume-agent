"""Save the adopted manual handoff; stdlib filesystem/metadata only."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ADOPTION = ROOT / "DocuN/evidence/TASK-120/orchestration-adoption06-20261020"
EXECUTION = ROOT / "DocuN/evidence/TASK-120/execution"
NOW = datetime.now(timezone(timedelta(hours=8)))
STAMP = NOW.isoformat(timespec="microseconds")
PERMIT_ID = "TASK-120-Q-PREP-CONTINUATION-06-20261020"
APPROVED_SHA = "3884a5c056cb13f0216c59652a408ea57edbbc5064d429b5d2ea783f172c5c70"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, data):
    path = path.resolve()
    assert path.is_relative_to(ROOT), path
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".continuation06.tmp")
    assert not temporary.exists(), temporary
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    assert path.read_bytes() == data


def save_json(path, data):
    save(path, (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def head(text, old):
    return (text.strip() + "\n\n").replace("\n", "\r\n").encode("utf-8") + old


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not (OUT / "save-proof.json").exists(), "Already saved; inspect the proof."
proposal = ADOPTION / "adoption-proposal.md"
assert digest(proposal.read_bytes()) == APPROVED_SHA
previous_proof = load(ADOPTION / "save-proof.json")
assert previous_proof["status"] == "SAVED_AND_READ_BACK" and previous_proof["next_CHG"] == 1552
shared = ["DocuN/results/TASK-120-work-decision.md", "DocuS/架构动态文档.MD",
          "DocuS/执行动态文档.MD", "DocuN/tasks/TASK-120.md", "DocuS/文档变更记录.MD"]
before = {name: (ROOT / name).read_bytes() for name in shared}
for entry in previous_proof["writes"]:
    assert digest(before[entry["path"]]) == entry["sha256"], entry["path"]
assert max(map(int, re.findall(r"CHG-(\d{4})", before[shared[4]].decode("utf-8-sig")))) == 1551

rules = load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
rule_matches = []
for entry in rules:
    actual = digest(Path(entry["absolute_path"]).read_bytes())
    assert actual == entry["sha256"], entry["relative_path"]
    rule_matches.append({"path": entry["absolute_path"], "sha256": actual})
assert len(rule_matches) == 7

identities = load(EXECUTION / "finalization-05/final-file-identities.json")["all_current_paths"]
protected = {}
for entry in identities:
    path = (ROOT / entry["path"]).resolve()
    assert path.is_relative_to(ROOT)
    actual = digest(path.read_bytes()) if path.is_file() else None
    assert actual == entry["sha256"], entry["path"]
    if actual is not None:
        protected[path] = actual
assert len(identities) == 202
for name in ("budget.json", "events.jsonl"):
    protected[EXECUTION / name] = digest((EXECUTION / name).read_bytes())
for name in ("DocuN/results/TASK-120-result.md", "AGENTS.md", "DocuS/原始需求文档.MD", "DocuS/最终需求文档.MD"):
    protected[ROOT / name] = digest((ROOT / name).read_bytes())
protected[proposal] = APPROVED_SHA
ledger = load(EXECUTION / "budget.json")
assert ledger["active_root"] is None and ledger.get("active_command") is None
assert ledger["counts"]["roots"] == 40 and ledger["counts"]["pg_starts"] == 39
assert ledger["counts"]["browser_starts"] == 11 and len(ledger["failures"]) == 111
assert ledger["engineering_status"] == "FINALIZATION_05_PARTIAL_STOPPED_PERMISSION_AND_UI_GAPS"
assert ledger["current_permit_id"] == "TASK-120-Q-PREP-FINALIZATION-05-20261019"
assert abs(ledger["command_wall_conservative_upper_seconds"] - 43917.209199) < 0.000001
assert NOW < datetime.fromisoformat("2026-10-22T08:41:08.5687758+00:00") - timedelta(seconds=1800)

old_caps = ledger["caps"]
new_caps = dict(old_caps, pg_objects=2, volumes=2)
assert old_caps["pg_objects"] == 1 and old_caps["volumes"] == 1
assert new_caps["pg_create_attempts"] == 2 and new_caps["volume_create_attempts"] == 2
contract_path = OUT / "contract-06.md"
contract_bytes = contract_path.read_bytes()
contract = contract_bytes.decode("utf-8-sig")
required_contract = [PERMIT_ID, APPROVED_SHA, "原A独占工程窗口", "015_activity_scope_delete_permission.sql",
    "完整DataContext", "namespace", "retrolume_task120_scope_ui_final", "retrolume-task120-scopeui-ro1",
    "43917.209199", "13682.790801", "2026-10-22T08:41:08.5687758Z", "## A.", "## B.", "## C.",
    "## 停止、精确清场与回传", "## 必要人工与待同步"]
assert all(value in contract for value in required_contract)
assert "〈" not in contract and "TODO" not in contract

approval = {
    "adoption_id": "AP-120-06", "user_reply_verbatim": "批准",
    "observed_and_recorded_by_orchestrator_at": STAMP,
    "approved_proposal_path": proposal.relative_to(ROOT).as_posix(), "approved_proposal_sha256": APPROVED_SHA,
    "scope": "One table DELETE; exact version compatibility; bounded isolated source/verified restore target and remaining UI proof",
    "proposal_pending_wording_retained_as_historical_text": True,
    "real_Q_or_real_provider_or_user_database_or_publication_authorized": False,
    "actual_executor_receipt_time": "NOT_YET_REPORTED",
}
permit = {
    "id": PERMIT_ID, "issued_at": STAMP, "task": "TASK-120", "R": "R-114", "STEP": "STEP018",
    "parent_permit": ledger["current_permit_id"], "adoption": approval,
    "kind": "prospective_TESTONLY_scope_permission_and_remaining_context_UI",
    "receiver": "Continue original A exclusive engineering window that returned finalization05; old A+ stays stopped",
    "execution_status": "SAVED_READABLE_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED_OR_STARTED",
    "contract_sha256": digest(contract_bytes),
    "old_counts_at_return": ledger["counts"], "old_caps": old_caps, "new_cumulative_caps": new_caps,
    "only_counter_cap_changes": {"pg_objects": [1, 2], "volumes": [1, 2]},
    "additional_named_logical_database": {"name": "retrolume_task120_scope_ui_final", "fixture_slot": "scope-ui-final",
        "create_attempt_cap": 1, "objects_cap": 1, "new_application_role_if_needed": "retrolume_task120_scopeui_app",
        "old_matrix_final_database_counter_1_of_1_retained": True},
    "permissions": {"migration": "backend/migrations/015_activity_scope_delete_permission.sql",
        "grant": "DELETE", "table": "public.activity_scope_sources", "grantee": "retrolume_data_app",
        "grantee_is_existing_NOLOGIN_application_group": True,
        "risk": "Table-level DELETE; row/activity CAS remains enforced by trusted repository and existing guard, not by ACL",
        "execution_databases": ["retrolume_task120_scope_ui_final", "retrolume_task120_scopeui_ro"],
        "exact_forward_profile_compatibility_adaptation_allowed": True,
        "old_R01_R02_constants_migrations001_to014_and_old_database_ACLs_unchanged": True,
        "no_other_table_DELETE_TRUNCATE_PUBLIC_or_administrative_grants": True,
        "pre_execution_permission_risk_check_required": True},
    "command_wall_cap_seconds": 57600,
    "old_conservative_command_wall_seconds_retained": ledger["command_wall_conservative_upper_seconds"],
    "remaining_command_wall_seconds_at_issue": 57600 - ledger["command_wall_conservative_upper_seconds"],
    "runtime_holding_union_cap_seconds": 21600,
    "old_holding_seconds_retained": ledger["runtime_holding_union_seconds"],
    "old_failures_retained": 111, "TASK117_old_failures_retained": 81,
    "actual_first_tool_utc_unchanged": ledger["actual_first_tool_utc"],
    "calendar_deadline_utc_unchanged": ledger["calendar_deadline_utc"],
    "maximum_finish_window_seconds_from_actual_receipt": 43200,
    "finish_deadline_rule": "min(recorded actual receipt + 43200s, original calendar_deadline)",
    "business_deadline_rule": "finish_deadline minus 1800s; final1800s cleanup/save only",
    "new_TESTONLY_grant_until_rule": "not later than business_deadline",
    "actual_receipt_must_be_recorded_before_first_new_tool": True,
    "no_window_reset_from_interruption_or_continue_message": True,
    "old_grants_activities_roots_and_frozen_samples_not_extended_thawed_or_rebound": True,
    "root_ids_begin_at": 41, "command_ids_begin_after": 59,
    "real_root_cap_seconds": 1800, "root_cleanup_reserve_seconds": 120,
    "metadata_batch_cap_seconds": 60, "test_build_subbatch_cap_seconds": 300,
    "container_id": "b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f",
    "container_name": "retrolume-task120-qprep-pg1", "volume": "retrolume-task120-qprep-data",
    "image_id": "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f",
    "original_source_permit_label_unchanged": "TASK-120-Q-PREP-IMPLEMENTATION-20261018",
    "ports": {"source_pg": 55480, "api": 18120},
    "old_databases_no_write": ["retrolume_task120_flow", "retrolume_task120_budget_01", "retrolume_task120_budget_02", "retrolume_task120_matrix_final"],
    "new_restore_target": {"factory": "backend/app/data_exit/restore.py::TargetFactory.allocate",
        "maximum_new_containers": 1, "maximum_new_named_volumes": 1,
        "name": "retrolume-task120-scopeui-ro1", "volume": "retrolume-task120-scopeui-ro1-data",
        "database": "retrolume_task120_scopeui_ro", "port_candidates_ordered": [55481, 55482],
        "port_rule": "Freeze first actually bindable loopback candidate before allocation; no changes after collision",
        "image_id": "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f",
        "cpu": 1, "memory_bytes": 536870912, "pids_limit": 128, "restart": "no", "host_bind_mounts": False,
        "labels": "Normal factory retrolume.data.job/profile/target/purpose matched to actual registry",
        "target_CID_recorded_immediately_after_actual_create": True,
        "target_credentials_created_by_factory_only": True,
        "requires_normal_backup_restore_verified_job_activate_readonly_and_readonly_probe": True,
        "no_manual_selector_verified_receipt_or_frozen_source_as_target": True},
    "only_frozen_TASK116_eight_text_inputs": True,
    "activity_roster": [
        {"id": "01800000-0000-4000-8000-000000000001", "requests": 48, "cost_microunits": 12000000},
        {"id": "01800000-0000-4000-8000-000000000002", "requests": 28, "cost_microunits": 7000000},
        {"id": "01800000-0000-4000-8000-000000000003", "requests": 24, "cost_microunits": 6000000}],
    "synthetic_global_limit": {"requests": 100, "cost_microunits": 25000000, "per_call_microunits": 250000, "max_running_seconds": 3600},
    "late_UI_order": ["finish permission/scope normal checks", "capture two actual approved GET200 responses while source normal",
        "production freeze/read_only and full DataContext observed", "release first old response and checkpoint",
        "normal verified restore target selected and namespace observed", "release second old response and checkpoint"],
    "normal_backup_may_freeze_source_so_capture_responses_before_that_point": True,
    "memory_minimum_MiB": {"PG_API": 512, "browser_single_headless_page": 512, "stop_below_two_samples": 256},
    "memory_poll_seconds": 1,
    "no_sandbox_auth_outbound_guard_approval_bypass": True,
    "source_target_overlap_only_when_normal_restore_activation_requires": True,
    "no_repeat_of_sufficient_old_ACK_matrix_normal_five_entries_or_common100_baseline": True,
    "old_memory_pre_financial_snapshot_limit_retained_for_final_audit": True,
    "final_independent_audit_required_after_complete_stable_candidate": True,
    "real_Q": "FROZEN", "real_provider_fee_preview_Git_new_budget": 0,
    "main_did_not_mutate_engineering_ledger_or_execute_product": True,
    "executor_append_only_adoption_after_actual_receipt_only": True,
}

for name, data in before.items():
    save(OUT / "before" / name, data)
for name in ("budget.json", "events.jsonl"):
    save(OUT / "returned-snapshot" / name, (EXECUTION / name).read_bytes())
save_json(OUT / "approval.json", approval)
save_json(OUT / "permit.json", permit)
save_json(OUT / "input-verification.json", {
    "timestamp": STAMP, "proposal_sha256": APPROVED_SHA, "user_approval": "批准",
    "rules": rule_matches, "current_202_file_identity_matches": True,
    "prior_adoption_review": "DocuN/evidence/TASK-120/orchestration-adoption06-20261020/input-verification.json",
    "prior_review_still_applicable": True,
    "returned_report_budget_events_hashes": {str(path.relative_to(ROOT)): value for path, value in protected.items()
        if path == EXECUTION / "budget.json" or path == EXECUTION / "events.jsonl" or path.name == "TASK-120-result.md"},
    "active_root": None, "active_command": None, "current_Docker_not_queried_by_main": True,
    "no_runtime_permission_recheck_required_from_user_for_approved_scope": True,
    "permit_sha256": digest((OUT / "permit.json").read_bytes()), "contract_sha256": digest(contract_bytes),
})

decision = f"""
# TASK-120 / R-114 主控AP-120-06采用与续作06裁定（当前有效）

{STAMP}。用户对主控给出的唯一AP-120-06明确回复“批准”，采用原件SHA256 {APPROVED_SHA}。权限/精确版本适配、隔离资源与至多12h补证窗获准；原提案待决文字保留为历史。05仍为部分验收，历史FAIL/UNKNOWN及权限门失败不改绿；采用不等于015已实现或动态通过。

签发前向{PERMIT_ID}，沿原TASK120/R114继续刚完成05的原A最强工程窗口，原A+停止，不另开实现窗/子Agent；完整A—D卡保存读回后待人工转交，未冒称工程已收到/开始。A为015仅授既有NOLOGIN retrolume_data_app在public.activity_scope_sources DELETE及精确前向profile/旧R01-R02兼容；B为合法实际scope收缩与仅此K2窗口；C为先捕获真实正常批准响应、再生产冻结及verified恢复目标切换的两项迟到UI；D为最终身份/金融分账/复用/失败与精确清场。普通修正留同卡，稳定后集中独审，不重复充分旧项。

这是表级权限，接受受信应用可直接删除本库绑定的风险；正常CAS/活动边界由既有仓储/guard保持，不虚构行级ACL。仅新增015与对应严格版本/权限识别，001—014/原R01-R02常量、用户库/旧四库/金融/公开wire/备份格式不改；不授其他表DELETE/TRUNCATE/PUBLIC/管理权。执行真实GRANT前须先做工程风险检查，工程自检不冒充独审。原冻结目标和过期批准不延长/重绑。

资源仅原CID/卷新增retrolume_task120_scope_ui_final（尝试/对象各1），必要本库新最小应用角色；至多一只生产TargetFactory正常创建的retrolume-task120-scopeui-ro1及同名-data命名卷、独立retrolume_task120_scopeui_ro。原本机完整镜像、1CPU/512MiB/pids128/restart=no、loopback55481/55482先验固化、无host bind；源55480/API18120不改。工厂须真实backup/restore/verify/activate_readonly，不手写selector或verified；新实际CID及时登记并精确停止，保留全部数据/对象，不prune/drop。

不重置root40、PG39、API44、Browser11、build4、Native59、HTTP1303、111失败、wall43917.209199/57600、持有2443.530295/21600及所有unknown预留/旧117历史。现有次数cap64/64/96/16/8/128/10000和wall/持有cap均不增；只把实际PG对象/卷cap1→2，原create尝试cap2（各已1）仍只余1。新增逻辑库计数单列，不清旧matrix-final1/1。12h是从真实接收起的日历窗，不新增wall；finish=min(receipt+43200,原2026-10-22T08:41:08.5687758Z)，末1800清场保存，不因继续消息重开。

主控重核7规则/202身份与未动原账，只保存合同/许可/采用记录和共享状态，未改产品/执行报告/预算/事件或运行资源。Q/真实provider/实际费用/preview/Git仍冻结或0；独立终审未启动，不占121/R115，不签STEP018整体/019/020/M1/项目。原scope503核销、ACK/K2/head-scope及memory证据限制按05接受范围继承。

---

# 以下旧裁定原字节保留
"""
architecture = f"""
# 架构动态文档

文档v1.53，{NOW.date().isoformat()}，Asia/Shanghai。需求v1.4、执行动态v2.81、task_model/07；以下v1.52原字节保留。

## AP-120-06已采用，单表权限及最后上下文UI增量待实施

{STAMP}。用户批准既定AP-120-06（原件SHA256 {APPROVED_SHA}）。采用新增015向retrolume_data_app授activity_scope_sources DELETE、精确前向权限/profile兼容及最小隔离合成源/真实恢复目标路线；权限仍为表级，CAS由原受信仓储和运行guard承担。001—014与旧R01-R02常量/合法旧包识别不改，业务列/金融/公开HTTP/备份格式不扩展。此为采用状态，不是代码已实现或运行通过。

续作06将真实scope移除及其K2收缩窗口、完整DataContext同namespace的mode/read_only变化、verified恢复选择导致namespace变化合并交原A工程窗口。先取真实正常批准响应再freeze/backup/selector，旧frozen matrix不解冻。普通修复同卡，已充分原安全/ACK/五入口/预算证据继承；最后稳定包集中独审。Q继续冻结，主控无产品运行。

## 以下为v1.52及更早历史
"""
state = f"""
# 执行动态文档

文档v2.81，{NOW.date().isoformat()}，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.53、task_model/07。以下v2.80原字节保留。

## AP-120-06已获用户批准；同号续作06完整合同已保存，待转交原A窗口

{STAMP}。用户对前一合并包明确回复“批准”；原件SHA256 {APPROVED_SHA}。主控重核7规则与202文件/原报告/原唯一budget-events未漂移，只登记采用和签发{PERMIT_ID}。TASK120原05调度已返回/验收部分通过；续作06已登记且合同可读、待人工转交，尚无工程接收/开始事实。

继续刚完成05的原A独占最强工程窗口，原A+停止，不换窗/委派。合同D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-120.md置顶06；精确permit/批准记录/输入核对/旧共享与返回账快照在DocuN/evidence/TASK-120/orchestration-continuation06-20261020/。A—D合并完成单表DELETE/精确版本兼容、scope真正收缩、完整DataContext与namespace两迟到UI、最终证据/金融/清场；已有充分矩阵和基线不重跑。旧memory快照限制、所有旧FAIL/UNKNOWN保留。

015仅作用新隔离合成源retrolume_task120_scope_ui_final及正常恢复目标，旧001—014/四库/原R01-R02常量/用户库不动。准许原CID/卷一个新逻辑库和至多一个生产TargetFactory创建的retrolume-task120-scopeui-ro1/同名-data卷，固定原镜像与1CPU/512MiB/pids128/loopback。真实backup/restore/verify/activate_readonly前置保持，先捕获正常响应再不可逆freeze/切换；不伪造selector/只读目标，不延旧grant或解冻matrix。

旧已用root40/64、PG39/64、API44/96、Browser11/16、build4/8、Native59/128、HTTP1303/10000、111失败照留。仅PG实际对象/卷cap1→2，原create尝试cap2各已用1；新源逻辑库创建尝试/对象各1单列。wall保守43917.209199/57600、持有2443.530295/21600及早前unknown预留不改。新日历窗从工程实际接收至多12h，仍不晚原96h截止2026-10-22T08:41:08.5687758Z且最后1800只清场保存，不新增wall/根等上限。

实际接收后执行者才append-only登记新permit/caps/接收UTC、预期command060/root41续号和新目标实际CID；主控未改工程账/产品/结果或启动资源。原058—059停止证明继承为原时点，不冒称本次实时Docker核查。Q/真实provider/费用/preview/Git仍冻结或0；旧S有限关闭保持，最终独立增强终审待稳定包，不占新TASK121/R115，不签STEP018整体/019/020/M1/项目。CHG1552—1556，下一1557。

## 以下为v2.80及更早历史
"""
new_values = {
    shared[0]: head(decision, before[shared[0]]),
    shared[1]: head(architecture, before[shared[1]]),
    shared[3]: head(contract, before[shared[3]]),
    shared[2]: head(state, before[shared[2]]),
}
changes = [
    (1552, shared[0], "记录用户批准AP-120-06和同号续作06裁定；单表DELETE/严格兼容/精确资源已授权，未冒称实现。"),
    (1553, shared[1], "v1.53登记已采用的015权限/兼容和正常恢复目标/UI路线，实施验证仍待。"),
    (1554, shared[2], "v2.81登记批准、原A同窗续作06已保存待转交、原账不重置及仅对象cap变化。"),
    (1555, shared[3], "置顶完整同号续作06 A—D合同，旧停止通知/合同原字节留作历史。"),
    (1556, "DocuN/evidence/TASK-120/orchestration-continuation06-20261020", "保存用户批准绑定、精确前向permit、合同快照、有限核对/旧共享与原账快照、保存读回；主控无产品运行。"),
]
new_values[shared[4]] = before[shared[4]] + ("\r\n\r\n" + "\r\n\r\n".join(
    f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{name}。{description}"
    for number, name, description in changes) + "\r\n").encode("utf-8")

for name, data in before.items():
    assert (ROOT / name).read_bytes() == data, f"Shared state changed: {name}"
for path, old_hash in protected.items():
    assert digest(path.read_bytes()) == old_hash, f"Protected input changed: {path}"
for name in (shared[0], shared[1], shared[3]):
    save(ROOT / name, new_values[name])
assert (ROOT / shared[3]).read_bytes().startswith(head(contract, b""))
# Only mark the manual handoff ready once the full saved card has been read back.
save(ROOT / shared[2], new_values[shared[2]])
save(ROOT / shared[4], new_values[shared[4]])
for name in shared[:4]:
    assert (ROOT / name).read_bytes().endswith(before[name]), name
assert (ROOT / shared[4]).read_bytes().startswith(before[shared[4]])
for path, old_hash in protected.items():
    assert digest(path.read_bytes()) == old_hash, f"Protected input changed: {path}"
saved_permit = load(OUT / "permit.json")
assert saved_permit["new_cumulative_caps"] == new_caps
assert all(saved_permit["new_cumulative_caps"][key] == old_caps[key]
           for key in old_caps if key not in {"pg_objects", "volumes"})
save_json(OUT / "save-proof.json", {
    "timestamp": STAMP, "status": "SAVED_READ_BACK_AWAITING_MANUAL_HANDOFF",
    "task": "TASK-120", "R": "R-114", "adoption": "AP-120-06_APPROVED_BY_USER",
    "permit_id": PERMIT_ID, "contract_sha256": digest(contract_bytes),
    "permit_sha256": digest((OUT / "permit.json").read_bytes()),
    "actual_executor_receipt_or_start_claimed": False, "product_runtime_operations": False,
    "rules_match": 7, "current_identities_match": 202,
    "original_report_budget_events_product_and_approved_proposal_unchanged": True,
    "shared_history_original_bytes_preserved": True,
    "writes": [{"path": name, "sha256": digest((ROOT / name).read_bytes()), "bytes": (ROOT / name).stat().st_size}
               for name in shared], "CHG": [1552, 1553, 1554, 1555, 1556], "next_CHG": 1557,
})
print(json.dumps({"status": "SAVED_READ_BACK_AWAITING_MANUAL_HANDOFF", "permit": PERMIT_ID,
                  "rules": 7, "current_identities": 202, "contract_bytes": len(contract_bytes),
                  "state_version": "2.81", "architecture_version": "1.53", "next_CHG": 1557}, ensure_ascii=False))
