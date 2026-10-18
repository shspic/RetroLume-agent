-- TASK-106 G10-P: synthetic adoption only. No automatic application/startup migration.
-- Additive to approved 001--010; no old facts, counters, functions or grants changed.
BEGIN;
DO $$ BEGIN
  IF to_regclass('public.activities') IS NULL OR to_regclass('public.activity_operation_results') IS NULL
     OR to_regclass('public.teaching_heads') IS NULL THEN RAISE EXCEPTION '011 prerequisites missing'; END IF;
  IF to_regclass('public.interview_heads') IS NOT NULL OR to_regclass('public.interview_commands') IS NOT NULL
     OR to_regclass('public.interview_records') IS NOT NULL THEN RAISE EXCEPTION '011 already present'; END IF;
  IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname IN ('retrolume_interview_owner','retrolume_interview_app'))
    THEN RAISE EXCEPTION '011 role collision'; END IF;
END; $$;
CREATE ROLE retrolume_interview_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE retrolume_interview_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT USAGE ON SCHEMA public TO retrolume_interview_owner,retrolume_interview_app;

CREATE TABLE public.interview_heads (
 activity_id uuid PRIMARY KEY REFERENCES public.activities(id),
 revision integer NOT NULL CHECK(revision BETWEEN 1 AND 2147483647),
 goal_version integer NOT NULL CHECK(goal_version BETWEEN 0 AND 32),
 phase text NOT NULL CHECK(phase IN ('needs_goal','ready','question_ready','answer_ready','feedback_ready','ended')),
 last_seq integer NOT NULL CHECK(last_seq BETWEEN 1 AND 4096),
 round_index integer NOT NULL CHECK(round_index BETWEEN 0 AND 4096),
 probe_depth integer NOT NULL CHECK(probe_depth BETWEEN 0 AND 4),
 goal_record_id uuid, root_question_id uuid, current_question_id uuid, current_answer_id uuid, current_feedback_id uuid,
 pending_key uuid,
 scope_revision integer NOT NULL CHECK(scope_revision BETWEEN 1 AND 2147483647),
 source_snapshot_sha256 text NOT NULL CHECK(source_snapshot_sha256 ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT interview_goal_shape CHECK((goal_version=0 AND goal_record_id IS NULL AND phase IN ('needs_goal','ended')) OR (goal_version>0 AND goal_record_id IS NOT NULL))
);
CREATE TABLE public.interview_commands (
 activity_id uuid NOT NULL REFERENCES public.activities(id), business_key uuid NOT NULL,
 action text NOT NULL CHECK(action IN ('start','goal','ask','answer','correct_answer','review','bind_scope','abandon','finish')),
 request_body text NOT NULL CHECK(octet_length(request_body) BETWEEN 1 AND 32768),
 request_sha256 text NOT NULL CHECK(request_sha256 ~ '^[0-9a-f]{64}$'),
 semantic_slot text NOT NULL CHECK(semantic_slot ~ '^[0-9a-f]{64}$'),
 execution_kind text NOT NULL CHECK(execution_kind IN ('local','model')),
 context_body text CHECK(octet_length(context_body) BETWEEN 1 AND 49152),
 context_sha256 text CHECK(context_sha256 ~ '^[0-9a-f]{64}$'),
 operation_id text,
 status text NOT NULL CHECK(status IN ('accepted','started','committed','history','not_sent','failed','unknown','abandoned')),
 launch_claimed boolean NOT NULL DEFAULT false, obsolete boolean NOT NULL DEFAULT false,
 effect_applied boolean NOT NULL DEFAULT false,
 duplicate_of uuid, retry_of uuid,
 before_revision integer NOT NULL CHECK(before_revision BETWEEN 0 AND 2147483647),
 after_revision integer CHECK(after_revision BETWEEN 1 AND 2147483647),
 goal_version integer NOT NULL CHECK(goal_version BETWEEN 0 AND 32),
 scope_revision integer NOT NULL CHECK(scope_revision BETWEEN 1 AND 2147483647),
 result_record_ids uuid[] NOT NULL DEFAULT '{}' CHECK(cardinality(result_record_ids)<=2),
 error_code text CHECK(error_code ~ '^[A-Za-z0-9._:/-]{1,64}$'),
 created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY(activity_id,business_key), UNIQUE(activity_id,operation_id),
 FOREIGN KEY(activity_id,duplicate_of) REFERENCES public.interview_commands(activity_id,business_key),
 FOREIGN KEY(activity_id,retry_of) REFERENCES public.interview_commands(activity_id,business_key),
 CONSTRAINT interview_command_execution CHECK(
  (duplicate_of IS NOT NULL AND operation_id IS NULL AND context_body IS NULL AND context_sha256 IS NULL AND NOT effect_applied AND NOT launch_claimed)
  OR (duplicate_of IS NULL AND execution_kind='local' AND operation_id IS NULL AND context_body IS NULL AND context_sha256 IS NULL AND NOT launch_claimed)
  OR (duplicate_of IS NULL AND execution_kind='model' AND action IN ('ask','review') AND context_body IS NOT NULL AND context_sha256 IS NOT NULL
      AND operation_id='int10m.'||replace(business_key::text,'-',''))),
 CONSTRAINT interview_command_hash CHECK(encode(sha256(convert_to(request_body,'UTF8')),'hex')=request_sha256
      AND (context_body IS NULL OR encode(sha256(convert_to(context_body,'UTF8')),'hex')=context_sha256))
);
CREATE UNIQUE INDEX interview_live_slot ON public.interview_commands(activity_id,semantic_slot)
 WHERE duplicate_of IS NULL AND status IN ('accepted','started','unknown','committed','history');
CREATE INDEX interview_command_status ON public.interview_commands(activity_id,status);
CREATE TABLE public.interview_records (
 activity_id uuid NOT NULL REFERENCES public.activities(id),record_id uuid NOT NULL,
 seq integer NOT NULL CHECK(seq BETWEEN 1 AND 4096),business_key uuid NOT NULL,ordinal integer NOT NULL CHECK(ordinal BETWEEN 0 AND 1),
 kind text NOT NULL CHECK(kind IN ('start','goal','scope','question','answer','probe','feedback','finish','abandon')),
 origin text NOT NULL CHECK(origin IN ('application','user','model')),
 goal_version integer NOT NULL CHECK(goal_version BETWEEN 0 AND 32),scope_revision integer NOT NULL CHECK(scope_revision BETWEEN 1 AND 2147483647),
 round_index integer NOT NULL CHECK(round_index BETWEEN 0 AND 4096),probe_depth integer NOT NULL CHECK(probe_depth BETWEEN 0 AND 4),
 answer_version integer CHECK(answer_version BETWEEN 1 AND 256),
 parent_ids uuid[] NOT NULL DEFAULT '{}' CHECK(cardinality(parent_ids)<=12),
 question_record_id uuid,supersedes_record_id uuid,
 source_refs jsonb NOT NULL CHECK(jsonb_typeof(source_refs)='array' AND jsonb_array_length(source_refs) BETWEEN 1 AND 10),
 body_sha256 text NOT NULL CHECK(body_sha256 ~ '^[0-9a-f]{64}$'),
 local_body text CHECK(octet_length(local_body) BETWEEN 1 AND 32768),operation_id text,payload_sha256 text,
 created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY(activity_id,record_id),UNIQUE(activity_id,seq),UNIQUE(activity_id,business_key,ordinal),
 UNIQUE(activity_id,question_record_id,answer_version),
 FOREIGN KEY(activity_id,business_key) REFERENCES public.interview_commands(activity_id,business_key),
 FOREIGN KEY(activity_id,question_record_id) REFERENCES public.interview_records(activity_id,record_id),
 FOREIGN KEY(activity_id,supersedes_record_id) REFERENCES public.interview_records(activity_id,record_id),
 FOREIGN KEY(activity_id,operation_id) REFERENCES public.activity_operation_results(activity_id,operation_id),
 CONSTRAINT interview_record_storage CHECK((origin='model' AND kind IN ('question','probe','feedback') AND local_body IS NULL
    AND operation_id IS NOT NULL AND payload_sha256=body_sha256)
  OR (origin<>'model' AND local_body IS NOT NULL AND operation_id IS NULL AND payload_sha256 IS NULL
    AND encode(sha256(convert_to(local_body,'UTF8')),'hex')=body_sha256)),
 CONSTRAINT interview_answer_shape CHECK((kind='answer' AND origin='user' AND answer_version IS NOT NULL AND question_record_id IS NOT NULL)
  OR (kind<>'answer' AND answer_version IS NULL AND supersedes_record_id IS NULL))
);
CREATE INDEX interview_record_parents ON public.interview_records USING gin(parent_ids);
ALTER TABLE public.interview_heads ADD FOREIGN KEY(activity_id,goal_record_id) REFERENCES public.interview_records(activity_id,record_id),
 ADD FOREIGN KEY(activity_id,root_question_id) REFERENCES public.interview_records(activity_id,record_id),
 ADD FOREIGN KEY(activity_id,current_question_id) REFERENCES public.interview_records(activity_id,record_id),
 ADD FOREIGN KEY(activity_id,current_answer_id) REFERENCES public.interview_records(activity_id,record_id),
 ADD FOREIGN KEY(activity_id,current_feedback_id) REFERENCES public.interview_records(activity_id,record_id),
 ADD FOREIGN KEY(activity_id,pending_key) REFERENCES public.interview_commands(activity_id,business_key);

CREATE FUNCTION public.interview_record_insert_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE c public.interview_commands; p public.interview_records; r public.activity_operation_results; o public.activity_operations; b jsonb; ref jsonb;
BEGIN
 SELECT * INTO c FROM public.interview_commands WHERE activity_id=NEW.activity_id AND business_key=NEW.business_key;
 IF c.activity_id IS NULL OR c.duplicate_of IS NOT NULL OR c.effect_applied OR c.status NOT IN ('accepted','started')
    OR NEW.seq<>(SELECT COALESCE(max(seq),0)+1 FROM public.interview_records WHERE activity_id=NEW.activity_id)
    THEN RAISE EXCEPTION 'interview record command/sequence invalid'; END IF;
 IF cardinality(NEW.parent_ids)<>(SELECT count(DISTINCT x) FROM unnest(NEW.parent_ids) x) THEN RAISE EXCEPTION 'duplicate parents'; END IF;
 FOR p IN SELECT * FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=ANY(NEW.parent_ids) LOOP
  IF p.seq>=NEW.seq OR p.goal_version<>NEW.goal_version OR p.scope_revision<>NEW.scope_revision THEN RAISE EXCEPTION 'interview parent invalid'; END IF;
 END LOOP;
 IF cardinality(NEW.parent_ids)<>(SELECT count(*) FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=ANY(NEW.parent_ids)) THEN RAISE EXCEPTION 'missing parents'; END IF;
 IF NEW.kind='answer' THEN
  SELECT * INTO p FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.question_record_id;
  IF p.kind NOT IN ('question','probe') OR p.goal_version<>NEW.goal_version OR p.scope_revision<>NEW.scope_revision
     OR NEW.answer_version<>(SELECT COALESCE(max(answer_version),0)+1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND question_record_id=NEW.question_record_id)
     THEN RAISE EXCEPTION 'answer version invalid'; END IF;
  IF NEW.answer_version>1 AND NOT EXISTS(SELECT 1 FROM public.interview_records a WHERE a.activity_id=NEW.activity_id AND a.record_id=NEW.supersedes_record_id
     AND a.question_record_id=NEW.question_record_id AND a.answer_version=NEW.answer_version-1) THEN RAISE EXCEPTION 'supersedes invalid'; END IF;
 END IF;
 IF NEW.origin='model' THEN
  SELECT * INTO r FROM public.activity_operation_results WHERE activity_id=NEW.activity_id AND operation_id=NEW.operation_id;
  SELECT * INTO o FROM public.activity_operations WHERE activity_id=NEW.activity_id AND operation_id=NEW.operation_id;
  b:=r.payload::jsonb->'value';
  IF c.execution_kind<>'model' OR c.operation_id<>NEW.operation_id OR NOT c.launch_claimed OR c.obsolete OR c.status<>'started'
    OR r.payload_format<>'json' OR r.payload_sha256<>NEW.body_sha256 OR o.kind<>'model' OR o.state<>'received'
    OR r.admission_id<>o.admission_id OR r.execution_generation<>o.execution_generation OR r.scope_revision<>NEW.scope_revision
    OR b->>'profile' IS DISTINCT FROM 'interview.v1' OR b->>'activity_id' IS DISTINCT FROM NEW.activity_id::text OR b->>'business_key' IS DISTINCT FROM NEW.business_key::text
    OR b->>'request_sha256' IS DISTINCT FROM c.request_sha256 OR b->>'context_sha256' IS DISTINCT FROM c.context_sha256 OR b->'value'->>'type' IS DISTINCT FROM NEW.kind
    THEN RAISE EXCEPTION 'interview result binding invalid'; END IF;
 ELSE
  b:=NEW.local_body::jsonb;
  IF b->>'schema' IS DISTINCT FROM 'interview.local.v1' OR b->>'activity_id' IS DISTINCT FROM NEW.activity_id::text OR b->>'business_key' IS DISTINCT FROM NEW.business_key::text
     OR b->>'kind' IS DISTINCT FROM NEW.kind OR (b->>'goal_version')::integer IS DISTINCT FROM NEW.goal_version OR (b->>'scope_revision')::integer IS DISTINCT FROM NEW.scope_revision
     OR jsonb_typeof(b->'value') IS DISTINCT FROM 'object'
     THEN RAISE EXCEPTION 'interview local binding invalid'; END IF;
 END IF;
 RETURN NEW;
END;
$body$;
CREATE FUNCTION public.interview_record_immutable_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN RAISE EXCEPTION 'interview records are immutable'; END;
$body$;
CREATE FUNCTION public.interview_command_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'interview commands retained'; END IF;
 IF TG_OP='INSERT' THEN
  IF (SELECT count(*) FROM public.interview_commands WHERE activity_id=NEW.activity_id)>=4096 THEN RAISE EXCEPTION 'interview command limit'; END IF;
  IF NEW.effect_applied OR NEW.launch_claimed THEN RAISE EXCEPTION 'no pre-applied command'; END IF;
  RETURN NEW;
 END IF;
 IF (to_jsonb(NEW)-ARRAY['status','launch_claimed','obsolete','effect_applied','after_revision','result_record_ids','error_code','updated_at'])
       IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['status','launch_claimed','obsolete','effect_applied','after_revision','result_record_ids','error_code','updated_at'])
   OR (OLD.launch_claimed AND NOT NEW.launch_claimed) OR (OLD.obsolete AND NOT NEW.obsolete)
   OR (OLD.effect_applied AND (NOT NEW.effect_applied OR NEW.after_revision IS DISTINCT FROM OLD.after_revision OR NEW.result_record_ids IS DISTINCT FROM OLD.result_record_ids))
   THEN RAISE EXCEPTION 'interview command identity immutable'; END IF;
 IF OLD.status IS DISTINCT FROM NEW.status AND NOT (
  (OLD.status='accepted' AND NEW.status IN ('started','committed','not_sent','unknown','abandoned'))
  OR (OLD.status='started' AND NEW.status IN ('committed','not_sent','failed','unknown','abandoned'))
  OR (OLD.status='unknown' AND NEW.status='abandoned') OR (OLD.status='committed' AND NEW.status='history'))
  THEN RAISE EXCEPTION 'interview command transition invalid'; END IF;
 IF NOT OLD.effect_applied AND NEW.effect_applied THEN
  IF NEW.duplicate_of IS NOT NULL OR NEW.status<>'committed' OR cardinality(NEW.result_record_ids) NOT BETWEEN 1 AND 2
     OR NEW.after_revision IS DISTINCT FROM NEW.before_revision+1 OR cardinality(NEW.result_record_ids)<>(SELECT count(*) FROM public.interview_records
       WHERE activity_id=NEW.activity_id AND business_key=NEW.business_key AND record_id=ANY(NEW.result_record_ids))
   THEN RAISE EXCEPTION 'interview effect binding invalid'; END IF;
 END IF;
 RETURN NEW;
END;
$body$;
CREATE FUNCTION public.interview_head_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE a public.activities; ptr uuid; p public.interview_records;
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'interview heads retained'; END IF;
 SELECT * INTO a FROM public.activities WHERE id=NEW.activity_id;
 IF TG_OP='INSERT' THEN
  IF a.status<>'pending' OR a.execution_generation<>0 OR a.executor_id IS NOT NULL OR a.lease_expires_at IS NOT NULL
     OR a.requests_reserved<>0 OR a.cost_reserved_microunits<>0 OR a.tools_reserved<>0 OR a.running_reserved_seconds<>0 OR a.running_settled_seconds<>0
     OR EXISTS(SELECT 1 FROM public.teaching_heads WHERE activity_id=NEW.activity_id)
     OR EXISTS(SELECT 1 FROM public.activity_operations WHERE activity_id=NEW.activity_id)
     OR EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=NEW.activity_id)
     OR NEW.revision<>1 THEN RAISE EXCEPTION 'interview requires fresh unselected activity'; END IF;
 ELSE
  IF NEW.activity_id<>OLD.activity_id OR NEW.created_at<>OLD.created_at OR NEW.revision NOT BETWEEN OLD.revision AND OLD.revision+1
    OR NEW.goal_version NOT BETWEEN OLD.goal_version AND OLD.goal_version+1 OR NEW.last_seq<OLD.last_seq
    OR (NEW.revision=OLD.revision AND (to_jsonb(NEW)-ARRAY['pending_key','updated_at']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['pending_key','updated_at']))
    OR (OLD.phase='ended' AND NEW.phase<>'ended') THEN RAISE EXCEPTION 'interview head revision invalid'; END IF;
 END IF;
 IF NEW.scope_revision<>a.scope_revision OR NEW.last_seq<>(SELECT max(seq) FROM public.interview_records WHERE activity_id=NEW.activity_id)
    THEN RAISE EXCEPTION 'interview head scope/sequence invalid'; END IF;
 FOREACH ptr IN ARRAY ARRAY[NEW.goal_record_id,NEW.root_question_id,NEW.current_question_id,NEW.current_answer_id,NEW.current_feedback_id] LOOP
  IF ptr IS NOT NULL THEN
   SELECT * INTO p FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=ptr;
   IF p.record_id IS NULL OR p.goal_version<>NEW.goal_version OR p.scope_revision<>NEW.scope_revision THEN RAISE EXCEPTION 'interview head pointer invalid'; END IF;
  END IF;
 END LOOP;
 IF NEW.goal_record_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.goal_record_id AND kind='goal') THEN RAISE EXCEPTION 'goal pointer kind'; END IF;
 IF NEW.current_question_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.current_question_id AND kind IN ('question','probe')) THEN RAISE EXCEPTION 'question pointer kind'; END IF;
 IF NEW.current_answer_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.current_answer_id AND kind='answer' AND question_record_id=NEW.current_question_id) THEN RAISE EXCEPTION 'answer pointer kind'; END IF;
 IF NEW.current_feedback_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.interview_records WHERE activity_id=NEW.activity_id AND record_id=NEW.current_feedback_id AND kind='feedback') THEN RAISE EXCEPTION 'feedback pointer kind'; END IF;
 RETURN NEW;
END;
$body$;
CREATE FUNCTION public.interview_result_eligible(aid uuid, op text) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
 SELECT EXISTS(SELECT 1 FROM public.interview_commands c JOIN public.interview_heads h USING(activity_id)
  JOIN public.interview_records ir ON ir.activity_id=c.activity_id AND ir.business_key=c.business_key AND ir.origin='model'
  JOIN public.activities a ON a.id=c.activity_id
  JOIN public.activity_operations o ON o.activity_id=c.activity_id AND o.operation_id=c.operation_id
  JOIN public.activity_operation_results r ON r.activity_id=o.activity_id AND r.operation_id=o.operation_id
 WHERE c.activity_id=aid AND c.operation_id=op AND c.duplicate_of IS NULL AND c.effect_applied AND c.status IN ('committed','history')
  AND NOT c.obsolete AND c.goal_version=h.goal_version AND c.scope_revision=h.scope_revision AND h.scope_revision=a.scope_revision
  AND a.status<>'cancelled' AND ir.operation_id=c.operation_id AND ir.payload_sha256=r.payload_sha256 AND ir.body_sha256=r.payload_sha256
  AND r.admission_id=o.admission_id AND r.execution_generation=o.execution_generation AND r.scope_revision=o.scope_revision AND o.state='received' AND o.kind='model'
  AND r.payload_format='json'
  AND NOT EXISTS(SELECT 1 FROM public.activity_scope_sources s LEFT JOIN public.material_sources m ON m.id=s.source_id
    WHERE s.activity_id=aid AND (m.id IS NULL OR m.current_version IS DISTINCT FROM s.version_id OR m.revision<>s.source_revision))
  AND EXISTS(SELECT 1 FROM public.activity_scope_sources WHERE activity_id=aid)
  AND NOT EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=aid))
$body$;
CREATE TRIGGER interview_record_insert BEFORE INSERT ON public.interview_records FOR EACH ROW EXECUTE FUNCTION public.interview_record_insert_guard();
CREATE TRIGGER interview_record_immutable BEFORE UPDATE OR DELETE ON public.interview_records FOR EACH ROW EXECUTE FUNCTION public.interview_record_immutable_guard();
CREATE TRIGGER interview_command BEFORE INSERT OR UPDATE OR DELETE ON public.interview_commands FOR EACH ROW EXECUTE FUNCTION public.interview_command_guard();
CREATE TRIGGER interview_head BEFORE INSERT OR UPDATE OR DELETE ON public.interview_heads FOR EACH ROW EXECUTE FUNCTION public.interview_head_guard();
ALTER TABLE public.interview_heads OWNER TO retrolume_interview_owner;
ALTER TABLE public.interview_commands OWNER TO retrolume_interview_owner;
ALTER TABLE public.interview_records OWNER TO retrolume_interview_owner;
ALTER FUNCTION public.interview_record_insert_guard() OWNER TO retrolume_interview_owner;
ALTER FUNCTION public.interview_record_immutable_guard() OWNER TO retrolume_interview_owner;
ALTER FUNCTION public.interview_command_guard() OWNER TO retrolume_interview_owner;
ALTER FUNCTION public.interview_head_guard() OWNER TO retrolume_interview_owner;
ALTER FUNCTION public.interview_result_eligible(uuid,text) OWNER TO retrolume_interview_owner;
GRANT SELECT ON public.activities,public.activity_scope_sources,public.material_sources,public.activity_operations,
 public.activity_operation_results,public.teaching_heads,public.activity_memory_bindings TO retrolume_interview_owner;
REVOKE ALL ON FUNCTION public.interview_record_insert_guard(),public.interview_record_immutable_guard(),public.interview_command_guard(),public.interview_head_guard(),public.interview_result_eligible(uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.interview_result_eligible(uuid,text) TO retrolume_interview_app;
GRANT SELECT,INSERT ON public.interview_heads,public.interview_commands,public.interview_records TO retrolume_interview_app;
GRANT UPDATE(revision,goal_version,phase,last_seq,round_index,probe_depth,goal_record_id,root_question_id,current_question_id,
 current_answer_id,current_feedback_id,pending_key,scope_revision,source_snapshot_sha256,updated_at) ON public.interview_heads TO retrolume_interview_app;
GRANT UPDATE(status,launch_claimed,obsolete,effect_applied,after_revision,result_record_ids,error_code,updated_at) ON public.interview_commands TO retrolume_interview_app;
COMMIT;
