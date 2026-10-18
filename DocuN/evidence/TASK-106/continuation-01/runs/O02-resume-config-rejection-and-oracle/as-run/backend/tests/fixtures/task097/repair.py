"""仅修复第二批HTTP夹具明确漏记的合成FK身份，不清理未知数据。"""
import hashlib
import json
from tests.fixtures.task097.support import Fixture
from tests.fixtures.task097.samples import ENGLISH


def prior_fixture(fixture:Fixture,out):
    source="4cff4ff5-9021-47ce-ace0-0dc4e809f413"
    version="1f77b594-911f-4594-bf9c-bfb7b7e569fe"
    rows=fixture.rows("SELECT v.id::text AS version,v.filename,v.sha256 FROM material_sources s "
        "JOIN material_versions v ON v.source_id=s.id WHERE s.id=%s",(source,))
    if not rows:return
    if rows!=[{"version":version,"filename":"atomicity.md","sha256":hashlib.sha256(ENGLISH.encode()).hexdigest()}]:
        raise ValueError("第二批夹具遗留身份不匹配，拒绝清理")
    activities=fixture.rows("SELECT activity_id::text AS id FROM activity_scope_sources WHERE source_id=%s",(source,))
    if len(activities)!=1:raise ValueError("第二批夹具遗留范围数量不匹配")
    activity=activities[0]["id"]
    operations=fixture.rows("SELECT count(*) AS n FROM activity_operations WHERE activity_id=%s",(activity,))[0]["n"]
    if operations!=0:raise ValueError("遗留零费活动出现业务操作，拒绝清理")
    fact={"origin":"integration-02-pg HTTP200断言前遗漏注册的新建活动", "source_id":source,"version_id":version,
        "activity_id":activity,"operations":operations,"source_sha256":rows[0]["sha256"]}
    (out/"prior-fk-repair.json").write_text(json.dumps(fact,indent=2),encoding="utf-8")
    own=Fixture(fixture.dsn,fixture.root);own.sources=[source];own.activities=[activity];own.cleanup()
