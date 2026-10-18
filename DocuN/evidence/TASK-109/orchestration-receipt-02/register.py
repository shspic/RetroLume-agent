"""登记C01有效构建与C02直接镜像诊断，旧根/旧截止不返额。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import time

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-109"
HERE = BASE / "orchestration-receipt-02"
OUT = BASE / "orchestration-continuation-02-20261009"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "先核断点，不覆盖新旧编排文件"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    receipt = load(HERE / "receipt.json")
    current = load(HERE / "current-baseline.json")
    assert len(current) == 493 and not OUT.exists()
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report = ROOT / "DocuN/results/TASK-109-result.md"
    assert sha(report.read_bytes()) == receipt["report_sha256"]
    state_path = ROOT / "DocuS/执行动态文档.MD"
    arch_path = ROOT / "DocuS/架构动态文档.MD"
    ledger_path = ROOT / "DocuS/文档变更记录.MD"
    card_path = ROOT / "DocuN/tasks/TASK-109.md"
    work_path = ROOT / "DocuN/results/TASK-109-work-decision.md"
    old_state, old_arch, old_ledger, old_card, old_work = [p.read_bytes() for p in [state_path, arch_path, ledger_path, card_path, work_path]]
    assert "文档 v2.25".encode("utf-8") in old_state[:500] and "文档 v1.03".encode("utf-8") in old_arch[:500]
    assert b"CHG-1072" in old_ledger and b"CHG-1073" not in old_ledger
    draft = (HERE / "proposed-continuation-02.md").read_bytes()
    text = draft.decode("utf-8")
    headings = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源", "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    assert all("## " + h in text for h in headings) and "*" not in text and "|" not in text
    assert receipt["image_manifest_id"].split(":",1)[1] in text and receipt["image_config_digest"].split(":",1)[1] in text
    OUT.mkdir(parents=True)
    for rel, data in [("DocuS/执行动态文档.MD",old_state), ("DocuS/架构动态文档.MD",old_arch), ("DocuS/文档变更记录.MD",old_ledger),
                      ("DocuN/tasks/TASK-109.md",old_card), ("DocuN/results/TASK-109-work-decision.md",old_work)]:
        p = OUT / "before" / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
    budget = {"action_permit": "TASK-109-G11-C02-20261009", "purpose": "直接复用成功镜像，只一次preview真实最小诊断",
        "old_global_roots": 73, "old_task_roots": 3, "new_root": 1, "new_preview_create": 1, "new_preview_start": 1, "new_controller": 1,
        "new_image_save_build": 0, "original_start_ns": 774301594189000, "original_deadline_ns": 795901594189000,
        "original_remaining_seconds_at_registration": max(0,(795901594189000-time.monotonic_ns())/1e9), "deadline_extension": False,
        "limits_seconds": {"active_subwindow": 1800, "metadata":300, "real_root":300, "offline":60, "cleanup":180, "preview":60, "diagnostic":15},
        "cumulative_H0_root_limit_amended":4, "cumulative_root_limit":8, "cumulative_preview_limit":16, "cumulative_controller_limit":2,
        "imagebuild_used_limit": "2/2封存不再build", "research_pages_new":0,
        "zero_new": ["PG","SQL","API","main_browser","frontend_build","profile_business","native_SUP_model","provider_fee","install_Git"],
        "old_fail_error_and_overlap_not_reset": True, "new_used":0}
    save("verification-budget.json",budget)
    save("continuation-input.json", {"at":NOW, "TASK":"TASK-109", "R":"R-103", "round":"C02", "current_files":current,
        "report_before":{"path":str(report),"bytes":receipt["report_bytes"],"sha256":receipt["report_sha256"]},
        "immutable_image":load(HERE / "image-resource-readonly.json")["image"],
        "image_config_is_not_manifest_same_digest":True,
        "build_input_binding":str(BASE / "execution/continuation-01/root-03/build-metadata.json"),
        "OCI_identity":str(BASE / "execution/continuation-01/root-03/OCI-identity.json"),
        "classification_false_positive":str(BASE / "execution/continuation-01/registry-classification.json"),
        "old_sessions_immutable":[str(BASE / "execution/session.json"),str(BASE / "execution/continuation-01/session.json")],
        "cached_image_already_built_and_loaded":True,"new_save_build_allowed":False,"business_frozen":True,
        "source_as_run":str(BASE / "execution/continuation-01/as-run-source-manifest.json"),"budget":budget})
    save("window-assignment.json", {"TASK":"TASK-109","R":"R-103","round":"C02","resource":"A+增强执行","window":"原109业务窗口",
        "dispatch":"待转交","sent":False,"received":False,"started":False,"new_used":0,"independent_107":"不实施/不泛审未齐业务"})
    work = f"""# TASK-109 / R-103 OCI构建回收与直接镜像续作02

{NOW}，Codex编排Agent。实际C01报告27219字节/692c6dce…、旧15176字节精确后缀及旧session保持。当前493对象/130 as-run源一致；R03真实root53.922秒、save30.172/build2.438成功子段，OCI客户端context/唯一material/c091实际源和loaded image aa824…/config e881…已核，image可复用。

R03原ERROR是控制字符串误判，标准化docker.io展示名不是network证据；实际metadata/material与客户端load佐证OCI来源。原根不改色不返额，接受成功构建/加载身份子事实，不接受新浏览器或H0通过。基础ID实际为manifest c091引用config fee853和七层，类型链澄清修正前卡不当字面相等要求，不假写config==manifest。

本轮明确补C02直接一次create/start/真实观测/收尾，save/build0，普通控制误判修正不问采用。新action许可TASK-109-G11-C02-20261009，原start774301594189000/deadline795901594189000不延；首读子窗1800/metadata300/rootreal300/offline60/cleanup180、preview60/诊断15。补一根R04/累计第74入口，计原总8/preview16/controller2，H0累计3→4；所有旧FAIL/ERROR和build2/2封存，官方新0。

阶段一资源仍UID10001/真sandbox/networknone/只读/capdrop/NoNewPrivileges/privateIPC/原memPIDs/无bindsocketportsecret，唯一preview01目前不存在。直接immutable image ID而不tag解析/拉取/重建/修改JS；源码只本轮必要Python控制/fixture，原image/currentJS/seccomp等冻结。错误或首反证立即停，不开第二根或换权限；即无反证也NOT_FULL_H0，PG/profile/模型/API/UI业务继续冻结。

累计真实73不是73PASS：原两根27.219与新53.922为81.141，build27.017是子段不重复加；C01 active1693.1上界/metadata600保守/cleanup30保守/offline0.297、旧2700.7重叠及1535.6研究/4页/13元/UNKNOWN保留。当前未有preview/CID/Node/browser，task容器/两端口为空，不签物理树空；主控只读核源/元数据无启动。C02待人工转交、新实际0、原107保持独立、110未派。

原report、所有原件与缓存/成功image保留，末修只代码不称已验证经验。诊断拿到关键反证后同轮允许一页最低必要方案差异，不删FR009/不暗加原生引擎或改变主要信任模型。若环境不足，准确层级交回，不泛断所有浏览器。G11-P不重问，关键新组件另裁。

## 以下为109首轮及续作01原裁定历史

"""
    work_path.write_bytes(work.encode("utf-8")+old_work)
    arch = f"""# 架构动态文档

文档 v1.04，2026-10-09，Asia/Shanghai。需求v1.1、唯一执行动态v2.26。OCI实际构建/加载子事实成立，控制误判在create前退出，浏览器/H0仍未验证；C02直接复用镜像诊断待转交，业务冻结。下面v1.03及历史原字节保留。

## 已构建镜像与下一最小诊断

基底manifest c091→config fee853/七层/rootfs顺序真实绑定，派生manifest aa824→config e881，User10001/Node entrypoint/linuxamd64/实际build context与唯一OCI material原件匹配；不能硬把manifest与config同值，也不根据docker.io标准化展示名判网络。R03 rootERROR不改，成功build身份不等Node/browser已经加载。

C02只用已加载immutable image，不save/build/install/变权限或重新执行错误guard。可信输入/新页/自身导航的最小原件及精确停止还需实际运行，一根/一preview有界。现image为无生产NavigationGate诊断器，任何环境失败或反证分层保留，即探针无反证也NOT_FULL_H0，业务仍冻结/110不泛审。

原G11采用/先关口/主应用不执行原HTML/页面无网文件系统模型工具、旧四账/Job/已验域都保持。原始失败、73计数/费用/计时与源/OCI/image历史不删不重置，未授权新引擎或主要替代方案不能实施。

## 以下为v1.03及更早历史

"""
    arch_path.write_bytes(arch.encode("utf-8")+old_arch)
    state = f"""# 执行动态文档

文档 v2.26，2026-10-09，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.04、task_model/阶段07。下面v2.25及全部历史原字节保留。

## OCI已构建，R03误判已定界；C02直接镜像运行待转交

109/R103 C01已实际返回27219字节/692c6dce…，旧15176精确历史后缀和旧session保持，当前493对象/130 as-run源匹配。C01 save0退出/30.172秒/949432320字节，OCI九blob及manifest-config-七层-rootfs顺序链验证；build exit0/2.438秒，actual image aa824fa2…/config e881d12c…已加载/User10001/Node入口/linuxamd64，成功基础输入/构建子事实普通验收可复用。

R03 rootERROR在create前因日志标准化docker.io/library/task109_cached_base被误当网络。唯一material为pkg:oci/c091，context oci-layout、日志客户端load佐证真实源；保原误报ERROR而采纳独立成功build，不改旧错误或费用。主控纠正先前config digest必须等于image ID的字面要求：本机ID是OCI manifest，严格manifest→所引用config/layers链才是事实，不虚写相等。

累计real根73不是73PASS，TASK109三根/H0修订3/3、build2/2封存；原27.219+新53.922=81.141，累计build27.017是子段不加第二次。C01 active1693.1保守/metadata600预留/cleanup30保守/offline0.297、旧2700.7重叠/研究1535.6/官方4/4/给定输入页1分项/13元及全部FAIL/UNKNOWN保持。preview/controller/Node/Browser/PG/SQL/API/model均0，无实际权限反证，不签H0/B-01/SEC003/STEP015016或项目。

已核实际immutable image可读、task容器为0/18109-55449无监听；源码只有8原阶段一差异及2新文件，旧363业务保护未改。主控没有save/build/create/start/SQL/产品测试，只读原件、config/descriptor、元数据与字节。当前诊断器无生产同步守卫，本轮绝不进入业务，也不安排110审未齐实现。

同109/R103续作02完整七节卡保存回读，原A+业务窗口待人工转交，未实际接收/开始，新使用0。新action许可TASK-109-G11-C02-20261009补一根R04/previewcreate1/start1/controller1，计原root8/preview16/controller2，H0累计3→4；save/build/PG/API/frontend/model/安装/费用/Git0。子窗1800/metadata300/rootreal300/offline60/cleanup180，preview60/诊断15；原总start774301594189000/deadline795901594189000不延，过期不运行，官方新0。

直接create用manifest aa824…且pullnever/核confige881…与源码image映射、label归属及actionC02，不再tag解析或原build关键词guard；classification只核真实材料/源/请求，不用标准化名字或文档URI替网络。不改image内JS/包/版本/seccomp/资源权限，只允许新Python控制/fixture最小提取真实run和收尾。原UID/trueSandbox/networknone/只读/capdrop/NoNewPrivileges/privateIPC/768MiBpids128/有限tmpfs无bindsocketportsecret保持。错误/首反证即收尾，第二根/image/preview0。

旧report/session/root/as-run/cache/image与全部原件只读保留，新记录独立但累计原总额。实际Node/browser启动/可信手势/loader/目标/frame与精确停止才是新取证，源语法/成功构建不可代。若关键真实反证，同轮只给一页必要方案差异和最小推荐，不降Must/暗加引擎；任何主要信任/模型变化仍需准确裁定，原G11-P不重问。

G10等有限关闭、旧O107观察/原R20/recoveryfalse/归档/规则/原始需求不改；旧106/103/100/088不启，新container停后保留不删，130源/OCI/caches也保留。HTML与退出恢复/完整provider向量/Compose-Linux-Nginx/自用和全Must/M-1/项目仍未放行，原107保持隔离/110未占未派。

本批CHG1073—1083，下一CHG1084。必要人工仅转109卡新C02前缀给原109A+，完成带回同109结果路径，无重复采用问题。

## 以下为v2.25及更早历史

"""
    state_path.write_bytes(state.encode("utf-8")+old_state)
    card_path.write_bytes(draft+b"\n\n"+old_card)
    entries = [(1073,"DocuN/evidence/TASK-109/orchestration-receipt-02/receive.py","普通核C01构建与误判/493源/镜像元数据，未启动产品。"),
        (1074,"DocuN/evidence/TASK-109/orchestration-receipt-02/receipt.json","27219报告/旧后缀/三root/成功build与false-positive分层，旧FAIL和计数保持。"),
        (1075,"DocuN/evidence/TASK-109/orchestration-receipt-02/image-resource-readonly.json","manifestaa824/confige881实际可读、UID/入口/标签、容器和端口空，只读。"),
        (1076,"DocuN/results/TASK-109-work-decision.md","置顶C02直接复用image，一根run/收尾，纠正manifest-config不当相等条件，业务冻结。"),
        (1077,"DocuS/架构动态文档.MD","v1.04实际OCI构建与标识类型/guard误判，不签新运行安全。"),
        (1078,"DocuS/执行动态文档.MD","v2.26收实际C01/73根并登记C02待转交/新0，失败和截止不重置。"),
        (1079,"DocuN/tasks/TASK-109.md","置顶七节C02直接运行现有image，不save/build/业务，保原C01和完整卡字节。"),
        (1080,"DocuN/evidence/TASK-109/orchestration-continuation-02-20261009/continuation-input.json","493对象/130src/build和实际image/config/ref/旧session、原件与程序用途冻结。"),
        (1081,"DocuN/evidence/TASK-109/orchestration-continuation-02-20261009/verification-budget.json","只补一根一preview，原总期限/额度累计不返，build2/2封存，业务0。"),
        (1082,"DocuN/evidence/TASK-109/orchestration-continuation-02-20261009/window-assignment.json","原109A+待人工转交，原107不实施，新增实际0。"),
        (1083,"DocuN/evidence/TASK-109/orchestration-continuation-02-20261009/delivery-proof.json","新前缀/七节/原卡报告和共享历史/493源一致，main产品运行0。")]
    proof = {"at":NOW,"TASK":"TASK-109","R":"R-103","round":"C02","card_prefix_bytes":len(draft),"card_prefix_sha256":sha(draft),
        "full_card_sha256":sha(card_path.read_bytes()),"seven_sections":headings,"old_card_suffix_exact":card_path.read_bytes().endswith(old_card),
        "report_unchanged":sha(report.read_bytes())==receipt["report_sha256"],"source_scope":len(current),"image_build_reused_not_run":True,
        "shared_history_exact":{"state":state_path.read_bytes().endswith(old_state),"arch":arch_path.read_bytes().endswith(old_arch),"work":work_path.read_bytes().endswith(old_work)},
        "new_used":0,"dispatch":"待转交","business_frozen":True,"original_deadline_preserved":True,
        "main_product_SQL_build_test_start":0,"CHG":"1073—1083","next_CHG":1084}
    assert all(proof["shared_history_exact"].values()) and proof["old_card_suffix_exact"] and proof["report_unchanged"]
    for rel,expected in current.items(): assert sha((ROOT/rel).read_bytes())==expected
    save("delivery-proof.json",proof)
    assert all((ROOT/rel).exists() for _,rel,_ in entries)
    ledger_path.write_bytes(old_ledger+("\n\n"+"\n\n".join(f"- CHG-{n:04d}，{NOW}，Codex编排Agent，{rel}。{desc}" for n,rel,desc in entries)+"\n").encode("utf-8"))
    assert ledger_path.read_bytes().startswith(old_ledger)
    print(json.dumps({"card":str(card_path),"prefix_bytes":len(draft),"sources":len(current),"state":"v2.26","arch":"v1.04","next_CHG":1084,
        "no_save_build_business":True,"dispatch":"待转交","main_runtime":0},ensure_ascii=False))


if __name__ == "__main__": main()
