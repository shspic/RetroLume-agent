"""从有限不可变事实重算当前图的观察；不执行程序、不写数据库。"""
from __future__ import annotations

import json

from .teaching_policy import derive_support_checks


def rebuild_progress(nodes: list[dict], facts: list[dict], path_id: str) -> dict:
    exercises, answers, feedbacks, corrections = {}, {}, {}, set()
    for row in facts:
        rid = str(row["record_id"])
        if row["kind"] == "exercise":
            value = row.get("document") or {}
            if value.get("path_record_id") == path_id:
                exercises[rid] = value
        elif row["kind"] == "answer":
            answers[rid] = json.loads(row["body"])
        elif row["kind"] == "feedback":
            feedbacks.setdefault(str(row["answer_record_id"]), []).append(row)
        elif row["kind"] == "correction":
            corrections.add(str(row["parent_record_id"]))
    result = {"pending_proposal_record_id": None, "nodes": {}}
    for index, node in enumerate(nodes):
        node_id = node.get("node_id", f"n{index+1}")
        required = {d["dimension"] for d in node["completion_dimensions"]}
        eligible, contested, assisted = {}, [], []
        latest_bad, observed = False, False
        for aid, versions in feedbacks.items():
            answer = answers.get(aid)
            if answer is None:
                continue
            eid = answer["exercise_record_id"]
            document = exercises.get(eid)
            if document is None or document.get("node_id") != node_id:
                continue
            normal = [v for v in versions if (v.get("document") or {}).get("result",{}).get("result_type") == "feedback"]
            if not normal:
                continue
            observed = True
            latest = normal[-1]
            output = latest["document"]["result"]
            opinions = [{d["id"]:d["observation"] for d in v["document"]["result"]["dimension_observations"]} for v in normal]
            conflict = len({json.dumps(v,sort_keys=True) for v in opinions}) > 1
            disputed = any(str(v["record_id"]) in corrections for v in versions)
            checks = derive_support_checks(document["result"], answer["text"])
            conflict = conflict or any(c["status"] == "conflict" for c in checks)
            if disputed or conflict:
                contested.append(aid)
                continue
            opinion = opinions[-1]
            # 确定核查只收紧模型观察；解析不足也不冒充该数值维度已核定。
            opinion = dict(opinion)
            for check in checks:
                for dimension in check.get("dimension_ids", []):
                    if check["status"] != "matched":
                        opinion[dimension] = "not_met" if check["status"] == "conflict" else "unknown"
            latest_bad = any(value == 'not_met' for value in opinion.values())
            if answer.get("exposures_seen") or answer["kind"] == "continuation" or document["result"]["variant"]["purpose"] == "continuation":
                assisted.append(aid)
                continue
            if required and all(opinion.get(dim) == "met" for dim in required):
                # 相同 instance_data 的改写题不增加独立实例。
                instance = json.dumps(document["result"]["variant"]["instance_data"],sort_keys=True,ensure_ascii=False)
                eligible.setdefault(instance,(aid,document["result"]["variant"]["purpose"]))
        independent = list(eligible.values())
        enough = len(independent) >= 2 and any(purpose == "retest" for _,purpose in independent)
        status = "evidence_sufficient" if enough and not latest_bad else (
            "needs_repair" if latest_bad or contested else "practising" if observed else "not_started")
        result["nodes"][node_id] = {"status":status,"independent_answers":[aid for aid,_ in independent[:2]],
                                  "contested":contested[-2:],"assisted":assisted[-2:]}
    return result
