"""主控限定文档收口，复用既有独审和运行证据，不执行产品。"""

from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
HERE = Path(__file__).resolve().parent
CORR = ROOT / "DocuN/evidence/TASK-123/execution/correction-01"
EXECUTION = ROOT / "DocuN/evidence/TASK-123/execution"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def raw(path):
    return Path(path).read_bytes()


def sha(data):
    return sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def norm(value):
    p = Path(str(value).replace("\\\\", "/").replace("\\", "/"))
    return p if p.is_absolute() else ROOT / p


def save_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


report_path = ROOT / "DocuN/results/TASK-123-result.md"
report = raw(report_path)
pre = load(CORR / "pre-snapshot.json")
original_report = pre["original_result"]
original_suffix = report[-original_report["bytes"]:]
assert sha(original_suffix) == original_report["sha256"] == "d64c3abb832589ab9f826e0327f97a64bd1c2df7c62a9d4b63684f2549886c36"
rows = []


def identity(path, expected, scope):
    p = norm(path)
    data = raw(p)
    mode = "original_report_preserved_as_suffix" if p == report_path and expected == original_report["sha256"] else "current_file"
    actual = sha(original_suffix) if mode != "current_file" else sha(data)
    rows.append({"path": p.as_posix(), "expected": expected, "actual": actual,
        "current_full_file_sha256": sha(data), "mode": mode, "scope": scope, "match": expected == actual})


for row in pre["inputs"]:
    identity(row["path"], row["sha256"], "35_frozen_inputs")
for row in pre["old_execution_files"]:
    identity(row["path"], row["sha256"], "49_original_execution_files")
for row in pre["old_delivery_manifest_rows"]:
    identity(row["path"], row["sha256"], "48_original_manifest_references")
for row in pre["product_files"]:
    identity(row["path"], row["post_sha256"], "six_passed_files")
for row in load(CORR / "source-relations.json")["sources"]:
    identity(row["path"], row["sha256"], "six_original_requirement_and_source_facts")
mapping = load(CORR / "original-to-corrected.json")
for pair in mapping["pairs"]:
    for key in ("original", "corrected"):
        row = pair[key]
        identity(row["path"], row["sha256"], "original_and_current_document_pairs")
seal = load(CORR / "save-proof.json")
identity(seal["current_result"]["path"], seal["current_result"]["sha256"], "current_unified_report")
audit_seal = load(ROOT / "DocuN/evidence/TASK-124/audit/save-proof.json")
for row in audit_seal["artifact_and_report_rows"]:
    identity(row["path"], row["sha256"], "unchanged_independent_audit")

old_finite = load(EXECUTION / "finite-inputs.json")
finite = load(CORR / "finite-inputs.json")
readback = finite["progress_reason_readback_contract"]
withdrawn = finite["withdrawn_reference"]
handoff = (CORR / "deployment-handoff.md").read_text(encoding="utf-8-sig")
checks = {
    "disabled_and_no_activation": finite["enabled"] is False,
    "original_HTML_object_unchanged": finite["html"] == old_finite["html"],
    "wrong_write_mapping_removed": "continuation_reason" not in finite and "allowed_local_projection" not in json.dumps(finite),
    "reference_not_written_or_sent": withdrawn["persisted"] is False and withdrawn["include_in_model_context"] is False and withdrawn["is_input"] is False and withdrawn["write_operation"] is None,
    "reference_original_text_retained_only": withdrawn["text"] == old_finite["continuation_reason"]["text"],
    "existing_progress_reason_contract": readback["existing_commit"]["action"] == "evaluate" and readback["existing_commit"]["saved_kind"] == "progress" and readback["existing_commit"]["saved_field"] == "body.reason",
    "no_extra_reason_action_or_paid_request": readback["extra_reason_write_action"] is None and readback["extra_model_or_query_requests"] == 0,
    "no_fabricated_runtime_ids_or_values": all(value is None for value in readback["actual"].values()) and readback["actual_runtime_evidence"] is None,
    "explicit_nonshortcut_contract": {"correct", "select_node", "answer", "goal"}.issubset(readback["forbidden_reason_storage_shortcuts"]),
    "new_handoff_links_new_finite": "execution/correction-01/finite-inputs.json" in handoff,
    "correct_not_offered_as_reason_storage": "不得用correct、select_node、answer、goal" in handoff and "先GET原evaluate业务键" in handoff,
    "unchanged_fixed_matrix": finite["inherited_matrix"] == old_finite["inherited_matrix"],
    "original_unified_report_suffix_preserved": sha(original_suffix) == original_report["sha256"],
}
for name, text_object in (("HTML", finite["html"]), ("withdrawn_reference", withdrawn)):
    data = text_object["text"].encode("utf-8")
    checks[name + "_bytes_and_hash"] = len(data) == text_object["utf8_bytes"] and sha(data) == text_object["sha256"]
doc_check = load(CORR / "document-consistency.json")
closing = load(CORR / "closing-receipt.json")
checks["one_original_document_check_exit_zero"] = doc_check["check_count"] == 1 and doc_check["passed"] is True and doc_check["exit_code"] == closing["one_document_check"]["exit_code"] == 0
budget = load(CORR / "budget.json")
checks["budget_and_original_caps_preserved"] = budget["new_total_conservative_charge_seconds"] == 3710.557411 and budget["new_conservative_charge_seconds"] == 156 and budget["product_tests_used"] == "3/3 frozen" and budget["new_product_imports_tests_runtime_network_cost"] == 0
passed = all(row["match"] for row in rows) and all(checks.values())
verification = {"at": NOW, "purpose": "主控限定文档核证，非新独审或产品验证", "identity_count": len(rows), "rows": rows,
    "mismatches": [row for row in rows if not row["match"]], "document_checks": checks,
    "actual_document_check_boolean_entries": len(doc_check["checks"]),
    "closing_receipt_reported_checks_passed": closing["one_document_check"]["checks_passed"],
    "metadata_count_limit": "收尾概数与document-consistency布尔项数不同则按实际JSON项采纳；不据概数补造验证，不因此新开修复。",
    "semantic_review": "两份更正文档全文读入；既有FR010/116 M06与progress理由源码关系沿上轮已核字节复用",
    "passed": passed, "product_or_test_runtime": 0}
save_json(HERE / "return-check.json", verification)
assert passed, {"identities": verification["mismatches"], "checks": [key for key, value in checks.items() if not value]}

paths = {"state": ROOT / "DocuS/执行动态文档.MD", "architecture": ROOT / "DocuS/架构动态文档.MD",
    "changes": ROOT / "DocuS/文档变更记录.MD", "task123": ROOT / "DocuN/tasks/TASK-123.md", "task124": ROOT / "DocuN/tasks/TASK-124.md",
    "decision123": ROOT / "DocuN/results/TASK-123-work-decision.md", "decision124": ROOT / "DocuN/results/TASK-124-work-decision.md"}
old = {key: raw(path) for key, path in paths.items()}
assert "文档v2.91" in old["state"].decode("utf-8-sig").splitlines()[2]
assert "文档v1.63" in old["architecture"].decode("utf-8-sig").splitlines()[2]
assert "CHG-1621" in old["changes"].decode("utf-8-sig")[-2500:]
assert "CHG-1622" not in old["changes"].decode("utf-8-sig")
before = HERE / "before"
before.mkdir(exist_ok=False)
for key, value in old.items():
    (before / (key + ".bytes")).write_bytes(value)

effective = [{"path": pair["corrected"]["path"], "sha256": pair["corrected"]["sha256"],
    "superseded_original_path": pair["original"]["path"], "superseded_original_sha256": pair["original"]["sha256"]} for pair in mapping["pairs"]]
receipt = {"schema": "retrolume.task123.finite-preparation-closure.v1", "at": NOW,
    "task": "TASK-123", "R": "R-117", "acceptance_scope": "有限readiness工程、计量资格结论、准确有限输入和关闭状态部署交接",
    "result": "PASS_AND_CLOSED", "F124-01": "CLOSED_BY_ORCHESTRATOR_DOCUMENT_VERIFICATION",
    "independent_code_evidence": {"report": "DocuN/results/TASK-124-result.md", "sha256": audit_seal["report"]["sha256"],
        "scope": "原A/B/C代码及13离线证据通过结论直接继承；原审计不通过记录不改；本次不是新独审"},
    "effective_documents": effective, "current_engineer_result_sha256": sha(report),
    "original_engineer_result_suffix_sha256": sha(original_suffix),
    "source_code_changed_in_correction": False, "rerun_tests_or_new_audit": False,
    "conservative_engineering_tool_seconds": 3710.557411, "remaining_permission_not_revived_after_close": True,
    "activation_receipt": False, "Q_activated": False, "T0": None, "Q": "FROZEN",
    "real_provider_calls": 0, "actual_paid_cost_microunits": 0,
    "remaining_activation_gates": ["当前输入分词/完整服务模板及版本对应", "Embedding单项/保守整批容量",
        "本人账号适用事实", "获准后真实normal初始化/绑定与装载readiness", "主控首次启用及真实Must语义/恢复验收"],
    "identical_search_design_or_trial_tasks_to_be_issued_without_new_evidence": False,
    "project_or_STEP018_019_020_M1_release_accepted": False}
save_json(HERE / "closure-receipt.json", receipt)

decision123 = f"""# TASK123有限前置工程验收通过并关闭，F124-01已收口

{NOW}，Asia/Shanghai。主控完成限定文档Review，F124-01关闭，TASK123/R117约定的有限readiness工程、计量资格结论、准确输入/关闭部署交接验收通过并结束。不是Q启用或真实语义验收。

核对{len(rows)}条当前/原件身份无漂移，两份更正文档已全文核到。新finite-inputs v2撤掉correct映射，159字节仅保留withdrawn_reference且非执行/未持久化/不进入模型上下文；实际理由合同准确落到既有evaluate COMMIT的progress.reason及准确record读取。HTML对象、405字节原文/hash与父顺序不变。真实ID/理由/COMMIT/重开值仍null，未新增动作/接口/迁移或把参考文字假称已保存。

有效文件唯一采用DocuN/evidence/TASK-123/execution/correction-01/finite-inputs.json（79e843d4…a0b1e5）与deployment-handoff.md（8ece6546…9e5f79）。旧execution同名文档只作历史，禁止继续采用其错误映射。原报告15558字节完整后缀及d64c3abb…886c36保留，当前报告23256字节/hash253c3725…1fa36。原六产品/说明、49旧执行文件、48旧清单引用、原独审及固定样本保持。

采纳TASK124原readiness代码/13方法证据/可核控制通过的限定结论；本次移除错误指引没有产品变化，按已给许可由主控核文档，不另做或冒充独立审计，不重跑测试。原124整包不通过结论原文不改，本次F124-01关闭有新文档与主控依据，不追改过去审计为通过。

一次原文档核对exit0，本轮prepare绑定对象错误修正及其退出保留，非产品失败。JSON实际布尔核对项与收尾概数如有不一致，以实际JSON/身份为准，不用概数补造验证，也不为此再次派修正。原600增量内保守新增156秒、累计3710.557411/7200，余3489.442589是封存余量，不恢复执行权；三测试批3/3、原截止和所有unknown/失败保留。

外部计量/模板/Embedding容量及本人账号门继续未具备。当前任务结束，不再为相同已知缺口派重复搜索/设计/试跑卡；有改变判定的新一手材料后再审相应门。正常实例初始化、真实loader/绑定、首次回执、原89动作/28Must语义与恢复仍未完成，100/25和三个分额不变。Q冻结、T0/72h空，真实provider/费用0；STEP018整体/019/020、M1/项目/发布未通过。

收口回执和有限核证在DocuN/evidence/TASK-123/orchestration-closure-20261022。以下为主控原裁定原字节，保留开放P1时点和旧判断历史。

""".encode("utf-8")
paths["decision123"].write_bytes(decision123 + old["decision123"])
decision124 = f"""# F124-01主控限定文档复核关闭，原独审结论按原时点保留

{NOW}。TASK123修正01返回后，主控核更正两文件、原代码/证据不变、原报告后缀及准确FR010/116合同。F124-01错误映射已撤回，现说明只读原evaluate同事务保存的progress.reason；不再使用correct或其它副作用动作保存中性参考文字，无新增产品接口或迁移。

原TASK124独立readiness代码、13方法与可核控制结论继续有效。此次文档修正由主控依既有独审事实作最终Review，不伪称原审计者又作review01或把旧不通过原文改掉。TASK123有限前置交付通过并关闭，真实Q计量和正常部署/真实语义门仍未通过。OBS124-01及历史控制/unknown限制保留。

收口证据在DocuN/evidence/TASK-123/orchestration-closure-20261022/return-check.json及closure-receipt.json。本独审任务不再在途或自动续审，原预算/时窗余量不转运行许可。以下原回收裁定原字节保留。

""".encode("utf-8")
paths["decision124"].write_bytes(decision124 + old["decision124"])

state = f"""# 执行动态文档

文档v2.92，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.64、task_model/07。以下v2.91原字节保留。

## F124-01关闭，TASK123有限前置工程验收结束；Q等待新外部依据与实际启用前置

{NOW}。TASK123修正01两文档已回收，主控核{len(rows)}身份无漂移及完整更正语义，关闭F124-01。TASK123/R117的有限readiness工程、计量资格结论、准确有限输入和关闭部署交接通过并结束；TASK124/R118原独审交付已结束，原代码/13方法证据/可核控制结论继承。未重跑任何产品测试或新增独审，原不通过历史保留，不追认旧错误文档曾正确。

唯一当前有效输入/交接为execution/correction-01/finite-inputs.json（79e843d4…a0b1e5）及deployment-handoff.md（8ece6546…9e5f79）。旧两文档历史冻结。新文档移除correct写入映射，159字节参考标撤销/非执行/未持久化/不入模型上下文；准确指向既有evaluate COMMIT→progress.reason/body/hash/state→原GET和页面。真实记录/理由/重开值仍null，不将已有B级源码承载或文字修正冒真实Q语义/恢复通过。HTML405字节/父顺序、89动作/28Must/24片6索引及100/25/分额保持。

原六代码/测试/用户说明、49旧执行文件、48旧清单引用和原13方法/独审均未改；当前统一报告23256字节/hash253c3725…1fa36，旧15558字节/d64c3abb…886c36完整后缀保留。一次原文档核对exit0；prepare合同hash对象误用后的有据修正和退出原件照留。预算保守新增156/600、累计3710.557411/7200，余3489.442589及三测试批3/3封存不再自动可用；原截止/失败/unknown照留。收尾核对项概数差异按实际JSON项和原件采纳，非产品故障，不据此新派修正。

当前没有待人工转交或在途工程/审计卡，未占新TASK/R。后续只有新官方适用计量/模板/Embedding容量材料或本人非敏感账号事实能改变启用判定时，才核对应门；不继续为相同已知缺口派搜索/设计/试跑任务。正常实例初始化/角色/绑定、真实loader readiness、主控首次回执及真实Must语义/恢复仍待后续具备前置时实施，当前不创建资源或授Q。

Q继续冻结，T0/72h空，provider/实际费用0。用户DeepSeek额度充足声明仍是C级，权限/币种税/特约及智谱事实未核。原120有限工程关闭、121五项关闭和历史控制失败/149与117旧81及全部旧账不重置；STEP018进行中/部分验证，019/020/M1/项目/发布未通过。主控仅文件核证无实时服务探针。CHG1622—1628，下一1629。

## 以下为v2.91及更早历史

""".encode("utf-8")
architecture = f"""# 架构动态文档

文档v1.64，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.92、task_model/07。以下v1.63原字节保留。

## 有限readiness工程与准确理由读回交付已验收，正式Q仍关闭

{NOW}。原TASK124独审接受的readiness snapshot/capabilities投影和13离线方法以不变六文件保留，TASK123文档修正01由主控确认，有限前置工程验收关闭。correct继续真实纠错/争议语义；新有限输入不再把中性参考文案写correct。原FR010理由承载为已存在的evaluate同事务progress.reason及准确记录读取/页面，未新增中性备注接口、表或写动作，也不改变进度规则。

当前交接采用execution/correction-01两文件，旧错误版本只作历史。HTML对象未变，159字节参考只标撤销/非执行，不被假称真实已保存理由或外发输入。真实progress身份/COMMIT/语义/重开还须在后续获准正常链验证；没有将代码静态承载或文档Review扩大为真实供应商通过。

qualification/账号/输入分词/完整模板与当前版本、Embedding容量均保持原未核边界，Q/normal/T0未启用。新正常初始化/受信迁移角色/实例/loader和主控启用回执仍需相应真实事实。当前不增加平台或新计费协议，不再重复相同无新依据的核查循环。原两个provider、100/25及固定分额、Must和历史控制限制保持。

## 以下为v1.63及更早历史

""".encode("utf-8")
paths["state"].write_bytes(state + old["state"])
paths["architecture"].write_bytes(architecture + old["architecture"])
notice123 = f"""# TASK123有限前置工程已验收关闭，停止原执行许可

{NOW}。主控已核修正01并关闭F124-01，约定有限前置交付通过；当前有效两文档在execution/correction-01。原13方法/独审复用，无追加测试/联网或运行许可。Q继续冻结，不从余量或旧卡恢复执行；详情DocuN/results/TASK-123-work-decision.md。以下完整旧卡原字节保留。

""".encode("utf-8")
paths["task123"].write_bytes(notice123 + old["task123"])
notice124 = f"""# TASK124已结束，F124-01经主控限定文档复核关闭

{NOW}。原代码/13方法/可核控制通过范围继承，原审计不通过历史原文保留。本次更正不变产品，由主控最终核证，不假称新独审或review01。Q/计量/正常部署仍未启用，原审计余量不恢复许可；详情DocuN/results/TASK-124-work-decision.md。以下原完整卡保留。

""".encode("utf-8")
paths["task124"].write_bytes(notice124 + old["task124"])

entries = [
    (1622, "DocuN/results/TASK-123-work-decision.md", "限定文档核证关闭F124-01，TASK123有限前置交付通过并结束；Q及真实阶段门保留。"),
    (1623, "DocuN/results/TASK-124-work-decision.md", "登记主控基于文档更正的缺陷关闭，原独审不通过历史及代码/证据分轴结论原样保持。"),
    (1624, "DocuS/架构动态文档.MD", "v1.64登记不变readiness已验及准确progress理由读回合同，无新接口/模型/权限。"),
    (1625, "DocuS/执行动态文档.MD", "v2.92登记两任务有限收口、唯一有效新文档、3710.557411账和无新在途卡/原启用缺口。"),
    (1626, "DocuN/tasks/TASK-123.md", "置顶有限验收关闭及停止许可通知，旧完整卡原字节保留。"),
    (1627, "DocuN/tasks/TASK-124.md", "置顶F124-01主控关闭/审计结束通知，不伪造新独审或改原报告。"),
    (1628, "DocuN/evidence/TASK-123/orchestration-closure-20261022", "保存新旧文档/代码/证据身份与限定Review、有效路径收口回执、旧共享及读回；产品运行0。"),
]
log = "\r\n\r\n" + "\r\n\r\n".join(f"- CHG-{number}，{NOW}，Codex编排Agent，{path}。{why}" for number, path, why in entries) + "\r\n"
paths["changes"].write_bytes(old["changes"] + log.encode("utf-8"))

for key, value in old.items():
    assert (raw(paths[key]).startswith(value) if key == "changes" else raw(paths[key]).endswith(value)), key
for row in rows:
    p = Path(row["path"])
    if p in set(paths.values()):
        continue
    assert sha(raw(p)) == row["current_full_file_sha256"], p
assert raw(report_path) == report
proof_paths = [*paths.values(), HERE / "return-check.json", HERE / "closure-receipt.json"]
save_json(HERE / "save-proof.json", {"saved_at": NOW, "state": "TASK123_FINITE_PREPARATION_ACCEPTED_CLOSED_F12401_CLOSED",
    "next_CHG": 1629, "product_tests_or_services_started": 0, "new_task_card": None, "Q": "FROZEN", "T0": None,
    "original_bytes_preserved": True, "files": [{"path": p.as_posix(), "bytes": p.stat().st_size, "sha256": sha(raw(p))} for p in proof_paths]})
print(json.dumps({"state": "TASK123_ACCEPTED_CLOSED_F12401_CLOSED", "identity_rows": len(rows),
    "mismatches": 0, "new_runtime": 0, "new_task_card": None, "next_CHG": 1629, "Q": "FROZEN"}, ensure_ascii=False))
