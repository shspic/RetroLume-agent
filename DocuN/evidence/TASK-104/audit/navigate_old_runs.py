from metadata import *
roots=[ROOT/'DocuN/evidence/TASK-103',ROOT/'DocuN/evidence/TASK-103/continuation-01',ROOT/'DocuN/evidence/TASK-103/continuation-02']
result=[]
for evidence in roots:
    ledger=load(evidence/'final/runs-ledger.json'); runs=ledger.get('runs',[]) if isinstance(ledger,dict) else ledger
    entries=[]
    for run in runs:
        name=run['name']; directory=ROOT/run['evidence_directory'] if run.get('evidence_directory') else Path(run.get('execution_path',run.get('path'))).parent
        execution=load(directory/'execution.json')
        entries.append({'name':name,'directory':str(directory),'exit_code':execution.get('exit_code'),'elapsed_seconds':execution.get('elapsed_seconds'),'execution_sha256':sha(directory/'execution.json'),'execution_keys':list(execution) if name==runs[0]['name'] else None,'source_mismatches_to_final':run.get('source_mismatches_to_final'), 'artifact_names':[p.name for p in directory.iterdir() if p.is_file()]})
    accounting=load(evidence/'final/accounting-final.json')
    result.append({'evidence_root':str(evidence),'runs':entries,'counts':accounting['counts'],'seconds':accounting['used_seconds'],'unknowns':accounting.get('unknowns'),'deviations':accounting.get('counter_deviation'),'limits':accounting.get('limits',accounting.get('count_limits'))})
save('old-run-navigation.json',result)
for group in result:
    print(json.dumps({'root':group['evidence_root'],'counts':group['counts'],'seconds':group['seconds'],'unknowns':group['unknowns'],'deviations':group['deviations']},ensure_ascii=False))
    for run in group['runs']: print(json.dumps({k:run[k] for k in ('name','directory','exit_code','source_mismatches_to_final','artifact_names')},ensure_ascii=False))
finish('actual-run-navigation-and-historical-counts',{'runs':sum(len(x['runs']) for x in result),'roots':3,'new_runs':0})
