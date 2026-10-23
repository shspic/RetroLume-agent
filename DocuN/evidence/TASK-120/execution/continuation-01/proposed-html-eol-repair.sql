-- REVIEW ONLY until explicit TASK120 supplemental DDL permission.
BEGIN;
CREATE OR REPLACE FUNCTION public.html_accept_command(aid uuid, key uuid, op text, rb text, rh text, cb text, ch text,
 renderer text, scope integer, pk text, loc text, ph text) RETURNS void
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
 INSERT INTO public.html_commands(activity_id,business_key,operation_id,request_body,request_sha256,context_body,context_sha256,
 renderer_sha256,scope_revision,parent_kind,parent_locator,parent_sha256) VALUES(aid,key,op,rb,rh,cb,ch,renderer,scope,pk,loc,ph)
$body$;

CREATE OR REPLACE FUNCTION public.html_artifact_eligible(aid uuid, art uuid) RETURNS boolean
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

CREATE OR REPLACE FUNCTION public.html_claim_command(aid uuid, key uuid) RETURNS boolean
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN UPDATE public.html_commands SET status='launch_claimed',updated_at=CURRENT_TIMESTAMP WHERE activity_id=aid AND business_key=key AND status='accepted'; RETURN FOUND; END;
$body$;

CREATE OR REPLACE FUNCTION public.html_commit_artifact(aid uuid, key uuid, art uuid, op text, body text, ah text, dh text, rh text, eh text, bh text) RETURNS void
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
 INSERT INTO public.html_artifacts(artifact_id,activity_id,business_key,operation_id,artifact_body,artifact_sha256,
 description_sha256,renderer_sha256,execution_package_sha256,body_sha256) VALUES(art,aid,key,op,body,ah,dh,rh,eh,bh)
$body$;

CREATE OR REPLACE FUNCTION public.html_finish_command(aid uuid,key uuid,disposition text,error text) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $body$
BEGIN
 IF disposition='succeeded' AND NOT EXISTS(SELECT 1 FROM public.html_artifacts WHERE activity_id=aid AND business_key=key)
 THEN RAISE EXCEPTION 'html missing committed artifact'; END IF;
 UPDATE public.html_commands SET status='terminal',terminal_disposition=disposition,error_code=error,updated_at=CURRENT_TIMESTAMP
 WHERE activity_id=aid AND business_key=key AND status='launch_claimed';
END;
$body$;

CREATE OR REPLACE FUNCTION public.html_immutable_guard() RETURNS trigger LANGUAGE plpgsql AS $body$
BEGIN RAISE EXCEPTION 'html artifact immutable'; END;
$body$;

CREATE OR REPLACE FUNCTION public.html_parent_eligible(aid uuid, frozen jsonb) RETURNS boolean
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

CREATE OR REPLACE FUNCTION public.html_reserve_preview(aid uuid, art uuid, pid uuid, sk uuid, ah text, owner uuid, oh text, auth text,
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

CREATE OR REPLACE FUNCTION public.html_update_preview(pid uuid, auth text, next_state text, exact_cid text, first_receipt text,
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
COMMIT;
