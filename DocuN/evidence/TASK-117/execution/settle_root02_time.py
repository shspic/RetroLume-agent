"""区分运行根目标跨度与真实资源持有并集，普通无资源等待仍计总活动窗。"""
import json
from control import HERE,state,write,event,sample
value=state()
if value.get('root02_time_classification_settled'):raise RuntimeError('已核销，不能重复')
if value['active_root'] is not None:raise RuntimeError('根未结束')
root=next(r for r in value['roots'] if r['id']==2)
original=[r for r in value['runtime_intervals'] if r['root']==2]
if len(original)!=1:raise RuntimeError('原单根时段不符')
intervals=[]
for resource in value['resources']:
    if resource.get('running'):raise RuntimeError('自有资源仍在运行')
    for period in resource.get('holding_intervals',[]):intervals.append((period['start']['mono_ns'],period['end']['mono_ns']))
merged=[]
for start,end in sorted(intervals):
    if merged and start<=merged[-1][1]:merged[-1][1]=max(end,merged[-1][1])
    else:merged.append([start,end])
actual=[{'root':2,'start_mono_ns':a,'end_mono_ns':b,'seconds':(b-a)/1e9,'basis':'所有本卡PG实际start attempt至精确stop/Pid0的并集；本根Native窗口全部包含其中'} for a,b in merged]
preflight=json.loads((HERE/'root-02-preflight.json').read_text(encoding='utf-8'))
offline={'root':2,'start_mono_ns':root['start']['mono_ns'],'end_mono_ns':preflight['end']['mono_ns'],
 'seconds':(preflight['end']['mono_ns']-root['start']['mono_ns'])/1e9,'basis':'入口语法/解释器修正至类型核对通过的保守整段；不将随后无人运行的内存等待作产品持有'}
adjustment={'recorded':sample(),'root':2,'original_goal_span':original[0],'actual_holding_union':actual,'offline_preflight_conservative':offline,
 'reason':'begin_root类别runtime曾把完整目标跨度暂作运行额；其中等待内存时无CID/PG/API/browser/preview，只有活动窗继续消耗。保留原跨度按精确资源生灭核真实持有，非延长或重置许可。'}
value.setdefault('time_classification_adjustments',[]).append(adjustment)
value['runtime_intervals']=[r for r in value['runtime_intervals'] if r['root']!=2]+actual
value['offline_intervals'].append(offline);value['root02_time_classification_settled']=True
write(HERE/'budget.json',value);write(HERE/'root02-time-classification.json',adjustment);event('time_classification_settled',**adjustment)
print(json.dumps({'total_activity_seconds':(sample()['mono_ns']-value['start_mono_ns'])/1e9,
 'runtime_holding_seconds':sum(x['seconds'] for x in value['runtime_intervals']),
 'offline_seconds':sum(x['seconds'] for x in value['offline_intervals']),'counts':value['counts']},ensure_ascii=False))
