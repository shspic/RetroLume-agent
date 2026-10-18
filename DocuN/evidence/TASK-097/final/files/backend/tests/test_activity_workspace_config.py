"""TASK-095 活动配置三层（L0/L1/L2）离线合同测试；不访问数据库与网络。"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.service_config import load_activity_config


APP_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = APP_ROOT / "config" / "activity.example.json"


def good_config(**overrides) -> dict:
    data = {
        "model_identity": {"provider": "deepseek_chat_completions", "model": "synthetic-model-095"},
        "activity_defaults": {
            "deadline_hours": 24, "max_requests": 8, "max_cost_microunits": 800_000,
            "reserve_cost_microunits": 100_000, "max_request_bytes": 65536,
            "max_output_tokens": 256, "max_running_seconds": 600,
            "allowed_tools": [], "max_tool_calls": None,
        },
        "service": {
            "base_url": "https://api.deepseek.com", "thinking": "disabled",
            "timeout_seconds": 10, "max_output_tokens_limit": 8192,
            "max_request_bytes": 65536, "max_response_bytes": 65536,
        },
        "api_key_env": "RETROLUME_TEST095_KEY",
    }
    for key, value in overrides.items():
        if value is None:
            data.pop(key, None)
        elif isinstance(value, dict) and isinstance(data.get(key), dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    return data


class ConfigLoaderTests(unittest.TestCase):
    def write(self, data, *, raw: str | None = None) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "activity.local.json"
        path.write_text(raw if raw is not None else json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self, path, *, key: str | None = None):
        env = {"RETROLUME_TEST095_KEY": key} if key is not None else {}
        with patch.dict(os.environ, env, clear=False):
            if key is None:
                os.environ.pop("RETROLUME_TEST095_KEY", None)
            return load_activity_config(path)

    def test_missing_file_is_config_missing(self):
        config = self.load(Path(tempfile.gettempdir()) / "definitely-not-a-config-095.json")
        self.assertEqual((config.create_layer.available, config.create_layer.reason), (False, "config_missing"))
        self.assertEqual((config.continue_layer.available, config.continue_layer.reason), (False, "config_missing"))

    def test_bad_json_and_non_dict_are_invalid(self):
        for raw in ("{not json", "[1,2,3]"):
            config = self.load(self.write(None, raw=raw))
            self.assertEqual(config.create_layer.reason, "config_invalid")

    def test_missing_sections_are_config_missing(self):
        data = good_config()
        data.pop("activity_defaults")
        config = self.load(self.write(data))
        self.assertEqual((config.create_layer.available, config.create_layer.reason), (False, "config_missing"))

    def test_committed_example_template_cannot_activate(self):
        config = self.load(EXAMPLE, key="synthetic-placeholder-key")
        self.assertFalse(config.create_layer.available)
        self.assertFalse(config.continue_layer.available)
        self.assertEqual(config.create_layer.reason, "config_invalid")

    def test_l1_without_key_and_l2_with_key(self):
        path = self.write(good_config())
        config = self.load(path)
        self.assertTrue(config.create_layer.available)
        self.assertEqual(config.continue_layer.reason, "provider_key_not_configured")
        self.assertIsNone(config.model_service)
        self.assertEqual(config.quota_preview["max_requests"], 8)
        self.assertEqual(config.quota_preview["max_tool_calls"], None)
        with_key = self.load(path, key="synthetic-placeholder-key")
        self.assertTrue(with_key.continue_layer.available)
        self.assertEqual(with_key.model_service.timeout_seconds, 10.0)
        self.assertEqual(with_key.model_service.model, "synthetic-model-095")

    def test_empty_key_value_is_not_configured(self):
        config = self.load(self.write(good_config()), key="   ")
        self.assertTrue(config.create_layer.available)
        self.assertEqual(config.continue_layer.reason, "provider_key_not_configured")

    def test_strict_types_reject_string_and_bool_numbers(self):
        for override in (
            {"activity_defaults": {"max_requests": "8"}},
            {"activity_defaults": {"max_requests": True}},
            {"activity_defaults": {"deadline_hours": 24.5}},
            {"model_identity": {"model": 7}},
        ):
            config = self.load(self.write(good_config(**override)), key="k")
            self.assertFalse(config.create_layer.available, override)
            self.assertEqual(config.create_layer.reason, "config_invalid", override)

    def test_field_bounds_fail_closed(self):
        cases = (
            {"activity_defaults": {"deadline_hours": 0}},
            {"activity_defaults": {"max_request_bytes": 65537}},
            {"activity_defaults": {"max_request_bytes": 512}},
            {"activity_defaults": {"reserve_cost_microunits": 900_000}},
            {"activity_defaults": {"allowed_tools": ["finite_calculate"]}},
            {"activity_defaults": {"max_tool_calls": 0}},
            {"model_identity": {"provider": "unknown_provider"}},
            {"model_identity": {"model": "REPLACE ME MODEL"}},
        )
        for override in cases:
            config = self.load(self.write(good_config(**override)), key="k")
            self.assertFalse(config.create_layer.available, override)
            self.assertEqual(config.create_layer.reason, "config_invalid", override)

    def test_service_mapping_incompatibilities(self):
        cases = ("timeout", "response", "thinking", "output_tokens", "missing_service")
        for case in cases:
            overrides = {
                "timeout": {"service": {"timeout_seconds": 30}},
                "response": {"service": {"max_response_bytes": 1_048_576}},
                "thinking": {"service": {"thinking": "enabled"}},
                "output_tokens": {"activity_defaults": {"max_output_tokens": 128}},
                "missing_service": {"service": None},
            }[case]
            config = self.load(self.write(good_config(**overrides)), key="k")
            self.assertTrue(config.create_layer.available, case)
            self.assertFalse(config.continue_layer.available, case)
            expected = "config_invalid" if case == "missing_service" else "config_incompatible"
            self.assertEqual(config.continue_layer.reason, expected, case)

    def test_default_paths_and_env_key_name(self):
        # 密钥变量名由配置声明；不读取未声明变量。
        data = good_config()
        data["api_key_env"] = "RETROLUME_OTHER_NAME"
        with patch.dict(os.environ, {"RETROLUME_TEST095_KEY": "value"}, clear=False):
            config = load_activity_config(self.write(data))
        self.assertEqual(config.continue_layer.reason, "provider_key_not_configured")


if __name__ == "__main__":
    unittest.main()
