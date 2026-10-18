from audit_io import *
index = load(ROOT/'DocuN/evidence/TASK-101/review-03-input.json')
locked = {x['absolute_path']:x['sha256'] for x in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')}
checks=[]
for group in ('contracts','rules','current_objects','raw_files'):
    for x in index[group]:
        expected=x.get('sha256',x.get('expected'))
        actual=sha(x['path'])
        item={'group':group,'path':x['path'],'expected':expected,'actual':actual,'match':expected==actual}
        if group=='rules':
            item['locked_sha256']=locked.get(x['path'])
            item['match']=item['match'] and item['locked_sha256']==expected
        checks.append(item)
save('input-identity-check.json',{'at':stamp(),'total':len(checks),'matched':sum(x['match'] for x in checks),'objects':checks})
rawroot=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
rawnames=[str(Path(x['path']).relative_to(rawroot)) for x in index['raw_files']]
save('raw-navigation.txt','\n'.join(rawnames)+'\n')
excluded=index['excluded_implementation_self_reports']
save('read-order-record.json',{'at':stamp(),'source_prelog_not_yet_saved':True,'raw_content_read':False,'excluded_implementation_self_reports_not_read':excluded,'incidental_shared_state':{'path':'DocuS/执行动态文档.MD','read':'first 18 lines, routing only; aggregate judgments excluded'},'read_only_shell_failure':{'path':'backend/app/learning/repository.py','reason':'wrong path in narrow rg; actual activities/teaching_repository.py from card will be used','exit_code':1,'duration_seconds':0.3232489,'no_business_execution':True}})
finish('identity-baseline',{'total':len(checks),'matched':sum(x['match'] for x in checks),'by_group':{g:sum(x['group']==g for x in checks) for g in ('contracts','rules','current_objects','raw_files')},'changes':index['changes'],'raw_non_snapshots':[p for p in rawnames if not p.startswith('batch-01\\as-run\\') and 'post\\backend\\' not in p]})
if not all(x['match'] for x in checks):
    raise ValueError('identity drift')
