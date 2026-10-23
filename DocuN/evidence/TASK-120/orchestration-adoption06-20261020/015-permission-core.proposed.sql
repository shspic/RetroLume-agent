-- AP-120-06 审阅草案，未批准、未执行；不是可在旧库直接运行的正式迁移。
-- 正式015还须具备预期schema/角色/trigger校验、严格版本指纹及兼容处理。
BEGIN;
LOCK TABLE public.activity_scope_sources IN ACCESS EXCLUSIVE MODE;
GRANT DELETE ON public.activity_scope_sources TO retrolume_data_app;
COMMIT;
