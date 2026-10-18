from metadata import *
base=ROOT/'DocuN/evidence/TASK-103'
rounds=[]
for suffix in ('','continuation-01','continuation-02'):
    path=base/suffix/'final/accounting-final.json';v=load(path)
    rounds.append({'round':suffix or '初轮','path':str(path),'sha256':sha(path),'counts':v['counts'],'seconds':v['used_seconds'],'active_seconds':v.get('active_conservative_including_reply',v.get('active_used_seconds')),'unknowns':v.get('unknowns',{'metadata_exact':v.get('metadata_exact'),'metadata_unknown_retained':v.get('metadata_unknown_retained'),'metadata_exact_split_unknown':v.get('metadata_exact_split_unknown')}),'counter_deviation':v.get('counter_deviation'),'stop_reason':v.get('stop_reason',v.get('stop_reasons'))})
assert sum(x['counts']['entry'] for x in rounds)==39
assert sum(x['counts']['sup'] for x in rounds)==38
ledger=load(ROOT/'DocuN/evidence/TASK-104/runtime-ledger.json')
summary={'at':stamp(),'historical_rounds':rounds,'historical_real_roots_total':39,'historical_SUP_total':38,'new_counts':ledger['counts'],'new_seconds':ledger['used'],'citation_direct_probe':'NOT_RUN','product_tests_compile_build':0,'business_POST_SQL_writes':0,'allowed_infrastructure_password_reset':1,'new_stop_basis':'entry3/3与fixture_offline3/3到限；三种前置失败，未追加第四根','new_controls_note':'首根cleanup判断false已由独立容器属性诊断证明全停；闭stdin辅助进程按出生/命令停止，耗时单列计入cleanup；原失败记录不改'}
save('execution-control-conclusion.json',summary)
finish('historical-and-current-control-reconciled',{'old_roots':39,'old_SUP':38,'new':ledger['counts'],'seconds':ledger['used'],'root_permission_ended':True})
