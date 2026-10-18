# F01 调用传播与证据级别

本件为最终未变源码的 B 级调用依据，不是本轮 PG 提交、SQL 查询或读面运行。实际离线返回值见 case-results.json 及 batch-01/stdout.txt。

实际 support 为 unchecked、dimension_ids=[value]；下列真实 rebuild_progress 将该维度 opinion 收紧为 unknown。返回投影不公开 opinion，本轮不虚构 observation/advance 返回字段；A 级证据为真实函数返回 practising、空 independent_answers/contested/assisted，unknown 内部赋值依据此处 B 级源码。

仓储导入同一 derive_support_checks；_teaching_rebuild_progress 对真实读取事实调用同一 rebuild_progress；当前反馈提交后据该投影选择下一节点，support_checks 使用保存的真实 answer 正文。没有更改这些调用点，也没有重新执行数据库链。

## backend/app/learning/teaching_progress.py

第 4—7 行：

```python
4: import json
5: 
6: from .teaching_policy import derive_support_checks
7: 
```

第 41—72 行：

```python
41:             latest = normal[-1]
42:             output = latest["document"]["result"]
43:             opinions = [{d["id"]:d["observation"] for d in v["document"]["result"]["dimension_observations"]} for v in normal]
44:             conflict = len({json.dumps(v,sort_keys=True) for v in opinions}) > 1
45:             disputed = any(str(v["record_id"]) in corrections for v in versions)
46:             checks = derive_support_checks(document["result"], answer["text"])
47:             conflict = conflict or any(c["status"] == "conflict" for c in checks)
48:             if disputed or conflict:
49:                 contested.append(aid)
50:                 continue
51:             opinion = opinions[-1]
52:             # 确定核查只收紧模型观察；解析不足也不冒充该数值维度已核定。
53:             opinion = dict(opinion)
54:             for check in checks:
55:                 for dimension in check.get("dimension_ids", []):
56:                     if check["status"] != "matched":
57:                         opinion[dimension] = "not_met" if check["status"] == "conflict" else "unknown"
58:             latest_bad = any(value == 'not_met' for value in opinion.values())
59:             if answer.get("exposures_seen") or answer["kind"] == "continuation" or document["result"]["variant"]["purpose"] == "continuation":
60:                 assisted.append(aid)
61:                 continue
62:             if required and all(opinion.get(dim) == "met" for dim in required):
63:                 # 相同 instance_data 的改写题不增加独立实例。
64:                 instance = json.dumps(document["result"]["variant"]["instance_data"],sort_keys=True,ensure_ascii=False)
65:                 eligible.setdefault(instance,(aid,document["result"]["variant"]["purpose"]))
66:         independent = list(eligible.values())
67:         enough = len(independent) >= 2 and any(purpose == "retest" for _,purpose in independent)
68:         status = "evidence_sufficient" if enough and not latest_bad else (
69:             "needs_repair" if latest_bad or contested else "practising" if observed else "not_started")
70:         result["nodes"][node_id] = {"status":status,"independent_answers":[aid for aid,_ in independent[:2]],
71:                                   "contested":contested[-2:],"assisted":assisted[-2:]}
72:     return result
```

## backend/app/activities/teaching_repository.py

第 40—45 行：

```python
40:     TeachingRefusal,
41:     semantic_slot,
42: )
43: from app.learning.contracts import canonical, sha
44: from app.learning.teaching_policy import validate_transition, validate_path, derive_support_checks
45: 
```

第 410—437 行：

```python
410:     async def _teaching_rebuild_progress(self, connection, activity_id, head, extra=None):
411:         path = await self._teaching_read_record_row(connection, activity_id, head["path_record_id"])
412:         path_body = await self._teaching_fact_result(connection, activity_id, path)
413:         cursor = await connection.execute(
414:             "SELECT r.*,p.parent_record_id AS correction_feedback_id,o.payload,o.payload_format,o.payload_sha256 FROM teaching_records r "
415:             "LEFT JOIN teaching_records p ON p.activity_id=r.activity_id AND p.record_id=r.parent_record_id AND r.kind='correction' AND p.kind='progress' "
416:             "LEFT JOIN activity_operation_results o ON o.activity_id=r.activity_id AND o.operation_id=r.operation_id "
417:             "WHERE r.activity_id=%s AND r.goal_version=%s AND r.kind=ANY(%s) ORDER BY r.seq",
418:             (activity_id,head["goal_version"],["exercise","answer","feedback","correction"]))
419:         facts = await cursor.fetchall()
420:         if extra:
421:             facts.append(extra)
422:         from app.capabilities.contracts import validate_business_payload
423:         for row in facts:
424:             if row.get('correction_feedback_id'):
425:                 row['parent_record_id']=row['correction_feedback_id']
426:             if row["operation_id"]:
427:                 try:
428:                     validate_business_payload(row["payload"],row["payload_format"],row["payload_sha256"])
429:                     if row["body_sha256"] != row["payload_sha256"]:
430:                         raise ValueError
431:                     row["document"] = _decode(row["payload"])["value"]
432:                 except (ValueError,TypeError,KeyError):
433:                     raise TeachingRefusal("integrity_error","当前观察正文不完整") from None
434:             elif sha(row["body"]) != row["body_sha256"]:
435:                 raise TeachingRefusal("integrity_error","当前观察摘要不一致")
436:         from app.learning.teaching_progress import rebuild_progress
437:         return rebuild_progress(path_body["nodes"],facts,str(head["path_record_id"])),path_body["nodes"]
```

第 1270—1293 行：

```python
1270:             if current and normal:
1271:                 projection,nodes = await self._teaching_rebuild_progress(connection,activity_id,head)
1272:                 current_node = projection["nodes"][head["node_id"]]
1273:                 candidate = None
1274:                 if current_node["status"] == "evidence_sufficient":
1275:                     candidate = next((n["node_id"] for n in nodes if projection["nodes"][n["node_id"]]["status"] != "evidence_sufficient"
1276:                         and all(projection["nodes"][f"n{p+1}"]["status"] == "evidence_sufficient" for p in n["prerequisites"])),None)
1277:                 progress_id = str(uuid4())
1278:                 seq += 1
1279:                 reason = "按当前评价已有两个不同的独立实例，含复测，可有限前进。" if candidate else "保留当前节点；独立实例不足、存在辅助或争议时不推定长期掌握。"
1280:                 progress_body = canonical({"feedback_record_id":record_id,"answer_record_id":body["answer_record_id"],
1281:                     "advance":bool(candidate),"node_before":head["node_id"],"node_after":candidate or head["node_id"],
1282:                     "reason":reason,"observations":current_node,"support_checks":derive_support_checks(
1283:                         await self._teaching_fact_result(connection,activity_id,reference_rows[body["exercise_record_id"]]),
1284:                         _decode(reference_rows[body["answer_record_id"]]["body"])["text"])})
1285:                 final_head.update(reason_record_id=progress_id,projection=projection)
1286:                 if candidate:
1287:                     final_head.update(node_id=candidate,phase="ready",exercise_record_id=None,answer_record_id=None,feedback_record_id=None)
1288:                 await self._teaching_insert_record(connection,activity_id,progress_id,seq,"progress",key,3,
1289:                     command["goal_version"],command["scope_revision"],progress_body,sha(progress_body),goal_record_id=goal["record_id"],
1290:                     parent_record_id=record_id,exercise_record_id=body["exercise_record_id"],answer_record_id=body["answer_record_id"],
1291:                     source_refs=source_refs,applied_revision=new_revision,state_after=_state_after(new_revision,final_head))
1292:         if current:
1293:             await self._teaching_update_head(connection,activity_id,head,new_revision,phase=final_head["phase"],
```
