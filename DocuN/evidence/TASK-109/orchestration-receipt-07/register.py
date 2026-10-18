"""核证最后反证、封存旧运行许可并登记只读技术方案任务。"""
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AREA = Path(__file__).resolve().parent
EXEC = ROOT / "DocuN/evidence/TASK-109/execution/continuation-05"
NEXT = ROOT / "DocuN/evidence/TASK-110/orchestration-20261010"
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def identity(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": sha(data)}


def save_json(path, value):
    path.resolve().relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not (AREA / "receipt.json").exists() and not (ROOT / "DocuN/tasks/TASK-110.md").exists()
report_path = ROOT / "DocuN/results/TASK-109-result.md"
report = report_path.read_bytes()
assert len(report) == 90881 and sha(report) == "30c63a9907925241185c3d8377fedea06da7901eed1b3d5a96409938ce207a01"
prior = (ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-06/TASK-109-C04-as-returned.md").read_bytes()
assert len(prior) == 72843 and report.endswith(prior)
baseline = read_json(ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-06/current-baseline.json")
assert len(baseline) == 497 and all(sha((ROOT / relative).read_bytes()) == expected for relative, expected in baseline.items())
new_files = {"backend/tests/fixtures/task109/navigation-tail.cjs": "fa2d405c4ee34a965554b0349ca7f690726d7ed64f9d8ddea3668cee5a9b3bc3", "backend/tests/fixtures/task109/h0-tail.py": "b331b208e91f9862306ee7ac0706e241c3cb628b2f8bf9a175f7d905b210fb43", "backend/tests/fixtures/task109/test_h0_tail_control.py": "6a736b859ed3a2cd05d11ff1e7707c0533e0fe74e39ac637d3fd4ccd28ef4f37"}
for relative, expected in new_files.items():
    assert sha((ROOT / relative).read_bytes()) == expected
    baseline[relative] = expected
index = read_json(EXEC / "evidence-file-index.json")
for row in index:
    path = Path(row["path"])
    path.resolve().relative_to(ROOT)
    raw = path.read_bytes()
    assert len(raw) == row["bytes"] and sha(raw) == row["sha256"]
nav_path = EXEC / "root-08/preview/navigation-hash-counterexample.json"
nav = read_json(nav_path)
binding = read_json(EXEC / "root-08/preview/frame-binding.json")
assert nav["id"] == "h0_hash" and nav["verdict"] == "FAIL" and nav["acknowledged"] and nav["actual_observation_seconds"] >= 2
before_doc = nav["before"]["child"]["documents"][0]
after_doc = nav["after"]["child"]["documents"][0]
assert before_doc["frameId"] == after_doc["frameId"] == binding["frameId"]
assert before_doc["url"] == "about:srcdoc" and after_doc["url"] == "about:srcdoc#H0_SAME_DOCUMENT_COMMITTED"
commit = nav["violation"]["commit"]
assert commit["name"] == "Page.navigatedWithinDocument" and commit["frameId"] == binding["frameId"] and commit["url"] == after_doc["url"]
assert nav["before"]["child"]["frameTree"]["frameTree"]["frame"]["loaderId"] == nav["after"]["child"]["frameTree"]["frameTree"]["frame"]["loaderId"]
assert before_doc["backendNodeId"] == after_doc["backendNodeId"]
assert binding["owner"]["backendNodeId"] == binding["actualOwner"]["backendNodeId"] and binding["owner"]["sandbox"] == "allow-scripts"
assert binding["childTarget"]["parentFrameId"] == binding["rootFrameId"] and binding["rootTarget"]["browserContextId"] == binding["childTarget"]["browserContextId"]
signals = nav["retained_signals"]
assert all(row["context_matches_subject"] and row["context"]["frameId"] == binding["frameId"] for row in signals)
assert any(row["data"]["kind"] == "gesture" and row["data"]["trusted"] and row["data"]["active"] for row in signals)
assert any(row["data"]["kind"] == "handler" and row["data"]["id"] == "h0_hash" for row in signals)
assert nav["engine_fault"] is None and nav["call_error"] is None and nav["capture_error"] is None
stdout = (EXEC / "root-08/preview/container-stdout.bin").read_bytes()
assert len(stdout) == 38699 and sha(stdout) == "6b1ab343a887e4e9bcbede47d80c08cdf1ff284b239c012651a018b19d3567a7"
session = read_json(EXEC / "session.json")
assert session["global_roots"] == 78 and session["task_roots"] == session["H0_roots"] == 8
assert session["cumulative_builds"] == session["cumulative_controllers"] == session["cumulative_preview_starts"] == 4
assert session["roots"][0]["state"] == "FAIL" and session["route_closed"] and not session["additional_real_root_allowed"]
assert session["new_real_seconds"] == 11.469
old_sessions = read_json(ROOT / "DocuN/evidence/TASK-109/orchestration-receipt-06/receipt.json")["old_sessions"]
assert all(sha(Path(path).read_bytes()) == expected for path, expected in old_sessions.items())
old_sessions[(EXEC / "session.json").as_posix()] = sha((EXEC / "session.json").read_bytes())
resources = []
for cid in ["5bd9e24d2a8ba06403f4daf4120aedcd7fe0ef4f0e3ae5f162b723918f189059", "0a449f648fc66020b937cdefa2f2cea4cc6ad305d42a9275cc96a76e77a4ccd0", "3215e8f81ce6ff9b465e1d4be14d7d681a6dc7fdd6058ec881cfa0862bd77392", "b5b220fcd582b8a8e2bee387f8544b1bc28f6d0281a77ba130340064a1d71a89"]:
    args = ["docker", "inspect", "--format", '{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"state":{{json .State}},"labels":{{json .Config.Labels}}}', cid]
    data = json.loads(subprocess.run(args, capture_output=True, encoding="utf-8", text=True, timeout=15, check=True).stdout)
    assert data["id"] == cid and data["labels"]["retrolume.task"] == "TASK-109" and not data["state"]["Running"] and not data["state"]["Restarting"] and data["state"]["Pid"] == 0
    resources.append(data)
rules = read_json(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
assert all(sha(Path(row["absolute_path"]).read_bytes()) == row["sha256"] for row in rules)
managed = ["DocuN/tasks/TASK-109.md", "DocuN/results/TASK-109-work-decision.md", "DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD"]
old = {relative: (ROOT / relative).read_bytes() for relative in managed}
assert "文档 v2.30" in old[managed[2]].decode("utf-8-sig").splitlines()[2] and "文档 v1.08" in old[managed[3]].decode("utf-8-sig").splitlines()[2]
assert "CHG-1118" in old[managed[4]].decode("utf-8-sig")[-1000:]
for relative, raw in old.items():
    target = AREA / "before" / relative
    target.resolve().relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
(AREA / "TASK-109-C05-as-returned.md").write_bytes(report)
save_json(AREA / "current-baseline.json", baseline)
save_json(AREA / "resources-readonly.json", {"at": STAMP, "containers": resources, "main_start": 0, "scope": "精确Stopped子事实，不签直接cgroup空"})
receipt = {"TASK": "TASK-109", "R": "R-103", "at": STAMP, "report": identity(report_path), "old72843_suffix_exact": True, "source_count": len(baseline), "new_sources": new_files, "C05_evidence_index_count": len(index), "all_index_match": True, "old_sessions": old_sessions, "finding": "真实同文档hash提交违反已采用108/109同步禁止条款", "proof": {"frameId": binding["frameId"], "rootFrameId": binding["rootFrameId"], "before_document": before_doc, "after_document": after_doc, "commit": commit, "actual_seconds": nav["actual_observation_seconds"], "raw_urlChanged_false_scope_preserved": "Frame.url裸字段不含fragment，不反驳完整document/target URL和真实提交事件"}, "scope": "不证明网络/文件/系统越权或其它导航协议；未运行的child/blob/data不补造，旧data根因仍未知", "counters": {"global_roots": 78, "task_roots": 8, "H0_roots": 8, "builds": 4, "controllers": 4, "preview": 4}, "real_seconds": 140.297, "build_seconds_subpart": 30.658, "new_active_upper_seconds": 2657.078, "new_metadata_upper_seconds": 180, "new_cleanup_upper_seconds": 20, "new_offline_seconds": 0.5006204, "old_failures_fees_and_overlaps_preserved": True, "orchestration_verdict": "TASK109已返回，H0不通过，完整交付未验收通过；反证诊断子目标完成且原运行路线封存", "all_TASK109_execution_permissions_closed": True, "main_product_runs": 0, "independent_audit": False}
save_json(AREA / "receipt.json", receipt)
input_paths = ["AGENTS.md", "DocuS/原始需求文档.MD", "DocuS/最终需求文档.MD", "DocuN/results/TASK-108-result.md", "DocuN/results/TASK-108-work-decision.md", "DocuN/tasks/TASK-109.md", "deploy/preview/host.cjs", "deploy/preview/wrapper.html", "backend/tests/fixtures/task109/navigation-tail.cjs", "backend/app/preview/contracts.py", "backend/app/preview/supervisor.py", "backend/app/preview/reaper.py"]
save_json(NEXT / "input-manifest.json", {"TASK": "TASK-110", "R": "R-104", "at": STAMP, "input_sources": [identity(ROOT / relative) for relative in input_paths if relative != "DocuN/tasks/TASK-109.md"], "raw_navigation": identity(nav_path), "frame_binding": identity(EXEC / "root-08/preview/frame-binding.json"), "raw_observations": identity(EXEC / "root-08/preview/observations.json"), "raw_stdout": identity(EXEC / "root-08/preview/container-stdout.bin"), "resource_samples": identity(EXEC / "root-08/preview/resource-observations.json"), "input_boundary": "原目标/采用决定/稳定源/原始证据；不传实现聊天或自评", "old_runtime_permits_closed": True, "raw_counterexample_is_not_a_proof_of_all_candidate_engines": True})
save_json(NEXT / "verification-budget.json", {"TASK": "TASK-110", "R": "R-104", "type": "只读技术可行性与完整方案合同", "new_time_seconds": {"active": 5400, "public_source_research": 2400, "document_check_each": 60}, "public_primary_pages_max": 8, "official_source_files_max": 4, "native_candidates_max": 2, "alternative_output_contract_max": 1, "document_checks_max": 1, "one_justified_recheck_max": 1, "real_roots": 0, "browser_or_container_start": 0, "compile_test_build": 0, "product_write": 0, "provider_fee": 0, "private_config": 0, "old_TASK109_roots": "8/8封存，不借剩余类别额", "old_global_roots": 78, "old_failures_costs_and_evidence_retained": True, "metadata_hash_scripts_only": True, "new_used": 0, "stopping": "依据足够即完成A—D，不凑资料页/候选/投入；不可虚构实现锚，关键未知写边界"})
save_json(NEXT / "window-assignment.json", {"TASK": "TASK-110", "R": "R-104", "resource": "A+增强执行，强推理", "window": "新隔离技术方案窗口，未参与109实现；不继承实现聊天", "reason": "工作从同栈运行诊断转为原生接口覆盖和输出/安全合同取舍，需要新技术上下文", "client_model": "由接收者实际登记，不虚构型号", "dispatch": "已登记，完成保存回读后待转交", "received": False, "started": False, "new_used": 0, "original109": "执行许可封存，原成果和窗口留存", "original107": "独立状态保留，不派泛审"})

closed = f'''# TASK-109 / R-103 执行许可已结束 — 诊断路线封存

{STAMP}，Codex编排Agent。C05最后根取得hash同文档提交的真实反证，H0不通过；根8/8、H0 8/8、build4/4、controller4/4与本TASK全部执行许可封存。下面所有旧卡仅历史，不授权重新运行、另开相同小批或使用名义preview余额。

原生成/持久化/模型/API/HTML业务仍冻结，TASK109完整交付未通过验收；有限反证诊断子目标已完成。原source/所有证据、失败/投入/时窗和资源保留。新TASK110/R104只读技术方案收敛待人工转交，新方案未采用、没有新引擎/权限/运行授权。

## 以下为原C05及更早完整合同历史

'''
work109 = f'''# TASK-109 / R-103 最后反证核证与原执行路线关闭

{STAMP}，Codex编排Agent。90881字节报告/30c63a99…及72843原后缀、500源与C05原件索引核证；gesture/handler ACK在准确OOPIF运行上下文成立，同一frame/document/target的完整URL由about:srcdoc变为带H0_SAME_DOCUMENT_COMMITTED fragment，Page.navigatedWithinDocument真实提交，loader与document backend未变符合同文档性质。原urlChanged:false只指裸Frame.url字段，不改原字段；原事件和完整URL交叉明确反证。并非只有导航请求、页面自述或旧data异常。

裁定H0不通过；已采用108/109强同步导航条款有P1级具体缺口。接受正确停止与反证诊断子交付，不签完整TASK109/G11/SEC003/M1/项目。child/blob/data依首反证未运行保持，不扩大推断为网络/文件/系统越权，旧data根因不追认为解决。元数据/sandbox/B01有限充分证据继承不复跑。

TASK109已返回，完整交付验收失败、原运行路线结束；全部旧许可封存，包括未使用的名义分类余额，不生成C06或第9根。累计78不是78PASS，task/H0各8/8、build4/4、controller4/4、preview4/16；real140.297含build30.658子段、C05active2657.078上界/metadata180/cleanup20/offline0.5006204及旧失败/未知/13元重叠原账保持。四精确CID当前Stopped/Pid0、原数据和image不删；namespace结束仍推断，不签直接cgroup空。

转TASK110/R104一张只读完整技术决策输入卡，由新A+窗口核具体可实现守卫覆盖、原安全条款出处与最小输出/信任合同调整，形成唯一推荐及一个待采用增量包。不预设已有可用Native组件、不默改Must，不再复现已明确hash反证。原G11-P已采用部分不取消，新主要架构/协议/权限/依赖改变仍待具体决定；主控统一裁定，110不是完整G11独立终审。以下原裁定原字节保留。

'''
state = '''# 执行动态文档

文档 v2.31，2026-10-10，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.09、task_model/逻辑07局部方案重评，05按需维护；以下v2.30及原历史保字节。

## 109真实导航反证成立，诊断路线结束；110只读技术方案待转交

109/R103 C05已返回，report90881/30c63a99…保72843原后缀，500映射source与原件索引匹配，七sessions保历史。真实2.055964316秒可信gesture/handler ACK在准确子frame，Page.navigatedWithinDocument提交hash，document和target完整URL同步变化；loader/document backend未变不能签拒绝，裸urlChanged:false的片段排除语义原样保留。H0明确不通过、已采用强导航条款为P1级缺口；TASK109完整验收失败，诊断子交付完成，原路线和全部许可封存，不再出同参数小批。

原元数据/sandbox/B01有限子事实继承，未运行child/blob/data保持，旧data origin/fork因果未知，不泛指网络/文件/系统越权。global78非78PASS、task/H08/8、build4/4、controller4/4、preview4/16；real140.297含build30.658子段，C05active2657.078/metadata180/cleanup20上界、offline0.5006204与旧费用13元/失败/UNKNOWN/重叠/时窗保留。四精确容器当前Stopped/Pid0，未签直接cgroup空，原source/image/数据不删。

新TASK110/R104已登记并保存完整七节卡，A+新隔离技术方案窗口待转交，未接收/开始。只读核原目标/采用强条款出处、至多两原生候选与一输出合同方向，逐路径查真实同步拒绝覆盖、正常交互/源码/许可/资源/维护成本，形成A—D及唯一推荐、唯一待采用包。不给空NativeNavigationGate接口当实现，不能静默允许hash、关闭Must或把特定引擎未经核源码称可用。

110新资料时间5400/研究2400秒、官方页最多8/官方源码4、一次文档检查60有据复检一次；真实root/代码/compile/test/build/Docker/浏览器/PG/模型/费用/安装/Git/删除0，不借109残余分类额。原109窗口成果保留但停止执行；原107独立，未来实现与稳定G11独立终审仍未派。原G11-P既有采用不取消，新方案未采用，生成/四表/模型/API/预览业务继续冻结，原G3—G10充分未变验收保持。

本批CHG1119—1129，下一CHG1130；回收orchestration-receipt-07、110输入DocuN/evidence/TASK-110/orchestration-20261010。下一动作由用户转TASK110至新A+窗口，结果回原约定新110路径；不存在在途新运行。完整FR009/SEC003/G11/STEP015016/M1/项目未通过，主控只有核证和共享维护。

## 以下为v2.30及更早历史

'''
arch = '''# 架构动态文档

文档 v1.09，2026-10-10，Asia/Shanghai。需求v1.1、执行动态v2.31；以下v1.08及历史原字节保留。

## 现有宿主不满足已采用的全协议同步导航条款

固定Browser/sandbox正常运行，C05准确OOPIF观测取得真实同文档fragment提交；同frame/loader/document不变但完整URL变化与实际提交事件成立。现有sandbox/CSP/网络route组合不足以满足108/109已采用的禁止后续所有导航要求，生产NativeNavigationGate仍没有可核实现。此反证不证明网络、文件、系统逃逸，也不宣其它scheme均已实测。

原运行诊断路线封存，充分元数据/B01/停止子事实保留。TASK110只读技术方案重评核真实守卫能力及最小输出/信任合同方向，按用户目标、有效强条款、维护成本和可实施性形成一个待采用包，不预设必须fork或现成组件可用，不默改Must。新方案尚未采用，当前架构不变更为任何新引擎或新的页面权；H0/G11不通过、业务冻结，原已验G3—G10不受影响。实际未知data原因和资源余量仍作为限制，不继续调同栈参数反复。

## 以下为v1.08及更早历史

'''
decision110 = f'''# TASK-110 / R-104 技术方案收敛授权登记

{STAMP}，Codex编排Agent。父TASK109/R103已得到明确hash导航反证并关闭原运行路线，旧8/8根、4/4build/controller封存。当前目标仍FR009交互HTML和SEC003安全；原G11-P采用生效，不因当前实现失败自动降Must或取消用户目标。

本卡只委派工程事实和完整决策输入，编排保留总体架构/最终采用/共享状态维护。A+新隔离方案窗口，理由为专业范围转成原生接口与输出/安全合同取舍，不继承实现重试聊天；只原目标、批准边界、稳定source与原始反证。不是G11完整终审，不复跑B01/导航。

连续完成A出处和差异、B有限可实现性、C唯一推荐完整最小实施合同、D唯一采用增量与验收矩阵。真实运行/产品写入/安装/Git/私配/付费0；资料预算和落点以完整卡及orchestration-20261010为准。原生组件不存在覆盖证据则诚实明确，不交命名空接口；输出/信任/已采用强条款调整必须具体列差异待用户决定，不自行生效。候选合同不安装、不编码、不建立新服务，不借109旧预算。

当前已登记待转交，新使用0，结果预期DocuN/results/TASK-110-result.md，仅实际保存后才算结果；不存在执行者已开始事实。
'''
task110 = '''# TASK-110 / R-104 — G11导航边界的可实施方案与最小采用增量

## 目标与交付

你是本卡只读技术方案执行者，为编排提供一次完整决策输入，不接管架构最终裁定、业务实现或完整G11终审。连续完成A—D，解决现有宿主允许hash提交、却承诺禁止全部导航的具体矛盾，选出可实施且与用户目标相称的唯一推荐。

交付 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-110-result.md，资料/读入hash/有限源码摘录和一次文档一致性记录到同根DocuN/evidence/TASK-110/。只有方案文档，不能安装、跑新浏览器或重复109反证。不要只交“需要Native NavigationGate”，该名字从108就存在，当前缺的是可核覆盖与实际最小路线。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md，task_model/V4.0/AGENTS CHG-0003，需求v1.1、架构v1.09、唯一执行动态v2.31，逻辑07缺口转局部技术/05方案重评。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；读同版DocuS/AGENTS.MD和WORK第2/6章必要合同，锁定七指纹见项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动用后来规则。

接收A+增强执行，强推理，必须胜任浏览器生命周期/原生API/输出协议安全设计。新隔离方案窗口，未参与109实现，不继承其完整聊天/思考/自评。身份按实际登记，档位不冒官方模型名。本卡是技术决策支撑，不声称完整独立安全审计通过；原107隔离保持。

关联父TASK109/R103、设计108/R102、FR009/SEC003/B01、STEP015/016及G11-P。用户目标和原G11-P已经采用，只读技术方案在已授权项目编排内；新的引擎/依赖/输出/安全合同/主要模型或资源权必须先给具体增量，本卡不得使其生效。旧global78真实入口非78PASS、109/H0各8/8、build/controller4/4封存、preview4/16名义余额不可用，旧所有失败/未知/费用13元与投入保持。新任务只有资料预算，没有新运行权。

## 背景与最小充分上下文

原输出方案是模型生成HTML及计算/图形脚本，在独立非root、真sandbox、无网/只读容器的受限子frame运行；已采用108/109条款要求一次受信初始化后所有导航、同文档fragment、新target/子frame均创建或提交前同步拒绝。现实现只有诊断host、网络route、sandbox/CSP和事后观察，没有生产同步锚。

R08原始Frame绑定、可信手势/handler ACK、真实Page.navigatedWithinDocument、document/target完整URL交叉支持hash提交；loader/document backend不变是同文档性质，不能以裸Frame.url不含片段判未导航。root真实FAIL、原诊断路线已结束；旧data异常及资源余量未知不能阻塞已明确反证的方案交付，也不追认为本轮已解决。没有证据证明所有其它引擎都不可行或某组件必然可用。

按顺序只读入口/规则、本卡及TASK-110-work-decision.md、DocuN/evidence/TASK-110/orchestration-20261010/input-manifest.json；用户原始需求和最终需求中FR009/SEC003/附带B01相关段；TASK-108-result.md原A—D与TASK-108-work-decision.md有效采用边界；TASK-109.md置顶关闭许可及C05有效原合同；必要host/wrapper、navigation-tail和原始navigation-hash-counterexample/frame-binding/observations/stdout。跳过TASK109结果自评和实现聊天，旧大批/实验只按明确直接依赖取一项，不通读历史。

项目原始需求文档仅用户维护且保留历史整理性质，不能据代理整理段声称用户逐字提出某条。原需求、已批准最终需求、Agent方案、用户采用的具体实施合同四层分开。发生已采用条款调整仍需明确决定，不能以“hash看起来安全”擅自豁免，也不能凭未找到用户原话断言用户从未要求。

## 执行边界与资源

允许最小只读项目source/原件以及必要官方文档/原仓库源码/许可资料；只写DocuN/results/TASK-110-result.md和DocuN/evidence/TASK-110/。不修改产品/测试/迁移/锁/正式DocuS/公共库/原始需求/旧证据/旧记忆，不自行新增框架、原生服务或接口stub，不Git提交。

真实root、compile/unittest/Node程序、浏览器、Docker命令含inspect/exec/build/start、PG/SQL/role、模型/provider、付费、用户数据/private配置、联网安装/下载二进制/clone、删除均0。只允许纯文件hash/JSON读取和文档检查脚本，不import产品。官方HTTP只读查资料，不传私有source、聊天或配置。

新资料总投入最多5400秒，公开资料研究最多2400秒，至多8官方页和4官方源码文件、原生候选至多2、输出合同替代方向至多1；失败页和真实投入计数，不凑满额度。候选未支持关键范围就排除，不对每个浏览器系列研究。无明确依据不推荐自建浏览器fork；若保持当前绝对条款确实只能大改，说明工程/维护代价与未证，不用一句“写原生组件”隐藏成本。

同资料已读复用，不重新hash整个500对象或复现hash/data/旧失败。一次文档一致性检查最多60秒，有具体修正最多一次复检。资料受限只写具体未证，不借此恢复旧运行预算；本卡可完整交付方案边界，不宣动态通过。

## 验证、证据与审计关系

A交付约束出处与已发生差异。逐项定位用户目标、最终Must、已采用108具体强化、当前实现、真实反证。明确hash、跨文档data/blob/file/http、父/顶层导航、popup/target、新子frame、脚本/DOM正常交互各自要求；不以某项窄通过签其它项，资源125/128线程和约698MiB/768MiB仅风险线索，不推旧fork唯一原因。资料结论用事实/推断/未知分级，原反证无需重测。

B交付有限可实现性判别。现Playwright路线已反证，无需再调参数。原生候选必须给确切公开API或原始函数、触发范围、同步/异步、返回值、同文档fragment是否覆盖、target/frame创建是否覆盖、不可绕过路径和正常交互影响；最多2个。事件通知/导航后close/回滚/网络request拦截、同文档不触发的callback不充当全协议前置否决。没有支持依据就写不覆盖或未证明，不能用一个Gate类名当锚。

同时评估一条最小输出/信任合同方向：模型输出有限结构化交互描述，由受信版本化程序生成并运行交互HTML，禁止执行模型自由JS/任意markup。说明能否满足实际FR009计算/图形/教育交互，哪些表达能力受限；生成物仍是真交互，不以静态图替代。严格类型/有限操作与表达式/文本和渲染安全、模型数据不能触发代码/URL/任意工具须有可实现边界，不能靠字符串黑名单或把任意JS封装成受信脚本。若此路需改变已采用HTML输出形态、安全策略或Must，具体列待采用，不自行降标准，不默移回主应用执行。

C交付唯一推荐的完整最小实施合同。按用户价值、可核覆盖、实施量/维护/许可/平台/资源风险选择，不能先假设现成同步锚或无代价换引擎。给正常入口与最少两类有据交互样例、可信/不可信输入、数据/产物/profile/版本/commit语义、UI操作/失败文案、来源与权限/管道/外部停止、预算与未确认行为、真实文件职责和接口计划、G3—G10复用/兼容/保留式失败恢复。未实施接口明确为计划，不编造已有签名。若无法在原条款下给小而可实施方案，要完整交付最小调整合同和缺失决定，不伪造“保持所有要求且现成可实现”。

D交付一个合并采用增量包与未来最小验收矩阵。只列会实质改变现采用的输出/信任边界、引擎/依赖/许可证、主要模型/公开接口和资源/维护代价，正常配置细节不拆审批。原已采用四表/原父消费/预算/控制是否可保留按实际方案列，尚未实现不能说已迁移。待决最多一个包；若无需新采用给覆盖授权依据，而非默认为已批。矩阵含正常真实交互、恶意描述/代码/XSS/导航/新页/文件/网络反例、无权/失效/刷新/预算/停止及受影响业务兼容；给具体oracle/身份快照/有限样本和一次实现验证批组织，禁止9项至少18秒却分15秒的结构性矛盾。后续完整高风险成果保留隔离增强终审，不能为省卡取消，也不逐普通修正加审计。

本卡验证只检查A—D完整、原Must未静默改变、计划相互一致、出处/路径/证据/未知边界与一个采用包可审阅；不以外部文档或方案完成声称软件可运行或关口通过。

## 停止与回传

已达到可裁定唯一方案与具体增量即停，不为消耗时间扩大研究。关键资料缺失、无法提供前置覆盖、重要权/费用变化或预算到限只停依赖，并保存已完成和最少未证；不发动新H0或要求用户先测试组件来交方案。不要交多个需要下一卡再逐个查的候选清单。

保存TASK-110-result.md，包含A—D、事实与来源/版本/许可、唯一推荐理由和被排除替代、具体采用包、文档一致性记录、读入hash/范围、实际资料页和投入、所有未证、人工决定与下一步。声明零产品/运行、非完整G11终审；编排核证和用户采用之后才可另卡实施，不自填最终验收。保存完整可读后只回一句结论与可点击结果绝对路径。
'''
prefixes = {managed[0]: closed, managed[1]: work109, managed[2]: state, managed[3]: arch}
for relative, prefix in prefixes.items():
    assert "*" not in prefix and "|" not in prefix and (ROOT / relative).read_bytes() == old[relative]
    (ROOT / relative).write_bytes(prefix.encode("utf-8") + old[relative])
for relative, text in {"DocuN/results/TASK-110-work-decision.md": decision110, "DocuN/tasks/TASK-110.md": task110}.items():
    path = ROOT / relative
    assert not path.exists() and "*" not in text and "|" not in text
    path.write_text(text, encoding="utf-8")
assignment = read_json(NEXT / "window-assignment.json")
assignment["dispatch"] = "待转交"
save_json(NEXT / "window-assignment.json", assignment)
changes = [(1119, "DocuN/evidence/TASK-109/orchestration-receipt-07/receipt.json", "核证hash实际提交、准确OOPIF/原URL片段语义、500源/原件与78累计。"), (1120, managed[1], "裁定H0不通过、原运行路线与旧许可封存，转只读技术方案。"), (1121, managed[0], "置顶执行许可已结束，保旧全部卡面字节，不再恢复名义余额。"), (1122, managed[3], "v1.09记录已采用导航条款失败与新技术路线待决，不静默改Must。"), (1123, managed[2], "v2.31记录109已返回验收失败/诊断完成、110/R104登记待转交，原账不返。"), (1124, "DocuN/results/TASK-110-work-decision.md", "明确只读技术决策支撑的权、产物与新隔离窗口，非终审和实施许可。"), (1125, "DocuN/tasks/TASK-110.md", "完整A—D技术可行性/唯一实施合同/一采用包，不再分散容器小批。"), (1126, "DocuN/evidence/TASK-110/orchestration-20261010/input-manifest.json", "原目标/采用边界/稳定source与原始反证的最小输入，不传实现自评聊天。"), (1127, "DocuN/evidence/TASK-110/orchestration-20261010/verification-budget.json", "只资料时间/有限官方页与源码，新真实运行和产品写入0，旧预算封存。"), (1128, "DocuN/evidence/TASK-110/orchestration-20261010/window-assignment.json", "A+新隔离技术方案窗口待人工转交，尚未接收/开始。"), (1129, "DocuN/evidence/TASK-110/orchestration-20261010/delivery-proof.json", "一次文档回读和历史/源/原件保护，主控产品运行0。")]
addition = "\n" + "\n\n".join(f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{relative}。{reason}" for number, relative, reason in changes) + "\n"
assert "*" not in addition and (ROOT / managed[4]).read_bytes() == old[managed[4]]
(ROOT / managed[4]).write_bytes(old[managed[4]] + addition.encode("utf-8"))
checks = {}
for relative, prefix in prefixes.items():
    assert (ROOT / relative).read_bytes() == prefix.encode("utf-8") + old[relative]
    checks[relative] = {"identity": identity(ROOT / relative), "old_suffix_exact": True}
for relative in ["DocuN/tasks/TASK-110.md", "DocuN/results/TASK-110-work-decision.md"]:
    checks[relative] = identity(ROOT / relative)
assert report_path.read_bytes() == report
assert all(sha((ROOT / relative).read_bytes()) == expected for relative, expected in baseline.items())
assert all(sha(Path(path).read_bytes()) == expected for path, expected in old_sessions.items())
task_text = (ROOT / "DocuN/tasks/TASK-110.md").read_text(encoding="utf-8")
assert all(title in task_text for title in ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源", "验证、证据与审计关系", "停止与回传"])
save_json(NEXT / "delivery-proof.json", {"TASK": "TASK-110", "R": "R-104", "at": STAMP, "checks": checks, "old90881_report_and_seven_sessions_unchanged": True, "all500_mapped_source_unchanged_by_main": True, "only_next_readonly_card": True, "old_runtime_permits_closed": True, "new_used": 0, "dispatch": "待转交", "main_compile_test_build_start": 0, "document_check": "一次完整回读通过，非独立审计或产品测试"})
print(json.dumps({"saved": True, "old_route": "TASK109诊断结束/H0不通过/许可封存", "next_card": str(ROOT / "DocuN/tasks/TASK-110.md"), "resource": "A+新隔离方案窗口", "new_runtime": 0, "versions": {"state": "2.31", "architecture": "1.09", "last_CHG": "1129"}, "main_product_runs": 0}, ensure_ascii=False))
