"""本卡唯一进程内有界控制器。截止线程直接执行回调，不依赖第二次工具调用。"""
from __future__ import annotations
import threading,time

class BoundedResources:
    def __init__(self,*,deadline,clock=time.monotonic,on_close=lambda report:None):
        self.deadline,self.clock,self.on_close=deadline,clock,on_close
        self._condition=threading.Condition(threading.RLock());self._entries=[]
        self.closing=False;self.closed=threading.Event();self.report=None;self._thread=None
        self.cleanup_deadline=deadline+120
        self._memory_probe=None;self._memory_every=2;self._memory_next=0;self._memory_lows=0
        self.memory={'samples':0,'minimum_bytes':None,'maximum_bytes':None,'pressure_events':[]}

    def monitor_memory(self,probe,*,every=2,minimum=256*1024**2):
        self._memory_probe=probe;self._memory_every=every;self._memory_minimum=minimum

    def _memory_tick(self):
        if self._memory_probe is None or self.clock()<self._memory_next:return None
        self._memory_next=self.clock()+self._memory_every
        try:
            available=self._memory_probe()
            if not isinstance(available,int) or available<0:raise ValueError('invalid physical memory sample')
        except BaseException as exc:
            self.memory['pressure_events'].append({'at':self.clock(),'error_type':type(exc).__name__})
            return 'memory_sample_failed'
        self.memory['samples']+=1;self.memory['last']={'at':self.clock(),'available_bytes':available}
        for key,op in [('minimum_bytes',min),('maximum_bytes',max)]:
            self.memory[key]=available if self.memory[key] is None else op(self.memory[key],available)
        self._memory_lows=self._memory_lows+1 if available<self._memory_minimum else 0
        if self._memory_lows and len(self.memory['pressure_events'])<8:self.memory['pressure_events'].append({**self.memory['last'],'consecutive':self._memory_lows})
        return 'memory_pressure' if self._memory_lows>=2 else None

    def remaining_cleanup(self,maximum):
        return max(.1,min(maximum,self.cleanup_deadline-self.clock()))

    def __enter__(self):
        self._thread=threading.Thread(target=self._watch,name='task120-bounded-cleanup',daemon=False)
        self._thread.start();return self

    def check(self):
        if self.closing or self.clock()>=self.deadline:raise RuntimeError('本根已拒新启动或mutation')

    def register(self,name,cleanup,*,priority=0):
        # 必须在真正启动前登记；启动只完成一半时回调仍能按已知身份收尾。
        with self._condition:
            self.check();self._entries.append((priority,len(self._entries),name,cleanup))

    def wake(self):
        with self._condition:self._condition.notify_all()

    def _watch(self):
        pressure=None
        with self._condition:
            while not self.closing:
                remaining=self.deadline-self.clock()
                if remaining<=0:break
                pressure=self._memory_tick()
                if pressure:break
                self._condition.wait(min(remaining,1,self._memory_every))
            timed_out=not self.closing
        if timed_out:self.close(pressure or 'business_deadline')

    def close(self,reason='normal_exit'):
        with self._condition:
            if self.closing:
                waiter=True
            else:
                self.closing=True;waiter=False;self._condition.notify_all()
        if waiter:
            if threading.current_thread() is not self._thread:self.closed.wait(120)
            return self.report
        report={'reason':reason,'resources':[],'all_confirmed':True,'physical_memory':self.memory}
        try:
            for _,_,name,callback in sorted(self._entries,reverse=True):
                try:
                    value=callback()
                    if value is False:raise RuntimeError('停止组合证据未确认')
                    report['resources'].append({'name':name,'confirmed':True,'proof':value})
                except BaseException as exc:
                    report['all_confirmed']=False;report['resources'].append({'name':name,'confirmed':False,'error_type':type(exc).__name__,'error':str(exc)[:200]})
            self.report=report;self.on_close(report)
        finally:self.closed.set()
        return report

    def __exit__(self,kind,value,tb):
        self.close('exception' if kind else 'normal_exit')
        if self._thread and self._thread is not threading.current_thread():self._thread.join(timeout=5)
        return False
