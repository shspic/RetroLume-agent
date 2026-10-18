"""真实PG/HTTP合并阶段，原始输出由统一runner保存。"""
import json
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/"backend"));sys.path.insert(0,str(ROOT/"DocuN/evidence/TASK-097"))
from artifacts import write,imported_modules
from tests.fixtures.task097.network import install
install()
# 第一批三次setUp在建资料后、建活动前被selfpipe守卫中断。
# 新建097空库与三份相同固定样本的身份可以精确归属；按实际ID清理。
from tests.fixtures.task097.support import Fixture,DSN
from tests.fixtures.task097.samples import ENGLISH
import hashlib
fixture=Fixture(DSN,ROOT/"DocuN/evidence/TASK-097/runtime/pg-originals")
orphans=fixture.rows("SELECT s.id::text AS source_id FROM material_sources s JOIN material_versions v ON v.source_id=s.id "
    "WHERE v.filename='atomicity.md' AND v.sha256=%s AND NOT EXISTS(SELECT 1 FROM activity_scope_sources a WHERE a.source_id=s.id)",
    (hashlib.sha256(ENGLISH.encode()).hexdigest(),))
if orphans:
    if len(orphans)!=3:raise ValueError("遗留合成资料归属数量不匹配")
    write(Path(os.environ["RETROLUME_TASK097_OUT"])/"prior-fixture-cleanup.json",{"origin":"integration-01-pg三次setUp中断",
        "source_ids":[r["source_id"] for r in orphans],"fixed_content_sha256":hashlib.sha256(ENGLISH.encode()).hexdigest()})
    fixture.sources=[r["source_id"] for r in orphans];fixture.cleanup()
suite=unittest.defaultTestLoader.loadTestsFromNames(["tests.test_learning_pg","tests.test_learning_api"])
result=unittest.TextTestRunner(verbosity=2).run(suite)
write(Path(os.environ["RETROLUME_TASK097_OUT"])/"pg-summary.json",{"tests":result.testsRun,"skipped":result.skipped,
    "failures":len(result.failures),"errors":len(result.errors),"modules":imported_modules()})
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
