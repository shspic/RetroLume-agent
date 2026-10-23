"""Entry used only inside the TASK-120 owned runtime Job."""
from pathlib import Path
import os
import sys
import traceback

ROOT=Path(__file__).resolve().parents[4]
root_id=int(os.environ['RETROLUME_TASK120_ROOT_ID'])
suffix=('-batch-'+os.environ['RETROLUME_TASK120_BATCH'].zfill(2)) if os.environ.get('RETROLUME_TASK120_BATCH') else ''
folder=ROOT/'DocuN/evidence/TASK-120/execution'
if os.environ.get('RETROLUME_TASK120_CONTINUATION')=='TASK-120-Q-PREP-AUDIT-REPAIR-07-20261021':folder=folder/'audit-repair-07'
if os.environ.get('RETROLUME_TASK120_CONTINUATION')=='TASK-120-Q-PREP-TARGETED-REPAIR-08-20261021':folder=folder/'audit-repair-08'
log=(folder/f'root-{root_id:02d}{suffix}-child.log').open('a',encoding='utf-8',buffering=1)
sys.stdout=sys.stderr=log


def bootstrap():
    import asyncio
    from . import resources as r
    from . import setup
    from .transport import install
    from app.runtime import psycopg_compatible_loop_factory
    install()
    for slot in ('flow','budget-01'):
        setup.initial_files(slot);setup.migrate(slot);setup.environment(slot)
        from app.main import create_app
        app=create_app()
        if app.state.data_exit_error or app.state.data_exit is None:raise RuntimeError('actual_application_data_exit_not_ready')
        mapping=setup.seed_sources(app,slot)
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(setup.bind_root(app,slot,mapping))
    if not (r.EVIDENCE/'bootstrap-result.json').exists():r.write(r.EVIDENCE/'bootstrap-result.json',{'status':'PASS','execution_class':'TESTONLY','databases':['retrolume_task120_flow','retrolume_task120_budget_01'],
        'real_Q':False,'provider_calls':0,'financial_baselines':'empty; activities created through production repository'})


def main():
    from . import resources as r
    phase=sys.argv[1]
    if str(r.state().get('active_root'))!=os.environ['RETROLUME_TASK120_ROOT_ID']:raise RuntimeError('unowned_runtime')
    try:
        if phase=='queue':
            from .queued import run_plan
            return run_plan()
        if phase=='merged':
            from .merged import run_batches
            return run_batches()
        if phase=='bootstrap':bootstrap()
        elif phase.startswith('r08_'):
            from tests.fixtures.task120.repair08 import execute
            result=execute(phase[4:])
        elif phase.startswith('a07_'):
            from .audit07 import execute
            execute(phase.removeprefix('a07_'))
        elif phase.startswith('c06_'):
            from .continuation06 import execute
            execute(phase.removeprefix('c06_'))
        elif phase.startswith('f05_'):
            from .final05 import execute
            execute(phase.removeprefix('f05_'))
        elif phase.startswith('v04_'):
            from .validation04 import execute
            execute(phase.removeprefix('v04_'))
        elif phase.startswith('r03_'):
            from . import repair03
            repair03.execute(phase.removeprefix('r03_'))
        elif phase in ('flow','teaching','interview','interview_repaired','legacy_html','gap'):
            from .flow import run_flow
            run_flow(None if phase=='flow' else phase)
        elif phase=='c02_races':
            from .recovery_races import run_races
            run_races()
        elif phase in ('c02_observe','c02_bootstrap_memory','c02_core','c02_memory','c02_ui'):
            from . import recovery
            if phase=='c02_observe':recovery.observe()
            elif phase=='c02_bootstrap_memory':recovery.bootstrap_memory()
            else:recovery.finite(phase.removeprefix('c02_'))
        elif phase=='observe':
            from .observe import observe
            observe()
        elif phase=='diagnose':
            from .diagnose import diagnose
            diagnose()
        elif phase=='html_eol':
            from .html_eol import apply
            apply()
        elif phase in ('integrated_core','integrated_ui'):
            from .integrated import integrated
            integrated(phase.removeprefix('integrated_'))
        elif phase in ('budget','budget_a2','budget_a3','budget_race'):
            from .budget import run_budget
            run_budget(phase)
        elif phase=='ui':
            from .ui import run_ui
            run_ui()
        elif phase=='reopen':
            from .budget import run_reopen
            run_reopen()
        else:raise ValueError('unknown_phase')
        return 0
    except BaseException as exc:
        # Test data only. Secrets/DSNs/SQL arguments are not printed.
        print(type(exc).__name__,getattr(exc,'sqlstate',None))
        for item in traceback.extract_tb(exc.__traceback__):print(item.filename,item.lineno,item.name)
        r.write(r.EVIDENCE/f'root-{root_id:02d}{suffix}-failure.json',{'phase':phase,'error_type':type(exc).__name__,'sqlstate':getattr(exc,'sqlstate',None),'safe_code':str(exc) if type(exc) is RuntimeError else None})
        return 1


if __name__=='__main__':raise SystemExit(main())
