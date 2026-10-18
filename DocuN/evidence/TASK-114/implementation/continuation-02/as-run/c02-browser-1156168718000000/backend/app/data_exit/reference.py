"""活原件 pin、PG ticket/epoch 与准确清理的两阶段协议。"""
from contextlib import contextmanager
from dataclasses import dataclass
import secrets
from uuid import uuid4
from .contracts import DataError
from .files import RootLease
from app.storage.originals import Original


@dataclass(frozen=True)
class PreparedReference:
    source_id: str
    version_id: str
    candidate_id: str | None
    sha256: str
    size: int


class ReferencePin:
    def __init__(self, coordinator, lease, prepared, permit):
        self.coordinator, self.lease, self.prepared, self.permit = coordinator, lease, prepared, permit
        self.ticket_id, self.nonce = str(uuid4()), secrets.token_hex(32)
        self.epoch, self.committed = None, False

    def check(self, root=None, prepared=None):
        self.lease.check()
        self.permit.check()
        if self.lease.exclusive or (root is not None and self.coordinator.root != root):
            raise DataError("reference_pin_invalid")
        if prepared is not None and prepared != self.prepared:
            raise DataError("reference_identity_invalid")

    def bind(self, connection):
        self.check()
        connection.execute("SELECT public.data_reference_bind(%s,%s)", (self.ticket_id, self.nonce))

    def commit(self, connection):
        self.check()
        connection.execute("SELECT public.data_reference_commit(%s,%s)", (self.ticket_id, self.nonce))


class LoadingReferencePin:
    """工厂 loading 权经真实专用连接核对后保护目标原件发布。"""
    def __init__(self,factory,target,lease,prepared):
        self.factory,self.target,self.lease,self.prepared=factory,target,lease,prepared
        import psycopg
        with psycopg.connect(factory.loader_dsn(target),connect_timeout=3) as connection:
            row=connection.execute('SELECT public.data_loading_allowed(),public.data_state()').fetchone()
        if row is None or row[0] is not True or tuple(str(row[1][key]) for key in ('dataset_id','instance_id','originals_root_id'))!=(target.dataset_id,target.instance_id,target.root_id):
            raise DataError('target_loading_identity_unknown',503)

    def check(self,root=None,prepared=None):
        self.lease.check()
        expected=self.target.data_root/'originals'
        state=self.factory.hub.state()
        target=state['targets'].get(self.target.target_id)
        if (self.lease.exclusive or self.lease.lock.root!=expected or (root is not None and root!=expected)
            or self.target.target_id not in self.factory._ephemeral or target is None or target.get('state')!='allocated'
            or state['jobs'][self.target.job_id]['state']!='running'):
            raise DataError('reference_pin_invalid')
        if prepared is not None and self.prepared!=prepared:raise DataError('reference_identity_invalid')


class OriginalReferenceCoordinator:
    def __init__(self, store, repository, mutation_gate, maintenance_key):
        self.store, self.repository, self.gate = store, repository, mutation_gate
        self.root, self.lease = store.root, RootLease(store.root)
        self.maintenance_key = maintenance_key
        state = repository.state()
        if state["mode"] != "normal": raise DataError("mode_unknown", 503)
        self.root_id = state["originals_root_id"]
        import json,os
        binding=self.root/'.reference.binding.json'
        expected={'profile':'data_exit.v1.r01','dataset_id':state['dataset_id'],'instance_id':state['instance_id'],'root_id':self.root_id}
        with self.lease.acquire(True):
            if binding.exists():
                from .files import regular
                regular(binding)
                if binding.stat().st_size>4096 or json.loads(binding.read_bytes())!=expected:raise DataError('originals_root_binding_mismatch',503)
            else:
                with binding.open('xb') as stream:
                    stream.write(json.dumps(expected,sort_keys=True).encode('utf-8'));stream.flush();os.fsync(stream.fileno())
        store.reference_coordinator = self

    @staticmethod
    def prepare_reference(sha256, size, *, source_id=None, version_id=None, candidate_id=None, pdf=False):
        return PreparedReference(source_id or str(uuid4()), version_id or str(uuid4()),
                                 candidate_id or (str(uuid4()) if pdf else None), sha256, size)

    @contextmanager
    def acquire_shared(self, prepared):
        with self.gate.acquire() as permit:
            with self.lease.acquire() as lease:
                pin = ReferencePin(self, lease, prepared, permit)
                with self.repository.connection() as connection:
                    pin.epoch = connection.execute("SELECT public.data_reference_begin(%s,%s,%s,%s,%s,%s,%s,%s,%s) AS epoch",
                        (pin.ticket_id, prepared.source_id, prepared.version_id, prepared.candidate_id,
                         prepared.sha256, prepared.size, self.root_id, pin.nonce,self.maintenance_key)).fetchone()["epoch"]
                # ticket 的 COMMIT 已正常返回，此后才允许原件发布。
                yield pin

    @contextmanager
    def reference_transaction(self, connection, pin, prepared):
        if pin is None or pin.coordinator is not self:
            raise DataError("reference_pin_required")
        pin.check(self.root, prepared)
        pin.bind(connection)
        yield
        pin.commit(connection)

    def reconcile(self, prepared):
        # 不凭无行或 OS 解锁推断 COMMIT 未发生，未知保留为未知。
        try:
            with self.repository.connection(readonly=True) as connection:
                row = connection.execute("SELECT source_id,sha256,size FROM public.material_versions WHERE id=%s", (prepared.version_id,)).fetchone()
            if row is not None and (str(row["source_id"]), row["sha256"], row["size"]) == (prepared.source_id, prepared.sha256, prepared.size):
                return "committed"
        except DataError:
            pass
        return "unknown"

    def cancel_old_epoch(self, operation=None):
        # 独立短事务，COMMIT 未确认绝不进入 unlink。
        with self.repository.connection(operation=operation) as connection:
            epoch = connection.execute("SELECT public.data_reference_cancel_epoch(%s,%s) AS epoch",
                                       (self.root_id, self.maintenance_key)).fetchone()["epoch"]
        return epoch

    def exclusive_cleanup(self, manifest, *, already_exclusive=None, operation=None):
        def perform(lease):
            lease.check()
            if not lease.exclusive: raise DataError("reference_pin_invalid")
            epoch = self.cancel_old_epoch(operation)
            outcomes = []
            for item in manifest:
                if operation is not None: operation.check()
                original = Original(item["sha256"], int(item["size"]))
                try:
                    # 第二个 READ COMMITTED 事务的新语句看全部历史和待 PDF 引用。
                    with self.repository.connection(operation=operation) as connection:
                        connection.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,113))", (self.root_id,))
                        row = connection.execute("""SELECT EXISTS(SELECT 1 FROM public.material_versions v
                          WHERE v.sha256=%s AND NOT EXISTS(SELECT 1 FROM public.data_tombstones t
                           WHERE t.entity_kind='source' AND t.entity_id=v.source_id)) AS retained""", (original.sha256,)).fetchone()
                        if row["retained"]:
                            state = "shared_retained"
                        else:
                            if operation is not None: operation.check()
                            state = self.store.unlink_exact(original, lease=lease)
                        outcomes.append({"sha256": original.sha256, "size": str(original.size), "state": state, "epoch": str(epoch)})
                except (OSError, ValueError, DataError):
                    outcomes.append({"sha256": original.sha256, "size": str(original.size), "state": "physical_result_unknown", "epoch": str(epoch)})
            return outcomes
        if already_exclusive is not None:
            return perform(already_exclusive)
        with self.gate.acquire():
            with self.lease.acquire(True, timeout=operation.remaining(30) if operation else 30) as lease:
                return perform(lease)
