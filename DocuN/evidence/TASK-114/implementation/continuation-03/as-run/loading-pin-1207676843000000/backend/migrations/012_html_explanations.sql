-- G11-P110受信交互域。受控迁移一次执行，启动器不迁移用户数据库。
BEGIN;
DO $pre$
DECLARE name text;
BEGIN
 IF to_regclass('public.activities') IS NULL OR to_regclass('public.activity_operation_results') IS NULL
    OR to_regclass('public.teaching_records') IS NULL OR to_regclass('public.activity_memory_bindings') IS NULL
    OR to_regclass('public.interview_heads') IS NULL THEN RAISE EXCEPTION '012 requires complete 001-011'; END IF;
 IF EXISTS(SELECT 1 FROM (VALUES ('activities','scope_revision','integer'),('activities','dispatch_closed','boolean'),
   ('activity_operations','kind','text'),('activity_operation_results','payload','text'),('teaching_records','source_refs','text'))
   r(t,c,y) WHERE NOT EXISTS(SELECT 1 FROM information_schema.columns i WHERE i.table_schema='public'
   AND i.table_name=r.t AND i.column_name=r.c AND i.data_type=r.y)) THEN RAISE EXCEPTION '012 prerequisite shape invalid'; END IF;
 IF EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public'
   AND c.relname IN ('html_commands','html_artifacts','html_preview_budgets','html_preview_sessions'))
   OR EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public'
   AND p.proname LIKE 'html_%') THEN RAISE EXCEPTION '012 partial or existing schema retained'; END IF;
 FOREACH name IN ARRAY ARRAY['retrolume_html_owner','retrolume_html_app'] LOOP
  IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname=name) THEN
   IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname=name AND (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls))
   THEN RAISE EXCEPTION '012 role identity invalid'; END IF;
  ELSE EXECUTE format('CREATE ROLE %I NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS',name); END IF;
 END LOOP;
END;
$pre$;

CREATE TABLE public.html_commands(
 activity_id uuid NOT NULL REFERENCES public.activities(id), business_key uuid NOT NULL,
 operation_id text NOT NULL CHECK(operation_id='html11m.'||replace(business_key::text,'-','')),
 request_body text NOT NULL CHECK(octet_length(request_body) BETWEEN 2 AND 8192),
 request_sha256 text NOT NULL CHECK(request_sha256 ~ '^[0-9a-f]{64}$'),
 context_body text NOT NULL CHECK(octet_length(context_body) BETWEEN 2 AND 24576),
 context_sha256 text NOT NULL CHECK(context_sha256 ~ '^[0-9a-f]{64}$'),
 renderer_sha256 text NOT NULL CHECK(renderer_sha256 ~ '^[0-9a-f]{64}$'),
 scope_revision integer NOT NULL CHECK(scope_revision>0),
 parent_kind text NOT NULL CHECK(parent_kind IN ('learning','teaching')),
 parent_locator text NOT NULL, parent_sha256 text NOT NULL CHECK(parent_sha256 ~ '^[0-9a-f]{64}$'),
 status text NOT NULL DEFAULT 'accepted' CHECK(status IN ('accepted','launch_claimed','terminal')),
 terminal_disposition text CHECK(terminal_disposition IN ('succeeded','invalid_output','not_sent','unknown','refused')),
 error_code text CHECK(error_code ~ '^[A-Za-z0-9._:/-]{1,64}$'),
 created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY(activity_id,business_key), UNIQUE(activity_id,operation_id),
 CHECK(encode(sha256(convert_to(request_body,'UTF8')),'hex')=request_sha256),
 CHECK(encode(sha256(convert_to(context_body,'UTF8')),'hex')=context_sha256),
 CHECK((status='terminal')=(terminal_disposition IS NOT NULL))
);
CREATE TABLE public.html_artifacts(
 artifact_id uuid PRIMARY KEY, activity_id uuid NOT NULL, business_key uuid NOT NULL, operation_id text NOT NULL,
 artifact_body text NOT NULL CHECK(octet_length(artifact_body) BETWEEN 2 AND 110592),
 artifact_sha256 text NOT NULL CHECK(artifact_sha256 ~ '^[0-9a-f]{64}$'),
 description_sha256 text NOT NULL CHECK(description_sha256 ~ '^[0-9a-f]{64}$'),
 renderer_sha256 text NOT NULL CHECK(renderer_sha256 ~ '^[0-9a-f]{64}$'),
 execution_package_sha256 text NOT NULL CHECK(execution_package_sha256 ~ '^[0-9a-f]{64}$'),
 body_sha256 text NOT NULL CHECK(body_sha256 ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(activity_id,artifact_id), UNIQUE(activity_id,business_key), UNIQUE(activity_id,operation_id),
 FOREIGN KEY(activity_id,business_key) REFERENCES public.html_commands(activity_id,business_key),
 FOREIGN KEY(activity_id,operation_id) REFERENCES public.activity_operation_results(activity_id,operation_id)
);
CREATE TABLE public.html_preview_budgets(
 activity_id uuid PRIMARY KEY REFERENCES public.activities(id), config_sha256 text NOT NULL CHECK(config_sha256 ~ '^[0-9a-f]{64}$'),
 max_starts integer NOT NULL DEFAULT 3 CHECK(max_starts=3), max_seconds integer NOT NULL DEFAULT 180 CHECK(max_seconds=180),
 starts_used integer NOT NULL DEFAULT 0 CHECK(starts_used BETWEEN 0 AND 3),
 settled_seconds integer NOT NULL DEFAULT 0 CHECK(settled_seconds BETWEEN 0 AND 180),
 reserved_seconds integer NOT NULL DEFAULT 0 CHECK(reserved_seconds BETWEEN 0 AND 180),
 revision integer NOT NULL DEFAULT 0 CHECK(revision BETWEEN 0 AND 2147483647),
 CHECK(settled_seconds+reserved_seconds<=max_seconds)
);
CREATE TABLE public.html_preview_sessions(
 preview_id uuid PRIMARY KEY, activity_id uuid NOT NULL REFERENCES public.activities(id), artifact_id uuid NOT NULL,
 start_key uuid NOT NULL, generation integer NOT NULL CHECK(generation>0),
 artifact_sha256 text NOT NULL CHECK(artifact_sha256 ~ '^[0-9a-f]{64}$'),
 owner_id uuid NOT NULL, owner_key_sha256 text NOT NULL CHECK(owner_key_sha256 ~ '^[0-9a-f]{64}$'),
 control_key_sha256 text NOT NULL CHECK(control_key_sha256 ~ '^[0-9a-f]{64}$'),
 boot_id uuid NOT NULL, nonce text NOT NULL CHECK(nonce ~ '^[0-9a-f]{64}$'),
 image_id text NOT NULL CHECK(image_id ~ '^sha256:[0-9a-f]{64}$'),
 reserve_seconds integer NOT NULL CHECK(reserve_seconds BETWEEN 30 AND 60),
 elapsed_seconds integer CHECK(elapsed_seconds BETWEEN 0 AND 60),
 t0_ns bigint NOT NULL CHECK(t0_ns>0), deadline_ns bigint NOT NULL CHECK(deadline_ns>t0_ns),
 deadline_at timestamptz NOT NULL, cid text CHECK(cid ~ '^[0-9a-f]{64}$'),
 state text NOT NULL CHECK(state IN ('reserved','registered','start_requested','ready','running','stopping','stopped','failed_unstarted','cleanup_unconfirmed')),
 first_stop_receipt text CHECK(octet_length(first_stop_receipt) BETWEEN 2 AND 24576),
 confirmation_receipt text CHECK(octet_length(confirmation_receipt) BETWEEN 2 AND 24576),
 revision integer NOT NULL DEFAULT 0, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(activity_id,start_key), UNIQUE(activity_id,generation),
 FOREIGN KEY(activity_id,artifact_id) REFERENCES public.html_artifacts(activity_id,artifact_id),
 CHECK(deadline_ns=t0_ns+reserve_seconds::bigint*1000000000),
 CHECK((state IN ('stopped','failed_unstarted'))=(elapsed_seconds IS NOT NULL))
);
CREATE UNIQUE INDEX html_one_unconfirmed_activity ON public.html_preview_sessions(activity_id)
 WHERE state NOT IN ('stopped','failed_unstarted');

-- 固定程序字节由本迁移的构建步骤填入，角色不能自行重新采用某个renderer。
CREATE FUNCTION public.html_expected_renderer() RETURNS text LANGUAGE sql IMMUTABLE
 SET search_path=pg_catalog,public AS $body$ SELECT '6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597'::text $body$;
CREATE FUNCTION public.html_expected_html() RETURNS text LANGUAGE sql IMMUTABLE
 SET search_path=pg_catalog,public AS $body$ SELECT 'b09e7e37a08ebd4a08f8c3da461f64c0322df6f7a013cd3ac07bb32d32b9be11'::text $body$;

CREATE FUNCTION public.html_parent_eligible(aid uuid, frozen jsonb) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
 SELECT COALESCE((SELECT a.status<>'cancelled' AND a.deadline_at>CURRENT_TIMESTAMP
  AND a.scope_revision=(frozen->>'scope_revision')::integer
  AND public.activity_memory_eligible(a.id)
  AND (NOT EXISTS(SELECT 1 FROM public.activity_memory_bindings m WHERE m.activity_id=a.id)
       OR EXISTS(SELECT 1 FROM public.activity_memory_bindings m WHERE m.activity_id=a.id
             AND m.selection_sha256=frozen->>'memory_selection_sha256'))
  AND EXISTS(SELECT 1 FROM public.activity_scope_sources s WHERE s.activity_id=a.id)
  AND NOT EXISTS(SELECT 1 FROM jsonb_array_elements(frozen->'sources') ref WHERE NOT EXISTS(
    SELECT 1 FROM public.activity_scope_sources s JOIN public.material_sources m ON m.id=s.source_id
      JOIN public.material_versions v ON v.id=s.version_id AND v.source_id=s.source_id
     WHERE s.activity_id=a.id AND s.source_id::text=ref->>'source_id' AND s.version_id::text=ref->>'version_id'
      AND s.source_revision=(ref->>'source_revision')::integer AND m.current_version=s.version_id
      AND m.revision=s.source_revision AND v.sha256=ref->>'original_sha256'))
  AND jsonb_array_length(frozen->'sources')=(SELECT count(*) FROM public.activity_scope_sources s WHERE s.activity_id=a.id)
  AND CASE WHEN frozen->'parent'->>'kind'='learning' THEN EXISTS(
    SELECT 1 FROM public.activity_operations o JOIN public.activity_operation_results r
     ON r.activity_id=o.activity_id AND r.operation_id=o.operation_id
    WHERE o.activity_id=a.id AND o.operation_id=frozen->'parent'->>'operation_id' AND o.kind='model'
     AND o.state='received' AND o.scope_revision=a.scope_revision AND r.payload_sha256=frozen->'parent'->>'payload_sha256'
     AND r.admission_id=o.admission_id AND r.execution_generation=o.execution_generation
     AND r.payload::jsonb->'value'->>'profile'='learning.v1' AND r.payload::jsonb->'value'->'result'->>'kind'='answer')
   ELSE EXISTS(SELECT 1 FROM public.teaching_heads h JOIN public.teaching_records r ON r.activity_id=h.activity_id
    WHERE h.activity_id=a.id AND r.record_id::text=frozen->'parent'->>'record_id'
     AND r.body_sha256=frozen->'parent'->>'body_sha256' AND r.goal_version=h.goal_version
     AND r.scope_revision=a.scope_revision AND (r.kind='exercise' AND r.record_id=h.exercise_record_id
       OR r.kind='feedback' AND r.record_id=h.feedback_record_id))
    AND NOT EXISTS(SELECT 1 FROM jsonb_array_elements(frozen->'dependencies') d WHERE NOT EXISTS(
      SELECT 1 FROM public.teaching_records r WHERE r.activity_id=a.id AND r.record_id::text=d->>'record_id'
       AND r.body_sha256=d->>'body_sha256' AND r.scope_revision=a.scope_revision)) END
 FROM public.activities a WHERE a.id=aid),false)
$body$;

CREATE FUNCTION public.html_artifact_eligible(aid uuid, art uuid) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
 SELECT COALESCE((SELECT c.status='terminal' AND c.terminal_disposition='succeeded'
   AND o.kind='model' AND o.state='received' AND r.payload_sha256=b.body_sha256
   AND r.admission_id=o.admission_id AND r.execution_generation=o.execution_generation
   AND b.renderer_sha256=public.html_expected_renderer() AND c.renderer_sha256=b.renderer_sha256
   AND public.html_parent_eligible(aid,c.context_body::jsonb)
  FROM public.html_artifacts b JOIN public.html_commands c ON c.activity_id=b.activity_id AND c.business_key=b.business_key
   JOIN public.activity_operations o ON o.activity_id=b.activity_id AND o.operation_id=b.operation_id
   JOIN public.activity_operation_results r ON r.activity_id=b.activity_id AND r.operation_id=b.operation_id
  WHERE b.activity_id=aid AND b.artifact_id=art),false)
$body$;

CREATE FUNCTION public.html_command_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'html commands retained'; END IF;
 IF NEW.renderer_sha256<>public.html_expected_renderer() OR NEW.context_body::jsonb->>'schema'<>'html.context.v2'
  OR NEW.context_body::jsonb->>'activity_id'<>NEW.activity_id::text OR NEW.context_body::jsonb->>'business_key'<>NEW.business_key::text
  OR NEW.context_body::jsonb->>'request_sha256'<>NEW.request_sha256 THEN RAISE EXCEPTION 'html command binding'; END IF;
 IF TG_OP='INSERT' THEN
  IF NEW.status<>'accepted' OR (SELECT count(*) FROM public.html_commands WHERE activity_id=NEW.activity_id)>=4096
   OR NOT public.html_parent_eligible(NEW.activity_id,NEW.context_body::jsonb) THEN RAISE EXCEPTION 'html command ineligible'; END IF;
 ELSE
  IF (to_jsonb(NEW)-ARRAY['status','terminal_disposition','error_code','updated_at']) IS DISTINCT FROM
     (to_jsonb(OLD)-ARRAY['status','terminal_disposition','error_code','updated_at']) OR OLD.status='terminal'
   OR (NEW.status<>OLD.status AND NOT (OLD.status='accepted' AND NEW.status='launch_claimed'
       OR OLD.status='launch_claimed' AND NEW.status='terminal')) THEN RAISE EXCEPTION 'html command immutable'; END IF;
  IF NEW.status='launch_claimed' AND NOT public.html_parent_eligible(NEW.activity_id,NEW.context_body::jsonb)
   THEN RAISE EXCEPTION 'html command invalidated'; END IF;
 END IF;
 RETURN NEW;
END;
$body$;
CREATE FUNCTION public.html_artifact_insert_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE c public.html_commands; r public.activity_operation_results; o public.activity_operations; b jsonb;
BEGIN
 SELECT * INTO c FROM public.html_commands WHERE activity_id=NEW.activity_id AND business_key=NEW.business_key;
 SELECT * INTO r FROM public.activity_operation_results WHERE activity_id=NEW.activity_id AND operation_id=NEW.operation_id;
 SELECT * INTO o FROM public.activity_operations WHERE activity_id=NEW.activity_id AND operation_id=NEW.operation_id;
 b:=NEW.artifact_body::jsonb;
 IF c.activity_id IS NULL OR c.status<>'launch_claimed' OR c.operation_id<>NEW.operation_id
   OR o.kind IS DISTINCT FROM 'model' OR o.state IS DISTINCT FROM 'received' OR r.payload_format IS DISTINCT FROM 'json'
   OR r.payload_sha256 IS DISTINCT FROM NEW.body_sha256 OR r.admission_id IS DISTINCT FROM o.admission_id
   OR r.scope_revision IS DISTINCT FROM c.scope_revision OR r.execution_generation IS DISTINCT FROM o.execution_generation
   OR r.payload::jsonb->'value'->>'profile' IS DISTINCT FROM 'html_explanation.v2'
   OR r.payload::jsonb->'value'->>'context_sha256' IS DISTINCT FROM c.context_sha256
   OR r.payload::jsonb->'value'->>'request_sha256' IS DISTINCT FROM c.request_sha256
   OR r.payload::jsonb->'value'->'package' IS DISTINCT FROM b
   OR b->>'schema' IS DISTINCT FROM 'compiled_interactive_html.v1'
   OR b->>'artifact_sha256' IS DISTINCT FROM NEW.artifact_sha256
   OR b->>'description_sha256' IS DISTINCT FROM NEW.description_sha256
   OR encode(sha256(convert_to(b->>'description_json','UTF8')),'hex') IS DISTINCT FROM NEW.description_sha256
   OR NEW.renderer_sha256 IS DISTINCT FROM public.html_expected_renderer()
   OR b->'renderer'->>'renderer_sha256' IS DISTINCT FROM public.html_expected_renderer()
   OR b->>'execution_package_sha256' IS DISTINCT FROM NEW.execution_package_sha256
   OR encode(sha256(convert_to(b->>'compiled_html','UTF8')),'hex') IS DISTINCT FROM public.html_expected_html()
   OR NOT public.html_parent_eligible(NEW.activity_id,c.context_body::jsonb)
   THEN RAISE EXCEPTION 'html artifact integrity or qualification'; END IF;
 RETURN NEW;
END;
$body$;
CREATE FUNCTION public.html_immutable_guard() RETURNS trigger LANGUAGE plpgsql AS $body$
BEGIN RAISE EXCEPTION 'html artifact immutable'; END;
$body$;
CREATE FUNCTION public.html_preview_budget_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE used integer; settled integer; reserved integer;
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'html budgets retained'; END IF;
 IF TG_OP='UPDATE' AND ((to_jsonb(NEW)-ARRAY['starts_used','settled_seconds','reserved_seconds','revision'])
    IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['starts_used','settled_seconds','reserved_seconds','revision'])
    OR NEW.revision<>OLD.revision+1 OR NEW.starts_used<OLD.starts_used OR NEW.settled_seconds<OLD.settled_seconds)
    THEN RAISE EXCEPTION 'html budget identity or monotonicity'; END IF;
 SELECT count(*),COALESCE(sum(elapsed_seconds),0),COALESCE(sum(CASE WHEN elapsed_seconds IS NULL THEN reserve_seconds ELSE 0 END),0)
 INTO used,settled,reserved FROM public.html_preview_sessions WHERE activity_id=NEW.activity_id;
 IF NEW.starts_used<>used OR NEW.settled_seconds<>settled OR NEW.reserved_seconds<>reserved
 THEN RAISE EXCEPTION 'html budget session mismatch'; END IF;
 RETURN NEW;
END;
$body$;
CREATE FUNCTION public.html_preview_session_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'html sessions retained'; END IF;
 IF TG_OP='INSERT' THEN
  IF NEW.state<>'reserved' OR NEW.cid IS NOT NULL OR NEW.elapsed_seconds IS NOT NULL
   OR NOT public.html_artifact_eligible(NEW.activity_id,NEW.artifact_id) THEN RAISE EXCEPTION 'html start qualification'; END IF;
 ELSE
  IF (to_jsonb(NEW)-ARRAY['cid','state','elapsed_seconds','first_stop_receipt','confirmation_receipt','revision']) IS DISTINCT FROM
    (to_jsonb(OLD)-ARRAY['cid','state','elapsed_seconds','first_stop_receipt','confirmation_receipt','revision'])
    OR NEW.revision<>OLD.revision+1 OR (OLD.cid IS NOT NULL AND NEW.cid IS DISTINCT FROM OLD.cid)
    OR (OLD.first_stop_receipt IS NOT NULL AND NEW.first_stop_receipt IS DISTINCT FROM OLD.first_stop_receipt)
    OR (OLD.confirmation_receipt IS NOT NULL AND NEW.confirmation_receipt IS DISTINCT FROM OLD.confirmation_receipt)
    OR (OLD.elapsed_seconds IS NOT NULL AND NEW.elapsed_seconds IS DISTINCT FROM OLD.elapsed_seconds)
    OR OLD.state IN ('stopped','failed_unstarted')
  THEN RAISE EXCEPTION 'html session identity immutable'; END IF;
  IF NEW.state<>OLD.state AND NOT(
   OLD.state='reserved' AND NEW.state IN ('registered','failed_unstarted','cleanup_unconfirmed')
   OR OLD.state='registered' AND NEW.state IN ('start_requested','failed_unstarted','cleanup_unconfirmed')
   OR OLD.state='start_requested' AND NEW.state IN ('ready','stopping','cleanup_unconfirmed')
   OR OLD.state='ready' AND NEW.state IN ('running','stopping','cleanup_unconfirmed')
   OR OLD.state='running' AND NEW.state IN ('stopping','cleanup_unconfirmed')
   OR OLD.state='stopping' AND NEW.state IN ('stopped','cleanup_unconfirmed')
   OR OLD.state='cleanup_unconfirmed' AND NEW.state IN ('stopped','failed_unstarted'))
  THEN RAISE EXCEPTION 'html session transition'; END IF;
  IF NEW.state IN ('stopped','failed_unstarted') AND (NEW.confirmation_receipt IS NULL
    OR COALESCE(NEW.confirmation_receipt::jsonb->>'tree_confirmation','') NOT IN ('private_pid_init_terminated','never_started'))
  THEN RAISE EXCEPTION 'html tree proof missing'; END IF;
 END IF;
 RETURN NEW;
END;
$body$;
CREATE TRIGGER html_command_identity BEFORE INSERT OR UPDATE OR DELETE ON public.html_commands FOR EACH ROW EXECUTE FUNCTION public.html_command_guard();
CREATE TRIGGER html_artifact_insert BEFORE INSERT ON public.html_artifacts FOR EACH ROW EXECUTE FUNCTION public.html_artifact_insert_guard();
CREATE TRIGGER html_artifact_immutable BEFORE UPDATE OR DELETE ON public.html_artifacts FOR EACH ROW EXECUTE FUNCTION public.html_immutable_guard();
CREATE TRIGGER html_budget_identity BEFORE INSERT OR UPDATE OR DELETE ON public.html_preview_budgets FOR EACH ROW EXECUTE FUNCTION public.html_preview_budget_guard();
CREATE TRIGGER html_session_identity BEFORE INSERT OR UPDATE OR DELETE ON public.html_preview_sessions FOR EACH ROW EXECUTE FUNCTION public.html_preview_session_guard();

-- app只能调用有限producer，不能通过直接DML伪造产物或预算/停止收据。
CREATE FUNCTION public.html_accept_command(aid uuid, key uuid, op text, rb text, rh text, cb text, ch text,
 renderer text, scope integer, pk text, loc text, ph text) RETURNS void
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
 INSERT INTO public.html_commands(activity_id,business_key,operation_id,request_body,request_sha256,context_body,context_sha256,
 renderer_sha256,scope_revision,parent_kind,parent_locator,parent_sha256) VALUES(aid,key,op,rb,rh,cb,ch,renderer,scope,pk,loc,ph)
$body$;
CREATE FUNCTION public.html_claim_command(aid uuid, key uuid) RETURNS boolean
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN UPDATE public.html_commands SET status='launch_claimed',updated_at=CURRENT_TIMESTAMP WHERE activity_id=aid AND business_key=key AND status='accepted'; RETURN FOUND; END;
$body$;
CREATE FUNCTION public.html_commit_artifact(aid uuid, key uuid, art uuid, op text, body text, ah text, dh text, rh text, eh text, bh text) RETURNS void
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
 INSERT INTO public.html_artifacts(artifact_id,activity_id,business_key,operation_id,artifact_body,artifact_sha256,
 description_sha256,renderer_sha256,execution_package_sha256,body_sha256) VALUES(art,aid,key,op,body,ah,dh,rh,eh,bh)
$body$;
CREATE FUNCTION public.html_finish_command(aid uuid,key uuid,disposition text,error text) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN
 IF disposition='succeeded' AND NOT EXISTS(SELECT 1 FROM public.html_artifacts WHERE activity_id=aid AND business_key=key)
 THEN RAISE EXCEPTION 'html missing committed artifact'; END IF;
 UPDATE public.html_commands SET status='terminal',terminal_disposition=disposition,error_code=error,updated_at=CURRENT_TIMESTAMP
 WHERE activity_id=aid AND business_key=key AND status='launch_claimed';
END;
$body$;
CREATE FUNCTION public.html_reserve_preview(aid uuid, art uuid, pid uuid, sk uuid, ah text, owner uuid, oh text, auth text,
 boot uuid, nn text, image text, reserve integer, t0 bigint, wall timestamptz, conf text) RETURNS integer
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE b public.html_preview_budgets; gen integer;
BEGIN
 -- 已有预算不能先触发INSERT守卫再靠ON CONFLICT跳过；其会核已有session总数。
 INSERT INTO public.html_preview_budgets(activity_id,config_sha256)
 SELECT aid,conf WHERE NOT EXISTS(SELECT 1 FROM public.html_preview_budgets WHERE activity_id=aid)
 ON CONFLICT(activity_id) DO NOTHING;
 SELECT * INTO b FROM public.html_preview_budgets WHERE activity_id=aid FOR UPDATE;
 IF b.starts_used>=3 OR reserve<30 OR reserve>60 OR b.settled_seconds+b.reserved_seconds+reserve>180
   OR b.config_sha256<>conf OR EXISTS(SELECT 1 FROM public.html_preview_sessions WHERE activity_id=aid AND elapsed_seconds IS NULL)
 THEN RAISE EXCEPTION 'html preview budget or owner unavailable'; END IF;
 SELECT COALESCE(max(generation),0)+1 INTO gen FROM public.html_preview_sessions WHERE activity_id=aid;
 INSERT INTO public.html_preview_sessions(preview_id,activity_id,artifact_id,start_key,generation,artifact_sha256,owner_id,
 owner_key_sha256,control_key_sha256,boot_id,nonce,image_id,reserve_seconds,t0_ns,deadline_ns,deadline_at,state)
 VALUES(pid,aid,art,sk,gen,ah,owner,oh,auth,boot,nn,image,reserve,t0,t0+reserve::bigint*1000000000,wall,'reserved');
 UPDATE public.html_preview_budgets SET starts_used=starts_used+1,reserved_seconds=reserved_seconds+reserve,revision=revision+1 WHERE activity_id=aid;
 RETURN gen;
END;
$body$;
CREATE FUNCTION public.html_update_preview(pid uuid, auth text, next_state text, exact_cid text, first_receipt text,
 confirmation text, elapsed integer) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE s public.html_preview_sessions;
BEGIN
 SELECT * INTO s FROM public.html_preview_sessions WHERE preview_id=pid FOR UPDATE;
 IF s.preview_id IS NULL OR encode(sha256(decode(auth,'hex')),'hex')<>s.control_key_sha256 THEN RAISE EXCEPTION 'html control authority invalid'; END IF;
 UPDATE public.html_preview_sessions SET state=next_state,cid=COALESCE(exact_cid,cid),
 first_stop_receipt=COALESCE(first_stop_receipt,first_receipt),confirmation_receipt=COALESCE(confirmation_receipt,confirmation),
 elapsed_seconds=COALESCE(elapsed_seconds,elapsed),revision=revision+1 WHERE preview_id=pid;
 IF elapsed IS NOT NULL AND s.elapsed_seconds IS NULL THEN
  UPDATE public.html_preview_budgets SET reserved_seconds=reserved_seconds-s.reserve_seconds,
   settled_seconds=settled_seconds+elapsed,revision=revision+1 WHERE activity_id=s.activity_id;
 END IF;
END;
$body$;

DO $rights$
DECLARE r record;
BEGIN
 FOR r IN SELECT unnest(ARRAY['html_commands','html_artifacts','html_preview_budgets','html_preview_sessions']) AS name LOOP
  EXECUTE format('ALTER TABLE public.%I OWNER TO retrolume_html_owner',r.name);
  EXECUTE format('REVOKE ALL ON public.%I FROM PUBLIC,retrolume_html_app',r.name);
  EXECUTE format('GRANT SELECT ON public.%I TO retrolume_html_app',r.name);
 END LOOP;
 FOR r IN SELECT p.oid::regprocedure AS name FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname='public' AND p.proname LIKE 'html_%' LOOP
  EXECUTE format('ALTER FUNCTION %s OWNER TO retrolume_html_owner',r.name);
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.name);
  IF r.name::text NOT LIKE '%guard(%' THEN EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO retrolume_html_app',r.name); END IF;
 END LOOP;
END;
$rights$;
GRANT USAGE ON SCHEMA public TO retrolume_html_owner,retrolume_html_app;
GRANT SELECT ON public.activities,public.activity_scope_sources,public.material_sources,public.material_versions,
 public.activity_operations,public.activity_operation_results,public.teaching_heads,public.teaching_records,
 public.teaching_commands,public.activity_memory_bindings,public.activity_memory_choices,public.learning_memories,
 public.learning_memory_revisions,public.learning_memory_dependencies,public.learning_memory_bodies TO retrolume_html_owner;
GRANT EXECUTE ON FUNCTION public.activity_memory_eligible(uuid) TO retrolume_html_owner;
-- 记忆资格只读取PDF核对状态和页数，不取得正文或写入权。
GRANT SELECT (id, version_id, status, page_count) ON public.pdf_review_candidates TO retrolume_html_owner;
GRANT SELECT (candidate_id) ON public.pdf_review_pages TO retrolume_html_owner;
GRANT SELECT (version_id) ON public.pdf_extracted_pages TO retrolume_html_owner;
GRANT EXECUTE ON FUNCTION public.memory_scope_digest(uuid),public.memory_choice_digest(uuid),
 public.memory_revision_eligible(uuid,integer),public.memory_revision_readable(uuid,integer),
 public.memory_dependency_digest(uuid,integer),public.memory_dependency_line(public.learning_memory_dependencies) TO retrolume_html_owner;
COMMIT;
