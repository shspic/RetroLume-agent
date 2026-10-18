CREATE OR REPLACE FUNCTION public.purge_learning_memory(revocation_key uuid, manifest_sha256 text, purge_business_key uuid, request_sha256 text)
 RETURNS text
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'pg_temp'
AS $function$
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
END $function$
