-- 候选迁移 009：G8 教学领域三表（TASK-100 / R-094，G8-P 批准包）。
-- 仅用于获批的合成数据库；不由应用启动器自动执行，不操作用户库。
-- 前置：001—008 已建（含 008 activity_operations.kind）。
-- 单事务内核 001—008 实际结构/必要列与 G8 残迹；任一不符 RAISE 整体回滚，
-- 不以表名相同采用被篡改约束。非空升级只新增表/索引/FK/触发器，
-- 零回填旧 G7 学习行、旧 received 无正文不补正文。重复执行不支持。
BEGIN;

DO $$
BEGIN
    -- 001—008 基线结构核验（列级；不只比表名）。
    IF to_regclass('material_sources') IS NULL OR to_regclass('material_versions') IS NULL
       OR to_regclass('activities') IS NULL OR to_regclass('activity_scope_sources') IS NULL
       OR to_regclass('activity_allowed_models') IS NULL OR to_regclass('activity_operations') IS NULL
       OR to_regclass('activity_operation_results') IS NULL THEN
        RAISE EXCEPTION '009 前置不存在：需要 001—008 已建基线';
    END IF;
    -- 008 关键列必须存在（kind / 工具预算）。
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema = current_schema() AND table_name = 'activity_operations'
                      AND column_name = 'kind')
       OR NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema = current_schema() AND table_name = 'activities'
                      AND column_name = 'max_tool_calls') THEN
        RAISE EXCEPTION '009 前置不完整：缺少 008 的 kind/工具预算列';
    END IF;
    -- 008 的 model/tool 域约束必须真实在位（被篡改即拒）。
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                    WHERE conrelid = 'activity_operations'::regclass
                      AND conname = 'activity_operations_kind_domain')
       OR NOT EXISTS (SELECT 1 FROM pg_constraint
                    WHERE conrelid = 'activity_operations'::regclass
                      AND conname = 'activity_operations_kind_shape') THEN
        RAISE EXCEPTION '009 前置约束被篡改或缺失：008 kind 域/形状约束不在位';
    END IF;
    -- G8 残迹检查：任何教学表已存在即拒绝重复执行。
    IF to_regclass('teaching_heads') IS NOT NULL OR to_regclass('teaching_commands') IS NOT NULL
       OR to_regclass('teaching_records') IS NOT NULL THEN
        RAISE EXCEPTION '检测到 009 已有痕迹：重复执行不支持，本事务整体回滚';
    END IF;
END $$;

CREATE TABLE teaching_heads (
    activity_id UUID PRIMARY KEY REFERENCES activities(id),
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision BETWEEN 0 AND 2147483647),
    goal_version INTEGER NOT NULL DEFAULT 0 CHECK (goal_version BETWEEN 0 AND 32),
    last_seq INTEGER NOT NULL DEFAULT 0 CHECK (last_seq BETWEEN 0 AND 4096),
    phase TEXT NOT NULL DEFAULT 'needs_goal' CHECK (phase IN
        ('needs_goal','needs_plan','path_review','ready','exercise_ready','answer_saved','feedback_ready')),
    goal_record_id UUID,
    path_record_id UUID,
    node_id VARCHAR(2) CHECK (node_id IS NULL OR node_id ~ '^n[1-6]$'),
    exercise_record_id UUID,
    answer_record_id UUID,
    feedback_record_id UUID,
    reason_record_id UUID,
    pending_business_key UUID,
    projection TEXT NOT NULL DEFAULT '{}' CHECK (octet_length(projection) BETWEEN 2 AND 8192),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ((goal_version = 0 AND goal_record_id IS NULL AND phase = 'needs_goal')
        OR (goal_version > 0 AND goal_record_id IS NOT NULL AND phase <> 'needs_goal')),
    CHECK ((path_record_id IS NULL AND node_id IS NULL) OR
        (path_record_id IS NOT NULL AND node_id IS NOT NULL)),
    CHECK (answer_record_id IS NULL OR exercise_record_id IS NOT NULL),
    CHECK (feedback_record_id IS NULL OR answer_record_id IS NOT NULL)
);

CREATE TABLE teaching_commands (
    activity_id UUID NOT NULL REFERENCES activities(id),
    business_key UUID NOT NULL,
    action TEXT NOT NULL CHECK (action IN
        ('goal','plan','accept_path','exercise','expose','answer','calculate','evaluate',
         'correct','abandon','select_node')),
    request_sha256 CHAR(64) NOT NULL CHECK (request_sha256 ~ '^[0-9a-f]{64}$'),
    request_body TEXT NOT NULL CHECK (octet_length(request_body) BETWEEN 2 AND 32768),
    slot_sha256 CHAR(64) NOT NULL CHECK (slot_sha256 ~ '^[0-9a-f]{64}$'),
    expected_revision INTEGER NOT NULL CHECK (expected_revision BETWEEN 0 AND 2147483647),
    goal_version INTEGER NOT NULL CHECK (goal_version BETWEEN 0 AND 32),
    scope_revision INTEGER NOT NULL CHECK (scope_revision > 0),
    parent_record_id UUID,
    context_body TEXT CHECK (context_body IS NULL OR octet_length(context_body) BETWEEN 2 AND 49152),
    context_sha256 CHAR(64) CHECK (context_sha256 IS NULL OR context_sha256 ~ '^[0-9a-f]{64}$'),
    operation_id VARCHAR(128) CHECK (operation_id IS NULL OR
        (char_length(operation_id) BETWEEN 1 AND 128 AND operation_id !~ '[^A-Za-z0-9._:/-]')),
    retry_of UUID,
    status TEXT NOT NULL CHECK (status IN
        ('accepted','started','committed','history','not_sent','failed','unknown','abandoned')),
    launch_claimed_at TIMESTAMPTZ,
    obsolete_at TIMESTAMPTZ,
    abandoned_at TIMESTAMPTZ,
    result_record_id UUID,
    error_code VARCHAR(64) CHECK (error_code IS NULL OR error_code ~ '^[A-Za-z0-9._:/-]{1,64}$'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_id,business_key),
    UNIQUE (activity_id,operation_id),
    FOREIGN KEY (activity_id,retry_of) REFERENCES teaching_commands(activity_id,business_key),
    CHECK ((context_body IS NULL) = (context_sha256 IS NULL)),
    CHECK ((action IN ('plan','exercise','evaluate','calculate') AND operation_id IS NOT NULL)
        OR (action NOT IN ('plan','exercise','evaluate','calculate') AND operation_id IS NULL)),
    CHECK (launch_claimed_at IS NULL OR action IN ('plan','exercise','evaluate','calculate')),
    CHECK (status <> 'started' OR launch_claimed_at IS NOT NULL)
);

CREATE UNIQUE INDEX teaching_command_live_slot ON teaching_commands(activity_id,action,slot_sha256)
    WHERE status IN ('accepted','started','unknown','committed','history');
CREATE INDEX teaching_commands_recent ON teaching_commands(activity_id,created_at,business_key);

CREATE TABLE teaching_records (
    activity_id UUID NOT NULL REFERENCES activities(id),
    record_id UUID NOT NULL,
    seq INTEGER NOT NULL CHECK (seq BETWEEN 1 AND 4096),
    kind TEXT NOT NULL CHECK (kind IN
        ('goal','path_proposal','path_accept','exercise','exposure','answer','calculation',
         'feedback','progress','correction','node_selection')),
    business_key UUID NOT NULL,
    ordinal SMALLINT NOT NULL CHECK (ordinal BETWEEN 1 AND 4),
    goal_version INTEGER NOT NULL CHECK (goal_version BETWEEN 1 AND 32),
    scope_revision INTEGER NOT NULL CHECK (scope_revision > 0),
    goal_record_id UUID,
    parent_record_id UUID,
    exercise_record_id UUID,
    answer_record_id UUID,
    supersedes_record_id UUID,
    operation_id VARCHAR(128),
    body TEXT CHECK (body IS NULL OR octet_length(body) BETWEEN 2 AND 32768),
    body_sha256 CHAR(64) NOT NULL CHECK (body_sha256 ~ '^[0-9a-f]{64}$'),
    source_refs TEXT NOT NULL CHECK (octet_length(source_refs) BETWEEN 2 AND 8192),
    applied_revision INTEGER CHECK (applied_revision BETWEEN 1 AND 2147483647),
    state_after TEXT CHECK (state_after IS NULL OR octet_length(state_after) BETWEEN 2 AND 8192),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_id,record_id),
    UNIQUE (activity_id,seq),
    UNIQUE (activity_id,business_key,ordinal),
    FOREIGN KEY (activity_id,business_key) REFERENCES teaching_commands(activity_id,business_key),
    FOREIGN KEY (activity_id,operation_id) REFERENCES activity_operation_results(activity_id,operation_id),
    FOREIGN KEY (activity_id,goal_record_id) REFERENCES teaching_records(activity_id,record_id),
    FOREIGN KEY (activity_id,parent_record_id) REFERENCES teaching_records(activity_id,record_id),
    FOREIGN KEY (activity_id,exercise_record_id) REFERENCES teaching_records(activity_id,record_id),
    FOREIGN KEY (activity_id,answer_record_id) REFERENCES teaching_records(activity_id,record_id),
    FOREIGN KEY (activity_id,supersedes_record_id) REFERENCES teaching_records(activity_id,record_id),
    CHECK ((kind IN ('path_proposal','exercise','calculation','feedback')
            AND operation_id IS NOT NULL AND body IS NULL)
        OR (kind NOT IN ('path_proposal','exercise','calculation','feedback')
            AND operation_id IS NULL AND body IS NOT NULL)),
    CHECK ((applied_revision IS NULL) = (state_after IS NULL)),
    CHECK ((kind = 'goal' AND goal_record_id IS NULL) OR
        (kind <> 'goal' AND goal_record_id IS NOT NULL)),
    CHECK (kind NOT IN ('feedback','calculation','progress') OR answer_record_id IS NOT NULL),
    CHECK (kind NOT IN ('answer','exposure','feedback','calculation','progress') OR exercise_record_id IS NOT NULL),
    CHECK (kind <> 'progress' OR parent_record_id IS NOT NULL)
);

CREATE UNIQUE INDEX teaching_goal_version ON teaching_records(activity_id,goal_version) WHERE kind='goal';
CREATE UNIQUE INDEX teaching_operation_fact ON teaching_records(activity_id,operation_id) WHERE operation_id IS NOT NULL;
CREATE UNIQUE INDEX teaching_effect_revision ON teaching_records(activity_id,applied_revision) WHERE applied_revision IS NOT NULL;
CREATE UNIQUE INDEX teaching_feedback_effect ON teaching_records(activity_id,parent_record_id) WHERE kind='progress';
CREATE UNIQUE INDEX teaching_answer_successor ON teaching_records(activity_id,supersedes_record_id)
    WHERE kind='answer' AND supersedes_record_id IS NOT NULL;
CREATE UNIQUE INDEX teaching_initial_answer ON teaching_records(activity_id,exercise_record_id)
    WHERE kind='answer' AND supersedes_record_id IS NULL;
CREATE INDEX teaching_history ON teaching_records(activity_id,seq DESC);
CREATE INDEX teaching_answer_observations ON teaching_records(activity_id,answer_record_id,seq)
    WHERE kind IN ('feedback','progress','correction');

ALTER TABLE teaching_heads
    ADD FOREIGN KEY (activity_id,goal_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,path_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,exercise_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,answer_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,feedback_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,reason_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,pending_business_key) REFERENCES teaching_commands(activity_id,business_key);
ALTER TABLE teaching_commands
    ADD FOREIGN KEY (activity_id,parent_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,result_record_id) REFERENCES teaching_records(activity_id,record_id);

-- 教学事实不可变（099 第 4 节批准原文）：任何 UPDATE/DELETE 一律拒绝，
-- 包括 applied_revision/state_after——它们是记录生效时点一次性写入的
-- 不可变效果事实（applied_revision + state_after 成对；历史不生效则两者
-- 均为 NULL）。仓储必须在同一事务内先算好最终效果再 INSERT，绝不事后回填。
-- 本轮不提供获准删除事务（STEP013/017 以后才有），不宣称删除已实现。
CREATE FUNCTION teaching_records_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '教学历史不可覆盖或直接删除';
END;
$$;
CREATE TRIGGER teaching_records_immutable BEFORE UPDATE OR DELETE ON teaching_records
    FOR EACH ROW EXECUTE FUNCTION teaching_records_immutable();
CREATE FUNCTION teaching_command_identity_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF ROW(NEW.activity_id,NEW.business_key,NEW.action,NEW.request_sha256,NEW.request_body,
           NEW.slot_sha256,NEW.expected_revision,NEW.goal_version,NEW.scope_revision,
           NEW.parent_record_id,NEW.context_body,NEW.context_sha256,NEW.operation_id,
           NEW.retry_of,NEW.created_at)
       IS DISTINCT FROM
       ROW(OLD.activity_id,OLD.business_key,OLD.action,OLD.request_sha256,OLD.request_body,
           OLD.slot_sha256,OLD.expected_revision,OLD.goal_version,OLD.scope_revision,
           OLD.parent_record_id,OLD.context_body,OLD.context_sha256,OLD.operation_id,
           OLD.retry_of,OLD.created_at) THEN
        RAISE EXCEPTION '教学命令身份不可改写';
    END IF;
    IF OLD.launch_claimed_at IS NOT NULL AND
       NEW.launch_claimed_at IS DISTINCT FROM OLD.launch_claimed_at THEN
        RAISE EXCEPTION '教学启动资格不可重置';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER teaching_command_identity_guard BEFORE UPDATE ON teaching_commands
    FOR EACH ROW EXECUTE FUNCTION teaching_command_identity_guard();
REVOKE ALL ON teaching_heads,teaching_commands,teaching_records FROM PUBLIC;

COMMIT;
