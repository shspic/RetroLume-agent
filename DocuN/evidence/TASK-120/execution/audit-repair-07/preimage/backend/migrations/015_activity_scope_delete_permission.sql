-- AP-120-06: only the existing application group's scope-binding DELETE.
BEGIN;
LOCK TABLE public.data_control, public.activity_scope_sources IN ACCESS EXCLUSIVE MODE;
DO $check$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='retrolume_data_app'
   AND NOT (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls))
 OR EXISTS(SELECT 1 FROM public.data_control WHERE schema_profile<>'data_exit.v1.r02' OR mode NOT IN('normal','loading'))
 OR NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conrelid='public.data_control'::regclass
   AND conname='data_control_schema_profile_check' AND convalidated
   AND pg_get_constraintdef(oid)=$old$CHECK ((schema_profile = ANY (ARRAY['data_exit.v1.r01'::text, 'data_exit.v1.r02'::text])))$old$)
 OR NOT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_proc p ON p.oid=t.tgfoid
   WHERE t.tgrelid='public.activity_scope_sources'::regclass AND t.tgname='data_runtime_write'
   AND NOT t.tgisinternal AND t.tgenabled='O' AND t.tgtype=31
   AND p.proname='data_runtime_write_guard' AND p.prosecdef
   AND encode(sha256(convert_to(regexp_replace(p.prosrc,'\s','','g'),'UTF8')),'hex')='91dac86ea0de0c3f943160430d30777528df2ecdbfe8fa7802a0debd90ca6295')
 OR NOT has_table_privilege('retrolume_data_app','public.activity_scope_sources','SELECT,INSERT,UPDATE')
 OR has_table_privilege('retrolume_data_app','public.activity_scope_sources','DELETE,TRUNCATE')
 OR has_table_privilege('retrolume_data_snapshot','public.activity_scope_sources','DELETE,TRUNCATE')
 OR has_table_privilege('retrolume_data_restore_loader','public.activity_scope_sources','DELETE,TRUNCATE')
 OR EXISTS(SELECT 1 FROM public.activities WHERE running_reserved_seconds>0 OR lease_expires_at>CURRENT_TIMESTAMP)
 THEN RAISE EXCEPTION 'scope_delete_migration_requires_exact_quiescent_r02'; END IF;
END $check$;
GRANT DELETE ON public.activity_scope_sources TO retrolume_data_app;
ALTER TABLE public.data_control DROP CONSTRAINT data_control_schema_profile_check;
ALTER TABLE public.data_control ADD CONSTRAINT data_control_schema_profile_check CHECK(schema_profile='data_exit.v1.r03');
UPDATE public.data_control SET schema_profile='data_exit.v1.r03';
COMMIT;
