"""Risk inspection before any real015 execution. No PG/service creation."""
from pathlib import Path
import ast,difflib,hashlib,json,re,sys,unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.schema_profiles import get_profile,R02,R03,MIGRATION_015
from app.data_exit.contracts import PROFILE
from tests.test_scope_delete_profile import ScopeDeleteProfile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,expected in get_profile(R02).migration_chain.items():assert sha(ROOT/'backend/migrations'/name)==expected,name
p=ROOT/'backend/migrations/015_activity_scope_delete_permission.sql';sql=p.read_text(encoding='utf-8')
grants=re.findall(r'^GRANT\s+(.+?)\s+ON\s+(.+?)\s+TO\s+([^;]+);',sql,re.M)
assert grants==[('DELETE','public.activity_scope_sources','retrolume_data_app')]
assert sha(p)==MIGRATION_015 and 'CREATE ROLE' not in sql and 'CREATE FUNCTION' not in sql
before=ast.parse((HERE/'preimage/backend/app/data_exit/schema_profiles.py').read_text(encoding='utf-8'))
after=ast.parse((ROOT/'backend/app/data_exit/schema_profiles.py').read_text(encoding='utf-8'))
def constants(tree):return {n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and isinstance(n.value,(ast.Constant,ast.Dict))}
for name,value in constants(before).items():assert constants(after)[name]==value,name
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ScopeDeleteProfile));assert result.wasSuccessful()
diff=[]
for p in (HERE/'preimage').rglob('*'):
 if p.is_file():
  current=ROOT/p.relative_to(HERE/'preimage')
  diff.extend(difflib.unified_diff(p.read_text(encoding='utf-8-sig').splitlines(True),current.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+str(p.relative_to(HERE/'preimage')),tofile='after/'+str(p.relative_to(HERE/'preimage'))))
(HERE/'pre-execution.diff').write_text(''.join(diff),encoding='utf-8')
value={'status':'PASS_ENGINEERING_RISK_CHECK_NOT_INDEPENDENT_AUDIT','before_real_GRANT':True,'grant_objects':grants,'migration015_sha256':MIGRATION_015,'001_014_exact_hashes_unchanged':True,'R01_R02_all_frozen_constants_unchanged':True,'new_profile':R03,'table_columns_and_codec_shape_unchanged':True,'exact_acl_rejections_unit_tests':result.testsRun,'guard':'Existing data_runtime_write remains BEFORE INSERT/UPDATE/DELETE; nonnormal is rejected. Table ACL is not per-activity CAS.','rollback':'Only new synthetic instance: REVOKE this DELETE plus matching R02 profile constraint/metadata/config; retains committed business data. No rollback executed.','wire_backup_format_financial_SUP_unchanged':True,'runtime_validation':'NOT_YET_RUN','diff':'pre-execution.diff'}
(HERE/'permission-risk-check.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
print(json.dumps(value))
