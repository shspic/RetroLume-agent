"""Register accepted design and one pending adoption package; no product execution."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-102/orchestration-receipt-01"
AT = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fresh_json(path, value):
    if path.exists():
        raise RuntimeError("Do not overwrite an existing decision or receipt")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def markdown(text):
    data = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    if b"*" in data or re.search(rb"(?m)^\|", data):
        raise RuntimeError("New managed Markdown formatting violation")
    return data


def prefix(rel, text, before):
    added = markdown(text)
    (ROOT / rel).write_bytes(added + before)
    return len(added)


STATE = """# 执行动态文档

文档 v2.10，2026-10-06，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.88，task_model/阶段07。下面v2.09及全部历史原字节保留。

## TASK102完整设计验收关闭；G9-P一次采用决定

102/R096调度已返回，完整A—D实施合同的文档交付验收通过，设计任务关闭。结果82360字节/SHA f3bf109c…与最终final_document_binding一致，59项实际指纹和26处函数/签名定位与当前相符。首次七表regex漏复数名称的false及纠正、初检旧hash0ea56869…保持原件；有效文档检查16/16，不是程序测试或DDL验证。

实际接收者为102回报的Codex desktop/GPT-6文件承接窗口，不能证明为原100同聊天；用户实际转卡形成接收事实，记录这个限制，不回填同窗、不可续原因或重审品牌。未来相关实施优先实际102窗口，不占101独立窗口。

G9-P推荐采用、待用户一次明确批准，尚未生效。它新增010七表、版本化记忆/固定活动选择、教学v2 recipe/profile与全链资格、受控正文精确清理函数/最小NOLOGIN角色、实际工作区和24组受影响合成验收。主要代价是任何所选记忆/依赖失效便停用该活动全部派生成果，继续需新活动明确重选；原始答/目标/纠错历史保留。不将“选择背景”当新的证据或独立作答。

具体包及固定普通接口边界保存于DocuN/results/TASK-102-work-decision.md，主控补明MemoryPage只返元数据/有资格短标题，正文/完整依赖另走受控详情、真实wire响应≤65536字节；同连接前缀锁、旧v1字节/预算/UNKNOWN/关门结算/停止权威不改。没有原结果重写或增加新用户选择。

包外为用户库迁移/真实role重配或用户真实删除、007/教学事实/资料/PDF/原件/WAL/备份物理清理、真实provider/付费/密钥、部署/Git/网络新权限/安装及面试/HTML/完整向量工程。本包删除仅在线本条记忆正文，元数据墓碑和保留副本界限明确，原source/事实FK目标真实存在，不通过关009触发器获得删除权。

编排已按真实源/函数核接线与关键风险，必要四页官方PG16公开手册支持函数权限/可信search_path、锁序、单语句快照与核心hash事实；不证明本机版本、实际登录role/拥有者/权限、新SQL或新产品行为。下一合成卡必须核并实测相应前提，缺失失败关闭，不偷偷扩权或安装扩展。当前只完成设计，G9/STEP013/M-1/项目尚未通过。

102设计许可结束：主动3122/10800秒是连续墙钟与首读120/封装回复60的保守口径，不称精确全量单调；元数据保守300/600，已知工具10.9571447为局部口径，未知及三次路径错误/一次辅助计数修正保留。官方4/6页、全部产品/DDL/测试/PG/HTTP/Windows/Docker/浏览器/模型工具/付费/安装/Git运行0。剩余设计时间不恢复实施许可，不借旧100/101投入或余额。

TASK103/R097仍仅批准后的一张完整实施计划，未占号、未存已授权执行卡、未实际发送/接收/启动。采用后才给具体文件/合成库角色/资源与新预算，卡内连续实现、定向验证及必要普通修复；稳定完整G9保留一次隔离增强审计，未先派依赖审计卡。当前没有其他在途执行任务。

G8批准有限切片/100/101仍验收关闭，DEF008及其他已闭根因保持；DEF019/P2非阻断跟踪可在后续相关完整实施明确范围合并，不重开G8，不自动加新PG/浏览器门。原DEF001/002及097旧runner禁用、全部旧FAIL/漏时/未知/历史资源时点、四旧根归档、公共锁定与原始需求保持。根目录和产品/配置/旧证据本次编排零改动，仅必要读取/公开文档核证与共享文档维护。

STEP014面试、015/016 HTML、017数据退出、018集成Compose/Linux/Nginx、019权限验收、020自用交接和真实provider/完整检索仍沿已批准阶段，不借本设计放行。Git仅既有一次首提交授权，不自动新commit/push。

本批CHG0906—0913，下一CHG0914；下一新TASK103/R097尚未占号。唯一人工决定为采用或不采用具体G9-P；原因是102只读合同未授权这些持久/权限/活动语义实施变化，不需要逐表或逐字段重复批准。

## 以下为v2.09及更早历史

"""

ARCH = """# 架构动态文档

文档 v0.88，2026-10-06，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.10。TASK102完整设计验收通过，G9-P候选待用户一次采用决定，产品未实施。下面v0.87及全部历史原字节保留。

## G9最小持久记忆候选与采用边界

候选使用七表分开头、不可变版本身份、可精确清理正文、依赖、幂等收据和活动选择头/项；追加修正/CAS、固定选用版本、单语句可读/可消费资格、来源/事件/上游失效及全活动派生抑制，保持原作答/事实不覆盖。记忆只作低信任背景，不作新的引用通道或本活动独立表现。

教学v2候选持久recipe/身份/消息摘要而不复制记忆正文，既有v1序列化兼容。来源→记忆→相关活动→操作/教学对象→记忆收据的锁前缀在第一活动锁前、同连接内接入；接受/launch/admit/mark/结果提交和所有公开读/重建均复核资格。旧取消/关门/结算/UNKNOWN/停止与四账主权不改。

撤销先提交墓碑/原清单/收据，随后唯一受限清理函数只删除本条在线记忆正文。NOLOGIN拥有者/清理者/app权限分离、撤PUBLIC执行、可信search_path与精确PK/hash/bytes校验是未来实现合同，未据公开PG文档宣称实际数据库已具备权限。原事实、007、原件、备份或已外发字节不包含在此清理。

实际记忆工作区、独立草稿/意图、分层配置及24组未来验收已完整提出。MemoryPage补定元数据与有资格短标题投影，完整正文/依赖只走详情，response wire≤65536；不传全部正文再应用裁剪。来源资格/删除影响/复建不复活及旧v1证明按实际受影响变化验证，不从零再测全G8。

G9-P仍候选，必要七表/清理权限/活动级失效等只读102范围外实施须有一次具体采用决定及后续完整卡；未创建010/新role、未迁移或运行产品。完整跨备份恢复/原事实退出属于STEP017，真实provider/tokenizer/模型容量、面试/HTML/向量/部署及其他Must继续原门。

G8已验有限结论及DEF019旧精度P2边界、原FAIL/缺原件/合成与真实质量限制保持。总状态、采用与预算只由执行动态文档维护。

## 以下为v0.87及更早历史

"""

NOTICE = """# TASK-102 / R-096 完整设计已返回验收关闭（2026-10-06，当前）

A—D文档交付已由编排验收通过，原结果82360字节/f3bf109c…保持，产品/DDL/权限与G9未实施未验收。G9-P推荐待用户一次采用决定，本任务的只读许可结束，剩余不能执行迁移、编码、用户删除或启动资源。

包及常规接口澄清见DocuN/results/TASK-102-work-decision.md；原完整合同与所有预算原字节保留。后续采用后才收到TASK103完整合成实施卡，优先实际TASK102执行窗口，不据原100同窗未证事实改写路由，不自行继续或代独立审计。

所有旧G8/100/101验收和历史限制保持。当前没有本任务在途执行或新增运行许可，本通知不追认尚未发生的G9-P批准。

## 以下为已结束的原合同

"""


def main():
    if (OUT / "delivery-proof.json").exists():
        raise RuntimeError("Already registered")
    decision_path = ROOT / "DocuN/results/TASK-102-work-decision.md"
    if decision_path.exists():
        raise RuntimeError("A decision already exists; read it rather than overwrite")
    before = {}
    for row in load(OUT / "before-manifest.json"):
        data = (ROOT / row["path"]).read_bytes()
        if data != Path(row["backup"]).read_bytes() or sha(data) != row["sha256"]:
            raise RuntimeError("Shared baseline changed")
        before[row["path"]] = data
    if max(map(int, re.findall(r"CHG-(\d+)", before["DocuS/文档变更记录.MD"].decode("utf-8-sig")))) != 905:
        raise RuntimeError("CHG allocation changed")
    checks = load(OUT / "identity-checks.json")
    for row in checks:
        if sha(Path(row["path"]).read_bytes()) != row["expected"]:
            raise RuntimeError("Design input changed")
    receipt = load(OUT / "receipt.json")
    report_path = ROOT / "DocuN/results/TASK-102-result.md"
    if sha(report_path.read_bytes()) != receipt["report_sha256"]:
        raise RuntimeError("Design result changed")
    decision_data = markdown((OUT / "G9-P-work-decision-prepared.md").read_text(encoding="utf-8"))
    decision_path.write_bytes(decision_data)
    offsets = {}
    for rel, text in [("DocuN/tasks/TASK-102.md", NOTICE), ("DocuS/架构动态文档.MD", ARCH), ("DocuS/执行动态文档.MD", STATE)]:
        offsets[rel] = prefix(rel, text, before[rel])
    mutable_context = {str((ROOT / rel).resolve()).casefold() for rel in offsets}
    stable = [row for row in checks if str(Path(row["path"]).resolve()).casefold() not in mutable_context]
    for row in stable:
        if sha(Path(row["path"]).read_bytes()) != row["expected"]:
            raise RuntimeError("Product/rule/parent source drift during document registration")
    if sha(report_path.read_bytes()) != receipt["report_sha256"]:
        raise RuntimeError("Author result was changed")
    histories, docs = [], []
    for rel, offset in offsets.items():
        data = (ROOT / rel).read_bytes()
        if data[offset:] != before[rel]:
            raise RuntimeError("Historical bytes changed")
        histories.append({"path": rel, "prefix_bytes": offset, "old_bytes": len(before[rel]), "old_sha256": sha(before[rel]), "exact": True})
        docs.append({"path": rel, "sha256": sha(data), "bytes": len(data)})
    fresh_json(OUT / "package-review.json", {"at": AT, "TASK": "TASK-102", "R": "R-096", "package": "G9-P",
        "document_acceptance": "passed, closed", "package_status": "pending one explicit adoption decision",
        "request_scope": "seven tables / versioned memory / fixed activity selection / v2 identity and qualification / precise online memory body cleanup / real workspace / bounded synthetic implementation",
        "principal_tradeoff": "Any selected memory/dependency invalidation suppresses that activity's derived results; new activity explicitly reselects; original user facts retained",
        "ordinary_clarifications": ["Metadata-only paged list with qualified short title; body/closure on bounded detail, <=65536 wire bytes", "New memory prefix before first activity lock on same connection", "Keep original v1 and budgets/UNKNOWN/close/settle/stop authority", "Database roles/version tested later, no official document equals actual permission proof"],
        "excluded": ["user DB migration", "real role reconfiguration", "real user deletion", "original materials/answers/007/teaching data/WAL/backups purge", "provider credentials or paid calls", "deployment/Git/install/new external permission"],
        "approval_source": str(ROOT / "DocuN/tasks/TASK-102.md"), "approval_reason": "Original contract authorizes read-only delivery only; new persistent model, deletion authority and activity semantics need a concrete adoption decision",
        "adoption_already_received": False, "next_task": "TASK103/R097 planned only, not occupied or dispatched",
        "next_actual_window": "actual TASK102 A+ design window, original TASK100 same-chat not proven", "no_product_or_resource_operations": True})
    entries = [
        (906, "DocuN/evidence/TASK-102/orchestration-receipt-01/receipt.json", "真实回收102完整A-D，59指纹/26函数定位核证，原结果和首次文档false保留；设计交付通过，G9-P待一次采用。"),
        (907, "DocuN/results/TASK-102-work-decision.md", "保存具体合并包推荐/代价/包外和固定列表投影等普通边界，解释只读合同未授实施，未登记用户批准。"),
        (908, "DocuN/tasks/TASK-102.md", "置顶设计已返回/验收关闭/许可结束，原完整卡与预算字节保留，不恢复代码/迁移/删除权限。"),
        (909, "DocuS/架构动态文档.MD", "v0.88记录七表/版本/固定选择/v2/全链资格与精确正文清理候选及未采边界，不预建结构/权限。"),
        (910, "DocuS/执行动态文档.MD", "v2.10登记102设计关闭、G9-P待用户采用、原投入3122墙钟保守/300元数据及未知、103未来未占号，G8等保持关闭。"),
        (911, "DocuN/evidence/TASK-102/orchestration-receipt-01/source-verification.json", "记录真实旧复合FK/锁及adapter接点，四页官方PG16事实和实际版本/权限尚未验证的分层。"),
        (912, "DocuN/evidence/TASK-102/orchestration-receipt-01/package-review.json", "保存一个具体待采用包、明确活动级失效代价/合成边界和审批依据；无已收到决定或实际派卡事实。"),
        (913, "DocuN/evidence/TASK-102/orchestration-receipt-01/delivery-proof.json", "保存裁定回读、历史/56未变输入/原结果及版本/编号核证，设计通过不等于G9实现授权。"),
    ]
    for _, rel, _ in entries[:-1]:
        if not (ROOT / rel).is_file():
            raise RuntimeError("Cannot record an unsaved actual artifact")
    addition = "\r\n\r\n" + "\r\n\r\n".join(f"- CHG-{number:04d}，{AT}，Codex编排Agent，{rel}。{description}" for number, rel, description in entries) + "\r\n"
    fresh_json(OUT / "delivery-proof.json", {"at": AT, "TASK": "TASK-102", "R": "R-096", "dispatch": "returned", "acceptance": "document passed/closed",
        "G9-P": "pending explicit adoption", "user_decision_received": False, "TASK103_R097": "planned only; no card or execution",
        "result_untouched": True, "result_sha256": receipt["report_sha256"], "decision_saved_readable": decision_path.is_file(), "decision_sha256": sha(decision_path.read_bytes()),
        "initial_inputs_verified": len(checks), "stable_inputs_after_registration": len(stable), "history_exact": histories, "documents": docs,
        "versions": {"state": "2.10", "architecture": "0.88", "requirements": "1.1"}, "CHG": {"first": 906, "last": 913, "next": 914},
        "CHG_expected_sha256": sha(before["DocuS/文档变更记录.MD"] + addition.encode("utf-8")), "root_product_writes": 0, "root_business_runs": 0,
        "permission_question_source": "TASK102 read-only contract + concrete G9-P persistent/cleanup/activity changes", "published_runtime_authorization": False})
    log_path = ROOT / "DocuS/文档变更记录.MD"
    log_path.write_bytes(before["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    actual_log = log_path.read_bytes()
    if not actual_log.startswith(before["DocuS/文档变更记录.MD"]) or max(map(int, re.findall(r"CHG-(\d+)", actual_log.decode("utf-8-sig")))) != 913:
        raise RuntimeError("CHG original history or final numbering mismatch")
    print(json.dumps({"document": "TASK102 A-D accepted/closed", "G9-P": "pending one adoption decision", "decision": str(decision_path),
        "state": "v2.10", "architecture": "v0.88", "stable_inputs": len(stable), "CHG": "0906-0913; next0914", "product_or_business_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
