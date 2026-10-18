"""同一卡原 source 的精确三函数前向围栏修正，不重跑完整迁移或重建资源。"""
import json
import re
import runpy
import sys
import time
from budget import ROOT,CONTROL,Budget
sys.path.insert(0,str(ROOT/'backend'))
from setup_source import reference,start_source,stop_source
from freeze import freeze
from app.data_exit.contracts import digest,canonical


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--matrix',action='store_true');args=parser.parse_args()
    budget=Budget();target,credentials=reference()
    if not start_source(budget,target):print(json.dumps({'state':'not_run','reason':'memory_start_guard'}));return 78
    label='source-forward-'+str(time.monotonic_ns());output=ROOT/'DocuN/evidence/TASK-114/implementation/batches'/label
    output.mkdir(parents=True)
    try:
        freeze(label)
        import psycopg
        from psycopg.rows import dict_row
        from app.data_exit.schema import DATA_FUNCTIONS
        old=runpy.run_path(str(ROOT/'DocuN/evidence/TASK-114/implementation/as-run/pg-source-init-02/backend/app/data_exit/schema.py'))['DATA_FUNCTIONS']
        migration=(ROOT/'backend/migrations/013_data_exit.sql').read_text(encoding='utf-8')
        statements={match[1]:match[0] for match in re.finditer(r'CREATE FUNCTION public\.(\w+)\(.*? AS \$(\w+)\$.*?\$\2\$;',migration,re.S)}
        names=['data_runtime_write_guard','data_control_frozen','data_mutation_enter','data_material_reference_guard']
        from seed_legacy import business_rows
        before=business_rows(credentials['admin_dsn'])
        with psycopg.connect(credentials['admin_dsn'],connect_timeout=3,row_factory=dict_row) as connection:
            actual=connection.execute("SELECT p.proname,p.prosrc,p.prosecdef,p.provolatile,p.proconfig,r.rolname AS owner FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner WHERE n.nspname='public' AND p.proname=ANY(%s)",(names,)).fetchall()
            hashes={row['proname']:digest(re.sub(r'\s+','',row['prosrc'])) for row in actual}
            for row in actual:
                if row['owner']!='retrolume_data_owner' or not row['prosecdef'] or row['proconfig']!=['search_path=pg_catalog, pg_temp']:raise RuntimeError('原函数授权身份漂移')
            for name in names:
                if hashes.get(name)==DATA_FUNCTIONS[name]['sha256']:continue
                if name!='data_mutation_enter' and hashes.get(name)!=old[name]['sha256']:raise RuntimeError('原函数正文与已执行十三版不符')
                if name=='data_mutation_enter' and name in hashes:raise RuntimeError('未知同名新函数')
                connection.execute(statements[name].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1))
            connection.execute('ALTER FUNCTION public.data_mutation_enter() OWNER TO retrolume_data_owner')
            connection.execute('REVOKE ALL ON FUNCTION public.data_mutation_enter() FROM PUBLIC')
            connection.execute('GRANT EXECUTE ON FUNCTION public.data_mutation_enter() TO retrolume_data_app')
        after=business_rows(credentials['admin_dsn'])
        if before!=after:raise RuntimeError('前向修正改写业务值')
        from app.data_exit.repository import DataRepository
        state=DataRepository(credentials['app_dsn']).state()
        from app.data_exit.control import ControlHub
        hub=ControlHub(ROOT/'DocuN/evidence/TASK-114/synthetic/control-root')
        known=hub.state()['source']
        if known is None:hub.commit('source.register',state)
        elif (known['dataset_id'],known['instance_id'],known['originals_root_id'])!=(state['dataset_id'],state['instance_id'],state['originals_root_id']):raise RuntimeError('源身份漂移')
        report={'state':'passed','before_functions':hashes,'final_functions':{name:DATA_FUNCTIONS[name]['sha256'] for name in names},
                'business_values_equal':True,'source_state':state,'patched_functions':names,'new_schema_probe':'passed'}
        (output/'forward-result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        (output/'result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        if args.matrix:
            from matrix_pg import environment,scenario
            from budget import FactoryHooks
            from app.main import create_app
            from app.runtime import psycopg_compatible_loop_factory
            import asyncio
            environment(credentials);app=create_app();runtime=app.state.data_exit
            if runtime is None:raise RuntimeError('修正后的入口未就绪')
            runtime.factory.hooks=FactoryHooks(budget)
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
                runner.run(scenario(runtime,credentials,budget,output,True))
        print(json.dumps({'state':'passed','batch':label}));return 0
    except BaseException as error:
        failure={'state':'failed','error_type':type(error).__name__,'code':getattr(error,'code',None),'sqlstate':getattr(error,'sqlstate',None)}
        (output/'result.json').write_text(json.dumps(failure,indent=2),encoding='utf-8');budget.event('source_forward_failed',failure)
        import traceback
        message=traceback.format_exc();causes=[];cause=error
        for _ in range(8):
            if cause is None:break
            causes.append({'type':type(cause).__name__,'sqlstate':getattr(cause,'sqlstate',None),'message_primary':getattr(getattr(cause,'diag',None),'message_primary',None)})
            cause=cause.__context__
        for value in credentials.values():
            if isinstance(value,str) and value:message=message.replace(value,'[已隐藏私密值]')
        (output/'failure.txt').write_text(message,encoding='utf-8')
        (output/'causes.json').write_text(json.dumps(causes,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(failure));return 1
    finally:stop_source(budget,target)


if __name__=='__main__':raise SystemExit(main())
