"""只用项目冻结身份核新控制函数，不信包内 expected hash。"""
import re
from .contracts import DataError,digest

FUNCTION_QUERY="""SELECT p.proname,p.prosrc,p.prosecdef,p.provolatile,p.proconfig,r.rolname AS owner,
 EXISTS(SELECT 1 FROM aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner))) a WHERE a.grantee=0 AND a.privilege_type='EXECUTE') AS public_execute
 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner
 WHERE n.nspname='public' AND p.proname=ANY(%s)"""
ROLE_QUERY="""SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls
 FROM pg_roles WHERE rolname=ANY(%s)"""
TRIGGER_QUERY="""SELECT c.relname,t.tgname,t.tgenabled,t.tgtype,p.proname AS function_name,f.nspname AS function_schema
 FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
 JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace f ON f.oid=p.pronamespace
 WHERE n.nspname='public' AND t.tgname='data_runtime_write' AND NOT t.tgisinternal"""
DATA_ROLES=['retrolume_data_owner','retrolume_data_app','retrolume_data_snapshot','retrolume_data_restore_loader']


def check_data_shape(rows,roles,triggers):
    from .schema import DATA_FUNCTIONS
    from .contracts import TABLES
    if len(rows)!=len(DATA_FUNCTIONS):raise DataError('data_schema_not_ready',503)
    for row in rows:
        expected=DATA_FUNCTIONS[row['proname']]
        if (digest(re.sub(r'\s+','',row['prosrc']))!=expected['sha256'] or row['prosecdef']!=expected['security_definer']
            or row['provolatile']!=expected['volatility'] or row['proconfig']!=['search_path=pg_catalog, pg_temp']
            or row['owner']!='retrolume_data_owner' or row['public_execute']):raise DataError('data_schema_not_ready',503)
    if len(roles)!=4 or any(any(v for k,v in row.items() if k!='rolname') for row in roles):raise DataError('data_schema_not_ready',503)
    if len(triggers)!=28 or {row['relname'] for row in triggers}!=set(TABLES) or any(
        row['tgenabled']!='O' or row['tgtype']!=31 or row['function_name']!='data_runtime_write_guard' or row['function_schema']!='public'
        for row in triggers):raise DataError('data_schema_not_ready',503)


def assert_data_schema_sync(connection):
    from .schema import DATA_FUNCTIONS
    rows=connection.execute(FUNCTION_QUERY,(list(DATA_FUNCTIONS),)).fetchall()
    roles=connection.execute(ROLE_QUERY,(DATA_ROLES,)).fetchall()
    triggers=connection.execute(TRIGGER_QUERY).fetchall()
    check_data_shape(rows,roles,triggers)


async def assert_data_schema(connection):
    from .schema import DATA_FUNCTIONS
    cursor=await connection.execute(FUNCTION_QUERY,(list(DATA_FUNCTIONS),))
    rows=await cursor.fetchall()
    cursor=await connection.execute(ROLE_QUERY,(DATA_ROLES,))
    roles=await cursor.fetchall()
    cursor=await connection.execute(TRIGGER_QUERY)
    check_data_shape(rows,roles,await cursor.fetchall())


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
    runtime_tables={'material_sources','material_versions','pdf_review_candidates','pdf_extracted_pages','pdf_review_pages',
                    'pdf_user_supplements','activities','activity_scope_sources','activity_allowed_models','activity_operations',
                    'activity_operation_results','teaching_commands','teaching_records','teaching_heads'}
    read_functions={'memory_revision_readable','memory_revision_eligible','activity_memory_eligible','memory_scope_digest',
                    'memory_choice_digest','memory_dependency_digest','memory_dependency_line','interview_result_eligible',
                    'html_expected_renderer','html_expected_html','html_parent_eligible','html_artifact_eligible'}
    def acl(text,table=None,*,function=None,qualification=False):
        if text is None:return None
        if not text.startswith('{') or not text.endswith('}'):raise DataError('data_schema_not_ready',503)
        keep=[]
        for entry in text[1:-1].split(','):
            match=re.fullmatch(r'([^=]+)=([^/]*)/(.+)',entry)
            if not match:raise DataError('data_schema_not_ready',503)
            role,privileges,_=match.groups()
            if role=='retrolume_data_app':
                if table not in runtime_tables or privileges!='arw':raise DataError('data_schema_not_ready',503)
                if qualification:keep.append(entry)
            elif role in allowed:
                permitted={'X'} if function in read_functions and role in ('retrolume_data_snapshot','retrolume_data_restore_loader') else allowed[role] if function is None else set()
                if privileges not in permitted:raise DataError('data_schema_not_ready',503)
            else:keep.append(entry)
        return '{'+','.join(keep)+'}' if keep else None
    for section in ('columns','table_acl','qualification_column_acls'):
        for row in result.get(section,[]):
            for name in ('acl','column_acl','table_acl'):
                if name in row:row[name]=acl(row[name],row.get('relname'),qualification=section=='qualification_column_acls' and name=='table_acl')
    for row in result.get('functions',[]):
        name=row['proname']
        if 'acl' in row:row['acl']=acl(row['acl'],function=name)
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
    constraints=[]
    for row in result.get('constraints',[]):
        if row['conname'] in ('data_restore_budget_shape','data_restore_session_shape'):
            table='html_preview_budgets' if row['conname']=='data_restore_budget_shape' else 'html_preview_sessions'
            if row['relname']!=table or row['contype']!='t' or row['convalidated'] is not True or row['definition']!='TRIGGER DEFERRABLE INITIALLY DEFERRED':
                raise DataError('data_schema_not_ready',503)
        else:constraints.append(row)
    result['constraints']=constraints
    return result


def normalize_html_qualification(shape,owners,runtime_role='retrolume_data_app'):
    """仅映射受信 bootstrap 和固定 app 的部署名字，逐个权限与授权者仍核对。"""
    import copy
    result=copy.deepcopy(shape)
    for row in result['qualification_column_acls']:
        owner=owners.get(row['relname'])
        if owner is None:raise DataError('data_schema_not_ready',503)
        for field in ('column_acl','table_acl'):
            acl=row[field]
            if acl is None:continue
            entries=[]
            for entry in acl[1:-1].split(','):
                match=re.fullmatch(r'([^=]+)=([^/]*)/(.+)',entry)
                if not match or match[3]!=owner:raise DataError('data_schema_not_ready',503)
                role,privileges=match[1],match[2]
                if field=='table_acl':
                    if role==owner and privileges=='arwdDxtm':role='bootstrap_owner'
                    elif role==runtime_role and privileges=='arw':role='runtime_app'
                    else:raise DataError('data_schema_not_ready',503)
                elif role!='retrolume_html_owner' or privileges!='r':raise DataError('data_schema_not_ready',503)
                entries.append(role+'='+privileges+'/bootstrap_owner')
            row[field]='{'+','.join(entries)+'}'
    return result


async def html_qualification_profile(connection,shape):
    cursor=await connection.execute("""SELECT c.relname,r.rolname,r.rolsuper FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname='public' AND c.relname=ANY(%s)""",
        (['pdf_review_candidates','pdf_review_pages','pdf_extracted_pages'],))
    rows=await cursor.fetchall()
    if len(rows)!=3 or any(not row['rolsuper'] for row in rows):raise DataError('data_schema_not_ready',503)
    return normalize_html_qualification(shape,{row['relname']:row['rolname'] for row in rows})
