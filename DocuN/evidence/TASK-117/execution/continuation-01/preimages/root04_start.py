from control import *
from runtime_control import start_pg,stop_pg,docker,metadata,dsn
import subprocess,sys,shutil
begin_root('ROOT04-真实HTTP两链与正常同库重开','runtime')
try:
    start_pg('source')
    old=HERE/'r02-frozen-catalog.json'
    old.rename(HERE/'r02-frozen-catalog-before-owner-normalization.json')
    r=subprocess.run([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(HERE/'freeze_profile.py')],capture_output=True,timeout=30)
    (HERE/'root04-profile-freeze.txt').write_bytes(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError('profile_refreeze_failed')
    sys.path.insert(0,str(ROOT/'backend'))
    import psycopg
    from psycopg.rows import dict_row
    from app.data_exit.schema_checks import assert_data_schema_sync
    with psycopg.connect(dsn('source'),row_factory=dict_row) as connection:assert_data_schema_sync(connection)
    event('root04_source_profile_checked',ordinary_role=True)
    info=__import__('json').loads(docker(['info','--format','{{json .}}']))
    image=__import__('json').loads(docker(['image','inspect','sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789']))[0]
    write(HERE/'root04-preview-host.json',{'kernel':info['KernelVersion'],'image':image['Id'],'os':image['Os'],'arch':image['Architecture'],'docker':shutil.which('docker')})
    print('Own source resumed and exact R02 profile checked; preview host metadata captured')
except Exception as e:
    failure('ROOT04-start',type(e).__name__+':'+str(e)[:200]);stop_pg('source');raise
