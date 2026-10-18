"""受限 ZIP_STORED、逐字节校验和精确的发布收据。"""
import hashlib
import os
from pathlib import Path
import re
import struct
import time
import zipfile
from .codec import load_json, lines, decode_row,validate_metadata
from .contracts import DataError, Limits, FORMAT, PROFILE, TABLES, canonical, digest, uuid
from .files import safe_root, regular, publish

UUID_PATH = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def allowed_member(name):
    if not isinstance(name, str) or not name.isascii() or any(ord(c) < 32 for c in name) or any(c in name for c in "\\:\x00"):
        return False
    fixed = {"manifest.json", "README.txt", "codec_description.json", "references/reference_edges.jsonl",
             "metadata/source_control.json", "metadata/operation_history.jsonl", "metadata/tombstones.jsonl"}
    if name in fixed: return True
    if re.fullmatch(r"originals/[0-9a-f]{64}|texts/[0-9a-f]{64}\.txt|summaries/" + UUID_PATH + r"\.txt", name): return True
    return name in {prefix + "/" + table + ".jsonl" for prefix in ("records", "checkpoint") for table in TABLES}


def hash_file(path, limit):
    if regular(path).st_size > limit: raise DataError("capacity_exceeded", 413)
    h, total = hashlib.sha256(), 0
    with Path(path).open("rb") as stream:
        while raw := stream.read(65536):
            total += len(raw)
            if total > limit: raise DataError("capacity_exceeded", 413)
            h.update(raw)
    return h.hexdigest(), total


class PackageReader:
    def __init__(self, path, limits=None):
        self.path, self.limits = Path(path), limits or Limits()
        self.archive = None
        self.manifest = None

    def __enter__(self):
        try:
            self._directory_bound()
            self.archive = zipfile.ZipFile(self.path, "r", allowZip64=False)
            self._verify()
            return self
        except (zipfile.BadZipFile, UnicodeError, ValueError, KeyError, OSError, OverflowError,TypeError,IndexError,AttributeError,RecursionError):
            if self.archive: self.archive.close()
            raise DataError("integrity_failed", 422) from None
        except BaseException:
            if self.archive: self.archive.close()
            raise

    def __exit__(self, *args): self.archive.close()

    def _directory_bound(self):
        length = regular(self.path).st_size
        if length > self.limits.package_bytes: raise DataError("capacity_exceeded", 413)
        if length < 22: raise DataError("integrity_failed", 422)
        with self.path.open("rb") as stream:
            stream.seek(max(0, length - 65557))
            tail = stream.read(65557)
        pos = tail.rfind(b"PK\x05\x06")
        if pos < 0 or len(tail) - pos < 22: raise DataError("integrity_failed", 422)
        _, disk, start_disk, count_disk, count, size, offset, comment = struct.unpack("<4s4H2IH", tail[pos:pos+22])
        if disk or start_disk or count_disk != count or count == 65535 or size == 0xFFFFFFFF or offset == 0xFFFFFFFF:
            raise DataError("unsupported_format", 415)
        if count > self.limits.members or size > self.limits.directory_bytes:
            raise DataError("capacity_exceeded", 413)
        if pos + 22 + comment != len(tail) or offset + size != length - len(tail) + pos:
            raise DataError("integrity_failed", 422)

    def _verify(self):
        infos = self.archive.infolist()
        seen, total, locations = set(), 0, []
        for info in infos:
            mode = info.external_attr >> 16
            if (not allowed_member(info.filename) or info.filename.casefold() in seen or info.is_dir()
                or info.flag_bits & 1 or info.compress_type != zipfile.ZIP_STORED or info.compress_size != info.file_size
                or mode & 0o170000 not in (0, 0o100000) or info.extra):
                raise DataError("unsupported_format", 415)
            seen.add(info.filename.casefold())
            total += info.file_size
            locations.append(info.header_offset)
            if total > self.limits.package_bytes: raise DataError("capacity_exceeded", 413)
            if info.filename == "manifest.json" and info.file_size > self.limits.manifest_bytes:
                raise DataError("capacity_exceeded", 413)
        if not locations or min(locations) != 0: raise DataError("unsupported_format", 415)
        if "manifest.json" not in seen: raise DataError("integrity_failed", 422)
        manifest = load_json(self.archive.read("manifest.json"), self.limits)
        required = {"format", "format_version", "package_id", "package_kind", "codec_profile", "source_business_table_count",
                    "snapshot_control_domain_count", "snapshot", "contents", "availability", "scope", "completion", "restore_eligible", "root_sha256"}
        if set(manifest) != required or manifest["format"] != FORMAT or manifest["format_version"] != 1 or manifest["codec_profile"] != PROFILE:
            raise DataError("unsupported_format", 415)
        uuid(manifest["package_id"])
        if manifest["package_kind"] not in ("portable_export", "restore_checkpoint") or manifest["source_business_table_count"] != 28 or manifest["snapshot_control_domain_count"] != 3:
            raise DataError("unsupported_format", 415)
        if type(manifest['format_version']) is not int:raise DataError('unsupported_format',415)
        point=manifest['snapshot']
        if (not isinstance(point,dict) or set(point)!={'logical_time_utc','database_snapshot','source_schema_profile',
                'source_dataset_id','runtime_authority_included','browser_drafts_included'}
            or point['source_schema_profile']!=PROFILE or point['runtime_authority_included'] is not False
            or point['browser_drafts_included'] is not False
            or not isinstance(point['database_snapshot'],str)
            or re.fullmatch(r'[0-9]+:[0-9]+:(?:[0-9]+(?:,[0-9]+)*)?',point['database_snapshot']) is None):
            raise DataError('codec_mismatch',422)
        uuid(point['source_dataset_id'])
        from datetime import datetime
        try:
            if datetime.fromisoformat(point['logical_time_utc']).utcoffset() is None:raise ValueError()
        except (TypeError,ValueError):raise DataError('codec_mismatch',422) from None
        if manifest["completion"] not in ("complete", "incomplete") or type(manifest["restore_eligible"]) is not bool:
            raise DataError("integrity_failed", 422)
        root = dict(manifest); expected = root.pop("root_sha256")
        if digest(canonical(root)) != expected: raise DataError("integrity_failed", 422)
        entries = manifest["contents"]
        if not isinstance(entries, list) or len(entries) > self.limits.members: raise DataError("capacity_exceeded", 413)
        if len({e["path"] for e in entries}) != len(entries) or {e["path"] for e in entries} | {"manifest.json"} != {i.filename for i in infos}:
            raise DataError("integrity_failed", 422)
        total_rows = 0
        for entry in entries:
            if set(entry) != {"path", "kind", "availability", "bytes", "sha256"} or not allowed_member(entry["path"]) or entry["path"] == "manifest.json" or entry["availability"] != "present":
                raise DataError("integrity_failed", 422)
            if not isinstance(entry["bytes"], str) or re.fullmatch(r"0|[1-9][0-9]*", entry["bytes"]) is None or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None:
                raise DataError("integrity_failed", 422)
            h, count = hashlib.sha256(), 0
            with self.archive.open(entry["path"]) as stream:
                while raw := stream.read(65536):
                    h.update(raw); count += len(raw)
                    if count > self.limits.package_bytes or count > int(entry["bytes"]): raise DataError("capacity_exceeded", 413)
            if h.hexdigest() != entry["sha256"] or count != int(entry["bytes"]): raise DataError("integrity_failed", 422)
            if entry["path"].startswith("originals/") and (count > self.limits.original_bytes or entry["path"].split("/")[1] != h.hexdigest()):
                raise DataError("integrity_failed", 422)
            if entry["path"].endswith(".jsonl"):
                with self.archive.open(entry["path"]) as stream:
                    for row in lines(stream, self.limits):
                        total_rows += 1
                        if total_rows > self.limits.rows * (2 if manifest["package_kind"] == "restore_checkpoint" else 1): raise DataError("capacity_exceeded", 413)
                        if entry["path"].startswith(("records/", "checkpoint/")):
                            decode_row(entry["path"].split("/")[1][:-6], row)
                        elif entry['path'].startswith('metadata/'):
                            validate_metadata(entry['path'].split('/')[1][:-6],row)
            elif entry["path"].endswith(".json"):
                if count > self.limits.manifest_bytes: raise DataError("capacity_exceeded", 413)
                value=load_json(self.archive.read(entry["path"]), self.limits)
                if entry['path']=='metadata/source_control.json':validate_metadata('source_control',value)
                if entry['path']=='codec_description.json':
                    from .schema import COLUMNS,MIGRATIONS
                    from .codec import TRANSFORMS
                    if value!={'profile':PROFILE,'columns':COLUMNS,'transformations':TRANSFORMS,'bigint_encoding':'decimal_string',
                        'text_encoding':'UTF-8 原字符串','migration_sha256':MIGRATIONS}:raise DataError('codec_mismatch',422)
        mandatory = {"records/" + t + ".jsonl" for t in TABLES} | {
            "README.txt", "codec_description.json", "metadata/source_control.json", "metadata/operation_history.jsonl",
            "metadata/tombstones.jsonl", "references/reference_edges.jsonl"}
        if not {name.casefold() for name in mandatory}.issubset(seen): raise DataError("integrity_failed", 422)
        if manifest["package_kind"] == "restore_checkpoint" and not {"checkpoint/" + t + ".jsonl" for t in TABLES}.issubset(seen):
            raise DataError("integrity_failed", 422)
        by_path={entry['path']:entry for entry in entries}
        if manifest['package_kind']=='restore_checkpoint':
            for table in TABLES:
                left,right=by_path['records/'+table+'.jsonl'],by_path['checkpoint/'+table+'.jsonl']
                if (left['bytes'],left['sha256'])!=(right['bytes'],right['sha256']):raise DataError('integrity_failed',422)
        control=load_json(self.archive.read('metadata/source_control.json'),self.limits)
        if control['dataset_id']!=point['source_dataset_id']:raise DataError('codec_mismatch',422)
        allowed_availability = {"present", "deleted", "revoked", "never_received", "legacy_without_payload", "missing_optional", "missing_required"}
        if not isinstance(manifest["availability"], list) or any(r.get("availability") not in allowed_availability for r in manifest["availability"]):
            raise DataError("integrity_failed", 422)
        if manifest["restore_eligible"] != (manifest["package_kind"] == "restore_checkpoint" and manifest["completion"] == "complete"):
            raise DataError("integrity_failed", 422)
        if (manifest['completion']=='complete')==any(r['availability']=='missing_required' for r in manifest['availability']):
            raise DataError('integrity_failed',422)
        self.manifest = manifest

    def rows(self, table):
        if table not in TABLES: raise ValueError("表未受信")
        with self.archive.open("checkpoint/" + table + ".jsonl") as stream:
            yield from lines(stream, self.limits)


class DataPackageService:
    def __init__(self, hub, snapshot, backup_root, limits=None, observer=None):
        self.hub, self.snapshot, self.root = hub, snapshot, safe_root(backup_root)
        self.limits = limits or Limits()
        self.observer=observer
        self.packages = self.root / "packages"
        if not self.packages.exists(): self.packages.mkdir()
        safe_root(self.packages)

    def path(self, package_id): return self.packages / (uuid(package_id) + ".rldata")

    def capture_and_publish(self, job_id, scope):
        job = self.hub.get(job_id)
        if job["state"] != "prepared": return self.reconcile(job_id)
        with self.hub.operation_lock.acquire(True, timeout=1):
            def check_cancel():
                if self.hub.get(job_id)["state"] == "cancelled": raise DataError("operation_cancelled")
            def stage(value):
                current = self.hub.get(job_id)
                if current['state']=='cancelled':raise DataError('operation_cancelled')
                receipt=self.hub.update_job(job_id, current["revision"], state="running", stage=value)
                if self.observer is not None:self.observer(receipt)
            try:
                captured = self.snapshot.capture(job_id, job["kind"], scope, check_cancel=check_cancel, on_stage=stage)
                stage("verifying")
                manifest = {"format": FORMAT, "format_version": 1, "package_id": job_id, "package_kind": job["kind"],
                            "codec_profile": PROFILE, "source_business_table_count": 28, "snapshot_control_domain_count": 3,
                            "snapshot": {**captured.point, "source_schema_profile": PROFILE,
                                         "source_dataset_id": captured.source_control["dataset_id"], "runtime_authority_included": False,
                                         "browser_drafts_included": False}, "contents": captured.entries,
                            "availability": captured.availability, "scope": captured.scope,
                            "completion": "incomplete" if any(e["availability"] == "missing_required" for e in captured.availability) else "complete",
                            "restore_eligible": job["kind"] == "restore_checkpoint"}
                manifest["root_sha256"] = digest(canonical(manifest))
                raw = canonical(manifest).encode("utf-8")
                if len(raw) > self.limits.manifest_bytes: raise DataError("capacity_exceeded", 413)
                temporary = self.packages / (job_id + ".pending")
                with temporary.open("xb") as output:
                    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
                        archive.writestr("manifest.json", raw)
                        for entry in captured.entries:
                            check_cancel()
                            archive.write(captured.root / entry["path"], entry["path"])
                    output.flush(); os.fsync(output.fileno())
                with PackageReader(temporary, self.limits): pass
                check_cancel()
                publish(temporary, self.path(job_id))
                package_sha, count = hash_file(self.path(job_id), self.limits.package_bytes)
                current = self.hub.get(job_id)
                receipt = self.hub.update_job(job_id, current["revision"], state="published", stage="published",
                    package_id=job_id, root_sha256=manifest["root_sha256"], package_sha256=package_sha,
                    counts={"bytes": str(count), "files": len(captured.entries) + 1, "rows": sum(map(len, captured.rows.values()))})
                if self.observer is not None:self.observer(receipt)
                return receipt
            except BaseException as error:
                # 完整文件发布与 Hub 收据是两个点，失败不生成第二个包。
                try:
                    current = self.hub.get(job_id)
                    if current["state"] not in ("cancelled", "published"):
                        state = "published_unconfirmed" if self.path(job_id).exists() else "failed"
                        self.hub.update_job(job_id, current["revision"], state=state, stage=state,
                                            error_code=error.code if isinstance(error, DataError) else "storage_unavailable")
                except (DataError, OSError): pass
                raise

    def reconcile(self, job_id):
        receipt = self.hub.reconcile(job_id)
        path = self.path(job_id)
        if path.exists():
            with PackageReader(path, self.limits) as reader:
                if reader.manifest["package_id"] != job_id: raise DataError("integrity_failed", 422)
                receipt.update(file_publication="confirmed", package_id=job_id, root_sha256=reader.manifest["root_sha256"])
        return receipt

    def download(self, package_id):
        receipt=self.hub.get(uuid(package_id))
        path = self.path(package_id)
        if not path.exists(): raise DataError("package_incomplete")
        with PackageReader(path, self.limits) as reader:
            if receipt.get('root_sha256') and receipt['root_sha256']!=reader.manifest['root_sha256']:raise DataError('integrity_failed',422)
        return path
