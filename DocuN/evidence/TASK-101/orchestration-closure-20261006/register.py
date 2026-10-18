"""Close accepted G8 and register the next read-only contract task."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-101/orchestration-closure-20261006"
AT = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def create_json(path, value):
    if path.exists():
        raise RuntimeError(f"Refuse replacing existing work: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_bytes(text):
    data = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    if b"*" in data or re.search(rb"(?m)^\|", data):
        raise RuntimeError("New managed Markdown formatting violation")
    return data


def prefix(rel, text, old):
    addition = md_bytes(text)
    (ROOT / rel).write_bytes(addition + old)
    return len(addition)


STATE = """# 执行动态文档

文档 v2.09，2026-10-06，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.87，task_model/阶段07。下面v2.08及全部历史原字节保留。

## G8有限切片验收关闭；TASK102学习记忆合同

101/R095 review-03调度已返回，审计交付验收通过。编排已读真实结论、差异/原件及限制并核当前306输入一致；报告88129字节/SHA91005c91…与delivery绑定，70370字节原历史尾段/SHA b75f00d8…原字节保留，100结果b4ba337a…未改。独立三轴在本轮有限范围通过，F01/DEF008/P1关闭，没有repair04新增P0/P1或确定回归。

TASK100/R094已批准G8有限合同验收通过并关闭，TASK101/R095完整集中审计及必要增量已关闭。范围为已批准目标路径/有据练习/反馈与有限支持检查/独立复测进度、公开读与工作区恢复、最终字节证据及授权控制；不是所有学科/开放表达/真实provider或全部Must通过。F02—F09/E02/E01、DEF005及其他已关闭定位根因保持；未改G3/G4/D3/G5/G6/G7证明直接继承，原FAIL/旧中间缺字节/其余限制不升级。

STEP009—012当前为已实现且有限合成闭环验收，完整需求仍部分验证，不再按旧基表写“路径未实现/010—012未开始”。未签V19真实provider、完整向量RAG、长期掌握/记忆、HTML、面试、物理删除、M-1、STEP018—020或项目。独立审计不是靠自评通过，普通元数据核证也没有新产品运行。

新登记DEF-019/P2，来源R03-O01：同单位64有效位乘除会把合法明确答案1+10^-65舍成1，tolerance=None存在极小精度边界。既有pre也如此，B级未运行观察，非repair04回归，不重开G8，不新增PG/浏览器门。主要修复归属为MOD006教学数值支持政策，后续相关完整实施可合并同单位保留原Decimal/跨单位可靠比较或超支持精度unknown及离线边界例；当前只跟踪不实施。原DEF001/002开放及097旧runner禁用不变，无开放新P0/P1归本G8切片。

101 review-03许可结束：主动最终上界2002.341/3600秒，含首读保守600及回传30；元数据保守180/300，已测helper4.529708/失败工具1.539763/另只读0.426514为不同局部口径，完整shell未知保留；四个元数据exit1原件和修正版保留。业务/资源/产品运行0，未用额度不借出。100修复04测试1/3、离线1.6463436/600、最终主动1779.265/3600秒与报告封装前1776.750差2.515保留；原100初轮/续01/02/修复03及101早轮投入/FAIL/漏时5.940/未知不清零。

所有100/101旧许可结束，代码/测试/dist和旧证据冻结，两个结果本次编排零改动；原容器停止观察保持2026-10-05T19:43:39+08历史时点，本轮未启资源或虚构新状态查询。归档四旧根目录、公共锁定规则及用户原始需求不动，无Git写入。

新TASK102/R096已占号，G9/STEP013学习记忆生命周期与删除一致性完整A—D实施合同，调度STATUS_TOKEN。接收A+原TASK100定向修复04业务窗口，不占用101审计窗口；只读设计，10800秒主动/600秒元数据，新使用0。允许必要官方只读查证≤6页，产品/DDL/测试/PG/HTTP/Windows/Docker/browser/build/模型工具/真实付费/用户数据操作/安装/Git运行全部0，没有实际发送/接收/开始事实。

新任务从实际FLOW004三层记忆、FLOW007撤销先行与精确清理、009不可变事实及现有上下文权威起步。一次交付真实缺口、唯一最小数据/事务/消费合同、工作区接线和删除/恢复验收矩阵；必要持久模型/权限等只给一个具体合并批准包，不现在索要空泛批准或实施。完整STEP009/012尚未全验，不阻塞依其已验有效子项做只读设计；G9未实现未验证，STEP013转为合同收敛待转交。

后续实现与一次稳定点独立增强审计待102合同真实返回及必要包批准后安排，未先发依赖卡。STEP014面试、015/016 HTML、017备份/退出、018集成Compose及Linux/Nginx边界、019权限验收、020自用交接与真实provider/完整检索仍按原需求推进，当前不借G8关闭放行。Git仅既有授权首提交，后续不自动commit/push。

本批CHG0895—0905，下一CHG0906；下一新TASK103/R097仅未来计划，未占号。用户只需转102完整合同卡，完成后带回结果路径。

## 以下为v2.08及更早历史

"""

ARCH = """# 架构动态文档

文档 v0.87，2026-10-06，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.09。G8批准有限合同实现/验证/独立审计已验收关闭；G9学习记忆合同待转交。下面v0.86及全部历史原字节保留。

## G8有限成果关闭与G9规划边界

F01可靠解析已闭合：完整有限肯定形式及受控辅助说明有实际正反离线证据，未知文本收紧数值维度，两个合法不同实例/无曝光/含retest的模型全met反例不能推进，双正确对照可推进。原参考/答案冲突分离、来源资格、原子事实、公开投影、恢复/工作区及最终字节证明按101有效范围成立；全STEP/真实provider/开放评价/长期掌握与其他Must不整体升级。

R03-O01由编排登记DEF019/P2：既有64有效位的极小精度观察非本次回归，不阻断有限交付。后续相关普通修复可保留同单位原Decimal、可靠跨单位比较或精度不足unknown，配定向离线例；不借此重开G8审计/PG/浏览器矩阵。

下一G9为STEP013的唯一最小实施合同，当前仅计划。仍沿FLOW004不可变事实、版本化用户记忆、可重建派生物三层，以及FLOW007逻辑撤销先行/精确清理/不承诺彻底擦除备份。009当前禁止事实直接UPDATE/DELETE且没有获准删除事务，不能用UI隐藏或关触发器冒充实现。

TASK102只读收敛实际表/权限/接口/上下文装配、工作区与修正/撤销/新活动选用/失效传播/恢复/后续退出边界；必要持久或权限变化作为具体合并包待裁，不提前新增表/删除权/运行许可。完整pgvector/面试/HTML/备份/集成/发布仍按各自阶段，既有源码不为设计修改。

原G3/G4/D3/G5/G6/G7与未改G8充分证据直接复用，原FAIL、旧缺版本、合成内容与真实质量限制分层保持。Compose/Linux/Nginx/Git安排继续原交付门，运行预算与进度只由执行动态文档维护。

## 以下为v0.86及更早历史

"""

DECISION100 = """# TASK-100 / R-094 G8有限合同最终验收关闭（2026-10-06，当前）

AT_TOKEN，Codex编排Agent。原独立101 review-03真实返回，三轴在本轮有限范围通过，F01/DEF008闭合、无新增P0/P1或确定回归。接受TASK100已批准G8完整有限合同的实现、验证与保留式交付，验收通过并关闭；不是仅凭实现者回卡，也不签全部STEP、V19真实provider、M-1、部署或项目完成。

306输入身份及审计结果91005c91…/88129字节与交付检查一致，审计旧70370字节历史完整；100结果b4ba337a…/61605字节及旧49113字节历史保持。18方法/81回调/64样本、合法不同实例与正常对照已独立核定；原仓储调用传播B与本地函数A分开，不假称新PG/Windows。

DEF009—018及DEF005限定关闭继承。R03-O01为既有P2精度观察，编排登记DEF019跟踪后续相关普通局部修复，不重开G8、不追加真实验证门。G8原未验证/旧FAIL/缺原件及通用质量范围保留。原公开读取缺字段观察等非阻断项不升级成硬门。

所有100许可结束，修复04测试1/3、离线1.6463436、最终主动1779.265秒及旧初轮/续01/02/修复03次数/费用/未知不清零，名义余额不复活。当前产品/测试/dist/旧证据冻结，结果本次编排零修改，资源历史时点不冒充新查询。

下一TASK102/R096只读记忆合同交原A+业务窗口，不恢复100实现权。新模型/权限/删除/用户库操作须按未来具体合同与批准，不在本次验收自动授权。共享维护及必要事实证据见orchestration-closure-20261006/receipt.json。

## 以下为原裁定及全部历史

"""

DECISION101 = """# TASK-101 / R-095 review-03最终回收并关闭（2026-10-06，当前）

AT_TOKEN，Codex编排Agent。调度已返回，独立审计交付验收通过并关闭；本次代码/证据/控制三轴通过，F01/DEF008闭合，原G8批准有限切片由编排验收关闭，无阻断补审或复跑。

报告91005c918e1ee80fbe34bdfed70e4fa7c60c9fdce813d14a521742d18c858e82/88129字节真实保存，与delivery匹配，原70370字节尾段b75f00d8…保持；306身份当前匹配。先源码初判、再实际原件与作者适用性说明的独立顺序/意外评价接触、对实现报告对象只hash后排除、四个元数据错误及修正版按原审计保留，不改作者原件或按品牌重审。

本轮新业务/资源0；主动最终上界2002.341/3600秒含首读保守600和回传30，元数据保守180/300，局部4.529708/1.539763/0.426514秒及未完整shell开销不混称精确全额。首轮/review02旧投入与未知不重置；所有许可结束，无自动review04或余量外借。

R03-O01为旧精度P2，编排占DEF019非阻断跟踪，不能将其微小边界据18项PASS抹去，也不扩大为本G8新P1。全部既有继承/限制有效，不签完整STEP/真实provider/M-1/项目。

下一TASK102为只读业务记忆合同，交原100业务窗口。本审计窗口不做实现/设计；新的高风险完整G9稳定后按新合同保留必要独立审计，目前未发依赖卡。TASK101原结果及证据零改动。

## 以下为原裁定及全部历史

"""

NOTICE100 = """# TASK-100 / R-094 G8有限成果已验收关闭（2026-10-06，当前）

编排据原101 review-03真实独立三轴结论与稳定证据验收通过并关闭本任务。F01/DEF008已闭合，R03-O01/DEF019既有P2跟踪不重开本任务；未签全部STEP/V19真实provider/M-1或项目。

所有原许可结束，无后续修复04复检或旧真实入口许可；原代码/测试/dist与证据保持。下面完整合同、失败/预算和历史不改，不能借名义余量。100结果及原件本次编排零修改。

原业务窗口如收到新TASK102合同可仅读记忆方案，不恢复本TASK源码写权；后续获准实现须另按具体任务范围。当前没有100在途操作或新增运行许可。

## 以下为已结束的原合同及全部历史

"""

NOTICE101 = """# TASK-101 / R-095 完整独立审计已回收关闭（2026-10-06，当前）

review-03审计交付验收通过，本轮三轴通过，F01/DEF008闭合，G8批准有限切片已由编排验收关闭。既有P2精度观察及原分层/FAIL/未知保留，不签全STEP/真实provider/M-1/部署/项目。

本任务所有只读/显示/元数据许可结束，不自动review04、重跑任何产品或继续写旧证据，不借任何未用余量。原TASK101结果与全部审计历史保持。新业务记忆合同由TASK102执行者承担，本窗口不接管实现。

下面原完整合同与所有历史原字节保留，结束条款不因可读取而恢复权利。未来需要独立审查时以实际新完整合同和稳定高风险成果为前置，目前没有依赖审计卡或开始事实。

## 以下为已结束的原合同及全部历史

"""


def main():
    if (OUT / "delivery-proof.json").exists():
        raise RuntimeError("Closure already registered")
    if (ROOT / "DocuN/tasks/TASK-102.md").exists() or (ROOT / "DocuN/results/TASK-102-result.md").exists():
        raise RuntimeError("Do not overwrite in-flight TASK102")
    before = {}
    for row in load(OUT / "before-manifest.json"):
        data = (ROOT / row["path"]).read_bytes()
        if data != Path(row["backup"]).read_bytes() or sha(data) != row["sha256"]:
            raise RuntimeError("Shared document drift since receipt")
        before[row["path"]] = data
    old_log = before["DocuS/文档变更记录.MD"].decode("utf-8-sig")
    if max(map(int, re.findall(r"CHG-(\d+)", old_log))) != 894:
        raise RuntimeError("CHG allocation changed")
    if any("DEF-019" in before[rel].decode("utf-8-sig") for rel in ("DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD")):
        raise RuntimeError("DEF019 already occupied")
    checks = load(OUT / "identity-checks.json")
    for row in checks:
        if sha(Path(row["path"]).read_bytes()) != row["expected"]:
            raise RuntimeError("Audited object changed")
    receipt = load(OUT / "receipt.json")
    report_paths = {"DocuN/results/TASK-101-result.md": receipt["audit_report_sha256"],
                    "DocuN/results/TASK-100-result.md": receipt["implementation_report_sha256"]}
    for rel, expected in report_paths.items():
        if sha((ROOT / rel).read_bytes()) != expected:
            raise RuntimeError("Accepted report drift")
    card = (OUT / "TASK-102-card.md").read_text(encoding="utf-8")
    headings = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
                "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    if any(f"## {heading}\n" not in card for heading in headings) or "〈" in card or "〉" in card:
        raise RuntimeError("Incomplete seven-section TASK102")
    card_data = md_bytes(card)
    offsets = {}
    offsets["DocuS/执行动态文档.MD"] = prefix("DocuS/执行动态文档.MD", STATE.replace("STATUS_TOKEN", "已登记，卡面准备中，未转交"), before["DocuS/执行动态文档.MD"])
    for rel, text in [
        ("DocuN/results/TASK-100-work-decision.md", DECISION100.replace("AT_TOKEN", AT)),
        ("DocuN/results/TASK-101-work-decision.md", DECISION101.replace("AT_TOKEN", AT)),
        ("DocuN/tasks/TASK-100.md", NOTICE100),
        ("DocuN/tasks/TASK-101.md", NOTICE101),
        ("DocuS/架构动态文档.MD", ARCH),
    ]:
        offsets[rel] = prefix(rel, text, before[rel])
    card_path = ROOT / "DocuN/tasks/TASK-102.md"
    card_path.write_bytes(card_data)
    if card_path.read_bytes() != card_data:
        raise RuntimeError("Full TASK102 card readback differs")
    offsets["DocuS/执行动态文档.MD"] = prefix("DocuS/执行动态文档.MD", STATE.replace("STATUS_TOKEN", "待转交"), before["DocuS/执行动态文档.MD"])
    selected = ["AGENTS.md", "DocuS/最终需求文档.MD", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD",
        "backend/app/activities/teaching_repository.py", "backend/app/activities/repository.py", "backend/app/activities/service.py",
        "backend/app/learning/teaching_service.py", "backend/app/learning/teaching_api.py", "backend/app/learning/teaching_views.py",
        "backend/app/learning/teaching_contracts.py", "backend/app/learning/teaching_evidence.py", "backend/app/learning/teaching_prompt.py",
        "backend/app/learning/teaching_policy.py", "backend/app/learning/teaching_progress.py", "backend/app/learning/service.py", "backend/app/learning/prompt.py",
        "backend/app/materials/repository.py", "backend/app/materials/api.py", "backend/app/storage/originals.py", "backend/app/retrieval/evidence.py",
        "frontend/src/activities/ActivityWorkspace.tsx", "frontend/src/activities/TeachingWorkspace.tsx", "frontend/src/activities/teachingApi.ts",
        "frontend/src/activities/teachingDrafts.ts", "frontend/src/activities/teachingIntents.ts", "frontend/src/activities/TeachingCitations.tsx",
        "DocuN/results/TASK-099-result.md", "DocuN/results/TASK-100-result.md", "DocuN/results/TASK-101-result.md",
        "DocuN/evidence/TASK-101/review-03/R03-O01-precision-observation.md"]
    selected += [str(path.relative_to(ROOT)).replace("\\", "/") for path in sorted((ROOT / "backend/migrations").glob("*.sql"))]
    objects = []
    for rel in selected:
        path = ROOT / rel
        if not path.is_file():
            raise RuntimeError(f"Missing real design input: {rel}")
        data = path.read_bytes()
        objects.append({"path": str(path), "relative_path": rel, "sha256": sha(data), "bytes": len(data)})
    rules = load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
    create_json(ROOT / "DocuN/evidence/TASK-102/input-snapshot.json", {"at": AT, "task": "TASK-102", "R": "R-096",
        "scope": "read-only G9/STEP013 full A-D implementation contract; no product authorization", "objects": objects, "rules": rules,
        "task_card_path": str(card_path), "task_card_sha256": sha(card_data),
        "accepted_parent": "G8/TASK100/TASK101 finite approved contract; no entire STEP/project completion",
        "limits": {"active_seconds": 10800, "metadata_seconds": 600, "official_readonly_pages": 6, "all_product_resource_runs": 0},
        "dispatch": "待转交", "started": False, "unchanged_existing_context_reuse": True})
    create_json(OUT / "DEF-019-source-record.json", {"at": AT, "DEF": "DEF-019", "severity": "P2", "status": "open, nonblocking G8 finite slice",
        "source": "TASK101 review03 R03-O01", "observation_path": str(ROOT / "DocuN/evidence/TASK-101/review-03/R03-O01-precision-observation.md"),
        "source_sha256": sha((ROOT / "DocuN/evidence/TASK-101/review-03/R03-O01-precision-observation.md").read_bytes()),
        "evidence_level": "B static, no newly run counterexample", "root_cause": "Existing same-unit conversion in 64-digit Decimal context rounds 1+1e-65 to1",
        "primary_fix_owner": "MOD006 teaching numeric support policy; future related full implementation, no repair run currently authorized",
        "not_repair04_regression": True, "does_not_reopen_G8": True,
        "future_minimum_validation": "offline same-unit/cross-unit exactness or explicitly unsupported precision unknown; no new PG/browser requirement",
        "shared_status_authority": "DocuS/执行动态文档.MD only"})
    histories, docs = [], []
    for rel, offset in offsets.items():
        data = (ROOT / rel).read_bytes()
        if data[offset:] != before[rel]:
            raise RuntimeError("Historical bytes changed")
        histories.append({"path": rel, "prefix_bytes": offset, "old_bytes": len(before[rel]), "old_sha256": sha(before[rel]), "exact": True})
        docs.append({"path": rel, "sha256": sha(data), "bytes": len(data)})
    for row in checks:
        if sha(Path(row["path"]).read_bytes()) != row["expected"]:
            raise RuntimeError("Stable product or audited input changed during documentation")
    for rel, expected in report_paths.items():
        if sha((ROOT / rel).read_bytes()) != expected:
            raise RuntimeError("Executor result was changed")
    entries = [
        (895, "DocuN/evidence/TASK-101/orchestration-closure-20261006/receipt.json", "真实回收101 review03及306身份，审计交付通过、F01闭合，G8批准有限合同验收通过；旧结果历史原样。"),
        (896, "DocuN/results/TASK-100-work-decision.md", "最终验收关闭TASK100/R094有限G8，原证据/FAIL/预算与未验证范围保持，未签完整项目。"),
        (897, "DocuN/results/TASK-101-work-decision.md", "接受完整独立审计并关闭，2002.341主动/180保守元数据及未知保留，无新增业务运行或review04。"),
        (898, "DocuN/tasks/TASK-100.md", "置顶验收关闭/许可结束通知，原完整合同及旧投入历史保持，新102不恢复100写权。"),
        (899, "DocuN/tasks/TASK-101.md", "置顶完整审计已关闭与所有许可结束，不自动继续补审或借余量，原报告/合同保留。"),
        (900, "DocuS/架构动态文档.MD", "v0.87记录有限G8关闭及精度非阻断边界、G9三层记忆/删除合同规划，不预建模型或删除权。"),
        (901, "DocuS/执行动态文档.MD", "v2.09更新100/101关闭、DEF008闭合/DEF019P2跟踪、009—012有限已验状态与102占号待转交，新预算独立。"),
        (902, "DocuN/tasks/TASK-102.md", "保存完整A-D记忆生命周期与删除一致性合同卡，A+原业务窗口，纯设计/资源0、必要合并包待未来裁定。"),
        (903, "DocuN/evidence/TASK-102/input-snapshot.json", "保存真实当前需求/架构/状态/直接源码/迁移及已验结果输入，规则锁定不变，没读用户私有配置。"),
        (904, "DocuN/evidence/TASK-101/orchestration-closure-20261006/DEF-019-source-record.json", "记录R03-O01既有P2精度问题的来源/主要归属与最小未来离线验证；不将其升级G8新门。"),
        (905, "DocuN/evidence/TASK-101/orchestration-closure-20261006/delivery-proof.json", "保存任务七节/A-D/全文回读、历史/306稳定输入及版本/编号核证，无实际发送/接收/开始。"),
    ]
    for _, rel, _ in entries[:-1]:
        if not (ROOT / rel).is_file():
            raise RuntimeError("Cannot record unsaved document")
    addition = "\r\n\r\n" + "\r\n\r\n".join(f"- CHG-{number:04d}，{AT}，Codex编排Agent，{rel}。{desc}" for number, rel, desc in entries) + "\r\n"
    create_json(OUT / "delivery-proof.json", {"at": AT, "accepted_G8_finite": True, "TASK100": "closed/accepted", "TASK101": "closed/audit accepted",
        "DEF008": "closed", "DEF019": "P2/open/nonblocking", "new_task": "TASK-102/R-096", "dispatch": "待转交", "sent_received_started": False,
        "recipient": "A+ original TASK100 repair04 implementation window", "all_seven_sections": True, "all_A_D_parts": True,
        "new_card_bytes": len(card_data), "new_card_sha256": sha(card_data), "history_exact": histories, "documents": docs,
        "stable_audited_identity_count": len(checks), "design_input_count": len(objects), "rules_count": len(rules),
        "versions": {"state": "2.09", "architecture": "0.87", "requirements": "1.1"}, "CHG": {"first": 895, "last": 905, "next": 906},
        "next_unused": "TASK103/R097, planned only", "CHG_expected_sha256": sha(before["DocuS/文档变更记录.MD"] + addition.encode("utf-8")),
        "both_executor_results_untouched": True, "root_product_writes": 0, "root_business_runs": 0, "design_actual_new_uses": 0,
        "scope_limit": "Not whole STEP/provider/M-1/project approval; G9 design only, no persistence/deletion/run approval"})
    log_path = ROOT / "DocuS/文档变更记录.MD"
    log_path.write_bytes(before["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    actual = log_path.read_bytes()
    if not actual.startswith(before["DocuS/文档变更记录.MD"]) or max(map(int, re.findall(r"CHG-(\d+)", actual.decode("utf-8-sig")))) != 905:
        raise RuntimeError("CHG history or numbering changed")
    print(json.dumps({"G8": "accepted finite slice closed", "TASK100_101": "closed", "DEF008": "closed", "DEF019": "P2 nonblocking tracked",
        "next_card": str(card_path), "card_bytes": len(card_data), "inputs": len(objects), "status": "ready for manual handover",
        "state": "v2.09", "architecture": "v0.87", "CHG": "0895-0905; next0906", "business_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
