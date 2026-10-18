"""只保存交付hash/diff与累计快照，不启动资源、模型或额外测试。"""
from __future__ import annotations
from datetime import datetime,timezone
import difflib
import hashlib
import json
from pathlib import Path
import time
from .control import ROOT,EVIDENCE,atomic


def identity(path):return {"path":str(path.relative_to(ROOT)).replace("\\","/"),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    folder=EVIDENCE/"delivery";folder.mkdir(exist_ok=False)
    before=json.loads((EVIDENCE/"source-pre-identity.json").read_text(encoding="utf-8-sig"))
    changes=[];lines=[];protected=[]
    allowed={"backend/app/activities/repository.py","backend/app/activities/service.py","backend/app/activities/api.py",
        "backend/app/capabilities/contracts.py","backend/app/capabilities/gateway.py","backend/app/main.py","backend/app/service_config.py",
        "frontend/src/learning/LearningResult.tsx","frontend/src/activities/ActivityWorkspace.tsx","frontend/src/learning/TeachingWorkspace.tsx"}
    for row in before:
        path=Path(row["path"]);relative=str(path.relative_to(ROOT)).replace("\\","/");post=identity(path)
        post["pre_sha256"]=row["actual"];post["changed"]=post["sha256"]!=row["actual"];changes.append(post)
        if post["changed"]:
            original=EVIDENCE/"pre"/relative
            if original.is_file():
                lines.extend(difflib.unified_diff(original.read_text(encoding="utf-8").splitlines(keepends=True),path.read_text(encoding="utf-8").splitlines(keepends=True),fromfile="pre/"+relative,tofile="final/"+relative))
            post["card_write_path"]=relative in allowed or relative in {"config/activity.example.json","README.md","deploy/start_local.py"}
        else:protected.append(relative)
    atomic(folder/"pre-post.json",changes);(folder/"pre-final.diff").write_text(''.join(lines),encoding="utf-8")
    candidates=[]
    old={"__init__.py","contracts.py","supervisor.py","reaper.py"}
    candidates.extend(p for p in (ROOT/"backend/app/preview").glob("*") if p.is_file() and p.name not in old)
    candidates.extend(p for p in (ROOT/"frontend/src/explanations").glob("*") if p.is_file())
    candidates.extend(p for p in (ROOT/"backend/tests/fixtures/task111").rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    candidates.extend(p for p in (ROOT/"frontend/tests/task111").glob("*") if p.is_file())
    for relative in ("backend/migrations/012_html_explanations.sql","deploy/preview/renderer-host.cjs","deploy/preview/renderer-bootstrap.cjs",
        "deploy/preview/runtime.cjs","deploy/preview/runtime.html","deploy/preview/runtime.css","deploy/preview/descriptor.schema.json",
        "deploy/preview/Dockerfile.production","deploy/preview/build_renderer.py","deploy/preview/collect_licenses.py","deploy/preview/README.md",
        "deploy/compose.local.yml","deploy/start_local.py","config/activity.example.json","config/preview.example.json","README.md"):
        candidates.append(ROOT/relative)
    files={item["path"]:item for item in [*changes,*[identity(path) for path in candidates]]}
    atomic(folder/"final-source-identity.json",sorted(files.values(),key=lambda row:row["path"]))
    inheritance=[]
    for name in ("offline-01","real-01/bound","real-06/attempt-01","real-06/attempt-02","offline-02","offline-03","offline-06"):
        original=EVIDENCE/name/"source-identity.json"
        if not original.is_file():continue
        manifest=json.loads(original.read_text(encoding="utf-8"));different=[];same=[]
        for row in manifest:
            current=files.get(row["path"])
            if current is None or current["sha256"]!=row["sha256"]:different.append(row["path"])
            else:same.append(row["path"])
        inheritance.append({"as_run":name,"same":same,"different":different,"full_final_bytes_pass":False})
    atomic(folder/"as-run-final-differences.json",inheritance)
    budget=json.loads((EVIDENCE/"budget.json").read_text(encoding="utf-8"))
    atomic(folder/"budget-final.json",budget)
    summary={"recorded_at_utc":datetime.now(timezone.utc).isoformat(),"recorded_at_ns":time.monotonic_ns(),"permit":budget["permit"],
      "deadline_ns":budget["deadline_ns"],"total_remaining_seconds":max(0,(budget["deadline_ns"]-time.monotonic_ns())/1e9),
      "changed_pre_files":[row["path"] for row in changes if row["changed"]],"unexpected_pre_changes":[row["path"] for row in changes if row["changed"] and not row["card_write_path"]],
      "protected_equal_count":len(protected),"protected_equal_files":protected,"candidate_source_files":len(files),
      "real_window_reopen_allowed":False,"full_matrix_complete":False,"cleanup_receipt":"cleanup-resume-20261010/cleanup-receipt.json",
      "category_seconds_note":"time_seconds为runner批实际经过秒数；meta/实现准备的细分类未完整分段，不假称分类投入已精确闭合"}
    atomic(folder/"delivery-summary.json",summary)
    print(json.dumps({"unexpected_pre_changes":summary["unexpected_pre_changes"],"protected_equal_count":len(protected),"source_files":len(files),"counts":budget["counts"]},ensure_ascii=False))


if __name__=="__main__":main()
