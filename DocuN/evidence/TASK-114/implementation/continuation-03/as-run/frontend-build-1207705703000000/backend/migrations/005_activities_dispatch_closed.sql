-- TASK-083 候选迁移：只用于全新/空 activities 合成库；本卡不执行。
BEGIN;

LOCK TABLE activities IN ACCESS EXCLUSIVE MODE;
DO $$
BEGIN
    PERFORM 1 FROM activities LIMIT 1;
    IF FOUND THEN
        RAISE EXCEPTION 'activities 非空：005 仅允许在空 activities 合成库执行，本事务已回滚';
    END IF;
END $$;

ALTER TABLE activities
    ADD COLUMN dispatch_closed BOOLEAN NOT NULL DEFAULT FALSE;

COMMIT;
