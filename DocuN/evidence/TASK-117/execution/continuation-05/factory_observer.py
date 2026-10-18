"""S06 one-PG lifecycle schedule at the existing factory hook; no selector or data semantics changed."""
from pathlib import Path
import sys
N=Path(__file__).resolve().parent;sys.path.insert(0,str(N.parent))
import control as c,runtime_control as rc
class Hooks:
    def before_start(self,target):
        if target.target_id!='634aa034-51f6-4510-b075-38cb005481d8':raise RuntimeError('S06_only_original_success01')
        # activate_readonly reaches this hook only after real drain/freeze/latest-overlay checks.
        from app.data_exit.control import ControlHub
        hub=ControlHub(N.parent/'synthetic/source-control');state=hub.state()
        assert state['fence']['state']=='frozen' and state['selection'] is None
        assert not any(x['state']!='ended' for x in state['owned'].values())
        source_stop=rc.stop_pg('source')
        rc.docker(['image','inspect',rc.PG_IMAGE]);rc.pg_memory_gate('S06-success01-after-source-stop');rc.port_gate(target.port)
        c.count('pg_starts');row=next(r for r in c.state()['resources'] if r.get('cid')==target.cid)
        row.update(running=True,holding_start=c.sample());rc.save_resource(row)
        c.write(N/'R02-one-PG-switch-stage.json',{'sample':c.sample(),'original_target_id':target.target_id,'source_exact_stop':source_stop,'fence':'frozen','outstanding_owned':0,'called_at_existing_factory_before_start_hook':True,'source_latest_already_read_by_original_activate':True,'selector_not_fabricated':True})
    def started(self,target,identity):c.event('S06_R02_factory_started',target_id=target.target_id,identity=rc.metadata(target.cid))
    def stopped(self,target,identity):c.event('S06_R02_factory_stopped',target_id=target.target_id)
    def before_create(self,slot):raise RuntimeError('S06_no_new_target_required')
    def created(self,target,identity):raise RuntimeError('S06_no_new_target_required')
def install(app):
    runtime=app.state.data_exit
    if runtime is not None and runtime.factory is not None:runtime.factory.hooks=Hooks()
