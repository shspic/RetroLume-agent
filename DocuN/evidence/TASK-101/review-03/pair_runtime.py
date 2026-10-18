from audit_io import *
from collections import Counter
import re
raw=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
index=load(ROOT/'DocuN/evidence/TASK-101/review-03-input.json')
observer=load(raw/'batch-01/unittest-result.json')
execution=load(raw/'batch-01/execution.json')
invocation=read(raw/'batch-01/unittest-invocation.txt')
stderr=read(raw/'batch-01/stderr.txt')
stdout=read(raw/'batch-01/stdout.txt')
stderr_names=[f'{m[2]}.{m[1]}' for m in re.finditer(r'^(test_[\w]+) \(([^)]+)\) \.\.\. ok$',stderr,re.M)]
expected=[]
for rel,module in [('backend/tests/test_teaching_policy.py','tests.test_teaching_policy'),('backend/tests/test_task100_answer_support.py','tests.test_task100_answer_support')]:
    tree=ast.parse(read(ROOT/rel))
    for cls in tree.body:
        if isinstance(cls,ast.ClassDef):
            expected.extend(f'{module}.{cls.name}.{n.name}' for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_'))
expected.extend('tests.test_task100_repair.RepairOfflineTests.'+x for x in ('test_answer_value_unit_and_ambiguous_input_are_separate_from_reference','test_misleading_model_met_cannot_advance_numeric_conflict_or_unknown'))
assert len(expected)==18 and sorted(expected)==sorted(observer['methods'])
assert stderr_names==observer['methods'] and 'Ran 18 tests' in stderr and stderr.rstrip().endswith('OK')
assert invocation.strip()==execution['command']['argv'][3].strip()
assert observer['testsRun_method_count']==18 and len(observer['methods'])==18
assert observer['subtest_count']==len(observer['subtests'])==81 and all(x['success'] for x in observer['subtests'])
assert all(observer[k]==0 for k in ('failure_count','error_count','skip_count','expected_failure_count','unexpected_success_count'))
assert observer['successful'] and execution['exit_code']==0
actual=[json.loads(line[len('ANSWER_SUPPORT_CASE '):]) for line in stdout.splitlines() if line.startswith('ANSWER_SUPPORT_CASE ')]
export=load(raw/'case-results.json')
assert len(actual)==export['count']==64 and actual==export['cases']
callbacks=[]
for x in observer['subtests']:
    tail=x['subtest'].rsplit(') (',1)[1][:-1]
    parsed=ast.parse('f('+tail+')', mode='eval').body
    callbacks.append({'method':x['method'],'parameters':{k.arg:ast.literal_eval(k.value) for k in parsed.keywords},'success':x['success']})
paired=[]
new_prefix='tests.test_task100_answer_support.AnswerSupportTests.'
methods={'positive':'test_closed_positive_answers_preserve_units_and_verified_auxiliaries','unknown':'test_negative_uncertain_quoted_and_open_answers_remain_unchecked','true_conflict':'test_real_conflicts_and_reference_checks_are_separate','reference_conflict':'test_real_conflicts_and_reference_checks_are_separate','unitless':'test_unitless_approximation_and_program_text_keep_existing_discipline','program_not_executed':'test_unitless_approximation_and_program_text_keep_existing_discipline'}
for rownum,x in enumerate(actual,1):
    case=x['case']; method=methods.get(case,'test_valid_distinct_instances_block_unknown_and_allow_two_correct_answers')
    params={'case':case} if 'answers' in x else ({'program':x['answer']} if case=='program_not_executed' else {'answer':x['answer']})
    if case=='reference_conflict': params['reference']='broken'
    matches=[c for c in callbacks if c['method']==new_prefix+method and c['parameters']==params]
    assert len(matches)==1,(rownum,case,params)
    support=x['support']
    if isinstance(support,dict):
        assert support['dimension_ids']==['value'] or case=='program_not_executed'
        if case in ('unknown','program_not_executed'):
            assert support['reference_status']=='matched' and support['answer_status']==support['status']=='unchecked'
            assert 'answer_value_decimal' not in support
        elif case=='positive':
            assert support['reference_status']==support['answer_status']==support['status']=='matched'
            assert support['unit_matched'] and support['value_matched'] and support['answer_value_decimal']=='1'
        elif case=='true_conflict':
            assert support['reference_status']=='matched' and support['answer_status']==support['status']=='conflict'
        elif case=='reference_conflict':
            assert support['reference_status']==support['status']=='conflict'
        elif case=='unitless':
            want='matched' if x['answer'].strip() in ('约0.5','约 0.5','0.5') else 'unchecked'
            assert support['reference_status']=='matched' and support['answer_status']==support['status']==want
    else:
        assert len(support)==2 and all(s['reference_status']=='matched' for s in support)
        projection=x['projection']; want_count={'negative':0,'uncertain':0,'correct_then_unknown':1,'unknown_then_correct':1,'two_correct':2}[case]
        assert len(projection['independent_answers'])==want_count
        assert projection['status']==('evidence_sufficient' if want_count==2 else 'practising')
        assert projection['contested']==projection['assisted']==[]
        if want_count==0: assert all(s['answer_status']==s['status']=='unchecked' for s in support)
        if want_count==2: assert all(s['answer_status']==s['status']=='matched' for s in support)
        exercises=x['exercises']; assert exercises[0]['variant']['instance_data']!=exercises[1]['variant']['instance_data']
        assert [e['variant']['purpose'] for e in exercises]==['initial','retest']
        for e,expected_distance,expected_minutes in zip(exercises,('120','180'),('2','3')):
            q={q['name']:q for q in e['variant']['instance_data']['quantities']}
            assert q['distance']['value_decimal']==expected_distance and q['time']['value_decimal']==expected_minutes
            n=e['reference_points'][0]['numeric']; assert n['left']==n['right']==expected_distance and n['value_decimal']=='1' and n['tolerance_decimal'] is None
        facts=x['facts']; ids=[f['record_id'] for f in facts]; assert len(set(ids))==6
        for f in facts:
            if f['kind']=='answer':
                body=json.loads(f['body']); assert body['kind']=='initial' and body['exposures_seen']==[]
            elif f['kind']=='feedback':
                assert all(d['observation']=='met' for d in f['document']['result']['dimension_observations'])
    paired.append({'stdout_line':rownum,'case':case,'method':new_prefix+method,'parameters':params,'actual':x})
current={x['path']:x['sha256'] for x in index['current_objects']}
asrun=load(raw/'batch-01/as-run-identities.json'); after=load(raw/'batch-01/after-identities.json')
aftermap={x['path']:x for x in after}
identities=[]
assert len(asrun)==len(after)==len(current)==133
for x in asrun:
    path=x['path']; snapshot=raw/'batch-01/as-run'/x['relative_path']; a=aftermap[path]
    copies_equal=Path(path).read_bytes()==snapshot.read_bytes()
    expected_sha=current[path]
    okay=(x['sha256']==sha(snapshot)==sha(path)==expected_sha==a['as_run_sha256']==a['after_sha256']) and copies_equal
    assert okay,path
    identities.append({'path':path,'snapshot':str(snapshot),'sha256':expected_sha,'full_bytes_equal':copies_equal,'after_equal':True})
identity=load(raw/'batch-01/python-identity.json'); assert sha(identity['executable'])==identity['sha256']
result={'at':stamp(),'observer_source_equals_actual_invocation':True,'expected_source_methods':expected,'stderr_methods':stderr_names,'all_18_methods_paired':True,'callback_counts':dict(Counter(x['method'] for x in callbacks)),'callback_parameter_pairs':callbacks,'stdout_samples':64,'stdout_export_exact':True,'case_counts':dict(Counter(x['case'] for x in actual)),'sample_pairs':paired,'as_run_full_copy_count':133,'as_run_after_current_checks':identities,'python_executable_identity_match':True,'no_new_product_execution':True}
save('runtime-evidence-pairing.json',result)
finish('runtime-evidence-paired',{'methods':18,'subtests':81,'samples':64,'per_method_callbacks':result['callback_counts'],'case_counts':result['case_counts'],'full_asrun_matches':133,'stdout_export_exact':True,'execution_exit_code':execution['exit_code'],'python_executable_hash_match':True})
