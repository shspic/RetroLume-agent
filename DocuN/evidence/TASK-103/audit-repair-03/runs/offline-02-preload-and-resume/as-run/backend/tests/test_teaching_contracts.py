"""teaching.v1 命令合同、canonical、语义槽与低信任输出联合的定向检查。

全部为纯合同检查：不联网、不 exec/eval、不需要数据库。
"""
import json
import unittest
from uuid import uuid4

from pydantic import ValidationError

from app.learning.teaching_contracts import (
    MAX_GOAL_VERSION,
    TEACHING_PREFIX_MODEL,
    TEACHING_PREFIX_TOOL,
    AnswerBody,
    ExerciseBody,
    FeedbackOutput,
    GoalBody,
    PathOutput,
    TeachingCommandInput,
    TeachingProfile,
    TeachingRefusal,
    parse_teaching_output,
    semantic_slot,
    validate_exposed_part,
)
from app.learning.contracts import canonical, sha

ACTIVITY = str(uuid4())


def command(action="goal", *, revision=0, goal_version=0, scope=1, body=None):
    defaults = {
        "goal": {"goal": "能正确换算平均速度并说明数量级", "self_report": None, "domain": None,
                 "seed_operation_id": None, "seed_payload_sha256": None},
        "plan": {"confirmed": True, "correction_record_id": None, "retry_of": None},
        "accept_path": {"proposal_record_id": str(uuid4())},
        "exercise": {"confirmed": True, "path_record_id": str(uuid4()), "node_id": "n1",
                     "purpose": "initial", "parent_feedback_record_id": None, "retry_of": None},
        "expose": {"exercise_record_id": str(uuid4()), "part": "reference"},
        "answer": {"exercise_record_id": str(uuid4()), "kind": "initial", "text": "120÷120=1m/s",
                   "supersedes_answer_record_id": None},
        "calculate": {"confirmed": True, "exercise_record_id": str(uuid4()),
                      "answer_record_id": str(uuid4()), "reference_point_id": "p1", "retry_of": None},
        "evaluate": {"confirmed": True, "exercise_record_id": str(uuid4()),
                     "answer_record_id": str(uuid4()), "correction_record_id": None, "retry_of": None},
        "correct": {"target_record_id": str(uuid4()), "text": "上一题是笔误", "disputed_dimensions": []},
        "abandon": {"target_business_key": str(uuid4())},
        "select_node": {"path_record_id": str(uuid4()), "node_id": "n2", "archive_current": False},
    }
    return TeachingCommandInput(business_key=str(uuid4()), expected_revision=revision,
                                expected_goal_version=goal_version, expected_scope_revision=scope,
                                action=action, body=defaults[action] if body is None else body)


class TeachingCommandContractTests(unittest.TestCase):
    def test_canonical_request_body_and_operation_identity(self):
        c = command("goal")
        body = c.canonical_request_body(ACTIVITY)
        self.assertEqual(set(body), {"activity_id", "action", "expected_revision",
                                     "expected_goal_version", "expected_scope_revision", "body"})
        self.assertEqual(c.request_sha256(ACTIVITY), sha(canonical(body)))
        # 业务键不在内容摘要内：换键同内容 request_sha 相同。
        other = TeachingCommandInput(business_key=str(uuid4()), expected_revision=0,
                                     expected_goal_version=0, expected_scope_revision=1,
                                     action="goal", body=c.body)
        self.assertEqual(other.request_sha256(ACTIVITY), c.request_sha256(ACTIVITY))
        self.assertEqual(c.operation_id(ACTIVITY),
                         TEACHING_PREFIX_MODEL + c.business_key + "." + c.request_sha256(ACTIVITY))
        calculate = command("calculate", revision=3, goal_version=1, scope=2)
        self.assertTrue(calculate.operation_id(ACTIVITY).startswith(TEACHING_PREFIX_TOOL))
        self.assertLessEqual(len(calculate.operation_id(ACTIVITY)), 128)

    def test_strict_fields_extras_and_integer_rejection(self):
        with self.assertRaises(ValidationError):
            TeachingCommandInput(business_key=str(uuid4()), expected_revision=0, expected_goal_version=0,
                                 expected_scope_revision=1, action="goal",
                                 body={"goal": "x", "extra": 1})
        with self.assertRaises(ValidationError):
            command("answer", body={"exercise_record_id": str(uuid4()), "kind": "initial",
                                    "text": "x", "supersedes_answer_record_id": str(uuid4())})
        with self.assertRaises(ValidationError):
            command("plan", body={"confirmed": False})
        with self.assertRaises(ValidationError):
            command("plan", body={"confirmed": True, "retry_of": "not-a-uuid"})
        # expected_goal_version=0 仅首次 goal
        with self.assertRaises(ValidationError):
            command("plan", goal_version=0)

    def test_size_domains(self):
        with self.assertRaises(ValidationError):
            GoalBody(goal="x" * 1025, self_report=None, domain=None,
                     seed_operation_id=None, seed_payload_sha256=None)
        with self.assertRaises(ValidationError):
            GoalBody(goal="速" * 1366, self_report=None, domain=None,
                     seed_operation_id=None, seed_payload_sha256=None)  # 4096 字节上限
        with self.assertRaises(ValidationError):
            AnswerBody(exercise_record_id=str(uuid4()), kind="initial", text="x" * 4097,
                       supersedes_answer_record_id=None)
        with self.assertRaises(ValidationError):
            command("correct", body={"target_record_id": str(uuid4()), "text": "x" * 1025,
                                     "disputed_dimensions": []})
        # 作答保留缩进与空行
        kept = AnswerBody(exercise_record_id=str(uuid4()), kind="initial",
                          text="  行1\n\n行2  ", supersedes_answer_record_id=None)
        self.assertEqual(kept.text, "  行1\n\n行2  ")
        with self.assertRaises(ValidationError):
            AnswerBody(exercise_record_id=str(uuid4()), kind="initial", text="   ",
                       supersedes_answer_record_id=None)
        with self.assertRaises(ValidationError):
            AnswerBody(exercise_record_id=str(uuid4()), kind="continuation", text="x",
                       supersedes_answer_record_id=None)

    def test_semantic_slot_excludes_key_and_text(self):
        base = command("answer", revision=3, goal_version=1)
        same_slot = semantic_slot(ACTIVITY, base, {})
        changed_text = command("answer", revision=3, goal_version=1, body={**base.body, "text": "完全不同"})
        self.assertEqual(same_slot, semantic_slot(ACTIVITY, changed_text, {}))
        # kind/supersedes 属于父槽（决定语义阶段），不是文本内容
        continuation = command("answer", revision=3, goal_version=1,
                               body={**base.body, "kind": "continuation",
                                     "supersedes_answer_record_id": str(uuid4())})
        self.assertNotEqual(same_slot, semantic_slot(ACTIVITY, continuation, {}))
        goal = command("goal", revision=4, goal_version=1)
        self.assertNotEqual(same_slot, semantic_slot(ACTIVITY, goal, {}))
        # scope 身份进入槽
        self.assertNotEqual(same_slot, semantic_slot(ACTIVITY, command(
            "answer", revision=3, goal_version=1, scope=2, body=base.body), {}))

    def test_output_union_paths_and_neutral_results(self):
        path = parse_teaching_output(json.dumps({
            "result_type": "path", "message": "建议三步",
            "nodes": [{"title": "单位", "objective": "统一时间单位", "prerequisites": [],
                       "rationale": "先统一秒", "citations": ["lc_" + "a" * 24],
                       "completion_dimensions": [{"dimension": "conversion", "required_point": "先换算"}]},
                      {"title": "数量级", "objective": "检查数量级", "prerequisites": [0],
                       "rationale": "数量级检查", "citations": ["lc_" + "a" * 24],
                       "completion_dimensions": [{"dimension": "order", "required_point": "数量级约1"}]}]}), "plan")
        self.assertEqual(path["result_type"], "path")
        for raw, action in ((json.dumps({"result_type": "clarification", "message": "缺什么",
                                         "questions": ["请说明领域"]}), "plan"),
                            (json.dumps({"result_type": "no_evidence", "message": "无证据",
                                         "missing": ["缺并发轨迹"]}), "plan"),
                            (json.dumps({"result_type": "conflict", "message": "两说不同",
                                         "claims": [{"text": "A", "citations": ["lc_" + "a" * 24]},
                                                    {"text": "B", "citations": ["lc_" + "b" * 24]}]}), "plan")):
            self.assertIn("result_type", parse_teaching_output(raw, action))
        # 重复字段/非有限数/越界
        with self.assertRaises(ValueError):
            parse_teaching_output('{"result_type":"clarification","result_type":"conflict","message":"x","claims":[]}', "plan")
        with self.assertRaises(ValueError):
            parse_teaching_output(json.dumps({"result_type": "clarification", "message": "x",
                                              "questions": ["a" * 161]}), "plan")
        with self.assertRaises(ValueError):
            parse_teaching_output('{"result_type":"path","message":"x","nodes":[]}', "plan")

    def test_trusted_fields_rejected_not_stripped(self):
        for value in ({"result_type": "path", "message": "x", "nodes": [], "passed": True},
                      {"result_type": "path", "message": "x", "nodes": [], "mastered": True},
                      {"result_type": "path", "message": "x", "nodes": [], "goal_version": 2}):
            with self.assertRaises(ValueError):
                parse_teaching_output(json.dumps(value), "plan")
        feedback = {
            "result_type": "feedback", "message": "评价",
            "correct_parts": [{"answer_excerpt": "120÷2=60", "explanation": "商正确",
                               "point_ids": ["p1"], "citations": []}],
            "errors": [{"answer_excerpt": "60 m/s", "explanation": "未换算",
                        "point_ids": ["p1"], "citations": []}],
            "evidence_gaps": [], "cause_hypotheses": [
                {"hypothesis": "可能忘换算", "evidence_for": "单位正确但数值大60倍",
                 "missing_evidence": "无统一秒过程", "confidence": "tentative"}],
            "dimension_observations": [{"id": "conversion", "observation": "not_met",
                                        "reason": "未统一时间单位", "point_ids": ["p1"]}],
            "next_focus": {"focus_dimension": "conversion", "reason": "先统一秒",
                           "suggested_mode": "continuation"}}
        parsed = parse_teaching_output(json.dumps(feedback), "evaluate")
        self.assertEqual(parsed["result_type"], "feedback")
        self.assertEqual(parsed["cause_hypotheses"][0]["confidence"], "tentative")
        with self.assertRaises(ValueError):
            parse_teaching_output(json.dumps({**feedback, "progress": True}), "evaluate")

    def test_path_prerequisites_must_reference_earlier_nodes(self):
        with self.assertRaises(ValueError):
            parse_teaching_output(json.dumps({
                "result_type": "path", "message": "x",
                "nodes": [{"title": "a", "objective": "o", "prerequisites": [1], "rationale": "r",
                           "citations": ["lc_" + "a" * 24],
                           "completion_dimensions": [{"dimension": "d", "required_point": "p"}]},
                          {"title": "b", "objective": "o", "prerequisites": [0], "rationale": "r",
                           "citations": ["lc_" + "a" * 24],
                           "completion_dimensions": [{"dimension": "d", "required_point": "p"}]}]}), "plan")
        with self.assertRaises(ValueError):
            parse_teaching_output(json.dumps({
                "result_type": "path", "message": "x",
                "nodes": [{"title": f"n{i}", "objective": "o", "prerequisites": [],
                           "rationale": "r", "citations": ["lc_" + "a" * 24],
                           "completion_dimensions": [{"dimension": "d", "required_point": "p"}]}
                          for i in range(7)]}), "plan")

    def test_exercise_variant_binding_and_code_limits(self):
        base = {
            "result_type": "exercise", "message": "题", "exercise_type": "calculation", "difficulty": 1,
            "stem": "骑行120米用时2分钟，求平均速度",
            "reference_points": [{"point_id": "p1", "text": "2分钟=120秒",
                                  "citations": ["lc_" + "a" * 24],
                                  "numeric": {"value_decimal": "120", "unit": None,
                                              "operation": "multiply", "left": "2", "right": "60"}}],
            "reference_explanation": "先统一秒再除",
            "dimensions": [{"id": "conversion", "point_ids": ["p1"], "description": "统一时间单位"}],
            "hint": "先换算时间",
            "variant": {"purpose": "initial", "parent_exercise_record_id": None,
                        "parent_feedback_record_id": None,
                        "instance_data": {"kind": "calculation", "quantities": [
                            {"name": "distance", "value_decimal": "120", "unit": "m"}]}}}
        parsed = parse_teaching_output(json.dumps(base), "exercise")
        self.assertEqual(parsed["variant"]["purpose"], "initial")
        # initial 不得带父引用
        with self.assertRaises(ValueError):
            parse_teaching_output(json.dumps({**base, "variant": {**base["variant"],
                         "parent_exercise_record_id": str(uuid4())}}), "exercise")
        # 程序题只作纯文本且有行数/字节上限
        program = {**base, "exercise_type": "program",
                   "variant": {"purpose": "initial", "parent_exercise_record_id": None,
                               "parent_feedback_record_id": None,
                               "instance_data": {"kind": "program", "language": "Python",
                                                 "code": "def f():\n    return 1\n",
                                                 "inputs": [{"name": "x", "value_json": "1"}],
                                                 "manual_expected": "1"}}}
        self.assertEqual(parse_teaching_output(json.dumps(program), "exercise")["exercise_type"], "program")
        with self.assertRaises(ValueError):
            parse_teaching_output(json.dumps({**program, "variant": {"purpose": "initial",
                         "parent_exercise_record_id": None, "parent_feedback_record_id": None,
                         "instance_data": {**program["variant"]["instance_data"],
                                           "code": "\n".join(f"x{i}=1" for i in range(40))}}}), "exercise")
        with self.assertRaises(ValueError):
            parse_teaching_output(json.dumps({**program, "variant": {"purpose": "initial",
                         "parent_exercise_record_id": None, "parent_feedback_record_id": None,
                         "instance_data": {**program["variant"]["instance_data"], "language": "Java"}}}), "exercise")

    def test_exposed_part_closed_union(self):
        self.assertEqual(validate_exposed_part({"part": "hint", "text": "先换算"})["part"], "hint")
        reference = validate_exposed_part({"part": "reference",
                                           "reference_points": [{"point_id": "p1", "text": "2分钟=120秒"}],
                                           "reference_explanation": "先统一秒"})
        self.assertEqual(reference["part"], "reference")
        for value in ({"part": "reference", "reference_points": [],
                       "reference_explanation": "x"},
                      {"part": "reference", "reference_points": [{"point_id": "p1", "text": "x"}]},
                      {"part": "other"},
                      {"part": "hint", "text": ""}, {"part": "hint", "text": "x" * 241}):
            with self.assertRaises(ValueError):
                validate_exposed_part(value)


if __name__ == "__main__":
    unittest.main()
