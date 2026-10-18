"""串行登记106真实回收和107完整终审合同，仅维护编排材料。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-106"
RECEIPT = BASE / "orchestration-receipt-02"
NEW = ROOT / "DocuN/evidence/TASK-107/orchestration-setup-20261008"
CARD = ROOT / "DocuN/tasks/TASK-107.md"
REPORT = ROOT / "DocuN/results/TASK-106-result.md"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(name, value):
    path = NEW / name
    assert not path.exists(), "不覆盖既有编排产物"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prefix(path, text, marker):
    old = path.read_bytes()
    assert marker.encode("utf-8") not in old[:4000], "本轮已登记，不重复写入"
    path.write_bytes(text.encode("utf-8") + old)
    return old


def identity(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": sha(data)}


def main():
    receipt = load(RECEIPT / "receipt.json")
    current = load(RECEIPT / "current-baseline.json")
    assert not CARD.exists() and not (ROOT / "DocuN/results/TASK-107-result.md").exists()
    assert not NEW.exists(), "存在107登记断点，先核已生效部分，不重跑"
    assert sha(REPORT.read_bytes()) == receipt["report_sha256"]
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected, rel
    state_path = ROOT / "DocuS/执行动态文档.MD"
    arch_path = ROOT / "DocuS/架构动态文档.MD"
    change_path = ROOT / "DocuS/文档变更记录.MD"
    state_before = state_path.read_bytes()
    arch_before = arch_path.read_bytes()
    change_before = change_path.read_bytes()
    assert "文档 v2.20".encode("utf-8") in state_before[:500]
    assert "文档 v0.98".encode("utf-8") in arch_before[:500]
    assert b"CHG-1017" in change_before and b"CHG-1018" not in change_before
    draft = (RECEIPT / "proposed-task107-card.md").read_bytes()
    text = draft.decode("utf-8")
    headings = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
                "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    assert all("## " + h in text for h in headings)
    assert "*" not in text and "|" not in text
    NEW.mkdir(parents=True)
    # 占号先于正式任务卡保存；若后续中断，唯一状态仍能定位已占的107。
    registering = (f"# 执行动态文档\n\n文档 v2.21，2026-10-08，Asia/Shanghai。需求v1.1、架构待同步v0.99。"
                   f"{NOW}已占TASK107/R101：集中独立终审与最后浏览器取证，合同登记中、未转交未执行。"
                   "106续作01已实际返回并停止，旧许可不恢复。\n\n## 以下为v2.20及更早历史\n\n")
    state_path.write_bytes(registering.encode("utf-8") + state_before)
    CARD.write_bytes(draft)
    assert CARD.read_bytes() == draft
    baseline = load(BASE / "orchestration-setup-20261008/baseline-input.json")["current_files"]
    original_map = load(BASE / "implementation-map.json")
    production = list(dict.fromkeys(original_map["modified"] + original_map["new_backend"] + original_map["new_frontend"]))
    production_rows = [{"path": rel, "before_G10": baseline.get(rel), "current": current[rel]} for rel in production]
    budget = {"permit": "TASK-107-G10-AUDIT-20261008", "start_fact": "待转交，未实际接收或开始",
              "seconds": {"active": 21600, "metadata": 10800, "own_fixture_offline": 600, "real": 1800, "cleanup": 600},
              "count_limits": {"root": 3, "container_start": 3, "listener_start": 3, "browser": 3, "driver": 3,
                  "own_fixture_offline_batch": 3, "SUP_attempt": 8, "transport_send": 8, "app_password_reset": 2,
                  "product_compile_tests_build": 0, "migration": 0, "new_container_volume_database_role": 0},
              "used": "全部新计数0；实际接收时固定deadline，不改变旧账",
              "per_root_seconds": 900, "per_offline_batch_seconds": 180,
              "normal_plan": "一次pg1启动、一个API会话、一个浏览器会话串行B1—3",
              "additional_attempts": "仅本卡明确夹具缺陷有据修正；同因两次修正仍失败停止；不重做已COMMIT",
              "old_permits_closed": ["TASK-106-G10-20261008", "TASK-106-G10-C01-20261008"],
              "old_real_entries": 67, "old_counts": receipt["counts"], "old_seconds": receipt["seconds"],
              "old_active_checkpoint": receipt["active_checkpoint"],
              "old_delivery_active_elapsed": receipt["delivery_active_elapsed"], "no_refund_unknown_or_failures": True}
    write("verification-budget.json", budget)
    resources = load(RECEIPT / "resource-readonly.json")
    setup_inputs = [BASE / "orchestration-setup-20261008/baseline-input.json", BASE / "implementation-map.json",
                    BASE / "final/baseline-post-and-build-identity.json", BASE / "final/run-index.json",
                    BASE / "continuation-01/final/baseline-diff-build.json", BASE / "continuation-01/final/post-source.json",
                    BASE / "continuation-01/final/run-index.json", BASE / "continuation-01/final/matrix.json",
                    BASE / "continuation-01/final/session-close.json", BASE / "continuation-01/final/resource-stop-proof.json"]
    originals = load(RECEIPT / "evidence-identities.json")
    write("evidence-pointer-index.json", {"navigation": [identity(p) for p in setup_inputs],
          "C01_raw_records_and_final_navigation": originals,
          "not_auditor_pass_answers": True, "summaries_not_primary_proof": True,
          "old_raw_run_index": str(BASE / "final/run-index.json"), "no_implementation_report_read": True})
    snapshot = load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
    for item in snapshot:
        assert sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"]
    write("audit-input.json", {"at": NOW, "TASK": "TASK-107", "R": "R-101", "parent": "TASK-106/R-100",
          "contract": identity(ROOT / "DocuN/results/TASK-105-result.md"),
          "approved_limits": identity(ROOT / "DocuN/results/TASK-105-work-decision.md"),
          "execution_contract": identity(ROOT / "DocuN/tasks/TASK-106.md"),
          "rules": snapshot, "current_files": current, "current_objects": len(current),
          "all_G10_production_actual_scope": production_rows,
          "initial_baseline": str(BASE / "orchestration-setup-20261008/baseline-input.json"),
          "C01_prebaseline": str(BASE / "orchestration-receipt-01/current-baseline.json"),
          "current_snapshot": str(BASE / "continuation-01/final/post"),
          "current_diff": str(BASE / "continuation-01/final/diff"),
          "C01_changed_and_build": str(BASE / "continuation-01/final/baseline-diff-build.json"),
          "raw_navigation": str(NEW / "evidence-pointer-index.json"),
          "resource_readonly_at": resources["at"], "exact_resources": resources["containers"],
          "runtime_allowed_container": "dca7942c0b39c136fbdfd9f38dafdabd60571ad472539a8961fe0bc3f2fa34e4",
          "runtime_database": "retrolume_task106_main", "runtime_role": "retrolume_task106_app",
          "API": "http://127.0.0.1:18106", "pg2_pg3_starts_SQL_allowed": False,
          "catalog_fingerprint": "13e3d8d9d78d7f6e119a226be6f4d6f3163b9bf5eaeeb1b8d66e5d44351f850b",
          "original_browser_seed": str(BASE / "continuation-01/runs/P04-resume-real-cancel-and-config/browser-seed.json"),
          "remaining_methods": ["B1历史答案UI修订及新反馈", "B2原键显式恢复与真实COMMIT响应丢失", "B3同活动view及key/hash/owner迟到守卫"],
          "product_write_allowed": False, "own_fixture_write_allowed": True,
          "bounded_synthetic_API_writes_native_allowed": True,
          "read_implementation_report_self_review_chat": False, "budget": budget,
          "independent_judgment_required": True, "dynamic_pass_or_DEF_closure_presupplied": False})
    write("window-assignment.json", {"at": NOW, "TASK": "TASK-107", "R": "R-101", "resource": "A+增强执行",
          "window": "原实际TASK104独立审计窗口，未参与105/106", "fallback": "若受污染或不可续，未参与105/106的独立新A+窗口",
          "original_106": "停止等待，不与107并行产品写或运行", "delegation": "人工转卡",
          "state": "待转交", "sent": False, "received": False, "started": False, "execution_used": 0})
    work_prefix = f"""# TASK-106 / R-100 续作01回收与集中收口裁定

{NOW}，Codex编排Agent。真实报告33407字节/700da005e9e327d24f2eb504e875ffcf554034e7befcf83684d80ac3c9cab515；原21949字节报告精确后缀保留。当前363对象及final/post相同，相对346基线339未变，5份生产源码修正及构建链匹配，10批记录/92原件导航身份核证。三CID停止、相关五端口无监听；主控仅元数据，业务运行0。

普通接受四核心修复候选、已保存的后端原件及收尾，不签完整G10、不关DEF024/025/026/E106-SEM。剩余为历史修订/新反馈UI、原键确认及模型提交后丢响应、同activity视图与意图迟到守卫三组浏览器方法。真实已经成立的后端分支不为整根PASS重做，原C01四个真实FAIL和一个离线FAIL及旧失败不改写。

C01许可结束，root6/8、start7/12、listener6/6、browser-driver2/3、SUP28/32/transport26/32、password2/2；收尾active6601.980466、交付active6792.3594045分列，offline15.9083644/real266.4731189/cleanup6.2744921/metadata600保守，名义余额不恢复。旧45+16+6共67真实入口，不是成功批数。

重新编排依据是代码与后端稳定，未齐部分现在为最后UI取证；配置分组与夹具失败共享监听限额造成末验反复截断，不继续发相同106-C02。新TASK107/R101集中独立终审附最后UI补证，原104独立A+窗口，一个持久API会话承载三组方法；只修自己的验证夹具，确定产品缺陷才合并回原106。独立产品只读与本卡精确合成API写/原生取证边界分开，未降低必需审计或UI标准。

新许可TASK-107-G10-AUDIT-20261008的精确main资源、秒数/计数、原账沿用与停止见107完整卡。源/SQL权限/旧worker/001—011/dist冻结，其他两库不启动，真实用户/provider/费用/新资源/安装/删除/Git0。107调度待人工转交，新使用0，尚无真实接收/开始。原106暂停；完整G10/STEP014/M-1/项目仍待最终裁定。

## 以下为初轮及续作01历史裁定

"""
    work_path = ROOT / "DocuN/results/TASK-106-work-decision.md"
    work_before = prefix(work_path, work_prefix, "续作01回收与集中收口裁定")
    new_work = ROOT / "DocuN/results/TASK-107-work-decision.md"
    assert not new_work.exists()
    new_work.write_text(f"""# TASK-107 / R-101 调度与有限取证授权登记

{NOW}，Codex编排Agent。106源码修复与后端证据已实际返回，三组浏览器最后取证尚缺。新107为原批准G10完整成果的必需集中独立审计，附同卡B1—3受控取证，不是实现续作或动态通过声明。

任务卡七节完整保存，363冻结对象/原308基线/实际28生产影响路径和92续作原件指针可独立核。接收原104未参与105/106的独立A+窗口；原106停止等结果。新许可TASK-107-G10-AUDIT-20261008，active21600/metadata10800/自有fixture离线600/real1800/cleanup600秒，root/start/API/browser-driver各3、原生SUP8/最低transport8分别计、现有合成app口令重置≤2。

只读产品与全部旧证据，自有fixture写本卡命名域；允许精确pg1/main普通app下通过既有API作B1—3必要合成动作/原键明确恢复，最低传输替身零外网。源码/SQL/ACL/001—011/dist冻结，pg2/3只读元数据，不DROP/DELETE、新建/安装/provider/用户库/Git。旧失败/预算/COMMIT/UNKNOWN不清零，一API会话预期整卡收口，只有确切本卡夹具修正才有据复验，原通过部分不重复执行。

当前待转交，尚无真实发送/接收/开始，新使用0。代码/证据/控制分别独立裁定，无相关阻断才能建议批准G10有限范围关闭；最终验收由编排，DEF/STEP/M-1/项目不预签。本文件是编排授权登记，不是给审计者的通过答案；具体动作仅完整107卡定义。
""", encoding="utf-8")
    architecture = f"""# 架构动态文档

文档 v0.99，2026-10-08，Asia/Shanghai。需求v1.1、唯一执行动态v2.21。G10源码修正及后端证据候选已齐，最后UI取证与集中独立终审并入107；未签G10通过。下面v0.98及历史原字节保留。

## G10稳定候选与集中收口

续作01修改新interview_repository历史答案资格与service caller取消收尾、InterviewWorkspace/Api/Intents历史修订及同activity视图/原意图身份守卫。339原对象未变，最终363文件含源码/fixture/dist与保存快照相同，最终bundle冻结；001—011和原worker/停止/账本主权未改。新T/H原句支持及真正后继抑制/取消/不可靠选择/消费/HTTP反例已有原件，未以结构/位置替语义、未当通用provider质量证据。

代码修复与后端记录普通接受为候选，DEF024/025/026和E106-SEM等待独立裁定，不预关。剩余历史修订UI、原键/模型COMMIT丢回包、same-activity view/key/hash/owner迟到三个方法，107集中审完整G10实际变化并用一个API会话补UI；审计只改自己的夹具、产品冻结，确定产品问题回原106合并修复。

验证权限限精确106 pg1/main和旧公开动作/真实原生链，其他两库停止不启，替身只最低传输，用户/provider/删除/新资源/平台改变不含。已充分旧G3—G9与后端原件继承，不重审未变系统；单机、UNKNOWN不重发/不退款及真实语义建议边界不变。G10/STEP014/M-1/全项目未验收，后续HTML/退出恢复/整链Compose/Linux/Nginx与本人自用仍按批准路线。

## 以下为v0.98及更早历史

"""
    arch_path.write_bytes(architecture.encode("utf-8") + arch_before)
    state = f"""# 执行动态文档

文档 v2.21，2026-10-08，Asia/Shanghai。唯一总状态账；需求v1.1、架构v0.99、task_model/阶段07。下面v2.20及全部历史原字节保留。

## 106续作01已返回；107集中终审与最后浏览器取证

106/R100续作01已实际返回，普通回收部分通过。报告33407字节/700da005…，旧21949字节精确后缀保留；当前363对象/final post全部一致，346修正前基线中339未变、5生产源码及构建替换匹配，10批记录/92原始事实与导航hash可重建。三精确CID均Stopped/Pid0，18106/18107/55446—55448无监听；主控产品写/测试/build/SQL/资源启动0。

四核心代码候选齐：T/H最低合成response引用真正原句；历史早期answer最高版本资格及UI另存；同activity expected view/key/hash/owner逐await恢复守卫；caller取消等待已有原生任务及有界一次finish。新T/H两轮、后继递归抑制/新review、澄清/newscope、probe限深、G9选择/M6不可靠、跨消费/旧合法入口、准确重复HTTP协程取消及COMMIT/mark两序/DB不可读、HTTP大小/配置拒绝已有原件。独立未审前不关闭DEF024/025/026/E106-SEM，不凭修码和根PASS预签。

实际剩余只有最后浏览器三组方法：历史答案显式另存与新反馈UI；accepted原键明确提交及模型COMMIT丢响应后刷新/只读确认；同activity view/intent身份变化的迟到守卫。原P03重复标签、P06下一题刷新未完即选历史的夹具错误原FAIL保留，最新wait/selector只有语法验证不冒实机。后端已经成立的效果/引用/取消/权限不重做以换整根绿。

C01许可关闭：root6/8、start7/12、listener6/6、browser-driver2/3、offline3/4、build1/2、compile初批1/1和复检1/1、SUP28/32、transport26/32、口令2/2，新资源0。active6601.980466收尾检查点及交付6792.3594045分列，offline/build15.9083644、real266.4731189、cleanup6.2744921、metadata600保守不返；旧45+初16+续6=67真实入口不是67PASS，四真实FAIL/一离线FAIL和原旧未知/费用/COMMIT/no-op均留。名义剩root2/SUP4等不授执行。

编排调整：配置分组和浏览器夹具错误共用有限监听额度，完整末验反复被截断，属预算/组织问题。现源码/后端稳定，不再出同一106-C02；将最后UI取证纳入原计划107集中独立终审，一API会话连续完成，不绕过独立审计或缺证门。原106停止待结果；确有产品缺陷才合并回原106修一次，原107只复查实际增量及影响，不为每个脚本错误再转卡。

TASK107/R101已占号，完整七节合同保存回读，A+原实际TASK104独立窗口优先；必须未参与105/106，否则独立新A+，既有审计历史披露。新G10实际28生产路径/初308基线/最终363与原证据给独立对象，不读106自评或实现聊天。调度待人工转交，新使用0，无实际发送/接收/开始，不记录虚假在途。

新许可TASK-107-G10-AUDIT-20261008：active21600/metadata10800/自有fixture离线600/real1800/独立cleanup600秒，root≤3各≤900、container start/API listener/browser-driver各≤3、离线3各≤180、nativeSUP8/最低transport8分别前计、现有合成app密码重置≤2。预期只一pg1/start/API/browser会话，另外两次限有原件定位的本卡夹具纠错；同因两修仍败停止、所有失败和旧次数延续，不花满额度造测试。

允许107自有fixture/证据写；产品/001—011/ACL/S1/dist/旧fixture及106原件冻结。验证合成写仅精确CID dca7942c…/main/55446普通retrolume_task106_app与既有API动作/合法旧未认领原键；实际ledger/worker/SUP/Job/提交保持，最低替身零外网。pg2/3只metadata不启SQL，旧卷/label/镜像/1CPU512MiB128pids保持。凭据RAM且角色属性ACL不改；DELETE/DROP、新容器/卷/库/role、安装、真实provider/用户数据/费用/Git0。

G9/103/104/105及旧有限DEF019—023关闭不重开，O01—03非阻断、原R20/UNKNOWN/recoveryfalse/预算/归档/规则/原始需求不变。G10/STEP014/全部Must/M-1/项目仍未签验收，后续路线不撤。待107合格实际回传再裁定106/107有限关闭；TASK108/R102仅必要后续计划未占/未出。

本批CHG1018—1029，下一CHG1030。用户必要动作仅转107整卡给原104独立A+窗口并带回107结果路径；不再向用户重复索取G10-P批准。

## 以下为v2.20及更早历史

"""
    state_path.write_bytes(state.encode("utf-8") + state_before)
    entries = [
        (1018, "DocuN/evidence/TASK-106/orchestration-receipt-02/receive.py", "纯元数据回收脚本，实际核源/原件/历史/精确CID，不运行产品。"),
        (1019, "DocuN/evidence/TASK-106/orchestration-receipt-02/receipt.json", "续作01真实回收363文件/10记录/92原件指针/33407报告/旧精确后缀及三CID停止，配套快照与备份保存。"),
        (1020, "DocuN/results/TASK-106-work-decision.md", "置顶候选接受/原新账/三组UI剩余及集中收口，原历史字节保持；旧106暂停。"),
        (1021, "DocuS/架构动态文档.MD", "v0.99同步五源修正与后端候选，集中107附最后UI，未签通过。"),
        (1022, "DocuS/执行动态文档.MD", "v2.21占107/R101先登记后存卡待转交，67原新入口/旧许可关闭与集中安排，不虚称已派发。"),
        (1023, "DocuN/tasks/TASK-107.md", "完整七节集中独立代码/证据/控制终审与最后三组真实UI，产品只读/自有夹具纠错/一持久API会话。"),
        (1024, "DocuN/evidence/TASK-107/orchestration-setup-20261008/audit-input.json", "当前363和初308/实际28生产路径/原件/锁定规则/精确资源，独立输入不预供通过结论。"),
        (1025, "DocuN/evidence/TASK-107/orchestration-setup-20261008/evidence-pointer-index.json", "原21批及续10批实际导航/92文件hash，版本和FAIL限制保持，不读取实现自评。"),
        (1026, "DocuN/evidence/TASK-107/orchestration-setup-20261008/verification-budget.json", "新21600许可/root3/监听3/SUP8发送8和只读审计独立额度，旧失败/时间/67入口不返。"),
        (1027, "DocuN/evidence/TASK-107/orchestration-setup-20261008/window-assignment.json", "原104独立A+窗口待人工转交，原106停止，新使用与实际发送接收开始0。"),
        (1028, "DocuN/results/TASK-107-work-decision.md", "有限合成API/原生取证授权与独立边界登记，不签结果或DEF关闭。"),
        (1029, "DocuN/evidence/TASK-107/orchestration-setup-20261008/delivery-proof.json", "正式卡/七节/版本CHG/当前363冻结/报告与共享历史读回核，主控产品运行0。")]
    change_text = "\n\n" + "\n\n".join(f"- CHG-{number:04d}，{NOW}，Codex编排Agent，{rel}。{meaning}" for number, rel, meaning in entries) + "\n"
    # 交付核证是本次最后的证据；失败会留占号断点，不能重复运行覆盖。
    proof = {"at": NOW, "TASK": "TASK-107", "R": "R-101", "card": identity(CARD),
             "seven_sections": headings, "state": "待转交", "not_sent_received_started": True,
             "source_objects_still_frozen": len(current), "report_106_unchanged": sha(REPORT.read_bytes()) == receipt["report_sha256"],
             "shared_history_exact": {"state": state_path.read_bytes().endswith(state_before),
                                      "architecture": arch_path.read_bytes().endswith(arch_before),
                                      "work106": work_path.read_bytes().endswith(work_before)},
             "next_CHG": 1030, "current_versions": {"state": "v2.21", "architecture": "v0.99"},
             "main_product_writes_tests_build_SQL_starts": 0}
    assert all(proof["shared_history_exact"].values()) and proof["report_106_unchanged"]
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    write("delivery-proof.json", proof)
    assert all((ROOT / rel).exists() for _, rel, _ in entries)
    change_path.write_bytes(change_before + change_text.encode("utf-8"))
    assert change_path.read_bytes().startswith(change_before)
    print(json.dumps({"card": str(CARD), "card_bytes": len(draft), "source_objects": len(current),
          "production_paths": len(production), "new_state": "v2.21", "new_architecture": "v0.99",
          "changes": "CHG1018—1029", "next_CHG": 1030, "dispatch": "待转交", "execution": 0,
          "history_and_report_kept": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
