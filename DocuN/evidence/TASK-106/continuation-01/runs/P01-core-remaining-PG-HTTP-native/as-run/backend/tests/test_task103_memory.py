"""G9命令、配置和精度的真实纯函数边界，不证明PG事务。"""
import unittest
from uuid import uuid4
from pydantic import ValidationError
from app.memory.contracts import MemoryCommandInput,MemorySelectionInput,MemoryContextConfig,dependencies_digest,order_dependencies
from app.learning.contracts import canonical,sha
from app.learning.teaching_contracts import TeachingCommandInput,TeachingFrozenContext,frozen_context_digest
from app.learning.teaching_policy import derive_support_checks


def memory_command(action="save",body=None,key=None,revision=0):
    return MemoryCommandInput(business_key=key or str(uuid4()),memory_id="11111111-1111-4111-8111-111111111111",
        expected_revision=revision,action=action,body=body or {"kind":"self_report","title":"个人笔记","text":"我仍需练习单位换算"})


class MemoryContractTests(unittest.TestCase):
    def test_key_is_not_content_and_revision_is_not_permission(self):
        a=memory_command();b=memory_command(key=str(uuid4()))
        self.assertEqual(a.request_sha(),b.request_sha())
        self.assertNotEqual(a.business_key,b.business_key)
        self.assertEqual(a.slot(),b.slot())

    def test_unknown_authority_and_noncanonical_uuid_are_rejected(self):
        data=memory_command().model_dump(by_alias=True)
        for field,value in (("allowed_tools",["shell"]),("path","D:/private"),("mastered",True)):
            bad={**data,field:value}
            with self.subTest(field=field),self.assertRaises(ValidationError):MemoryCommandInput.model_validate(bad)
        data["business_key"]="11111111-1111-4111-8111-11111111111A"
        with self.assertRaises(ValidationError):MemoryCommandInput.model_validate(data)

    def test_confirmation_is_real_boolean(self):
        for value in (1,"true",False,None):
            with self.subTest(value=value),self.assertRaises(ValidationError):
                MemorySelectionInput(confirmed=value,entries=[{"memory_id":str(uuid4()),"version":1,"revision":1,"body_sha256":"a"*64}])

    def test_source_dependencies_are_deterministic_and_not_dropped(self):
        dep={"dependency_kind":"source","source_id":str(uuid4()),"source_version_id":str(uuid4()),
             "source_revision":1,"original_sha256":"a"*64}
        ordered=order_dependencies([dep,dict(dep)])
        self.assertEqual(len(ordered),1)
        self.assertEqual(dependencies_digest(ordered),sha("source|"+dep["source_id"]+"|"+dep["source_version_id"]+"|1|"+"a"*64))
        from app.memory.contracts import MemoryRefusal
        many=[{**dep,"source_id":str(uuid4())} for _ in range(11)]
        with self.assertRaises(MemoryRefusal):order_dependencies(many)

    def test_body_and_capture_kind_do_not_upgrade_self_report(self):
        with self.assertRaises(ValidationError):
            memory_command(body={"kind":"learning_observation","title":"已掌握","text":"无事实"})
        with self.assertRaises(ValidationError):
            memory_command(body={"kind":"self_report","title":"笔记","text":"x\0"})

    def test_capacity_needs_explicit_identity_and_reserves(self):
        values={"selected_items":4,"max_memory_bytes":4096,"max_memory_chars":2048,
          "model_context_tokens":32768,"max_input_tokens_estimate":24576,"protocol_reserve_tokens":1024,
          "reserved_output_tokens":2048,"safety_tokens":2048,"estimate_policy":"utf8_bytes.v1",
          "model_identity":{"provider":"deepseek_chat_completions","model":"synthetic"}}
        MemoryContextConfig.model_validate(values)
        with self.assertRaises(ValidationError):MemoryContextConfig.model_validate({**values,"max_input_tokens_estimate":32768})

    def test_legacy_command_and_tool_frozen_bytes_have_no_memory_fields(self):
        command=TeachingCommandInput(business_key=str(uuid4()),expected_revision=0,expected_goal_version=0,
          expected_scope_revision=1,action="goal",body={"goal":"平均速度","self_report":None,"domain":None,
          "seed_operation_id":None,"seed_payload_sha256":None})
        expected={"activity_id":"11111111-1111-4111-8111-111111111111","action":"goal","expected_revision":0,
          "expected_goal_version":0,"expected_scope_revision":1,"body":command.body}
        self.assertEqual(command.canonical_request_body(expected["activity_id"]),expected)
        frozen=TeachingFrozenContext(kind="tool",reference_hashes=[],operation_id="teach8t.sample",
          context_sha256="0"*64,call={"call_id":"c1","name":"finite_calculate","arguments_json":"{}","arguments_sha256":"a"*64})
        value=frozen.model_dump(by_alias=True)
        self.assertEqual(set(value),{"schema","kind","reference_hashes","operation_id","context_sha256",
          "profile_version","prompt_version","max_output_tokens","messages","catalog","call"})
        self.assertEqual(frozen_context_digest(frozen),sha(canonical({k:v for k,v in value.items() if k!="context_sha256"})))


class PrecisionTests(unittest.TestCase):
    def exercise(self):
        return {"exercise_type":"calculation","reference_points":[{"point_id":"p1","numeric":{"operation":"divide",
          "left":"120","right":"120","value_decimal":"1","unit":"m/s","tolerance_decimal":None}}],
          "dimensions":[{"id":"value","point_ids":["p1"]}]}

    def test_same_unit_retains_exact_decimal_difference(self):
        for answer,status in (("1m/s","matched"),("1."+"0"*64+"1m/s","conflict")):
            with self.subTest(answer=answer):
                result=derive_support_checks(self.exercise(),answer)[0]
                self.assertEqual(result["reference_status"],"matched")
                self.assertEqual(result["answer_status"],status)

    def test_cross_unit_exact_ratio_and_support_limit(self):
        self.assertEqual(derive_support_checks(self.exercise(),"60m/min")[0]["answer_status"],"matched")
        answer="60."+"0"*256+"1m/min"
        self.assertEqual(derive_support_checks(self.exercise(),answer)[0]["answer_status"],"unchecked")

    def test_negated_and_uncertain_answers_remain_unknown(self):
        for answer in ("平均速度不等于1m/s","答案未知，可能1m/s"):
            with self.subTest(answer=answer):
                self.assertEqual(derive_support_checks(self.exercise(),answer)[0]["answer_status"],"unchecked")

