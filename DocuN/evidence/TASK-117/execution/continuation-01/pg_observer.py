"""本卡app角色真实PG只读阻塞观测，有限150样本，不改变原时限或事务。"""
from batch_runtime import *
import threading

def observe_pg(run,label):
    stopped=threading.Event();rows=[]
    def watch():
        import psycopg
        from psycopg.rows import dict_row
        for _ in range(150):
            if stopped.wait(2):break
            try:
                with psycopg.connect(rc.dsn('source'),connect_timeout=2,row_factory=dict_row,autocommit=True) as db:
                    db.execute("SET statement_timeout='1s'")
                    current=db.execute("SELECT pid,state,wait_event_type,wait_event,pg_blocking_pids(pid) AS blockers,left(query,140) AS SQL_prefix FROM pg_stat_activity WHERE datname=current_database() AND usename=current_user AND pid<>pg_backend_pid() ORDER BY pid").fetchall()
                rows.append({'sample':c.sample(),'own_app_rows':current})
            except Exception as exc:rows.append({'sample':c.sample(),'error_type':type(exc).__name__})
            c.write(C01/(label+'-PG-observation.json'),rows)
    thread=threading.Thread(target=watch,name='task117-readonly-PG-observation',daemon=False)
    def close():
        stopped.set();thread.join(timeout=5)
        if thread.is_alive():raise RuntimeError('own_PG_observer_unconfirmed')
        return {'samples':len(rows),'thread_joined':True}
    run.register('finite-own-PG-observation',close,priority=70);thread.start()
    return close
