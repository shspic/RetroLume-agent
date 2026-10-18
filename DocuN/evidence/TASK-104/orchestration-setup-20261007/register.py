"""登记G9集中独立终审合同，只维护共享文档与冻结元数据。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-103"
RECEIPT = BASE / "orchestration-receipt-03"
OUT = ROOT / "DocuN/evidence/TASK-104/orchestration-setup-20261007"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    path = OUT / name
    assert not path.exists(), "保留已有登记，不能覆盖或重复派卡"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepend(rel, text, old):
    path = ROOT / rel
    assert path.read_bytes() == old, "共享对象出现并行变化，停止覆盖"
    prefix = (text.strip() + "\n\n").encode("utf-8")
    assert "*" not in text
    path.write_bytes(prefix + old)
    assert path.read_bytes()[len(prefix):] == old
    return {"path": rel, "prefix_bytes": len(prefix), "old_sha256": sha(old),
            "new_sha256": sha(path.read_bytes()), "history_exact": True}


def product(rel):
    return rel.startswith(("backend/app/", "frontend/src/")) or rel in {
        "backend/migrations/010_learning_memory.sql", "config/activity.example.json", ".gitignore", "README.md"}


def main():
    receipt = load(RECEIPT / "receipt.json")
    assert receipt["all_owned_stopped"] and receipt["no_target_listeners"]
    current = load(RECEIPT / "current-baseline.json")
    assert len(current) == 291
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report = ROOT / "DocuN/results/TASK-103-result.md"
    assert sha(report.read_bytes()) == receipt["report_sha256"]
    before = load(RECEIPT / "before-manifest.json")
    old = {r["path"]: (RECEIPT / "before" / r["path"]).read_bytes() for r in before}
    for rel, body in old.items():
        assert (ROOT / rel).read_bytes() == body
    task_path = ROOT / "DocuN/tasks/TASK-104.md"
    assert not task_path.exists() and not (ROOT / "DocuN/results/TASK-104-result.md").exists()
    assert "文档 v2.13" in old["DocuS/执行动态文档.MD"].decode("utf-8")[:400]
    assert "文档 v0.91" in old["DocuS/架构动态文档.MD"].decode("utf-8")[:400]
    at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    initial = load(BASE / "orchestration-setup-20261006/product-baseline.json")
    original = {row["path"]: row for row in initial}
    changed, added, removed = [], [], []
    for rel, expected in current.items():
        if product(rel) and (rel not in original or original[rel]["sha256"] != expected):
            row = {"path": str(ROOT / rel), "relative_path": rel, "current_sha256": expected,
                   "initial_sha256": original[rel]["sha256"] if rel in original else None,
                   "initial_bytes_path": str(BASE / "pre" / rel) if rel in original else None}
            (changed if rel in original else added).append(row)
    for rel in original:
        if rel not in current:
            removed.append({"relative_path": rel, "initial_sha256": original[rel]["sha256"],
                            "preserved_initial_path": str(BASE / "pre" / rel)})
    rules = load(BASE / "continuation-02/rules-verified.json")
    protected = load(BASE / "continuation-01/final/protected-files.json")
    for row in rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    binding_paths = ["AGENTS.md", "DocuS/最终需求文档.MD", "DocuN/results/TASK-102-result.md",
                     "DocuN/results/TASK-102-work-decision.md", "DocuN/tasks/TASK-103.md"]
    contracts = [{"path": str(ROOT / p), "sha256": sha((ROOT / p).read_bytes()), "bytes": (ROOT / p).stat().st_size}
                 for p in binding_paths]
    source_relations = {"initial_233_manifest": str(BASE / "orchestration-setup-20261006/product-baseline.json"),
        "changed_existing_products": changed, "new_products": added, "removed_generated_preserved": removed,
        "current_files": current, "current_complete_post": str(BASE / "continuation-02/final/post"),
        "complete_diff_inputs": [str(BASE / p) for p in ["final/pre-diff-post.json", "final/product.patch",
            "continuation-01/final/pre-diff-post.json", "continuation-01/final/product.patch",
            "continuation-02/final/pre-diff-post.json"]],
        "scope": "实际G9产品差异与直接依赖，非291个对象全部逐行重审；保留所有最终字节"}
    save("baseline-and-changes.json", source_relations)
    resources = load(RECEIPT / "resource-readonly.json")
    permit = {"permit": "TASK-104-G9-AUDIT-20261007", "seconds": {"active": 21600, "metadata": 1800,
        "real": 600, "cleanup": 300, "fixture_offline": 300},
        "counts": {"entry": 3, "container_start": 3, "listener_start": 3, "browser": 3, "driver": 3,
                   "fixture_offline": 3, "build": 0, "SUP": 0, "container_create": 0, "volume_create": 0, "role_create": 0},
        "resources_now": resources, "allowed_start": resources["containers"][0]["cid"],
        "port": 18103, "db_port": 55443, "database": "retrolume_task103_g9_main",
        "pg2_pg3": "仅inspect，一直停止，不连接", "product_or_business_write": 0,
        "exceptional_resource_setup": "仅精确owned retrolume_task103_app一次RAM随机口令重置；原服务全停，role属性／ACL不变；不改业务",
        "new_actual_usage": 0, "previous_permissions": "TASK103初轮／C01／C02均已结束，旧失败／未知／投入不重置或借用",
        "dispatch": "准备，全文保存回读后待转交，不是已发或执行"}
    save("resource-permit.json", permit)
    navigation = {
        "original_goal_contracts": contracts,
        "evidence_roots": [str(BASE), str(BASE / "continuation-01"), str(BASE / "continuation-02")],
        "old_run_and_version_records": [str(BASE / p) for p in ["final/runs-ledger.json", "final/pre-diff-post.json",
            "final/function-diff.json", "final/bundle-chain.json", "final/sql-snapshot-evidence.json",
            "continuation-01/final/runs-ledger.json", "continuation-01/final/pre-diff-post.json",
            "continuation-01/final/function-diff.json", "continuation-01/final/sql-chain.json",
            "continuation-01/final/bundle-chain.json", "continuation-02/final/runs-ledger.json",
            "continuation-02/final/pre-diff-post.json", "continuation-02/final/bundle-chain.json"]],
        "c02_direct_raw": [str(BASE / "continuation-02" / p) for p in ["no-evidence-http.json", "browser/result.json",
            "browser/late-edit-controller.json", "browser-02/late-switch-controller.json", "tail/pg-before.json",
            "tail/old-pending-readonly-confirmation.json", "target-selection.json", "browser-target.json",
            "citation-selector-final-not-run.json"]],
        "accounting_and_resources": [str(BASE / p) for p in ["final/accounting-final.json", "final/resources-after.json",
            "continuation-01/final/accounting-final.json", "continuation-01/final/resources-after.json",
            "continuation-02/final/accounting-final.json", "continuation-02/final/resources-after.json"]],
        "reading_method": "按性质从run记录定位as-run、stdout、真实PG／网络／DOM／控制器；自己判适用，汇总matrix不能代原件",
        "exclusion": "不读TASK103结果或work-decision、自评／实现聊天／思考，不以编排回收结论替代审计",
        "independence": "全新未参与102／103窗口；偶然接触如实披露，先形成独立判断"
    }
    for group in ["old_run_and_version_records", "c02_direct_raw", "accounting_and_resources"]:
        for filename in navigation[group]:
            assert Path(filename).is_file(), "导航路径缺失，不提供虚构证据"
    save("raw-evidence-navigation.json", navigation)
    save("audit-input.json", {"at": at, "TASK": "TASK-104", "R": "R-098", "parent": "TASK-103 / R-097",
        "original_contract": "TASK-102 / R-096", "approved_scope": "用户2026-10-06批准G9-P，task_model／V4.0／CHG-0003",
        "current_files": current, "complete_snapshot_files": 291, "protected_files": protected,
        "rules_and_contracts": rules, "goal_contracts": contracts,
        "product_scope_changed_existing": changed, "product_scope_new": added,
        "scope_and_diffs": str(OUT / "baseline-and-changes.json"), "raw_navigation": str(OUT / "raw-evidence-navigation.json"),
        "resource_permit": str(OUT / "resource-permit.json"),
        "candidate_state": "实现稳定冻结，尚缺最后只读引用迟到直接证据和集中独立审计；不预先判通过",
        "final_pending_case": {"activity_id": "a29a945b-a58f-4798-b4b3-93cc1e736aed",
            "record_id": "e6964ce9-7686-45c3-b8b2-8e247cd25dcf", "citation_id": "lc_c0655a9aed2099f2e0d9f328",
            "raw_source": str(BASE / "continuation-02/browser-target.json"), "run_permission": "GET／SELECT只读，业务POST／SUP／model／tool0"},
        "unknown_preserved": "a392c565-1731-4314-b22e-6cee9458f862，R20，UNKNOWN，不能退款／结算／重发",
        "independence": "不给实现者自评或聊天，只提供原合同／现有字节／原始证据，当前并非已派发"})
    state_prefix = """# 执行动态文档

文档 v2.14，2026-10-07，Asia/Shanghai。唯一总状态账；需求v1.1、架构v0.92，task_model／阶段07。下面v2.13及全部历史原字节保留。

## TASK103续作02回收；TASK104集中独立终审与只读补证

103/R097续作02已实际返回，普通回收三项有限补证通过，保存实现候选，完整G9未通过。当前291文件与291完整post、20保护和9规则／合同一致，281旧对象零改变，仅新10份C02材料。结果52856字节／8b544e50…，11834前缀及41022原历史后缀精确保留；原24351初轮也未变。产品与SQL无新差异，已到稳定审查点。

真实HTTP no_evidence409／对应中文、六表与四账前后同值／0新accepted command／operation／SUP／发送成立；浏览器双owner先各获真实预览后A追加、B真正POST409与草稿／绑定保留，后批PG唯一效果成立；真实COMMIT响应暂停期间新编辑与旧绑定／新草稿保留成立。显式身份切换另有真实回执与浏览器断言，没有最后独立PG快照，按有限层级采纳。DEF022候选已具真实补证但与019—021仍待独立确认，不自签共享关闭。

最后引用迟到仍NOT_RUN。C02三根总FAIL及两个browser总FAIL原样，真实首根许可日期旧字面量导致启动前失败，第二根同名旧标题选择器命中9项，第三根误用section.collection／列表limit20。修正后fixture未执行；真实GET200目标不是已经发生浏览器引用挂起或Abort。不能只据报告把总批转PASS，原已COMMIT的另一个旧key只读确认、不重发。

C02许可已结束，entry3/3／offline3/3触顶，start2/3／listener2/3／browser-driver2/3、build0/1／SUP0名义剩额不借。主动3159.755/7200秒，offline7.906／real50.233／cleanup2.687／metadata82.500；元数据保守分段未知和清理重叠保留。初轮及C01全部失败／投入／UNKNOWN不清零，累计39真实根不是39成功批。旧失败command a392c565…的requests4／cost4000／tool1／settled12／R20、恢复开关false不改。

本轮编排只读核三精确CID／镜像／卷／标签／配额匹配且Stopped/Pid0，五端口无监听，业务运行0。十二函数和源／应用／catalog、最终前端24源与加载JS／CSS按未改字节继承；不重做已有三项或全部旧链。

下一完整成果调整为TASK104/R098集中隔离独立终审，同时完成最后一个GET／SELECT浏览器引用迟到补证。理由为产品与SQL稳定未变、该余项只读且不需新业务效果；终审允许针对证据缺口验证，不把未验性质先判通过，也不派第三张纯实施补卡。103实现阶段许可保持结束／验收待终审，不委派其原窗口自己审。

TASK104/R098现已占号并保存完整七节合同，接收A+强推理、全新隔离且未参与102／103窗口，调度待转交，新使用0，无实际发送／接收／开始。三轴审查代码／版本证据／执行控制，完整G9范围一次裁定，发现问题合并回原103修复；不增加逐文件审计或不受影响大套重跑。

新许可TASK-104-G9-AUDIT-20261007，主动21600秒、metadata1800、真实只读600、独立收尾300、fixture离线300；组合根3、pg1 start3、listener3、browser-driver各3、fixture离线3批。预计一个主根；最多两次有据不同原因受影响复验，两修同因仍败即停。产品compile／业务测试／build／DDL／SUP／模型／工具／provider／费用／新容器／卷／角色0，业务POST0。必要未知API最多6页官方原文，不为了审计重复研究。

只可复用pg1 CID4889202d…／库retrolume_task103_g9_main／55443与API18103；pg2／3只inspect保持停止。唯一附条件资源写为旧服务已停后精确本卡app一次RAM口令重置，原role属性／ACL和业务行不变；不更改权限或其他账户。新104独立data／profile／fixture／证据，不激活C02旧permit或复制日期字面量盲启动。

G9最终仍待最后引用直接证据和独立结论，STEP013／M-1／项目／真实provider及后续面试／HTML／退出／Compose／Linux／Nginx门保持。G8与其他有效验收、DEF001／002原禁用、归档／规则／原始需求不变。本次产品、SQL、构建、业务测试／PG启动0，编排只核证和维护共享文档。

本批CHG0944—0953，下一CHG0954；下一TASK105/R099仅未来计划未占号。用户只需转104到新隔离窗口并带回104结果路径，无需重批G9-P。

## 以下为v2.13及更早历史
"""
    arch_prefix = """# 架构动态文档

文档 v0.92，2026-10-07，Asia/Shanghai。需求v1.1，唯一执行动态v2.14。G9当前产品与SQL稳定候选，最后只读引用迟到补证并入TASK104集中独立终审；完整G9未签通过。下面v0.91及全部历史原字节保留。

## G9稳定候选与集中裁定

C02未改281份原对象／产品／010，新增10验证材料。no_evidence实际HTTP409零副作用、双owner真正陈旧POST409／唯一版本效果、真实晚保存回执编辑epoch及显式身份切换已取得有限原件，后者末后PG快照仍未取得，不扩大其证明。十二个函数／角色／清理语义、实际三函数前向、前端24源／dist字节沿C01未改证据保持。

晚引用响应浏览器请求尚未开始，C02仅在列表选择器失败，已保存的section.library／默认GET修正不等于实测。当前无新产品缺陷直接原件，也不宣告此项通过。UI序列／Abort、教学读／资格／来源版本与不可变背景的整个G9实现进入一次集中独立审查，最后GET／SELECT性质可由审计者在原合成资源单独补证。

TASK104只读业务并审代码／证据／控制，禁止业务POST、产品修复／build／DDL／SUP／付费，不重审D3平台或重跑全部G3—G8。若发现阻断回原103合并修复；没有阻断且最后引用实际成立才可建议批准G9有限切片通过。DEF019—022分别给独立建议，未提前关闭。

旧CAS／恢复／四账／UNKNOWN／关门／停止／退款权威、七表／精确清理及v1／v2原批准包不改。旧失败R20、不可变M5、pg2反向DDL落点、pg3 pending墓碑正文和全部原失败保留；元数据身份匹配不冒动态通过。用户库／真实provider／全面能力／M-1／后续面试／HTML／退出／Compose／Linux／Nginx／项目仍原关口。

## 以下为v0.91及更早历史
"""
    decision_prefix = f"""# TASK-103 / R-097 续作02普通回收与集中独立终审裁定

{at}，Codex编排Agent。续作02结果已实际返回，52856字节／8b544e505c574b0bc666ca8ebd651bf4275000848dbb9b2af8ad386cb835aa18，41022旧历史后缀精确保留。291完整文件／post、281未变基线、20保护／9规则合同全部核一致；本次回收320项hash与实际自有资源metadata，不是产品重跑或独立审计。

普通回收接受三项真实有限补证。no_evidence HTTP409零新增和六表／四账不变；陈旧真实POST409／草稿绑定保留加后批PG唯一效果；晚保存真实COMMIT回执下编辑epoch保护加后批PG一effect。显式身份切换另有回执／浏览器断言，没有最后独立PG快照，记录边界。三个根和两个browser总FAIL保持，剩余只读引用迟到仍NOT_RUN。

C02entry3／offline3触顶结束，start2／listener2／browser-driver2／build0／SUP0及3159.755主动、7.906离线、50.233真实、2.687清理、82.500元数据保守投入与旧账原样，不返或借余额。旧另一save已COMMIT但客户端未收到只读确认、不重发；R20／UNKNOWN及single_host_recovery=false保持。

没有新产品或SQL变化，候选实现已稳定。下一采用TASK104/R098完整集中隔离终审，并在审计许可中补最后GET／SELECT引用迟到；不是先判剩余通过，也不是主控或原实现者自审。依public允许终审按实际证据缺口定向验证，取消原先额外纯补卡的计划，不取消独立门槛。

104新A+隔离窗口只读产品，三轴审查并形成闭合G9建议；最多一次主组合和两次有据受影响复验，真实／fixture／精确资源上限见104卡。角色资源准备只精确本卡app一次RAM口令重置，不能修改业务或权限。任何产品缺陷由编排合并回103唯一修复路线，不在104修产品。

当前104整卡已保存回读，待转交，新使用0，无实际发送或开始。DEF019—022／G9／STEP／M-1／项目不提前关闭。原103结果、原任务卡、全部旧证据／产品／公共库／原始需求本次编排未写，唯一总状态见执行动态v2.14。

## 以下为续作01回收及更早裁定历史
"""
    saved = []
    saved.append(prepend("DocuS/执行动态文档.MD", state_prefix, old["DocuS/执行动态文档.MD"]))
    saved.append(prepend("DocuS/架构动态文档.MD", arch_prefix, old["DocuS/架构动态文档.MD"]))
    saved.append(prepend("DocuN/results/TASK-103-work-decision.md", decision_prefix, old["DocuN/results/TASK-103-work-decision.md"]))
    card = (OUT / "TASK-104-card.md").read_bytes()
    card_text = card.decode("utf-8")
    for heading in ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
                    "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]:
        assert "## " + heading in card_text
    assert "*" not in card_text
    task_path.write_bytes(card)
    assert task_path.read_bytes() == card
    descriptions = [
        (944, "DocuN/evidence/TASK-103/orchestration-receipt-03/receipt.json", "实际回收C02，291对象／post／原字节历史／三项原件与资源收尾核对，不签G9"),
        (945, "DocuN/results/TASK-103-work-decision.md", "置顶三项有限补证接收和集中终审＋最后只读引用的新完整安排，原许可结束／历史不改"),
        (946, "DocuS/架构动态文档.MD", "v0.92登记稳定候选及末尾只读性质，集中终审边界，不提前签G9或扩大证据"),
        (947, "DocuS/执行动态文档.MD", "v2.14登记C02实际返回／账封闭，正式占104/R098，独立新窗口和精确预算待转交"),
        (948, "DocuN/tasks/TASK-104.md", "完整七节G9独立代码／证据／控制终审与引用迟到GET补证，禁止产品修复与业务POST"),
        (949, "DocuN/evidence/TASK-104/orchestration-setup-20261007/audit-input.json", "冻结291对象／20保护／9规则合同／原始批准输入，隔离自评，末尾引用目标与读取界限"),
        (950, "DocuN/evidence/TASK-104/orchestration-setup-20261007/raw-evidence-navigation.json", "原始run／as-run／SQL／网络／PG／预算导航，三组旧总FAIL与子性质分层，不重新执行103"),
        (951, "DocuN/evidence/TASK-104/orchestration-setup-20261007/baseline-and-changes.json", "原233基线到最终产品完整实际差异范围，独立审读边界与旧生成资产保留导航"),
        (952, "DocuN/evidence/TASK-104/orchestration-setup-20261007/resource-permit.json", "新104只读组合许可、精确复用pg1／18103、角色口令唯一附条件、原余量不借"),
        (953, "DocuN/evidence/TASK-104/orchestration-setup-20261007/delivery-proof.json", "全文回读／版本／CHG／历史／291冻结／旧报告不变，实际发送与业务运行0")
    ]
    changelog = ROOT / "DocuS/文档变更记录.MD"
    assert changelog.read_bytes() == old["DocuS/文档变更记录.MD"]
    addition = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{at}，Codex编排Agent，{p}。{d}。" for n, p, d in descriptions) + "\n"
    changelog.write_bytes(old["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    assert changelog.read_bytes().startswith(old["DocuS/文档变更记录.MD"])
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    assert report.read_bytes() == (RECEIPT / "TASK-103-as-returned.md").read_bytes()
    for row in contracts:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    save("delivery-proof.json", {"at": at, "TASK": "TASK-104", "R": "R-098", "dispatch": "待转交",
        "versions": {"state": "v2.14", "architecture": "v0.92", "requirements": "v1.1"},
        "CHG": "0944—0953", "next_CHG": "0954", "next_task": "TASK105/R099未来计划未占号",
        "full_card_readback": True, "seven_sections": True, "managed_new_markdown_no_asterisks_or_tables": True,
        "histories": saved, "change_history_prefix_exact": True, "TASK103_report_unchanged": True,
        "TASK103_card_unchanged": True, "291_current_objects_unchanged": True,
        "nine_rules_contracts_unchanged": True, "new_usage": 0, "actual_sent_received_started": False,
        "root_product_write_SQL_start_test_build": 0, "card_path": str(task_path), "card_sha256": sha(card), "card_bytes": len(card),
        "new_result_created": False, "metadata_note": "首次探读误用result-history-proof.json文件名不存在，实际C02为history-proof.json已读取；非产品或执行Agent失败"})
    print(json.dumps({"TASK": "TASK-104", "R": "R-098", "dispatch": "待转交", "state": "v2.14", "architecture": "v0.92",
        "CHG": "0944—0953", "current_frozen": 291, "product_existing_changes": len(changed), "new_product_files": len(added),
        "card_bytes": len(card), "root_business_runs": 0, "history_preserved": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
