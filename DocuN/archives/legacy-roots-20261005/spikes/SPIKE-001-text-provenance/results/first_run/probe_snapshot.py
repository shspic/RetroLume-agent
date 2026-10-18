"""TASK-003：离线、合成资料、可保留反例的提取探针；不是产品解析器。"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata
import io
import json
import logging
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import traceback
import warnings

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parent
FONT = Path("C:/Windows/Fonts/simhei.ttf")
MODES = ("plain", "layout")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_canvas(path, title):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"拒绝覆盖已有样本：{path}")
    c = Canvas(str(path), pagesize=A4, invariant=1, pageCompression=1)
    c.setTitle(title)
    c.setAuthor("RetroLume synthetic SPIKE-001")
    c.setFont("SyntheticCJK", 11)
    return c


def line(c, x, y, content, size=11):
    c.setFont("SyntheticCJK", size)
    c.drawString(x, y, content)


def generate_fixtures():
    """样本内容独立写在这里；绝不从提取结果生成或改写预期。"""
    fixture_root = ROOT / "fixtures"
    if fixture_root.exists():
        raise FileExistsError("fixtures 已存在；复跑请省略 --generate，保留原件。")
    pdfmetrics.registerFont(TTFont("SyntheticCJK", str(FONT)))
    fixture_root.mkdir()
    (fixture_root / "bilingual.txt").write_text(
        "RetroLume synthetic notes\n"
        "学习目标：理解能量守恒。\n"
        "Energy is conserved in an isolated system.\n"
        "核对单位：焦耳。 Check units: joules.\n", encoding="utf-8")
    (fixture_root / "bilingual.md").write_text(
        "# 复习卡片 / Review card\n\n"
        "- 中文：先解释，再举例。\n"
        "- English: explain first, then give an example.\n\n"
        "| 项目 / Item | 数值 / Value |\n"
        "| --- | --- |\n"
        "| 时间 / Time | 3 seconds |\n", encoding="utf-8")
    c = make_canvas(fixture_root / "ordinary_two_pages.pdf", "Ordinary bilingual two-page fixture")
    line(c, 42, 790, "普通文字资料 / Ordinary text", 16)
    line(c, 42, 730, "第一页：先定义问题，再检查证据。")
    line(c, 42, 695, "Page one: define the question before checking evidence.")
    line(c, 42, 48, "Printed page 101", 9)
    c.showPage()
    line(c, 42, 790, "复测记录 / Second attempt", 16)
    line(c, 42, 730, "第二页：复测结果可以改变下一步练习。")
    line(c, 42, 695, "Page two: use a second attempt to choose the next exercise.")
    line(c, 42, 48, "Printed page 205", 9)
    c.save()

    c = make_canvas(fixture_root / "two_columns_table.pdf", "Two columns and table: reading-order counterexample")
    line(c, 42, 795, "双栏与表格 / Two columns and table", 16)
    line(c, 42, 765, "Read LEFT top-to-bottom, then RIGHT, then TABLE by rows.", 10)
    line(c, 42, 744, "先左栏、后右栏；表格逐行从左向右。", 10)
    c.setStrokeColorRGB(0.4, 0.4, 0.4)
    c.line(295, 585, 295, 715)
    # 合法的 PDF 绘制顺序与可见栏阅读顺序不同；反例设计预先固定。
    for y, left, right in [
        (700, "L1 左栏一：先理解概念。", "R1 右栏一：开始另一道题。"),
        (657, "L2 Left two: connect the evidence.", "R2 Right two: compare two attempts."),
        (614, "L3 左栏三：最后给出解释。", "R3 右栏三：更新复习计划。"),
    ]:
        line(c, 42, y, left, 10)
        line(c, 310, y, right, 10)
    line(c, 42, 549, "TABLE: each value belongs to the topic on the same row.", 10)
    for y in (527, 485, 443, 401):
        c.line(42, y, 548, y)
    for x in (42, 295, 548):
        c.line(x, 401, x, 527)
    # 表格按列写入内容流，但可视语义是按行配对。
    for x, values in [
        (54, ["T-H1 Topic", "T-1A Energy", "T-2A Time"]),
        (307, ["T-H2 Value", "T-1B 12 joules", "T-2B 3 seconds"]),
    ]:
        for y, value in zip((502, 460, 418), values):
            line(c, x, y, value)
    line(c, 42, 48, "Physical page 1; synthetic counterexample", 9)
    c.save()
    (fixture_root / "broken.pdf").write_bytes(b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog\n% deliberately truncated fixture\n")
    for version, chinese, english in [
        (1, "复习间隔：三天。", "Retention interval: 3 days."),
        (2, "复习间隔：七天。", "Retention interval: 7 days."),
    ]:
        c = make_canvas(fixture_root / f"version_{version}" / "notes.pdf", f"Synthetic notes version {version}")
        line(c, 42, 790, "同名资料 / Same file name", 16)
        line(c, 42, 730, f"VERSION={version}")
        line(c, 42, 690, chinese)
        line(c, 42, 650, english)
        c.save()


def extract(case, mode):
    """仅直接调用 pypdf 或 UTF-8 读取，不改写顺序、修复内容或注入预期。"""
    path = ROOT / case["path"]
    if case["kind"] == "pdf":
        reader = PdfReader(path, strict=False)
        return [{"physical_page": i + 1, "text": page.extract_text(extraction_mode=mode)}
                for i, page in enumerate(reader.pages)]
    return [{"physical_page": None, "text": path.read_text(encoding="utf-8")}]


def evaluate(case, pages):
    observations = []
    for expected in case["fragments"]:
        hits = []
        for page in pages:
            source = page["text"]
            cursor = 0
            while (offset := source.find(expected["text"], cursor)) >= 0:
                hit = {"physical_page": page["physical_page"], "extracted_offset": offset,
                       "text": source[offset:offset + len(expected["text"])],
                       "excerpt": source[max(0, offset - 30):offset + len(expected["text"]) + 30]}
                if case["kind"] != "pdf":
                    hit["source_line"] = source.count("\n", 0, offset) + 1
                hits.append(hit)
                cursor = offset + len(expected["text"])
        location_ok = len(hits) == 1 and (
            hits[0]["physical_page"] == expected["physical_page"] if case["kind"] == "pdf"
            else hits[0]["source_line"] == expected["line"])
        observations.append({"id": expected["id"], "expected": expected, "hits": hits,
                             "content_unique_pass": len(hits) == 1, "location_pass": location_ok})
    indexed = {o["id"]: o for o in observations}
    order_checks = []
    for order in case["orders"]:
        available = [(fragment_id, indexed[fragment_id]["hits"][0]) for fragment_id in order["ids"]
                     if len(indexed[fragment_id]["hits"]) == 1]
        observed_ids = [item[0] for item in sorted(available, key=lambda item: (
            item[1]["physical_page"] or 1, item[1]["extracted_offset"]))]
        order_checks.append({"name": order["name"], "expected": order["ids"],
                             "observed": observed_ids, "pass": observed_ids == order["ids"]})
    return {"fragments": observations, "orders": order_checks,
            "page_count": {"expected": case.get("expected_pages"), "actual": len(pages),
                           "pass": len(pages) == case["expected_pages"]} if case["kind"] == "pdf" else None}


def isolated_collect(case, mode, output):
    record = {"case_id": case["id"], "source_path": case["path"], "source_sha256": digest(ROOT / case["path"]),
              "basename": Path(case["path"]).name, "mode": mode,
              "adapter": "pypdf" if case["kind"] == "pdf" else "Python UTF-8 source read (no Markdown renderer)"}
    stream = io.StringIO()
    log_capture = logging.StreamHandler(stream)
    log_capture.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logger = logging.getLogger("pypdf")
    logger.addHandler(log_capture)
    captured_stdout, captured_stderr = io.StringIO(), io.StringIO()
    try:
        with warnings.catch_warnings(record=True) as caught, contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(captured_stderr):
            warnings.simplefilter("always")
            try:
                pages = extract(case, mode)
                record.update(status="success", pages=pages, evaluation=evaluate(case, pages))
            except Exception as exc:
                record.update(status="error", error={"type": type(exc).__name__, "message": str(exc),
                                                       "traceback": traceback.format_exc()})
            record["python_warnings"] = [{"category": w.category.__name__, "message": str(w.message)} for w in caught]
    finally:
        logger.removeHandler(log_capture)
    record.update(pypdf_log=stream.getvalue(), captured_stdout=captured_stdout.getvalue(), captured_stderr=captured_stderr.getvalue())
    record["status_matches_manifest"] = record["status"] == case["expected_status"]
    base = output / "extractions" / mode
    base.mkdir(parents=True, exist_ok=True)
    write_json(base / f"{case['id']}.json", record)
    if record["status"] == "success":
        for i, page in enumerate(record["pages"], 1):
            (base / f"{case['id']}.page-{i}.txt").write_text(page["text"], encoding="utf-8")
    return record


def bare_worker(manifest, mode):
    """故意不捕捉逐文件异常，展示裸批次中断和不可达文件；父进程保留 traceback。"""
    cases = {case["id"]: case for case in manifest["cases"]}
    for case_id in manifest["bare_batch_order"]:
        print(json.dumps({"event": "started", "case_id": case_id}), flush=True)
        pages = extract(cases[case_id], mode)
        print(json.dumps({"event": "completed", "case_id": case_id, "page_count": len(pages)}), flush=True)


def execute(command):
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
                               env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return {"argv": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def run(manifest, args):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", args.run_id):
        raise ValueError("run-id 只能包含字母、数字、短横线或下划线，最多 64 位。")
    output = ROOT / "results" / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    # 固定并保存预期快照，发生在任何提取之前；复跑仍使用同一个原始 manifest。
    write_json(output / "expectation_snapshot.json", manifest)
    shutil.copyfile(ROOT / "probe.py", output / "probe_snapshot.py")
    if args.generate:
        generate_fixtures()
    inputs = [{"case_id": case["id"], "path": case["path"], "sha256": digest(ROOT / case["path"]),
               "bytes": (ROOT / case["path"]).stat().st_size} for case in manifest["cases"]]
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise RuntimeError("缺少已有 pdftoppm；停止，不安装替代依赖。")
    environment = {"argv": sys.orig_argv, "python_executable": sys.executable, "python_version": sys.version,
                   "platform": platform.platform(), "versions": {p: importlib.metadata.version(p) for p in ("pypdf", "reportlab", "Pillow")},
                   "manifest_sha256": digest(ROOT / "manifest.json"), "script_sha256": digest(ROOT / "probe.py"),
                   "font": {"path": str(FONT), "sha256": digest(FONT)}, "renderer": execute([renderer, "-v"]),
                   "git_head": execute(["git", "rev-parse", "HEAD"]),
                   "root_read_only_baseline": {name: digest(ROOT.parents[1] / name) for name in (
                       "AGENTS.md", "REQUIREMENTS.md", "PROJECT_FLOW.md", "PROJECT_INDEX.md", "OPEN_SOURCE_RESEARCH.md")}}
    write_json(output / "environment.json", environment)
    write_json(output / "input_inventory.json", inputs)
    commands = []
    render_dir = output / "renders"
    render_dir.mkdir()
    for case in manifest["cases"]:
        if case["kind"] == "pdf" and case["expected_status"] == "success":
            command = [renderer, "-r", "85", "-png", str(ROOT / case["path"]), str(render_dir / case["id"])]
            commands.append({"step": "render", "case_id": case["id"], **execute(command)})
    bare = []
    for mode in MODES:
        command = [sys.executable, "-I", "-B", str(ROOT / "probe.py"), "--bare-worker", mode]
        evidence = execute(command)
        events = [json.loads(s) for s in evidence["stdout"].splitlines() if s.startswith("{")]
        started = [e["case_id"] for e in events if e["event"] == "started"]
        completed = [e["case_id"] for e in events if e["event"] == "completed"]
        evidence.update(mode=mode, started=started, completed=completed,
                        unvisited=[c for c in manifest["bare_batch_order"] if c not in started])
        bare.append(evidence)
    write_json(output / "bare_batch.json", bare)
    records = [isolated_collect(case, mode, output) for mode in MODES for case in manifest["cases"]]
    version_checks = []
    for mode in MODES:
        old = next(r for r in records if r["case_id"] == "version_1" and r["mode"] == mode)
        current = next(r for r in records if r["case_id"] == "version_2" and r["mode"] == mode)
        old_reference = {"source_path": old["source_path"], "source_sha256": old["source_sha256"],
                         "physical_page": 1, "quote": "Retention interval: 3 days."}
        version_checks.append({"mode": mode, "old_reference": old_reference,
                               "current_source_path": current["source_path"], "current_sha256": current["source_sha256"],
                               "same_basename": old["basename"] == current["basename"],
                               "different_hashes": old["source_sha256"] != current["source_sha256"],
                               "old_quote_present_in_old": old["status"] == "success" and old_reference["quote"] in old["pages"][0]["text"],
                               "old_quote_absent_in_current": current["status"] == "success" and old_reference["quote"] not in current["pages"][0]["text"],
                               "current_quote_present": current["status"] == "success" and "Retention interval: 7 days." in current["pages"][0]["text"],
                               "old_reference_matches_current_hash": old_reference["source_sha256"] == current["source_sha256"],
                               "boundary": "仅实验快照与引用标记；没有覆盖原件、生产导入、失效传播或知识库删除。"})
    write_json(output / "replacement.json", version_checks)
    fragments = [f for r in records if r["status"] == "success" for f in r["evaluation"]["fragments"]]
    order_checks = [{"case_id": r["case_id"], "mode": r["mode"], **o} for r in records if r["status"] == "success" for o in r["evaluation"]["orders"]]
    failed_orders = [o for o in order_checks if not o["pass"]]
    batch_pass = all(b["returncode"] != 0 and b["completed"] == ["ordinary"] and b["started"] == ["ordinary", "broken"] for b in bare)
    replacements_pass = all(all(v[k] for k in ("same_basename", "different_hashes", "old_quote_present_in_old", "old_quote_absent_in_current", "current_quote_present")) and not v["old_reference_matches_current_hash"] for v in version_checks)
    unchanged = all(digest(ROOT / i["path"]) == i["sha256"] for i in inputs)
    all_statuses = all(r["status_matches_manifest"] for r in records)
    page_counts = [r["evaluation"]["page_count"] for r in records if r["status"] == "success" and r["evaluation"]["page_count"]]
    # 实验留证完成与资料提取完全正确分别计数，反例失败绝不转写成业务通过。
    evidence_complete = (all_statuses and batch_pass and replacements_pass and unchanged
                         and all(c["returncode"] == 0 for c in commands)
                         and any(o["case_id"] == "complex" for o in failed_orders))
    summary = {"ids": ["TASK-003", "SPIKE-001", "HYP-001", "FR-001", "FR-004", "NFR-001", "NFR-002", "DR-001", "DR-003"],
               "run_id": args.run_id, "fixture_count": len(inputs), "parse_attempts": len(records),
               "parse_successes": sum(r["status"] == "success" for r in records),
               "parse_errors": sum(r["status"] == "error" for r in records),
               "manifest_status_checks": {"passed": sum(r["status_matches_manifest"] for r in records), "total": len(records)},
               "fragment_checks": {"passed": sum(f["content_unique_pass"] for f in fragments), "total": len(fragments)},
               "location_checks": {"passed": sum(f["location_pass"] for f in fragments), "total": len(fragments)},
               "page_count_checks": {"passed": sum(p["pass"] for p in page_counts), "total": len(page_counts)},
               "reading_order_checks": {"passed": len(order_checks) - len(failed_orders), "total": len(order_checks), "failures": failed_orders},
               "bare_batch_failure_reproduced": batch_pass, "isolated_wrapper_expected_statuses": all_statuses,
               "replacement_observations_pass": replacements_pass, "input_hashes_unchanged": unchanged,
               "render_commands": {"passed": sum(c["returncode"] == 0 for c in commands), "total": len(commands)},
               "visual_review": "pending human/agent PNG inspection; command success alone does not validate glyphs or layout",
               "experiment_evidence_collected": evidence_complete,
               "general_pdf_semantic_order_supported": not failed_orders,
               "hypothesis_recommendation": "部分支持简单资料的内容/位置与包装层失败隔离；通用文字 PDF 阅读顺序被合成反例否定，HYP-001 不可标为整体通过。",
               "entrypoint_exit_code": 0 if evidence_complete else 2}
    write_json(output / "commands.json", commands)
    write_json(output / "results.json", records)
    write_json(output / "summary.json", summary)
    (output / "stdout.txt").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_json(output / "artifact_hashes.json", [{"path": str(p.relative_to(output)), "sha256": digest(p), "bytes": p.stat().st_size}
                                                for p in sorted(output.rglob("*")) if p.is_file()])
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return summary["entrypoint_exit_code"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true", help="首次生成合成样本，拒绝覆盖。")
    parser.add_argument("--run-id", help="每次使用新的结果子目录，拒绝覆盖。")
    parser.add_argument("--bare-worker", choices=MODES, help=argparse.SUPPRESS)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if args.bare_worker:
        bare_worker(manifest, args.bare_worker)
        return 0
    if not args.run_id:
        parser.error("必须指定 --run-id")
    return run(manifest, args)


if __name__ == "__main__":
    raise SystemExit(main())
