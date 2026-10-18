"""One justified final Python recompile plus new contract checks only."""
import io,json,unittest
from .control import ROOT,batch,reserve,atomic_json,source_manifest
from tests.test_interview_contracts import InterviewContracts

def main():
    with batch('O02-final-repair-compile-and-new-closed-contracts',category='offline_build',count='offline_batch',maximum=180) as out:
        reserve('compile',dict(cause='Actual post-mark diagnostic repair and new source/fixtures since O01; second and final permitted in-memory compile'))
        paths=[p for p in source_manifest() if p.endswith('.py')]
        for name in paths:compile((ROOT/name).read_bytes(),str(ROOT/name),'exec')
        names=('test_carrier_closed_no_tool_parent_and_wire_alias','test_malicious_output_and_unicode_identity','test_probe_cap_and_catalog_identity',
               'test_configuration_closed_and_wire_capacity','test_three_profiles_exclusive_and_frozen_message_binding')
        stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(InterviewContracts(name) for name in names))
        (out/'test-log.txt').write_text(stream.getvalue(),encoding='utf-8')
        atomic_json(out/'compile-contract-result.json',dict(compiled=paths,compile_writes_pyc=False,tests=list(names),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),
            inherited_unchanged='O01 original text/hash/key and strict command authority tests; no repeated old platform suite'))
        print(stream.getvalue());assert result.wasSuccessful(),'New contracts failed; complete actual test log retained'

if __name__=='__main__':main()
