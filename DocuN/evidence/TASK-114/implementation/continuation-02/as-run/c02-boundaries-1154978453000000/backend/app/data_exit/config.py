"""主机配置只从明确私有文件与环境引用读取，不接受 HTTP 路径或 DSN。"""
import os
from pathlib import Path
import secrets
from .codec import load_json
from .contracts import DataContext, DataError, Limits, PROFILE
from .control import ControlHub
from .deletions import SourceDeletionService
from .files import independent_roots, RootLease, safe_root
from .maintenance import MutationGate, MaintenanceCoordinator
from .packages import DataPackageService
from .reference import OriginalReferenceCoordinator
from .repository import DataRepository
from .restore import TargetFactory, RestoreController
from .snapshot import SnapshotCoordinator


def load_profile():
    path = os.environ.get("RETROLUME_DATA_EXIT_CONFIG")
    if not path: return None
    info = Path(path).lstat()
    if info.st_size > 65536: raise DataError("restore_executor_missing", 503)
    from .files import regular
    regular(path)
    value = load_json(Path(path).read_bytes())
    if set(value) - {"enabled", "snapshot_url_env", "maintenance_key_env", "factory", "limits"}:
        raise DataError("restore_executor_missing", 503)
    if value.get("enabled") is not True: return None
    for field in ("snapshot_url_env", "maintenance_key_env"):
        name = value.get(field)
        if not isinstance(name, str) or not name.startswith("RETROLUME_"):
            raise DataError("restore_executor_missing", 503)
    if value.get("limits"):
        baseline = Limits()
        for name, limit in value["limits"].items():
            if not hasattr(baseline, name) or type(limit) is not int or not 1 <= limit <= getattr(baseline, name):
                raise DataError("invalid_input", 400)
    return value


class DataRuntime:
    def __init__(self, app, settings, profile):
        self.app, self.settings, self.profile = app, settings, profile
        required = ("RETROLUME_CONTROL_ROOT", "RETROLUME_RESTORE_ROOT")
        if any(not os.environ.get(name) for name in required): raise DataError("storage_unavailable", 503)
        _, _, restore_root, control_root = independent_roots(settings.data_dir, settings.backup_dir,
                                                           os.environ[required[1]], os.environ[required[0]])
        self.hub = ControlHub(control_root)
        self.limits = Limits(**profile.get("limits", {}))
        source_dsn=os.environ.get('RETROLUME_DATABASE_URL')
        self.source = DataRepository(source_dsn) if source_dsn else None
        self.maintenance_key = os.environ.get(profile["maintenance_key_env"])
        self.snapshot_dsn = os.environ.get(profile["snapshot_url_env"])
        self.factory = TargetFactory(self.hub, restore_root, profile["factory"], limits=self.limits) if profile.get("factory") else None
        self.source_state = None
        self.source_error=None
        self.target_error=None
        selection = self.hub.state()["selection"]
        if selection is None:
            known=self.hub.state()['source']
            try:
                if self.source is None:raise DataError('storage_unavailable',503)
                self.source_state = self.source.state()
                if known is None:self.hub.commit('source.register',self.source_state)
                elif (known['dataset_id'],known['instance_id'],known['originals_root_id'])!=(self.source_state['dataset_id'],self.source_state['instance_id'],self.source_state['originals_root_id']):
                    raise DataError('source_identity_changed',503)
            except DataError as error:
                if known is None:raise
                self.source_error=error.code
                self.source_state={**known,'mode':'unavailable'}
            if self.source_state["schema_profile"] != PROFILE: raise DataError("schema_profile_mismatch", 503)
        self.gate = MutationGate(self.hub, self.context)
        self.gate.validate_source=self.validate_source
        async def close_owned():
            controller = app.state.preview_controller
            if controller is not None:
                await controller.close()
        self.maintenance = MaintenanceCoordinator(self.gate, self.source, self.maintenance_key, close_owned)
        self.incoming = settings.backup_dir / "incoming"
        if not self.incoming.exists(): self.incoming.mkdir()
        safe_root(self.incoming)
        self.restore = RestoreController(self.hub, self.incoming, self.factory, self.source, self.maintenance,
                                         rebind=self.bind_readonly, limits=self.limits)
        self.tasks = {}
        self.references, self.deletions, self.packages = None, None, None
        self.packages=DataPackageService(self.hub,None,self.settings.backup_dir,self.limits)
        if selection is not None:
            if self.factory is None: raise DataError("restore_executor_missing", 503)
            target = self.factory.target(selection["target_id"])
            try:self.bind_readonly(target, self.factory.readonly_credentials(target.target_id), selection)
            except (DataError,OSError) as error:
                # 选中目标不可连时仍保留同Hub的job/包查询；业务入口已在绑定前关闭。
                self.target_error=error.code if isinstance(error,DataError) else 'storage_unavailable'
        else:
            self._configure_source()

    def context(self):
        state = self.hub.state()
        selection = state["selection"]
        if selection:
            return DataContext(self.hub.control_id, selection["generation"], selection["dataset_id"], selection["instance_id"],
                               "restored_readonly", selection["target_id"])
        if self.source_state is None: raise DataError("mode_unknown", 503)
        mode = self.source_state["mode"]
        if state["fence"] is not None and state["fence"].get("state") == "frozen": mode = "frozen"
        return DataContext(self.hub.control_id, 0, self.source_state["dataset_id"], self.source_state["instance_id"], mode)

    def validate_source(self,context):
        if self.source is None:raise DataError('mode_unknown',503)
        current=self.source.state()
        if (current['dataset_id'],current['instance_id'],current['mode'])!=(context.dataset_id,context.instance_id,'normal'):
            raise DataError('mode_unknown',503)

    def _configure_source(self):
        app = self.app
        if self.source_state['mode']=='unavailable':
            app.state.materials=None
            app.state.activities_ledger=None
            app.state.preview_controller=None
            return
        if self.source_state["mode"] == "normal":
            if not self.maintenance_key: raise DataError("maintenance_configuration_missing", 503)
            self.references = OriginalReferenceCoordinator(app.state.originals, self.source, self.gate, self.maintenance_key)
            if app.state.preview_controller is None and app.state.preview_policy is not None:
                from app.preview.production_supervisor import PreviewController
                app.state.preview_controller = PreviewController(app.state.activities_ledger, app.state.preview_policy)
        app.state.materials.configure_data_exit(self.gate, self.references)
        app.state.activities_ledger.mutation_gate = self.gate
        app.state.activities_ledger.data_enabled = True
        app.state.activities_ledger.data_readonly = self.context().mode != "normal"
        app.state.activities_ledger.tombstone_observer=self.observe_memory
        if app.state.preview_controller is not None:
            app.state.preview_controller.mutation_gate = self.gate
        if self.snapshot_dsn:
            lease = self.references.lease if self.references else RootLease(app.state.originals.root)
            snapshot = SnapshotCoordinator(self.snapshot_dsn, app.state.originals, lease, self.settings.backup_dir, self.limits)
            self.packages = DataPackageService(self.hub, snapshot, self.settings.backup_dir, self.limits, observer=self.observe_job)
        if self.references is not None:
            async def affected(ids):
                controller = app.state.preview_controller
                if controller is None or controller.current is None: return "not_owned"
                current = controller.current
                registry = current.get("registry", {})
                if registry.get("activity_id") not in ids: return "not_owned"
                await controller.stop(registry["activity_id"], registry["preview_id"], registry["generation"])
                return "unconfirmed" if controller.has_unconfirmed() else "confirmed_by_original_supervisor"
            self.deletions = SourceDeletionService(self.hub, self.source, self.references, self.gate, stop_affected=affected, limits=self.limits)

    def observe_job(self,receipt):
        try:
            with self.gate.acquire():self.source.observe_job(receipt)
        except DataError:pass

    async def observe_memory(self,memory_id):
        import asyncio
        from .codec import plain
        def read():
            with self.source.connection(readonly=True) as connection:
                return plain(connection.execute("SELECT * FROM public.data_export_tombstones_v1 WHERE entity_kind='memory' AND entity_id=%s",(memory_id,)).fetchone())
        tomb=await asyncio.to_thread(read)
        if tomb is not None:self.hub.commit('deletion.observe',tomb)

    def bind_readonly(self, target, credentials, selection):
        from app.materials.repository import PostgresMaterials
        from app.activities import PostgresAdmissionLedger
        from app.storage.originals import OriginalStore
        app=self.app
        # 选择器已提交时，任何后续绑定失败都须关闭旧源读取入口。
        app.state.materials=None
        app.state.activities_ledger=None
        app.state.preview_controller=None
        app.state.session_token=secrets.token_urlsafe(32)
        self.references,self.deletions=None,None
        self.packages=DataPackageService(self.hub,None,self.settings.backup_dir,self.limits)
        safe = DataRepository(credentials["readonly_dsn"]).safe_state()
        if str(safe["dataset_id"]) != target.dataset_id or str(safe["source_instance_observed"]) != target.instance_id or safe["mode_observed"] != "restored_readonly":
            raise DataError("target_seal_unconfirmed", 503)
        app.state.originals = OriginalStore(target.data_root / "originals")
        app.state.materials = PostgresMaterials(credentials["readonly_dsn"])
        app.state.materials.configure_data_exit(self.gate)
        app.state.activities_ledger = PostgresAdmissionLedger(credentials["readonly_dsn"])
        app.state.activities_ledger.mutation_gate = self.gate
        app.state.activities_ledger.data_enabled = True
        app.state.activities_ledger.data_readonly = True
        app.state.preview_controller = None
        snapshot = SnapshotCoordinator(credentials["snapshot_dsn"], app.state.originals, RootLease(app.state.originals.root), self.settings.backup_dir, self.limits)
        self.packages = DataPackageService(self.hub, snapshot, self.settings.backup_dir, self.limits)

    def caps(self):
        return {**self.context().public(), "format": PROFILE, "scope": ["all", "selected"],
                "backup_available": self.packages is not None and self.packages.snapshot is not None, "restore_executor_configured": self.factory is not None,
                'source_delete_available':self.deletions is not None and self.hub.state()['fence'] is None,
                'source_observation_status':'unknown' if self.source_error else 'configured',
                'target_observation_status':'unknown' if self.target_error else 'configured',
                "limits": self.limits.__dict__, "browser_drafts_included": False, "permanent_readonly_restore": True}
