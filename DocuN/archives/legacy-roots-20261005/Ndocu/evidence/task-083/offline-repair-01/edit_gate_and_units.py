"""Expose irreversible close observation and test the marked-before-send crossing."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def replace_once(relative, old, new):
    path = ROOT / relative
    data = path.read_text(encoding="utf-8")
    assert data.count(old) == 1, (relative, data.count(old))
    path.write_text(data.replace(old, new), encoding="utf-8", newline="")


replace_once(
    "backend/app/worker/gate.py",
    "    @property\n    def active_calls(self) -> int:\n        return self._active\n",
    "    @property\n    def active_calls(self) -> int:\n        return self._active\n\n    @property\n    def closed(self) -> bool:\n        return self._closed\n",
)
replace_once(
    "backend/tests/fixtures/task083/offline_unit.py",
    "        await gateway.marked.wait()\n        await asyncio.sleep(0)\n        self.assertFalse(runner.done())\n        gateway.release.set()\n",
    "        await gateway.marked.wait()\n        for _ in range(10):\n            if captured[0].closed:\n                break\n            await asyncio.sleep(0)\n        self.assertTrue(captured[0].closed)\n        self.assertFalse(runner.done())\n        self.assertEqual(gateway.events, [\"admit\", \"mark\"])\n        with self.assertRaises(GateClosed):\n            await captured[0].call(None, None)\n        gateway.release.set()\n",
)
