"""修正残尾夹具并排除无关挂起族，按产品Windows Selector策略补剩余检查。"""
import json
from control import N,ROOT,py,run,write,sample,sha
paths=list(json.loads((N/'changes.json').read_text(encoding='utf-8')))
write(N/'targeted-as-run.json',{'sample':sample(),'files':[{'path':p,'sha256':sha((ROOT/p).read_bytes())} for p in paths if (ROOT/p).is_file()],
    'reason':'首批残尾夹具读取非公开scope已修；未执行或未完成的方法与类型检查；asyncio使用产品同类Selector事件循环，未改产品',
    'original_failure_preserved':'backend-targeted.log及原累计账',
    'scope_not_claimed':'真实SQL/PG/供应商/原全局账组合'})
names=['test_step018_control_snapshot', 'test_step018_audit_repairs']
names += ['test_step018_flows.IntegrationContractTests.'+x for x in (
 'test_valid_adopted_source_and_both_capabilities','test_unapproved_version_fragment_or_query_is_closed',
 'test_grant_expired_tampered_roster_and_price_are_closed','test_grant_expiry_after_admission_prevents_dispatch',
 'test_legacy_command_bytes_and_new_local_profile','test_legacy_teaching_canonical_has_no_new_null')]
names += ['test_step018_embedding_contracts.EmbeddingContractTests.'+x for x in (
 'test_v4_embedding_closed_and_v3_unchanged','test_worker_bound_and_secret_not_argv_or_receipt',
 'test_four_input_payload_with_007_hash','test_unknown_retained_and_no_second_send','test_actual_network_default_fails_before_admit')]
program='import asyncio,unittest;asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy());unittest.main(module=None)'
checks=[('backend-targeted-v2',py()+['-c',program,'-v',*names]),
 ('typecheck',['C:/Program Files/nodejs/node.exe',str(ROOT/'frontend/node_modules/typescript/bin/tsc'),'--noEmit','-p',str(ROOT/'frontend/tsconfig.json')])]
rows=[]
for label,command in checks:
    code=run(command,label,timeout=120);rows.append({'label':label,'command':command,'exit_code':code})
write(N/'product-checks-v2.json',{'sample':sample(),'checks':rows})
raise SystemExit(any(row['exit_code'] for row in rows))
