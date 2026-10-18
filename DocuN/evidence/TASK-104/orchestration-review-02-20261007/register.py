"""回收修复候选并登记原104只读增量，历史和产品字节保持。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-103/audit-repair-03"
RECEIPT = ROOT / "DocuN/evidence/TASK-103/orchestration-repair-03-receipt"
OUT = ROOT / "DocuN/evidence/TASK-104/orchestration-review-02-20261007"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    p = OUT / name
    assert not p.exists(), "不覆盖已有本轮登记"
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepend(rel, text, old):
    p = ROOT / rel
    assert p.read_bytes() == old, "共享文档并行变化，不能覆盖"
    prefix = (text.strip() + "\n\n").encode("utf-8")
    assert "*" not in text
    p.write_bytes(prefix + old)
    assert p.read_bytes()[len(prefix):] == old
    return {"path": rel, "prefix_bytes": len(prefix), "old_sha256": sha(old), "new_sha256": sha(p.read_bytes()), "history_exact": True}


def main():
    receipt = load(RECEIPT / "receipt.json")
    assert receipt["all_owned_stopped"] and receipt["no_listeners"]
    current = load(RECEIPT / "current-baseline.json")
    assert len(current) == 308
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report103 = ROOT / "DocuN/results/TASK-103-result.md"
    assert sha(report103.read_bytes()) == receipt["report_sha256"]
    report104 = ROOT / "DocuN/results/TASK-104-result.md"
    expected104 = "54306f7a9e7145f52ef22cdd8c99511f173f9674deda22f2418779ab32d48d3b"
    assert sha(report104.read_bytes()) == expected104 and len(report104.read_bytes()) == 21896
    old = {r["path"]: (RECEIPT / "before" / r["path"]).read_bytes() for r in load(RECEIPT / "before-manifest.json")}
    for rel, data in old.items():
        assert (ROOT / rel).read_bytes() == data
    assert "文档 v2.15" in old["DocuS/执行动态文档.MD"].decode("utf-8")[:300]
    at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    delta = load(BASE / "final/pre-diff-post.json")
    navigation = {
        "delta": [str(BASE / "final/pre-diff-post.json"), str(BASE / "final/product.patch")],
        "pre": str(BASE / "pre"), "current_post": str(BASE / "final/post"),
        "p1_real03": [str(BASE / "groups/real-03-r03-p1-unique-effect" / p) for p in ["result.json",
            "browser/result.json", "browser/p1-post-controller.json", "browser/p1-confirmed-refresh-controller.json",
            "persistent-command-proof.json", "pg-before.json", "pg-after.json"]],
        "real02_regression_and_citation": [str(BASE / "groups/real-02-r03-preloaded-targets" / p) for p in ["result.json",
            "browser/result.json", "browser/late-citation-controller.json", "pg-before.json", "pg-after.json"]],
        "fixture_and_network": str(ROOT / "frontend/tests/task103-r03-ui.cjs"),
        "version_and_accounting": [str(BASE / "final" / p) for p in ["runs-ledger.json", "bundle-chain.json", "accounting-final.json",
            "resources-after.json", "old-facts-preserved.json", "sql-backend-frozen.json"]],
        "raw_case_directories": [str(BASE / "groups/real-02-r03-preloaded-targets/browser"), str(BASE / "groups/real-03-r03-p1-unique-effect/browser")],
        "source_method": "依据run记录定位完整as-run与原始控制器/网络/DOM/截图/PG；real03前五项继承，回real01/02真执行，不据executed字段扩大",
        "excluded": "不读TASK103结果/自评/work-decision或实现聊天；本导航只给原目标、差异和原件位置"}
    for group in ["p1_real03", "real02_regression_and_citation", "version_and_accounting", "delta"]:
        assert all(Path(p).is_file() for p in navigation[group])
    save("raw-evidence-navigation.json", navigation)
    rules = load(BASE / "rules-verified.json")
    accounting = load(BASE / "final/accounting-final.json")
    save("review-input.json", {"at": at, "TASK": "TASK-104", "R": "R-098", "round": "review-02",
        "permit": "TASK-104-G9-REVIEW02-20261007", "parent": "TASK-103 / R-097 审计修复03",
        "current_files": current, "current_objects": 308, "pre_baseline_objects": 297,
        "actual_changes": delta, "rules_contracts": rules,
        "protected_files": load(ROOT / "DocuN/evidence/TASK-103/continuation-01/final/protected-files.json"),
        "current_source_SHA": {p: current[p] for p in ["frontend/src/activities/MemoryWorkspace.tsx", "frontend/src/activities/memoryIntents.ts"]},
        "old_audit_report": {"path": str(report104), "bytes": 21896, "sha256": expected104},
        "raw_navigation": str(OUT / "raw-evidence-navigation.json"),
        "root_ordinary_receipt": "308现有对象与308post/两pre/六加载副本/9执行记录身份核对；不是独立通过结论",
        "closed_old_permit": accounting,
        "new_seconds": {"active": 7200, "metadata": 1200}, "new_real_compile_test_build_PG_HTTP_browser_model_POST": 0,
        "new_actual_usage": 0, "dispatch": "待转交，无实际发送/接收/开始",
        "read_scope": "仅两文件及直接影响、准确P1/最后引用原件和最终版本/控制；其余自有104有效范围继承",
        "four_questions": ["F01及同链回归", "准确P1窗口和正常/恢复证据", "最后引用E01真实闭合", "最终身份/继承/控制适用性"],
        "resource_observation": load(RECEIPT / "resource-readonly.json"),
        "independence": "沿原104独立窗口，前101审计历史受限披露保持，未参与102/103，不读实现自评或聊天"})
    save("reuse-and-control.json", {"at": at, "old_scope": "原104完整33产品审查的未改范围、12函数/角色/legacy/v2/旧停止/权限/事实保持",
        "open": "DEF023/P1修复候选及R104-E01新直接证据均待独立review02，未关闭G9",
        "closed_defects_unchanged": "DEF019—022有限关闭，O01—03非阻断观察，不重开",
        "record_count": 9, "report_quantity_correction": "原103本轮正文写八份实际应9；不改其历史，自增量报告按9份核",
        "real02": "browser六类PASS、root末后夹具FAIL，不混同；准确新effect按real03",
        "real03": "本轮只新跑P1，其余五类自real01/02继承，不伪称第三根新跑全部",
        "memory_commands": "8个不同key/7effect/1同内容no-op，正常无新效果不改成缺陷或重复写",
        "new_execution": 0, "old_failed_batches": "real01/02、offline03及42旧根全部原件保留，预算与未知不清零"})
    source_prefix = f"""# TASK-103 / R-097 审计修复03回收裁定

{at}，Codex编排Agent。用户已带回修复候选，结果67135字节／58ff3590a8cbeb7cb6443a996359ccff6ed710a28f73bf39b262b6712d30429f，原52856字节历史后缀精确保留。308当前对象/308完整post、297基线pre及允许差异、9规则合同、24前端源/六实际加载身份、9执行记录普通核一致，资源再核停止，不等同独立通过。

接受两文件最小修复候选与准确P1、新引用直接原件。MemoryWorkspace增加实例/owner/完整绑定及read/edit授权，memoryIntents增加有条件IDB删除；dist新JS实际加载。后端/SQL/权限/TeachingCitations等未改。real03确认准确保存后refresh窗口新nonce真正effect；real02六类browserPASS有卸载/正常/早窗/引用，root末后夹具总FAIL保留，其他五类按来源继承，不扩签第三根重跑。

源/fixture最终版本与run记录可定位。实际是5offline/1build/3真实共9记录，原报告八份数量误写登记而不改历史。八key/七effect/一合法no-op原样；允许专用A/B修改不扩旧数据域，旧R20/UNKNOWN/不可变事实不退款或重发。

修复03许可封闭，offline5/5、口令设置2/2、build1/2、entry/start/listener/browser-driver3/6、POST8/12；主动3270.215/10800、offline/build9.079、real77.702、cleanup4.375、metadata98.266及保守/重叠/未知保留。42旧加3新入口合计45，不当45成功批，不借余量。

DEF023仍为修复候选待原104独立增量；E01当前已有原件也待独立有效性判断。现在派同104/R098 review02仅文件/原件复核，零运行，其他完整未改审查直接继承。新card待转交，实际使用0，原103窗口停止等待；原G9/STEP/M-1/项目均未最终通过。

## 以下为修复03授权及更早裁定历史
"""
    audit_prefix = f"""# TASK-104 / R-098 review-02增量接续裁定

{at}，Codex编排Agent。103审计修复03已真实返回，当前308对象及最终post、两源码pre与原104基线匹配，后端/SQL/权限和引用实现未改。普通接收候选与新增原件，不替代独立判断，原104不通过报告21896字节／54306f7a…保留。

同104/R098 review02待转交，沿实际完成104的A+独立窗口，不参与修复，原101审计历史的受限披露不重审。只四问：两文件身份/IDB/lifecycle同链修复与回归、准确P1控制窗口及正常证据、最后真实引用迟到E01、最终字节/继承/控制。原完整审查未变范围直接复用，不读103自评，不再开PG/API/browser或执行compile/test/build。

新许可TASK-104-G9-REVIEW02-20261007，active7200/metadata1200秒，真实与产品执行额度0，必要最多4页官方规范计metadata。旧104三个前置FAIL、旧许可/未知及103全部历史不清零，不重启旧控制器或修bootstrap。现在有新真实引用原件，按原始网络/DOM/PG判即可。

DEF023及G9仍待独立结论，DEF019—022有限关闭/O01—03非阻断保持。新使用0、无实际发送/接收/开始。完成后只当前差异/原件一次增量，编排依其结果最终裁定，不另占105。

## 以下为104首轮回收裁定历史
"""
    state_prefix = """# 执行动态文档

文档 v2.16，2026-10-07，Asia/Shanghai。唯一总状态账；需求v1.1、架构v0.94，task_model/阶段07。下面v2.15及全部历史原字节保留。

## TASK103修复候选回收；原104 review02只读增量

103/R097审计修复03已实际返回，普通回收候选与有效原件通过，未独立签DEF023/G9。结果67135字节/58ff3590…，14279新前缀/52856旧历史精确保留；308当前文件/308完整post、297基线pre、两源码+dist入口三改变/替换JS一删除保留pre/十二新增匹配。九规则合同、24前端源与六完整加载副本一致；源码身份检查317项不是317测试。

实际改MemoryWorkspace和memoryIntents，加入实例/owner/完整绑定/read-edit授权与IDB条件删除，保存确认后旧refresh不再主动抢回已离开身份；当前为修正候选，独立确认尚未完成。新JS index-GgrE4smT.js/773924/cdb6fa38…实际加载，CSS/pdf.worker原字节；后端/001—010/角色/权限/worker/关门/TeachingCitations及其他工作区未改，原104充分范围继承。

新增准确P1窗口取real03，真实COMMIT回执已交付、随后列表GET挂起时明确载入干净B，再释放旧GET后B身份/正文/新草稿保持、A详情请求增量0；A新nonce收据与PG一effect/head6对应。real02六类browserPASS含卸载/正常/早窗/真实引用迟到，对新活动0643576f…的明确身份不复活旧原文/位置、引用POST0，按原件时间与未改字节有据继承。

real01分页/按钮前置失败但A/B三effects已COMMIT；real02 root末后夹具把允许本轮M1更新判旧行变化而FAIL；offline03把同内容合法no-op当effect必须true而FAIL，原件全部保留。real03只新跑P1，其余五类继承，不据复制executed=true称再新跑六类。实际新run共9（5offline+1build+3真实），报告八份为数量误写，核证按真实9，不回写原历史或加产品阻断。

八POST八不同key，七effect和一合法同内容no-op，专用A/B不被旧活动选择，旧行除批准本轮M1版本字段外未变；不重复真实已COMMIT效果、不删除旧数据。引用原目标未受修订样本影响；旧command a392c565…requests4/cost4000/tool1/settled12/R20/UNKNOWN、recoveryfalse和不可变旧收据/pg2落点/pg3 pending全部保持。

修复03许可结束，offline5/5、口令设置2/2，entry/start/listener/browser-driver3/6、build1/2、POST8/12名义余额不恢复。主动3270.215/10800、offline/build9.079/600、real77.702/1200、cleanup4.375/300、metadata98.266/600；首读映射60、metadata40+20及重叠/未知保留，42旧根+3新=45不等于成功批。两次口令设置仅owned app RAM且属性ACL不改，SUP/model/tool/provider/迁移/create0。

当前编排只读核三CID/镜像/卷/标签/配额皆Stopped/Pid0，五端口无监听，产品/SQL/构建/测试/资源启动0。只对新字节/原件作普通回收，不重新执行103或104的已经结束runner。

同104/R098 review02整卡已保存回读，A+原实际独立窗口，调度待转交，新使用0，无实际发送/接收/开始。复核四问只两文件/直接影响、准确窗口/正常语义、新引用原件与最终版本控制；原完整33文件审查未改范围及旧结论直接继承，现阶段不再启PG/HTTP/browser/Windows/compile/test/build或重跑既有证明。

新许可TASK-104-G9-REVIEW02-20261007，主动7200/metadata1200秒、真实执行0，必要最多4页官方原文计metadata。首轮104失败/投入/披露不清零，原101隔离审计历史受限独立性保持，不以品牌重新审。DEF023仍待增量关闭，E01当前新增直接证据待独立采纳；DEF019—022有限关闭/O01—03非阻断跟踪不变。

G9/STEP013、M-1/项目/真实provider与后续面试/HTML/退出/Compose/Linux/Nginx门仍未整体通过，G8及已有验收/归档/规则/原始需求不变。105/R099仍未来计划未占号。用户仅需转原104卡并带回原结果路径，G9-P无需重批。

本批CHG0964—0973，下一CHG0974。

## 以下为v2.15及更早历史
"""
    arch_prefix = """# 架构动态文档

文档 v0.94，2026-10-07，Asia/Shanghai。需求v1.1、唯一执行动态v2.16。G9编辑身份修复与最后引用候选证据已返回，待原104只读增量，未签G9完成。下面v0.93及全部历史原字节保留。

## 编辑身份最小修正及新增证明

MemoryWorkspace候选以实例lifecycle、owner、完整绑定与读取/编辑epoch限定保存后的列表/选择/提示/错误续处理；memoryIntents新增同IDB事务回调中条件删除对应editor draft，保留新输入和新身份。正常保存/卸载/早窗与准确晚窗口已有直接原件，是否关闭DEF023由104增量独立判断。

引用实现与工作区挂载未改，实际现有引用GET200被暂停、旧面板卸载并打开新活动后尝试交付，旧原文/位置不复活、业务POST0的新证据可定位。前后PG只允许专用A/B样本字段/版本效果，旧角色/权限/十二函数/001—010/worker/停止/四账保持。合法同内容no-op不是新effect，不为夹具总FAIL重写历史。

24前端源经唯一build01与最终新JS/原CSS及六份实际加载副本绑定，旧JS保留pre但不能签新guard。只有两源码和生成物改变，其他33项原审查未受影响部分直接继承；原104 review02零运行核两文件、真实新原件和控制，不重复集中审计。

DEF019—022有限关闭、O01—03非阻断观察与单机边界不变。G9/STEP013/M-1/真实provider/全面能力/面试/HTML/退出/部署与项目关口保持，产品状态仍修复候选待独立增量。精确许可和任务调度见唯一执行动态v2.16。

## 以下为v0.93及更早历史
"""
    card = (OUT / "TASK-104-review-02-card.md").read_bytes()
    card_text = card.decode("utf-8")
    assert "*" not in card_text
    for h in ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
              "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]:
        assert "## " + h in card_text
    saved = []
    saved.append(prepend("DocuS/执行动态文档.MD", state_prefix, old["DocuS/执行动态文档.MD"]))
    saved.append(prepend("DocuS/架构动态文档.MD", arch_prefix, old["DocuS/架构动态文档.MD"]))
    saved.append(prepend("DocuN/results/TASK-103-work-decision.md", source_prefix, old["DocuN/results/TASK-103-work-decision.md"]))
    saved.append(prepend("DocuN/results/TASK-104-work-decision.md", audit_prefix, old["DocuN/results/TASK-104-work-decision.md"]))
    saved.append(prepend("DocuN/tasks/TASK-104.md", card_text, old["DocuN/tasks/TASK-104.md"]))
    changes = [
        (964, "DocuN/evidence/TASK-103/orchestration-repair-03-receipt/receipt.json", "回收修复候选308对象/完整post/两pre/六加载/实际9run原件/历史后缀/资源状态，不签独立通过"),
        (965, "DocuN/results/TASK-103-work-decision.md", "置顶修复03实际回收及许可封闭，原42+3入口/八键七effect一no-op/失败与继承分层保留"),
        (966, "DocuN/results/TASK-104-work-decision.md", "原104四问增量接续，只读零运行，不参与修复或重审全部G9"),
        (967, "DocuS/架构动态文档.MD", "v0.94同步身份/IDB/lifecycle候选、新引用真实证据和新bundle，未改后端权限继承"),
        (968, "DocuS/执行动态文档.MD", "v2.16登记103实际候选返回/旧账封闭/104review02待转交，DEF023和G9仍待独立"),
        (969, "DocuN/tasks/TASK-104.md", "置顶七节review02四问合同，原独立窗口/零测试启动/原报告21896历史不改"),
        (970, "DocuN/evidence/TASK-104/orchestration-review-02-20261007/review-input.json", "冻结308字节/297pre/两源码SHA/原104报告/规则合同与新只读预算，实际使用0"),
        (971, "DocuN/evidence/TASK-104/orchestration-review-02-20261007/raw-evidence-navigation.json", "指向real03准确P1/real02引用兼容/控制器DOMPG与as-run，不以自评或复制executed扩大证据"),
        (972, "DocuN/evidence/TASK-104/orchestration-review-02-20261007/reuse-and-control.json", "明确未改审查继承/合法no-op/实际9记录/原失败，避免多次复验或全面再审"),
        (973, "DocuN/evidence/TASK-104/orchestration-review-02-20261007/delivery-proof.json", "全文回读/七节/版本/编号/原字节历史/308源码/两个报告不变/新使用及实际派发0")
    ]
    change_path = ROOT / "DocuS/文档变更记录.MD"
    assert change_path.read_bytes() == old["DocuS/文档变更记录.MD"]
    addition = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{at}，Codex编排Agent，{p}。{d}。" for n, p, d in changes) + "\n"
    change_path.write_bytes(old["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    assert change_path.read_bytes().startswith(old["DocuS/文档变更记录.MD"])
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    for row in rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    assert sha(report103.read_bytes()) == receipt["report_sha256"] and sha(report104.read_bytes()) == expected104
    save("delivery-proof.json", {"at": at, "TASK": "TASK-104", "R": "R-098", "round": "review-02",
        "dispatch": "待转交", "state": "v2.16", "architecture": "v0.94", "CHG": "0964—0973", "next_CHG": "0974",
        "seven_sections_full_readback": True, "new_markdown_no_asterisks_or_tables": True, "histories": saved,
        "both_result_reports_unchanged": True, "current308_unchanged": True, "rule_contracts_unchanged": True,
        "new_actual_usage": 0, "actually_sent_received_started": False, "root_product_SQL_test_build_start": 0,
        "card_path": str(ROOT / "DocuN/tasks/TASK-104.md"), "card_prefix_bytes": len((card_text.strip() + "\n\n").encode("utf-8")),
        "card_sha256": sha((ROOT / "DocuN/tasks/TASK-104.md").read_bytes())})
    print(json.dumps({"TASK": "TASK-104", "R": "R-098", "round": "review-02", "dispatch": "待转交",
        "state": "v2.16", "architecture": "v0.94", "CHG": "0964—0973", "current_frozen": 308,
        "product_runs": 0, "histories_preserved": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
