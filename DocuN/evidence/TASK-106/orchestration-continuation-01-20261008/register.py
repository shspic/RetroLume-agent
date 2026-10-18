"""登记部分回收及106同卡接续许可，不接管执行层或开启资源。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-106"
RECEIPT = BASE / "orchestration-receipt-01"
OUT = BASE / "orchestration-continuation-01-20261008"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, value):
    assert not path.exists(), "不覆盖或重复新的接续记录"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepend(rel, text, old):
    path = ROOT / rel
    assert path.read_bytes() == old, "共享文档出现并行变化"
    prefix = (text.strip() + "\n\n").encode("utf-8")
    assert "*" not in text
    path.write_bytes(prefix + old)
    assert path.read_bytes()[len(prefix):] == old
    return {"path": rel, "old_sha256": sha(old), "new_sha256": sha(path.read_bytes()), "prefix_bytes": len(prefix), "history_exact": True}


def main():
    receipt = load(RECEIPT / "receipt.json")
    assert receipt["all_owned_stopped"] and receipt["no_listeners"]
    current = load(RECEIPT / "current-baseline.json")
    assert len(current) == 346
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report = ROOT / "DocuN/results/TASK-106-result.md"
    assert sha(report.read_bytes()) == receipt["report_sha256"]
    old = {r["path"]: (RECEIPT / "before" / r["path"]).read_bytes() for r in load(RECEIPT / "before-manifest.json")}
    for rel, body in old.items():
        assert (ROOT / rel).read_bytes() == body
    state_old = old["DocuS/执行动态文档.MD"].decode("utf-8")
    assert "文档 v2.19" in state_old[:300]
    assert all(name not in state_old for name in ["DEF024", "DEF025", "DEF026", "DEF-024", "DEF-025", "DEF-026"])
    at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    card = (OUT / "TASK-106-continuation-01-card.md").read_bytes()
    card_text = card.decode("utf-8")
    assert "*" not in card_text
    for h in ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
              "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]:
        assert "## " + h in card_text
    close = load(BASE / "final/session-close.json")
    declared = load(BASE / "final/baseline-post-and-build-identity.json")
    budgets = {"permit": "TASK-106-G10-C01-20261008", "seconds": {"active": 21600, "offline_build": 1200,
        "real": 3600, "cleanup": 600, "metadata": 1200},
        "counts": {"root": 8, "container_start": 12, "listener_start": 6, "browser": 3, "driver": 3,
                   "offline_batch": 4, "build": 2, "compile_initial": 1, "compile_recheck": 1,
                   "SUP_attempt": 32, "transport_send": 32, "password_reset": 2,
                   "container_create": 0, "volume_create": 0, "role_create": 0},
        "per_batch": {"root": 600, "offline": 180, "build": 300, "native_manager": 50, "window_lease": 20},
        "usage_now": 0, "counter_policy": "旧许可整体结束，新额明确授权不借旧14/17余额；原同因失败/已COMMIT/UNKNOWN不返，不超过两次同因有据修正"}
    save(OUT / "verification-budget.json", budgets)
    save(OUT / "findings.json", {
        "at": at, "TASK": "TASK-106", "R": "R-100",
        "E106-SEM": {"kind": "正向语义验证FAIL", "trigger": "最低fixture按catalog排序第一项/每source第一项引用，T只免责声明，H第二处无2013",
                     "grade": "真实已提交值/原片段A级原件，不自动上升生产通用证明缺陷", "action": "正确支持片段及预设oracle，新key合法结果，旧immutable保留"},
        "DEF024": {"priority": "P2", "state": "开放", "source": "frontend/src/activities/InterviewWorkspace.tsx",
                   "fact": "历史answer选中仅只读，没有105允许的同goal/scope合格早期答案显式修订UI", "owner": "106同卡"},
        "DEF025": {"priority": "P2", "state": "开放", "source": "InterviewWorkspace.reconcile",
                   "fact": "live仅panel/activity/owner，未捕获同活动expected view和原intent key/hash在各await后的授权边界", "owner": "106同卡"},
        "DEF026": {"priority": "P1", "state": "开放条件路径", "source": "backend/app/interview/service.py submit_command",
                   "fact": "caller cancelled在shield完成后先raise，位于必要finish_interview_supervision前；mark后拒结果场景可能跳过native UNKNOWN诊断/领域收尾",
                   "grade": "B级源确定可达跳过分支；组合遗留的动态影响尚未跑，不称已观察第二故障", "owner": "106新service/必要仓储接线，原worker不改"},
        "existing_fixed": "P05 native诊断由P06复验，P11立即卸载由F03/P12/P16复验，未变部分保留",
        "scope": "四核心/直接未覆盖风险同106整卡，未新增G10包/平台或107审计"})
    navigation = {"previous_report": str(report), "current_baseline": str(RECEIPT / "current-baseline.json"),
        "post_subset": str(BASE / "final/post"), "post_subset_count": 54,
        "full_old_fields": str(BASE / "final/baseline-post-and-build-identity.json"),
        "matrix": str(BASE / "final/matrix.json"), "runs": str(BASE / "final/run-index.json"),
        "semantic": str(BASE / "final/semantic-oracle.json"), "remainder": str(BASE / "final/remainder-work.json"),
        "resources": str(RECEIPT / "resource-readonly.json"), "old_session": str(BASE / "final/session-close.json"),
        "inheritance": "所有已验实际方法按as-run/变化区定位；早P11没有mjs原件不伪造，54post仅子集不是346完整运行副本",
        "runtime_semantic": "结构/位置/客户端显示/源支持分层，T/H旧误支持原件不改，总rootFAIL保持"}
    save(OUT / "reuse-and-remainder.json", navigation)
    rules = declared["locked_rules"]
    input_path = BASE / "continuation-01-input.json"
    save(input_path, {"at": at, "TASK": "TASK-106", "R": "R-100", "round": "续作01", "current_files": current,
        "current_objects": 346, "post_subset": 54, "protected_objects": 292,
        "report": {"path": str(report), "bytes": 21949, "sha256": receipt["report_sha256"]},
        "old_card_backup": str(RECEIPT / "before/DocuN/tasks/TASK-106.md"),
        "new_card_prefix_sha256": sha(card), "new_card_prefix_bytes": len(card),
        "new_budget": budgets, "old_permission_ended": close, "old_unknown": "保留所有，包括原103 R20/UNKNOWN，不重发或退款",
        "resources_now": load(RECEIPT / "resource-readonly.json"), "new_usage": 0, "dispatch": "待转交，实际发送/接收/开始0",
        "rules_locked": rules, "schema_actual_fingerprint": "13e3d8d9d78d7f6e119a226be6f4d6f3163b9bf5eaeeb1b8d66e5d44351f850b",
        "migration_source_sha256": current["backend/migrations/011_text_interview.sql"],
        "facts": str(OUT / "findings.json"), "remaining_mapping": str(OUT / "reuse-and-remainder.json"), "root_product_runs": 0})
    decision_prefix = f"""# TASK-106 / R-100 部分回收与续作01裁定

{at}，Codex编排Agent。106实际部分返回，报告21949字节/123afe0988d0736420f16751dd794da926d99eb993b185d8f834a5b993664fea与最终交付一致，主控普通接受保存的实现候选、有限成立原件和停止。当前346对象/15授权变化/292保护/16新生产源/54 post子集/21执行记录匹配，54不是346完整快照。G10/STEP014未通过，107未占或派发。

正向T只引免责声明、H第二引用无2013原句，原semantic-oracle FAIL保留；位置/结构PASS不能闭语义。历史answer显式修订UI和reconcile expected view/key/hash欠合同，登记DEF024/025-P2；service caller取消先raise跳过finish登记DEF026/P1条件路径，源码可达但取消/mark后拒结果的遗留尚未动态跑，不夸成已观察故障。

旧root16/start18/build3/compile2耗尽许可结束；SUP34/48、transport31/48、browser3/4等名义余量不授新入口。旧active15866.782是05:19:52检查点，05:22:10交付更晚时段未精准分项，未知不返；real502.303/cleanup7.481/offline16.116/metadata780保守及原所有45+16=61根、FAIL/UNKNOWN/不可变旧结果保持。

续作01同106/R100沿原A+强模型窗口，先补四核心、必要高风险未验与最终证据，普通修复同卡统一返回。G10-P已批准不重复问。新许可TASK-106-G10-C01-20261008，active21600/offline_build1200/real3600/cleanup600/metadata1200秒；root8/start12/listener6/browser-driver3/offline4/build2/compile1+有据复检1/SUP32/transport32/口令重置2，新container/volume/role0。新使用0、卡待转交，不借旧14/17余额，不复位同因失败。

精确原106三个CID/卷/镜像/标签/配额当前Stopped/Pid0和18106/18107/55446—55448无监听已只读核；仅这些资源新许可可复用。原样本/失败输出/旧已COMMIT、fault view/全部role数据保留，不重bootstrap/DROP/DELETE或触用户库。011/ACL默认冻结，必要同新域函数前向维护必须精确pre/定义/owner/ACL/hash/行保留，不扩主要模型或保护平台。

已真实P05/P06诊断及P11/F03/P12/P16立即卸载原件继承，旧V01—24未穷举的纯契约变体不机械全跑。新语义必须真正源支持、准确取消/历史修订和view窗口补新证据；已过效果不为总批绿重造。稳定完整后再派107集中独立风险审计，现在不先审未补候选、不逐四核心各审一轮。

最终报告置顶保原21949字节，new证据continuation-01，本次主控源/SQL/测试/build/资源启动0。源/共享历史原字节保持，原103/104/105与旧有限验收/非阻断O01—03不重开。具体资源/写权/停止在完整106新前缀。用户只需转原106窗口并带回原结果路径。

## 以下为106初轮执行授权历史
"""
    state_prefix = """# 执行动态文档

文档 v2.20，2026-10-08，Asia/Shanghai。唯一总状态账；需求v1.1、架构v0.98，task_model/阶段07。下面v2.19及全部历史原字节保留。

## TASK106部分返回；四核心及最终证据同卡接续

106/R100已实际返回，普通回收部分通过，接受保存的实现/有限运行/收尾，不签完整候选G10。报告21949字节/123afe09…与delivery一致；原308变化和当前346对象、54份post源码fixture/dist子范围、15授权变化、292保护、16新生产/21执行记录身份匹配。54post不扩成346完整运行快照；原105合同/公共锁定相同，产品运行主控0。

已落011三表/五函数/领域角色、原子正文/新carrier/公开六路由/九动作/配置/UI，实际PG/原生SUP/HTTP/build/browser有原件。P05的native dispatched诊断欠缺经P06修复，P11立即选中活动失效经F03/P12/P16修复，未改路径和其他独立成立子性质有效。未写空PG/HTTP skip来冒实测；早as-run多hash、P11缺mjs原件的限制保持，不能伪造旧字节。

真实语义E106-SEM仍FAIL：T认可引免责声明无法支持110/覆盖，H第二处只冲突说明没有2013原句；支持条款不能被位置PASS/结构PASS或P03/P04总断言代替。根因最低合成fixture取排序/每source第一片段明确，旧immutable结果保留，需正确支持原句/oracle及新key合法结果，不自动把它称生产通用语义验证器缺陷。

登记DEF024/P2：历史详情只有读，缺同goal/scope合格早期answer显式修订UI；DEF025/P2：reconcile live仅panel/activity/owner，未捕获same-activity expected view及原intent key/hash逐await授权。DEF026/P1条件路径：submit_command caller取消在shield完成后先raise跳过finish，遇mark后结果资格拒绝可能漏native UNKNOWN/领域收尾；源码B级可达，尚未动态验证该组合，不夸成新增已实跑故障。四条同一个106收口，不新模型/权限包。

初轮许可结束：root16/16、start18/18、build3/3、compile2/2触顶；listener6/8、native34/48/transport31/48、browser-driver3/4/offline2/6余量不恢复执行。新container/volume3/3。offline/build16.116/1800、real502.303/7200、cleanup7.481/900、metadata780/1800保守未知保持；active15866.782在05:19:52检查点、更晚05:22:10交付未分项精准不返额。旧45加新16=61入口，不是61成功。

七rootFAIL原样：P02语义仍开、P05诊断（P06已修）、P06夹具漏slot码、P09资料Origin误用（P10正确5173）、P11旧面板（已修）、P13例外类型误判、P14read_status当status。初矩阵未充分逐项冻结调用/预期的偏差、早P11缺mjs以及一次非任务进程metadata接触/之后收窄均照实，不宣从未发生；无源码或业务越权的新事实推导。旧COMMIT不重造/FAIL不改绿。

同TASK106/R100续作01已登记，沿原业务A+强推理窗口，整卡准备四核心及真实剩余/最终版本/原件/资源，新实际使用0、调度待转交，无实际发送/接收/开始。原G10-P已批准不再问。完整稳定后107/R101才派一次相关风险独立审计，当前未占/出/发，不审未齐候选，也不因小修反复审。

新许可TASK-106-G10-C01-20261008：active21600、offline/build1200、real3600、独立cleanup600、metadata1200秒；root8(≤600)、start12、listener6、browser-driver3、offline4(≤180)、build2(≤300)、compile内存1+有据复检1、nativeSUP32/最低transport32分别计、精确本卡口令重置≤2，新create容器/volume/role0。旧14/17不是预算来源；原失败、同因两修仍败停止不清零，余量不盲试。

精确reuse pg1 dca7942c…/main/55446、pg2 25ba629d…/upgrade/55447、pg3 5cee6773…/fault/55448及原卷/镜像/许可标签/1CPU/512MiB/pids128/restartno/loopback；当前主控只读核均Stopped/Pid0、API18106/fake18107/PG端口无监听。原role属性/ACL不改，必要本卡密码只RAM，旧服务停；不启用户/103等旧资源，不DROP/DELETE或改变系统时钟。fault额外view保留，011/S1指纹13e3d8d9…仍ready。

现域允许修到原包功能契约，默认011/ACL冻结；确需原新域函数普通纠错仅精确前向/源和S1同步及旧行/权限hash保留，主要结构/平台/工具变化仍交具体差异。新证据continuation-01、报告原21949字节历史不改，新正文无星号/表格，旧格式不追改。数据/未知/声明保留，不能mockSQL/权限/Job/提交/停止。

新T/H正向来源、历史修订后继/真实UI、same-activity view恢复、caller取消/mark/拒结果，和直接必要nativeprobe/新scope/澄清/记忆不可靠/跨消费/容量及恢复小例联合覆盖；不穷举所有属性或重跑旧G3—G9。源码/build修改后相关性质绑定最终字节，其他未变原方法继承；结构、位置、源支持、oracle、实际行为分层。

G10/STEP014未完成验收，M-1/整体Must/provider/发布/项目保持后续门。G9/103/104/105及DEF019—023有限关闭/O01—03非阻断/旧未知R20/recoveryfalse/预算/归档/规则/原始需求不重开不修改。本次主控仅核证共享维护，产品/测试/构建/SQL启动0。

本批CHG1007—1017，下一CHG1018；107/R101计划未占号。用户必要动作仅转106续作01整卡原窗口并带回原结果路径。

## 以下为v2.19及更早历史
"""
    arch_prefix = """# 架构动态文档

文档 v0.98，2026-10-08，Asia/Shanghai。需求v1.1、唯一执行动态v2.20。G10完整代码候选部分返回，正向语义/历史UI/恢复守卫/取消收尾未齐，原106同卡接续，未签通过。下面v0.97及全部历史原字节保留。

## G10实际候选与四核心缺口

011三表/新领域/受信carrier/原子007 hook/消费隔离/配置及面试UI已落，PG/原生/HTTP/最终F03与UI链有有限原件；新S1目录指纹13e3d8d9…及普通角色权限有实测，不等新语义和所有窗口已通过。原预算/worker/停止平台/001—010未改，新域两个已观察问题已有修正证据。

T/H源支持oracle失败保留，最低合成响应误选免责声明/无2013句，结构与位置不能签语义；只按真实支持片段新key补结果，不把模型建议升级机器证明。历史answerUI与后继合法修订、reconcile same-view/key/hash授权欠契约，callerCancelledError在新service必要收尾前raise是条件路径风险；分别登记024/025/026，原106唯一修复归属，不扩包或旧平台。

续作01在原G10-P内一份完整剩余接续，旧T/H immutable/FAIL/no-op/UNKNOWN/原在途事实保持。默认011/ACL冻结，若确需同新域函数普通修正精确前向且原行/权限不变；不能建新模型/角色或放松资格指纹。旧G3—G9充分原件未变继承，高风险新窗口须真实proof，稳定后才一次集中独立审计。

现原native与UI主链不代完整G10/STEP014/M-1/provider/全项目验收，能力/恢复/取消远端边界不变。精确复用三本卡CID停后保留，不启旧用户或删除资源，实际运行许可/计数/45+16失败链及新配额见唯一执行动态v2.20。

## 以下为v0.97及更早历史
"""
    saved = []
    saved.append(prepend("DocuS/执行动态文档.MD", state_prefix, old["DocuS/执行动态文档.MD"]))
    saved.append(prepend("DocuS/架构动态文档.MD", arch_prefix, old["DocuS/架构动态文档.MD"]))
    saved.append(prepend("DocuN/results/TASK-106-work-decision.md", decision_prefix, old["DocuN/results/TASK-106-work-decision.md"]))
    saved.append(prepend("DocuN/tasks/TASK-106.md", card_text, old["DocuN/tasks/TASK-106.md"]))
    save(OUT / "window-assignment.json", {"at": at, "TASK": "TASK-106", "R": "R-100", "round": "续作01",
        "tier": "A+", "window": "原实际106业务窗口", "dispatch": "待转交", "new_usage": 0,
        "same_goal_and_scope": True, "original_permission_ended": True, "actual_sent_received_started": False,
        "independent107": "候选完整稳定后计划，不现在占号/发卡"})
    changes = [
        (1007, "DocuN/evidence/TASK-106/orchestration-receipt-01/receipt.json", "真实部分回收21949结果/346对象/54post子集/292保护/21记录/三CID停止，完整G10未通过"),
        (1008, "DocuN/results/TASK-106-work-decision.md", "置顶初轮闭账/四核心/原窗口新接续配额/同一批准包，旧执行授权原字节保持"),
        (1009, "DocuN/evidence/TASK-106/orchestration-continuation-01-20261008/findings.json", "保留T/H真实支持FAIL，登记024/025欠契约和026取消跳过收尾B级条件路径，不虚构动态故障"),
        (1010, "DocuS/架构动态文档.MD", "v0.98同步G10实际候选及四核心，旧平台/表保护，默认011冻结和必要精确同域前向边界"),
        (1011, "DocuS/执行动态文档.MD", "v2.20登记106实际部分返回/61原新入口/闭账与续作01新许可待转交，107仍计划"),
        (1012, "DocuN/tasks/TASK-106.md", "置顶完整七节同106接续四核心/直接高风险缺证/最终UI原生与资源，旧完整卡原字节保留"),
        (1013, "DocuN/evidence/TASK-106/continuation-01-input.json", "冻结346实际字节/54子集/原报告和批准/CID/目录指纹/已结束账及新预算，执行使用0"),
        (1014, "DocuN/evidence/TASK-106/orchestration-continuation-01-20261008/reuse-and-remainder.json", "原矩阵和as-run限定复用，正向/位置/结构分层，已有P05/P11修复和原FAIL不重造"),
        (1015, "DocuN/evidence/TASK-106/orchestration-continuation-01-20261008/verification-budget.json", "独立C01明确8根/12start/32SUP与发送/2build等新许可，不借旧余量，失败因果累积"),
        (1016, "DocuN/evidence/TASK-106/orchestration-continuation-01-20261008/window-assignment.json", "原业务窗口強资源待人工转交，共享状态唯一，未实际发送/接收/开始"),
        (1017, "DocuN/evidence/TASK-106/orchestration-continuation-01-20261008/delivery-proof.json", "全文七节回读/报告346源和历史不变/版本CHG对齐/当前资源时点，只读元数据无主控执行")
    ]
    log = ROOT / "DocuS/文档变更记录.MD"
    assert log.read_bytes() == old["DocuS/文档变更记录.MD"]
    addition = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{at}，Codex编排Agent，{p}。{d}。" for n, p, d in changes) + "\n"
    log.write_bytes(old["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    assert log.read_bytes().startswith(old["DocuS/文档变更记录.MD"])
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    for row in rules:
        assert sha(Path(row["path"]).read_bytes()) == row["before"]
    assert report.read_bytes() == (RECEIPT / "TASK-106-as-returned.md").read_bytes()
    save(OUT / "delivery-proof.json", {"at": at, "TASK": "TASK-106", "R": "R-100", "round": "续作01",
        "dispatch": "待转交", "state": "v2.20", "architecture": "v0.98", "CHG": "1007—1017", "next_CHG": "1018",
        "full_card_seven_sections_readback": True, "managed_new_markdown_no_asterisks_or_tables": True,
        "histories": saved, "old_change_history_exact": True, "report_21949_unchanged": True,
        "current346_unchanged": True, "locked_rules_unchanged": True, "new_usage": 0,
        "actual_sent_received_started": False, "root_product_SQL_test_build_start": 0,
        "card_path": str(ROOT / "DocuN/tasks/TASK-106.md"), "card_sha256": sha((ROOT / "DocuN/tasks/TASK-106.md").read_bytes()),
        "card_prefix_bytes": len((card_text.strip() + "\n\n").encode("utf-8")), "input_sha256": sha(input_path.read_bytes())})
    print(json.dumps({"TASK": "TASK-106", "R": "R-100", "round": "续作01", "dispatch": "待转交", "state": "v2.20",
        "architecture": "v0.98", "CHG": "1007—1017", "current346_unchanged": True, "product_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
