"""仅既有字段/总根下标缺陷及受信组合回归，不mock CDP或浏览器。"""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location("task109_h0_tail", Path(__file__).with_name("h0-tail.py"))
CONTROL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTROL)


class TailControlChecks(unittest.TestCase):
    def test_saved_image_build_and_run_ownership(self):
        path = ROOT / "DocuN/evidence/TASK-109/execution/continuation-04/root-07/loaded-image.json"
        actual = json.loads(path.read_text("utf-8"))
        self.assertNotIn("containerimage.config.digest", actual)
        self.assertTrue(CONTROL.validate_image_projection(actual))
        actual["labels"]["retrolume.action-permit"] = "TASK-109-G11-C05-20261009"
        self.assertFalse(CONTROL.validate_image_projection(actual))

    def test_global_root_eight_with_only_one_attempt(self):
        descriptor = {"root": "H0-R08", "attempt": 1, "runtime_start_ns": 100, "runtime_observed_until_ns": 2100000100, "state": "FAIL"}
        session = {"roots": [{"id": "H0-R08", "task_ordinal": 8}], "attempts": [descriptor], "cleanup_seconds": 0, "new_runtime_seconds": 0}
        CONTROL.account_attempt(session, descriptor, {"elapsed_seconds": 1.25, "runtime_upper_seconds_until_stopped": 3.35})
        self.assertEqual(len(session["attempts"]), 1)
        self.assertIs(session["attempts"][0], descriptor)
        self.assertEqual(session["attempts"][0]["state"], "FAIL")
        self.assertEqual(session["cleanup_seconds"], 1.25)
        self.assertEqual(session["new_runtime_seconds"], 3.35)

    def test_original_literal_and_exact_composition(self):
        counter = (ROOT / "backend/tests/fixtures/task109/h0-counter.cjs").read_bytes()
        literal = re.search(rb"const pageHtml = `[\s\S]*?`;", counter).group(0)
        helper = (ROOT / "backend/tests/fixtures/task109/navigation-tail.cjs").read_bytes()
        self.assertEqual(helper.count(literal), 1)
        template = (ROOT / "deploy/preview/runtime-bootstrap.cjs").read_text("utf-8")
        combined = CONTROL.compose_source(template, helper.decode("utf-8"))
        self.assertEqual(combined.count(helper.decode("utf-8")), 1)
        self.assertNotIn('require("/opt/preview/h0-counter.cjs");', combined)
        self.assertIn('actual_navigation_fixture: "navigation-tail.cjs"', combined)
        broken = template + '\nrequire("/opt/preview/h0-counter.cjs");'
        with self.assertRaises(RuntimeError):
            CONTROL.compose_source(broken, helper.decode("utf-8"))

    def test_exact_windows_native_argv_and_scope(self):
        template = (ROOT / "deploy/preview/runtime-bootstrap.cjs").read_text("utf-8")
        helper = (ROOT / "backend/tests/fixtures/task109/navigation-tail.cjs").read_text("utf-8")
        combined = CONTROL.compose_source(template, helper)
        args = CONTROL.make_create_args(combined, "0" * 32)
        self.assertLessEqual(CONTROL.windows_argv_units(shutil.which("docker"), args), 32767)
        self.assertEqual(args[-3:], [CONTROL.IMAGE, "-e", combined])
        self.assertIn("retrolume.root=H0-R08", args)
        self.assertIn("retrolume.action-permit=TASK-109-G11-C05-20261009", args)
        self.assertIn("--user=10001:10001", args)
        self.assertIn("--network=none", args)
        self.assertIn("--pids-limit=128", args)
        self.assertFalse(any(value.startswith("--mount") or value.startswith("--volume") or value.startswith("--publish") for value in args))

    def test_all_deadlines_obey_fixed_effective_window(self):
        now = 900000000000
        session = {"effective_deadline_ns": now + 37000000000}
        actual = CONTROL.deadline_set(session, now)
        self.assertTrue(all(value <= session["effective_deadline_ns"] for value in actual.values()))
        self.assertEqual(actual["diagnostic"], now + 20000000000)
        self.assertEqual(actual["preview"], session["effective_deadline_ns"])
        self.assertEqual(actual["root"], session["effective_deadline_ns"])


if __name__ == "__main__":
    unittest.main()
