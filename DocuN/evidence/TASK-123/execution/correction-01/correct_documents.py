"""TASK123修正01，仅用标准库处理文档、原字节副本及一次一致性检查。"""
import copy
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
EXECUTION = OUT.parent
ROOT = OUT.parents[4]
ORCHESTRATION = ROOT / "DocuN/evidence/TASK-123/orchestration-correction01-20261022"
RESULT = ROOT / "DocuN/results/TASK-123-result.md"
DOCS = ("finite-inputs.json", "deployment-handoff.md")

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def load(path):
    return json.loads(path.read_bytes())

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def identity(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": sha(raw)}

def prepare():
    now = datetime.datetime.now(datetime.timezone.utc)
    assert OUT == OUT.resolve() and OUT.is_relative_to(ROOT)
    permit = load(ORCHESTRATION / "permit.json")
    assert now < datetime.datetime.fromisoformat(permit["calendar_deadline"])
    contract_raw = (ORCHESTRATION / "contract.md").read_bytes()
    assert sha(contract_raw) == permit["contract_sha256"]
    assert (ROOT / "DocuN/tasks/TASK-123.md").read_bytes().startswith(contract_raw)
    assert sha((ORCHESTRATION / "input-manifest.json").read_bytes()) == permit["input_manifest_sha256"]
    manifest = load(ORCHESTRATION / "input-manifest.json")
    checked = []
    for row in manifest["rows"]:
        current = identity(Path(row["path"]))
        current["matches_frozen"] = current["sha256"] == row["sha256"] and current["bytes"] == row["bytes"]
        assert current["matches_frozen"], row["path"]
        checked.append(current)
    original_files = []
    for path in sorted(EXECUTION.rglob("*")):
        if path.is_file() and not path.is_relative_to(OUT):
            original_files.append(identity(path))
    pre = OUT / "pre"
    pre.mkdir(exist_ok=False)
    for name in DOCS:
        (pre / (name + ".bytes")).write_bytes((EXECUTION / name).read_bytes())
    (pre / "TASK-123-result.md.bytes").write_bytes(RESULT.read_bytes())
    original_manifest = load(EXECUTION / "delivery-manifest.json")
    save("pre-snapshot.json", {"at": now.isoformat(), "inputs": checked,
        "old_execution_files": original_files, "old_delivery_manifest_rows": original_manifest["rows"],
        "original_result": identity(RESULT), "product_files": load(EXECUTION / "post-snapshot.json")["products"]})
    save("receipt.json", {"task": "TASK-123", "R": "R-117", "round": "correction-01",
        "first_clock_utc": "2026-10-22T00:39:56+00:00", "saved_at": now.isoformat(),
        "client": "Codex desktop", "specific_model_id": None,
        "resource": "原工程窗口承接常规档文档修正，不更换或委派",
        "permit_id": permit["permit_id"], "calendar_deadline": permit["calendar_deadline"],
        "prior_charge_seconds": permit["prior_conservative_charge_seconds"],
        "new_tool_wall_cap_seconds": 600, "closing_reserve_seconds": 120,
        "product_tests_imports_network_runtime_started": False,
        "rules": "同窗已读AGENTS/WORK相关段和07复用，锁定七指纹实际匹配；未加载或采用后来版本"})
    print(json.dumps({"inputs_matched": len(checked), "old_execution_files": len(original_files),
        "old_delivery_rows": len(original_manifest["rows"]), "result_pre_bytes": RESULT.stat().st_size}))

def write_documents():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    old = load(EXECUTION / DOCS[0])
    new = copy.deepcopy(old)
    reference = new.pop("continuation_reason")
    new["schema"] = "retrolume.task123.finite-inputs.v2"
    new["status"] = "CORRECTED_DISABLED_FUTURE_READBACK_NOT_RUN"
    new["original_created_at"] = new["created_at"]
    new["created_at"] = now
    new["supersedes"] = {"path": str(EXECUTION / DOCS[0]), "sha256": sha((EXECUTION / DOCS[0]).read_bytes()),
        "finding": "F124-01", "history_only": True,
        "current_effective_document": str(OUT / DOCS[0])}
    new["withdrawn_reference"] = {key: reference[key] for key in
        ("text", "encoding", "codepoints", "utf8_bytes", "sha256", "source_rubric")}
    new["withdrawn_reference"].update(status="WITHDRAWN_NON_EXECUTABLE_REFERENCE",
        persisted=False, include_in_model_context=False, is_input=False,
        reason="原159字节只保留为撤销映射的历史参考；不承诺由现有接口保存，也不当实际progress.reason或后续模型上下文。",
        write_operation=None)
    new["progress_reason_readback_contract"] = {
        "schema": "retrolume.task123.progress-reason-readback.v1",
        "status": "FUTURE_ACCEPTANCE_CONTRACT_NOT_RUN", "evidence_grade": "B 当前源码/原合同事实",
        "requirement": "FR010/DR002、116 L01/L05及M06要求的真实进度理由；不新增任意用户手写备注Must",
        "existing_commit": {"action": "evaluate", "branch": "current and normal",
            "repository": "backend/app/activities/teaching_repository.py",
            "reason_function": "_progress_reason", "saved_kind": "progress", "saved_field": "body.reason",
            "insert_function": "_teaching_insert_record", "hash_field": "body_sha256",
            "head_field": "reason_record_id", "state_field": "state_after",
            "body_fields": ["feedback_record_id", "answer_record_id", "reason", "observations", "support_checks",
                            "advance", "node_before", "node_after"],
            "transaction": "原evaluate正常当前结果分支同一事务保存feedback/progress并更新head；未COMMIT或非当前/非正常结果不得报保存成立"},
        "read_functions": ["read_teaching_command", "read_teaching_workspace", "read_teaching_record"],
        "existing_page": {"file": "frontend/src/activities/TeachingWorkspace.tsx", "panel": "更新或保留理由",
            "projection": "workspace.reason.body.reason / reasonBody.reason"},
        "actual": {key: None for key in ("activity_id", "evaluate_business_key", "evaluate_command_request_sha256",
            "feedback_record_id", "answer_record_id", "exercise_record_id", "progress_record_id", "progress_body_sha256",
            "source_refs", "source_versions", "scope_revision", "goal_version", "path_record_id", "head_revision",
            "applied_revision", "state_after", "DataContext", "reason", "observations", "support_checks", "advance",
            "node_before", "node_after", "transaction_committed", "reopened_record_sha256")},
        "readback_steps": [
            "沿原evaluate业务键先GET已有命令事实，核同活动、反馈/作答/练习、来源/版本、scope/goal/revision与DataContext；不为取得理由新增请求。",
            "定位该次evaluate同事务COMMIT的kind=progress记录，核body.reason、feedback_record_id/answer_record_id、原业务键、body_sha256及state_after；只截理由页面不足以证明持久化。",
            "记录reason及observations.independent_answers/assisted/contested、support_checks、advance、node_before/node_after，保留真实原因，不把159字节参考文字写成实际reason。",
            "下一动作前GET准确workspace和该progress记录，核当前已有页面的理由；先保存本次progress ID/hash。后续动作如改变head.reason_record_id，读这条历史准确记录，不用新head替代旧理由。",
            "未来获准真实重开后仍GET相同progress ID并核相同body/hash及其进度事实，保留后续合法变更。此处只写核对合同，当前未运行PG/HTTP/browser或真实语义。"],
        "progress_rules": [
            "单次复测可以保留节点；两份不同且未暴露、required met的独立实例并含复测及推进前置满足时，才按既有规则处理。",
            "即使独立实例足够，没有满足前置的待推进节点也应保留节点并保存对应理由，不伪造advance。",
            "原辅助/争议依据及真实纠错保护不改；本修正不追加correction、不把任何作答因参考理由从依据集合剔除。"],
        "extra_reason_write_action": None, "extra_model_or_query_requests": 0,
        "forbidden_reason_storage_shortcuts": ["correct", "select_node", "answer", "goal", "新增reason action/字段/表"],
        "actual_runtime_evidence": None}
    save(DOCS[0], new)
    old_handoff = (EXECUTION / DOCS[1]).read_text(encoding="utf-8")
    handoff = old_handoff.replace("# TASK123 关闭状态部署交接\n", "# TASK123 修正01 关闭状态部署交接\n\n本文件为本轮当前有效交接，配套[新finite-inputs.json](" + str(OUT / DOCS[0]).replace("\\", "/") + ")。旧execution目录同名两文件及原报告仅作原字节历史；F124-01的继续理由操作映射已撤销，不沿旧指引执行。\n", 1)
    old_section_start = old_handoff.index("[finite-inputs.json]")
    old_section_end = old_handoff.index("89动作、28Must", old_section_start)
    replacement = """[finite-inputs.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/finite-inputs.json) 的HTML focus原文、405 UTF8字节/hash、Q01.03.model当前合格feedback父、Q01.04.query前的顺序及未运行状态保持。真实record/body/point/config、业务键、typed/payload、description/artifact和控件ID仍null。原159字节继续理由文字仅在withdrawn_reference保留，非执行、未持久化、不加入模型上下文，也不承诺存在保存该任意文字的中性备注接口。

FR010/DR002及116 M06/主链已有承载是原evaluate正常当前结果COMMIT时同事务保存kind=progress、body.reason、feedback/answer、observations/support_checks、advance及node_before/node_after，记录body_sha256和state_after，更新head.reason_record_id。这是当前源码的B级事实，尚不是本轮真实PG/Q或重开验证。保存理由不需另发POST；不得用correct、select_node、answer、goal或新增reason动作替代。现有correct保留其真实争议保护。

未来获准链按progress_reason_readback_contract先GET原evaluate业务键及对应progress，核COMMIT、kind/body/hash、原feedback/answer、来源/版本、scope/goal/revision和DataContext。读取reason、observations的独立/辅助/争议依据、support_checks、advance及前后节点；一次复测可以保留节点。两份合格独立实例且推进前置都满足才按原规则处理，没有可推进节点时保存真实保留理由。

下一明确动作按当时真实阶段进行。动作前保存该次progress的准确record ID/hash，再GETworkspace/record核对页面已有“更新或保留理由”。下一动作若改变head.reason_record_id，之后读取已保存ID对应的历史准确记录，不拿新head替代原理由；未来实际重开仍核同条记录/body/hash及进度。页面截图不能单独证明事务持久化。本轮这些实际记录、理由、绑定和重开值全部null/未运行，不预写参考文案或假UUID，不额外增加模型/query次数。未来 IDs、24片实际排序与6批真实批号仍待获准 normal 导入后冻结。

"""
    old_section = old_handoff[old_section_start:old_section_end]
    assert old_section in handoff
    handoff = handoff.replace(old_section, replacement, 1)
    identity_notice = "\nOBS124-01沿原独审作为非阻塞配置风险保留。模型及returned_models身份栏只填可公开模型别名，不填密钥、密钥hash或私有标签；字符正则不保证识别任意误填秘密，未知别名也不构成真实返回资格。本轮不改产品。\n"
    anchor = "## 计量与账号剩余门"
    handoff = handoff.replace(anchor, identity_notice + "\n" + anchor, 1)
    old_final = "下一动作是取得外部适用依据并由主控核证稳定差异。新增秘密投影/资格解释若作为运行依据采用，须在稳定候选上完成相应一次独立增量审查；执行者没有自签独审，旧120/121关闭不重开。外部门齐备后才由主控给精确资源与实际部署/真实语义合同，按122 runbook继续；不再派同样浏览/批准协议设计卡。本交接不签 STEP018/019/020、M1、项目或发布通过。"
    new_final = "TASK124独立增量审查的readiness代码、13方法原证据及可核控制通过范围直接继承，原报告、失败和unknown保留。本轮只撤销F124-01错误指引并补已有progress理由的读回合同，由主控对照原独审和准确需求限定核文档；不把此次核证冒充新独审，不预设再派完整审计或重跑13方法。Q外部计量/账号缺口、L01/L05真实语义及恢复门继续保留。外部门齐备后才由主控给精确资源与实际部署/真实语义合同，按122 runbook继续；不再派同样浏览/批准协议设计卡。本交接不签 STEP018/019/020、M1、项目或发布通过。"
    assert old_final in handoff
    handoff = handoff.replace(old_final, new_final, 1)
    (OUT / DOCS[1]).write_text(handoff, encoding="utf-8")
    pairs = []
    diff = []
    for name in DOCS:
        before = (EXECUTION / name).read_bytes()
        after = (OUT / name).read_bytes()
        pairs.append({"original": identity(EXECUTION / name), "corrected": identity(OUT / name),
            "original_effective_for_execution": False, "current_effective_path": str(OUT / name)})
        diff.extend(difflib.unified_diff(before.decode("utf-8").splitlines(), after.decode("utf-8").splitlines(),
            fromfile="historical/execution/" + name, tofile="effective/execution/correction-01/" + name, lineterm=""))
    save("original-to-corrected.json", {"finding": "F124-01", "written_at": now, "pairs": pairs,
        "HTML_object_identical": new["html"] == old["html"], "allowed_local_projection_removed": True,
        "reference_not_executable_or_persisted_or_model_context": True,
        "effective_progress_reason": "原evaluate正常当前结果COMMIT的kind=progress.body.reason",
        "old_artifacts_unchanged": "最终一次document-consistency.json核证", "Q_enabled": False,
        "finding_closed_by_executor": False})
    (OUT / "documents.diff").write_text("\n".join(diff) + "\n", encoding="utf-8")
    source_facts = load(ORCHESTRATION / "source-facts.json")
    save("source-relations.json", {"evidence_grade": "B 源码/原合同事实，未导入或运行产品", "sources": source_facts["sources"],
        "relations": [
            {"path": "backend/app/activities/teaching_repository.py", "lines": [19,24], "fact": "_progress_reason区分不足、无可推进节点和有限前进理由"},
            {"path": "backend/app/activities/teaching_repository.py", "lines": [1311,1336], "fact": "current and normal evaluate同事务progress.reason/body_sha256/state_after和head理由"},
            {"path": "backend/app/activities/teaching_repository.py", "lines": [830,874], "fact": "correct写correction并触发重建，不能用空disputed_dimensions作中性理由"},
            {"path": "backend/app/activities/teaching_repository.py", "lines": [1501,1544], "fact": "已有workspace/command/record读取可核准确历史事实"},
            {"path": "backend/app/learning/teaching_progress.py", "lines": [12,50], "fact": "correction父反馈入争议集合并排除相应独立作答"},
            {"path": "frontend/src/activities/TeachingWorkspace.tsx", "lines": [805,807], "fact": "已有更新或保留理由面板读reasonBody.reason及独立/辅助/争议观察"}],
        "exact_free_text_note_Must_found": False, "product_changes": False})
    print(json.dumps({"corrected": [identity(OUT / name) for name in DOCS], "HTML_identical": True}, ensure_ascii=True))

def check_once():
    target = OUT / "document-consistency.json"
    assert not target.exists(), "文档一致性仅一次；有失败保留，不机械重跑"
    now = datetime.datetime.now(datetime.timezone.utc)
    pre = load(OUT / "pre-snapshot.json")
    original_result = (OUT / "pre/TASK-123-result.md.bytes").read_bytes()
    current_result = RESULT.read_bytes()
    checks = {}
    checks["original_result_suffix_preserved"] = current_result.endswith(original_result) and len(current_result) > len(original_result)
    frozen_inputs = []
    for row in pre["inputs"]:
        if Path(row["path"]) == RESULT: continue
        match = sha(Path(row["path"]).read_bytes()) == row["sha256"]
        frozen_inputs.append({"path": row["path"], "unchanged": match})
    checks["all_other_inputs_unchanged"] = all(r["unchanged"] for r in frozen_inputs)
    old_files = [{"path": row["path"], "unchanged": sha(Path(row["path"]).read_bytes()) == row["sha256"]}
                 for row in pre["old_execution_files"]]
    checks["all_old_execution_artifacts_unchanged"] = all(r["unchanged"] for r in old_files)
    manifest_rows = []
    for row in pre["old_delivery_manifest_rows"]:
        path = ROOT / row["path"]
        data = original_result if path == RESULT else path.read_bytes()
        manifest_rows.append({"path": row["path"], "matches_original": sha(data) == row["sha256"],
                              "mode": "original_report_suffix" if path == RESULT else "unchanged_file"})
    checks["old_48_manifest_rows_preserved"] = len(manifest_rows) == 48 and all(r["matches_original"] for r in manifest_rows)
    product_rows = [{"path": row["path"], "unchanged": sha((ROOT / row["path"]).read_bytes()) == row["post_sha256"]}
                    for row in pre["product_files"]]
    checks["six_passed_product_test_docs_unchanged"] = len(product_rows) == 6 and all(r["unchanged"] for r in product_rows)
    old = load(EXECUTION / DOCS[0]); new = load(OUT / DOCS[0])
    reference = new["withdrawn_reference"]
    contract = new["progress_reason_readback_contract"]
    checks["disabled"] = new["enabled"] is False
    checks["HTML_object_and_parent_order_unchanged"] = new["html"] == old["html"]
    raw_html = new["html"]["text"].encode("utf-8")
    checks["HTML_405_bytes_hash_and_lengths"] = len(raw_html) == 405 and sha(raw_html) == new["html"]["sha256"] and len(new["html"]["text"]) == new["html"]["codepoints"]
    checks["no_local_write_mapping"] = "continuation_reason" not in new and "allowed_local_projection" not in (OUT / DOCS[0]).read_text(encoding="utf-8")
    checks["reference_withdrawn_not_input_persisted_or_context"] = reference["status"] == "WITHDRAWN_NON_EXECUTABLE_REFERENCE" and all(reference[key] is False for key in ("persisted", "is_input", "include_in_model_context")) and reference["write_operation"] is None
    checks["reference_159_bytes_retained_only_as_history"] = reference["text"] == old["continuation_reason"]["text"] and len(reference["text"].encode("utf-8")) == 159 and sha(reference["text"].encode("utf-8")) == reference["sha256"]
    checks["real_progress_bindings_all_null"] = all(value is None for value in contract["actual"].values())
    checks["evaluate_progress_source_and_no_extra_action"] = contract["existing_commit"]["action"] == "evaluate" and contract["existing_commit"]["saved_kind"] == "progress" and contract["existing_commit"]["saved_field"] == "body.reason" and contract["extra_reason_write_action"] is None and contract["extra_model_or_query_requests"] == 0
    handoff = (OUT / DOCS[1]).read_text(encoding="utf-8")
    checks["handoff_corrected_reference_and_readback_intent"] = str(OUT / DOCS[0]).replace("\\", "/") in handoff and "correct/CorrectBody.text 作本地保存" not in handoff and all(term in handoff for term in ("kind=progress", "head.reason_record_id", "OBS124-01", "record ID/hash", "原evaluate"))
    mapping = load(OUT / "original-to-corrected.json")
    checks["mapping_hashes_exact"] = all(identity(Path(pair["original"]["path"])) == pair["original"] and identity(Path(pair["corrected"]["path"])) == pair["corrected"] for pair in mapping["pairs"])
    links = []
    import re
    for path in (OUT / DOCS[1], RESULT):
        content = path.read_text(encoding="utf-8") if path != RESULT else current_result[:-len(original_result)].decode("utf-8")
        for link in re.findall(r"\]\((D:/[^)]+)\)", content):
            exists = Path(link.split(":", 2)[0] + ":" + link.split(":", 2)[1]).exists() if len(link.split(":")) > 2 else Path(link).exists()
            links.append({"path": link, "exists": exists})
    checks["current_document_links_exist"] = all(row["exists"] for row in links)
    source = (ROOT / "backend/app/activities/teaching_repository.py").read_text(encoding="utf-8")
    progress = (ROOT / "backend/app/learning/teaching_progress.py").read_text(encoding="utf-8")
    page = (ROOT / "frontend/src/activities/TeachingWorkspace.tsx").read_text(encoding="utf-8")
    checks["actual_function_relations_static"] = all(token in source for token in ("def _progress_reason", "if current and normal:", '"reason":reason', '"progress",key,3', "read_teaching_workspace", "read_teaching_record")) and 'corrections.add(str(row["parent_record_id"]))' in progress and "reasonBody.reason" in page
    checks["new_result_prepend_clear_and_readable"] = current_result.startswith("# TASK-123 / R-117 修正轮01".encode("utf-8")) and "原报告原字节保留" in current_result[:-len(original_result)].decode("utf-8")
    passed = all(checks.values())
    marker = b"{{DOCUMENT_CHECK_OUTCOME}}"
    assert current_result[:-len(original_result)].count(marker) == 1
    outcome = ("一次文档一致性核对通过，真实退出0。" if passed else "一次文档一致性核对未通过，真实退出1；具体失败项保留于document-consistency.json。")
    current_result = current_result.replace(marker, outcome.encode("utf-8"), 1)
    RESULT.write_bytes(current_result)
    assert RESULT.read_bytes() == current_result and current_result.endswith(original_result)
    result = {"task": "TASK-123", "round": "correction-01", "checked_at": now.isoformat(), "check_count": 1,
        "scope": "仅文件/JSON/文档，不导入或运行产品", "checks": checks, "passed": passed, "exit_code": 0 if passed else 1,
        "frozen_input_rows": frozen_inputs, "old_execution_rows": old_files, "old_delivery_rows": manifest_rows,
        "six_frozen_files": product_rows, "links": links,
        "original_result": {"bytes": len(original_result), "sha256": sha(original_result)},
        "current_result": identity(RESULT), "new_documents": [identity(OUT / name) for name in DOCS],
        "function_relations": "source-relations.json", "product_tests_rerun": 0, "Q_enabled": False}
    save("document-consistency.json", result)
    save("save-proof.json", {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "saved_and_reread": True, "document_consistency_passed": passed,
        "current_result": identity(RESULT), "original_report_suffix_sha256": sha(original_result),
        "new_documents": [identity(OUT / name) for name in DOCS],
        "original_report_suffix_preserved": current_result.endswith(original_result),
        "original_artifacts_unchanged": checks["all_old_execution_artifacts_unchanged"],
        "finding_final_decision_owner": "主控限定文档复核，执行者未自签关闭"})
    print(json.dumps({"passed": result["passed"], "checks": checks, "old_execution_files": len(old_files), "result": identity(RESULT)}, ensure_ascii=True))
    raise SystemExit(0 if result["passed"] else 1)

def prepend_result():
    before = (OUT / "pre/TASK-123-result.md.bytes").read_bytes()
    assert RESULT.read_bytes() == before, "结果原件漂移，不覆盖"
    prefix = (OUT / "result-prefix.md").read_bytes()
    assert prefix.startswith("# TASK-123 / R-117 修正轮01".encode("utf-8"))
    RESULT.write_bytes(prefix + before)
    print(json.dumps({"prepended_bytes": len(prefix), "original_suffix_bytes": len(before),
        "original_suffix_sha256": sha(before)}))

if __name__ == "__main__":
    {"prepare": prepare, "write": write_documents, "prepend": prepend_result, "check": check_once}[sys.argv[1]]()
