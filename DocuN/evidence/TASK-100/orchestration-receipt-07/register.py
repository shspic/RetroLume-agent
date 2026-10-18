"""One-time shared-document registration; never execute product code."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-100/orchestration-receipt-07"
AT = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def prefix(rel, text, old):
    data = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    if b"*" in data or re.search(rb"(?m)^\|", data):
        raise RuntimeError("New managed Markdown must not contain asterisks or tables")
    (ROOT / rel).write_bytes(data + old)
    return len(data)


STATE = """# 执行动态文档

文档 v2.08，2026-10-06，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.86，task_model/阶段07。下面v2.07及全部历史原字节保留。

## TASK100定向修复04已返回；TASK101 review-03剩余F01增量复核

100/R094定向修复04调度已返回，普通回收部分通过：接受有限解析候选、最终字节的离线证据和保留式交付；F01/DEF008/P1仍待原101独立确认，不将执行者“已修”自评直接登记关闭，不签G8。

实际三个源/测试文件变化：policy局部完整肯定语法与辅助解析、test_task100_repair的两个指定离线方法、新增test_task100_answer_support；test_teaching_policy、support主体、teaching_progress/仓储/009及其他冻结权威未变。基线132旧对象只两项改变，新增一项，其他已核F02—F09/E02/E01及DEF005有限关闭不重开。

编排核133当前与完整as-run副本、after相同，168本轮证据hash匹配，真实pre/post及四个源码diff一致，报告b4ba337a…与交付冻结一致。原49113字节历史尾段SHA18819a4b…完整。旧已核2618/2933大基线直接复用，不重新全量采集。

真实stderr18方法OK与unittest观察器18方法一致；81次成功addSubTest回调、失败/error/skip等0；stdout64条真实样本与导出逐项相等。两个否定/不确定反例、单正确加未知和双正确实例可定位到实际函数返回及断言。此为普通回收，有限语法正确性、有效实例辨别力、旧文字兼容/unknown和调用传播由101独立核，不以合计PASS代裁判。

100修复04许可结束：测试1/3批，离线1.6463436/600秒，最终主动上界1779.265/3600秒，含初读180秒和封装/回传15秒保守额；报告1776.750为封装前检查点，最终账追加2.515秒，旧报告不改。业务/真实资源/模型工具全部0，无复检。一次历史路径检索错误按原账保留；编排接收脚本曾把不同结构的as-run/after JSON整对象比较而exit1，发生在共享写入前，按真实path/hash字段纠正并留原helper，没有业务重跑或改作者原件。

原100修复03entry4/4、start4/4、app3/3、SUP12/18、browser2/3、driver2/3、build2/2及78.735离线/199.422真实/26.906清理/10059.821主动秒、三总FAIL和B4只读PASS保留。旧初轮/续01/02的次数/漏时5.940/未知全部独立保留。101首轮3038.528身份核后计时及未知、review-02主动6778.853/元数据3.725及未知、资源0保持，原许可不复活，任何名义余额不借用。

101/R095 review-03已登记，调度STATUS_TOKEN；A+原review-02独立审计窗口，不能用100实现窗口或记忆。中性索引review-03-input.json SHA f5febafa…列133当前、7规则、3合同与163本轮原件，排除100实施报告/作者结果前缀等五原件。先源码初判再核原始方法/样本与控制，仅剩F01完整增量，不重做G8全审或旧PG/Windows/UI。当前没有真实发送、接收或开始事实。

本轮新许可TASK-101-F01-review-03-20261006：主动3600/元数据300秒，新增使用0；产品导入/compile/unittest/PG/HTTP/Docker/Windows/Job/browser/build/模型工具/联网/Git等全部0，未授予显示probe。100源码/测试/dist冻结，无并行执行；共享文档前缀已正常更新，不把作者旧接收上下文hash当产品漂移。实际原容器停止观察仍保留2026-10-05T19:43:39+08时点，本轮不启资源或虚构新状态检查。

独立101完整真实结果回来后一次裁定DEF008与批准G8有限切片；不预签关闭，不新增TASK102/R096，后者仍仅未来计划。原DEF001/002及097旧runner禁用、其他已关闭根因及全部历史限制保持。STEP009—012、V19真实provider、M-1、部署/项目未放行；其余已验成果、剩余Must与Compose/Linux/Nginx/Git计划沿现有状态。

本批CHG0885—0894，下一CHG0895。用户只需转101完整review-03卡，完成后带回原结果路径。

## 以下为v2.07及更早历史

"""

ARCH = """# 架构动态文档

文档 v0.86，2026-10-06，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.08。G8剩余F01有限解析候选已返回，原101增量复核待转交；G8未关闭。下面v0.85及全部历史原字节保留。

## F01有限肯定形式候选与继承边界

本轮候选把开放文本的同量纲唯一数值搜索改为全文有限肯定形式：单个明确量值起始、封闭肯定说明或精确分钟转秒等式，未知/否定/猜测/引用/问句/开放尾段不作为已核定答案。原参考算术、support主体、数值域、progress及仓储提交调用保持，未增加DTO/持久列、服务或评分平台。

候选18方法/81子测试的真实离线证据和两个有效实例的进度反例已回收；只证明真实函数本地结果，不签新PG/Windows。已验有限说明及单位转换有正例，部分旧开放表达现在unknown，只继承它们未变存储/CAS/账本/停止事实，不强行继承旧数值解析判定。

F01/DEF008可靠性和增量回归尚待原101独立确认；其余F02—F09/E02/E01与DEF005有限读面及旧事务/停止/界面结论保持，旧总FAIL和各未验证范围不整体升级。独立复核只覆盖三文件差异、直接传播、最终离线原件与许可账，默认零业务运行，不从零重复全阶段审计。

G8/父STEP/V19真实provider/M-1/部署/项目仍未通过；原Compose/Linux/Nginx/Git与其他已批准交付计划不变。预算和TASK调度只由执行动态文档维护。

## 以下为v0.85及更早历史

"""

DECISION100 = """# TASK-100 / R-094 定向修复04回收裁定（2026-10-06，当前）

AT_TOKEN，Codex编排Agent。用户已真实回传，调度已返回，普通核证部分通过：接受稳定F01候选及真实最终字节离线证明，不签DEF008/P1关闭或G8。F02—F09/E02/E01和DEF005限定关闭继承，不重开其他已核成果。

报告b4ba337a1fc3bf79652d0718994983895fb81538ee3d217a128a82940a9c40cb，61605字节，与delivery冻结一致；原49113字节历史SHA18819a4b…真实保留。源码变化仅policy、两个离线方法所在test_task100_repair和新增纯测试；实际pre/post及四个源码diff可重建，133当前/被测副本与after一致，168新证据身份匹配。旧2618证据和独立基线直接复用。

真实stderr/观察器方法18、81成功子测试、64stdout样本与导出相等，退出0且零skip/error。普通回收不代独立审计判定语法边界、数据有效性或是否关闭P1。旧开放文字现在unknown的兼容边界已明确，未改进度/仓储/DDL/前端/出站与停止权威，不为新语法默认增加PG/Windows/browser门。

许可结束，测试1/3、离线1.6463436/600、最终主动保守上界1779.265/3600秒；报告1776.750为封装前检查点，差2.515见最终账，保守180及15另列。业务资源全部0，旧许可/失败/未知不复活。本轮实际元数据路径错误及编排接收结构比较错误原件保留，后者发生在共享写入前；都不是业务补跑。

原101/R095 review-03前置已满足，A+原独立审计窗口，仅核F01差异/实际离线原件/传播/控制。新主动3600/元数据300秒、业务0；当前完整卡已保存核可读、待转交，未实际发送或开始。没有新TASK102/R096或新批准包，原100候选冻结。

两执行者结果、旧原件、公共规则/原始需求/归档本次编排零改动；读/hash与文档元数据核证见orchestration-receipt-07/receipt.json和raw-log-receipt.json。最终验收待真实独立结果。

## 以下为原裁定及全部历史

"""

DECISION101 = """# TASK-101 / R-095 review-03登记（2026-10-06，当前）

AT_TOKEN，Codex编排Agent。原review-02审计交付通过及仅F01/DEF008/P1阻断的裁定保持；100定向修复04已实际返回并普通核证稳定，剩余F01增量复核前置满足。沿原独立review-02窗口，A+增强执行，不读实施报告/聊天/推理/实现记忆，不扩大成G8全审。

中性输入review-03-input.json SHA f5febafa84ace45f2a77783873a641ea414ec165ee7d55224f570bfd5d15959f，冻结三差异及133当前对象、七规则、三合同和163本轮原件，排除五份作者结果原件与当前100实施报告。原review-02及未变源码/PG/Windows/UI结论直接继承；代码初判先于作者语法/传播说明，实际原日志再核18方法、81回调、64样本及有效进度实例。

新许可TASK-101-F01-review-03-20261006为主动3600/元数据300秒，当前使用0、调度待转交；业务/资源/产品执行全部0，无显示probe。原review-02主动6778.853、已登记辅助3.725及未知、首轮3038.528身份核后范围和未知均保留，100各轮原账不借用。

共享state/task/work-decision正常更新不属于冻结产品漂移；产品只以当前中性133/规则核，不拿作者旧接收上下文对比新共享前缀。原101结果70370字节/b75f00d8…及历史完整保留，新增结果在同文件置顶review-03，审计只建议，编排后来裁定G8。

完整卡保存回读通过，没有真实发送、接收或开始事实，不登记已派发。本轮不新增TASK/R/DEF或批准包，不预签F01关闭；具体受限继承和未验证范围在卡内完整列明。

## 以下为原裁定及全部历史

"""

NOTICE100 = """# TASK-100 / R-094 定向修复04已返回冻结通知（2026-10-06，当前）

候选及最终离线证据已由编排普通回收，F01/DEF008关闭仍待原101独立增量复核。原修复04新许可结束，测试1/3与所有旧未用余额均不恢复；不再测试、编辑或启任何旧真实入口。当前三文件候选、范围外产品/测试/dist、规则及原证据全部冻结，无并行执行。

原完整修复04合同已保存在DocuN/evidence/TASK-100/orchestration-receipt-07/TASK-100-repair-04-card-as-returned.md，下面卡面/预算/失败历史原字节保留。结果及旧原件不由编排改写，不签G8或父STEP。

下一步原101/R095 review-03，A+原独立窗口仅读本次F01增量及离线原件；本窗口等待真实裁定，不代审、不暗用余量。需要获准修改时须收到新的完整合同。

## 以下为已结束的原合同及全部历史

"""


def main():
    proof_path = OUT / "delivery-proof.json"
    if proof_path.exists():
        raise RuntimeError("Registration already completed")
    before = {}
    for row in load(OUT / "before-manifest.json"):
        data = (ROOT / row["path"]).read_bytes()
        if data != Path(row["backup"]).read_bytes() or sha(data) != row["sha256"]:
            raise RuntimeError("Shared input changed since receipt")
        before[row["path"]] = data
    if max(map(int, re.findall(r"CHG-(\d+)", before["DocuS/文档变更记录.MD"].decode("utf-8-sig")))) != 884:
        raise RuntimeError("Next CHG changed")
    neutral_path = ROOT / "DocuN/evidence/TASK-101/review-03-input.json"
    neutral = load(neutral_path)
    if sha(neutral_path.read_bytes()) != "f5febafa84ace45f2a77783873a641ea414ec165ee7d55224f570bfd5d15959f":
        raise RuntimeError("Independent input changed")
    stable = list(neutral["current_objects"]) + list(neutral["contracts"])
    stable += [{"path": row["path"], "sha256": row["expected"]} for row in neutral["rules"]]
    stable += [{"path": str(ROOT / "DocuN/results/TASK-100-result.md"), "sha256": "b4ba337a1fc3bf79652d0718994983895fb81538ee3d217a128a82940a9c40cb"},
               {"path": str(ROOT / "DocuN/results/TASK-101-result.md"), "sha256": "b75f00d8a9a1e3c564d221dc70ca591cb0fa0a23ddf276a691cd1d323ba1dbb2"}]
    for row in stable:
        if sha(Path(row["path"]).read_bytes()) != row["sha256"]:
            raise RuntimeError("Source, rule, or executor report drifted")
    card = (OUT / "TASK-101-review-03-card.md").read_text(encoding="utf-8")
    headings = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
                "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    if any(f"## {title}\n" not in card for title in headings) or "〈" in card or "〉" in card:
        raise RuntimeError("Incomplete seven-section card")
    offsets = {}
    offsets["DocuS/执行动态文档.MD"] = prefix("DocuS/执行动态文档.MD", STATE.replace("STATUS_TOKEN", "卡面整理中，未转交"), before["DocuS/执行动态文档.MD"])
    for rel, text in [
        ("DocuN/results/TASK-100-work-decision.md", DECISION100.replace("AT_TOKEN", AT)),
        ("DocuN/tasks/TASK-100.md", NOTICE100),
        ("DocuN/results/TASK-101-work-decision.md", DECISION101.replace("AT_TOKEN", AT)),
        ("DocuS/架构动态文档.MD", ARCH),
        ("DocuN/tasks/TASK-101.md", card),
    ]:
        offsets[rel] = prefix(rel, text, before[rel])
    actual_card = (ROOT / "DocuN/tasks/TASK-101.md").read_bytes()
    expected_prefix = card.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    if actual_card != expected_prefix + before["DocuN/tasks/TASK-101.md"]:
        raise RuntimeError("Full saved task card differs from prepared card")
    offsets["DocuS/执行动态文档.MD"] = prefix("DocuS/执行动态文档.MD", STATE.replace("STATUS_TOKEN", "待转交"), before["DocuS/执行动态文档.MD"])
    docs, histories = [], []
    for rel, offset in offsets.items():
        data = (ROOT / rel).read_bytes()
        exact = data[offset:] == before[rel]
        if not exact:
            raise RuntimeError("Shared history changed")
        docs.append({"path": rel, "sha256": sha(data), "bytes": len(data)})
        histories.append({"path": rel, "prefix_bytes": offset, "old_bytes": len(before[rel]), "old_sha256": sha(before[rel]), "exact": exact})
    for row in stable:
        if sha(Path(row["path"]).read_bytes()) != row["sha256"]:
            raise RuntimeError("Product or report changed during document registration")
    entries = [
        (885, "DocuN/evidence/TASK-100/orchestration-receipt-07/receipt.json", "回收100定向修复04，候选与有限离线证据接收，F01仍待独立确认；报告旧49113字节保留。"),
        (886, "DocuN/evidence/TASK-101/review-03-input.json", "保存剩余F01中性输入，133当前/七规则/三合同/163本轮原件，排除实施自评与结果前缀，不重采旧大基线。"),
        (887, "DocuN/results/TASK-100-work-decision.md", "普通核证三个实际文件差异、final/as-run及18/81/64原件，1779.265最终计量与旧封装检查点分列，许可结束。"),
        (888, "DocuN/tasks/TASK-100.md", "置顶实际返回/冻结和全部许可结束；原完整修复04合同与旧预算原字节保留，不借未用批。"),
        (889, "DocuN/results/TASK-101-work-decision.md", "登记原A+独立窗口review-03剩余增量安排，新主动3600/元数据300秒、业务资源0，尚无发送或开始事实。"),
        (890, "DocuS/架构动态文档.MD", "v0.86说明全文有限肯定解析候选及unknown/继承边界，原support/进度/仓储/DDL/前端保持，未签G8。"),
        (891, "DocuS/执行动态文档.MD", "v2.08登记100实际回收/预算冻结、F01候选待验、101完整卡核证后待转交，TASK/R/DEF及历史未重置。"),
        (892, "DocuN/tasks/TASK-101.md", "保存完整七节review-03卡，原窗口只核剩余P1的源码/真实离线证据/控制，旧充分结论直接继承，零新业务执行。"),
        (893, "DocuN/evidence/TASK-100/orchestration-receipt-07/raw-log-receipt.json", "普通重建实际18方法/81成功子测试与64stdout样本，区别检查点和最终费用，不代独立断言裁定。"),
        (894, "DocuN/evidence/TASK-100/orchestration-receipt-07/delivery-proof.json", "保存完整卡回读、七节/历史/稳定来源与输入核证，未声称实际转交/接收/开始。"),
    ]
    for _, rel, _ in entries[:-1]:
        if not (ROOT / rel).is_file():
            raise RuntimeError("Cannot log a missing actual document")
    addition = "\r\n\r\n" + "\r\n\r\n".join(f"- CHG-{number:04d}，{AT}，Codex编排Agent，{rel}。{text}" for number, rel, text in entries) + "\r\n"
    proof_path.write_text(json.dumps({"at": AT, "task": "TASK-101", "R": "R-095", "round": "review-03",
        "status": "待转交", "sent_received_started": False, "recipient": "A+ original TASK-101 review02 independent window",
        "all_sections_present": True, "headings": headings, "card_prefix_bytes": len(expected_prefix), "card_prefix_sha256": sha(expected_prefix),
        "neutral_input_sha256": sha(neutral_path.read_bytes()), "stable_input_checks": len(stable),
        "source_objects": 133, "rule_objects": 7, "actual_old_reports_untouched": True, "history_exact": histories,
        "documents": docs, "CHG": {"first": 885, "last": 894, "next": 895},
        "versions": {"state": "2.08", "architecture": "0.86", "requirements": "1.1"},
        "CHG_expected_sha256": sha(before["DocuS/文档变更记录.MD"] + addition.encode("utf-8")),
        "root_product_writes": 0, "root_business_runs": 0, "independent_new_resource_budget": 0,
        "candidate_status": "F01/DEF008/P1 pending independent review, no G8 closure"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "DocuS/文档变更记录.MD").write_bytes(before["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    actual_log = (ROOT / "DocuS/文档变更记录.MD").read_bytes()
    if not actual_log.startswith(before["DocuS/文档变更记录.MD"]) or max(map(int, re.findall(r"CHG-(\d+)", actual_log.decode("utf-8-sig")))) != 894:
        raise RuntimeError("Change history or final numbering differs")
    print(json.dumps({"card": str(ROOT / "DocuN/tasks/TASK-101.md"), "prefix_bytes": len(expected_prefix),
        "history_preserved": len(histories), "stable_identity_checks": len(stable), "state": "v2.08", "architecture": "v0.86",
        "CHG": "0885-0894; next0895", "status": "ready for manual handover", "root_product_writes": 0, "business_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
