"""仅因面试索引先后门产品修正而构建第6次；全部自有运行资源已停。"""
from batch_runtime import *

def main():
    c.guard()
    if c.state()['active_root'] is not None:raise RuntimeError('build_requires_no_running_root')
    resources=[rc.metadata(r['cid']) for r in c.state()['resources'] if r.get('kind')=='pg' and r.get('cid')]
    assert all(not r['running'] and r['pid']==0 for r in resources)
    from profiles_batch import listeners
    assert not listeners()
    for p in (ROOT/'frontend/dist').rglob('*'):
        if p.is_file():c.pre(p.relative_to(ROOT).as_posix())
    c.count('frontend_builds');start=c.sample()
    result=subprocess.run(['cmd','/d','/c','npm.cmd','run','build'],cwd=ROOT/'frontend',capture_output=True,timeout=180)
    (C01/'build-6.log').write_bytes(result.stdout+result.stderr)
    end=c.sample();value=c.state();value['offline_intervals'].append({'root':None,'segment':value['active_segment'],'start_mono_ns':start['mono_ns'],'end_mono_ns':end['mono_ns'],'seconds':(end['mono_ns']-start['mono_ns'])/1e9,'basis':'面试持久目标未加载时拒模型动作并使用持久目标的产品修正，必要最后正式build/typecheck，全部运行资源已停止'})
    c.write(EXEC/'budget.json',value)
    if result.returncode:raise RuntimeError('final_build_failed_no_attempts_remaining')
    c.write(C01/'bundle-6.json',{'attempt':6,'sample':end,'reason':'interview v2 uses verified persisted goal; model actions disabled before goal detail is ready','files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())} for p in sorted((ROOT/'frontend/dist').rglob('*')) if p.is_file()],'actual_browser_binding':'NOT_RUN; bundle5 historical browser evidence retained; host browser cap8 exhausted'})
    print('Formal build6/typecheck passed; final bundle not claimed browser verified')

if __name__=='__main__':main()
