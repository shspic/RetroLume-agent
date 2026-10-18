"""登记104审查裁定和103唯一修复路线，不接管执行层。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
R104 = ROOT / "DocuN/evidence/TASK-104/orchestration-receipt-01"
OUT = ROOT / "DocuN/evidence/TASK-103/orchestration-repair-03-20261007"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, value):
    assert not path.exists(), "不重复或覆盖现有编排登记"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepend(rel, text, old):
    path = ROOT / rel
    assert path.read_bytes() == old, "共享状态存在并行变化，不能覆盖"
    prefix = (text.strip() + "\n\n").encode("utf-8")
    assert "*" not in text
    path.write_bytes(prefix + old)
    assert path.read_bytes()[len(prefix):] == old
    return {"path": rel, "prefix_bytes": len(prefix), "old_sha256": sha(old), "new_sha256": sha(path.read_bytes()), "history_exact": True}


def main():
    receipt = load(R104 / "receipt.json")
    assert receipt["all_owned_stopped"] and receipt["no_listeners"]
    current = load(R104 / "current-baseline.json")
    assert len(current) == 297
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report104 = ROOT / "DocuN/results/TASK-104-result.md"
    assert sha(report104.read_bytes()) == receipt["report_sha256"]
    report103 = ROOT / "DocuN/results/TASK-103-result.md"
    expected103 = "8b544e505c574b0bc666ca8ebd651bf4275000848dbb9b2af8ad386cb835aa18"
    assert sha(report103.read_bytes()) == expected103 and len(report103.read_bytes()) == 52856
    old = {r["path"]: (R104 / "before" / r["path"]).read_bytes() for r in load(R104 / "before-manifest.json")}
    for rel, data in old.items():
        assert (ROOT / rel).read_bytes() == data
    state_old = old["DocuS/执行动态文档.MD"].decode("utf-8")
    assert "文档 v2.14" in state_old[:400] and "DEF023" not in state_old and "DEF-023" not in state_old
    assert not (ROOT / "DocuN/results/TASK-104-work-decision.md").exists()
    at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    card = (OUT / "TASK-103-repair-03-card.md").read_bytes()
    card_text = card.decode("utf-8")
    for h in ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
              "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]:
        assert "## " + h in card_text
    assert "*" not in card_text
    frozen_rules = load(ROOT / "DocuN/evidence/TASK-103/continuation-02/rules-verified.json")
    for row in frozen_rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    input_record = {"at": at, "TASK": "TASK-103", "R": "R-097", "round": "审计修复03",
        "permit": "TASK-103-G9-R03-20261007", "current_files": current, "current_files_count": 297,
        "previous291_unchanged": True, "extra104_harness_files": 6,
        "original_goal_rules": frozen_rules,
        "protected_files": load(ROOT / "DocuN/evidence/TASK-103/continuation-01/final/protected-files.json"),
        "audit_report": {"path": str(report104), "sha256": receipt["report_sha256"], "bytes": receipt["report_bytes"]},
        "implementation_history": {"path": str(report103), "sha256": expected103, "bytes": 52856},
        "finding": {"shared_id": "DEF023", "local_id": "R104-F01", "priority": "P1", "source": "frontend/src/activities/MemoryWorkspace.tsx",
                    "line": 135, "scope": "保存已确认后旧列表GET等待期间明确载入B，旧返回select(A)抢回编辑身份",
                    "grade": "源码及当前实际加载bundle的B级确定路径；没有声称实测误写"},
        "resource_identity": load(R104 / "resource-readonly.json"),
        "old103_accounting_paths": [str(ROOT / p) for p in ["DocuN/evidence/TASK-103/final/accounting-final.json",
             "DocuN/evidence/TASK-103/continuation-01/final/accounting-final.json", "DocuN/evidence/TASK-103/continuation-02/final/accounting-final.json"]],
        "old104_counts": receipt["counts"], "old104_seconds": receipt["used_seconds"],
        "old104_active_upper_seconds": receipt["active_upper_with_reply"],
        "new_seconds": {"active": 10800, "offline_build": 600, "real": 1200, "cleanup": 300, "metadata": 600},
        "new_counts": {"entry": 6, "container_start": 6, "listener_start": 6, "browser": 6, "driver": 6,
                       "offline": 5, "build": 2, "memory_POST_attempt": 12, "app_password_reset": 2,
                       "SUP": 0, "model": 0, "tool": 0, "container_create": 0, "volume_create": 0, "role_create": 0},
        "new_actual_usage": 0, "dispatch": "待转交，未实际发送／接收／开始",
        "card_prefix_sha256": sha(card), "card_prefix_bytes": len(card),
        "independent_next": "原104已完成范围复用，修后仅实际差异和新增两类证据一次增量复核，不现在另派",
        "root_product_write_SQL_test_build_or_start": 0}
    save(ROOT / "DocuN/evidence/TASK-103/repair-03-input.json", input_record)
    save(OUT / "defect-decisions.json", {
        "at": at, "DEF019": "限定关闭：批准支持域内数值比较修复，原F01语法不变；不签任意精度",
        "DEF020": "限定关闭：普通continue／通用tool拒绝映射及最终真实证据范围",
        "DEF021": "限定关闭：可靠可辨legacy及v2残迹失败关闭，不承诺离线全库替换检测",
        "DEF022": "限定关闭：no_evidence真实HTTP409、六表四账零副作用；不包含新P1或引用迟到",
        "DEF023": {"priority": "P1", "state": "开放阻断", "audit_id": "R104-F01", "owner": "TASK-103 / R-097",
                   "closing_gate": "准确竞态窗口修复及有辨别力验证，原104独立增量确认"},
        "nonblocking_observations": receipt["nonblocking"],
        "observation_policy": "O01—03继续按原audit-local ID／P2边界跟踪，不在本卡修改或自动升级最终硬门",
        "audit_independence": receipt["independence"],
        "G9": "终审不通过，DEF023及引用迟到均待闭，不因四个旧DEF关闭判父阶段通过"})
    save(OUT / "reused-evidence-navigation.json", {
        "audit_scope": str(ROOT / "DocuN/evidence/TASK-104/audit/audit-conclusions.json"),
        "version_applicability": str(ROOT / "DocuN/evidence/TASK-104/audit/all-run-version-applicability.json"),
        "sql": str(ROOT / "DocuN/evidence/TASK-104/audit/sql-current-source-app-live-catalog-binding.json"),
        "bundle": str(ROOT / "DocuN/evidence/TASK-104/audit/final-bundle-source-and-old-native-load-binding.json"),
        "P1": [str(ROOT / "DocuN/evidence/TASK-104/audit" / f) for f in ["R104-F01-static-finding.md", "R104-F01-final-bundle-excerpt.json"]],
        "old_direct": str(ROOT / "DocuN/evidence/TASK-103/continuation-02/final/four-proof-matrix.json"),
        "citation_target": str(ROOT / "DocuN/evidence/TASK-103/continuation-02/browser-target.json"),
        "root01_03_failures": [str(ROOT / f"DocuN/evidence/TASK-104/read-only-{i:02d}/root-result.json") for i in range(1, 4)],
        "reuse": "104未受前端最小修复影响的源码／原证据结论和已验子性质保留，不再全面审计或重跑42根",
        "new": "保存确认后的列表await准确窗口及正常／未确认兼容；引用迟到真实GET／切换／晚交付，不补建教学"})
    audit_decision = f"""# TASK-104 / R-098 独立终审回收裁定

{at}，Codex编排Agent。实际报告21896字节／54306f7a9e7145f52ef22cdd8c99511f173f9674deda22f2418779ab32d48d3b匹配交付记录，325输入身份一致，291原对象未改；六个104自有fixture／browser源码另冻结。接受独立审查交付和有效范围，G9终审不通过，审计任务补证部分未完成，待修后增量，不将报告存在当产品通过。

R104-F01/P1与当前MemoryWorkspace execute135及现有JS编译片段相符，正常UI可达“保存确认→等待列表GET→明确载入干净B→旧返回select(A)”；这是源码和构建身份的B级确定推导，不冒实测误写。登记DEF023/P1，归原103唯一修复路线，完整G9保留阻断。

R104-E01引用迟到未运行。三根均fixture前置失败，browser／driver0：named volume被Binds非空误判、参数化LIKE未转义、session入口native客户端加不支持Origin。末项只有non200原件，403由源码及固定输入推导，不伪造原网络响应。当前产品没有这三项缺陷直接证据，失败不改绿、根3/3与fixture3/3许可结束，名义余额不恢复。

实际窗口是101独立审计职责延续，不是完全空白会话；未参与102／103、未读其实现自评／聊天，例外已披露，独立性在这个受限范围接受，不按模型或旧审计历史另重审。产品未写、业务POST／SQL写0，仅精确app RAM口令重置一次；三资源已停，当前metadata及端口另核无残留。

DEF019—022依据本次独立源码／最终原件按原批准有限域关闭，具体限制见defect-decisions.json；不能因此忽略新DEF023、引用直接证据或签G9。O01—03保留audit-local ID和非阻断P2边界，不自动添加新硬门，也不在本轮扩到仓储／SQL／锁模型。

下一为103/R097审计修复03，A+原实现窗口，一次修P1、验准确窗口及正常／未确认语义、补最后引用GET，修后只原104独立增量。现在不派104复检或新105。共享状态为执行动态v2.15、架构v0.93，原104报告／证据／任务卡不改。
"""
    audit_path = ROOT / "DocuN/results/TASK-104-work-decision.md"
    assert "*" not in audit_decision
    audit_path.write_text(audit_decision.strip() + "\n", encoding="utf-8")
    source_decision = f"""# TASK-103 / R-097 审计修复03编排裁定

{at}，Codex编排Agent。104独立终审报告已回收，代码轴不通过、最后引用证据不足；325身份及291旧对象匹配，原产品未改。接受其其他已核有限代码／版本证据范围与当前控制／资源结论，完整G9仍不通过。

新增DEF023/P1归R104-F01，execute在保存确认后await refresh期间允许用户明确载入B，旧返回未经重新确认当前owner／完整绑定／epoch就select(A)。原C02回执前切换与继续输入不覆盖这个更晚窗口。修复只前端同一身份续处理与必要小helper，正常确认／只清对应旧草稿／未确认不重发保持。

104三个真实根均前置失败且browser0，引用仍NOT_RUN。named volume／LIKE参数／session Origin／闭stdin问题根因及原件保留，不能照抄失败输入。新03需要整条fixture先核、真实准确P1窗口和最后引用一次合并，已有42根与已验三项不重做。

旧103和104许可均已结束。104主动计量11726.360/21600是含封装预留的保守上界，metadata600／1800未知分段，真实43.906／清理24.2681504／fixture离线0.264及entry3/start2/listener1/browser-driver0/offline3/口令重置1不返额；旧初轮／C01／C02全部投入／失败／R20／UNKNOWN保留。

同103/R097新审计修复03许可TASK-103-G9-R03-20261007，主动10800、离线构建600、真实1200、独立收尾300、metadata600秒；6根／6start／6listener／6browser-driver、5离线、2build、最多12显式专用记忆POST／2精确app口令重置，SUP／model／tool／容器／卷／role create／DDL0。一主组合预期，余量有具体不同修正依据才用，两修同因仍败即停。当前新实际使用0，整卡待转交。

源码仅MemoryWorkspace及有据必要memoryIntents／memoryApi；不改其他已审业务／SQL／权限。最后引用只GET／SELECT、零新增教学，样本修订不能失效引用目标依赖。所有新原件audit-repair-03，52856原结果后缀不改。当前297对象（含104六fixture）冻结，pg1精确可复用、pg2／3只metadata保持停止，五端口无监听；本次编排产品／业务运行0。

DEF019—022按104有限域关闭，O01—03非阻断保留，DEF023与引用最后门不松。修后稳定只交原104同独立窗口一次增量，已核未改范围继承；不自签G9／STEP／M-1／项目。105/R099仍未来计划未占号，用户无需重批G9-P，仅转原103卡并回传原结果路径。

## 以下为续作02与更早裁定历史
"""
    state_prefix = """# 执行动态文档

文档 v2.15，2026-10-07，Asia/Shanghai。唯一总状态账；需求v1.1、架构v0.93，task_model／阶段07。下面v2.14及全部历史原字节保留。

## TASK104终审不通过；原103合并修复03

104/R098已实际返回。报告21896字节／54306f7a…与交付hash一致，325原输入／291完整C02 post对象未漂移，104六份新harness/browser另冻结，当前297对象。接受独立审查交付及有效未变范围，G9终审不通过；任务104最后补证未完成，待原103修后独立增量，不新占105/R099。

确定DEF023/P1对应R104-F01，MemoryWorkspace保存已确认后列表refresh还在await期间用户明确载入B，旧返回直接select(A)抢回编辑身份。当前源码135及已真实加载JS存在同一链，B级确定可达，不冒实测误写。旧C02回执前切B／仅追加编辑两种PASS没有覆盖这个更晚窗口，不能据它们排除P1。

104其他七类源码／原版本证据适用性有效部分接收。按其独立结论限定关闭DEF019支持域数值比较、020普通continue/tool拒绝映射、021可靠可辨legacy/v2残迹关闭、022实际no_evidence409零副作用。四项关闭不授G9通过。R104-O01—03为独立集合显示／SQL直接抑制／撤销宽锁域的非阻断P2观察，事实及限制保留，不在此卡改SQL／模型／锁或自动升级硬门。

独立性例外实际为101审计职责会话延续，未参与102/103且未读实现自评／聊天，披露后在受限范围接受；不按品牌／旧审计历史再重审。原完整33项产品差异审读、12函数与实际目录／角色绑定、55份执行记录版本分级及六份实际bundle载入核证保持。55不是成功测试数。

引用迟到仍NOT_RUN，104三个真实根均fixture前置FAIL，browser/driver0。HostConfig.Binds非空误判实际命名卷、参数化LIKE百分号、session native bootstrap带不支持Origin均已定界；第三根仅non200原件，403为源码推导，原HTTP响应未存。旧root1 cleanup=false保持，实际精确资源停止旁证独立成立；闭stdin等输入runner已经按PID/出生/命令收尾，失误不追改。

104许可结束，entry3/3、fixture3/3触顶，start2/3、listener1/3、browser-driver0、口令重置1/1。真实43.906/600秒、cleanup24.2681504/300、fixture0.264/300；主动含初读保守360与回传60共11726.360/21600，metadata保守600/1800及部分helper14.219非全量精确。原103初轮/C01/C02累计39根加104三根为42，所有FAIL、未知、保守/重叠/晚计不返额。

新103/R097审计修复03已登记，调度待转交，A+原实际实现窗口强推理，当前新使用0，无实际发送/接收/开始。整卡只修P1同链前端身份续处理、准确窗口/正常未确认回归、最后引用GET和封装，其他已验直接复用。原104保持独立停止，修后才发增量，不默认每层重审。

新许可TASK-103-G9-R03-20261007，主动10800秒、offline/build600、real1200、独立cleanup300、metadata600；根/start/listener/browser-driver各6、offline5批、build2、专用合成记忆POST最多12、精确app口令重置最多2。预期一主组合，余量只证据明确的修正/受影响复验；同根因两修仍败即停。SUP/model/tool/provider/付费、新容器/卷/role/DDL0，真实用户库与配置0，不借旧余额。

产品写域只MemoryWorkspace及有据必要的memoryIntents/memoryApi与本次dist；SQL/权限/后端/worker/其他工作区/锁文件冻结。专用A/B通过产品save/revise，不能失效引用目标所选记忆，不删旧行。fixture一次核命名卷/psycopg参数/session入口/实际library/默认cursor/ROOT-depth/非交互finally完整链，不重复先前已确诊输入；新证据audit-repair-03保留52856旧结果原字节。

当前编排只读核三精确CID/镜像/卷/标签/配额均Stopped/Pid0、五端口无监听；仅pg1/55443与API18103可由新许可启动，pg2/3只inspect不连PG。role重置只本卡app RAM口令且旧服务停止，属性/ACL不变；不触用户账户。旧command a392c565…requests4/cost4000/tool1/settled12/R20/UNKNOWN及recoveryfalse不改、不退款/结算/重发。

G9/STEP013、M-1/项目/真实provider、后续面试/HTML/退出/Compose/Linux/Nginx仍原门，G8等有效验收及DEF001/002禁用、归档/原始需求/规则不变。本次编排源/SQL/测试/构建/业务资源启动0，仅核证共享记录。

本批CHG0954—0963，下一CHG0964。必要用户动作仅转103修复03整卡并带回原结果路径；104增量前置未满足不现在派发，105/R099未占号。

## 以下为v2.14及更早历史
"""
    arch_prefix = """# 架构动态文档

文档 v0.93，2026-10-07，Asia/Shanghai。需求v1.1、唯一执行动态v2.15。G9集中终审不通过，编辑身份P1及引用迟到未闭；原103同卡修复，未改范围独立证据继承。下面v0.92及全部历史原字节保留。

## G9独立审查结论与最小修复

完整33项G9产品差异、十二函数/实际角色、v1/v2/事实/精确清理/锁序/恢复与原动态版本适用性已独立核，存在确定UI P1。MemoryWorkspace execute旧保存确认后await列表GET期间明确载入B，旧返回不再核当前身份就select(A)；源码及现有最终JS一致，属于B级可达风险，未声称已真实误写。

DEF023/P1开放，修复保持当前实例/owner/完整绑定/读取编辑epoch在await之后仍有权处理当前视图，旧确认不抢回已离开身份、不清新草稿；正常合法保存与持久key事实不改变。仅前端同链最小修正及最终构建，SQL/七表/清理角色/旧四账/停止主体不改。准确“回执确认后列表GET”窗口须真实可辨，不重复已有更早回执窗口。

DEF019—022依本次独立审查各自有限域关闭，不推G9整体通过。O01合格独立IDs显示集合、O02SQL CASE直接抑制、O03revoke宽锁域按原非阻断观察保留，未证明当前progress误增/外部泄露/死锁，不为本P1改持久模型或叠加PG大门。

引用迟到补证没有启动浏览器，三根均104 fixture前置错误，与产品引用实现缺陷不可混同。修复卡一次核完整运行链并完成真实GET挂起/身份切换/晚交付或Abort/旧原文不复活。源改变需要新dist实际加载绑定，未改后端和SQL的充分证据继承。修后仅原104同独立窗口增量确认，不重新审全G9。

单机/单会话边界、UNKNOWN/R20/不退款、不清旧收据/事实、pg2反向落点/pg3 pending正文及真实provider/用户库/全面能力/M-1/后续部署和项目门保持。许可与唯一状态见执行动态v2.15；本次编排未写产品。

## 以下为v0.92及更早历史
"""
    saved = []
    saved.append(prepend("DocuS/执行动态文档.MD", state_prefix, old["DocuS/执行动态文档.MD"]))
    saved.append(prepend("DocuS/架构动态文档.MD", arch_prefix, old["DocuS/架构动态文档.MD"]))
    saved.append(prepend("DocuN/results/TASK-103-work-decision.md", source_decision, old["DocuN/results/TASK-103-work-decision.md"]))
    saved.append(prepend("DocuN/tasks/TASK-103.md", card_text, old["DocuN/tasks/TASK-103.md"]))
    changes = [
        (954, "DocuN/evidence/TASK-104/orchestration-receipt-01/receipt.json", "回收独立终审不通过、325身份及现有源码/bundleP1，保留原件和三个前置FAIL，资源再核"),
        (955, "DocuN/results/TASK-104-work-decision.md", "接受审计交付/独立性受限披露和有效未变范围，G9不通过，修后仅原104增量"),
        (956, "DocuN/evidence/TASK-103/orchestration-repair-03-20261007/defect-decisions.json", "限定关闭019—022，登记023/P1归原103；O01—03保留非阻断边界，不伪转全G9通过"),
        (957, "DocuN/results/TASK-103-work-decision.md", "同103审计修复03一次身份修正/准确窗口/引用尾项，原42根失败与预算不返，原历史保留"),
        (958, "DocuS/架构动态文档.MD", "v0.93记录旧保存后列表await的身份风险、前端最小修改和未改后端审计继承，不扩模型/停止主权"),
        (959, "DocuS/执行动态文档.MD", "v2.15登记104实际返回/许可结束/阻断及03新预算待转交，105仍未占号"),
        (960, "DocuN/tasks/TASK-103.md", "置顶七节修复03，合并P1真实窗口/正常恢复/引用只读证据及整条前置走查，旧合同原字节保留"),
        (961, "DocuN/evidence/TASK-103/repair-03-input.json", "冻结297对象/291旧字节/两个真实报告/精确资源/原账，新实际使用0及明确源/POST/构建预算"),
        (962, "DocuN/evidence/TASK-103/orchestration-repair-03-20261007/reused-evidence-navigation.json", "指向104已核原件、P1静态与旧bundle、当前引用目标和前置失败，仅实际影响补验"),
        (963, "DocuN/evidence/TASK-103/orchestration-repair-03-20261007/delivery-proof.json", "全文回读/七节/版本编号/历史后缀/297对象/报告/规则核对，实际发送和产品运行0")
    ]
    change_file = ROOT / "DocuS/文档变更记录.MD"
    assert change_file.read_bytes() == old["DocuS/文档变更记录.MD"]
    addition = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{at}，Codex编排Agent，{p}。{d}。" for n, p, d in changes) + "\n"
    change_file.write_bytes(old["DocuS/文档变更记录.MD"] + addition.encode("utf-8"))
    assert change_file.read_bytes().startswith(old["DocuS/文档变更记录.MD"])
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    assert sha(report103.read_bytes()) == expected103 and sha(report104.read_bytes()) == receipt["report_sha256"]
    for row in frozen_rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    save(OUT / "delivery-proof.json", {"at": at, "TASK": "TASK-103", "R": "R-097", "round": "审计修复03",
        "dispatch": "待转交", "state": "v2.15", "architecture": "v0.93", "CHG": "0954—0963", "next_CHG": "0964",
        "seven_sections_readback": True, "new_markdown_no_asterisks_or_tables": True, "history_preserved": saved,
        "both_returned_results_unchanged": True, "current297_unchanged": True, "rules_contracts_unchanged": True,
        "old104_card_evidence_unchanged": True, "new_execution_usage": 0, "actually_sent_received_started": False,
        "root_product_SQL_test_build_start": 0, "card_path": str(ROOT / "DocuN/tasks/TASK-103.md"),
        "card_prefix_bytes": len((card_text.strip() + "\n\n").encode("utf-8")), "card_sha256": sha((ROOT / "DocuN/tasks/TASK-103.md").read_bytes()),
        "repair_input_sha256": sha((ROOT / "DocuN/evidence/TASK-103/repair-03-input.json").read_bytes())})
    print(json.dumps({"TASK": "TASK-103", "R": "R-097", "round": "审计修复03", "dispatch": "待转交",
        "state": "v2.15", "architecture": "v0.93", "CHG": "0954—0963", "frozen": 297,
        "new_P1": "DEF023", "root_product_runs": 0, "histories_preserved": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
