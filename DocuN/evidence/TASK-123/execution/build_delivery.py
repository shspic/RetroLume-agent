"""生成本卡有限交接材料与可核证差异，不运行产品或重复分片。"""
import ast
import datetime
import difflib
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def text_value(value):
    return {"text": value, "encoding": "UTF-8，无BOM，无尾换行", "codepoints": len(value),
            "utf8_bytes": len(value.encode("utf-8")), "sha256": digest(value.encode("utf-8"))}

now = datetime.datetime.now(datetime.timezone.utc)
samples_path = ROOT / "DocuN/evidence/TASK-116/design/sample-inputs.json"
samples = json.loads(samples_path.read_bytes())
matrix_path = ROOT / "DocuN/evidence/TASK-122/preparation/remaining-must-matrix.json"
matrix = json.loads(matrix_path.read_bytes())
runbook = ROOT / "DocuN/evidence/TASK-122/preparation/operation-runbook.md"

html_focus = "请依据当前仍合格的平均速度反馈制作交互说明。路程 d 的单位是米，时间 t 的单位是秒，速度为 d/t 米每秒。只设 d、t 两个输入，初值分别为 120、120；初始显示 1。保持 d=120，把 t 改为 240 时显示 0.5。t=0 和未定义字段必须在计算前拒绝；reset 恢复初值并显示 1。只解释这次单位换算，不扩展到长期掌握。"
reason = "继续核对分钟换秒与平均速度的单位，下一步仅按当前已保存的作答、反馈和复测记录选择；本次练习不说明长期掌握。"
finite = {"schema": "retrolume.task123.finite-inputs.v1", "enabled": False,
    "status": "FROZEN_TEXT_ONLY_NOT_RUN", "created_at": now.isoformat(),
    "inherited_matrix": {"path": str(matrix_path), "sha256": digest(matrix_path.read_bytes()),
        "requests": 89, "must": 28, "fragments": 24, "index_batches": 6,
        "note": "采用122主控已验结论，不再次分片或重算同一预算"},
    "unchanged_samples": {"path": str(samples_path), "sha256": digest(samples_path.read_bytes())},
    "html": {**text_value(html_focus), "purpose": "L10/Q10.html 的 HtmlCommand.focus 精确原文，不是已生成的interactive_description或可运行artifact",
        "source_rubric": {"path": "DocuN/evidence/TASK-116/design/acceptance-contract.md", "scenario": "L10",
            "original": "L01的合格父feedback→描述生成→v2-08真实宿主；固定d/t控件d120,t120读1，t240读0.5，t0及未定义字段被前拒，reset回1"},
        "source_input_pointers": ["#/sources/0/text", "#/inputs/numeric_wrong_answer"],
        "current_parent": {"action_id": "Q01.03.model", "before_action_id": "Q01.04.query",
            "required_answer_text": samples["inputs"]["numeric_wrong_answer"],
            "kind": "teaching", "record_id": None, "body_sha256": None, "point_id": None,
            "qualification": None, "actual_description_sha256": None, "artifact_sha256": None,
            "rule": "只允许同活动当前已COMMIT合格feedback、父hash及currentness重新核齐后组包；未匹配则停，不选历史007替代"},
        "actual_business_key": None, "expected_config_sha256": None,
        "actual_request_sha256": None, "operator_approval": None,
        "limits": {"focus_codepoints_max": 1024, "focus_bytes_max": 4096},
        "control_labels": ["d", "t"], "control_ids": None,
        "control_note": "标签沿原rubric；真实控件ID由合格封闭description生成并符合hctl_规则，不把裸d/t冒充已生成ID。0和未定义字段是拒绝负例，不新增许可输入。"},
    "continuation_reason": {**text_value(reason),
        "purpose": "L01/L05之后保存用户的有限继续理由，只记录下一动作依据的边界，不预写成功或长期掌握结论",
        "source_rubric": {"path": "DocuN/evidence/TASK-116/design/acceptance-contract.md", "scenarios": ["L01", "L05"],
            "original": "主链必须完整到保存理由，不能停在生成题。"},
        "source_input_pointers": ["#/inputs/numeric_goal", "#/inputs/retest_question", "#/inputs/retest_answer"],
        "allowed_local_projection": {"TeachingCommandInput.action": "correct", "CorrectBody.text": reason,
            "CorrectBody.target_record_id": None, "CorrectBody.disputed_dimensions": []},
        "rule": "沿现有correct本地文本保存到真实当前feedback/progress父；先核同一作答链、head和CAS。不是新增advance接口，不触发模型、不改变进度判据。若需要作为下一次模型上下文，须在未来实际manifest有限文字及逐请求完整payload中明确冻结，不由此JSON授外发。",
        "current_parent_record_id": None, "parent_body_sha256": None, "business_key": None,
        "DataContext": None, "command_committed": False},
    "not_generated": ["normal实例与source/version/fragment真实ID", "typed/payload最终字节", "grant", "T0", "operator批准", "HTML产物与控件实际ID"],
    "no_new_answer_or_source_or_must": True}
assert len(html_focus) <= 1024 and len(html_focus.encode("utf-8")) <= 4096
save("finite-inputs.json", finite)

findings = [
 {"id": "M01", "category": "已证明", "scope": "当前产品payload构造与有效UTF8 JSON序列化",
  "conclusion": "W是完整线上canonical JSON的UTF8字节数，不是文本token数。U为所有原始文本字段UTF8字节之和；对这些未压缩、未base64解码的纯文本字段，合法JSON转义不缩小UTF8字节，故U≤W。",
  "basis": ["backend/app/capabilities/gateway.py::_build_payload", "backend/app/capabilities/embedding.py::_call_original"],
  "limits": "不把W当服务模板后的字符数；若服务预处理扩张、重复或加入工具/角色模板，此关系不直接约束prompt_tokens。"},
 {"id": "M02", "category": "已证明", "scope": "当前DeepSeek公开计数/计价合同内的输出项，文档推论，非服务实测",
  "conclusion": "显式thinking.type=disabled选择非思考模式。API把reasoning_tokens列为completion_tokens_details的组成，max_tokens限制生成completion总数；价格页按输入/输出总token计费。因此合同内输出上界可用max_tokens覆盖，无须在其外另加一个无界reasoning预算。",
  "basis": ["https://api-docs.deepseek.com/api/create-chat-completion/", "https://api-docs.deepseek.com/zh-cn/guides/thinking_mode/", "https://api-docs.deepseek.com/zh-cn/quick_start/pricing/"],
  "evidence": ["web-responses/W123-04.json", "web-responses/W123-05.json", "web-responses/W123-06.json"],
  "limits": "不要求证明供应商永不违约；不证明本人账号报价、税费及特约。该推论未被填入任何grant，也不能补齐输入上界。"},
 {"id": "M03", "category": "缺外部依据", "scope": "deepseek-flash / DeepSeek-V4.1-Flash-1017 的输入全域",
  "conclusion": "当前价格页把服务别名映射到1017；同名官方仓库存在。未取得当前tokenizer原件或完整服务模板及其版本绑定，不能证明预处理后的文本token T≤U，更不能证明完整prompt token≤W+F、F≤4096覆盖全部W≤65536。",
  "basis": ["https://api-docs.deepseek.com/zh-cn/quick_start/pricing/", "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017", "download-ledger.jsonl"],
  "limits": "模型名对应不等于公开repo具体commit/模板字节与API实际部署相同。没有实测反例，原公式为未证明而非已证伪。"},
 {"id": "M04", "category": "缺外部依据", "scope": "Embedding-3单项与保守整批容量",
  "conclusion": "沿122官方guide的3072限制及保守解释，单项与sum整批均须≤3072。未取得与embedding-3当前服务对应的tokenizer/预处理/特殊token规则，故这两个门都未证明。4项/2048字符/4096查询字节/费用预留不能替代容量。",
  "basis": ["DocuN/evidence/TASK-122/preparation/official-facts.json#O04", "https://docs.bigmodel.cn/cn/guide/models/embedding/embedding-3"],
  "limits": "本轮两种限定官方源检索均未返回可采用的专属分词资料；错误API文档路径亦未取得正文，不能据此断言供方资料不存在。DeepSeek tokenizer及OpenAI同名embedding模型均不能替代。"},
 {"id": "M05", "category": "仅有限样本成立", "scope": "冻结样本的字节与既有分片算术，非token计数",
  "conclusion": "继承122已验八文24片/6批、任四片规范JSON静态上界446字节；本轮只新增两段精确文字及各自UTF8/hash，不重跑分片。没有执行任何有限token计数，有限样本的token资格也仍未知。",
  "basis": ["DocuN/evidence/TASK-122/preparation/sample-fragments.json", "DocuN/evidence/TASK-122/orchestration-acceptance-20261022/return-check.json", "finite-inputs.json"],
  "limits": "未来query、模型派生正文、真实ID与模板尚未冻结；有限样本即便将来有精确计数，也不覆盖所有可接受输入。"},
 {"id": "M06", "category": "缺外部依据", "scope": "账号适用与最终费用上界",
  "conclusion": "2/8及0.5元每百万token仅为122/本轮官方公开价格依据；本人权限、CNY/含税/特约与智谱余额仍null。用户只声明DeepSeek额度充足。费用公式的算术成立不能使当前启用合格。",
  "basis": ["DocuN/evidence/TASK-122/orchestration-acceptance-20261022/account-facts-received.json", "DocuN/evidence/TASK-122/preparation/cost-calculation.json"],
  "limits": "不访问账号后台、不取真实key、不新加零保留/不训练标准。"}
]
metering = {"schema": "retrolume.task123.metering-evidence.v1", "created_at": now.isoformat(),
    "verdict": "NOT_QUALIFIED_FOR_CURRENT_ACTIVATION", "token_upper_bound_verified": False,
    "account_terms_verified": None, "provider_runtime_verified": False,
    "findings": findings,
    "categories": {name: [r["id"] for r in findings if r["category"] == name]
                   for name in ("已证明", "仅有限样本成立", "版本不适用", "缺外部依据")},
    "version_not_applicable_note": "没有取得可定性为明确错误版本的分词原件，因此此组为空；不把未取得或未绑定说成已证版本不适用。旧通用zip链接不作为当前服务依据。",
    "relations": {"W": "完整线上canonical JSON UTF8字节，现产品门≤65536",
        "U": "原始输入文本UTF8字节之和，对当前文本payload有U≤W",
        "preprocessing": "当前供应商normalize/pretokenize/added-token处理未取得原件并绑定，未知",
        "T": "文本token数未知；BPE名称本身不足",
        "F": "消息角色、边界、工具/JSON/特殊token及服务注入总开销未知；≤4096尚未证明",
        "completion": "当前DS公开合同的max_tokens总生成上限包含completion明细的reasoning，推论已说明",
        "embedding_capacity": "须分别核每项T_i≤3072及sum(T_i+服务计入的开销)≤3072，不与收费上界互换",
        "cost": "原ceil(((W+F)*input_rate+max_output_tokens*output_rate)*(1+margin))不改；输入/F与账号缺口使其尚不能用于启用核证"},
    "non_expansion_analysis": [
        "只有当前适用分词配置证实无扩张normalize，U才能控制初始字节符号数。",
        "ByteLevel映射须逐UTF8字节一一映射；前缀空格若有须单独界定。正则切片只有分割而不复制/插入时不增加总符号数。",
        "若BPE初始符号恰为这些字节，merge只合并相邻符号，则普通文本token数不超过初始字节符号数；byte fallback/unknown处理和added tokens必须分别审定。",
        "Unigram需核normalizer、metaspace/空白规则、byte fallback和每片覆盖方式；单凭Unigram名称或词表大小不能推出不等式。",
        "BOS/EOS、消息角色模板、generation prefix、tools/response_format文本化及服务额外注入计入F；公开模板的本地行为仍须与当前API部署绑定。",
        "本轮未取得可解析原件，以上是待满足的推导条件，不是对当前DS或Embedding分词实现的断言。"],
    "counterexamples_to_invalid_inferences": [
        {"claim": "U≤W即可推出T≤W+4096", "counterexample": "一种未被排除的扩张预处理可将一个原字符展开为多个符号，随后逐符号编码；纯JSON字节关系不限制此服务行为。这是逻辑反例，不声称当前服务这样实现。"},
        {"claim": "四项或2048字符保证整批3072", "counterexample": "若每项token数等于其2048字符，四项总和8192；即便每项≤3072，整批仍超3072。这是满足字符门的容量反例，不是Embedding-3实测。"},
        {"claim": "查询≤4096UTF8字节保证3072token", "counterexample": "逐字节而无合并的分词可对4096字节产生4096token；没有当前绑定规则就不能排除。"},
        {"claim": "费用预留充足即可发送", "counterexample": "即使费用为0或0.25元以内，容量超3072仍非法；两类约束独立。"}],
    "finite_coverage": {"tokenizer_executed": False, "token_counts": None,
        "bytes_only": {"html_focus": {k:v for k,v in text_value(html_focus).items() if k != "text"},
                       "continuation_reason": {k:v for k,v in text_value(reason).items() if k != "text"}},
        "later_if_only_exact_counts_available": "在两个实际payload builder生成规范字节之后、原grant.check/admission/dispatch之前，以当前proof版本+精确payload字节摘要拒绝未覆盖项，并对Embedding逐项/整批容量检查；原operator逐请求批准不能替代此限制。仅提条件性最小方案，本卡未改gateway或合同。"},
    "vendor_data": {"new_version_candidates": {"DeepSeek": 1, "Zhipu": 0},
        "candidate": {"publisher": "deepseek-ai", "model": "DeepSeek-V4.1-Flash-1017",
            "url": "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017",
            "observed_revision_prefix_from_official_search": "1bae0e1", "full_commit": None,
            "license_claim": "官方HF页面检索结果标MIT，未取得LICENSE原件，不作采用许可核证",
            "license_file_sha256": None, "original_file_sha256": None,
            "service_alias_model_name_binding": "当前官方price页映射1017",
            "current_service_tokenizer_template_byte_binding": None},
        "download_ledger": "download-ledger.jsonl", "downloads_attempted": 2, "downloaded_bytes": 0,
        "unpacked_bytes": 0, "unpacked_items": 0, "dependency_downloads": 0, "dependencies_installed": 0,
        "remote_code_executed": False, "trust_remote_code": False, "weights_downloaded": False,
        "status": "未取得元数据原字节，两次URLError后停止网络脚本；网页材料只作带范围的检索/正文返回记录，不冒充源文件hash"},
    "bounded_search": {"ledger": "web-request-ledger.json", "new_official_document_identities_attempted_conservative": 6,
        "cap": 12, "methods": {"DS_input": ["官方token用量页的资料链", "当前官方1017模型仓库/元数据及分词文件身份"],
            "Embedding_input": ["当前官方文档限定API/分词资料检索", "官方zai-org源限定分词资料检索"],
            "DS_output": ["当前API计数schema及thinking开关", "当前价格页的总token扣费定义"]},
        "no_more_same_lookup_card_recommended": True},
    "supplier_questions_unsent": {
        "DeepSeek": "请提供当前deepseek-flash（DeepSeek-V4.1-Flash-1017）API所用tokenizer、normalize/pretokenize和聊天/工具/JSON模板的明确版本或hash，以及与公开仓库commit的对应。我们只发纯文本JSON、thinking=disabled、完整请求UTF8≤65536；需要可保守界定prompt_tokens相对这些字节的关系及全部模板/特殊token开销，或能离线核证每个精确请求的等价规则。",
        "Zhipu": "请提供embedding-3当前API的tokenizer/预处理/特殊token版本与离线等价依据，并明确3072 Tokens是逐项还是整批限制、数组token及计费如何合计。我们使用512维、每批最多4项，需要同时保守核单项和整批容量；公开0.5元/百万token的本人项目适用币种/税费与权限由账号方另核。"},
    "account_facts": {"DeepSeek_balance_sufficient_user_statement": True, "console_verified": False,
        "DeepSeek_API_permission": None, "currency_tax_special_terms": None,
        "Zhipu_permission_balance_terms": None},
    "contract_change_required": None,
    "contract_change_note": "没有证明原公式为假；当前缺适用依据。取得原合同覆盖的上界即可保留现接口，不先扩Grant/wire。若只能核有限集合，前述发送前门须另经明确增量裁定。",
    "actual_provider_calls": 0, "actual_cost_microunits": 0, "Q_enabled": False}
save("metering-evidence.json", metering)

web_docs = ["https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017",
    "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/blob/main/tokenizer.json",
    "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/blob/main/tokenizer_config.json",
    "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/blob/main/chat_template.jinja",
    "https://docs.bigmodel.cn/cn/api/dev/api-reference/embedding",
    "https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4.1-Flash-1017"]
observations = json.loads((OUT / "tool-observations.json").read_bytes())
save("web-request-ledger.json", {"schema": "retrolume.task123.web-ledger.v1", "created_at": now.isoformat(),
    "observed_date_Asia_Shanghai": "2026-10-22", "exact_subrequest_timestamps": None,
    "timestamp_limit": "未逐项采绝对时刻；各工具wall与原返回保留，资料在本卡接收之后、本文件生成之前取得。不得把保存时刻冒充每次请求时刻。",
    "entries": observations["web"], "search_queries": 4, "web_subrequests": 17,
    "new_identities_conservative_including_failed_and_metadata": web_docs,
    "inaccessible_web_documents": 4, "download_failures": 2,
    "limits": "search批次没有返回与embedding-3匹配的可采用专属资料；无结果不证明不存在。只依赖官方文档/官方仓库身份，未采用无关OpenAI同名embedding或第三方结果。"})

pre = json.loads((OUT / "pre-snapshot.json").read_bytes())
post = []
patches = []
for row in pre["products"]:
    path = ROOT / row["path"]
    raw = path.read_bytes()
    before = Path(row["pre_copy"]).read_bytes() if row["exists"] else b""
    post.append({"path": row["path"], "pre_exists": row["exists"], "pre_sha256": row["sha256"],
                 "pre_bytes": row["bytes"], "post_bytes": len(raw), "post_sha256": digest(raw),
                 "changed": raw != before})
    patches.extend(difflib.unified_diff(before.decode("utf-8").splitlines(), raw.decode("utf-8").splitlines(),
                   fromfile="a/" + row["path"] if row["exists"] else "/dev/null", tofile="b/" + row["path"], lineterm=""))
    if path.suffix == ".py": ast.parse(raw.decode("utf-8"), filename=str(path))
save("post-snapshot.json", {"captured_at": now.isoformat(), "products": post})
(OUT / "product.diff").write_text("\n".join(patches) + "\n", encoding="utf-8")
batch = json.loads((OUT / "batch3/command.json").read_bytes())
tested = [{"path": row["path"], "matches_tested_bytes": digest((ROOT / row["path"]).read_bytes()) == row["sha256"]}
          for row in batch["input_bytes"]]
assert all(row["matches_tested_bytes"] for row in tested)
manifest = json.loads((ROOT / "DocuN/evidence/TASK-123/orchestration-20261022/input-manifest.json").read_bytes())
changed = {row["path"] for row in post if row["changed"]}
preserved = []
for row in manifest["rows"]:
    if row.get("relative_path") in changed: continue
    path = Path(row["path"])
    matched = digest(path.read_bytes()) == row["sha256"]
    preserved.append({"path": row["path"], "unchanged": matched})
assert all(row["unchanged"] for row in preserved)
save("final-consistency.json", {"at": now.isoformat(), "product_changed_count": len(changed),
    "post_matches_tested_bytes": tested, "unchanged_input_rows": preserved,
    "new_text_bounds_valid": True, "python_ast_valid": True,
    "scope_note": "仅文件身份、差异与文档检查；不重跑旧安全矩阵/分片/算术，不增加第四批验证"})
save("deviations-and-limits.json", {"test_batches": [
    {"batch": 1, "result": "timeout", "exit_code": 124, "elapsed_seconds": 120.031,
     "meaning": "首个TestClient用例未完成，无通过行为证据"},
    {"batch": 2, "result": "traceback_diagnostic_exit", "exit_code": 1, "elapsed_seconds": 20.453,
     "meaning": "20秒faulthandler终止；栈定位Windows socket._fallback_socketpair.accept，未进入API请求"},
    {"batch": 3, "result": "passed", "exit_code": 0, "elapsed_seconds": 1.828,
     "meaning": "平台正常审批的require_escalated，干净白名单环境与原tripwire保持；13方法通过"}],
    "selected_method_refinement": "初始列表中的旧OfflineApiTests.test_capabilities_without_storage在首个挂起前从未运行。静态pre main本来就覆盖缺key原reason为outbound_not_authorized，该旧断言不适用于当前原语义；最终改选既有guard_rejections并由新增测试核candidate缺key与最终关闭。未删除/改写旧测试或产品行为，未把未运行项称通过。",
    "lookup_errors": ["test_service_config.py不存在", "payload.py不存在", "preview/business.py不存在", "preview/service.py不存在", "系统Python无fastapi元数据；使用已存在backend/.venv"],
    "download_errors": "同一官方metadata两次URLError，脚本退出0不代表下载成功；底层原因未采够细，不断言官方仓库不可用。网页4个不可访问返回另保留。",
    "old_failures_and_unknowns_unchanged": True,
    "engineering_audit": "只有执行者普通Review与离线方法证据，不自签独立审计；新增秘密投影/资格解释供主控在稳定差异上裁定一次增量独审。"})
print(json.dumps({"written": ["finite-inputs.json", "metering-evidence.json", "web-request-ledger.json", "post-snapshot.json",
    "product.diff", "final-consistency.json", "deviations-and-limits.json"], "changed_products": len(changed),
    "tested_bytes_still_match": True}, ensure_ascii=False))
