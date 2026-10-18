import os
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import create_app

class ConfigurationTests(unittest.TestCase):
    def test_missing_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "RETROLUME_DATA_DIR"):
                create_app()

    def test_health_and_host_boundary(self):
        with tempfile.TemporaryDirectory() as data, tempfile.TemporaryDirectory() as backup:
            with patch.dict(os.environ, {"RETROLUME_DATA_DIR": data, "RETROLUME_BACKUP_DIR": backup}):
                with TestClient(create_app()) as client:
                    self.assertEqual(client.get("/health").json(), {"status": "ok", "mode": "development"})
                    self.assertEqual(client.get("/health", headers={"host": "untrusted.example"}).status_code, 400)

    def test_overlapping_directories(self):
        with tempfile.TemporaryDirectory() as data:
            with patch.dict(os.environ, {"RETROLUME_DATA_DIR": data, "RETROLUME_BACKUP_DIR": data}):
                with self.assertRaisesRegex(ValueError, "必须独立"):
                    create_app()

if __name__ == "__main__":
    unittest.main()
