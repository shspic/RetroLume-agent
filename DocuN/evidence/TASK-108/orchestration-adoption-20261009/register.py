"""登记用户采用G11-P与109完整合同，仅维护共享编排文件。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
STAGE = ROOT / "DocuN/evidence/TASK-108/orchestration-adoption-20261009"
OUT = ROOT / "DocuN/evidence/TASK-109/orchestration-setup-20261009"
CARD = ROOT / "DocuN/tasks/TASK-109.md"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def identity(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": sha(data)}


def save(name, obj):
    path = OUT / name
    assert not path.exists(), "断点先核已登记对象，不重复运行覆盖"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    baseline = load(STAGE / "baseline-input.json")
    current = baseline["current_files"]
    resources = load(STAGE / "resource-preflight.json")
    assert len(current) == 363 and not CARD.exists() and not OUT.exists()
    assert not (ROOT / "DocuN/results/TASK-109-result.md").exists()
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    rules = load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
    for item in rules:
        assert sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"]
    package = load(STAGE / "playwright-local-files.json")
    for rel, expected in package["files"].items():
        assert sha((Path(package["path"]) / rel).read_bytes()) == expected
    state_path = ROOT / "DocuS/执行动态文档.MD"
    arch_path = ROOT / "DocuS/架构动态文档.MD"
    change_path = ROOT / "DocuS/文档变更记录.MD"
    work108 = ROOT / "DocuN/results/TASK-108-work-decision.md"
    state_before, arch_before, changes_before, work_before = [p.read_bytes() for p in [state_path, arch_path, change_path, work108]]
    assert "文档 v2.23".encode("utf-8") in state_before[:500] and "文档 v1.01".encode("utf-8") in arch_before[:500]
    assert b"CHG-1049" in changes_before and b"CHG-1050" not in changes_before
    assert sha(work_before) == baseline["work_decision_before"]["sha256"]
    draft = (STAGE / "proposed-task109-card.md").read_bytes()
    text = draft.decode("utf-8")
    sections = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
                "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    assert all("## " + s in text for s in sections) and "*" not in text and "|" not in text
    OUT.mkdir(parents=True)
    for rel, raw in [("DocuS/执行动态文档.MD", state_before), ("DocuS/架构动态文档.MD", arch_before),
                     ("DocuS/文档变更记录.MD", changes_before), ("DocuN/results/TASK-108-work-decision.md", work_before)]:
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
    adoption = {"registered_at": NOW, "user_message": "批准", "client_date": "2026-10-09",
                "message_exact_timestamp": "未提供，不回填为登记时刻", "package": "G11-P",
                "approved_source": baseline["source_contract"], "approved_work_before": baseline["work_decision_before"],
                "approved_proposal_before": baseline["approved_proposal_before"], "adopted": True,
                "execution_only_by_full_TASK109_contract": True, "safety_or_product_pass": False,
                "first_gate_order_unchanged": True, "native_new_engine_not_authorized": True,
                "new_runs_started_by_main": 0}
    adoption_path = STAGE / "adoption-received.json"
    assert not adoption_path.exists()
    adoption_path.write_text(json.dumps(adoption, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # 先由唯一账占号，后保存正式卡。
    reserved = f"# 执行动态文档\n\n文档 v2.24，2026-10-09，Asia/Shanghai。{NOW}用户G11-P采用已登记，TASK109/R103占号登记中、未转交未执行。\n\n## 以下为v2.23及更早历史\n\n"
    state_path.write_bytes(reserved.encode("utf-8") + state_before)
    CARD.write_bytes(draft)
    assert CARD.read_bytes() == draft
    budget = {"permit": "TASK-109-G11-20261009", "status": "待转交，实际首读时固定deadline",
          "seconds": {"active": 21600, "metadata": 10800, "offline_build": 1800, "real": 5400, "cleanup": 900},
          "per_root_seconds": 1200, "H0": {"metadata_seconds": 1800, "official_pages": 4, "root_max": 2, "root_seconds": 900,
              "preview_create_start_max": 4, "image_build_max": 2, "included_in_total_not_extra": True},
          "count_limits": {"root": 8, "image_build": 2, "preview_create": 16, "preview_start": 16,
              "PG_create": 1, "volume_create": 1, "PG_start": 4, "new_databases": 3, "new_LOGIN_roles": 3, "new_NOLOGIN_roles": 2,
              "API_listener": 2, "main_browser": 3, "main_driver": 3, "Reaper_controller_sessions": 2,
              "SUP_attempt": 6, "transport_send": 6, "app_password_reset": 2, "offline_batch": 5,
              "compile_initial": 1, "compile_corrected_recheck": 1, "typecheck_build": 2},
          "subseconds": {"preview_one": 60, "preview_runtime_total": 960, "preview_diagnostic_total": 240,
              "Reaper_controller_one": 1200, "main_browser_one": 1800, "offline_batch_one": 300, "typecheck_build_one": 300,
              "image_build_one": 600},
          "HTTP_limits": {"total": 1024, "PNG": 500, "public_inputs": 300, "fault_internal_inputs": 1200, "inputs_total": 1500},
          "runtime_config": {"preview_per_activity_starts": 3, "preview_per_activity_seconds": 180,
              "preview_one_seconds": 60, "native_manager_seconds": 50, "native_window_and_lease": 20,
              "native_request_timeout": 2, "native_stop_grace": 2, "recovery": False},
          "new_used": 0, "old_real_roots": 70, "old_design_active_metadata_upper_each": 3814.6,
          "old_design_overlap_not_added": True, "old_failure_unknown_money_not_reset": True,
          "Gate_failure_stops_business_schema_API_profile_model": True,
          "build_time_accounting": "image build计real并独立记录，不再计offline重复相加",
          "zero": ["new_native_engine", "real_provider_paid_calls", "dependency_network_install_pull", "user_DB", "data_delete_drop", "Git_write_publish"]}
    save("verification-budget.json", budget)
    original_roots = [ROOT / "AGENTS.md", ROOT / "DocuS/最终需求文档.MD", ROOT / "DocuN/results/TASK-108-result.md"]
    input_doc = {"at": NOW, "TASK": "TASK-109", "R": "R-103", "current_files": current, "objects": len(current),
          "source_contract": baseline["source_contract"], "approved_package": adoption,
          "rules": rules, "resource_preflight": resources,
          "dependency_local_tree": identity(STAGE / "playwright-local-files.json"),
          "static_inputs": [identity(p) for p in original_roots],
          "extra_fact_addendum": identity(ROOT / "DocuN/evidence/TASK-108/design/fact-addendum.json"),
          "source_function_facts": identity(ROOT / "DocuN/evidence/TASK-108/design/source-function-facts.json"),
          "baseline_363_scope_not_whole_untracked_workspace": True, "product_paths_previously_absent": True,
          "mutual_exclusion": "单机preview全局同时1，原107不实现/不运行；旧所有任务资源不启",
          "required_gate_evidence_before_business_phase": True,
          "PG_plan": {"name": "retrolume-task-109-g11-pg1", "volume": "retrolume-task-109-g11-pg1-data", "port": 55449,
              "image": "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f",
              "databases": ["retrolume_task109_main", "retrolume_task109_upgrade", "retrolume_task109_fault"],
              "LOGIN": ["retrolume_task109_bootstrap", "retrolume_task109_app", "retrolume_task109_denied"],
              "NOLOGIN": ["retrolume_html_owner", "retrolume_html_app"]},
          "preview_names": resources["container_names_reserved"][1:], "API": "127.0.0.1:18109",
          "no_fake_provider_listener": True, "budget": budget}
    save("input-baseline.json", input_doc)
    save("resource-preflight.json", resources)
    save("window-assignment.json", {"at": NOW, "TASK": "TASK-109", "R": "R-103", "resource": "A+增强执行",
          "window": "原实际TASK108业务窗口", "fallback": "真实不可续/容量不足则同等A+新业务窗口，不重置号和旧账",
          "independent_107": "保持隔离，计划未来110/R104稳定点审计未占号",
          "status": "待转交", "sent": False, "received": False, "started": False, "new_actual_used": 0})
    adoption_prefix = f"""# TASK-108 / R-102 G11-P采用生效

{NOW}，Codex编排Agent。用户2026-10-09对上一条具体G11-P采用请求明确“批准”，采用生效；确切消息时刻未给，不用登记时刻回填。采用源为67263字节108合同/91d004bf…及其6485字节work-decision/0903a5ff…和先关键关口后业务的收窄，原待采用段保作历史。

具体012四表/两最小NOLOGIN角色、新html_explanation.v1/API007与画面客户端、固定本地依赖派生受限宿主/外部控制及独立preview3次180秒已获采用。批准不是H0/B-01/SEC003或产品通过，不扩页面权/新原生引擎/provider/用户库/安装/费用/删除/Git。先实际可实现机制与有界H0，失败停依赖，成立后才四表/模型/接口完整接线的顺序继续约束。

TASK109/R103完整执行/普通修复/定向取证/精确收尾卡已登记、保存回读，沿原108 A+业务窗口，当前待人工转交，新使用0，无真实接收/开始。运行权限只有109完整卡及其输入/预算定义，108旧许可和参考建议不复活。旧70/FAIL/UNKNOWN/13元及3814.6设计保守重叠账不清零。

## 以下为108设计验收与原采用请求历史

"""
    work108.write_bytes(adoption_prefix.encode("utf-8") + work_before)
    work109 = ROOT / "DocuN/results/TASK-109-work-decision.md"
    assert not work109.exists()
    work109.write_text(f"""# TASK-109 / R-103 G11完整执行授权登记

{NOW}，Codex编排Agent。G11-P用户明确采用，完整执行卡与源合同/先关口序共同为实际授权。当前仅待转交，无真实发送/接收/开始，实际使用0；108设计、G10有限关闭不是HTML动态通过。

基线363对象/公共锁定/111本地包文件一致，preview/012新路径不存在；两镜像缓存/new17容器名/新卷/18109-55449端口无碰撞，主控仅read/hash/metadata，业务创建/运行0。执行前再核归属/前提，不以预检时点抢占新对象。

许可TASK-109-G11-20261009，active21600/metadata10800/offline-build1800/real5400/cleanup900秒，root8/各1200，H0仅metadata1800/官方4页/roots2各900/preview4子限。imagebuild2、previewcreate/start16且同时1/960执行240诊断、PGcreate1卷1/start4/API listener2/main browser-driver3/Reaper session2/nativeSUP和发送各6、app口令2、offline5/compile1+有据1/typecheck-build2；具体子限见完整卡/verification-budget.json，含失败预检，不借旧余额。

H0关键事前否决/sandbox/精确停止真实原件齐后才business Phase。无同步机制或真实反证即停依赖，不建012/PG、不开模型/公开接口，不以CSP截图/after-close降标准，不自动引入CEF/Electron/fork。实际新PG/普通role/镜像/CID/nonce/管道及API资源按卡身份固定，旧106/103/100/088不启。新旧数据/卷/role/容器停后保留，无网络安装/用户库/provider/费用/数据删除/逆迁移/Git或发布。

原108业务A+负责全部实现与普通验证/修复，原107隔离窗保持未来审计。完整稳定后计划TASK110/R104集中安全/一致性终审，当前未占/未出/未派，不自签B01/SEC003/STEP/M-1/项目。正式DocuS和共享编号只编排维护，用户只需转卡带回109结果。
""", encoding="utf-8")
    arch = f"""# 架构动态文档

文档 v1.02，2026-10-09，Asia/Shanghai。需求v1.1、唯一执行动态v2.24。G11-P用户采用生效，TASK109宿主关键关口及完整实施待转交，HTML尚未实现/运行，B-01开放。下面v1.01及历史原字节保留。

## G11采用与实际实施顺序

采用108 A—D及work-decision收窄：新HTMLprofile/父消费、012四表/最小角色、原007同COMMIT/原四账、独立preview次数与时间、有限API/画面客户端/学习回流、固定受限Docker宿主/外部监督。生成HTML不在主应用浏览器执行，页面无网络/文件/系统/模型工具权；默认能力仍关闭，采用不替H0或独立审计。

关键导航/B01/sandbox/物理停止先给实际可实现锚并有界真实证明；失败停业务依赖，不先建模型/接口或更换未授权原生组件。109阶段一仅最小宿主/协议/控制/夹具，关口成立后连续四表/生成/正常UI/预算/故障与收尾；实际源/镜像/输入/协议/加载原件齐后一次隔离安全一致性审计，不按普通步骤拆卡。

主控当前363和111本地依赖文件/镜像/新名字及端口仅只读核，没有编排者执行产品。正式路径config/html.example.json沿既有config，设计backend/config仅历史候选，不建两份。原G3—G10/worker/停止退款主体/001—011/旧合同充分证据不重开，O107-01/02保留。

G11未来允许本卡专用合成PG/预览资源和最低模型替身；不启动旧资源，不准用户库/provider/费用/下载安装/新引擎/数据删除/Git/发布。Linux容器新停止证明不能引用Windows Job代替，真实provider/全Must/退出/整链Compose与Linux-Nginx/自用/M-1/项目仍原关口。

## 以下为v1.01及更早历史

"""
    arch_path.write_bytes(arch.encode("utf-8") + arch_before)
    state = f"""# 执行动态文档

文档 v2.24，2026-10-09，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.02、task_model/阶段07。下面v2.23及全部历史原字节保留。

## G11-P已采用；109完整关口/实现合同待转交

用户对上一条具体G11-P采用请求明确“批准”，采用生效。批准输入为原10867263字节/91d004bf…及原work6485字节/0903a5ff…的先关键关口后业务限定；确切消息时刻未知，不冒登记时间。原待采用条目为历史，不重新问HTML/Docker方向或普通参数。批准仅实现/合成验证许可，H0/B01/SEC003/HTML产品/STEP015016尚未通过。

本包012四表/两最小NOLOGIN角色、专用html_explanation.v1父消费、原007与四账同COMMIT、新有限API/画面/输入/学习回流、受限Docker宿主/外部Supervisor-Reaper和持久preview3次180秒每次60秒已采用。页面能力不扩，主界面不执行原HTML，原Job/四账退款权保持；用户库/provider/真实资料/费用/联网安装/原生新引擎/删除/逆迁移/Git/发布不含。

TASK109/R103已占号，完整七节卡保存回读待人工转交，原实际TASK108业务A+窗负责，原107保持隔离。无真实发送/接收/开始，新实际使用0。110/R104仅未来完整稳定点独立安全/一致性审计计划未占/未出/未派，不审尚未齐整体候选或代执行。

预检363现有对象、锁定规则/源合同、111本地1.62.1包文件匹配，preview/explanations/012不存在；缓存基础c091b21d…与PGcf134a76…metadata可读，新17容器名/新卷无碰撞、18109/55449无监听、venv/vite/WindowsChromium缓存存在。主控仅文件与Docker只读枚举/inspect，未build/create/start/SQL/产品导入/测试；执行前重核不以时点推执行结果。

关键序约束：阶段一实际同步否决锚、B01可信手势/对照、data/blob/动态frame等原性质、非root真sandbox、精确物理停止先行；H0首段metadata1800/官方4页/真实根2各900/preview4/imagebuild2子限计总账。无依据或反证停依赖，不建PG/012/生成profile/API，不能用命名空接口/CSP截图/after-close替证明，不能盲换CEF/Electron/fork。关口齐后同卡连续完整接线/方法/普通修复/收尾。

新许可TASK-109-G11-20261009：active21600、metadata10800、offline-build1800、real5400、独立cleanup900；root8各1200、imagebuild2各600、previewcreate/start16且同时1/运行960/诊断240、PGcreate1卷1/start4、API listener2、main browser-driver3、Reaper/controller2各固定1200、nativeSUP及最低transport分别6、现有新app密码重置2、offline5每批300、内存compile初1+有据1、typecheck-build2每批300。HTTP1024/PNG500/公开input300/内部fault1200/输入总1500共同约束；建议已转具体卡许可，实际用量0，所有失败/预检/UNKNOWN前置计数不返。

H0及普通修复都在上述总额内，正常一API/主浏览器/controller串行完成，已COMMIT/独立成立方法有据继承、不重造效果刷根PASS；同因两修仍败/归属漂移/无关键锚/类上限即停依赖。阶段二只有实际新profile/preview主体与直接受影响旧接口补证，既有G3—G10/旧128等充分未变证明不全面重跑。

预览只本卡preview01—16，无volume/端口/宿主bind/socket/secret，UID10001、networknone/read-only/capdrop/no-new-privileges/privateIPC/保留sandbox/1CPU768MiBpids128/tmpfs限额。主SQL仅新pg1/同名卷/55449、合成main-upgrade-fault三库/本卡三登录role与012领域角色，普通runtime无admin证明替代。新CID/immutable派生image/label/nonce/进程出生及manifest首次创建就冻结；旧106/103/100/088不启，所有新旧容器/数据/卷/role停后保留，禁rm/prune/DROP/DELETE。

新的本地依赖/镜像构建无网络pull/install，stage source/完整包hash/真实加载/binary/许可证明，不用旧044声明或Linux容器借旧Job停止结论。配置示例统一config目录、旧材料/auth默认拒绝/001—011/worker/旧协议/旧模板规则不扩；源码/测试/运行不得依赖公共库或丢失SPIKE实现。

108设计许可已闭，active/metadata3814.6保守重叠/六页失败/编码路径纠正全部保留；原70真实入口不是70次PASS，旧预算/FAIL/UNKNOWN/13元、原R20/recoveryfalse/归档/规则/原始需求不清零。G10/106/107/108设计及DEF024—026/E106-SEM有限关闭、O107-01/02非阻断不重开；真实provider/全部Must/M-1/项目/退出/018Compose-Linux-Nginx/019020仍未来关口。

本批CHG1050—1061，下一CHG1062。用户仅需转109整卡原108 A+业务窗口并带回109结果路径，无新的采用问题或真实数据操作要求。当前尚无执行中的109事实。

## 以下为v2.23及更早历史

"""
    state_path.write_bytes(state.encode("utf-8") + state_before)
    entries = [
        (1050, str(adoption_path.relative_to(ROOT)).replace("\\", "/"), "用户G11-P明确批准采用生效，精确消息时刻未知，原源/裁定hash保留，不签运行安全。"),
        (1051, "DocuN/results/TASK-108-work-decision.md", "置顶实际采用/109具体卡限定，原pending与设计授权原字节保留。"),
        (1052, "DocuN/evidence/TASK-108/orchestration-adoption-20261009/resource-preflight.json", "两缓存image/新17名字新卷/两端口及工具只读可用，不创建启动，完整111本地包manifest保存。"),
        (1053, "DocuS/架构动态文档.MD", "v1.02采用G11具体新域与关口先行，标准/旧权威不降，产品尚未实现。"),
        (1054, "DocuS/执行动态文档.MD", "v2.24先占109/R103后保存待转交，旧70/许可及观察保持，新使用0。"),
        (1055, "DocuN/tasks/TASK-109.md", "完整七节关口/业务/定向验证/普通修复/精确收尾，原108A+窗口，H0未过不铺业务。"),
        (1056, "DocuN/evidence/TASK-109/orchestration-setup-20261009/input-baseline.json", "冻结363/批准输入前后/规则/本地包/新精确resource计划，阶段隔离与旧保护范围。"),
        (1057, "DocuN/evidence/TASK-109/orchestration-setup-20261009/resource-preflight.json", "新PG/预览/镜像/端口只读观察，未来CID第一次创建冻结，不抢占旧资源。"),
        (1058, "DocuN/evidence/TASK-109/orchestration-setup-20261009/verification-budget.json", "21600许可/5400real与H0子限计总额、root及listener等前计，普通有据接续不返失败。"),
        (1059, "DocuN/evidence/TASK-109/orchestration-setup-20261009/window-assignment.json", "原108业务窗待人工转交，107保持独立，110计划未占，实际发送接收开始0。"),
        (1060, "DocuN/results/TASK-109-work-decision.md", "执行授权/门序/精确资源及停止保留登记，不签安全/M-1或最终验收。"),
        (1061, "DocuN/evidence/TASK-109/orchestration-setup-20261009/delivery-proof.json", "七节读回/363及111包未变/版本CHG/报告与共享旧历史字节保留，新实际运行0。")]
    proof = {"at": NOW, "TASK": "TASK-109", "R": "R-103", "card": identity(CARD), "seven_sections": sections,
        "package_adopted": True, "source_objects": len(current), "package_files": package["count"],
        "dispatch": "待转交", "sent_received_started": False, "new_used": 0,
        "shared_history_exact": {"state": state_path.read_bytes().endswith(state_before),
                                 "architecture": arch_path.read_bytes().endswith(arch_before), "work108": work108.read_bytes().endswith(work_before)},
        "source_contract_unchanged": identity(Path(baseline["source_contract"]["path"]))["sha256"] == baseline["source_contract"]["sha256"],
        "first_gate_order_unchanged": True, "main_product_SQL_tests_build_starts": 0,
        "versions": {"state": "v2.24", "architecture": "v1.02"}, "CHG": "1050—1061", "next_CHG": 1062}
    assert all(proof["shared_history_exact"].values()) and proof["source_contract_unchanged"]
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    save("delivery-proof.json", proof)
    assert all((ROOT / rel).exists() for _, rel, _ in entries)
    append = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{NOW}，Codex编排Agent，{rel}。{desc}" for n, rel, desc in entries) + "\n"
    change_path.write_bytes(changes_before + append.encode("utf-8"))
    assert change_path.read_bytes().startswith(changes_before)
    print(json.dumps({"adoption": "G11-P已批准", "card": str(CARD), "card_bytes": len(draft), "source_objects": len(current),
        "state": "v2.24", "architecture": "v1.02", "CHG": "1050—1061", "next_CHG": 1062,
        "dispatch": "待转交", "product_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
