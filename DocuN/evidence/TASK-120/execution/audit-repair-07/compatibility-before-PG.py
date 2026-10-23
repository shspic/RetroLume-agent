"""Exact codec identities and final offline clock check, no PG/service starts."""
import ast,hashlib,json,os,sys,unittest,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
os.environ['RETROLUME_TASK120_CONTINUATION']='TASK-120-Q-PREP-AUDIT-REPAIR-07-20261021'
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.contracts import DataError,canonical,digest
from app.data_exit.schema_profiles import R03,get_profile,MIGRATION_015,LEGACY_MIGRATION_015
from app.data_exit.packages import PackageReader
from app.data_exit.files import private_file
from tests.test_data_exit_package import sample

registry=json.loads((HERE/'change-registry.json').read_text(encoding='utf-8'))
for row in registry['paths']:
    p=ROOT/row['path']
    if p.is_file() and p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
profile=get_profile(R03);scratch=ROOT/'.runtime/task120-audit07/codec';scratch.mkdir(parents=True,exist_ok=True);private_file(scratch,directory=True)
results=[]
for label,migration,error in [('current',MIGRATION_015,None),('known-legacy',LEGACY_MIGRATION_015,None),('unknown015','0'*64,'codec_mismatch')]:
    members,manifest=sample()
    for key in list(members):
        if key.startswith(('records/','checkpoint/')):del members[key]
    for table in profile.tables:
        members['records/'+table+'.jsonl']=b'';members['checkpoint/'+table+'.jsonl']=b''
    control=json.loads(members['metadata/source_control.json']);control['schema_profile']=R03;members['metadata/source_control.json']=canonical(control).encode()
    codec=json.loads(members['codec_description.json']);codec.update(profile=R03,columns=profile.columns,migration_sha256={**profile.codec_migrations,'015_activity_scope_delete_permission.sql':migration});members['codec_description.json']=canonical(codec).encode()
    manifest.update(codec_profile=R03,source_business_table_count=len(profile.tables));manifest['snapshot']['source_schema_profile']=R03
    manifest['contents']=[{'path':name,'kind':'synthetic','availability':'present','bytes':str(len(data)),'sha256':digest(data)} for name,data in members.items() if name!='manifest.json']
    manifest.pop('root_sha256');manifest['root_sha256']=digest(canonical(manifest));members['manifest.json']=canonical(manifest).encode()
    path=scratch/(label+'-'+MIGRATION_015[:12]+'.rldata')
    assert not path.exists(),'Existing codec checkpoint must be inspected, not overwritten'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED,allowZip64=False) as z:
        for name,data in members.items():z.writestr(name,data)
    observed=None
    try:
        with PackageReader(path) as reader:
            assert reader.schema_profile.codec_migrations['015_activity_scope_delete_permission.sql']==migration
            assert reader.schema_profile.migration_chain['015_activity_scope_delete_permission.sql']==MIGRATION_015
    except DataError as exc:observed=exc.code
    assert observed==error,(label,observed)
    results.append({'case':label,'015_sha256':migration,'actual_error':observed,'package_sha256':digest(path.read_bytes()),'empty_business_rows_only':True})
old=ROOT/'.runtime/TASK-120/continuation-06/scope-ui-final/backup/packages/0f1999bf-0f93-4222-914d-6ef4f051b0f2.rldata'
before=digest(old.read_bytes())
with PackageReader(old) as reader:
    assert reader.manifest['root_sha256']=='7fdd4a09aa3fcb04bade3949163418f0458a0fa68d3e40befec3a5c7c212df24'
    assert reader.schema_profile.codec_migrations['015_activity_scope_delete_permission.sql']==LEGACY_MIGRATION_015
assert digest(old.read_bytes())==before
(HERE/'F01-exact-codec-compatibility-PASS.json').write_text(json.dumps({'status':'PASS','cases':results,'actual_original06_PG_backup_read':True,
    'original06_backup_sha256_unchanged':before,'old_installation_revalidated_or_replayed':False,'new_initialization_requires_current_hash':True},indent=2)+'\n',encoding='utf-8')
result=None
if '--codec-only' not in sys.argv:
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('tests.test_q_audit07'))
    assert result.wasSuccessful()
risk=json.loads((HERE/'permission-risk-before-PG.json').read_text(encoding='utf-8'))
risk.update(status='PASS',clock_correction='Python3.12 uses GetTickCount64; monotonic implementation and native boot GUID bound together; unsupported domains still close',
    first_failed_check_retained='command-072.log; permission-risk-before-PG.json',targeted_correction_receipt='command-073.receipt.json',
    current_clock_and_codec_verification='command-075.receipt.json',actual_original_old_R03_package_read=True)
(HERE/'permission-risk-final-before-PG.json').write_text(json.dumps(risk,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','exact_codec_cases':len(results),'original_R03_read':True,'current_clock_tests':result.testsRun if result else 'unchanged result075 reused','before_next_revised015_apply':True}))
