"""已有阻塞栈证明Windows socketpair accept挂起；最低transport夹具禁止真实I/O。"""
import json
from control import N,ROOT,py,run,write,sample,sha
paths=list(json.loads((N/'changes.json').read_text(encoding='utf-8')))
write(N/'targeted-no-io-as-run.json',{'sample':sample(),'files':[{'path':p,'sha256':sha((ROOT/p).read_bytes())} for p in paths if (ROOT/p).is_file()],
 'environment_evidence':'async-stack.log: socket.py fallback_socketpair accept，未进入任何gateway协程',
 'boundary':'只改离线测试事件循环self-pipe，实际gateway/协议/ledger/transport检查不替换；真实I/O fd注册直接拒绝'})
names=['test_step018_audit_repairs']
names += ['test_step018_flows.IntegrationContractTests.'+x for x in (
 'test_valid_adopted_source_and_both_capabilities','test_unapproved_version_fragment_or_query_is_closed',
 'test_grant_expired_tampered_roster_and_price_are_closed','test_grant_expiry_after_admission_prevents_dispatch',
 'test_legacy_command_bytes_and_new_local_profile','test_legacy_teaching_canonical_has_no_new_null')]
names += ['test_step018_embedding_contracts.EmbeddingContractTests.'+x for x in (
 'test_v4_embedding_closed_and_v3_unchanged','test_worker_bound_and_secret_not_argv_or_receipt',
 'test_four_input_payload_with_007_hash','test_unknown_retained_and_no_second_send','test_actual_network_default_fails_before_admit')]
rows=[]
for label,command in [('backend-no-io',py()+['-m','unittest','-v',*names]),
 ('typecheck',['C:/Program Files/nodejs/node.exe',str(ROOT/'frontend/node_modules/typescript/bin/tsc'),'--noEmit','-p',str(ROOT/'frontend/tsconfig.json')]),
 ('browser-contract',['C:/Program Files/nodejs/node.exe',str(ROOT/'frontend/tests/step018-s08.mjs'),'--contract-check'])]:
    code=run(command,label,timeout=90);rows.append({'label':label,'command':command,'exit_code':code})
write(N/'product-checks-no-io.json',{'sample':sample(),'checks':rows})
raise SystemExit(any(row['exit_code'] for row in rows))
