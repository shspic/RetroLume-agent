"""确定样本的合同及独立手工 oracle 对照；不签真实模型生成质量。"""
import copy
import unittest
from tests.fixtures.task100.synthetic_content import path,exercise,feedback
from app.learning.teaching_contracts import parse_teaching_output
from app.learning.contracts import canonical

CITATION='lc_'+'a'*24

class ContentOracleTests(unittest.TestCase):
    def task(self,node,purpose='initial'):
        return {'node_id':node,'purpose':purpose,'parent_exercise_record_id':None,'parent_feedback_record_id':None}
    def test_three_types_strict_output_and_manual_reference(self):
        parse_teaching_output(canonical(path(CITATION)),'plan')
        expected={'n1':('calculation','1 m/s'),'n2':('concept','A100/B50'),'n3':('program','2')}
        for node,(kind,point) in expected.items():
            value=exercise(self.task(node),CITATION);parse_teaching_output(canonical(value),'exercise')
            self.assertEqual(value['exercise_type'],kind);self.assertIn(point,value['reference_points'][0]['text'])
        self.assertIn('0>0 为假',exercise(self.task('n3'),CITATION)['reference_points'][1]['text'])
    def test_unit_negation_logic_contrasts_have_explicit_oracle(self):
        pairs=[('n1','60m/min=1m/s，先乘60秒，单位m/s，数量级1','120÷2=60m/s'),
            ('n2','A100/B50，全部成功或全部不生效，原子性不能单独保证隔离，资料未给级别','原子性能够单独保证隔离'),
            ('n3','返回2，逐次0/0/1/2，0不满足，return在循环后','返回2，0也满足value>0并被计数')]
        for node,correct,wrong in pairs:
            ex=exercise(self.task(node),CITATION)
            for answer,has_error in ((correct,False),(wrong,True)):
                result=feedback({'exercise':ex,'answer_text':answer},CITATION)
                parse_teaching_output(canonical(result),'evaluate')
                self.assertEqual(bool(result['errors']),has_error)
                self.assertTrue(result['correct_parts'])
                self.assertNotIn('mastered',canonical(result));self.assertNotIn('passed',result)
    def test_new_retest_changes_instance_and_preserves_parent(self):
        from uuid import uuid4
        task=self.task('n1','retest');task.update(parent_exercise_record_id=str(uuid4()),parent_feedback_record_id=str(uuid4()))
        e2=exercise(task,CITATION);parse_teaching_output(canonical(e2),'exercise')
        task['parent_feedback']={'message':'180 米'}
        e3=exercise(task,CITATION);parse_teaching_output(canonical(e3),'exercise')
        self.assertNotEqual(e2['variant']['instance_data'],e3['variant']['instance_data'])
        self.assertEqual(e2['variant']['parent_feedback_record_id'],task['parent_feedback_record_id'])

    def test_actual_message_objects_build_trusted_result_and_reject_foreign_citation(self):
        import json
        from uuid import uuid4
        from tests.test_teaching_api import _fake_view
        from app.learning.teaching_contracts import TeachingProfile,stored_teaching_result
        from app.learning.contracts import CatalogEntry,SourceIdentity
        from app.capabilities.contracts import Message
        view=_fake_view();value=json.loads(view['current_bodies'][1]['payload'])['value'];entry=CatalogEntry.model_validate(value['catalog'][0])
        profile=TeachingProfile(action='plan',activity_id=view['activity']['id'],command_key=str(uuid4()),request_sha256='a'*64,context_sha256='b'*64,
            expected_revision=5,goal_record_id=view['head']['goal_record_id'],goal_version=1,path_record_id=None,node_id=None,
            exercise_record_id=None,answer_record_id=None,correction_record_id=None,scope_revision=1,
            sources=[SourceIdentity(source_id=entry.source_id,version_id=entry.version_id,source_revision=1)],catalog=[entry],messages_sha256='c'*64,max_output_tokens=2048)
        messages=[Message(role='user',content=json.dumps({'task':{'kind':'plan'}}))]
        result=path(entry.citation_id);saved=stored_teaching_result(profile,result,messages)
        self.assertEqual(saved['goal_record_id'],view['head']['goal_record_id']);self.assertEqual(saved['catalog'][0]['citation_id'],entry.citation_id)
        result['nodes'][0]['citations']=[CITATION]
        with self.assertRaises(ValueError):stored_teaching_result(profile,result,messages)
