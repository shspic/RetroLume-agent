"""单批离线S1/当前守卫：源码编译不落pyc，协议样例、独立browser模块和定向测试。"""
from pathlib import Path
import json, os, subprocess, sys, unittest
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'backend'))
for p in (ROOT/'backend/tests/fixtures/task097').glob('*.py'):compile(p.read_bytes(),str(p),'exec')
for p in Path(__file__).parent.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
for p in [ROOT/'frontend/tests/task097-continuation.mjs']:
    r=subprocess.run(['node','--check',str(p)],capture_output=True);sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr);assert r.returncode==0
    r=subprocess.run(['node',str(p)],env={**os.environ,'RETROLUME_TASK097_PREFLIGHT':'1'},capture_output=True);sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr);assert r.returncode==0
suite=unittest.defaultTestLoader.loadTestsFromNames(['tests.test_learning_continuation.ContinuationContractTests','tests.test_learning_gateway.LearningGatewayTests.test_worker_after_claim_scope_slot_and_mixed_profile_rejection'])
r=unittest.TextTestRunner(verbosity=2).run(suite)
print('source compile / Node syntax / module preload / current strict guards completed; no resource starts')
raise SystemExit(0 if r.wasSuccessful() else 1)
