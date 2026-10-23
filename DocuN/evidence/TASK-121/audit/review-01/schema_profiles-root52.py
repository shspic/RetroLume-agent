"""封闭数据profile；旧常量不改，R03仅增加015单表权限。"""
from dataclasses import dataclass
from copy import deepcopy
from .contracts import PROFILE,TABLES,DataError,canonical,digest
from .schema import COLUMNS,MIGRATIONS,MIGRATION_013

R02='data_exit.v1.r02'
R03='data_exit.v1.r03'
LEGACY_MIGRATION_015='59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e'
MIGRATION_015='1fbe278e19bd65f55d043159167e108563adcde8dae870a0bcf060b2f9c0a712'
MIGRATION_014='3a919b2562ded5765de132519b841c1d1439c65c001795cfbd608cbc03586e78'
VECTOR_EXTENSION_VERSION='0.8.6'
R02_EXTRA_SHAPE_SHA='5b7dc68a94101307bcbd63a16607c5b2ee79906b5f32669d764853a55172dc12'
FORWARD_FUNCTIONS={'interview_head_guard': '6219aa292d679bff71b2dbdbe54c4757a17bdee5cd3e2a76927d2fa9a7abc134', 'interview_record_insert_guard': 'f7423ecf9109244b5a87db568a552f9a0027b2ad9968281af66af07c56729c90', 'interview_result_eligible': '3a876b12080499d63c36bd7b1fa0d7960dc902f07bcabec99750cdf242342da6'}
ORIGINAL_FUNCTIONS_013={'interview_head_guard': "\nDECLARE a public.activities; ptr uuid; p public.interview_records;\nBEGIN\n IF TG_OP='DELETE' THEN RAISE EXCEPTION 'interview heads retained'; END IF;\n SELECT * INTO a FROM public.activities WHERE id=NEW.activity_id;\n IF TG_OP='INSERT' THEN\n  IF NOT public.data_loading_allowed() AND (a.status<>'pending' OR a.execution_generation<>0 OR a.executor_id IS NOT NULL OR a.lease_expires_at IS NOT NULL\n     OR a.requests_reserved<>0 OR a.cost_reserved_microunits<>0 OR a.tools_reserved<>0 OR a.running_reserved_seconds<>0 OR a.running_settled_seconds<>0\n     OR EXISTS(SELECT 1 FROM public.teaching_heads WHERE activity_id=NEW.activity_id)\n     OR EXISTS(SELECT 1 FROM public.activity_operations WHERE activity_id=NEW.activity_id)\n     OR EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=NEW.activity_id)\n     OR NEW.revision<>1) THEN RAISE EXCEPTION 'interview requires fresh unselected activity'; END IF;\n ELSE\n  IF NEW.activity_id<>OLD.activity_id OR NEW.created_at<>OLD.created_at OR NEW.revision NOT BETWEEN OLD.revision AND OLD.revision+1\n    OR NEW.goal_version NOT BETWEEN OLD.goal_version AND OLD.goal_version+1 OR NEW.last_seq<OLD.last_seq\n    OR (NEW.revision=OLD.revision AND (to_jsonb(NEW)-ARRAY['pending_key','updated_at']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['pending_key','updated_at']))\n    OR (OLD.phase='ended' AND NEW.phase<>'ended') THEN RAISE EXCEPTION 'interview head revision invalid'; END IF;\n END IF;\n IF NEW.scope_revision<>a.scope_revision OR NEW.last_seq<>(SELECT max(seq) FROM public.interview_records WHERE activity_id=NEW.activity_id)\n    THEN RAISE EXCEPTION 'interview head scope/sequence invalid'; END IF;\n FOREACH ptr IN ARRAY ARRAY[NEW.goal_record_id,NEW.root_question_id,NEW.current_question_id,NEW.current_answer_id,NEW.current_feedback_id] LOOP\n  IF ptr IS NOT NULL THEN\n   SELECT * INTO p FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=ptr;\n   IF p.record_id IS NULL OR p.goal_version<>NEW.goal_version OR p.scope_revision<>NEW.scope_revision THEN RAISE EXCEPTION 'interview head pointer invalid'; END IF;\n  END IF;\n END LOOP;\n IF NEW.goal_record_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.goal_record_id AND kind='goal') THEN RAISE EXCEPTION 'goal pointer kind'; END IF;\n IF NEW.current_question_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.current_question_id AND kind IN ('question','probe')) THEN RAISE EXCEPTION 'question pointer kind'; END IF;\n IF NEW.current_answer_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.current_answer_id AND kind='answer' AND question_record_id=NEW.current_question_id) THEN RAISE EXCEPTION 'answer pointer kind'; END IF;\n IF NEW.current_feedback_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.current_feedback_id AND kind='feedback') THEN RAISE EXCEPTION 'feedback pointer kind'; END IF;\n RETURN NEW;\nEND;\n", 'interview_record_insert_guard': "\nDECLARE c public.interview_commands; p public.interview_records; r public.activity_operation_results; o public.activity_operations; b jsonb; ref jsonb;\nBEGIN\n SELECT * INTO c FROM public.interview_commands WHERE activity_id=NEW.activity_id AND business_key=NEW.business_key;\n IF c.activity_id IS NULL OR c.duplicate_of IS NOT NULL OR (NOT public.data_loading_allowed() AND (c.effect_applied OR c.status NOT IN ('accepted','started')))\n    OR NEW.seq<>(SELECT COALESCE(max(seq),0)+1 FROM public.interview_records WHERE activity_id=NEW.activity_id)\n    THEN RAISE EXCEPTION 'interview record command/sequence invalid'; END IF;\n IF cardinality(NEW.parent_ids)<>(SELECT count(DISTINCT x) FROM unnest(NEW.parent_ids) x) THEN RAISE EXCEPTION 'duplicate parents'; END IF;\n FOR p IN SELECT * FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=ANY(NEW.parent_ids) LOOP\n  IF p.seq>=NEW.seq OR p.goal_version<>NEW.goal_version OR p.scope_revision<>NEW.scope_revision THEN RAISE EXCEPTION 'interview parent invalid'; END IF;\n END LOOP;\n IF cardinality(NEW.parent_ids)<>(SELECT count(*) FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=ANY(NEW.parent_ids)) THEN RAISE EXCEPTION 'missing parents'; END IF;\n IF NEW.kind='answer' THEN\n  SELECT * INTO p FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.question_record_id;\n  IF p.kind NOT IN ('question','probe') OR p.goal_version<>NEW.goal_version OR p.scope_revision<>NEW.scope_revision\n     OR NEW.answer_version<>(SELECT COALESCE(max(answer_version),0)+1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND question_record_id=NEW.question_record_id)\n     THEN RAISE EXCEPTION 'answer version invalid'; END IF;\n  IF NEW.answer_version>1 AND NOT EXISTS(SELECT 1 FROM public.interview_records a WHERE a.activity_id=NEW.activity_id AND a.record_id=NEW.supersedes_record_id\n     AND a.question_record_id=NEW.question_record_id AND a.answer_version=NEW.answer_version-1) THEN RAISE EXCEPTION 'supersedes invalid'; END IF;\n END IF;\n IF NEW.origin='model' THEN\n  SELECT * INTO r FROM public.activity_operation_results WHERE activity_id=NEW.activity_id AND operation_id=NEW.operation_id;\n  SELECT * INTO o FROM public.activity_operations WHERE activity_id=NEW.activity_id AND operation_id=NEW.operation_id;\n  b:=r.payload::jsonb->'value';\n  IF c.execution_kind<>'model' OR c.operation_id<>NEW.operation_id OR (NOT public.data_loading_allowed() AND (NOT c.launch_claimed OR c.obsolete OR c.status<>'started'))\n    OR r.payload_format<>'json' OR r.payload_sha256<>NEW.body_sha256 OR o.kind<>'model' OR o.state<>'received'\n    OR r.admission_id<>o.admission_id OR r.execution_generation<>o.execution_generation OR r.scope_revision<>NEW.scope_revision\n    OR b->>'profile' IS DISTINCT FROM 'interview.v1' OR b->>'activity_id' IS DISTINCT FROM NEW.activity_id::text OR b->>'business_key' IS DISTINCT FROM NEW.business_key::text\n    OR b->>'request_sha256' IS DISTINCT FROM c.request_sha256 OR b->>'context_sha256' IS DISTINCT FROM c.context_sha256 OR b->'value'->>'type' IS DISTINCT FROM NEW.kind\n    THEN RAISE EXCEPTION 'interview result binding invalid'; END IF;\n ELSE\n  b:=NEW.local_body::jsonb;\n  IF b->>'schema' IS DISTINCT FROM 'interview.local.v1' OR b->>'activity_id' IS DISTINCT FROM NEW.activity_id::text OR b->>'business_key' IS DISTINCT FROM NEW.business_key::text\n     OR b->>'kind' IS DISTINCT FROM NEW.kind OR (b->>'goal_version')::integer IS DISTINCT FROM NEW.goal_version OR (b->>'scope_revision')::integer IS DISTINCT FROM NEW.scope_revision\n     OR jsonb_typeof(b->'value') IS DISTINCT FROM 'object'\n     THEN RAISE EXCEPTION 'interview local binding invalid'; END IF;\n END IF;\n RETURN NEW;\nEND;\n", 'interview_result_eligible': "\n SELECT EXISTS(SELECT 1 FROM public.interview_commands c JOIN public.interview_heads h USING(activity_id)\n  JOIN public.interview_records ir ON ir.activity_id=c.activity_id AND ir.business_key=c.business_key AND ir.origin='model'\n  JOIN public.activities a ON a.id=c.activity_id\n  JOIN public.activity_operations o ON o.activity_id=c.activity_id AND o.operation_id=c.operation_id\n  JOIN public.activity_operation_results r ON r.activity_id=o.activity_id AND r.operation_id=o.operation_id\n WHERE c.activity_id=aid AND c.operation_id=op AND c.duplicate_of IS NULL AND c.effect_applied AND c.status IN ('committed','history')\n  AND NOT c.obsolete AND c.goal_version=h.goal_version AND c.scope_revision=h.scope_revision AND h.scope_revision=a.scope_revision\n  AND a.status<>'cancelled' AND ir.operation_id=c.operation_id AND ir.payload_sha256=r.payload_sha256 AND ir.body_sha256=r.payload_sha256\n  AND r.admission_id=o.admission_id AND r.execution_generation=o.execution_generation AND r.scope_revision=o.scope_revision AND o.state='received' AND o.kind='model'\n  AND r.payload_format='json'\n  AND NOT EXISTS(SELECT 1 FROM public.activity_scope_sources s LEFT JOIN public.material_sources m ON m.id=s.source_id\n    WHERE s.activity_id=aid AND (m.id IS NULL OR m.current_version IS DISTINCT FROM s.version_id OR m.revision<>s.source_revision))\n  AND EXISTS(SELECT 1 FROM public.activity_scope_sources WHERE activity_id=aid)\n  AND NOT EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=aid))\n"}
ORIGINAL_CONSTRAINTS_013={'interview_command_execution': "CHECK ((((duplicate_of IS NOT NULL) AND (operation_id IS NULL) AND (context_body IS NULL) AND (context_sha256 IS NULL) AND (NOT effect_applied) AND (NOT launch_claimed)) OR ((duplicate_of IS NULL) AND (execution_kind = 'local'::text) AND (operation_id IS NULL) AND (context_body IS NULL) AND (context_sha256 IS NULL) AND (NOT launch_claimed)) OR ((duplicate_of IS NULL) AND (execution_kind = 'model'::text) AND (action = ANY (ARRAY['ask'::text, 'review'::text])) AND (context_body IS NOT NULL) AND (context_sha256 IS NOT NULL) AND (operation_id = ('int10m.'::text || replace((business_key)::text, '-'::text, ''::text))))))"}
FORWARD_CONSTRAINTS_014={'interview_command_execution': "CHECK ((((duplicate_of IS NOT NULL) AND (operation_id IS NULL) AND (context_body IS NULL) AND (context_sha256 IS NULL) AND (NOT effect_applied) AND (NOT launch_claimed)) OR ((duplicate_of IS NULL) AND (execution_kind = 'local'::text) AND (operation_id IS NULL) AND (context_body IS NULL) AND (context_sha256 IS NULL) AND (NOT launch_claimed)) OR ((duplicate_of IS NULL) AND (execution_kind = 'model'::text) AND (action = ANY (ARRAY['ask'::text, 'review'::text])) AND (context_body IS NOT NULL) AND (context_sha256 IS NOT NULL) AND (((((request_body)::jsonb ->> 'schema'::text) = 'interview.command.v1'::text) AND (((context_body)::jsonb ->> 'schema'::text) = 'interview.context.v1'::text) AND (operation_id = ('int10m.'::text || replace((business_key)::text, '-'::text, ''::text)))) OR ((((request_body)::jsonb ->> 'schema'::text) = 'interview.command.v2'::text) AND (((context_body)::jsonb ->> 'schema'::text) = 'interview.context.v2'::text) AND (operation_id = ('int18m.'::text || replace((business_key)::text, '-'::text, ''::text))))))))"}
EXTRA_FUNCTIONS={'interview_head_guard': '6219aa292d679bff71b2dbdbe54c4757a17bdee5cd3e2a76927d2fa9a7abc134', 'interview_record_insert_guard': 'f7423ecf9109244b5a87db568a552f9a0027b2ad9968281af66af07c56729c90', 'interview_result_eligible': '3a876b12080499d63c36bd7b1fa0d7960dc902f07bcabec99750cdf242342da6', 'purge_retrieval_payloads': '9061a126b5071be4fb7fb290715cda2b32f3d36dd9b8c3fcd8c30152a69f9879', 'retrieval_chunk_guard': '2b8801abe7c42eaaa8c2ffc5e4117e251c459c593110c16faf0016d696431bab', 'retrieval_command_guard': '60f095b5fce6112ba379e55225fe1d5891776af49add282732b35f76922af8f9', 'retrieval_embedding_operation_guard': '281ee019897fa19348f4dbcf4ef3413bb3ee437f425013fb388798cf39ce1d1f', 'retrieval_grant_guard': '4180d259e118ea97920af23c4b522a81407c64fcf56255ec8cff3cda8fb3a7b1', 'retrieval_result_guard': '4be9a24c1b99970b490ea9668b322112008ea63a0feac62ae1b5fcc6639f42dc', 'retrieval_space_guard': 'd59fb999006732863da65b08717fe2dfddf4afcc796cd7d0dc9348cebcd38321', 'retrieval_vector_digest': 'f02439231d89a6da4fe1497980e114042719ff5eb36ab884e530ad9e232ba4cb'}

NEW_COLUMNS={
 'retrieval_spaces':{'space_id':'text','provider':'text','configured_model':'text','dimensions':'smallint','normalization':'text','chunk_recipe':'text','created_at':'timestamptz'},
 'retrieval_commands':{'activity_id':'uuid','business_key':'uuid','action':'text','space_id':'text','scope_revision':'integer','domain':'text','domain_revision':'integer','request_body':'text','request_sha256':'text','source_refs':'jsonb','parent_refs':'jsonb','query_sha256':'text','manifest_sha256':'text','batch_count':'smallint','status':'text','terminal_disposition':'text','result_sha256':'text','error_code':'text','created_at':'timestamptz','updated_at':'timestamptz'},
 'retrieval_chunks':{'space_id':'text','evidence_id':'text','source_id':'uuid','source_version_id':'uuid','source_revision':'integer','origin':'text','physical_page':'integer','start_codepoint':'integer','end_codepoint':'integer','text_sha256':'text','vector_value':'vector(512)','vector_sha256':'text','committed_activity_id':'uuid','committed_operation_id':'text','created_at':'timestamptz'}}
columns02=deepcopy(COLUMNS);columns02['activities']['outbound_grant_sha256']='text';columns02.update(NEW_COLUMNS)
tables02=['retrieval_spaces']
for table in TABLES:
    if table=='activity_operations':tables02.append('retrieval_commands')
    tables02.append(table)
    if table=='activity_operation_results':tables02.append('retrieval_chunks')


@dataclass(frozen=True)
class SchemaProfile:
    name:str
    tables:tuple
    columns:dict
    codec_migrations:dict
    migration_chain:dict


def get_profile(name):
    chain01={**MIGRATIONS,'013_data_exit.sql':MIGRATION_013}
    if name==PROFILE:return SchemaProfile(PROFILE,TABLES,COLUMNS,MIGRATIONS,chain01)
    if name in (R02,R03):
        chain02={**chain01,'014_step018_retrieval.sql':MIGRATION_014}
        chain=chain02 if name==R02 else {**chain02,'015_activity_scope_delete_permission.sql':MIGRATION_015}
        return SchemaProfile(name,tuple(tables02),columns02,chain,chain)
    raise DataError('schema_profile_mismatch',503)


def get_read_profile(name,migrations):
    """Two exact known R03 codec identities; installations always use current DDL.

    Legacy package recognition never claims the old installation passed revised
    preconditions. A restored target is freshly initialized with current DDL.
    """
    profile=get_profile(name)
    if migrations==profile.codec_migrations:return profile
    if name==R03:
        legacy={**get_profile(R02).codec_migrations,'015_activity_scope_delete_permission.sql':LEGACY_MIGRATION_015}
        if migrations==legacy:
            return SchemaProfile(name,profile.tables,profile.columns,legacy,profile.migration_chain)
    raise DataError('codec_mismatch',422)


def observed_profile(connection,*,empty_profile=None):
    row=connection.execute('SELECT schema_profile FROM public.data_export_control_v1').fetchone()
    if row is None:
        if empty_profile is None:raise DataError('mode_unknown',503)
        return get_profile(empty_profile)
    return get_profile(row['schema_profile'] if isinstance(row,dict) else row[0])


async def observed_profile_async(connection):
    cursor=await connection.execute('SELECT schema_profile FROM public.data_export_control_v1');row=await cursor.fetchone()
    if row is None:raise DataError('mode_unknown',503)
    return get_profile(row['schema_profile'])


def extra_shape_queries():
    """仅固定新增对象和明确旧表增量；常量hash由本卡受信迁移实库冻结。"""
    return {
      'columns':"""SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod) AS type,a.attnotnull,pg_get_expr(d.adbin,d.adrelid) AS default,r.rolname AS owner,r.rolsuper AS owner_super,a.attacl::text AS acl
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner JOIN pg_attribute a ON a.attrelid=c.oid
        LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
        WHERE n.nspname='public' AND a.attnum>0 AND NOT a.attisdropped AND (c.relname IN('retrieval_spaces','retrieval_commands','retrieval_chunks') OR c.relname='activities' AND a.attname='outbound_grant_sha256') ORDER BY c.relname,a.attnum""",
      'constraints':"""SELECT c.relname,k.conname,pg_get_constraintdef(k.oid) AS definition,k.convalidated,k.condeferrable,k.condeferred
        FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND (c.relname IN('retrieval_spaces','retrieval_commands','retrieval_chunks') OR k.conname IN('activities_outbound_grant_sha256_check','activity_operations_kind_domain','activity_operations_kind_shape','activity_operations_max_output_tokens_check','interview_command_execution','data_control_schema_profile_check')) ORDER BY c.relname,k.conname""",
      'indexes':"SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' AND tablename IN('retrieval_spaces','retrieval_commands','retrieval_chunks') ORDER BY tablename,indexname",
      'triggers':"""SELECT c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid) AS definition FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND NOT t.tgisinternal AND (c.relname IN('retrieval_spaces','retrieval_commands','retrieval_chunks') OR t.tgname IN('retrieval_embedding_result','retrieval_embedding_operation','retrieval_grant_immutable','retrieval_source_tombstone')) ORDER BY c.relname,t.tgname""",
      'table_acl':"SELECT c.relname,c.relacl::text AS acl FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname IN('retrieval_spaces','retrieval_commands','retrieval_chunks') ORDER BY c.relname",
      'roles':"SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname IN('retrolume_retrieval_owner','retrolume_retrieval_app') ORDER BY rolname",
      'functions':"""SELECT p.proname,pg_get_function_identity_arguments(p.oid) AS arguments,p.prosrc,p.prosecdef,p.provolatile,p.proconfig,r.rolname AS owner,p.proacl::text AS acl
        FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner
        WHERE n.nspname='public' AND p.proname IN('retrieval_vector_digest','retrieval_space_guard','retrieval_command_guard','retrieval_result_guard','retrieval_chunk_guard','retrieval_grant_guard','retrieval_embedding_operation_guard','purge_retrieval_payloads','interview_head_guard','interview_record_insert_guard','interview_result_eligible') ORDER BY p.proname""",
      'interview_read_acl':"SELECT c.relname,has_table_privilege('retrolume_interview_owner',c.oid,'SELECT') AS readable,has_table_privilege('retrolume_interview_owner',c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') AS writable FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname IN('learning_memories','learning_memory_revisions','learning_memory_bodies','learning_memory_dependencies','learning_memory_commands','activity_memory_choices','teaching_commands','material_versions','pdf_review_candidates','pdf_review_pages','pdf_extracted_pages','teaching_records') ORDER BY c.relname",
      'extensions':"SELECT extname,extversion FROM pg_extension WHERE extname='vector'"}


def normalized_extra_shape(shape):
    """缓存集群bootstrap owner名字可不同；只规范grantor，权限集合仍必须精确。"""
    import copy,re
    value=copy.deepcopy(shape)
    for row in value.get('columns',[]):
        if row['relname']=='activities' and row['attname']=='outbound_grant_sha256' and row.get('owner_super') is True:
            row['owner']='bootstrap_owner'
    for section in ('columns','table_acl','functions'):
        for row in value.get(section,[]):
            if row.get('acl'):
                row['acl']=re.sub(r'/[^,}]+','/trusted_owner',row['acl'])
    return value


PROFILE_CONSTRAINT_02="CHECK ((schema_profile = ANY (ARRAY['data_exit.v1.r01'::text, 'data_exit.v1.r02'::text])))"
PROFILE_CONSTRAINT_03="CHECK ((schema_profile = 'data_exit.v1.r03'::text))"


def check_extra_shape(shape,profile=R02):
    if profile==R03:
        shape=deepcopy(shape)
        rows=[r for r in shape.get('constraints',[]) if r['conname']=='data_control_schema_profile_check']
        if len(rows)!=1 or rows[0]['definition']!=PROFILE_CONSTRAINT_03:raise DataError('data_schema_not_ready',503)
        rows[0]['definition']=PROFILE_CONSTRAINT_02
    elif profile!=R02:raise DataError('schema_profile_mismatch',503)
    if digest(canonical(normalized_extra_shape(shape)))!=R02_EXTRA_SHAPE_SHA:raise DataError('data_schema_not_ready',503)


SCOPE_ACL_QUERY="""SELECT a.attname,CASE WHEN x.grantee=c.relowner THEN '<owner>'
 ELSE COALESCE(g.rolname,'<public>') END AS grantee,x.privilege_type,x.is_grantable,
 x.grantor=c.relowner AS trusted_grantor,d.mode_observed,
 ARRAY(SELECT privilege_type FROM aclexplode(acldefault('r',c.relowner)) ORDER BY privilege_type) AS owner_privileges
 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN public.data_export_control_v1 d
 CROSS JOIN LATERAL (SELECT NULL::name AS attname,c.relacl AS acl UNION ALL
 SELECT attname,attacl FROM pg_attribute WHERE attrelid=c.oid AND attnum>0 AND NOT attisdropped) a
 CROSS JOIN LATERAL aclexplode(a.acl) x LEFT JOIN pg_roles g ON g.oid=x.grantee
 WHERE n.nspname='public' AND c.relname='activity_scope_sources'
 ORDER BY a.attname NULLS FIRST,grantee,x.privilege_type"""


def check_scope_permissions(rows,profile):
    get_profile(profile)
    modes={row['mode_observed'] for row in rows}
    if len(modes)!=1 or not modes<={'normal','loading','frozen','restored_readonly'}:raise DataError('data_schema_not_ready',503)
    expected={None:{'<owner>':set(rows[0]['owner_privileges']) if rows else set(),
      'retrolume_data_app':{'SELECT','INSERT','UPDATE'}|({'DELETE'} if profile==R03 else set()),
      'retrolume_data_owner':{'SELECT'},'retrolume_data_restore_loader':{'SELECT','INSERT'},
      'retrolume_interview_owner':{'SELECT'},'retrolume_html_owner':{'SELECT'}}}
    if profile in (R02,R03):expected[None]['retrolume_retrieval_owner']={'SELECT'}
    if modes=={'restored_readonly'}:expected[None]['retrolume_data_snapshot']={'SELECT'}
    for column in ('activity_id','source_id','version_id','source_revision'):
        expected[column]={'retrolume_data_snapshot':{'SELECT'}}
    actual={}
    for row in rows:
        if row['is_grantable'] and row['grantee']!='<owner>' or not row['trusted_grantor']:
            raise DataError('data_schema_not_ready',503)
        actual.setdefault(row['attname'],{}).setdefault(row['grantee'],set()).add(row['privilege_type'])
    if actual!=expected:raise DataError('data_schema_not_ready',503)


def project_scope_permission(shape):
    """Only after assert_data_schema checked the actual profile and exact ACL."""
    result=deepcopy(shape)
    for section in ('columns','table_acl','qualification_column_acls'):
        for row in result.get(section,[]):
            if row.get('relname')!='activity_scope_sources':continue
            for field in ('acl','table_acl','column_acl'):
                text=row.get(field)
                if text:
                    import re
                    row[field]=re.sub(r'(?<=[{,])retrolume_data_app=arwd/', 'retrolume_data_app=arw/',text)
    return result


def project_014(shape):
    """经精确R02校验后，旧领域指纹只扣除已注册014变化，不采用未知DDL。"""
    import re
    result=deepcopy(shape)
    for row in result.get('functions',[]):
        name=row['proname']
        if name in FORWARD_FUNCTIONS:
            actual=digest(re.sub(r'\s+','',row['prosrc']))
            if actual==FORWARD_FUNCTIONS[name]:row['prosrc']=ORIGINAL_FUNCTIONS_013[name]
            elif actual!=digest(re.sub(r'\s+','',ORIGINAL_FUNCTIONS_013[name])):raise DataError('data_schema_not_ready',503)
    for row in result.get('constraints',[]):
        if row['conname'] in ORIGINAL_CONSTRAINTS_013:
            if row['definition']==FORWARD_CONSTRAINTS_014[row['conname']]:row['definition']=ORIGINAL_CONSTRAINTS_013[row['conname']]
            elif row['definition']!=ORIGINAL_CONSTRAINTS_013[row['conname']]:raise DataError('data_schema_not_ready',503)
    # 新授予interview owner的记忆只读/资格执行，逐项精确校验后回投旧形状。
    readable={'learning_memories','learning_memory_revisions','learning_memory_bodies','learning_memory_dependencies','learning_memory_commands','activity_memory_choices','teaching_commands','material_versions','pdf_review_candidates','pdf_review_pages','pdf_extracted_pages','teaching_records'}
    functions={'memory_revision_readable','memory_revision_eligible','activity_memory_eligible','memory_dependency_line','memory_dependency_digest','memory_scope_digest','memory_choice_digest'}
    for section in ('columns','table_acl','functions','qualification_column_acls'):
        for row in result.get(section,[]):
            for field in ('acl','table_acl','column_acl'):
                text=row.get(field)
                if not text:continue
                kept=[]
                for entry in text[1:-1].split(','):
                    if entry.startswith('retrolume_interview_owner='):
                        privilege=entry.split('=',1)[1].split('/',1)[0]
                        if not ((section=='functions' and row['proname'] in functions and privilege=='X') or row.get('relname') in readable and privilege=='r'):
                            kept.append(entry);continue
                    else:kept.append(entry)
                row[field]='{'+','.join(kept)+'}' if kept else None
    return result
