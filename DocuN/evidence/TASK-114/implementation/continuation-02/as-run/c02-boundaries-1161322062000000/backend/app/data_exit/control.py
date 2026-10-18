"""私有日志为长期操作和选择器的唯一权威；GET 不执行动作。"""
import ctypes
import json
import os
from pathlib import Path
import struct
from uuid import uuid4
from datetime import datetime, timezone
from .contracts import DataContext, DataError, canonical, digest, business_key, uuid
from .files import RootLease, safe_root, regular, publish,private_file

MAX_FRAME, MAX_JOURNAL = 65536, 64 * 1024**2
TAIL = b"\nCOMMIT:"
PUBLIC_JOB = ("job_id", "business_key", "kind", "request_sha256", "state", "stage", "revision",
              "control_seq", "package_id", "root_sha256", "plan_id", "target_id", "error_code",
              "selection_generation", "created_at", "updated_at", "counts", "latest_status")
PUBLIC_JOB += ('receipt_id','receipt_sha256')


class ControlHub:
    def __init__(self, root):
        self.root = safe_root(root)
        private_file(self.root,directory=True)
        self.lock = RootLease(self.root, ".journal.lock")
        self.operation_lock = RootLease(self.root, ".operation.lock")
        self.path = self.root / "journal.bin"
        with self.lock.acquire(True):
            if not self.path.exists():
                with self.path.open("xb") as stream:
                    stream.flush(); os.fsync(stream.fileno())
                private_file(self.path)
                self._append([], "hub.init", {"control_id": str(uuid4())})
            events, tail = self._read()
            if not events or events[0]["kind"] != "hub.init":
                raise DataError("control_unavailable", 503)
            self.control_id = events[0]["payload"]["control_id"]

    def _read(self):
        regular(self.path)
        if self.path.stat().st_size > MAX_JOURNAL:
            raise DataError("capacity_exceeded", 413)
        events, previous = [], "0" * 64
        with self.path.open("rb") as stream:
            while True:
                header = stream.read(4)
                if not header:
                    return events, False
                if len(header) != 4:
                    return events, True
                length = struct.unpack("!I", header)[0]
                if not 1 <= length <= MAX_FRAME:
                    raise DataError("control_corrupt", 503)
                raw = stream.read(length)
                tail = stream.read(len(TAIL) + 65)
                if len(raw) != length or len(tail) != len(TAIL) + 65:
                    return events, True
                if tail != TAIL + digest(raw).encode("ascii") + b"\n":
                    raise DataError("control_corrupt", 503)
                try:
                    from .codec import load_json
                    event = load_json(raw)
                    valid = (event["format"] == "data.control.v1" and event["seq"] == len(events) + 1
                             and event["prev_hash"] == previous and event["body_hash"] == digest(canonical(event["payload"])))
                except (KeyError, ValueError, TypeError):
                    valid = False
                if not valid:
                    raise DataError("control_corrupt", 503)
                if raw != canonical(event).encode('utf-8'):
                    raise DataError('control_corrupt',503)
                previous = digest(raw)
                events.append(event)

    def _append(self, events, kind, payload):
        event = {"format": "data.control.v1", "seq": len(events) + 1,
                 "prev_hash": "0" * 64 if not events else digest(canonical(events[-1])),
                 "event_id": str(uuid4()), "kind": kind, "payload": payload,
                 "body_hash": digest(canonical(payload)), "utc": datetime.now(timezone.utc).isoformat()}
        raw = canonical(event).encode("utf-8")
        frame = struct.pack("!I", len(raw)) + raw + TAIL + digest(raw).encode("ascii") + b"\n"
        if len(raw) > MAX_FRAME or self.path.stat().st_size + len(frame) > MAX_JOURNAL:
            raise DataError("capacity_exceeded", 413)
        with self.path.open("ab") as stream:
            stream.write(frame); stream.flush(); os.fsync(stream.fileno())
        return event

    @staticmethod
    def replay(events):
        state = {"jobs": {}, "plans": {}, "targets": {}, "selection": None, "fence": None, "owned": {}, "deletions": {}, 'source':None}
        for event in events:
            kind, p = event["kind"], event["payload"]
            if kind in ("job.create", "job.update"):
                old = state["jobs"].get(p["job_id"], {})
                state["jobs"][p["job_id"]] = {**old, **p, "control_seq": event["seq"]}
            elif kind == "plan.create":
                state["plans"][p["plan_id"]] = p
            elif kind in ("target.register", "target.seal"):
                state["targets"][p["target_id"]] = {**state["targets"].get(p["target_id"], {}), **p}
            elif kind == "selector_commit":
                state["selection"] = p
            elif kind == "maintenance.fence":
                state["fence"] = p
            elif kind in ("owned.begin", "owned.end"):
                state["owned"][p["owned_id"]] = {**state["owned"].get(p["owned_id"], {}), **p}
            elif kind == "deletion.observe":
                state["deletions"][p["entity_kind"] + ":" + p["entity_id"]] = p
            elif kind=='source.register':state['source']=p
        return state

    def state(self):
        with self.lock.acquire():
            events, _ = self._read()
            return self.replay(events)

    def commit(self, kind, payload, *, validate=None):
        with self.lock.acquire(True, timeout=1):
            events, tail = self._read()
            if tail:
                raise DataError("control_tail_unconfirmed", 503)
            state = self.replay(events)
            if validate is not None:
                validate(state)
            return self._append(events, kind, payload)

    def assert_writable(self):
        with self.lock.acquire():
            events, tail = self._read()
            if tail:
                raise DataError("control_tail_unconfirmed", 503)
            return self.replay(events)

    @staticmethod
    def receipt(job):
        return {key: job[key] for key in PUBLIC_JOB if key in job}

    def current_receipt(self, state, job):
        receipt = self.receipt(job)
        if job.get('completion_protocol') == 1 and job['state'] in ('published','received','verified','active_readonly','deleted','deleted_pending'):
            confirmation=job.get('completion_confirmed_ns')
            deadline=job.get('execution',{}).get('deadline_ns')
            if type(confirmation) is not int or type(deadline) is not int or not 0 < confirmation < deadline:
                receipt.update(state={'portable_export':'published_unconfirmed','restore_checkpoint':'published_unconfirmed',
                    'upload':'upload_unconfirmed','restore':'restore_unconfirmed','activate':'activation_unconfirmed',
                    'source_delete':'deletion_unconfirmed'}[job['kind']],stage='completion_unconfirmed')
        if job['kind']=='restore':
            receipt.update(plan_id=job['scope']['plan_id'],plan_sha256=job['scope']['plan_sha256'])
        selection = state['selection']
        if selection is not None and selection.get('activation_job_id') == job['job_id']:
            receipt.update(selector_commit='confirmed',selection_generation=selection['generation'],target_id=selection['target_id'])
            if job['state'] != 'active_readonly':
                receipt.update(state='activation_unconfirmed', stage='selector_committed')
        return receipt

    def create_or_get_job(self, command, origin_context):
        request_sha = digest(command.normalized())
        key = business_key(command.business_key)
        with self.lock.acquire(True, timeout=1):
            events, tail = self._read()
            state = self.replay(events)
            for job in state["jobs"].values():
                if job["business_key"] == key:
                    if job["request_sha256"] != request_sha or job["kind"] != command.kind:
                        raise DataError("request_conflict")
                    return self.current_receipt(state, job)
            if tail:
                raise DataError("control_tail_unconfirmed", 503)
            if len(state["jobs"]) >= 256:
                raise DataError("capacity_exceeded", 413)
            now = datetime.now(timezone.utc).isoformat()
            job = {"job_id": str(uuid4()), "business_key": key, "kind": command.kind,
                   "request_sha256": request_sha, "scope": command.scope,
                   "origin": origin_context.public(), "state": "prepared", "stage": "prepared",
                   "revision": 1, "created_at": now, "updated_at": now, "execution_protocol": 2, "completion_protocol": 1}
            event = self._append(events, "job.create", job)
            return self.receipt({**job, "control_seq": event["seq"]})

    def update_job(self, job_id, expected_revision, *, expected_states=None, validate=None, **changes):
        uuid(job_id)
        changes.pop("control_seq", None)
        forbidden = {"business_key", "kind", "request_sha256", "origin", "scope", "job_id", "revision"}
        if forbidden.intersection(changes):
            raise ValueError("不可改写操作身份")
        payload = {"job_id": job_id, **changes, "revision": expected_revision + 1,
                   "updated_at": datetime.now(timezone.utc).isoformat()}
        def check(state):
            job = state["jobs"].get(job_id)
            if job is None or job["revision"] != expected_revision:
                raise DataError("request_conflict")
            if expected_states is not None and job['state'] not in expected_states:
                raise DataError('request_conflict')
            if job['state'] in ('cancelled', 'cancel_requested') and changes.get('state', job['state']) not in ('cancel_requested', 'cancelled', 'cleanup_unconfirmed'):
                raise DataError('operation_cancelled')
            if changes.get('state') in ('published', 'received', 'verified', 'active_readonly', 'deleted', 'deleted_pending'):
                from .operations import validate_success
                if job.get('execution_protocol') != 2 or validate is None or expected_states != ('committing',):
                    raise DataError('operation_authority_unknown')
                validate_success(job, changes['state'])
            if validate is not None:
                validate(job)
        self.commit("job.update", payload, validate=check)
        return self.get(job_id)

    def change_job(self, job_id, decide):
        """短锁内读取、验证与CAS；decide仅计算字段，不能进行I/O。"""
        uuid(job_id)
        with self.lock.acquire(True, timeout=1):
            events, tail = self._read()
            if tail: raise DataError('control_tail_unconfirmed', 503)
            state = self.replay(events)
            job = state['jobs'].get(job_id)
            if job is None: raise DataError('not_found', 404)
            changes = decide(job)
            if changes:
                payload = {'job_id': job_id, **changes, 'revision': job['revision'] + 1,
                           'updated_at': datetime.now(timezone.utc).isoformat()}
                event = self._append(events, 'job.update', payload)
                job = {**job, **payload, 'control_seq': event['seq']}
            return self.current_receipt(state, job)

    def get(self, job_id):
        state = self.state()
        job = state["jobs"].get(uuid(job_id))
        if job is None:
            raise DataError("not_found", 404)
        return self.current_receipt(state, job)

    def get_by_key(self, key, kind=None):
        business_key(key)
        state = self.state()
        for job in state["jobs"].values():
            if job["business_key"] == key and (kind is None or kind == job["kind"]):
                return self.current_receipt(state, job)
        raise DataError("not_found", 404)

    def reconcile(self, job_id):
        return {**self.get(job_id), "reconcile": "journal_confirmed"}

    def artifact_path(self, category, identity):
        if category not in ("plans", "credentials", "overlays", "receipts"):
            raise ValueError("私有类别未受信")
        uuid(identity)
        return self.root / f"{category}-{identity}.bin"

    def save_artifact(self, category, identity, data, check=lambda: None):
        check()
        path = self.artifact_path(category, identity)
        temporary = path.with_suffix(".pending")
        with temporary.open("xb") as stream:
            check()
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        check()
        private_file(temporary)
        publish(temporary, path, check=check)
        # 只删除本调用准确临时文件，发布原件保留。
        temporary.unlink()
        check()
        return digest(data)

    def read_artifact(self, category, identity, expected_sha=None, limit=64 * 1024**2):
        path = self.artifact_path(category, identity)
        if regular(path).st_size > limit:
            raise DataError("capacity_exceeded", 413)
        data = path.read_bytes()
        if expected_sha is not None and digest(data) != expected_sha:
            raise DataError("integrity_failed", 422)
        return data


class CredentialVault:
    """只读凭据仅以当前 Windows 用户的 DPAPI 密文持久保存。"""
    def __init__(self, hub):
        self.hub = hub

    @staticmethod
    def _crypt(data, decrypt=False):
        if os.name != "nt":
            raise DataError("credential_unavailable", 503)
        from ctypes import wintypes
        class Blob(ctypes.Structure):
            _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]
        buf = ctypes.create_string_buffer(data)
        incoming = Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)))
        outgoing = Blob()
        dll = ctypes.WinDLL("crypt32", use_last_error=True)
        function = dll.CryptUnprotectData if decrypt else dll.CryptProtectData
        function.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
        if not function(ctypes.byref(incoming), None, None, None, None, 1, ctypes.byref(outgoing)):
            raise DataError("credential_unavailable", 503)
        try:
            return ctypes.string_at(outgoing.data, outgoing.size)
        finally:
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.LocalFree.argtypes = [ctypes.c_void_p]
            kernel.LocalFree(outgoing.data)

    def save(self, credentials):
        identity = str(uuid4())
        encrypted = self._crypt(canonical(credentials).encode("utf-8"))
        sha = self.hub.save_artifact("credentials", identity, encrypted)
        return {"id": identity, "sha256": sha}

    def read(self, reference):
        try:
            encrypted = self.hub.read_artifact("credentials", reference["id"], reference["sha256"], 65536)
            return json.loads(self._crypt(encrypted, True))
        except (OSError, ValueError, KeyError):
            raise DataError("credential_unavailable", 503) from None
