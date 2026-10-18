"""登记109部分回收与有限一次诊断续作，保留旧次数与原总截止。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import time

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-109"
RECEIPT = BASE / "orchestration-receipt-01"
OUT = BASE / "orchestration-continuation-01-20261009"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    path = OUT / name
    assert not path.exists(), "先核已存在断点，不重复覆盖"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    receipt = load(RECEIPT / "receipt.json")
    current = load(RECEIPT / "current-baseline.json")
    old_session = receipt["session"]
    assert not OUT.exists() and len(current) == 491
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report_path = ROOT / "DocuN/results/TASK-109-result.md"
    assert sha(report_path.read_bytes()) == receipt["report_sha256"]
    state_path = ROOT / "DocuS/执行动态文档.MD"
    arch_path = ROOT / "DocuS/架构动态文档.MD"
    change_path = ROOT / "DocuS/文档变更记录.MD"
    card_path = ROOT / "DocuN/tasks/TASK-109.md"
    work_path = ROOT / "DocuN/results/TASK-109-work-decision.md"
    old_state, old_arch, old_change, old_card, old_work = [p.read_bytes() for p in [state_path, arch_path, change_path, card_path, work_path]]
    assert "文档 v2.24".encode("utf-8") in old_state[:500] and "文档 v1.02".encode("utf-8") in old_arch[:500]
    assert b"CHG-1061" in old_change and b"CHG-1062" not in old_change
    draft = (RECEIPT / "proposed-continuation-01.md").read_bytes()
    text = draft.decode("utf-8")
    sections = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
                "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    assert all("## " + s in text for s in sections) and "*" not in text and "|" not in text
    assert str(old_session["deadline_ns"]) in text
    OUT.mkdir(parents=True)
    budget = {"permit": "TASK-109-G11-C01-20261009", "kind": "同边界原任务限额修订，只一次离线构建+真实最小诊断",
              "old_global_roots": 72, "old_TASK109_roots": 2, "old_H0_roots_failed": 2, "old_builds_failed": 1,
              "new_root_limit": 1, "new_image_save_limit": 1, "new_image_build_limit": 1,
              "new_preview_create_start_limit": 1, "new_controller_limit": 1,
              "seconds": {"active_subwindow": 3600, "metadata": 600, "real_root": 1200, "offline": 60, "cleanup": 300,
                          "preview_runtime": 60, "preview_diagnostic": 15, "build": 600},
              "original_start_ns": old_session["start_ns"], "original_deadline_ns": old_session["deadline_ns"],
              "original_deadline_not_extended": True,
              "remaining_original_total_seconds_at_registration": max(0, (old_session["deadline_ns"] - time.monotonic_ns()) / 1e9),
              "cumulative_TASK109_root_cap": 8, "cumulative_build_cap": 2, "cumulative_preview_cap": 16,
              "cumulative_H0_roots_cap_after_amendment": 3,
              "official_research_new": 0, "old_official_pages_used": 4, "old_metadata_active_each_upper": 2700.7,
              "old_real_root_including_build": 27.219, "old_build_seconds": 24.579, "old_syntax_seconds": 0.344,
              "overlap_not_added_unknown_not_refunded": True,
              "zero_new": ["PG", "volume", "SQL", "API", "frontend_build", "main_browser", "native_SUP_model", "business_wiring", "provider_fee", "new_engine_install", "Git"],
              "if_old_deadline_passed": "只完成不受阻文件准备，禁止实际运行，不复写原deadline",
              "after_any_runtime_fail_or_first_counterexample": "收尾并交回，不开第二根/第二build/第二preview",
              "new_used": 0}
    save("verification-budget.json", budget)
    tech = load(RECEIPT / "technical-review.json")
    resources = load(RECEIPT / "resource-readonly.json")
    save("continuation-input.json", {"at": NOW, "TASK": "TASK-109", "R": "R-103", "round": "续作01",
         "current_files": current, "scope": len(current), "old_protected": 363, "new_109": 128,
         "source_manifest": str(BASE / "execution/final-source-manifest.json"),
         "report_before": {"path": str(report_path), "bytes": receipt["report_bytes"], "sha256": receipt["report_sha256"]},
         "old_session_immutable": str(BASE / "execution/session.json"), "old_raw_identity": str(RECEIPT / "evidence-identities.json"),
         "builder_facts": resources, "primary_refs": tech["primary_sources"], "builder_network_attempt": "R02 registry解析尝试及失败保留",
         "current_program": "反例诊断器，未实现生产NavigationGate；NOT_FULL_H0不准进入业务",
         "full_business_phase_allowed_this_round": False, "budget": budget})
    save("window-assignment.json", {"at": NOW, "TASK": "TASK-109", "R": "R-103", "round": "续作01", "resource": "A+增强执行",
         "window": "原实际109业务窗口", "independent_107": "不实施、不泛审未实现业务",
         "dispatch": "待转交", "sent": False, "received": False, "started": False, "new_used": 0})
    work = f"""# TASK-109 / R-103 部分回收与一次最小诊断续作

{NOW}，Codex编排Agent。真实返回15176字节/76b6a8ee…；原363保护对象未改，阶段一128源/fixture/白名单副本一致，当前491文件身份核证。两根FAIL各为2秒metadata超时、裸FROM被当docker.io仓库，build24.579/两根27.219秒；没有preview/Node/Browser/PG/API/model，不能说H0安全失败或成功。

普通接受已保存准备源、真实失败和停止，不验收G11。metadata8秒已在R02有前置原件，correct repo digest仅改source未build。networknone仅RUN，不是FROM离线保证；R02外部token解析尝试和失败偏差保留，不宣0网络。当前host/counter只是诊断器，即使无反证也NOT_FULL_H0，不能靠调返回值解冻四表/业务。

新限定续作01沿原109/R103窗口，唯一一次本地OCI基础命名上下文构建和最小真实证伪；不改Docker store/daemon/builder、不切legacy、不新增原生引擎，不因正确digest仍未知而再盲试registry引用。官方依据已由主控有限核证并给引用，本机Windows路径/实际构建仍未验证。只读确认desktop-linux/docker、v0.32.2/containerd，主控unsupported inspect format元数据错误如实保留，无运行效果。

补充许可TASK-109-G11-C01-20261009明确新增一个H0根H0-R03/累计第73入口、一个save/一个build/一个preview/controller；计原总root8/build2/preview16，H0累计上限由2修订到3，旧两FAIL不返。新active子窗3600/metadata600/realroot1200/offline60/cleanup300、preview60/诊断15/build600，原start774301594189000和deadline795901594189000不延后；若已过旧总截止禁止运行，仅保存不受阻准备。新阶段官方0，不借旧4页/1535.6研究余额。

本轮全部四表/PG/profile/API/frontend/model及完整业务继续冻结；任何build/加载失败、首个真实权限反证或unknown停止即收尾，不开第二根、换方式或重复套件。当前无同步守卫，不安排110审未实现成果。诊断后若需新原生组件/改主要方案，给精确差异另裁，G11-P原采用仍有效但不含新增引擎/权限。

旧72入口/所有FAIL/UNKNOWN/13元及active/metadata2700.7重叠保守/前置1535.6/语法0.344/source末修未复验保持。当前只读枚举本卡资源为空、18109/55449无监听；原cleanup未知不改写成物理停止测试。本轮新结果置顶保15176旧原文，原源/证据/许可旧session只读，新账独立但累计原总额。卡保存回读待转交，未实际接收/开始，新实际使用0。

## 以下为109原完整授权历史

"""
    work_path.write_bytes(work.encode("utf-8") + old_work)
    arch = f"""# 架构动态文档

文档 v1.03，2026-10-09，Asia/Shanghai。需求v1.1、唯一执行动态v2.25。109停在H0准备，两根未到browser；最小诊断续作待转交，G11业务未实现，B-01开放。下面v1.02及历史原字节保留。

## H0准备事实与诊断范围

原363未变，新128阶段一源/fixture/构建副本保存。新监督/救援与受限host是准备原型，无生产NavigationGate或放行票据；两根失败是metadata期限和基础FROM解析，不是浏览器权限反证。正确repo digest源改未建，Builder networknone不保证FROM解析不联网，真实token尝试保留。

已核本机Docker29.7.2/docker builder/BuildKit0.32.2/containerd，当前无本卡容器。一次补充续作选本地OCI内容的命名build-context，精确config/层/manifest绑定缓存，不切store/daemon/旧builder；方法有Docker官方来源，实际Windows输入/构建/加载和安全仍not_run。源码修正和声明值不能关闭B-01。

本轮只读准备加一次真正最小证伪/精确停止，四表/SQL/profile/model/API/UI继续冻结，NOT_FULL_H0不进入业务；任何反证或环境不足如实留证停止，不按每个新页/导航分别开容器。G11-P采用和先关口序不变，不扩原生新引擎、页面权或旧停止/四账主权。完整宿主后再集中独立审计，当前110未派，不重审未变G10。

## 以下为v1.02及更早历史

"""
    arch_path.write_bytes(arch.encode("utf-8") + old_arch)
    state = f"""# 执行动态文档

文档 v2.25，2026-10-09，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.03、task_model/阶段07。下面v2.24及全部历史原字节保留。

## 109准备两根FAIL已回收；同卡一次最小真实诊断

109/R103已实际部分返回，15176字节/76b6a8ee…与delivery/session一致；原363/新增128现491对象身份吻合、规则未改。root01 metadata2秒超时，8秒前置修正R02通过；root02错误裸FROM触发docker.io token解析失败，整根25.062/build24.579秒。两根合27.219，未产生派生image/CID/preview/controller/browser/PG/SQL/API/model，未验证关口更未接线，不能误记安全策略被真实反证。

原报告/两原FAIL/as-run/源末修/外部解析尝试及cleanup未知保持。后改repo digest源仍未build，不据pullfalse/networknone宣整个构建离线；Docker官方说明network为RUN范围。host/counter明确是反例诊断，没有生产NavigationGate，最小无反证也是NOT_FULL_H0。本卡候选完整尚未成立，G11/B01/SEC003/STEP015016/M-1/项目未过。

普通接受准备/失败/停止，所有原业务仍冻结。主控只核源/原件、Docker版本/实际builder/containerd及两端口/本卡零容器，未执行build/create/start/产品测试/SQL。补同TASK109/R103续作01至原A+窗口，以一次本地OCI命名基础输入构建和最小可信手势/导航证伪取得能决定路线的原件，不再派笼统完整实现/泛审卡。

新action许可TASK-109-G11-C01-20261009：新增真实根1、image save1/build1、preview create/start1/controller1，所有失败前计。计原总root8/build2/preview16，H0子上限2→3，原root2/2与build1失败不返；原72加实际本轮才为73，当前新增实际0。首读子窗≤3600/metadata600/rootreal1200/offline60/cleanup300，build600/preview60/诊断15；原start774301594189000/deadline795901594189000保持不可延后，原截止已过则不运行。官方新额度0，旧4页/1535.6研究与1535.6以后的记录时段分开不重置。

本轮源/运行仅stage一构建与真实诊断，完整业务PG/四表/profile/API/frontend/native模型/provider费0。本地OCI完整config/层/hash与缓存ID验证、本机URI明确且无registry来源才build；不切legacy/store/daemon，不新增builder，不fallback联网或额外引擎。源码同链控制8秒metadata/15秒create等有界修正和2秒真实动作观测一并准备，原scope权限不松；根失败/首反证即精确收尾，第二根/build/preview0。

原109scope/root许可已在stage限额停止，本次只是已采用同包内的显式限额修订，不自动借余量。active与metadata2700.7保守重叠/H0研究1535.6/old70+new2=72/13元/FAIL/UNKNOWN均保留。旧106/103/100/088和用户资源不启，new OCI/cache/image/container及data保留，不rm/prune/DROP/DELETE。一次真正加载尚待执行，不签规范代运行或data跳过路由事实代整个引擎失败。

当前109续作01卡完整保存回读待人工转交，未实际发送/接收/开始；原107独立不接实现，110/R104计划未占/未出/未派。G10等有限关闭/DEF024—026/E106-SEM/O107观察/原R20/recoveryfalse/归档/规则/原始需求不变，HTML与退出/整链/Compose-Linux-Nginx/provider/全部Must和自用关口继续原约束。

本批CHG1062—1072，下一CHG1073。必要人工仅转109卡的新续作01前缀到原109A+窗口，带回同109结果路径；普通本地构建/剩余诊断无需重新批准G11-P。

## 以下为v2.24及更早历史

"""
    state_path.write_bytes(state.encode("utf-8") + old_state)
    card_path.write_bytes(draft + b"\n\n" + old_card)
    entries = [
        (1062, "DocuN/evidence/TASK-109/orchestration-receipt-01/receive.py", "纯元数据核证109准备失败/源/空资源，不代执行产品。"),
        (1063, "DocuN/evidence/TASK-109/orchestration-receipt-01/receipt.json", "15176报告/363+128/两根FAIL/无browser和业务，原32类账保持，partial接受不签H0。"),
        (1064, "DocuN/evidence/TASK-109/orchestration-receipt-01/technical-review.json", "Docker实际builder/store及官方OCI输入依据，元数据flag误用披露；网络none不保证FROM离线，diag不放业务。"),
        (1065, "DocuN/results/TASK-109-work-decision.md", "置顶同卡限定一次离线构建与真实最小诊断，旧两FAIL和原总deadline保留。"),
        (1066, "DocuS/架构动态文档.MD", "v1.03实际H0准备原型/无同步守卫/OCI候选与未知，不扩引擎或弱化标准。"),
        (1067, "DocuS/执行动态文档.MD", "v2.25登记109真实返回/72入口和有限C01新使用0，业务继续冻结/110未派。"),
        (1068, "DocuN/tasks/TASK-109.md", "置顶完整七节续作01先本地内容绑定一次build/probe，保原24876完整卡字节。"),
        (1069, "DocuN/evidence/TASK-109/orchestration-continuation-01-20261009/continuation-input.json", "491快照/原报告源/原deadline和官方引用、实际程序只diag，旧证据原件保留。"),
        (1070, "DocuN/evidence/TASK-109/orchestration-continuation-01-20261009/verification-budget.json", "明确只补一根/save/build/preview，计原总额与H0累计3，不延总期不返未知。"),
        (1071, "DocuN/evidence/TASK-109/orchestration-continuation-01-20261009/window-assignment.json", "原109A+待人工转交，共享状态唯一，原107不实施，新增实际0。"),
        (1072, "DocuN/evidence/TASK-109/orchestration-continuation-01-20261009/delivery-proof.json", "新前缀/七节/原卡与共享历史/报告/491源回读、所有main产品运行0。")]
    proof = {"at": NOW, "TASK": "TASK-109", "R": "R-103", "round": "续作01", "card_prefix_bytes": len(draft),
         "card_prefix_sha256": sha(draft), "full_card_bytes": len(card_path.read_bytes()), "full_card_sha256": sha(card_path.read_bytes()),
         "seven_sections": sections, "old_card_bytes": len(old_card), "old_card_suffix_exact": card_path.read_bytes().endswith(old_card),
         "report_unchanged": sha(report_path.read_bytes()) == receipt["report_sha256"], "current_scope_unchanged": len(current),
         "shared_history_exact": {"state": state_path.read_bytes().endswith(old_state), "architecture": arch_path.read_bytes().endswith(old_arch), "work109": work_path.read_bytes().endswith(old_work)},
         "new_used": 0, "dispatch": "待转交", "not_sent_received_started": True,
         "all_business_phase_frozen": True, "original_deadline_unchanged": True,
         "main_product_SQL_build_tests_starts": 0, "CHG": "1062—1072", "next_CHG": 1073}
    assert all(proof["shared_history_exact"].values()) and proof["old_card_suffix_exact"] and proof["report_unchanged"]
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    save("delivery-proof.json", proof)
    assert all((ROOT / rel).exists() for _, rel, _ in entries)
    change_path.write_bytes(old_change + ("\n\n" + "\n\n".join(f"- CHG-{n:04d}，{NOW}，Codex编排Agent，{rel}。{desc}" for n, rel, desc in entries) + "\n").encode("utf-8"))
    assert change_path.read_bytes().startswith(old_change)
    print(json.dumps({"card": str(card_path), "prefix_bytes": len(draft), "current_scope": len(current),
        "state": "v2.25", "architecture": "v1.03", "next_CHG": 1073, "business_phase": "冻结",
        "dispatch": "待转交", "main_runtime": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
