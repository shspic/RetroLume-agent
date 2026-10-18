"""Register a bounded continuation and preserve all returned evidence."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-103/orchestration-receipt-01"
AT = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fresh_json(path, value):
    if path.exists():
        raise RuntimeError("Existing work must not be overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md(text):
    data = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    if b"*" in data or re.search(rb"(?m)^\|", data):
        raise RuntimeError("New managed Markdown format violation")
    return data


STATE = """# 执行动态文档

文档 v2.12，2026-10-06，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.90，task_model/阶段07。下面v2.11及全部历史原字节保留。

## TASK103部分返回；续作01完整缺口收口

103/R097调度已返回，普通核证部分通过：接受保存的G9实现候选、可定位有限运行与资源收尾；完整G9合同未通过，尚未形成稳定完整候选，独立审计未启动。不将三browser总FAIL或任一总批失败改PASS，不凭报告“部分A级”签全性质。

报告24351字节/SHA b62695f7…已真实读取并冻结副本；manifest268对象检查含266存续对象、2已移除但pre保留资产一致，246份post运行快照是子范围；10规则/合同输入匹配。初始233/改变24/新增34、源码缺失0和既有pdfjs版权遗漏枚举说明保持，旧授权基线和改动身份不重置。

原许可按触顶结束：entry24/24、browser/driver3/3、build3/3；offline4/6、container/volume create3/3、start23/24、listener3/12、SUP16/64。主动保守19020.059186/28800秒，offline/build15.453、real539.251内外重叠保守不返额、cleanup22.018、metadata548.453及未知/旧失败保持，剩余名义次数/时间不恢复执行权。

源/副作用分层可采：七表/roles初次创建、非空14表32行旧值不变和空新反向DDL、部分CAS/来源/后继/上游/清理与权限、16真实SUP及树零/合法结算、部分只读快照/恢复及最终dist加载身份已有原件。未闭合为末改两SQL函数/缺M6残迹/新HTTP映射、合法calc和通用tool、PDF/新feedback无关反例/闭包/源并发、浏览器完整写与恢复等。SQL部署仍旧而源码指纹已新，不能借之前绿事实签最终版。

新增DEF020/P2：real24普通continue业务拒绝memory_profile_required，但HTTP200；映射候选已改，待真实最终版本复验。新增DEF021/P2：memory schema=damaged的源码当前无条件FALSE/selected=True，已可安全识别的无选择legacy降级不符合合同，待补精准分类及实际兼容反例。它们归103同一个完整修复；不占更多号或升级成全仓门。browser03缺第二页DOM，当前代码有editSequence保护，根因未证明仅fixture；续作须同时核加载/绑定/编辑状态，不先宣告产品无缺陷。

同TASK103/R097续作01已登记，调度STATUS_TOKEN，A+原实际103业务窗口，用可用最强推理资源；G9-P仍已批准，不再问采用。原103完整文件写域/包语义继承，补所有真实剩余性质，主组合/最终UI/必要有据复验同卡，稳定完整后才派104集中隔离审计；104/R098仍未来计划未占号。

新许可TASK-103-G9-C01-20261006：主动21600/离线1200/真实3600/收尾600/元数据600秒，根入口12、container start16、listener6、SUP尝试24、browser/driver各3、build2、离线6批；create容器/卷0。动作前计数，新使用0，不借旧余额，不清原同根因失败；原browser停止后只有新的具体受控方案获一次主验证与必要取证/有据补验，不能反复原sleep方案。根≤900、离线≤180、build≤300、真实SUP manager50，均受新剩额。

精确复用原pg1 CID4889202d…、pg2 f96ac8dc…、pg3 4b813f9e…及原标签/卷/镜像/配额/端口；当前编排只读核三CID均Stopped/Running=false/Pid0，未启动/连接PG/修改函数或资源。只向前精确更新本包末改函数并保row/owner/ACL，不重跑010创建，不重写旧不可变收据。实际SessionConfig W20/req2/grace2/start5/db5/cleanup5/mutex3/overhead30/recoveryfalse，manager50/lease20作为本轮配置；原建议lease60偏差按实保留，不改监督主体。

续作证据新目录continuation-01，原24根/三browserFAIL、root21已提交UNKNOWN但证据序列化失败、旧checkpoint与所有原件不覆盖、不重新产生同一效果。原v1/G8/001—009/worker/依赖锁和其他已验权威按真实未改范围继承，DEF019为修正候选仍待最终独立确认；旧DEF001/002与097禁用、全部更早FAIL/漏5.940/预算/未知/归档与锁定规则保持。

原结果/正式需求/公共库/产品与原证据本次编排零修改；仅读/hash/精确资源metadata与共享文档写入。G9/STEP013、其他Must/真实provider/M-1/Compose/Linux/Nginx部署/项目未通过，后续仍原阶段。

本批CHG0924—0933，下一CHG0934；必要用户动作仅转103续作01整卡并带回原结果路径。当前没有实际发送/接收/启动事实。

## 以下为v2.11及更早历史

"""

ARCH = """# 架构动态文档

文档 v0.90，2026-10-06，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.12。G9部分候选已返回，同103续作01待转交，未签完成。下面v0.89及全部历史原字节保留。

## G9候选实际落地及剩余边界

当前010七表/最小角色、记忆保存修订撤销/固定选择、v2 recipe/资格、只读投影和工作区已写候选，部分真实PG/HTTP/16SUP/迁移/清理/权限子性质成立；不是完整B1—B8/C1—C3已验。末改activity_memory_eligible/purge_learning_memory及缺M6残迹、HTTP错误映射未经最终PG/HTTP验证，浏览器三总FAIL的后续部分未运行，最终bundle已加载只能证明身份。

本轮主控登记HTTP状态映射DEF020/P2及damaged下已可识别legacy被全关的DEF021/P2，原F01/G8闭合与DEF019定向候选边界保持。schema损坏时不能默认legacyTrue，但已有绑定仍可可靠读/无v2残迹时需精准兼容，无法判明则相关项失败关闭，不增新持久模型或回退能力。

续作保持新包主权/七表，精确前向更新两个本包函数并保原数据/ACL，补合法calc/通用tool拒、未做传播/闭包/并发和最终工作区；先核真实页面状态/绑定/输入与整个fixture链，不把三次失败一概归夹具或改成PASS。稳定完整G9后一次隔离增强审计，不为缺口预加逐模块审计或重跑旧停止全矩阵。

实际监督配置lease随W20绑定、管理50，原卡建议60是偏差不是新时间授权；不改监督/关门/结算/UNKNOWN/四账主权。旧函数/代码/条件未改的充分证明继承，变过的SQL/读面/包不混当前版本。真实provider、完整向量/HTML/面试/退出恢复/M-1/部署与项目门保持。

## 以下为v0.89及更早历史

"""

DECISION = """# TASK-103 / R-097 首轮回收与续作01裁定

AT_TOKEN，Codex编排Agent。首轮已真实返回，普通核证部分通过，完整G9未验收。报告b62695f7da2b3b5c65553f7a7ec5f87a979c7029c3e2b33ed5ee9cb06fe21b13/24351字节与当前成果已冻结；266存续/2删除资产/246post子范围/10规则合同身份匹配。实现自评不能替独立审计，24根、三browser总FAIL及全部旧副作用/不足保持。

原许可结束，entry24/browser3/driver3/build3触顶，offline4/create3/volume3/start23/listener3/SUP16及19020.059186主动、15.453离线构建、539.251真实、22.018收尾、548.453元数据/未知不清零，不转借其余次数。root21诊断已COMMIT但落证失败不能重做为新效果；root19弱numeric_status断言不能扩签正确性。

同103续作01授权完成当前完整剩余实现与最终证据，原A+实际业务窗口，必要时增强到可用最强资源。G9-P已批准不再询问，新主动21600/离线1200/真实3600/收尾600/辅助600秒及12根/16start/6listener/24SUP/3browser-driver/2build/6offline，原同根因失败保留。本轮新使用0、整卡待转交，无实际接收/开始。原产品写域不扩大，010前向函数维护与新源码按具体差异，不复位库/role或重写不可变收据。

DEF020/P2映射候选待真实409/零效应；DEF021/P2精准legacy降级待补源/实际样本，不能损坏不明默认True。UI当前editSequence保护存在、原second页缺证据，先核加载/完整绑定/owner/输入epoch与整个选择器/API语义，再主批，原sleep等待方案不能反复。完整剩余传播/闭包/并发/工具/UI性质一次合并，不一处一张。

当前只读三ownedCID均Stopped/Pid0；精确CID/label/镜像/卷配额沿原，创建0、旧数据保留。只向前更新已末改本包函数及必要指纹，实查原definition/owner/ACL/数据后原子更新，正常旧v1和损坏可辨分支分级。实际SessionConfig manager50/lease20被明确作为本轮口径，原建议60偏差保留；不改worker监督来迎合配置。

原已真迁移、权限、清理、来源、CAS、UNKNOWN/终态、Window等按未改字段/函数/条件继承，所有末改函数/映射和未跑子项必须真实填缺，不重做无关大链。稳定完整候选后才占104/R098隔离审计，不能本轮自签DEF/G9/STEP/M-1或项目。TASK103原报告、旧证据和产品本次编排零改动。

完整本轮合同见DocuN/tasks/TASK-103.md顶部，唯一总状态见DocuS/执行动态文档.MD，原记录副本与身份/当前资源见证见orchestration-receipt-01。用户只需转卡和带回结果。
"""


def main():
    if (OUT / "delivery-proof.json").exists():
        raise RuntimeError("Continuation already registered")
    before = {}
    for row in load(OUT / "before-manifest.json"):
        data=(ROOT / row["path"]).read_bytes()
        if data != Path(row["backup"]).read_bytes() or sha(data)!=row["sha256"]:
            raise RuntimeError("Shared state changed")
        before[row["path"]]=data
    if max(map(int,re.findall(r"CHG-(\d+)",before["DocuS/文档变更记录.MD"].decode("utf-8-sig"))))!=923:
        raise RuntimeError("CHG allocation changed")
    if "DEF-020" in before["DocuS/执行动态文档.MD"].decode("utf-8-sig") or "DEF-021" in before["DocuS/执行动态文档.MD"].decode("utf-8-sig"):
        raise RuntimeError("DEF allocation changed")
    current=load(OUT / "current-baseline.json")
    for rel,expected in current.items():
        if sha((ROOT / rel).read_bytes())!=expected:raise RuntimeError("Candidate drift")
    receipt=load(OUT / "receipt.json")
    report=ROOT / "DocuN/results/TASK-103-result.md"
    if sha(report.read_bytes())!=receipt["report_sha256"]:raise RuntimeError("Returned report drift")
    card=(OUT / "TASK-103-continuation-01-card.md").read_text(encoding="utf-8")
    headings=["目标与交付","项目、规则与接收安排","背景与最小充分上下文","执行边界与资源","验证、证据与审计关系","停止与回传","必要人工与待同步信息"]
    if any(f"## {heading}\n" not in card for heading in headings) or "〈" in card or "〉" in card:raise RuntimeError("Incomplete continuation")
    offsets={}
    offsets["DocuS/执行动态文档.MD"]=len(md(STATE.replace("STATUS_TOKEN","卡面整理中，未转交")))
    (ROOT / "DocuS/执行动态文档.MD").write_bytes(md(STATE.replace("STATUS_TOKEN","卡面整理中，未转交"))+before["DocuS/执行动态文档.MD"])
    (ROOT / "DocuS/架构动态文档.MD").write_bytes(md(ARCH)+before["DocuS/架构动态文档.MD"])
    offsets["DocuS/架构动态文档.MD"]=len(md(ARCH))
    decision_path=ROOT / "DocuN/results/TASK-103-work-decision.md"
    if decision_path.exists():raise RuntimeError("Existing Markdown decision must be read, not replaced")
    decision_path.write_bytes(md(DECISION.replace("AT_TOKEN",AT)))
    card_data=md(card)
    (ROOT / "DocuN/tasks/TASK-103.md").write_bytes(card_data+before["DocuN/tasks/TASK-103.md"])
    offsets["DocuN/tasks/TASK-103.md"]=len(card_data)
    if (ROOT / "DocuN/tasks/TASK-103.md").read_bytes()!=card_data+before["DocuN/tasks/TASK-103.md"]:raise RuntimeError("Complete card readback differs")
    final_state=md(STATE.replace("STATUS_TOKEN","待转交"))
    (ROOT / "DocuS/执行动态文档.MD").write_bytes(final_state+before["DocuS/执行动态文档.MD"])
    offsets["DocuS/执行动态文档.MD"]=len(final_state)
    definitions={"DEF-020":{"severity":"P2","finding":"real24 HTTP200 business memory_profile_required rejection; final mapping candidate not rerun","state":"open; candidate fix awaiting real verification"},
                 "DEF-021":{"severity":"P2","finding":"schema damaged unconditionally FALSE/selectedTrue affects safely identifiable no-selection legacy; B source and explicit V21 gap","state":"open; bounded compatibility fix and validation required"}}
    fresh_json(OUT / "defect-source-records.json",{"at":AT,"primary_fix_TASK":"TASK-103/R-097","records":definitions,"new_P0_P1_claimed":False,"UI_root_cause":"not declared purely fixture; existing editSequence guard acknowledged; need page/identity evidence","shared_status_authority":"DocuS/执行动态文档.MD"})
    fresh_json(ROOT / "DocuN/evidence/TASK-103/continuation-01-input.json",{"at":AT,"TASK":"TASK-103","R":"R-097","round":"continuation-01","current_files":current,
        "result_before":{"path":str(report),"sha256":receipt["report_sha256"],"bytes":receipt["report_bytes"]},"decision":{"path":str(decision_path),"sha256":sha(decision_path.read_bytes())},
        "original_card_snapshot":str(OUT / "TASK-103-first-card-as-returned.md"),"resource_readonly":str(OUT / "resource-readonly.json"),"old_accounting":str(ROOT / "DocuN/evidence/TASK-103/final/accounting-final.json"),
        "new_permit":"TASK-103-G9-C01-20261006","new_limits":{"active":21600,"offline":1200,"real":3600,"cleanup":600,"metadata":600},
        "new_counts_limits":{"entry":12,"container_start":16,"listener_start":6,"sup":24,"browser":3,"driver":3,"build":2,"offline":6,"container_create":0,"volume_create":0},"new_actual_uses":0,
        "old_counts_immutable":receipt["counts"],"all_old_permissions_ended":True,"session_reconciliation":"Actual SessionConfig W20/request2/grace2/start5/db5/cleanup5/mutex3/overhead30/manager50/lease20; no worker change",
        "new_card_prefix_sha256":sha(card_data),"dispatch":"待转交","started":False,"scope":"remaining full G9 only, existing resources, no user approval repetition"})
    fresh_json(OUT / "evidence-reuse-navigation.json",{"at":AT,"not_an_independent_audit":True,"full_manifest_current":266,"as_run_post_subset":246,
        "old_witnesses_reused_without_new_business_runs":["010 initial valid structure/roles and verified FK targets","pg2 14 tables32 old rows unchanged and empty new reverseDDL","normal exact body purge and subset of attacks/permission denials","known committedUNKNOWN from root21 confirmed root22","16SUP tree0/close/settle facts with unchanged worker","old browser03 save/GET/owner identities only, totalFAIL kept"],
        "must_not_inherit_as_final":["last two SQL functions","last mapping409","damaged legacy fallback","remaining tool/calculator path","full browser/write/recovery/selection/clear","unexecuted dependency/loop/PDF/newfeedback/source concurrency branches"],"role":"navigation only; executor maps actual unchanged bytes and new assertions"})
    histories=[]
    for rel,offset in offsets.items():
        data=(ROOT / rel).read_bytes()
        if data[offset:]!=before[rel]:raise RuntimeError("Shared history changed")
        histories.append({"path":rel,"prefix_bytes":offset,"old_bytes":len(before[rel]),"old_sha256":sha(before[rel]),"exact":True})
    for rel,expected in current.items():
        if sha((ROOT / rel).read_bytes())!=expected:raise RuntimeError("Product altered during root registration")
    if sha(report.read_bytes())!=receipt["report_sha256"]:raise RuntimeError("Executor report altered")
    entries=[
        (924,"DocuN/evidence/TASK-103/orchestration-receipt-01/receipt.json","普通回收部分G9候选和266实际对象/246post子集/10输入，旧完整报告与24失败账保持，未签完整G9。"),
        (925,"DocuN/results/TASK-103-work-decision.md","保存首轮部分裁定与同任务完整剩余续作，新明许可/实际SessionConfig/证据分层，不重复G9-P批准。"),
        (926,"DocuN/evidence/TASK-103/orchestration-receipt-01/defect-source-records.json","登记020HTTP映射P2候选和021damaged可辨legacy兼容P2，同103修复；UI根因不假称仅fixture。"),
        (927,"DocuS/架构动态文档.MD","v0.90同步真实部分实现、末尾SQL未部署/读面/工具/UI缺口和有限继承，不提前判稳定或权限通过。"),
        (928,"DocuS/执行动态文档.MD","v2.12登记真实返回/原许可触顶/投入/未完成及续作01独立新预算/原资源，整卡核证后待转交。"),
        (929,"DocuN/tasks/TASK-103.md","置顶完整七节续作01，补真实剩余与最终版本、同连接向前函数维护、限定UI新方案/工具/降级/传播，旧完整卡原字节保留。"),
        (930,"DocuN/evidence/TASK-103/continuation-01-input.json","冻结当前266对象、旧报告/原许可与三个精确CID来源、新许可及实际类型口径，新资源创建0、新使用0。"),
        (931,"DocuN/evidence/TASK-103/orchestration-receipt-01/resource-readonly.json","只读核三owned容器Stopped/Pid0/镜像标签卷，未接DB/启资源/输出Env，不将旧样本当新实验。"),
        (932,"DocuN/evidence/TASK-103/orchestration-receipt-01/evidence-reuse-navigation.json","保留迁移/权限/清理/UNKNOWN/Window/部分UI可采与末改/未跑排除，导航不代独立审计。"),
        (933,"DocuN/evidence/TASK-103/orchestration-receipt-01/delivery-proof.json","完整卡回读/七节/历史/当前代码与结果不变/版本编号核证，没有实际发送或开始。")]
    for _,rel,_ in entries[:-1]:
        if not (ROOT / rel).is_file():raise RuntimeError("Cannot record an unsaved artifact")
    addition="\r\n\r\n"+"\r\n\r\n".join(f"- CHG-{number:04d}，{AT}，Codex编排Agent，{rel}。{description}" for number,rel,description in entries)+"\r\n"
    fresh_json(OUT / "delivery-proof.json",{"at":AT,"TASK":"TASK-103","R":"R-097","round":"continuation01","dispatch":"待转交","sent_received_started":False,
        "acceptance_of_first_return":"partial candidate only","recipient":"A+ original TASK103 window; strongest available reasoning","all_seven_sections":True,"card_prefix_bytes":len(card_data),"card_prefix_sha256":sha(card_data),
        "history_exact":histories,"old_result_untouched":True,"old_result_sha256":receipt["report_sha256"],"unchanged_current_sources":len(current),
        "versions":{"state":"2.12","architecture":"0.90","requirements":"1.1"},"CHG":{"first":924,"last":933,"next":934},"new_task104":"planned only, not occupied",
        "CHG_expected_sha256":sha(before["DocuS/文档变更记录.MD"]+addition.encode("utf-8")),"root_product_writes":0,"root_business_runs":0,"new_resource_starts":0,"new_permission_uses":0})
    logpath=ROOT / "DocuS/文档变更记录.MD"
    logpath.write_bytes(before["DocuS/文档变更记录.MD"]+addition.encode("utf-8"))
    actual=logpath.read_bytes()
    if not actual.startswith(before["DocuS/文档变更记录.MD"]) or max(map(int,re.findall(r"CHG-(\d+)",actual.decode("utf-8-sig"))))!=933:raise RuntimeError("CHG history mismatch")
    print(json.dumps({"card":str(ROOT / "DocuN/tasks/TASK-103.md"),"prefix_bytes":len(card_data),"status":"ready for manual handover","current_sources_unchanged":len(current),
        "state":"v2.12","architecture":"v0.90","CHG":"0924-0933; next0934","G9":"partial, not accepted","new_uses":0},ensure_ascii=False))


if __name__=="__main__":
    main()
