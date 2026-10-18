"""登记用户采用并保存完整执行合同；编排不执行产品实现或测试。"""
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AREA = Path(__file__).resolve().parent
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()
PERMIT = "TASK-111-G11-P110-20261010"
PG_IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
BASE_MANIFEST = "c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    raw = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(raw), "sha256": sha(raw)}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path, value):
    path.resolve().relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def docker_read(args):
    return subprocess.run(["docker", *args], capture_output=True, encoding="utf-8", text=True, timeout=15, check=True).stdout.strip()


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not (ROOT / "DocuN/tasks/TASK-111.md").exists() and not (AREA / "adoption-receipt.json").exists()
report = ROOT / "DocuN/results/TASK-110-result.md"
report_bytes = report.read_bytes()
assert len(report_bytes) == 53624 and sha(report_bytes) == "4072cfb433aa22fcf4648aa16fa03031300b746faf4c48050ca4eb3512efb30e"
work110_path = ROOT / "DocuN/results/TASK-110-work-decision.md"
assert sha(work110_path.read_bytes()) == "466f39b54abad9544c4048b5b37a25709e0a92f26ba7463c8b68720359dc52da"
rules = read_json(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
assert all(sha(Path(row["absolute_path"]).read_bytes()) == row["sha256"] for row in rules)
pg = json.loads(docker_read(["image", "inspect", "--format", '{"id":{{json .Id}},"descriptor":{{json .Descriptor}},"digests":{{json .RepoDigests}},"os":{{json .Os}},"architecture":{{json .Architecture}}}', PG_IMAGE]))
assert pg["id"] == PG_IMAGE and pg["os"] == "linux" and pg["architecture"] == "amd64"
assert not docker_read(["ps", "-a", "--filter", "name=^retrolume-task-111-", "--format", "{{.Names}}"])
assert not docker_read(["volume", "ls", "--filter", "name=^retrolume-task-111-", "--format", "{{.Name}}"])
compose_version = docker_read(["compose", "version", "--short"])
base_path = ROOT / "deploy/preview/task109-c01-cache/oci/blobs/sha256" / BASE_MANIFEST
assert sha(base_path.read_bytes()) == BASE_MANIFEST
vendor_package = ROOT / "deploy/preview/task109-c04-context/attempt-02/vendor/playwright-core/package.json"
assert read_json(vendor_package)["version"] == "1.62.1"
ps_script = "$r=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18111,55451) } | Select-Object LocalAddress,LocalPort,OwningProcess); ConvertTo-Json -InputObject $r -Compress"
ports = json.loads(subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script], capture_output=True, encoding="utf-8", text=True, timeout=20, check=True).stdout)
assert ports == []
managed = ["DocuN/results/TASK-110-work-decision.md", "DocuS/最终需求文档.MD", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD", "DocuS/文档变更记录.MD"]
old = {relative: (ROOT / relative).read_bytes() for relative in managed}
assert "文档 v1.10" in old[managed[2]].decode("utf-8-sig").splitlines()[2] and "文档 v2.32" in old[managed[3]].decode("utf-8-sig").splitlines()[2]
assert "CHG-1137" in old[managed[4]].decode("utf-8-sig")[-1000:]
original_req = identity(ROOT / "DocuS/原始需求文档.MD")
for relative, raw in old.items():
    target = AREA / "before" / relative
    target.resolve().relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
source_paths = ["backend/app/activities/repository.py", "backend/app/activities/service.py", "backend/app/capabilities/contracts.py", "backend/app/capabilities/gateway.py", "backend/app/capabilities/transport.py", "backend/app/service_config.py", "backend/app/main.py", "backend/app/local_session.py", "backend/app/preview/contracts.py", "backend/app/preview/supervisor.py", "backend/app/preview/reaper.py", "backend/app/worker/command.py", "backend/app/worker/one_call.py", "backend/app/worker/worker_main.py", "frontend/src/activities/LearningResult.tsx", "frontend/src/activities/TeachingWorkspace.tsx", "frontend/src/activities/ActivityWorkspace.tsx", "frontend/package.json", "frontend/package-lock.json", "backend/requirements.txt", "backend/requirements.lock", "deploy/start_local.py", "config/activity.example.json", "deploy/preview/seccomp.json", "deploy/preview/host.cjs", "deploy/preview/wrapper.html"]
source_ids = [identity(ROOT / relative) for relative in source_paths if (ROOT / relative).is_file()]
source_ids.extend(identity(path) for path in sorted((ROOT / "backend/migrations").glob("*.sql")))
new_expected = ["backend/app/preview/description.py", "backend/app/preview/compiler.py", "backend/app/preview/generation.py", "backend/app/preview/repository.py", "backend/app/preview/api.py", "backend/app/preview/host_policy.py", "backend/migrations/012_html_explanations.sql", "deploy/preview/renderer-host.cjs", "deploy/preview/runtime.html", "deploy/preview/runtime.cjs", "deploy/preview/runtime.css", "deploy/preview/descriptor.schema.json", "deploy/compose.local.yml", "frontend/src/explanations"]
assert all(not (ROOT / relative).exists() for relative in new_expected), "预期新路径已有成果，不能覆盖"
receipt = {"at": STAMP, "authority": "用户2026-10-10对G11-P110及已保存Work裁定回复确认，明确采用；实际消息时刻未给不以登记时刻回填", "user_message": "确认", "package": "G11-P110", "source_result": identity(report), "source_work_before_adoption": identity(work110_path), "adopted": True, "implementation_contract": "TASK-111/R-105在本卡精确范围内有效；不恢复TASK109", "old_global_roots": 78, "old_failures_costs_times_not_reset": True, "new_product_runs": 0, "no_user_DB_provider_paid_install_delete_git_publish_permission": True}
save_json(AREA / "adoption-receipt.json", receipt)
save_json(AREA / "input-manifest.json", {"TASK": "TASK-111", "R": "R-105", "at": STAMP, "report": identity(report), "work_before_adoption": identity(work110_path), "source_inputs": source_ids, "new_paths_absent": new_expected, "public_rules": rules, "existing_OCI_manifest": identity(base_path), "existing_vendor_package": identity(vendor_package), "original_user_requirement": original_req, "minimum_read_scope": "补本卡/110有效采用/新正式头段；原110未变A—D复用，执行时按真实改动定向读直接依赖，不重读旧500对象"})
budget = {"TASK": "TASK-111", "R": "R-105", "permit": PERMIT, "start_policy": "执行者首次读卡即同机单调起点，一次固定12小时总截止，所有准备/实现/修正/证据保存计本窗，换日期窗口不重开", "seconds": {"total_window": 43200, "metadata": 7200, "offline_total": 7200, "real_total": 14400, "real_batch_each": 3600, "preview_each": 60, "stop_diagnostic_each": 15, "preview_total": 840, "stop_diagnostic_total": 210, "preview_reaper_batch": 1200, "cleanup_reserved": 1800, "main_browser_each": 2400, "imagebuild_each": 600}, "counts": {"real_batches": 6, "image_builds": 3, "preview_creates": 14, "preview_starts": 14, "preview_total_simultaneous": 1, "preview_reaper_validation_batches": 2, "PG_containers": 1, "PG_volumes": 1, "PG_container_starts": 6, "API_listener_starts": 4, "main_browser_starts": 3, "model_synthetic_requests": 6, "Windows_OneCall_sessions": 8, "frontend_typecheck_build_batches": 3, "offline_related_batches": 6, "HTTP_total": 5000, "public_PNG_gets_subset": 3000, "public_inputs_subset": 300, "internal_inputs": 500}, "first_plus_repair": "所有上限含首次/失败/同卡有依据的普通修正，不是完成后必须用满；根批内step/subattempt必须留源绑定和次数，不能叫免费probe", "preview_product_policy": {"max_starts_activity": 3, "max_seconds_activity": 180, "window_max": 60, "window_min": 30, "ready_max": 8, "input_close_margin": 10}, "offline_checks": "先定向集中，实际普通修正才复检；无变化不全量重跑", "old_global_roots": 78, "old109": "root/H0各8/8、build/controller4/4与所有许可封存，preview4/16名义余额不可借", "new_used": 0, "zero": ["paid_provider", "user_database", "user_private_config", "internet_install_pull", "new_engine_dependency", "privileged_or_host_bind", "git_commit_push", "committed_delete_drop", "release"]}
save_json(AREA / "verification-budget.json", budget)
resources = {"TASK": "TASK-111", "R": "R-105", "at": STAMP, "main_metadata_readonly": True, "PG": {"image": pg, "container": "retrolume-task-111-g11-v2-pg1", "volume": "retrolume-task-111-g11-v2-pg1-data", "network_mode": "bridge", "host": "127.0.0.1", "port": 55451, "container_port": 5432, "cpu": 1, "memory_MiB": 512, "pids": 128, "databases": ["retrolume_task111_main", "retrolume_task111_upgrade", "retrolume_task111_fault"], "roles": ["retrolume_task111_admin", "retrolume_task111_app", "retrolume_task111_denied"], "credentials": "生成仅进程内/安全stdin或限定子进程Env，不放argv/文档/日志/证据；本卡角色密码允许有据内存重置，不能触其它角色"}, "preview": {"names": ["retrolume-task-111-g11-preview-" + str(i).zfill(2) for i in range(1, 15)], "tag_prefix": "retrolume-task-111-g11-renderer", "tags_max": 3, "network": "none", "read_only": True, "uid_gid": "10001:10001", "CPU": 1, "memory_swap_MiB": 1024, "pids": 256, "private_PID_IPC": True, "init": True, "restart": "no", "tmpfs_MiB": {"/tmp": 128, "/home/preview": 32}, "new_privileges_mounts_socket_ports": 0}, "API": {"address": "127.0.0.1", "port": 18111}, "cached_build": {"base_manifest": BASE_MANIFEST, "OCI_dir": (ROOT / "deploy/preview/task109-c01-cache/oci").as_posix(), "vendor_source": (ROOT / "deploy/preview/task109-c04-context/attempt-02/vendor/playwright-core").as_posix(), "version": "1.62.1", "runtime_source_target": "deploy/preview/vendor/playwright-core", "old_cache_readonly": True, "no_old_runner_or_container_execution": True}, "compose_version_seen": compose_version, "new_names_ports_absent": True, "remaining_check": "执行者每次启动前在新批固定归属与对象实际身份；不使用本次只读快照抢占冲突对象", "retention": "停止所有本卡自有运行，保容器/卷/库/角色/合成数据/镜像/失败日志，不rm/prune/drop/DELETE提交"}
save_json(AREA / "resource-mapping.json", resources)

work110 = f'''# TASK-110 / R-104 G11-P110采用生效

{STAMP}，Codex编排Agent。用户2026-10-10对上一条具体G11-P110及Work裁定回复“确认”，采用生效；没有精确消息时刻，不把登记时间填作批准时刻。源结果53624/4072cfb4…、原完整裁定6982/466f39b5…保持对应，原待采用正文保作历史。

有限description/profile html_explanation.v2/compiled artifact/preview.v2、固定程序的计算图形、禁止模型自由HTML/JS/markup执行、输入从click/key变有限set_number/reset、原生成图片取消，以及数据/代码边界替代任意已执行脚本全导航原生同步否决承诺均已采用。合法描述仍不得产生任何导航/URL历史变化/新target/frame；突破时是缺陷须关能力/精确停止，不能冒事前已拒。首版表达限制和pids256/memory-swap1024MiB、一preview/3次180秒、原其它隔离及四账/资格/同COMMIT/四表角色设计保留，停止/数值/时钟/短事务细化一起有效。

新TASK111/R105完整实现接线/定向合成验证/有据普通修正/精确收尾卡才是本次执行许可，采用不是软件运行/停止/独立终审通过。沿原110方案窗口A+强推理，旧109及110资料许可不恢复；旧78根/13元/所有失败/时间原账保留。新预算与精确新合成资源以111卡与orchestration-20261010为准，不触真实用户库/provider/费用、安装联网、特权、删除提交、Git或发布。

当前111已登记保存回读待人工转交，新实际0、尚未接收/开始。稳定完整G11候选仍有一次新隔离增强安全/一致性终审，普通修正不逐次审计；未最终验收不能用户放行。以下原验收与采用请求保留原字节。

'''
requirements = '''# 最终需求文档

需求与实现验收基线 v1.2，2026-10-10，Asia/Shanghai。用户明确确认G11-P110及主控裁定，更新FR009/SEC003的具体输出与执行边界；31项需求编号、优先级与其它Must保留。以下v1.1及更早批准原文完整保字节，历史不能覆盖本次明确采用。

## 已采用的交互HTML有限实现与安全边界

FR009仍要求应用内真正可交互、计算/内容可核、资料关联、错误可解释且不破坏原成果；首版有限参数、数值读值、柱/曲线/点线图及reset，不承诺任意布局脚本、复杂动画拖拽、插件或独立HTML导出。模型只提供interactive_description.v1，固定项目程序在独立容器生成并运行交互HTML，计算/图形脚本限受信固定实现，不执行模型自由HTML/JS/markup，不以静态图替代真实交互。

SEC003的无页面联网、本地文件、系统命令、直接模型/工具能力及真实权限反例、正常交互、必要独立终审保持Must。已采用实现条款改为严格数据/编译边界及固定程序无导航/任意代码能力出口；合法描述与有限输入不得产生导航/URL历史变化/新页面或frame。未知/越权输入前拒，文字仅普通文本；运行程序/解析器/浏览器偏差导致这些行为仍为缺陷须关能力并停止，不将事后停止称为对任意已执行自由脚本的事前同步否决。不豁免hash，旧109反证与失败不改写。

源为DocuN/results/TASK-110-result.md D1/C2—C7及TASK-110-work-decision.md有效采用。原独立容器/画面/有限输入/外部停止、四账/COMMIT/父来源资格、3次180秒/每次最多60秒继续；固定资源pids256/memory-swap1024MiB而其它隔离不放宽。完整G11/B01/STEP015016放行仍需当前方案完整真实证据和独立增强终审，采用不等于已实现或通过。用户原始需求文件不修改。

## 以下为v1.1及更早原字节历史

'''
arch = '''# 架构动态文档

文档 v1.11，2026-10-10，Asia/Shanghai。需求v1.2、执行动态v2.33；以下v1.10及旧历史保字节。G11-P110采用生效，实际代码仍未实现。

## G11已采用有限描述和受信程序路线

采用interactive_description.v1→受信html_explanation.v2→compiled_interactive_html.v1及preview.v2，固定项目程序在独立容器计算/Canvas，模型不产生可执行自由HTML/JS/markup或通用URL/DOM操作。参数/数学AST/图形/reset闭合，未知输入失败关闭；合法数据无导航/新target/frame能力出口，观察到越界仍缺陷须关能力/精确停止，不承诺对任意已执行脚本全协议原生同步否决。

四表/两个NOLOGIN角色/旧四账/OneCall/同COMMIT/父与source/scope/记忆资格、API007/PNG/owner/preview3次180秒延续设计并按新版本调整，保持主应用不执行远端代码。可信控件只发set_number/reset，所有迟到身份守卫仍需实现。新固定pids256、memory/swap1024MiB、CPU1/一preview，其它隔离和临时空间不增权；最低reserve30秒才允许预扣，以保证8秒准备/交互/10秒停止余量。Supervisor/Reaper使用同机单调权威，Node不延限或退款。

物理停止候选为实际private PID/init及工作子树/无逃逸前提、平台kernel机制、外部精确kill/wait/events/EOF与控制者退出的完整组合；不是单字段Stopped或直接cgroup文件唯一门，缺证仍unconfirmed保全reserve。实际新正常/故障/恢复与集中独立终审未做，不能追签旧109为树空。新产品程序/自包含依赖/许可证和安全数据流需实现与验证。

TASK111计划整合完整生成/持久资格/预览/输入/停止/工作台、生产控制和本地部署。Compose以现有本机PG依赖服务+renderer构建入口落实，preview仍按持久预算动态创建，不能常驻服务绕次数；Windows本地app+外部Docker控制不切到容器内Docker socket。新合成实例独占验证，旧user库/旧合成及109资源不启。Linux/Nginx公共部署仍后续阶段，不在本卡安装或发布。旧G3—G10充分未变证据复用，旧hash FAIL/109许可封存；G11尚未通过。

## 以下为v1.10及更早历史

'''
state = '''# 执行动态文档

文档 v2.33，2026-10-10，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.11、task_model/阶段07；以下v2.32及原历史保字节。

## G11-P110已明确采用，TASK111/R105完整实现卡待转交

用户对唯一G11-P110及已保存Work裁定回复确认，采用生效，原110文档验收保持通过。有限模型数据/受信计算图形/profile-artifact-protocol v2和固定资源256任务/1GiB、原其它隔离、停止证明候选与数值/时钟/短事务条件一起有效；表达能力限制已接受，不默许hash或新页面权限，不将数据到代码边界冒任意脚本原生同步否决。

TASK111/R105已登记并保存完整七节卡，A+沿原110方案窗口，L工作量/高风险复杂跨模块，以完整用户成果合并校验编译、真实renderer、同COMMIT/资格/预览预算、外部控制/恢复、API/可信控件/UI及必要本地部署/Compose和验证收尾。当前待人工转交，未接收/开始，新实际0；主控不接管实现。稳定完整G11再一次新隔离增强终审，未来审计仅计划未派，不逐普通修正加门。

新许可TASK-111-G11-P110-20261010，首读固定12小时总窗43200，metadata7200/offline7200/real14400/cleanup预留1800，各综合real批3600至多6、镜像build3、previewcreate/start14且一时一个/每次60总840+诊断210、Reaper验证批2各1200、模型合成6/Windows OneCall8、PG新容器卷各1/start6、API启动4、主浏览器3各2400、frontend构建3、HTTP总5000/PNG子3000/公开input子300/内部input500。所有失败和普通有据修正计额，完成即止，不消费储备凑数；root批内子attempt冻结源码并计对应类，不把每条shell命令当新root，也不隐性免费重试。

新专PG17缓存cf134…、容器卷retrolume-task-111-g11-v2-pg1及-data、三个新库/专role、127.0.0.1:55451；API18111；preview01—14新前缀retrolume-task-111-g11，镜像三新tag、UID10001/networknone/readonly/capdrop/NNP/privatePID-IPC/1CPU/1GiB/pids256/临时128+32MiB。现名字/卷/端口无冲突，缓存OCI c091及本地PW1.62.1可读、Compose5.5.1只读核可用；不是新产品运行证据，执行前再核真实归属。角色密码限内存/安全stdin或子进程Env，不入argv/日志/源码/证据；不读用户私配。

全部新DB/数据/卷/image/容器停止后保留，不提交DELETE/DROP，不启动旧106/103/100/088/109或用户库，不安装联网/pull/换引擎/新依赖/特权/宿主挂载socket、不真实provider或付费、不Git或发布。保留旧78根/140.297含build30.658/13元/失败UNKNOWN/重叠时间；旧109与110资料剩余封存，不借分类额。旧正常/权限与领域充分未变证据继承，修改后风险与真实v2需定向验证；原G11未通过、不宣STEP或M1/项目。

本批CHG1138—1149，下一CHG1150；采用、输入/资源/预算/窗口和文档回读DocuN/evidence/TASK-111/orchestration-20261010。用户只需转TASK111给原110 A+，回传DocuN/results/TASK-111-result.md；无额外确认/人工开服务。原107独立保持，所有共享状态由主控串行维护。

## 以下为v2.32及更早历史

'''
work111 = f'''# TASK-111 / R-105 G11-P110完整执行授权

{STAMP}，Codex编排Agent。用户明确确认已审G11-P110及Work裁定，有限描述与受信程序、输入/安全承诺和固定资源新基线生效。源110结果4072cfb4…、原待采用裁定466f39b5…保字节，旧109全部根与许可封存。普通字段/布局/数值实现/验证路由由本卡执行者自主，不再次询问采用。

本卡把全部生成/数据边界/renderer/事务资格/预算/外部停止与恢复/API/可访问UI/部署依赖和定向验证合成一个完整成果，A+沿110设计窗口。具体边界/允许文件/精确资源/首次含有据修正预算、合成验证与收尾以完整TASK111和orchestration-20261010为准。未经终审的候选仅可由本卡固定合成许可/隔离harness运行，生产默认能力仍关闭，不设公开fault或通用绕过开关。

采用private PID namespace/init结束组合证明路径，保实际平台与完整对象身份/无逃逸/外部kill-wait-events/EOF/控制者结束和独立终审核适用。缺字段/未知仍不退款不放新session，不为不能读取停后cgroup而新开准备卡，不加privileged或host挂载。准确Decimal格点、明确有限AST数学/步数、最低reserve30、单机监督时钟和短事务纯处理是执行合同的必需细化。

既有合成目标本次全新独占，真实用户资料/库/private配置/provider/费用/安装联网/删除提交/Git/发布不获授权。新角色必要内存口令恢复可在同批按本卡身份进行；所有旧失败、源版本/预算/投入、动作和资源保留，不能用普通修复清账。原G3—G10未改充分证明继承，只做实际影响回归；高风险完整G11稳定后一次新隔离增强终审不取消，本执行者不自签放行。

当前合同完整保存回读待转交，未实际接收或运行；执行者完成整卡或真实停止条件才统一交回，不按模型/字段/页面/普通修复逐次来回。
'''
card = '''# TASK-111 / R-105 — 受信交互HTML完整实现、业务接线与合成验收

## 目标与交付

你继续担任原110方案执行者，在已确认G11-P110边界内一次实现完整成果，卡内连续完成实现、相关验证和有依据的普通修正，完成或遇真实停止条件才统一回传。不是只写renderer、只跑准备或逐接口交回。用户获得“从当前学习答案或教学练习/反馈显式生成→保存→打开→调数字/图形→查资料→停止/回学习→刷新核对”的完整候选链。

交付有限描述校验/编译与固定程序、v2产物同COMMIT/父资格/预览持久预算、真实独立容器Supervisor/Reaper/停止恢复、API007/可信控件与身份守卫、生产自包含镜像/配置/本地服务部署及必要Compose，连同110 M01—M12定向原件和精确收尾。完整结果 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-111-result.md，证据同根DocuN/evidence/TASK-111/，旧结果/证据不改。数学/图形真的在远端重算，不静态写数值或在主UI假更新。

完成标准为方案约定正常/关键拒绝/费用COMMIT/资格/预算/停止恢复/可访问UI与加载身份均有相称有效证据，所有资源收尾，未验证/偏差明确。只报告候选实现与卡内验证，不自签完整G11、B01、SEC003、STEP015/016、M1/项目或发布；稳定后另有一次新隔离增强终审。普通修正不逐次加独审。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model/V4.0/公共AGENTS CHG-0003；公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD及WORK第2/6章合同有效，七锁定指纹项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。同窗未变规则/110 A—D不全文重读，只补本卡、已变采用/正式头段和实际影响源码。需求v1.2、架构v1.11、唯一执行动态v2.33、阶段07。

关联TASK110/R104、108/G11-P、109已封存反证、FR009/SEC003/B01、STEP015/016、原G3—G10/四账/OneCall。用户2026-10-10对具体G11-P110/已保存Work裁定明确“确认”，采用已生效；本卡TASK-111-G11-P110-20261010才是新的精确实现与合成运行许可，不复活109/110。A+强推理，沿原110方案窗口，理由为解析安全/事务/权限/跨进程监督/前后端复杂且高风险，实际身份如实登记，标签不冒型号。本执行不是独立审计，不接管编排，不自行派其它执行窗口。

旧global78非78PASS，109/H0各8/8、build/controller4/4封存、preview4/16名义余额不借；real140.297含build30.658子段、旧13元/所有失败UNKNOWN/时窗/重叠投入保留。新TASK/R和新许可不清旧失败；本卡实际当前0，仅待人工转交。源110结果53624字节/SHA4072cfb433aa22fcf4648aa16fa03031300b746faf4c48050ca4eb3512efb30e；采用范围由TASK-110-work-decision.md置顶及本卡补强，原6982/466f39b5…裁定完整后缀保持。

## 背景与最小充分上下文

109已明确hash提交，旧任意脚本全协议同步Native NavigationGate承诺不可拿网络route/CSP/后置kill冒实现。现在只执行固定项目程序，模型的有限数据没有JS/markup/URL/DOM/工具能力出口；合法描述/输入不得导航/新target/frame，出现这些行为仍缺陷须停，不给hash豁免，不声称能在任意已执行恶意脚本所有浏览器路径前同步取消。旧反证/旧data根因原样保留，不再复跑旧小批。

依次读入口/适用规则、本卡、TASK110采用头与TASK111-work-decision，110 C2—C7/D1—D3作为已读原合同复用，项目正式三文档仅新头/相关G11段，DocuN/evidence/TASK-111/orchestration-20261010/input-manifest.json、resource-mapping.json、verification-budget.json、必要真实接口/迁移/测试。实际改动前核文件差异及调用方，保存pre/hash/有限diff；若相符未变复用，不全仓重审、不重新hash500对象。发生他人修改或新目标路径已有成果先查明，不覆盖。

现backend/app/preview/contracts/supervisor/reaper及deploy/preview/host/wrapper是诊断原型，supervisor硬coded旧permit，不能拿其main或已结束runner直接做生产。生产控制可以复用已核函数原理，在新明确接口/权限下接线；旧as-run、contexts/cache、h0 fixtures和所有旧session原字节只读。没有012新域/新业务/renderer现成实现，不把计划接口当已存在。

已有环境backend/.venv/Scripts/python.exe、frontend/node_modules/锁定React/Playwright等可用；PG缓存pgvector/pgvector镜像index sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，linux/amd64。预览基础OCI manifest c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac在deploy/preview/task109-c01-cache/oci，PW1.62.1本地包在task109-c04-context/attempt-02/vendor/playwright-core。这些只是可读输入/缓存，不是旧执行许可；正式运行依赖复制到deploy/preview/vendor并完整记录来源/许可/校验，生产不import DocuN/外部参考/公共库临时代码。Compose5.5.1已只读核，PG画像ID是index类型，renderer manifest/config分别解释；不假定build metadata有containerimage.config.digest。

## 执行边界与资源

允许backend/app/preview内生产contracts/description/compiler/generation/repository/api/host_policy/supervisor/reaper及必要process/pipe模块，新增backend/migrations/012_html_explanations.sql；必要薄扩展capabilities/contracts/gateway、activities/repository/service/api、service_config/main及worker的profile/结果接线。保原worker/Windows Job/四账/UNKNOWN主权，不重写admit/mark/record/recover或时钟，只实际新增profile/binding/同connection hook及必要资格投影；默认旧序列化不增加None字段。涉及数据资格/次数/取消必须复用现锁序/幂等，不绕原准入。

允许新deploy/preview/renderer-host.cjs、runtime.html/cjs/css、descriptor.schema.json、production Dockerfile/配置/manifest/许可清单和正式vendored同包；不改旧host.cjs/wrapper.html/runtime-bootstrap/h0源码、contexts/cache/as-build旧字节。前端新增src/explanations的Panel/Canvas/typedAPI/intents/contracts/可信参数控件与必要样式，LearningResult/TeachingWorkspace及Exercise/Feedback/ActivityWorkspace仅必要挂载/父回调；不改旧历史UI身份守卫、不扩大资料/PDF来源权限。允许config/activity.example.json和新公开模板、README/deploy/start_local.py及新deploy/compose.local.yml的必要部署接线，不能读取/改用户local配置。

测试可新增backend/tests相关交互域/预算/角色/原子提交/资格/恢复和fixture/task111、frontend/tests/task111的保留式fixture与统一runner；旧测试只必要签名/配置适配，保业务断言及原定向隔离纪律。生产不用test-only传输/故障开关；合成harness仅本卡精确库/role/image/permit、测试进程安全环境注入，不形成公开配置绕过或接受任意代码的路由。完整产物准入签名/审核票据前生产默认HTML关闭，候选可按本卡合成许可验证，不让“审计尚未执行”死锁内部测试。

禁止用户原始需求/公共库/正式DocuS/旧卡报告证据/依赖锁/001—011/无关G3—G10修复，禁止新CEF/Qt/fork/数学库/模型provider/网络安装pull/用户库资料/private配置、真实密钥/付费/新页面系统权限、privileged/SYS_ADMIN/ptrace/hostPID-IPC-network/host bind/socket/预览端口、Git提交推送/发布和数据删除。只在本任务全新专库内无条件ROLLBACK的越权反例允许尝试UPDATE/DELETE等拒绝；不COMMIT破坏任何对象，不用cleanup删除样本。不复制旧失败成新通过，不以版本变化或flag降安全。

协议/语法与旧110一致。描述必须interactive_description.v1，closed枚举/未知或重复键/UTF8/非有限/坏引用/大小/AST依赖失败关闭；8 inputs/32 calculations/256 AST节点深度16、图形合计128点/更新50000步、13有限数学op和reset、规范描述24576/固定HTML65536/产物110592/旧正文131072字节及token4096取原活动更小限不扩大。固定source/hash/CSP脚本hash、文字textContent/Canvas，无eval/Function/string代码、动态markup/URL、任意SVG/图片数据或CSS。Node需全类型和规范字节复核，Map索引不任意对象合并，后端/Node精确一致；结构合法不当数学/概念真实性证明。

控制十进制/范围/格点必须规范string+精确缩放整数/Decimal等价比较，先锁一次跨语言规范/域/舍入和步数扣减；AST有限浮点语义、域/非有限/上界与独立误差明确，不能用二进制舍入伪造格点。先完成整个候选数值/图形再交换，错误保上次完整一致快照；初次失败不ready，非法模型收到仍记真实RECEIVED/费用但无artifact。编译规范化在同COMMIT只做有限纯数据，绝不DB事务内启动/等Docker、网络或渲染；hook异常全rollback/UNKNOWN不重发。hash排自身/会话/未来image以防循环，deployment再bind实际image/来源。

012四表和两NOLOGIN角色内的必要具体列/约束/索引/函数与字段名字可自主细化，必须满足原108 C2与110C4资格/immutable/ACL/锁序/同COMMIT和v2身份，不加第五表/权限域或更旧schema。升级非空旧资料/活动库要保旧行字段和ACL不变，partial/未知schema先拒绝无部分DDL；原APP不能绕producer改artifact预算/资格。public _guard/session/no-store/同源UUID和分页保持，所有start/input/frame/public serialize资格核与准确cache-before-query race覆盖；父/来源/记忆失效、取消与迟到都不能复活PNG/输入/正文/引用。停止同应用身份可请求，不把HTTP成功称树空。

预览三次180秒/次≤60与模型时间账分开。最小reserve固定30秒，小于30则预扣前拒绝且不扣次数；t0在reserve前固定，准备/事务/启动均计D=t0+reserve，ready≤t0+8且≤D-10，input至D-10关闭；2秒软停止后外部精确kill，确认不延D。失败不返次数，配置/刷新/新owner不reset；只有确认未启动或物理停止证据齐才能结preview实耗/退未用秒，未知全reserve保持、后续start封闭，不触模型请求/工具/费用/原生时间退款权。

采用private PID namespace/init结束组合证明：真实平台/kernel来源与机制适用、init=1/namespace/出生、所有工作在该namespace及子树、无祖先/共享namespace迁移途径、精确CID/image/nonce外部kill与init退出/wait/events、无restart、拥有的CLI/管道/监督者结束，全部互相绑定。源依据已纳入110Work和stop-proof-candidate.json。主控/旧审从未签109完整树空；本卡新候选正常/故障/恢复和终审核适用。Stopped/Pid0、kill0、DB状态或源码单独不充分；不强制停后host cgroup直接可读为唯一证据，更不先反复开额外准备批。缺组合字段unknown/不退额/不放新start，不加特权，不宣cgroup目录或内存已经完全释放。

Reaper先READY且create意图/唯一name/image/nonce归属登记后才create；cid回包后确认bind和固定D再start，create回包丢失只找回同一自有对象不二次create。parent死亡在CID未知阶段仍能按预登记意图有界找回清理或明确unknown；不能泄漏孤儿后说无CID无法处理。绑定后deadline/身份不后移。Supervisor/Reaper共享宿主单调源，Node时钟/console/postMessage/读值不授权、不延限或退款；持久owner/boot不同实例不直接比较旧mono值。重启只读核/精确救援，不租约抢占旧运行。PID出生读取access_denied等是未知，不能None就说死或杀别人的进程。不得全局taskkill/stopdaemon。

独占新PG镜像cf134…，容器retrolume-task-111-g11-v2-pg1/卷同名-data，CPU1/512MiB/pids128/bridge只127.0.0.1:55451映射5432。三个本卡库retrolume_task111_main/upgrade/fault及角色retrolume_task111_admin/app/denied，允许新域DDL/grants/自身角色有据内存密码重置，不触用户或旧库/角色；PG镜像默认数据库身份按实核，不把renderer UID约束套PG初始化。密码/DSN只内存安全stdin/限定子进程Env，禁止argv/日志/源码/evidence/会话泄露和输出全Env。

preview固定新前缀retrolume-task-111-g11-preview-01至14，不reuse或start旧109/100/088/103/106；每次nonce独立，同task/permit/owner/birth、实际image/source/policy，一次create/start。UID10001/GID10001、networknone/readonly/capdropALL/NNP/原seccomp/privatePID-IPC/CPU1/SHM64MiB/1024MiB等swap/pids256/init/restartno，临时/tmp128MiB/home32MiB同uidgid/nosuid-nodev-noexec/私有0700及原安全HOME/XDG用途，不读host私配或加挂载/端口/容量。三新renderer tag retrolume-task-111-g11-renderer:v2-01/02/03，对应实image manifest/config；新输入字节与old cache/image分型绑定，旧tag/image/source不覆盖。

CPU服务API仅127.0.0.1:18111，主browser用既有锁定本地依赖/无真实资料。Compose同一次成果落实PG依赖和renderer构建入口：使用项目正式compose.local.yml的本卡synthetic override独占name/volume/port/密码环境，或等价明确profile；production用户数据库仅准备配置不启动。preview必须外部监督按预算动态创建，不能compose up常驻renderer绕次数；不把backend迁容器加Docker socket，不在本卡安装Linux/Nginx或公开部署。Compose身份/最终配置只保存脱敏白名单，不把口令展开落盘。

新首次读卡即单调固化43200秒总窗，metadata≤7200/offline≤7200/real总≤14400/cleanup独立预留≤1800；换日/窗口/模型不重置，任一更早子截止优先。真实综合批最多6，每批≤3600，首触真实预检前计；每shell或普通step不是新批，但所有子attempt/源修改/资源/发送都原样计。首次完整组合与最多两次有据相关修正优先，额外未用批只确有本卡缺口才用，不用满凑数。批内普通修正可继续，先停读取改动源的自有服务/容器并留旧as-run/hash/原错误，再冻结新差异进入子attempt，外层截止不延；不得未记账隐性重试。

上限包含首次/失败/修正：build3各≤600秒；previewcreate/start14且同时1，各60执行+15停止诊断，总840/210，Reaper验证批最多2各1200包含1050上界和150收尾余量；PG容器卷各1/start6、API启动4、main browser3各2400；合成模型4基线+2有据修正=6次、真实Windows OneCall会话≤8，provider/费用0；frontend typecheck/build≤3批、offline关联批≤6。HTTP总5000，其中公开PNG_GET≤3000、公开input≤300，内部pipeinput≤500；Nodeframe3fps/60秒/14容器理论2520包在限内、单帧524288且只最新加一在途。检查范围由实际diff选，不默认全仓。任何上限/同因两次有据修正仍败/根因不稳/新方案权限即停相关部分并完成不受阻成果，不暗开第7批或第15preview。

## 验证、证据与审计关系

先完整准备：确认v2接线/生成父域/规范数字与两处校验/可信sink/pipe字段、所有真实SDK前置与身份、预算与资源树、实际Docker image投影/compose/PG credential/Windows兼容loopFactory、TreeProof收据，制作唯一预算runner和as-run绑定。充分已知错误用保存原件与离线解析核，不重复109/meta小批或要求用户开Docker。第一组合真实批将新schema/renderer/身份、正常交互/停止就绪一起取得，不单独退回一个准备子事实。

以110 D2 M01—M12为必需矩阵，正常机械能m2/h3=58.8、h0/m0为0；二项n3/k2/p0.5=0.375及21柱上界/端点、非整数/坏关系拒绝，独立手算误差1e-9，实际remote ACK/文本/图形几何/来源并列。scope拒绝32类定向坏描述大部分offline/无容器；至少非法模型响应一项走真实Windows OneCall+替身+PG，收到费用事实无artifact。有限合法字符串XSS/脚本闭合标签必须普通文本真实显示，不先删才通过；无危险sink、image/SVG/CSS/URL/任意code字段，重复杂描50000步上界和域错保完整旧视图。

实际v2 PG/HTTP验证合格RECEIVED/正文/artifact/terminal同COMMIT、强制hook异常全rollback、同key至多一发送/异输入409、丢回包GET/UNKNOWN不重发、app/public权限拒绝、非空升级/坏schema、旧model/tool/学习教学的具体被影响入口。DSN用RETROLUME_INTERACTIVE_TEST_DATABASE_URL或本卡明确变量，缺则显式skip且此目标未跑不冒通过，绝不fallback用户DSN。每例synthetic ID定向隔离/保留，旧分页无空库假设；旧PG tests若会提交DELETE不能直接跑，按同有效行为用本卡保留式夹具补证并登记，不能弱化正确业务断言或复制SQL字符串/mock冒事务。所有原失败原件不可覆盖。

正常UI两会话尽量复用完成参数/图形/键盘可访问/owner与seq/引用、刷新只读/同键核对、迟到PNG+引用/切scope/activity/隐藏/卸载清空。缓存候选帧后公开资格查询前准确barrier提交失效/取消，后释放必须拒绝；合法检查后在途边界如实，不将delay放在已序列化后假覆盖。独立OOPIF事件和完整URL/fragment/loader/document/target证明合法描述初始化后不导航/增frame，原自由JS输入在本生产数据边界前拒，不再执行旧hash代码要求原生取消；任何合法输入导致提交即FAIL，缺观察UNKNOWN，不删场景造绿。

12基线preview用途按正常N1/N2、资格race、取消刷新/预算、renderer忙死、browser/Node忙死、Supervisor死亡、Reaper死亡、create回包丢失、控制失联、pipe破坏、硬截止冻结；允许最多2与实际修正直接相关重测总14，不按每个断言起容器。每preview最多8个需真实2秒的动作，ready8+动作16+采集16+停止10=50小于60；非动态校验不虚耗2秒，不能9项至少18秒塞15秒。故障只隔离fixture/programvariant，独立hash，不公共fault开关，不把故障版签生产导航安全。

停请求/返学/隐藏失联/预算deadline/忙死/两监督者故障/控制不可达，逐精确对象核外部停止、任务树组合、额度结算/未确认保留/重启救援/无新start。控制不可达试样最后由本卡独立获准验收控制者仅清本CID，不停daemon或其他容器。正常及停树证据不齐的条件，不给退款/产品验证票据。旧四账/Windows Job充分未变证据复用，不重复跨代次旧大套；受新record/profile/资格/共享认证的真实影响定向回归，说明用例ID和为什么。

保存每批真实command参数脱敏、exit/时钟/失败/源码pre-diff-post、加载hash/modelprofile/template-policy/schema/image/platform来源、角色catalog/ACL、SQL/HTTP/pipe/cache-barrier/Frame原件、权限与预算/停止收据和资源表。as-run与final不同的测试按真实hash分级，非最后字节的证据只在明确差异仍适用时继承；最末产品修正应在保留预算内相关复检，不只build通过就签浏览器。结束停止所有本卡自有PG/app/browser/preview/helper并核端口/身份/EOF，保全部新旧数据与image；没有本卡证据可推别人的资源已停止。

运行许可仅合成测试。用户HTML生成/预览默认缺最终manifest/合格证据及独审裁定即关闭，合成scope经过本卡harness验证不等于用户放行；不能用“没有审计票据”阻塞这张卡自己采候选原件，也不能把candidate flag留作通用生产绕过。集中独立审计归稳定完整G11父成果，新隔离未参与110/111/无实现聊天的A+，不沿本窗口自签、不减门、不每个普通修正重审。Card完成后交编排回收，新审计尚未派。

## 停止与回传

有据普通修正连续在本卡落实、相关复验与完整收尾，不因为一个field/fixture/页面中间步骤就回传。不得额外依赖/Git/特权/外网或扩大功能；若确需第五表/新角色权域/新主API语义等，先保不受阻成果交精确差异。关键方案推翻/同因两修仍失败/根因不稳/任一额度或总截止到达时停止受影响动作，保护旧结果和实际剩余，不能换模型/日期重置。

完整结果写DocuN/results/TASK-111-result.md，先结论、完成边界/实际字段签名/API/文件差异与证据，再110矩阵逐项真实通过/失败/继承/skip/not_run、失败修正/投入/资源/权限、停止/退款边界、未验证风险/偏差、正式文档建议与必要人工/下一步。保存可读后只回复一句结论与结果完整绝对路径，不填编排最终验收、不宣STEP/M1/项目或运行用户数据。

## 必要人工与待同步信息

用户只需转交本卡并带回结果路径，无需开服务/贴密钥或再批准普通参数。正式DocuS/共享编号/总状态/变更账仅主控串行维护，执行者给实际字段、流程、接口/权限/资源/配置和README差异建议，不自更新正式文档。错误经验只提已经解决、根因确认且实际验证的可复用候选，不占共享ERR号或写公共库。已保存但用户或接收者不能访问须说明真实保存和必要正文，不能虚称未保存或多建同义状态账。
'''
prefixes = {managed[0]: work110, managed[1]: requirements, managed[2]: arch, managed[3]: state}
for relative, prefix in prefixes.items():
    assert "*" not in prefix and "|" not in prefix and (ROOT / relative).read_bytes() == old[relative]
    (ROOT / relative).write_bytes(prefix.encode("utf-8") + old[relative])
for relative, text in {"DocuN/results/TASK-111-work-decision.md": work111, "DocuN/tasks/TASK-111.md": card}.items():
    assert not (ROOT / relative).exists() and "*" not in text and "|" not in text
    (ROOT / relative).write_text(text, encoding="utf-8")
save_json(AREA / "window-assignment.json", {"TASK": "TASK-111", "R": "R-105", "resource": "A+强推理", "window": "沿原110方案窗口", "why": "同一完整成果连续性，解析/SQL/权限/进程/UI跨模块高风险", "dispatch": "待转交", "received": False, "started": False, "new_used": 0, "independent_final": "稳定G11后新隔离A+，未占/未派", "old109": "继续封存"})
changes = [(1138, managed[0], "用户确认G11-P110/主控条件采用生效，原请求保历史、不恢复109许可。"), (1139, managed[1], "v1.2固化有限真实交互与新数据/代码安全实现边界，31项Must/原文保字节。"), (1140, managed[2], "v1.11已采用计划/资源/停止/生产部署，尚未实现或验证。"), (1141, managed[3], "v2.33登记111/R105完整实施待转交，新明确预算和资源、旧78账保留。"), (1142, "DocuN/results/TASK-111-work-decision.md", "G11完整执行、细化条件、合成范围和集中审计权登记。"), (1143, "DocuN/tasks/TASK-111.md", "完整七节一次实现接线/定向验证/有据修正/收尾，不按普通步骤碎卡。"), (1144, "DocuN/evidence/TASK-111/orchestration-20261010/input-manifest.json", "新鲜最小直接源/迁移、规则、旧缓存和新路径不存在身份绑定。"), (1145, "DocuN/evidence/TASK-111/orchestration-20261010/verification-budget.json", "新12小时/综合批/资源/类次数含失败修正，旧额度不返，不实际运行。"), (1146, "DocuN/evidence/TASK-111/orchestration-20261010/resource-mapping.json", "唯一新专库/role/容器卷/port/image出处、vendor复制和Compose身份。"), (1147, "DocuN/evidence/TASK-111/orchestration-20261010/window-assignment.json", "A+沿110原窗口待人工转交，未来独审仅计划。"), (1148, "DocuN/evidence/TASK-111/orchestration-20261010/adoption-receipt.json", "记录用户确认真实来源与原未采用范围hash，非回填批准时刻或新运行证据。"), (1149, "DocuN/evidence/TASK-111/orchestration-20261010/delivery-proof.json", "一次完整路径/预算/采用/历史/源回读，主控产品和资源启动0。")]
addition = "\n" + "\n\n".join(f"- CHG-{number:04d}，{STAMP}，Codex编排Agent，{relative}。{reason}" for number, relative, reason in changes) + "\n"
assert "*" not in addition and (ROOT / managed[4]).read_bytes() == old[managed[4]]
(ROOT / managed[4]).write_bytes(old[managed[4]] + addition.encode("utf-8"))
checks = {}
for relative, prefix in prefixes.items():
    assert (ROOT / relative).read_bytes() == prefix.encode("utf-8") + old[relative]
    checks[relative] = {"identity": identity(ROOT / relative), "old_suffix_exact": True}
assert report.read_bytes() == report_bytes and identity(ROOT / "DocuS/原始需求文档.MD") == original_req
assert all(identity(Path(row["path"])) == row for row in source_ids)
task_text = (ROOT / "DocuN/tasks/TASK-111.md").read_text(encoding="utf-8")
assert all(header in task_text for header in ["目标与交付", "项目、规则与接收安排", "背景与最小充分上下文", "执行边界与资源", "验证、证据与审计关系", "停止与回传"])
assert 8 + 16 + 16 + 10 < budget["seconds"]["preview_each"]
assert budget["counts"]["preview_starts"] * (60 + 15) + 150 <= budget["seconds"]["preview_reaper_batch"]
assert budget["counts"]["preview_starts"] * 60 * 3 <= budget["counts"]["public_PNG_gets_subset"]
save_json(AREA / "delivery-proof.json", {"TASK": "TASK-111", "R": "R-105", "at": STAMP, "checks": checks, "task_card": identity(ROOT / "DocuN/tasks/TASK-111.md"), "work": identity(ROOT / "DocuN/results/TASK-111-work-decision.md"), "original_user_text_unmodified": True, "110_result_and_all_read_source_unmodified": True, "old_shared_histories_preserved": True, "canonical_adoption_scope_true": True, "single_current_full_card": True, "budget_arithmetic_pass": True, "dispatch": "待转交", "new_used": 0, "main_compile_test_build_start": 0, "readback": "一次文档一致性通过，非产品行为通过"})
print(json.dumps({"saved": True, "adopted": "G11-P110", "card": str(ROOT / "DocuN/tasks/TASK-111.md"), "window": "A+沿原110方案窗口", "versions": {"requirements": "1.2", "architecture": "1.11", "state": "2.33", "last_CHG": "1149"}, "new_used": 0, "main_product_runs": 0}, ensure_ascii=False))
