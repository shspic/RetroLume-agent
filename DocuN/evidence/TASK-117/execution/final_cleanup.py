"""硬预算停止后的精确清场；不启动产品、测试或新资源。"""
from control import HERE,ROOT,state,write,event,failure,end_root,sample
from runtime_control import stop_pg,metadata
import json,time,subprocess

value=state()
event('hard_budget_stop_observed',elapsed_seconds=(time.monotonic_ns()-value['start_mono_ns'])/1e9,reason='恢复入口已超过28800秒；停止新实现/验证，仅精确清场与保存',approval_review_rejected_action='browser continuation launch was not executed due approval reviewer usage limit')
proof=[]
for row in value['resources']:
    if row.get('kind')=='pg' and row.get('cid'):
        actual=metadata(row['cid'])
        if row['slot']=='source' and actual['running']:actual=stop_pg('source')
        elif actual['running']:raise RuntimeError('unexpected_own_running_resource_requires_exact_cleanup')
        if actual['running'] or actual['pid']:raise RuntimeError('cleanup_unconfirmed')
        proof.append(actual)
write(HERE/'final-resource-stop.json',{'sample':sample(),'pg':proof,'containers_and_volumes_retained':True,'api_stop_event':'2026-10-14T12:24:08.537905+00:00 PID24396 exact launch handle wait','browser_1_2_finished':True,'browser_3_not_executed':True,'no_preview_created':True})
value=state()
if value['active_root'] is not None:end_root(result='Hard activity budget exceeded during interruption; exact own resources stopped; HTTP chains passed but S candidate incomplete, no additional business run',resources_confirmed_stopped=True)
value=state();elapsed=(time.monotonic_ns()-value['start_mono_ns'])/1e9
holding=sum(x['seconds'] for x in value['runtime_intervals']);offline=sum(x['seconds'] for x in value['offline_intervals'])
failure('HARD-BUDGET-INTERRUPTION',f'活动实测{elapsed:.3f}/28800秒；运行根含PG持有保守计{holding:.3f}/14400秒；离线{offline:.3f}/7200秒。审批服务用量阻断后，PG未随API控制器截止一并停止，恢复后才精确停机。',effect='超额如实保留，不清零、不删除资源、不追加业务许可；原card余量0，后续必须主控有效续作合同')
write(HERE/'final-budget-observed.json',{'sample':sample(),'activity_elapsed_seconds':elapsed,'activity_cap_seconds':28800,'activity_remaining_seconds':0,'runtime_holding_conservative_seconds':holding,'runtime_cap_seconds':14400,'offline_seconds':offline,'offline_cap_seconds':7200,'counts':state()['counts'],'all_original_failures_and_counts_retained':True,'continued_business_after_observed_stop':False,'incomplete':True})
event('cleanup_complete',pg_count=len(proof),all_stopped=True,volumes_retained=True)
print('Two exact own PGs stopped/Pid0; all data retained; hard-budget overrun preserved')
