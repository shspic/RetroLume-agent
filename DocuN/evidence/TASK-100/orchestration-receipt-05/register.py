"""Publish an existing-task audit continuation and maintain shared state serially."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def original(rel):
    return (OUT / "before" / rel).read_bytes()


def prefix(rel, text):
    p = ROOT / rel
    if p.read_bytes() != original(rel):
        raise SystemExit(f"Concurrent shared-state change: {rel}")
    p.write_bytes(text.encode("utf-8") + original(rel))


proof_path = OUT / "delivery-proof.json"
if proof_path.exists():
    raise SystemExit("Already published; do not repeat registration.")
for x in json.loads((OUT / "before-manifest.json").read_text(encoding="utf-8")):
    assert digest(ROOT / x["path"]) == x["sha256"], x["path"]
checks = json.loads((OUT / "current-pre-diff-rule-checks.json").read_text(encoding="utf-8"))
for x in checks:
    p = Path(x["path"])
    if not p.is_absolute():
        p = ROOT / p
    assert digest(p) == x["actual"], str(p)
receipt = json.loads((OUT / "receipt.json").read_text(encoding="utf-8"))
assert receipt["identity_mismatches"] == receipt["raw_index_mismatches"] == 0
assert receipt["old_result_suffix_preserved"]
assert digest(ROOT / "DocuN/results/TASK-100-result.md") == receipt["report_sha256"]
assert digest(ROOT / "DocuN/results/TASK-101-result.md") == "b5db0b2e6f787fd6a3fb78ee1e4c1f6ee54b98114731890fb889accd88bd71b4"
index = ROOT / "DocuN/evidence/TASK-101/review-02-input.json"
assert digest(index) == "3d268db805e4d2fe5b8630c7bf4cda7585c4aaeb1c5c572e0b478668aa1382e8"
user_original = ROOT / "DocuS/原始需求文档.MD"
user_original_sha = digest(user_original)
card = (OUT / "TASK-101-review-02-card.md").read_text(encoding="utf-8")
sections = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
            "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
assert all("## " + x in card for x in sections)
assert "*" not in card
assert all(x in card for x in ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "E01", "E02"))

prefix("DocuN/results/TASK-100-work-decision.md", f"""# TASK-100 / R-094 审计修复03回收裁定（2026-10-05，当前）

{STAMP}，Codex编排Agent。调度已返回，普通核证部分通过：接受稳定候选、可定位的有限运行及保留式资源收尾，DEF008—018仍为候选修正待101独立增量裁定，不签G8完整成果。

报告18819a4b8851ab4bb8ecf3eb98ab524ec980bffe680e0cb7d212601a7408c0e3可读且与交付冻结一致，原33904字节历史尾段hash及原文保留。核132当前文件、120pre、36diff-final、7规则、18保护对象合计313身份零漂移；2618原件身份匹配；B1/B3/B4后端180项as-run副本与当前逐一一致。原001—009/出站与停止权威未由本轮改动；初稿错误保护对象删除分类保留，当前按正确diff-final判断。

原日志逐项OK定位为B1 PG29、B3 PG3及HTTP3、最终离线58加18；三前批整体FAIL保留，B4只读专项PASS不冒充应用整链。B3十二SessionOutcome及实际发送可定位，B4七检查/原生IDB/Web Locks为最终包有限显示证据；只读快照不签新的认证/POST/业务事务。内容24对与F/E关闭由101独立核原文/断言，不用作者oracle或合计数代审计。首批n2题干与资料根变化的复用范围同样待独立核。

修复03新账entry4/4、start4/4、app3/3、SUP12/18、browser2/3、driver2/3、build2/2；离线78.735/1800、真实199.422/3600、清理26.906/480、主动10059.821/21600秒为本轮冻结口径。许可结束，余额不借；首读保守120秒/重叠收费/封装尾段及原初轮、续01/02失败/未知另列保留，不追认或清零。

2026-10-05T19:43:39+08编排只读核精确容器Exited(0)、Running=false/Pid=0，18100/55442无监听，无task100运行进程；数据库/卷/行保留，编排未连接PG、启停资源或执行产品测试/build/browser/Job。回收元数据解析首次漏两个被警告/预期失败关闭输出分隔的独立ok行，原解析器/索引保留后修正；不计成业务重跑或改原测试结果。

下一步同101/R095 review-02，A+原独立窗口一次增量复核，默认纯只读；不重跑原故障矩阵或已充分未变验证。完整中性索引及合同已保存核证，调度待转交，没有真实接收/开始证据。新增审计许可主动10800/元数据600秒，所有业务/资源/网络/构建/测试运行0；原101和100许可不复活。

## 以下为原裁定及全部历史

""")
prefix("DocuN/tasks/TASK-100.md", """# TASK-100 / R-094 审计修复03已返回冻结通知（2026-10-05，当前）

修复03真实回传已完成编排普通回收，接受候选及有限证据；F/E和G8放行待101独立增量复核。全部运行许可结束，禁止启动repair-combo、readonly-browser-combo/main-combo或借用SUP/browser名义余额。当前产品、009、夹具、dist和原证据冻结，无并行业务运行。

原结果/许可/失败/历史原文保留；本次完整执行合同原字节见DocuN/evidence/TASK-100/orchestration-receipt-05/TASK-100-card-as-returned.md。此通知不修改被审实现，不签G8或父STEP，后续有据修正必须取得编排新合同。

## 以下为已结束的原合同及全部历史

""")
prefix("DocuN/results/TASK-101-work-decision.md", f"""# TASK-101 / R-095 review-02登记（2026-10-05，当前）

{STAMP}，Codex编排Agent。首轮集中审计交付通过、G8不通过的原结论和报告保持；100修复03已真实返回，候选身份/原件稳定，原独立窗口增量复核前置满足。新增review-02登记待转交，尚无实际接收/开始/本轮审计结果。

复核全部F01—F09/E02/E01实际修复、新引入风险、内容/最终版本与四批控制，沿首轮未变原件及门槛继承；不从零重审整仓、不自修、不重跑PG/HTTP/Windows/browser。中性输入review-02-input.json hash 3d268db805e4d2fe5b8630c7bf4cda7585c4aaeb1c5c572e0b478668aa1382e8；132当前对象/120pre/36差异/2618原件及保护规则，先独立读源码，再核实际原件/片段，实施自评和编排裁定不当证据。

新的主动10800/元数据600秒，业务入口、连接、资源操作、browser/driver、build/compile/unittest、模型工具及联网/Git写入全部0。原3038.528秒身份核后计时、前读/shell未知、旧辅助解析错误及零业务运行保留；不借首轮未用probe或100余额。

本轮结果沿TASK-101-result.md置顶保留首轮原字节，审计者只给三个轴及综合建议，编排后据真实结果裁定DEF和G8。不提前签关闭，不预占102/R096，普通复核不冒充独立审计。原101许可已结束，本轮只恢复新明确只读范围。

## 以下为首轮裁定历史

""")
prefix("DocuS/架构动态文档.MD", """# 架构动态文档

文档 v0.84，2026-10-05，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.06。G8审计修复03候选已返回，101稳定点增量复核待转交。下面v0.83及全部历史原字节保留。

## G8审计修复候选及验证分层

当前增量为有限实际答案支持/数值域、每条事实来源资格、一致读面、严格HTTP、未claim意图同键恢复、32路径上限、有效G7seed、引用及cursor历史、答/版本编辑身份和两标签草稿owner。14既有产品模块与1引用组件候选已落地；source_refs和既有命令冻结/事实字段承载，001—009及原账本/停止/退款/旧G7后端权威未改，不新增模型或权限批准包。

三主题合成片段按实际节点/论点选取，12新Windows窗口、PG/HTTP与最终原生浏览器补证已有原件。最终B4只读快照证明UI/IDB/Web Locks，不证明新应用认证/POST；内容oracle、首批题干/资料根差异及旧中间版方法等价补证须由101独立核，合计OK和生成索引不是完成证明。三前批FAIL原样保留。

修复产品与最终bundle当前身份稳定，原保护对象/规则和原证据保持；完整G8、DEF008—018及原DEF005读面范围待101一次实际增量复核，不逐小修审计、不重跑未受影响旧链。其他已验切片和边界、STEP009—012未放行、V19真实provider/长期记忆/删除/M-1/部署与项目限制及Compose/Linux/Nginx/Git安排保持。

## 以下为v0.83及更早历史

""")
state_text = """# 执行动态文档

文档 v2.06，2026-10-05，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.84，task_model/阶段07。下面v2.05及全部历史原字节保留。

## TASK100修复03已返回；TASK101 review-02集中增量复核

100/R094审计修复03调度已返回，普通回收部分通过：候选及可定位有限证据接收，全部F/E为候选修正待独立确认，DEF008—018仍开放；DEF005剩余来源/投影同样待验。执行报告18819a4b…及原33904字节历史尾段真实保留，首輪101不通过结论不由实施自评改写。

编排核132当前文件/120pre/36正确diff/7规则/18保护对象共313身份零漂移，2618原件hash匹配，B1/B3/B4后端180项as-run与当前一致。原日志PG29加3补验、HTTP3、最终离线58加18 OK可定位，实际12SessionOutcome与七最终包浏览器检查可读。这是普通回收，不代独立审计的断言/内容/版本与执行控制判定。首批n2题干/独立data-backups变化的继承范围及24引用对等待独立核证。

原三新真实总批FAIL保留，B4只读专项PASS不冒称应用整链。B3实际HTTP与Windows事实、B4原生IDB/Web Locks及最终bundle证明分层，B4为只读快照回放、56GET/0POST/0SUP/0业务写，不签新增认证/写入证明。旧17故障窗/六迁移未重跑，原25中间版证据限制不整体升级。元数据索引保护对象误分类及解析修正原件保留，不改任何实际测试失败。

100修复03许可结束：entry4/4、container-start4/4、app3/3、SUP12/18、browser2/3、driver2/3、build2/2；离线78.735/1800、真实199.422/3600、清理26.906/480、主动10059.821/21600秒。初读保守120秒、重叠收费和封装尾段按原冻结口径；旧续02entry6/start5/app3/SUP21/browser3/driver3/build1及旧初轮/续01、漏5.940秒和未知全部独立保留，不清零、不借名义余额。

2026-10-05T19:43:39+08只读精确容器Exited(0)/Running=false/Pid=0、18100/55442无监听，无task100执行进程；原库/卷/数据保留，无编排业务连接或启停/测试/build/browser/Job。接收辅助解析首次漏两个独立ok行后有据修正，原parser/index保留；未重跑业务。原始需求/公共库/归档映射及保护对象未改。

101/R095首轮审计交付通过，现登记review-02，调度待保存核证，A+原101独立审计窗口；新窗口只在原窗口确不可续时采用，不能用100实现窗口或其记忆。新任务号不增加，102/R096仍仅未来计划。全部本次实际代码/证据/控制同卡一次复核，首轮未变充分结论继承，形成独立源码初判后核原件；不读取实施报告/聊天/推理作为证明。

101 review-02新许可主动10800/元数据600秒，新增使用0，业务/资源/PG/HTTP/Docker/应用/SUP/Job/browser/build/compile/unittest/模型工具/联网/Git写入0，没有显示probe。旧101计时3038.528秒为身份核后范围，前读/shell未知及辅助错误、业务0保留。当前没有实际转交/开始证据；100源码/夹具/dist已冻结，无并行执行。

原DEF001/002及097旧控制器禁用保持；DEF003/004/006/007原定位根因和DEF005已关闭子项沿v2.05，不恢复旧问题/许可。STEP009—012仍进行中/部分验证，不签G8、V19真实质量、M-1、部署或项目。待101真实review-02结果回收后一次裁定，其他已验成果/剩余Must及Compose/Linux/Nginx/Git安排保持。

本批CHG0866—0875，下一CHG0876；TASK/R/投入/失败不因本轮结果接收重置。用户只需转101完整增量卡并带回结果路径。

## 以下为v2.05及更早历史

"""
# Register the existing review continuation before publishing its complete card.
prefix("DocuS/执行动态文档.MD", state_text)
prefix("DocuN/tasks/TASK-101.md", card)

changes = [
    (866, "DocuN/results/TASK-100-result.md", "登记修复03真实返回，原结果及33904字节历史不改；候选和有限证据接收，未签DEF或G8"),
    (867, "DocuN/evidence/TASK-100/orchestration-receipt-05/", "保存313身份/2618原件/后端180项as-run复核、逐原日志与只读资源；原解析器错误及修正保留，未执行业务"),
    (868, "DocuN/evidence/TASK-101/review-02-input.json", "保存132当前对象/120pre/36差异及原件中性索引，原审计报告不可变副本，排除实施自评"),
    (869, "DocuN/results/TASK-100-work-decision.md", "置顶普通回收部分通过、候选状态、证据分层及新旧许可结束；历史保持"),
    (870, "DocuN/tasks/TASK-100.md", "置顶返回/冻结/运行许可结束通知；原完整合同备份，名义余额不恢复"),
    (871, "DocuN/results/TASK-101-work-decision.md", "登记原任务review-02只读增量安排与新预算，首轮结论和旧投入保留"),
    (872, "DocuS/架构动态文档.MD", "v0.84同步修正候选与证据分层，不改009/旧权威或预判验收"),
    (873, "DocuS/执行动态文档.MD", "v2.06登记100真实回收、冻结/预算与101同任务复核，核完整保存后待转交"),
    (874, "DocuN/tasks/TASK-101.md", "保存完整review-02合同，A+原独立窗口一次代码/内容/版本/控制增量复核，业务运行0"),
    (875, "DocuN/evidence/TASK-100/orchestration-receipt-05/delivery-proof.json", "保存全文回读、模板/路径/快照/历史一致性和只读前置核证，不声称派发或复核完成"),
]
log = ROOT / "DocuS/文档变更记录.MD"
assert log.read_bytes() == original("DocuS/文档变更记录.MD")
addition = "\n## TASK100修复03回收与TASK101集中增量复核\n\n" + "\n\n".join(
    f"- CHG-{n:04d}，{STAMP}，Codex编排Agent，{p}。{d}。" for n, p, d in changes) + "\n"
log.write_bytes(original("DocuS/文档变更记录.MD") + addition.encode("utf-8"))

for rel in (
    "DocuN/tasks/TASK-100.md", "DocuN/tasks/TASK-101.md", "DocuN/results/TASK-100-work-decision.md",
    "DocuN/results/TASK-101-work-decision.md", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD",
):
    assert (ROOT / rel).read_bytes().endswith(original(rel)), rel
assert (ROOT / "DocuN/tasks/TASK-101.md").read_bytes().startswith(card.encode("utf-8"))
state = ROOT / "DocuS/执行动态文档.MD"
ready = state_text.replace("调度待保存核证", "调度待转交，完整合同已保存回读核证")
state.write_bytes(ready.encode("utf-8") + original("DocuS/执行动态文档.MD"))
assert digest(ROOT / "DocuN/results/TASK-100-result.md") == receipt["report_sha256"]
assert digest(ROOT / "DocuN/results/TASK-101-result.md") == "b5db0b2e6f787fd6a3fb78ee1e4c1f6ee54b98114731890fb889accd88bd71b4"
assert digest(user_original) == user_original_sha
assert not any((ROOT / n).exists() for n in ("docu", "evidence", "Ndocu", "spikes"))
for obj in checks:
    p = Path(obj["path"])
    if not p.is_absolute():
        p = ROOT / p
    assert digest(p) == obj["actual"], str(p)
needed = (
    "AGENTS.md", "DocuN/results/TASK-099-result.md", "DocuN/results/TASK-100-result.md",
    "DocuN/results/TASK-101-result.md", "DocuN/evidence/TASK-101/review-02-input.json",
    "DocuN/evidence/TASK-100/orchestration-receipt-05/TASK-100-card-as-returned.md",
    "DocuN/evidence/TASK-100/orchestration-receipt-05/TASK-101-first-audit-as-returned.md",
)
assert all((ROOT / p).is_file() for p in needed)
proof = {
    "at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-101", "R": "R-095", "review": "review-02",
    "dispatch": "ready_for_manual_transfer", "TASK100_dispatch": "returned_frozen", "G8": "candidate_pending_independent_review",
    "full_card": str(ROOT / "DocuN/tasks/TASK-101.md"), "full_card_sha256": digest(ROOT / "DocuN/tasks/TASK-101.md"),
    "new_contract_bytes": len(card.encode("utf-8")), "template_sections": sections, "new_contract_asterisk": False,
    "neutral_input_sha256": digest(index), "history_suffixes_preserved": True,
    "identity_checks": len(checks), "identity_mismatches": 0,
    "raw_checks": receipt["raw_index_count"], "raw_mismatches": 0,
    "user_original_sha256": user_original_sha, "new_business_resources_or_runs": 0,
    "CHG_range": [866, 875], "next_CHG": 876, "verified_paths": needed,
    "updated_files": [{"path": str(ROOT / p), "sha256": digest(ROOT / p)} for _, p, _ in changes
                      if not p.endswith("/") and not p.endswith("delivery-proof.json")],
}
proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"dispatch": proof["dispatch"], "card": proof["full_card"], "card_bytes": proof["new_contract_bytes"],
                  "current_source_identity": 132, "raw_files": proof["raw_checks"], "CHG": "0866—0875"}, ensure_ascii=False))
