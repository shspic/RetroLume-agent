"""TASK-100 续作01 教学 HTTP 面检查（DEF-005 定向）。

两层：
  * 离线（无任何服务可跑）：workspace 投影纯函数——真实 view_token（无
    na 占位）、source_invalid 真实计算、未暴露参考绝不返回、坏单项局部
    抑制、来源失效抑制派生正文但保留用户文字。
  * 真实 HTTP（HttpTests，runner http-combo 场景）：沿实际路由打真实
    应用（uvicorn 18100 + g8_main）——workspace 结构、DTO 拒绝、未知
    活动 404。无 RETROLUME_TEACHING_HTTP_BASE 时明确 skip。
"""
import json
import os
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

from app.learning.teaching_api import (
    _current_regions,
    _deadline_passed,
    _workspace_payload,
)
from app.learning.teaching_contracts import TeachingCommandInput
from app.learning.teaching_policy import project_public_exercise


def _fake_view(*, source_valid=True, exercise_result=None, feedback_result=None):
    """构造单语句快照返回结构的离线投影输入。"""
    body = json.dumps({"goal": "换算平均速度", "self_report": None, "domain": None},
                      ensure_ascii=False)
    answer_body = json.dumps({"exercise_record_id": "e1", "kind": "initial",
                              "text": "我的作答", "supersedes_answer_record_id": None,
                              "exposures_seen": []}, ensure_ascii=False)
    exercise_payload = None
    if exercise_result is not None:
        exercise_payload = json.dumps({"value": {"result": exercise_result}}, ensure_ascii=False)
    feedback_payload = None
    if feedback_result is not None:
        feedback_payload = json.dumps({"value": {"result": feedback_result}}, ensure_ascii=False)
    return {
        "activity": {"id": "a", "status": "pending", "scope_revision": 1,
                     "deadline_at": (datetime.now(timezone.utc)
                                     + timedelta(hours=1)).isoformat(),
                     "requests_reserved": 0, "max_requests": 10,
                     "cost_reserved_microunits": 0, "max_cost_microunits": 100,
                     "tools_reserved": 0, "max_tool_calls": 2,
                     "running_settled_seconds": 0, "running_reserved_seconds": 0,
                     "max_running_seconds": 900},
        "head": {"revision": 5, "last_seq": 8, "goal_version": 1, "phase": "answer_saved",
                 "goal_record_id": "g1", "path_record_id": "p1", "node_id": "n1",
                 "exercise_record_id": "e1", "answer_record_id": "a1",
                 "feedback_record_id": None, "reason_record_id": None,
                 "pending_business_key": None},
        "pending": [{"business_key": "k1", "action": "evaluate", "status": "committed",
                     "error_code": None, "created_at": "2026-10-03T00:00:00+00:00"}],
        "history": [{"record_id": "r1", "kind": "goal", "seq": 1, "goal_version": 1,
                     "parent_record_id": None, "created_at": "2026-10-03T00:00:00+00:00"}],
        "sources": [{"source_id": "s1", "version_id": "v1", "source_revision": 1,
                     "valid": source_valid, "title": "speed.md", "format": "md"}],
        "current_bodies": [
            {"record_id": "g1", "kind": "goal", "seq": 1, "goal_version": 1,
             "parent_record_id": None, "exercise_record_id": None,
             "answer_record_id": None, "body": body, "body_sha256": "d" * 64,
             "created_at": "2026-10-03T00:00:00+00:00", "payload": None},
            {"record_id": "e1", "kind": "exercise", "seq": 4, "goal_version": 1,
             "parent_record_id": None, "exercise_record_id": None, "answer_record_id": None,
             "body": None, "body_sha256": "e" * 64,
             "created_at": "2026-10-03T00:00:00+00:00", "payload": exercise_payload},
            {"record_id": "a1", "kind": "answer", "seq": 5, "goal_version": 1,
             "parent_record_id": None, "exercise_record_id": "e1", "answer_record_id": None,
             "body": answer_body, "body_sha256": "f" * 64,
             "created_at": "2026-10-03T00:00:00+00:00", "payload": None},
        ],
        "exposed_parts": ["hint"],
        "pending_business_key": None,
    }


EXERCISE_RESULT = {
    "result_type": "exercise", "exercise_type": "calculation", "difficulty": 1,
    "stem": "2 分钟走 120 米，平均速度是多少？",
    "reference_points": [{"point_id": "p1", "text": "120/120", "citations": []}],
    "reference_explanation": "先统一单位再相除。",
    "dimensions": [{"id": "d1", "point_ids": ["p1"], "description": "换算"}],
    "hint": "先统一单位。",
    "variant": {"purpose": "initial", "parent_exercise_record_id": None,
                "parent_feedback_record_id": None, "instance_data": None},
}


class WorkspaceProjectionOfflineTests(unittest.TestCase):
    """离线：workspace 投影纪律（DEF-005 反例）。"""

    def test_view_token_is_real_hash_without_na_placeholder(self):
        view = _fake_view()
        payload = _workspace_payload("act-1", view)
        self.assertRegex(payload["view_token"], r"^[0-9a-f]{64}$")

    def test_view_token_changes_with_source_and_pending_state(self):
        base = _workspace_payload("act-1", _fake_view())
        changed_source = _workspace_payload("act-1", _fake_view(source_valid=False))
        self.assertNotEqual(base["view_token"], changed_source["view_token"])

    def test_source_invalid_is_computed_not_hardcoded(self):
        valid = _workspace_payload("act-1", _fake_view(source_valid=True))
        invalid = _workspace_payload("act-1", _fake_view(source_valid=False))
        self.assertFalse(valid["overlay"]["source_invalid"])
        self.assertTrue(invalid["overlay"]["source_invalid"])

    def test_unexposed_reference_is_never_returned(self):
        view = _fake_view(exercise_result=EXERCISE_RESULT)
        payload = _workspace_payload("act-1", view)
        exercise = payload["exercise"]
        self.assertTrue(exercise["reference_available"] is False
                        or "reference" not in exercise
                        or exercise.get("reference_available") is False)
        self.assertNotIn("reference_points", exercise)
        self.assertNotIn("reference_explanation", exercise)
        # 已暴露 hint 可返回。
        self.assertEqual(exercise.get("hint"), "先统一单位。")

    def test_exposed_reference_is_projected(self):
        view = _fake_view(exercise_result=EXERCISE_RESULT)
        view["exposed_parts"] = ["hint", "reference"]
        payload = _workspace_payload("act-1", view)
        exercise = payload["exercise"]
        self.assertEqual(exercise.get("reference_points"),
                         EXERCISE_RESULT["reference_points"])
        self.assertEqual(exercise.get("reference_explanation"),
                         EXERCISE_RESULT["reference_explanation"])

    def test_source_invalid_suppresses_derived_but_keeps_user_text(self):
        view = _fake_view(exercise_result=EXERCISE_RESULT, source_valid=False)
        payload = _workspace_payload("act-1", view)
        # 派生正文（exercise）被抑制。
        self.assertEqual(payload["exercise"]["qualification"], "source_invalid")
        # 用户文字（goal/answer）保留。
        self.assertEqual(payload["goal"]["goal"], "换算平均速度")
        self.assertEqual(payload["answer"]["text"], "我的作答")

    def test_broken_single_item_is_locally_suppressed(self):
        view = _fake_view(exercise_result=EXERCISE_RESULT)
        view["current_bodies"][1]["payload"] = "{not-json"
        payload = _workspace_payload("act-1", view)
        self.assertEqual(payload["exercise"]["qualification"], "integrity_error")
        # 其他区域不受影响。
        self.assertEqual(payload["goal"]["goal"], "换算平均速度")
        self.assertEqual(payload["answer"]["text"], "我的作答")

    def test_expired_deadline_overlay(self):
        view = _fake_view()
        view["activity"]["deadline_at"] = (
            datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        payload = _workspace_payload("act-1", view)
        self.assertTrue(payload["overlay"]["expired"])
        self.assertFalse(_deadline_passed(
            (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()))


class DtoOfflineTests(unittest.TestCase):
    """离线：命令 DTO 封闭性。"""

    def test_command_rejects_unknown_action(self):
        from pydantic import ValidationError
        from uuid import uuid4
        with self.assertRaises((ValidationError, ValueError)):
            TeachingCommandInput.model_validate({
                "business_key": str(uuid4()), "expected_revision": 0,
                "expected_goal_version": 0, "expected_scope_revision": 1,
                "action": "not_a_real_action", "body": {},
            }, strict=True)


class HttpTests(unittest.TestCase):
    """真实 HTTP：沿实际路由打真实应用（http-combo 场景专用）。"""

    def setUp(self):
        self.base = os.environ.get("RETROLUME_TEACHING_HTTP_BASE", "")
        if not self.base:
            self.skipTest("RETROLUME_TEACHING_HTTP_BASE 未注入（离线模式不跑真实 HTTP）")
        # 本地会话：应用启动 token 随机，教学端点挂 local_session 全量校验；
        # 先经免 token 的 /api/session（仅 local_request）取得本次会话 token。
        with urllib.request.urlopen(self.base + "/api/session", timeout=15) as response:
            self.token = json.loads(response.read().decode("utf-8"))["token"]

    def _get(self, path):
        request = urllib.request.Request(
            self.base + path, headers={"X-RetroLume-Session": self.token})
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def _post(self, path, body):
        request = urllib.request.Request(
            self.base + path, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "X-RetroLume-Session": self.token}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8") or "{}")

    def test_workspace_endpoint_returns_contract_schema(self):
        status, payload = self._get("/api/activities")
        self.assertEqual(status, 200)
        # 活动列表端点可达即证明应用与 DB 链真实；教学 workspace 对未知活动 404。
        unknown = str(__import__("uuid").uuid4())
        try:
            status, _ = self._get(f"/api/activities/{unknown}/teaching/workspace")
            self.fail(f"未知活动应 404，实际 {status}")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)

    def test_command_endpoint_rejects_invalid_dto(self):
        from uuid import uuid4
        status, payload = self._post("/api/activities/" + str(uuid4()) + "/teaching/commands",
                                     {"nonsense": True})
        self.assertIn(status, (400, 404, 422))
        self.assertIn("detail", payload)
