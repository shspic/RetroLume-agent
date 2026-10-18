"""续作01当前严格确认、有限数值和公开/内部隔离；仅离线定向。"""
import unittest
from uuid import uuid4
from app.learning.api import FirstInput,FollowupInput
from app.learning.contracts import normalize_input,LearningProfile,SourceIdentity,request_fingerprint,read_document,normalize_result
from tests.test_learning_config import LearningConfigTests,config
from tests.fixtures.task097.samples import profile,answer

class ContinuationContractTests(unittest.TestCase):
    def test_confirmed_strict_and_public_authority_closed(self):
        base={'business_key':str(uuid4()),'goal':'atomicity','confirmed':True}
        self.assertTrue(FirstInput(**base).confirmed)
        for v in [1,0,'true',False,None]:
            with self.assertRaises(ValueError):FirstInput(**(base|{'confirmed':v}))
        for key in ['learning_profile','system','scope_revision','source_revision','ready','budget','base_url']:
            with self.assertRaises(ValueError):FirstInput(**(base|{key:'synthetic forbidden'}))
        f={'business_key':str(uuid4()),'parent_operation_id':'learn-first-v1.'+'a'*64,'question':'atomicity','confirmed':True}
        self.assertTrue(FollowupInput(**f).confirmed)
        with self.assertRaises(ValueError):FollowupInput(**(f|{'confirmed':1}))
    def test_input_utf8_exact_upper_and_overflow(self):
        for text in ['a','a'*1024,'𠀀'*1024]:self.assertEqual(normalize_input(text),text)
        for text in ['', 'a'*1025, '𠀀'*1025]:
            with self.assertRaises(ValueError):normalize_input(text)
    def test_learning_output_explicit_bounds_and_old_layers(self):
        helper=LearningConfigTests()
        for tokens in [1,256]:
            v=config();v['learning']['max_output_tokens']=tokens
            c=helper.load(v);self.assertTrue(c.learning_layer.available);self.assertEqual(c.learning_output_tokens,tokens)
        for tokens in [0,257,True]:
            v=config();v['learning']['max_output_tokens']=tokens
            c=helper.load(v);self.assertFalse(c.learning_layer.available);self.assertTrue(c.create_layer.available);self.assertTrue(c.continue_layer.available)
    def test_source_revision_domain_and_profile_public_private(self):
        p=profile();s=p.sources[0].model_dump()
        for rev in [0,2147483647]:self.assertEqual(SourceIdentity(**(s|{'source_revision':rev})).source_revision,rev)
        for rev in [-1,2147483648,True]:
            with self.assertRaises(ValueError):SourceIdentity(**(s|{'source_revision':rev}))
        data=p.model_dump()
        for change in [{'profile':'learning.v2'},{'retrieval_mode':'vector'},{'max_output_tokens':257},{'verified':True}]:
            with self.assertRaises(ValueError):LearningProfile(**(data|change))
        stored=normalize_result(p,answer(p));self.assertNotIn('parent_payload_sha256',stored);self.assertNotIn('history',stored)
        with self.assertRaises(ValueError):read_document(stored|{'history':'unsafe expansion'})
