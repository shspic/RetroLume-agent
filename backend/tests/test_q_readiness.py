"""TASK123 启动快照与只读投影的离线行为，所有凭据为合成占位。"""
from contextlib import ExitStack, contextmanager
from dataclasses import replace
import io
import json
import logging
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient
from app.main import create_app
from app.q_readiness import build_readiness, read_readiness
from app.service_config import LayerState, load_activity_config
from app.retrieval.service import IntegrationConfig
from app.capabilities.embedding import EmbeddingServiceConfig
from app.data_exit.contracts import DataContext, DataError, canonical
from test_activity_workspace_config import good_config


class ReadinessTests(unittest.TestCase):
    @contextmanager
    def isolated_app(self, *, model_key=True, embedding_key=True, bad_model=False,
                     missing_model=False, integration_enabled=True):
        with tempfile.TemporaryDirectory(prefix="task123-") as temporary, ExitStack() as stack:
            root = Path(temporary).resolve()
            data, backup = root / "data", root / "backup"
            data.mkdir(); backup.mkdir()
            activity = root / "activity.synthetic.json"
            integration = root / "integration.synthetic.json"
            body = good_config(model_identity={"model": "deepseek-flash"},
                               service={"returned_models": ["deepseek-flash"]},
                               learning={"profile": "learning.v2", "max_output_tokens": 128})
            if not missing_model:
                activity.write_text("{bad" if bad_model else json.dumps(body), encoding="utf-8")
            integration.write_text(json.dumps({"schema": "retrolume.integration.v1",
                "enabled": integration_enabled, "embedding": {"returned_models": ["embedding-3"]}}), encoding="utf-8")
            env = {"RETROLUME_DATA_DIR": str(data), "RETROLUME_BACKUP_DIR": str(backup),
                   "RETROLUME_ACTIVITY_CONFIG": str(activity),
                   "RETROLUME_INTEGRATION_CONFIG": str(integration)}
            if model_key: env["RETROLUME_TEST095_KEY"] = "TASK123_SYNTHETIC_MODEL_SECRET"
            if embedding_key: env["RETROLUME_EMBEDDING_API_KEY"] = "TASK123_SYNTHETIC_EMBEDDING_SECRET"
            stack.enter_context(patch.dict(os.environ, env, clear=True))
            # 这些路径一旦被新投影误调用，立即失败并保留可观察计数。
            tripwires = {}
            for name in ("app.main.PostgresAdmissionLedger", "app.main.PostgresMaterials",
                         "app.data_exit.config.ControlHub", "app.data_exit.q_store.QAuthority.bind",
                         "app.data_exit.q_store.QAuthority.approve",
                         "app.operator.q_request.configure_application", "app.operator.q_request.operator_ledger",
                         "app.capabilities.transport.HttpxModelTransport.__init__",
                         "app.capabilities.gateway.ControlledModelGateway.__init__",
                         "app.capabilities.embedding.ControlledEmbeddingGateway.__init__",
                         "psycopg.connect", "psycopg.AsyncConnection.connect"):
                tripwires[name] = stack.enter_context(patch(name, side_effect=AssertionError("禁止执行 " + name)))
            for name in ("app.main.load_activity_config", "app.main.load_integration_config"):
                import app.main as main
                original = getattr(main, name.rsplit(".", 1)[1])
                tripwires[name] = stack.enter_context(patch(name, wraps=original))
            application = create_app()
            with TestClient(application) as client:
                headers = {"x-retrolume-session": application.state.session_token}
                yield application, client, headers, tripwires, activity, integration
            for name, mock in tripwires.items():
                self.assertEqual(mock.call_count, 1 if name.startswith("app.main.load_") else 0, name)

    def diagnostic(self, client, headers):
        response = client.get("/api/activities/capabilities", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["cache-control"], "no-store")
        return response.json()

    def test_missing_bad_and_disabled_configs(self):
        for options, reason in (({"missing_model": True}, "config_missing"),
                                ({"bad_model": True}, "config_invalid")):
            with self.subTest(options=options), self.isolated_app(**options) as (app, client, headers, *_):
                body = self.diagnostic(client, headers)
                diag = body["diagnostics"]["readiness"]
                self.assertEqual(diag["candidate"]["model"]["load"]["reason"], reason)
                self.assertIsNone(diag["key_presence"]["model"])
                self.assertFalse(body["continue"]["available"])
                self.assertFalse(diag["authorizes_requests"])
                self.assertEqual(body["q_approval"], app.state.q_readiness)
                self.assertFalse(body["q_approval"]["real_outbound_authorized"])
        with self.isolated_app(integration_enabled=False) as (app, client, headers, *_):
            diag = self.diagnostic(client, headers)["diagnostics"]["readiness"]
            self.assertEqual(diag["candidate"]["embedding"]["load"]["reason"], "retrieval_disabled")
            self.assertIsNone(diag["candidate"]["embedding"]["service"]["identity"])

    def test_either_key_absent_and_keys_without_grant_stay_closed(self):
        for model_key, embedding_key in ((False, True), (True, False), (True, True)):
            with self.subTest(model=model_key, embedding=embedding_key), self.isolated_app(
                    model_key=model_key, embedding_key=embedding_key) as (app, client, headers, *_):
                body = self.diagnostic(client, headers)
                diag = body["diagnostics"]["readiness"]
                self.assertEqual(diag["key_presence"], {"model": model_key, "embedding": embedding_key})
                self.assertFalse(body["continue"]["available"])
                self.assertFalse(body["retrieval"]["available"])
                self.assertFalse(body["q_approval"]["real_outbound_authorized"])
                self.assertIsNone(diag["qualification"]["metering"])
                self.assertIsNone(diag["qualification"]["account"])
                self.assertFalse(diag["authorizes_requests"])

    def test_candidate_effective_limits_and_strict_allowlists(self):
        with self.isolated_app() as (app, client, headers, *_):
            diag = self.diagnostic(client, headers)["diagnostics"]["readiness"]
            candidate, effective = diag["candidate"]["model"], diag["effective"]["model"]
            self.assertTrue(candidate["execution"]["available"])
            self.assertEqual(effective["execution"], {"available": False, "reason": "outbound_not_authorized"})
            self.assertEqual(candidate["service"]["returned_models"], ["deepseek-flash"])
            self.assertEqual(candidate["service"]["limits"], {"timeout_seconds": 10.0,
                "max_request_bytes": 65536, "max_response_bytes": 65536, "max_output_tokens": 8192})
            self.assertEqual(candidate["output_limits"]["learning"]["max_output_tokens"], 128)
            self.assertIsNone(effective["output_limits"]["learning"]["max_output_tokens"])
            embedding = diag["effective"]["embedding"]["service"]
            self.assertEqual(embedding["returned_models"], ["embedding-3"])
            self.assertEqual(embedding["limits"]["max_batch_items"], 4)
            self.assertEqual(embedding["limits"]["dimensions"], 512)
            self.assertEqual(embedding["returned_models_status"], "configured_not_observed")

    def test_repeat_reads_never_reload_bind_or_add_pg_probes(self):
        with self.isolated_app() as (app, client, headers, calls, activity, integration):
            app.state.activities_ledger = SimpleNamespace(probe_memory=AsyncMock(return_value={"read": True}))
            app.state.activity_config = replace(app.state.activity_config, memory_layer=LayerState(True))
            # 保留原GET的storage/memory行为，只计其既有合成probe。
            with patch("app.activities.api.ActivityService.probe_storage", new=AsyncMock(return_value=True)) as probe:
                first = self.diagnostic(client, headers)["diagnostics"]["readiness"]
                activity.write_text("{changed", encoding="utf-8")
                integration.write_text("{changed", encoding="utf-8")
                os.environ.clear()
                with patch.object(Path, "read_text", side_effect=AssertionError("GET重读文件")), \
                     patch.object(Path, "read_bytes", side_effect=AssertionError("GET重读文件")):
                    second = self.diagnostic(client, headers)["diagnostics"]["readiness"]
                self.assertEqual(first, second)
                self.assertEqual(probe.await_count, 2)
                self.assertEqual(app.state.activities_ledger.probe_memory.await_count, 2)
                second["key_presence"]["model"] = False
                self.assertTrue(read_readiness(app.state)["key_presence"]["model"])

    def test_auth_context_readonly_and_error_redaction(self):
        with self.isolated_app() as (app, client, headers, *_):
            self.assertEqual(client.get("/api/activities/capabilities").status_code, 403)
            for extra in ({"origin": "https://cross.invalid"}, {"sec-fetch-site": "cross-site"}):
                self.assertEqual(client.get("/api/activities/capabilities", headers={**headers, **extra}).status_code, 403)
            for profile in ("data_exit.v1.r01", "data_exit.v1.r02"):
                context = DataContext("synthetic-control", 1, "synthetic-dataset", "synthetic-instance", "restored_readonly")
                gate = Mock()
                gate.acquire.side_effect = DataError("data_readonly")
                app.state.data_exit = SimpleNamespace(context=lambda: context, gate=gate,
                    profile=profile, hub=SimpleNamespace(state=Mock(return_value={})))
                self.assertEqual(self.diagnostic(client, headers)["diagnostics"]["readiness"]["qualification"]["state"], "unknown")
                app.state.data_exit.hub.state.assert_not_called()
                stale = client.post("/api/activities", json={}, headers={**headers, "x-retrolume-data-context": "{}"})
                self.assertEqual(stale.json()["code"], "selection_changed")
                readonly = client.post("/api/activities", json={}, headers={**headers, "x-retrolume-data-context": canonical(context.public())})
                self.assertEqual(readonly.json()["code"], "data_readonly")
            app.state.data_exit = None
            app.state.data_exit_error = "storage_unavailable"
            response = client.get("/api/activities/capabilities", headers=headers)
            self.assertEqual(response.status_code, 503)
            for secret in ("TASK123_SYNTHETIC_MODEL_SECRET", "TASK123_SYNTHETIC_EMBEDDING_SECRET"):
                self.assertNotIn(secret, response.text)

    def test_loaded_claims_testonly_and_bad_evidence_cannot_verify(self):
        with self.isolated_app() as (app, client, headers, *_):
            grant = {"schema": "retrolume.outbound-grant.v2", "grant_id": "synthetic-no-authority",
                **{name: "a" * 64 for name in ("approved_receipt_sha256", "q_activation_receipt_sha256",
                    "source_manifest_sha256", "price_snapshot_sha256", "instance_binding_sha256")},
                "valid_from_utc": "2000-01-01T00:00:00+00:00", "valid_until_utc": "2000-01-02T00:00:00+00:00",
                "allowed_activity_ids": ["01800000-0000-4000-8000-000000000001"],
                "provider_capabilities": ["deepseek_chat_completions/deepseek-flash", "zhipu_embeddings/embedding-3"],
                "global_max_requests": 100, "global_max_cost_microunits": 25000000,
                "capabilities_verified": True, "account_terms_verified": True, "token_upper_bound_verified": True,
                "input_rate_cny_per_million": "2", "output_rate_cny_per_million": "8",
                "framing_token_upper_bound": 4096, "margin_percent": 25}
            model = replace(app.state.activity_config, model_service=app.state.activity_config.model_service.model_copy(update={"outbound_grant": grant}))
            integration = IntegrationConfig(app.state.integration_config.service.model_copy(update={"outbound_grant": grant}), None)
            for q_class in ("TESTONLY", "Q"):
                result = build_readiness(model, integration, effective_model=model, effective_embedding=integration,
                    q_approval={"available": True, "execution_class": q_class, "real_outbound_authorized": q_class == "Q"})
                self.assertEqual(result["loaded_evidence"]["grant"]["state"], "shape_validated")
                self.assertTrue(result["loaded_evidence"]["model_embedding_grant_match"])
                self.assertEqual(result["loaded_evidence"]["price"]["state"], "reference_only")
                self.assertIsNone(result["loaded_evidence"]["activation"]["content_match"])
                self.assertIsNone(result["loaded_evidence"]["instance"]["deployment_match"])
                self.assertFalse(result["authorizes_requests"])
                self.assertEqual(result["qualification"]["state"], "unknown")
            bad = IntegrationConfig(integration.service.model_copy(update={"outbound_grant": {"secret": "PRIVATE_EXCEPTION_VALUE"}}), None)
            stream = io.StringIO(); handler = logging.StreamHandler(stream)
            logging.getLogger().addHandler(handler)
            try:
                result = build_readiness(model, bad, effective_model=model, effective_embedding=bad)
            finally:
                logging.getLogger().removeHandler(handler)
            self.assertEqual(result["loaded_evidence"]["reason"], "loaded_evidence_invalid")
            self.assertNotIn("PRIVATE_EXCEPTION_VALUE", json.dumps(result) + stream.getvalue())

    def test_empty_allowlist_unknown_reason_and_secret_fields_are_not_exposed(self):
        with self.isolated_app() as (app, client, headers, *_):
            config = app.state.activity_config
            service = config.model_service.model_copy(update={"returned_models": ()})
            config = replace(config, model_service=service, continue_layer=LayerState(False, "postgres://SECRET_DSN"))
            result = build_readiness(config, effective_model=config)
            self.assertEqual(result["candidate"]["model"]["service"]["returned_models_status"], "allowlist_empty")
            self.assertEqual(result["candidate"]["model"]["execution"]["reason"], "load_state_unknown")
            raw = json.dumps(result)
            for secret in ("SECRET_DSN", "TASK123_SYNTHETIC_MODEL_SECRET", "TASK123_SYNTHETIC_EMBEDDING_SECRET", "api_key", "api_key_env"):
                self.assertNotIn(secret, raw)
            service = service.model_copy(update={"returned_models": ("C:/private-secret",)})
            result = build_readiness(replace(config, model_service=service))
            self.assertIsNone(result["candidate"]["model"]["service"]["returned_models"])
            self.assertNotIn("private-secret", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
