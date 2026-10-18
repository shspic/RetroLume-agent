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
    """真实合法冻结上下文的 claim/finish，预置状态不签动态 SUP。"""
    async def asyncSetUp(self):
        await super().asyncSetUp()
        from tests.fixtures.task100.synthetic_content import MATERIAL,GOAL
        from tests.fixtures.task100.seed_helpers import command,config
        from app.learning.teaching_service import TeachingService
        self.source=self.fixture.text(MATERIAL,'task100-recovery.md')
        self.activity=await self.fixture.activity([self.source])
        self.goal=command(None,'goal',{'goal':GOAL,'self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
        await self.ledger.apply_teaching_local(self.activity,self.goal)
        self.command=command(self.fixture.head(self.activity),'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None})
        service=TeachingService(self.ledger,self.fixture.materials,self.fixture.originals)
        self.frozen,_=await service._freeze_model_context(self.activity,self.command,config())
        await self.ledger.accept_teaching_command(self.activity,self.command,self.frozen)
        self.key=self.command.business_key
    def row(self):
        return self.fixture.rows('SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s',(self.activity,self.key))[0]
    async def claim(self): return await self.ledger.claim_teaching_launch(self.activity,self.key,self.command.request_sha256(self.activity))
    async def test_finish_not_admitted_fails_and_clears_pending(self):
        self.assertTrue((await self.claim())['launch_allowed'])
        receipt=await self.ledger.finish_teaching_supervision(self.activity,self.key,supervision_facts('not_started'))
        self.assertEqual(receipt.status,'failed');self.assertIsNone(self.fixture.head(self.activity)['pending_business_key'])
    async def test_cancelled_without_receipt_stays_unknown_and_keeps_slot(self):
        await self.claim()
        receipt=await self.ledger.finish_teaching_supervision(self.activity,self.key,supervision_facts('cancelled'))
        self.assertEqual(receipt.status,'unknown');self.assertEqual(str(self.fixture.head(self.activity)['pending_business_key']),self.key)
        self.assertEqual(receipt.retry_policy,'read_only')
    async def test_unknown_pending_blocks_second_launch_of_same_slot(self):
        await self.claim();await self.ledger.finish_teaching_supervision(self.activity,self.key,supervision_facts('cancelled'))
        self.assertEqual((await self.claim())['reason'],'status_unknown')
    async def test_claimed_command_cannot_relaunch_without_operation(self):
        self.assertTrue((await self.claim())['launch_allowed']);self.assertFalse((await self.claim())['launch_allowed'])
        self.assertIsNone(self.row()['result_record_id'])
    async def test_committed_command_receipt_is_not_overwritten(self):
        first=await self.ledger.finish_teaching_supervision(self.activity,self.goal.business_key,supervision_facts('not_started'))
        self.assertEqual(first.status,'committed');self.assertEqual(len(first.record_ids),1)
        self.assertEqual(self.fixture.head(self.activity)['revision'],1)
    async def test_obsolete_command_cannot_launch(self):
        self.fixture.rows('UPDATE teaching_commands SET obsolete_at=now() WHERE activity_id=%s AND business_key=%s',(self.activity,self.key))
        self.assertEqual((await self.claim())['reason'],'command_obsolete')
    async def test_frozen_digest_corruption_rejected_before_claim(self):
        from tests.fixtures.task100.seed_helpers import command,config
        from app.learning.teaching_service import TeachingService
        aid=await self.fixture.activity([self.source])
        goal=command(None,'goal',self.goal.body)
        await self.ledger.apply_teaching_local(aid,goal)
        candidate=command(self.fixture.head(aid),'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None})
        frozen,_=await TeachingService(self.ledger,self.fixture.materials,self.fixture.originals)._freeze_model_context(aid,candidate,config())
        with self.assertRaises(TeachingRefusal) as ctx:
            await self.ledger.accept_teaching_command(aid,candidate,frozen.model_copy(update={'context_sha256':'0'*64}))
        self.assertEqual(ctx.exception.code,'integrity_error')
        self.assertEqual(len(self.fixture.commands(aid)),1)
        self.assertIsNone(self.fixture.head(aid)['pending_business_key'])
