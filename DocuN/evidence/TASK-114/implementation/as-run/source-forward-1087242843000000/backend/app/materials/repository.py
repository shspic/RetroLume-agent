"""PostgreSQL来源版本适配器；不创建表，不使用文件元数据替代数据库。"""
from contextlib import contextmanager
import json
from uuid import UUID, uuid4

from app.pdf_review.contracts import validate_review_pages

class VersionConflict(Exception):
    pass

class DatabaseUnavailable(Exception):
    pass

class PostgresMaterials:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.mutation_gate = None
        self.reference_coordinator = None
        self.data_enabled = False

    def configure_data_exit(self, gate, references=None):
        self.mutation_gate, self.reference_coordinator, self.data_enabled = gate, references, True
        self.CANDIDATE_SELECT = type(self).CANDIDATE_SELECT.replace(
            "JOIN material_sources s ON s.id=c.source_id",
            "JOIN material_sources s ON s.id=c.source_id AND NOT EXISTS(SELECT 1 FROM data_tombstones dt WHERE dt.entity_kind='source' AND dt.entity_id=s.id)")

    @contextmanager
    def connection(self, *, writable=False, reference_pin=None):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            raise DatabaseUnavailable("尚未安装PostgreSQL驱动") from None
        try:
            with psycopg.connect(self.dsn, connect_timeout=3, row_factory=dict_row) as conn:
                if writable:
                    if self.data_enabled and self.mutation_gate is None:
                        from app.data_exit.contracts import DataError
                        raise DataError("data_readonly")
                    if self.mutation_gate is not None:
                        with self.mutation_gate.acquire():
                            if reference_pin is not None: reference_pin.bind(conn)
                            else:conn.execute('SELECT public.data_mutation_enter()')
                            yield conn
                            if reference_pin is not None: reference_pin.commit(conn)
                            conn.commit()
                        return
                yield conn
        except psycopg.Error:
            # 不向用户返回连接串、SQL或服务器内部错误。
            raise DatabaseUnavailable("本地数据库暂不可用或尚未初始化") from None

    @staticmethod
    def normalize(row):
        if row is None:
            return None
        return {
            key: value.isoformat() if hasattr(value, "isoformat")
            else str(value) if isinstance(value, UUID)
            else value
            for key, value in row.items()
        }

    SELECT = """SELECT s.id,s.title,s.revision,v.id AS version_id,v.sha256,v.size,v.filename,v.format,v.created_at
                FROM material_sources s JOIN material_versions v ON v.id=s.current_version"""

    def list(self, limit=100, offset=0):
        with self.connection() as conn:
            return [self.normalize(row) for row in conn.execute(self.SELECT + " ORDER BY v.created_at DESC,s.id LIMIT %s OFFSET %s", (limit, offset)).fetchall()]

    def get(self, source_id):
        with self.connection() as conn:
            return self.normalize(conn.execute(self.SELECT + " WHERE s.id=%s", (source_id,)).fetchone())

    def save(self, *, source_id, expected_version, filename, format, sha256, size, reference_pin=None, prepared_ids=None):
        self._require_reference(reference_pin, prepared_ids)
        with self.connection(writable=True, reference_pin=reference_pin) as conn:
            if source_id:
                source = conn.execute("SELECT id,current_version FROM material_sources WHERE id=%s FOR UPDATE", (source_id,)).fetchone()
                if source is None:
                    raise KeyError(source_id)
                if str(source["current_version"]) != expected_version:
                    raise VersionConflict()
            else:
                source_id = prepared_ids.source_id if prepared_ids is not None else str(uuid4())
                conn.execute("INSERT INTO material_sources(id,title,revision) VALUES(%s,%s,0)", (source_id, filename))
            version_id = prepared_ids.version_id if prepared_ids is not None else str(uuid4())
            conn.execute("INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES(%s,%s,%s,%s,%s,%s)", (version_id, source_id, filename, format, sha256, size))
            conn.execute("UPDATE material_sources SET current_version=%s,revision=revision+1,title=%s WHERE id=%s", (version_id, filename, source_id))
            return self.normalize(conn.execute(self.SELECT + " WHERE s.id=%s", (source_id,)).fetchone())

    CANDIDATE_SELECT = """SELECT c.id AS candidate_id,c.source_id,c.version_id,c.expected_version,
                           c.expected_revision,c.status,c.page_count,c.extraction_method,c.created_at,c.decided_at,
                           v.filename,v.sha256,v.size,s.title,s.current_version,s.revision
                           FROM pdf_review_candidates c
                           JOIN material_versions v ON v.id=c.version_id
                           JOIN material_sources s ON s.id=c.source_id"""

    def _require_reference(self, pin, prepared):
        if self.data_enabled:
            from app.data_exit.contracts import DataError
            if self.reference_coordinator is None or pin is None or prepared is None or pin.coordinator is not self.reference_coordinator:
                raise DataError("reference_pin_required")
            pin.check(self.reference_coordinator.root, prepared)

    def create_pdf_candidate(
        self,
        *,
        source_id,
        expected_version,
        expected_revision,
        filename,
        sha256,
        size,
        extraction,
        reference_pin=None,
        prepared_ids=None,
    ):
        self._require_reference(reference_pin, prepared_ids)
        with self.connection(writable=True, reference_pin=reference_pin) as conn:
            if source_id:
                source = conn.execute(
                    "SELECT id,current_version,revision FROM material_sources WHERE id=%s FOR UPDATE",
                    (source_id,),
                ).fetchone()
                if source is None:
                    raise KeyError(source_id)
                if str(source["current_version"]) != expected_version or source["revision"] != expected_revision:
                    raise VersionConflict()
            else:
                if expected_version is not None or expected_revision != 0:
                    raise VersionConflict()
                source_id = prepared_ids.source_id if prepared_ids is not None else str(uuid4())
                conn.execute(
                    "INSERT INTO material_sources(id,title,revision) VALUES(%s,%s,0)",
                    (source_id, filename),
                )
            version_id, candidate_id = (prepared_ids.version_id, prepared_ids.candidate_id) if prepared_ids is not None else (str(uuid4()), str(uuid4()))
            conn.execute(
                "INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES(%s,%s,%s,'pdf',%s,%s)",
                (version_id, source_id, filename, sha256, size),
            )
            conn.execute(
                """INSERT INTO pdf_review_candidates(
                       id,source_id,version_id,expected_version,expected_revision,status,page_count,extraction_method
                   ) VALUES(%s,%s,%s,%s,%s,'pending',%s,%s)""",
                (
                    candidate_id,
                    source_id,
                    version_id,
                    expected_version,
                    expected_revision,
                    extraction.page_count,
                    extraction.extraction_method,
                ),
            )
            with conn.cursor() as cursor:
                cursor.executemany(
                    """INSERT INTO pdf_extracted_pages(version_id,physical_page,extracted_text,warnings)
                       VALUES(%s,%s,%s,%s::jsonb)""",
                    [
                        (
                            version_id,
                            page.physical_page,
                            page.text,
                            json.dumps(page.warnings, ensure_ascii=False),
                        )
                        for page in extraction.pages
                    ],
                )
            row = conn.execute(self.CANDIDATE_SELECT + " WHERE c.id=%s", (candidate_id,)).fetchone()
            return self.normalize(row)

    def list_pdf_candidates(self):
        with self.connection() as conn:
            rows = conn.execute(
                self.CANDIDATE_SELECT + " WHERE c.status='pending' ORDER BY c.created_at,c.id"
            ).fetchall()
            return [self.normalize(row) for row in rows]

    def get_pdf_candidate(self, candidate_id):
        with self.connection() as conn:
            row = conn.execute(self.CANDIDATE_SELECT + " WHERE c.id=%s", (candidate_id,)).fetchone()
            if row is None:
                return None
            result = self.normalize(row)
            pages = conn.execute(
                """SELECT physical_page,extracted_text,warnings
                   FROM pdf_extracted_pages WHERE version_id=%s ORDER BY physical_page""",
                (row["version_id"],),
            ).fetchall()
            result["pages"] = [
                {
                    "version_id": str(row["version_id"]),
                    "physical_page": page["physical_page"],
                    "raw_text": page["extracted_text"],
                    "identity": "pdf_extracted_text",
                    "warnings": page["warnings"],
                }
                for page in pages
            ]
            result["query_ready"] = False
            return result

    def get_pdf_candidate_original(self, candidate_id):
        with self.connection() as conn:
            if self.data_enabled:
                visible = conn.execute(self.CANDIDATE_SELECT + " WHERE c.id=%s", (candidate_id,)).fetchone()
                if visible is None: return None
            row = conn.execute(
                """SELECT v.filename,v.sha256,v.size
                   FROM pdf_review_candidates c JOIN material_versions v ON v.id=c.version_id
                   WHERE c.id=%s""",
                (candidate_id,),
            ).fetchone()
            return self.normalize(row)

    def confirm_pdf_candidate(self, *, candidate_id, version_id, pages, reference_pin=None):
        self._require_reference(reference_pin, None if reference_pin is None else reference_pin.prepared)
        with self.connection(writable=True, reference_pin=reference_pin) as conn:
            candidate_hint = conn.execute(
                "SELECT source_id FROM pdf_review_candidates WHERE id=%s",
                (candidate_id,),
            ).fetchone()
            if candidate_hint is None:
                raise KeyError(candidate_id)
            source = conn.execute(
                "SELECT id,current_version,revision FROM material_sources WHERE id=%s FOR UPDATE",
                (candidate_hint["source_id"],),
            ).fetchone()
            candidate = conn.execute(
                """SELECT id,source_id,version_id,expected_version,expected_revision,status,page_count
                   FROM pdf_review_candidates WHERE id=%s FOR UPDATE""",
                (candidate_id,),
            ).fetchone()
            if candidate is None:
                raise KeyError(candidate_id)
            if candidate["status"] != "pending" or str(candidate["version_id"]) != version_id:
                raise VersionConflict()
            current_version = str(source["current_version"]) if source["current_version"] is not None else None
            expected_version = str(candidate["expected_version"]) if candidate["expected_version"] is not None else None
            if current_version != expected_version or source["revision"] != candidate["expected_revision"]:
                raise VersionConflict()
            checked = validate_review_pages(candidate["page_count"], pages)
            with conn.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO pdf_review_pages(candidate_id,version_id,physical_page) VALUES(%s,%s,%s)",
                    [(candidate_id, version_id, page.physical_page) for page in checked],
                )
                supplements = [
                    (str(uuid4()), candidate_id, version_id, page.physical_page, page.supplement)
                    for page in checked
                    if page.supplement is not None and page.supplement.strip()
                ]
                if supplements:
                    cursor.executemany(
                        """INSERT INTO pdf_user_supplements(id,candidate_id,version_id,physical_page,text)
                           VALUES(%s,%s,%s,%s,%s)""",
                        supplements,
                    )
            filename = conn.execute(
                "SELECT filename FROM material_versions WHERE id=%s",
                (version_id,),
            ).fetchone()["filename"]
            conn.execute(
                "UPDATE material_sources SET current_version=%s,revision=revision+1,title=%s WHERE id=%s",
                (version_id, filename, source["id"]),
            )
            conn.execute(
                "UPDATE pdf_review_candidates SET status='confirmed',decided_at=CURRENT_TIMESTAMP WHERE id=%s",
                (candidate_id,),
            )
            return self.normalize(conn.execute(self.SELECT + " WHERE s.id=%s", (source["id"],)).fetchone())

    def skip_pdf_candidate(self, candidate_id):
        with self.connection(writable=True) as conn:
            hint = conn.execute(
                "SELECT source_id FROM pdf_review_candidates WHERE id=%s",
                (candidate_id,),
            ).fetchone()
            if hint is None:
                raise KeyError(candidate_id)
            conn.execute(
                "SELECT id FROM material_sources WHERE id=%s FOR UPDATE",
                (hint["source_id"],),
            ).fetchone()
            row = conn.execute(
                self.CANDIDATE_SELECT + " WHERE c.id=%s FOR UPDATE OF c",
                (candidate_id,),
            ).fetchone()
            if row is None:
                raise KeyError(candidate_id)
            if row["status"] != "pending":
                raise VersionConflict()
            conn.execute(
                "UPDATE pdf_review_candidates SET status='skipped',decided_at=CURRENT_TIMESTAMP WHERE id=%s",
                (candidate_id,),
            )
            result = self.normalize(row)
            result["status"] = "skipped"
            result["query_ready"] = False
            return result

    def get_active_pdf_pages(self, source_id, version_id):
        with self.connection() as conn:
            material = conn.execute(self.SELECT + " WHERE s.id=%s", (source_id,)).fetchone()
            if material is None:
                return None
            if str(material["version_id"]) != version_id:
                raise VersionConflict()
            if material["format"] != "pdf":
                return None
            candidate = conn.execute(
                "SELECT id,status FROM pdf_review_candidates WHERE version_id=%s",
                (version_id,),
            ).fetchone()
            if candidate is None or candidate["status"] != "confirmed":
                raise VersionConflict()
            pages = conn.execute(
                """SELECT physical_page,extracted_text,warnings FROM pdf_extracted_pages
                   WHERE version_id=%s ORDER BY physical_page""",
                (version_id,),
            ).fetchall()
            supplements = conn.execute(
                """SELECT id,version_id,physical_page,text,created_at FROM pdf_user_supplements
                   WHERE version_id=%s ORDER BY physical_page,created_at,id""",
                (version_id,),
            ).fetchall()
            by_page = {}
            for supplement in supplements:
                normalized = self.normalize(supplement)
                normalized["identity"] = "user_supplement"
                by_page.setdefault(supplement["physical_page"], []).append(normalized)
            return {
                "material": self.normalize(material),
                "review_status": "confirmed",
                "query_ready": True,
                "pages": [
                    {
                        "version_id": version_id,
                        "physical_page": page["physical_page"],
                        "raw_text": page["extracted_text"],
                        "identity": "pdf_extracted_text",
                        "warnings": page["warnings"],
                        "supplements": by_page.get(page["physical_page"], []),
                    }
                    for page in pages
                ],
            }

    def get_active_pdf_original(self, source_id, version_id):
        with self.connection() as conn:
            row = conn.execute(
                """SELECT v.id AS version_id,v.filename,v.sha256,v.size,v.format
                   FROM material_sources s JOIN material_versions v ON v.id=s.current_version
                   WHERE s.id=%s""",
                (source_id,),
            ).fetchone()
            if row is None:
                return None
            if str(row["version_id"]) != version_id:
                raise VersionConflict()
            if row["format"] != "pdf":
                return None
            return self.normalize(row)
