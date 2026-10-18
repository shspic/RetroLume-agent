"""串行登记续作01实际回收和续作02合同，不执行产品或验证任务。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-103"
OUT = BASE / "orchestration-receipt-02"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_new(path, obj):
    if path.exists():
        raise RuntimeError("目标已存在，不能覆盖编排记录")
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepend(rel, text, old):
    current = ROOT / rel
    if current.read_bytes() != old:
        raise RuntimeError("共享文档发生并行漂移，先保留双方成果")
    prefix = (text.strip() + "\n\n").encode("utf-8")
    current.write_bytes(prefix + old)
    assert current.read_bytes()[len(prefix):] == old
    return {"path": rel, "prefix_bytes": len(prefix), "old_bytes": len(old),
            "old_sha256": sha(old), "new_sha256": sha(current.read_bytes()), "history_exact": True}


def main():
    receipt = load(OUT / "receipt.json")
    assert receipt["all_owned_stopped_verified"] and receipt["no_target_listeners"]
    assert receipt["current_sources"] == 281
    baseline = load(OUT / "current-baseline.json")
    report_path = ROOT / "DocuN/results/TASK-103-result.md"
    assert sha(report_path.read_bytes()) == receipt["report_sha256"]
    before = load(OUT / "before-manifest.json")
    old = {r["path"]: (OUT / "before" / r["path"]).read_bytes() for r in before}
    for rel, data in old.items():
        assert (ROOT / rel).read_bytes() == data
    assert "DEF022" not in old["DocuS/执行动态文档.MD"].decode("utf-8")
    assert "DEF-022" not in old["DocuS/执行动态文档.MD"].decode("utf-8")
    for rel, expected in baseline.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    bindings = load(OUT / "finite-binding-checks.json")
    rules = load(BASE / "continuation-01/final/rules-contracts-final.json")
    accounting = load(BASE / "continuation-01/final/accounting-final.json")
    prefix_file = OUT / "TASK-103-continuation-02-card.md"
    card = prefix_file.read_bytes()
    card_text = card.decode("utf-8")
    required = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
                "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    assert all("## " + h in card_text for h in required)
    assert "*" not in card_text
    input_path = BASE / "continuation-02-input.json"
    input_record = {
        "at": at, "TASK": "TASK-103", "R": "R-097", "continuation": "02", "permit": "TASK-103-G9-C02-20261007",
        "current_files": baseline, "current_file_count": 281,
        "current_report": {"path": str(report_path), "bytes": receipt["report_bytes"], "sha256": receipt["report_sha256"]},
        "current_rules_contracts": rules,
        "protected_files": load(BASE / "continuation-01/final/protected-files.json"),
        "previous_ended_permit": accounting,
        "first_ended_accounting": str(BASE / "final/accounting-final.json"),
        "resources": load(OUT / "resource-readonly.json"),
        "actual_bundle": bindings["dist"],
        "sql_raw_and_text_hash_domains": {"raw": bindings["migration_raw_bytes_sha256"], "text_LF": bindings["migration_universal_newline_text_sha256"]},
        "new_limit_seconds": {"active": 7200, "offline_and_build": 600, "real": 1200, "cleanup": 300, "metadata": 300},
        "new_count_limits": {"entry": 3, "container_start": 3, "listener_start": 3, "browser": 3, "driver": 3,
                             "offline": 3, "build": 1, "sup": 2, "container_create": 0, "volume_create": 0, "role_create": 0},
        "sup_condition": "默认0，只在旧真实引用目标全部不合格时准备最小新合法引用，最多2；no_evidence负例SUP0",
        "new_usage": 0, "dispatch": "登记准备，全文回读后待转交；无实际发送或执行",
        "card_prefix_sha256": sha(card), "card_prefix_bytes": len(card),
        "expected_receipt_checks": ["晚到真实保存回执", "晚到真实引用响应", "浏览器真正陈旧POST409", "最终no_evidence真实HTTP零副作用"],
        "unknown_preserved": "a392c565-1731-4314-b22e-6cee9458f862，R20及UNKNOWN不结算、不退款、不重发",
        "root_product_changes": 0, "root_business_runs": 0
    }
    save_new(input_path, input_record)
    save_new(OUT / "metadata-verification-correction.json", {
        "at": at, "操作": "编排纯读取／hash／AST／只读inspect",
        "首次命令": "backend/.venv/Scripts/python.exe -B DocuN/evidence/TASK-103/orchestration-receipt-02/receive.py",
        "首次退出": 1, "首次耗时秒": 8.1687477,
        "根因": "编排首次比较将CRLF原文件字节哈希和package.py read_text统一换行文本哈希混为同域",
        "修正": "分别核原字节与LF文本，并直接重建十二函数指纹对照应用与原catalog；保留已写回收记录，不覆盖原证据",
        "复查退出": 0, "复查耗时秒": 4.366166,
        "结论": "两个哈希域均匹配，无产品或SQL漂移；不是执行Agent失败，不占其新执行额度",
        "raw_sha256": bindings["migration_raw_bytes_sha256"],
        "text_LF_sha256": bindings["migration_universal_newline_text_sha256"],
        "产品运行": 0
    })
    save_new(OUT / "defect-source-records.json", {
        "DEF019": {"等级": "P2", "状态": "原最小精度修复及有效离线证据继承，待完整成果独立确认"},
        "DEF020": {"等级": "P2", "状态": "候选修复，续作01真实普通continue409／中文／零SUP已核原件；待独立终审"},
        "DEF021": {"等级": "P2", "状态": "候选修复，续作01实际damaged可辨legacy及残迹拒绝已核有限原件；待独立终审"},
        "DEF022": {"等级": "P2", "归属": "TASK-103 / R-097", "问题": "TeachingService抛LearningRefusal/no_evidence时教学HTTP未按既定错误拒绝语义接住",
                   "候选修正": "teaching_api.py捕获LearningRefusal并映射no_evidence为409，源码与offline06 pre500/final409原件已有",
                   "未验": "最终真实HTTP、合法鉴权和PG零新增事实尚缺；续作02同一主根补，不另开设计或实施卡",
                   "状态": "修复候选，真实补证与独立确认前不关闭"}
    })
    save_new(OUT / "evidence-reuse-navigation.json", {
        "receipt": str(OUT / "receipt.json"), "finite_bindings": str(OUT / "finite-binding-checks.json"),
        "current_baseline": str(OUT / "current-baseline.json"),
        "current_final_post": str(BASE / "continuation-01/final/post"),
        "reuse": "未变V01—V24子性质、SQL三函数、工具、兼容、传播、权限、旧SUP与已成立浏览器性质按实际字节及前提继承",
        "remaining": input_record["expected_receipt_checks"],
        "old_failures": "初轮三browser总FAIL，续作01browser01/02总FAIL、03尾链，全部原UNKNOWN和计数不改",
        "audit": "稳定完整后才派计划TASK104/R098，当前未占号或实际派发"
    })
    state_prefix = """# 执行动态文档

文档 v2.13，2026-10-07，Asia/Shanghai。唯一总状态账；需求v1.1，架构v0.91，task_model／阶段07。下面v2.12及全部历史原字节保留。

## TASK103续作01实际回收；最后四项合并接续

用户带回原路径，103/R097续作01已实际返回。普通回收部分通过，接受已保存候选、可定位子性质与收尾；完整G9尚未验收，未启动独立审计。结果41022字节／SHA fe80b616…，续作01前缀16671字节、初轮24351字节后缀精确保留。281现有对象与281完整post一致，20保护对象、9规则／合同、七锁定规则匹配；原266基线中8改变／16新增／1替换JS删除，原资产pre保留。

十二函数源码／应用指纹／原始pg1与pg3 catalog一致；三函数前向更新行hash、安全属性不变，pg2原反向DDL后的14表32行保留。纯回收首次把CRLF字节hash与LF文本hash混为一域导致assert失败，已核明确两域与十二函数；不是产品／SQL漂移，记录保留，不占执行者预算。最终24份前端源码与build01及实际JS／CSS加载对应；浏览器03只是尾链PASS，01／02总FAIL照实。

续作01核心SQL、工具标量、同answer反馈／两层闭包、PDF与来源／并发／异常清理、legacy有限降级和主工作区已有真实子证据。DEF020普通continue409、DEF021可辨legacy／残迹失败关闭的有限真实证明已补，仍为修正候选待独立终审；DEF019原有效精度离线证据继承。未将未观察的时态、事件9／上游15、真实provider／离线全库回滚等扩大为已验。

仍缺四项直接证据。V15保存响应晚到、引用响应晚到、浏览器陈旧revision实际POST；旧409仅impact GET。另登记DEF022/P2，最终teaching_api新增LearningRefusal捕获／no_evidence409映射只有offline06异常替身ASGI证据，真实鉴权／PG零写待补。四项一张同103续卡，不增加G9采用审批或逐项审计。

续作01许可结束，entry12/12、browser／driver3/3、offline6/6触顶；build1/2、start14/16、listener3/6、SUP22/24名义余量不恢复执行权。主动12072.453/21600秒，offline/build12.641、real233.702、cleanup13.513、metadata413.812；元数据保守及offline03外壳导入失败晚记次数偏差原样保留。初轮全部旧投入、24根／三browserFAIL／未知及原失败不清零。

22次真实SUP、20有限传输发送／1工具，21已结算R0；失败command a392c565-1731-4314-b22e-6cee9458f862树零但requests4／cost4000／tool1／settled12／R20及UNKNOWN保留，不代结算、退款、重发或开恢复。未把无底层异常的worker失败归因为性能或夹具。

续作02同TASK103/R097已登记，接收A+原实际103业务窗口，强推理资源；完整七节合同已回读，调度待转交，新实际使用0，无实际发送／接收／开始事实。新许可TASK-103-G9-C02-20261007，主动7200／离线构建600／真实1200／独立收尾300／metadata300秒；根3、pg1 start3、listener3、browser／driver各3、offline3、build1。预期一个主根四项一次完成，最多两次有据受影响复验，旧失败不返额。同根因两次有据修正仍失败或真实前提不稳即停。

默认SUP0；只有当前已有真实引用均不合格时允许最小新合法引用准备最多2SUP，仍有限合成无外网／付费，no_evidence负例SUP0。W20／manager50／lease20／single_host_recovery=false保持。没有新容器／卷／角色／DDL许可，pg2／3只读metadata保持停止。产品默认冻结，只允许直接UI或本错误映射的确证最小修复及一次必要build。

编排当前只读核三精确CID／镜像／卷／旧permit标签／配额皆匹配、Stopped/Pid0；五相关端口无监听。只可在新许可内复用pg1 CID4889202d…及18103，不复位库或删除旧样本。保护原不可变M5、pg3 pending正文、旧pg2反向落点。所有新动作由执行者自己在C02前计数，不重启C01入口绕原触顶。

稳定完整候选后才占计划TASK104/R098集中隔离增强审计，当前未出卡、未占号。G9／STEP013、M-1、真实provider、其他Must与Compose／Linux／Nginx／项目交付未通过；G8及早前有效验收、DEF001／002禁用、归档／规则／原始需求均保持。本次编排产品／SQL／测试／构建运行0，只核证和更新共享文档。

本批CHG0934—0943，下一CHG0944。必要用户动作仅转同103续作02整卡并带回原结果路径，不重问批准。

## 以下为v2.12及更早历史
"""
    arch_prefix = """# 架构动态文档

文档 v0.91，2026-10-07，Asia/Shanghai。需求v1.1，唯一执行动态v2.13。G9核心剩余实现与直接子证据已返回，最后四项待同103续作02；不签完整G9。下面v0.90及全部历史原字节保留。

## G9续作01实际候选与最终补证边界

010仍七表与既有角色；activity_memory_eligible、purge_learning_memory、memory_final_shape_guard三函数实际前向到最终指纹，原行和安全属性保持，十二函数源码／应用／真实catalog一致。CRLF原字节与read_text统一换行文本hash是两个口径，不是部署不一致；原pg2反向DDL结果保持，未新增模型／权限。

memory schema分类现在按实际结构／权限／不可变M6及v2残迹分级，已可可靠识别的无选择legacy保留旧行为，缺绑定／有残迹／不可辨仍关闭；DEF020错误映射和DEF021有限兼容已有候选真实证明，待集中独立确认。合法calc标量重建、教学recipe批读、同answer反馈／两层闭包和依赖传播补实际证据，不重跑旧四账／停止／退款主体。

MemoryWorkspace候选以读取／编辑epoch、IDB owner和完整绑定身份防迟到覆盖，已有慢真实GET／输入旧绑定／明确载入原子切换等证明；TeachingCitations序列及Abort边界保持。最后待实际晚到保存回执／引用响应、双页真正陈旧POST409，不能用旧impact GET409或源码说明签全性质。最后no_evidence捕获409映射登记DEF022/P2修复候选，需要同主根真实鉴权／PG零副作用确认，ASGI异常替身范围不能扩签。

续作02仅四项合并，默认产品／SQL冻结，允许直接界面或错误映射确证最小修正，源码改变才一次构建并复验受影响部分。不增持久模型、部署／角色、worker／SUP协议或新平台；原UNKNOWN／R20、不可变收据／旧样本、单机／单会话限制保持。当前281完整post／前端24源／实际加载dist身份一致，不凭这些静态身份签动态全绿。

完整候选稳定后一次集中隔离增强审计；当前TASK104/R098仅计划。G8已有关闭不重开，G9／STEP013、真实provider、全面能力、M-1、后续面试／HTML／退出与Compose／Linux／Nginx／项目门不提前通过。精确许可与唯一进度见执行动态v2.13。

## 以下为v0.90及更早历史
"""
    decision_prefix = f"""# TASK-103 / R-097 续作01回收与续作02裁定

{at}，Codex编排Agent。用户已带回真实续作01结果。普通回收部分通过，当前281对象与281完整post、20保护／9规则合同／7锁定输入一致，原24351字节历史精确保留；结果41022字节／fe80b6161bff72942a09bb3ef8cb5a61e507aa42015f149aa9e3495fed1591c3。十二函数及最终24份前端源码／加载bundle已按原始记录核身份，不等同独立审计。

接受已完成核心子性质及精确资源收尾，仍不关闭完整G9或共享DEF。C01 entry12／browser-driver3／offline6触顶结束，主动12072.453与全部旧尝试／UNKNOWN保留，不借剩余SUP／start或时间。初次编排metadata混用CRLF／LF哈希已核清并留证，不计为产品失败。

未完成仅V15晚到保存响应、晚到引用响应、浏览器真陈旧POST及最后no_evidence映射真实HTTP零效应。DEF020／021已有真实有限候选证明；新增DEF022/P2从LearningRefusal源码与offline06 pre500/final409确定，修正候选已保存，真实补证同卡，独立审计前不关闭。

续作02获准按完整七节卡合并四项，A+原实际103窗口，G9-P已批准不重复问。新许可TASK-103-G9-C02-20261007，7200主动／600离线构建／1200真实／300收尾／300metadata秒及3根／3start／3listener／3browser-driver／3offline／1build，新使用0。默认SUP0，仅无法复用真实current引用目标时最多2有限合成SUP。一个主根预期足够，其余最多两次有据受影响复验，同根因两修仍败即停；不扩大数据模型或SQL写权。

精确pg1可复用，pg2／3只读metadata维持停止。产品默认冻结，只修直接四项的确证界面／本错误映射缺陷；源改变才构建／复验。旧失败R20／UNKNOWN、pending墓碑／正文、旧非规范M5收据／反向DDL和全部原计数保持；不伪citation／receipt，不用impact GET替代实际POST。

卡全文与当前基线已回读，待用户转交，无实际派发／接收／开始证据。稳定完整G9后才派计划104/R098集中隔离审计。原文结果／公共库／原始需求／产品本次编排零写，唯一总状态为执行动态v2.13。

## 以下为首轮回收和续作01历史裁定
"""
    saved = []
    saved.append(prepend("DocuS/执行动态文档.MD", state_prefix, old["DocuS/执行动态文档.MD"]))
    saved.append(prepend("DocuS/架构动态文档.MD", arch_prefix, old["DocuS/架构动态文档.MD"]))
    saved.append(prepend("DocuN/results/TASK-103-work-decision.md", decision_prefix, old["DocuN/results/TASK-103-work-decision.md"]))
    saved.append(prepend("DocuN/tasks/TASK-103.md", card_text, old["DocuN/tasks/TASK-103.md"]))
    changes = [
        (934, "DocuN/evidence/TASK-103/orchestration-receipt-02/receipt.json", "续作01普通回收部分候选、281完整快照／保护输入／三容器收尾，四项待补，不签G9"),
        (935, "DocuN/evidence/TASK-103/orchestration-receipt-02/finite-binding-checks.json", "直接核十二函数源码／应用／真实catalog、原行／bundle链；CRLF原字节和LF文本口径分列，回收metadata初错留证"),
        (936, "DocuN/results/TASK-103-work-decision.md", "置顶真实续作01回收和续作02四项合并裁定，旧裁定原字节保留，G9-P不重批"),
        (937, "DocuN/evidence/TASK-103/orchestration-receipt-02/defect-source-records.json", "020／021真实候选证明接收，新增022/P2最后no_evidence映射候选及实际HTTP缺口，019继承待终审"),
        (938, "DocuS/架构动态文档.MD", "v0.91同步三函数／精准legacy／工具重建／epoch／最终映射候选，最后四项与集中审计边界"),
        (939, "DocuS/执行动态文档.MD", "v2.13登记续作01实际返回与已结束账、续作02新精确许可和待转交，同根因旧失败／UNKNOWN不清零"),
        (940, "DocuN/tasks/TASK-103.md", "置顶完整七节续作02，一根合并三浏览器子项＋末尾HTTP，最小复验余量与冻结写域，旧合同原字节保留"),
        (941, "DocuN/evidence/TASK-103/continuation-02-input.json", "冻结281现有对象／当前41022结果／9规则合同／20保护／原账和精确资源，新执行使用0"),
        (942, "DocuN/evidence/TASK-103/orchestration-receipt-02/evidence-reuse-navigation.json", "分明已成立有限性质、原总FAIL／UNKNOWN、剩余四项与未来独立审计，不扩大复跑"),
        (943, "DocuN/evidence/TASK-103/orchestration-receipt-02/delivery-proof.json", "全文回读／历史后缀／输入／版本号／281产品冻结核对，实际发送与产品运行0")
    ]
    change_text = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{at}，Codex编排Agent，{path}。{message}。" for n, path, message in changes) + "\n"
    changelog = ROOT / "DocuS/文档变更记录.MD"
    assert changelog.read_bytes() == old["DocuS/文档变更记录.MD"]
    changelog.write_bytes(old["DocuS/文档变更记录.MD"] + change_text.encode("utf-8"))
    assert changelog.read_bytes().startswith(old["DocuS/文档变更记录.MD"])
    saved.append({"path": "DocuS/文档变更记录.MD", "old_sha256": sha(old["DocuS/文档变更记录.MD"]),
                  "new_sha256": sha(changelog.read_bytes()), "history_exact": True})
    assert report_path.read_bytes() == (OUT / "TASK-103-as-returned.md").read_bytes()
    for rel, expected in baseline.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    for row in rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    for text in [state_prefix, arch_prefix, decision_prefix, change_text]:
        assert "*" not in text
    delivered_card = (ROOT / "DocuN/tasks/TASK-103.md").read_bytes()
    prefix_bytes = (card_text.strip() + "\n\n").encode("utf-8")
    assert delivered_card[:len(prefix_bytes)] == prefix_bytes
    assert delivered_card[len(prefix_bytes):] == old["DocuN/tasks/TASK-103.md"]
    save_new(OUT / "delivery-proof.json", {"at": at, "TASK": "TASK-103", "R": "R-097", "continuation": "02",
        "state": "v2.13", "architecture": "v0.91", "CHG": "0934—0943", "next_CHG": "0944",
        "future_audit": "TASK104/R098计划，未占号／未出卡", "dispatch": "待转交",
        "new_actual_usage": 0, "full_card_readback": True, "seven_sections_present": True,
        "new_managed_markdown_no_asterisk_or_table": True, "shared_histories_exact": saved,
        "returned_report_unchanged": True, "current281_unchanged": True, "nine_rule_contract_inputs_unchanged": True,
        "actual_product_write_run_build_SQL_or_start": 0, "actual_sent_or_received": False,
        "card_path": str(ROOT / "DocuN/tasks/TASK-103.md"), "card_prefix_bytes": len(prefix_bytes),
        "card_sha256": sha(delivered_card), "input_sha256": sha(input_path.read_bytes())})
    print(json.dumps({"状态": "续作02整卡已保存并回读，待转交", "TASK": "TASK-103", "R": "R-097",
        "状态版本": "v2.13", "架构版本": "v0.91", "CHG": "0934—0943", "源码变更": 0,
        "产品运行": 0, "历史保留": True, "卡路径": str(ROOT / "DocuN/tasks/TASK-103.md")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
