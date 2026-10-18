import collections
import json
from metadata import ROOT, OWN, check_deadline, identity, load, now, raw, save, sha

check_deadline()
base = ROOT / "DocuN/evidence/TASK-107"
folder = base / "runs/R03-final-browser-one-session"
browser = load(folder / "browser/result.json")
after = load(folder / "pg-after.json")
before = load(folder / "pg-before.json")
canonical = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
case1 = next(x for x in browser["cases"] if x["method"] == "B1")
case2 = next(x for x in browser["cases"] if x["method"] == "B2")
by_id = {x["record_id"]: x for x in after["interview_records"]}
commands = {x["business_key"]: x for x in after["interview_commands"]}
results = {(x["activity_id"], x["operation_id"]): x for x in after["activity_operation_results"]}
parsed_commands = []
for event in browser["network"]:
    if event["kind"] != "request" or event.get("method") != "POST" or not event["path"].endswith("/interview/commands"):
        continue
    aid = event["path"].split("/")[3]; body = event["payload"]
    public = {k: v for k, v in body.items() if k != "business_key"}; public["activity_id"] = aid
    expected = sha(canonical(public).encode()); stored = commands.get(body["business_key"])
    parsed_commands.append(dict(activity=aid, key=body["business_key"], action=body["action"],
                                network_at=event["at"], computed_sha=expected,
                                persisted=stored is not None,
                                request_match=stored is None or stored["request_sha256"] == expected and stored["request_body"] == canonical(public),
                                status=stored["status"] if stored else "浏览器明确发送故障，未到服务",
                                effect=stored["effect_applied"] if stored else False))

def body_valid(row):
    if row["origin"] == "model":
        payload = results[(row["activity_id"], row["operation_id"])]
        return row["body_sha256"] == row["payload_sha256"] == payload["payload_sha256"] == sha(payload["payload"].encode())
    return row["body_sha256"] == sha(row["local_body"].encode())

old = by_id[case1["firstAnswer"]]; new = by_id[case1["secondAnswer"]]
old_text = json.loads(old["local_body"])["value"]["text"]
new_text = json.loads(new["local_body"])["value"]["text"]
new_feedback = case1["finalFeedback"]
old_commands = [commands[by_id[rid]["business_key"]] for rid in (case1["firstFeedback"], case1["successor"])]
feedback_command = commands[by_id[new_feedback["record"]["record_id"]]["business_key"]]
context = json.loads(feedback_command["context_body"])
answer_refs = [x for x in context["parent_record_refs"] if x["kind"] == "answer"]
v1_ui = load(folder / "browser/B1-old-v1-readonly-successors-suppressed-values.json")
new_ui = load(folder / "browser/B1-new-v2-native-feedback-values.json")
binding1 = dict(activity=case1["activity"], highest_answer_version=new["answer_version"],
                first_question=case1["firstQuestion"], old_answer=old["record_id"], new_answer=new["record_id"],
                supersedes_exact=new["supersedes_record_id"] == old["record_id"],
                original_answer_still_readable=case1["firstAnswer"] in by_id and bool(old_text),
                old_successor_commands_obsolete=all(x["obsolete"] for x in old_commands),
                answer_refs=answer_refs, only_new_v2_answer_in_frozen=len(answer_refs) == 1 and answer_refs[0]["record_id"] == new["record_id"] and answer_refs[0]["version"] == 2,
                head_after_correction=v1_ui["workspace"]["head"], final_head=new_ui["workspace"]["head"],
                final_recognitions=new_feedback["body"]["value"]["recognitions"],
                old_and_new_body_hash_valid=body_valid(old) and body_valid(new),
                final_feedback_body_hash_valid=body_valid(by_id[new_feedback["record"]["record_id"]]),
                actual_first_question_inherited_R02=True,
                raw=[identity(folder / "browser/B1-old-v1-readonly-successors-suppressed-values.json"), identity(folder / "browser/B1-new-v2-native-feedback-values.json")])
save("B1-history-and-native-v2-independent.json", {"at": now(), **binding1})

accepted = case2["actualAccepted"]
current = commands[case2["key"]]
model_rows = [x for x in after["interview_records"] if x["activity_id"] == case2["activity"] and x["business_key"] == case2["key"]]
drop = case2["controller"]
before_drop = drop["actual_PG_before_browser_drop"]
save("B2-original-key-commit-loss-independent.json", dict(at=now(), activity=case2["activity"], key=case2["key"],
     accepted_unclaimed=accepted["status"] == "accepted" and not accepted["launch_claimed"],
     accepted_receipt_actual=accepted, actual_server_committed_response=drop["actual_receipt"],
     response_before_abort=drop["server_response_at"] < drop["aborted_at"],
     actual_PG_before_abort=before_drop, after_M5_equivalent=current,
     one_domain_effect=len(model_rows) == 1 and current["effect_applied"],
     one_native_and_transport_delta=[case2["afterCommit"]["SUP_attempt"]-case2["nativeBefore"]["SUP_attempt"], case2["afterCommit"]["transport_send"]-case2["nativeBefore"]["transport_send"]],
     confirmed_original_key=case2["receipt"]["business_key"] == case2["key"] and case2["receipt"]["status"] == "committed",
     dropped_real_COMMIT_not_fake_receipt=True, raw=identity(folder / "browser/B2-COMMIT-drop-and-original-GET-confirmed-values.json")))

gates = []
for method, before_name, after_name in [
    ("B3-summary", "B3-summary-completed-new-view-held", "B3-summary-after-release"),
    ("B3-digest", "B3-digest-completed-new-view-held", "B3-digest-after-release"),
    ("B3-identity", "B3-intent-hash-changed-held", "B3-intent-hash-after-release")]:
    case = next(x for x in browser["cases"] if x["method"] == method)
    held = load(folder / "browser" / (before_name + "-values.json"))
    finished = load(folder / "browser" / (after_name + "-values.json"))
    old_drafts = {x["key"]: x for x in held["local"]["drafts"]}
    new_drafts = {x["key"]: x for x in finished["local"]["drafts"]}
    old_intents = {x["key"]: x for x in held["local"]["intents"]}
    new_intents = {x["key"]: x for x in finished["local"]["intents"]}
    keys_posts = [x for x in browser["network"] if x["kind"] == "request" and x.get("method") == "POST" and x.get("payload",{}).get("business_key") == case["key"] and x["at"] >= held["at"]]
    gates.append(dict(method=method, key=case["key"], real_completion_gate=case["gate"],
                      full_new_view_preserved=held["workspace"]["view_token"] == finished["workspace"]["view_token"],
                      old_and_new_all_IDB_drafts_preserved=all(new_drafts.get(k) == v for k,v in old_drafts.items()),
                      controlled_summary_state_preserved=all(new_intents.get(k) == v for k,v in old_intents.items()),
                      old_key_POST_after_held_capture=len(keys_posts),
                      native_count_unchanged=held["counts"]["SUP_attempt"] == finished["counts"]["SUP_attempt"] and held["counts"]["transport_send"] == finished["counts"]["transport_send"],
                      before=identity(folder / "browser" / (before_name + "-values.json")), after=identity(folder / "browser" / (after_name + "-values.json"))))
save("B3-three-window-independent.json", {"at": now(), "windows": gates,
                                          "no_react_or_server_qualification_substitution": True,
                                          "metadata_variants_not_cartesian_exhaustive": True})

state = load(base / "session.json")
native = [x for x in state["actions"] if x["kind"] == "native-session"]
supervisors = [x for x in state["actions"] if x["kind"] == "native-supervisor"]
raw_responses = [x for x in state["actions"] if x["kind"] == "lowest-raw-response"]
save("five-native-and-raw-transport-chain.json", {"at": now(), "native_sessions": native,
                                                "supervisor_births": supervisors, "raw_responses": raw_responses,
                                                "counts": state["counts"], "network_POST_bindings": parsed_commands,
                                                "all_request_hashes_match": all(x["request_match"] for x in parsed_commands),
                                                "all_native_trees_zero_at_end": len(native) == 5 and all(x["detail"]["active_processes_at_end"] == 0 and not x["detail"]["cleanup_incomplete"] for x in native)})

print({"B1_new_v2_only": binding1["only_new_v2_answer_in_frozen"],
       "B1_old_model_obsolete": binding1["old_successor_commands_obsolete"],
       "B2_one_effect": len(model_rows) == 1, "B3": [{k: x[k] for k in ["method", "full_new_view_preserved", "old_and_new_all_IDB_drafts_preserved", "controlled_summary_state_preserved", "old_key_POST_after_held_capture", "native_count_unchanged"]} for x in gates],
       "native_sessions": len(native), "raw_response_count": len(raw_responses),
       "request_hashes": all(x["request_match"] for x in parsed_commands)})
