"""Entry used only inside the TASK-120 owned runtime Job."""
from pathlib import Path
import os
import sys
import traceback

ROOT=Path(__file__).resolve().parents[4]
root_id=int(os.environ['RETROLUME_TASK120_ROOT_ID'])
suffix=('-batch-'+os.environ['RETROLUME_TASK120_BATCH'].zfill(2)) if os.environ.get('RETROLUME_TASK120_BATCH') else ''
log=(ROOT/f'DocuN/evidence/TASK-120/execution/root-{root_id:02d}{suffix}-child.log').open('a',encoding='utf-8',buffering=1)
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
        if phase=='merged':
            from .merged import run_batches
            return run_batches()
        if phase=='bootstrap':bootstrap()
        elif phase=='flow':
            from .flow import run_flow
            run_flow()
        elif phase=='budget':
            from .budget import run_budget
            run_budget()
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
        print(type(exc).__name__,getattr(exc,'sqlstate',None),getattr(getattr(exc,'diag',None),'message_primary',None))
        for item in traceback.extract_tb(exc.__traceback__):print(item.filename,item.lineno,item.name)
        r.write(r.EVIDENCE/f'root-{root_id:02d}{suffix}-failure.json',{'phase':phase,'error_type':type(exc).__name__,'sqlstate':getattr(exc,'sqlstate',None),'safe_code':str(exc) if type(exc) is RuntimeError else None})
        return 1


if __name__=='__main__':raise SystemExit(main())
