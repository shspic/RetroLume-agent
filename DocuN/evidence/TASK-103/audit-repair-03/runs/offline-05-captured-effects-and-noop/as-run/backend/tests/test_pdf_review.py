"""PDF候选HTTP/领域契约；内存仓储仅用于本卡，不代表PostgreSQL已验证。"""
import os
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from app.materials.repository import VersionConflict
from app.pdf_import import PdfImportResult, PdfInvalidError, PdfPage
from app.pdf_review.contracts import validate_review_pages


class MemoryPdfMaterials:
    def __init__(self):
        self.sources = {}
        self.candidates = {}

    def list(self, limit=100, offset=0):
        active = [source["current"] for source in self.sources.values() if source["current"]]
        return active[offset:offset + limit]

    def get(self, source_id):
        source = self.sources.get(source_id)
        return source["current"] if source else None

    def save(self, *, source_id, expected_version, filename, format, sha256, size):
        source = self.sources.get(source_id)
        if source_id and source is None:
            raise KeyError(source_id)
        if source and (source["current"] is None or source["current"]["version_id"] != expected_version):
            raise VersionConflict()
        source_id = source_id or str(uuid4())
        revision = source["revision"] + 1 if source else 1
        row = dict(id=source_id, title=filename, version_id=str(uuid4()), revision=revision,
                   filename=filename, format=format, sha256=sha256, size=size,
                   created_at="2026-09-14T00:00:00+00:00")
        self.sources[source_id] = {"current": row, "revision": revision, "title": filename}
        return row

    def create_pdf_candidate(self, *, source_id, expected_version, expected_revision, filename, sha256, size, extraction):
        source = self.sources.get(source_id)
        if source_id and source is None:
            raise KeyError(source_id)
        current = source["current"] if source else None
        revision = source["revision"] if source else 0
        if (current["version_id"] if current else None) != expected_version or revision != expected_revision:
            raise VersionConflict()
        source_id = source_id or str(uuid4())
        if source is None:
            source = {"current": None, "revision": 0, "title": filename}
            self.sources[source_id] = source
        candidate_id, version_id = str(uuid4()), str(uuid4())
        candidate = dict(candidate_id=candidate_id, source_id=source_id, version_id=version_id,
                         expected_version=expected_version, expected_revision=expected_revision,
                         filename=filename, sha256=sha256, size=size, page_count=extraction.page_count,
                         extraction_method=extraction.extraction_method, status="pending",
                         current_version=current["version_id"] if current else None,
                         revision=revision, created_at="2026-09-14T00:00:00+00:00",
                         pages=[dict(version_id=version_id, physical_page=page.physical_page,
                                     raw_text=page.text,
                                     identity="pdf_extracted_text", warnings=list(page.warnings))
                                for page in extraction.pages], supplements=[])
        self.candidates[candidate_id] = candidate
        return {key: value for key, value in candidate.items() if key not in {"pages", "supplements"}}

    def list_pdf_candidates(self):
        return [{key: value for key, value in item.items() if key not in {"pages", "supplements"}}
                for item in self.candidates.values() if item["status"] == "pending"]

    def get_pdf_candidate(self, candidate_id):
        candidate = self.candidates.get(candidate_id)
        if not candidate:
            return None
        result = {**candidate, "query_ready": False}
        result.pop("supplements")
        return result

    def get_pdf_candidate_original(self, candidate_id):
        item = self.candidates.get(candidate_id)
        return {key: item[key] for key in ("filename", "sha256", "size")} if item else None

    def confirm_pdf_candidate(self, *, candidate_id, version_id, pages):
        candidate = self.candidates.get(candidate_id)
        if not candidate:
            raise KeyError(candidate_id)
        source = self.sources[candidate["source_id"]]
        current = source["current"]
        if candidate["status"] != "pending" or candidate["version_id"] != version_id:
            raise VersionConflict()
        if (current["version_id"] if current else None) != candidate["expected_version"] or source["revision"] != candidate["expected_revision"]:
            raise VersionConflict()
        checked = validate_review_pages(candidate["page_count"], pages)
        candidate["supplements"] = [dict(id=str(uuid4()), version_id=version_id, physical_page=page.physical_page,
                                          text=page.supplement, identity="user_supplement")
                                    for page in checked if page.supplement and page.supplement.strip()]
        source["revision"] += 1
        source["current"] = dict(id=candidate["source_id"], title=candidate["filename"],
                                 version_id=version_id, revision=source["revision"], filename=candidate["filename"],
                                 format="pdf", sha256=candidate["sha256"], size=candidate["size"],
                                 created_at="2026-09-14T00:00:00+00:00")
        candidate["status"] = "confirmed"
        return source["current"]

    def skip_pdf_candidate(self, candidate_id):
        candidate = self.candidates.get(candidate_id)
        if not candidate:
            raise KeyError(candidate_id)
        if candidate["status"] != "pending":
            raise VersionConflict()
        candidate["status"] = "skipped"
        return {**candidate, "query_ready": False}

    def get_active_pdf_pages(self, source_id, version_id):
        source = self.sources.get(source_id)
        if not source or not source["current"]:
            return None
        if source["current"]["version_id"] != version_id:
            raise VersionConflict()
        candidate = next((item for item in self.candidates.values()
                          if item["version_id"] == version_id and item["status"] == "confirmed"), None)
        if not candidate:
            return None
        supplements = {}
        for item in candidate["supplements"]:
            supplements.setdefault(item["physical_page"], []).append(item)
        pages = [{**page, "supplements": supplements.get(page["physical_page"], [])} for page in candidate["pages"]]
        return {"material": source["current"], "review_status": "confirmed", "query_ready": True, "pages": pages}

    def get_active_pdf_original(self, source_id, version_id):
        source = self.sources.get(source_id)
        if not source or not source["current"]:
            return None
        row = source["current"]
        if row["version_id"] != version_id:
            raise VersionConflict()
        if row["format"] != "pdf":
            return None
        return {key: row[key] for key in ("filename", "sha256", "size")}


class PdfReviewTests(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.TemporaryDirectory(); self.backup = tempfile.TemporaryDirectory()
        self.addCleanup(self.data.cleanup); self.addCleanup(self.backup.cleanup)
        self.env = patch.dict(os.environ, {"RETROLUME_DATA_DIR": self.data.name,
                                           "RETROLUME_BACKUP_DIR": self.backup.name,
                                           "RETROLUME_DATABASE_URL": ""})
        self.env.start(); self.addCleanup(self.env.stop)
        self.repo = MemoryPdfMaterials(); self.client = TestClient(create_app(self.repo)); self.addCleanup(self.client.close)
        self.token = self.client.get("/api/session").json()["token"]
        self.headers = {"x-retrolume-session": self.token, "origin": "http://127.0.0.1:8000"}
        self.extraction = PdfImportResult(2, (PdfPage(1, "raw one", ()), PdfPage(2, "raw two", ())), ())

    def upload(self, name, body, **params):
        return self.client.post("/api/materials", params={"filename": name, **params}, content=body, headers=self.headers)

    def upload_pdf(self, **params):
        with patch("app.materials.api.parse_pdf_bytes", return_value=self.extraction):
            return self.upload("source.pdf", b"%PDF synthetic original", **params)

    def test_first_pdf_is_complete_pending_candidate_and_not_active(self):
        response = self.upload_pdf()
        self.assertEqual(response.status_code, 200)
        candidate = response.json()["candidate"]
        self.assertFalse(response.json()["query_ready"])
        self.assertEqual(self.client.get("/api/materials", headers=self.headers).json()["items"], [])
        detail = self.client.get(f"/api/pdf-candidates/{candidate['candidate_id']}", headers=self.headers).json()["candidate"]
        self.assertEqual([page["physical_page"] for page in detail["pages"]], [1, 2])
        self.assertEqual(detail["pages"][0]["raw_text"], "raw one")
        self.assertEqual(detail["pages"][0]["identity"], "pdf_extracted_text")
        self.assertEqual(detail["version_id"], candidate["version_id"])
        self.assertEqual(detail["sha256"], candidate["sha256"])

    def test_missing_duplicate_out_of_range_rejected_then_supplement_keeps_identity(self):
        candidate = self.upload_pdf().json()["candidate"]
        url = f"/api/pdf-candidates/{candidate['candidate_id']}/confirm"
        invalid = [
            [{"physical_page": 1, "reviewed": True}],
            [{"physical_page": 1, "reviewed": True}, {"physical_page": 1, "reviewed": True}],
            [{"physical_page": 1, "reviewed": True}, {"physical_page": 3, "reviewed": True}],
        ]
        for pages in invalid:
            self.assertEqual(self.client.post(url, json={"version_id": candidate["version_id"], "pages": pages}, headers=self.headers).status_code, 422)
        pages = [{"physical_page": 1, "reviewed": True, "supplement": "用户纠字说明"},
                 {"physical_page": 2, "reviewed": True}]
        confirmed = self.client.post(url, json={"version_id": candidate["version_id"], "pages": pages}, headers=self.headers)
        self.assertEqual(confirmed.status_code, 200)
        content_url = f"/api/materials/{candidate['source_id']}/content?expected_version={candidate['version_id']}"
        with patch.object(self.client.app.state.originals, "read", side_effect=AssertionError("PDF content不得解码原字节")):
            content = self.client.get(content_url, headers=self.headers).json()
        self.assertTrue(content["query_ready"])
        self.assertEqual(content["pages"][0]["raw_text"], "raw one")
        self.assertEqual(content["pages"][0]["identity"], "pdf_extracted_text")
        self.assertEqual(content["pages"][0]["supplements"][0]["identity"], "user_supplement")

    def test_stale_confirmation_cannot_replace_intervening_update(self):
        old = self.upload("old.md", b"old").json()["material"]
        candidate = self.upload_pdf(source_id=old["id"], expected_version=old["version_id"], expected_revision=old["revision"]).json()["candidate"]
        newer = self.upload("new.txt", b"new", source_id=old["id"], expected_version=old["version_id"]).json()["material"]
        pages = [{"physical_page": 1, "reviewed": True}, {"physical_page": 2, "reviewed": True}]
        response = self.client.post(f"/api/pdf-candidates/{candidate['candidate_id']}/confirm",
                                    json={"version_id": candidate["version_id"], "pages": pages}, headers=self.headers)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.repo.get(old["id"])["version_id"], newer["version_id"])

    def test_skip_and_parse_failure_leave_old_version_active(self):
        old = self.upload("old.md", b"old").json()["material"]
        params = dict(source_id=old["id"], expected_version=old["version_id"], expected_revision=old["revision"])
        candidate = self.upload_pdf(**params).json()["candidate"]
        skipped = self.client.post(f"/api/pdf-candidates/{candidate['candidate_id']}/skip", headers=self.headers)
        self.assertEqual(skipped.status_code, 200)
        self.assertEqual(self.repo.get(old["id"])["version_id"], old["version_id"])
        with patch("app.materials.api.parse_pdf_bytes", side_effect=PdfInvalidError("bad")):
            failed = self.upload("bad.pdf", b"not a pdf", **params)
        self.assertEqual(failed.status_code, 422)
        self.assertEqual(self.repo.get(old["id"])["version_id"], old["version_id"])

    def test_original_bytes_use_only_session_controlled_pdf_endpoints(self):
        candidate = self.upload_pdf().json()["candidate"]
        url = f"/api/pdf-candidates/{candidate['candidate_id']}/original"
        self.assertEqual(self.client.get(url).status_code, 403)
        original = self.client.get(url, headers=self.headers)
        self.assertEqual(original.content, b"%PDF synthetic original")
        self.assertEqual(original.headers["content-type"], "application/pdf")

    def test_pdf_to_text_conversion_uses_current_version_cas(self):
        candidate = self.upload_pdf().json()["candidate"]
        pages = [{"physical_page": 1, "reviewed": True}, {"physical_page": 2, "reviewed": True}]
        active = self.client.post(f"/api/pdf-candidates/{candidate['candidate_id']}/confirm",
                                  json={"version_id": candidate["version_id"], "pages": pages}, headers=self.headers).json()["material"]
        text = self.upload("replacement.md", b"text", source_id=active["id"], expected_version=active["version_id"])
        self.assertEqual(text.status_code, 200)
        self.assertEqual(text.json()["material"]["format"], "md")
        stale = self.upload("stale.txt", b"stale", source_id=active["id"], expected_version=active["version_id"])
        self.assertEqual(stale.status_code, 409)


if __name__ == "__main__":
    unittest.main()
