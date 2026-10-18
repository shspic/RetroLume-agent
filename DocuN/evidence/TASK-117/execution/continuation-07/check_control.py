"""有限纯时钟反例与准确关闭闭包自检；不修改系统时间或旧许可。"""
import copy
from datetime import datetime,timedelta
import subprocess
from unittest.mock import patch
import control as c

b=c.state();now=c.sample();checked=[]
# 外层受控命令正是本自检进程；纯替身基准须显式剥离这一在途事实。
c.segment(b)['offline_process_run_active']=None
def refusal(name,change,clock=None):
    candidate=copy.deepcopy(b);change(candidate)
    try:c.limits(candidate,clock or now)
    except RuntimeError:checked.append(name)
    else:raise AssertionError(name+'没有拒绝')
def seg(x):return c.segment(x)
assert c.limits(b,now)>0;checked.append('S08正常剩余')
refusal('许可身份',lambda x:x.update(active_segment='旧S07'))
refusal('日历仅收口',lambda x:seg(x).update(calendar_deadline_utc=(datetime.fromisoformat(now['utc'])+timedelta(seconds=1199)).isoformat()))
refusal('单调倒退',lambda x:seg(x)['last_clock'].update(mono_ns=now['mono_ns']+1))
refusal('跨宿主域',lambda x:seg(x)['last_clock'].update(boot_epoch_seconds=now['boot_epoch_seconds']-10))
refusal('UTC倒退',lambda x:seg(x)['last_clock'].update(utc=(datetime.fromisoformat(now['utc'])+timedelta(seconds=10)).isoformat()))
refusal('上个命令未结束',lambda x:seg(x).update(offline_process_run_active={'start_mono_ns':now['mono_ns']}))
refusal('实际命令总额',lambda x:seg(x).update(offline_process_run_seconds=3600))
refusal('持有总额',lambda x:x['runtime_intervals'].append({'segment':c.PERMIT,'seconds':3600}))
for counter in ('browser_starts','frontend_builds','fixture_server_starts','http','pg_starts','api_starts','provider_calls','actual_fee_microunits'):
    candidate=copy.deepcopy(b);candidate['counts'][counter]=c.segment(candidate)['cumulative_caps'][counter]
    try:c.check_count(candidate,counter)
    except RuntimeError:checked.append('次数门 '+counter)
    else:raise AssertionError(counter)
candidate=copy.deepcopy(b);candidate['active_root']=25;candidate['roots'].append({'id':25,'segment':c.PERMIT,'business_deadline_mono_ns':now['mono_ns']-1})
try:c.limits(candidate,now)
except RuntimeError:checked.append('原根截止不延长')
else:raise AssertionError('根已到期仍放行')
closed=[];failures=[]
class Child:
    _handle=1;pid=123;returncode=0;calls=0
    def communicate(self,timeout):
        self.calls+=1
        if self.calls==1:raise subprocess.TimeoutExpired(['纯替身'],timeout)
        return b'expected finite closure',None
    def poll(self):return 0
class FakeJob:
    def spawn(self,*args,**kwargs):return Child()
    def close(self):closed.append(True)
with patch.object(c,'guard',return_value=copy.deepcopy(b)),patch.object(c,'state',side_effect=lambda:copy.deepcopy(b)),patch.object(c,'limits',return_value=.1),patch.object(c,'write'),patch.object(c,'event'),patch.object(c,'birth',return_value=1),patch.object(c,'failure',side_effect=lambda *args:failures.append(args)),patch.object(c,'Job',FakeJob):
    try:c.run(['纯替身'],'expected-close-proof',timeout=.1)
    except subprocess.TimeoutExpired:pass
    else:raise AssertionError('模拟超时未返回')
assert closed and len(failures)==1;checked.append('超时准确关闭闭包')
c.write(c.N/'control-selfcheck.json',{'sample':c.sample(),'cases':checked,'passed':len(checked),'system_clock_changed':False,'scope':'本卡控制层纯替身，不是产品安全结论'})
print('有限控制自检通过',len(checked))
