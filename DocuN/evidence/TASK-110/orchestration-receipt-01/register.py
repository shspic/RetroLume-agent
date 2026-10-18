"""核证方案文档并保存唯一待采用包；不执行产品或运行许可。"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AREA = Path(__file__).resolve().parent
SOLUTION = ROOT / "DocuN/evidence/TASK-110/solution-20261010"
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def identity(path):
    raw = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(raw), "sha256": sha(raw)}


def save_json(path, value):
    path.resolve().relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not (AREA / "receipt.json").exists()
result_path = ROOT / "DocuN/results/TASK-110-result.md"
result = result_path.read_bytes()
delivery = read_json(SOLUTION / "delivery-check.json")
assert len(result) == delivery["result_bytes"] == 53624
assert sha(result) == delivery["result_sha256"] == "4072cfb433aa22fcf4648aa16fa03031300b746faf4c48050ca4eb3512efb30e"
assert delivery["formal_document_check_count"] == 1 and delivery["recheck_count"] == 0 and delivery["document_checks_pass"]
assert all(value == 0 for value in delivery["runtime_counts"].values())
inputs = read_json(SOLUTION / "input-identity.json")
assert inputs["all_manifest_inputs_match"] and inputs["all_seven_rule_hashes_match"]
for row in inputs["local_inputs"]:
    path = Path(row["path"])
    raw = path.read_bytes()
    assert len(raw) == row["bytes"] and sha(raw) == row["sha256"]
for row in inputs["locked_rules"]:
    assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
supplementary = read_json(SOLUTION / "supplementary-input-identity.json")
supplement_rows = supplementary if isinstance(supplementary, list) else supplementary.get("files", supplementary.get("inputs", []))
for row in supplement_rows:
    assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
official = read_json(SOLUTION / "official-sources.json")
assert official["unique_official_resources_attempted"] == 8 and official["official_source_files_attempted"] == 4 and official["failed_resources"] == 1
assert official["native_candidates"] == 2 and official["output_contract_directions"] == 1
assert delivery["total_material_seconds_conservative_upper"] == 1951 and delivery["public_research_wall_seconds"] == 253
raw_report109 = ROOT / "DocuN/results/TASK-109-result.md"
raw109 = raw_report109.read_bytes()
assert sha(raw109) == "30c63a9907925241185c3d8377fedea06da7901eed1b3d5a96409938ce207a01"
managed = ["DocuN/results/TASK-110-work-decision.md", "DocuN/tasks/TASK-110.md", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD", "DocuS/文档变更记录.MD"]
old = {relative: (ROOT / relative).read_bytes() for relative in managed}
assert "文档 v1.09" in old[managed[2]].decode("utf-8-sig").splitlines()[2] and "文档 v2.31" in old[managed[3]].decode("utf-8-sig").splitlines()[2]
assert "CHG-1129" in old[managed[4]].decode("utf-8-sig")[-1000:]
for relative, raw in old.items():
    path = AREA / "before" / relative
    path.resolve().relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
(AREA / "TASK-110-as-returned.md").write_bytes(result)
evidence = {path.name: identity(path) for path in SOLUTION.iterdir() if path.is_file()}
save_json(AREA / "receipt.json", {"TASK": "TASK-110", "R": "R-104", "at": STAMP, "report": identity(result_path), "direct_input_count": inputs["manifest_items"], "local_hash_rows_checked": len(inputs["local_inputs"]), "seven_locked_rules_match": True, "evidence": evidence, "reading_basis": "完整A—D、原采纳边界、原件摘要/身份、有限候选官方范围与完整计划，不凭自评判动态通过", "verdict": "通过，仅只读技术方案交付；推荐包待用户采用", "package": "G11-P110", "package_adopted": False, "implementation_authorized": False, "new_product_runs": 0, "material_seconds_upper": 1951, "research_seconds_upper": 253, "metadata_path_lookup_correction": "主控首次查document-check.json不存在，已定位并读取实际delivery-check.json；未运行产品", "old_TASK109_permits_sealed": True, "old_global_roots": 78, "old_costs_failures_and_evidence_not_reset": True, "scope": "不宣G11/B01/SEC003或数学、运行、停止、独立终审通过"})
save_json(AREA / "stop-proof-candidate.json", {"at": STAMP, "status": "主控方案细化候选，包含在待采用包实施条件内；非实际停止验证", "source_basis": [{"url": "https://man7.org/linux/man-pages/man7/pid_namespaces.7.html", "scope": "init终止、嵌套命名空间和禁止返回祖先的规范"}, {"url": "https://raw.githubusercontent.com/microsoft/WSL2-Linux-Kernel/linux-msft-wsl-6.6.114.1/kernel/pid_namespace.c", "function": "zap_pid_ns_processes", "scope": "与此前实测kernel版本对应的固定tag，禁止新PID、发送SIGKILL并等待namespace其余任务退出"}, {"url": "https://raw.githubusercontent.com/torvalds/linux/v6.6/kernel/pid_namespace.c", "function": "zap_pid_ns_processes", "scope": "同主版本标准源旁证"}], "supported_mechanism": "private PID namespace init结束时内核清理本namespace任务；init回收前等待其余任务退出。子namespace及无祖先迁入能力需结合对象前提核证", "proof_requires": ["实际平台/kernel来源版本与机制适用", "privatePID且init=1的真实身份/出生/namespace，工作均在该namespace及其子树", "无host/sharedPID/其它namespaceFD或任务迁移途径、原最小权限和受信启动链", "同CID/image/nonce外部kill与init退出/wait及events相互绑定", "无restart、所有拥有的CLI/管道/控制器结束且时序完整", "完整候选合成验证与独立安全/一致性终审核证适用"], "never_sufficient_alone": ["HTTP200", "一次docker kill返回0", "Stopped或Pid0字段", "数据库状态", "只公开源码未核本对象"], "output_scope": "可核证自有工作任务树停止，不声称cgroup目录删除或内存完全释放", "if_incomplete": "cleanup_unconfirmed/tree_unconfirmed，全reserve保留、后续start封闭；不加特权或制造空值", "avoid_unnecessary_gate": "不把停后cgroup文件直接可读取作为唯一证据路径，不单独复现109或开额外准备批", "old109_dynamic_verdict_unchanged": True})

work = f'''# TASK-110 / R-104 方案文档验收关闭与G11-P110待采用

{STAMP}，Codex编排Agent。110报告53624字节/SHA4072cfb433aa22fcf4648aa16fa03031300b746faf4c48050ca4eb3512efb30e完整A—D、16冻结直接输入和补充读入/七规则身份一致；一次文档检查0.2472807秒、研究253秒/资料1951保守上界、零产品运行和写入证据吻合。通过只读技术方案交付，原结果原字节不改；资料许可结束，剩余资料额度不恢复运行。不是完整独立终审或G11/B01/SEC003实际通过。

## 唯一推荐与需要采用的具体变化

推荐G11-P110，主体为有限interactive_description.v1数据、html_explanation.v2受信profile、compiled_interactive_html.v1产物和retrolume.preview.v2管道。固定项目代码在独立容器解释有限AST/计算/绘图，模型不提供可执行自由HTML/JS/markup。参数调节、计算读值、柱/曲线/点线图和reset是真实远端交互；首版不支持任意布局/脚本/CSS、复杂动画/拖拽、插件或媒体，unsupported明确失败并保原成果。独立HTML导出没有新增为Must。

这是原采用输出/信任/公开输入语义的实质调整：将任意脚本执行后全部导航创建前同步否决的承诺，替换为有限类型/编译与固定源码无URL/历史/目标/frame能力出口；任何合法输入都不得导航或新建页面，代码/markup/URL在入口被拒或仅作文本。若程序/解析器/浏览器发生缺陷而导航已经发生，必须判缺陷、关能力、精确停止，不能声称前置拒绝。没有hash豁免，不回放旧109反例或改其FAIL。

原学习/教学来源与资格、原四账/UNKNOWN/OneCall/同COMMIT、012四表和两个NOLOGIN角色、API007路由/PNG/owner/独立持久3次180秒及每次最多60秒设计保留，字段/校验/hash按新类型更新；目前未实现，不宣迁移。输入从通用click/raw key改为可信控件set_number/reset，模型图片入口取消。资源候选明确pids256与memory/swap1024MiB，较旧增加128任务/256MiB，同时仍一个preview；时间/频次不增加，其他UID/sandbox/networknone/readonly/capdrop/NNP/privateIPC/临时空间/无挂载socketportsecret不放宽。无新CEF/Qt/fork/数学第三方库/服务，维护有限校验器与固定renderer；源码和第三方清单完整仍为实现检查。

## 主控纳入完整实施卡的细化条件

结果C6的物理任务停止要求保留，但不把停后直接读取host cgroup文件指定为唯一可行证明。主控有限核[PID namespace规范](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)与[对应WSL内核固定tag](https://raw.githubusercontent.com/microsoft/WSL2-Linux-Kernel/linux-msft-wsl-6.6.114.1/kernel/pid_namespace.c)的zap_pid_ns_processes，内核停止init时关闭新PID并清理/等待namespace其余任务，标准源6.6相符。此为B类机制依据，不是新生产对象或历史109树空的动态通过。

下一卡采用private PID namespace/init结束组合证明候选：核实际平台适用、init/namespace/出生与所有工作子树及无祖先/共享namespace迁移途径，精确CID/image/nonce外部kill-init退出/wait-events、无restart、拥有的CLI/管道/控制者结束。不得单凭Stopped/Pid0或kill返回0宣树空；不声称cgroup目录/内存已释放。组合不齐仍unconfirmed/全reserve保留/start封闭，不加privileged/挂载或放宽权限；该路径与真实正常/故障停止并入同一完整实现批和集中独立终审，不能单独反复前置“能不能读cgroup”。旧109namespace推断、8/8和所有失败不追签成新通过。

数值与入口普通细节需在实现前一次锁清。规范十进制控制值/范围/step格点关系必须精确比较，不用二进制浮点把不同合法步值当相同；受信AST数学采用明示有限数字语义、步骤扣减与独立oracle误差，Python/Node规则一致，域/步数错误保整个最后一致快照。新preview必须有准备/至少一次操作/停止余量才预扣，最低reserve在完整卡固定，不返还失败次数、不用微小剩余时间给无法交互的session。Supervisor/Reaper是同机单调时钟与预算权，容器时钟/读值无延限或退款权。编译/规范化同COMMIT只能有限纯数据处理，禁止事务内Docker/网络/渲染；非法输出仍记真实RECEIVED/费用但无可预览artifact，hook异常rollback/UNKNOWN不重发。这些细化不改C2枚举/域/上界或增页面权限。

## 一个待决定包与授权终点

唯一待采用项为结果D1的G11-P110及以上实施条件。当前recommended_pending_user_adoption，adopted=false、implementation_authorized=false。主控建议采用：保FR009真实交互/可核计算/资料关联和SEC003禁止网/文件/系统/模型工具，调整已采用的输出语言、实现安全承诺和固定资源；不是对原任意脚本合同悄悄降标准。需要用户明确接受表达能力限制和信任合同取舍；普通布局、内部函数名字不另拆审批。

用户采用后才出新完整实施/业务接线/定向合成验证/普通修复/收尾卡，相关工作沿原110方案窗口、A+强推理优先，稳定成果一次新隔离增强终审。未采用则业务继续冻结，不再旧109小批。当前不占TASK111/R105、不派发代码任务，不开容器/PG/HTTP/模型，不安装/触用户库/真实provider/费用/Git/删除/发布，不改变正式最终需求或用户原文。原G11-P已采用部分和旧事实保留，新技术包未生效。

## 以下为110原授权登记

'''
closed = f'''# TASK-110 / R-104 只读方案已交付并验收，资料许可结束

{STAMP}，Codex编排Agent。A—D文档交付通过，结果原53624字节/SHA4072cfb4…保留。下一步只有G11-P110及TASK-110-work-decision.md置顶实施条件的明确采用，当前adopted=false、implementation_authorized=false。

下面原合同只保历史；剩余资料时间不恢复产品/运行许可，不继续研究更多浏览器或重复旧109。所有旧失败/时窗/费用保持；未授权任何新引擎、代码、用户库/provider/安装/Git/删除。候选完整实现和必需独立终审仍未派。

## 以下为原110完整合同

'''
arch = '''# 架构动态文档

文档 v1.10，2026-10-10，Asia/Shanghai。需求v1.1、执行动态v2.32；以下v1.09及原历史保字节。新内容为未采用候选，不改变当前生效合同。

## G11-P110候选为有限数据语言与受信交互程序

110/R104只读技术方案已交付，通过文档核证；唯一推荐模型只产interactive_description.v1，固定版本/hash的自有程序在原独立容器完成有限计算/图形，profile html_explanation.v2/产物compiled_interactive_html.v1/内部preview.v2。禁止模型自由HTML/JS/markup成为代码或危险sink；可信控件只set_number/reset，保真实交互/来源和原禁止权限，首版不支持任意布局脚本/复杂动画拖拽。无新原生引擎或数学库。

候选以输入/编译闭包和固定程序无导航能力出口替换任意已执行脚本的全协议原生同步否决承诺，导航出现仍为缺陷需关能力/精确停止，不豁免hash。四表/角色、原四账/COMMIT/资格/PNG/owner/3次180秒设计延续并按新类型调整。候选固定资源pids256/memory-swap1024MiB、其余隔离不变；成本为表达能力限制和有限语言/程序维护。主控物理停止候选路线为private PID namespace/init结束的完整身份与kernel机制/外部停止组合，保真实验证与独立终审，不把Stopped或不能读cgroup单字段当结论。

本包尚待用户明确采用，数值/最低reserve/时钟/短事务普通细节在完整实施卡锁定。当前原108/109强条款仍生效但已被hash反证、旧运行路线封存；新协议/程序/DDL/API未实现，不签已验证或生效。原G3—G10充分未变结论保留，生成/预览业务冻结，完整G11/M1/项目未通过。

## 以下为v1.09及更早历史

'''
state = '''# 执行动态文档

文档 v2.32，2026-10-10，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.10、task_model/07局部方案重评与05维护；以下v2.31及原历史保字节。

## 110方案文档通过，唯一G11-P110包待用户采用

TASK110/R104已返回53624/4072cfb4…，A—D完整与16冻结直接输入/补充身份/七规则匹配；研究253秒、资料1951保守上界、一次文档检查0.2472807/无复检、产品和代码运行0。两个原生候选仅在已读范围排除、移动branch/失败源未冒固定版本；唯一推荐有限结构化描述加固定受信renderer，真实数字/图形交互保留，表达能力和执行信任合同实质变化。通过仅只读方案交付，不签数学/安全/运行/G11或终审。

G11-P110包括新description/profile/artifact/管道v2，禁止模型自由HTML/JS/markup执行，可信数据控件代click/raw key、取消模型图片；同COMMIT/四表角色/原四账资格/PNG/owner/preview3次180秒保留设计，固定pids256/memory-swap1024MiB而其它权限不放宽。任意脚本的全部导航同步否决改为合法数据无此能力出口、违法输入前拒、程序偏差检测后停止，导航仍缺陷不准hash。首版布局/操作/图形有限，复杂动画拖拽未支持。这是待明确采用包，不自动生效。

主控实施条件同Work决定：核对应WSL内核的private PID namespace/init结束机制并结合新对象身份、外部kill/wait/events/EOF/控制进程退出、无逃逸前提，作为物理停止组合证明候选；不强制停后host cgroup读取唯一门、不单字段签通过。数值格点精确/数学域与步数、最低可交互reserve、同机监督单调时钟和事务内纯处理在完整卡锁定。候选动态证据与稳定成果一次隔离增强终审仍必需。

110文档验收关闭/资料许可结束，adopted=false、implementation_authorized=false，当前等待唯一采用决定；尚未占TASK111/R105或派代码。通过后沿原110A+窗口组织一张完整实现/接线/验证/普通修复/收尾卡，再集中独审，不逐普通改动审。未采用则保持当前冻结，不恢复109。

原TASK109/H0 8/8、build/controller4/4、preview4/16名义余额及全部许可封存，global78不是78PASS、140.297真实量含30.658build子段、原失败/UNKNOWN/13元/分类重叠/时窗保持；旧hash反证/data未知不改。原107隔离/旧G3—G10有效，全HTML/G11/STEP015016/M1/项目未通过，原始/最终需求未修改。本批CHG1130—1137，下一CHG1138；回收DocuN/evidence/TASK-110/orchestration-receipt-01，主控仅只读源核/文档，无产品或资源运行。

## 以下为v2.31及更早历史

'''
prefixes = {managed[0]: work, managed[1]: closed, managed[2]: arch, managed[3]: state}
for relative, prefix in prefixes.items():
    assert "*" not in prefix and "|" not in prefix and (ROOT / relative).read_bytes() == old[relative]
    (ROOT / relative).write_bytes(prefix.encode("utf-8") + old[relative])
save_json(AREA / "adoption-status.json", {"TASK": "TASK-110", "R": "R-104", "at": STAMP, "package": "G11-P110", "single_decision": True, "authoritative_scope": {"result": identity(result_path), "orchestration_decision": identity(ROOT / managed[0]), "sections": "D1/C2—C7及主控停止/数值/时钟/短事务实施细化"}, "adopted": False, "implementation_authorized": False, "task_document_verdict": "通过", "next_implementation_task_allocated": False, "old109_sealed": True, "no_new_runtime": True, "reason_for_confirmation": "已采用的输出/信任/公开输入和固定资源的实质变更；锁定公共AGENTS第2节31行", "ordinary_internal_details_not_extra_approvals": True})
save_json(AREA / "window-status.json", {"TASK": "TASK-110", "R": "R-104", "dispatch": "已返回", "acceptance": "通过，仅文档", "old_material_permit_closed": True, "adoption": "等待用户唯一决定", "recommended_implementation_window": "采用后沿原110方案窗口A+，未派发", "next_independent_review": "稳定完整G11后新隔离A+，未派发", "new_product_runs": 0})
changes = [(1130, "DocuN/evidence/TASK-110/orchestration-receipt-01/receipt.json", "核53624方案/输入和资料账，文档通过、所有动态门保留。"), (1131, "DocuN/evidence/TASK-110/orchestration-receipt-01/stop-proof-candidate.json", "固定WSL/Linux规范机制与对象身份的停止证明候选，非历史动态追签。"), (1132, managed[0], "置顶文档验收与唯一G11-P110请求、输出/安全/资源变化和实施细化。"), (1133, managed[1], "110资料许可结束/原卡字节保留，候选未采用未授运行。"), (1134, managed[2], "v1.10登记有限数据/受信程序候选，旧生效合同和失败保持。"), (1135, managed[3], "v2.32登记110已返回文档通过、等待唯一采用、111未占未派，原78账不返。"), (1136, "DocuN/evidence/TASK-110/orchestration-receipt-01/adoption-status.json及window-status.json", "唯一包尚待用户决定，与资料通过/实现/终审分轴，不虚构派发。"), (1137, "DocuN/evidence/TASK-110/orchestration-receipt-01/delivery-proof.json", "一次回读与历史/source/结果保护，主控产品运行0。")]
addition = "\n" + "\n\n".join(f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{relative}。{reason}" for number, relative, reason in changes) + "\n"
assert "*" not in addition and (ROOT / managed[4]).read_bytes() == old[managed[4]]
(ROOT / managed[4]).write_bytes(old[managed[4]] + addition.encode("utf-8"))
checks = {}
for relative, prefix in prefixes.items():
    assert (ROOT / relative).read_bytes() == prefix.encode("utf-8") + old[relative]
    checks[relative] = {"identity": identity(ROOT / relative), "old_suffix_exact": True}
assert result_path.read_bytes() == result and raw_report109.read_bytes() == raw109
for row in inputs["local_inputs"]:
    relative = Path(row["path"]).resolve().relative_to(ROOT).as_posix()
    if relative not in prefixes:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
save_json(AREA / "delivery-proof.json", {"TASK": "TASK-110", "R": "R-104", "at": STAMP, "checks": checks, "reports110_and109_unmodified": True, "read_inputs_unmodified_except_serial_shared_state_prefixes": True, "new_prefix_no_stars_or_tables": True, "document_readback": "一次通过，非软件验证/独立终审", "one_package_pending": True, "next_task_not_allocated": True, "product_compile_test_build_start_by_main": 0})
print(json.dumps({"saved": True, "verdict": "110文档通过", "adoption": "G11-P110待用户唯一决定", "decision": str(ROOT / managed[0]), "versions": {"state": "2.32", "architecture": "1.10", "last_CHG": "1137"}, "runtime": 0, "TASK111_allocated": False}, ensure_ascii=False))
