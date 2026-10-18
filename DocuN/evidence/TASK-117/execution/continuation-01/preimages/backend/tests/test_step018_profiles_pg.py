"""R01/R02隔离目标使用真实readonly角色，封印后写入必须拒绝。"""
def verify_readonly_target(connection,profile):
    from app.data_exit.schema_checks import assert_data_schema_sync
    state=connection.execute('SELECT public.data_state() AS value').fetchone()['value']
    assert state['schema_profile']==profile and state['mode']=='restored_readonly'
    assert_data_schema_sync(connection)
    assert connection.execute('SHOW default_transaction_read_only').fetchone()['default_transaction_read_only']=='on'
    assert not connection.execute('SELECT rolsuper FROM pg_roles WHERE rolname=current_user').fetchone()['rolsuper']
    assert not any(r['rolcanlogin'] for r in connection.execute("SELECT rolcanlogin FROM pg_roles WHERE rolname IN('step018_admin','step018_loader')").fetchall())
    return {'profile':profile,'mode':state['mode'],'exact_schema':True,'readonly_default':True,'nonsuper':True,'temporary_logins_revoked':True}
