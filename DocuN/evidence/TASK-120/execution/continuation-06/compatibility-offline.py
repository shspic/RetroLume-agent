"""Real ZIP/codec recognition only. Never claims database authorization proof."""
from pathlib import Path
import json,os,sys,unittest,zipfile
ROOT=Path(__file__).resolve().parents[5];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from tests.test_data_exit_package import DataPackageOffline,sample
from app.data_exit.contracts import PROFILE,DataError,canonical,digest
from app.data_exit.schema_profiles import R02,R03,get_profile
from app.data_exit.packages import PackageReader
scratch=ROOT/'.runtime/TASK-120/continuation-06/compatibility';scratch.mkdir(exist_ok=True)
os.environ['RETROLUME_TASK114_SCRATCH']=str(scratch)
if not (HERE/'R01-file-compatibility-PASS.json').exists():
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([DataPackageOffline('test_valid_exact_domains')]))
 assert result.wasSuccessful()
members,manifest=sample();schema=get_profile(R02)
manifest['codec_profile']=R02;manifest['snapshot']['source_schema_profile']=R02;manifest['source_business_table_count']=len(schema.tables)
control=json.loads(members['metadata/source_control.json']);control['schema_profile']=R02;members['metadata/source_control.json']=canonical(control).encode()
codec=json.loads(members['codec_description.json']);codec.update(profile=R02,columns=schema.columns,migration_sha256=schema.codec_migrations);members['codec_description.json']=canonical(codec).encode()
for table in schema.tables:
 for prefix in ('records','checkpoint'):members.setdefault(prefix+'/'+table+'.jsonl',b'')
def seal(members,manifest,path):
 manifest['contents']=[{'path':n,'kind':'synthetic','availability':'present','bytes':str(len(v)),'sha256':digest(v)} for n,v in members.items() if n!='manifest.json']
 manifest.pop('root_sha256',None);manifest['root_sha256']=digest(canonical(manifest));members['manifest.json']=canonical(manifest).encode()
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as z:
  for n,v in members.items():z.writestr(n,v)
path=scratch/'R02-valid.rldata';seal(members,manifest,path)
with PackageReader(path) as reader:assert reader.schema_profile.name==R02
codec['migration_sha256']={**codec['migration_sha256'],'014_step018_retrieval.sql':'0'*64};members['codec_description.json']=canonical(codec).encode();bad=scratch/'R02-wrong-migration-hash.rldata';seal(members,manifest,bad)
try:
 with PackageReader(bad):pass
except DataError as exc:assert exc.code=='codec_mismatch';wrong=exc.code
else:raise AssertionError('wrong_migration_hash_accepted')
manifest['codec_profile']='data_exit.v1.unknown';bad=scratch/'unknown-profile.rldata';seal(members,manifest,bad)
try:
 with PackageReader(bad):pass
except DataError as exc:assert exc.code=='unsupported_format';unknown=exc.code
else:raise AssertionError('unknown_profile_accepted')
actual=next((ROOT/'.runtime/TASK-120/continuation-06/scope-ui-final/backup/packages').glob('*.rldata'))
with PackageReader(actual) as reader:assert reader.schema_profile.name==R03;actual_sha=reader.manifest['root_sha256']
value={'status':'PASS_OFFLINE_FILE_CODEC_ONLY','old_R01_existing_valid_exact_domains_test':True,'old_R02_actual_ZIP_reader':True,'wrong_migration_hash_denial':wrong,'unknown_profile_denial':unknown,'new_R03_actual_PG_backup_package_root_sha256':actual_sha,'database_authorization_and_transactions':'Separate real PG evidence; no mock/SQL-string authorization claim','wire_format_or_encoding_changed':False}
(HERE/'old-new-package-compatibility.json').write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value))
