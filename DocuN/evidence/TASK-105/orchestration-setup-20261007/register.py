"""完成G9有限验收并登记下一只读面试合同，编排不执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
CLOSE = ROOT / "DocuN/evidence/TASK-104/orchestration-close-20261007"
OUT = ROOT / "DocuN/evidence/TASK-105/orchestration-setup-20261007"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, value):
    assert not path.exists(), "已有登记不覆盖、不重复占号或派卡"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepend(rel, text, old):
    p = ROOT / rel
    assert p.read_bytes() == old, "共享文档已并行变化，停止覆盖"
    prefix = (text.strip() + "\n\n").encode("utf-8")
    assert "*" not in text
    p.write_bytes(prefix + old)
    assert p.read_bytes()[len(prefix):] == old
    return {"path": rel, "old_sha256": sha(old), "prefix_bytes": len(prefix), "new_sha256": sha(p.read_bytes()), "history_exact": True}


def main():
    receipt = load(CLOSE / "receipt.json")
    assert receipt["all_owned_stopped"] and receipt["no_listeners"]
    current = load(CLOSE / "current-baseline.json")
    assert len(current) == 308
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report104 = ROOT / "DocuN/results/TASK-104-result.md"
    report103 = ROOT / "DocuN/results/TASK-103-result.md"
    assert sha(report104.read_bytes()) == receipt["report_sha256"]
    assert sha(report103.read_bytes()) == "58ff3590a8cbeb7cb6443a996359ccff6ed710a28f73bf39b262b6712d30429f"
    old = {r["path"]: (CLOSE / "before" / r["path"]).read_bytes() for r in load(CLOSE / "before-manifest.json")}
    for rel, data in old.items():
        assert (ROOT / rel).read_bytes() == data
    assert "文档 v2.16" in old["DocuS/执行动态文档.MD"].decode("utf-8")[:300]
    task = ROOT / "DocuN/tasks/TASK-105.md"
    assert not task.exists() and not (ROOT / "DocuN/results/TASK-105-result.md").exists()
    at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    source_paths = [
        "backend/app/activities/repository.py", "backend/app/activities/service.py", "backend/app/activities/api.py",
        "backend/app/activities/teaching_repository.py", "backend/app/learning/contracts.py", "backend/app/learning/service.py",
        "backend/app/learning/teaching_contracts.py", "backend/app/learning/teaching_service.py",
        "backend/app/learning/teaching_views.py", "backend/app/learning/teaching_api.py",
        "backend/app/capabilities/contracts.py", "backend/app/capabilities/gateway.py",
        "backend/app/worker/one_call.py", "backend/app/worker/launcher.py", "backend/app/worker/session.py",
        "backend/app/memory/contracts.py", "backend/app/memory/context.py", "backend/app/memory/repository.py",
        "backend/app/service_config.py", "backend/app/main.py", "config/activity.example.json",
        "frontend/src/activities/ActivityWorkspace.tsx", "frontend/src/activities/TeachingWorkspace.tsx",
        "frontend/src/activities/teachingApi.ts", "frontend/src/activities/teachingIntents.ts",
        "frontend/src/activities/teachingDrafts.ts", "frontend/src/main.tsx",
        "backend/migrations/007_activity_operation_results.sql", "backend/migrations/008_activity_tool_budget.sql",
        "backend/migrations/009_teaching.sql", "backend/migrations/010_learning_memory.sql"]
    for rel in source_paths:
        assert (ROOT / rel).is_file(), "合同直接依赖路径缺失，不能猜路径转交"
    save(OUT / "source-baseline.json", {"at": at, "current_objects": 308, "current_files": current,
        "minimum_direct_inputs": [{"path": str(ROOT / p), "relative_path": p, "sha256": sha((ROOT / p).read_bytes())}
                                  for p in source_paths],
        "reading": "按函数/类型直接影响选读，非31文件全文强制通读；同窗未变材料复用",
        "existing_migrations": "001—010，设计下一编号建议须实际核，不创建",
        "no_runtime": True})
    acceptance = {"at": at, "TASK103": "R097批准G9实现与卡内定向验证有限验收关闭",
        "TASK104": "R098集中独立终审及review02有限验收关闭", "G9": "批准单机有限切片验收通过",
        "DEF023": "关闭，原R104-F01准确窗口修正与最终原件经独立确认", "R104_E01": "关闭，真实GET200/卸载Abort/新面板后尝试晚交付不复活范围",
        "source": {"current308": True, "audit_report": str(report104), "audit_sha256": receipt["report_sha256"],
                   "implementation_report": str(report103), "implementation_sha256": sha(report103.read_bytes()),
                   "accepted_raw_pointer_count": receipt["raw_pointer_count"]},
        "remaining_limits": ["原首轮/增量总FAIL及实际45根、no-op、未知/保守开销原样保留",
            "E01不冒客户端解析旧正文或专属阶段PG快照", "O01—03非阻断观察保留，DEF019—022按原有限域关闭",
            "R20/UNKNOWN不退款/结算/重发，单机/单会话边界保持", "用户库/真实provider/完整向量/数据退出/发布与项目Must未整体放行"],
        "STEP013": "本批准G9范围已实现并有限合成验收；完整跨功能/真实服务/退出恢复要求仍按018—020及017总验收",
        "next": "STEP014文字模拟面试，TASK105/R099只读完整最小实施合同，不实施未经采用的新模型包",
        "root_product_runs": 0}
    save(CLOSE / "final-acceptance.json", acceptance)
    source_prefix = f"""# TASK-103 / R-097 批准G9有限验收关闭

{at}，Codex编排Agent。依据原104集中审查及review02独立通过、当前308最终对象/完整post和58个原件指针绑定，103实现与批准单机有限G9的定向验证验收通过，任务103/R097关闭。DEF023/R104-F01与最后引用E01已闭合，原其他有效审查继承；不是实现者自签或重复跑测试。

最终报告67135字节/58ff3590…保持，10439639字节/ce2dba4f…及21896旧不通过历史精确保留。当前两源码/新bundle/准确竞态/正常及卸载/最后引用的独立适用性足够，无需追加运行。E01实际验证卸载Abort与新身份不复活，不能宣称客户端接纳旧正文或有引用专属PG快照。

原45真实入口、所有rootFAIL/browserPASS分层、八键七effect一合法no-op、元数据/cleanup重叠/未知、旧R20/UNKNOWN和全部预算保持封闭，不恢复余量，不删除合成资源或历史。O01—03非阻断观察及DEF019—022有限关闭保持；完整Must、M-1、真实provider、退出恢复/部署/项目未整体通过。

原103业务窗口已完成并释放，可承接新105/R099文字面试完整只读实施合同；本次未发送/开始105。任何新主要模型/公开语义待具体G10-P核证和必要采用，不借G9-P实施。

## 以下为修复候选回收及更早裁定历史
"""
    audit_prefix = f"""# TASK-104 / R-098 review02有限终审验收关闭

{at}，Codex编排Agent。review02实际返回，39639字节/ce2dba4f7b7fcb2ce0636bf1587b86b665b4ea3ab58172a04b33d43fd7cf6984及17743前缀/21896原历史一致，308最终对象/9规则合同/58原件指针匹配。接受本次代码/证据/控制三轴有限通过，结合首轮未改有效范围，104/R098验收关闭，批准G9单机有限切片可关闭。

DEF023/R104-F01及E01关闭，不扩展为任意迟到路径穷尽、原客户端解析旧正文或引用阶段独立PG快照。原104不通过/三个前置FAIL、自有metadata四错误及过宽截断/受限独立性披露不改。O01—03保留非阻断，旧DEF019—022有限域保持。

本次独立增量active1754.429/7200秒、metadata223.121/1200，含120/90保守项、部分精确11.621秒及未知分段，官方一页/上限四页。全部测试/产品/fixture/PG/HTTP/browser/资源/密码/POST执行0，许可结束，余量不作未来运行授权。本次编排仅核证/hash/精确资源只读，产品运行0。

下一按已批准STEP014只读收敛G10面试合同，由原业务窗口承接新105，104窗口保持独立并结束本卡。未来新高风险稳定成果按实际影响集中审计，不重新开G9闭合循环。

## 以下为review02接续与更早裁定历史
"""
    state_prefix = """# 执行动态文档

文档 v2.17，2026-10-07，Asia/Shanghai。唯一总状态账；需求v1.1、架构v0.95，task_model/阶段07。下面v2.16及全部历史原字节保留。

## G9有限验收关闭；STEP014文字面试合同待转交

104/R098 review02已实际返回，代码/新增证据/控制有限通过。39639字节/ce2dba4f…与交付及原21896字节不通过后缀一致，308最终对象/9规则合同和58真实原件指针匹配。根据其独立判定及首轮有效未改范围，编排验收关闭TASK103/R097、TASK104/R098与批准单机有限G9，关闭DEF023/P1/R104-F01和R104-E01；无该批准切片阻断补项。

F01准确回执确认后列表GET等待窗口经源码/新bundle/真实干净B完整身份/一次新效果核证；正常/卸载/早窗由原实际执行继承。E01真实服务GET200被挂起，卸载触发Abort，新活动加载后控制器尝试交付，旧原文/位置未复活、POST0；不声称客户端曾解析旧正文、解析后分支穷尽或有阶段专属PG快照。整根PG旧行/四账及允许专用A/B范围明确，不扩证据。

源两文件修复及24源/唯一build/六实际加载链稳定，后端/001—010/十二函数/角色ACL/worker/停止/旧预算权威未变。原首轮/各rootFAIL、real02 browserPASS而rootFAIL、real03五项继承、九份新记录、八POST七effect一no-op、所有原件/保守/未知保持，45根不是45成功批。R20/UNKNOWN不退款/结算/重发，recoveryfalse及单机边界不变，O01—03非阻断观察继续跟踪。

旧103与104所有许可封闭，名义余量不借。本次104review02 active1754.429/7200、metadata223.121/1200，首读120/文稿网页90保守、精确部分/未知及四metadata错误保留，官方1/4页，所有新业务/fixture/测试/PG/HTTP/browser/资源启动/密码/POST0。编排当前精确只读核三个CID/镜像/卷/标签/配额Stopped/Pid0，五相关端口无监听，不新增执行。

STEP013更新为本批准G9范围已实现/有限合成验收；原历史总表“未开始”不覆盖当前事实。完整跨功能/真实服务/导出恢复/长期质量等仍在STEP017—020及相应实际关口，没有因此签完整NFR005/全Must/M-1/项目。STEP009—012已实现有限闭环事实与G8有效验收保持，全文向量/真实provider及其他明确未覆盖项保留，不用未完成的远期门阻塞只读后续规划。

下一沿已批准路线进入STEP014/FR011文字模拟面试：资料/目标→问题→回答→必要追问→有依据反馈/显式继续/历史恢复，FR004/012、MOD006/FLOW002/DATA005。当前未有该产品闭环验收。本卡只读完成一个完整最小实施合同，不实施新接口/主要模型，不将面试硬塞教学掌握状态或放宽G9背景/工具权。

TASK105/R099已占号，G10面试完整合同，A+原实际TASK103业务窗口（此前承接102）继续，原103验收后已释放；原104不做方案，维持独立。完整七节合同已保存回读，调度待转交，新实际使用0，无实际发送/接收/开始。方案需A—D、具体数据/接口/配置/UI/版本/异常/恢复、一个必要实质批准包及未来定向验收，不按字段或页面分卡。

新许可TASK-105-G10-DESIGN-20261007，active10800/metadata900秒，所有产品/compile/test/build/PG/SQL/HTTP/app/Docker/browser/Windows/模型/工具/安装/付费/Git运行0；最多4页直接必要官方原文计metadata。只写105结果和design证据，不维护共享DocuS。优先函数/契约读入，同窗未变复用，不提前验证未来设计、不读取私有配置或用户真实简历。

面试输入与反馈必须区分自报/证据/假设，有据部分给予对应认可、不编造经历/测量效果，缺证据追问具体补充；不固定岗位/学科/题数，文字Must保持。若需新主要模型/公开语义/受信profile，先形成唯一G10-P具体包供核证后必要采用；设计授权不含真实库/角色/付费/外部发简历/部署权限，不重复空审批。

STEP015/016 HTML与B01/SEC003、017退出/备份恢复、018整链/Compose与Linux/Nginx边界、019风险独立验收、020本人自用交接仍按原批准Must，不默认豁免。Git只既有首提交授权，不自动新commit/push；Should/Could/公开发布非本次范围。G8/旧DEF001/002禁用、归档/规则/原始需求不变。

本批CHG0974—0984，下一CHG0985；下一TASK106/R100仅未来计划未占号。必要用户动作仅把105转原103业务窗口，完成带回105结果路径，G9不再反复确认或重验。

## 以下为v2.16及更早历史
"""
    arch_prefix = """# 架构动态文档

文档 v0.95，2026-10-07，Asia/Shanghai。需求v1.1、唯一执行动态v2.17。批准单机有限G9已验收关闭，下一STEP014文字模拟面试只读合同，产品未实施。下面v0.94及全部历史原字节保留。

## G9有效实现与有限验收边界

版本化用户记忆/有限观察、固定活动选用/依赖资格、v2背景及来源传播/失效公开读抑制、墓碑先行与唯一在线M3精确清理、工作区/本机意图/编辑身份/引用保护已实现并在批准范围独立终审通过。七表/十二函数/最小角色与旧不可变事实/四账/worker/停止权威保持；103/104及DEF023/F01、E01关闭，不扩大数据删除或远端权限。

准确旧保存续处理窗口修复、正常与未确认未改语义及最终构建加载已有独立原件。引用有限证明是服务200、卸载Abort及新面板后尝试晚交付不复活；没有客户端曾解析旧正文/所有解析后分支或专属PG阶段快照保证。旧FAIL/no-op/未知保留，O01—03非阻断观察待后续适用工作，不重开G9循环。

STEP013本批准实现与合成验收完成，整个Must/真实provider/完整向量/长期质量/退出备份/整链/权限/本人自用仍后续；本地记忆清理不承诺删除WAL/备份/远端字节。单机/单会话恢复及原未知预留边界不改。

## STEP014文字面试合同范围

沿FR011/012及FR004、MOD006/FLOW002/DATA005，下一只读收敛资料/目标、提问/回答/必要追问/有依据反馈、可修正目标/历史与显式继续/刷新恢复及可理解预算。共享现有受控模型/原子正文/事务/监督和意图权威，面试专用语义与旧教学掌握分开；记忆只背景，选用与失效不得绕G9受信消费类型。

TASK105只交唯一最小A—D实施合同、真实接口/文件差异、必要G10-P采用包和未来代表性验收矩阵。当前不新建表/迁移/公开接口/profile或运行模型；若主要模型/权限改变先形成具体包，不从设计推导实施许可。UI/数据/配置/失败/恢复作为一个完整成果，稳定点才一次实际风险集中审计。

HTML/面试之外Must、数据退出、Compose/Linux/Nginx交付边界与Git后续授权门保持。原始需求/公共规则不改，唯一调度与预算见执行动态v2.17。

## 以下为v0.94及更早历史
"""
    saved = []
    saved.append(prepend("DocuS/执行动态文档.MD", state_prefix, old["DocuS/执行动态文档.MD"]))
    saved.append(prepend("DocuS/架构动态文档.MD", arch_prefix, old["DocuS/架构动态文档.MD"]))
    saved.append(prepend("DocuN/results/TASK-103-work-decision.md", source_prefix, old["DocuN/results/TASK-103-work-decision.md"]))
    saved.append(prepend("DocuN/results/TASK-104-work-decision.md", audit_prefix, old["DocuN/results/TASK-104-work-decision.md"]))
    card = (OUT / "TASK-105-card.md").read_bytes()
    text = card.decode("utf-8")
    assert "*" not in text
    for h in ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
              "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]:
        assert "## " + h in text
    task.write_bytes(card)
    assert task.read_bytes() == card
    rules = load(ROOT / "DocuN/evidence/TASK-103/audit-repair-03/rules-verified.json")
    for row in rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    context_paths = ["AGENTS.md", "DocuS/最终需求文档.MD", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD",
                     "DocuN/results/TASK-103-work-decision.md", "DocuN/results/TASK-104-work-decision.md"]
    save(OUT / "design-input.json", {"at": at, "TASK": "TASK-105", "R": "R-099", "STEP": "STEP-014", "G": "G10",
        "mode": "task_model", "versions": {"requirements": "v1.1", "architecture": "v0.95", "state": "v2.17"},
        "rules_contracts": rules, "source_baseline": str(OUT / "source-baseline.json"),
        "current_context": [{"path": str(ROOT / p), "sha256": sha((ROOT / p).read_bytes())} for p in context_paths],
        "design_inputs": source_paths, "accepted_predecessor": str(CLOSE / "final-acceptance.json"),
        "existing_route": "STEP014已有Must；当前仅设计收敛。015/016HTML、017退出、018整链Compose/Linux/Nginx、019权限、020自用后续保持",
        "new_permit": "TASK-105-G10-DESIGN-20261007", "seconds": {"active": 10800, "metadata": 900},
        "official_pages_max": 4, "actual_new_runtime": 0, "dispatch": "待转交", "assigned": "A+原TASK103业务方案窗口",
        "privacy_and_authority": "本地合同只读；无用户简历/私配/密钥/真实库/新model/新公开接口写权；实质新增先具体G10-P",
        "expected": "A—D一次完整交付，一次文档一致性检查，不产品测试；结果TASK105-result.md",
        "new_goal_created": False, "actual_sent_received_started": False})
    save(OUT / "task-registration.json", {"at": at, "TASK": "TASK-105", "R": "R-099", "dispatch": "待转交",
        "window": "原TASK103实现/方案窗口，已完成验收释放", "tier": "A+", "type": "只读完整实施合同",
        "independent_window": "104保留审计职责，不接设计", "front_conditions": "批准需求路线与G3—G9有限资产够用，不假称父全Must已经完成",
        "scope": "STEP014/文字面试，公开/持久/profile新包仅建议未批准", "new_actual_usage": 0})
    changes = [
        (974, "DocuN/evidence/TASK-104/orchestration-close-20261007/receipt.json", "核39639报告/21896历史/308最终字节/58指针及F01/E01有限原件，精确资源停止，运行0"),
        (975, "DocuN/evidence/TASK-104/orchestration-close-20261007/final-acceptance.json", "编排验收关闭103/104/批准有限G9和DEF023/E01，保留旧失败/不确定/非阻断观察和后续Must"),
        (976, "DocuN/results/TASK-103-work-decision.md", "置顶有限实现验收关闭、原许可封闭、释放原业务窗口供新105，原字节历史保留"),
        (977, "DocuN/results/TASK-104-work-decision.md", "置顶独立终审有限验收关闭/1754.429主动/223.121metadata/运行0，原受限与失败不改"),
        (978, "DocuS/架构动态文档.MD", "v0.95登记G9实现/有限通过，下一文字面试主链合同与原批准数据/权限/删除边界"),
        (979, "DocuS/执行动态文档.MD", "v2.17关闭G9任务/阻断并更新STEP013实际有限状态，正式占105/R099/零运行设计预算待转交"),
        (980, "DocuN/tasks/TASK-105.md", "完整七节A—D文字面试合同任务，一包必要采用/完整实现计划与验收，原窗口强资源，零产品写入"),
        (981, "DocuN/evidence/TASK-105/orchestration-setup-20261007/source-baseline.json", "冻结308对象与31直接接口/源码/迁移输入，函数定向读，不逼全文通读或设计前测试"),
        (982, "DocuN/evidence/TASK-105/orchestration-setup-20261007/design-input.json", "正式需求/架构/状态/裁定指纹及新设计许可与必要边界，未签新G10-P"),
        (983, "DocuN/evidence/TASK-105/orchestration-setup-20261007/task-registration.json", "新105/R099待转交/原103窗口释放/104独立保留，真实发送和使用0"),
        (984, "DocuN/evidence/TASK-105/orchestration-setup-20261007/delivery-proof.json", "断点核对后完成状态关闭/全文七节回读/历史/308不变/输入路径与版本，产品运行0")
    ]
    log = ROOT / "DocuS/文档变更记录.MD"
    assert log.read_bytes() == old["DocuS/文档变更记录.MD"]
    addition = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{at}，Codex编排Agent，{p}。{d}。" for n, p, d in changes) + "\n"
    log.write_bytes(old["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    assert log.read_bytes().startswith(old["DocuS/文档变更记录.MD"])
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    assert sha(report104.read_bytes()) == receipt["report_sha256"]
    assert sha(report103.read_bytes()) == "58ff3590a8cbeb7cb6443a996359ccff6ed710a28f73bf39b262b6712d30429f"
    for row in rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    save(OUT / "delivery-proof.json", {"at": at, "closed": ["TASK103/R097", "TASK104/R098", "批准单机有限G9", "DEF023/F01", "R104-E01"],
        "TASK": "TASK-105", "R": "R-099", "dispatch": "待转交", "versions": {"state": "v2.17", "architecture": "v0.95"},
        "CHG": "0974—0984", "next_CHG": "0985", "next_TASK_R": "TASK106/R100未来计划未占号",
        "seven_sections_full_readback": True, "managed_new_markdown_no_asterisks_or_tables": True, "histories": saved,
        "both_reports_unchanged": True, "current308_unchanged": True, "rule_contracts_unchanged": True,
        "minimum31_paths_real": True, "new_execution_usage": 0, "actually_sent_received_started": False,
        "root_product_SQL_test_build_start": 0, "card_path": str(task), "card_bytes": len(card), "card_sha256": sha(card)})
    print(json.dumps({"closed": "批准单机有限G9/103/104/DEF023/E01", "TASK": "TASK-105", "R": "R-099",
        "dispatch": "待转交", "state": "v2.17", "architecture": "v0.95", "CHG": "0974—0984",
        "sources_frozen": 308, "minimum_inputs": len(source_paths), "product_runs": 0, "histories_preserved": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
