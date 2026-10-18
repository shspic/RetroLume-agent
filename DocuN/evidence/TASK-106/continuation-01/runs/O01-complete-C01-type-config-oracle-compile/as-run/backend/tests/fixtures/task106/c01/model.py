"""Lowest raw-response fixture; selects existing actual catalog evidence only."""
import json
from .samples import SERIAL,TRACE,YEAR_A,YEAR_B

def choose(catalog,needle):
    found=[x for x in catalog if needle in x['text']]
    if not found:raise ValueError('C01 declared support sentence absent from actual catalog: '+needle)
    return found[0]['citation_id']

def response_value(frozen,scenario='normal'):
    catalog=frozen['catalog'];goal=frozen['goal_body']['target'];texts='\n'.join(x['text'] for x in catalog)
    history=YEAR_A in texts and YEAR_B in texts;technical=SERIAL in texts and TRACE in texts
    if any(x in goal for x in ('史料','策展','活动X')):history=True
    if '余额算法' in goal:technical=True
    if history:ids=[choose(catalog,YEAR_A),choose(catalog,YEAR_B)]
    elif technical:ids=[choose(catalog,SERIAL),choose(catalog,TRACE)]
    else:ids=[x['citation_id'] for x in catalog[:2]]
    if frozen['action']=='ask':
        if goal.strip().casefold()=='spring':return dict(type='question',purpose='clarification',reason='ambiguous_target',text='Spring在资料中可能为软件框架或季节，请明确领域与具体概念。',reference_ids=ids)
        text='请并列2012和2013两份史料及不确定、补充依据。' if history else '请解释给定算法的串行110及先读100后写120、90的覆盖风险。' if technical else '请说明当前资料中的具体概念，收益主张需要独立依据。'
        return dict(type='question',purpose='interview',reason='topic',text=text,reference_ids=ids)
    answers=[x for x in frozen['parent_record_refs'] if x['kind']=='answer'];answer=answers[-1];text=answer['body']['value']['text'];rid=answer['record_id']
    recog=dict(answer_record_id=rid,start_offset=0,end_offset=len(text),answer_excerpt=text,reference_ids=ids,semantic_support='supports',explanation='对照已定位的两条原句，保留语义建议身份。')
    if '60%' in text or scenario=='force_probe':
        return dict(type='probe',reason='missing_claim_evidence',text='请提供60%主张的基线、口径、样本、环境、时间窗口和测量记录。',recognitions=[recog],gaps=[dict(answer_record_id=rid,text='自报收益尚缺测量依据。',reference_ids=[])],reference_ids=ids)
    return dict(type='feedback',summary='对照明确虚构的源与用户原文；现实表现仍未知。',recognitions=[recog],gaps=[],
        conflicts=[dict(text='史料A的2012与史料B的2013冲突，年份保持未知，需补档案或同期记录。',reference_ids=ids)] if history else [],next_steps=['是否继续下一题由你显式选择。'])
