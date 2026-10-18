CREATE OR REPLACE FUNCTION public.memory_final_shape_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SET search_path TO 'pg_catalog', 'pg_temp'
AS $function$
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
END $function$
