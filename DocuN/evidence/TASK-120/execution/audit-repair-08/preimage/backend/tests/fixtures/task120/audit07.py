"""One finite07 repair plan. Only named new databases and normal product flows."""
import json,traceback
from . import resources as r
HERE=r.EVIDENCE
SLOT='audit07-main'


def case(name,action):
    p=HERE/(name+'-PASS.json')
    if p.exists():return json.loads(p.read_text(encoding='utf-8'))['facts']
    try:
        facts=action();r.write(p,{'status':'PASS','facts':facts,'root':r.state()['active_root']});return facts
    except BaseException as exc:
        r.write(HERE/(name+'-FAIL-root-'+str(r.state()['active_root'])+'.json'),{'status':'FAIL',
            'error_type':type(exc).__name__,'code':getattr(exc,'code',None),'sqlstate':getattr(exc,'sqlstate',None),
            'frames':[{'file':str(x.filename).replace(str(r.ROOT),'PROJECT'),'line':x.lineno,'function':x.name} for x in traceback.extract_tb(exc.__traceback__)]})
        raise


def execute(mode):
    if r.state()['current_permit_id']!='TASK-120-Q-PREP-AUDIT-REPAIR-07-20261021':raise RuntimeError('audit07_permit_required')
    if mode=='permissions':
        from .audit07_permissions import permissions
        return permissions()
    if mode=='bootstrap':return bootstrap()
    if mode=='claim_clock':
        from .audit07_time_claim import exercise
        return exercise()
    if mode=='cleanup':
        from .audit07_cleanup import exercise
        return exercise()
    if mode=='final':return final()
    raise RuntimeError('audit07_unknown_phase')


def bootstrap():
    from . import setup
    from .transport import install
    from .api_runtime import run,financials
    setup.environment(SLOT);install()
    from app.main import create_app
    app=create_app()
    assert app.state.data_exit is not None and app.state.data_exit_error is None
    mapping=setup.seed_sources(app,SLOT);run(setup.bind_root(app,SLOT,mapping))
    return case('new-main-normal-root',lambda:{'identity':{k:setup.info(SLOT)[k] for k in ('database','database_oid','dataset_id','instance_id','originals_root_id')},
        'schema_profile':'data_exit.v1.r03','fixed_sources':len(mapping),'financials':financials(SLOT),'execution_class':'TESTONLY','real_Q':'FROZEN'})


def final():
    from .api_runtime import financials
    from . import setup
    import psycopg
    from psycopg.rows import dict_row
    from app.data_exit.schema_checks import assert_data_schema_sync
    values={}
    for slot in ('audit07-r02','audit07-main'):
        with psycopg.connect(setup.dsn(slot),row_factory=dict_row) as c:
            c.execute('SET TRANSACTION READ ONLY');assert_data_schema_sync(c)
            values[slot]={'identity':{k:setup.info(slot)[k] for k in ('database','database_oid','dataset_id','instance_id')},'financials':financials(slot)}
    assert sum(x['financials']['requests'] for x in values.values())<=16
    return case('final-new-instances-separated',lambda:values)
