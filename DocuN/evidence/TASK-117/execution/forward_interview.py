"""从锁定011/013精确函数原文形成014前向增量；不写旧迁移。"""
from pathlib import Path
import re
from control import ROOT,event,guard

guard()
old11=(ROOT/'backend/migrations/011_text_interview.sql').read_text(encoding='utf-8')
old13=(ROOT/'backend/migrations/013_data_exit.sql').read_text(encoding='utf-8')
target=ROOT/'backend/migrations/014_step018_retrieval.sql'
body=target.read_text(encoding='utf-8')
if '-- STEP018面试v2前向合同' in body:raise RuntimeError('前向增量已存在，不能重复拼接')

def function(source,name):
    pattern=r'CREATE(?: OR REPLACE)? FUNCTION public\.'+name+r'\([^;]+?\$body\$(.*?)\$body\$;'
    match=re.search(pattern,source,re.S)
    if match is None:raise RuntimeError('精确旧函数未找到：'+name)
    return match.group(0).replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)

def one(text,old,new):
    if text.count(old)!=1:raise RuntimeError('前向替换计数不为1：'+old[:60])
    return text.replace(old,new,1)

head=function(old13,'interview_head_guard')
head=one(head,'OR EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=NEW.activity_id)',
  "OR (EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=NEW.activity_id) AND NOT (public.activity_memory_eligible(NEW.activity_id) AND EXISTS(SELECT 1 FROM public.interview_commands s WHERE s.activity_id=NEW.activity_id AND s.action='start' AND s.execution_kind='local' AND s.before_revision=0 AND s.duplicate_of IS NULL AND s.request_body::jsonb->>'schema'='interview.command.v2')))" )
record=function(old13,'interview_record_insert_guard')
record=one(record,"b->>'profile' IS DISTINCT FROM 'interview.v1'",
  "b->>'profile' IS DISTINCT FROM (CASE WHEN c.request_body::jsonb->>'schema'='interview.command.v2' AND c.context_body::jsonb->>'schema'='interview.context.v2' THEN 'interview.v2' ELSE 'interview.v1' END)")
eligible=function(old11,'interview_result_eligible')
eligible=one(eligible,'AND NOT EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=aid)',
  "AND public.activity_memory_eligible(aid) AND (NOT EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=aid) OR EXISTS(SELECT 1 FROM public.interview_commands sc WHERE sc.activity_id=aid AND sc.action='start' AND sc.effect_applied AND sc.duplicate_of IS NULL AND sc.request_body::jsonb->>'schema'='interview.command.v2' AND r.payload::jsonb->'value'->>'profile'='interview.v2'))")
piece='''-- STEP018面试v2前向合同
ALTER TABLE public.interview_commands DROP CONSTRAINT interview_command_execution;
ALTER TABLE public.interview_commands ADD CONSTRAINT interview_command_execution CHECK(
 (duplicate_of IS NOT NULL AND operation_id IS NULL AND context_body IS NULL AND context_sha256 IS NULL AND NOT effect_applied AND NOT launch_claimed)
 OR (duplicate_of IS NULL AND execution_kind='local' AND operation_id IS NULL AND context_body IS NULL AND context_sha256 IS NULL AND NOT launch_claimed)
 OR (duplicate_of IS NULL AND execution_kind='model' AND action IN('ask','review') AND context_body IS NOT NULL AND context_sha256 IS NOT NULL
   AND ((request_body::jsonb->>'schema'='interview.command.v1' AND context_body::jsonb->>'schema'='interview.context.v1' AND operation_id='int10m.'||replace(business_key::text,'-',''))
     OR (request_body::jsonb->>'schema'='interview.command.v2' AND context_body::jsonb->>'schema'='interview.context.v2' AND operation_id='int18m.'||replace(business_key::text,'-','')))));
GRANT SELECT ON public.learning_memories,public.learning_memory_revisions,public.learning_memory_bodies,public.learning_memory_dependencies,
 public.learning_memory_commands,public.activity_memory_choices TO retrolume_interview_owner;
GRANT EXECUTE ON FUNCTION public.memory_revision_readable(uuid,integer),public.memory_revision_eligible(uuid,integer),public.activity_memory_eligible(uuid),
 public.memory_dependency_line(public.learning_memory_dependencies),public.memory_dependency_digest(uuid,integer),public.memory_scope_digest(uuid),public.memory_choice_digest(uuid) TO retrolume_interview_owner;
'''+head+'\n'+record+'\n'+eligible+'''\nREVOKE ALL ON FUNCTION public.interview_head_guard(),public.interview_record_insert_guard(),public.interview_result_eligible(uuid,text) FROM PUBLIC;
'''
body=one(body,'ALTER TABLE public.data_control DROP CONSTRAINT data_control_schema_profile_check;',piece+'\nALTER TABLE public.data_control DROP CONSTRAINT data_control_schema_profile_check;')
target.write_text(body,encoding='utf-8',newline='\n')
event('forward_migration_extended',path='backend/migrations/014_step018_retrieval.sql',old_migrations_written=0,functions=['interview_head_guard','interview_record_insert_guard','interview_result_eligible'])
print('014 added closed interview v2 forward shapes; old migrations untouched')
