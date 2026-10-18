"""登记G10有限关闭和108只读完整HTML合同；保留所有旧记录。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-107"
RECEIPT = BASE / "orchestration-receipt-01"
NEW = ROOT / "DocuN/evidence/TASK-108/orchestration-setup-20261008"
CARD = ROOT / "DocuN/tasks/TASK-108.md"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def identity(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": sha(data)}


def write(name, obj):
    path = NEW / name
    assert not path.exists(), "断点先核现存文件，不覆盖或复位登记"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    receipt = load(RECEIPT / "receipt.json")
    source = load(RECEIPT / "current-baseline.json")
    assert receipt["fresh_resources_stopped"] and receipt["all_relevant_ports_free"]
    assert not CARD.exists() and not NEW.exists() and not (ROOT / "DocuN/results/TASK-108-result.md").exists()
    for rel, expected in source.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    report107 = ROOT / "DocuN/results/TASK-107-result.md"
    report106 = ROOT / "DocuN/results/TASK-106-result.md"
    assert sha(report107.read_bytes()) == receipt["report_sha256"]
    report106_before = identity(report106)
    state_path = ROOT / "DocuS/执行动态文档.MD"
    arch_path = ROOT / "DocuS/架构动态文档.MD"
    change_path = ROOT / "DocuS/文档变更记录.MD"
    state_before = state_path.read_bytes()
    arch_before = arch_path.read_bytes()
    change_before = change_path.read_bytes()
    assert "文档 v2.21".encode("utf-8") in state_before[:500]
    assert "文档 v0.99".encode("utf-8") in arch_before[:500]
    assert b"CHG-1029" in change_before and b"CHG-1030" not in change_before
    draft = (RECEIPT / "proposed-task108-card.md").read_bytes()
    text = draft.decode("utf-8")
    headings = ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源",
                "验证、证据与审计关系", "停止与回传", "必要人工与待同步信息"]
    assert all("## " + h in text for h in headings) and "*" not in text and "|" not in text
    rules = load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
    for rule in rules:
        assert sha(Path(rule["absolute_path"]).read_bytes()) == rule["sha256"]
    NEW.mkdir(parents=True)
    # 先占号再保存正式卡，任何断点都能由唯一状态恢复。
    reservation = (f"# 执行动态文档\n\n文档 v2.22，2026-10-08，Asia/Shanghai。{NOW}已占TASK108/R102，"
                   "G11交互HTML完整合同登记中，未转交未执行。106/107与批准G10有限切片已依据107独立原件验收关闭；"
                   "B-01保持开放，旧许可封闭。\n\n## 以下为v2.21及更早历史\n\n")
    state_path.write_bytes(reservation.encode("utf-8") + state_before)
    CARD.write_bytes(draft)
    assert CARD.read_bytes() == draft
    observations = load(RECEIPT / "observations-retained.json")
    resources = load(RECEIPT / "resource-readonly.json")
    historic = ROOT / "DocuN/archives/legacy-roots-20261005/Ndocu"
    dependency_inputs = [ROOT / "AGENTS.md", ROOT / "DocuS/最终需求文档.MD",
                         historic / "results/TASK-044-result.md", historic / "tasks/TASK-044.md",
                         ROOT / "DocuN/results/TASK-105-result.md", ROOT / "DocuN/results/TASK-105-work-decision.md",
                         report107, ROOT / "backend/pyproject.toml", ROOT / "frontend/package.json",
                         ROOT / "frontend/package-lock.json"]
    dependencies = [identity(p) for p in dependency_inputs if p.exists()]
    write("design-input.json", {"at": NOW, "TASK": "TASK-108", "R": "R-102", "parent": "已关闭G10/TASK106/107",
          "contract_inputs": dependencies, "current_files": source, "current_objects": len(source), "locked_rules": rules,
          "independent_result": identity(report107), "ordinary_reception": identity(RECEIPT / "receipt.json"),
          "retained_observations": observations, "fresh_resources": resources,
          "HTML_currently_absent": {"backend/app/preview": not (ROOT / "backend/app/preview").exists(),
                                    "frontend/src/explanations": not (ROOT / "frontend/src/explanations").exists()},
          "historical_SPIKE_path": "D:/shuice12/RetroLume-SPIKE-017",
          "historical_SPIKE_accessible": Path(r"D:\shuice12\RetroLume-SPIKE-017").exists(),
          "archived_044": str(historic / "results/TASK-044-result.md"),
          "B01": "开放：旧候选Review不是固定产品宿主动态证明，创建后暂停不能代创建前拒绝",
          "old_artifacts_missing_is_not_new_whole_suite_permission": True,
          "new_product_or_running_authorization": False, "next_implementation_only_after_contract_and_necessary_adoption": True})
    limits = {"permit": "TASK-108-G11-DESIGN-20261008", "seconds": {"active": 14400, "metadata": 7200},
              "official_primary_pages": 6, "used_at_dispatch": 0,
              "all_product_execution_compile_test_build_SQL_HTTP_browser_model_Docker_start_pull_install_Git": 0,
              "allowed_writes": ["DocuN/results/TASK-108-result.md", "DocuN/evidence/TASK-108/design/"],
              "allowed_readonly_metadata": "有限文件/函数/包声明与精确必要镜像inspect，不输出Env",
              "old_real_roots": 70, "old_all_permits_closed": True, "old_accounting": receipt["accounting"],
              "old_failures_unknown_time_and_money_not_reset": True,
              "document_consistency_checks": 1, "no_test_to_deliver_plan": True}
    write("readonly-limits.json", limits)
    write("window-assignment.json", {"TASK": "TASK-108", "R": "R-102", "at": NOW, "resource": "A+增强方案执行",
          "preferred_window": "原实际TASK106业务窗口", "fallback": "原窗口不可用或容量不足时新A+方案窗口",
          "independent_107_window": "验收结束保持独立，不参与设计/实现", "delegation": "人工转卡",
          "status": "待转交", "sent": False, "received": False, "started": False, "new_execution_used": 0})
    closure106 = f"""# TASK-106 / R-100 G10有限验收关闭

{NOW}，Codex编排Agent。用户带回TASK107独立结果后，实际读取17418字节/f49a17d3053dc66b265c0c18e9596ff1bdc8ae4b8a0cbdabdab7b3505fcae028，核当前363对象、373独立身份、833原始引用SHA、B1/B2/B3五方法/五native及停止证据；未重跑产品。

按批准G10-P的合成文字面试有限边界，验收通过并关闭TASK106/R100、TASK107/R101和本G10切片；DEF024/025/026及E106-SEM有限关闭。历史答案v2/真实新反馈、accepted原键与真实COMMIT丢回包的只读恢复、同activity的WebLock/digest/hash迟到窗口成立，旧取消/正文/事务/权限等未改有效原件继承。剩余不再是一张浏览器补验卡。

107 R01/R02/R03根FAIL保持：分页等待、空答按钮等待为夹具错误，R03五方法PASS/driver0与根收尾conhost退出竞态FAIL分层；补出生身份停止已核，精确三CID停止/五端口释放。原70根不是70次成功；SUP/transport5、root/start/API/browser-driver3/3、离线3/3、口令2/2、主动交付14515.5、metadata10000保守分割未知/real127.407/offline0.641/cleanup18.452及重叠口径保留，旧余额不复活。

O107-01无序多源公开bind_scope可能后续拒绝、O107-02同activity旧错误提示仍为P2/B级非阻断观察，保存条件和未测试边界，不冒所有API排列/迟到错误投影通过；不为了它们重开整个G10或在设计卡顺手修旧域。真实provider质量/用户数据/完整Must/M-1/项目/发布不在本验收。

原106/107所有许可结束，源码/原结果/历史预算及未知完整保留。下一TASK108/R102沿已批准HTML STEP015/016只读设计，一份完整宿主+生成+学习接线合同；B-01开放，尚无HTML产品运行，必要具体采用包待真实合同后裁定。原始需求/公共库/用户配置只读，本次主控产品/SQL/build/业务运行0。

## 以下为106初轮及续作01原裁定历史

"""
    work106 = ROOT / "DocuN/results/TASK-106-work-decision.md"
    before106 = work106.read_bytes()
    work106.write_bytes(closure106.encode("utf-8") + before106)
    closure107 = f"""# TASK-107 / R-101 有限独立验收采纳与关闭

{NOW}，Codex编排Agent。独立报告、373身份/833原始引用、当前363源码、五UI方法、五真实native与最终精确资源普通核证成立。采纳代码/必要证据/执行控制的有限通过，关闭107及父106批准G10切片，DEF024/025/026/E106-SEM有限关闭；不要求重复审计或运行已过后端。

原三根FAIL保持，R03方法PASS与收尾异常补证分层，conhost原出生身份已退出、三CIDStopped/Pid0/五端口无监听。独立性原101/104窗口和意外第7/9行候选摘要暴露如实披露，判断由原目标/源/原件形成，不因该受限接触重审。O107-01/02为非阻断观察保留，不代表全部公开API排列或错误投影已验证。

107许可关闭，70累计根及全部FAIL/UNKNOWN/精确/保守账不返；source/dist/报告零改。后续109相关HTML最终独立审计只是未来计划，不能借本审计验收HTML、真实provider/M-1/整个项目。用户本次无需再批G10或运行命令，下一已授权工作为108完整HTML只读合同。

## 以下为107原调度与取证授权历史

"""
    work107 = ROOT / "DocuN/results/TASK-107-work-decision.md"
    before107 = work107.read_bytes()
    work107.write_bytes(closure107.encode("utf-8") + before107)
    work108 = ROOT / "DocuN/results/TASK-108-work-decision.md"
    assert not work108.exists()
    work108.write_text(f"""# TASK-108 / R-102 G11只读合同授权登记

{NOW}，Codex编排Agent。G10有限验收关闭后，按原已批准FR009/SEC003和连续开发目标进入STEP015/016。只读一次交付A—D完整宿主/生成/持久/画面交互/学习回流/停止协议及未来最小真实验证、必要合并采用包，不执行HTML或源/SQL修改。

新许可TASK-108-G11-DESIGN-20261008：active14400、metadata7200秒、最多6页直接必要官方一手资料；所有产品compile/test/build/PG/SQL/HTTP/app/browser/model/container-start/pull/install/Git0。允许有限metadata与指定结果/证据写入，原70根/失败/费用/未知不清零。

沿原106业务A+窗口，新实际使用0，完整卡已保存回读、待人工转交，无实际接收/开始。原107独立窗口不做方案。B-01保持开放；旧044候选有限Review保留，外部SPIKE017原件当前不可达，不假造恢复或重跑旧套件，正式产品将按合同本地重写。

当前G11-P仅未来可能采用包，实际源和所需主要模型/公开接口/依赖/权限变化由108明确后才核证必要决定；不重问已批准需求，不用本登记扩安装/用户库/provider/付费/外发/删除/Git权限。最终共享状态与结果裁定仍编排维护。
""", encoding="utf-8")
    arch = f"""# 架构动态文档

文档 v1.00，2026-10-08，Asia/Shanghai。需求v1.1、唯一执行动态v2.22。批准G10合成文字面试有限切片已独立终审并编排验收关闭，HTML STEP015/016进入完整合同；B-01开放。下面v0.99及历史原字节保留。

## G10有限闭环与G11下一合同

106/107实际28生产影响范围和当前363字节未变，原011/领域carrier/007原子提交/九动作/六路由/版本修正/原键与四账恢复/工作区已按批准范围交付。107独立源、证据与执行控制有限通过，主控373身份/833原始引用和五UI/五native及停止普通核证成立，关闭DEF024/025/026/E106-SEM；T/H原句是有限合成支持，不是通用provider质量证明。

O107-01的公开无序bind_scope可能产生权威hash顺序差异、O107-02旧错误可能显示到同activity新view保留为P2/B级非阻断观察；UI排序和发送/notice/草稿守卫的已验方法保持，不宣整个字段/API排列穷尽。旧UNKNOWN/不重发/不退款/单机/Job权威、原失败和R03补停止分层不改。

下一G11合并MOD009/FLOW006/DATA008/API007/FILE010的独立受限HTML宿主和学习接线设计。生成HTML不在主应用浏览器执行，已采用独立Docker画面/有限输入/外部可信停止和页面无业务工具权边界保持。044仅支持容器内trusted wrapper/sandbox子frame候选，固定产品动态与B-01创建前拒绝未过；旧SPIKE017源/两HTML原件当前不可访问，不伪造复用或变许可。

108只读收敛唯一A—D合同、最小依赖与可能G11-P，不实施或运行；参数/协议/持久/资格/恢复/时间账/可访问性和未来真实正反例都需完整。新主要模型/公开接口/依赖/容器权限变化须有具体采用依据。HTML/完整向量/provider、数据退出、Compose/Linux/Nginx、自用验收与完整Must/M-1/项目仍后续；不以G10关闭提前签任何HTML安全结论。

## 以下为v0.99及更早历史

"""
    arch_path.write_bytes(arch.encode("utf-8") + arch_before)
    state = f"""# 执行动态文档

文档 v2.22，2026-10-08，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.00、task_model/阶段07。下面v2.21及全部历史原字节保留。

## G10有限验收关闭；108完整HTML合同待转交

107/R101已实际返回。报告17418字节/f49a17d3…与delivery一致，363当前文件及373独立身份匹配，833原始引用SHA核证；B1历史v2与新原生反馈、B2真实accepted原键明确提交/COMMIT回包丢失后GET恢复、B3两个完成窗口与hash身份代表共五方法通过，原五native均树零/收尾完整。三精确CID均Stopped/Pid0、18106/18107/55446—55448无监听，主控产品/SQL/测试/build/资源启动0。

依据原批准G10-P、独立源/证据/控制与普通回收原件，验收关闭TASK106/R100、TASK107/R101及G10有限切片，DEF024/025/026与E106-SEM有限关闭。STEP014更新为本批准合成文字面试闭环已实现/有限验收，原历史未开始或未齐状态不覆盖当前事实。真实provider质量/开放样本/完整Must/M-1/发布/项目仍未通过，不从合成支持外推通用语义证明。

独立性沿原101/104未参与105/106窗口，读state头意外候选摘要的受限披露保留，不作为通过答案。完整28生产差异/原子与权限/source支持/异步及旧未改范围已审；不再出G10末验/重审卡。O107-01无序多源公开bind_scope潜在拒绝和O107-02同activity旧错误提示继续非阻断观察，有条件/未测边界保留；原UI排序及B1—3范围不被扩大。

原107三根全部FAIL不改：R01分页等待、R02空答按钮等待是夹具失误，R03五方法/driver0 PASS而conhost退出竞争造成根收尾FAIL；准确出生身份补停止和三CID/五端口已核，不能把原FAIL刷绿。新root/start/API/browser-driver/离线批各3/3、SUP与最低transport各5/8、口令2/2，无产品build/compile/test/迁移/新资源。active交付14515.5/21600、metadata10000/10800保守未知拆分、real127.407、offline0.641、cleanup18.452及与real重叠说明保持，所有旧余额结束。

累计旧45+106初16+C01六+107三=70真实入口不是70次成功，全部FAIL/UNKNOWN/已COMMIT/no-op/源样本与13元旧费用不重置。106原检查点与交付计时、metadata保守、旧R20/recoveryfalse等保持，不借结束runner和容器可读恢复其执行权。

按原批准Must路线转STEP015/016交互HTML，当前产品无preview/explanations，B-01仍开放。MOD009/FLOW006独立非root受监督Docker画面/有限输入、禁网/宿主文件/系统/模型工具与主页面不执行原HTML边界不降低。044候选仅只读Review，旧D:/shuice12/RetroLume-SPIKE-017/task-036和两代表HTML当前不可达，项目归档无原件；保留历史hash和不等同限制，不要求恢复外部实验、不重跑旧四容器套件。

TASK108/R102已占号并保存完整七节A—D只读方案卡，G11合并宿主/B-01、生成/持久/资格、受限输入/画面、学习回流/配置/资源停止与未来最小真实验收。接收A+原106业务窗口优先，不可续或容量不足才新A+方案窗；原107保持独立。待人工转交，新使用0，无实际发送/接收/开始。新许可TASK-108-G11-DESIGN-20261008 active14400/metadata7200秒、官方最多6页；所有产品/compile/test/build/SQL/HTTP/browser/模型/安装/Docker启动pull/Git0。

只读设计按已批准方向自主完成，必要新主要模型/公开接口/依赖/权限由真实合同提出唯一G11-P再裁定，不提前实施或重复审批旧FR009。未来实现TASK109/R103仅计划未占/未出/未发；稳定完整HTML后一次相关独立安全审计，不用普通文稿前置测试阻塞设计。当前产品/正式状态维护不依赖公共库或外部SPIKE源码。

G9/G8和此前有限验收不重开，O01—03/原未知及预算/归档/规则/原始需求不变。STEP017数据退出/备份恢复、018完整整链与Compose/Linux/Nginx边界、019权限预算一致性独立验收、020本人自用交接仍按原Must；HTML、完整向量、真实provider及其他不足仍要相关验收，不宣项目完成。Git仅已授权首提交，不新commit/push。

本批CHG1030—1042，下一CHG1043。必要人工仅把108完整卡转原106业务A+窗口并带回108结果路径；G10已关闭，不再转原审计补验卡。

## 以下为v2.21及更早历史

"""
    state_path.write_bytes(state.encode("utf-8") + state_before)
    entries = [
        (1030, "DocuN/evidence/TASK-107/orchestration-receipt-01/receive.py", "纯元数据/精确资源普通回收，不重跑或接管产品。"),
        (1031, "DocuN/evidence/TASK-107/orchestration-receipt-01/receipt.json", "17418报告/363源/373身份/833原始引用/五方法五native与三CID停止核证，三原FAIL不改写。"),
        (1032, "DocuN/evidence/TASK-107/orchestration-receipt-01/observations-retained.json", "保留O107-01/02-P2/B级条件与未验证范围，非阻断，未扩签全部公开API或错误投影。"),
        (1033, "DocuN/results/TASK-106-work-decision.md", "置顶按独立原件关闭106/107和G10有限切片/DEF024—026/E106-SEM，旧预算/报告原字节不改。"),
        (1034, "DocuN/results/TASK-107-work-decision.md", "采纳三轴有限验收、五UI补证及准确补停止，原三根FAIL和受限独立披露保留。"),
        (1035, "DocuS/架构动态文档.MD", "v1.00同步G10有限闭环与观察，转G11独立HTML候选，B-01保持开放。"),
        (1036, "DocuS/执行动态文档.MD", "v2.22关闭106/107及有限STEP014，70根非成功数，先占108/R102再保存待转交。"),
        (1037, "DocuN/tasks/TASK-108.md", "完整七节STEP015/016合并只读A—D合同，原106A+窗口，零产品运行/一次文档核对。"),
        (1038, "DocuN/evidence/TASK-108/orchestration-setup-20261008/design-input.json", "当前363/批准需求/044归档/规则与资源、旧外部SPIKE不可达和B-01边界实际基线。"),
        (1039, "DocuN/evidence/TASK-108/orchestration-setup-20261008/readonly-limits.json", "14400/7200纯设计许可与官方6页上限，原70/失败未知不返，未来运行尚未授权。"),
        (1040, "DocuN/evidence/TASK-108/orchestration-setup-20261008/window-assignment.json", "原106业务A+优先待人工转交，原107保持独立，新使用与实际派发开始0。"),
        (1041, "DocuN/results/TASK-108-work-decision.md", "G11只读完整合同获准，具体新采用包待真实合同核证，不扩用户库/页面权限/安装/费用。"),
        (1042, "DocuN/evidence/TASK-108/orchestration-setup-20261008/delivery-proof.json", "七节完整回读/版本CHG/当前363与旧报告不变/共享历史字节保持，主控运行0。")]
    proof = {"at": NOW, "card": identity(CARD), "seven_sections": headings,
             "source_scope": len(source), "TASK106_closed": True, "TASK107_closed": True, "G10_limited_closed": True,
             "DEF024_025_026_E106SEM_limited_closed": True, "O107_01_02_retained": True,
             "B01_still_open": True, "STEP015_016_dynamic_not_run": True, "no_project_M1_or_provider_pass": True,
             "shared_history_exact": {"state": state_path.read_bytes().endswith(state_before),
                 "architecture": arch_path.read_bytes().endswith(arch_before),
                 "work106": work106.read_bytes().endswith(before106), "work107": work107.read_bytes().endswith(before107)},
             "report106": report106_before, "report107": identity(report107),
             "dispatch": "待转交", "not_sent_received_started": True, "new_used": 0,
             "current_versions": {"state": "v2.22", "architecture": "v1.00"}, "CHG": "1030—1042", "next_CHG": 1043,
             "main_product_writes_tests_build_SQL_starts": 0}
    assert all(proof["shared_history_exact"].values())
    assert identity(report106) == report106_before
    assert identity(report107)["sha256"] == receipt["report_sha256"]
    for rel, expected in source.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    write("delivery-proof.json", proof)
    assert all((ROOT / rel).exists() for _, rel, _ in entries)
    lines = "\n\n" + "\n\n".join(f"- CHG-{n:04d}，{NOW}，Codex编排Agent，{rel}。{desc}" for n, rel, desc in entries) + "\n"
    change_path.write_bytes(change_before + lines.encode("utf-8"))
    assert change_path.read_bytes().startswith(change_before)
    print(json.dumps({"closed": ["TASK106/R100", "TASK107/R101", "G10有限切片", "DEF024/025/026/E106-SEM有限范围"],
          "new_card": str(CARD), "card_bytes": len(draft), "source_frozen": len(source),
          "state": "v2.22", "architecture": "v1.00", "CHG": "1030—1042", "next_CHG": 1043,
          "dispatch": "待转交", "product_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
