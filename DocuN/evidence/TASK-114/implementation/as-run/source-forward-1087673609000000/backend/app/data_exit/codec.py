"""固定逐列编码，原正文不重新序列化，控制身份不入包。"""
from datetime import datetime, timezone
import json
import math
import re
from uuid import UUID, uuid4
from .contracts import DataError, Limits, canonical, digest


def load_json(raw, limits=None):
    limits = limits or Limits()
    if isinstance(raw, bytes):
        if raw.startswith(b"\xef\xbb\xbf"):
            raise DataError("integrity_failed", 422)
        try:
            raw = raw.decode("utf-8")
        except UnicodeError:
            raise DataError("integrity_failed", 422) from None
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise DataError("integrity_failed", 422)
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(DataError("integrity_failed", 422)))
    except (ValueError, UnicodeError, RecursionError):
        raise DataError("integrity_failed", 422) from None
    def check(value, depth=0):
        if depth > limits.json_depth:
            raise DataError("capacity_exceeded", 413)
        if isinstance(value, str) and any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise DataError("integrity_failed", 422)
        if isinstance(value, float) and not math.isfinite(value):
            raise DataError("integrity_failed", 422)
        if isinstance(value, dict):
            for key, child in value.items():
                check(key, depth + 1); check(child, depth + 1)
        elif isinstance(value, list):
            for child in value: check(child, depth + 1)
    check(value)
    return value


def plain(value):
    if isinstance(value, UUID): return str(value)
    if isinstance(value, datetime): return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, dict): return {key: plain(v) for key, v in value.items()}
    if isinstance(value, (list, tuple)): return [plain(v) for v in value]
    return value


def encode_row(table, row):
    from .schema import COLUMNS
    encoded = {}
    for column, kind in COLUMNS[table].items():
        value = row[column]
        if value is not None and kind == "bigint":
            value = str(value)
        encoded[column] = plain(value)
    return encoded


def decode_row(table, row):
    from .schema import COLUMNS
    if not isinstance(row, dict) or set(row) != set(COLUMNS[table]):
        raise DataError("codec_mismatch", 422)
    result = {}
    for column, kind in COLUMNS[table].items():
        value = row[column]
        if value is None:
            result[column] = None
            continue
        if kind.endswith("[]"):
            if not isinstance(value, list): raise DataError("codec_mismatch", 422)
            if kind == "uuid[]":
                if any(not isinstance(v, str) or str(UUID(v)) != v for v in value): raise DataError("codec_mismatch", 422)
            elif any(not isinstance(v, str) for v in value): raise DataError("codec_mismatch", 422)
        elif kind in ("integer", "smallint"):
            if type(value) is not int or not -(2**31) <= value < 2**31:
                raise DataError("codec_mismatch", 422)
        elif kind == "bigint":
            if not isinstance(value, str) or re.fullmatch(r"-?(0|[1-9][0-9]*)", value) is None:
                raise DataError("codec_mismatch", 422)
            value = int(value)
            if not -(2**63) <= value < 2**63: raise DataError("codec_mismatch", 422)
        elif kind == "boolean":
            if type(value) is not bool: raise DataError("codec_mismatch", 422)
        elif kind == "jsonb":
            from psycopg.types.json import Jsonb
            value = Jsonb(value)
        elif kind == "uuid":
            if not isinstance(value, str) or str(UUID(value)) != value:
                raise DataError("codec_mismatch", 422)
            value = UUID(value)
        elif kind in ("timestamptz", "timestamp with time zone"):
            try:
                value = datetime.fromisoformat(value)
                if value.utcoffset() is None: raise ValueError()
            except (TypeError, ValueError):
                raise DataError("codec_mismatch", 422) from None
        elif not isinstance(value, str) or "\x00" in value:
            raise DataError("codec_mismatch", 422)
        result[column] = value
    if table == "activities":
        result["executor_id"] = "archived.non_authorizing" if row["status"] == "running" else None
        result["running_owner_session_id"] = None
    elif table == "activity_operations":
        result["executor_id"] = "archived.non_authorizing"
    elif table == "html_preview_sessions":
        import secrets
        result.update(owner_id=uuid4(), boot_id=uuid4(), nonce=secrets.token_hex(32),
                      owner_key_sha256=digest(secrets.token_bytes(32)), control_key_sha256=digest(secrets.token_bytes(32)),
                      cid=None, t0_ns=1, deadline_ns=1 + row["reserve_seconds"] * 10**9,
                      first_stop_receipt=None, confirmation_receipt=None)
    return result


def lines(stream, limits=None):
    limits = limits or Limits()
    rows = 0
    while True:
        raw = stream.readline(limits.json_line_bytes + 1)
        if not raw: break
        if len(raw) > limits.json_line_bytes or not raw.endswith(b"\n"):
            raise DataError("capacity_exceeded", 413)
        rows += 1
        if rows > limits.rows: raise DataError("capacity_exceeded", 413)
        yield load_json(raw[:-1], limits)


TRANSFORMS = {
    "activities.executor_id": "running 时使用 archived.non_authorizing 占位，原执行身份排除",
    "activities.running_owner_session_id": "NULL，不认领旧窗口",
    "activity_operations.executor_id": "archived.non_authorizing，不授出站资格",
    "html_preview_sessions.owner_id/boot_id/nonce/key_hashes": "随机不可用占位，原秘密排除并立即丢弃占位原密钥",
    "html_preview_sessions.cid/receipts": "NULL，不授停止证明或退款资格",
    "html_preview_sessions.t0_ns/deadline_ns": "1 与 1+reserve_seconds*1000000000，clock_origin=archive_placeholder",
    "data_control": "目标身份由可信工厂新建，源仅观察",
    "data_operation_jobs": "archive_history，authorizes_reference=false",
}

CONTROL_FIELDS={'dataset_id','schema_profile','created_at','source_instance_observed','mode_observed','source_snapshot_id','source_root_sha256'}
HISTORY_FIELDS={'origin_source_row_id','record_class','business_key','kind','request_sha256','observed_state','observed_stage',
                'control_seq_observed','package_id','root_sha256','counts','error_code','created_at','updated_at','terminal_at','scope_summary','archive_origin_source_row_id'}
TOMBSTONE_FIELDS={'tombstone_id','entity_kind','entity_id','effective_revision','business_id_observed','deleted_at',
                  'cleanup_state_observed','manifest_sha256','hash_size_targets'}


def validate_metadata(name,row):
    from .contracts import PROFILE,uuid
    expected=CONTROL_FIELDS if name=='source_control' else HISTORY_FIELDS if name=='operation_history' else TOMBSTONE_FIELDS
    if not isinstance(row,dict) or set(row)!=expected:raise DataError('codec_mismatch',422)
    def timestamp(field,optional=False):
        value=row[field]
        if value is None and optional:return
        try:
            if datetime.fromisoformat(value).utcoffset() is None:raise ValueError()
        except (TypeError,ValueError):raise DataError('codec_mismatch',422) from None
    def hex_value(field,optional=False):
        value=row[field]
        if value is None and optional:return
        if not isinstance(value,str) or re.fullmatch(r'[0-9a-f]{64}',value) is None:raise DataError('codec_mismatch',422)
    if name=='source_control':
        uuid(row['dataset_id']);uuid(row['source_instance_observed'])
        if row['schema_profile']!=PROFILE or row['mode_observed'] not in ('normal','loading','frozen','restored_readonly'):raise DataError('codec_mismatch',422)
        timestamp('created_at');hex_value('source_root_sha256',True)
        if row['source_snapshot_id'] is not None:uuid(row['source_snapshot_id'])
    elif name=='operation_history':
        uuid(row['origin_source_row_id'])
        if row['record_class'] not in ('hub_observation','reference_fence','archive_history'):raise DataError('codec_mismatch',422)
        for field in ('created_at','updated_at','terminal_at'):timestamp(field,field=='terminal_at')
        for field in ('request_sha256','root_sha256'):hex_value(field,True)
        for field in ('package_id','archive_origin_source_row_id'):
            if row[field] is not None:uuid(row[field])
        if (not isinstance(row['counts'],dict) or not isinstance(row['scope_summary'],dict)
            or any(not isinstance(row[field],str) or len(row[field])>128 for field in ('kind','observed_state'))
            or (row['control_seq_observed'] is not None and (type(row['control_seq_observed']) is not int or not 0<=row['control_seq_observed']<2**63))):raise DataError('codec_mismatch',422)
    else:
        uuid(row['tombstone_id']);uuid(row['entity_id'])
        if row['entity_kind'] not in ('source','memory') or type(row['effective_revision']) is not int or row['effective_revision']<=0:raise DataError('codec_mismatch',422)
        timestamp('deleted_at');hex_value('manifest_sha256')
        if row['cleanup_state_observed'] not in ('pending','done','shared_retained','physical_result_unknown','archive_observation'):raise DataError('codec_mismatch',422)
        if not isinstance(row['hash_size_targets'],list):raise DataError('codec_mismatch',422)
        for target in row['hash_size_targets']:
            if set(target)!={'sha256','size'} or re.fullmatch(r'[0-9a-f]{64}',target['sha256']) is None or not 0<=int(target['size'])<=5*1024**2:raise DataError('codec_mismatch',422)
