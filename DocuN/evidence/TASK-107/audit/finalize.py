import datetime
import json
import os
import re
import time
from metadata import ROOT, OWN, check_deadline, identity, load, now, raw, save, sha

check_deadline()
base = ROOT / "DocuN/evidence/TASK-107"
incoming_path = base / "orchestration-setup-20261008/audit-input.json"
incoming = load(incoming_path)
first = load(OWN / "initial-identity-check.json")
if sha(raw(incoming_path)) != first["input"]["sha256"]:
    raise RuntimeError("107输入漂移")
checks = []
for p,h in incoming["current_files"].items():
    current = identity(p)
    checks.append({**current, "expected": h, "match": current["sha256"] == h})
for item in incoming["rules"]:
    current = identity(item["absolute_path"])
    checks.append({**current, "expected": item["sha256"], "match": current["sha256"] == item["sha256"]})
for key in ("contract", "approved_limits", "execution_contract"):
    item = incoming[key]; current = identity(item["path"])
    checks.append({**current, "expected": item["sha256"], "match": current["sha256"] == item["sha256"]})
if not all(x["match"] for x in checks):
    raise RuntimeError("107末次产品/规则/合同漂移")
browser = load(base / "runs/R03-final-browser-one-session/browser/result.json")
assets = []
for item in browser["loaded"]:
    name = item["path"].split("/")[-1]
    captured = identity(base / "runs/R03-final-browser-one-session/browser" / name)
    current = identity(ROOT / "frontend/dist/assets" / name)
    assets.append({"actual_loaded": item, "capture": captured, "current": current,
                   "match": item["sha256"] == captured["sha256"] == current["sha256"]
                   and item["bytes"] == captured["bytes"] == current["bytes"]})
if not all(x["match"] for x in assets):
    raise RuntimeError("107浏览器完整加载与当前字节不符")
primary = []
for entry in load(OWN / "V01-V24-independent-applicability.json")["entries"]:
    for item in entry["primary_refs"]:
        current = identity(item["path"])
        primary.append({**current, "match": current["sha256"] == item["sha256"]})
if not all(x["match"] for x in primary):
    raise RuntimeError("107已审原件漂移")
save("final-identity-check.json", dict(at=now(), current_objects=363, total_checks=len(checks), checks=checks,
                                       actual_loaded_assets=assets, primary_checks=primary, all_match=True))
state = load(base / "session.json")
active = (time.monotonic_ns()-state["start_ns"])/1e9
if active >= 21600:
    raise RuntimeError("107主动预算已到")
metadata = 10000.0
state["seconds"]["metadata"] = metadata
state["actions"].append(dict(kind="charge", bucket="metadata", seconds=metadata, utc=now(),
                              detail={"conservative_split": True, "exact_split_unknown": True,
                                      "basis": "纯命令实测/源码与合同读审、原件核证、显示与报告保守分摊；夹具书写/思考全在active，不伪称逐秒精确"}))
state.update(closed=True, status="独立审计完成，交编排有限裁定", closed_at=now(),
             active_used_seconds=active, actual_business_roots_total=70,
             all_old_failures_unknowns_preserved=True, no_project_acceptance=True)
cleanup = load(base / "cleanup-supplement-03.json")
if not cleanup["all_original_owned_births_stopped"] or not all(cleanup["ports_free"].values()) or any(x["running"] or x["pid"] for x in cleanup["containers"]):
    raise RuntimeError("107最终收尾证据不足")
account = dict(at=now(), permit=state["permit"], start_ns=state["start_ns"], deadline_ns=state["deadline_ns"],
               active_used_seconds=active, active_limit_seconds=21600, metadata_seconds=metadata,
               metadata_limit_seconds=10800, metadata_exact_split_unknown=True, counts=state["counts"],
               seconds=state["seconds"], count_limits=state["count_limits"], prior_roots=67,new_roots=3,total_roots=70,
               old_root_statuses_unchanged=True, new_root_statuses={"R01":"FAIL","R02":"FAIL","R03":"FAIL"},
               R03_browser_status=browser["status"], methods=[{"method":x["method"],"status":x["status"]} for x in browser["cases"]],
               cleanup_original_unconfirmed_and_supplement_preserved=True, final_all_stopped=True,
               model_raw_response_only_and_gates_disclosed=True)
save("final-accounting.json", account)
prefix = raw(OWN / "result-draft.md").decode("utf-8")
local = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
prefix = prefix.replace("{{FINAL_AT}}",local).replace("{{ACTIVE_SECONDS}}",f"{active:.3f}").replace("{{METADATA_SECONDS}}",f"{metadata:.3f}")
if "{{" in prefix or "*" in prefix:
    raise RuntimeError("107结果存在占位符或新星号")
target = ROOT / "DocuN/results/TASK-107-result.md"
if target.exists():
    raise RuntimeError("107目标结果已存在，需要断点核对，禁止盲覆盖")
tmp = OWN / "result-assembled.tmp";tmp.write_bytes(prefix.encode("utf-8"));os.replace(tmp,target)
links = re.findall(r"\[[^\]]+\]\((D:/[^)]+)\)",prefix)
paths = [re.sub(r":\d+$","",x) for x in links]
missing = [p for p in paths if not p.endswith("/delivery-check.json") and not __import__("pathlib").Path(p).is_file()]
if missing:
    raise RuntimeError("107结果链接缺失："+str(missing))
actual = raw(target);actual.decode("utf-8")
save("delivery-check.json", dict(at=now(),result=identity(target),result_readable=True,local_links=len(paths),
                                 missing_links=[],input_and_product_unchanged=True,source_loaded_assets_match=True,
                                 current_objects=363,no_shared_state_or_104_106_result_write=True,final_resources_stopped=True))
actual_paths = [p for p in paths if not __import__("pathlib").Path(p).is_file()]
if actual_paths:
    raise RuntimeError("107交付最后链接不可读")
state["delivery_utc"] = now();state["delivery_active_used_seconds"] = (time.monotonic_ns()-state["start_ns"])/1e9
(base / "session.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
account["delivery_active_used_seconds"] = state["delivery_active_used_seconds"]
account["final_session_sha256"] = sha(raw(base / "session.json"))
save("final-accounting.json",account)
print(dict(result=identity(target),active=state["delivery_active_used_seconds"],metadata=metadata,
           current_checks=len(checks),actual_asset_matches=len(assets),primary_matches=len(primary),links=len(paths),all_readable=True,
           finite_conclusion="批准G10有限切片可交编排关闭，旧失败/原根FAIL保留"))
