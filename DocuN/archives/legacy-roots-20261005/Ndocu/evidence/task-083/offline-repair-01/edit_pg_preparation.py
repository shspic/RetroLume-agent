"""Add real PG received/cancel convergence cases without connecting to PG."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "backend/tests/fixtures/task083/pg_close.py"
data = path.read_text(encoding="utf-8")


def once(old, new):
    global data
    assert data.count(old) == 1, data.count(old)
    data = data.replace(old, new)


once(
    '        dispatched = await self.ledger.admit(self.intent(lease, "dispatched-op"))\n        await self.ledger.mark_dispatch_started(dispatched)\n',
    '        dispatched = await self.ledger.admit(self.intent(lease, "dispatched-op"))\n        received = await self.ledger.admit(self.intent(lease, "received-op"))\n        await self.ledger.mark_dispatch_started(dispatched)\n        await self.ledger.mark_dispatch_started(received)\n',
)
once(
    '        await self.ledger.record_outcome(dispatched, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="synthetic_unknown"))\n        rows = await self.row("SELECT count(*) FILTER (WHERE state=\'not_sent\') AS not_sent,count(*) FILTER (WHERE state=\'unknown\') AS unknown FROM activity_operations WHERE activity_id=%s", (self.activity_id,))\n        self.assertEqual(rows, {"not_sent": 1, "unknown": 1})\n',
    '        await self.ledger.record_outcome(dispatched, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="synthetic_unknown"))\n        await self.ledger.record_outcome(received, LedgerOutcome(LedgerDisposition.RECEIVED, remote_request_id="synthetic-id", returned_model="synthetic-model", finish_reason="stop", prompt_tokens=1, completion_tokens=1, response_bytes=12))\n        rows = await self.row("SELECT count(*) FILTER (WHERE state=\'not_sent\') AS not_sent,count(*) FILTER (WHERE state=\'unknown\') AS unknown,count(*) FILTER (WHERE state=\'received\') AS received FROM activity_operations WHERE activity_id=%s", (self.activity_id,))\n        self.assertEqual(rows, {"not_sent": 1, "unknown": 1, "received": 1})\n',
)
extra = '''    async def test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges(self):
        lease = await self.build()
        permit = await self.ledger.admit(self.intent(lease, "before-cancel"))
        await self.ledger.mark_dispatch_started(permit)
        cancelled_generation = await self.ledger.cancel_activity(self.activity_id)
        self.assertEqual(cancelled_generation, lease.execution_generation + 1)
        row = await self.row("SELECT status,dispatch_closed,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s", (self.activity_id,))
        self.assertEqual(row, {"status": "cancelled", "dispatch_closed": True, "running_reserved_seconds": 0, "running_settled_seconds": 90})
        await self.ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="cancelled"))
        self.assertEqual(await self.row("SELECT state FROM activity_operations WHERE admission_id=%s", (permit.admission_id,)), {"state": "unknown"})


'''
once('\n\nif __name__ == "__main__":\n', '\n\n' + extra + 'if __name__ == "__main__":\n')
path.write_text(data, encoding="utf-8", newline="")
