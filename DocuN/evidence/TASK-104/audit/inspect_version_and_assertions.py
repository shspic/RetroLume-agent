from metadata import *
base=ROOT/'DocuN/evidence/TASK-103'
paths=['runs/real-16-fault-cleanup/execution.json','continuation-01/runs/real-12-resume-contract-status-and-absent/execution.json','continuation-02/runs/real-02-permit-corrected-composite/execution.json','continuation-01/final/bundle-chain.json','final/sql-snapshot-evidence.json']
for rel in paths:
    p=base/rel;v=load(p)
    shape={k:({'count':len(x),'first':x[0] if x and k in ('as_run','files','source_matches_build') else None} if isinstance(x,list) else {'keys':list(x)} if isinstance(x,dict) else x) for k,x in v.items()}
    if 'argv' in shape:shape['argv']='见执行原件，本次不执行'
    print(json.dumps({'path':str(p),'shape':shape},ensure_ascii=False))
for rel in ('backend/tests/fixtures/task103/memory_pg_smoke.py','backend/tests/fixtures/task103/memory_boundaries.py','backend/tests/fixtures/task103/c01/cleanup_gaps.py'):
    src=read(ROOT/rel)
    lines=src.splitlines()
    useful=[{'line':i+1,'text':line} for i,line in enumerate(lines) if any(x in line for x in ('assert ', 'check(', 'passed(', 'case(', 'capture', 'command', 'connect(', 'DELETE ', 'SELECT ', 'before', 'after'))]
    print(json.dumps({'fixture':rel,'lines':len(lines),'assertion_and_effect_lines':useful},ensure_ascii=False))
finish('old-version-raw-execution-and-assertion-navigation',{'new_run':False})
