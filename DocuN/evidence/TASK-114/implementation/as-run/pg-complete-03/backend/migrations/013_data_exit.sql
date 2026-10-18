-- STEP017-P1，可信安装器一次安装；不自动迁移已有用户库。
BEGIN;
CREATE ROLE retrolume_data_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE retrolume_data_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE retrolume_data_snapshot NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE retrolume_data_restore_loader NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

CREATE TABLE public.data_control (
 singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),
 dataset_id uuid NOT NULL, instance_id uuid NOT NULL UNIQUE,
 schema_profile text NOT NULL CHECK(schema_profile='data_exit.v1.r01'),
 mode text NOT NULL CHECK(mode IN('normal','loading','frozen','restored_readonly')),
 source_snapshot_id uuid, source_root_sha256 text,
 restore_manifest_sha256 text, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 originals_root_id uuid NOT NULL, reference_epoch bigint NOT NULL DEFAULT 0 CHECK(reference_epoch>=0),
 loader_session_user name, maintenance_key_sha256 text NOT NULL CHECK(maintenance_key_sha256~'^[0-9a-f]{64}$'),
 CHECK(mode<>'loading' OR (loader_session_user IS NOT NULL AND source_snapshot_id IS NOT NULL))
);
CREATE TABLE public.data_operation_jobs (
 id uuid PRIMARY KEY, record_class text NOT NULL CHECK(record_class IN('hub_observation','reference_fence','archive_history')),
 origin_source_row_id uuid, business_key text, kind text NOT NULL,
 request_sha256 text CHECK(request_sha256 IS NULL OR request_sha256~'^[0-9a-f]{64}$'),
 observed_state text NOT NULL, observed_stage text, control_seq_observed bigint,
 package_id uuid, root_sha256 text, counts jsonb NOT NULL DEFAULT '{}', error_code text,
 created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 terminal_at timestamptz, scope_summary jsonb NOT NULL DEFAULT '{}',
 authorizes_reference boolean NOT NULL DEFAULT false,
 prepared_source_id uuid, prepared_version_id uuid, prepared_candidate_id uuid,
 original_sha256 text, original_size bigint, originals_root_id uuid, reference_epoch bigint,
 pin_nonce_sha256 text, owner_session_user name,
 CHECK((record_class='reference_fence' AND authorizes_reference AND
   prepared_source_id IS NOT NULL AND prepared_version_id IS NOT NULL AND original_sha256~'^[0-9a-f]{64}$'
   AND original_size BETWEEN 0 AND 5242880 AND originals_root_id IS NOT NULL AND reference_epoch IS NOT NULL
   AND pin_nonce_sha256~'^[0-9a-f]{64}$' AND owner_session_user IS NOT NULL
   AND observed_state IN('open','committed','rejected','ambiguous','cancelled'))
   OR(record_class<>'reference_fence' AND NOT authorizes_reference AND pin_nonce_sha256 IS NULL AND owner_session_user IS NULL)),
 CHECK(record_class<>'archive_history' OR observed_state='archive_only')
);
CREATE INDEX data_reference_prepared ON public.data_operation_jobs(prepared_source_id,prepared_version_id) WHERE record_class='reference_fence';
CREATE TABLE public.data_tombstones (
 tombstone_id uuid PRIMARY KEY, entity_kind text NOT NULL CHECK(entity_kind IN('source','memory')),
 entity_id uuid NOT NULL, effective_revision integer NOT NULL CHECK(effective_revision>0),
 business_id_observed text NOT NULL, deleted_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 cleanup_state_observed text NOT NULL CHECK(cleanup_state_observed IN('pending','done','shared_retained','physical_result_unknown','archive_observation')),
 manifest_sha256 text NOT NULL CHECK(manifest_sha256~'^[0-9a-f]{64}$'),
 hash_size_targets jsonb NOT NULL CHECK(jsonb_typeof(hash_size_targets)='array'),
 UNIQUE(entity_kind,entity_id,effective_revision)
);
ALTER TABLE public.data_control OWNER TO retrolume_data_owner;
ALTER TABLE public.data_operation_jobs OWNER TO retrolume_data_owner;
ALTER TABLE public.data_tombstones OWNER TO retrolume_data_owner;
REVOKE ALL ON public.data_control,public.data_operation_jobs,public.data_tombstones FROM PUBLIC;

CREATE VIEW public.data_export_control_v1 WITH(security_invoker=true) AS SELECT
 dataset_id,schema_profile,created_at,instance_id AS source_instance_observed,mode AS mode_observed,
 source_snapshot_id,source_root_sha256 FROM public.data_control;
CREATE VIEW public.data_export_job_history_v1 WITH(security_invoker=true) AS SELECT
 id AS origin_source_row_id,record_class,business_key,kind,request_sha256,observed_state,observed_stage,
 control_seq_observed,package_id,root_sha256,counts,error_code,created_at,updated_at,terminal_at,scope_summary,
 origin_source_row_id AS archive_origin_source_row_id FROM public.data_operation_jobs;
CREATE VIEW public.data_export_tombstones_v1 WITH(security_invoker=true) AS SELECT
 tombstone_id,entity_kind,entity_id,effective_revision,business_id_observed,deleted_at,
 cleanup_state_observed,manifest_sha256,hash_size_targets FROM public.data_tombstones;
ALTER VIEW public.data_export_control_v1 OWNER TO retrolume_data_owner;
ALTER VIEW public.data_export_job_history_v1 OWNER TO retrolume_data_owner;
ALTER VIEW public.data_export_tombstones_v1 OWNER TO retrolume_data_owner;
GRANT SELECT ON public.data_export_control_v1,public.data_export_job_history_v1,public.data_export_tombstones_v1
 TO retrolume_data_snapshot,retrolume_data_app,retrolume_data_restore_loader;
GRANT SELECT(dataset_id,schema_profile,created_at,instance_id,mode,source_snapshot_id,source_root_sha256)
 ON public.data_control TO retrolume_data_snapshot,retrolume_data_app,retrolume_data_restore_loader;
GRANT SELECT(id,record_class,business_key,kind,request_sha256,observed_state,observed_stage,control_seq_observed,
 package_id,root_sha256,counts,error_code,created_at,updated_at,terminal_at,scope_summary,origin_source_row_id)
 ON public.data_operation_jobs TO retrolume_data_snapshot,retrolume_data_app,retrolume_data_restore_loader;
GRANT SELECT ON public.data_tombstones TO retrolume_data_snapshot,retrolume_data_app,retrolume_data_restore_loader;

CREATE FUNCTION public.data_loading_allowed() RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
 SELECT EXISTS(SELECT 1 FROM public.data_control WHERE mode='loading' AND loader_session_user=SESSION_USER
 AND source_snapshot_id IS NOT NULL AND pg_has_role(SESSION_USER,'retrolume_data_restore_loader','member'))
$f$;
CREATE FUNCTION public.data_runtime_write_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE m text;rid uuid;
BEGIN
 SELECT originals_root_id INTO rid FROM public.data_control;
 PERFORM pg_advisory_xact_lock_shared(hashtextextended(rid::text,113));
 SELECT mode INTO m FROM public.data_control;
 IF m='loading' AND public.data_loading_allowed() AND
   (TG_OP='INSERT' OR(TG_TABLE_NAME='material_sources' AND TG_OP='UPDATE'
      AND (to_jsonb(NEW)-'current_version')=(to_jsonb(OLD)-'current_version'))) THEN RETURN NEW; END IF;
 IF m IS DISTINCT FROM 'normal' THEN RAISE EXCEPTION 'data_runtime_readonly' USING ERRCODE='42501'; END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $f$;
CREATE FUNCTION public.data_mutation_enter() RETURNS void LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE c public.data_control;
BEGIN
 SELECT * INTO c FROM public.data_control;
 PERFORM pg_advisory_xact_lock_shared(hashtextextended(c.originals_root_id::text,113));
 SELECT * INTO c FROM public.data_control;
 IF c.dataset_id IS NULL OR c.mode<>'normal' THEN RAISE EXCEPTION 'data_runtime_readonly' USING ERRCODE='42501'; END IF;
END $f$;
CREATE FUNCTION public.data_state() RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
 SELECT jsonb_build_object('dataset_id',dataset_id,'instance_id',instance_id,'mode',mode,
 'schema_profile',schema_profile,'originals_root_id',originals_root_id,'reference_epoch',reference_epoch)
 FROM public.data_control
$f$;
CREATE FUNCTION public.data_reference_begin(tid uuid,sid uuid,vid uuid,cid uuid,sha text,bytes bigint,rid uuid,nonce text,maintenance_key text)
 RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE c public.data_control;
BEGIN
 PERFORM pg_advisory_xact_lock_shared(hashtextextended(rid::text,113));
 SELECT * INTO c FROM public.data_control FOR SHARE;
 IF c.dataset_id IS NULL OR maintenance_key IS NULL OR c.maintenance_key_sha256<>encode(sha256(convert_to(maintenance_key,'UTF8')),'hex')
 OR c.mode<>'normal' OR c.originals_root_id<>rid OR nonce IS NULL OR length(nonce)<>64
 OR EXISTS(SELECT 1 FROM public.data_tombstones WHERE entity_kind='source' AND entity_id=sid)
 THEN RAISE EXCEPTION 'reference_not_admitted' USING ERRCODE='42501'; END IF;
 INSERT INTO public.data_operation_jobs(id,record_class,kind,observed_state,authorizes_reference,
 prepared_source_id,prepared_version_id,prepared_candidate_id,original_sha256,original_size,
 originals_root_id,reference_epoch,pin_nonce_sha256,owner_session_user)
 VALUES(tid,'reference_fence','original_reference','open',true,sid,vid,cid,sha,bytes,rid,c.reference_epoch,
 encode(sha256(convert_to(nonce,'UTF8')),'hex'),SESSION_USER);
 RETURN c.reference_epoch;
END $f$;
CREATE FUNCTION public.data_reference_bind(tid uuid,nonce text) RETURNS void LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE j public.data_operation_jobs; c public.data_control;
BEGIN
 SELECT * INTO c FROM public.data_control;
 PERFORM pg_advisory_xact_lock_shared(hashtextextended(c.originals_root_id::text,113));
 SELECT * INTO c FROM public.data_control;
 SELECT * INTO j FROM public.data_operation_jobs WHERE id=tid FOR UPDATE;
 IF c.dataset_id IS NULL OR j.id IS NULL OR nonce IS NULL OR c.mode<>'normal' OR j.record_class<>'reference_fence' OR j.observed_state<>'open'
 OR NOT j.authorizes_reference OR j.owner_session_user<>SESSION_USER OR j.originals_root_id<>c.originals_root_id
 OR j.reference_epoch<>c.reference_epoch OR j.pin_nonce_sha256<>encode(sha256(convert_to(nonce,'UTF8')),'hex')
 OR EXISTS(SELECT 1 FROM public.data_tombstones WHERE entity_kind='source' AND entity_id=j.prepared_source_id)
 THEN RAISE EXCEPTION 'reference_ticket_invalid' USING ERRCODE='42501'; END IF;
 PERFORM set_config('retrolume.reference_id',tid::text,true);
 PERFORM set_config('retrolume.reference_nonce',nonce,true);
END $f$;
CREATE FUNCTION public.data_reference_commit(tid uuid,nonce text) RETURNS void LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 PERFORM public.data_reference_bind(tid,nonce);
 IF NOT EXISTS(SELECT 1 FROM public.material_versions v JOIN public.data_operation_jobs j ON j.id=tid
 WHERE v.id=j.prepared_version_id AND v.source_id=j.prepared_source_id AND v.sha256=j.original_sha256 AND v.size=j.original_size)
 THEN RAISE EXCEPTION 'reference_metadata_missing'; END IF;
 UPDATE public.data_operation_jobs SET observed_state='committed',updated_at=CURRENT_TIMESTAMP,terminal_at=CURRENT_TIMESTAMP WHERE id=tid;
END $f$;
CREATE FUNCTION public.data_reference_cancel_epoch(rid uuid,maintenance_key text) RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE c public.data_control;
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(rid::text,113));
 SELECT * INTO c FROM public.data_control FOR UPDATE;
 IF c.dataset_id IS NULL OR maintenance_key IS NULL OR c.mode<>'normal' OR c.originals_root_id<>rid OR c.maintenance_key_sha256<>encode(sha256(convert_to(maintenance_key,'UTF8')),'hex')
 THEN RAISE EXCEPTION 'cleanup_not_admitted' USING ERRCODE='42501'; END IF;
 UPDATE public.data_operation_jobs SET observed_state='cancelled',updated_at=CURRENT_TIMESTAMP,terminal_at=CURRENT_TIMESTAMP
 WHERE record_class='reference_fence' AND observed_state IN('open','ambiguous') AND originals_root_id=rid;
 UPDATE public.data_control SET reference_epoch=reference_epoch+1;
 RETURN c.reference_epoch+1;
END $f$;
CREATE FUNCTION public.data_material_reference_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE j public.data_operation_jobs; sid uuid; vid uuid;
BEGIN
 IF TG_TABLE_NAME='material_sources' THEN
  IF NEW.current_version IS NULL OR (TG_OP='UPDATE' AND NEW.current_version IS NOT DISTINCT FROM OLD.current_version) THEN RETURN NEW; END IF;
  sid=NEW.id; vid=NEW.current_version;
 ELSE sid=NEW.source_id; vid=NEW.id; END IF;
 IF public.data_loading_allowed() THEN RETURN NEW; END IF;
 IF EXISTS(SELECT 1 FROM public.data_tombstones WHERE entity_kind='source' AND entity_id=sid)
 THEN RAISE EXCEPTION 'source_deleted' USING ERRCODE='42501'; END IF;
 IF current_setting('retrolume.reference_id',true) IS NULL OR current_setting('retrolume.reference_id',true)=''
 THEN RAISE EXCEPTION 'reference_pin_required' USING ERRCODE='42501'; END IF;
 PERFORM public.data_reference_bind(current_setting('retrolume.reference_id')::uuid,current_setting('retrolume.reference_nonce'));
 SELECT * INTO j FROM public.data_operation_jobs WHERE id=current_setting('retrolume.reference_id')::uuid;
 IF j.prepared_source_id<>sid OR j.prepared_version_id<>vid OR
 (TG_TABLE_NAME='material_versions' AND (j.original_sha256<>NEW.sha256 OR j.original_size<>NEW.size))
 THEN RAISE EXCEPTION 'reference_identity_invalid'; END IF;
 RETURN NEW;
END $f$;
CREATE TRIGGER data_material_version_reference BEFORE INSERT ON public.material_versions
 FOR EACH ROW EXECUTE FUNCTION public.data_material_reference_guard();
CREATE TRIGGER data_material_pointer_reference BEFORE INSERT OR UPDATE ON public.material_sources
 FOR EACH ROW EXECUTE FUNCTION public.data_material_reference_guard();

CREATE FUNCTION public.data_source_delete(sid uuid,expected_revision integer,bkey text,impact_sha text,targets jsonb,maintenance_key text)
 RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE c public.data_control; s public.material_sources; t public.data_tombstones;
BEGIN
 SELECT * INTO c FROM public.data_control;
 PERFORM pg_advisory_xact_lock(hashtextextended(c.originals_root_id::text,113));
 IF c.dataset_id IS NULL OR maintenance_key IS NULL OR c.mode<>'normal' OR c.maintenance_key_sha256<>encode(sha256(convert_to(maintenance_key,'UTF8')),'hex')
 THEN RAISE EXCEPTION 'deletion_not_admitted' USING ERRCODE='42501'; END IF;
 SELECT * INTO s FROM public.material_sources WHERE id=sid FOR UPDATE;
 SELECT * INTO t FROM public.data_tombstones WHERE entity_kind='source' AND entity_id=sid;
 IF t.tombstone_id IS NOT NULL THEN
  IF t.business_id_observed<>bkey OR t.manifest_sha256<>impact_sha THEN RAISE EXCEPTION 'deletion_key_conflict'; END IF;
  RETURN to_jsonb(t);
 END IF;
 IF s.id IS NULL OR s.revision<>expected_revision OR jsonb_typeof(targets)<>'array'
 OR EXISTS(SELECT 1 FROM public.material_versions v WHERE v.source_id=sid AND NOT EXISTS(
 SELECT 1 FROM jsonb_array_elements(targets) x WHERE x->>'sha256'=v.sha256 AND (x->>'size')::bigint=v.size))
 OR EXISTS(SELECT 1 FROM jsonb_array_elements(targets) x WHERE NOT EXISTS(SELECT 1 FROM public.material_versions v
 WHERE v.source_id=sid AND v.sha256=x->>'sha256' AND v.size=(x->>'size')::bigint))
 THEN RAISE EXCEPTION 'deletion_impact_changed'; END IF;
 INSERT INTO public.data_tombstones(tombstone_id,entity_kind,entity_id,effective_revision,business_id_observed,
 cleanup_state_observed,manifest_sha256,hash_size_targets)
 VALUES(gen_random_uuid(),'source',sid,s.revision+1,bkey,'pending',impact_sha,targets) RETURNING * INTO t;
 UPDATE public.material_sources SET current_version=NULL,revision=revision+1 WHERE id=sid;
 RETURN to_jsonb(t);
END $f$;
CREATE FUNCTION public.data_control_frozen(did uuid,iid uuid,maintenance_key text) RETURNS void LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE rid uuid;
BEGIN
 SELECT originals_root_id INTO rid FROM public.data_control WHERE dataset_id=did AND instance_id=iid;
 PERFORM pg_advisory_xact_lock(hashtextextended(rid::text,113));
 UPDATE public.data_control SET mode='frozen' WHERE dataset_id=did AND instance_id=iid AND mode IN('normal','frozen')
 AND maintenance_key_sha256=encode(sha256(convert_to(maintenance_key,'UTF8')),'hex');
 IF NOT FOUND THEN RAISE EXCEPTION 'maintenance_identity_unknown' USING ERRCODE='42501'; END IF;
END $f$;
CREATE FUNCTION public.data_control_archive_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NOT public.data_loading_allowed() OR TG_OP<>'INSERT' THEN RAISE EXCEPTION 'archive_loading_only' USING ERRCODE='42501'; END IF;
 IF TG_TABLE_NAME='data_operation_jobs' AND (NEW.record_class<>'archive_history' OR NEW.authorizes_reference
 OR NEW.observed_state<>'archive_only' OR NEW.pin_nonce_sha256 IS NOT NULL OR NEW.owner_session_user IS NOT NULL)
 THEN RAISE EXCEPTION 'archive_not_authority'; END IF;
 RETURN NEW;
END $f$;
-- 归档加载走受限函数，源 runtime 不能授自己 loading。
CREATE FUNCTION public.data_archive_history(value jsonb) RETURNS void LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NOT public.data_loading_allowed() THEN RAISE EXCEPTION 'archive_loading_only' USING ERRCODE='42501'; END IF;
 INSERT INTO public.data_operation_jobs(id,record_class,origin_source_row_id,business_key,kind,request_sha256,
 observed_state,observed_stage,control_seq_observed,package_id,root_sha256,counts,error_code,created_at,updated_at,terminal_at,scope_summary)
 VALUES(gen_random_uuid(),'archive_history',(value->>'origin_source_row_id')::uuid,value->>'business_key',value->>'kind',value->>'request_sha256',
 'archive_only',value->>'observed_state',(value->>'control_seq_observed')::bigint,(value->>'package_id')::uuid,
 value->>'root_sha256',COALESCE(value->'counts','{}'),value->>'error_code',(value->>'created_at')::timestamptz,
 (value->>'updated_at')::timestamptz,(value->>'terminal_at')::timestamptz,COALESCE(value->'scope_summary','{}'));
END $f$;
CREATE FUNCTION public.data_archive_tombstone(value jsonb) RETURNS void LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NOT public.data_loading_allowed() THEN RAISE EXCEPTION 'archive_loading_only' USING ERRCODE='42501'; END IF;
 INSERT INTO public.data_tombstones SELECT * FROM jsonb_populate_record(NULL::public.data_tombstones,value)
 ON CONFLICT(entity_kind,entity_id,effective_revision) DO NOTHING;
END $f$;
CREATE FUNCTION public.data_observe_job(value jsonb) RETURNS void LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF (SELECT mode FROM public.data_control) IS DISTINCT FROM 'normal' THEN RAISE EXCEPTION 'source_not_normal'; END IF;
 INSERT INTO public.data_operation_jobs(id,record_class,business_key,kind,request_sha256,observed_state,observed_stage,
 control_seq_observed,package_id,root_sha256,counts,error_code)
 VALUES((value->>'job_id')::uuid,'hub_observation',value->>'business_key',value->>'kind',value->>'request_sha256',
 value->>'state',value->>'stage',(value->>'control_seq')::bigint,(value->>'package_id')::uuid,value->>'root_sha256',
 COALESCE(value->'counts','{}'),value->>'error_code') ON CONFLICT(id) DO UPDATE SET
 observed_state=EXCLUDED.observed_state,observed_stage=EXCLUDED.observed_stage,control_seq_observed=EXCLUDED.control_seq_observed,
 package_id=EXCLUDED.package_id,root_sha256=EXCLUDED.root_sha256,counts=EXCLUDED.counts,error_code=EXCLUDED.error_code,updated_at=CURRENT_TIMESTAMP
 WHERE data_operation_jobs.record_class='hub_observation';
END $f$;

CREATE FUNCTION public.data_tombstone_immutable() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF TG_OP='DELETE' OR current_user<>'retrolume_data_owner' OR
 (to_jsonb(NEW)-'cleanup_state_observed') IS DISTINCT FROM (to_jsonb(OLD)-'cleanup_state_observed')
 THEN RAISE EXCEPTION 'tombstone_history_immutable'; END IF;
 RETURN NEW;
END $f$;
CREATE TRIGGER data_tombstone_history BEFORE UPDATE OR DELETE ON public.data_tombstones
 FOR EACH ROW EXECUTE FUNCTION public.data_tombstone_immutable();
CREATE FUNCTION public.data_memory_tombstone() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE c public.learning_memory_commands; targets jsonb;
BEGIN
 IF NEW.state<>'revoked' OR (SELECT mode FROM public.data_control)<>'normal' THEN RETURN NULL; END IF;
 SELECT * INTO c FROM public.learning_memory_commands WHERE business_key=NEW.revocation_key AND action='revoke' AND effect_applied;
 IF c.business_key IS NULL OR c.manifest_sha256 IS NULL THEN RAISE EXCEPTION 'memory_tombstone_receipt_missing'; END IF;
 SELECT COALESCE(jsonb_agg(jsonb_build_object('sha256',body_sha256,'size',body_bytes::text) ORDER BY version),'[]')
 INTO targets FROM public.learning_memory_revisions WHERE memory_id=NEW.memory_id;
 INSERT INTO public.data_tombstones(tombstone_id,entity_kind,entity_id,effective_revision,business_id_observed,
 deleted_at,cleanup_state_observed,manifest_sha256,hash_size_targets)
 VALUES(gen_random_uuid(),'memory',NEW.memory_id,NEW.revision,NEW.revocation_key::text,NEW.revoked_at,
 CASE WHEN NEW.purge_state='done' THEN 'done' ELSE 'pending' END,c.manifest_sha256,targets)
 ON CONFLICT(entity_kind,entity_id,effective_revision) DO UPDATE SET cleanup_state_observed=EXCLUDED.cleanup_state_observed;
 RETURN NULL;
END $f$;
CREATE TRIGGER data_memory_deletion_observation AFTER UPDATE ON public.learning_memories
 FOR EACH ROW EXECUTE FUNCTION public.data_memory_tombstone();
CREATE FUNCTION public.data_cleanup_observe(tid uuid,manifest_sha text,results jsonb,maintenance_key text) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE t public.data_tombstones; state text;
BEGIN
 IF maintenance_key IS NULL OR (SELECT maintenance_key_sha256 FROM public.data_control) IS DISTINCT FROM encode(sha256(convert_to(maintenance_key,'UTF8')),'hex')
 OR (SELECT mode FROM public.data_control) IS DISTINCT FROM 'normal' THEN RAISE EXCEPTION 'cleanup_observation_denied'; END IF;
 SELECT * INTO t FROM public.data_tombstones WHERE tombstone_id=tid FOR UPDATE;
 IF t.tombstone_id IS NULL OR manifest_sha IS NULL OR results IS NULL OR t.manifest_sha256<>manifest_sha OR jsonb_array_length(results)<>jsonb_array_length(t.hash_size_targets)
 OR EXISTS(SELECT 1 FROM jsonb_array_elements(t.hash_size_targets) x WHERE NOT EXISTS(SELECT 1 FROM jsonb_array_elements(results) r
 WHERE r->>'sha256'=x->>'sha256' AND r->>'size'=x->>'size')) THEN RAISE EXCEPTION 'cleanup_observation_identity'; END IF;
 IF EXISTS(SELECT 1 FROM jsonb_array_elements(results) r WHERE r->>'state' NOT IN('done','shared_retained','physical_result_unknown'))
 THEN RAISE EXCEPTION 'cleanup_observation_state'; END IF;
 state=CASE WHEN EXISTS(SELECT 1 FROM jsonb_array_elements(results) r WHERE r->>'state'='physical_result_unknown') THEN 'physical_result_unknown'
 WHEN EXISTS(SELECT 1 FROM jsonb_array_elements(results) r WHERE r->>'state'='shared_retained') THEN 'shared_retained' ELSE 'done' END;
 UPDATE public.data_tombstones SET cleanup_state_observed=state WHERE tombstone_id=tid;
END $f$;
GRANT EXECUTE ON FUNCTION public.data_cleanup_observe(uuid,text,jsonb,text) TO retrolume_data_app;

DO $acl$
DECLARE r record;
BEGIN
 FOR r IN SELECT p.oid::regprocedure AS name FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='public' AND p.proname LIKE 'data_%' LOOP
  EXECUTE format('ALTER FUNCTION %s OWNER TO retrolume_data_owner',r.name);
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.name);
 END LOOP;
END $acl$;
GRANT EXECUTE ON FUNCTION public.data_loading_allowed() TO retrolume_memory_owner,retrolume_memory_app,
 retrolume_memory_purger,retrolume_interview_owner,retrolume_html_owner,retrolume_data_restore_loader;
GRANT EXECUTE ON FUNCTION public.data_state() TO retrolume_data_app,retrolume_data_restore_loader;
GRANT EXECUTE ON FUNCTION public.data_mutation_enter() TO retrolume_data_app;
GRANT EXECUTE ON FUNCTION public.data_reference_begin(uuid,uuid,uuid,uuid,text,bigint,uuid,text,text),
 public.data_reference_bind(uuid,text),public.data_reference_commit(uuid,text),public.data_reference_cancel_epoch(uuid,text),
 public.data_source_delete(uuid,integer,text,text,jsonb,text),public.data_control_frozen(uuid,uuid,text),public.data_observe_job(jsonb)
 TO retrolume_data_app;
GRANT UPDATE(current_version,revision) ON public.material_sources TO retrolume_data_owner;
GRANT EXECUTE ON FUNCTION public.data_archive_history(jsonb),public.data_archive_tombstone(jsonb)
 TO retrolume_data_restore_loader;
GRANT SELECT,INSERT,UPDATE ON public.material_sources,public.material_versions,public.pdf_review_candidates,
 public.pdf_extracted_pages,public.pdf_review_pages,public.pdf_user_supplements,public.activities,
 public.activity_scope_sources,public.activity_allowed_models,public.activity_operations,
 public.activity_operation_results,public.teaching_commands,public.teaching_records,public.teaching_heads
 TO retrolume_data_app;
GRANT UPDATE(current_version,revision) ON public.material_sources TO retrolume_data_owner;

-- 教学循环只延后两条指定外键，日常事务仍即时检查。
DO $fk$
DECLARE r record; matched integer=0;
BEGIN
 FOR r IN SELECT k.conname,array_agg(a.attname ORDER BY x.ordinality) AS cols FROM pg_constraint k
 JOIN unnest(k.conkey) WITH ORDINALITY x(attnum,ordinality) ON true
 JOIN pg_attribute a ON a.attrelid=k.conrelid AND a.attnum=x.attnum
 WHERE k.conrelid='public.teaching_commands'::regclass AND k.contype='f' GROUP BY k.conname LOOP
  IF 'parent_record_id'=ANY(r.cols) OR 'result_record_id'=ANY(r.cols) THEN
   EXECUTE format('ALTER TABLE public.teaching_commands ALTER CONSTRAINT %I DEFERRABLE INITIALLY IMMEDIATE',r.conname);
   matched=matched+1;
  END IF;
 END LOOP;
 IF matched<>2 THEN RAISE EXCEPTION 'teaching FK identity mismatch'; END IF;
END $fk$;

-- 下方固定加载分支及逐列 ACL 由项目内受信生成器冻结，不读取数据包定义。
CREATE OR REPLACE FUNCTION public.memory_head_guard() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE ok BOOLEAN;
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION '记忆头不可直接删除'; END IF;
 IF TG_OP='INSERT' THEN
  IF NOT public.data_loading_allowed() AND (NEW.revision<>1 OR NEW.current_version<>1 OR NEW.state<>'active') THEN RAISE EXCEPTION '记忆初始身份不符'; END IF;
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

CREATE OR REPLACE FUNCTION public.memory_body_guard() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE h record; r record; value JSONB;
BEGIN
 IF TG_OP='UPDATE' THEN RAISE EXCEPTION '记忆正文不可覆盖'; END IF;
 IF TG_OP='DELETE' THEN
  IF current_user<>'retrolume_memory_purger' THEN RAISE EXCEPTION '只可用获准精确清理函数'; END IF;
  RETURN OLD;
 END IF;
 SELECT state,current_version INTO h FROM public.learning_memories WHERE memory_id=NEW.memory_id FOR KEY SHARE;
 IF NOT public.data_loading_allowed() AND (h.state IS DISTINCT FROM 'active' OR NEW.version NOT IN(h.current_version,h.current_version+1)) THEN
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

CREATE OR REPLACE FUNCTION public.interview_command_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'interview commands retained'; END IF;
 IF TG_OP='INSERT' THEN
  IF (SELECT count(*) FROM public.interview_commands WHERE activity_id=NEW.activity_id)>=4096 THEN RAISE EXCEPTION 'interview command limit'; END IF;
  IF NOT public.data_loading_allowed() AND (NEW.effect_applied OR NEW.launch_claimed) THEN RAISE EXCEPTION 'no pre-applied command'; END IF;
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

CREATE OR REPLACE FUNCTION public.interview_record_insert_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE c public.interview_commands; p public.interview_records; r public.activity_operation_results; o public.activity_operations; b jsonb; ref jsonb;
BEGIN
 SELECT * INTO c FROM public.interview_commands WHERE activity_id=NEW.activity_id AND business_key=NEW.business_key;
 IF c.activity_id IS NULL OR c.duplicate_of IS NOT NULL OR (NOT public.data_loading_allowed() AND (c.effect_applied OR c.status NOT IN ('accepted','started')))
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
  IF c.execution_kind<>'model' OR c.operation_id<>NEW.operation_id OR (NOT public.data_loading_allowed() AND (NOT c.launch_claimed OR c.obsolete OR c.status<>'started'))
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

CREATE OR REPLACE FUNCTION public.interview_head_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE a public.activities; ptr uuid; p public.interview_records;
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'interview heads retained'; END IF;
 SELECT * INTO a FROM public.activities WHERE id=NEW.activity_id;
 IF TG_OP='INSERT' THEN
  IF NOT public.data_loading_allowed() AND (a.status<>'pending' OR a.execution_generation<>0 OR a.executor_id IS NOT NULL OR a.lease_expires_at IS NOT NULL
     OR a.requests_reserved<>0 OR a.cost_reserved_microunits<>0 OR a.tools_reserved<>0 OR a.running_reserved_seconds<>0 OR a.running_settled_seconds<>0
     OR EXISTS(SELECT 1 FROM public.teaching_heads WHERE activity_id=NEW.activity_id)
     OR EXISTS(SELECT 1 FROM public.activity_operations WHERE activity_id=NEW.activity_id)
     OR EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=NEW.activity_id)
     OR NEW.revision<>1) THEN RAISE EXCEPTION 'interview requires fresh unselected activity'; END IF;
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

CREATE OR REPLACE FUNCTION public.html_command_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'html commands retained'; END IF;
 IF NEW.renderer_sha256<>public.html_expected_renderer() OR NEW.context_body::jsonb->>'schema'<>'html.context.v2'
  OR NEW.context_body::jsonb->>'activity_id'<>NEW.activity_id::text OR NEW.context_body::jsonb->>'business_key'<>NEW.business_key::text
  OR NEW.context_body::jsonb->>'request_sha256'<>NEW.request_sha256 THEN RAISE EXCEPTION 'html command binding'; END IF;
 IF TG_OP='INSERT' THEN
  IF (NOT public.data_loading_allowed() AND NEW.status<>'accepted') OR (SELECT count(*) FROM public.html_commands WHERE activity_id=NEW.activity_id)>=4096
   OR (NOT public.data_loading_allowed() AND NOT public.html_parent_eligible(NEW.activity_id,NEW.context_body::jsonb)) THEN RAISE EXCEPTION 'html command ineligible'; END IF;
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

CREATE OR REPLACE FUNCTION public.html_artifact_insert_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE c public.html_commands; r public.activity_operation_results; o public.activity_operations; b jsonb;
BEGIN
 SELECT * INTO c FROM public.html_commands WHERE activity_id=NEW.activity_id AND business_key=NEW.business_key;
 SELECT * INTO r FROM public.activity_operation_results WHERE activity_id=NEW.activity_id AND operation_id=NEW.operation_id;
 SELECT * INTO o FROM public.activity_operations WHERE activity_id=NEW.activity_id AND operation_id=NEW.operation_id;
 b:=NEW.artifact_body::jsonb;
 IF c.activity_id IS NULL OR (NOT public.data_loading_allowed() AND c.status<>'launch_claimed') OR c.operation_id<>NEW.operation_id
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
   OR (NOT public.data_loading_allowed() AND NOT public.html_parent_eligible(NEW.activity_id,c.context_body::jsonb))
   THEN RAISE EXCEPTION 'html artifact integrity or qualification'; END IF;
 RETURN NEW;
END;
$body$;

CREATE OR REPLACE FUNCTION public.html_preview_budget_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
DECLARE used integer; settled integer; reserved integer;
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'html budgets retained'; END IF;
 IF TG_OP='UPDATE' AND ((to_jsonb(NEW)-ARRAY['starts_used','settled_seconds','reserved_seconds','revision'])
    IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['starts_used','settled_seconds','reserved_seconds','revision'])
    OR NEW.revision<>OLD.revision+1 OR NEW.starts_used<OLD.starts_used OR NEW.settled_seconds<OLD.settled_seconds)
    THEN RAISE EXCEPTION 'html budget identity or monotonicity'; END IF;
 SELECT count(*),COALESCE(sum(elapsed_seconds),0),COALESCE(sum(CASE WHEN elapsed_seconds IS NULL THEN reserve_seconds ELSE 0 END),0)
 INTO used,settled,reserved FROM public.html_preview_sessions WHERE activity_id=NEW.activity_id;
 IF NOT (TG_OP='INSERT' AND public.data_loading_allowed()) AND (NEW.starts_used<>used OR NEW.settled_seconds<>settled OR NEW.reserved_seconds<>reserved)
 THEN RAISE EXCEPTION 'html budget session mismatch'; END IF;
 RETURN NEW;
END;
$body$;

CREATE OR REPLACE FUNCTION public.html_preview_session_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'html sessions retained'; END IF;
 IF TG_OP='INSERT' THEN
  IF NOT public.data_loading_allowed() AND (NEW.state<>'reserved' OR NEW.cid IS NOT NULL OR NEW.elapsed_seconds IS NOT NULL
   OR NOT public.html_artifact_eligible(NEW.activity_id,NEW.artifact_id)) THEN RAISE EXCEPTION 'html start qualification'; END IF;
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


CREATE FUNCTION public.data_restore_final_shape() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE aid uuid;
BEGIN
 IF NOT public.data_loading_allowed() THEN RETURN NULL; END IF;
 aid=NEW.activity_id;
 IF EXISTS(SELECT 1 FROM public.html_preview_budgets b WHERE b.activity_id=aid AND
 (b.starts_used<>(SELECT count(*) FROM public.html_preview_sessions s WHERE s.activity_id=aid)
 OR b.settled_seconds<>(SELECT COALESCE(sum(elapsed_seconds),0) FROM public.html_preview_sessions s WHERE s.activity_id=aid)
 OR b.reserved_seconds<>(SELECT COALESCE(sum(reserve_seconds) FILTER(WHERE elapsed_seconds IS NULL),0) FROM public.html_preview_sessions s WHERE s.activity_id=aid)))
 THEN RAISE EXCEPTION 'archive_preview_budget_mismatch'; END IF;
 RETURN NULL;
END $f$;
ALTER FUNCTION public.data_restore_final_shape() OWNER TO retrolume_data_owner;
REVOKE ALL ON FUNCTION public.data_restore_final_shape() FROM PUBLIC;
CREATE CONSTRAINT TRIGGER data_restore_budget_shape AFTER INSERT ON public.html_preview_budgets
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION public.data_restore_final_shape();
CREATE CONSTRAINT TRIGGER data_restore_session_shape AFTER INSERT ON public.html_preview_sessions
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION public.data_restore_final_shape();


GRANT SELECT(id,title,current_version,revision) ON public.material_sources TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.material_sources TO retrolume_data_restore_loader;

GRANT SELECT ON public.material_sources TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.material_sources FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(id,source_id,filename,format,sha256,size,created_at) ON public.material_versions TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.material_versions TO retrolume_data_restore_loader;

GRANT SELECT ON public.material_versions TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.material_versions FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(id,status,scope_revision,execution_generation,lease_expires_at,deadline_at,max_requests,requests_reserved,max_cost_microunits,cost_reserved_microunits,reserve_cost_microunits,max_request_bytes,max_output_tokens,allowed_tools,created_at,updated_at,cancelled_at,max_running_seconds,running_reserved_seconds,running_settled_seconds,last_settled_generation,last_settled_seconds,dispatch_closed,max_tool_calls,tools_reserved) ON public.activities TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.activities TO retrolume_data_restore_loader;

GRANT SELECT ON public.activities TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.activities FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,source_id,version_id,source_revision) ON public.activity_scope_sources TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.activity_scope_sources TO retrolume_data_restore_loader;

GRANT SELECT ON public.activity_scope_sources TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.activity_scope_sources FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,provider,model) ON public.activity_allowed_models TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.activity_allowed_models TO retrolume_data_restore_loader;

GRANT SELECT ON public.activity_allowed_models TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.activity_allowed_models FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,operation_id,admission_id,execution_generation,scope_revision,provider,configured_model,request_bytes,max_output_tokens,tool_names,reserved_cost_microunits,state,disposition,error_code,remote_request_id,returned_model,finish_reason,prompt_tokens,completion_tokens,response_bytes,reserved_at,dispatch_started_at,recorded_at,kind,arguments_sha256,tool_call_id) ON public.activity_operations TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.activity_operations TO retrolume_data_restore_loader;

GRANT SELECT ON public.activity_operations TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.activity_operations FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(id,source_id,version_id,expected_version,expected_revision,status,page_count,extraction_method,created_at,decided_at) ON public.pdf_review_candidates TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.pdf_review_candidates TO retrolume_data_restore_loader;

GRANT SELECT ON public.pdf_review_candidates TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.pdf_review_candidates FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(version_id,physical_page,extracted_text,warnings) ON public.pdf_extracted_pages TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.pdf_extracted_pages TO retrolume_data_restore_loader;

GRANT SELECT ON public.pdf_extracted_pages TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.pdf_extracted_pages FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(candidate_id,version_id,physical_page,reviewed_at) ON public.pdf_review_pages TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.pdf_review_pages TO retrolume_data_restore_loader;

GRANT SELECT ON public.pdf_review_pages TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.pdf_review_pages FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(id,candidate_id,version_id,physical_page,identity,text,created_at) ON public.pdf_user_supplements TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.pdf_user_supplements TO retrolume_data_restore_loader;

GRANT SELECT ON public.pdf_user_supplements TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.pdf_user_supplements FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,operation_id,admission_id,execution_generation,scope_revision,payload_format,payload,payload_sha256,committed_at) ON public.activity_operation_results TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.activity_operation_results TO retrolume_data_restore_loader;

GRANT SELECT ON public.activity_operation_results TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.activity_operation_results FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,revision,goal_version,last_seq,phase,goal_record_id,path_record_id,node_id,exercise_record_id,answer_record_id,feedback_record_id,reason_record_id,pending_business_key,projection,updated_at) ON public.teaching_heads TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.teaching_heads TO retrolume_data_restore_loader;

GRANT SELECT ON public.teaching_heads TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.teaching_heads FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,business_key,action,request_sha256,request_body,slot_sha256,expected_revision,goal_version,scope_revision,parent_record_id,context_body,context_sha256,operation_id,retry_of,status,launch_claimed_at,obsolete_at,abandoned_at,result_record_id,error_code,created_at,updated_at) ON public.teaching_commands TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.teaching_commands TO retrolume_data_restore_loader;

GRANT SELECT ON public.teaching_commands TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.teaching_commands FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,record_id,seq,kind,business_key,ordinal,goal_version,scope_revision,goal_record_id,parent_record_id,exercise_record_id,answer_record_id,supersedes_record_id,operation_id,body,body_sha256,source_refs,applied_revision,state_after,created_at) ON public.teaching_records TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.teaching_records TO retrolume_data_restore_loader;

GRANT SELECT ON public.teaching_records TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.teaching_records FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(memory_id,revision,current_version,state,created_at,updated_at,revoked_at,revocation_key,purged_at,purge_state) ON public.learning_memories TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.learning_memories TO retrolume_data_restore_loader;

GRANT SELECT ON public.learning_memories TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.learning_memories FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(business_key,action,memory_id,request_sha256,slot_sha256,effect_applied,before_revision,after_revision,after_version,result_meta,cleanup_manifest,manifest_sha256,committed_at) ON public.learning_memory_commands TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.learning_memory_commands TO retrolume_data_restore_loader;

GRANT SELECT ON public.learning_memory_commands TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.learning_memory_commands FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(memory_id,version,claim_kind,uncertainty,policy_version,body_sha256,body_bytes,dependencies_sha256,dependency_count,created_by_key,created_at) ON public.learning_memory_revisions TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.learning_memory_revisions TO retrolume_data_restore_loader;

GRANT SELECT ON public.learning_memory_revisions TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.learning_memory_revisions FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(memory_id,version,body) ON public.learning_memory_bodies TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.learning_memory_bodies TO retrolume_data_restore_loader;

GRANT SELECT ON public.learning_memory_bodies TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.learning_memory_bodies FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(memory_id,version,ordinal,dependency_kind,source_id,source_version_id,source_revision,original_sha256,origin_activity_id,record_id,record_kind,record_sha256,origin_scope_revision,origin_goal_version,upstream_memory_id,upstream_version,upstream_body_sha256) ON public.learning_memory_dependencies TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.learning_memory_dependencies TO retrolume_data_restore_loader;

GRANT SELECT ON public.learning_memory_dependencies TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.learning_memory_dependencies FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,selection_sha256,create_request_sha256,bound_scope_revision,bound_scope_sha256,selected_count,policy_version,selected_at) ON public.activity_memory_bindings TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.activity_memory_bindings TO retrolume_data_restore_loader;

GRANT SELECT ON public.activity_memory_bindings TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.activity_memory_bindings FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,memory_id,version,selected_revision,body_sha256,ordinal) ON public.activity_memory_choices TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.activity_memory_choices TO retrolume_data_restore_loader;

GRANT SELECT ON public.activity_memory_choices TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.activity_memory_choices FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,revision,goal_version,phase,last_seq,round_index,probe_depth,goal_record_id,root_question_id,current_question_id,current_answer_id,current_feedback_id,pending_key,scope_revision,source_snapshot_sha256,created_at,updated_at) ON public.interview_heads TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.interview_heads TO retrolume_data_restore_loader;

GRANT SELECT ON public.interview_heads TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.interview_heads FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,business_key,action,request_body,request_sha256,semantic_slot,execution_kind,context_body,context_sha256,operation_id,status,launch_claimed,obsolete,effect_applied,duplicate_of,retry_of,before_revision,after_revision,goal_version,scope_revision,result_record_ids,error_code,created_at,updated_at) ON public.interview_commands TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.interview_commands TO retrolume_data_restore_loader;

GRANT SELECT ON public.interview_commands TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.interview_commands FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,record_id,seq,business_key,ordinal,kind,origin,goal_version,scope_revision,round_index,probe_depth,answer_version,parent_ids,question_record_id,supersedes_record_id,source_refs,body_sha256,local_body,operation_id,payload_sha256,created_at) ON public.interview_records TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.interview_records TO retrolume_data_restore_loader;

GRANT SELECT ON public.interview_records TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.interview_records FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,business_key,operation_id,request_body,request_sha256,context_body,context_sha256,renderer_sha256,scope_revision,parent_kind,parent_locator,parent_sha256,status,terminal_disposition,error_code,created_at,updated_at) ON public.html_commands TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.html_commands TO retrolume_data_restore_loader;

GRANT SELECT ON public.html_commands TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.html_commands FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(artifact_id,activity_id,business_key,operation_id,artifact_body,artifact_sha256,description_sha256,renderer_sha256,execution_package_sha256,body_sha256,created_at) ON public.html_artifacts TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.html_artifacts TO retrolume_data_restore_loader;

GRANT SELECT ON public.html_artifacts TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.html_artifacts FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(activity_id,config_sha256,max_starts,max_seconds,starts_used,settled_seconds,reserved_seconds,revision) ON public.html_preview_budgets TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.html_preview_budgets TO retrolume_data_restore_loader;

GRANT SELECT ON public.html_preview_budgets TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.html_preview_budgets FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT SELECT(preview_id,activity_id,artifact_id,start_key,generation,artifact_sha256,image_id,reserve_seconds,elapsed_seconds,deadline_at,state,revision,created_at) ON public.html_preview_sessions TO retrolume_data_snapshot;

GRANT SELECT,INSERT ON public.html_preview_sessions TO retrolume_data_restore_loader;

GRANT SELECT ON public.html_preview_sessions TO retrolume_data_owner;

CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.html_preview_sessions FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();

GRANT UPDATE(current_version) ON public.material_sources TO retrolume_data_restore_loader;

GRANT USAGE ON SCHEMA public TO retrolume_data_owner,retrolume_data_app,retrolume_data_snapshot,retrolume_data_restore_loader;

GRANT EXECUTE ON FUNCTION public.memory_revision_readable(uuid,integer),public.memory_revision_eligible(uuid,integer),public.activity_memory_eligible(uuid),public.memory_scope_digest(uuid),public.memory_choice_digest(uuid),public.memory_dependency_digest(uuid,integer),public.memory_dependency_line(public.learning_memory_dependencies),public.interview_result_eligible(uuid,text),public.html_expected_renderer(),public.html_expected_html(),public.html_parent_eligible(uuid,jsonb),public.html_artifact_eligible(uuid,uuid) TO retrolume_data_snapshot,retrolume_data_restore_loader;
COMMIT;
