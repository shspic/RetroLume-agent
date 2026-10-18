"""TASK-100 续作01 教学恢复状态机检查（DEF-007 定向反例）。

两层：
  * 离线（无 DSN 可跑）：TeachingSupervisionFacts 严格校验与「确定未准入」
    判定输入域——取消且无收据不是未准入证明，只有启动阶段确定失败状态
    才可判定。
  * 真实 PG（PgTests，runner pg-recovery 场景）：finish_teaching_supervision
    以「本次确认后的结局」处理 pending 指针（不得读旧 status）；UNKNOWN
    占槽保留；已 claimed 无 operation 不得二次 launch。

只用本卡合成库（support.PGBase）。无 DSN 时明确 skip，不回退用户库。
"""
import json
import unittest
from uuid import uuid4

from app.learning.teaching_contracts import TeachingRefusal, TeachingSupervisionFacts
from tests.fixtures.task100.support import PGBase

# 启动阶段确定失败状态集合：与服务层 definitely_not_admitted 判定一致。
STARTUP_FAILED_STATES = frozenset(
    {"not_started", "budget_exhausted", "startup_deadline", "partial_window_too_small"})


def supervision_facts(state: str, model_receipt=None) -> TeachingSupervisionFacts:
    """按服务层同构规则构造监督事实（无收据 + 启动阶段失败才判未准入）。

    服务层内联逻辑的可复验投影：receipt_present = bool(model_receipt)；
    definitely_not_admitted = not receipt_present and state in 启动失败集合。
    """
    receipt_present = bool(model_receipt)
    return TeachingSupervisionFacts.model_validate({
        "state": state,
        "definitely_not_admitted": not receipt_present and state in STARTUP_FAILED_STATES,
        "model_receipt": model_receipt,
        "settled_seconds": None,
    }, strict=False)


class SupervisionFactsOfflineTests(unittest.TestCase):
    """离线：监督事实构造纪律（DEF-007 反例）。"""

    def test_cancelled_without_receipt_is_not_definitely_not_admitted(self):
        """取消且无 model_receipt 不是未准入证明：必须保守 unknown。"""
        facts = supervision_facts("cancelled")
        self.assertFalse(facts.definitely_not_admitted)

    def test_startup_failed_states_are_definitely_not_admitted(self):
        for state in sorted(STARTUP_FAILED_STATES):
            with self.subTest(state=state):
                facts = supervision_facts(state)
                self.assertTrue(facts.definitely_not_admitted)

    def test_receipt_presence_blocks_not_admitted_even_in_startup_state(self):
        """启动阶段状态但已有模型收据：不能判未准入（可能已真实发送）。"""
        facts = supervision_facts("not_started", model_receipt={"ok": True})
        self.assertFalse(facts.definitely_not_admitted)

    def test_settled_and_failed_closed_are_conservative_unknown(self):
        for state in ("settled", "failed_closed", "cancelled_by_caller", "overrun_unconfirmed"):
            with self.subTest(state=state):
                self.assertFalse(supervision_facts(state).definitely_not_admitted)


class RecoveryPgTests(PGBase):
    """真实 PG：finish/claim 状态机与 pending 指针纪律。"""

    def _seed_accepted_command(self, *, operation_id: str | None, status: str = "accepted",
                               action: str = "evaluate") -> str:
        """直接构造 accepted 教学命令行并置为 head pending（状态机测试种子）。"""
        key = str(uuid4())
        context_sha = "b" * 64
        request_sha = "a" * 64
        self.fixture.rows(
            """INSERT INTO teaching_commands(activity_id,business_key,action,request_sha256,
                   request_body,slot_sha256,expected_revision,goal_version,scope_revision,
                   context_body,context_sha256,operation_id,status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (self.activity, key, action, request_sha,
             json.dumps({"action": action}), "c" * 64,
             self._revision, 1, 1,
             json.dumps({"schema": "teaching.context.v1", "kind": "tool"}), context_sha,
             operation_id, status))
        self.fixture.rows(
            "UPDATE teaching_heads SET pending_business_key=%s WHERE activity_id=%s",
            (key, self.activity))
        return key

    def _head_row(self) -> dict:
        return self.fixture.rows(
            "SELECT * FROM teaching_heads WHERE activity_id=%s", (self.activity,))[0]

    def _command_row(self, key: str) -> dict:
        return self.fixture.rows(
            "SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s",
            (self.activity, key))[0]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.source = self.fixture.text(
            "恢复状态机夹具资料：评价在途、监督收尾、UNKNOWN 占槽。\n", "recovery.md")
        self.activity = await self.fixture.activity([self.source])
        from app.learning.teaching_contracts import GoalBody, TeachingCommandInput
        command = TeachingCommandInput(
            business_key=str(uuid4()), expected_revision=0, expected_goal_version=0,
            expected_scope_revision=1, action="goal",
            body=GoalBody(goal="恢复状态机夹具目标", self_report=None, domain=None,
                          seed_operation_id=None, seed_payload_sha256=None).model_dump())
        receipt = await self.ledger.apply_teaching_local(self.activity, command)
        self.assertEqual(receipt.status, "committed")
        self._revision = 1

    async def test_finish_not_admitted_fails_and_clears_pending(self):
        """确定未准入（not_started 无收据）→ failed 且 pending 清除。"""
        key = self._seed_accepted_command(operation_id="teach8m." + str(uuid4()) + "." + "a" * 64)
        facts = supervision_facts("not_started")
        receipt = await self.ledger.finish_teaching_supervision(self.activity, key, facts)
        self.assertEqual(receipt.status, "failed")
        self.assertEqual(receipt.error_code, "supervision_not_admitted")
        self.assertIsNone(self._head_row()["pending_business_key"])
        self.assertEqual(self._command_row(key)["status"], "failed")

    async def test_cancelled_without_receipt_stays_unknown_and_keeps_slot(self):
        """取消且无收据：保守 unknown，pending 占槽保留（DEF-007 反例）。"""
        key = self._seed_accepted_command(operation_id="teach8m." + str(uuid4()) + "." + "a" * 64)
        facts = supervision_facts("cancelled")
        receipt = await self.ledger.finish_teaching_supervision(self.activity, key, facts)
        self.assertEqual(receipt.status, "unknown")
        self.assertEqual(self._head_row()["pending_business_key"], key)
        self.assertEqual(self._command_row(key)["status"], "unknown")

    async def test_unknown_pending_blocks_second_launch_of_same_slot(self):
        """UNKNOWN 同父：同槽命令不得再次启动（占槽不释放）。"""
        key = self._seed_accepted_command(operation_id="teach8m." + str(uuid4()) + "." + "a" * 64)
        await self.ledger.finish_teaching_supervision(self.activity, key, supervision_facts("cancelled"))
        decision = await self.ledger.claim_teaching_launch(
            self.activity, key, self._command_row(key)["request_sha256"])
        self.assertFalse(decision["launch_allowed"])
        self.assertEqual(decision["reason"], "status_unknown")

    async def test_claimed_command_cannot_relaunch_without_operation(self):
        """已 claimed 且无 operation：重复 claim 返回 already_claimed，不重启。"""
        key = self._seed_accepted_command(operation_id="teach8m." + str(uuid4()) + "." + "a" * 64)
        first = await self.ledger.claim_teaching_launch(
            self.activity, key, self._command_row(key)["request_sha256"])
        self.assertTrue(first["launch_allowed"])
        second = await self.ledger.claim_teaching_launch(
            self.activity, key, self._command_row(key)["request_sha256"])
        self.assertFalse(second["launch_allowed"])
        self.assertEqual(second["reason"], "already_claimed")
        self.assertIsNone(self._command_row(key)["result_record_id"])

    async def test_committed_command_receipt_is_not_overwritten(self):
        """已有终态收据：finish 不覆盖原结局（先读原收据）。"""
        key = self._seed_accepted_command(operation_id="teach8m." + str(uuid4()) + "." + "a" * 64)
        self.fixture.rows(
            """UPDATE teaching_commands SET status='committed',
                   result_record_id=NULL WHERE activity_id=%s AND business_key=%s""",
            (self.activity, key))
        receipt = await self.ledger.finish_teaching_supervision(
            self.activity, key, supervision_facts("not_started"))
        self.assertEqual(receipt.status, "committed")

    async def test_obsolete_command_cannot_launch(self):
        """已废弃命令：launch 拒绝（no_longer_current_binding / command_obsolete）。"""
        key = self._seed_accepted_command(operation_id="teach8m." + str(uuid4()) + "." + "a" * 64)
        # head pending 切到其他键：本命令不再当前绑定。
        self.fixture.rows(
            "UPDATE teaching_heads SET pending_business_key=%s WHERE activity_id=%s",
            (str(uuid4()), self.activity))
        decision = await self.ledger.claim_teaching_launch(
            self.activity, key, self._command_row(key)["request_sha256"])
        self.assertFalse(decision["launch_allowed"])
        self.assertIn(decision["reason"], ("no_longer_current_binding", "command_obsolete"))
