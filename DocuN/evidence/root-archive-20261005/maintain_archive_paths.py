"""用户授权的归档路径维护；只做文件、语法和 Git 忽略规则检查。"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path("D:/shspic/project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/archives/legacy-roots-20261005"
EVID = ROOT / "DocuN/evidence/root-archive-20261005"
REPORT = ROOT / "DocuN/results/root-archive-20261005-result.md"
NAMES = ("docu", "evidence", "Ndocu", "spikes")
STATE = "DocuS/执行动态文档.MD"
ARCH = "DocuS/架构动态文档.MD"
LOG = "DocuS/文档变更记录.MD"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now().astimezone().isoformat()


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path):
    return path.relative_to(ROOT).as_posix()


def commands(args, **kwargs):
    completed = subprocess.run(args, cwd=ROOT, capture_output=True, check=False, timeout=30, **kwargs)
    if completed.returncode:
        raise RuntimeError(f"元数据/语法检查失败：{args[0]} exit={completed.returncode}")
    return completed


def prepare():
    if (EVID / "maintenance-ready.json").exists():
        raise RuntimeError("维护已完成；不覆盖已有证据")
    if not all((ROOT / name).is_dir() for name in NAMES):
        raise RuntimeError("源目录状态与准备阶段不符")
    manifest = json.loads((BASE / "manifest.json").read_text(encoding="utf-8-sig"))
    if [item["name"] for item in manifest["records"]] != list(NAMES):
        raise RuntimeError("归档清单目录集合不符")
    total = sum(len(item["files"]) for item in manifest["records"])
    total_bytes = sum(f["bytes"] for item in manifest["records"] for f in item["files"])
    original_requirement = ROOT / "DocuS/原始需求文档.MD"
    requirement_sha = sha(original_requirement.read_bytes())
    ignored = commands(["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", *NAMES])
    old_ignored = [p.decode("utf-8") for p in ignored.stdout.split(b"\0") if p]
    owned = []
    changes = []

    def write(path, new, reason, previous=None):
        path = ROOT / path if isinstance(path, str) else path
        before = path.read_bytes() if path.exists() else None
        if previous is not None and before != previous:
            raise RuntimeError("写入前发生并行变化：" + relative(path))
        if before == new:
            raise RuntimeError("预期变更未发生：" + relative(path))
        backup = EVID / "before" / relative(path)
        if before is not None:
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists():
                raise RuntimeError("不覆盖维护前副本")
            backup.write_bytes(before)
        path.parent.mkdir(parents=True, exist_ok=True)
        if (path.read_bytes() if path.exists() else None) != before:
            raise RuntimeError("写入瞬间发生并行变化：" + relative(path))
        path.write_bytes(new)
        owned.append({"path": relative(path), "sha256": sha(new)})
        changes.append({"path": relative(path), "before_sha256": sha(before) if before is not None else None,
                        "after_sha256": sha(new), "reason": reason})
        diff = "".join(difflib.unified_diff(
            (before or b"").decode("utf-8-sig").splitlines(keepends=True),
            new.decode("utf-8-sig").splitlines(keepends=True),
            fromfile="before/" + relative(path), tofile="after/" + relative(path)))
        out = EVID / "diffs" / (relative(path).replace("/", "__") + ".diff")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(diff, encoding="utf-8")

    def replace(path, old, new, reason):
        data = (ROOT / path).read_bytes()
        a, b = old.encode("utf-8"), new.encode("utf-8")
        if data.count(a) == 0 and b"\r\n" in a:
            a, b = a.replace(b"\r\n", b"\n"), b.replace(b"\r\n", b"\n")
        if data.count(a) != 1:
            raise RuntimeError("原文匹配非唯一：" + path)
        write(path, data.replace(a, b), reason, data)

    ignore = ROOT / ".gitignore"
    old_ignore = ignore.read_bytes()
    added_ignore = "\n# 2026-10-05 归档后继续保护旧证据中的合成凭据；旧规则保留\n" + "\n".join([
        "/DocuN/archives/legacy-roots-20261005/Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json",
        "/DocuN/archives/legacy-roots-20261005/Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json",
        "/DocuN/archives/legacy-roots-20261005/Ndocu/evidence/task-079/",
    ]) + "\n"
    write(".gitignore", old_ignore + added_ignore.encode("utf-8"), "迁移旧证据的精确凭据忽略规则", old_ignore)
    mapped_ignored = ["DocuN/archives/legacy-roots-20261005/" + p for p in old_ignored]
    check = commands(["git", "check-ignore", "--stdin", "-z"], input=("\0".join(mapped_ignored) + "\0").encode("utf-8"))
    confirmed = {p.decode("utf-8") for p in check.stdout.split(b"\0") if p}
    if set(mapped_ignored) != confirmed:
        raise RuntimeError("归档后有原忽略文件失去保护")
    save_json(EVID / "git-ignore-verification.json", {
        "result": "PASS", "old_ignored_files": len(old_ignored), "archive_ignored_files": len(confirmed),
        "missing": [], "git_mutations": "仅.gitignore文件；无init/config/add/commit等Git写操作"})

    asset_pairs = [
        ("Ndocu/evidence/task-083/d3-repair-11/contracts.py", "backend/tests/fixtures/task083/archived_d3_control/contracts.py"),
        ("Ndocu/evidence/task-083/d3-repair-11/controlled_child.py", "backend/tests/fixtures/task083/archived_d3_control/controlled_child.py"),
        ("Ndocu/evidence/task-083/d3-repair-11/runner.py", "backend/tests/fixtures/task083/archived_d3_control/runner.py"),
        ("Ndocu/evidence/task-063/task063-resume1-20260921T0905Z/task057-db-schema-inventory-after-migration.json",
         "tests/fixtures/task063/task057-db-schema-inventory-after-migration.json"),
    ]
    assets = []
    for source, target in asset_pairs:
        original = BASE / source
        data = original.read_bytes()
        if (ROOT / target).exists():
            raise RuntimeError("正式夹具目标已存在，不能覆盖：" + target)
        write(target, data, "正式测试所需旧辅助代码或样本原字节复制；不恢复历史运行许可")
        if sha(data) != sha((ROOT / target).read_bytes()):
            raise RuntimeError("夹具字节不一致")
        assets.append({"source": relative(original), "target": target, "sha256": sha(data), "byte_equal": True})
    fixture_guide = """# D3 回归测试夹具来源

本目录三份 Python 文件原字节来自已归档的 TASK-083 d3-repair-11 证据，仅供 backend/tests/test_d3_runner_control.py 的既有替身、导入无资源副作用及重试判断检查使用。逐文件 SHA-256 见 DocuN/evidence/root-archive-20261005/asset-relocations.json。

runner.py 保留原文、原资源身份与原预算，作为回归被测输入。它不是当前资源执行入口，不准因复制而重启历史容器或重新使用旧运行许可。其他已完结 TASK-083—090 runner 同样只作历史资料；需要重新执行时应由新有效合同单独处理实际路径与权限。

归档原件在 D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/Ndocu/evidence/task-083/d3-repair-11/，没有改写。
"""
    write("backend/tests/fixtures/task083/archived_d3_control/README.md", fixture_guide.encode("utf-8"), "说明正式回归输入的来源与旧运行许可边界")
    save_json(EVID / "asset-relocations.json", assets)
    python_test = "backend/tests/test_d3_runner_control.py"
    old_test = (ROOT / python_test).read_bytes()
    replace(python_test, 'str(ROOT/"Ndocu/evidence/task-083/d3-repair-11")',
            'str(ROOT/"backend/tests/fixtures/task083/archived_d3_control")', "只改测试导入辅助文件目录")
    reconstructed = (ROOT / python_test).read_bytes().replace(
        b'backend/tests/fixtures/task083/archived_d3_control', b'Ndocu/evidence/task-083/d3-repair-11')
    if reconstructed != old_test:
        raise RuntimeError("Python测试存在目录之外的改动")
    replace("tests/task064_candidate_constraints.test.mjs",
            'dirname(fileURLToPath(import.meta.url)), "..", "Ndocu", "evidence", "task-063",\r\n  "task063-resume1-20260921T0905Z", "task057-db-schema-inventory-after-migration.json",',
            'dirname(fileURLToPath(import.meta.url)), "fixtures", "task063",\r\n  "task057-db-schema-inventory-after-migration.json",',
            "只改原始结构JSON样本读取路径")
    replace("tests/task054_pdf_materials_integration.mjs",
            'join(root, "Ndocu", "evidence", "task057-runs",', 'join(root, "DocuN", "evidence", "task057-runs",',
            "新生成的测试输出使用DocuN，避免恢复已移除根目录")

    entry_old = "新执行材料进入 DocuN 的 tasks、results、evidence、spikes、handoffs、archives，有内容才创建。已有 TASK-001—090 的卡、结果、证据及旧实验继续位于 Ndocu 或原已登记位置，未验收同边界续作沿原路径，不复制或强搬证据。新卡自 TASK-091 使用 DocuN，编号连续。\r\n\r\n旧 docu 英文文档只保留只读迁移导航。docu/AGENTS.MD、WORK.MD 的原正文已归档在 DocuN/archives/legacy-project-rules-v3-20260930，不作为当前规则。历史证据记载的旧路径和规则时点不追改。"
    entry_new = "新执行材料进入 DocuN 的 tasks、results、evidence、spikes、handoffs、archives，有内容才创建。新卡自 TASK-091 使用 DocuN，编号连续。\r\n\r\n用户2026-10-05明确批准归档并移除四个旧根目录。TASK-001—090 及旧导航、证据和实验的原字节统一保留在 DocuN/archives/legacy-roots-20261005/ 的 docu、evidence、Ndocu、spikes 同名子目录。遇历史路径时只将根前缀替换为此归档位置，余下相对路径不变；完整清单与导航见该目录 README.md 和 manifest.json。历史报告、路径、预算与验收原文不改写。\r\n\r\n旧任务若需获准续作仍沿用原 TASK/R 和有效证据，新产物使用 DocuN，不得改写归档原件或重新创建四个旧根目录。已完结历史 runner 的复制或路径可读不恢复其执行许可。旧 docu 英文导航随本次归档保留；AGENTS.MD、WORK.MD 原正文仍位于 DocuN/archives/legacy-project-rules-v3-20260930，不作为当前规则。"
    replace("AGENTS.md", entry_old, entry_new, "登记用户特定归档授权及当前路径映射")
    replace("README.md", "`evidence/task-041/` 保留脱敏的最终 hash、执行导航和限定独立审查，适用范围见其中说明。",
            "[TASK-041 归档证据](D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/evidence/task-041/) 保留脱敏的最终 hash、执行导航和限定独立审查，适用范围见其中说明。",
            "修复当前工程说明的历史证据导航")
    readme = ROOT / "README.md"
    before_readme = readme.read_bytes()
    # README的两处变更合并到首次修改证据，不覆盖首次before。
    addition = "\n## 文档与历史归档\n\n正式需求、架构和唯一执行状态在 DocuS；当前任务卡、结果、证据及新实验在 DocuN。旧 docu、evidence、Ndocu、spikes 已统一归档；旧路径的对应位置、恢复方法与逐文件清单见[归档说明](D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/README.md)。归档不改变任务编号、历史预算或产品验收状态。\n"
    readme.write_bytes(before_readme + addition.encode("utf-8"))
    for record in owned:
        if record["path"] == "README.md":
            record["sha256"] = sha(readme.read_bytes())
    for record in changes:
        if record["path"] == "README.md":
            record["after_sha256"] = sha(readme.read_bytes())
    old_readme = (EVID / "before/README.md").read_bytes()
    (EVID / "diffs/README.md.diff").write_text("".join(difflib.unified_diff(
        old_readme.decode("utf-8-sig").splitlines(keepends=True), readme.read_text(encoding="utf-8-sig").splitlines(keepends=True),
        fromfile="before/README.md", tofile="after/README.md")), encoding="utf-8")

    guide = f"""# 2026-10-05 旧根目录归档

用户批准完整归档并移除旧根目录。本归档共 {total} 个文件、{total_bytes} 字节，四个子目录保持原始层级、全部文件原字节及空目录。manifest.json 是复制时逐文件 SHA-256 清单；移除后的核验见 [移除记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/root-archive-20261005/removal-verification.json)。当前状态仍以 DocuS/执行动态文档.MD 为唯一权威。

历史路径只替换以下前缀，余下路径不变。

D:/shspic/project_NO3_RetroLume-agent/docu/ 对应 [docu](D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/docu/)，10个旧导航文件。当前正式文档在 DocuS。

D:/shspic/project_NO3_RetroLume-agent/evidence/ 对应 [evidence](D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/evidence/)，12个早期工程与审查文件。

D:/shspic/project_NO3_RetroLume-agent/Ndocu/ 对应 [Ndocu](D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/Ndocu/)，1560个历史任务、结果、证据和交接文件。

D:/shspic/project_NO3_RetroLume-agent/spikes/ 对应 [spikes](D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/spikes/)，143个早期实验文件。后续实验进入 DocuN/spikes。

历史报告与原日志里的路径及状态没有追改；遇旧绝对路径或旧链接请按上述映射定位。旧任务、失败次数、时间费用、有效证据和许可终点不因归档清零。旧runner及早期spike仅供历史阅读，重新运行需要当时之外的有效授权和当前路径核对。

两个现有回归测试所需三份D3辅助代码与一份结构JSON样本已原字节复制到正式测试夹具目录，来源与hash见 DocuN/evidence/root-archive-20261005/asset-relocations.json。旧证据中原本被Git排除的合成凭据继续排除，原件仅保留在本机，不因归档而公开。

如确需恢复旧目录，先确认项目根下对应同名目录不存在，再将本归档内同名子目录复制回项目根，并按manifest核对文件与hash；不能覆盖新文件。正常接续使用当前映射，无需恢复旧根目录。归档原件不要原地修改。
"""
    write(BASE / "README.md", guide.encode("utf-8"), "归档原件外新增完整前缀导航、证据与恢复说明")
    path_map = {"at": now(), "archive_root": str(BASE),
                "prefix_mappings": [{"old": str(ROOT / name), "current": str(BASE / name)} for name in NAMES],
                "test_assets": assets, "history_bytes_rewritten": False,
                "inactive_historical_fixtures": ["backend/tests/fixtures/task083/launcher_control.py",
                    "backend/tests/fixtures/task085", "backend/tests/fixtures/task088", "backend/tests/fixtures/task089",
                    "backend/tests/fixtures/task090", "backend/tests/fixtures/task083/archived_d3_control/runner.py"],
                "legacy_fixture_policy": "保留历史代码及旧预算，未启用；需要重跑时由新有效合同处理路径，当前测试导入不触资源"}
    write(BASE / "current-reference-map.json", (json.dumps(path_map, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), "辅助当前路径查找；不建立第二份项目状态")
    state_old = (ROOT / STATE).read_bytes()
    arch_old = (ROOT / ARCH).read_bytes()
    state_intro = """# 执行动态文档

文档 v2.03，2026-10-05，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.81，task_model/阶段07。下面v2.02及全部历史原字节保留。

## 用户授权的旧根目录归档

用户明确同意完整归档、更新当前引用后移除 docu、evidence、Ndocu、spikes。1725文件/29400868字节完整复制到 DocuN/archives/legacy-roots-20261005/ 同名子目录，逐文件SHA-256、目录清单与源变化核对一致。归档和引用维护完成，四个旧根目录移除待最终核验；完成结果见 DocuN/results/root-archive-20261005-result.md。

旧路径仅将项目根下四个目录前缀替换为该归档对应子目录，其余路径不变；完整映射见归档README和manifest。早期TASK001—090卡/结果/证据、旧实验及失败记录不追改，当前材料继续用DocuN。两个回归测试所需辅助文件和样本原字节复制到正式tests目录，默认新证据输出改DocuN；旧凭据Git忽略规则同步。旧runner许可未恢复，不重开旧验收，不改TASK/R/预算。

本次仅用户指定目录与引用维护，编排未接管TASK100或运行产品/PG/Job/浏览器/build，也未Git提交。100的在途/结果和预算按原卡及实际回传核证，本次不重新判断，继续使用现有DocuN路径。公共规则仍锁定V4.0/CHG0003，用户原始需求原字节保持。后续项目阶段、未验证项和集中独立审计安排均沿用下方既有状态。

本批CHG范围及下一号见下面归档完成登记；共享账仅本文件维护。

## 以下为v2.02及更早历史

"""
    arch_intro = """# 架构动态文档

文档 v0.81，2026-10-05，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.03。仅维护已获用户批准的历史存储路径；G8及既有业务切片的状态和合同不因归档改变。下面v0.80及全部历史原字节保留。

## 历史材料存储与正式测试输入

FILE布局将原根docu/evidence/Ndocu/spikes归档到 DocuN/archives/legacy-roots-20261005/ 四个同名子目录。当前正式文档仍在DocuS，新增任务/结果/证据/实验仍在DocuN，产品与部署仍在backend/frontend/config/deploy。归档切换在实施中，完整原件及每文件hash已核一致，最终状态以唯一执行动态与移除记录为准。

当前D3控制回归所需contracts/controlled_child/runner和候选约束回归所需原始结构JSON保存在正式测试夹具目录；测试只改导入/读取路径，旧实验与证据不再承担当前测试文件查找入口。复制的runner只作回归输入，旧资源许可与预算不被重新启用。旧报告中的路径按统一前缀映射读取，原字节与既有证据适用范围不变。

未修改产品写路径、HTTP/worker/transport、持久模型或依赖锁；没有新DB迁移/服务配置/部署授权。TASK100继续沿有效卡完成G8，Compose/Linux/Nginx/Git与其他Must的原安排保持，未宣告任何新业务验收。

## 以下为v0.80及更早历史

"""
    write(ARCH, arch_intro.encode("utf-8") + arch_old, "v0.81仅同步历史存储与正式测试输入边界", arch_old)
    write(STATE, state_intro.encode("utf-8") + state_old, "v2.03登记用户特定授权与当前路径；原TASK100状态保留", state_old)

    syntax = []
    for filename in [python_test, *[target for _, target in asset_pairs if target.endswith(".py")]]:
        ast.parse((ROOT / filename).read_text(encoding="utf-8-sig"), filename=filename)
        syntax.append({"path": filename, "check": "ast.parse", "result": "PASS", "executed": False})
    for filename in ["tests/task064_candidate_constraints.test.mjs", "tests/task054_pdf_materials_integration.mjs"]:
        commands(["node", "--check", filename])
        syntax.append({"path": filename, "check": "node --check", "exit": 0, "executed": False})
    parsed = json.loads((ROOT / asset_pairs[-1][1]).read_text(encoding="utf-8-sig"))
    if not isinstance(parsed.get("constraints"), list):
        raise RuntimeError("迁移结构样本缺constraints")
    # 当前测试导入目录包含其全部直接同目录依赖；不导入或执行历史runner。
    fixture = ROOT / "backend/tests/fixtures/task083/archived_d3_control"
    for filename in ("runner.py", "contracts.py", "controlled_child.py"):
        if not (fixture / filename).is_file():
            raise RuntimeError("测试导入闭包缺文件")
    if sha(original_requirement.read_bytes()) != requirement_sha:
        raise RuntimeError("用户原始需求发生变化")
    rules = json.loads((ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json").read_text(encoding="utf-8-sig"))
    rule_checks = [{"path": item["relative_path"], "matches_locked": sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"]} for item in rules]
    verification = {"at": now(), "result": "PASS", "syntax_checks": syntax, "assets_byte_equal": True,
                    "test_import_closure_complete": True, "old_ignored_files_still_ignored": len(confirmed),
                    "original_requirement_sha256": requirement_sha, "original_requirement_unchanged": True,
                    "public_rules": rule_checks, "runtime_tests_run": False, "archive_file_count": total,
                    "archive_bytes": total_bytes, "historical_refs_policy": "原报告与完结runner不追改；有效读取前缀统一映射"}
    save_json(EVID / "maintenance-verification.json", verification)
    save_json(EVID / "changes.json", changes)
    report = f"""# 旧根目录归档与引用维护

用户2026-10-05明确授权；已完整复制并核对{total}文件/{total_bytes}字节。归档在 D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/，四个同名子目录原字节和结构保留。原根目录移除待最终核验。

当前入口、README、Git忽略规则、两份测试读取/导入和一份测试新输出路径已更新；三份D3辅助代码与一份结构JSON样本原字节复制到正式测试目录。历史报告和旧runner原文不改，旧路径按归档README映射；历史运行许可不恢复。{len(confirmed)}个原先被Git忽略的文件在归档后继续被忽略，无Git暂存或提交。

验证仅文件SHA-256/目录清单、四份Python AST、两份JavaScript node --check、JSON结构与当前路径检查；没有运行unittest、业务测试、PG/Job/浏览器/build或启动服务。用户原始需求未动，TASK100执行文件与预算未动，业务源码/迁移/配置/依赖锁没有本次改动。原路径的历史链接不批量改写，归档提供映射导航。

维护前副本、完整差异、资产来源hash、忽略规则检查与完成记录在 DocuN/evidence/root-archive-20261005/。如需恢复旧目录，先确认旧同名目录不存在，再复制归档子目录回项目根并按manifest核验；不要覆盖现有内容。共享状态以 DocuS/执行动态文档.MD 为唯一权威。
"""
    write(REPORT, report.encode("utf-8"), "保存授权范围、已执行/未执行验证和归档导航")
    save_json(EVID / "changes.json", changes)
    save_json(EVID / "maintenance-ready.json", {"at": now(), "result": "PASS", "changed_files": owned,
        "verification": relative(EVID / "maintenance-verification.json"), "protected_original_requirement": requirement_sha})
    print(json.dumps({"phase": "prepare", "result": "PASS", "files": total, "owned_files": len(owned),
                      "ignored_preserved": len(confirmed), "syntax_checks": len(syntax)}, ensure_ascii=False))


def finish():
    removal = json.loads((EVID / "removal-verification.json").read_text(encoding="utf-8-sig"))
    if removal["result"] != "PASS" or removal["removed_count"] != 4 or not removal["archive_verified_after_removal"]:
        raise RuntimeError("移除证据未通过")
    if any((ROOT / name).exists() for name in NAMES):
        raise RuntimeError("源根目录仍存在")
    if sha((BASE / "manifest.json").read_bytes()) != removal["manifest_sha256"]:
        raise RuntimeError("归档清单被改变")
    changes = json.loads((EVID / "changes.json").read_text(encoding="utf-8"))
    ready = json.loads((EVID / "maintenance-ready.json").read_text(encoding="utf-8"))
    for item in ready["changed_files"]:
        if sha((ROOT / item["path"]).read_bytes()) != item["sha256"]:
            raise RuntimeError("维护结果发生并行变化：" + item["path"])
    for path, before, after in [
        (ROOT / STATE, "四个旧根目录移除待最终核验", "四个旧根目录移除已完成，归档复核通过"),
        (ROOT / ARCH, "归档切换在实施中", "归档切换已完成"),
        (REPORT, "原根目录移除待最终核验。", "四个原根目录已移除，移除后全部1725文件hash与目录再次核验一致；归档完整保留。"),
    ]:
        data = path.read_bytes()
        if data.count(before.encode()) != 1:
            raise RuntimeError("完成阶段原文匹配非唯一：" + relative(path))
        updated = data.replace(before.encode(), after.encode())
        path.write_bytes(updated)
        for item in changes:
            if item["path"] == relative(path):
                item["after_sha256"] = sha(updated)
    log_path = ROOT / LOG
    original_log = log_path.read_bytes()
    if "CHG-0820" in original_log.decode("utf-8-sig"):
        raise RuntimeError("CHG编号已被占用，停止共享记录写入")
    (EVID / "before" / LOG).parent.mkdir(parents=True, exist_ok=True)
    (EVID / "before" / LOG).write_bytes(original_log)
    registered = [
        {"path": relative(EVID / "archive-roots.ps1"), "reason": "固定四源/目标绝对路径、防链接、清单核验及原生PowerShell保留式归档移除"},
        {"path": relative(EVID / "maintain_archive_paths.py"), "reason": "用户授权的路径、夹具和当前文档维护，仅元数据/语法检查"},
        {"path": relative(BASE / "manifest.json"), "reason": "保存四目录1725文件hash/大小及空目录；全部历史原件字节未改"},
        {"path": relative(EVID / "copy-verification.json"), "reason": "四源与归档逐文件核对PASS后才允许进入引用维护"},
        *changes,
        {"path": relative(EVID / "asset-relocations.json"), "reason": "三辅助代码与一结构样本原字节来源和SHA核对"},
        {"path": relative(EVID / "git-ignore-verification.json"), "reason": "272原忽略文件在归档位置继续全部被排除"},
        {"path": relative(EVID / "maintenance-verification.json"), "reason": "语法/JSON/路径/原需求检查；未运行业务验证"},
        {"path": relative(EVID / "maintenance-ready.json"), "reason": "删除前维护文件hash门，不借文件存在声明产品通过"},
        {"path": relative(EVID / "removal-verification.json"), "reason": "四源目录精确移除后逐文件复核PASS，原件在归档完整保留"},
    ]
    stamp = now()
    lines = []
    for i, item in enumerate(registered, 820):
        lines.append(f"- CHG-{i:04d}，{stamp}，Codex编排Agent，{item['path']}。{item['reason']}。")
    last = 819 + len(registered)
    next_id = last + 1
    log_path.write_bytes(original_log + ("\n\n" + "\n\n".join(lines) + "\n").encode("utf-8"))
    state = ROOT / STATE
    data = state.read_bytes()
    old = "本批CHG范围及下一号见下面归档完成登记；共享账仅本文件维护。"
    new = f"本次归档维护CHG0820—{last:04d}，下一CHG{next_id:04d}；TASK/R、阶段与业务预算不改。共享账仅本文件维护。"
    if data.count(old.encode()) != 1:
        raise RuntimeError("状态编号原文不唯一")
    state.write_bytes(data.replace(old.encode(), new.encode()))
    for item in changes:
        item["after_sha256"] = sha((ROOT / item["path"]).read_bytes())
        backup = EVID / "before" / item["path"]
        before = backup.read_bytes() if backup.exists() else b""
        out = EVID / "diffs" / (item["path"].replace("/", "__") + ".diff")
        out.write_text("".join(difflib.unified_diff(before.decode("utf-8-sig").splitlines(keepends=True),
            (ROOT / item["path"]).read_text(encoding="utf-8-sig").splitlines(keepends=True),
            fromfile="before/" + item["path"], tofile="after/" + item["path"])), encoding="utf-8")
    save_json(EVID / "changes.json", changes)
    current_hashes = [{"path": item["path"], "sha256": sha((ROOT / item["path"]).read_bytes())} for item in registered]
    current_hashes.append({"path": LOG, "sha256": sha(log_path.read_bytes())})
    verification = json.loads((EVID / "maintenance-verification.json").read_text(encoding="utf-8"))
    if sha((ROOT / "DocuS/原始需求文档.MD").read_bytes()) != verification["original_requirement_sha256"]:
        raise RuntimeError("原始需求变化")
    save_json(EVID / "final-verification.json", {"at": now(), "result": "PASS", "removed_roots": list(NAMES),
        "all_original_files_archived": 1725, "archive_bytes": 29400868, "archive_post_remove_verified": True,
        "current_owned_file_hashes": current_hashes, "original_requirement_unchanged": True,
        "shared_versions": {"architecture": "0.81", "state": "2.03"}, "next_chg": f"CHG-{next_id:04d}",
        "runtime_product_operations": 0, "git_commits": 0})
    print(json.dumps({"phase": "finish", "result": "PASS", "removed": 4, "archived_files": 1725,
                      "next_chg": f"CHG-{next_id:04d}"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("prepare", "finish"))
    phase = parser.parse_args().phase
    prepare() if phase == "prepare" else finish()
