"""Publish a manual independent-audit contract and shared status; no runtime tools."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
AUDIT = ROOT / "DocuN/evidence/TASK-121/orchestration-20261021"
EXEC = ROOT / "DocuN/evidence/TASK-120/execution"
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="microseconds")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def put(path, data):
    path = path.resolve()
    assert path.is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".audit121.tmp")
    assert not temporary.exists(), temporary
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    assert path.read_bytes() == data


def put_json(path, value):
    put(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def prepend(text, old):
    return (text.strip() + "\n\n").replace("\n", "\r\n").encode("utf-8") + old


assert not (OUT / "save-proof.json").exists()
new_task = ROOT / "DocuN/tasks/TASK-121.md"
assert not new_task.exists() and not (ROOT / "DocuN/results/TASK-121-result.md").exists()
bounded = load(OUT / "bounded-review.json")
inputs, scope = load(AUDIT / "audit-inputs.json"), load(AUDIT / "scope-index.json")
assert bounded["current_identity_match"] == 209 and bounded["net_product_change_count"] == 55
protected = {}
for entry in inputs["current_frozen_files"] + inputs["formal_dist"] + inputs["raw_evidence_identity_entries"] + inputs["engineering_ledger"]:
    path = (ROOT / entry["path"]).resolve()
    assert path.is_relative_to(ROOT)
    expected = entry["sha256"]
    assert (sha(path.read_bytes()) if path.is_file() else None) == expected, entry["path"]
    if expected is not None:
        protected[path] = expected
for entry in scope["net_product_changes_relative_to_initial_manifest"]:
    path = (ROOT / entry["path"]).resolve()
    assert (sha(path.read_bytes()) if path.is_file() else None) == entry["final_sha256"], entry["path"]
    if entry["final_sha256"] is not None:
        protected[path] = entry["final_sha256"]
for entry in inputs["rules"]:
    assert sha(Path(entry["absolute_path"]).read_bytes()) == entry["sha256"]
opaque = inputs["opaque_engineering_report"]
assert sha((ROOT / opaque["path"]).read_bytes()) == opaque["sha256"]
protected[ROOT / opaque["path"]] = opaque["sha256"]
for name in ("AGENTS.md", "DocuS/原始需求文档.MD", "DocuS/最终需求文档.MD"):
    protected[ROOT / name] = sha((ROOT / name).read_bytes())

shared = ["DocuN/results/TASK-120-work-decision.md", "DocuS/架构动态文档.MD",
          "DocuS/执行动态文档.MD", "DocuN/tasks/TASK-120.md", "DocuS/文档变更记录.MD"]
before = {name: (ROOT / name).read_bytes() for name in shared}
assert "文档v2.81" in before[shared[2]].decode("utf-8-sig")[:240]
assert "文档v1.53" in before[shared[1]].decode("utf-8-sig")[:240]
assert max(map(int, re.findall(r"CHG-(\d{4})", before[shared[4]].decode("utf-8-sig")))) == 1556
ledger = load(EXEC / "budget.json")
assert ledger["active_root"] is None and ledger.get("active_command") is None
assert ledger["engineering_status"] == "CONTINUATION06_COMPLETE_STOPPED_READY_FOR_INDEPENDENT_AUDIT"

contract = (AUDIT / "contract.md").read_bytes()
text = contract.decode("utf-8-sig")
for word in ("TASK-121 / R-115", "55", "015", "DataContext", "代码、证据、执行控制", "新建一个隔离审计会话", "运行额度全部0"):
    assert word in text, word
assert "〈" not in text and "TODO" not in text
permit = {
    "id": "TASK-121-CONCENTRATED-READONLY-AUDIT-20261021", "issued_at": STAMP,
    "task": "TASK-121", "R": "R-115", "parent": "TASK-120/R-114", "STEP": "STEP018",
    "receiver": "A+ independent enhanced audit resource, responsibility continuous with118; new isolated audit conversation",
    "status": "REGISTERED_SAVED_READABLE_AWAITING_MANUAL_HANDOFF", "actual_receipt_or_start_not_yet_reported": True,
    "rules": "task_model V4.0 AGENTS CHG-0003 pinned seven files",
    "scope": "Complete actual TASK120 net delta, original contract and adopted increments, related raw evidence and execution control",
    "current_identity_file": "DocuN/evidence/TASK-121/orchestration-20261021/audit-inputs.json",
    "net_scope_file": "DocuN/evidence/TASK-121/orchestration-20261021/scope-index.json",
    "contract_sha256": sha(contract), "runtime_budget": 0, "product_writes_budget": 0,
    "maximum_elapsed_window_seconds_from_actual_receipt": 28800,
    "maximum_observed_tool_wall_seconds": 1800, "metadata_command_limit_seconds": 60,
    "allowed_tool_operations": ["bounded read-only file hashes/diffs/ZIP identity checks", "own stdlib-only metadata scripts", "write own audit evidence and result"],
    "optional_official_document_pages_maximum": 6,
    "prohibited_runtime": ["compile", "unittest", "product or fixture imports", "PG", "Docker", "API", "Windows Job", "browser", "build", "model", "business network", "Git writes"],
    "allowed_write_paths": ["DocuN/evidence/TASK-121/audit/", "DocuN/results/TASK-121-result.md"],
    "engineering_source_tests_dist_result_evidence_ledger_immutable": True,
    "do_not_decode_implementation_result_work_decision_chat_or_reasoning": True,
    "engineering120_kept_stopped_and_old_budgets_not_reset_or_borrowed": True,
    "original125_failure_records_and_TASK117_old81_retained": True,
    "real_Q_remains_frozen": True, "no_final_project_or_real_Q_activation_authorization": True,
}
put_json(AUDIT / "audit-permit.json", permit)
for name, data in before.items():
    put(OUT / "before" / name, data)
for name in ("budget.json", "events.jsonl"):
    put(OUT / "returned-snapshot" / name, (EXEC / name).read_bytes())
put_json(OUT / "metadata-command-events.json", {
    "purpose": "Orchestration filesystem metadata review only; no product or engineering runtime attempts",
    "attempts": [{"tool_chunk": "83dce4", "exit_code": 1, "wall_seconds": 2.2245629,
                  "cause": "Path-key separator mismatch in main's JSON lookup; no project input changed or product operation occurred"},
                 {"tool_chunk": "3d5aed", "exit_code": 0, "wall_seconds": 1.2186928,
                  "correction": "Normalize Windows path separators in the metadata key, then finish bounded review"}],
    "engineering_failure_count_not_modified": 125})

decision = f"""
# TASK-120 / R-114 主控续作06回收与集中独审裁定（当前有效）

{STAMP}。收到并读取工程06完整候选。主控有限核对7锁定规则、209当前身份、8项本轮产品diff、55项相对初始清单的产品净变化导航、四正式dist、286项候选包整体SHA256、旧报告原字节后缀、原始权限/scope/K2/UI/财务和070—071停止/退出记录。未运行产品/模型/PG/Docker/Browser或独审，不把工程声明直接签通过。

收存批准AP-120-06范围的完整工程候选，已到集中独审点；TASK120调度已返回，技术总验收仍待独立结果/主控裁定，不提前关闭。015/R03及单表DELETE、实际scope收缩与准确来源拒绝、完整DataContext和namespace两项真实迟到及只读列表补证均有候选实现/原件。最终额外sealed-reader纯读QAuthority构造顺序修补需作为重点审查，不以列表成功替代写/claim/外发拒绝检查。

原7类S未变部分沿118结论，TASK120的全部实际变化首次集中独审，不能只审最后8文件。签发TASK121/R115给A+独立增强审计资源，沿原118独审责任新建隔离会话，避开117/120实现聊天/思考；独立输入只含原批准合同/实际源diff/原始证据和身份，不解码120工程结果/本主控裁定。代码/证据/执行控制三轴独立，当前真实Q仍冻结；这是已授权的必需审查，不再向用户索取运行或费用许可。

完整卡DocuN/tasks/TASK-121.md已保存读回待人工转交，未虚记收到/开始。审计真实运行0，仅有限文件元数据/原件复核，8h日历/工具wall1800s/单命令60s，达到覆盖即停；不重跑充分ACK/五入口/C12、不借工程剩余资源。工程原A与更早A+保持停止，209身份及额外实际变化全冻结；修复等审计合并结果后再回唯一TASK120，原118/S结论不重开。

工程唯一账root51/64、PG52/64、API55/96、Browser14/16、build5/8、Native64/128、HTTP1459/10000，容器/卷实际与创建尝试各2/2，新源逻辑库1/1、原matrix1/1保留，失败125条/旧117的81另留，active_root/command空。071回执后wall50243.003003/57600，报告50299.862003仅该60s保存预留换实测3.141，不动旧未知；持有2667.078295/21600约44.4513分钟。新源5/1250000与恢复副本5/1250000分账，旧四库不变，真实provider/实际费用/preview/Git0。

070在2026-10-20T23:08:53.727173+08核622 PID/birth/135 Job、原源与实际目标两CID stopped/Pid0、55480/55481/18120无监听；071仅文件保存exit0/tree_empty。主控仅核原停止时点，不执行现时资源探针。原FAIL/UNKNOWN/控制偏差、memory缺即时before-financial快照、R01仅ZIP读取未新做库恢复、root46与最终仅sealed-reader差异由50/51补证的适用性等全部留给独审分层判断，不伪补旧件。

候选收存不等于实现/证据/控制已独立通过，也不启真实Q或签STEP018整体/019/020/M1/项目/发布。主控未改工程结果/唯一预算/事件/产品，只保存只读核证、审计输入与共享状态。

---

# 以下旧裁定原字节保留
"""
architecture = f"""
# 架构动态文档

文档v1.54，2026-10-21，Asia/Shanghai。需求v1.4、执行动态v2.82、task_model/07；以下v1.53原字节保留。

## AP-120-06完整候选落地并交集中独审，Q仍冻结

{STAMP}。续作06新增015_activity_scope_delete_permission.sql（SHA256 59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e），仅scope绑定表DELETE、精确R03 metadata/ACL/profile/迁移链与旧R01-R02识别；q_protocol允许精确R03，snapshot包含原R02检索图。001—014与业务列/金融/公开wire/编码保持。此为实际候选/工程证据状态，独立审查尚待。

同轮8文件增量还含面试bind_scope来源current_version/revision准确source_invalid校验、dataFetch普通响应完整DataContext守卫，以及服务器data_readonly/既有纯读分类下不构造normal QAuthority的只读列表修补。实际scope缩减/K2、生产normal响应先取回再冻结/正常恢复选择的两类迟到UI、R03生产备份恢复/只读列表有原件。root46后只读分支变化用50/51补直接影响；最终JS index-GSKO5ska.js及四资产已冻结，不把磁盘四项等同全部实载。

原源新增scope_ui_final、真实工厂恢复目标scopeui-ro1均已封存，源frozen、目标restored_readonly不恢复Q执行资格。原S与旧充分正常链/权限/ACK/C12证据按适用对象继承。55项TASK120产品净变化与209当前身份交TASK121/R115首次完整集中独审，重点严格ACL投影/旧兼容、完整请求批准/账本、上下文与sealed-reader例外；未获独立结论前不关闭TASK120/真实Q或STEP018整体。

## 以下为v1.53及更早历史
"""
state_template = f"""
# 执行动态文档

文档v2.82，2026-10-21，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.54、task_model/07。以下v2.81原字节保留。

## TASK120续作06完整候选已收存；TASK121/R115集中独审{{dispatch_status}}

{STAMP}。工程06已返回并封存；主控只做有界源diff/原件与身份核证：7规则、209当前文件、8个最新产品文件、55项初始以来净变化导航、4正式dist、候选ZIP整体hash/286条目、旧报告后缀、两项迟到原件及070/071回执。不执行功能测试或独审，不凭报告存在签通过。TASK120调度已返回、完整技术验收待集中独审与主控最后裁定，原部分通过和所有历史限制保留。

新TASK121/R115已登记，父120/R114、STEP018，A+增强独立资源沿原118独审责任新建隔离审计会话；{{card_status}}。审TASK120完整实际差异/证据/控制，不只最后8文件，不重审未变S。审计运行0，文件核对工具wall1800s/日历8h/单命令60s，代码/证据/控制三轴分开，不读工程结果/思考。卡DocuN/tasks/TASK-121.md，冻结输入/范围/许可在DocuN/evidence/TASK-121/orchestration-20261021/；工程原A及旧A+保持停止，源码/fixture/dist/工程账冻结，余量不自动重启。

候选包含015单表DELETE/R03严格版本兼容、真实scope收缩与K2、完整DataContext同namespace变只读和生产恢复切namespace两迟到、sealed-reader列表修正及50/51补证。新源5/1250000与恢复副本5/1250000独立，旧四库原账不变；真实Q资格仍关闭，原UNKNOWN/预扣不清不退，memory即时before快照缺口和旧R01仅ZIP读取等限制作原事实交审。

实际累计root51/64、PGstart52/64、API55/96、Browser14/16、build5/8、Native64/128、HTTP1459/10000，PG/卷对象与create尝试均2/2，源新逻辑库1/1、旧matrix1/1保持，125失败记录/旧117的81另留。唯一账071退出后wall50243.003003/57600，持有2667.078295/21600约44.4513分钟，所有旧unknown预留保持；报告50299.862003仅末071预留60换实测3.141。active_root/command空。新审计不重置/借用工程预算或延旧grant/96h。

070于2026-10-20T23:08:53.727173+08核622组PID/birth、135Job、两精确CID Running=false/Pid0、55480/55481/18120无监听，071仅有限文件保存exit0/tree_empty；主控核的是原时点，不称本轮实时Docker核查。工程报告/预算/events/旧包和原S/旧控制不通过均保持。Q/provider/实际费用/preview/Git冻结或0；不签STEP018整体/019/020/M1/项目。CHG1557—1562，下一1563；等待用户转交和审计真实结果，不提前派工程修复。

## 以下为v2.81及更早历史
"""
freeze_notice = f"""
# TASK-120 / R-114 — 当前工程冻结通知：续作06已返回，等待TASK121集中独审

{STAMP}。完整候选/原始证据已回收并有界核证。原A工程窗口与更早A+保持停止，产品/测试/dist/原证据/唯一预算和事件在审计期间只读冻结；剩余次数或尚未届满的原时窗不构成新增业务/修补许可。本通知优先于下方历史“当前有效”工程卡。

新TASK121/R115承接完整TASK120的独立终审（代码、证据、执行控制分别裁定），不重跑已过基线，不自签验收。审计完整卡D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-121.md；它交独立A+隔离会话，不交本工程窗。发现需要修复时由主控合并交回本TASK120同窗，不另起竞争修复者。

原source/restore目标均按070原时点已停，最后071仅保存；原报告、所有失败/UNKNOWN、累计预算和批准边界原样保留。Q仍冻结，未签任何项目或真实启用通过。以下06与更早合同仅作历史，未被本通知删除或改写。

---

# 以下为续作06及更早合同原字节
"""
for name, data in before.items():
    assert (ROOT / name).read_bytes() == data
for path, value in protected.items():
    assert sha(path.read_bytes()) == value

# Register this new audit before saving its canonical contract; then mark ready only after readback.
registration = prepend(state_template.format(dispatch_status="已登记，合同保存核对中", card_status="完整合同正在保存，未派发/未开始"), before[shared[2]])
put(ROOT / shared[2], registration)
put(OUT / "registration-state.bytes", registration)
put(new_task, contract)
assert new_task.read_bytes() == contract
put(ROOT / shared[0], prepend(decision, before[shared[0]]))
put(ROOT / shared[1], prepend(architecture, before[shared[1]]))
put(ROOT / shared[3], prepend(freeze_notice, before[shared[3]]))
put(ROOT / shared[2], prepend(state_template.format(dispatch_status="完整卡已保存待转交", card_status="完整卡已真实保存并读回，可人工转交；未冒称实际接收或开始"), before[shared[2]]))
changes = [
    (1557, shared[0], "收存06完整工程候选并交集中独审；核身份/原件/停止与预算，不自签独立或最终验收。"),
    (1558, shared[1], "v1.54登记015/R03、scope收缩、完整DataContext与sealed-reader候选实现/证据，独审待决。"),
    (1559, shared[2], "v2.82登记120已返回/冻结和新121集中独审已登记、保存读回后待转交，工程旧账不变。"),
    (1560, shared[3], "置顶工程冻结通知，旧06及更早合同原字节保留，余量不自动续跑。"),
    (1561, "DocuN/tasks/TASK-121.md", "保存Q v2完整候选集中只读独审合同，A+隔离会话、三轴/全实际差异/零运行。"),
    (1562, "DocuN/evidence/TASK-120/orchestration-review06-20261021及TASK-121/orchestration-20261021", "保存有界核证、209身份/55净变化/原始证据导航、审计许可、旧共享和返回账快照及读回复核；主控无产品执行。"),
]
change_bytes = ("\r\n\r\n" + "\r\n\r\n".join(
    f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{name}。{note}"
    for number, name, note in changes) + "\r\n").encode("utf-8")
put(ROOT / shared[4], before[shared[4]] + change_bytes)
for name in shared[:4]:
    assert (ROOT / name).read_bytes().endswith(before[name]), name
assert (ROOT / shared[4]).read_bytes().startswith(before[shared[4]])
for path, value in protected.items():
    assert sha(path.read_bytes()) == value, f"Protected engineering input drift: {path}"
assert new_task.read_bytes() == contract
put_json(OUT / "save-proof.json", {
    "timestamp": STAMP, "status": "AUDIT121_SAVED_READABLE_AWAITING_MANUAL_HANDOFF",
    "TASK120": "returned complete engineering candidate; frozen; independent and final acceptance pending",
    "TASK121": {"R": "R-115", "registered": True, "contract_read_back": True, "actual_receipt_or_start_claimed": False,
        "path": "DocuN/tasks/TASK-121.md", "sha256": sha(contract), "bytes": len(contract), "runtime_budget": 0},
    "rules_match": 7, "current_identity_match": 209, "net_product_changes": 55,
    "engineering_product_result_budget_events_and_raw_evidence_unchanged": True,
    "shared_history_original_bytes_preserved": True, "functional_or_independent_tests_by_main": False,
    "writes": [{"path": name, "sha256": sha((ROOT / name).read_bytes()), "bytes": (ROOT / name).stat().st_size} for name in shared],
    "CHG": [1557, 1558, 1559, 1560, 1561, 1562], "next_CHG": 1563})
put_json(AUDIT / "dispatch-readback.json", {
    "timestamp": STAMP, "status": "SAVED_READABLE_NOT_DISPATCHED", "task": "TASK-121", "R": "R-115",
    "contract_sha256": sha(contract), "contract_bytes": len(contract),
    "audit_inputs_sha256": sha((AUDIT / "audit-inputs.json").read_bytes()),
    "scope_index_sha256": sha((AUDIT / "scope-index.json").read_bytes()),
    "audit_permit_sha256": sha((AUDIT / "audit-permit.json").read_bytes()),
    "main_did_not_perform_independent_audit": True})
print(json.dumps({"status": "AUDIT121_SAVED_READABLE_AWAITING_MANUAL_HANDOFF", "task": "TASK-121", "R": "R-115",
    "contract_bytes": len(contract), "frozen_current_files": 209, "net_product_changes": 55,
    "versions": ["2.82", "1.54"], "next_CHG": 1563, "runtime_budget": 0}, ensure_ascii=False))
