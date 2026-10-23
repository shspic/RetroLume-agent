"""主控采纳独审、澄清原合同并保存同号文档修正许可。"""

from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
HERE = Path(__file__).resolve().parent
REPAIR = ROOT / "DocuN/evidence/TASK-123/orchestration-correction01-20261022"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def raw(path):
    return Path(path).read_bytes()


def sha(data):
    return sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


checked = load(HERE / "return-check.json")
assert checked["passed"] and checked["identity_count"] == 141
for row in checked["rows"]:
    assert sha(raw(row["path"])) == row["actual"], row["path"]

paths = {"state": ROOT / "DocuS/执行动态文档.MD", "architecture": ROOT / "DocuS/架构动态文档.MD",
    "changes": ROOT / "DocuS/文档变更记录.MD", "task123": ROOT / "DocuN/tasks/TASK-123.md",
    "task124": ROOT / "DocuN/tasks/TASK-124.md", "decision123": ROOT / "DocuN/results/TASK-123-work-decision.md"}
old = {key: raw(value) for key, value in paths.items()}
assert "文档v2.90" in old["state"].decode("utf-8-sig").splitlines()[2]
assert "文档v1.62" in old["architecture"].decode("utf-8-sig").splitlines()[2]
assert "CHG-1614" in old["changes"].decode("utf-8-sig")[-2500:]
assert "CHG-1615" not in old["changes"].decode("utf-8-sig")
decision124 = ROOT / "DocuN/results/TASK-124-work-decision.md"
assert not decision124.exists()
before = HERE / "before"
before.mkdir(exist_ok=False)
for key, data in old.items():
    (before / (key + ".bytes")).write_bytes(data)

root_cause = f"""# F124-01根因与唯一修正范围

{NOW}。本文件是主控原合同解释和执行边界，不是产品验证或独立审计替代。

## 接受的独立事实

TASK124报告19419字节，SHA256 60c7394a8315739e6468e6fc4ebd586300155edb7179555152c3efbea0e05661。主控核141引用身份均匹配，采纳readiness有限代码通过、13方法证据成立、执行控制在可核范围通过/实测unknown保留；整包因F124-01 P1不通过。OBS124-01是配置误填的条件风险，不自动升级新产品门。F124-01当前仍开放，不能在修正文档尚未返回时写关闭。

原交接把中性理由文本映射到correct/空disputed_dimensions。当前correct会保存correction，teaching_progress.rebuild_progress把其父反馈入争议集合，随后排除对应独立作答；空数组不能避免。原correct真实纠错语义应保持。主控此前TASK124卡面也沿用了correct本地保存的未充分核实假设，本轮纠正该判断，不将问题归咎资源标签或要求用户再次批准相同预算。

## 原批准要求和已有承载

DocuS/最终需求文档.MD的FR010正常要求是依据复测更新路径、理由与进度；其验收要求保存可观察依据、重开保持和重复提交不重复计分。DR002要求理由等本地持久可读。原文没有独立任意手写中性备注接口的Must。

TASK116 integration-contract.md的M06及学习主链明确evaluate同事务保存progress与保留/推进理由；acceptance-contract的L01/L05要求完整到理由及实际证据，不是把一段固定参考文字再发correct。

当前activities/teaching_repository.py第19—24行_progress_reason产生有限理由；第1311—1336行当前正常evaluate结果保存progress_body.reason、feedback/answer、observations、advance、前后节点及support_checks，写kind=progress/body_sha256和head.reason_record_id/state_after。第1501—1544行提供既有workspace/record读取。前端TeachingWorkspace.tsx第805—807行用reasonBody.reason显示更新或保留理由。这些是B级原源码/接口事实，不证明本轮真实Q语义或重开实测已过。

无需为本修正新增中性备注承载，也不允许将select_node等其他动作当无副作用保存。两份错误交付须撤掉该映射，改为原evaluate COMMIT→准确progress记录→GET/已有页面→未来获准重开核同记录的验收说明。原159字节参考文案若保留只作被撤销非执行说明，不能说它已由产品保存；任意用户备注能力仍未实现，也不是此次原Must新增项。

## 防止再次循环的终点

同TASK123/R117修正轮01，原工程窗口，只更正两份交付和统一结果。原48产物及旧报告原字节保留，新有效版本写execution/correction-01，原六文件和13方法完全冻结。一次文件/JSON/文档一致性检查，产品/PG/浏览器/网络/下载/费用0，原剩余工具/日历不重置。

修后主控按原独审事实和本准确合同作限定文档核证，不预设再派完整独审或重跑13方法。原必需独立readiness代码审查已完成，移除错误操作指引不构成新的高风险产品实现；若出现产品改动或真实新风险，停止该越界部分再定门，不把主控普通文档核证称新独审。

Q的供应商输入分词/模板、Embedding容量和本人账号适用性仍缺，不因本修正消失，也不再发同样搜索/设计卡机械尝试。STEP018真实语义/恢复和最终交付Must仍须真实证据，不用合同澄清省略验收。
"""
(REPAIR / "root-cause-and-scope.md").write_text(root_cause, encoding="utf-8")
save_json(REPAIR / "source-facts.json", {"at": NOW, "sources": checked["source_facts"],
    "finding": "F124-01", "code_change_required_by_this_correction": False,
    "manual_free_text_note_implemented": False, "existing_progress_reason_source_grade": "B",
    "Musts_removed": 0, "root_research_restart": False})

decision124.write_text(f"""# TASK124主控回收裁定

{NOW}。独立审计交付通过并结束本轮；采纳其有限readiness代码通过、最终13方法证据通过、执行控制在可核范围通过/unknown保留。TASK123完整交付因F124-01 P1不通过，当前不能签整包关闭；该P1未因本计划自动关闭。

报告19419字节/hash60c7394a…e05661及原79输入、8封存输出、六文件和48工程产物共141引用由主控核对无漂移。原独审事实/失败/预算不改，audit保守1400.706969/1800及实测unknown保留。原18xx审计许可不自动续审。

本次不是要求修readiness产品，也不需要重跑13项。主控重新对照FR010/DR002、116的M06/主链和实际仓储/页面后确认：原Must的理由由evaluate同事务写progress.reason已有承载；错误是新增参考文字被误用correct。任意手写中性备注确无现成接口，但它不是原批准Must，不能由错误交接反推新增功能。

沿原TASK123/R117只更正两份文档，保旧原件并给新有效版本。原六产品/说明和原代码审计结论冻结继承。完成后主控对照F124-01原独审证据作有限文档核证，不把普通核证冒充独审，不预设新的全面独审/产品测试；确有越界产品变化则另定相应风险门。准确根因/合同在DocuN/evidence/TASK-123/orchestration-correction01-20261022/root-cause-and-scope.md。

OBS124-01保持非阻塞，正常模型别名栏只能放可公开身份，不保证任意误填秘密内容可被字符正则识别。本轮不扩成产品修补。计量输入/模板/Embedding容量/本人账号的外部门保持未满足，Q冻结、T0/72h空，STEP018/019/020、M1/项目/发布未通过。
""", encoding="utf-8")

decision123 = f"""# TASK123 F124-01已接受，唯一修正为错误操作指引撤回

{NOW}。原TASK124独审已完成，readiness代码/13方法原证据/可核执行控制结论采纳；完整有限交付因F124-01 P1不通过，状态仍待修正。主控核141身份无漂移，没有运行产品或测试。

根因为中性理由被误映射correct，后者必保留争议副作用；主控此前复核卡沿用该假设有误，已裁定撤销。原FR010和116 M06要求保存真实进度依据，已有evaluate→progress.reason→原读取/页面的承载，不新增任意中性备注接口、不改纠错/进度逻辑、不删Must。准确原句/源码范围见本轮root-cause-and-scope.md。

同号修正轮01完整卡已保存读回，待人工转交原TASK123窗口；常规文档资源可用，不另开工程/审计线。仅新写execution/correction-01两份有效文档及pre/diff/身份，统一报告置顶保旧原字节；原48证据和六文件不动。工具最多新增600秒含120保存，原3554.557411/7200和剩余3645.442589、原三测试批3/3、原截止2026-10-23 00:19:11.451055+08不重置，产品/所有真实运行/联网/费用0。

完成后主控依据已有独审与具体撤映射差异作有限文档收口，不为文档移除再预设一次完整审计或重复13方法。独立代码结论不由主控自查替代，也不把现在的计划写成P1已关闭。Q及外部计量/账号门、原89请求/28Must/24片6批与100/25/分额全部保持。以下原主控候选裁定原字节保留。

""".encode("utf-8")
paths["decision123"].write_bytes(decision123 + old["decision123"])

state = f"""# 执行动态文档

文档v2.91，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.63、task_model/07。以下v2.90原字节保留。

## TASK124独审已回收：readiness代码通过，F124-01仅指向错误交接映射；原123文档修正01待转交

{NOW}。TASK124/R118审计交付完成并由主控接受，报告19419字节/hash60c7394a…e05661及141引用核对无漂移。采纳有限readiness代码通过、13方法原证据成立、执行控制可核范围通过/全量实测unknown保留；TASK123完整交付因F124-01 P1不通过，尚未关闭。原六文件、13方法和HTML/有限计量已通过范围保留，不重跑代码审计。

F124-01是finite-inputs/deployment-handoff用correct保存中性理由；空disputed_dimensions仍产生correction并剔除父反馈的独立作答依据。主控此前复核卡沿用了该错误承载假设，本轮纠正。对照FR010/DR002、116 M06/主链与现源码，原Must已有evaluate同事务保存progress.reason/head理由及原读取/页面；没有另存任意用户中性备注的原批准Must。准确源码承载是B级事实，不冒真实Q语义或恢复已过，也不修改原Must。

唯一修正沿同TASK123/R117、原窗口，只更正两份交付和统一结果，在execution/correction-01写新有效版本，原48产物/报告失败与六文件冻结。禁止换其它动作承载、加接口/迁移、改纠错或进度逻辑。完整卡/原事实/permit已保存读回，待人工转交，未宣称已接收/开始。常规A−文档资源足够，原窗固定A+可沿用，不为标签换窗。

本轮新增工具至多600秒含120保存，原保守3554.557411/7200、剩余3645.442589、三测试批3/3及原截止2026-10-23 00:19:11.451055+08不重置；回传等待不是工具wall。产品导入/测试/PG/HTTP/browser/网络/模型/费用/Git0。修后由主控对照原独审与准确合同限定核文档；原必需独立代码门已完成，不预设重跑13方法或完整独审。若实际越界产品变化则停止并重定相关门，不把主控核证称新独审。F124-01在真实修正返回前保持开放。

原124审计保守1400.706969/1800、unknown和已通过分轴留档，原任务本轮结束，不自动恢复审计许可。OBS124-01只作模型身份栏误填风险说明，不升级新产品门。Q输入分词/模板、Embedding容量和本人账号外部材料继续缺失，不为此重复同样核查/设计卡；Q冻结、T0/72h空、provider/费用0。原120有限关闭/121五项关闭及149/117旧81失败和全部旧账保持；STEP018仍进行中/部分验证，019/020/M1/项目/发布未通过。CHG1615—1621，下一1622。

## 以下为v2.90及更早历史

""".encode("utf-8")
architecture = f"""# 架构动态文档

文档v1.63，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.91、task_model/07。以下v1.62原字节保留。

## readiness有限代码独审通过；继续理由交接退回原progress持久事实

{NOW}。TASK124独立确认新增启动snapshot/capabilities诊断无本范围确定授权/秘密属性直出/启动回归，13方法证据和可核控制成立，原qualification仍unknown。模型身份字段不得填秘密是配置内容条件风险，不假称正则能识别所有敏感信息；无需扩建诊断平台。

唯一P1为交付把中性参考文本映射correct，现correct会将对应反馈视为争议，必须撤销该用途而非削弱保护。原FR010及116 M06要求的实际进度理由已有evaluate分支在原短事务写progress.reason/observations/advance/节点前后、原head.reason_record_id及读取/页面承载；这是既有B级代码事实，完整真实语义/恢复仍待未来验收。任意用户中性备注不是本轮新增能力，不加字段/动作/表、不用select_node等副作用接口替代。

TASK123只作两文档更正，新版本独立保存，旧错误原件和全部代码冻结；当前P1尚未关闭。原readiness独审结论直接继承，文档修正完成由主控按已有独立证据作有限Review，若出现新的实际代码风险再定相关审计，不机械重审。Q和输入token/模板/Embedding容量/账号门保持未核，预算、分额与原Must不变。

## 以下为v1.62及更早历史

""".encode("utf-8")
paths["state"].write_bytes(state + old["state"])
paths["architecture"].write_bytes(architecture + old["architecture"])

contract = raw(REPAIR / "contract.md")
assert "TASK-123 / R-117 修正轮01" in contract.decode("utf-8")
assert "*" not in contract.decode("utf-8")
paths["task123"].write_bytes(contract + b"\n\n" + old["task123"])
task124_notice = f"""# TASK124本轮已回收结束，原代码及离线证据结论保留

{NOW}。主控接受审计交付和分轴结论，F124-01仍开放。原TASK123仅修正两份交接文档，原六代码/说明与13方法冻结；主控按原独立证据核更正，不自动续审或重跑。主控裁定见DocuN/results/TASK-124-work-decision.md。以下完整原审计合同原字节保留。

""".encode("utf-8")
paths["task124"].write_bytes(task124_notice + old["task124"])

manifest = []


def add(path, kind):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    assert p.is_file(), p
    manifest.append({"path": p.as_posix(), "bytes": p.stat().st_size, "sha256": sha(raw(p)), "kind": kind})


for item in load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json"):
    p = Path(item["absolute_path"].replace("\\\\", "/").replace("\\", "/"))
    assert sha(raw(p)) == item["sha256"]
    add(p, "locked_rule")
for rel in ["AGENTS.md", "DocuS/最终需求文档.MD", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD",
    "DocuN/results/TASK-123-work-decision.md", "DocuN/results/TASK-124-work-decision.md", "DocuN/results/TASK-124-result.md",
    "DocuN/evidence/TASK-124/audit/findings.json", "DocuN/evidence/TASK-123/execution/finite-inputs.json",
    "DocuN/evidence/TASK-123/execution/deployment-handoff.md", "DocuN/evidence/TASK-123/execution/post-snapshot.json",
    "DocuN/evidence/TASK-123/execution/delivery-manifest.json", "DocuN/results/TASK-123-result.md",
    "DocuN/evidence/TASK-123/execution/budget.json", "DocuN/evidence/TASK-123/orchestration-20261022/permit.json",
    "DocuN/evidence/TASK-116/design/acceptance-contract.md", "DocuN/evidence/TASK-116/design/integration-contract.md",
    "backend/app/activities/teaching_repository.py", "backend/app/learning/teaching_progress.py",
    "frontend/src/activities/TeachingWorkspace.tsx",
    "DocuN/evidence/TASK-123/orchestration-correction01-20261022/root-cause-and-scope.md",
    "DocuN/evidence/TASK-123/orchestration-correction01-20261022/source-facts.json"]:
    add(rel, "repair_input")
for row in load(ROOT / "DocuN/evidence/TASK-123/execution/post-snapshot.json")["products"]:
    p = ROOT / row["path"]
    assert sha(raw(p)) == row["post_sha256"]
    if not any(item["path"] == p.as_posix() for item in manifest):
        add(p, "frozen_passed_scope")
save_json(REPAIR / "input-manifest.json", {"task": "TASK-123", "R": "R-117", "round": "correction-01",
    "frozen_at": NOW, "rows": manifest, "product_changes_allowed": False})

original_permit = load(ROOT / "DocuN/evidence/TASK-123/orchestration-20261022/permit.json")
permit = {"permit_id": "TASK-123-F12401-DOCUMENT-CORRECTION-01-20261022", "task": "TASK-123", "R": "R-117",
    "round": "correction-01", "issued_at": NOW, "calendar_deadline": original_permit["calendar_deadline"],
    "contract_sha256": sha(contract), "input_manifest_sha256": sha(raw(REPAIR / "input-manifest.json")),
    "status": "SAVED_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED", "same_original_engineering_window_preferred": True,
    "resource": "A- regular documentation repair; existing A+ fixed window may continue without replacement",
    "original_tool_wall_cap_seconds": 7200, "prior_conservative_charge_seconds": 3554.557411,
    "remaining_before_correction_seconds": 3645.442589,
    "incremental_tool_wall_cap_seconds": 600, "closing_reserve_within_increment_seconds": 120,
    "single_command_seconds": 60, "product_test_batches_used": "3/3 frozen",
    "idle_manual_handoff_or_audit_wait_is_not_new_tool_wall": True,
    "allowed_writes": ["DocuN/evidence/TASK-123/execution/correction-01/", "DocuN/results/TASK-123-result.md prepend preserving old bytes"],
    "old_artifacts_and_passed_product_test_files_write_permission": False,
    "runtime_caps": {name: 0 for name in ["product_import", "compile", "unittest", "TestClient", "build", "PG", "SQL", "API",
        "Docker", "browser", "Job", "network", "download", "install", "provider_calls", "cost", "Git", "subagents"]},
    "one_document_consistency_check_allowed": True, "F124-01": "OPEN_UNTIL_ACTUAL_CORRECTION_VERIFIED",
    "needs_repeat_full_independent_audit_for_document_only_removal": False,
    "independent_code_audit_already_performed_and_unchanged": "TASK-124 A/B/C pass in original scope",
    "new_product_change_requires_stop_and_scope_reassessment": True, "Q": "FROZEN", "T0": None}
save_json(REPAIR / "permit.json", permit)

changes = [
    (1615, "DocuN/results/TASK-124-work-decision.md", "接受独审交付及代码/13证据/控制限定结论，整包F124-01开放；区分原progress理由与任意手写备注。"),
    (1616, "DocuN/results/TASK-123-work-decision.md", "置顶唯一文档修正路线，纠正主控旧承载假设，原候选裁定原字节保留。"),
    (1617, "DocuS/架构动态文档.MD", "v1.63登记readiness独审通过、错误correct用途与既有progress承载，未新增产品接口/表。"),
    (1618, "DocuS/执行动态文档.MD", "v2.91登记124已返回、123同号修正01待转交、原剩余账与限定文档核证终点。"),
    (1619, "DocuN/tasks/TASK-123.md", "置顶完整修正01合同，只准新目录更正两文档/报告保历史，旧所有完整卡原字节保留。"),
    (1620, "DocuN/tasks/TASK-124.md", "置顶本轮独审回收结束通知，原独立结论保留，不自动续审。"),
    (1621, "DocuN/evidence/TASK-124/orchestration-return-20261022及TASK-123/orchestration-correction01-20261022", "保存141身份、根因原文/源码定位、旧共享、同号合同/输入/继承许可和读回，主控业务运行0。"),
]
addition = "\r\n\r\n" + "\r\n\r\n".join(f"- CHG-{num}，{NOW}，Codex编排Agent，{path}。{why}" for num, path, why in changes) + "\r\n"
paths["changes"].write_bytes(old["changes"] + addition.encode("utf-8"))

for key in ("state", "architecture", "task123", "task124", "decision123"):
    assert raw(paths[key]).endswith(old[key]), key
assert raw(paths["changes"]).startswith(old["changes"])
assert raw(paths["task123"]).startswith(contract)
for rel, expected in checked["protected_before_publication"].items():
    assert sha(raw(ROOT / rel)) == expected, rel
for item in checked["rows"]:
    if Path(item["path"]) in set(paths.values()):
        continue
    assert sha(raw(item["path"])) == item["actual"], item["path"]
for item in manifest:
    assert sha(raw(item["path"])) == item["sha256"], item["path"]

save_json(REPAIR / "dispatch-readback.json", {"saved_at": NOW, "contract_bytes": len(contract), "task_card_prefix_matches_contract": raw(paths["task123"]).startswith(contract),
    "full_contract_readback": (REPAIR / "contract.md").read_text(encoding="utf-8") == contract.decode("utf-8"),
    "frozen_input_count": len(manifest), "received": False, "started": False, "manual_handoff_required": True})
proof_paths = [*paths.values(), decision124, REPAIR / "contract.md", REPAIR / "input-manifest.json", REPAIR / "permit.json",
    REPAIR / "root-cause-and-scope.md", REPAIR / "source-facts.json", REPAIR / "dispatch-readback.json", HERE / "return-check.json"]
save_json(HERE / "save-proof.json", {"saved_at": NOW, "state": "TASK124_RETURN_ACCEPTED_TASK123_DOCUMENT_REPAIR_READY_FOR_MANUAL_HANDOFF",
    "F124-01": "OPEN_PENDING_CORRECTION", "next_CHG": 1622, "runtime": 0, "Q": "FROZEN",
    "previous_shared_bytes_and_original_engineering_audit_evidence_preserved": True,
    "files": [{"path": p.as_posix(), "bytes": p.stat().st_size, "sha256": sha(raw(p))} for p in proof_paths]})
print(json.dumps({"state": "TASK123_DOCUMENT_CORRECTION01_READY_FOR_MANUAL_HANDOFF", "input_identity_rows": 141,
    "repair_input_rows": len(manifest), "contract_bytes": len(contract), "next_CHG": 1622,
    "F124-01": "OPEN_PENDING_ACTUAL_CORRECTION", "runtime": 0}, ensure_ascii=False))
