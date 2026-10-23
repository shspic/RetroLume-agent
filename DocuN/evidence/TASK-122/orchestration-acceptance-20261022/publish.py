"""串行保存主控裁定、共享状态及下一完整任务卡，不执行产品。"""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
HERE = Path(__file__).resolve().parent
NEXT = ROOT / "DocuN/evidence/TASK-123/orchestration-20261022"
PREP = ROOT / "DocuN/evidence/TASK-122/preparation"
STAMP = datetime.now(timezone(timedelta(hours=8)))
NOW = STAMP.isoformat()


def sha(data):
    return sha256(data).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize(path):
    return Path(str(path).replace("\\\\", "/").replace("\\", "/"))


def raw(path):
    return Path(path).read_bytes()


checked = json.loads((HERE / "return-check.json").read_text(encoding="utf-8"))
assert checked["passed"] and checked["identity_count"] == 109
for row in checked["identity_rows"]:
    assert sha(raw(row["path"])) == row["actual"], row["path"]

state = ROOT / "DocuS/执行动态文档.MD"
arch = ROOT / "DocuS/架构动态文档.MD"
change = ROOT / "DocuS/文档变更记录.MD"
task122 = ROOT / "DocuN/tasks/TASK-122.md"
task123 = ROOT / "DocuN/tasks/TASK-123.md"
decision = ROOT / "DocuN/results/TASK-122-work-decision.md"
assert not task123.exists() and not decision.exists(), "已有成果，先核对，不覆盖"
state_before, arch_before, change_before, task_before = [raw(p) for p in (state, arch, change, task122)]
assert "文档v2.88" in state_before.decode("utf-8-sig").splitlines()[2]
assert "文档v1.60" in arch_before.decode("utf-8-sig").splitlines()[2]
assert "CHG-1597" in change_before.decode("utf-8-sig")[-2500:]
assert "CHG-1598" not in change_before.decode("utf-8-sig")

before_dir = HERE / "before"
before_dir.mkdir(exist_ok=False)
for name, data in [("execution-state.bytes", state_before), ("architecture.bytes", arch_before),
                   ("change-log.bytes", change_before), ("TASK-122.bytes", task_before)]:
    (before_dir / name).write_bytes(data)

report_hash = sha(raw(ROOT / "DocuN/results/TASK-122-result.md"))
assert report_hash == "a96890e662e83dcb7bed41f79b5383796bacc339cda220d5ccfe5806129cc11a"
README_hash = sha(raw(ROOT / "README.md"))
assert README_hash == "b64dc3d895acba72c0bdba5635d406d6b6953117cdf7b47866a73af592d5a201"

public_checks = {
    "schema": "retrolume.task122.orchestration-source-check.v1", "at": NOW,
    "scope": "对关键计量缺口作有限官方原文抽查；非重复122全量研究，非账号或实际API调用",
    "sources": [
        {"url": "https://api-docs.deepseek.com/zh-cn/quick_start/token_usage/", "observation": "公开说明为近似字符比例、实际以usage为准，并给tokenizer压缩包；本次返回正文未给Flash-1017模板及W+F保守证明。"},
        {"url": "https://api-docs.deepseek.com/api/create-chat-completion/", "observation": "公开schema含deepseek-flash、thinking disabled及max_tokens；没有据此将账号或完整计量上界改为已核。"},
        {"url": "https://docs.bigmodel.cn/cn/guide/models/embedding/embedding-3", "observation": "公开技术参数有3072 token和数组64项；支持512维。容量与费用证明仍分开，未实际调用。"},
        {"url": "https://api-docs.deepseek.com/api/list-models/", "observation": "针对用户是否全部用DeepSeek，核公开模型与API目录，未找到可替代Embedding-3的公开向量接口。只表示本次公开支持未建立，不宣称私有或未来产品不存在。"},
        {"url": "https://api-docs.deepseek.com/zh-cn/", "observation": "官方当前公开模型/调用方式为生成模型入口，未建立当前项目向量端点替换依据。"},
    ],
    "download_or_provider_request": 0, "Q": "FROZEN",
}
save_json(HERE / "public-source-check.json", public_checks)

account = {
    "schema": "retrolume.account-facts-user-statement.v1", "recorded_at": NOW,
    "source": "当前主控聊天，用户对集中非敏感账号问题的回答",
    "user_exact_text": "可以都用deep seek吗，deep seek额度充足",
    "DeepSeek_balance_sufficient": {"value": True, "grade": "C 用户声明", "verified_in_account_console": False},
    "DeepSeek_model_API_permission": None, "billing_currency_tax_and_terms": None,
    "Zhipu_account_permission_balance_terms": None,
    "provider_replacement_adopted": False,
    "interpretation": "用户表达单供应商意愿并声明DeepSeek额度充足；不是向量接口已存在、其它账号事实或移除混合检索的批准。主控已解释公开接口未建立替换依据。",
    "secrets_or_private_account_access": False,
}
save_json(HERE / "account-facts-received.json", account)

decision_text = f"""# TASK-122 / R-116 主控验收与后续裁定

{NOW}，Asia/Shanghai。验收范围为启用前置资料和A—D操作包，不是正常Q启用、服务语义或产品发布。

## 本次验收

文档准备交付通过并关闭。主控重新核对32项锁定输入、24个返回产物、结果、README前后及50个读取文件身份，共109条引用无漂移；结果16827字节，SHA256 {report_hash}。README当前26346字节，SHA256 {README_hash}，原文保留的四处替换及操作限制补充符合卡面。原TASK120/121报告、预算、事件与公共七规则不变。

重算89个动作、13组、28个Must及分额守恒；八原文按已读逐行规则静态核得24片，分别4/4/5/1/1/2/3/4，空缓存6批，任意四片embedding规范JSON静态上界446字节。主控没有执行产品分片或导入。条件费用算术成立不等于本人账号报价，更不等于token上界已经证明。细节见同根orchestration-acceptance-20261022/return-check.json。

范围轴为已完成；证据轴对本次文档交付充分；执行控制按已存账未见确定超限，但原元数据失败至少2项、若干子命令退出和未逐项计时unknown保留。交付保守工具记账1340.9775537/2400秒含收尾预留，已知命令实测37.4398905秒，不把预留叫实际实测。不新增文档独审，亦未作独立进程审计。产品执行、provider和费用0据已有材料分级记录，主控没有实际启动资源。

## 采纳与不扩大的边界

采纳24片/6索引、L05额外4调用及89/22.25预留矩阵为后续准备基线。它纠正旧静态规模假设，未增来源、改原文或删Must，也不改已批准100/25和48/28/24、12/7/6分额。学习43、面试28、补证18；面试无失败余量，后续若实际不足按原键留账并交精确缺口，不能跨活动借额或新建根清账。

计量和实际部署仍未通过。当前tokenizer/完整模板/disabled额外计价及Embedding单项和保守整批3072 token依据、账号适用事实、真实normal绑定、实际readiness和首次主控回执缺失。主控对三个关键官方页面作有限抽查，确认不能由近似字符比例/示例补齐上述证明；没有复跑122整个调研。资料不存在的保证不能虚构，公开条款的合理适用范围外也不自加无限保证或必须零留存等新标准。

用户本轮确认DeepSeek额度充足，按用户声明保存，不冒充后台余额核验或同时证明权限/币种税费。用户询问能否都用DeepSeek；当前官方公开支持未建立替代Embedding-3的向量接口，主控已答复。该询问未作为删除混合检索、更换向量模型或已采用供应商变更。本人账号缺项不阻塞零付费前置工程，密钥不进聊天。

## 直接推进

登记TASK123/R117，优先沿TASK122原A+窗口，一张完成有限官方分词资料取得/离线资格核证、现capabilities非敏感只读投影工程、精确输入与部署交接。完整合同和明确7200秒/24h、资料/隔离依赖范围、运行0许可在TASK123本轮orchestration目录。普通实现细节由原有效开发与采用范围覆盖，不重问模型或预算。

本卡已关闭，不沿原TASK122许可执行产品或下载；原120/121运行许可同样不恢复。TASK123仅待人工转交，未宣称已接收/开始。稳定差异才按真正新增风险安排一次Review或独立增量审查，不重开已关闭120修复循环。

Q继续冻结，T0/72h空，真实provider/费用0；正常资源创建与启用不在TASK123许可。STEP018仍进行中/部分验证，STEP019/020、M1、项目及发布未通过。
"""
decision.write_text(decision_text, encoding="utf-8")

task122_notice = f"""# TASK122准备交付已验收结束，原许可不转为执行权

{NOW}。主控已接受A—D资料准备和README限制补充，结论见DocuN/results/TASK-122-work-decision.md。Q仍冻结，计量/账号/normal/首次启用门未核齐；不得据本卡运行产品、下载tokenizer或启用Q。后续最小前置工程沿新TASK123/R117完整卡，不清零旧历史和失败。以下TASK122原卡原字节保留。

""".encode("utf-8")
task122.write_bytes(task122_notice + task_before)

state_header = f"""# 执行动态文档

文档v2.89，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.61、task_model/07。以下v2.88原字节保留。

## TASK122前置资料交付通过，TASK123计量/readiness最小工程待转交

{NOW}。TASK122/R116的A—D准备及README当前限制更新已完成并由主控验收关闭。主控有限核109项身份/原报告hash a96890e6…c11a，24片/6批、89逐请求动作/28Must和分额/条件费用算术通过。它不是服务行为、账号或实际计费证明，不新增文档独审；原元数据至少2失败、子退出/计时unknown保留，保守工具记1340.9775537/2400。详情DocuN/results/TASK-122-work-decision.md与本轮orchestration-acceptance-20261022。

后续准备采纳八原文24片/6索引及L05额外4次，预计41 model/41 query/6 index/1 HTML=89次，22.25元预留。学习43/48、面试28/28、补证18/24；面试无失败余量留明，不改100/25及固定分额，不借额、不删Must。实际Q已用仍0，不将预计“剩余”当已发生扣账。token/framing/额外计价、Embedding3072容量、本人账号适用、正常绑定和首次主控启用回执仍缺。

用户本轮声明DeepSeek额度充足，未证明权限/币种税/特约；询问全部改DeepSeek并非采用供应商切换。当前官方公开目录未建立替代Embedding-3的向量接口，维持生成DeepSeek/检索向量Embedding-3的已采用边界，等待账号事实，不擅自移除混合检索。集中账号提问已答复该部分，不反复索key或要求释放内存。

TASK123/R117已登记，优先沿原122 A+核查窗转工程，完整卡和事实/manifest/permit已保存读回，待用户人工转交；无接收、启动或在途执行声明。一次完成允许的官方分词数据/隔离最小依赖核证、现capabilities安全只读投影、精确有限输入及部署交接；新许可24h、工具7200秒含600收尾，仅离线/有限公开资料，PG/Docker/API服务/browser/Job/真实模型/费用/Git均0，不预改授权/计费合同。真正外部证明缺失只留相关启用门，不使其他工程重做；按新实际风险集中Review/增量审查。

TASK120有限工程关闭、TASK121审计结束和五项缺陷关闭保持；历史控制不通过、149失败/117旧81及原69357.418110工具/2943.704295持有/2113.8359792审计账不重置，旧root/PG64/64和全部旧时窗不恢复。主控本轮只有文件/官方原文有限核对，未探测实时资源。Q冻结，T0/72h空；STEP018仍进行中/部分验证，019/020/M1/项目/发布未通过。CHG1598—1605，下一1606。

## 以下为v2.88及更早历史

""".encode("utf-8")

arch_header = f"""# 架构动态文档

文档v1.61，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.89、task_model/07。以下v1.60原字节保留。

## 正常Q前置事实已整理，计量与只读可观察性进入最小补齐

{NOW}。TASK122完成启用前置资料/关闭草案/操作包；当前所有运行与付费门继续关闭。主控采纳原八文逐行24片/6索引及完整89请求矩阵的准备规模，不改变原来源和混合检索架构、不改固定100/25预算或三个活动分额。公式中的线上bytes、token和服务模板开销仍需当前适用证明，Embedding容量须独立核；公开示例与key存在都不等于normal实际可用。

TASK123获准的计划增量只是在main已装载状态和现capabilities中增加不授权的非敏感只读投影，并有限核证官方分词材料。严禁诊断触发QAuthority/ControlHub/配置再装载/新PG探针，不输出密钥/DSN/私有路径，原认证/DataContext/关闭行为保持。尚未实现或验证，不将该计划记成已落地。旧Q v2协议、费用账、schema和已验安全主体冻结；不预改receipt TASK谱系。

DeepSeek生成/评价与Embedding-3检索向量分工保持。用户说明DeepSeek额度充足及询问单供应商；当前公开接口核查未建立等价向量替换依据，未采用架构切换。数据条款按原实际要求核适用，不新增零留存或不训练等未要求保证。有限工程关闭与历史控制不通过的原限制原样继承；Q/STEP018整体/发布仍未放行。

## 以下为v1.60及更早历史

""".encode("utf-8")

# 先在唯一状态账占号，继而保存完整卡；没有人为转交就不标已派发。
state.write_bytes(state_header + state_before)
arch.write_bytes(arch_header + arch_before)
contract = raw(NEXT / "contract.md")
assert "TASK-123 / R-117" in contract.decode("utf-8")
assert "*" not in contract.decode("utf-8")
task123.parent.mkdir(exist_ok=True)
task123.write_bytes(contract)

frozen = []
rule_snapshot = json.loads((ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json").read_text(encoding="utf-8-sig"))
for item in rule_snapshot:
    p = normalize(item["absolute_path"])
    assert sha(raw(p)) == item["sha256"]
    frozen.append({"path": p.as_posix(), "sha256": sha(raw(p)), "bytes": p.stat().st_size, "kind": "locked_rule"})

inputs = [
    "AGENTS.md", "DocuS/最终需求文档.MD", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD",
    "DocuN/results/TASK-122-work-decision.md", "DocuN/results/TASK-122-result.md",
    "DocuN/evidence/TASK-122/preparation/official-facts.json", "DocuN/evidence/TASK-122/preparation/web-request-ledger.json",
    "DocuN/evidence/TASK-122/preparation/readiness-plan.json", "DocuN/evidence/TASK-122/preparation/remaining-must-matrix.json",
    "DocuN/evidence/TASK-122/preparation/sample-fragments.json", "DocuN/evidence/TASK-122/preparation/cost-calculation.json",
    "DocuN/evidence/TASK-122/preparation/operation-runbook.md", "DocuN/evidence/TASK-122/preparation/decisions-and-blockers.json",
    "DocuN/evidence/TASK-122/orchestration-acceptance-20261022/return-check.json",
    "DocuN/evidence/TASK-122/orchestration-acceptance-20261022/account-facts-received.json",
    "DocuN/evidence/TASK-122/orchestration-acceptance-20261022/public-source-check.json",
    "DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json",
    "DocuN/evidence/TASK-116/design/sample-inputs.json", "DocuN/evidence/TASK-116/design/acceptance-contract.md",
    "DocuN/evidence/TASK-116/design/integration-contract.md",
    "backend/app/main.py", "backend/app/activities/api.py", "backend/app/service_config.py",
    "backend/app/retrieval/service.py", "backend/app/retrieval/evidence.py", "backend/app/operator/q_request.py",
    "backend/app/capabilities/contracts.py", "backend/app/capabilities/embedding.py",
    "config/activity.example.json", "config/integration.example.json", "config/q-approval.example.json",
    "README.md", "deploy/q-approval.md", "deploy/start_local.py", "deploy/initialize-materials.py",
]
for rel in inputs:
    p = ROOT / rel
    assert p.is_file(), rel
    frozen.append({"path": p.as_posix(), "sha256": sha(raw(p)), "bytes": p.stat().st_size,
                   "kind": "project_input", "relative_path": rel})
save_json(NEXT / "input-manifest.json", {"frozen_at": NOW, "rows": frozen,
    "task": "TASK-123", "R": "R-117", "instruction": "共享文档只作版本定位；产品和固定原文须核身份，报告保留原字节"})

facts = {
    "task": "TASK-123", "R": "R-117", "received_or_started": False, "prepared_at": NOW,
    "previous_tasks": {"TASK120": "FINITE_FEATURE_AND_EVIDENCE_CLOSED_HISTORICAL_CONTROL_FAILED",
        "TASK121": "AUDIT_COMPLETE_ENDED", "TASK122": "PREPARATION_DELIVERY_ACCEPTED_ENDED"},
    "source_identity_check": "../.. /TASK-122/orchestration-acceptance-20261022/return-check.json",
    "baseline": {"sources": 8, "static_fragments": 24, "index_batches": 6, "Musts": 28,
        "planned_requests": 89, "planned_reserved_microunits": 22250000,
        "global_max_requests": 100, "global_max_cost_microunits": 25000000,
        "role_requests": [48, 28, 24], "role_cost_microunits": [12000000, 7000000, 6000000],
        "planned_role_requests": [43, 28, 18], "interview_failure_buffer_requests": 0},
    "account_facts_source": (HERE / "account-facts-received.json").as_posix(),
    "DeepSeek_balance_user_statement_received": True, "embedding_provider_replacement_adopted": False,
    "prior_minimum_metadata_failures": 2, "prior_subcommand_failures_unknown_retained": True,
    "previous_TASK120_failures": 149, "previous_TASK117_failures": 81,
    "Q": "FROZEN", "T0": None, "real_provider_calls": 0, "real_cost_microunits": 0,
    "no_old_runtime_permission_revived": True,
}
facts["source_identity_check"] = (HERE / "return-check.json").as_posix()
save_json(NEXT / "handoff-facts.json", facts)

permit = {
    "permit_id": "TASK-123-Q-METERING-AND-READINESS-OFFLINE-20261022", "task": "TASK-123", "R": "R-117",
    "issued_at": NOW, "calendar_deadline": (STAMP + timedelta(hours=24)).isoformat(),
    "contract_sha256": sha(contract), "input_manifest_sha256": sha(raw(NEXT / "input-manifest.json")),
    "status": "SAVED_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED",
    "route": "A+ 承接TASK122原窗口；不可续则增强工程新窗；不使用121独审窗口，不委派",
    "budgets": {"tool_wall_seconds": 7200, "closing_reserve_within_wall_seconds": 600,
        "default_command_seconds": 60, "targeted_test_batch_seconds": 120,
        "targeted_test_batches_initial_plus_justified_corrections": 3,
        "new_official_document_identities": 12, "download_total_MiB": 128, "single_file_MiB": 64,
        "unpacked_total_MiB": 256, "unpacked_files": 512, "version_candidates_per_provider": 2},
    "product_write_allowlist": ["backend/app/main.py", "backend/app/activities/api.py", "backend/app/q_readiness.py",
        "backend/tests/test_q_readiness.py", "necessary_minimal_existing_offline_config_activity_fixture_adaptation",
        "README.md", "deploy/q-approval.md"],
    "evidence_write_root": "DocuN/evidence/TASK-123/execution/", "result": "DocuN/results/TASK-123-result.md",
    "official_data_and_isolated_minimum_pinned_tokenizer_dependency_allowed": True,
    "product_global_venv_lock_mutation_allowed": False, "remote_custom_code_pickle_model_weights_allowed": False,
    "runtime_caps": {key: 0 for key in ["provider_calls", "paid_cost_microunits", "PG", "SQL", "Docker",
        "API_service_starts", "browser", "Job", "preview", "Git_writes", "subagents"]},
    "local_pure_projection_and_inprocess_synthetic_TestClient_tests_allowed": True,
    "existing_financial_authorization_grant_protocol_or_contract_change_allowed": False,
    "activation_or_normal_resource_creation_allowed": False,
}
save_json(NEXT / "permit.json", permit)

entries = [
    (1598, "DocuN/results/TASK-122-work-decision.md", "验收A—D准备交付，采纳24片/6批/89矩阵，计量账号实际启用门未通过；新账号答复分级留证。"),
    (1599, "README.md", "登记执行者122获准的四处现状替换与操作限制补充，主控核前后hash及实际diff，未再次修改README。"),
    (1600, "DocuS/架构动态文档.MD", "v1.61登记待实现的非敏感readiness投影和计量核证，保持原供应商分工和关闭边界。"),
    (1601, "DocuS/执行动态文档.MD", "v2.89登记122文档关闭、123R117待转交、89请求准备基线和真实Q前置缺口，不重置旧账。"),
    (1602, "DocuN/tasks/TASK-122.md", "置顶本卡准备验收结束通知，原完整卡原字节保留，旧许可不转产品执行权。"),
    (1603, "DocuN/tasks/TASK-123.md", "保存一张完整零付费计量核证/readiness工程卡，原A+窗口优先，仅待人工转交。"),
    (1604, "DocuN/evidence/TASK-122/orchestration-acceptance-20261022", "保存109身份/文档算术、有限官方抽查、非敏感用户声明、旧共享和保存核证，主控产品运行0。"),
    (1605, "DocuN/evidence/TASK-123/orchestration-20261022", "保存冻结合同/输入/事实/精确许可与读回，禁止正常资源和Q激活，隔离离线资料取得范围明确。"),
]
log = "\r\n\r\n" + "\r\n\r\n".join(f"- CHG-{number}，{NOW}，Codex编排Agent，{path}。{description}" for number, path, description in entries) + "\r\n"
change.write_bytes(change_before + log.encode("utf-8"))

assert raw(state).endswith(state_before)
assert raw(arch).endswith(arch_before)
assert raw(change).startswith(change_before)
assert raw(task122).endswith(task_before)
assert raw(task123) == contract
for path, expected in checked["unchanged_objects_for_publication"].items():
    assert sha(raw(ROOT / path)) == expected, path
for row in checked["identity_rows"]:
    if normalize(row["path"]) in {state, arch, task122}:
        continue
    assert sha(raw(row["path"])) == row["actual"], row["path"]
for row in frozen:
    assert sha(raw(row["path"])) == row["sha256"], row["path"]

proof_paths = [decision, state, arch, change, task122, task123, NEXT / "contract.md", NEXT / "permit.json",
               NEXT / "input-manifest.json", NEXT / "handoff-facts.json", HERE / "return-check.json",
               HERE / "account-facts-received.json", HERE / "public-source-check.json"]
proof = {"saved_at": NOW, "status": "TASK122_ACCEPTED_TASK123_READY_FOR_MANUAL_HANDOFF", "next_CHG": 1606,
    "task123_received_or_running": False, "orchestrator_product_runtime": 0, "Q": "FROZEN", "T0": None,
    "preserved_previous_state_architecture_change_task_bytes": True,
    "protected_original_results_ledgers_rules_unchanged": True,
    "files": [{"path": p.as_posix(), "bytes": p.stat().st_size, "sha256": sha(raw(p))} for p in proof_paths]}
save_json(HERE / "save-proof.json", proof)
save_json(NEXT / "dispatch-readback.json", {"saved_at": NOW, "contract_matches_card": raw(task123) == contract,
    "contract_sha256": sha(contract), "card_bytes": len(contract), "full_text_read_back": task123.read_text(encoding="utf-8") == contract.decode("utf-8"),
    "input_identity_count": len(frozen), "received": False, "started": False, "manual_handoff_required": True})
print(json.dumps({"status": proof["status"], "prior_identity_rows": 109, "new_input_identity_rows": len(frozen),
    "task123_card_bytes": len(contract), "next_CHG": 1606, "orchestrator_runtime": 0, "Q": "FROZEN"}, ensure_ascii=False))
