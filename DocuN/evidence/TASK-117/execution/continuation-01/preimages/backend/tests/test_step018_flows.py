"""新增profile不改旧规范字节，不能缺检索引用或把本地动作送模型。"""
import json
import unittest
from uuid import uuid4
from app.interview.contracts import InterviewCommandInput,parse_command
from app.learning.teaching_contracts import TeachingCommandInput
from app.capabilities.embedding import OutboundGrant
from app.retrieval.service import IntegrationConfig
from app.capabilities.transport import HttpxModelTransport
from app.data_exit.schema_profiles import normalized_extra_shape

class IntegrationContractTests(unittest.TestCase):
    def test_legacy_command_bytes_and_new_local_profile(self):
        aid,key=str(uuid4()),str(uuid4())
        body=dict(schema='interview.command.v1',business_key=key,action='start',expected_head_revision=0,expected_goal_version=0,expected_scope_revision=1,body={'goal':None})
        old=InterviewCommandInput.model_validate(body)
        expected={k:v for k,v in old.model_dump().items() if k!='business_key'};expected['activity_id']=aid
        self.assertEqual(json.loads(old.request_body(aid)),expected)
        new=parse_command({**body,'schema':'interview.command.v2','retrieval_ref':None})
        self.assertNotEqual(new.request_hash(aid),old.request_hash(aid))
        self.assertIsNone(new.retrieval_ref)

    def test_hybrid_model_without_retrieval_rejected(self):
        with self.assertRaises(ValueError):
            parse_command(dict(schema='interview.command.v2',business_key=str(uuid4()),action='ask',expected_head_revision=1,expected_goal_version=1,expected_scope_revision=1,body={'confirmed':True}))

    def test_legacy_teaching_canonical_has_no_new_null(self):
        command=TeachingCommandInput(business_key=str(uuid4()),expected_revision=0,expected_goal_version=0,expected_scope_revision=1,action='goal',body={'goal':'有限合成目标'})
        self.assertNotIn('retrieval_ref',command.canonical_request_body(str(uuid4())))

    def test_only_verified_bootstrap_owner_name_is_normalized(self):
        def shape(owner,superuser):return {'columns':[{'relname':'activities','attname':'outbound_grant_sha256','owner':owner,'owner_super':superuser,'acl':None}]}
        self.assertEqual(normalized_extra_shape(shape('source_admin',True)),normalized_extra_shape(shape('restore_admin',True)))
        self.assertNotEqual(normalized_extra_shape(shape('attacker',False)),normalized_extra_shape(shape('source_admin',True)))

if __name__=='__main__':unittest.main()
