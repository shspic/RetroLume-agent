"""teaching.v1 策略层定向检查：阶段前提、路径 DAG、支持性检查与进度推导。

支持性内容 oracle 使用 S1—S3 给定合成资料的有限手算/手推结论
（K01—K06），作为独立判定标准，不以模型自评替代。
"""
import unittest

from app.learning.teaching_contracts import TeachingRefusal
from app.learning.teaching_policy import (
    compute_view_token,
    derive_progress,
    derive_support_checks,
    normalize_output_for_action,
    project_public_exercise,
    validate_path,
    validate_transition,
)


class TransitionTests(unittest.TestCase):
    def test_action_phase_matrix(self):
        validate_transition("goal", "needs_plan")
        validate_transition("goal", "feedback_ready")
        with self.assertRaises(TeachingRefusal):
            validate_transition("plan", "needs_goal")
        validate_transition("plan", "needs_plan")
        validate_transition("accept_path", "path_review")
        with self.assertRaises(TeachingRefusal):
            validate_transition("accept_path", "ready")
        validate_transition("expose", "exercise_ready")
        validate_transition("answer", "answer_saved")
        validate_transition("evaluate", "answer_saved")
        with self.assertRaises(TeachingRefusal):
            validate_transition("evaluate", "ready")
        validate_transition("calculate", "answer_saved")
        validate_transition("select_node", "ready")
        validate_transition("correct", "ready")
        # 复测/续答需要 feedback_ready
        validate_transition("exercise", "feedback_ready", purpose="retest")
        with self.assertRaises(TeachingRefusal):
            validate_transition("exercise", "ready", purpose="retest")
        with self.assertRaises(TeachingRefusal):
            validate_transition("unknown_action", "ready")


class PathTests(unittest.TestCase):
    def test_node_id_assignment_and_dag(self):
        nodes = [{"prerequisites": []}, {"prerequisites": [0]}, {"prerequisites": [0, 1]}]
        self.assertEqual(validate_path(nodes), ["n1", "n2", "n3"])
        with self.assertRaises(TeachingRefusal):
            validate_path([{"prerequisites": [1]}, {"prerequisites": [0]}])
        with self.assertRaises(TeachingRefusal):
            validate_path([{"prerequisites": [0]}])
        with self.assertRaises(TeachingRefusal):
            validate_path([{"prerequisites": []}] * 7)
        with self.assertRaises(TeachingRefusal):
            validate_path([])


class SupportCheckTests(unittest.TestCase):
    """S1 数值/单位/数量级：确定运算对照，开放语义不由字符串裁判。"""

    def exercise(self, points):
        return {"reference_points": points}

    def test_s1_minute_conversion_arithmetic(self):
        # 2分钟=120秒（multiply 2*60=120）符合；120/120=1（divide）符合。
        checks = derive_support_checks(self.exercise([
            {"point_id": "p1", "numeric": {"value_decimal": "120", "operation": "multiply",
                                           "left": "2", "right": "60"}},
            {"point_id": "p2", "numeric": {"value_decimal": "1", "operation": "divide",
                                           "left": "120", "right": "120"}},
        ]), "120/120=1m/s")
        self.assertEqual([c["status"] for c in checks], ["matched", "matched"])
        # 参考本身算错时必须报冲突，不迎合作答（K13）
        wrong = derive_support_checks(self.exercise([
            {"point_id": "p2", "numeric": {"value_decimal": "60", "operation": "divide",
                                           "left": "120", "right": "2"}},
        ]), "120/2=60m/s")
        self.assertEqual(wrong[0]["status"], "matched")
        broken = derive_support_checks(self.exercise([
            {"point_id": "p2", "numeric": {"value_decimal": "1", "operation": "divide",
                                           "left": "120", "right": "2"}},
        ]), "任意作答")
        self.assertEqual(broken[0]["status"], "conflict")

    def test_s1_retest_hand_arithmetic_and_tolerance(self):
        # 复测 E2：150/300=0.5
        retest = derive_support_checks(self.exercise([
            {"point_id": "p1", "numeric": {"value_decimal": "300", "operation": "multiply",
                                           "left": "5", "right": "60"}},
            {"point_id": "p2", "numeric": {"value_decimal": "0.5", "operation": "divide",
                                           "left": "150", "right": "300"}},
        ]), "150/300=0.5m/s")
        self.assertEqual([c["status"] for c in retest], ["matched", "matched"])
        approximate = derive_support_checks(self.exercise([
            {"point_id": "p2", "numeric": {"value_decimal": "0.5", "operation": "divide",
                                           "left": "150", "right": "300",
                                           "tolerance_decimal": "0.01"}}]), "约0.5")
        self.assertEqual(approximate[0]["status"], "matched")

    def test_unchecked_when_no_numeric_reference(self):
        checks = derive_support_checks(self.exercise([
            {"point_id": "p1", "numeric": None},
            {"point_id": "p4", "numeric": {"value_decimal": "NaN", "operation": "add",
                                           "left": "1", "right": "1"}},
            {"point_id": "p3", "numeric": {"value_decimal": "1", "operation": "divide",
                                           "left": "1", "right": "0"}},
        ]), "任意自然语言")
        # 非数值参考点不产生检查项；非有限域输入（NaN）与除零不硬评分，
        # 只能是 unchecked——conflict 会参与推进裁决，不能由非法数值伪造。
        by_id = {c["point_id"]: c["status"] for c in checks}
        self.assertNotIn("p1", by_id)
        self.assertEqual(by_id.get("p4"), "unchecked")
        self.assertEqual(by_id.get("p3"), "unchecked")
        self.assertNotIn("conflict", by_id.values())

    def test_program_question_is_never_executed(self):
        code = {"reference_points": [{"point_id": "p1", "numeric": {"value_decimal": "2",
                                     "operation": "add", "left": "1", "right": "1"}}]}
        # 只做同一有限域的算术对照；代码文本本身不进入本函数
        self.assertEqual(derive_support_checks(code, "def f(): import os")[0]["status"], "matched")


class ProgressTests(unittest.TestCase):
    def feedback(self, observations):
        return {"dimension_observations": [{"id": d, "observation": o, "reason": "r", "point_ids": []}
                                          for d, o in observations]}

    def test_two_independent_instances_required(self):
        one = derive_progress(self.feedback([("conversion", "met")]), ["a1"], ["conversion"])
        self.assertEqual(one["status"], "practising")
        self.assertFalse(one["advance"])
        two = derive_progress(self.feedback([("conversion", "met")]), ["a1", "a2"], ["conversion"])
        self.assertEqual(two["status"], "evidence_sufficient")
        self.assertTrue(two["advance"])
        # 一次正确不毕业：同题重复只按不同 answer ID 计数
        same_answer = derive_progress(self.feedback([("conversion", "met")]), ["a1", "a1"], ["conversion"])
        self.assertEqual(same_answer["status"], "practising")

    def test_partial_unknown_and_errors(self):
        self.assertEqual(derive_progress(self.feedback([("conversion", "partial")]),
                                         ["a1", "a2"], ["conversion"])["status"], "practising")
        self.assertEqual(derive_progress(self.feedback([("conversion", "unknown")]),
                                         ["a1", "a2"], ["conversion"])["status"], "practising")
        self.assertEqual(derive_progress(self.feedback([("conversion", "not_met")]),
                                         ["a1", "a2"], ["conversion"])["status"], "needs_repair")
        mixed = derive_progress(self.feedback([("conversion", "met"), ("reason", "not_met")]),
                                ["a1", "a2"], ["conversion", "reason"])
        self.assertEqual(mixed["status"], "needs_repair")
        # 无长期 mastered 语义
        self.assertNotIn("mastered", str(derive_progress(self.feedback([("conversion", "met")]),
                                                        ["a1", "a2"], ["conversion"])))


class PublicProjectionTests(unittest.TestCase):
    def test_reference_hidden_until_exposed(self):
        exercise = {"exercise_type": "calculation", "difficulty": 1, "stem": "题",
                    "dimensions": [{"id": "conversion", "point_ids": ["p1"], "description": "d"}],
                    "variant": {"purpose": "initial"}, "hint": "提示文本",
                    "reference_points": [{"point_id": "p1", "text": "2分钟=120秒", "citations": []}],
                    "reference_explanation": "先统一秒"}
        hidden = project_public_exercise(exercise, set())
        self.assertNotIn("reference_points", hidden)
        self.assertNotIn("reference_explanation", hidden)
        self.assertNotIn("hint", hidden)
        self.assertFalse(hidden["reference_available"])
        hinted = project_public_exercise(exercise, {"hint"})
        self.assertEqual(hinted["hint"], "提示文本")
        self.assertNotIn("reference_points", hinted)
        shown = project_public_exercise(exercise, {"hint", "reference"})
        self.assertEqual(shown["reference_points"][0]["point_id"], "p1")
        self.assertTrue(shown["reference_available"])


class ViewTokenTests(unittest.TestCase):
    def test_token_changes_with_revision_scope_and_source(self):
        a = compute_view_token(1, 2, 3, "s1", "c1")
        self.assertNotEqual(a, compute_view_token(2, 2, 3, "s1", "c1"))
        self.assertNotEqual(a, compute_view_token(1, 3, 3, "s1", "c1"))
        self.assertNotEqual(a, compute_view_token(1, 2, 4, "s1", "c1"))
        self.assertNotEqual(a, compute_view_token(1, 2, 3, "s2", "c1"))
        self.assertNotEqual(a, compute_view_token(1, 2, 3, "s1", "c2"))
        self.assertEqual(a, compute_view_token(1, 2, 3, "s1", "c1"))


class OutputNormalisationTests(unittest.TestCase):
    def test_failure_codes_are_closed(self):
        with self.assertRaises(TeachingRefusal) as ctx:
            normalize_output_for_action('{"result_type":"path","message":"x","nodes":[]}', "plan")
        self.assertEqual(ctx.exception.code, "invalid_teaching_output")
        with self.assertRaises(TeachingRefusal):
            normalize_output_for_action('{"result_type":"feedback","message":"x","correct_parts":[],'
                                        '"errors":[],"evidence_gaps":[],"cause_hypotheses":[],'
                                        '"dimension_observations":[],"next_focus":{"focus_dimension":"d",'
                                        '"reason":"r","suggested_mode":"retest"}}', "evaluate")
        with self.assertRaises(TeachingRefusal):
            normalize_output_for_action("x" * 16385, "plan")


if __name__ == "__main__":
    unittest.main()
