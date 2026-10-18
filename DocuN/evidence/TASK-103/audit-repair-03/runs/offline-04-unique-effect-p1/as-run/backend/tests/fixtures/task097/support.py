"""097专库断言、真实资料发布和每例定向FK清理。"""
import asyncio
from datetime import datetime, timedelta, timezone
import io
import os
from pathlib import Path
import unittest
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from app.activities import ActivitySpec, PostgresAdmissionLedger, SourceSnapshot
from app.materials.repository import PostgresMaterials
from app.storage.originals import OriginalStore
from app.runtime import psycopg_compatible_loop_factory
from app.pdf_import.contracts import PdfImportResult, PdfPage
from app.pdf_review.contracts import ReviewPage

DB="retrolume_task097_g7"
ROLE="retrolume_task097_synth"
DSN=os.environ.get("RETROLUME_TASK097_DSN", "")
ROOT=Path(__file__).resolve().parents[4]


def minimal_pdf():
    # 合成两页PDF，xref按真实字节生成；无外部字体、链接或脚本。
    objects=[b"<< /Type /Catalog /Pages 2 0 R >>",b"<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 7 0 R >> >> >>",
        b"",b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 6 0 R /Resources << /Font << /F1 7 0 R >> >> >>",b"",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for index,text in [(3,"Atomicity: all changes commit together."),(5,"PDF physical page two: atomicity.")]:
        stream=f"BT /F1 14 Tf 72 700 Td ({text}) Tj ET".encode()
        objects[index]=b"<< /Length "+str(len(stream)).encode()+b" >>\nstream\n"+stream+b"\nendstream"
    raw=b"%PDF-1.4\n"; offsets=[0]
    for number,body in enumerate(objects,1):
        offsets.append(len(raw));raw+=f"{number} 0 obj\n".encode()+body+b"\nendobj\n"
    xref=len(raw)
    raw+=f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
    for offset in offsets[1:]: raw+=f"{offset:010d} 00000 n \n".encode()
    return raw+f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


class Fixture:
    def __init__(self,dsn,root):
        self.dsn=dsn;self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
        self.originals=OriginalStore(self.root)
        self.materials=PostgresMaterials(dsn)
        self.ledger=PostgresAdmissionLedger(dsn)
        self.activities=[];self.sources=[]
        fact=self.rows("SELECT current_database() AS db,current_user AS role")[0]
        if fact != {"db":DB,"role":ROLE}: raise ValueError("097合成身份不匹配")
    def rows(self,sql,params=()):
        with psycopg.connect(self.dsn,row_factory=dict_row) as connection:
            cursor=connection.execute(sql,params)
            return cursor.fetchall() if cursor.description else []
    def text(self,text,title="atomicity.md",format="md"):
        raw=text.encode("utf-8");original=self.originals.put(io.BytesIO(raw),max_bytes=5242880)
        row=self.materials.save(source_id=None,expected_version=None,filename=title,format=format,sha256=original.sha256,size=original.size)
        self.sources.append(row["id"]);return row
    def pdf(self, *, confirmed=True, supplement="事务原子性用户补充：一起提交或全部不提交。", title="atomicity.pdf"):
        raw=minimal_pdf();original=self.originals.put(io.BytesIO(raw),max_bytes=5242880)
        extraction=PdfImportResult(2,(PdfPage(1,"Atomicity all changes commit together.\n",()),
            PdfPage(2,"PDF physical page two: atomicity.\n",())),())
        candidate=self.materials.create_pdf_candidate(source_id=None,expected_version=None,expected_revision=0,
            filename=title,sha256=original.sha256,size=original.size,extraction=extraction)
        self.sources.append(candidate["source_id"])
        if not confirmed:return candidate
        return self.materials.confirm_pdf_candidate(candidate_id=candidate["candidate_id"],version_id=candidate["version_id"],
            pages=[ReviewPage(1,True),ReviewPage(2,True,supplement)])
    async def activity(self, rows, **overrides):
        activity_id=str(uuid4());self.activities.append(activity_id)
        values=dict(activity_id=activity_id,sources=tuple(SourceSnapshot(r["id"],r["version_id"],r["revision"]) for r in rows),
            deadline_at=datetime.now(timezone.utc)+timedelta(hours=1),max_requests=16,max_cost_microunits=1600000,
            reserve_cost_microunits=100000,max_request_bytes=65536,max_output_tokens=256,max_running_seconds=900,
            allowed_models=(("deepseek_chat_completions","synthetic-model-097"),))
        await self.ledger.create_activity(ActivitySpec(**(values|overrides)))
        return activity_id
    def cleanup(self):
        for activity in self.activities:
            for table in ["activity_operation_results","activity_operations","activity_allowed_models","activity_scope_sources"]:
                self.rows(f"DELETE FROM {table} WHERE activity_id=%s",(activity,))
            self.rows("DELETE FROM activities WHERE id=%s",(activity,))
        for source in self.sources:
            self.rows("UPDATE material_sources SET current_version=NULL WHERE id=%s",(source,))
            for table in ["pdf_user_supplements","pdf_review_pages","pdf_extracted_pages"]:
                self.rows(f"DELETE FROM {table} WHERE version_id IN (SELECT id FROM material_versions WHERE source_id=%s)",(source,))
            self.rows("DELETE FROM pdf_review_candidates WHERE source_id=%s",(source,))
            self.rows("DELETE FROM material_versions WHERE source_id=%s",(source,))
            self.rows("DELETE FROM material_sources WHERE id=%s",(source,))


class PGBase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self):
        self._asyncioRunner=asyncio.Runner(debug=True,loop_factory=psycopg_compatible_loop_factory)
    async def asyncSetUp(self):
        if not DSN: self.skipTest("097专用合成DSN未注入")
        self.fixture=Fixture(DSN,ROOT/"DocuN/evidence/TASK-097/runtime/pg-originals")
        self.ledger=self.fixture.ledger
    async def asyncTearDown(self): self.fixture.cleanup()
