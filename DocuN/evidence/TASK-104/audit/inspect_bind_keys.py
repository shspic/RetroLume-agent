from metadata import *
p=ROOT/'DocuN/evidence/TASK-103/continuation-02/runs/real-02-permit-corrected-composite/execution.json';v=load(p)
print(json.dumps({'before_first':v['before'][0],'after_first':v['after'][0]},ensure_ascii=False))
p=ROOT/'DocuN/evidence/TASK-103/continuation-01/final/bundle-chain.json';v=load(p)
print(json.dumps({'dist':v['dist'],'loaded':v['loaded'],'sources':v['source_matches_build']},ensure_ascii=False))
paths=list((ROOT/'DocuN/evidence/TASK-103').glob('*.json'))
print(json.dumps({'top_raw_names':[x.name for x in paths if not any(k in x.name for k in ('result-prefix','package','delivery','matrix','snapshot','index','plan','result-history'))]},ensure_ascii=False))
