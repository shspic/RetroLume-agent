"""Finite offline checks before any07 database creation or revised015 execution."""
import ast,hashlib,json,os,subprocess,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
os.environ['RETROLUME_TASK120_CONTINUATION']='TASK-120-Q-PREP-AUDIT-REPAIR-07-20261021'
sys.path.insert(0,str(ROOT/'backend'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
registry=json.loads((HERE/'change-registry.json').read_text(encoding='utf-8'))
for row in registry['paths']:
    p=ROOT/row['path']
    if p.is_file() and p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
old=ast.parse((HERE/'preimage/backend/app/data_exit/schema_profiles.py').read_text(encoding='utf-8'))
new=ast.parse((ROOT/'backend/app/data_exit/schema_profiles.py').read_text(encoding='utf-8'))
def constants(tree):
    return {node.targets[0].id:ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign)
            and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('R02','MIGRATION_014','R02_EXTRA_SHAPE_SHA')}
assert constants(old)==constants(new)
from app.data_exit.schema_profiles import MIGRATION_015,LEGACY_MIGRATION_015
assert sha(ROOT/'backend/migrations/015_activity_scope_delete_permission.sql')==MIGRATION_015
assert LEGACY_MIGRATION_015=='59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e'
suite=unittest.TestSuite()
for name in ('tests.test_scope_delete_profile','tests.test_q_audit07'):
    suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
result=unittest.TextTestRunner(verbosity=2).run(suite)
probe={}
try:
    command=subprocess.run(['docker','container','inspect','b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f',
        '4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332'],capture_output=True,timeout=15)
    if command.returncode:probe={'status':'UNAVAILABLE','returncode':command.returncode}
    else:
        rows=json.loads(command.stdout);probe={'status':'PASS','objects':[{'Id':x['Id'],'Running':x['State']['Running'],'Pid':x['State']['Pid']} for x in rows]}
        assert all(not x['Running'] and x['Pid']==0 for x in probe['objects'])
except (OSError,subprocess.TimeoutExpired):probe={'status':'UNAVAILABLE'}
(HERE/'runtime-readonly-preflight.json').write_text(json.dumps(probe,indent=2)+'\n',encoding='utf-8')
risk={'status':'PASS' if result.wasSuccessful() else 'FAIL','before_real07_GRANT':True,'revised015_sha256':MIGRATION_015,
      'old015_sha256_preserved':LEGACY_MIGRATION_015,'old001_to014_and_R01_R02':'unchanged; audit baseline322 verified',
      'grant_objects':['DELETE public.activity_scope_sources TO retrolume_data_app'],
      'DDL_scope':'existing015 only; separate SELECT, INSERT, UPDATE mandatory predicates; extra DELETE/TRUNCATE OR semantics retained',
      'compatibility':'exact old R03 codec chain recognized for reading; default/new initialization exact revised015; no old database replay',
      'F02':'actual effective rights plus PG17 INHERIT/SET paths and dangerous ADMIN capability checked before shape/ACL projection; real transaction proof still required',
      'offline_tests':{'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)},
      'PG_runtime_not_started':True,'frontend_unchanged':True}
(HERE/'permission-risk-before-PG.json').write_text(json.dumps(risk,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'offline':risk['offline_tests'],'docker_readonly_probe':probe,'risk':risk['status']}))
raise SystemExit(0 if result.wasSuccessful() else 1)
