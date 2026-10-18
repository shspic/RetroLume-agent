"""原日志和617行包的有限离线区别计时；无PG连接、无目标创建。"""
from pathlib import Path
import sys,json,time,shutil,importlib.util
from uuid import uuid4
N=Path(__file__).resolve().parent;E=N.parent;R=E.parents[3]
sys.path[:0]=[str(E),str(R/'backend')]
import control as c
from app.data_exit.control import ControlHub
from app.data_exit.contracts import DataContext,DataJobCommand,Limits
from app.data_exit.operations import Operation
from app.data_exit.packages import PackageReader
from app.data_exit.restore import RestoreController
from app.data_exit.spool import PackageRows


def main():
    c.reserve_offline(150)
    old_path=N/'preimages/backend/app/data_exit/control.py'
    spec=importlib.util.spec_from_file_location('app.data_exit.s04_before_control',old_path)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    source=E/'synthetic/source-control/journal.bin'
    package=E/'synthetic/source-backup/packages/7a10f64c-26bc-4c89-a409-4417ddc1a6dc.rldata'
    before_source=c.sha(source.read_bytes());package_sha=c.sha(package.read_bytes())
    results={'sample':c.sample(),'package_file_sha256':package_sha,'source_journal_sha256':before_source,'source_journal_bytes':source.stat().st_size,'SQL':'NOT_RUN; PG/trigger/connection cost is not measured here','authority_protocol':'真实副本上合法prepared→running；不恢复failed loader'}
    begin=time.perf_counter()
    with PackageReader(package) as reader:
        results['package_validate_seconds']=time.perf_counter()-begin
        tables=reader.schema_profile.tables
        rows={table:PackageRows(reader,table,lambda:None) for table in tables}
        begin=time.perf_counter();components=[]
        for comp in RestoreController._components(rows):
            counts={table:len(values) for table,values in comp.items()}
            components.append({'rows':sum(counts.values()),'tables':{t:v for t,v in counts.items() if v}})
        results['graph_and_repeated_package_scan_seconds']=time.perf_counter()-begin
        results['components']=components;assert sum(x['rows'] for x in components)==617
    for label,cls in [('before',old.ControlHub),('after',ControlHub)]:
        root=N/('diagnostic-'+label+'-'+str(time.time_ns()));root.mkdir(exist_ok=False);shutil.copyfile(source,root/'journal.bin')
        hub=cls(root);context=DataContext(hub.control_id,0,str(uuid4()),str(uuid4()),'normal')
        receipt=hub.create_or_get_job(DataJobCommand('restore',str(uuid4()),{'plan_id':str(uuid4()),'plan_sha256':'0'*64}),context)
        op=Operation(hub,receipt['job_id'],1800,'offline_profile')
        check_seconds=0;calls=0;stopped=False
        def check():
            nonlocal check_seconds,calls
            start=time.perf_counter()
            if label=='before':
                job=hub.state()['jobs'][op.job_id];op._validate(job)
                assert job['revision']==op.revision
            else:op.check()
            check_seconds+=time.perf_counter()-start;calls+=1
            if check_seconds>32:raise TimeoutError('offline_profile_stop_32_seconds_no_SQL')
        measured=[]
        try:
            with PackageReader(package) as reader:
                rowset={table:PackageRows(reader,table,check) for table in reader.schema_profile.tables}
                for index,component in enumerate(RestoreController._components(rowset)):
                    start=time.perf_counter();start_calls=calls;start_check=check_seconds
                    try:
                        for table in reader.schema_profile.tables:
                            for row in component.get(table,[]):check()
                    finally:
                        measured.append({'component_index':index,'seconds':time.perf_counter()-start,'check_calls':calls-start_calls,'check_seconds':check_seconds-start_check,'SQL_count':0})
        except TimeoutError:stopped=True
        finally:hub.lock.close();hub.operation_lock.close()
        results[label]={'total_check_calls':calls,'total_check_seconds':check_seconds,'components':measured,'bounded_diagnostic_stop':stopped}
    assert c.sha(source.read_bytes())==before_source
    results['scope']='相同原包/日志；逐表和每行相同取消校验点；未计SQL、trigger、实际目标性能，只证明重复日志工作能单独耗尽组件门'
    c.write(N/'restore-cost-diagnosis.json',results)
    print(json.dumps({k:results[k] for k in ('package_validate_seconds','graph_and_repeated_package_scan_seconds','before','after')},ensure_ascii=False))


if __name__=='__main__':main()
