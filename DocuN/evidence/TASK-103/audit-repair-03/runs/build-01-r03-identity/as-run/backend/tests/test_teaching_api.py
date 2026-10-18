"""TASK-100 教学读取、零费命令和引用封套的定向验证。

离线投影及引用路由替身不证明数据库事务。真实 HttpTests 仅由有限
main-combo 注入本地应用、专库和会话；未注入时明确 skip。
"""
import json
import os
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

from app.learning.teaching_api import _deadline_passed, _workspace_payload
from app.learning.teaching_contracts import TeachingCommandInput
from app.learning.teaching_policy import project_public_exercise


def _fake_view(*,source_valid=True,exercise_result=None,feedback_result=None):
    from uuid import uuid4
    from dataclasses import replace
    from app.learning.contracts import canonical,sha,CatalogEntry
    from app.capabilities.contracts import build_business_payload
    from app.retrieval.evidence import EvidenceFragment,_evidence_id
    from tests.fixtures.task100.synthetic_content import exercise
    aid,sid,vid,gid,eid,answerid,key=map(str,[uuid4() for _ in range(7)])
    text='平均速度先统一分钟和秒。'
    frag=EvidenceFragment('ev_'+'0'*64,sid,vid,1,None,'original',1,1,0,len(text),sha(text),text)
    frag=replace(frag,evidence_id=_evidence_id(frag))
    request_sha='a'*64;citation='lc_'+sha(request_sha+frag.evidence_id)[:24]
    entry=CatalogEntry(source_id=sid,version_id=vid,source_revision=1,citation_id=citation,evidence_id=frag.evidence_id,
        title='speed.md',format='md',original_sha256=sha(text),unit_sha256=sha(text),fragment_sha256=sha(text),start_line=1,end_line=1,start_offset=0,end_offset=len(text),origin_kind='original',text=text)
    result=exercise({'node_id':'n1','purpose':'initial','parent_exercise_record_id':None,'parent_feedback_record_id':None},citation)
    value={'activity_id':aid,'command_key':key,'goal_version':1,'scope_revision':1,'request_sha256':request_sha,'catalog':[entry.model_dump()],'result':result}
    fmt,payload,digest=build_business_payload(json_object=value)
    body=canonical({'goal':'换算平均速度','self_report':None,'domain':None})
    ans=canonical({'exercise_record_id':eid,'kind':'initial','text':'我的作答','supersedes_answer_record_id':None,'exposures_seen':[]})
    def local(rid,kind,raw,seq):
        return {'activity_id':aid,'record_id':rid,'kind':kind,'seq':seq,'goal_version':1,'scope_revision':1,'command_key':key,
            'parent_record_id':None,'exercise_record_id':eid if kind=='answer' else None,'answer_record_id':None,
            'body':raw,'body_sha256':sha(raw),'created_at':'2026-10-04T00:00:00+00:00','payload':None}
    exposure=canonical({'exercise_record_id':eid,'part':'hint'})
    return {'activity':{'id':aid,'status':'pending','scope_revision':1,'deadline_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),
        'requests_reserved':0,'max_requests':10,'cost_reserved_microunits':0,'max_cost_microunits':100,'tools_reserved':0,'max_tool_calls':2,
        'running_settled_seconds':0,'running_reserved_seconds':0,'max_running_seconds':900},
        'head':{'revision':5,'last_seq':8,'goal_version':1,'phase':'answer_saved','goal_record_id':gid,'path_record_id':None,'node_id':None,
            'exercise_record_id':eid,'answer_record_id':answerid,'feedback_record_id':None,'reason_record_id':None,'pending_business_key':None,'projection':'{}'},
        'pending':[{'business_key':key,'action':'evaluate','status':'committed','error_code':None,'created_at':'2026-10-04T00:00:00+00:00'}],
        'history':[],'sources':[{'source_id':sid,'version_id':vid,'source_revision':1,'valid':source_valid,'ready':True,'title':'speed.md','format':'md'}],
        'current_bodies':[local(gid,'goal',body,1),{'activity_id':aid,'record_id':eid,'kind':'exercise','seq':4,'goal_version':1,'scope_revision':1,'command_key':key,
            'exercise_record_id':None,'answer_record_id':None,'body':None,'body_sha256':digest,'payload':payload,'payload_format':fmt,'operation_payload_sha256':digest},local(answerid,'answer',ans,5)],
        'exposures':[{'exercise_record_id':eid,'parent_record_id':None,'command_key':key,'body':exposure,'body_sha256':sha(exposure)}],
        'pending_business_key':None}

EXERCISE_RESULT={}


class WorkspaceProjectionOfflineTests(unittest.TestCase):
    """离线：workspace 投影纪律（DEF-005 反例）。"""

    def test_view_token_is_real_hash_without_na_placeholder(self):
        view = _fake_view()
        payload = _workspace_payload("act-1", view)
        self.assertRegex(payload["view_token"], r"^[0-9a-f]{64}$")

    def test_view_token_changes_with_source_and_pending_state(self):
        view=_fake_view();base=_workspace_payload('act-1',view)
        view['sources'][0]['valid']=False
        changed_source=_workspace_payload('act-1',view)
        self.assertNotEqual(base["view_token"], changed_source["view_token"])

    def test_source_invalid_is_computed_not_hardcoded(self):
        valid = _workspace_payload("act-1", _fake_view(source_valid=True))
        invalid = _workspace_payload("act-1", _fake_view(source_valid=False))
        self.assertFalse(valid["overlay"]["source_invalid"])
        self.assertTrue(invalid["overlay"]["source_invalid"])

    def test_unexposed_reference_is_never_returned(self):
        view = _fake_view(exercise_result=EXERCISE_RESULT)
        payload = _workspace_payload("act-1", view)
        exercise = payload["exercise"]
        self.assertTrue(exercise["reference_available"] is False
                        or "reference" not in exercise
                        or exercise.get("reference_available") is False)
        self.assertNotIn("reference_points", exercise)
        self.assertNotIn("reference_explanation", exercise)
        # 已暴露 hint 可返回。
        self.assertIn('先写依据',exercise.get('hint',''))

    def test_exposed_reference_is_projected(self):
        view = _fake_view(exercise_result=EXERCISE_RESULT)
        from app.learning.contracts import canonical,sha
        ex=view['head']['exercise_record_id'];body=canonical({'exercise_record_id':ex,'part':'reference'})
        view['exposures'].append({'exercise_record_id':ex,'parent_record_id':None,'command_key':'k','body':body,'body_sha256':sha(body)})
        payload = _workspace_payload("act-1", view)
        exercise = payload["exercise"]
        self.assertEqual(exercise['reference_points'][0]['numeric']['value_decimal'],'1')
        self.assertEqual(len(exercise['reference_points']),4)
        self.assertTrue(exercise['reference_available'])
        self.assertTrue(exercise['reference_explanation'])

    def test_source_invalid_suppresses_derived_but_keeps_user_text(self):
        view = _fake_view(exercise_result=EXERCISE_RESULT, source_valid=False)
        payload = _workspace_payload("act-1", view)
        # 派生正文（exercise）被抑制。
        self.assertEqual(payload["exercise"]["qualification"], "source_invalid")
        # 用户文字（goal/answer）保留。
        self.assertEqual(payload["goal"]["goal"], "换算平均速度")
        self.assertEqual(payload["answer"]["text"], "我的作答")

    def test_broken_single_item_is_locally_suppressed(self):
        view = _fake_view(exercise_result=EXERCISE_RESULT)
        view["current_bodies"][1]["payload"] = "{not-json"
        payload = _workspace_payload("act-1", view)
        self.assertEqual(payload["exercise"]["qualification"], "integrity_error")
        # 其他区域不受影响。
        self.assertEqual(payload["goal"]["goal"], "换算平均速度")
        self.assertEqual(payload["answer"]["text"], "我的作答")

    def test_expired_deadline_overlay(self):
        view = _fake_view()
        view["activity"]["deadline_at"] = (
            datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        payload = _workspace_payload("act-1", view)
        self.assertTrue(payload["overlay"]["expired"])
        self.assertFalse(_deadline_passed(
            (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()))

    def test_citation_route_returns_bound_catalog_envelope_without_database(self):
        """复现 HTTP 夹具误读顶层 text；路由仍核真实原件位置与 hash。"""
        import asyncio
        import io
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import AsyncMock,patch
        from app.learning import teaching_api
        from app.learning.contracts import canonical,sha,CatalogEntry
        from app.storage.originals import OriginalStore
        view=_fake_view();row=dict(view['current_bodies'][1])
        catalog=json.loads(row['payload'])['value']['catalog'][0]
        text=catalog['text'];raw=text.encode('utf-8')
        view['sources'][0].update(sha256=sha(text),size=len(raw))
        exposed=canonical({'exercise_record_id':row['record_id'],'part':'reference'})
        view['exposures'].append({'exercise_record_id':row['record_id'],'parent_record_id':None,
            'command_key':row['command_key'],'body':exposed,'body_sha256':sha(exposed)})
        row.update(snapshot_sources=view['sources'],snapshot_exposures=view['exposures'],
            snapshot_head=view['head'],snapshot_activity=view['activity'],snapshot_read_at='2026-10-04T00:00:00+00:00')
        with tempfile.TemporaryDirectory(prefix='task100-citation-contract-') as directory:
            originals=OriginalStore(Path(directory));originals.put(io.BytesIO(raw),max_bytes=5242880)
            service=SimpleNamespace(read_record=AsyncMock(return_value=row),materials=None,originals=originals)
            with patch.object(teaching_api,'_guard'),patch.object(teaching_api,'_service',return_value=service):
                response=asyncio.run(teaching_api.read_teaching_citation(None,view['activity']['id'],row['record_id'],catalog['citation_id']))
        payload=json.loads(response.body)
        self.assertEqual(set(payload),{'citation','read_at'})
        bound=CatalogEntry.model_validate(payload['citation'])
        self.assertEqual(bound.text,text);self.assertEqual(bound.fragment_sha256,sha(text))
        self.assertEqual(bound.end_offset-bound.start_offset,len(text))


class DtoOfflineTests(unittest.TestCase):
    """离线：命令 DTO 封闭性。"""

    def test_command_rejects_unknown_action(self):
        from pydantic import ValidationError
        from uuid import uuid4
        with self.assertRaises((ValidationError, ValueError)):
            TeachingCommandInput.model_validate({
                "business_key": str(uuid4()), "expected_revision": 0,
                "expected_goal_version": 0, "expected_scope_revision": 1,
                "action": "not_a_real_action", "body": {},
            }, strict=True)


class HttpTests(unittest.TestCase):
    """真实 HTTP：沿实际路由打真实应用（http-combo 场景专用）。"""

    def setUp(self):
        self.base = os.environ.get("RETROLUME_TEACHING_HTTP_BASE", "")
        if not self.base:
            self.skipTest("RETROLUME_TEACHING_HTTP_BASE 未注入（离线模式不跑真实 HTTP）")
        # 本地会话：应用启动 token 随机，教学端点挂 local_session 全量校验；
        # 先经免 token 的 /api/session（仅 local_request）取得本次会话 token。
        with urllib.request.urlopen(self.base + "/api/session", timeout=15) as response:
            self.token = json.loads(response.read().decode("utf-8"))["token"]

    def _get(self, path):
        request = urllib.request.Request(
            self.base + path, headers={"X-RetroLume-Session": self.token})
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def _post(self, path, body):
        request = urllib.request.Request(
            self.base + path, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "X-RetroLume-Session": self.token}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8") or "{}")

    def test_workspace_endpoint_returns_contract_schema(self):
        status, payload = self._get("/api/activities")
        self.assertEqual(status, 200)
        # 活动列表端点可达即证明应用与 DB 链真实；教学 workspace 对未知活动 404。
        unknown = str(__import__("uuid").uuid4())
        try:
            status, _ = self._get(f"/api/activities/{unknown}/teaching/workspace")
            self.fail(f"未知活动应 404，实际 {status}")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)

    def test_command_endpoint_rejects_invalid_dto(self):
        from uuid import uuid4
        status, payload = self._post("/api/activities/" + str(uuid4()) + "/teaching/commands",
                                     {"nonsense": True})
        self.assertIn(status, (400, 404, 422))
        self.assertIn("detail", payload)

    def _fixture(self):
        from pathlib import Path
        from tests.fixtures.task100.support import Fixture,DSN
        return Fixture(DSN,Path(os.environ['RETROLUME_TASK100_ORIGINALS_DIR']))

    def _run(self,coro):
        import asyncio
        from app.runtime import psycopg_compatible_loop_factory
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(coro)

    def test_real_zero_fee_replay_command_receipt_and_cursor(self):
        from uuid import uuid4
        from tests.fixtures.task100.seed_helpers import command
        from tests.fixtures.task100.synthetic_content import MATERIAL,GOAL
        fixture=self._fixture();source=fixture.text(MATERIAL,'task100-http-'+uuid4().hex[:8]+'.md');aid=str(uuid4())
        self.assertEqual(self._post('/api/activities',{'activity_id':aid,'source_ids':[source['id']]})[0],200)
        endpoint=f'/api/activities/{aid}/teaching'
        _,view=self._get(endpoint+'/workspace');self.assertEqual(view['head']['phase'],'needs_goal')
        self.assertIsNone(fixture.head(aid))
        body={'goal':GOAL,'self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None}
        cmd=command(None,'goal',body);wire=cmd.model_dump(mode='json')
        status,receipt=self._post(endpoint+'/commands',wire);self.assertEqual(status,200);self.assertEqual(receipt['status'],'committed')
        self.assertEqual(self._post(endpoint+'/commands',wire)[1]['record_ids'],receipt['record_ids'])
        second=command(None,'goal',body)
        self.assertEqual(self._post(endpoint+'/commands',second.model_dump(mode='json'))[1]['duplicate_of'],cmd.business_key)
        _,read=self._get(endpoint+'/commands/'+cmd.business_key)
        self.assertEqual(read['record_ids'],receipt['record_ids']);self.assertEqual(read['applied_revision'],receipt['applied_revision'])
        _,history=self._get(endpoint+'/history?limit=1');self.assertTrue(history['next_cursor'])
        changed=command(fixture.head(aid),'goal',body|{'goal':'新目标：区分原子性与隔离性'})
        self.assertEqual(self._post(endpoint+'/commands',changed.model_dump(mode='json'))[0],200)
        with self.assertRaises(urllib.error.HTTPError) as stale:self._get(endpoint+'/history?limit=1&cursor='+history['next_cursor'])
        self.assertEqual(stale.exception.code,409)
        wire['body']['goal']='同键不同内容'
        self.assertEqual(self._post(endpoint+'/commands',wire)[0],409)
        counts=fixture.rows('SELECT requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds FROM activities WHERE id=%s',(aid,))[0]
        self.assertTrue(all(n==0 for n in counts.values()));self.assertEqual(len(fixture.records(aid)),2)

    def test_real_exposure_records_citations_and_answer_offsets(self):
        from tests.fixtures.task100.seed_helpers import ready_answer,command
        from app.learning.contracts import sha
        fixture=self._fixture();aid,_,eid,answer=self._run(ready_answer(fixture));endpoint=f'/api/activities/{aid}/teaching'
        before=fixture.records(aid)
        _,record=self._get(endpoint+'/records/'+eid);self.assertNotIn('reference_points',record['public_body'])
        self.assertEqual(fixture.records(aid),before)
        cmd=command(fixture.head(aid),'expose',{'exercise_record_id':eid,'part':'reference'})
        status,receipt=self._post(endpoint+'/commands',cmd.model_dump(mode='json'));self.assertEqual(status,200)
        self.assertTrue(receipt['exposed_part']['reference_points'])
        _,record=self._get(endpoint+'/records/'+eid);self.assertEqual(record['public_body']['reference_points'][0]['numeric']['value_decimal'],'1')
        citation=record['public_body']['reference_points'][0]['citations'][0]
        _,cited=self._get(endpoint+f'/records/{eid}/citations/{citation}')
        from app.learning.contracts import CatalogEntry
        cited_entry=CatalogEntry.model_validate(cited['citation'])
        self.assertEqual(cited_entry.citation_id,citation);self.assertTrue(cited_entry.text)
        self.assertEqual(cited_entry.fragment_sha256,sha(cited_entry.text))
        self.assertEqual(cited_entry.end_offset-cited_entry.start_offset,len(cited_entry.text))
        row=fixture.rows('SELECT body_sha256 FROM teaching_records WHERE activity_id=%s AND record_id=%s',(aid,answer))[0]
        ref='ar_'+sha(answer+row['body_sha256'])[:24]
        _,saved=self._get(endpoint+f'/answers/{answer}/references/{ref}')
        self.assertEqual(saved['text'],'120÷2=60m/s');self.assertEqual(saved['sha256'],sha(saved['text']))
        request=urllib.request.Request(self.base+endpoint+'/workspace')
        with self.assertRaises(urllib.error.HTTPError) as guard:urllib.request.urlopen(request,timeout=5)
        self.assertEqual(guard.exception.code,403)
        with urllib.request.urlopen(urllib.request.Request(self.base+endpoint+'/workspace',headers={'X-RetroLume-Session':self.token}),timeout=5) as response:
            self.assertEqual(response.headers.get('Cache-Control'),'no-store')
