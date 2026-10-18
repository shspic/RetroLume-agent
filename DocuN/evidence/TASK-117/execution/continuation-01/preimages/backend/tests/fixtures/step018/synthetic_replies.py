"""仅最低传输的有限JSON合成响应；不评价真实服务语义质量。"""
import json

def reply(payload):
    values=[]
    for item in payload['messages']:
        if item.get('role')=='user':
            try:values.append(json.loads(item['content']))
            except (ValueError,KeyError):pass
    value=next((x for x in reversed(values) if isinstance(x,dict) and 'task' in x),values[-1] if values else {})
    if 'task' in value:
        ids=[e['id'] for e in value['evidence']][:1]
        task=value['task'];action=task['kind']
        if not ids:return {'result_type':'no_evidence','message':'合成传输没有目录证据','missing':['当前资料片段']}
        if action=='plan':
            return {'result_type':'path','message':'合成路径，仅验证结构与位置','nodes':[{'title':'分钟换秒与平均速度','objective':'说明换算与速度单位','prerequisites':[],'rationale':'按当前已核资料安排练习','citations':ids,'completion_dimensions':[{'dimension':'units','required_point':'先换成秒，再计算米每秒'}]}]}
        if action=='exercise':
            purpose=task['purpose']
            return {'result_type':'exercise','message':'合成题目结构验证','exercise_type':'calculation','difficulty':1,'stem':'120米用2分钟，平均速度是多少？请说明换算与单位。','reference_points':[{'point_id':'p1','text':'2分钟为120秒，平均速度120/120=1米每秒','citations':ids,'numeric':{'value_decimal':'1','unit':'米每秒','operation':'divide','left':'120','right':'120','tolerance_decimal':'0'}}],'reference_explanation':'先把分钟换成秒，再用路程除以时间。','dimensions':[{'id':'units','point_ids':['p1'],'description':'保留换算与速度单位'}],'hint':'先将分钟转换成秒。','variant':{'purpose':purpose,'parent_exercise_record_id':task.get('parent_exercise_record_id'),'parent_feedback_record_id':task.get('parent_feedback_record_id'),'instance_data':{'kind':'calculation','quantities':[{'name':'路程','value_decimal':'120','unit':'米'},{'name':'时间','value_decimal':'2','unit':'分钟'}]}}}
        answer=task['answer_text']
        return {'result_type':'feedback','message':'合成反馈，仅验证原作答位置和保守进度','correct_parts':[{'answer_excerpt':answer[:200],'explanation':'引用本次已保存作答，不推断长期掌握','point_ids':['p1'],'citations':ids}],'errors':[],'evidence_gaps':[],'cause_hypotheses':[],'dimension_observations':[{'id':'units','observation':'partial','reason':'合成反馈不证明开放语义或长期掌握','point_ids':['p1']}],'next_focus':{'focus_dimension':'units','reason':'需要独立复测并说明单位','suggested_mode':'retest'}}
    context=value.get('context',value)
    if str(context.get('schema','')).startswith('interview.context.'):
        ids=[e['citation_id'] for e in context.get('catalog',[])][:1]
        if context['action']=='ask':return {'type':'question','purpose':'interview','reason':'topic','text':'请说明这份资料中的换算步骤，并区分资料依据与你的自报经历。','reference_ids':ids}
        if context.get('probe_depth',0)==0:return {'type':'probe','reason':'missing_claim_evidence','text':'请再说明分钟换秒的依据，并明确哪些经历尚未独立核实。','recognitions':[],'gaps':[],'reference_ids':ids}
        return {'type':'feedback','summary':'合成结构验证反馈，不能证明真实面试质量','recognitions':[],'gaps':[],'conflicts':[],'next_steps':['请明确选择下一题，继续说明依据。']}
    if context.get('schema')=='html.context.v2':
        citations=[]
        def visit(x):
            if isinstance(x,dict):
                for k,v in x.items():
                    if k in ('citation_id','id') and isinstance(v,str) and v.startswith(('lc_','ic_','hc_')):citations.append(v)
                    else:visit(v)
            elif isinstance(x,list):
                for y in x:visit(y)
        visit(context);ids=list(dict.fromkeys(citations))[:1]
        return {'schema':'interactive_description.v1','title':'平均速度换算','concept':'合成固定解释，只验证受控输入、计算与显示。','inputs':[{'id':'hctl_distance','kind':'number','label':'路程（米）','description':'本轮合成值','min':'1','max':'1000','step':'1','default':'120'}],'calculations':[{'id':'hcalc_speed','expression':{'op':'div','args':[{'op':'input','id':'hctl_distance'},{'op':'const','value':'120'}]}}],'views':[{'id':'hout_speed','kind':'readout','label':'平均速度','calculation':'hcalc_speed','unit':'米每秒'}],'actions':[{'id':'hact_reset','kind':'reset','label':'重置'}],'calculation_notes':[{'formula':'v=s/120','domain':'路程1至1000米，时间固定120秒','error':'不含测量误差','samples':[{'input':'120','expected':'1'},{'input':'240','expected':'2'}],'citations':ids}],'limitations':['合成传输不构成真实服务语义验收'],'citations':ids}
    raise ValueError('synthetic_model_profile_not_implemented')
