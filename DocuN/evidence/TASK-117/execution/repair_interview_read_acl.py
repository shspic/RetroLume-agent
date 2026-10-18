from control import *
from runtime_control import dsn,metadata,PG_IMAGE
import sys,subprocess,json
sys.path.insert(0,str(ROOT/'backend'))
import psycopg
from psycopg.rows import dict_row
guard()
for slot in sys.argv[1:] or ['source']:
    resource=next(x for x in state()['resources'] if x['id']=='pg-'+slot)
    if metadata(resource['cid'])['image']!=PG_IMAGE:raise RuntimeError('exact_image_required')
    with psycopg.connect(dsn(slot,'admin'),row_factory=dict_row) as connection:
        if connection.execute('SELECT EXISTS(SELECT 1 FROM activities WHERE running_reserved_seconds>0 OR lease_expires_at>CURRENT_TIMESTAMP) AS busy').fetchone()['busy']:raise RuntimeError('not_quiescent')
        rows=connection.execute("SELECT activity_id::text,business_key::text,action,status,error_code,effect_applied FROM interview_commands ORDER BY created_at").fetchall()
        write(HERE/f'{slot}-interview-before-read-acl.json',rows)
        before=connection.execute("SELECT has_table_privilege('retrolume_interview_owner','public.teaching_commands','SELECT') AS read,has_table_privilege('retrolume_interview_owner','public.teaching_commands','INSERT,UPDATE,DELETE') AS write").fetchone()
        if before['write']:raise RuntimeError('unexpected_write_grant')
        connection.execute('GRANT SELECT ON public.teaching_commands TO retrolume_interview_owner')
        event('014_invoker_acl_repair',slot=slot,cid=resource['cid'],before=before,grant='SELECT only for activity_memory_eligible invoker call')
if 'source' in sys.argv[1:] or not sys.argv[1:]:
    path=HERE/'r02-frozen-catalog.json';path.rename(HERE/'r02-frozen-catalog-before-invoker-acl.json')
    result=subprocess.run([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(HERE/'freeze_profile.py')],capture_output=True,timeout=30)
    (HERE/'root04-invoker-refreeze.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('refreeze_failed')
print('Exact CID minimal invoker read grant repaired; original commands retained')
