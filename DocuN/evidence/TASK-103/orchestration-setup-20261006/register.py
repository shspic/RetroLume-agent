"""Persist approved packet, full card and shared status; metadata only."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-103/orchestration-setup-20261006"
AT = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fresh_json(path, value):
    if path.exists():
        raise RuntimeError("Refuse overwriting registered work")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md(text):
    data = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    if b"*" in data or re.search(rb"(?m)^\|", data):
        raise RuntimeError("Managed Markdown contains asterisks/tables")
    return data


def prefix(rel, text, old):
    added = md(text)
    (ROOT / rel).write_bytes(added + old)
    return len(added)


DECISION = """# G9-P用户采用已批准；TASK103合成实施（2026-10-06，当前）

用户在编排上一条具体G9-P核证请求后明确回复“批准”。包采用现生效；本记录登记时点AT_TOKEN，确切用户消息时间未提供，只知客户端日期2026-10-06/Asia/Shanghai，不编造同一时刻。原推荐/待批全文原字节保留，下方当时未批准的句子是历史。

采用内容为原102结果A—D和本裁定的固定澄清：七表/版本化记忆/固定选择、活动级失效、教学v2及全读/写资格、受限M3清理、实际工作区与受影响合成验证。清理及模式变化仅后续明确合成目标，原用户库/真实角色/真实删除、007/009/资料/原件/WAL/备份、真实provider/付费/部署/安装/Git未扩大授权。

完整TASK103/R097已准备并核可读，A+实际TASK102业务窗口，新许可TASK-103-G9-20261006；源码/DDL/相关测试/工作区与合成资源的真实写权、边界、配额和停止由TASK103.md定义，调度待转交，新使用0，无实际发送/接收/启动。

三新独立PG实例按需创建，复用本机缓存镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；本机tag为pgvector/pgvector:0.8.6-pg17-bookworm，实际SQL能力/角色再在获准实例核。旧100容器80ae9141…当前只读核exited/Running=false/Pid0/Exit0，原库卷不触。新pg1/2/3及卷在准备时无碰撞，55443/55444/55445/18103/18104无监听，实际用前重核；镜像/venv/node/playwright/Chromium缓存现存，不pull/安装。

新主动28800/离线1800/真实7200/清理900/辅助600秒；真实入口24、容器create3/卷create3/start24、监听app及fake进程start12、SUP尝试64、browser/driver各3、离线6批/build3。动作前计数、固定单调截止，普通有据修复同卡，两次同根因修正仍失败或上限到达交回；全成即停，不为了用尽额度追加工作。旧102/100/101全部失败/投入/未知及许可结束事实保持。

本卡明确合并DEF019的最小policy/离线边界修正，不新微修卡、不改F01全文肯定文法/其他政策。不修改监督/协议3/4、关门/结算/退款主体；记忆失效UNKNOWN保留模型/费用/工具未知预留，时间在原树零/关门合法证明下结算规则仍旧。固定镜像无法真实形成的版本缺功能条件分级，不删pg_catalog或伪环境冒实测。

稳定完整G9候选返回后再给一次隔离增强独立审计，当前没有依赖审计卡。G9/STEP013/M-1/项目尚未完成；原G8已验关闭、其余Must/Compose/Linux/Nginx/Git阶段安排保持。编排仅只读基础设施与文件/hash/文档操作，没有创建容器/卷、启数据库/应用或产品运行。

## 以下为采用前裁定历史

"""

STATE = """# 执行动态文档

文档 v2.11，2026-10-06，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.89，task_model/阶段07。下面v2.10及全部历史原字节保留。

## G9-P用户批准；TASK103完整合成实现待转交

用户对上一条具体G9-P包核证请求明确“批准”，采用生效，见DocuN/results/TASK-102-work-decision.md新前缀。一次批准包含七表/版本/固定选用/活动级保守失效、v2身份与全链资格、精确在线记忆正文清理和实际工作区，包外真实用户库/角色/删除、旧事实/原件/备份、真实provider/付费/部署/Git/安装不变。不是重复确认，也不追认任何此前未授权运行。

TASK102/R096完整设计验收关闭保持，原结果82360字节/f3bf109c…不改；实际完成102的A+Codex desktop/GPT-6文件承接窗口继续，不冒称原100同聊天，也不重审品牌。56个未变源码/规则/父输入一致，准备233产品/测试/生成物基线，无新memory产品/010或103实际结果，当前无在途业务。

新TASK103/R097已占号，G9/STEP013完整实现、24组受影响验证和收尾，调度STATUS_TOKEN。完整七节卡已保存回读，新许可TASK-103-G9-20261006；新实际使用0，没有真实发送/接收/开始。执行者独占本包源/测试/dist和新合成对象，原审计窗口不接管实现，无自动子Agent。

新额度主动28800、离线1800、真实准备/PG/HTTP/Windows/browser总7200、独立收尾900、辅助600秒（主动含全封装）；真实根入口24，容器create3/卷create3/start24，监听app/fake进程start合计12，SUP尝试64且会话≤120秒，browser/driver各3，离线6批各≤180秒，build3各≤300秒，真实根各≤900秒且受剩余总额限制。动作前计数，失败/BLOCKED也占额，不混入口/方法/子测试/请求/业务窗，全成即停，不耗尽为目标。

本卡明确定向合并DEF019/P2数值比较与离线例，原F01等有效性质保留，未触及的G3—G8权威/证明直接继承。修改源码之后实际影响才补相应检查，PG事务权限不用mock，实际HTTP/最终UI不靠只读快照，普通修复同卡统一回传。稳定完整G9后才派一张隔离增强独立审计，下一TASK104/R098仅未来计划，未占号/出卡。

合成隔离资源：新retrolume-task-103-g9-pg1/pg2/pg3及同名-data卷，主/非空升级/坏基线与故障分别独立cluster；固定缓存镜像cf134a76…（本机pgvector0.8.6-pg17-bookworm），pull=never，1CPU/512MiB/pids128/无host bind或特权/仅loopback55443—55445，一次最多一个运行。主API/最终dist18103，必要fake最低HTTP传输18104；库和role前缀/完整配额及精确收尾见卡，创建后冻结CID，不凭名字盲复用。

编排当前只读核旧100容器80ae9141…exited/Running=false/Pid0/Exit0，旧命名卷原样；新3名称/卷无撞名，五端口无监听，镜像/venv/node_modules/playwright与Chromium缓存可用。未创建卷/容器、启应用/DB或执行PG/测试/build。实际执行前重核，旧观察时点不替代当前；不读取旧容器Env/private配置。两次根只读rg候选路径不存在已定位真实bootstrap，非产品失败，准备元数据记录保留。

新凭据仅本卡owned容器与新role内存/stdin/子进程Env，不在argv/日志/对话/配置，只有核归属的新容器可单项内存取回bootstrap口令。所有数据/库/role/卷/容器保留停止，DELETE只新M3精确清单，DROP只批准空新010对象精确反向DDL且无其他依赖，不删旧事实或用泛清理夹具。

原102设计3122墙钟保守/300元数据、三路径错误和辅助regex修正及运行0许可结束；原100修复04的1/3/1.6463436/1779.265、101review03的2002.341/180及更早FAIL/漏5.940/未知全部原样。G8/100/101已验关闭，DEF008等闭合、DEF001/002旧runner禁用、归档/公共锁定和原始需求保持，预算不借、不清零。

STEP013转实施待转交，G9未实现未动态验收，不签完整STEP/V19真实provider/M-1或项目。面试/HTML/数据退出/完整向量及018Compose/Linux/Nginx/019权限/020自用交接、Git既有首提交后新提交另门仍保持。

本批CHG0914—0923，下一CHG0924；下一新TASK104/R098未占号。必要用户动作仅转103完整卡，完成后带回结果路径；G9-P批准不再重复询问。

## 以下为v2.10及更早历史

"""

ARCH = """# 架构动态文档

文档 v0.89，2026-10-06，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.11。G9-P用户已批准，TASK103完整合成实现待转交，产品尚未完成。下面v0.88及全部历史原字节保留。

## G9采用边界与完整实施

采用102七表职责分离、不可变记忆版本/CAS/墓碑、固定活动选择、全活动保守失效、v2 recipe/消息身份与全读写资格、唯一精确M3清理及NOLOGIN最小角色、工作区和24组受影响合成性质。原用户作答/事实不改，记忆只背景不作新引用或独立表现，不授模型/工具新权。

列表固定元数据/有资格短标题，完整正文/依赖走详情；v2持续上下文不复制记忆正文，legacy无选择原字节保持。锁前缀在第一活动锁前同连接接旧后段，所有读取/接受/launch/admit/mark/结果/重建核资格；旧取消/关门/结算/UNKNOWN/停树与四账主权保持。DEF019最小比较/离线修复在本完整卡合并，不重开G8。

本机缓存镜像tag为pgvector0.8.6-pg17-bookworm，实际新库SQL能力/角色仍需获准合成验证；使用独立主/升级/故障cluster隔离新角色与坏样本，不涉及旧100库卷或真实用户role。新010/权限/工作区未落地，实际验证与最终独立审计门保持，不能据采用或公开文档称通过。

撤销优先停用、精确清理只在线本条记忆正文；原事实/007/资料/原件/WAL/备份与供应商字节不包含。未改G8和其他充分证据直接继承；完整向量/真实provider/长期质量/面试/HTML/退出恢复/M-1/部署/项目仍后续门。Compose/Linux/Nginx/Git原计划保持。

## 以下为v0.88及更早历史

"""


def main():
    if (OUT / "delivery-proof.json").exists():
        raise RuntimeError("TASK103 already registered")
    if (ROOT / "DocuN/tasks/TASK-103.md").exists():
        raise RuntimeError("Do not overwrite new task")
    before = {}
    for row in load(OUT / "before-manifest.json"):
        data = (ROOT / row["path"]).read_bytes()
        if data != Path(row["backup"]).read_bytes() or sha(data) != row["sha256"]:
            raise RuntimeError("Shared baseline drift")
        before[row["path"]] = data
    if max(map(int,re.findall(r"CHG-(\d+)",before["DocuS/文档变更记录.MD"].decode("utf-8-sig")))) != 913:
        raise RuntimeError("CHG allocation changed")
    checks = load(OUT / "identity-checks.json")
    for row in checks:
        if sha(Path(row["path"]).read_bytes()) != row["expected"]:
            raise RuntimeError("Stable parent source changed")
    baseline = load(OUT / "product-baseline.json")
    for row in baseline:
        if sha((ROOT / row["path"]).read_bytes()) != row["sha256"]:
            raise RuntimeError("Product changed since setup")
    decision_rel = "DocuN/results/TASK-102-work-decision.md"
    offsets = {decision_rel: prefix(decision_rel,DECISION.replace("AT_TOKEN",AT),before[decision_rel])}
    decision_sha = sha((ROOT / decision_rel).read_bytes())
    prepared = (OUT / "TASK-103-card-prepared.md").read_text(encoding="utf-8")
    if prepared.count("__APPROVED_DECISION_SHA__") != 1:
        raise RuntimeError("Unexpected decision placeholder count")
    card = prepared.replace("__APPROVED_DECISION_SHA__",decision_sha)
    headings = ["目标与交付","项目、规则与接收安排","背景与最小充分上下文","执行边界与资源","验证、证据与审计关系","停止与回传","必要人工与待同步信息"]
    if any(f"## {heading}\n" not in card for heading in headings) or "__APPROVED_" in card or "〈" in card or "〉" in card:
        raise RuntimeError("Incomplete card")
    offsets["DocuS/执行动态文档.MD"] = prefix("DocuS/执行动态文档.MD",STATE.replace("STATUS_TOKEN","卡面整理中，未转交"),before["DocuS/执行动态文档.MD"])
    offsets["DocuS/架构动态文档.MD"] = prefix("DocuS/架构动态文档.MD",ARCH,before["DocuS/架构动态文档.MD"])
    card_data = md(card)
    card_path = ROOT / "DocuN/tasks/TASK-103.md"
    card_path.write_bytes(card_data)
    if card_path.read_bytes() != card_data:
        raise RuntimeError("Saved complete card differs")
    offsets["DocuS/执行动态文档.MD"] = prefix("DocuS/执行动态文档.MD",STATE.replace("STATUS_TOKEN","待转交"),before["DocuS/执行动态文档.MD"])
    protected = [{"path":row["path"],"sha256":row["sha256"]} for row in baseline if row["path"].startswith("backend/migrations/")]
    resources = load(OUT / "resource-preflight.json")
    fresh_json(ROOT / "DocuN/evidence/TASK-103/input-snapshot.json",{
        "at":AT,"TASK":"TASK-103","R":"R-097","project_root":str(ROOT),"task_card_sha256":sha(card_data),
        "contracts":[{"path":str(ROOT / "DocuN/results/TASK-102-result.md"),"sha256":"f3bf109c1398b5cf1a8d112f4ebcc55db6d3c0a1f42dc2f92d7aff67377f22b3"},{"path":str(ROOT / decision_rel),"sha256":decision_sha}],
        "product_before":baseline,"protected_migrations":protected,"rules":load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json"),
        "approval_record":str(OUT / "approval.json"),"resource_preflight":str(OUT / "resource-preflight.json"),
        "permit":"TASK-103-G9-20261006","dispatch":"待转交","started":False,
        "time_limits":{"active":28800,"offline":1800,"real":7200,"cleanup":900,"metadata":600},
        "counts":{"real_entries":24,"container_creates":3,"volume_creates":3,"container_starts":24,"app_fake_starts":12,"sup_attempts":64,"browser":3,"driver":3,"offline_batches":6,"frontend_build":3},
        "initial_uses":0,"new_resources_started_by_orchestrator":0,"old_resources_not_reused":True,
        "source_existing_at_snapshot_only":True,"new_files_preserve_existing_changes_on_discovery":True})
    fresh_json(ROOT / "DocuN/results/TASK-103-work-decision.md.json",{"at":AT,"TASK":"TASK-103","R":"R-097","adoption":"G9-P approved by explicit user message",
        "contract_authority":"DocuN/tasks/TASK-103.md and adopted TASK102-work-decision", "dispatch":"待转交","actual_started":False,
        "synthetic_only":True,"new_budget_only":True,"independent_audit_after_stable_complete":True,"shared_state_authority":"DocuS/执行动态文档.MD"})
    histories,docs = [],[]
    for rel,offset in offsets.items():
        data = (ROOT / rel).read_bytes()
        if data[offset:] != before[rel]:
            raise RuntimeError("History changed")
        histories.append({"path":rel,"prefix_bytes":offset,"old_bytes":len(before[rel]),"old_sha256":sha(before[rel]),"exact":True})
        docs.append({"path":rel,"sha256":sha(data),"bytes":len(data)})
    for row in baseline:
        if sha((ROOT / row["path"]).read_bytes()) != row["sha256"]:
            raise RuntimeError("Product drift during doc registration")
    if sha((ROOT / "DocuN/results/TASK-102-result.md").read_bytes()) != "f3bf109c1398b5cf1a8d112f4ebcc55db6d3c0a1f42dc2f92d7aff67377f22b3":
        raise RuntimeError("Design report changed")
    entries = [
        (914,"DocuN/evidence/TASK-103/orchestration-setup-20261006/approval.json","登记用户明确批准上一具体G9-P，合成实施采用生效，原消息确切时刻不编造，旧许可不复活。"),
        (915,decision_rel,"置顶采用已批准及103新完整卡/资源/预算，原待批裁定全字节保留，时间与UNKNOWN规则不扩大。"),
        (916,"DocuN/evidence/TASK-103/orchestration-setup-20261006/resource-preflight.json","只读核cached镜像/旧100停止状态/新名称端口空闲与已装依赖，无Env秘密或启动/DDL，元数据路径错误留记录。"),
        (917,"DocuS/架构动态文档.MD","v0.89登记采用与完整合成实施边界，旧v1/停止主权和未验门保持，未预判新结构/权限通过。"),
        (918,"DocuS/执行动态文档.MD","v2.11登记103/R097占号、批准/独立新预算与资源隔离、核完整卡后待转交，新使用0；旧历史不清零。"),
        (919,"DocuN/tasks/TASK-103.md","保存完整七节长卡，七表/全链/v2/工作区/24性质/普通修复/收尾一成果，稳定后集中独立审计。"),
        (920,"DocuN/evidence/TASK-103/input-snapshot.json","冻结批准合同hash、233产品/测试基线、旧迁移/七规则、具体新许可及当前资源事实，不恢复旧入口。"),
        (921,"DocuN/results/TASK-103-work-decision.md.json","登记新任务授权与待转交的元数据记录，不冒实际执行或另建总进度账。"),
        (922,"DocuN/evidence/TASK-103/orchestration-setup-20261006/product-baseline.json","存实际现有非私配置源/测试/生成物hash，首改保护和最终diff核对，不读取用户配置。"),
        (923,"DocuN/evidence/TASK-103/orchestration-setup-20261006/delivery-proof.json","核七节/全文回读、批准裁定hash/历史/233未变基线/版本编号，新资源启动0、无派发或开始事实。")]
    for _,rel,_ in entries[:-1]:
        if not (ROOT / rel).is_file():
            raise RuntimeError("Cannot log an absent artifact")
    addition="\r\n\r\n"+"\r\n\r\n".join(f"- CHG-{number:04d}，{AT}，Codex编排Agent，{rel}。{description}" for number,rel,description in entries)+"\r\n"
    fresh_json(OUT / "delivery-proof.json",{"at":AT,"G9-P":"user-approved","TASK":"TASK-103","R":"R-097","dispatch":"待转交","sent_received_started":False,
        "recipient":"A+ actual TASK102 window","all_seven_sections":True,"full_card_bytes":len(card_data),"full_card_sha256":sha(card_data),"adopted_decision_sha256":decision_sha,
        "history_exact":histories,"documents":docs,"unchanged_product_baseline":len(baseline),"parent_report_untouched":True,"root_product_writes":0,"root_business_runs":0,"new_resources_created_started":0,
        "versions":{"state":"2.11","architecture":"0.89","requirements":"1.1"},"CHG":{"first":914,"last":923,"next":924},"next_task":"TASK104/R098 planned only",
        "CHG_expected_sha256":sha(before["DocuS/文档变更记录.MD"]+addition.encode("utf-8")),"no_unfilled_decision_placeholder":True,
        "budget_authorization_in_card":True,"resource_metadata_only":True,"independent_audit_not_dispatched":True})
    log_path=ROOT / "DocuS/文档变更记录.MD"
    log_path.write_bytes(before["DocuS/文档变更记录.MD"]+addition.encode("utf-8"))
    actual=log_path.read_bytes()
    if not actual.startswith(before["DocuS/文档变更记录.MD"]) or max(map(int,re.findall(r"CHG-(\d+)",actual.decode("utf-8-sig"))))!=923:
        raise RuntimeError("CHG history/number mismatch")
    print(json.dumps({"adopted":"G9-P","card":str(card_path),"bytes":len(card_data),"product_unchanged":len(baseline),"state":"v2.11","architecture":"v0.89","CHG":"0914-0923; next0924","status":"ready for manual handover","new_resources_started":0},ensure_ascii=False))


if __name__=="__main__":
    main()
