-- TASK117 pending forward repair, NOT EXECUTED. Original 001..013 unchanged.
BEGIN;
DO $guard$ BEGIN
 IF NOT EXISTS(SELECT 1 FROM public.data_export_control_v1 WHERE schema_profile='data_exit.v1.r02' AND mode_observed='normal') THEN RAISE EXCEPTION 'TASK117 expected normal R02 source'; END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_proc WHERE oid='public.retrieval_chunk_guard()'::regprocedure AND encode(sha256(convert_to(regexp_replace(prosrc,'\s','','g'),'UTF8')),'hex') IN ('4efdb6c4b774ef67c00534c26e7c1b9963d4341b6113a7d1c9ce339e0aaddf55','2b8801abe7c42eaaa8c2ffc5e4117e251c459c593110c16faf0016d696431bab')) THEN RAISE EXCEPTION 'TASK117 prior function identity mismatch'; END IF;
END $guard$;
GRANT SELECT ON public.material_versions,public.pdf_review_candidates,public.pdf_review_pages,public.pdf_extracted_pages,public.teaching_records TO retrolume_interview_owner;
CREATE OR REPLACE FUNCTION public.retrieval_chunk_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE op public.activity_operations;r public.activity_operation_results;c public.retrieval_commands;b jsonb;item jsonb;meta jsonb;key uuid;
BEGIN
 IF TG_OP='DELETE' THEN
  IF NOT EXISTS(SELECT 1 FROM public.data_tombstones WHERE entity_kind='source' AND entity_id=OLD.source_id)
   AND NOT EXISTS(SELECT 1 FROM public.retrieval_commands purge_command,jsonb_array_elements(purge_command.source_refs) s,public.data_tombstones t
     WHERE purge_command.activity_id=OLD.committed_activity_id AND purge_command.business_key=split_part(OLD.committed_operation_id,'.',2)::uuid
       AND t.entity_kind='source' AND t.entity_id=(s->>'source_id')::uuid)
   THEN RAISE EXCEPTION 'retrieval_purge_not_authorized'; END IF;
  RETURN OLD;
 END IF;
 IF TG_OP='UPDATE' THEN RAISE EXCEPTION 'retrieval_chunk_immutable'; END IF;
 SELECT * INTO op FROM public.activity_operations WHERE activity_id=NEW.committed_activity_id AND operation_id=NEW.committed_operation_id;
 SELECT * INTO r FROM public.activity_operation_results WHERE activity_id=NEW.committed_activity_id AND operation_id=NEW.committed_operation_id;
 key:=split_part(NEW.committed_operation_id,'.',2)::uuid;
 SELECT * INTO c FROM public.retrieval_commands WHERE activity_id=NEW.committed_activity_id AND business_key=key;
 b:=r.payload::jsonb->'value';
 IF op.kind IS DISTINCT FROM 'embedding' OR op.state IS DISTINCT FROM 'received' OR c.action IS DISTINCT FROM 'source_index'
  OR b->>'profile' IS DISTINCT FROM 'embedding.v1' OR c.space_id<>NEW.space_id THEN RAISE EXCEPTION 'retrieval_chunk_result'; END IF;
 IF NEW.vector_value IS NOT NULL THEN
  IF NEW.vector_sha256 IS DISTINCT FROM public.retrieval_vector_digest(NEW.vector_value) THEN RAISE EXCEPTION 'retrieval_vector_digest'; END IF;
  SELECT x INTO item FROM jsonb_array_elements(b->'inputs') x WHERE x->>'identity_sha256' IN
   (SELECT y->>'identity_sha256' FROM jsonb_array_elements(c.request_body::jsonb->'manifest') y WHERE y->>'evidence_id'=NEW.evidence_id);
  IF item IS NULL OR item->>'vector_sha256' IS DISTINCT FROM NEW.vector_sha256
   OR (((item->'vector')::text::public.vector OPERATOR(public.=) NEW.vector_value) IS NOT TRUE) THEN RAISE EXCEPTION 'retrieval_vector_fact'; END IF;
 END IF;
 SELECT x INTO meta FROM jsonb_array_elements(c.request_body::jsonb->'manifest') x WHERE x->>'evidence_id'=NEW.evidence_id;
 IF meta IS NULL OR meta->>'source_id' IS DISTINCT FROM NEW.source_id::text OR meta->>'source_version_id' IS DISTINCT FROM NEW.source_version_id::text
  OR (meta->>'source_revision')::integer IS DISTINCT FROM NEW.source_revision OR meta->>'origin' IS DISTINCT FROM NEW.origin
  OR (meta->>'physical_page')::integer IS DISTINCT FROM NEW.physical_page OR (meta->>'start_codepoint')::integer IS DISTINCT FROM NEW.start_codepoint
  OR (meta->>'end_codepoint')::integer IS DISTINCT FROM NEW.end_codepoint OR meta->>'text_sha256' IS DISTINCT FROM NEW.text_sha256
 THEN RAISE EXCEPTION 'retrieval_chunk_source'; END IF;
 RETURN NEW;
END $f$;
DO $verify$ DECLARE name text; BEGIN FOREACH name IN ARRAY ARRAY['public.material_versions','public.pdf_review_candidates','public.pdf_review_pages','public.pdf_extracted_pages','public.teaching_records'] LOOP
 IF NOT has_table_privilege('retrolume_interview_owner',name,'SELECT') OR has_table_privilege('retrolume_interview_owner',name,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') THEN RAISE EXCEPTION 'TASK117 exact read-only privilege mismatch'; END IF;
END LOOP; END $verify$;
COMMIT;
