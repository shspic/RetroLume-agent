-- TASK-103 / G9-P 合成许可010；不由应用启动执行，不操作用户库。
BEGIN;
DO $pre$
DECLARE r record; shape text; domain text;
BEGIN
 IF current_schema()<>'public' OR current_setting('server_encoding')<>'UTF8' THEN
  RAISE EXCEPTION '010需要已核public/UTF8基线';
 END IF;
 IF to_regprocedure('pg_catalog.sha256(bytea)') IS NULL THEN RAISE EXCEPTION '010缺核心SHA256'; END IF;
 FOR r IN SELECT value FROM unnest(ARRAY['material_sources','material_versions','activities',
 'activity_scope_sources','activity_operations','activity_operation_results','teaching_heads',
 'teaching_commands','teaching_records']) AS value LOOP
  IF to_regclass('public.'||r.value) IS NULL THEN RAISE EXCEPTION '010旧基线缺失'; END IF;
 END LOOP;
 FOR r IN SELECT * FROM (VALUES
 ('material_sources','revision','integer'),('material_versions','sha256','character'),
 ('activities','scope_revision','integer'),('activities','execution_generation','integer'),
 ('activities','dispatch_closed','boolean'),('activities','max_tool_calls','integer'),
 ('activities','running_reserved_seconds','bigint'),('activities','running_settled_seconds','bigint'),
 ('activity_operations','kind','text'),('activity_operation_results','payload','text'),
 ('activity_operation_results','payload_sha256','text'),('teaching_records','source_refs','text'),
 ('teaching_records','applied_revision','integer'),('teaching_records','state_after','text'),
 ('teaching_commands','context_body','text')) x(tbl,col,typ) LOOP
  IF NOT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema='public'
    AND table_name=r.tbl AND column_name=r.col AND data_type=r.typ) THEN
   RAISE EXCEPTION '010列基线不符';
  END IF;
 END LOOP;
 IF NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conrelid='public.material_versions'::regclass
   AND contype='u' AND pg_get_constraintdef(oid)='UNIQUE (source_id, id)') OR
 NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conrelid='public.teaching_records'::regclass
   AND contype='p' AND pg_get_constraintdef(oid)='PRIMARY KEY (activity_id, record_id)') THEN
  RAISE EXCEPTION '010复合FK基线不符';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_proc p ON p.oid=t.tgfoid
  WHERE t.tgrelid='public.teaching_records'::regclass AND t.tgname='teaching_records_immutable'
  AND t.tgenabled='O' AND NOT t.tgisinternal
  AND regexp_replace(p.prosrc,'[[:space:]]','','g')=
      'BEGINRAISEEXCEPTION''教学历史不可覆盖或直接删除'';END;') THEN
  RAISE EXCEPTION '010旧事实不可变基线不符';
 END IF;
 SELECT pg_get_expr(conbin,conrelid) INTO domain
 FROM pg_constraint WHERE conrelid='public.activity_operations'::regclass
 AND conname='activity_operations_kind_domain' AND convalidated;
 SELECT pg_get_expr(conbin,conrelid) INTO shape FROM pg_constraint
 WHERE conrelid='public.activity_operations'::regclass
 AND conname='activity_operations_kind_shape' AND convalidated;
 domain:=lower(regexp_replace(regexp_replace(domain,'::text|::character varying(\([0-9]+\))?(\[\])?','','g'),'[[:space:]()]','','g'));
 shape:=lower(regexp_replace(regexp_replace(shape,'::text|::character varying(\([0-9]+\))?(\[\])?','','g'),'[[:space:]()]','','g'));
 IF domain IS DISTINCT FROM $expected$kind=anyarray['model','tool']$expected$
 OR shape IS DISTINCT FROM $expected$kind='model'andproviderisnotnullandconfigured_modelisnotnullandrequest_bytesisnotnullandrequest_bytes>0andmax_output_tokensisnotnullandmax_output_tokens>0andreserved_cost_microunits>0andarguments_sha256isnullandtool_call_idisnullorkind='tool'andproviderisnullandconfigured_modelisnullandrequest_bytesisnullandmax_output_tokensisnullandreserved_cost_microunits=0andtool_names=array['finite_calculate']andarguments_sha256isnotnullandoctet_lengtharguments_sha256=64andarguments_sha256~'^[0-9a-f]{64}$'andtool_call_idisnotnullandchar_lengthtool_call_id>=1andchar_lengthtool_call_id<=128andtool_call_id!~'[^a-za-z0-9._:/-]'andremote_request_idisnullandreturned_modelisnullandfinish_reasonisnullandprompt_tokensisnullandcompletion_tokensisnullandresponse_bytesisnull$expected$ THEN
  RAISE EXCEPTION '010旧kind约束不符';
 END IF;
 FOR r IN SELECT value FROM unnest(ARRAY['learning_memories','learning_memory_revisions',
 'learning_memory_bodies','learning_memory_dependencies','learning_memory_commands',
 'activity_memory_bindings','activity_memory_choices']) AS value LOOP
  IF to_regclass('public.'||r.value) IS NOT NULL THEN RAISE EXCEPTION '010残迹/重复迁移'; END IF;
 END LOOP;
 IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname IN
  ('retrolume_memory_owner','retrolume_memory_app','retrolume_memory_purger')) THEN
  RAISE EXCEPTION '010角色残迹，不宽松复用';
 END IF;
END $pre$;
CREATE ROLE retrolume_memory_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE retrolume_memory_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE retrolume_memory_purger NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

CREATE TABLE public.learning_memories(
 memory_id UUID PRIMARY KEY, revision INTEGER NOT NULL CHECK(revision BETWEEN 1 AND 2147483647),
 current_version INTEGER NOT NULL CHECK(current_version BETWEEN 1 AND 32),
 state TEXT NOT NULL CHECK(state IN ('active','revoked')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 revoked_at TIMESTAMPTZ, revocation_key UUID, purged_at TIMESTAMPTZ,
 purge_state TEXT NOT NULL DEFAULT 'none' CHECK(purge_state IN ('none','pending','done')),
 CHECK((state='active' AND revoked_at IS NULL AND revocation_key IS NULL AND purged_at IS NULL AND purge_state='none')
 OR(state='revoked' AND revoked_at IS NOT NULL AND revocation_key IS NOT NULL
 AND((purge_state='pending' AND purged_at IS NULL) OR(purge_state='done' AND purged_at IS NOT NULL))))
);
CREATE TABLE public.learning_memory_commands(
 business_key UUID PRIMARY KEY, action TEXT NOT NULL CHECK(action IN ('save','revise','revoke','purge')),
 memory_id UUID NOT NULL REFERENCES public.learning_memories(memory_id) DEFERRABLE INITIALLY DEFERRED,
 request_sha256 TEXT NOT NULL CHECK(request_sha256 ~ '^[0-9a-f]{64}$'),
 slot_sha256 TEXT NOT NULL CHECK(slot_sha256 ~ '^[0-9a-f]{64}$'), effect_applied BOOLEAN NOT NULL,
 before_revision INTEGER NOT NULL CHECK(before_revision BETWEEN 0 AND 2147483647),
 after_revision INTEGER NOT NULL CHECK(after_revision BETWEEN 1 AND 2147483647),
 after_version INTEGER NOT NULL CHECK(after_version BETWEEN 1 AND 32),
 result_meta TEXT NOT NULL CHECK(octet_length(result_meta) BETWEEN 2 AND 4096),
 cleanup_manifest TEXT CHECK(cleanup_manifest IS NULL OR octet_length(cleanup_manifest) BETWEEN 2 AND 8192),
 manifest_sha256 TEXT CHECK(manifest_sha256 IS NULL OR manifest_sha256 ~ '^[0-9a-f]{64}$'),
 committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(memory_id,business_key),
 CHECK((cleanup_manifest IS NULL)=(manifest_sha256 IS NULL)),
 CHECK(action='revoke' OR cleanup_manifest IS NULL)
);
CREATE UNIQUE INDEX memory_effect_slot ON public.learning_memory_commands(slot_sha256) WHERE effect_applied;
CREATE TABLE public.learning_memory_revisions(
 memory_id UUID NOT NULL REFERENCES public.learning_memories(memory_id),
 version INTEGER NOT NULL CHECK(version BETWEEN 1 AND 32), PRIMARY KEY(memory_id,version),
 claim_kind TEXT NOT NULL CHECK(claim_kind IN ('self_report','preference','focus','learning_observation')),
 uncertainty TEXT NOT NULL CHECK(uncertainty IN ('self_reported','unknown','limited')),
 policy_version TEXT NOT NULL CHECK(policy_version IN ('memory.user.v1','memory.observation.v1')),
 body_sha256 TEXT NOT NULL CHECK(body_sha256 ~ '^[0-9a-f]{64}$'),
 body_bytes INTEGER NOT NULL CHECK(body_bytes BETWEEN 2 AND 4096),
 dependencies_sha256 TEXT NOT NULL CHECK(dependencies_sha256 ~ '^[0-9a-f]{64}$'),
 dependency_count SMALLINT NOT NULL CHECK(dependency_count BETWEEN 0 AND 32),
 created_by_key UUID NOT NULL UNIQUE, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(memory_id,created_by_key) REFERENCES public.learning_memory_commands(memory_id,business_key)
 DEFERRABLE INITIALLY DEFERRED,
 CHECK((claim_kind='learning_observation' AND uncertainty IN ('limited','unknown') AND policy_version='memory.observation.v1')
 OR(claim_kind<>'learning_observation' AND uncertainty IN ('self_reported','unknown') AND policy_version='memory.user.v1'))
);
ALTER TABLE public.learning_memories ADD CONSTRAINT memory_current_version
 FOREIGN KEY(memory_id,current_version) REFERENCES public.learning_memory_revisions(memory_id,version)
 DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE public.learning_memories ADD CONSTRAINT memory_revoke_command
 FOREIGN KEY(memory_id,revocation_key) REFERENCES public.learning_memory_commands(memory_id,business_key)
 DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE public.learning_memory_bodies(
 memory_id UUID NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL CHECK(octet_length(body) BETWEEN 2 AND 4096),
 PRIMARY KEY(memory_id,version),
 FOREIGN KEY(memory_id,version) REFERENCES public.learning_memory_revisions(memory_id,version)
);
CREATE TABLE public.learning_memory_dependencies(
 memory_id UUID NOT NULL, version INTEGER NOT NULL, ordinal SMALLINT NOT NULL CHECK(ordinal BETWEEN 1 AND 32),
 dependency_kind TEXT NOT NULL CHECK(dependency_kind IN ('source','event','memory')),
 source_id UUID, source_version_id UUID, source_revision INTEGER CHECK(source_revision>=0), original_sha256 TEXT,
 origin_activity_id UUID, record_id UUID, record_kind TEXT, record_sha256 TEXT,
 origin_scope_revision INTEGER CHECK(origin_scope_revision>0), origin_goal_version INTEGER CHECK(origin_goal_version BETWEEN 1 AND 32),
 upstream_memory_id UUID, upstream_version INTEGER CHECK(upstream_version BETWEEN 1 AND 32), upstream_body_sha256 TEXT,
 PRIMARY KEY(memory_id,version,ordinal),
 FOREIGN KEY(memory_id,version) REFERENCES public.learning_memory_revisions(memory_id,version),
 FOREIGN KEY(source_id,source_version_id) REFERENCES public.material_versions(source_id,id),
 FOREIGN KEY(origin_activity_id,record_id) REFERENCES public.teaching_records(activity_id,record_id),
 FOREIGN KEY(upstream_memory_id,upstream_version) REFERENCES public.learning_memory_revisions(memory_id,version),
 CHECK(upstream_memory_id IS NULL OR upstream_memory_id<>memory_id),
 CHECK(original_sha256 IS NULL OR original_sha256 ~ '^[0-9a-f]{64}$'),
 CHECK(record_sha256 IS NULL OR record_sha256 ~ '^[0-9a-f]{64}$'),
 CHECK(upstream_body_sha256 IS NULL OR upstream_body_sha256 ~ '^[0-9a-f]{64}$'),
 CHECK(record_kind IS NULL OR record_kind IN ('exercise','answer','feedback','progress','correction')),
 CHECK(
 (dependency_kind='source' AND num_nonnulls(source_id,source_version_id,source_revision,original_sha256)=4
  AND num_nonnulls(origin_activity_id,record_id,record_kind,record_sha256,origin_scope_revision,origin_goal_version,
   upstream_memory_id,upstream_version,upstream_body_sha256)=0)
 OR(dependency_kind='event' AND num_nonnulls(origin_activity_id,record_id,record_kind,record_sha256,
  origin_scope_revision,origin_goal_version)=6
  AND num_nonnulls(source_id,source_version_id,source_revision,original_sha256,
  upstream_memory_id,upstream_version,upstream_body_sha256)=0)
 OR(dependency_kind='memory' AND num_nonnulls(upstream_memory_id,upstream_version,upstream_body_sha256)=3
  AND num_nonnulls(source_id,source_version_id,source_revision,original_sha256,origin_activity_id,record_id,
   record_kind,record_sha256,origin_scope_revision,origin_goal_version)=0))
);
CREATE UNIQUE INDEX memory_source_once ON public.learning_memory_dependencies(memory_id,version,source_id,source_version_id) WHERE dependency_kind='source';
CREATE UNIQUE INDEX memory_event_once ON public.learning_memory_dependencies(memory_id,version,origin_activity_id,record_id) WHERE dependency_kind='event';
CREATE UNIQUE INDEX memory_upstream_once ON public.learning_memory_dependencies(memory_id,version,upstream_memory_id,upstream_version) WHERE dependency_kind='memory';
CREATE INDEX memory_source_dependencies ON public.learning_memory_dependencies(source_id,source_version_id,memory_id,version);
CREATE INDEX memory_event_dependencies ON public.learning_memory_dependencies(origin_activity_id,record_id,memory_id,version);
CREATE INDEX memory_upstream_dependencies ON public.learning_memory_dependencies(upstream_memory_id,upstream_version,memory_id,version);
CREATE INDEX memory_heads_recent ON public.learning_memories(state,updated_at DESC,memory_id);
CREATE TABLE public.activity_memory_bindings(
 activity_id UUID PRIMARY KEY REFERENCES public.activities(id),
 selection_sha256 TEXT NOT NULL CHECK(selection_sha256 ~ '^[0-9a-f]{64}$'),
 create_request_sha256 TEXT NOT NULL CHECK(create_request_sha256 ~ '^[0-9a-f]{64}$'),
 bound_scope_revision INTEGER NOT NULL CHECK(bound_scope_revision>0),
 bound_scope_sha256 TEXT NOT NULL CHECK(bound_scope_sha256 ~ '^[0-9a-f]{64}$'),
 selected_count SMALLINT NOT NULL CHECK(selected_count BETWEEN 1 AND 4),
 policy_version TEXT NOT NULL CHECK(policy_version='memory.selection.v1'),
 selected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.activity_memory_choices(
 activity_id UUID NOT NULL REFERENCES public.activity_memory_bindings(activity_id), memory_id UUID NOT NULL,
 version INTEGER NOT NULL CHECK(version BETWEEN 1 AND 32), selected_revision INTEGER NOT NULL CHECK(selected_revision>0),
 body_sha256 TEXT NOT NULL CHECK(body_sha256 ~ '^[0-9a-f]{64}$'), ordinal SMALLINT NOT NULL CHECK(ordinal BETWEEN 1 AND 4),
 PRIMARY KEY(activity_id,memory_id), UNIQUE(activity_id,ordinal),
 FOREIGN KEY(memory_id,version) REFERENCES public.learning_memory_revisions(memory_id,version)
);
CREATE INDEX memory_choice_dependents ON public.activity_memory_choices(memory_id,version,activity_id);

CREATE FUNCTION public.memory_dependency_line(d public.learning_memory_dependencies) RETURNS TEXT
 LANGUAGE SQL IMMUTABLE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT CASE d.dependency_kind
 WHEN 'source' THEN concat_ws('|','source',d.source_id,d.source_version_id,d.source_revision,d.original_sha256)
 WHEN 'event' THEN concat_ws('|','event',d.origin_activity_id,d.record_id,d.record_kind,d.origin_scope_revision,d.origin_goal_version,d.record_sha256)
 WHEN 'memory' THEN concat_ws('|','memory',d.upstream_memory_id,d.upstream_version,d.upstream_body_sha256) END
$f$;
CREATE FUNCTION public.memory_dependency_digest(mid UUID,ver INTEGER) RETURNS TEXT
 LANGUAGE SQL STABLE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT encode(sha256(convert_to(coalesce(string_agg(public.memory_dependency_line(d),E'\n' ORDER BY ordinal),''),'UTF8')),'hex')
 FROM public.learning_memory_dependencies d WHERE d.memory_id=mid AND d.version=ver
$f$;
CREATE FUNCTION public.memory_scope_digest(aid UUID) RETURNS TEXT
 LANGUAGE SQL STABLE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT encode(sha256(convert_to(coalesce(string_agg(concat_ws('|',s.source_id,s.version_id,s.source_revision,v.sha256),
 E'\n' ORDER BY s.source_id),''),'UTF8')),'hex')
 FROM public.activity_scope_sources s JOIN public.material_versions v ON v.source_id=s.source_id AND v.id=s.version_id WHERE s.activity_id=aid
$f$;
CREATE FUNCTION public.memory_choice_digest(aid UUID) RETURNS TEXT
 LANGUAGE SQL STABLE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT encode(sha256(convert_to(coalesce(string_agg(concat_ws('|',memory_id,version,selected_revision,body_sha256),
 E'\n' ORDER BY ordinal),''),'UTF8')),'hex') FROM public.activity_memory_choices WHERE activity_id=aid
$f$;
CREATE FUNCTION public.memory_revision_readable(mid UUID,ver INTEGER) RETURNS BOOLEAN
 LANGUAGE SQL STABLE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT EXISTS(
 SELECT 1 FROM public.learning_memories h JOIN public.learning_memory_revisions r USING(memory_id)
 JOIN public.learning_memory_bodies b USING(memory_id,version)
 WHERE h.memory_id=mid AND r.version=ver AND h.state='active'
 AND r.body_sha256=encode(sha256(convert_to(b.body,'UTF8')),'hex') AND r.body_bytes=octet_length(b.body)
 AND r.dependency_count=(SELECT count(*) FROM public.learning_memory_dependencies WHERE memory_id=mid AND version=ver)
 AND r.dependencies_sha256=public.memory_dependency_digest(mid,ver)
 AND NOT EXISTS(
 SELECT 1 FROM public.learning_memory_dependencies d
 LEFT JOIN public.material_sources s ON s.id=d.source_id
 LEFT JOIN public.material_versions v ON v.source_id=d.source_id AND v.id=d.source_version_id
 WHERE d.memory_id=mid AND d.version=ver AND d.dependency_kind='source'
 AND(s.current_version IS DISTINCT FROM d.source_version_id OR s.revision IS DISTINCT FROM d.source_revision
 OR v.sha256 IS DISTINCT FROM d.original_sha256
 OR(v.format='pdf' AND NOT EXISTS(SELECT 1 FROM public.pdf_review_candidates c WHERE c.version_id=v.id
 AND c.status='confirmed' AND c.page_count BETWEEN 1 AND 50
 AND(SELECT count(*) FROM public.pdf_review_pages p WHERE p.candidate_id=c.id)=c.page_count
 AND(SELECT count(*) FROM public.pdf_extracted_pages p WHERE p.version_id=c.version_id)=c.page_count))))
 AND NOT EXISTS(
 SELECT 1 FROM public.learning_memory_dependencies d LEFT JOIN public.teaching_records t
 ON t.activity_id=d.origin_activity_id AND t.record_id=d.record_id
 WHERE d.memory_id=mid AND d.version=ver AND d.dependency_kind='event'
 AND(t.kind IS DISTINCT FROM d.record_kind OR t.body_sha256 IS DISTINCT FROM d.record_sha256
 OR t.scope_revision IS DISTINCT FROM d.origin_scope_revision OR t.goal_version IS DISTINCT FROM d.origin_goal_version
 OR EXISTS(SELECT 1 FROM public.teaching_records x WHERE x.activity_id=t.activity_id
 AND((x.kind='correction' AND x.parent_record_id=t.record_id)
 OR(x.kind='answer' AND x.supersedes_record_id=t.record_id)
 OR(x.kind='feedback' AND t.kind IN ('feedback','progress') AND x.answer_record_id=t.answer_record_id AND x.seq>t.seq)))))
 AND NOT EXISTS(
 SELECT 1 FROM public.learning_memory_dependencies d
 LEFT JOIN public.learning_memories up ON up.memory_id=d.upstream_memory_id
 LEFT JOIN public.learning_memory_revisions ur ON ur.memory_id=d.upstream_memory_id AND ur.version=d.upstream_version
 LEFT JOIN public.learning_memory_bodies ub ON ub.memory_id=ur.memory_id AND ub.version=ur.version
 WHERE d.memory_id=mid AND d.version=ver AND d.dependency_kind='memory'
 AND(up.state IS DISTINCT FROM 'active' OR up.current_version IS DISTINCT FROM d.upstream_version
 OR ur.body_sha256 IS DISTINCT FROM d.upstream_body_sha256 OR ub.body IS NULL
 OR encode(sha256(convert_to(ub.body,'UTF8')),'hex') IS DISTINCT FROM d.upstream_body_sha256
 OR EXISTS(SELECT 1 FROM public.learning_memory_dependencies pd WHERE pd.memory_id=d.upstream_memory_id
 AND pd.version=d.upstream_version AND NOT EXISTS(SELECT 1 FROM public.learning_memory_dependencies cd
 WHERE cd.memory_id=mid AND cd.version=ver AND public.memory_dependency_line(cd)=public.memory_dependency_line(pd)))))
 )
$f$;
CREATE FUNCTION public.memory_revision_eligible(mid UUID,ver INTEGER) RETURNS BOOLEAN
 LANGUAGE SQL STABLE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT public.memory_revision_readable(mid,ver) AND EXISTS(SELECT 1 FROM public.learning_memories WHERE memory_id=mid AND current_version=ver AND state='active')
$f$;
CREATE FUNCTION public.activity_memory_eligible(aid UUID) RETURNS BOOLEAN
 LANGUAGE SQL STABLE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT (NOT EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=aid)
 AND NOT EXISTS(SELECT 1 FROM public.activity_operation_results r WHERE r.activity_id=aid
  AND r.payload_format='json' AND r.payload::jsonb->'value'->>'profile'='teaching.v2')
 AND NOT EXISTS(SELECT 1 FROM public.teaching_commands c WHERE c.activity_id=aid
  AND c.context_body IS NOT NULL AND c.context_body::jsonb->>'schema'='teaching.context.v2')) OR EXISTS(
 SELECT 1 FROM public.activity_memory_bindings b JOIN public.activities a ON a.id=b.activity_id
 WHERE b.activity_id=aid AND b.bound_scope_revision=a.scope_revision
 AND EXISTS(SELECT 1 FROM public.activity_scope_sources WHERE activity_id=aid)
 AND NOT EXISTS(SELECT 1 FROM public.activity_scope_sources sc LEFT JOIN public.material_sources ms ON ms.id=sc.source_id
 WHERE sc.activity_id=aid AND(ms.current_version IS DISTINCT FROM sc.version_id OR ms.revision IS DISTINCT FROM sc.source_revision))
 AND b.bound_scope_sha256=public.memory_scope_digest(aid) AND b.selection_sha256=public.memory_choice_digest(aid)
 AND b.selected_count=(SELECT count(*) FROM public.activity_memory_choices WHERE activity_id=aid)
 AND NOT EXISTS(SELECT 1 FROM public.activity_memory_choices c JOIN public.learning_memories h USING(memory_id)
 WHERE c.activity_id=aid AND(h.revision<>c.selected_revision OR h.current_version<>c.version
 OR NOT public.memory_revision_eligible(c.memory_id,c.version)
 OR c.body_sha256 IS DISTINCT FROM(SELECT body_sha256 FROM public.learning_memory_revisions WHERE memory_id=c.memory_id AND version=c.version)
 OR EXISTS(SELECT 1 FROM public.learning_memory_dependencies d WHERE d.memory_id=c.memory_id AND d.version=c.version
 AND d.dependency_kind='source' AND NOT EXISTS(SELECT 1 FROM public.activity_scope_sources s
 WHERE s.activity_id=aid AND s.source_id=d.source_id AND s.version_id=d.source_version_id AND s.source_revision=d.source_revision))))
 )
$f$;

CREATE FUNCTION public.memory_immutable_guard() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN RAISE EXCEPTION '学习记忆身份不可改写或直接删除'; END $f$;
CREATE TRIGGER memory_revision_immutable BEFORE UPDATE OR DELETE ON public.learning_memory_revisions FOR EACH ROW EXECUTE FUNCTION public.memory_immutable_guard();
CREATE TRIGGER memory_dependency_immutable BEFORE UPDATE OR DELETE ON public.learning_memory_dependencies FOR EACH ROW EXECUTE FUNCTION public.memory_immutable_guard();
CREATE TRIGGER memory_command_immutable BEFORE UPDATE OR DELETE ON public.learning_memory_commands FOR EACH ROW EXECUTE FUNCTION public.memory_immutable_guard();
CREATE TRIGGER memory_binding_immutable BEFORE UPDATE OR DELETE ON public.activity_memory_bindings FOR EACH ROW EXECUTE FUNCTION public.memory_immutable_guard();
CREATE TRIGGER memory_choice_immutable BEFORE UPDATE OR DELETE ON public.activity_memory_choices FOR EACH ROW EXECUTE FUNCTION public.memory_immutable_guard();
CREATE FUNCTION public.memory_head_guard() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE ok BOOLEAN;
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION '记忆头不可直接删除'; END IF;
 IF TG_OP='INSERT' THEN
  IF NEW.revision<>1 OR NEW.current_version<>1 OR NEW.state<>'active' THEN RAISE EXCEPTION '记忆初始身份不符'; END IF;
  RETURN NEW;
 END IF;
 IF ROW(NEW.memory_id,NEW.created_at) IS DISTINCT FROM ROW(OLD.memory_id,OLD.created_at) THEN RAISE EXCEPTION '记忆身份不可改'; END IF;
 IF current_user='retrolume_memory_purger' THEN
  IF ROW(NEW.revision,NEW.current_version,NEW.state,NEW.revoked_at,NEW.revocation_key,NEW.updated_at)
   IS DISTINCT FROM ROW(OLD.revision,OLD.current_version,OLD.state,OLD.revoked_at,OLD.revocation_key,OLD.updated_at)
   OR OLD.state<>'revoked' OR OLD.purge_state<>'pending' OR NEW.purge_state<>'done' OR NEW.purged_at IS NULL THEN
   RAISE EXCEPTION '清理只可完成原墓碑'; END IF;
  RETURN NEW;
 END IF;
 IF OLD.state='revoked' OR NEW.revision<>OLD.revision+1 OR NEW.purged_at IS DISTINCT FROM OLD.purged_at THEN
  RAISE EXCEPTION '撤销不可复活或CAS不符'; END IF;
 SELECT EXISTS(SELECT 1 FROM public.learning_memory_commands c WHERE c.memory_id=NEW.memory_id
 AND c.effect_applied AND c.before_revision=OLD.revision AND c.after_revision=NEW.revision
 AND c.after_version=NEW.current_version
 AND((NEW.state='active' AND c.action='revise' AND NEW.current_version=OLD.current_version+1)
 OR(NEW.state='revoked' AND c.action='revoke' AND c.business_key=NEW.revocation_key
 AND NEW.current_version=OLD.current_version))) INTO ok;
 IF NOT ok THEN RAISE EXCEPTION '记忆修改缺同事务收据'; END IF;
 RETURN NEW;
END $f$;
CREATE TRIGGER memory_head_identity BEFORE INSERT OR UPDATE OR DELETE ON public.learning_memories FOR EACH ROW EXECUTE FUNCTION public.memory_head_guard();
CREATE FUNCTION public.memory_body_guard() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE h record; r record; value JSONB;
BEGIN
 IF TG_OP='UPDATE' THEN RAISE EXCEPTION '记忆正文不可覆盖'; END IF;
 IF TG_OP='DELETE' THEN
  IF current_user<>'retrolume_memory_purger' THEN RAISE EXCEPTION '只可用获准精确清理函数'; END IF;
  RETURN OLD;
 END IF;
 SELECT state,current_version INTO h FROM public.learning_memories WHERE memory_id=NEW.memory_id FOR KEY SHARE;
 IF h.state IS DISTINCT FROM 'active' OR NEW.version NOT IN(h.current_version,h.current_version+1) THEN
  RAISE EXCEPTION '撤销正文不可重插'; END IF;
 SELECT body_sha256,body_bytes,claim_kind,uncertainty INTO r FROM public.learning_memory_revisions WHERE memory_id=NEW.memory_id AND version=NEW.version;
 IF r.body_sha256 IS DISTINCT FROM encode(sha256(convert_to(NEW.body,'UTF8')),'hex')
 OR r.body_bytes IS DISTINCT FROM octet_length(NEW.body) THEN RAISE EXCEPTION '记忆正文hash/字节不符'; END IF;
 value=NEW.body::jsonb;
 IF jsonb_typeof(value)<>'object' OR value->>'schema'<>'memory.body.v1'
 OR value->>'kind' IS DISTINCT FROM r.claim_kind OR value->>'uncertainty' IS DISTINCT FROM r.uncertainty
 OR jsonb_typeof(value->'title') IS DISTINCT FROM 'string' OR char_length(value->>'title')>80
 OR jsonb_typeof(value->'text') IS DISTINCT FROM 'string' OR char_length(value->>'text')>1024
 OR EXISTS(SELECT 1 FROM jsonb_object_keys(value) k WHERE k NOT IN('schema','title','kind','text','uncertainty','observation')) THEN
  RAISE EXCEPTION '记忆正文性质或字段不符';
 END IF;
 RETURN NEW;
END $f$;
CREATE TRIGGER memory_body_integrity BEFORE INSERT OR UPDATE OR DELETE ON public.learning_memory_bodies FOR EACH ROW EXECUTE FUNCTION public.memory_body_guard();
CREATE FUNCTION public.memory_final_shape_guard() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE r record; b record;
BEGIN
 IF TG_TABLE_NAME='activity_memory_choices' OR TG_TABLE_NAME='activity_memory_bindings' THEN
  SELECT selected_count,selection_sha256,bound_scope_sha256 INTO b FROM public.activity_memory_bindings WHERE activity_id=NEW.activity_id;
  IF b.selected_count IS DISTINCT FROM(SELECT count(*)::smallint FROM public.activity_memory_choices WHERE activity_id=NEW.activity_id)
  OR b.selection_sha256 IS DISTINCT FROM public.memory_choice_digest(NEW.activity_id)
  OR b.bound_scope_sha256 IS DISTINCT FROM public.memory_scope_digest(NEW.activity_id) THEN RAISE EXCEPTION '记忆选择数量/摘要不符'; END IF;
 ELSE
  SELECT dependency_count,dependencies_sha256,claim_kind INTO r FROM public.learning_memory_revisions WHERE memory_id=NEW.memory_id AND version=NEW.version;
  IF r.dependency_count IS DISTINCT FROM(SELECT count(*)::smallint FROM public.learning_memory_dependencies WHERE memory_id=NEW.memory_id AND version=NEW.version)
  OR r.dependencies_sha256 IS DISTINCT FROM public.memory_dependency_digest(NEW.memory_id,NEW.version)
  OR(r.claim_kind='learning_observation' AND NOT EXISTS(SELECT 1 FROM public.learning_memory_dependencies WHERE memory_id=NEW.memory_id AND version=NEW.version AND dependency_kind='event')) THEN
   RAISE EXCEPTION '记忆依赖数量/摘要不符'; END IF;
  IF (SELECT count(*) FROM public.learning_memory_dependencies WHERE memory_id=NEW.memory_id AND version=NEW.version AND dependency_kind='source')>10
   OR (SELECT count(*) FROM public.learning_memory_dependencies WHERE memory_id=NEW.memory_id AND version=NEW.version AND dependency_kind='event')>8
   OR (SELECT count(*) FROM public.learning_memory_dependencies WHERE memory_id=NEW.memory_id AND version=NEW.version AND dependency_kind='memory')>14 THEN
   RAISE EXCEPTION '记忆依赖种类容量不符'; END IF;
  IF EXISTS(SELECT 1 FROM public.learning_memory_dependencies d WHERE d.memory_id=NEW.memory_id AND d.version=NEW.version
    AND d.dependency_kind='memory' AND(
     NOT EXISTS(SELECT 1 FROM public.learning_memory_dependencies e JOIN public.activity_memory_choices c
      ON c.activity_id=e.origin_activity_id AND c.memory_id=d.upstream_memory_id AND c.version=d.upstream_version
       AND c.body_sha256=d.upstream_body_sha256 WHERE e.memory_id=NEW.memory_id AND e.version=NEW.version AND e.dependency_kind='event')
     OR EXISTS(SELECT 1 FROM public.learning_memory_dependencies p WHERE p.memory_id=d.upstream_memory_id AND p.version=d.upstream_version
      AND NOT EXISTS(SELECT 1 FROM public.learning_memory_dependencies child WHERE child.memory_id=NEW.memory_id AND child.version=NEW.version
        AND public.memory_dependency_line(child)=public.memory_dependency_line(p))))) THEN
   RAISE EXCEPTION '记忆上游缺选用事实或完整闭包'; END IF;
 END IF;
 RETURN NULL;
END $f$;
CREATE CONSTRAINT TRIGGER memory_revision_shape AFTER INSERT ON public.learning_memory_revisions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION public.memory_final_shape_guard();
CREATE CONSTRAINT TRIGGER memory_dependencies_shape AFTER INSERT ON public.learning_memory_dependencies DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION public.memory_final_shape_guard();
CREATE CONSTRAINT TRIGGER memory_binding_shape AFTER INSERT ON public.activity_memory_bindings DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION public.memory_final_shape_guard();
CREATE CONSTRAINT TRIGGER memory_choices_shape AFTER INSERT ON public.activity_memory_choices DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION public.memory_final_shape_guard();

CREATE FUNCTION public.purge_learning_memory(revocation_key UUID,manifest_sha256 TEXT,purge_business_key UUID,request_sha256 TEXT)
 RETURNS TEXT LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE cmd record; h record; existing record; item record; bodyrow record; manifest JSONB; meta TEXT; total INTEGER; slot TEXT;
BEGIN
 SELECT c.memory_id,c.cleanup_manifest,c.manifest_sha256 INTO cmd FROM public.learning_memory_commands c
 WHERE c.business_key=purge_learning_memory.revocation_key AND c.action='revoke' AND c.effect_applied;
 IF cmd.memory_id IS NULL OR cmd.manifest_sha256 IS DISTINCT FROM manifest_sha256
 OR encode(sha256(convert_to(cmd.cleanup_manifest,'UTF8')),'hex') IS DISTINCT FROM manifest_sha256 THEN RAISE EXCEPTION '精确清理清单无效'; END IF;
 SELECT mh.revision,mh.current_version,mh.state,mh.purge_state,mh.revocation_key INTO h
 FROM public.learning_memories mh WHERE mh.memory_id=cmd.memory_id FOR UPDATE;
 SELECT c.request_sha256,c.result_meta INTO existing FROM public.learning_memory_commands c WHERE c.business_key=purge_business_key;
 IF existing.result_meta IS NOT NULL THEN
  IF existing.request_sha256 IS DISTINCT FROM request_sha256 THEN RAISE EXCEPTION '清理键冲突'; END IF;
  RETURN existing.result_meta;
 END IF;
 slot=encode(sha256(convert_to('purge|'||revocation_key::text||'|'||manifest_sha256,'UTF8')),'hex');
 SELECT c.result_meta INTO meta FROM public.learning_memory_commands c WHERE c.slot_sha256=slot AND c.effect_applied;
 IF meta IS NOT NULL THEN RETURN meta; END IF;
 IF h.state<>'revoked' OR h.purge_state<>'pending' OR h.revocation_key IS DISTINCT FROM purge_learning_memory.revocation_key THEN RAISE EXCEPTION '清理要求原撤销墓碑'; END IF;
 manifest=cmd.cleanup_manifest::jsonb;
 IF manifest->>'policy'<>'memory.purge.v1' OR (manifest->>'memory_id')::uuid<>cmd.memory_id
 OR (manifest->>'revocation_key')::uuid<>revocation_key OR (manifest->>'revision')::integer<>h.revision
 OR jsonb_typeof(manifest->'targets')<>'array' THEN RAISE EXCEPTION '清理身份不符'; END IF;
 total=jsonb_array_length(manifest->'targets');
 IF total NOT BETWEEN 1 AND 32 OR total<>(SELECT count(DISTINCT value->>'version') FROM jsonb_array_elements(manifest->'targets')) OR total<>(SELECT count(*) FROM public.learning_memory_bodies WHERE memory_id=cmd.memory_id) THEN RAISE EXCEPTION '清理集合不符'; END IF;
 FOR item IN SELECT value FROM jsonb_array_elements(manifest->'targets') LOOP
  IF (item.value->>'memory_id')::uuid<>cmd.memory_id THEN RAISE EXCEPTION '清理不得越记忆'; END IF;
  SELECT b.body,r.body_sha256,r.body_bytes INTO bodyrow FROM public.learning_memory_bodies b
  JOIN public.learning_memory_revisions r USING(memory_id,version)
  WHERE b.memory_id=cmd.memory_id AND b.version=(item.value->>'version')::integer;
  IF bodyrow.body IS NULL OR bodyrow.body_sha256 IS DISTINCT FROM item.value->>'body_sha256'
   OR bodyrow.body_bytes IS DISTINCT FROM (item.value->>'body_bytes')::integer
   OR encode(sha256(convert_to(bodyrow.body,'UTF8')),'hex') IS DISTINCT FROM bodyrow.body_sha256
   OR octet_length(bodyrow.body)<>bodyrow.body_bytes THEN RAISE EXCEPTION '清理目标hash不符'; END IF;
 END LOOP;
 FOR item IN SELECT value FROM jsonb_array_elements(manifest->'targets') ORDER BY (value->>'version')::integer LOOP
  DELETE FROM public.learning_memory_bodies WHERE memory_id=cmd.memory_id AND version=(item.value->>'version')::integer;
 END LOOP;
 -- 字段只来自已核UUID/hash/整数，按应用canonical键序和无空白格式保存。
 meta='{"manifest_sha256":"'||manifest_sha256||'","memory_id":"'||cmd.memory_id::text||
  '","purge_state_now":"done","revision_after":'||h.revision::text||',"revocation_key":"'||revocation_key::text||
  '","status":"committed","version_after":'||h.current_version::text||'}';
 INSERT INTO public.learning_memory_commands(business_key,action,memory_id,request_sha256,slot_sha256,effect_applied,
 before_revision,after_revision,after_version,result_meta) VALUES(purge_business_key,'purge',cmd.memory_id,
 request_sha256,slot,true,h.revision,h.revision,h.current_version,meta);
 UPDATE public.learning_memories SET purge_state='done',purged_at=CURRENT_TIMESTAMP WHERE memory_id=cmd.memory_id;
 RETURN meta;
END $f$;

DO $own$
DECLARE r record;
BEGIN
 FOR r IN SELECT value FROM unnest(ARRAY['learning_memories','learning_memory_revisions','learning_memory_bodies',
 'learning_memory_dependencies','learning_memory_commands','activity_memory_bindings','activity_memory_choices']) AS value LOOP
  EXECUTE format('ALTER TABLE public.%I OWNER TO retrolume_memory_owner',r.value);
  EXECUTE format('REVOKE ALL ON public.%I FROM PUBLIC',r.value);
  EXECUTE format('GRANT SELECT,INSERT ON public.%I TO retrolume_memory_app',r.value);
 END LOOP;
 FOR r IN SELECT p.oid::regprocedure AS name FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='public' AND(p.proname=ANY(ARRAY['memory_dependency_line','memory_dependency_digest','memory_scope_digest','memory_choice_digest','memory_revision_readable','memory_revision_eligible','activity_memory_eligible','memory_immutable_guard','memory_head_guard','memory_body_guard','memory_final_shape_guard','purge_learning_memory'])) LOOP
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.name);
  EXECUTE format('ALTER FUNCTION %s OWNER TO retrolume_memory_owner',r.name);
  EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO retrolume_memory_app',r.name);
 END LOOP;
END $own$;
ALTER FUNCTION public.purge_learning_memory(UUID,TEXT,UUID,TEXT) OWNER TO retrolume_memory_purger;
GRANT USAGE ON SCHEMA public TO retrolume_memory_app,retrolume_memory_purger;
GRANT UPDATE(current_version,revision,state,updated_at,revoked_at,revocation_key,purge_state) ON public.learning_memories TO retrolume_memory_app;
GRANT SELECT ON public.learning_memories,public.learning_memory_revisions,public.learning_memory_bodies,public.learning_memory_commands TO retrolume_memory_purger;
GRANT DELETE ON public.learning_memory_bodies TO retrolume_memory_purger;
GRANT INSERT ON public.learning_memory_commands TO retrolume_memory_purger;
GRANT UPDATE(purge_state,purged_at) ON public.learning_memories TO retrolume_memory_purger;
COMMIT;

