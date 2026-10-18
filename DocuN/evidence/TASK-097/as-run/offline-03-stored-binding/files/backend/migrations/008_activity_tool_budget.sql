-- 候选迁移 008：受控工具次数与操作 kind（TASK-092 / R-086，G5 批准包 B2）。
-- 仅用于获批的合成数据库；不由应用启动器自动执行，不操作用户库。
-- 前置：001—007 已建（含 007 activity_operation_results）。
-- 旧行解释：activities 新增 max_tool_calls=NULL、tools_reserved=0；
-- activity_operations 旧行 kind='model'（列默认值），不自动赋工具额度、
-- 不伪造历史工具调用。001—007 只读，本迁移不修改它们。
-- 迁移真实限制：ALTER 会取表级排他锁并可能扫描/验证既有行；本文件不承诺
-- ALTER 零重写或零扫描，也不承诺重复执行为天然幂等——重复执行由下方门禁
-- 明确报错并整体回滚。若 008 已 COMMIT 且已存在工具行，事后反向 DROP 回
-- 007 不保证无损（工具已用次数与 kind=model 约束冲突），需备份与向前修正。
BEGIN;

-- 单事务内核 001—007 基线与本库是否已含 008 痕迹；重复执行立即失败回滚。
DO $$
BEGIN
    IF to_regclass('activities') IS NULL OR to_regclass('activity_operations') IS NULL
       OR to_regclass('activity_operation_results') IS NULL THEN
        RAISE EXCEPTION '008 前置不存在：需要 001—007 已建基线';
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'activities' AND column_name = 'max_tool_calls')
       OR EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'activity_operations' AND column_name = 'kind') THEN
        RAISE EXCEPTION '检测到 008 已有痕迹：重复执行不支持，本事务整体回滚';
    END IF;
END $$;

-- activities：工具次数上限与已用预扣。NULL 表示未配置（必须已用 0），
-- 0 表示明确禁用；配置时已用不得超过上限。INTEGER 自身限制上界。
ALTER TABLE activities
    ADD COLUMN max_tool_calls INTEGER
        CONSTRAINT activities_tool_budget_limit CHECK (
            max_tool_calls IS NULL OR max_tool_calls >= 0),
    ADD COLUMN tools_reserved INTEGER NOT NULL DEFAULT 0
        CONSTRAINT activities_tool_budget_reserved CHECK (tools_reserved >= 0);

ALTER TABLE activities
    ADD CONSTRAINT activities_tool_budget_balance CHECK (
        (max_tool_calls IS NULL AND tools_reserved = 0)
        OR
        (max_tool_calls IS NOT NULL
         AND tools_reserved BETWEEN 0 AND max_tool_calls)
    );

-- activity_operations：kind、参数摘要与调用 ID；模型专属列放宽为可空，
-- 由下方 model/tool 总条件收紧。旧成本单列正值约束按 pg_constraint
-- 真实名称精确识别后替换；名称或定义数量不符即整体回滚，不宽泛 DROP。
ALTER TABLE activity_operations
    ADD COLUMN kind TEXT NOT NULL DEFAULT 'model',
    ADD COLUMN arguments_sha256 TEXT,
    ADD COLUMN tool_call_id VARCHAR(128);

ALTER TABLE activity_operations
    ALTER COLUMN provider DROP NOT NULL,
    ALTER COLUMN configured_model DROP NOT NULL,
    ALTER COLUMN request_bytes DROP NOT NULL,
    ALTER COLUMN max_output_tokens DROP NOT NULL;

DO $$
DECLARE
    matched text[] := ARRAY[]::text[];
    con record;
BEGIN
    FOR con IN
        SELECT conname, pg_get_constraintdef(oid) AS definition
          FROM pg_constraint
         WHERE conrelid = 'activity_operations'::regclass
           AND contype = 'c'
    LOOP
        -- 原 002 单列约束在 PG 中规范形如 CHECK ((reserved_cost_microunits > 0))。
        IF con.definition IN (
            'CHECK ((reserved_cost_microunits > 0))',
            'CHECK (reserved_cost_microunits > 0)'
        ) THEN
            matched := matched || con.conname;
        END IF;
    END LOOP;
    IF coalesce(array_length(matched, 1), 0) <> 1 THEN
        RAISE EXCEPTION '原成本正值约束未能唯一识别（匹配 % 条），迁移整体回滚',
            coalesce(array_length(matched, 1), 0);
    END IF;
    EXECUTE format('ALTER TABLE activity_operations DROP CONSTRAINT %I', matched[1]);
END $$;

-- model/tool 完整条件；显式 IS NOT NULL 防止 SQL 三值逻辑放过不完整工具行。
-- 模型原可空返回/usage 字段不改为非空，继续原取值校验；工具行不允许任何
-- 模型元数据、虚假 0 token 或伪费用占位。工具名复用单项数组。
ALTER TABLE activity_operations
    ADD CONSTRAINT activity_operations_kind_domain CHECK (kind IN ('model', 'tool')),
    ADD CONSTRAINT activity_operations_kind_shape CHECK (
        (kind = 'model'
         AND provider IS NOT NULL AND configured_model IS NOT NULL
         AND request_bytes IS NOT NULL AND request_bytes > 0
         AND max_output_tokens IS NOT NULL AND max_output_tokens > 0
         AND reserved_cost_microunits > 0
         AND arguments_sha256 IS NULL AND tool_call_id IS NULL)
        OR
        (kind = 'tool'
         AND provider IS NULL AND configured_model IS NULL
         AND request_bytes IS NULL AND max_output_tokens IS NULL
         AND reserved_cost_microunits = 0
         AND tool_names = ARRAY['finite_calculate']::VARCHAR(64)[]
         AND arguments_sha256 IS NOT NULL
         AND octet_length(arguments_sha256) = 64
         AND arguments_sha256 ~ '^[0-9a-f]{64}$'
         AND tool_call_id IS NOT NULL
         AND char_length(tool_call_id) BETWEEN 1 AND 128
         AND tool_call_id !~ '[^A-Za-z0-9._:/-]'
         AND remote_request_id IS NULL AND returned_model IS NULL
         AND finish_reason IS NULL AND prompt_tokens IS NULL
         AND completion_tokens IS NULL AND response_bytes IS NULL)
    );

-- 新约束全部当次验证既有行，不留 NOT VALID 逃逸；任一不符本事务回滚。
COMMIT;
