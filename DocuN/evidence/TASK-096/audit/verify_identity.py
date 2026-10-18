# TASK-096 审计脚本：对象身份核验（只读，输出写本卡 evidence/audit/）
import hashlib, json, os

ROOT = "D:/shspic/project_NO3_RetroLume-agent"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    with open(os.path.join(ROOT, "DocuN/evidence/TASK-096/input-snapshot.json"), "r", encoding="utf-8") as f:
        snap = json.load(f)

    results = {"current_files": [], "original_evidence": [], "final_snapshot_vs_current": []}

    for item in snap["current_files"]:
        p = os.path.join(ROOT, item["path"].replace("/", os.sep))
        e = {"path": item["path"], "expected": item["sha256"]}
        if os.path.exists(p):
            e["actual"] = sha256(p)
            e["match"] = e["actual"] == item["sha256"]
        else:
            e["actual"] = None; e["match"] = False; e["missing"] = True
        results["current_files"].append(e)

    for item in snap["original_evidence"]:
        p = os.path.join(ROOT, item["path"].replace("/", os.sep))
        e = {"path": item["path"], "expected": item["sha256"]}
        if os.path.exists(p):
            e["actual"] = sha256(p)
            e["match"] = e["actual"] == item["sha256"]
        else:
            e["actual"] = None; e["match"] = False; e["missing"] = True
        results["original_evidence"].append(e)
        if "final-snapshot/" in item["path"]:
            rel = item["path"].split("final-snapshot/", 1)[1]
            cur = os.path.join(ROOT, rel.replace("/", os.sep))
            fe = {"final_snapshot_path": item["path"], "snapshot_intact": e["match"]}
            if os.path.exists(cur):
                fe["current_actual"] = sha256(cur)
                fe["current_matches_snapshot"] = fe["current_actual"] == item["sha256"]
            else:
                fe["current_actual"] = None; fe["current_matches_snapshot"] = False; fe["current_missing"] = True
            results["final_snapshot_vs_current"].append(fe)

    out_dir = os.path.join(ROOT, "DocuN/evidence/TASK-096/audit")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "identity-check.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    cm = [r for r in results["current_files"] if not r["match"]]
    om = [r for r in results["original_evidence"] if not r["match"]]
    print(f"current_files: {len(results['current_files'])-len(cm)}/{len(results['current_files'])} MATCH")
    for r in cm: print(f"  DRIFT/MISSING: {r['path']} expected={r['expected']} actual={r['actual']}")
    print(f"original_evidence: {len(results['original_evidence'])-len(om)}/{len(results['original_evidence'])} MATCH")
    for r in om: print(f"  DRIFT/MISSING: {r['path']} expected={r['expected']} actual={r['actual']}")
    print(f"final_snapshot_vs_current: {len(results['final_snapshot_vs_current'])} entries")
    for e in results["final_snapshot_vs_current"]:
        flag = "OK" if (e["snapshot_intact"] and e["current_matches_snapshot"]) else "CHECK"
        print(f"  [{flag}] {e['final_snapshot_path'].split('final-snapshot/')[1]} intact={e['snapshot_intact']} current_match={e['current_matches_snapshot']}")

if __name__ == "__main__":
    main()
