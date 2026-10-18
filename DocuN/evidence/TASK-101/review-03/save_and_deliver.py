from audit_io import *
import os, re
index=load(ROOT/'DocuN/evidence/TASK-101/review-03-input.json')
receipt=load(OWN/'audit-receipt.json'); anchor=load(OWN/'audit-budget-anchor.json')
result_path=ROOT/'DocuN/results/TASK-101-result.md'
old=(OWN/'prior-report-preserved.md').read_bytes()
assert result_path.read_bytes()==old and len(old)==70370
assert hashlib.sha256(old).hexdigest()=='b75f00d8a9a1e3c564d221dc70ca591cb0fa0a23ddf276a691cd1d323ba1dbb2'
checks=[]
for group in ('contracts','rules','current_objects','raw_files'):
    for item in index[group]:
        expected=item.get('sha256',item.get('expected')); actual=sha(item['path'])
        checks.append({'group':group,'path':item['path'],'expected':expected,'actual':actual,'match':expected==actual})
assert len(checks)==306 and all(x['match'] for x in checks)
save('final-input-identity-check.json',{'at':stamp(),'total':306,'matched':306,'objects':checks,'business_execution_new':0})
logs=[json.loads(x) for x in read(OWN/'metadata-actions.jsonl').splitlines() if x.strip()]
known_helper=sum(x['elapsed_seconds'] for x in logs)
failed_seconds=0.3232489+0.4125323+0.369566+0.4344155
charged_checkpoint=time.monotonic()-anchor['fixed_charged_monotonic_origin']
active_charged_upper=charged_checkpoint+30
assert active_charged_upper<3600 and known_helper+failed_seconds<180<300
account={'at':stamp(),'permit':'TASK-101-F01-review-03-20261006','active_limit_seconds':3600,'fixed_charged_monotonic_origin':anchor['fixed_charged_monotonic_origin'],'fixed_monotonic_deadline':anchor['fixed_monotonic_deadline'],'active_charged_checkpoint_seconds':charged_checkpoint,'active_charged_upper_with_final_reply_allowance_seconds':active_charged_upper,'pre_receipt_first_reads_unknown':True,'pre_receipt_conservative_charge_seconds':600,'final_tool_return_and_reply_allowance_seconds':30,'metadata_limit_seconds':300,'metadata_completed_function_measured_seconds':known_helper,'failed_helpers_and_narrow_rg_known_tool_seconds':failed_seconds,'separate_read_method_notes_known_tool_seconds':0.4265144,'all_initial_reads_and_shell_overhead':'unknown individually; not zero or exact full-overhead claim','metadata_conservative_charge_seconds':180,'metadata_charge_basis':'conservative budget reservation for small standard-library helpers and file reads; measured function/tool values are partial and different, not summed as complete precise time','business_runs':0,'resource_counts':{'entry':0,'container':0,'app':0,'SUP':0,'browser':0,'driver':0,'build':0,'model':0,'tool':0,'network_install':0},'status':'all required review complete; final save and readable history check pending in this bounded helper'}
save('session-accounting.json',account)
prefix=read(OWN/'report-prefix.md')
metric=f'最终封装检查点主动计入{charged_checkpoint:.3f}秒（含初读保守600秒），加回传预留30秒为{active_charged_upper:.3f}/3600秒；已完成helper函数已测{known_helper:.6f}秒，四个失败工具单列已知{failed_seconds:.7f}秒，另方法说明只读工具0.4265144秒；这些不冒称完整shell开销或相同统计口径。纯元数据预算保守记180/300秒，未知明列。最终306项仍匹配，完整报告原尾段70370字节/SHA不变。\n\n'
prefix=prefix.replace('\n---\n\n以下review-02', '\n'+metric+'---\n\n以下review-02')
save('report-prefix-final.md',prefix)
links=[]
for rawpath in re.findall(r'\[[^\]]+\]\((D:/[^)]+)\)',prefix):
    p=Path(re.sub(r':\d+$','',rawpath))
    assert p.exists(),str(p)
    links.append({'target':rawpath,'exists':True})
prefix_bytes=prefix.encode('utf-8')
new_bytes=prefix_bytes+old
pending=OWN/'TASK-101-result.pending.md'
pending.write_bytes(new_bytes)
assert result_path.resolve()==(ROOT/'DocuN/results/TASK-101-result.md').resolve()
os.replace(pending,result_path)
actual=result_path.read_bytes()
assert actual==new_bytes and actual[-70370:]==old
final_checkpoint=time.monotonic()-anchor['fixed_charged_monotonic_origin']
assert final_checkpoint+30<3600
account.update({'at_final_package':stamp(),'active_charged_final_package_seconds':final_checkpoint,'active_charged_final_upper_with_reply_seconds':final_checkpoint+30,'checkpoint_to_final_package_seconds':final_checkpoint-charged_checkpoint,'status':'complete; no further product execution; permit work ends with result handback'})
save('session-accounting.json',account)
delivery={'at':stamp(),'result_path':str(result_path),'result_bytes':len(actual),'result_sha256':sha(result_path),'prefix_bytes':len(prefix_bytes),'preserved_history_bytes':len(old),'preserved_history_sha256':hashlib.sha256(actual[-70370:]).hexdigest(),'history_full_bytes_equal':True,'result_saved_and_readable':True,'markdown_file_links':links,'final_inputs_total':306,'final_inputs_matched':306,'new_product_execution':0,'F01':'closed within approved finite scope','nonblocking_existing_P2':'R03-O01; no new P0/P1 or regression','G8':'approved finite slice ready for orchestration closure; no project/STEP/V19 signoff','active_charged_upper_seconds':account['active_charged_final_upper_with_reply_seconds'],'metadata_conservative_charge_seconds':180}
save('delivery-check.json',delivery)
finish('final-save-and-history-check', {k:v for k,v in delivery.items() if k!='markdown_file_links'})
