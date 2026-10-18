"""Serial orchestration registration. No product imports, tests or services."""
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
    dst = ROOT / rel
    if dst.read_bytes() != original(rel):
        raise SystemExit(f"Unexpected shared-state drift: {rel}")
    dst.write_bytes(text.encode("utf-8") + original(rel))


proof = OUT / "delivery-proof.json"
if proof.exists():
    raise SystemExit("Already registered; do not repeat this mutation.")
for b in json.loads((OUT / "before-manifest.json").read_text(encoding="utf-8")):
    if digest(ROOT / b["path"]) != b["sha256"]:
        raise SystemExit(f"Shared-state drift before registration: {b['path']}")
baseline = json.loads((OUT / "baseline-checks.json").read_text(encoding="utf-8"))
for item in baseline:
    if digest(Path(item["path"])) != item["actual"]:
        raise SystemExit(f"Input drift before registration: {item['path']}")
user_original = ROOT / "DocuS/原始需求文档.MD"
user_original_sha = digest(user_original)
card = (OUT / "TASK-100-audit-repair-03.md").read_text(encoding="utf-8")
headings = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
            "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
assert all("## " + h in card for h in headings)
assert "*" not in card
assert all(f"DEF-{n:03d}/" in card for n in range(8, 19))
assert "23736" not in card
next_chg = 866
mapping = "\n".join(f"- DEF-{8+i:03d}，{code}，{severity}，开放；{description}。" for i, (code, severity, description) in enumerate([
    ("F01", "P1", "实际答案支持核算与进度屏障"),
    ("F02", "P1", "逐记录来源资格及旧源派生正文抑制"),
    ("F03", "P2", "有界HTTP流、严格UTF-8及重复键"),
    ("F04", "P2", "accepted未claim的同键显式恢复"),
    ("F05", "P2", "32条接受路径容量"),
    ("F06", "P2", "有效G7目标显式沿用"),
    ("F07", "P2", "教学依据与完整历史分页入口"),
    ("F08", "P2", "答案/版本编辑身份及历史选择迟到保护"),
    ("F09", "P2", "规范数值/容差/实例闭域"),
    ("E02", "P1", "概念及程序合成引用不支持实际结论"),
    ("E01", "P2", "25个中间版PG方法的最终版本证据限制"),
]))

audit_decision = f"""# TASK-101 / R-095 编排回收裁定

2026-10-05，Asia/Shanghai，{STAMP}，Codex编排Agent。用户真实回传审计完成；调度已返回，审计交付验收通过。通过的是完整集中只读审计的合同履行，不是被审产品。代码轴不通过、证据轴部分可采且不足、执行控制轴新许可符合授权；G8完整成果不通过，交TASK100同边界集中修复。

报告真实保存且hash与审计冻结一致：b5db0b2e6f787fd6a3fb78ee1e4c1f6ee54b98114731890fb889accd88bd71b4。编排复核141个合同/源码/保护对象/规则/报告身份零漂移，读实际答案核算、来源投影/单SQL、accepted返回、前端身份、数值校验与合成引用原件；未重做797对象审计或运行产品/测试/PG/Job/浏览器。证据DocuN/evidence/TASK-100/orchestration-receipt-04/receipt.json与audit-delivery-identity.json；原101报告和原件不改。

采纳F01—F09、E02和E01。实际引用记录确将原子性/隔离及程序条件/return指向速度公式；目录成员资格不证明内容支持。旧25PG为中间版A，不能以当前B或最后4PG签最终29PG全过。有限结构/事务/窗口、真实DOM字面显示、009及十个浏览器控制继续按101原分级采纳，不废弃全部旧验证、不改六个原总FAIL。

原DEF003/004/006/007已定位根因可关闭；DEF005只关闭TEXT/JSONB/单业务SQL根因，完整逐记录来源与读面仍开放。其他完整G8不变量及早期反例最终覆盖仍受E01限制。新DEF008—018映射见唯一执行动态及100本轮裁定；旧DEF001/002和097禁用控制器不因本卡复活。

本卡默认只读及可选显示probe使用0，旧许可结束，不借给100。独立性按原报告披露：新GPT-6 Codex审计窗口、只读，部分编排评价意外可见但未用于判断，源码初判先于原日志；不因真实型号或品牌补审已完成工作。已知审计辅助解析错误原件保留，未变业务计数。

下一步是原100业务窗口一次合并修复及受影响验证。完整成果稳定后向原101窗口另给一次增量复核合同，只审实际变化、内容oracle和版本补证，不逐小修审计。当前不启动后续审计、不并行读正在改的产品；不签G8、STEP、M-1、V19或部署/项目通过。
"""
audit_path = ROOT / "DocuN/results/TASK-101-work-decision.md"
if audit_path.exists():
    raise SystemExit("Existing TASK101 decision requires explicit continuation handling.")
audit_path.write_text(audit_decision, encoding="utf-8")

prefix("DocuN/results/TASK-100-work-decision.md", f"""# TASK-100 / R-094 审计回收与修复03裁定（2026-10-05，当前）

{STAMP}，Codex编排Agent。101审计交付已验收通过，G8完整成果不通过；100既有候选与限定已采子证据仍部分通过，不能签完整交付。报告及141身份复核零漂移，必要源码/真实引用样本普通核证成立；编排没有执行产品或补业务证据。

采纳并登记全部新发现，以下编号连续由编排占用，同一TASK100修复，不另造TASK102：

{mapping}

DEF003/004/006/007关闭的是原定位根因，DEF005的TEXT/JSONB及单条业务SQL根因关闭、来源/完整投影范围仍开放。不能把旧定位根因关闭扩大为整体G8通过。旧25PG是中间版A，最后4PG及HTTP/实际窗口按具体对象成立，原“29不同PG OK定位”降为这一准确版本分类；不抹原结果。旧概念/程序引用内容不支持层不采，结构/事务与其余已证行为保持。浏览器尾失败的有限字面显示证据够用，不为原总FAIL补绿。

组织一张原100审计修复03长卡：原续作02A+最强业务窗口，F01—F09/E02及E01缺证卡内连续完成，必要受影响验证同批，稳定后原101一次增量审计。009/ACL/原四账/停止权威不改，用户G8-P不重复批准。若需要持久模型或权限变更交具体合同差异。

新许可主动21600/离线1800/真实3600/收尾480秒，entry4/container-start4/app3/SUP尝试18/browser3/driver3/build2，新增使用0。旧entry6/6、start5/5、app3/3、SUP21/24、browser3/3、driver3/3、build1/1及旧失败/未知仍保留；101显示probe余额不借。默认一合并主批，后续只做有据修正的受影响补验，两次修正仍失败或限额到即交回。

2026-10-05T16:32:48+08只读核精确容器Exited(0)/Running=false/Pid=0、18100/55442无监听和本卡进程无残留。两库/卷/行保留；新运行首用再核归属，零DELETE/DROP/TRUNCATE、无用户库/付费/外网/Git。卡与输入保存并回读后调度待转交，不虚构已接收。

本轮原件在DocuN/evidence/TASK-100/orchestration-receipt-04/；原101结果及100执行结果/旧裁定原字节保持。下一步交原业务窗口执行完整卡，完成后带回100结果路径即可。

## 以下为原裁定及全部历史

""")
prefix("DocuN/tasks/TASK-101.md", """# TASK-101 / R-095 已返回及审计交付验收通过（2026-10-05，当前）

本卡已真实完成，独立代码/证据/控制集中审计交付通过；被审G8不通过，具体F01—F09/E01/E02已采纳并转原TASK100合并修复。原只读/可选显示许可已结束，显示probe未使用不借出。报告DocuN/results/TASK-101-result.md及编排裁定TASK-101-work-decision.md原件可读。

修复成果稳定后编排另发原窗口一次增量复核合同；当前不执行补审、不修产品、不并行读取100正在变动对象。下方原合同及其预算原字节保留。

## 以下为本轮已完成的原合同

""")
prefix("DocuS/架构动态文档.MD", """# 架构动态文档

文档 v0.83，2026-10-05，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.05。101集中审计已完成，G8完整成果不通过；同TASK100修复，不新增设计批准包。下面v0.82及全部历史原字节保留。

## G8审计发现与批准合同内修正

产品候选的009不可变事实/最小权限、007原子正文、原四账、launcher/SUP/Job、未知及停止权威保持。当前确定缺陷是支持核算未用实际答案、逐记录来源没有独立于当前新范围复核；这些使正确性与来源边界未达到099，不是持久模型需扩建。

F03—F09仍属批准合同欠实现：严格有界HTTP、accepted未claim同键明确恢复、路径32容量、G7显式seed、教学依据和历史分页、编辑/选择完整身份、规范数值域。按实际教学模块和前端直接依赖修复，不能以设计未改或函数有名就称完整功能。source_refs、命令冻结上下文和既有接口可承载，不批准新表/权限扩大或改旧G7first。

内容样本概念/程序实际引用速度资料，原“有据”质量层不采，要求有限片段与逐论点oracle；目录成员与状态/事务事实继续区分。早期25PG依赖无完整中间原件的三模块，保留中间版A；后4PG及具体HTTP/Windows/浏览器子事实按101绑定可采，不称最终29PG全绿。原总FAIL、旧账未知不改，原显示尾误报不制造新的全批通过要求。

本轮只改教学直接路径和其合成控制/验证，不改001—009、原出站/停止/退款权威、用户数据。稳定点集中原101增量复核实际变化，未受影响G3/G4/D3/G5/G6/G7及有限旧证据继承。完整G8、父STEP、V19真实provider、M-1、部署与项目仍未通过；Compose/Linux/Nginx/Git及其他Must安排保持。

## 以下为v0.82及更早历史

""")
state_text = f"""# 执行动态文档

文档 v2.05，2026-10-05，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.83，task_model/阶段07。下面v2.04及全部历史原字节保留。

## TASK101已返回并验收审计交付；TASK100合并修复03

101/R095调度已返回，审计交付验收通过；新隔离Codex GPT-6窗口只读集中审查完成，身份和意外评价接触已披露，不因此按品牌重审。代码轴不通过，证据轴部分可采且不足，执行控制轴原续02新许可符合授权。可选显示probe及新资源/业务运行使用0，许可结束，不能借给100。报告及本次141合同/源码/保护对象/规则/报告身份零漂移，原审计及657证据没有改动。

100/R094旧候选及确证子事实部分通过，完整G8验收不通过；旧默认与追加许可已结束。同任务审计修复03已登记，调度待保存核证；接收优先原100续作02A+最强业务实现窗口。不是任务重新开始，不新建102/R096，不让审计窗口代实现。当前没有实际转交/开始/运行证据。

原DEF003/004/006/007的已定位根因关闭；DEF005只关闭TEXT/JSONB及单条业务SQL根因，完整逐记录来源/投影范围仍开放。原DEF001/002开放，097旧控制夹具禁用不解除。新发现由编排连续占号，状态均开放，由100一次处置：

{mapping}

证据裁定：25个PG方法实际为三中间模块A，无法直接绑定当前版；最后4PG与具体HTTP/真实窗口/页面控制按101范围可采。概念/程序引用内容不支持层不采，但结构/状态/事务不废弃。浏览器reason尾FAIL是夹具字段错误，实际字面显示可采，不为给旧总批换PASS再跑。原六批FAIL、旧漏时/未知及全部原文保留。受影响新性质与最终字节缺证集中验证，未受改动影响的17旧窗/迁移/全仓不默认重跑。

新增修复03许可主动21600/离线1800/真实3600/独立收尾480秒，entry4/start4/app3/SUP尝试18/browser3/driver3/build2，当前新增使用0。默认一合并主批，其余限有据普通修正后受影响补验，完成即停，两次同根因修正仍失败或限额触顶即交回。原续02entry6/6、start5/5、app3/3、SUP21/24、browser3/3、driver3/3、build1/1；原离线42.750/真实261.211/清理33.313秒、主动13643.958505分段口径与未知旧尾段；初轮至少9入口/漏5.940秒及续01四入口，全部并列不清零。新预算不是旧超限追认。

16:32:48+08编排只读核精确容器Exited(0)/Running=false/Pid=0、18100/55442无监听，无task100运行进程；没有资源启停、数据库连接、产品导入/测试/build/浏览器/Job。精确原容器/卷、g8_main/fault、三个角色与数据保留，新首次使用再核身份，零DELETE/DROP/TRUNCATE。四旧根目录不恢复，归档映射继续有效。公共库和原始需求原字节保持。

101待100稳定完整结果后一次原窗口增量复核，未满足前置不先发补审卡；目前只给一张100完整修复长卡。STEP009—012仍进行中/部分验证，不签G8/V19真实provider/M-1/部署/项目。其他已验切片、剩余Must及Compose/Linux/Nginx/Git计划保持；下一TASK102/R096仅未来计划不占号。

本批CHG0857—0865，下一CHG0866。100/101原结果及旧失败原件不改，完整卡与输入以实际文件为准，用户完成转卡后只需带回100结果路径。

## 以下为v2.04及更早历史

"""
# Register existing TASK continuation before publishing the complete canonical card.
prefix("DocuS/执行动态文档.MD", state_text)
prefix("DocuN/tasks/TASK-100.md", card)

changes = [
    (857, "DocuN/results/TASK-101-result.md", "登记真实审计返回；原报告不改，代码/证据/控制三轴及独立性采纳，审计交付通过与G8不通过分开"),
    (858, "DocuN/evidence/TASK-100/orchestration-receipt-04/", "保存141身份复核、审计交付对象身份、只读资源时点、共享账原字节备份及新合同输入；元数据脚本不执行业务"),
    (859, "DocuN/results/TASK-101-work-decision.md", "保存审计回收裁定、旧根因限定关闭与证据适用性；下一次只审稳定修复实际增量"),
    (860, "DocuN/results/TASK-100-work-decision.md", "置顶集中修复裁定、DEF008—018映射、旧账保留及新许可；原文保留"),
    (861, "DocuN/tasks/TASK-101.md", "置顶已返回/审计交付通过/旧许可结束；原合同原字节保留，未提前启动补审"),
    (862, "DocuS/架构动态文档.MD", "v0.83同步确定教学/来源缺陷、合同欠实现、内容及版本分级；009与原权威不变"),
    (863, "DocuS/执行动态文档.MD", "v2.05登记101实际回收、连续新DEF、100同任务修复和新旧预算；完整卡核证后待转交"),
    (864, "DocuN/tasks/TASK-100.md", "置顶完整审计修复03长卡，A+原实现窗口，F/E/版本补证同卡连续，原冻结和许可保留历史"),
    (865, "DocuN/evidence/TASK-100/orchestration-receipt-04/delivery-proof.json", "保存全文回读、模板/身份/历史/预算一致性与链接核证；不声称已派发或修复完成"),
]
entry = "\n## TASK101审计回收与TASK100合并修复03\n\n" + "\n\n".join(
    f"- CHG-{num:04d}，{STAMP}，Codex编排Agent，{path}。{desc}。" for num, path, desc in changes) + "\n"
log = ROOT / "DocuS/文档变更记录.MD"
if log.read_bytes() != original("DocuS/文档变更记录.MD"):
    raise SystemExit("CHG log changed concurrently.")
log.write_bytes(original("DocuS/文档变更记录.MD") + entry.encode("utf-8"))

# Validate the saved card and original byte-preserving history, then set dispatch readiness.
assert (ROOT / "DocuN/tasks/TASK-100.md").read_bytes().startswith(card.encode("utf-8"))
assert all((ROOT / rel).read_bytes().endswith(original(rel)) for rel in (
    "DocuN/tasks/TASK-100.md", "DocuN/tasks/TASK-101.md", "DocuN/results/TASK-100-work-decision.md",
    "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD"))
assert log.read_bytes().startswith(original("DocuS/文档变更记录.MD"))
state = ROOT / "DocuS/执行动态文档.MD"
final_state_prefix = state_text.replace("调度待保存核证", "调度待转交，完整卡已保存回读核证")
state.write_bytes(final_state_prefix.encode("utf-8") + original("DocuS/执行动态文档.MD"))
assert digest(user_original) == user_original_sha
assert all(digest(Path(x["path"])) == x["actual"] for x in baseline)
assert not any((ROOT / n).exists() for n in ("docu", "evidence", "Ndocu", "spikes"))
paths = [ROOT / p for _, p, _ in changes if not p.endswith("/") and not p.endswith("delivery-proof.json")]
links = ["AGENTS.md", "DocuN/results/TASK-099-result.md", "DocuN/results/TASK-099-work-decision.md",
         "DocuN/results/TASK-100-result.md", "DocuN/results/TASK-101-result.md",
         "DocuN/evidence/TASK-100/orchestration-receipt-04/continuation-input.json",
         "DocuN/evidence/TASK-101/database-http-method-runs.json"]
assert all((ROOT / p).is_file() for p in links)
data = {
    "completed_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "TASK": "TASK-100", "R": "R-094", "continuation": "audit-repair-03",
    "dispatch": "ready_for_manual_transfer", "audit_delivery_TASK101": "accepted", "G8": "not_accepted",
    "card_path": str(ROOT / "DocuN/tasks/TASK-100.md"),
    "card_sha256": digest(ROOT / "DocuN/tasks/TASK-100.md"), "new_card_bytes": len(card.encode("utf-8")),
    "template_sections": headings, "new_card_contains_asterisk": False,
    "historical_suffixes_preserved": True, "baseline_checks": len(baseline), "baseline_mismatches": 0,
    "user_original_sha256": user_original_sha, "old_roots_remain_absent": True,
    "new_resources_started": 0, "new_business_runs": 0, "paths_verified": links,
    "CHG_range": [857, 865], "next_CHG": next_chg,
    "files": [{"path": str(p), "sha256": digest(p)} for p in paths],
}
proof.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"dispatch": data["dispatch"], "card": data["card_path"], "new_card_bytes": data["new_card_bytes"],
                  "baseline_checks": len(baseline), "CHG": "0857—0865", "next": next_chg}, ensure_ascii=False))
