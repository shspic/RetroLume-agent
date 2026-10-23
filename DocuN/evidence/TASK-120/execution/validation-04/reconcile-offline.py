"""Read saved private metadata/copies; no PG/API/worker/Browser start."""
from pathlib import Path
import hashlib,json,sys,unittest,py_compile,subprocess
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from tests.fixtures.task120.api_runtime import transaction_failure_metadata
from app.data_exit.control import ControlHub
from app.data_exit.q_store import QAuthority
from app.data_exit.contracts import DataError
HERE=Path(__file__).resolve().parent
def write(name,value):r.write(HERE/name,value)
class Diagnostics(unittest.TestCase):
    def test_nested_SQLSTATE_without_messages_values_or_DSN(self):
        import psycopg
        inner=psycopg.errors.UndefinedColumn('SECRET_DSN_AND_REQUEST_BODY')
        outer=RuntimeError('SECRET_WRAPPER');outer.__cause__=inner
        value=transaction_failure_metadata(outer)
        self.assertEqual(value,[{'error_type':'RuntimeError','sqlstate':None},{'error_type':'UndefinedColumn','sqlstate':'42703'}])
        self.assertNotIn('SECRET',json.dumps(value))
    def test_exception_cycle_and_malformed_state_are_closed(self):
        e=RuntimeError('untrusted');e.sqlstate='secret-untrusted';e.__context__=e
        self.assertEqual(transaction_failure_metadata(e),[{'error_type':'RuntimeError','sqlstate':None}])
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Diagnostics))
copies=[]
for folder in sorted((r.PRIVATE/'negative-copies').iterdir()):
    if not folder.is_dir():continue
    path=folder/'journal.bin';raw=path.read_bytes();tail=raw.endswith(b'\xff')
    try:QAuthority(ControlHub(folder))
    except DataError as exc:
        expected='control_tail_unconfirmed' if tail else 'q_instance_identity'
        if exc.code!=expected:raise RuntimeError('saved_private_copy_unexpected_boundary_'+exc.code)
        copies.append({'copy_id':folder.name,'journal_sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'damaged_tail_byte_appended':tail,'actual_denial':exc.code,'original_journal_not_modified':True,'reopened_copy_only_no_PG':True})
    else:raise RuntimeError('saved_private_copy_not_rejected')
write('copied-control-reconciliation.json',{'status':'PASS_FOR_EXACT_SAVED_COPIES_ONLY','copies':copies,'root24_callback_FAIL_preserved':True,'other_root24_gate_assertions':'Control-flow reached this guard; individual positive/negative receipt values were not saved before failure, so no blanket full-matrix pass.','ACK_not_reached':True,'financial_claim_authority':'final real PG snapshot and saved original Q rows; copied hub is not financial authority'})
unknown=('1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e','430a4e36-08e1-411f-a73e-097506a6278b','3b561488-07b7-4d6d-8b98-05e793c96749')
for slot in ('flow','budget-02'):
    hub=ControlHub(r.PRIVATE/slot/'control');q=hub.state()['q'];authority=QAuthority(hub);rows=[]
    for row in q['requests'].values():
        p=row['prepared']
        rows.append({'activity_id':p['activity_id'],'business_key':p['business_key'],'operation_id':p['operation_id'],'prepared_id':row['prepared_id'],'prepared_sha256':row['prepared_sha256'],'claim_present':bool(row.get('claim')),'admission':row.get('admission'),'approval_present':bool(row.get('approval')),'revoked':bool(row.get('revoked')),'closed':bool(row.get('closed')),'artifact_sha256':hashlib.sha256(hub.artifact_path('q-prepared',row['prepared_id']).read_bytes()).hexdigest(),'original_never_resend':p['business_key'] in unknown})
    write(slot+'-final-Q-metadata.json',{'utc':r.utc(),'metadata_only':True,'not_financial_authority':True,'requests':rows,'live_control_journal_sha256':hashlib.sha256(hub.path.read_bytes()).hexdigest()})
for file in [ROOT/'backend/app/activities/teaching_repository.py',*(ROOT/'backend/tests/fixtures/task120').glob('*.py')]:py_compile.compile(str(file),doraise=True)
node=subprocess.run(['node','--check',str(ROOT/'frontend/tests/task120-ui-continuation.mjs')],timeout=15)
write('offline-final-checks.json',{'utc':r.utc(),'tests':result.testsRun,'success':result.wasSuccessful() and node.returncode==0,'JS_syntax_exit':node.returncode,'PG_API_Browser_SUP_started':0,'new_fixture_tail_panel_diagnostics_not_PG_UI_rerun':True})
raise SystemExit(0 if result.wasSuccessful() and node.returncode==0 else 1)
