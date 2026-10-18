"""验收105设计并保存唯一G10-P待采用包，不授未经确认实施权限。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-105/orchestration-receipt-20261008"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "现有登记保留，不能重复占号或覆盖"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepend(rel, text, old):
    p = ROOT / rel
    assert p.read_bytes() == old, "共享状态出现并行变化"
    prefix = (text.strip() + "\n\n").encode("utf-8")
    assert "*" not in text
    p.write_bytes(prefix + old)
    assert p.read_bytes()[len(prefix):] == old
    return {"path": rel, "old_sha256": sha(old), "new_sha256": sha(p.read_bytes()), "history_exact": True, "prefix_bytes": len(prefix)}


def main():
    receipt = load(OUT / "receipt.json")
    assert receipt["product_runs"] == 0
    current = load(OUT / "current-baseline.json")
    assert len(current) == 308
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report = ROOT / "DocuN/results/TASK-105-result.md"
    assert sha(report.read_bytes()) == receipt["report_sha256"] and len(report.read_bytes()) == 77012
    old = {r["path"]: (OUT / "before" / r["path"]).read_bytes() for r in load(OUT / "before-manifest.json")}
    for rel, data in old.items():
        assert (ROOT / rel).read_bytes() == data
    assert "文档 v2.17" in old["DocuS/执行动态文档.MD"].decode("utf-8")[:300]
    decision_path = ROOT / "DocuN/results/TASK-105-work-decision.md"
    assert not decision_path.exists() and not (ROOT / "DocuN/tasks/TASK-106.md").exists()
    at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    rule_path = "D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4/DocuS/AGENTS.MD"
    decision = f"""# TASK-105 / R-099 设计验收与G10-P采用决定

{at}，Codex编排Agent。105完整A—D文档交付验收通过，设计任务105/R099关闭。实际结果77012字节、SHA-256 c1b192aa05cdab6384b9c3114269c7396ec44022685f1ac7d48edcd03f37483d，46输入、17源码文件73处AST函数/类位置及当前308产品对象一致，22项同一次文档核对/登记名补正可回查。这是设计交付，不是产品/DDL/动态审计。

## 唯一推荐采用包

G10-P推荐采用，当前待用户明确决定，尚未生效。采用对象是原105合同A—D及本裁定普通接口澄清，共同构成下一完整实施的输入；与原合同冲突处按本裁定，原结果不改。

该包一次包括以下实质增量。

- 011新增interview_heads、interview_commands、interview_records三表，五个保护/资格函数，retrolume_interview_owner/app两个NOLOGIN领域角色及最小合成运行能力；旧007正文、009教学事实、010记忆和四账不搬移、不回填。
- interview.v1受信profile、三profile互斥/无工具、同一既有模型配置、原准入/mark/原子结果同事务领域钩子、旧通用/学习/教学对面试域及int10m结果的消费隔离。原worker/协议3/监督/停止/未知预留权威保持。
- start、goal、ask、answer、correct_answer、review、bind_scope、abandon、finish九个封闭动作及六条公开读写路由，目标/回答/范围修正保留不可变历史、CAS/同键同槽/明确launch领取与只读恢复、不自动重发。
- 首版只使用全新且未选择记忆的活动，不把旧学习/教学转域、不复制余额或清掉记忆；不支持面试记忆时确定拒绝，用户界面明确显示，不以背景当引用/独立表现。后续扩记忆消费另有实际受信边界合同。
- 面试工作区、真实引用回查、独立本机intent/draft命名空间和owner/view防迟到保护、分层配置失败关闭。完整资料/目标→问题→答案→必要追问→有依据反馈→显式继续/结束/历史恢复，方向和题数不固定，具体活动仍有有限额度。

用户价值是可纠正、可恢复、有依据的文字模拟面试。代价是新增持久及公开语义、原ledger必须增加同事务hook和领域消费隔离；新增16产品文件/修改11产品文件及1公开配置，未来完整一张实施卡核新增及真实影响，稳定后一次相关风险独立审计。旧未改充分证据继承，不重跑G3—G9全套。

采用权限只覆盖本包的合成实现与相称定向验证，编排随后给精确文件/新合成对象/进程/role/端口/预算。原105 D1建议次数/资源不自行成为运行许可。新领域NOLOGIN与测试runtime的授权只在该未来明确合成范围；不涉及用户库、真实账户/简历/资料、provider/费用/条款、远端外发、安装/锁升级、真实role重配、数据删除/逆迁移、部署/Git或新增工具权限。

## 普通读接口与容量澄清

以下细节由编排在原最小读域内固定，不新增待选方向或用户审批项，保证B5/B7可直接实施。

- history分页仅返回record元数据/版本/资格/抑制原因和opaque引用身份，不夹带模型正文、catalog原文或用户回答全文，SQL本身不取这些正文后删。完整记录只走单record接口；workspace是有界当前head/预算/能力/pending及当前记录投影，不嵌全历史。
- 完整UTF-8 wire编码后workspace上限131072字节，history、单record与citation各65536字节，单次请求及模型value保持原105 B1更小上限；不得用较大读上限扩大模型发送容量。超限413/interview_snapshot_limit、retryable=false，不静默截断正文改变hash；本地合法原文本身不因此重写。
- 若UI需要分开获取当前record详情，响应携带同语句资格派生view_token；前端当前activity/owner/panel/token匹配才采用，失配明确重新只读核对而不是自动POST。同一读SQL的资格/正文要求不放宽，引用仍按105最后资格语句快照的真实截止和前端迟到抑制。
- closed/ended重试按原同键回执确认，不新增effect或再次模型调用；普通新写仍拒绝，abandon/finish不退款/代结算。新表容量/追问深度是安全上限，不是固定面试题数或通过阈值。

## 当前事实、兼容与后续门

原105报告/旧证据/308产品字节未改，011和全部16新生产路径未创建。本轮输入/函数位置核对只是文件解析，不运行compile/test/build/PG/HTTP/Docker/browser/模型。G9/103/104及DEF019—023有限关闭、原O01—03观察保持，本合同没有实现或验收新的面试产品。

105设计许可结束，active4011.714/10800秒、metadata660.136/900，前段300/续作60/人工300为保守项，精确部分和未知保持；官方0/4、所有运行0，patch段落未匹配及登记名修正两项metadata问题留原件。日期从07跨08不清零旧45真实入口/FAIL/R20/UNKNOWN或任何预算，余量不作为实施许可。

采用后下一计划为TASK106/R100完整G10合成实现/接线/定向验证/修复/收尾，沿实际完成105的A+业务窗口。必要新配置/样本/资源和验收在那张卡冻结，不拆表/接口/页面反复转卡；独立审计不由实现者自签。现在106未占号、未出卡、未派发或开始。

## 本次为何需要采用决定

本包新增主要持久模型、公开写接口及受信profile，原G9-P和105只读设计授权没有覆盖该实施边界。依据锁定公共 [AGENTS第2节](<{rule_path}>)，原文为“改变目标、Must、验收标准、锁定架构、主要数据模型、公开接口、重大费用、数据外发或许可证义务，先形成具体影响、替代与代价说明，再处理缺少的决定。”

原最终需求FR011/012的采用继续有效；此处只需对上述具体G10-P实施包一次决定，不重新批准文字面试需求，不逐字段/配置重复问。推荐批准；未收到明确决定前只保留计划，不实施三表/profile/路由或启动运行。
"""
    assert "*" not in decision
    decision_path.write_text(decision.strip() + "\n", encoding="utf-8")
    save("adoption-package.json", {"at": at, "package": "G10-P", "status": "recommended_pending_user_adoption",
        "source_contract": str(report), "source_contract_sha256": receipt["report_sha256"],
        "work_decision": str(decision_path), "work_decision_sha256": sha(decision_path.read_bytes()),
        "includes": ["011三表/五函数/两NOLOGIN角色与合成最小能力", "受信interview.v1/无工具/原子结果hook/消费隔离",
            "九动作六路由/修正历史/CAS与只读恢复", "全新无记忆活动首版边界", "工作区/独立intent与draft/分层配置"],
        "fixed_read_limits": {"workspace_bytes": 131072, "history_record_citation_bytes": 65536, "history_body": False},
        "excludes": "真实用户库/账号数据/简历/provider/付费/外发/安装/删除/部署/Git/工具新权",
        "user_adoption_received": False, "implementation_authorized": False, "TASK106": "未来计划未占号/未出卡"})
    save("contract-review.json", {"at": at, "TASK": "TASK-105", "R": "R-099", "design_delivery": "验收通过，设计任务关闭",
        "coverage": "A-D完整；九动作/三表/五函数/六路由/锁序提交点/源目标重新绑定/同键重试/权限回滚/无记忆/profile隔离/24未来用例/5非运行轨迹可对应",
        "actual_source_basis": "46输入和73函数/类位置复核；SourceSnapshot.revision映射、operation→head锁次序、OneCall参数和007事务挂钩位置存在",
        "clarification": "普通读DTO元数据投影/完整wire容量/同快照view绑定已具体化，不追加审批子项或提前测试",
        "new_runtime": 0, "future_G10_validation": "未实施/未验证，矩阵不冒实测，必要采用仍待用户"})
    save("authorization-and-route.json", {"at": at, "authorized_complete": "本地只读设计交付与编排核证/共享文档维护",
        "missing_only": "新G10-P包采用，因主要模型/公开接口/受信profile实质增量",
        "rule_source": rule_path, "rule_section": "2 授权、角色与修改边界",
        "possible_next": "采用后106/R100一个完整实施卡及稳定点相关风险独立审计，前置未满足不出执行卡",
        "no_reset": "105/45旧入口/历史失败/未知/费用/时间封闭保留，所有名义余量不授实施"})
    save("window-release.json", {"at": at, "TASK105": "设计验收关闭", "window": "原103/105 A+业务窗口，等待必要采用决定",
        "TASK104": "已独立终审关闭，保留未来独立性", "in_flight_new_business": False, "actual_new_dispatch": False})
    state_prefix = """# 执行动态文档

文档 v2.18，2026-10-08，Asia/Shanghai。唯一总状态账；需求v1.1、架构v0.96，task_model/阶段07。下面v2.17及全部历史原字节保留。

## TASK105设计验收关闭；G10-P待一次采用

105/R099已实际返回。77012字节/c1b192aa…与文档核对及session一致，46输入/17源码文件73处AST位置可回查，当前308产品字节未改变，011/16新增生产路径未创建。A-D完整，22项一次文档一致性核对含同次登记名补正，不是22程序测试。编排验收设计交付通过，关闭105/R099；不把文档通过当面试实现/动态/独立终审通过。

唯一推荐G10-P待用户明确采用：三表/011/五保护或资格函数/两NOLOGIN领域角色及合成最小能力，interview.v1受信carrier/原四账及007同事务hook/跨profile消费隔离，九封闭动作六路由，目标/答/范围修正保不可变历史/CAS/只读恢复，无记忆全新活动首版，完整工作区/独立本机意图/引用/分层配置。具体包见105-work-decision及原105合同A-D，新生产16/改11/公开配置1。

资料/目标→问题→答案→必要追问→有据反馈/显式继续/结束/历史恢复完整承接FR011/012，方向/题数不固定，有限预算/存储/追问深度可辨。自报经历/测量不提升事实，reference用途不背书来源真实性，语义建议与位置验证分别呈现，正确片段和证据缺口并列。首版面试不支持G9已选择活动，明确拒绝而非清记忆/通用profile降级；没有改或删原Must。

主控普通接口澄清已固化：history只有元数据不读取或传正文/catalog/答案全文，workspace有界当前投影，单record取全文且同快照资格；workspace完整wire≤131072、history/record/citation≤65536，超限明确413/interview_snapshot_limit不静默截断；不扩大模型/命令原更小容量。view/owner/panel及原键绑定，关闭同键只确认不重发，不为这些常规细节单独问用户。

原105设计许可结束，active4011.714/10800、metadata660.136/900，其中300/60/300保守段和精确/未知保留，官方0/4；原45真实入口/FAIL/R20/UNKNOWN及所有历史账不清零。patch未匹配和函数登记名两项metadata失误已补正，产品FAIL新增0，产品/compile/test/build/PG/SQL/HTTP/app/Docker/browser/Windows/SUP/模型/工具/安装/费用/Git新运行0。

采用关口来自锁定公共AGENTS第2节的主要数据模型/公开接口/权限实质变化要求。原FR011/012需求已批准，G9-P和105只读许可不覆盖011/新领域/profile/新写路由；故只对具体G10-P一次决定，不重复需求批准。未收到决定前状态recommended_pending_user_adoption，implementation_authorized=false，无真实用户库/provider/角色/付费/外发/删除/部署/Git写权。

后续TASK106/R100仍未来计划未占号/未出卡/未派发，采用后才给一张完整合成实现/接线/定向验证/修复/收尾卡，沿实际105的A+业务窗口；105 D1资源/32调用等只是建议，不是现成运行许可证。新预算/精确对象/样本/配置未来卡冻结，完整稳定点一次相关风险独立审计，104保持独立，不按表/接口/页面拆卡。

G9/103/104/DEF023/F01/E01仍有限关闭，DEF019—022有限域和O01—03非阻断观察保持；完整Must/真实provider/向量/长期质量/M-1/项目未通过。STEP014仅设计已交付、G10尚未实施；STEP015/016 HTML、017退出恢复、018整链Compose/Linux/Nginx、019风险独立验收、020本人自用交接等按原需求继续，规则/归档/原始需求不改。本次编排产品/测试/资源运行0。

本批CHG0985—0994，下一CHG0995。当前必要用户决定仅采用G10-P具体包；106/R100未占号。已有报告/字节/有效检查保留，无新在途执行者。

## 以下为v2.17及更早历史
"""
    arch_prefix = """# 架构动态文档

文档 v0.96，2026-10-08，Asia/Shanghai。需求v1.1、唯一执行动态v2.18。G10文字面试A-D设计已验收交付，G10-P推荐待用户采用；未实施011/新profile/新接口。下面v0.95及全部历史原字节保留。

## 文字面试唯一候选边界

采用建议为独立interview.v1领域和工作区，三表heads/commands/records与五个保护/资格函数、NOLOGIN owner/app及最小能力；原007 model正文及四账共用，009教学状态/掌握和010记忆不混入。九动作/六路由、版本/CAS/原子结果/域隔离、显式launch/未知不重发、源/答/目标修正及历史抑制均给出完整合同，不另造监督或预算平台。

首版全新无记忆活动，材料角色/用户陈述/位置/语义建议分层，不把自报或reference标签升级成验证事实。异步工作区与本机先存/原键恢复、owner/view/引用晚到保护和分层能力关闭同一成果接线。普通历史读只元数据，当前投影及详情wire容量由105-work-decision固定，模型发送原限不扩大。

三表/新公开写/受信profile是真实主要模型和接口增量，具体G10-P待采用；当前只是完整建议，16新增/11修改产品及1例子未实施，D矩阵/手工轨迹不冒实测。采用后同一完整实施卡连续实现/验证/修复/收尾，稳定点一次相关风险独立审计；旧未改G3—G9充分证据继承。

当前G9有限验收与旧角色/预算/worker/停止/事实/无退款边界保持，105设计0产品运行。用户库/provider/付费/外部简历/工具新权/数据删除/逆迁移/生产部署/Git均非本包默认许可。面试记忆消费扩展、HTML/退出/整链与其他Must仍按已批准路线，不以设计放行。

## 以下为v0.95及更早历史
"""
    saved = []
    saved.append(prepend("DocuS/执行动态文档.MD", state_prefix, old["DocuS/执行动态文档.MD"]))
    saved.append(prepend("DocuS/架构动态文档.MD", arch_prefix, old["DocuS/架构动态文档.MD"]))
    rules = load(ROOT / "DocuN/evidence/TASK-105/orchestration-setup-20261007/design-input.json")["rules_contracts"]
    for row in rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    changes = [
        (985, "DocuN/evidence/TASK-105/orchestration-receipt-20261008/receipt.json", "真实回收77012设计/46输入/73位置/308产品不变，22文档核对非测试，新16路径未创建"),
        (986, "DocuN/results/TASK-105-work-decision.md", "设计验收关闭/唯一G10-P具体采用包/普通读DTO与wire界限/明确批准来源，尚未采用不授实施"),
        (987, "DocuS/架构动态文档.MD", "v0.96登记独立interview.v1三表/原子hook/域隔离/工作区唯一建议，原G9和监督主权保持"),
        (988, "DocuS/执行动态文档.MD", "v2.18登记105真实返回/设计闭账/采用待决定/106仍计划，所有运行0和旧失败保留"),
        (989, "DocuN/evidence/TASK-105/orchestration-receipt-20261008/adoption-package.json", "具体五类G10-P及普通读限制、明确不含用户库/真实费用/外发/删除/部署，新采用尚未生效"),
        (990, "DocuN/evidence/TASK-105/orchestration-receipt-20261008/function-position-checks.json", "17真实源文件73处AST位置复核，非产品导入/执行，避免依据错误接口发实施卡"),
        (991, "DocuN/evidence/TASK-105/orchestration-receipt-20261008/contract-review.json", "A-D/状态动作/事务hash/语义层级/兼容/矩阵文档核证与普通接口澄清，不追加前置运行"),
        (992, "DocuN/evidence/TASK-105/orchestration-receipt-20261008/authorization-and-route.json", "实际缺失仅新包采用，锁定AGENTS2引用/106前置，旧余额和建议次数不授执行"),
        (993, "DocuN/evidence/TASK-105/orchestration-receipt-20261008/window-release.json", "105原业务窗口设计完成待采用，104独立保留，无新派发或业务在途"),
        (994, "DocuN/evidence/TASK-105/orchestration-receipt-20261008/delivery-proof.json", "回读采用包/版本CHG/原字节历史/报告与308不变/未创建106，产品运行0")
    ]
    log = ROOT / "DocuS/文档变更记录.MD"
    assert log.read_bytes() == old["DocuS/文档变更记录.MD"]
    addition = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{at}，Codex编排Agent，{p}。{d}。" for n, p, d in changes) + "\n"
    log.write_bytes(old["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    assert log.read_bytes().startswith(old["DocuS/文档变更记录.MD"])
    assert sha(report.read_bytes()) == receipt["report_sha256"] and report.read_bytes() == (OUT / "TASK-105-as-returned.md").read_bytes()
    assert (ROOT / "DocuN/tasks/TASK-105.md").read_bytes() == old["DocuN/tasks/TASK-105.md"]
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    assert not (ROOT / "DocuN/tasks/TASK-106.md").exists()
    save("delivery-proof.json", {"at": at, "TASK": "TASK-105", "R": "R-099", "acceptance": "设计验收通过，任务关闭",
        "G10_P": "推荐待用户采用，未授权实施", "versions": {"state": "v2.18", "architecture": "v0.96"},
        "CHG": "0985—0994", "next_CHG": "0995", "TASK106_R100": "未来计划未占号/未出卡",
        "report_77012_original_unchanged": True, "task105_original_unchanged": True, "current308_unchanged": True,
        "histories": saved, "change_history_preserved": True, "rule_contracts_unchanged": True,
        "decision_readback": decision_path.read_text(encoding="utf-8") == decision.strip() + "\n",
        "managed_new_markdown_no_asterisks_or_tables": True, "new_user_approval_received": False,
        "root_product_SQL_test_build_start": 0, "pending_only": "具体G10-P一次采用决定"})
    print(json.dumps({"TASK105": "设计验收关闭", "G10_P": "待用户采用", "state": "v2.18", "architecture": "v0.96",
        "CHG": "0985—0994", "current308_unchanged": True, "product_runs": 0, "TASK106_created": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
