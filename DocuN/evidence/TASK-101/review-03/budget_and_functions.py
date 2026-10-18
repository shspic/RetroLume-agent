from audit_io import *
from collections import Counter
receipt=load(OWN/'audit-receipt.json')
now=datetime.datetime.now(datetime.timezone.utc)
receipt_wall=datetime.datetime.fromisoformat(receipt['at'])
spent=(now-receipt_wall).total_seconds()+receipt['pre_receipt_conservative_charge_seconds']
mono=time.monotonic()
save('audit-budget-anchor.json',{'at':stamp(),'fixed_charged_monotonic_origin':mono-spent,'fixed_monotonic_deadline':mono-spent+3600,'conservative_pre_receipt_charge_seconds':600,'original_receipt_utc':receipt['at'],'original_wall_deadline_unchanged':receipt['active_deadline_utc'],'basis':'original receipt clock plus elapsed; first tool reads not individually timed; no reset or exact-first-read claim','budget_at_anchor_seconds':spent,'first_reads_and_shell_overhead':'not individually measured; retained unknown','final_packaging_allowance_seconds':30,'own_executable':sys.executable,'own_version':sys.version})
raw=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
comparisons=[]
for rel, allowed in [('backend/app/learning/teaching_policy.py',{'_answer_quantity'}),('backend/tests/test_task100_repair.py',{'test_answer_value_unit_and_ambiguous_input_are_separate_from_reference','test_misleading_model_met_cannot_advance_numeric_conflict_or_unknown'})]:
    def collect(path):
        src=read(path); lines=src.splitlines(keepends=True)
        return {(n.name,n.col_offset):''.join(lines[min([n.lineno]+[d.lineno for d in n.decorator_list])-1:n.end_lineno]) for n in ast.walk(ast.parse(src)) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    pre,cur=collect(raw/'pre'/rel),collect(ROOT/rel)
    for key,text in pre.items():
        comparisons.append({'path':rel,'name':key[0],'column':key[1],'protected':key[0] not in allowed,'identical':cur.get(key)==text,'segment_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest()})
    if any(x['protected'] and not x['identical'] for x in comparisons if x['path']==rel):
        raise ValueError('protected byte segment drift')
save('all-protected-function-bytes.json',comparisons)
finish('fixed-budget-anchor-and-all-functions',{'charged_active_seconds':spent,'protected_counts':dict(Counter(x['path'] for x in comparisons if x['protected'])),'all_protected_identical':all(x['identical'] for x in comparisons if x['protected'])})
