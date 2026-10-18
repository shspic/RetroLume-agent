from pathlib import Path
import sys,subprocess,os,json
HERE=Path(__file__).resolve().parent;EXEC=HERE.parent;ROOT=EXEC.parents[3]
sys.path.insert(0,str(EXEC));from control import *
if state()['active_root']!=5:raise RuntimeError('root_identity')
failure('S02-grant-fixture-initial','首三个新grant断言的合成CatalogEntry手填evidence_id被原正确校验拒绝；已改用原build_fragments生成，没有削弱校验。',effect='首失败保留；原v3/v4两项定向复检已通过，本次不重复')
env=dict(os.environ);env['PYTHONPATH']=os.pathsep.join(str(ROOT/p) for p in ('backend','backend/tests','backend/tests/fixtures/step018'))
names=['test_step018_flows.IntegrationContractTests.'+x for x in ('test_valid_adopted_source_and_both_capabilities','test_unapproved_version_fragment_or_query_is_closed','test_grant_expired_tampered_roster_and_price_are_closed')]
r=subprocess.run([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8','-m','unittest',*names,'-v'],cwd=ROOT,env=env,capture_output=True,timeout=30)
(HERE/'grant-contracts.txt').write_bytes(r.stdout+r.stderr)
if r.returncode:print(r.stderr.decode('utf-8','replace'));raise SystemExit(1)
write(HERE/'root05-contracts.json',{'cleanup_methods':3,'cleanup_result':'passed','v3_v4_wire_impacted_methods':2,'wire_result':'passed in preceding direct tool','grant_methods':3,'grant_result':'passed','actual_provider_calls':0,'Q_activation':False,'S01_evidence_unchanged':True,'as_run':{p:sha((ROOT/p).read_bytes()) for p in ('backend/app/capabilities/embedding.py','backend/app/capabilities/contracts.py','backend/app/worker/one_call.py','backend/tests/test_step018_flows.py','backend/tests/fixtures/step018/lifecycle.py')}})
end_root(result='S02：3清场+2最终wire+3实际source/grant合同断言通过，首fixture错误保留；未启动PG/API/Browser')
print('Eight focused contract methods passed; ROOT05 ended with no runtime resources')
