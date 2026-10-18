"""One-time orchestration registration; document/hash operations only."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-100/orchestration-receipt-06"
AT = datetime.now(timezone(timedelta(hours=8))).isoformat()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def new_json(name, value):
    path = OUT / name
    if path.exists():
        raise RuntimeError(f"Refuse repeated registration: {path}")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prefix(rel, text, old):
    data = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    if b"*" in data or re.search(rb"(?m)^\|", data):
        raise RuntimeError("New managed Markdown contains asterisks or a table")
    (ROOT / rel).write_bytes(data + old)
    return len(data)


STATE = """# 执行动态文档

文档 v2.07，2026-10-05，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.85，task_model/阶段07。下面v2.06及全部历史原字节保留。

## TASK101 review-02已返回；TASK100剩余F01定向修复04

101/R095 review-02调度已返回，审计交付验收通过；其被审代码仍不通过，仅F01/DEF-008/P1未关闭。实际报告b75f00d8…与交付检查一致，39114字节首轮历史尾段完整；原独立Codex desktop/GPT-6窗口未参与实施，实际身份与接触范围按报告披露，不按品牌重审。

本轮裁定如下，有限关闭不升级未验证范围：

- DEF-008/F01/P1开放：原不读实际答案已修，60/0.01数值冲突屏障和原正确样例有效；当前解析仍把单值否定/不确定当matched。该遗漏是源码可确定B级，不声称真实provider已误判。
- DEF-009/F02/P1关闭：记录原来源与当前合法新范围分开核、共同单SQL读取及旧源题/路径/反馈抑制，原资格缺字段仅为不可达条件观察。
- DEF-010—016/F03—F09关闭：严格HTTP、accepted未claim同键恢复、32路径、有效G7显式seed、引用及完整历史、答案/版本与双标签草稿身份、规范有限数值域按101范围成立。G7仅薄沿用，不升级旧G7整链。
- DEF-017/E02/P1关闭：九正常输出25个引用对象、作者八记录24对及额外输出独立分级核实；故意false_met两窗为负屏障，未导出完整007 payload和真实provider质量保持限制，旧无关引用不追改PASS。
- DEF-018/E01/P2关闭：29个不同当前PG方法加3次补验、3HTTP和58加18离线逐方法/字节可绑定；不是32个不同PG方法，不是原29PG/4HTTP全名单重新通过。旧25中间版缺原件保留历史。
- DEF-005剩余逐记录来源/公开投影有限范围关闭；旧TEXT/JSONB与单SQL根因已关闭事实继承。全面投影重建未动态验证，旧不可追回版本不伪造补齐。

原DEF001/002及097旧注入/runner禁用不变，DEF003/004/006/007的已定位根因保持关闭。没有本轮新增共享缺陷号；非阻断观察不自动变新门槛。

编排普通核当前132、七规则、18保护对象及真实审计报告158项一致；审计实际独立hash为2933匹配、作者result-header一项排除，不把索引2934写成全匹配。原2618证据、内容/方法/浏览器/控制独立配对按101直接继承，不新增测试或重新全量采集。接收辅助误以保护对象与current不重叠而exit1，发生在备份/共享写入前；按原索引纠正，原helper保留，没有产品或业务重跑。

101 review-02许可结束：业务与资源运行0，主动6778.853/10800秒、已登记辅助3.725/600秒，保存/计数纠正按其原件另列，首读及未逐次shell开销未知。首轮3038.528秒身份核后范围及未知不清零，不借未用probe。100修复03全部许可结束，entry4/4、start4/4、app3/3、SUP12/18、browser2/3、driver2/3、build2/2；78.735离线/199.422真实/26.906清理/10059.821主动秒及原三总FAIL、旧初轮/续01/02账和漏时保持。

同100/R094定向修复04已登记，调度STATUS_TOKEN；接收A+原审计修复03实现窗口，不占用独立101窗口。只修有限答案解析与受影响纯函数验证，teaching_progress/repository只读，001—009、其他模块、前端/dist和旧证据冻结。新许可TASK-100-F01-repair-04-20261005，主动3600/离线600秒，最多3批各≤60秒；新增使用0，全部PG/HTTP服务器/Docker/应用/Windows/Job/browser/build/模型工具/网络/Git运行0。原资源停止观察保留2026-10-05T19:43:39+08时点，本轮不启资源，也不虚构新现状检查。

完整卡保存核证后转为待转交；当前没有实际发送、接收或启动证据。稳定结果返回后，才由编排更新原101 review-03合同，只核F01真实增量/离线原件/调用传播，不从零再审G8或重跑已成立PG/Windows/UI。下一TASK102/R096仍仅未来计划，未占号。

G8仍未关闭，STEP009—012仍进行中/部分验证；不签真实provider/V19、M-1、部署或项目。其余已验切片、剩余Must及Compose/Linux/Nginx/Git安排沿现有事实继续，本次不新增批准包或重复审批。

本批CHG0876—0884，下一CHG0885。用户只需转100完整修复04卡，完成后带回原结果路径。

## 以下为v2.06及更早历史

"""

ARCH = """# 架构动态文档

文档 v0.85，2026-10-05，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.07。101 review-02有限增量审计交付通过；G8仅剩有限答案可靠解析P1，未整体通过。下面v0.84及全部历史原字节保留。

## G8有限修正采纳与剩余可靠解析

当前逐记录原来源资格、共同单SQL读面、严格有界HTTP、未claim冻结意图同键恢复、32路径容量、显式合法G7seed、引用/历史分页、答案版本和草稿owner隔离、规范有限数值域已由101独立按实际源码与证据核实。DEF009—018及DEF005剩余公开投影有限范围关闭；共同读取链保证source_qualified为bool，缺字段的防御观察不升级为可达缺陷。

合成三题实际内容引用与当前方法/最终UI版本绑定已可采，旧总FAIL、旧缺原件、007完整payload未导出、额外一个输出无新HTTP引用证明、合成只读浏览器不证明新认证/写入等边界继续分级。没有把旧29PG/4HTTP整名单或真实provider质量整体重签通过。

唯一剩余阻断是F01/DEF008：有限数值解析从开放文字中筛唯一同量纲候选，不能区分“否定1m/s”与“答案未知、可能1m/s”；模型met可绕过进度收紧。原真实值冲突和正确支持已成立，接续只完善闭集肯定形式与unknown传播，不建设任意语言判分器，不增加DTO、持久列或服务。

实施仍用原100窗口，只允许policy局部解析与对应离线样例。实际rebuild_progress/仓储调用、001—009、原账本/资格/停止/退款、前端dist及其他已验切片保持；额外生产改动如确为必需须带最小冲突交回。稳定后原101只核剩余增量，不重复全面审计或真实资源运行。

G8、父STEP、V19/真实provider、长期记忆、删除、M-1、部署和项目验收限制与Compose/Linux/Nginx/Git交付安排保持。总状态与预算只由执行动态文档维护，本文件仅记机制与审定边界。

## 以下为v0.84及更早历史

"""

DECISION101 = """# TASK-101 / R-095 review-02回收裁定（2026-10-05，当前）

AT_TOKEN，Codex编排Agent。用户已真实回传，调度已返回；本轮独立审计交付验收通过，被审G8代码仍不通过，唯一阻断F01/DEF-008/P1。报告b75f00d8a9a1e3c564d221dc70ca591cb0fa0a23ddf276a691cd1d323ba1dbb2与交付检查匹配，39114字节首轮全文尾段保留；不是只凭返回摘要判定。

DEF009—016/F02—F09、DEF017/E02、DEF018/E01在报告有限范围关闭，DEF005来源/公开投影剩余有限项关闭；DEF008原不读答案子项关闭但单值否定/不确定可靠解析仍开放。原60/0.01冲突、不同实例推进、真实提交/停止及当前来源/最终UI已采子事实继承，没有新的未决批准包。五项等价或未变方法不冒称全量重新运行，旧25中间字节缺失与旧FAIL保留。

审计三轴原件、源码确定触发及辅助身份经编排核证：当前132/七规则/18保护对象/报告158项匹配，2933独立hash与1作者header排除口径采纳。内容、方法、浏览器、控制相互绑定及相应局限按review-02分级继承，没有编排业务测试/产品修改。辅助接收脚本保护对象重叠假设错误在共享写入前停止，修正按原中性索引18项；原脚本保留，不修改作者证据。

新审计许可结束：业务与资源0，主动6778.853/10800秒、已登记辅助3.725/600秒，保存确认/计数纠正另见原件，首读及未登记开销仍未知；首轮3038.528及其未知不重置，未用probe或余额不转借。

下一步只同100/R094定向修复04，A+原实现窗口，离线纯函数验证。真正完整稳定返回后才更新原101 review-03，只核F01实际差异、受影响原始日志及调用传播，其他未变充分结论直接继承。现在无新审计卡或新运行许可，不能自动重跑PG/Windows/browser或为旧总FAIL换PASS。

详见 DocuN/evidence/TASK-100/orchestration-receipt-06/receipt.json、identity-checks.json及158身份记录；报告和自有审计证据全部原字节保持。G8/STEP/M-1/部署/项目未通过，本轮不新增TASK/R/DEF号。

## 以下为原裁定及全部历史

"""

DECISION100 = """# TASK-100 / R-094 F01定向修复04裁定（2026-10-05，当前）

AT_TOKEN，Codex编排Agent。101 review-02真实返回，审计交付通过，100候选仍部分通过，G8暂不通过。F02—F09/E02/E01及DEF005剩余来源/公开投影有限项按独立证据关闭；仅F01/DEF008/P1剩余单值否定/不确定被当数值肯定答案。

修复04沿原TASK/R和实现窗口，A+增强执行。范围仅teaching_policy有限解析及相关离线测试，直接调用derive_support_checks与rebuild_progress核两个有效独立实例的false_met屏障和正常兼容；现有unknown收紧、仓储提交、DTO/DDL/前端/停止退款均不改。追加的新许可主动3600/离线600秒、最多3个≤60秒测试批，真实资源/模型/联网/Git全部0；新使用0，调度待转交，没有实际发送/开始。

100修复03及初轮/续01/02许可已结束，所有旧失败、预算、漏时/未知保留。101实际2933hash/1排除、有限方法与内容边界沿报告，不为关闭新解析漏洞废弃旧提交/控制/界面证明。新纯函数结果只签本地函数行为，源码传播只签调用事实，不冒充新PG/Windows动态通过。

原TASK100结果18819a4b8851ab4bb8ecf3eb98ab524ec980bffe680e0cb7d212601a7408c0e3、原TASK101结果b75f00d8…本次编排零修改。首改基线和接收元数据已保存到orchestration-receipt-06，实际差异及最终日志由原实现窗口交付后，原独立101只作受影响增量复核。

完整当前卡仍在DocuN/tasks/TASK-100.md；不增加102/R096或新批准包。G8、父STEP、真实provider/M-1/项目与部署保持未放行。必要用户动作仅转卡和带回结果路径。

## 以下为原裁定及全部历史

"""

NOTICE101 = """# TASK-101 / R-095 review-02已返回并结束许可（2026-10-05，当前）

独立审计交付已由编排验收通过；代码仅剩F01/DEF008/P1，G8未关闭。F02—F09/E02/E01及DEF005剩余来源/投影有限范围采纳，具体分层、原失败、未知与非阻断观察沿实际结果和work-decision。

review-02只读许可结束，业务/资源运行0；不自动继续写其证据、不启动旧显示probe、PG/Windows/browser或借余量。原TASK100接续修复04已登记，当前独立窗口等待真实稳定结果；只有收到编排更新的完整review-03合同后，才核本次F01实际增量。现在没有review-03已派发或新运行许可。

下面完整review-02合同及历史原字节保留，旧条款不恢复执行权；原TASK101-result.md及review-02证据不由编排改写。审计最终结果以真实文件为准，不以作者摘要或总OK数替代。

## 以下为已结束的原合同及全部历史

"""


def main():
    if (OUT / "delivery-proof.json").exists():
        raise RuntimeError("Registration already completed; do not run again")
    backups = load(OUT / "before-manifest.json")
    before = {}
    for item in backups:
        rel = item["path"]
        data = (ROOT / rel).read_bytes()
        archived = Path(item["backup"]).read_bytes()
        if data != archived or digest(data) != item["sha256"]:
            raise RuntimeError(f"Shared file changed since receipt: {rel}")
        before[rel] = data
    chg = before["DocuS/文档变更记录.MD"].decode("utf-8-sig")
    if max(map(int, re.findall(r"CHG-(\d+)", chg))) != 875:
        raise RuntimeError("Next CHG changed")
    checks = load(OUT / "identity-checks.json")
    for item in checks:
        path = Path(item["path"])
        if not path.is_file() or digest(path.read_bytes()) != item["expected"]:
            raise RuntimeError(f"Input changed since receipt: {path}")
    frozen = load(ROOT / "DocuN/evidence/TASK-100/audit-repair-03/final-identity.json")
    essentials = load(OUT / "essential-identities.json")
    card = (OUT / "TASK-100-repair-04-card.md").read_text(encoding="utf-8")
    required = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文",
                "执行边界与资源", "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    if any(f"## {heading}\n" not in card for heading in required):
        raise RuntimeError("Incomplete task template")
    if "〈" in card or "〉" in card or "*" in card:
        raise RuntimeError("Unfilled card or managed formatting violation")
    allowed = ["backend/app/learning/teaching_policy.py", "backend/tests/test_task100_repair.py",
               "backend/tests/test_teaching_policy.py", "backend/tests/test_task100_answer_support.py"]
    new_json("scope-baseline.json", {"at": AT, "task": "TASK-100", "R": "R-094", "round": "repair-04",
        "allowed_sources_tests": allowed, "optional_new_file": allowed[-1],
        "optional_new_file_already_present": (ROOT / allowed[-1]).exists(),
        "post_baseline": frozen["post_files"], "protected_and_rules": [x for x in checks if x["group"] in ("protected", "rules")],
        "audit_report_and_finding": [x for x in essentials if x["path"] in ("DocuN/results/TASK-101-result.md", "DocuN/evidence/TASK-101/review-02/F01-static-finding.md")],
        "permission": "TASK-100-F01-repair-04-20261005", "limits": {"active_seconds": 3600, "offline_seconds": 600, "test_batches": 3, "batch_seconds": 60},
        "real_resources": 0, "prior_permissions_ended": True, "only_manual_handover": True})
    offsets = {}
    # Register the continuation before saving and verifying the deliverable card.
    offsets["DocuS/执行动态文档.MD"] = prefix("DocuS/执行动态文档.MD", STATE.replace("STATUS_TOKEN", "卡面整理中，未转交"), before["DocuS/执行动态文档.MD"])
    for rel, text in [
        ("DocuN/results/TASK-101-work-decision.md", DECISION101.replace("AT_TOKEN", AT)),
        ("DocuN/tasks/TASK-101.md", NOTICE101),
        ("DocuN/results/TASK-100-work-decision.md", DECISION100.replace("AT_TOKEN", AT)),
        ("DocuS/架构动态文档.MD", ARCH),
        ("DocuN/tasks/TASK-100.md", card),
    ]:
        offsets[rel] = prefix(rel, text, before[rel])
    saved_card = (ROOT / "DocuN/tasks/TASK-100.md").read_bytes()
    expected_prefix = card.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    if saved_card != expected_prefix + before["DocuN/tasks/TASK-100.md"]:
        raise RuntimeError("Saved task card differs from complete prepared card")
    # The entire card has been read back and checked; now it is ready for manual handover.
    offsets["DocuS/执行动态文档.MD"] = prefix("DocuS/执行动态文档.MD", STATE.replace("STATUS_TOKEN", "待转交"), before["DocuS/执行动态文档.MD"])
    history = []
    docs = []
    for rel, length in offsets.items():
        data = (ROOT / rel).read_bytes()
        exact = data[length:] == before[rel]
        history.append({"path": rel, "prefix_bytes": length, "original_suffix_bytes": len(before[rel]),
                        "original_suffix_sha256": digest(before[rel]), "exact": exact})
        docs.append({"path": rel, "sha256": digest(data), "bytes": len(data)})
        if not exact:
            raise RuntimeError(f"Historical bytes changed: {rel}")
    unchanged = [check for check in checks if digest(Path(check["path"]).read_bytes()) == check["expected"]]
    if len(unchanged) != len(checks):
        raise RuntimeError("Product, rule, or audit input changed during document registration")
    for item in essentials:
        if item["path"] in ("DocuN/results/TASK-100-result.md", "DocuN/results/TASK-101-result.md"):
            if digest((ROOT / item["path"]).read_bytes()) != item["sha256"]:
                raise RuntimeError("Executor report changed")
    entries = [
        (876, "DocuN/evidence/TASK-100/orchestration-receipt-06/receipt.json", "回收101 review-02与158输入身份；报告历史保留，审计交付通过，G8仅F01仍P1。接收元数据修正留原件，无业务运行。"),
        (877, "DocuN/results/TASK-101-work-decision.md", "登记review-02三轴及有限关闭；2933匹配/1排除、6778.853秒及未知分层，原许可结束。"),
        (878, "DocuN/tasks/TASK-101.md", "置顶review-02已返回与许可结束；原合同保留，等待实际100修复04后再给增量合同。"),
        (879, "DocuN/results/TASK-100-work-decision.md", "仅剩F01同任务修复04，原A+窗口、纯函数验证与新有界离线许可，旧失败/投入不清零。"),
        (880, "DocuS/架构动态文档.MD", "v0.85采纳已核有限修正，说明唯一可靠解析缺口；旧权威/DDL/UI与未验证边界保持。"),
        (881, "DocuS/执行动态文档.MD", "v2.07登记101真实回收、DEF009—018及DEF005限定关闭、DEF008仍开放和100接续；整卡核证后待转交。"),
        (882, "DocuN/tasks/TASK-100.md", "保存完整七节定向修复04合同；有限肯定形式、反例/正常兼容、最终字节与三批离线验证，真实资源0。"),
        (883, "DocuN/evidence/TASK-100/orchestration-receipt-06/scope-baseline.json", "保存本轮允许写域与冻结基线、独立输入和明确新增预算，不借旧许可或发新TASK号。"),
        (884, "DocuN/evidence/TASK-100/orchestration-receipt-06/delivery-proof.json", "完整卡回读、七节/路径/历史/版本与158未变身份核证；无派发或开始事实。"),
    ]
    for number, rel, _ in entries[:-1]:
        if not (ROOT / rel).is_file():
            raise RuntimeError(f"Cannot record missing CHG object {number}: {rel}")
    additions = "\r\n\r\n" + "\r\n\r\n".join(
        f"- CHG-{number:04d}，{AT}，Codex编排Agent，{rel}。{desc}" for number, rel, desc in entries) + "\r\n"
    new_json("delivery-proof.json", {"at": AT, "task": "TASK-100", "R": "R-094", "round": "repair-04",
        "routing": "A+ original TASK-100 repair03 implementation window, manual handover",
        "status": "待转交", "sent_received_started": False, "active_agents_created": 0,
        "card_prefix_sha256": digest(expected_prefix), "card_prefix_bytes": len(expected_prefix),
        "required_sections": required, "all_sections_present": True,
        "new_managed_markdown_has_asterisks_or_tables": False,
        "documents": docs, "history_exact": history, "unchanged_identity_count": len(unchanged),
        "executor_results_untouched": True, "root_product_writes": 0, "root_business_runs": 0,
        "versions": {"architecture": "0.85", "state": "2.07", "requirements": "1.1"},
        "CHG": {"first": 876, "last": 884, "next": 885},
        "CHG_original_bytes": len(before["DocuS/文档变更记录.MD"]),
        "CHG_expected_final_sha256": digest(before["DocuS/文档变更记录.MD"] + additions.encode("utf-8")),
        "receipt_scope": "Only F01 remains blocking; previous independent audit sufficiency reused, no new product audit or tests by root"})
    change_path = ROOT / "DocuS/文档变更记录.MD"
    change_path.write_bytes(before["DocuS/文档变更记录.MD"] + additions.encode("utf-8"))
    check_log = change_path.read_bytes()
    if not check_log.startswith(before["DocuS/文档变更记录.MD"]):
        raise RuntimeError("CHG history changed")
    if max(map(int, re.findall(r"CHG-(\d+)", check_log.decode("utf-8-sig")))) != 884:
        raise RuntimeError("CHG final numbering mismatch")
    print(json.dumps({"saved_complete_card": str(ROOT / "DocuN/tasks/TASK-100.md"),
        "prefix_bytes": len(expected_prefix), "history_exact": len(history), "unchanged_identities": len(unchanged),
        "state": "v2.07", "architecture": "v0.85", "status": "待转交", "CHG": "0876-0884; next 0885",
        "resources_run": 0, "product_writes": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
