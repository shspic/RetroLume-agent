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
ROLE_CAPABILITIES="""SELECT r.oid,r.rolname,r.rolcanlogin,r.rolsuper,r.rolcreatedb,r.rolcreaterole,
 r.rolreplication,r.rolbypassrls,
 ARRAY(SELECT p FROM unnest(ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN']) p
       WHERE has_table_privilege(r.oid,'public.activity_scope_sources',p) ORDER BY p) AS privileges,
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
    def closure(start,option):
        result={start};pending=[start]
        while pending:
            for edge in edges.get(pending.pop(),[]):
                if edge[option] and edge['roleid'] not in result:
                    result.add(edge['roleid']);pending.append(edge['roleid'])
        return result
    def accessible(oid):
        # SET uses the session-user chain. It is never made transitively
        # available through an INHERIT-only hop.
        selected=closure(oid,'set_option')
        effective=set().union(*(closure(x,'inherit_option') for x in selected))
        return selected,effective
    def management(role):
        return any(role[k] for k in ('rolsuper','rolcreatedb','rolcreaterole','rolreplication','rolbypassrls'))
    audited=[]
    for subject in roles:
        name=subject['rolname'];selected,effective=accessible(subject['oid'])
        group_names={by_id[x]['rolname'] for x in effective}&set(GROUPS)
        owner=name in OWNERS
        if name not in GROUPS and not owner and not (subject['rolcanlogin'] and group_names):continue
        # A trusted function/table owner may manage its own declared objects,
        # never via membership in another owner or normal application group.
        if owner:allowed={'SELECT'}
        elif name=='retrolume_data_snapshot' or 'retrolume_data_snapshot' in group_names:allowed={'SELECT'}
        elif name=='retrolume_data_restore_loader' or 'retrolume_data_restore_loader' in group_names:allowed={'SELECT','INSERT'}
        else:allowed={'SELECT','INSERT','UPDATE'}|({'DELETE'} if profile=='data_exit.v1.r03' else set())
        for oid in effective:
            role=by_id[oid]
            if not set(role['privileges'])<=allowed:
                raise DataError('data_role_capability_mismatch',503)
            if (role['owns_objects'] or role['owns_definers']) and not (owner and oid==subject['oid']):
                raise DataError('data_role_capability_mismatch',503)
            for edge in edges.get(oid,[]):
                target=by_id[edge['roleid']]
                if edge['admin_option'] and (management(target) or target['owns_objects'] or target['owns_definers']
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
