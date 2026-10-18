-- 候选迁移 007：G3 业务成果正文（activity_operation_results）。
-- 仅用于获批的新本地合成数据库；不由应用启动器自动执行，不操作用户库。
-- 前置：001/002 已建（material_sources/material_versions/activities/
-- activity_scope_sources/activity_operations 存在）；不要求 activities 为空，
-- 不回填任何旧 received/unknown 操作的正文。
-- 重复执行不支持（无 IF NOT EXISTS）：重复执行报 duplicate table 并整体回滚，
-- 不宣称迁移天然幂等——与 004/005 的“仅空库 ALTER”是两种不同约定。
BEGIN;

CREATE TABLE activity_operation_results (
    activity_id UUID NOT NULL,
    operation_id VARCHAR(128) NOT NULL,
    admission_id UUID NOT NULL,
    execution_generation INTEGER NOT NULL CHECK (execution_generation >= 0),
    scope_revision INTEGER NOT NULL CHECK (scope_revision > 0),
    payload_format TEXT NOT NULL CHECK (payload_format IN ('text', 'json')),
    payload TEXT NOT NULL CHECK (octet_length(payload) BETWEEN 1 AND 131072),
    payload_sha256 TEXT NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_id, operation_id),
    FOREIGN KEY (activity_id, operation_id)
        REFERENCES activity_operations(activity_id, operation_id)
);

COMMIT;
