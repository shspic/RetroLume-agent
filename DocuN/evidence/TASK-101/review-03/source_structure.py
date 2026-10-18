from audit_io import *
import difflib
rawroot=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
def functions(path):
    src=read(path); lines=src.splitlines(keepends=True); tree=ast.parse(src)
    out={}
    def visit(nodes, prefix=''):
        for node in nodes:
            if isinstance(node, ast.ClassDef):
                visit(node.body,prefix+node.name+'.')
            elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                start=min([node.lineno]+[x.lineno for x in node.decorator_list])
                out[prefix+node.name]={'line':start,'end':node.end_lineno,'text':''.join(lines[start-1:node.end_lineno])}
    visit(tree.body)
    return out
records=[]
for rel, changed in [('backend/app/learning/teaching_policy.py',{'_answer_quantity'}),('backend/tests/test_task100_repair.py',{'RepairOfflineTests.test_answer_value_unit_and_ambiguous_input_are_separate_from_reference','RepairOfflineTests.test_misleading_model_met_cannot_advance_numeric_conflict_or_unknown'})]:
    old=functions(rawroot/'pre'/rel); current=functions(ROOT/rel)
    for name,value in old.items():
        same=name in current and value['text']==current[name]['text']
        records.append({'path':rel,'name':name,'old_line':value['line'],'current_line':current.get(name,{}).get('line'),'allowed_change':name in changed,'identical_source_segment':same,'test_method':name.split('.')[-1].startswith('test_')})
    unexpected=[name for name in current if name not in old and name!='_answer_auxiliary']
    if unexpected or any(not x['identical_source_segment'] and not x['allowed_change'] for x in records if x['path']==rel):
        raise ValueError('unexpected protected-function change')
index=load(ROOT/'DocuN/evidence/TASK-101/review-03-input.json')
diffchecks=[]
for x in index['changes']:
    rel=x['path']; before='' if x['absent_before'] else read(rawroot/'pre'/rel)
    after=read(ROOT/rel)
    computed=''.join(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
    provided=read(rawroot/x['diff'])
    match=computed==provided
    diffchecks.append({'path':rel,'computed_diff_equals_original':match,'current_equals_post':(ROOT/rel).read_bytes()==(rawroot/x['post']).read_bytes(),'before_sha256':None if x['absent_before'] else sha(rawroot/'pre'/rel),'after_sha256':sha(ROOT/rel)})
    if not match or not diffchecks[-1]['current_equals_post']:
        raise ValueError('diff/post mismatch')
save('source-structure-check.json',{'at':stamp(),'methods':records,'diff_post_checks':diffchecks,'test_names':{p:list(functions(ROOT/p)) for p in ('backend/tests/test_teaching_policy.py','backend/tests/test_task100_answer_support.py')}})
finish('ast-protected-methods-and-diffs',{'policy_protected':sum(x['path'].endswith('teaching_policy.py') and not x['allowed_change'] and x['identical_source_segment'] for x in records),'protected_test_methods':sum(x['test_method'] and not x['allowed_change'] and x['identical_source_segment'] for x in records),'diff_checks':diffchecks})
