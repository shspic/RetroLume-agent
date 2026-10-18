"""学习配置显式开关及旧L0/L1/L2兼容边界。"""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from app.service_config import load_activity_config
from tests.test_activity_workspace_config import good_config


def config():
    value = good_config()
    value["model_identity"]["model"] = "synthetic-model-097"
    value["api_key_env"] = "RETROLUME_TEST097_KEY"
    value["learning"] = {"profile":"learning.v1", "max_output_tokens":256}
    return value


class LearningConfigTests(unittest.TestCase):
    def load(self, data, key=True):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"synthetic.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.dict(os.environ, {"RETROLUME_TEST097_KEY":"synthetic-097" if key else ""}):
                return load_activity_config(path)

    def test_explicit_learning_only_and_no_budget_default(self):
        value = config()
        c = self.load(value)
        self.assertTrue(c.learning_layer.available); self.assertEqual(c.learning_output_tokens,256)
        value.pop("learning")
        c = self.load(value)
        self.assertTrue(c.create_layer.available); self.assertTrue(c.continue_layer.available)
        self.assertFalse(c.learning_layer.available)
        self.assertIsNone(c.learning_output_tokens)

    def test_learning_invalid_does_not_disable_old_layers(self):
        for setting in [None, {}, {"profile":"unknown", "max_output_tokens":256},
            {"profile":"learning.v1", "max_output_tokens":257},
            {"profile":"learning.v1", "max_output_tokens":True},
            {"profile":"learning.v1", "max_output_tokens":256, "tools":["finite_calculate"]}]:
            value = config(); value["learning"] = setting
            c = self.load(value)
            self.assertTrue(c.create_layer.available); self.assertTrue(c.continue_layer.available)
            self.assertFalse(c.learning_layer.available)

    def test_key_missing_and_l1_bad_fail_closed(self):
        c = self.load(config(),key=False)
        self.assertTrue(c.create_layer.available)
        self.assertEqual(c.learning_layer.reason,"provider_key_not_configured")
        value=config(); value["activity_defaults"]["reserve_cost_microunits"]=999999
        c = self.load(value)
        self.assertFalse(c.create_layer.available); self.assertFalse(c.learning_layer.available)
        value=config(); value["service"]["max_output_tokens_limit"]=128
        c=self.load(value)
        self.assertTrue(c.continue_layer.available)
        self.assertEqual(c.learning_layer.reason,"learning_config_incompatible")
