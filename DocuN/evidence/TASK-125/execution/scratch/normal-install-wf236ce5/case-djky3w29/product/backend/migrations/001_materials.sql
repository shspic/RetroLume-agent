-- 候选迁移：只用于获批的新本地数据库，尚未执行；失败整笔回滚。
BEGIN;
CREATE TABLE material_sources (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    current_version UUID,
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision >= 0)
);
CREATE TABLE material_versions (
    id UUID PRIMARY KEY,
    source_id UUID NOT NULL REFERENCES material_sources(id),
    filename TEXT NOT NULL,
    format TEXT NOT NULL CHECK (format IN ('txt','md')),
    sha256 CHAR(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    size BIGINT NOT NULL CHECK (size >= 0 AND size <= 5242880),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id,id)
);
ALTER TABLE material_sources ADD CONSTRAINT material_current_version_source
    FOREIGN KEY (id,current_version) REFERENCES material_versions(source_id,id);
CREATE INDEX material_versions_source ON material_versions(source_id);
COMMIT;

