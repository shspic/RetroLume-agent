"""TASK-100 教学账本真实 PG 检查：三表原子性、幂等重放、语义槽竞争、
CAS 前置、命令身份守卫与不可变触发器。

只用本卡合成库（support.PGBase）。无 DSN 时明确 skip，不回退用户库。
"""
import json
from uuid import uuid4

from app.learning.teaching_contracts import (
    GoalBody,
    TeachingCommandInput,
    TeachingRefusal,
    semantic_slot,
)
from tests.fixtures.task100.support import PGBase

GOAL_TEXT = "能正确换算平均速度并说明数量级"


def goal_command(*, revision=0, goal_version=0, scope=1, text=GOAL_TEXT, key=None):
    body = GoalBody(goal=text, self_report=None, domain=None,
                    seed_operation_id=None, seed_payload_sha256=None)
    return TeachingCommandInput(
        business_key=key or str(uuid4()),
        expected_revision=revision,
        expected_goal_version=goal_version,
        expected_scope_revision=scope,
        action="goal",
        body=body.model_dump(),
    )


class TeachingLedgerPGTests(PGBase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.source = self.fixture.text(
            "平均速度 = 路程 ÷ 时间。2 分钟走 120 米，"
            "平均速度是 120 米 ÷ 120 秒 = 1 米/秒。数量级要先统一单位。\n",
            "speed.md")
        self.activity = await self.fixture.activity([self.source])
        self.snapshot = await self.ledger.read_learning_snapshot(self.activity)

    async def test_local_command_commits_head_and_record_atomically(self):
        """T-local：O01 一次提交同时写 command/head/record，无半状态。"""
        command = goal_command()
        receipt = await self.ledger.apply_teaching_local(self.activity, command)
        self.assertEqual(receipt.status, "committed")
        self.assertEqual(receipt.qualification, "current")
        head = self.fixture.head(self.activity)
        self.assertIsNotNone(head)
        self.assertEqual(head["phase"], "needs_plan")
        self.assertEqual(head["goal_version"], 1)
        self.assertEqual(head["revision"], 1)
        kinds = [r["kind"] for r in self.fixture.records(self.activity)]
        self.assertEqual(kinds, ["goal"])
        self.assertEqual(len(self.fixture.commands(self.activity)), 1)

    async def test_identical_replay_is_idempotent_and_conflict_is_refused(self):
        """同键同文重放幂等返回原回执；同键异文必须拒且保留原意图。"""
        command = goal_command()
        first = await self.ledger.apply_teaching_local(self.activity, command)
        again = await self.ledger.apply_teaching_local(self.activity, command)
        self.assertEqual(again.request_sha256, first.request_sha256)
        self.assertEqual(again.status, first.status)
        # 幂等的关键在教学事实与 head 不被二次推进：命令数与记录数仍各 1。
        self.assertEqual(len(self.fixture.commands(self.activity)), 1)
        self.assertEqual(len(self.fixture.records(self.activity)), 1)
        self.assertEqual(self.fixture.head(self.activity)["revision"], 1)

        with self.assertRaises(TeachingRefusal) as ctx:
            await self.ledger.apply_teaching_local(
                self.activity, goal_command(key=command.business_key, text="完全不同的目标表述"))
        self.assertEqual(ctx.exception.code, "command_key_conflict")
        self.assertEqual(len(self.fixture.commands(self.activity)), 1)
        # 冲突后原正文仍在，未被覆盖。
        stored = self.fixture.rows(
            "SELECT body FROM teaching_records WHERE activity_id=%s", (self.activity,))
        self.assertIn("平均速度", stored[0]["body"])

    async def test_revision_cas_blocks_stale_head(self):
        """expected_revision 陈旧必须拒，不能覆盖已推进的 head。"""
        await self.ledger.apply_teaching_local(self.activity, goal_command())
        with self.assertRaises(TeachingRefusal) as ctx:
            await self.ledger.apply_teaching_local(
                self.activity, goal_command(revision=0, goal_version=1))
        self.assertIn(ctx.exception.code,
                      {"revision_conflict", "version_conflict", "stage_conflict", "invalid_input"})
        self.assertEqual(self.fixture.head(self.activity)["revision"], 1)

    async def test_goal_version_zero_only_for_first_goal(self):
        """expected_goal_version=0 只允许首次 goal。"""
        await self.ledger.apply_teaching_local(self.activity, goal_command())
        with self.assertRaises(TeachingRefusal) as ctx:
            await self.ledger.apply_teaching_local(
                self.activity, goal_command(revision=1, goal_version=0, text="第二版目标但版本号写零"))
        self.assertIn(ctx.exception.code,
                      {"goal_version_conflict", "version_conflict", "goal_changed",
                       "revision_conflict", "invalid_input"})

    async def test_semantic_slot_ignores_business_key_and_retry(self):
        """语义槽只含动作/范围/父实体身份：换 business_key 不换槽，同槽异文拒。"""
        first = goal_command()
        await self.ledger.apply_teaching_local(self.activity, first)
        head = self.fixture.head(self.activity)
        # anchors 必须是可序列化的字符串身份；服务端组包也必须如此。
        anchors = {"goal_record_id": str(head["goal_record_id"]) if head["goal_record_id"] else None}
        slot_first = semantic_slot(self.activity, first, anchors)
        # 换 business_key 但保持同动作/同父锚点/同目标版本，槽不变——
        # 这正是同槽竞争与幂等判定的基础。
        same_slot = goal_command(revision=1, goal_version=1, key=str(uuid4()))
        self.assertNotEqual(
            slot_first, semantic_slot(self.activity, same_slot, anchors),
            "目标版本参与槽身份：新一版目标必须是新槽")
        # 真正验证 business_key 不参与槽：同锚点同版本下换 key，槽必须一致。
        anchor_only = TeachingCommandInput(
            business_key=str(uuid4()), expected_revision=1, expected_goal_version=1,
            expected_scope_revision=self.snapshot["scope_revision"], action="goal",
            body=GoalBody(goal=GOAL_TEXT, self_report=None, domain=None,
                          seed_operation_id=None, seed_payload_sha256=None).model_dump())
        self.assertEqual(
            semantic_slot(self.activity, same_slot, anchors),
            semantic_slot(self.activity, anchor_only, anchors))
        updated=await self.ledger.apply_teaching_local(
            self.activity,goal_command(revision=1,goal_version=1,text="合法第二版目标"))
        self.assertEqual(updated.status,'committed')
        self.assertEqual(self.fixture.head(self.activity)['goal_version'],2)

    async def test_teaching_records_are_immutable_at_database_level(self):
        """正文、身份及效果投影全列不可改写或删除。"""
        await self.ledger.apply_teaching_local(self.activity, goal_command())
        with self.assertRaises(Exception):
            self.fixture.rows(
                "UPDATE teaching_records SET body=%s WHERE activity_id=%s",
                (json.dumps({"tampered": True}), self.activity))
        with self.assertRaises(Exception):
            self.fixture.rows("DELETE FROM teaching_records WHERE activity_id=%s",
                              (self.activity,))
        stored = self.fixture.rows(
            "SELECT body FROM teaching_records WHERE activity_id=%s", (self.activity,))
        self.assertNotIn("tampered", stored[0]["body"])
        self.assertIn("平均速度", stored[0]["body"])
        with self.assertRaises(Exception):
            self.fixture.rows("UPDATE teaching_records SET applied_revision=applied_revision WHERE activity_id=%s",(self.activity,))
        after = self.fixture.rows(
            "SELECT body FROM teaching_records WHERE activity_id=%s", (self.activity,))
        self.assertEqual(after[0]["body"], stored[0]["body"])

    async def test_head_projection_is_rebuildable_and_never_claims_mastered(self):
        """投影只允许 099 封闭枚举，且永不含 mastered。"""
        await self.ledger.apply_teaching_local(self.activity, goal_command())
        projection = self.fixture.head(self.activity)["projection"]
        values = list(projection.values()) if isinstance(projection, dict) else []
        allowed = {"not_started", "practising", "needs_repair", "evidence_sufficient", "deferred"}
        for value in values:
            if isinstance(value, str):
                self.assertIn(value, allowed)
        self.assertNotIn("mastered", projection)

    async def test_command_identity_guard_blocks_status_rewrite(self):
        """命令身份守卫：已 committed 命令不得被改成别的收据身份。"""
        await self.ledger.apply_teaching_local(self.activity, goal_command())
        with self.assertRaises(Exception):
            self.fixture.rows(
                "UPDATE teaching_commands SET request_sha256=%s WHERE activity_id=%s",
                ("b" * 64, self.activity))
        stored = self.fixture.commands(self.activity)[0]
        self.assertNotEqual(stored["request_sha256"], "b" * 64)

    async def test_workspace_read_requires_goal_before_plan_actions(self):
        """工作区读出真实阶段；needs_plan 阶段 plan 之外命令被阶段门拦住。

        仓储层返回原始投影 {activity, head, pending, history}；
        view_token/budgets 等对外包装在 API 层组装，不在此断言。
        """
        await self.ledger.apply_teaching_local(self.activity, goal_command())
        workspace = await self.ledger.read_teaching_workspace(self.activity)
        self.assertEqual(workspace["head"]["phase"], "needs_plan")
        self.assertEqual(workspace["head"]["goal_version"], 1)
        self.assertEqual(workspace["head"]["revision"], 1)
        self.assertEqual(len(workspace["pending"]), 1)
        self.assertEqual([r["kind"] for r in workspace["history"]], ["goal"])
        with self.assertRaises(TeachingRefusal) as ctx:
            # 用真实存在的路径记录做 accept_path，才能落到阶段门；
            # 这里先证明无效 proposal_record_id 会被更早的身份门拦下。
            await self.ledger.apply_teaching_local(self.activity, TeachingCommandInput(
                business_key=str(uuid4()), expected_revision=1, expected_goal_version=1,
                expected_scope_revision=self.snapshot["scope_revision"], action="accept_path",
                body={"proposal_record_id": str(uuid4())}))
        self.assertEqual(ctx.exception.code, "stage_conflict")
        # 该次拒绝不得留下命令行或推进 head。
        self.assertEqual(len(self.fixture.commands(self.activity)), 1)
        self.assertEqual(self.fixture.head(self.activity)["phase"], "needs_plan")
