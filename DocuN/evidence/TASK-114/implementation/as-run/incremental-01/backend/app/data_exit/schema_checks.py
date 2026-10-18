"""只用项目冻结身份核新控制函数，不信包内 expected hash。"""
import re
from .contracts import DataError,digest


async def assert_data_schema(connection):
    from .schema import DATA_FUNCTIONS
    cursor=await connection.execute("""SELECT p.proname,p.prosrc,p.prosecdef,p.provolatile,p.proconfig,r.rolname AS owner,
       EXISTS(SELECT 1 FROM aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner))) a WHERE a.grantee=0 AND a.privilege_type='EXECUTE') AS public_execute
       FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner
       WHERE n.nspname='public' AND p.proname=ANY(%s)""",(list(DATA_FUNCTIONS),))
    rows=await cursor.fetchall()
    if len(rows)!=len(DATA_FUNCTIONS):raise DataError('data_schema_not_ready',503)
    for row in rows:
        expected=DATA_FUNCTIONS[row['proname']]
        if (digest(re.sub(r'\s+','',row['prosrc']))!=expected['sha256'] or row['prosecdef']!=expected['security_definer']
            or row['provolatile']!=expected['volatility'] or row['proconfig']!=['search_path=pg_catalog, pg_temp']
            or row['owner']!='retrolume_data_owner' or row['public_execute']):
            raise DataError('data_schema_not_ready',503)
    cursor=await connection.execute("""SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls
      FROM pg_roles WHERE rolname=ANY(%s)""",(['retrolume_data_owner','retrolume_data_app','retrolume_data_snapshot','retrolume_data_restore_loader'],))
    roles=await cursor.fetchall()
    if len(roles)!=4 or any(any(v for k,v in r.items() if k!='rolname') for r in roles):raise DataError('data_schema_not_ready',503)
    cursor=await connection.execute("SELECT count(*) AS n FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND t.tgname='data_runtime_write' AND t.tgenabled='O' AND NOT t.tgisinternal")
    if (await cursor.fetchone())['n']!=28:raise DataError('data_schema_not_ready',503)


async def schema_mode(connection):
    await assert_data_schema(connection)
    cursor=await connection.execute('SELECT mode_observed FROM public.data_export_control_v1')
    row=await cursor.fetchone()
    if row is None or row['mode_observed'] not in ('normal','loading','frozen','restored_readonly'):raise DataError('mode_unknown',503)
    return row['mode_observed']


def legacy_business_shape(shape):
    """核十三版精确新增后投影回十二版指纹，任意额外授权仍会失败。"""
    import copy
    from .schema import BUSINESS_FUNCTIONS_013,LEGACY_FUNCTION_SOURCES
    result=copy.deepcopy(shape)
    allowed={'retrolume_data_snapshot':{'r'},'retrolume_data_restore_loader':{'ar','ra'},'retrolume_data_owner':{'r'}}
    def acl(text):
        if text is None:return None
        if not text.startswith('{') or not text.endswith('}'):raise DataError('data_schema_not_ready',503)
        keep=[]
        for entry in text[1:-1].split(','):
            match=re.fullmatch(r'([^=]+)=([^/]*)/(.+)',entry)
            if not match:raise DataError('data_schema_not_ready',503)
            role,privileges,_=match.groups()
            if role in allowed:
                if privileges not in allowed[role]:raise DataError('data_schema_not_ready',503)
            else:keep.append(entry)
        return '{'+','.join(keep)+'}' if keep else None
    for section in ('columns','table_acl','qualification_column_acls'):
        for row in result.get(section,[]):
            for name in ('acl','column_acl','table_acl'):
                if name in row:row[name]=acl(row[name])
    for row in result.get('functions',[]):
        name=row['proname']
        if name in BUSINESS_FUNCTIONS_013:
            if digest(re.sub(r'\s+','',row['prosrc']))!=BUSINESS_FUNCTIONS_013[name]:raise DataError('data_schema_not_ready',503)
            row['prosrc']=LEGACY_FUNCTION_SOURCES[name]
    filtered=[]
    for row in result.get('triggers',[]):
        if row['tgname'] in ('data_runtime_write','data_restore_budget_shape','data_restore_session_shape'):
            function='data_runtime_write_guard' if row['tgname']=='data_runtime_write' else 'data_restore_final_shape'
            if row['tgenabled']!='O' or function+'()' not in row['definition']:raise DataError('data_schema_not_ready',503)
        else:filtered.append(row)
    result['triggers']=filtered
    return result
