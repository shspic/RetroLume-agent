"""S1—S3 的受控返回样本；只合成 provider 返回，不评真实模型质量。"""
from __future__ import annotations
import json

MATERIAL='''平均速度 = 路程 ÷ 时间。2 分钟走 120 米，平均速度为 1 米/秒。 分钟换秒要乘 60。60m/min 等于 1m/s；60m/s 则大 60 倍。数量级先统一单位。
原子性使同一事务全部成功或全部不生效；原子性不能单独保证隔离性。 转账 A100/B50，扣 10 后加 10 失败，原子性成立时仍为 A100/B50；材料未给隔离级别。
程序 count=0 遍历列表，只在 value>0 时加 1；0 不满足条件，return 在循环后。 输入 [-2,0,3,5] 的逐次 count 为 0/0/1/2，返回 2；只阅读推理，不执行程序。
'''
GOAL='能换算平均速度、解释原子性并手推程序条件'

def _citations(citation, node, point=None):
    if isinstance(citation,str): return [citation]  # explicit DTO-only legacy helper
    return citation[node if point is None else f'{node}.{point}']

def path(citation):
    definitions=[('单位与数量级','先统一时间单位并说明数量级',['value','unit','reason','order'],[]),
        ('原子性与隔离','解释整体生效并区分并发可见性',['state','atomic_explanation','property_distinction','evidence_boundary'],[0]),
        ('程序条件与返回','手推严格正数条件、逐次状态及返回位置',['result','condition','trace','return_position'],[0])]
    return {'result_type':'path','message':'先核单位，再按资料复习概念和程序推理；能力目前未知。',
        'nodes':[{'title':title,'objective':objective,'prerequisites':prerequisites,'rationale':'依据当前合成资料与尚未观察的能力；完成依据需独立复测。',
            'citations':_citations(citation,f'n{index+1}'),'completion_dimensions':[{'dimension':d,'required_point':'作答明确说明并符合给定资料'} for d in dims]} for index,(title,objective,dims,prerequisites) in enumerate(definitions)]}

def exercise(task,citation):
    nid=task['node_id']; purpose=task['purpose']; parent=task.get('parent_exercise_record_id'); feedback=task.get('parent_feedback_record_id')
    if nid=='n1':
        previous=task.get('parent_feedback',{}).get('message','')
        distance=240 if purpose=='retest' and '180' in previous else 180 if purpose=='retest' else 120
        minutes=distance//60
        stem=f'{minutes} 分钟走 {distance} 米，平均速度是多少？说明换算、单位与数量级。'
        points=[('p1','统一秒后速度为 1 m/s。'),('p2','分钟乘 60 才是秒。'),('p3','直接把分钟当秒会大 60 倍。'),('p4','明确量纲与数量级检查。')]
        dims=['value','unit','reason','order']; kind='calculation'
        data={'kind':'calculation','quantities':[{'name':'distance','value_decimal':str(distance),'unit':'m'},{'name':'time','value_decimal':str(minutes),'unit':'min'}]}
    elif nid=='n2':
        kind='concept';stem='A100/B50 同一事务扣 10 成功、加 10 失败，原子性成立时最终是多少？是否单独保证隔离？资料能判隔离级别吗？'
        points=[('p1','最终 A100/B50。'),('p2','全部成功或全部不生效。'),('p3','原子性不能单独保证隔离。'),('p4','材料未给具体隔离级别。')]
        dims=['state','atomic_explanation','property_distinction','evidence_boundary']
        data={'kind':'concept','scenarios':[{'label':'转账失败','text':'A100/B50；扣10后加10失败。'}]}
    else:
        kind='program';stem='输入 [-2,0,3,5] 返回多少？给逐次 count，解释 0 是否计入与 return 位置。'
        points=[('p1','结果为 2。'),('p2','0>0 为假。'),('p3','逐次 count 为 0/0/1/2。'),('p4','return 在循环后。')]
        dims=['result','condition','trace','return_position']
        data={'kind':'program','language':'Python','code':'def count_positive(values):\n    count = 0\n    for value in values:\n        if value > 0:\n            count += 1\n    return count',
            'inputs':[{'name':'values','value_json':'[-2,0,3,5]'}],'manual_expected':'2，逐次0/0/1/2'}
    references=[{'point_id':pid,'text':text,'citations':_citations(citation,nid,pid),'numeric':None} for pid,text in points]
    if kind=='calculation': references[0]['numeric']={'value_decimal':'1','unit':'m/s','operation':'divide','left':str(distance),'right':str(distance),'tolerance_decimal':None}
    return {'result_type':'exercise','message':'按有限资料完成练习，能力仍待观察。','exercise_type':kind,'difficulty':2,'stem':stem,'reference_points':references,
        'reference_explanation':'按给定资料逐项核对，未知原因保留；本样本未运行用户程序。',
        'dimensions':[{'id':dim,'point_ids':[f'p{i+1}'],'description':description} for i,(dim,description) in enumerate(zip(dims,
            ['给出数值或最终状态','说明单位、性质或条件','写出换算依据或逐步过程','说明数量级、资料边界或返回位置']))],
        'hint':'先写依据，再对照单位、条件或逻辑关系。',
        'variant':{'purpose':purpose,'parent_exercise_record_id':parent,'parent_feedback_record_id':feedback,'instance_data':data}}

def feedback(task,citation):
    ex=task['exercise']; answer=task['answer_text']; kind=ex['exercise_type']
    wrong='60m/s' in answer or '0.01m/s' in answer or '能够单独保证隔离' in answer or '0也满足' in answer
    correct_reason={'calculation':'120÷2的算术商60可保留，但须按m/min解释，不能称为60m/s。',
        'concept':'已提出原子性与隔离性的关系；仍须分别核查两种性质。','program':'返回2这一结果可保留。'}
    error_reason={'calculation':'分钟不能直接当秒；2分钟是120秒，120÷120=1m/s，60m/s大60倍。',
        'concept':'原子性只约束全部成功或不生效，不能单独保证隔离性；材料没有给隔离级别。',
        'program':'0>0为假，0不计入；逐次count为0/0/1/2，return位于循环后。'}
    node={'calculation':'n1','concept':'n2','program':'n3'}[kind]
    item={'answer_excerpt':answer[:200],'explanation':correct_reason[kind] if wrong else '答案明确说明了给定资料中的依据。',
          'point_ids':['p1'],'citations':_citations(citation,node)}
    dims=ex['dimensions']
    wrong_observations={'calculation':['not_met','not_met','unknown','unknown'],
        'concept':['unknown','unknown','not_met','unknown'],'program':['met','not_met','unknown','unknown']}
    observations=[{'id':d['id'],'observation':wrong_observations[kind][i] if wrong else 'met','reason':'按当前给定答案和资料核对，暂不推断长期能力。','point_ids':d['point_ids']} for i,d in enumerate(dims)]
    gap_reason={'calculation':'仍缺分钟换秒的明确依据及单位与数量级检查。',
        'concept':'仍缺转账最终状态、整体生效解释及资料未给隔离级别的边界说明。',
        'program':'仍缺逐次count状态及return位于循环后的说明。'}
    return {'result_type':'feedback','message':ex['stem']+'：保留正确部分，针对理由复测。' if wrong else ex['stem']+'：本次观察符合有限依据。',
        'correct_parts':[item],'errors':[dict(item,explanation=error_reason[kind],point_ids=['p2'] if kind=='program' else ['p3'] if kind=='concept' else ['p1','p2'])] if wrong else [],'evidence_gaps':[dict(item,explanation=gap_reason[kind])] if wrong else [],
        'cause_hypotheses':[{'hypothesis':'可能混用了单位或误读了条件','evidence_for':answer[:200],
            'missing_evidence':'仍缺另一独立实例观察','confidence':'tentative'}] if wrong else [],
        'dimension_observations':observations,'next_focus':{'focus_dimension':dims[1]['id'],'reason':'新实例需独立完成，当前一次观察不能代表长期掌握。','suggested_mode':'retest'}}

# Selection is deliberately limited to these synthetic source statements.
# The independent content oracle records actual claims and raw source separately.
_SUPPORT = {
    'n1.p1': ('平均速度', '路程', '时间'),
    'n1.p2': ('分钟', '秒', '60'),
    'n1.p3': ('60m/s', '60', '倍'),
    'n1.p4': ('单位', '数量级'),
    'n2.p1': ('A100/B50', '失败'),
    'n2.p2': ('原子性', '全部成功', '不生效'),
    'n2.p3': ('原子性', '不能单独保证隔离'),
    'n2.p4': ('未给', '隔离级别'),
    'n3.p1': ('[-2,0,3,5]', '返回 2'),
    'n3.p2': ('value>0', '0 不满足'),
    'n3.p3': ('count', '0/0/1/2'),
    'n3.p4': ('return', '循环后'),
}

def supported_catalog(document):
    task=document['task']
    nodes=['n1','n2','n3'] if task['kind']=='plan' else [task['node_id']] if task['kind']=='exercise' else [
        {'calculation':'n1','concept':'n2','program':'n3'}[task['exercise']['exercise_type']]]
    matched={};missing=[]
    for node in nodes:
        for i in range(1,5):
            key=f'{node}.p{i}'
            matches=sorted({e['id'] for e in document['evidence'] if all(word in e['text'] for word in _SUPPORT[key])})
            if not matches: missing.append(key)
            else: matched[key]=matches[:1]
        if not any(k.startswith(node+'.') for k in missing):
            matched[node]=sorted({id for i in range(1,5) for id in matched[f'{node}.p{i}']})[:4]
    return matched,missing

def output_for(document):
    citations,missing=supported_catalog(document); task=document['task']
    if missing:
        return {'result_type':'no_evidence','message':'当前实际目录不足以支持这些参考或论点；不猜测引用。','missing':missing[:4]}
    if task['kind']=='plan': return path(citations)
    if task['kind']=='exercise': return exercise(task,citations)
    return feedback(task,citations)
