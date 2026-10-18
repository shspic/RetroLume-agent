"""F01 修复04：闭集肯定答案的实际解析、支持检查和进度合并；纯离线。"""
import copy
import json
import unittest
from decimal import Decimal
from uuid import UUID

from app.learning.contracts import canonical
from app.learning.teaching_contracts import ExerciseOutput, FeedbackOutput
from app.learning.teaching_policy import _answer_quantity, derive_support_checks
from app.learning.teaching_progress import rebuild_progress
from tests.fixtures.task100.synthetic_content import exercise, feedback


def emit(case, **values):
    # 每个实际样本输出其真实返回值，随批次 stdout 原件保存。
    print("ANSWER_SUPPORT_CASE " + json.dumps({"case": case, **values}, ensure_ascii=False, sort_keys=True))


def speed_exercise(index=0):
    value = exercise({
        "node_id": "n1", "purpose": "initial" if index == 0 else "retest",
        "parent_exercise_record_id": None if index == 0 else str(UUID(int=10)),
        "parent_feedback_record_id": None if index == 0 else str(UUID(int=30)),
    }, "lc_" + "a" * 24)
    # 使用实际合同校验，不用非法实例或错误参考使反例天然无法推进。
    return ExerciseOutput.model_validate(value).model_dump()


def progress_facts(texts):
    facts, exercises = [], []
    for index, text in enumerate(texts):
        ex = speed_exercise(index)
        exercises.append(ex)
        model = feedback({"exercise": ex, "answer_text": text}, "lc_" + "a" * 24)
        for observation in model["dimension_observations"]:
            observation["observation"] = "met"  # 故意模拟低信任模型全 met。
        model = FeedbackOutput.model_validate(model).model_dump()
        eid, aid, fid = (str(UUID(int=base + index)) for base in (10, 20, 30))
        facts.extend([
            {"kind": "exercise", "record_id": eid, "document": {
                "path_record_id": "path", "node_id": "n1", "result": ex}},
            {"kind": "answer", "record_id": aid, "body": canonical({
                "exercise_record_id": eid, "text": text, "kind": "initial", "exposures_seen": []})},
            {"kind": "feedback", "record_id": fid, "answer_record_id": aid,
             "document": {"result": model}},
        ])
    nodes = [{"node_id": "n1", "completion_dimensions": [
        {"dimension": d["id"]} for d in exercises[0]["dimensions"]]}]
    return nodes, facts, exercises


class AnswerSupportTests(unittest.TestCase):
    def test_negative_uncertain_quoted_and_open_answers_remain_unchecked(self):
        ex = speed_exercise()
        texts = [
            "平均速度不等于1m/s", "答案未知，可能1m/s",
            "不是1m/s", "1m/s不是答案", "大概1m/s", "1m/s，尚不确定",
            "也许是1m/s", "1m/s，可能不对", "参考答案是1m/s", "示例：1m/s",
            "“1m/s”", '"1m/s"', "假设答案为1m/s", "如果是1m/s",
            "1m/s？", "1m/s?", "1m/s或60m/s", "1m/s；60m/s",
            "1m/s，2分钟=120秒，但我还没有得出答案", "1m/s；先统一秒；也许不对",
            "求证1m/s", "可能1m/s也可能60m/s", "一段开放解释", "1e3m/s",
            "1E0m/s", "1m/s；2分钟=60秒", "1m/s，", "1m/s，-2分钟=-120秒",
            "1m/s，2e0分钟=120秒", "1m/s；先统一秒吗", "1m/s；先统一秒。答案未知",
        ]
        for text in texts:
            with self.subTest(answer=text):
                self.assertIsNone(_answer_quantity(text, "m/s"))
                check = derive_support_checks(ex, text)[0]
                self.assertEqual(check["reference_status"], "matched")
                self.assertEqual(check["answer_status"], "unchecked")
                self.assertEqual(check["status"], "unchecked")
                self.assertEqual(check["dimension_ids"], ["value"])
                self.assertNotIn("answer_value_decimal", check)
                emit("unknown", answer=text, support=check)

    def test_closed_positive_answers_preserve_units_and_verified_auxiliaries(self):
        ex = speed_exercise()
        texts = [
            "1m/s", "  1 m / s  ", "1米/秒", "1 米 / 秒", "1米每秒",
            "60m/min", "60 m / min", "1m/s，2分钟=120秒",
            "1m/s；先统一秒，单位与数量级合理",
            "1m/s；2分钟=120秒，先统一时间单位，数量级合理。",
            "1m/s；3分钟=180秒，先统一秒，单位与数量级合理。",
            "1m/s；2分钟=120秒，单位与数量级正确。",
            "1m/s；3分钟=180秒，先换算秒，数量级正确。",
            "1m/s，分钟乘60，数量级合理", "1m/s; 2 min = 120 s.",
        ]
        for text in texts:
            with self.subTest(answer=text):
                quantity = _answer_quantity(text, "m/s")
                self.assertIsNotNone(quantity)
                check = derive_support_checks(ex, text)[0]
                self.assertEqual(check["reference_status"], "matched")
                self.assertEqual(check["answer_status"], "matched")
                self.assertEqual(check["status"], "matched")
                self.assertTrue(check["unit_matched"])
                self.assertEqual(Decimal(check["answer_value_decimal"]), Decimal("1"))
                emit("positive", answer=text, support=check)

    def test_real_conflicts_and_reference_checks_are_separate(self):
        ex = speed_exercise()
        for text in ["60m/s", "0.01m/s", "1m"]:
            with self.subTest(answer=text):
                self.assertIsNotNone(_answer_quantity(text, "m/s"))
                check = derive_support_checks(ex, text)[0]
                self.assertEqual(check["reference_status"], "matched")
                self.assertEqual(check["answer_status"], "conflict")
                self.assertEqual(check["status"], "conflict")
                self.assertEqual(check["unit_matched"], text != "1m")
                emit("true_conflict", answer=text, support=check)
        broken = copy.deepcopy(ex)
        broken["reference_points"][0]["numeric"]["right"] = "2"
        for text, answer_status in [("1m/s", "matched"), ("答案未知，可能1m/s", "unchecked")]:
            with self.subTest(reference="broken", answer=text):
                check = derive_support_checks(broken, text)[0]
                self.assertEqual(check["reference_status"], "conflict")
                self.assertEqual(check["answer_status"], answer_status)
                self.assertEqual(check["status"], "conflict")
                emit("reference_conflict", answer=text, support=check)

    def test_unitless_approximation_and_program_text_keep_existing_discipline(self):
        ex = speed_exercise()
        ex["reference_points"][0]["numeric"].update(
            left="150", right="300", value_decimal="0.5", unit=None, tolerance_decimal="0.01")
        for text, status in [("约0.5", "matched"), (" 约 0.5 ", "matched"),
                             ("0.5", "matched"), ("不等于0.5", "unchecked"),
                             ("约0.5，但我不知道", "unchecked"), ("0.5e0", "unchecked")]:
            with self.subTest(answer=text):
                check = derive_support_checks(ex, text)[0]
                self.assertEqual(check["reference_status"], "matched")
                self.assertEqual(check["answer_status"], status)
                self.assertEqual(check["status"], status)
                emit("unitless", answer=text, support=check)
        program = exercise({"node_id": "n3", "purpose": "initial"}, "lc_" + "a" * 24)
        program["reference_points"][0]["numeric"] = {
            "value_decimal": "2", "unit": None, "operation": "add", "left": "1", "right": "1"}
        program = ExerciseOutput.model_validate(program).model_dump()
        for text in ["2", "raise AssertionError('user program executed') # 2"]:
            with self.subTest(program=text):
                check = derive_support_checks(program, text)[0]
                self.assertEqual(check["reference_status"], "matched")
                self.assertEqual(check["answer_status"], "unchecked")
                self.assertEqual(check["status"], "unchecked")
                emit("program_not_executed", answer=text, support=check)

    def test_valid_distinct_instances_block_unknown_and_allow_two_correct_answers(self):
        cases = [
            ("negative", ["平均速度不等于1m/s"] * 2, []),
            ("uncertain", ["答案未知，可能1m/s"] * 2, []),
            ("correct_then_unknown", ["1m/s", "答案未知，可能1m/s"], [str(UUID(int=20))]),
            ("unknown_then_correct", ["平均速度不等于1m/s", "60m/min"], [str(UUID(int=21))]),
            ("two_correct", ["1m/s，2分钟=120秒", "60m/min"], [str(UUID(int=20)), str(UUID(int=21))]),
        ]
        for name, texts, expected_answers in cases:
            with self.subTest(case=name):
                nodes, facts, exercises = progress_facts(texts)
                self.assertNotEqual(exercises[0]["variant"]["instance_data"], exercises[1]["variant"]["instance_data"])
                self.assertEqual([ex["variant"]["purpose"] for ex in exercises], ["initial", "retest"])
                for ex in exercises:
                    quantities = {q["name"]: q for q in ex["variant"]["instance_data"]["quantities"]}
                    numeric = ex["reference_points"][0]["numeric"]
                    self.assertEqual(Decimal(numeric["left"]), Decimal(quantities["distance"]["value_decimal"]))
                    self.assertEqual(Decimal(numeric["right"]), Decimal(quantities["time"]["value_decimal"]) * 60)
                    self.assertEqual(Decimal(numeric["value_decimal"]), Decimal("1"))
                for fact in facts:
                    if fact["kind"] == "answer":
                        self.assertEqual(json.loads(fact["body"])["exposures_seen"], [])
                    if fact["kind"] == "feedback":
                        self.assertTrue(all(d["observation"] == "met" for d in fact["document"]["result"]["dimension_observations"]))
                checks = [derive_support_checks(ex, text)[0] for ex, text in zip(exercises, texts)]
                self.assertEqual([c["reference_status"] for c in checks], ["matched", "matched"])
                projection = rebuild_progress(nodes, facts, "path")["nodes"]["n1"]
                self.assertEqual(projection["independent_answers"], expected_answers)
                self.assertEqual(projection["status"], "evidence_sufficient" if len(expected_answers) == 2 else "practising")
                self.assertEqual(projection["contested"], [])  # unknown 不伪装成冲突。
                self.assertEqual(projection["assisted"], [])
                emit(name, answers=texts, exercises=exercises, facts=facts, support=checks, projection=projection)
