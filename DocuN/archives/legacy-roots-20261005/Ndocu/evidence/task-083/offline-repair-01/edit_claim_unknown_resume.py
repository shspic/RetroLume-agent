"""Resume precise claim-ambiguity edit after first anchor applied and script typo stopped."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def once(relative, old, new):
    path = ROOT / relative
    data = path.read_text(encoding="utf-8")
    assert data.count(old) == 1, (relative, data.count(old))
    path.write_text(data.replace(old, new), encoding="utf-8", newline="")


once(
    "backend/app/worker/session.py",
    "            t0_ns = time.monotonic_ns()  # claim前固定；响应丢失不spawn或重领。\n            lease = await self._db(self.ledger.claim_lease(\n",
    "            t0_ns = time.monotonic_ns()  # claim前固定；响应丢失不spawn或重领。\n            claim_attempted = True\n            lease = await self._db(self.ledger.claim_lease(\n",
)
once(
    "backend/app/worker/session.py",
    "            if settlement_attempted:\n                settled_seconds = None\n                reserved_seconds = None\n                pending_fold_seconds = None\n",
    "            if settlement_attempted or (claim_attempted and lease is None):\n                settled_seconds = None\n                reserved_seconds = None\n                pending_fold_seconds = None\n",
)
once(
    "backend/tests/fixtures/task083/offline_unit.py",
    "        self.assertEqual((result.reserved_seconds, result.settled_seconds), (0, 0))\n        self.assertIsNone(result.job_name)\n",
    "        self.assertEqual((result.reserved_seconds, result.settled_seconds, result.pending_fold_seconds), (None, None, None))\n        self.assertIsNone(result.job_name)\n",
)
