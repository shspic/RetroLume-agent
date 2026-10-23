"""Purpose-specific PG17 capability separation, before shape/ACL projection.

Membership alone is not a privilege. Follow SET chains and, from each possible
current role, INHERIT chains; inspect ADMIN edges separately. SQL privilege
inquiries below report actual inherited table rights, not an ACL simulation.
"""
from .contracts import DataError

GROUPS=('retrolume_data_app','retrolume_data_snapshot','retrolume_data_restore_loader','retrolume_data_owner')
OWNERS=('retrolume_data_owner','retrolume_memory_owner','retrolume_teaching_owner',
        'retrolume_interview_owner','retrolume_html_owner','retrolume_retrieval_owner')
PRIVILEGES=('SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN')
DANGEROUS_PREDEFINED=frozenset(('pg_execute_server_program','pg_read_server_files','pg_write_server_files',
    'pg_signal_backend','pg_checkpoint','pg_maintain','pg_create_subscription'))
ROLE_CAPABILITIES="""SELECT r.oid,r.rolname,r.rolcanlogin,r.rolsuper,r.rolcreatedb,r.rolcreaterole,
 r.rolreplication,r.rolbypassrls,
 ARRAY(SELECT p FROM unnest(ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN']) p
       WHERE has_table_privilege(r.oid,'public.activity_scope_sources',p) ORDER BY p) AS privileges,
 ARRAY(SELECT p FROM unnest(ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN']) p
       WHERE has_table_privilege(r.oid,'public.data_control',p) ORDER BY p) AS control_privileges,
 has_schema_privilege(r.oid,'public','CREATE') AS schema_create,
 has_database_privilege(r.oid,current_database(),'CREATE') AS database_create,
 EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE c.relowner=r.oid AND n.nspname='public' AND c.relkind IN('r','p','v')) AS owns_objects,
 EXISTS(SELECT 1 FROM pg_proc f JOIN pg_namespace n ON n.oid=f.pronamespace
        WHERE f.proowner=r.oid AND n.nspname='public' AND f.prosecdef) AS owns_definers
 FROM pg_roles r ORDER BY r.oid"""
MEMBERSHIPS="SELECT roleid,member,grantor,inherit_option,set_option,admin_option FROM pg_auth_members ORDER BY member,roleid,grantor"


def check_role_capabilities(roles,members,profile):
    if len(roles)>1024 or len(members)>4096:raise DataError('data_role_capability_mismatch',503)
    by_id={r['oid']:r for r in roles};by_name={r['rolname']:r for r in roles};edges={}
    if not set(GROUPS)<=set(by_name):raise DataError('data_role_capability_mismatch',503)
    for m in members:edges.setdefault(m['member'],[]).append(m)
    def accessible(oid,*,admin=False):
        # SET uses the session-user chain. It is never made transitively
        # available through an INHERIT-only hop.
        selected=set();effective=set();pending=[(oid,True)]
        # ADMIN can grant its target to a controlled/SET-accessible role,
        # enabling SET/INHERIT regardless of the original edge's options.
        # Newly reachable roles can themselves hold ADMIN. Saturate that
        # capability, not just the target's current inherited table rights.
        # Sets grow monotonically within the bounded input role set; cycles
        # cannot recurse indefinitely or manufacture new role identities.
        # Each role is processed at most once in each mode, with at most
        # two scans of each edge per subject, including cyclic inputs.
        while pending:
            current,select=pending.pop();seen=selected if select else effective
            if current in seen:continue
            seen.add(current)
            if select:pending.append((current,False))
            for edge in edges.get(current,[]):
                if select and edge['set_option']:pending.append((edge['roleid'],True))
                if not select and edge['inherit_option']:pending.append((edge['roleid'],False))
                if not select and admin and edge['admin_option']:pending.append((edge['roleid'],True))
        return selected,effective
    def management(role):
        return any(role[k] for k in ('rolsuper','rolcreatedb','rolcreaterole','rolreplication','rolbypassrls'))
    def extra_management(role):
        return bool(role['control_privileges'] or role['schema_create'] or role['database_create']
                    or role['rolname'] in DANGEROUS_PREDEFINED)
    audited=[]
    for subject in roles:
        name=subject['rolname'];_,current_effective=accessible(subject['oid'])
        group_names={by_id[x]['rolname'] for x in current_effective}&set(GROUPS)
        owner=name in OWNERS
        if name not in GROUPS and not owner and not (subject['rolcanlogin'] and group_names):continue
        selected,effective=accessible(subject['oid'],admin=True)
        # A trusted function/table owner may manage its own declared objects,
        # never via membership in another owner or normal application group.
        if owner:allowed={'SELECT'}
        elif name=='retrolume_data_snapshot' or 'retrolume_data_snapshot' in group_names:allowed={'SELECT'}
        elif name=='retrolume_data_restore_loader' or 'retrolume_data_restore_loader' in group_names:allowed={'SELECT','INSERT'}
        else:allowed={'SELECT','INSERT','UPDATE'}|({'DELETE'} if profile=='data_exit.v1.r03' else set())
        for oid in effective:
            role=by_id[oid]
            if role['rolname'] in DANGEROUS_PREDEFINED or role['schema_create'] or role['database_create']:
                raise DataError('data_role_capability_mismatch',503)
            if role['control_privileges'] and not (name=='retrolume_data_owner' and oid==subject['oid']):
                raise DataError('data_role_capability_mismatch',503)
            if not set(role['privileges'])<=allowed:
                raise DataError('data_role_capability_mismatch',503)
            if (role['owns_objects'] or role['owns_definers']) and not (owner and oid==subject['oid']):
                raise DataError('data_role_capability_mismatch',503)
            for edge in edges.get(oid,[]):
                target=by_id[edge['roleid']]
                if edge['admin_option'] and (management(target) or extra_management(target) or target['owns_objects'] or target['owns_definers']
                        or not set(target['privileges'])<=allowed):
                    raise DataError('data_role_capability_mismatch',503)
        if any(management(by_id[oid]) for oid in selected):raise DataError('data_role_capability_mismatch',503)
        audited.append({'role':name,'purpose':'trusted_owner' if owner else sorted(group_names),
                        'set_roles':[by_id[x]['rolname'] for x in sorted(selected)],
                        'effective_roles':[by_id[x]['rolname'] for x in sorted(effective)]})
    return audited


def assert_roles_sync(connection,profile):
    roles=connection.execute(ROLE_CAPABILITIES).fetchall();members=connection.execute(MEMBERSHIPS).fetchall()
    return check_role_capabilities(roles,members,profile)


async def assert_roles(connection,profile):
    cursor=await connection.execute(ROLE_CAPABILITIES);roles=await cursor.fetchall()
    cursor=await connection.execute(MEMBERSHIPS);members=await cursor.fetchall()
    return check_role_capabilities(roles,members,profile)
