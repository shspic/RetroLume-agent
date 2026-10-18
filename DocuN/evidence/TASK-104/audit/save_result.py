from metadata import *
import re
receipt=load(OWN/'audit-receipt.json');now=time.monotonic();active=now-receipt['fixed_active_monotonic_origin']
assert active+60<21600
metadata_entries=[json.loads(line) for line in read(OWN/'metadata-actions.jsonl').splitlines() if line.strip()]
known=sum(x['metadata_measured_seconds'] for x in metadata_entries)
ledger=load(ROOT/'DocuN/evidence/TASK-104/runtime-ledger.json')
account={'at':stamp(),'permit':receipt['permit'],'fixed_active_monotonic_origin':receipt['fixed_active_monotonic_origin'],'fixed_active_deadline':receipt['fixed_active_deadline'],'active_package_checkpoint_seconds':active,'active_charged_upper_with_60s_final_packaging_reply':active+60,'active_limit':21600,'first_reads_not_individually_measured':True,'initial_conservative_charge':360,'metadata_completed_helpers_measured_seconds':known,'metadata_tool_shell_first_read_overhead':'未逐项登记，未知保留，不称0或精确全部时间','metadata_conservative_charge_seconds':600,'metadata_limit':1800,'runtime_counts':ledger['counts'],'runtime_known_seconds':ledger['used'],'resource_stopped':load(OWN/'final-readonly-resource-state.json'),'business_writes':0,'allowed_ram_password_reset':1,'status':'已完成独立审查；补证受entry/offline到限停止，最后场景NOT_RUN；只剩结果封装回传'}
save('session-accounting.json',account)
draft=read(OWN/'result-draft.md')
measurement='\n最终封装检查点主动计入'+format(active,'.3f')+'秒，含初读保守360秒；加封装/回传预留60秒为'+format(active+60,'.3f')+'/21600秒。已完成helper函数已测'+format(known,'.6f')+'秒，仅为部分口径；工具/shell/最初读入未逐项精确计量，未知保留。metadata保守记600/1800秒。最终325身份行及291完整post仍相同，三CID Running=false/Pid0、本卡相关Python/Node/Chrome进程0、18103/55443等端口可用；最终核为只读元数据，不恢复运行许可。\n'
draft+='\n## 六 封装与最终计量\n'+measurement+'\n完整自有证据与最终冻结检查见[交付核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/delivery-check.json)，结果文件保存回读后交回，编排据此维护唯一总账。\n'
result=ROOT/'DocuN/results/TASK-104-result.md'
assert not result.exists(),'已有104结果，禁止覆盖历史'
result.write_text(draft,encoding='utf-8')
assert read(result)==draft
links=[]
for target in re.findall(r'\[[^\]]+\]\((D:/[^)]+)\)',draft):
    path=Path(re.sub(r':\d+$','',target))
    if path.name=='delivery-check.json':continue
    assert path.exists(),target
    links.append({'target':target,'readable':True})
check={'at':stamp(),'result_path':str(result),'result_sha256':sha(result),'result_bytes':len(result.read_bytes()),'result_saved_readable':True,'links':links,'scope':'G9有限批准切片集中独立终审','overall':'不通过','blocking':'R104-F01/P1','evidence_gap':'最后引用迟到NOT_RUN，三根104前置失败','new_business_POST_SQL':0,'product_unchanged':True,'identity_rows':325,'root_counts':ledger['counts'],'actual_root_failures_preserved':3,'active_checkpoint_seconds':active,'active_upper_with_reply':active+60,'no_more_runtime_permission':True}
save('delivery-check.json',check)
finish('result-saved-and-readable', {k:v for k,v in check.items() if k!='links'})
