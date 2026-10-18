-- TASK-083 D3: old rows remain NULL and cannot gain automatic recovery rights.
BEGIN;

ALTER TABLE activities
    ADD COLUMN running_owner_session_id BIGINT DEFAULT NULL
        CHECK (running_owner_session_id BETWEEN 0 AND 4294967295);

COMMIT;
