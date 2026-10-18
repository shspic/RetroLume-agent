"""从项目内锁定迁移冻结 codec 和九个定向加载分支，保留旧迁移原字节。"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXCLUDED = {"activities": {"executor_id", "running_owner_session_id"},
            "activity_operations": {"executor_id"},
            "html_preview_sessions": {"owner_id", "owner_key_sha256", "control_key_sha256", "boot_id",
                                      "nonce", "cid", "t0_ns", "deadline_ns", "first_stop_receipt", "confirmation_receipt"}}


def split_top(text):
    depth, quote, start = 0, False, 0
    for i, c in enumerate(text):
        if c == "'": quote = not quote
        if not quote:
            depth += (c == "(") - (c == ")")
            if c == "," and depth == 0:
                yield text[start:i].strip(); start = i + 1
    yield text[start:].strip()


def main():
    migrations = sorted((ROOT / "backend/migrations").glob("0[01][0-2]_*.sql"))
    migrations = sorted(p for p in (ROOT / "backend/migrations").glob("*.sql") if int(p.name[:3]) <= 12)
    schema, identities, functions = {}, {}, {}
    for path in migrations:
        raw = path.read_bytes(); identities[path.name] = hashlib.sha256(raw).hexdigest()
        text = re.sub(r"--[^\n]*", "", raw.decode("utf-8-sig").replace("\r\n", "\n"))
        for match in re.finditer(r"CREATE TABLE (?:public\.)?(\w+)\s*\(", text, re.I):
            start = match.end(); depth = 1; quote = False; end = start
            for end in range(start, len(text)):
                c = text[end]
                if c == "'": quote = not quote
                if not quote: depth += (c == "(") - (c == ")")
                if depth == 0: break
            columns = {}
            for line in split_top(text[start:end]):
                column = re.match(r"(\w+)\s+((?:character varying|double precision|timestamp with time zone|[A-Za-z]+)(?:\(\d+\))?(?:\[\])?)", line, re.I)
                if column and column.group(1).upper() not in ("CHECK", "UNIQUE", "PRIMARY", "FOREIGN", "CONSTRAINT"):
                    columns[column.group(1)] = column.group(2).lower()
            schema[match.group(1)] = columns
        for match in re.finditer(r"ALTER TABLE (?:public\.)?(\w+)(.*?);", text, re.I | re.S):
            if match.group(1) not in schema: continue
            for column in re.finditer(r"ADD COLUMN (\w+)\s+([A-Za-z]+(?:\(\d+\))?(?:\[\])?)", match.group(2), re.I):
                schema[match.group(1)][column.group(1)] = column.group(2).lower()
        for match in re.finditer(r"CREATE FUNCTION public\.(\w+)\(.*?\$(\w+)\$;", text, re.S):
            functions[match.group(1)] = match.group(0)
    if len(schema) != 28: raise RuntimeError("业务表身份不完整")
    safes = {t: {c: y for c, y in cols.items() if c not in EXCLUDED.get(t, set())} for t, cols in schema.items()}
    output = ROOT / "backend/app/data_exit/schema.py"
    output.write_text('"""由受信 001—012 冻结的逐列 codec，不采用包内 schema。"""\n'
                      + "COLUMNS = " + repr(safes) + "\n"
                      + "ALL_COLUMNS = " + repr(schema) + "\n"
                      + "MIGRATIONS = " + repr(identities) + "\n", encoding="utf-8")
    changes = {
      "memory_head_guard": [("IF NEW.revision<>1 OR NEW.current_version<>1 OR NEW.state<>'active' THEN", "IF NOT public.data_loading_allowed() AND (NEW.revision<>1 OR NEW.current_version<>1 OR NEW.state<>'active') THEN")],
      "memory_body_guard": [
        ("SELECT state,current_version INTO h FROM public.learning_memories WHERE memory_id=NEW.memory_id FOR KEY SHARE;",
         "IF public.data_loading_allowed() THEN\n  SELECT state,current_version INTO h FROM public.learning_memories WHERE memory_id=NEW.memory_id;\n ELSE\n  SELECT state,current_version INTO h FROM public.learning_memories WHERE memory_id=NEW.memory_id FOR KEY SHARE;\n END IF;"),
        ("IF h.state IS DISTINCT FROM 'active' OR NEW.version NOT IN(h.current_version,h.current_version+1) THEN", "IF NOT public.data_loading_allowed() AND (h.state IS DISTINCT FROM 'active' OR NEW.version NOT IN(h.current_version,h.current_version+1)) THEN")],
      "interview_command_guard": [("IF NEW.effect_applied OR NEW.launch_claimed THEN", "IF NOT public.data_loading_allowed() AND (NEW.effect_applied OR NEW.launch_claimed) THEN")],
      "interview_record_insert_guard": [
        ("OR c.effect_applied OR c.status NOT IN ('accepted','started')", "OR (NOT public.data_loading_allowed() AND (c.effect_applied OR c.status NOT IN ('accepted','started')))"),
        ("OR NOT c.launch_claimed OR c.obsolete OR c.status<>'started'", "OR (NOT public.data_loading_allowed() AND (NOT c.launch_claimed OR c.obsolete OR c.status<>'started'))")],
      "interview_head_guard": [("IF a.status<>'pending'", "IF NOT public.data_loading_allowed() AND (a.status<>'pending'"),
                                ("OR NEW.revision<>1 THEN", "OR NEW.revision<>1) THEN")],
      "html_command_guard": [("IF NEW.status<>'accepted' OR", "IF (NOT public.data_loading_allowed() AND NEW.status<>'accepted') OR"),
                             ("OR NOT public.html_parent_eligible(NEW.activity_id,NEW.context_body::jsonb) THEN", "OR (NOT public.data_loading_allowed() AND NOT public.html_parent_eligible(NEW.activity_id,NEW.context_body::jsonb)) THEN")],
      "html_artifact_insert_guard": [("OR c.status<>'launch_claimed'", "OR (NOT public.data_loading_allowed() AND c.status<>'launch_claimed')"),
         ("OR NOT public.html_parent_eligible(NEW.activity_id,c.context_body::jsonb)", "OR (NOT public.data_loading_allowed() AND NOT public.html_parent_eligible(NEW.activity_id,c.context_body::jsonb))")],
      "html_preview_budget_guard": [("IF NEW.starts_used<>used OR NEW.settled_seconds<>settled OR NEW.reserved_seconds<>reserved", "IF NOT (TG_OP='INSERT' AND public.data_loading_allowed()) AND (NEW.starts_used<>used OR NEW.settled_seconds<>settled OR NEW.reserved_seconds<>reserved)")],
      "html_preview_session_guard": [("IF NEW.state<>'reserved' OR NEW.cid IS NOT NULL OR NEW.elapsed_seconds IS NOT NULL\n   OR NOT public.html_artifact_eligible(NEW.activity_id,NEW.artifact_id) THEN", "IF NOT public.data_loading_allowed() AND (NEW.state<>'reserved' OR NEW.cid IS NOT NULL OR NEW.elapsed_seconds IS NOT NULL\n   OR NOT public.html_artifact_eligible(NEW.activity_id,NEW.artifact_id)) THEN")],
    }
    blocks = []
    for name, replacements in changes.items():
        block = functions[name].replace("CREATE FUNCTION", "CREATE OR REPLACE FUNCTION", 1)
        # 九函数只在 INSERT 分支或专用 INSERT 触发器内使用上述受信身份。
        for before, after in replacements:
            if block.count(before) != 1: raise RuntimeError("定向分支身份漂移 " + name)
            block = block.replace(before, after, 1)
        blocks.append(block)
    blocks.append("""
CREATE FUNCTION public.data_restore_final_shape() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
DECLARE aid uuid;
BEGIN
 IF NOT public.data_loading_allowed() THEN RETURN NULL; END IF;
 aid=NEW.activity_id;
 IF EXISTS(SELECT 1 FROM public.html_preview_budgets b WHERE b.activity_id=aid AND
 (b.starts_used<>(SELECT count(*) FROM public.html_preview_sessions s WHERE s.activity_id=aid)
 OR b.settled_seconds<>(SELECT COALESCE(sum(elapsed_seconds),0) FROM public.html_preview_sessions s WHERE s.activity_id=aid)
 OR b.reserved_seconds<>(SELECT COALESCE(sum(reserve_seconds) FILTER(WHERE elapsed_seconds IS NULL),0) FROM public.html_preview_sessions s WHERE s.activity_id=aid)))
 THEN RAISE EXCEPTION 'archive_preview_budget_mismatch'; END IF;
 RETURN NULL;
END $f$;
ALTER FUNCTION public.data_restore_final_shape() OWNER TO retrolume_data_owner;
REVOKE ALL ON FUNCTION public.data_restore_final_shape() FROM PUBLIC;
CREATE CONSTRAINT TRIGGER data_restore_budget_shape AFTER INSERT ON public.html_preview_budgets
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION public.data_restore_final_shape();
CREATE CONSTRAINT TRIGGER data_restore_session_shape AFTER INSERT ON public.html_preview_sessions
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION public.data_restore_final_shape();
""")
    for table, columns in safes.items():
        safe_columns = ",".join(columns)
        blocks.append(f"GRANT SELECT({safe_columns}) ON public.{table} TO retrolume_data_snapshot;")
        blocks.append(f"GRANT SELECT,INSERT ON public.{table} TO retrolume_data_restore_loader;")
        blocks.append(f"GRANT SELECT ON public.{table} TO retrolume_data_owner;")
        blocks.append(f"CREATE TRIGGER data_runtime_write BEFORE INSERT OR UPDATE OR DELETE ON public.{table} FOR EACH ROW EXECUTE FUNCTION public.data_runtime_write_guard();")
    blocks.append("GRANT UPDATE(current_version) ON public.material_sources TO retrolume_data_restore_loader;")
    blocks.append("GRANT USAGE ON SCHEMA public TO retrolume_data_owner,retrolume_data_app,retrolume_data_snapshot,retrolume_data_restore_loader;")
    # 只读资格不含任何结算、清理或旧执行函数。
    blocks.append("GRANT EXECUTE ON FUNCTION public.memory_revision_readable(uuid,integer),public.memory_revision_eligible(uuid,integer),public.activity_memory_eligible(uuid),public.memory_scope_digest(uuid),public.memory_choice_digest(uuid),public.memory_dependency_digest(uuid,integer),public.memory_dependency_line(public.learning_memory_dependencies),public.interview_result_eligible(uuid,text),public.html_expected_renderer(),public.html_expected_html(),public.html_parent_eligible(uuid,jsonb),public.html_artifact_eligible(uuid,uuid) TO retrolume_data_snapshot,retrolume_data_restore_loader;")
    path = ROOT / "backend/migrations/013_data_exit.sql"
    marker = "-- 下方固定加载分支及逐列 ACL 由项目内受信生成器冻结，不读取数据包定义。"
    core = path.read_text(encoding="utf-8").split(marker)[0] + marker + "\n"
    path.write_text(core + "\n\n".join(blocks) + "\nCOMMIT;\n", encoding="utf-8")
    text=path.read_text(encoding='utf-8')
    data_functions={};business_functions={}
    pattern=r'CREATE (?:OR REPLACE )?FUNCTION public\.(\w+)\(.*? AS \$(\w+)\$(.*?)\$\2\$;'
    for match in re.finditer(pattern,text,re.S):
        name,body=match.group(1),match.group(3)
        fingerprint=hashlib.sha256(re.sub(r'\s+','',body).encode('utf-8')).hexdigest()
        if name.startswith('data_'):
            declaration=match.group(0).split(' AS $')[0]
            data_functions[name]={'sha256':fingerprint,'security_definer':'SECURITY DEFINER' in declaration,
                                 'volatility':'s' if 'STABLE' in declaration else 'i' if 'IMMUTABLE' in declaration else 'v'}
        else:business_functions[name]=fingerprint
    with output.open('a',encoding='utf-8') as stream:
        stream.write('DATA_FUNCTIONS = '+repr(data_functions)+'\nBUSINESS_FUNCTIONS_013 = '+repr(business_functions)+'\n')
        stream.write('MIGRATION_013 = '+repr(hashlib.sha256(path.read_bytes()).hexdigest())+'\n')
        legacy_sources={}
        for name in changes:
            match=re.search(r'AS \$(\w+)\$(.*?)\$\1\$;',functions[name],re.S)
            legacy_sources[name]=match.group(2)
        stream.write('LEGACY_FUNCTION_SOURCES = '+repr(legacy_sources)+'\n')
    # 旧固定业务形状只替换两种部署名字，不从被测新库学习权限白名单。
    import sys
    sys.path.insert(0,str(ROOT/'backend'))
    from app.data_exit.schema_checks import normalize_html_qualification
    frozen=ROOT/'DocuN/evidence/TASK-111/execution/continuation-04/root-14/step-01-qualify/schema-shape.json'
    shape=json.loads(frozen.read_text(encoding='utf-8'))
    profile_path=ROOT/'backend/app/preview/schema-fingerprint.json'
    profile=json.loads(profile_path.read_text(encoding='utf-8'))
    from app.data_exit.contracts import canonical,digest
    if digest(canonical(shape))!=profile['sha256']:raise RuntimeError('旧固定业务形状不是当前十二版指纹')
    owners={name:'retrolume_task111_admin' for name in ('pdf_review_candidates','pdf_review_pages','pdf_extracted_pages')}
    profile['data_exit_013_sha256']=digest(canonical(normalize_html_qualification(shape,owners,'retrolume_task111_app')))
    profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({"tables": len(schema), "changed_guards": list(changes), "migration_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == "__main__": main()
