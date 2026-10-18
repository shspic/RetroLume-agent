"""唯一纯单元修正：合成成功路径明确产生正耗时与Job关闭次序。"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "backend/tests/fixtures/task083/offline_unit.py"
data = path.read_text(encoding="utf-8")


def once(old, new):
    global data
    assert data.count(old) == 1, data.count(old)
    data = data.replace(old, new)


once(
    "    def __init__(self, *, hang=False, terminate_error=False, close_error=False):\n",
    "    def __init__(self, *, hang=False, terminate_error=False, close_error=False, external_events=None):\n",
)
once(
    "        self.close_error = close_error\n        self.events = []\n",
    "        self.close_error = close_error\n        self.external_events = external_events\n        self.events = []\n",
)
once(
    "    def wait_empty_until(self, deadline):\n        self.events.append(\"query\")\n        return not self.hang or self.terminated\n",
    "    def wait_empty_until(self, deadline):\n        self.events.append(\"query\")\n        if not self.hang and not self.terminated:\n            time.sleep(0.002)  # 纯替身模拟正耗时；真实C0仍拒绝部分退款。\n        return not self.hang or self.terminated\n",
)
once(
    "    def close(self):\n        self.events.append(\"close_job\")\n        if self.close_error:\n",
    "    def close(self):\n        self.events.append(\"close_job\")\n        if self.external_events is not None:\n            self.external_events.append(\"job_closed\")\n        if self.close_error:\n",
)
once(
    "        ledger = Ledger(settle_lost_once=True)\n        job = FakeJob()\n",
    "        ledger = Ledger(settle_lost_once=True)\n        job = FakeJob(external_events=ledger.events)\n",
)
once(
    "        self.assertLess(job.events.index(\"close_job\"), len(job.events))\n        self.assertEqual(ledger.events, [\"inspect\", \"claim\", \"close_db\", \"settle\", \"settle\"])\n",
    "        self.assertIn(\"close_job\", job.events)\n        self.assertEqual(ledger.events, [\"inspect\", \"claim\", \"job_closed\", \"close_db\", \"settle\", \"settle\"])\n",
)
path.write_text(data, encoding="utf-8", newline="")
