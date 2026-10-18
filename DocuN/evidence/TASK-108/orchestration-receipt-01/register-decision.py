"""登记108设计验收与唯一待采用包，不派未获采用的实现卡。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-108/orchestration-receipt-01"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    path = OUT / name
    assert not path.exists(), "本轮已经登记，先核断点，不重复覆盖"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    receipt = load(OUT / "receipt.json")
    source = load(OUT / "current-baseline.json")
    report = ROOT / "DocuN/results/TASK-108-result.md"
    assert sha(report.read_bytes()) == receipt["report_sha256"]
    for rel, expected in source.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    assert not (ROOT / "DocuN/tasks/TASK-109.md").exists()
    state_path = ROOT / "DocuS/执行动态文档.MD"
    arch_path = ROOT / "DocuS/架构动态文档.MD"
    change_path = ROOT / "DocuS/文档变更记录.MD"
    work_path = ROOT / "DocuN/results/TASK-108-work-decision.md"
    old_state = state_path.read_bytes()
    old_arch = arch_path.read_bytes()
    old_change = change_path.read_bytes()
    old_work = work_path.read_bytes()
    assert "文档 v2.22".encode("utf-8") in old_state[:500]
    assert "文档 v1.00".encode("utf-8") in old_arch[:500]
    assert b"CHG-1042" in old_change and b"CHG-1043" not in old_change
    proposal = {"id": "G11-P", "source_contract": str(report), "source_sha256": receipt["report_sha256"],
        "state": "recommended_pending_user_adoption", "adopted": False, "implementation_authorized": False,
        "already_adopted_not_asked_again": ["FR009应用内交互HTML", "SEC003禁止页面联网/文件/系统/模型工具", "独立受限Docker画面方向"],
        "material_changes": [
            "html_explanation.v1专用生成绑定/父消费隔离，固定消息、无工具，原007及四账同COMMIT",
            "012的html_commands/html_artifacts/html_preview_budgets/html_preview_sessions，两个NOLOGIN最小领域角色及保护/资格函数",
            "API007生成/只读产物/显式预览/有限画面输入/停止，与学习/教学父资格和可访问UI接线",
            "固定缓存基础派生镜像/Playwright1.62.1本地包/必要产品lock及最小seccomp差异，非root/privateIPC/保留browser sandbox",
            "宿主机专用Supervisor/Reaper精确CID控制与新的持久预览次数/时间账，不改旧Windows Job或原四账退款权"],
        "default_proposal": {"starts_per_activity": 3, "seconds_per_activity": 180, "seconds_per_preview": 60,
                             "viewport": [640,480], "frames_per_second": 3, "old_model_budget_auto_increase": False},
        "first_gate": {
            "before_business_tables_profile_model_API_full_wiring": True,
            "first_require_actual_callable_guard_not_named_stub": True,
            "check": ["自身data/blob等导航事前否决锚与B01真实新页拒绝", "固定非root/seccomp/privateIPC保留sandbox", "精确容器可确认物理停止"],
            "fail": "停止依赖，不推进四表/模型调用/公开预览接线，不盲换浏览器或重跑整套",
            "after_creation_close_pause_or_CSP_screenshot_is_not_pass": True,
            "native_CEF_Electron_browser_fork_addition_authorized": False},
        "local_resources_after_adoption_only": {
            "cached_base": "sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac",
            "dependencies": "优先校验本地固定1.62.1包复用并构建；缺包或需要新引擎组件时报告准确差异，不自动联网安装",
            "new_synthetic_PG": "一个专用PG17实例/命名卷，同实例内main/升级/坏schema库；新CID/role/端口在正式卡冻结",
            "preview": "新专用预览容器串行，全局同时至多1个；关口资源计入整卡总上限，不能另加未记账批",
            "new_data_preserved": True, "old_106_103_100_088_resources_not_started": True},
        "planning_caps_not_active_permit": {
            "active_seconds": 21600, "metadata_seconds": 10800,
            "preview_creates_starts_total": 16, "preview_runtime_total_seconds": 960, "preview_diagnostic_total_seconds": 240,
            "native_model_attempts_total": 6, "model_provider_paid_or_external": 0,
            "normal_one_API_one_main_browser_session": True,
            "real_root_API_listener_container_start_build_counts": "正式卡先核现存资源与最低样本后统一冻结；建议不赋执行许可"},
        "audit": "完整稳定后一次隔离增强安全/一致性终审，原107窗口可沿用，不用采用批准代替安全票据",
        "forbidden": ["原HTML在主应用浏览器执行", "新页面/宿主文件/系统/模型工具能力", "root/no-sandbox/privileged/SYS_ADMIN/hostIPC/hostnetwork/挂载/socket/开放端口",
                      "真实用户库/资料/private配置/密钥/provider/付费/用户数据外发", "数据DELETE/DROP/逆迁移", "联网安装/浏览器fork默认引入", "Git提交推送/部署发布"],
        "rollback": "失败关闭新能力，精确停止并保留事实；不逆迁移或删除数据",
        "TASK109_R103": "未占号未出卡未派发；采用后才正式冻结完整执行合同"}
    save("adoption-proposal.json", proposal)
    work = f"""# TASK-108 / R-102 设计验收关闭与G11-P待采用裁定

{NOW}，Codex编排Agent。108实际返回67263字节/91d004bfde204c83b8f8387d8df2489e72889ef4d53935a63b80ad46693e4710。363当前对象、9合同输入、7锁定规则、17追加读入及11文件221函数AST位置匹配；一次文档一致性自检与A—D完整，产品/源码/运行0。编排验收关闭108只读设计交付，不把设计、静态候选或采用批准当B-01/HTML安全与实际闭环通过。

## 唯一请求：采用G11-P，关键宿主关口先行

当前仅recommended_pending_user_adoption，implementation_authorized=false。原FR009/SEC003/独立Docker方向不重新审批；这次需要采用的是具体新模型、公开接口及运行资源主权。完整字段/协议/文件/失败与D矩阵以原108 A—D为准，以下编排序与禁止收窄优先；普通参数不拆成多次决定。

1 新html_explanation.v1生成profile/专用父消费，012四表html_commands/html_artifacts/html_preview_budgets/html_preview_sessions、两个NOLOGIN最小角色及相应保护资格函数。合格正文/007/领域产物同COMMIT，原四账/UNKNOWN/无自动重发不改变；不更改001—011原件或旧业务数据。

2 新API007显式生成/原键核对/产物读取/预览/有限输入和停止、可访问画面客户端与学习/教学父接线。HTML不在主应用可信源执行，不给页面业务工具/模型或文件权限；失效、回包丢失/刷新与迟到处理以真实身份/资格为准。

3 专用非root受限Docker可信宿主/wrapper/sandbox子frame、外部Supervisor/Reaper精确CID控制和持久独立preview额度，建议每activity3次/累计180秒/每次至多60秒；这不是旧模型执行时间额度增加，也不是无限免费预览。固定镜像/本地包派生构建与最小seccomp差异必须逐项绑定；旧Job/停止/原四账退款权不变。

## 执行顺序与未核关口

报告明确NavigationGate全协议事前否决没有现成可实现锚，固定sandbox/节点版本和物理树空也未运行。采用若生效，正式实现卡先给出实际可调用的守卫依据，并以有界新合成资源验证自身data/blob关键导航、B01、非root/sandbox/精确停止；不接受命名空接口、静态CSP截图或创建后close/暂停来签事前阻断。

关口成立后才推进四表迁移/生成模型调用/API和完整业务接线；关口失败就保存精确原件并停依赖，不先铺整套业务、再发现宿主无法交付，也不连续换浏览器/组件盲试。原报告允许先完成独立生成/持久部分的顺序，在本次采用请求中收紧为关键宿主先行。需要CEF/Electron/浏览器fork或其他原生新组件时，交准确差异/来源/成本另裁，当前包不授权暗加引擎或降低标准。

本包只请求本机合成实现与定向验证：复用精确缓存基础与校验的本地Playwright1.62.1运行包构建派生镜像；若本地材料不足，不自动联网安装/pull。采用后正式卡冻结一个新合成PG17实例/main及同cluster升级/坏schema库、专用卷/普通role、精确新预览CID/image/标签/限制、API/浏览器会话与计时账。所有旧106/103/100/088资源停止保留，不启动或删除；新数据/卷/容器/role也停后保留，不DROP/DELETE。

整卡参考上界包含首次和有据修复：预览create/start至多16、同时1、总执行960/诊断240秒，原生最低传输替身至多6、零真实provider与费用，active21600/metadata10800秒。关口用量计入总账，一API/主浏览器会话尽量串行；其他真实入口/监听/构建/收尾类别在采用后的正式卡按实际资源统一冻结，建议数字尚不构成许可，不借108剩余。充分未改G3—G10证据继承，完整稳定点一次隔离增强安全/一致性终审。

## 禁止和恢复

禁止新页面网络/宿主文件/系统/模型工具能力，root/no-sandbox/privileged/SYS_ADMIN/hostIPC/network、宿主挂载/socket/开放端口、真实用户库/资料/private配置/密钥/provider/费用/外发、联网安装、数据删除/逆迁移、Git提交推送或部署发布。普通失败恢复为关闭HTML能力、精确停止和保留新旧事实；没有成功H0和必要独立审计不得启用用户生成/预览，也不降级裸HTML。

原108许可结束：active/metadata各3814.6保守上界，metadata按全部active重叠计、不可相加成两份墙钟；官方6/6含失败页、两次编码/四路径纠正及未核固定151源码原文保持。原70入口/FAIL/UNKNOWN/13元历史及G10有限关闭不重置，不要求恢复旧SPIKE目录或重跑旧四容器套件。

采用关口依据锁定公共DocuS/AGENTS.MD第2节：改变主要数据模型/公开接口等须先形成具体影响并处理缺少的决定；原需求批准不等于012/新profile/公开预览/专用控制和新额度已获采用。本次只对上述一个具体G11-P决定，不问普通配置项。当前TASK109/R103仅未来计划未占/未出/未派，新实际执行0；用户决定后由编排出完整卡，不提前激活建议预算。

## 以下为108原设计授权历史

"""
    work_path.write_bytes(work.encode("utf-8") + old_work)
    arch = f"""# 架构动态文档

文档 v1.01，2026-10-09，Asia/Shanghai。需求v1.1、唯一执行动态v2.23。G11 A—D设计交付已验收，唯一G11-P待采用，HTML宿主与接线未实施/未运行，B-01开放。下面v1.00及历史原字节保留。

## HTML完整候选与关键关口先行

108推荐专用html_explanation.v1/父成果适配、012四表/最小角色、007同COMMIT/原四账、独立非root受限Docker可信wrapper/sandbox子frame、宿主机Supervisor/Reaper、有限画面/输入和可访问学习回流。拟新增持久preview3次/180秒/每次60秒额度独立于旧模型时间，尚未采用；主页面不执行HTML、页面无模型/工具/网络文件权、UNKNOWN不重发保持。

原候选缓存镜像与本地1.62.1包元数据已读，但实际Node/browser/许可证/sandbox、全协议自身导航与动态frame事前否决锚、物理容器树空未验证。NavigationGate是未解必需性质，不是一份现成已核API；不能用新页创建后暂停、CSP或源码声明直接闭B-01/SEC003。108只做设计，旧044有限Review及外部旧源缺失限制保持。

唯一G11-P包含具体新profile/四表角色/API/依赖构建/专用Docker控制/preview主权，待用户采用。编排序收紧为先实际可实现锚及有界H0关键验证，成立后才四表/生成/公开接口与完整接线；失败停宿主依赖，不扩CEF/Electron/浏览器fork或暗降权限。采用不替运行安全和稳定点独立终审，不先造大段不可交付业务来掩盖未知宿主。

本轮363当前源、9输入、7规则/17追加源/221函数身份匹配，产品未写未运行；G10及DEF024—026/E106-SEM有限关闭不重开，原O107-01/02及旧失败/预算保持。HTML、完整provider/向量、退出恢复、Compose/Linux/Nginx与最终自用/全部Must/M-1/项目仍后续关口。建议模型/预算/权限与运行只是待采用合同，实际指令仍未来正式任务卡。

## 以下为v1.00及更早历史

"""
    arch_path.write_bytes(arch.encode("utf-8") + old_arch)
    state = f"""# 执行动态文档

文档 v2.23，2026-10-09，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.01、task_model/阶段07。下面v2.22及全部历史原字节保留。

## 108设计已验收；唯一G11-P待采用

TASK108/R102已实际返回，67263字节/91d004bf…与一次文档核对收据/session一致。A—D完整，当前363对象/9输入/7锁定规则/17追加必要源无漂移，11文件221函数AST位置匹配。编排验收关闭只读完整设计交付，接受已明确的待采用包及未核技术条件；不把文档/规范/缓存声明当程序、安全或HTML产品通过，主控产品/SQL/compile/test/build/资源启动0。

推荐G11-P尚未采用：html_explanation.v1新生成binding/父消费、012四表/两NOLOGIN最小角色、API007新公开动作及画面UI/学习回流、固定本地依赖派生非rootDocker宿主/外部Supervisor-Reaper、preview3次/180秒/每次60秒的新持久额度。原FR009/SEC003和独立Docker方向已批准，不重复问；具体主要模型/公开接口/控制与额度新增需一次采用，implementation_authorized=false。

核心未核是NavigationGate全协议自身导航及新frame的事前否决实际锚、固定sandbox/Node/browser/许可身份、精确容器物理树空证据。预览仍关闭，B-01/STEP015—016未实现未验证。既有主页面不执行原HTML/默认禁网文件系统模型工具、创建后暂停不等创建前拒绝、安全独立审计门保持；未核不假称已经实现或可凭模型自评通过。

采用请求内的编排顺序收紧：先有限确认实际守卫依据并有界H0验证自身data/blob等关键导航、B01/nonroot sandbox/精确停止，成立后才新四表迁移/模型调用/接口与完整接线。失败交准确原件，停依赖而不先铺全套业务或盲换内核。新的CEF/Electron/浏览器fork不在包内，必须另外准确差异/成本裁定。用户若采用，正式109完整卡再冻结精确对象与预算；无安全票据不得开放用户功能。

新合成运行建议不生效：一个新PG17实例及同cluster合成库、串行专用preview/container、一个API及持久主浏览器、最低传输替身；参考整卡预览create/start16含关口与修复、执行960/诊断240秒、模型6且零provider费用、active21600/metadata10800。精确CID/image/role/端口/root及监听类别上限待正式卡，旧资源不启、新旧数据停后保留。当前没有create/build/pull/SQL/app/browser/模型实际启动或授权；本地缓存依赖优先，缺料/新组件不自动联网安装。

108设计许可结束：首读2026-10-08T23:40:45+08:00，交付2026-10-09T00:43:19.651978+08:00；active与metadata各3814.6保守上界，metadata与active重叠不相加。官方6/6含固定151源码读取失败和CDP索引有限，原编码/路径错误及未核限制保留。原70入口/所有FAIL/UNKNOWN/13元与各结束许可不返额；旧SPIKE017缺源不造副本/恢复许可，未重跑四容器套件。

TASK109/R103仅未来计划未占/未出/未派，尚未收到G11-P有效采用决定，无新在途执行者。原108业务A+可在采用后承接完整实施；原107维持独立审计资源。旧G10/106/107及DEF024/025/026/E106-SEM有限关闭/O107-01/02非阻断、原R20/recoveryfalse/归档/规则/用户原始需求不变。

STEP017数据退出/恢复、018整链/Compose及Linux-Nginx界限、019风险独立验收、020自用交接和真实provider/完整向量/全部Must/M-1/项目仍沿原路线，不被设计交付放行。不为本方案追加泛读独立审计或产品前置测试；真正宿主H0和稳定点独立安全审计在获得采用/运行卡后执行。

本批CHG1043—1049，下一CHG1050。唯一必要用户决定为采用上述具体G11-P，理由与字段/资源/禁止/先关口序均在108-work-decision置顶；不是再次批准原HTML需求，也不询问普通参数。

## 以下为v2.22及更早历史

"""
    state_path.write_bytes(state.encode("utf-8") + old_state)
    entries = [
        (1043, "DocuN/evidence/TASK-108/orchestration-receipt-01/receive.py", "纯文件/hash/函数AST普通设计回收，不导入或运行产品。"),
        (1044, "DocuN/evidence/TASK-108/orchestration-receipt-01/receipt.json", "67263合同/363源/9输入/7规则/17追加/221定位，一次文档自检身份核证，设计交付关闭而安全not_run。"),
        (1045, "DocuN/evidence/TASK-108/orchestration-receipt-01/adoption-proposal.json", "唯一具体G11-P pending，新模型/API/控制与preview额度，关口先于业务及未知原生组件排除。"),
        (1046, "DocuN/results/TASK-108-work-decision.md", "置顶设计验收与合并采用请求/精确禁止/先H0停依赖序，原许可与FAIL完整保留。"),
        (1047, "DocuS/架构动态文档.MD", "v1.01完整HTML候选与实际缺口，B-01开放，不将NavigationGate名称当现成机制。"),
        (1048, "DocuS/执行动态文档.MD", "v2.23关闭108设计/新包未采用/109未占未派，原70与3814.6保守重叠账不返，唯一决定待用户。"),
        (1049, "DocuN/evidence/TASK-108/orchestration-receipt-01/delivery-proof.json", "共享历史/原报告/363源/条件序与未占号回读，新实际运行0。")]
    proof = {"at": NOW, "report_bytes": receipt["report_bytes"], "report_sha256": receipt["report_sha256"],
             "design_accepted_closed": True, "G11_P": "recommended_pending_user_adoption", "implementation_authorized": False,
             "work_decision": {"path": str(work_path), "bytes": len(work_path.read_bytes()), "sha256": sha(work_path.read_bytes())},
             "source_scope_still_unchanged": len(source),
             "shared_history_exact": {"state": state_path.read_bytes().endswith(old_state), "architecture": arch_path.read_bytes().endswith(old_arch),
                                      "work108": work_path.read_bytes().endswith(old_work)},
             "TASK109_R103_not_reserved_card_sent_or_started": True,
             "no_B01_STEP015016_M1_project_pass": True, "main_product_runs": 0,
             "CHG": "1043—1049", "next_CHG": 1050}
    assert all(proof["shared_history_exact"].values())
    assert sha(report.read_bytes()) == receipt["report_sha256"]
    for rel, expected in source.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    save("delivery-proof.json", proof)
    assert all((ROOT / rel).exists() for _, rel, _ in entries)
    appended = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{NOW}，Codex编排Agent，{rel}。{description}" for n, rel, description in entries) + "\n"
    change_path.write_bytes(old_change + appended.encode("utf-8"))
    assert change_path.read_bytes().startswith(old_change)
    print(json.dumps({"design_closed": "TASK108/R102", "G11_P": "待一次采用", "state": "v2.23", "architecture": "v1.01",
          "decision_file": str(work_path), "source_objects": len(source), "CHG": "1043—1049", "next_CHG": 1050,
          "109_reserved": False, "runtime": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
