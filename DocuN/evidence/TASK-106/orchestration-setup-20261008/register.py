"""登记用户采用及106完整实施许可，不创建或运行业务资源。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-106/orchestration-setup-20261008"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "保留现有登记，不重复派卡"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepend(rel, text, old):
    p = ROOT / rel
    assert p.read_bytes() == old, "共享文档并行变化，不能覆盖"
    prefix = (text.strip() + "\n\n").encode("utf-8")
    assert "*" not in text
    p.write_bytes(prefix + old)
    assert p.read_bytes()[len(prefix):] == old
    return {"path": rel, "old_sha256": sha(old), "new_sha256": sha(p.read_bytes()), "prefix_bytes": len(prefix), "history_exact": True}


def main():
    adoption = load(OUT / "adoption-received.json")
    assert adoption["status"] == "approved" and adoption["user_message"] == "批准"
    baseline = load(OUT / "baseline-input.json")
    current = baseline["current_files"]
    assert len(current) == 308
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report = ROOT / "DocuN/results/TASK-105-result.md"
    assert sha(report.read_bytes()) == adoption["source_contract_sha256"]
    old = {r["path"]: (OUT / "before" / r["path"]).read_bytes() for r in load(OUT / "before-manifest.json")}
    for rel, data in old.items():
        assert (ROOT / rel).read_bytes() == data
    assert "文档 v2.18" in old["DocuS/执行动态文档.MD"].decode("utf-8")[:300]
    task = ROOT / "DocuN/tasks/TASK-106.md"
    assert not task.exists() and not (ROOT / "DocuN/results/TASK-106-result.md").exists()
    preflight = load(OUT / "resource-preflight.json")
    assert preflight["image"]["available"] and not preflight["matching_existing_container_names"]
    assert not preflight["matching_existing_volume_names"] and not preflight["listeners"]
    at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    decision_prefix = f"""# G10-P用户采用批准生效；TASK106完整实施

{at}，Codex编排Agent。用户2026-10-08对上一条具体G10-P合成实现与定向验证采用请求明确回复“批准”，包采用生效；消息具体时刻未提供，不回填。批准来源和原合同SHA见106/orchestration-setup-20261008/adoption-received.json。原105设计验收关闭、原77012结果不改，以下推荐待批准文字均为历史。

采用范围为原105 A—D及本work-decision普通读DTO/wire/恢复澄清，三表/011/五函数/两NOLOGIN领域角色与新合成最小能力、无工具interview.v1/原子结果hook/消费隔离、九动作六路由、无记忆全新活动首版、修正历史与工作区/本机意图/分层配置。用户真实库/资料/账户/provider/费用/安装/外发/删除/逆迁移/部署/Git/工具新权不在采用内，旧事实/停止/UNKNOWN/R20保持。

已组织TASK106/R100完整合成实现/接线/定向验证/修复/收尾，原实际完成105的A+业务窗口，卡全文回读后待转交，当前新使用0、无实际发送/接收/开始。具体白名单、隔离cluster/角色/端口/动作上限和最终报告见106卡；105 D1建议次数不自行成为新许可。

新许可TASK-106-G10-20261008，active28800、offline/build1800、real7200、独立cleanup900、metadata1800秒；root16/start18/listener8/SUP48/transport48/browser-driver4/offline6/build3、compile1+有据复检1、新container-volume3。每类含失败和未知，旧45根/预算不清零或借用。同因两次有据修正仍败停受影响，不以总上限无限试。

仅新retrolume-task-106-g10-pg1/2/3及同名-data、主/upgrade/fault cluster，缓存镜像cf134a76…、1CPU/512MiB/pids128/restart=no/loopback55446—55448、API18106/fake18107。主控仅核镜像、名称/卷/端口和308当前源均可用，未创建/启动/连SQL或读Env。原103/100/088资源保留不启；普通runtime权限与bootstrap分离，role/口令只本卡新隔离范围。

现在包批准不需再次问采用/继续，普通实现细节和相称修复同卡完成；新主要模型/受信消费/保护平台或真实用户权必需仍交具体差异。稳定候选后才计划107/R101集中独立风险审计，不预发依赖审计卡，不自签G10/STEP/M-1/项目通过。

## 以下为105设计验收及待采用历史
"""
    state_prefix = """# 执行动态文档

文档 v2.19，2026-10-08，Asia/Shanghai。唯一总状态账；需求v1.1、架构v0.97，task_model/阶段07。下面v2.18及全部历史原字节保留。

## G10-P已获采用；TASK106完整实施待转交

用户对上一条具体G10-P合成实现与定向验证请求明确“批准”，采用生效。原10577012字节/c1b192aa…和旧work-decision澄清共同为批准输入，具体消息时刻未提供不回填；原待批准条目为历史，不再询问采用或重批FR011/012。105设计验收关闭保持，尚无面试产品实现/动态通过。

本包三表/011/五保护函数/两个NOLOGIN领域角色与合成最小权限、无工具interview.v1/007同事务hook/跨profile消费隔离、九动作六路由/目标答范围修正/只读恢复、无记忆全新活动首版、工作区/本机意图/配置及原读DTO/wire上限已采用。真实用户库/角色/简历/provider/费用/外发/安装/删除/逆迁移/部署/Git/工具新权继续未授权，不借新包更改旧监督/停止/退款权威。

TASK106/R100已占号，沿原实际105/103业务窗口A+強推理，完整七节实现/接线/相关验证/普通修复/收尾卡已保存回读，调度待转交，新使用0，无实际发送/接收/开始。新增16产品及11直接原文件/1公开例子范围按105，必要中性activities/__init__最小导出允许但不扩服务依赖；测试/fixture/dist仅实际本包/受影响签名，旧业务断言不弱化。保护001—010/worker/协议3/Job/记忆/其他既定模块/锁/正式DocuS/用户配置/旧证据保持。

前置核证308存续对象与合同/规则SHA无漂移，011/新interview代码未创建；缓存镜像cf134a76…可用，三新container/volume名称无碰撞，18106/18107/55446—55448无监听，venv/vite/playwright和Chromium缓存存在。主控仅read/hash/元数据inspect，没有新业务创建/PG连接/测试/构建/模型或Env读取；观察时点不替代执行前重核。

新许可TASK-106-G10-20261008，active28800秒、offline/build1800、real7200、独立cleanup900、metadata1800；root16（各≤900）、container start18、app/fake listener8、native SUP48/最低transport发送48分别计、browser-driver各4、offline6（各≤180）、build3（各≤300）、compile内存初批1+有据复检1，新container/volume各3。预期核心真实组合和最终UI两组，普通有据复验同卡；同根因两次修正仍失败停受影响，失败/BLOCKED/未知前计数不返额，不以“上限大”盲试。

隔离新pg1/2/3为retrolume-task-106-g10-pg1/2/3与同名-data，主/旧非空升级/坏schema与故障分别独立cluster；数据库retrolume_task106_main/upgrade/fault，固定镜像pull=never、1CPU/512MiB/pids128/restart=no、唯一声明命名卷/无host bind/cap/特权/公开监听，loopback55446—55448。API/最终dist18106、必要fake最低provider18107；创建后冻结CID/标签/配额，不按名字盲操，最多一个PG运行。

每cluster admin仅bootstrap合成准备/受控故障，普通runtime retrolume_task106_app/denied与NOLOGIN interview角色分权，权限/指纹真实比对；随机secret只RAM/stdin/Env，绝不回退用户DSN/私配或泄argv/日志。所有数据/容器/卷/role/profile保留停止，旧103/100/088不启不删。缺/坏schema采用新坏基线或回滚故障，实际DROP/DELETE/逆迁移未授权；011旧非空行与权限不无关回填。

实现前先一次核完整类/签名/字段/FK/不可变/配置/原子/类型/OneCall容量和runtime前置，禁止到每首根才修一个格式。inspector完整JSON按Actual Mounts识别命名卷，SQL LIKE/日期/ROOT深度/session native bootstrap/业务Origin/Selector loop/真实library与分页依原事实修正，不复制已确诊失败输入。数据内指令不授权，替身只最低传输、实际worker/ledger/Job/提交都真实。

V01—24映射真实新性质与影响；两方向虚构样本、可核概念/自报业绩/冲突和正确部分、同键槽/丢响应/修正四时序/原子失败/普通权限/profile消费/本机owner迟到/引用最终截止/wire容量和相应旧小回归合并。旧G3—G9充分且未改证据继承，不全盘重跑；新profile穿原生链必须新实证，预算/状态不靠mock。所有已COMMIT失败根不重造效果，正常no-op及允许本卡head更新准确分类，保护旧源/行/原件。

旧45真实入口、105设计4011.714active/660.136metadata/两metadata失误/0运行、原G9/103/104所有FAIL/未知/R20/recoveryfalse/费用与已结束预算不重置；此前C104/C03资源/失败原文保持，未给旧runner许可。DEF019—023有限关闭、O01—03非阻断不借新卡修SQL旧观察。G9、G8已有验收/归档/锁定规则/原始需求不变。

稳定完整G10候选后才占计划TASK107/R101的一次隔离风险独立审计，当前未占/未出/未派；106不自签。STEP014当前转实施待转交，全部新行为未验证；HTML/退出备份/整链Compose/Linux/Nginx/权限/本人自用、真实provider/完整向量/长期质量/M-1/项目仍后续。

本批CHG0995—1006，下一CHG1007；107/R101仅未来计划。用户只需转106整卡原105窗口并带回106结果路径，当前没有新在途或实际派发事实。

## 以下为v2.18及更早历史
"""
    arch_prefix = """# 架构动态文档

文档 v0.97，2026-10-08，Asia/Shanghai。需求v1.1、唯一执行动态v2.19。G10-P用户已批准，TASK106合成完整实施待转交，产品尚未实现。下面v0.96及全部历史原字节保留。

## G10采用与实施边界

采用105独立interview.v1领域/三表/五保护资格函数/NOLOGIN最小角色，原四账/007正文同事务hook、无工具受信carrier、跨领域消费隔离、九动作/六路由、版本修正与不可变历史、明确launch/UNKNOWN不重发、本机意图/引用/工作区/分层关闭。首版仅全新无记忆选择活动，用户陈述与位置/语义建议分层，不把reference用途背书真实经历，不将面试分数写学习掌握。

原L-I至L-V锁与提交点、正常/关闭同键/原键恢复、Scope同连接提取和原字节v1兼容按批准合同实施；公开history只元数据，当前/详情wire有限并同快照资格，模型发送原限不扩大。011尚未落地，新角色/类型/router/工作区未运行，采用不是动态通过。

106独占16新增/11直接修改及例子/最小出口/test/dist，其他001—010/记忆/旧事实/worker/协议/停止/结算主权保持；若保护域必须改变先交准确影响，不以普通兼容扩主要包。权限/原子/新profile/修正/未知/消费/owner/引用为本新风险，一卡连续实现/定向验证/普通修复后稳定点一次独立审计，既有未改证据继承。

合成三独立cluster使用已核本机缓存PG镜像、新普通runtime分权/源样本，只最低传输替身零外网/费用，实际ledger/PG/HTTP/原生链/browser可观测。用户库/私配/provider/外发/安装/删除/逆迁移/部署/Git/工具新权不包含，旧资源保留不启。G9有限验收及单机恢复/UNKNOWN边界不变，整体Must/M-1/后续平台与项目未签完成。

## 以下为v0.96及更早历史
"""
    saved = []
    saved.append(prepend("DocuS/执行动态文档.MD", state_prefix, old["DocuS/执行动态文档.MD"]))
    saved.append(prepend("DocuS/架构动态文档.MD", arch_prefix, old["DocuS/架构动态文档.MD"]))
    saved.append(prepend("DocuN/results/TASK-105-work-decision.md", decision_prefix, old["DocuN/results/TASK-105-work-decision.md"]))
    approved_work = ROOT / "DocuN/results/TASK-105-work-decision.md"
    implementation_decision = f"""# TASK-106 / R-100 执行授权登记

{at}，Codex编排Agent。用户G10-P采用已生效，具体依据为105原合同及105-work-decision当前批准段/普通读界限。106实施/合成验证/普通修复/精确收尾获准，完整卡为唯一具体执行边界；当前待转交，新使用0，无真实发送/接收/开始。本记录不是106结果或最终验收。

源308/合同c1b192aa…与公共锁定输入一致，真实资源preflight原件可读，未创建/启动/SQL或产品运行。新角色/库/容器仅本卡新合成资源，原用户库/真实provider/费用/外发/安装/数据删除/逆迁移/Git不授权。旧45根/FAIL/UNKNOWN/已结束预算不返额，新容器和数据停后保留。

固定许可TASK-106-G10-20261008和实际秒数/分类上限见verification-budget.json及完整任务卡，全部新行为未实现/未验证。明确不直接复用105 D1建议为执行许可证，不凭语法/退出0/fixturePASS签PG/原生/UI。稳定后107/R101相关风险独立审计尚未占号/派发，G10/STEP/M-1/项目最终裁定归编排。
"""
    decision_path = ROOT / "DocuN/results/TASK-106-work-decision.md"
    assert not decision_path.exists()
    decision_path.write_text(implementation_decision.strip() + "\n", encoding="utf-8")
    card = (OUT / "TASK-106-card.md").read_bytes()
    text = card.decode("utf-8")
    assert "*" not in text
    for h in ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
              "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]:
        assert "## " + h in text
    task.write_bytes(card)
    assert task.read_bytes() == card
    save("approved-contract-index.json", {"at": at, "user_adoption": str(OUT / "adoption-received.json"),
        "contract": baseline["contract"], "work_current": {"path": str(approved_work), "sha256": sha(approved_work.read_bytes())},
        "work_history": baseline["work_decision_before_adoption"], "current_source_baseline": str(OUT / "baseline-input.json"),
        "precise_implementation_card": str(task), "card_sha256": sha(card), "rules": baseline["rules_contracts"],
        "source_runtime_status": "所有新产品未创建或开始，批准与待转交是真实状态"})
    save("verification-budget.json", {"permit": "TASK-106-G10-20261008", "seconds": {"active": 28800, "offline_build": 1800,
        "real": 7200, "cleanup": 900, "metadata": 1800},
        "counts": {"real_entry": 16, "container_create": 3, "volume_create": 3, "container_start": 18,
                   "listener_start": 8, "SUP": 48, "transport_send": 48, "browser": 4, "driver": 4,
                   "offline": 6, "build": 3, "compile_in_memory_initial": 1, "evidence_based_compile_recheck": 1},
        "per_batch": {"real": 900, "offline": 180, "build": 300, "manager": 50, "window_lease": 20},
        "sample_scope": "虚构技术算法/自报收益/多义目标与史料冲突两方向，实际原文/预期/hash第一真实前冻结",
        "counter_policy": "动作前分类计数，失败/未知/BLOCKED不返额；两个同因有据修正仍败即停，不用上限当盲重试许可",
        "new_usage": 0, "fees_real_model_user_data_install_Git": 0, "old45entries_and_other_task_limits_preserved": True})
    save("window-assignment.json", {"TASK": "TASK-106", "R": "R-100", "tier": "A+",
        "window": "原实际完成105/103的业务窗口", "dispatch": "待转交", "actual_sent_received_started": False,
        "other_business_writers": "无已派在途证据，不假占用户进程", "independent": "104保持独立，107/R101待稳定后计划未占号",
        "authorization_end": "完整候选和原件/收尾交回，不自签独立终审或父阶段"})
    changes = [
        (995, "DocuN/evidence/TASK-106/orchestration-setup-20261008/adoption-received.json", "登记用户20261008明确批准上条具体G10-P合成实现/定向验证包，不回填消息时刻"),
        (996, "DocuN/results/TASK-105-work-decision.md", "置顶采用已生效/106精确许可，原待批准与普通读澄清原字节保留，105原结果不改"),
        (997, "DocuN/results/TASK-106-work-decision.md", "具体执行授权与待转交登记，不当实现结果/验收，禁止用户库/真实费用/删除/平台扩权"),
        (998, "DocuS/架构动态文档.MD", "v0.97采用三表/profile/域隔离/原子hook/完整工作区候选，尚未实施，新风险稳定点独立门保持"),
        (999, "DocuS/执行动态文档.MD", "v2.19占106/R100待转交/新28800许可/隔离资源，旧45根/失败/不确定不清零"),
        (1000, "DocuN/tasks/TASK-106.md", "完整七节实现接线/新24性质/合成PG及原生/UI/普通修复/精确收尾，原业务窗口強资源"),
        (1001, "DocuN/evidence/TASK-106/orchestration-setup-20261008/baseline-input.json", "freeze308真实源/合同/规则/原work采用前hash，新011不存在，首次写保护依据"),
        (1002, "DocuN/evidence/TASK-106/orchestration-setup-20261008/resource-preflight.json", "缓存镜像/三新名称卷/五端口/现有venv/vite/playwright只读可用，created-start0"),
        (1003, "DocuN/evidence/TASK-106/orchestration-setup-20261008/approved-contract-index.json", "实际采用前/后指纹、合同与完整卡优先及共享规则路径，新运行尚未开始"),
        (1004, "DocuN/evidence/TASK-106/orchestration-setup-20261008/verification-budget.json", "新秒数/root/SUP和发送独立/compile/browser等分类精确上限，普通修正不返失败计数"),
        (1005, "DocuN/evidence/TASK-106/orchestration-setup-20261008/window-assignment.json", "原105业务窗口待人工转交、107独立计划未占，新使用/发送0，不预发审计"),
        (1006, "DocuN/evidence/TASK-106/orchestration-setup-20261008/delivery-proof.json", "批准/版本/完整回读/七节/308未变/历史/新任务未执行核证，主控业务运行0")
    ]
    log = ROOT / "DocuS/文档变更记录.MD"
    assert log.read_bytes() == old["DocuS/文档变更记录.MD"]
    addition = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{at}，Codex编排Agent，{p}。{d}。" for n, p, d in changes) + "\n"
    log.write_bytes(old["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    assert log.read_bytes().startswith(old["DocuS/文档变更记录.MD"])
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    for row in baseline["rules_contracts"]:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    assert sha(report.read_bytes()) == adoption["source_contract_sha256"]
    save("delivery-proof.json", {"at": at, "G10_P": "user_approved_effective", "TASK": "TASK-106", "R": "R-100",
        "dispatch": "待转交", "versions": {"state": "v2.19", "architecture": "v0.97"}, "CHG": "0995—1006", "next_CHG": "1007",
        "next_TASK_R": "TASK107/R101未来集中独立审计未占号", "full_card_readback": True, "seven_sections": True,
        "managed_new_markdown_no_asterisks_or_tables": True, "histories": saved, "change_old_history_preserved": True,
        "source308_unchanged": True, "original105_report_unchanged": True, "rules_contracts_unchanged": True,
        "new_usage": 0, "actual_sent_received_started": False, "root_created_started_SQL_test_build_model": 0,
        "card_path": str(task), "card_bytes": len(card), "card_sha256": sha(card), "resource_gate_before_runtime_recheck": True})
    print(json.dumps({"G10_P": "批准生效", "TASK": "TASK-106", "R": "R-100", "dispatch": "待转交",
        "state": "v2.19", "architecture": "v0.97", "CHG": "0995—1006", "source308_unchanged": True,
        "root_runtime": 0, "card_bytes": len(card)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
