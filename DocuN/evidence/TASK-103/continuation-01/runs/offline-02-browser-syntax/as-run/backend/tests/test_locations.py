"""TASK-045：行段位置和当前版本绑定的局部 HTTP 契约。"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from app.materials.repository import VersionConflict


class MemoryMaterials:
    def __init__(self):
        self.rows = {}

    def list(self, limit=100, offset=0):
        return list(self.rows.values())[offset:offset + limit]

    def get(self, source_id):
        return self.rows.get(source_id)

    def save(self, *, source_id, expected_version, filename, format, sha256, size):
        previous = self.rows.get(source_id)
        if source_id and previous is None:
            raise KeyError(source_id)
        if previous and previous["version_id"] != expected_version:
            raise VersionConflict()
        source_id = source_id or str(uuid4())
        row = {"id": source_id, "title": filename, "version_id": str(uuid4()), "revision": (previous["revision"] if previous else 0) + 1, "filename": filename, "format": format, "sha256": sha256, "size": size, "created_at": "2026-09-14T00:00:00+00:00"}
        self.rows[source_id] = row
        return row


class LocationTests(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.TemporaryDirectory()
        self.backup = tempfile.TemporaryDirectory()
        self.addCleanup(self.data.cleanup)
        self.addCleanup(self.backup.cleanup)
        self.env = patch.dict(os.environ, {"RETROLUME_DATA_DIR": self.data.name, "RETROLUME_BACKUP_DIR": self.backup.name, "RETROLUME_DATABASE_URL": ""})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.repo = MemoryMaterials()
        self.client = TestClient(create_app(self.repo))
        self.addCleanup(self.client.close)
        self.headers = {"x-retrolume-session": self.client.get("/api/session").json()["token"]}

    def upload(self, body, name="notes.md", **params):
        return self.client.post("/api/materials", params={"filename": name, **params}, content=body.encode("utf-8"), headers=self.headers)

    def content(self, source_id, **params):
        return self.client.get(f"/api/materials/{source_id}/content", params=params, headers=self.headers)

    def test_locations_preserve_text_and_only_recognize_three_newlines(self):
        cases = [("中文\nEnglish\n\n第三段", "LF", 4, [{"paragraph": 1, "start_line": 1, "end_line": 2}, {"paragraph": 2, "start_line": 4, "end_line": 4}]), ("a\r\nb\r\n", "CRLF", 3, [{"paragraph": 1, "start_line": 1, "end_line": 2}]), ("a\rb", "CR", 2, [{"paragraph": 1, "start_line": 1, "end_line": 2}]), ("<img src=x onerror=alert(1)>\u2028literal", "none", 1, [{"paragraph": 1, "start_line": 1, "end_line": 1}])]
        for text, ending, line_count, paragraphs in cases:
            with self.subTest(ending=ending):
                row = self.upload(text).json()["material"]
                payload = self.content(row["id"]).json()
                self.assertEqual(payload["text"], text)
                self.assertEqual(payload["locations"]["line_ending"], ending)
                self.assertEqual(payload["locations"]["total_lines"], line_count)
                self.assertEqual(payload["locations"]["paragraphs"], paragraphs)

    def test_excerpt_range_limits_and_missing_pair_are_rejected(self):
        row = self.upload("第一行\n\n第三行").json()["material"]
        response = self.content(row["id"], expected_version=row["version_id"], start_line=1, end_line=2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["excerpt"], {"start_line": 1, "end_line": 2, "text": "第一行\n"})
        self.assertEqual(self.content(row["id"], start_line=1).status_code, 400)
        self.assertEqual(self.content(row["id"], start_line=0, end_line=1).status_code, 422)
        self.assertEqual(self.content(row["id"], start_line=2, end_line=9).status_code, 422)

    def test_excerpt_keeps_crlf_and_cr_between_selected_lines(self):
        for text, expected in [("甲\r\n乙\r\n丙", "甲\r\n乙"), ("甲\r乙\r丙", "甲\r乙")]:
            with self.subTest(text=repr(text)):
                row = self.upload(text).json()["material"]
                response = self.content(row["id"], start_line=1, end_line=2)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["excerpt"]["text"], expected)

    def test_replaced_version_cannot_read_current_text_as_old_reference(self):
        old = self.upload("旧版第一行").json()["material"]
        new = self.upload("新版第一行", source_id=old["id"], expected_version=old["version_id"]).json()["material"]
        stale = self.content(old["id"], expected_version=old["version_id"], start_line=1, end_line=1)
        self.assertEqual(stale.status_code, 409)
        self.assertIn("不能以当前原文冒充旧引用", stale.json()["detail"])
        current = self.content(old["id"], expected_version=new["version_id"], start_line=1, end_line=1)
        self.assertEqual(current.status_code, 200)
        self.assertEqual(current.json()["excerpt"]["text"], "新版第一行")

    def test_many_paragraphs_return_a_bounded_metadata_window(self):
        text = "\n\n".join(f"p{i}" for i in range(101))
        row = self.upload(text).json()["material"]
        location = self.content(row["id"]).json()["locations"]
        self.assertEqual(location["total_paragraphs"], 101)
        self.assertEqual(len(location["paragraphs"]), 100)
        self.assertTrue(location["paragraphs_truncated"])


if __name__ == "__main__":
    unittest.main()
