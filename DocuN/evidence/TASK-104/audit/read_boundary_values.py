from metadata import *
base=ROOT/'DocuN/evidence/TASK-103'
boundaries=load(base/'memory-boundaries-result.json')
print(json.dumps({'raw_boundary_cases':boundaries['cases']},ensure_ascii=False))
for filename in ('migration-fault-resume-result.json','migration-upgrade-resume-result.json'):
    v=load(base/filename)
    print(json.dumps({'file':filename,'actual_cases':v['cases']},ensure_ascii=False))
src=read(ROOT/'backend/tests/fixtures/task103/integration_remaining.py')
for i,line in enumerate(src.splitlines()):
    if any(x in line for x in ('assert ','check(', 'before_', 'after_', 'after_admit', 'before_result', 'rebuild','no_evidence','purge')):print(str(i+1)+': '+line)
finish('original-migration-role-and-boundary-values',{'new_business_execution':False})
