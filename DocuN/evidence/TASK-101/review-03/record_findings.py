from audit_io import *
anchor=load(OWN/'audit-budget-anchor.json')
charged=time.monotonic()-anchor['fixed_charged_monotonic_origin']
assert charged+30<3600
raw=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
observation_answer='1.'+'0'*64+'1m/s'
save('R03-O01-precision-observation.md',f'''# R03-O01：既有超64有效位小数的精确对照限制（P2，非本轮阻断）

只读B级源码观察，未调用产品函数、测试或浏览器；不新占共享DEF编号，不改F02—F09状态。

实际文本：`{observation_answer}`，{len(observation_answer)}个ASCII字符，远低于AnswerBody的4096字符/12288字节限制；没有非法形状、开放语义或非有限量值。标准Decimal HALF_EVEN上下文中它精确等于1+10^-65。参考采用既有合法calculation样例120/120=1、unit=m/s、tolerance_decimal=None。

当前policy88—91/127—129完整文法接受该明确量值并构造精确Decimal；200—202即使同单位也在prec=64中乘除1，会把超出64有效位的差值舍掉；203—204按舍后值判matched。与099第5.2节366行“未提供就精确对照”存在这一个极小精度边界。若两个合法不同实例的低信任意见全met，该support会与其他matched一样进入既有progress资格路径；此传播是B级条件推导，没有新增运行返回值。

旧pre/policy已采用相同prec=64主体，旧finditer也接受这条完整单量值。因此不是repair04引入的回归，不恢复原已闭其他缺陷，也不否定原两条否定/不确定触发已闭合。偏差仅1e-65，未见本轮普通量值/否定或尾文被放行的实际故障；按有限教学切片评为P2非阻断。不能把18项PASS推广为任意十进制位数的绝对精确性。

后续最小建议：同单位保留原Decimal，不作舍入乘除；跨单位以足够精度或精确比例比较，或者明确超支持精度时unknown。将来有相应局部修复授权时仅补定向离线边界例，不增PG/HTTP/Windows/browser门。本轮不修改或运行任何产品。
''')
functions=load(OWN/'all-protected-function-bytes.json')
ctrl=load(OWN/'execution-control-check.json')
pairs=load(OWN/'runtime-evidence-pairing.json')
notes=load(raw/'method-applicability.json')
assert [x['method'] for x in notes['final_bindings']]==pairs['stderr_methods']
for x in notes['final_bindings']:
    expected_changed=not x['method'].startswith('tests.test_teaching_policy.')
    assert x['file_changed_in_04']==expected_changed
source_pre=load(OWN/'read-order-record.json')
save('audit-findings.json',{'at':stamp(),'scope':'TASK-101/R-095 review-03 F01 delta only','code_axis':'pass in authorized F01 scope; R03-O01 pre-existing P2 observation retained','evidence_axis':'pass with local-function A / propagation B / inherited old limitations','execution_control_axis':'pass on actual historical bounded batch and conservative/unknown accounting; no new resources','overall':'F01 closed; no new P0/P1 or definite regression from repair04; approved finite G8 ready for orchestration closure','F01':{'DEF':'DEF-008','former_severity':'P1','status':'closed in authorized limited support/progress scope','counterexamples':['平均速度不等于1m/s','答案未知，可能1m/s'],'reference_status':'matched','answer_status':'unchecked','support_status':'unchecked','projection_status':'practising','independent_answers':[],'local_runtime_grade':'A on repair04 full copies, not a new audit run','internal_unknown_assignment_and_repository_propagation_grade':'B'},'new_blocking_findings':[],'nonblocking_observations':[{'id':'R03-O01','severity':'P2','introduced_by_repair04':False,'grade':'B conditional default Decimal context; no new runtime'}],'author_notes_read_after_prelog':True,'implementation_self_report_body_not_decoded_or_adopted':True,'incidental_access':[source_pre['incidental_shared_state'],{'path':'DocuN/results/TASK-100-result.md','operation':'initial check_control.py included report record and SHA256 only before assertion failure; never decoded/printed or used as self-evaluation; v2 skips it','scope_deviation':'extra identity read, not author narrative review'}],'protected_policy_functions':9,'protected_test_functions':26,'full_snapshots':133,'methods':18,'subtest_callbacks':81,'stdout_samples':64,'method_note_bindings_match_independent_pairs':True,'business_execution_new':0,'metadata_failures':[{'command':'narrow rg','path':'backend/app/learning/repository.py','exit_code':1,'seconds':0.3232489,'reason':'wrong path; correct activities/teaching_repository.py subsequently read'}, {'script':'source_structure.py','exit_code':1,'seconds':0.4125323,'reason':'new-file diff fromfile must be /dev/null; v2 exact full diff/post matches'}, {'script':'pair_runtime.py','exit_code':1,'seconds':0.369566,'reason':'unittest stderr parentheses already contain full method ID; v2 pairs exact IDs'}, {'script':'check_control.py','exit_code':1,'seconds':0.4344155,'reason':'author result changed_from_pre record is not a source delta; v2 explicitly excludes self-report content'}],'unchanged_historical_authority_paths':[x['path'] for x in ctrl['final_snapshot_rows'] if x['binding']=='orchestration-receipt-07/before'],'active_charged_checkpoint_seconds':charged,'first_reads_unknown_conservatively_charged_seconds':600,'final_reply_allowance_seconds':30,'original_permits_ended':True})
finish('findings-and-method-notes-checked',{'charged_active_checkpoint_seconds':charged,'remaining_seconds':3600-charged,'F01':'closed','new_blocking_findings':0,'nonblocking_existing_P2':1,'author_note_methods_independently_paired':18,'historical_routing_snapshot_paths':[x['path'] for x in ctrl['final_snapshot_rows'] if x['binding']=='orchestration-receipt-07/before']})
