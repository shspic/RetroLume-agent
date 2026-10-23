"""保存工程回收事实与集中独审合同，保留旧共享和原证据。"""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
HERE = Path(__file__).resolve().parent
AUDIT = ROOT / "DocuN/evidence/TASK-124/orchestration-20261022"
EXECUTION = ROOT / "DocuN/evidence/TASK-123/execution"
STAMP = datetime.now(timezone(timedelta(hours=8)))
NOW = STAMP.isoformat()


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


checked = load(HERE / "return-check.json")
assert checked["passed"] and checked["identity_count"] == 118
for item in checked["identities"]:
    assert sha(raw(item["path"])) == item["actual"], item["path"]

paths = {
    "state": ROOT / "DocuS/执行动态文档.MD", "architecture": ROOT / "DocuS/架构动态文档.MD",
    "change": ROOT / "DocuS/文档变更记录.MD", "TASK123": ROOT / "DocuN/tasks/TASK-123.md",
}
old = {name: raw(path) for name, path in paths.items()}
assert "文档v2.89" in old["state"].decode("utf-8-sig").splitlines()[2]
assert "文档v1.61" in old["architecture"].decode("utf-8-sig").splitlines()[2]
assert "CHG-1605" in old["change"].decode("utf-8-sig")[-2500:]
assert "CHG-1606" not in old["change"].decode("utf-8-sig")
decision_path = ROOT / "DocuN/results/TASK-123-work-decision.md"
card_path = ROOT / "DocuN/tasks/TASK-124.md"
assert not decision_path.exists() and not card_path.exists(), "已保存则先核对，不覆盖"

backup = HERE / "before"
backup.mkdir(exist_ok=False)
for name, data in old.items():
    (backup / (name + ".bytes")).write_bytes(data)

report = load(EXECUTION / "save-proof.json")["result"]
assert report["sha256"] == "d64c3abb832589ab9f826e0327f97a64bd1c2df7c62a9d4b63684f2549886c36"
decision = f"""# TASK-123 / R-117 主控回收与集中增量审计安排

{NOW}，Asia/Shanghai。工程候选、有限输入和资料结论已真实返回；本次为主控有限文件核证，代码独立结论仍待TASK124。未执行产品、测试或服务。

## 核到的事实

统一报告15558字节，SHA256 {report['sha256']}。主控重新核118条身份，包括48个返回产物、六个最终文件、四个pre副本、43发卡输入按允许变化适配、六个as-run输入、日志和旧不可变结果/账。零漂移。最终batch3原命令绑定当前四个新改Python及两既有测试，原始stderr/summary/退出0一致，13方法无failure/error/skip；主控采纳这批有限离线证据，不重跑。

初批120.031秒超时、第二批20.453秒诊断、第三批1.828秒经平台正常审批通过原件保留。超时124是父控制映射，下载外层0只说明保存了失败，二者均不冒成功。工具总实测unknown，3554.557411/7200是按签发至收尾包络加未记录余量/600收尾预留的保守账，不是实测。两下载失败、四网页不可访问、猜路径/元数据失败及旧122至少2失败/unknown保留。卡内三测试批用满；本轮不恢复其测试批或任何真实运行额度。

六文件实际变化是main/api、新q_readiness.py/新离线测试、README与deploy/q-approval.md。新增diagnostics.readiness从启动对象形成快照，候选/最终层、key presence、严格返回allowlist、限额及已装载摘要引用可辨。它不授外发资格，account/metering/normal等qualification继续unknown；原费用/Grant/loader协议/DDL/worker/前端/数据权限未改。以上是被审候选边界，不能因13方法通过就直接签独立安全通过。

两段有限文字的hash与长度核对成立，HTML405字节、继续理由159字节，真实父/IDs/typed/payload/description/artifact和主控首次启用仍未建立；不把文本冻结当语义通过。

## 计量停止点与验收分界

作者对max_tokens包含reasoning明细的当前官方契约给出有限文档推论，未据此填写完整token资格。其适用性列入本轮集中复核，不扩成本人报价已核。输入分词/完整服务模板的版本适用与Embedding单项和保守整批容量仍缺外部材料。下载/访问失败不证明资料不存在，也没有反证证明原公式必假。当前本人账号只知用户声明DeepSeek额度充足，权限/币种税/特约及智谱事实未补，不重复索key。

Q继续冻结，T0/72h空、provider/费用0。禁止再派相同公开搜索/协议设计卡机械续试；外部材料真缺就等精确供应商依据或以后形成可审阅的最小变更决定，其余交付独立完成。原89请求/28Must/24片6索引/22.25元预留和100/25固定分额继承，不加次数或删除Must。

## 一次集中增量复核

新增服务启动投影、key/模型/摘要公开和资格解释涉及敏感信息与权限语义，按锁定AGENTS第5节及TASK123原合同，需要在稳定候选作一次集中独立增量审查。不是对旧120/121重审，也不增加真实业务验证。

TASK124/R118完整卡已保存读回，优先原TASK121独立A+窗口，须未参与123；不符合就新隔离审计窗。只审六文件和直接依赖、原13方法及失败账、有限文字和计量分级，工具1800秒含240收尾、24h、所有产品运行和联网0。只准保存审计证据/结果，不写产品或共享账。待用户人工转交，未称已接收或运行。

当前TASK123范围为实现候选交付/离线证据已核，最终验收待TASK124，非启用通过。原120有限工程关闭、121五项关闭及历史执行控制失败留账；STEP018整体/019/020/M1/项目/发布不通过或未通过的原状态不变。
"""
decision_path.write_text(decision, encoding="utf-8")

state = f"""# 执行动态文档

文档v2.90，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.62、task_model/07。以下v2.89原字节保留。

## TASK123完整候选已回收冻结；TASK124集中独立增量复核待转交

{NOW}。TASK123/R117返回六文件readiness工程及有限文字/计量分级。主控核118身份、48产物、六post/四pre、43输入允许差异及最终六个as-run字节/日志，零漂移；报告15558字节/hashd64c3abb…886c36。batch3原证据13方法无failure/error/skip、exit0、父1.828秒采纳，不重跑。范围为候选完成、离线定向证据已核，最终验收待独立增量结论，不因自评或报告保存直接签通过。

新增main启动snapshot及capabilities diagnostics.readiness，公开有限非敏感身份/allowlist/限额/存在性/摘要引用，candidate/effective/qualification分层；原Q资格和全部token/账号/normal未核保持关闭。新模块/测试和README/deploy说明均已保存，旧Grant/费用/DDL/worker/前端及loader协议不改。两段有限HTML/继续理由文字冻结405/159字节，当前父和真实产物仍待未来部署。

初批120.031超时、第二批20.453诊断、第三批审批后通过的原件保留；两下载失败/四不可访问网页及路径/元数据错误保留。新工具精确总量unknown，按包络保守3554.557411/7200含600收尾，三测试批用尽；不借余量跑业务，旧1221340.9775537及旧控制unknown不抹零。当前没有新资源启动，主控没有实时资源探针，过去停止证明不当新鲜状态。

TASK124/R118已登记，完整只读集中增量合同/输入/许可真实保存读回，待用户人工转交，无已接收/启动事实。优先原121独审A+窗口且未参与123，否则新隔离窗；只审新六文件/直接影响、13方法原件/控制/计量分级与有限文字，工具1800秒含240收尾/24h，运行与联网全0。新增秘密投影/资格解释需要该一次稳定增量审查；旧120/121关闭项不重审。

计量启用仍缺供应商现行输入分词/完整模板版本绑定、Embedding单项及保守整批容量和本人账号适用材料。max_tokens/reasoning文档推论待限定审查，不等于完整计费门通过。不再派同样公开查核设计卡或以增加margin/短样本/余额冒证明。已知用户声明DeepSeek额度充足，原两provider分工与100/25、分额保持；账号新事实未提供，不反复问key。

TASK120有限工程关闭、TASK121审计结束/五缺陷关闭、历史控制不通过/149及原117的81失败/69357.418110工具/2943.704295持有/2113.8359792原审计与root/PG64/64继续留档，不恢复任何旧许可。Q冻结、T0/72h空、实际provider/费用0；89请求/28Must/24片6批预留基线沿用；STEP018进行中/部分验证，019/020/M1/项目/发布未通过。CHG1606—1614，下一1615。

## 以下为v2.89及更早历史

""".encode("utf-8")
architecture = f"""# 架构动态文档

文档v1.62，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.90、task_model/07。以下v1.61原字节保留。

## 启动readiness有限投影已实现候选，计量启用资格继续关闭

{NOW}。TASK123新增backend/app/q_readiness.py与main启动capture，现capabilities增加diagnostics.readiness，candidate/effective、key presence、严格allowlist/限额与已装载grant/manifest及price/activation/instance摘要引用分层。快照不提供请求授权，qualification对账号/计量/实际返回/normal均unknown；原loader/费用/Grant/协议、PG探针及认证/DataContext主体不改。仅13方法离线合成证据，不宣称normal部署、PG/profile或真实供应商通过。六文件稳定候选交TASK124集中独立增量，尚未最终验收。

HTML focus与继续理由以disabled有限文字补齐，依赖同活动当前合格COMMIT父与原CAS，不产生真实控件/description/artifact或新接口。部署说明反映现有实际参数与初始化只覆盖001的不足，没有创建normal/签启用回执。

计量材料没有获得当前分词/完整模板和服务绑定，Embedding单项/保守整批3072仍未获证；输出max_tokens/reasoning的文档推论只限原契约，留待本轮独立分级，不据此扩大总token或本人价格资格。外部缺证保持关闭，不新造计费平台/无限保证；当前未采用供应商替换、预算调整或新的动态计量接口。旧已验Q v2主体、有限关闭及历史控制失败限制继续继承。

## 以下为v1.61及更早历史

""".encode("utf-8")

# 唯一状态账先占号；随后保存完整卡，只有人工转交后才可能开始。
paths["state"].write_bytes(state + old["state"])
paths["architecture"].write_bytes(architecture + old["architecture"])
notice = f"""# TASK123候选已回收冻结，原工程停止；待TASK124独立增量复核

{NOW}。主控已核最终六文件与13方法证据身份，报告/代码/测试/资料冻结，无追加测试或外发许可。最终验收待TASK124，只读原件可用，不自行续搜或启用Q。主控事实见DocuN/results/TASK-123-work-decision.md。以下完整原卡原字节保留。

""".encode("utf-8")
paths["TASK123"].write_bytes(notice + old["TASK123"])
contract = raw(AUDIT / "contract.md")
assert b"TASK-124 / R-118" in contract and "*" not in contract.decode("utf-8")
card_path.write_bytes(contract)

manifest_paths = {}


def add(path, kind, usage=None):
    p = norm(path)
    assert p.is_file(), p
    key = p.as_posix()
    if key in manifest_paths:
        return
    manifest_paths[key] = {"path": key, "bytes": p.stat().st_size, "sha256": sha(raw(p)), "kind": kind}
    if usage:
        manifest_paths[key]["usage"] = usage


for row in load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json"):
    add(row["absolute_path"], "locked_rule")
    assert manifest_paths[norm(row["absolute_path"]).as_posix()]["sha256"] == row["sha256"]

for rel in ["AGENTS.md", "DocuS/最终需求文档.MD",
    "DocuN/evidence/TASK-123/orchestration-20261022/contract.md",
    "DocuN/evidence/TASK-123/orchestration-20261022/permit.json",
    "DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json",
    "backend/app/service_config.py", "backend/app/retrieval/service.py", "backend/app/operator/q_request.py",
    "backend/app/capabilities/contracts.py", "backend/app/capabilities/embedding.py", "backend/app/capabilities/gateway.py",
    "backend/app/local_session.py", "backend/tests/test_activity_workspace_config.py", "backend/tests/test_activity_workspace_api.py",
    "DocuN/evidence/TASK-116/design/sample-inputs.json", "DocuN/evidence/TASK-116/design/acceptance-contract.md",
    "DocuN/evidence/TASK-122/preparation/remaining-must-matrix.json",
    "DocuN/evidence/TASK-123/execution/delivery-manifest.json", "DocuN/evidence/TASK-123/execution/save-proof.json"]:
    add(rel, "original_contract_or_direct_dependency")
for row in load(EXECUTION / "delivery-manifest.json")["rows"]:
    add(row["path"], "as_returned_artifact", "只有身份与原始材料用途，作者自查结论不作独立证明")
for row in load(EXECUTION / "post-snapshot.json")["products"]:
    add(row["path"], "frozen_final_change")

save_json(AUDIT / "input-manifest.json", {"task": "TASK-124", "R": "R-118", "frozen_at": NOW,
    "rows": list(manifest_paths.values()), "independence": "不含工程统一结果、聊天或主控代码结论；计量文件是被审交付，不是作者自证",
    "runtime_permission": False})

permit = {"permit_id": "TASK-124-Q-READINESS-CONCENTRATED-DELTA-AUDIT-20261022", "task": "TASK-124", "R": "R-118",
    "issued_at": NOW, "calendar_deadline": (STAMP + timedelta(hours=24)).isoformat(),
    "status": "SAVED_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED", "contract_sha256": sha(contract),
    "input_manifest_sha256": sha(raw(AUDIT / "input-manifest.json")),
    "role": "A+ independent auditor; previous TASK121 window only if independent of TASK123; otherwise fresh isolated auditor",
    "tool_wall_seconds": 1800, "closing_reserve_within_cap_seconds": 240, "single_command_seconds": 60,
    "allowed_writes": ["DocuN/evidence/TASK-124/audit/", "DocuN/results/TASK-124-result.md"],
    "allowed_computation": "stdlib bounded file reads, sha256, JSON and finite diff only",
    "runtime_caps": {name: 0 for name in ["product_import", "compile", "unittest", "TestClient", "PG", "SQL", "Docker",
        "API", "browser", "Job", "provider_calls", "paid_cost", "network", "download", "install", "Git_writes", "subagents"]},
    "private_config_account_console_vault_reads": False, "implementation_or_shared_state_writes": False,
    "old_TASK121_audit_conservative_seconds_retained": 2113.8359792,
    "old_TASK123_conservative_seconds_retained": 3554.557411,
    "old_TASK122_conservative_seconds_retained": 1340.9775537,
    "new_scope_does_not_reset_prior_failures_or_restore_old_permissions": True,
    "Q": "FROZEN", "activation_permission": False,
}
save_json(AUDIT / "permit.json", permit)

facts = {"prepared_at": NOW, "engineering_candidate_returned": True, "TASK123_final_acceptance": "PENDING_INDEPENDENT_DELTA",
    "identity_evidence": (HERE / "return-check.json").as_posix(),
    "final_changed_files": 6, "as_returned_evidence_artifacts": 48, "as_run_offline_methods": 13,
    "real_Q_calls": 0, "T0": None, "normal_created": False,
    "no_more_identical_public_research_task": True, "execution123_frozen": True,
    "audit124_received": False, "audit124_started": False,
    "original_engineer_result": {"path": report["path"], "sha256": report["sha256"], "usage": "主控保存，审计不读自评"}}
save_json(HERE / "candidate-receipt.json", facts)

changes = [
    (1606, "DocuN/results/TASK-123-work-decision.md", "核收稳定六文件候选/13方法原证据，计量与账号门仍缺，安排一次限定集中独审，未签工程最终通过。"),
    (1607, "DocuS/架构动态文档.MD", "v1.62登记启动snapshot/capabilities新投影候选和有限文字、原资格关闭与计量停止点。"),
    (1608, "DocuS/执行动态文档.MD", "v2.90登记123回收冻结及124R118保存待转交，旧失败和预算/unknown保持。"),
    (1609, "DocuN/tasks/TASK-123.md", "置顶工程回收冻结通知，旧完整合同原字节保留，不恢复测试或运行许可。"),
    (1610, "DocuN/tasks/TASK-124.md", "保存六文件/直接影响/原离线证据/计量分级的集中只读独审卡，优先原121独立窗口。"),
    (1611, "README.md", "登记123执行者获准的诊断说明增量，当前hash0410c757…04d938；本轮主控未修改。"),
    (1612, "deploy/q-approval.md", "登记123执行者获准的readiness字段/未知/原PG探测说明，hash0a3a44dd…3cb60；待独立增量确认。"),
    (1613, "DocuN/evidence/TASK-123/orchestration-return-20261022", "保存118身份/原件绑定、候选回收与旧共享快照，主控产品运行0。"),
    (1614, "DocuN/evidence/TASK-124/orchestration-20261022", "保存独立合同/准确输入/1800秒零运行许可与人工转交读回，不自动派发。"),
]
addition = "\r\n\r\n" + "\r\n\r\n".join(f"- CHG-{num}，{NOW}，Codex编排Agent，{path}。{why}" for num, path, why in changes) + "\r\n"
paths["change"].write_bytes(old["change"] + addition.encode("utf-8"))

for name in ("state", "architecture", "TASK123"):
    assert raw(paths[name]).endswith(old[name]), name
assert raw(paths["change"]).startswith(old["change"])
assert raw(card_path) == contract
for rel, expected in checked["protected_for_publication"].items():
    assert sha(raw(ROOT / rel)) == expected, rel
for row in load(EXECUTION / "delivery-manifest.json")["rows"]:
    assert sha(raw(norm(row["path"]))) == row["sha256"], row["path"]
for item in checked["identities"]:
    if norm(item["path"]) in set(paths.values()):
        continue
    assert sha(raw(item["path"])) == item["actual"], item["path"]
for row in manifest_paths.values():
    assert sha(raw(row["path"])) == row["sha256"], row["path"]

readback = {"saved_at": NOW, "task": "TASK-124", "R": "R-118", "card_bytes": len(contract),
    "contract_matches_card": raw(card_path) == contract, "full_text_readback": card_path.read_text(encoding="utf-8") == contract.decode("utf-8"),
    "frozen_input_rows": len(manifest_paths), "manual_handoff_required": True, "received": False, "started": False}
save_json(AUDIT / "dispatch-readback.json", readback)
proof_paths = [decision_path, card_path, *paths.values(), AUDIT / "permit.json", AUDIT / "input-manifest.json", AUDIT / "dispatch-readback.json",
    HERE / "return-check.json", HERE / "candidate-receipt.json"]
proof = {"saved_at": NOW, "status": "TASK123_CANDIDATE_FROZEN_TASK124_READY_FOR_MANUAL_HANDOFF",
    "next_CHG": 1615, "original_bytes_preserved": True, "original_results_evidence_rules_unchanged": True,
    "orchestrator_product_runtime": 0, "Q": "FROZEN", "T0": None,
    "files": [{"path": p.as_posix(), "bytes": p.stat().st_size, "sha256": sha(raw(p))} for p in proof_paths]}
save_json(HERE / "save-proof.json", proof)
print(json.dumps({"status": proof["status"], "return_identities": 118, "audit_input_rows": len(manifest_paths),
    "task124_bytes": len(contract), "next_CHG": 1615, "runtime": 0, "Q": "FROZEN"}, ensure_ascii=False))
