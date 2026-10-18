"""R01/R02隔离目标使用真实readonly角色，封印后写入必须拒绝。"""
def verify_readonly_target(connection,profile):
    from app.data_exit.schema_checks import assert_data_schema_sync
    state=connection.execute('SELECT * FROM public.data_export_control_v1').fetchone()
    assert state['schema_profile']==profile and state['mode_observed']=='restored_readonly'
    assert_data_schema_sync(connection)
    default=connection.execute('SHOW default_transaction_read_only').fetchone()['default_transaction_read_only']
    assert not connection.execute('SELECT rolsuper FROM pg_roles WHERE rolname=current_user').fetchone()['rolsuper']
    assert not any(r['rolcanlogin'] for r in connection.execute("SELECT rolcanlogin FROM pg_roles WHERE rolname IN('step018_admin','step018_loader')").fetchall())
    return {'profile':profile,'mode':state['mode_observed'],'exact_schema':True,'transaction_readonly_default_observed':default,'nonsuper':True,'temporary_logins_revoked':True,'write_proof':'由原factory探针及调用方实际UPDATE拒绝核对；不把session默认flag误当seal合同'}
