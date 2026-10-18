CREATE OR REPLACE FUNCTION public.activity_memory_eligible(aid uuid)
 RETURNS boolean
 LANGUAGE sql
 STABLE
 SET search_path TO 'pg_catalog', 'pg_temp'
AS $function$
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
$function$
