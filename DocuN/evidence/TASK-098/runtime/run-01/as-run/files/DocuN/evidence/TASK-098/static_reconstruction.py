"""独立静态重建，只读合同、产品与原件，输出仅在098目录。"""
import ast
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
E = ROOT / "DocuN/evidence/TASK-097"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def brief(value, key=""):
    # 正文不复制，保留原件摘要及有辨别力的原始字段。
    if isinstance(value, dict):
        return {k: brief(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [brief(v, key) for v in value]
    if key == "payload" and isinstance(value, str):
        try:
            body = json.loads(value)["value"]
            return {"sha256": hashlib.sha256(value.encode()).hexdigest(),
                    "profile": body.get("profile"), "goal": body.get("goal"),
                    "question": body.get("question"), "parent_operation_id": body.get("parent_operation_id"),
                    "request_sha256": body.get("request_sha256"), "kind": body.get("result", {}).get("kind"),
                    "catalog_count": len(body.get("catalog", []))}
        except (ValueError, KeyError, TypeError):
            return {"sha256": hashlib.sha256(value.encode()).hexdigest(), "bytes": len(value.encode())}
    if isinstance(value, str) and len(value) > 1500:
        return {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest(),
                "begin": value[:300], "end": value[-600:]}
    return value


def funcs(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    result = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result[node.name] = ast.dump(node, include_attributes=False)
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result[node.name + "." + child.name] = ast.dump(child, include_attributes=False)
    return result


def main():
    started = time.perf_counter()
    changes = read(E / "changes.json")
    product = [x for x in changes if x["path"].startswith(("backend/app/", "frontend/src/", "config/")) or x["path"] == "README.md"]
    pre = {x["path"]: x for x in read(E / "pre-manifest.json")}
    current = read(OUT / "input-snapshot.json")["current_objects"]
    comparison = []
    for item in current:
        rel = item["path"]
        old = E / "pre" / rel
        now = ROOT / rel
        row = {"path": rel, "current_sha256": digest(now), "pre_manifest_present": rel in pre,
               "pre_file_present": old.exists()}
        if old.exists():
            row["pre_sha256"] = digest(old)
            row["bytes_unchanged"] = old.read_bytes() == now.read_bytes()
            row["text_newlines_unchanged"] = old.read_text(encoding="utf-8-sig") == now.read_text(encoding="utf-8-sig") if now.suffix in {".py", ".tsx", ".ts", ".md", ".json", ".css"} else None
            if now.suffix == ".py":
                before, after = funcs(old), funcs(now)
                row["old_functions_changed"] = [k for k in before if before[k] != after.get(k)]
                row["functions_added"] = [k for k in after if k not in before]
        comparison.append(row)
    evidence = {}
    for batch in sorted(E.glob("integration-*")):
        files = {}
        for name in ("run.json", "business-checks.json", "pg-summary.json", "affected-pg-summary.json",
                     "business-summary.json", "combined-summary.json", "repair-summary.json", "ui-summary.json",
                     "browser-report.json", "served-bundle.json", "process-cleanup.json", "container-pre.json", "container-post.json"):
            path = batch / name
            if path.exists():
                files[name] = {"source": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "raw_fields": brief(read(path))}
        evidence[batch.name] = files
    manifests = {}
    for base in (E / "as-run", E / "continuation-01/as-run"):
        for path in sorted(base.glob("*/manifest.json")):
            manifest = read(path)
            objects = manifest.get("files", []) if isinstance(manifest, dict) else manifest
            matches = []
            for obj in objects:
                rel = obj["path"]
                final = ROOT / rel
                snapshot = path.parent / "files" / rel
                matches.append({"path": rel, "as_run_sha256": obj.get("sha256"),
                                "current_match": final.exists() and digest(final) == obj.get("sha256"),
                                "saved_bytes_match": snapshot.exists() and digest(snapshot) == obj.get("sha256")})
            manifests[path.relative_to(ROOT).as_posix()] = {"command": manifest.get("command") if isinstance(manifest, dict) else None,
                                                          "objects": matches}
    result = {"product_change_count": len(product), "product_changes": product,
              "pre_comparisons": comparison, "raw_evidence": evidence, "as_run_bindings": manifests,
              "elapsed_seconds": time.perf_counter() - started}
    target = OUT / "static-reconstruction.json"
    with target.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({"product_change_count": len(product), "changed_existing_functions":
                      [x for x in comparison if x.get("old_functions_changed")],
                      "elapsed_seconds": result["elapsed_seconds"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
