"""同一PG权威库的记忆事务与前缀锁；不进行模型或文件调用。"""
from __future__ import annotations
import base64
import json
from uuid import UUID
from app.learning.contracts import canonical, sha
from .contracts import MemoryRefusal, MemoryCommandInput, MemorySelectionInput, dependency_line, order_dependencies, dependencies_digest

TABLES=("learning_memories","learning_memory_revisions","learning_memory_bodies","learning_memory_dependencies",
        "learning_memory_commands","activity_memory_bindings","activity_memory_choices")
BINDING_FINGERPRINTS={'tables':'18ec6224b24bbe495fd5ddd98530e6ef1408ecab94c2e982324f14c6b2793f26','constraints':'9ebae3afa28bab399d6fd1b49abe0f2910e76c83cd3f46633a36fee07feb54bb','triggers':'fcd57dd714c48dbd0fa40c6127fe7c549802ee35b038f60c3d4a776dd55678bb'}
SCHEMA_FINGERPRINTS={'tables': '93583d47f23a7d9530554c3f49801328c7f21f6c325eaa3892182c2f0203ef2a', 'constraints': '0ee5a68a453bac88c8abf705178fd837b61f2474d62a86adfb32194ee2a51bbc', 'triggers': 'a4a9d8c4daa95ed6b2e721df999305e0f2ab82bba8c0f2de8323ef516b9abf54'}
FUNCTION_FINGERPRINTS={'memory_dependency_line': '6fd98bae92a118ad22c6b5a11645ce95f71d52cf2ffc2c1711f51587461d0f66', 'memory_dependency_digest': '60a5ce8dc4deb0c3919a75d949b5f9a552f9822640caf25200f0f7002589fac7', 'memory_scope_digest': '6a1a25099f395b6cffc1a7fa97a0d97ef754e57f848ed999e5f9608aac4d15a3', 'memory_choice_digest': 'f4303f3117a83db2c24d02184b7d1dccbccfa4791bf8f2838d8b536929947d12', 'memory_revision_readable': '2b67c4c85c714dae7c181d67acfccbb3b60e6fe5d39bc43e8ff533487fdd2f3f', 'memory_revision_eligible': '69d4e1a885ce570ff6466546ab1807a875db87c06e0312da28deab27460374bb', 'activity_memory_eligible': '103632ed8c37c1ffce17281e1cd7ac915b96ca09cb6dffece890e04777ff6c36', 'memory_immutable_guard': 'f2fe3bed7332630c92ea998fbbd4937633a720b4b7749ab5ab9f8f55b551fa45', 'memory_head_guard': '76a8dd4d0c5ab879a8c9b8f58818f5b6a7e7573dbac64a57d165140b7772dd5d', 'memory_body_guard': '868cb3cf8bb7319b8c7dc60094db97d799cbf20e4967b8ac3af7ea3b38f9ba47', 'memory_final_shape_guard': '2ae3b5b54cc9d1a6f0d488e1d3f10ccbd4cbf2422e3b99a56cb967d6760291d2', 'purge_learning_memory': 'b8927752476771593bf51d0dd69894af1ea9fae4f1e786e3320138ec11665bb9'}
DEP_COLUMNS=("dependency_kind","source_id","source_version_id","source_revision","original_sha256",
 "origin_activity_id","record_id","record_kind","record_sha256","origin_scope_revision","origin_goal_version",
 "upstream_memory_id","upstream_version","upstream_body_sha256")


def plain(value):
    if isinstance(value,dict):return {k:plain(v) for k,v in value.items()}
    if isinstance(value,list):return [plain(v) for v in value]
    if isinstance(value,UUID):return str(value)
    if hasattr(value,"isoformat"):return value.isoformat()
    return value


def impact_token(head, revision):
    return sha(canonical({"policy":"memory.impact.v1","memory_id":str(head["memory_id"]),
                         "revision":head["revision"],"body_sha256":revision["body_sha256"],
                         "dependencies_sha256":revision["dependencies_sha256"]}))


class MemoryLedgerMethods:
    @staticmethod
    def _memory_require_call(activity,operation_id,binding=None,tool=False):
        from app.capabilities.contracts import AdmissionDenied
        if activity is None:return
        if not activity.get('_memory_eligible',True):
            raise AdmissionDenied('memory_dependency_invalid')
        if activity.get('_memory_selected'):
            if tool:
                if not operation_id.startswith('teach8t.'):
                    raise AdmissionDenied('memory_profile_required')
            elif operation_id.startswith('int18m.'):
                from app.interview.contracts import InterviewHybridCallBinding
                if type(binding) is not InterviewHybridCallBinding or binding.memory_selection_sha256!=activity.get('_memory_selection_sha256') or binding.memory_dependency_sha256!=activity.get('_memory_dependency_sha256'):
                    raise AdmissionDenied('memory_profile_required')
            elif not operation_id.startswith('teach8m.') or not getattr(binding,'memory_selection_sha256',None):
                raise AdmissionDenied('memory_profile_required')

    async def _memory_result_sql(self,connection,sql):
        if '/*memory*/' in sql:
            guard=await self._memory_sql_guard(connection,'o.activity_id','r')
            sql=sql.replace('/*memory*/TRUE',guard)
        if '/*memory_meta*/' in sql:
            schema=await self._memory_schema_info(connection)
            meta="""(SELECT jsonb_build_object('selected',true,'selection_sha256',mb.selection_sha256,
             'create_request_sha256',mb.create_request_sha256,'eligible',public.activity_memory_eligible(a.id),
             'entries',COALESCE((SELECT jsonb_agg(jsonb_build_object('memory_id',mc.memory_id,'version',mc.version,
             'revision',mc.selected_revision,'body_sha256',mc.body_sha256) ORDER BY mc.ordinal)
             FROM public.activity_memory_choices mc WHERE mc.activity_id=a.id),'[]'::jsonb))
             FROM public.activity_memory_bindings mb WHERE mb.activity_id=a.id)""" if schema=='ready' else 'NULL::jsonb'
            sql=sql.replace('/*memory_meta*/NULL::jsonb',meta)
        if '/*learning_memory*/' in sql:
            guard=await self._memory_sql_guard(connection,'a.id')
            schema=await self._memory_schema_info(connection)
            selected=await self._memory_selected_sql(connection,'a.id')
            sql=sql.replace('/*learning_memory*/TRUE',guard).replace('/*learning_selected*/FALSE',selected)
        return sql

    async def _memory_teaching_sql(self,connection,sql):
        schema=await self._memory_schema_info(connection)
        guard=await self._memory_sql_guard(connection,'(SELECT id FROM a)')
        record_guard=await self._memory_sql_guard(connection,'r.activity_id')
        selected=await self._memory_selected_sql(connection,'(SELECT id FROM a)')
        return sql.replace('/*teach_memory*/TRUE',guard).replace('/*teach_selected*/FALSE',selected).replace('/*teach_record_memory*/TRUE',record_guard)

    async def _memory_schema_info(self, connection):
        fingerprints=FUNCTION_FINGERPRINTS
        if getattr(self,'data_enabled',False):
            from app.data_exit.schema_checks import assert_data_schema
            from app.data_exit.schema import BUSINESS_FUNCTIONS_013
            await assert_data_schema(connection)
            fingerprints={**FUNCTION_FINGERPRINTS,**{k:v for k,v in BUSINESS_FUNCTIONS_013.items() if k in FUNCTION_FINGERPRINTS}}
        cursor=await connection.execute("""SELECT
          (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname='public' AND c.relname=ANY(%s) AND c.relkind='r') AS tables,
          (SELECT count(*) FROM pg_roles WHERE rolname=ANY(%s)) AS roles,
          (SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
           WHERE n.nspname='public' AND p.proname=ANY(%s)) AS functions""",
          (list(TABLES),["retrolume_memory_owner","retrolume_memory_app","retrolume_memory_purger"],
           ["memory_revision_readable","memory_revision_eligible","activity_memory_eligible","purge_learning_memory"]))
        row=await cursor.fetchone()
        if row["tables"]==0 and row["roles"]==0 and row["functions"]==0:return "absent"
        if row["tables"]!=7 or row["roles"]!=3 or row["functions"]!=4:return "damaged"
        cursor=await connection.execute("""SELECT count(*) AS n FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
         JOIN pg_namespace ns ON ns.oid=c.relnamespace
         WHERE ns.nspname='public' AND t.tgenabled='O' AND NOT t.tgisinternal AND t.tgname=ANY(%s)""",
         (["memory_revision_immutable","memory_dependency_immutable","memory_command_immutable",
           "memory_binding_immutable","memory_choice_immutable","memory_head_identity","memory_body_integrity",
           "memory_revision_shape","memory_dependencies_shape","memory_binding_shape","memory_choices_shape"],))
        if (await cursor.fetchone())["n"]!=11:return "damaged"
        cursor=await connection.execute("""SELECT
          NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=ANY(%s) AND
            (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls)) AS roles_safe,
          NOT EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
             WHERE n.nspname='public' AND c.relname=ANY(%s)
             AND c.relowner<>(SELECT oid FROM pg_roles WHERE rolname='retrolume_memory_owner')) AS owner_safe,
          EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE n.nspname='public' AND p.proname='purge_learning_memory' AND p.prosecdef
             AND p.proowner=(SELECT oid FROM pg_roles WHERE rolname='retrolume_memory_purger')
             AND NOT EXISTS(SELECT 1 FROM aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner))) a
               WHERE a.grantee=0 AND a.privilege_type='EXECUTE')) AS purge_safe""",
            (["retrolume_memory_owner","retrolume_memory_app","retrolume_memory_purger"],list(TABLES)))
        safety=await cursor.fetchone()
        if not all(safety.values()):return 'damaged'
        shapes=await self._memory_shape_hashes(connection,list(TABLES))
        if shapes!=SCHEMA_FINGERPRINTS:return 'damaged'
        cursor=await connection.execute("""SELECT p.proname,p.prosrc,p.provolatile,p.prosecdef,p.proconfig,
            EXISTS(SELECT 1 FROM aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner))) a WHERE a.grantee=0 AND a.privilege_type='EXECUTE') AS public_execute
          FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
          WHERE n.nspname='public' AND p.proname=ANY(%s)""",(list(FUNCTION_FINGERPRINTS),))
        import re
        functions=await cursor.fetchall()
        if len(functions)!=len(FUNCTION_FINGERPRINTS):return 'damaged'
        for function in functions:
            if sha(re.sub(r'\s+','',function['prosrc']))!=fingerprints[function['proname']]:return 'damaged'
            if function['public_execute'] or function['proconfig']!=['search_path=pg_catalog, pg_temp']:return 'damaged'
            if function['prosecdef']!=(function['proname']=='purge_learning_memory'):return 'damaged'
        return 'ready'

    async def _memory_shape_hashes(self,connection,tables):
        queries={
          'tables':"""SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod),a.attnotnull
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid
            WHERE n.nspname='public' AND c.relname=ANY(%s) AND a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum""",
          'constraints':"""SELECT c.relname,k.conname,pg_get_constraintdef(k.oid),k.convalidated
            FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND c.relname=ANY(%s) ORDER BY c.relname,k.conname""",
          'triggers':"""SELECT c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid)
            FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND c.relname=ANY(%s) AND NOT t.tgisinternal
            AND t.tgname IN('memory_binding_immutable','memory_binding_shape','memory_choice_immutable','memory_choices_shape',
             'memory_head_identity','memory_body_integrity','memory_command_immutable','memory_dependencies_shape',
             'memory_dependency_immutable','memory_revision_immutable','memory_revision_shape') ORDER BY c.relname,t.tgname"""}
        result={}
        for section,query in queries.items():
            cursor=await connection.execute(query,(tables,))
            result[section]=sha(canonical([list(row.values()) for row in await cursor.fetchall()]))
        return result

    async def _memory_bindings_reliable(self,connection):
        cursor=await connection.execute("""SELECT
          EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
            JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname='public' AND c.relname='activity_memory_bindings'
             AND c.relkind='r' AND r.rolname='retrolume_memory_owner' AND NOT r.rolcanlogin AND NOT r.rolsuper) AS owned,
          has_table_privilege(current_user,to_regclass('public.activity_memory_bindings'),'SELECT') AS readable,
          NOT has_table_privilege(current_user,to_regclass('public.activity_memory_bindings'),'DELETE')
           AND NOT has_table_privilege(current_user,to_regclass('public.activity_memory_bindings'),'TRUNCATE') AS immutable_role,
          NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) AS ordinary""")
        if not all((await cursor.fetchone()).values()):return False
        if await self._memory_shape_hashes(connection,['activity_memory_bindings'])!=BINDING_FINGERPRINTS:return False
        cursor=await connection.execute("""SELECT p.proname,p.prosrc,p.prosecdef,p.proconfig,p.provolatile,
          r.rolname AS owner FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner
          WHERE n.nspname='public' AND p.proname=ANY(%s)""",(['memory_immutable_guard','memory_final_shape_guard'],))
        rows=await cursor.fetchall()
        import re
        return len(rows)==2 and all(not r['prosecdef'] and r['owner']=='retrolume_memory_owner' and r['provolatile']=='v'
          and r['proconfig']==['search_path=pg_catalog, pg_temp'] and sha(re.sub(r'\s+','',r['prosrc']))==FUNCTION_FINGERPRINTS[r['proname']] for r in rows)

    async def _memory_no_v2_sql(self,connection,expression):
        cursor=await connection.execute("SELECT to_regclass('public.activity_operation_results') IS NOT NULL AS results,to_regclass('public.teaching_commands') IS NOT NULL AS commands")
        objects=await cursor.fetchone();parts=[]
        if objects['results']:
            parts.append(f"NOT EXISTS(SELECT 1 FROM public.activity_operation_results mr WHERE mr.activity_id={expression} AND mr.payload_format='json' AND mr.payload::jsonb->'value'->>'profile' IN ('teaching.v2','teaching.v3','interview.v2'))")
        if objects['commands']:
            parts.append(f"NOT EXISTS(SELECT 1 FROM public.teaching_commands mt WHERE mt.activity_id={expression} AND mt.context_body IS NOT NULL AND mt.context_body::jsonb->>'schema' IN ('teaching.context.v2','teaching.context.v3'))")
        return ' AND '.join(parts) or 'TRUE'

    async def _memory_selected_sql(self,connection,expression):
        schema=await self._memory_schema_info(connection)
        if schema=='ready' or (schema=='damaged' and await self._memory_bindings_reliable(connection)):
            clean=await self._memory_no_v2_sql(connection,expression)
            return f"(EXISTS(SELECT 1 FROM public.activity_memory_bindings mb WHERE mb.activity_id={expression}) OR NOT ({clean}))"
        if schema=='absent':return 'NOT ('+await self._memory_no_v2_sql(connection,expression)+')'
        return 'TRUE'

    async def probe_memory(self):
        async def operation(connection):
            schema=await self._memory_schema_info(connection)
            if schema!="ready":return {"read":False,"write":False,"cleanup":False,"reason":"memory_schema_not_ready"}
            cursor=await connection.execute("""SELECT
              NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user)
              AND NOT pg_has_role(current_user,'retrolume_memory_owner','MEMBER')
              AND NOT pg_has_role(current_user,'retrolume_memory_purger','MEMBER')
              AND NOT has_table_privilege(current_user,'public.learning_memory_bodies','DELETE')
              AND NOT has_table_privilege(current_user,'public.learning_memory_bodies','TRUNCATE')
              AND has_table_privilege(current_user,'public.learning_memory_bodies','INSERT') AS app,
              has_function_privilege(current_user,'public.purge_learning_memory(uuid,text,uuid,text)','EXECUTE') AS cleanup,
              NOT EXISTS(SELECT 1 FROM unnest(%s::text[]) table_name
                WHERE NOT has_table_privilege(current_user,'public.'||table_name,'SELECT')) AS readable""",(list(TABLES),))
            row=await cursor.fetchone()
            return {"read":bool(row['readable']),"write":bool(row["app"] and row['readable']),"cleanup":bool(row["app"] and row["cleanup"] and row['readable']),
                    "reason":None if row["app"] and row['readable'] else "memory_permissions_not_ready"}
        return await self._transaction(operation)

    async def _memory_sql_guard(self,connection,activity_expression, result_alias=None):
        schema=await self._memory_schema_info(connection)
        if schema=="ready":return f"public.activity_memory_eligible({activity_expression})"
        no_v2=await self._memory_no_v2_sql(connection,activity_expression)
        if schema=='damaged':
            if not await self._memory_bindings_reliable(connection):return 'FALSE'
            return f"(NOT EXISTS(SELECT 1 FROM public.activity_memory_bindings mb WHERE mb.activity_id={activity_expression}) AND {no_v2})"
        return no_v2

    async def _memory_assert_schema(self,connection):
        if await self._memory_schema_info(connection)!="ready":
            raise MemoryRefusal("memory_schema_not_ready","学习记忆存储未就绪",503)

    async def _memory_lock_prefix(self,connection,activity_id,extra_sources=(),memory_ids=(),origin_ids=()):
        """必须先于任何活动/operation锁；只定位、锁定与复核，不复制正文。"""
        schema=await self._memory_schema_info(connection)
        hint=await self._source_rows(connection,activity_id) if activity_id else []
        if schema=="ready":
            cursor=await connection.execute("SELECT memory_id::text,version FROM public.activity_memory_choices WHERE activity_id=%s",(activity_id,))
            choices=await cursor.fetchall()
        else:choices=[]
        ids=set(str(x) for x in memory_ids)|{x["memory_id"] for x in choices}
        deps=[];head_hints={}
        if ids and schema!="ready":raise MemoryRefusal("memory_schema_not_ready","记忆资格不可核对",503)
        if ids:
            # 先定位完整上下游头及相关活动，锁后核对头身份，禁止逆序补锁。
            cursor=await connection.execute("""WITH RECURSIVE related(mid) AS(
              SELECT unnest(%s::uuid[])
              UNION SELECT CASE WHEN d.memory_id=x.mid THEN d.upstream_memory_id ELSE d.memory_id END
              FROM related x JOIN public.learning_memory_dependencies d
               ON d.dependency_kind='memory' AND (d.memory_id=x.mid OR d.upstream_memory_id=x.mid))
              SELECT h.memory_id::text,h.revision,h.current_version FROM public.learning_memories h
              JOIN related x ON x.mid=h.memory_id""",(sorted(ids),))
            head_hints={r['memory_id']:(r['revision'],r['current_version']) for r in await cursor.fetchall()}
            ids|=set(head_hints)
            cursor=await connection.execute("""SELECT d.* FROM public.learning_memory_dependencies d
              JOIN public.learning_memories h ON h.memory_id=d.memory_id AND h.current_version=d.version
              WHERE d.memory_id=ANY(%s::uuid[]) ORDER BY d.memory_id,d.ordinal""",(sorted(ids),))
            deps=await cursor.fetchall()
        origins=set(str(x) for x in origin_ids)|{str(d["origin_activity_id"]) for d in deps if d["dependency_kind"]=="event"}
        if ids:
            cursor=await connection.execute("SELECT DISTINCT activity_id::text FROM public.activity_memory_choices WHERE memory_id=ANY(%s::uuid[])",(sorted(ids),))
            origins|={r['activity_id'] for r in await cursor.fetchall()}
        if activity_id:origins.add(activity_id)
        scope_hints={}
        all_sources={str(r["source_id"]) for r in [*hint,*extra_sources]}
        all_sources|={str(d["source_id"]) for d in deps if d["dependency_kind"]=="source"}
        for aid in sorted(origins,key=lambda x:UUID(x).int):
            rows=await self._source_rows(connection,aid)
            scope_hints[aid]=rows
            all_sources|={str(r["source_id"]) for r in rows}
        locked_sources={}
        for sid in sorted(all_sources,key=lambda x:UUID(x).int):
            cursor=await connection.execute("SELECT current_version,revision FROM material_sources WHERE id=%s FOR UPDATE",(sid,))
            locked_sources[sid]=await cursor.fetchone()
        for mid in sorted(ids,key=lambda x:UUID(x).int):
            cursor=await connection.execute("SELECT revision,current_version FROM public.learning_memories WHERE memory_id=%s FOR UPDATE",(mid,))
            actual=await cursor.fetchone()
            if mid in head_hints and (actual is None or (actual['revision'],actual['current_version'])!=head_hints[mid]):
                raise MemoryRefusal('impact_changed','锁定前记忆身份已变化，请只读核对')
        activities={}
        for aid in sorted(origins,key=lambda x:UUID(x).int):
            cursor=await connection.execute("SELECT * FROM activities WHERE id=%s FOR UPDATE",(aid,))
            activities[aid]=await cursor.fetchone()
            await self._verify_scope_hint(connection,aid,scope_hints[aid])
        valid=bool(hint) and all((s:=locked_sources.get(str(r["source_id"]))) is not None
              and str(s["current_version"])==str(r["version_id"]) and s["revision"]==r["source_revision"] for r in hint)
        if schema=="ready":
            cursor=await connection.execute("SELECT public.activity_memory_eligible(%s) AS valid, EXISTS(SELECT 1 FROM public.activity_memory_bindings WHERE activity_id=%s) AS selected",(activity_id,activity_id))
            state=await cursor.fetchone()
        else:
            legacy=await self._memory_sql_guard(connection,"%s")
            cursor=await connection.execute("SELECT "+legacy+" AS valid",tuple(activity_id for _ in range(legacy.count('%s'))))
            state={"valid":(await cursor.fetchone())["valid"]}
            selected=await self._memory_selected_sql(connection,'%s')
            cursor=await connection.execute('SELECT '+selected+' AS selected',tuple(activity_id for _ in range(selected.count('%s'))))
            state['selected']=(await cursor.fetchone())['selected']
        row=activities.get(activity_id)
        if row is not None:
            row["_memory_eligible"]=bool(state["valid"])
            row["_memory_selected"]=bool(state.get("selected"))
            row['_memory_selection_sha256'],row['_memory_dependency_sha256']=await self._memory_binding_identity(connection,activity_id) if schema=='ready' else (None,None)
        return {"activity":row,"snapshots":hint,"sources_valid":valid,"selected":bool(state.get("selected")),
                "eligible":bool(state["valid"]),"activities":activities,"dependencies":deps}

    async def _memory_binding_identity(self,connection,activity_id):
        cursor=await connection.execute('SELECT selection_sha256 FROM activity_memory_bindings WHERE activity_id=%s',(activity_id,))
        binding=await cursor.fetchone()
        if binding is None:return None,None
        cursor=await connection.execute('''SELECT c.memory_id,c.version,c.selected_revision,c.body_sha256,r.dependencies_sha256
          FROM activity_memory_choices c JOIN learning_memory_revisions r ON r.memory_id=c.memory_id AND r.version=c.version
          WHERE c.activity_id=%s ORDER BY c.ordinal''',(activity_id,))
        return binding['selection_sha256'],sha(canonical(plain(await cursor.fetchall())))

    async def _memory_revision_rows(self,connection,memory_id,version=None):
        cursor=await connection.execute("""SELECT h.*,r.claim_kind,r.uncertainty,r.policy_version,r.body_sha256,
         r.body_bytes,r.dependencies_sha256,r.dependency_count,r.version,r.created_by_key,
         b.body FROM public.learning_memories h JOIN public.learning_memory_revisions r
         ON r.memory_id=h.memory_id AND r.version=COALESCE(%s,h.current_version)
         LEFT JOIN public.learning_memory_bodies b ON b.memory_id=r.memory_id AND b.version=r.version WHERE h.memory_id=%s""",(version,memory_id))
        return await cursor.fetchone()

    async def _memory_receipt(self,connection,row,key=None,request_sha=None,duplicate=None):
        meta=json.loads(row["result_meta"])
        cursor=await connection.execute("SELECT state,revision,purge_state FROM public.learning_memories WHERE memory_id=%s",(row["memory_id"],))
        head=await cursor.fetchone()
        return {"schema":"memory.receipt.v1","business_key":key or str(row["business_key"]),
          "action":row["action"],"request_sha256":request_sha or row["request_sha256"],**meta,
          "duplicate_of":duplicate,"qualification_now":"revoked" if head["state"]=="revoked" else
             "current" if head["revision"]==row["after_revision"] else "superseded",
          "purge_state_now":head["purge_state"]}

    async def read_memory_command(self,key):
        async def operation(connection):
            await self._memory_assert_schema(connection)
            cursor=await connection.execute("SELECT * FROM public.learning_memory_commands WHERE business_key=%s",(key,))
            row=await cursor.fetchone()
            return None if row is None else await self._memory_receipt(connection,row)
        return await self._transaction(operation)

    async def read_memory_snapshot(self,memory_id=None,version=None,limit=20,cursor_token=None):
        if type(limit) is not int or not 1<=limit<=50:raise MemoryRefusal("invalid_input","列表容量无效",400)
        after=None;expected=None
        if cursor_token:
            try:
                cursor=json.loads(base64.urlsafe_b64decode(cursor_token+"="*(-len(cursor_token)%4)))
                if set(cursor)!={"after","view_token"}:raise ValueError()
                after=cursor["after"];expected=cursor["view_token"];UUID(after)
            except (ValueError,TypeError,KeyError):raise MemoryRefusal("invalid_input","列表游标无效",400) from None
        async def operation(connection):
            await self._memory_assert_schema(connection)
            if memory_id:
                cur=await connection.execute("""WITH q AS(
                 SELECT h.*,r.version,r.claim_kind,r.uncertainty,r.policy_version,r.body_sha256,r.dependencies_sha256,
                  public.memory_revision_readable(h.memory_id,r.version) AS readable,
                  public.memory_revision_eligible(h.memory_id,r.version) AS eligible
                 FROM public.learning_memories h JOIN public.learning_memory_revisions r ON r.memory_id=h.memory_id
                  AND r.version=COALESCE(%s,h.current_version) WHERE h.memory_id=%s)
                 SELECT q.*,CASE WHEN q.readable THEN b.body ELSE NULL END AS body,
                  CASE WHEN q.readable THEN(SELECT jsonb_agg(to_jsonb(d) ORDER BY d.ordinal) FROM public.learning_memory_dependencies d
                   WHERE d.memory_id=q.memory_id AND d.version=q.version) ELSE NULL END AS dependencies,
                  CURRENT_TIMESTAMP AS read_at FROM q LEFT JOIN public.learning_memory_bodies b USING(memory_id,version)""",(version,memory_id))
                row=await cur.fetchone()
                if row is None:return None
                row=plain(row);row["body"]=json.loads(row["body"]) if row["body"] else None
                row["qualification"]="revoked" if row["state"]=="revoked" else "current" if row["eligible"] else "superseded" if row["readable"] else "memory_dependency_invalid"
                row["view_token"]=sha(canonical({k:row[k] for k in ("memory_id","revision","version","readable","eligible","body_sha256")}))
                return row
            cur=await connection.execute("""WITH q AS(
             SELECT h.memory_id,h.revision,h.current_version AS version,h.state,h.purge_state,h.updated_at,
              r.claim_kind,r.uncertainty,public.memory_revision_readable(h.memory_id,h.current_version) AS readable
             FROM public.learning_memories h JOIN public.learning_memory_revisions r
              ON r.memory_id=h.memory_id AND r.version=h.current_version),
             page AS(SELECT q.*,CASE WHEN q.readable THEN left(b.body::jsonb->>'title',80) ELSE NULL END AS title
              FROM q LEFT JOIN public.learning_memory_bodies b ON b.memory_id=q.memory_id AND b.version=q.version
              WHERE(%s::uuid IS NULL OR q.memory_id>%s::uuid) ORDER BY q.memory_id LIMIT %s)
             SELECT COALESCE((SELECT jsonb_agg(to_jsonb(p) ORDER BY p.memory_id) FROM page p),'[]'::jsonb) AS items,
             (SELECT encode(sha256(convert_to(COALESCE(string_agg(concat_ws('|',memory_id,revision,version,readable),
             E'\n' ORDER BY memory_id),''),'UTF8')),'hex') FROM q) AS view_token,CURRENT_TIMESTAMP AS read_at""",(after,after,limit+1))
            row=await cur.fetchone()
            if expected and row["view_token"]!=expected:raise MemoryRefusal("snapshot_changed","记忆列表已变化，请刷新")
            items=plain(row["items"]);more=len(items)>limit;items=items[:limit]
            for item in items:
                item["qualification"]="revoked" if item["state"]=="revoked" else "current" if item.pop("readable") else "memory_dependency_invalid"
            token=base64.urlsafe_b64encode(canonical({"after":items[-1]["memory_id"],"view_token":row["view_token"]}).encode()).decode().rstrip("=") if more else None
            return {"items":items,"view_token":row["view_token"],"next_cursor":token,"read_at":row["read_at"].isoformat()}
        return await self._transaction(operation)

    async def preview_memory_change(self,memory_id,expected_revision,action):
        async def operation(connection):
            await self._memory_assert_schema(connection)
            cursor=await connection.execute("""SELECT h.*,r.body_sha256,r.dependencies_sha256,
             (SELECT count(DISTINCT activity_id) FROM public.activity_memory_choices WHERE memory_id=h.memory_id) AS activity_count,
             (SELECT count(DISTINCT memory_id) FROM public.learning_memory_dependencies WHERE upstream_memory_id=h.memory_id) AS memory_count,
             (SELECT count(*) FROM public.learning_memory_revisions WHERE memory_id=h.memory_id) AS version_count
             FROM public.learning_memories h JOIN public.learning_memory_revisions r ON r.memory_id=h.memory_id
             AND r.version=h.current_version WHERE h.memory_id=%s""",(memory_id,))
            row=await cursor.fetchone()
            if row is None:raise MemoryRefusal("memory_not_found","记忆不存在",404)
            if row["revision"]!=expected_revision:raise MemoryRefusal("memory_revision_conflict","记忆已有新版本，请核对")
            return {"memory_id":memory_id,"revision":row["revision"],"action":action,"impact_token":impact_token(row,row),
              "activity_count":row["activity_count"],"dependent_memory_count":row["memory_count"],
              "version_count":row["version_count"],"effect":"旧选择和依赖背景停用；原始作答、资料、活动历史及备份实体保留。"}
        return await self._transaction(operation)

    async def _memory_capture(self,connection,activity_id,record_id):
        from app.learning.teaching_views import bound_references, verified_document
        cursor=await connection.execute("""SELECT r.activity_id,r.record_id,r.kind,r.body_sha256,r.scope_revision,r.goal_version,
         r.answer_record_id,r.seq,r.source_refs,
         CASE WHEN public.activity_memory_eligible(r.activity_id)
          AND NOT EXISTS(SELECT 1 FROM jsonb_array_elements(r.source_refs::jsonb) ref
            LEFT JOIN material_sources ms ON ms.id=(ref->>'source_id')::uuid
            LEFT JOIN material_versions mv ON mv.id=(ref->>'version_id')::uuid AND mv.source_id=ms.id
            WHERE ms.current_version IS DISTINCT FROM (ref->>'version_id')::uuid
              OR ms.revision IS DISTINCT FROM (ref->>'source_revision')::integer
              OR mv.sha256 IS DISTINCT FROM ref->>'original_sha256')
          AND NOT EXISTS(SELECT 1 FROM teaching_records x WHERE x.activity_id=r.activity_id
           AND((x.kind='correction' AND x.parent_record_id IN(r.record_id,r.parent_record_id))
             OR(x.kind='answer' AND x.supersedes_record_id=r.answer_record_id)
             OR(x.kind='feedback' AND x.answer_record_id=r.answer_record_id AND x.seq>r.seq)))
          THEN r.body ELSE NULL END AS body
         FROM teaching_records r WHERE r.activity_id=%s AND r.record_id=%s""",(activity_id,record_id))
        progress=await cursor.fetchone()
        if progress is None or progress["kind"]!="progress":
            raise MemoryRefusal("record_not_found","请选择可回查的学习进度",404)
        if progress["body"] is None:raise MemoryRefusal("memory_dependency_invalid","该学习观察已失效，不能保存其内容")
        document=verified_document(progress)
        answer_ids=set(document.get("observations",{}).get("independent_answers",[]))
        if progress["answer_record_id"]:answer_ids.add(str(progress["answer_record_id"]))
        ids={record_id}
        cursor=await connection.execute("""SELECT r.* FROM teaching_records r WHERE r.activity_id=%s
          AND(r.record_id=ANY(%s::uuid[]) OR(r.kind='feedback' AND r.answer_record_id=ANY(%s::uuid[]) AND r.seq<=%s))
          ORDER BY r.seq DESC""",(activity_id,sorted(answer_ids),sorted(answer_ids),progress["seq"]))
        rows=await cursor.fetchall();latest={}
        for row in rows:
            if row["kind"]=="feedback":
                latest.setdefault(str(row["answer_record_id"]),row)
            else:ids.add(str(row["record_id"]))
        selected=[progress,*[r for r in rows if r["kind"]=="answer"],*latest.values()]
        for row in selected:
            if row.get("exercise_record_id"):ids.add(str(row["exercise_record_id"]))
            ids.add(str(row["record_id"]))
        cursor=await connection.execute("SELECT * FROM teaching_records WHERE activity_id=%s AND record_id=ANY(%s::uuid[]) ORDER BY seq",(activity_id,sorted(ids)))
        records=await cursor.fetchall();deps=[]
        for record in records:
            refs=bound_references(record)
            if refs is None:raise MemoryRefusal("memory_source_invalid","观察来源无法核对")
            for ref in refs:
                deps.append({"dependency_kind":"source","source_id":ref["source_id"],"source_version_id":ref["version_id"],
                             "source_revision":ref["source_revision"],"original_sha256":ref["original_sha256"]})
            deps.append({"dependency_kind":"event","origin_activity_id":activity_id,"record_id":str(record["record_id"]),
               "record_kind":record["kind"],"record_sha256":record["body_sha256"],"origin_scope_revision":record["scope_revision"],
               "origin_goal_version":record["goal_version"]})
        cursor=await connection.execute("SELECT * FROM public.activity_memory_choices WHERE activity_id=%s ORDER BY ordinal",(activity_id,))
        choices=await cursor.fetchall()
        for choice in choices:
            deps.append({"dependency_kind":"memory","upstream_memory_id":str(choice["memory_id"]),
                         "upstream_version":choice["version"],"upstream_body_sha256":choice["body_sha256"]})
            cursor=await connection.execute("SELECT * FROM public.learning_memory_dependencies WHERE memory_id=%s AND version=%s ORDER BY ordinal",(choice["memory_id"],choice["version"]))
            deps.extend(await cursor.fetchall())
        deps=order_dependencies(deps)
        token=sha(canonical({"id":record_id,"hash":progress["body_sha256"],"dependencies":dependencies_digest(deps)}))
        observation={"activity_id":activity_id,"progress_record_id":record_id,
                     "status":document.get("observations",{}).get("status","unknown"),
                     "reason":str(document.get("reason",""))[:240],"independent_answer_ids":sorted(answer_ids),
                     "uncertainty":"limited","limitation":"当时有限活动观察，不证明长期掌握。"}
        return {"record_sha256":progress["body_sha256"],"view_token":token,"dependencies":deps,"observation":observation}

    async def preview_memory_observation(self,activity_id,record_id):
        async def operation(connection):
            await self._memory_assert_schema(connection)
            value=await self._memory_capture(connection,activity_id,record_id)
            value["capture"]={"activity_id":activity_id,"progress_record_id":record_id,
                 "record_sha256":value["record_sha256"],"view_token":value["view_token"]}
            value.pop("dependencies")
            return value
        return await self._transaction(operation)

    async def _memory_insert_receipt(self,connection,command,after_revision,after_version,effect,meta,manifest=None):
        await connection.execute("""INSERT INTO public.learning_memory_commands(business_key,action,memory_id,
         request_sha256,slot_sha256,effect_applied,before_revision,after_revision,after_version,result_meta,cleanup_manifest,manifest_sha256)
         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
         (command.business_key,command.action,command.memory_id,command.request_sha(),command.slot(),effect,
          command.expected_revision,after_revision,after_version,canonical(meta),manifest,sha(manifest) if manifest else None))

    async def q_snapshot_memory_cleanup_ids(self,memory_id):
        async def q_snapshot_memory_dependencies(connection):
            cursor=await connection.execute("""WITH RECURSIVE affected(memory_id) AS(
              SELECT %s::uuid UNION SELECT d.memory_id FROM public.learning_memory_dependencies d
              JOIN affected a ON d.upstream_memory_id=a.memory_id
            ) SELECT memory_id::text FROM affected ORDER BY memory_id""",(memory_id,))
            return [row['memory_id'] for row in await cursor.fetchall()]
        return await self._transaction(q_snapshot_memory_dependencies)

    async def apply_memory_command(self,command:MemoryCommandInput):
        async def operation(connection):
            await self._memory_assert_schema(connection)
            cursor=await connection.execute("SELECT * FROM public.learning_memory_commands WHERE business_key=%s",(command.business_key,))
            existing=await cursor.fetchone()
            if existing:
                if existing["request_sha256"]!=command.request_sha():raise MemoryRefusal("command_key_conflict","同键已经绑定不同内容")
                return {**await self._memory_receipt(connection,existing),"replayed":True}
            if command.action=="purge":
                cursor=await connection.execute("SELECT memory_id FROM public.learning_memory_commands WHERE business_key=%s AND action='revoke'",(command.body["revocation_key"],))
                original=await cursor.fetchone()
                if original is None or str(original["memory_id"])!=command.memory_id:
                    raise MemoryRefusal("memory_dependency_invalid","清理意图不属于这条记忆")
                cursor=await connection.execute("SELECT public.purge_learning_memory(%s,%s,%s,%s) AS meta",
                    (command.body["revocation_key"],command.body["manifest_sha256"],command.business_key,command.request_sha()))
                result=json.loads((await cursor.fetchone())["meta"])
                return {"schema":"memory.receipt.v1","business_key":command.business_key,"action":"purge",
                        "request_sha256":command.request_sha(),"qualification_now":"revoked","duplicate_of":None,**result}
            hint=None
            if command.action=="save" and command.body["kind"]=="learning_observation":
                cap=command.body["capture"];hint=await self._memory_capture(connection,cap["activity_id"],cap["progress_record_id"])
                if hint["record_sha256"]!=cap["record_sha256"] or hint["view_token"]!=cap["view_token"]:
                    raise MemoryRefusal("impact_changed","保存观察已变化，请重新查看")
                sources=[{"source_id":d["source_id"],"version_id":d["source_version_id"],"source_revision":d["source_revision"]}
                         for d in hint["dependencies"] if d["dependency_kind"]=="source"]
                upstream=[d["upstream_memory_id"] for d in hint["dependencies"] if d["dependency_kind"]=="memory"]
                await self._memory_lock_prefix(connection,cap["activity_id"],extra_sources=sources,
                    memory_ids=[command.memory_id,*upstream],origin_ids=[cap["activity_id"]])
                current=await self._memory_capture(connection,cap["activity_id"],cap["progress_record_id"])
                if current["view_token"]!=hint["view_token"]:raise MemoryRefusal("impact_changed","观察发生变化")
                hint=current
            else:
                await self._memory_lock_prefix(connection,None,memory_ids=[command.memory_id])
            cursor=await connection.execute("SELECT * FROM public.learning_memory_commands WHERE business_key=%s",(command.business_key,))
            existing=await cursor.fetchone()
            if existing:
                if existing['request_sha256']!=command.request_sha():raise MemoryRefusal('command_key_conflict','同键已经绑定不同内容')
                return {**await self._memory_receipt(connection,existing),'replayed':True}
            cursor=await connection.execute("SELECT * FROM public.learning_memory_commands WHERE slot_sha256=%s AND effect_applied",(command.slot(),))
            winner=await cursor.fetchone()
            if winner:
                if winner["request_sha256"]!=command.request_sha():raise MemoryRefusal("memory_revision_conflict","相同修订已有不同操作")
                await self._memory_insert_receipt(connection,command,winner["after_revision"],winner["after_version"],False,json.loads(winner["result_meta"]))
                cursor=await connection.execute("SELECT * FROM public.learning_memory_commands WHERE business_key=%s",(command.business_key,))
                return await self._memory_receipt(connection,await cursor.fetchone(),duplicate=str(winner["business_key"]))
            head=await self._memory_revision_rows(connection,command.memory_id)
            if command.action=="save":
                if head:raise MemoryRefusal("memory_revision_conflict","此记忆编号已存在")
                body={"schema":"memory.body.v1","title":command.body["title"],"kind":command.body["kind"],
                      "text":command.body.get("text",""),"uncertainty":"limited" if hint else "self_reported",
                      "observation":hint["observation"] if hint else None}
                deps=hint["dependencies"] if hint else []
                revision=version=1
                await connection.execute("INSERT INTO public.learning_memories(memory_id,revision,current_version,state) VALUES(%s,1,1,'active')",(command.memory_id,))
            else:
                if head is None:raise MemoryRefusal("memory_not_found","记忆不存在",404)
                if head["state"]!="active":raise MemoryRefusal("memory_revoked","记忆已经撤销")
                if head["revision"]!=command.expected_revision:raise MemoryRefusal("memory_revision_conflict","记忆已有新版本")
                if command.body["impact_token"]!=impact_token(head,head):raise MemoryRefusal("impact_changed","修改影响已变化")
                if command.action=="revoke":
                    cursor=await connection.execute("""SELECT b.memory_id::text,b.version,r.body_sha256,r.body_bytes
                      FROM public.learning_memory_bodies b JOIN public.learning_memory_revisions r USING(memory_id,version)
                      WHERE b.memory_id=%s ORDER BY b.version""",(command.memory_id,))
                    targets=await cursor.fetchall()
                    manifest=canonical({"policy":"memory.purge.v1","memory_id":command.memory_id,"revocation_key":command.business_key,
                       "revision":head["revision"]+1,"targets":targets})
                    meta={"memory_id":command.memory_id,"revision_after":head["revision"]+1,"version_after":head["current_version"],
                          "status":"committed","revocation_key":command.business_key,"manifest_sha256":sha(manifest)}
                    await self._memory_insert_receipt(connection,command,head["revision"]+1,head["current_version"],True,meta,manifest)
                    await connection.execute("""UPDATE public.learning_memories SET state='revoked',revision=revision+1,
                      revoked_at=CURRENT_TIMESTAMP,revocation_key=%s,purge_state='pending',updated_at=CURRENT_TIMESTAMP WHERE memory_id=%s""",(command.business_key,command.memory_id))
                    cur=await connection.execute("SELECT * FROM public.learning_memory_commands WHERE business_key=%s",(command.business_key,))
                    return await self._memory_receipt(connection,await cur.fetchone())
                if command.body["base_body_sha256"]!=head["body_sha256"]:raise MemoryRefusal("memory_revision_conflict","编辑身份已变化")
                old=json.loads(head["body"])
                if command.body["kind"]=="learning_observation" and old["kind"]!="learning_observation":
                    raise MemoryRefusal("invalid_input","用户自报不能改成受检观察",400)
                body={**old,"title":command.body["title"],"text":command.body["text"],"kind":command.body["kind"],
                      "uncertainty":"limited" if command.body["kind"]=="learning_observation" else "self_reported"}
                cursor=await connection.execute("SELECT * FROM public.learning_memory_dependencies WHERE memory_id=%s AND version=%s ORDER BY ordinal",(command.memory_id,head["current_version"]))
                deps=order_dependencies(await cursor.fetchall())
                if canonical(body)==head["body"]:
                    meta={"memory_id":command.memory_id,"revision_after":head["revision"],"version_after":head["current_version"],"status":"committed"}
                    await self._memory_insert_receipt(connection,command,head["revision"],head["current_version"],False,meta)
                    cur=await connection.execute("SELECT * FROM public.learning_memory_commands WHERE business_key=%s",(command.business_key,))
                    return await self._memory_receipt(connection,await cur.fetchone())
                if head["current_version"]==32:raise MemoryRefusal("memory_version_limit","版本容量已满，请另存明确的新记忆")
                revision=head["revision"]+1;version=head["current_version"]+1
            body_text=canonical(body)
            if len(body_text.encode("utf-8"))>4096:raise MemoryRefusal("memory_context_limit","记忆正文超过有限容量")
            meta={"memory_id":command.memory_id,"revision_after":revision,"version_after":version,"status":"committed"}
            await self._memory_insert_receipt(connection,command,revision,version,True,meta)
            await connection.execute("""INSERT INTO public.learning_memory_revisions(memory_id,version,claim_kind,uncertainty,
              policy_version,body_sha256,body_bytes,dependencies_sha256,dependency_count,created_by_key)
              VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(command.memory_id,version,body["kind"],body["uncertainty"],
              "memory.observation.v1" if body["kind"]=="learning_observation" else "memory.user.v1",
              sha(body_text),len(body_text.encode("utf-8")),dependencies_digest(deps),len(deps),command.business_key))
            for ordinal,d in enumerate(deps,1):
                await connection.execute("INSERT INTO public.learning_memory_dependencies(memory_id,version,ordinal,"+
                 ",".join(DEP_COLUMNS)+") VALUES("+",".join(["%s"]*(3+len(DEP_COLUMNS)))+")",
                 (command.memory_id,version,ordinal,*[d.get(k) for k in DEP_COLUMNS]))
            await connection.execute("INSERT INTO public.learning_memory_bodies(memory_id,version,body) VALUES(%s,%s,%s)",(command.memory_id,version,body_text))
            if command.action=="revise":
                await connection.execute("UPDATE public.learning_memories SET revision=%s,current_version=%s,updated_at=CURRENT_TIMESTAMP WHERE memory_id=%s",(revision,version,command.memory_id))
            if hint:
                cursor=await connection.execute("SELECT public.memory_revision_eligible(%s,%s) AS valid",(command.memory_id,version))
                if not (await cursor.fetchone())["valid"]:raise MemoryRefusal("memory_dependency_invalid","该观察或上游背景已变化")
            cursor=await connection.execute("SELECT * FROM public.learning_memory_commands WHERE business_key=%s",(command.business_key,))
            return await self._memory_receipt(connection,await cursor.fetchone())
        from app.capabilities.contracts import AdmissionUnavailable
        closing=False
        gate=getattr(self,'mutation_gate',None)
        if command.action=='purge' and gate is not None:
            from app.data_exit.maintenance import CLOSE_LANE
            owner=gate.hub.state()['owned'].get(CLOSE_LANE.get())
            if owner is not None and owner.get('state')=='registered':
                identity=owner['identity']
                closing=identity.get('service')=='MemoryService.submit_command' and identity.get('memory_id')==command.memory_id and (
                    identity.get('action')=='revoke' and identity.get('business_key')==command.body['revocation_key'] or
                    identity.get('action')=='purge' and identity.get('business_key')==command.business_key)
        try:return await (self._transaction(operation,closing_memory_purge=True) if closing else self._transaction(operation))
        except AdmissionUnavailable:
            # 同时首次INSERT可能由唯一约束决定赢家；仅做一次有限收据核对。
            async def confirm(connection):
                await self._memory_assert_schema(connection)
                cursor=await connection.execute('SELECT * FROM public.learning_memory_commands WHERE business_key=%s OR (slot_sha256=%s AND effect_applied) ORDER BY (business_key=%s) DESC LIMIT 1',
                  (command.business_key,command.slot(),command.business_key))
                row=await cursor.fetchone()
                if row is None:return None
                if row['request_sha256']!=command.request_sha():
                    raise MemoryRefusal('command_key_conflict' if str(row['business_key'])==command.business_key else 'memory_revision_conflict','已有动作绑定不同内容')
                duplicate=None
                if str(row['business_key'])!=command.business_key:
                    duplicate=str(row['business_key'])
                    await self._memory_insert_receipt(connection,command,row['after_revision'],row['after_version'],False,json.loads(row['result_meta']))
                    cursor=await connection.execute('SELECT * FROM public.learning_memory_commands WHERE business_key=%s',(command.business_key,))
                    row=await cursor.fetchone()
                return {**await self._memory_receipt(connection,row,duplicate=duplicate),'replayed':True}
            receipt=await self._transaction(confirm)
            if receipt is not None:return receipt
            raise

    async def read_memory_selection(self,activity_id,include_bodies=False):
        async def operation(connection):
            schema=await self._memory_schema_info(connection)
            if schema!="ready":
                guard=await self._memory_sql_guard(connection,"%s")
                cursor=await connection.execute("SELECT "+guard+" AS valid",tuple(activity_id for _ in range(guard.count('%s'))))
                eligible=(await cursor.fetchone())["valid"]
                return {"selected":not eligible,"eligible":bool(eligible),"selection_sha256":None,"entries":[],"classification":"legacy" if eligible else "unavailable","reason":None if eligible else "memory_schema_not_ready"}
            await self._memory_assert_schema(connection)
            cursor=await connection.execute("""SELECT b.selection_sha256,b.bound_scope_revision,
             public.activity_memory_eligible(b.activity_id) AS eligible,
             COALESCE((SELECT jsonb_agg(jsonb_build_object('memory_id',c.memory_id,'version',c.version,
              'revision',c.selected_revision,'body_sha256',c.body_sha256,
              'body',CASE WHEN %s AND public.activity_memory_eligible(b.activity_id) THEN mb.body ELSE NULL END)
              ORDER BY c.ordinal) FROM public.activity_memory_choices c LEFT JOIN public.learning_memory_bodies mb
              ON mb.memory_id=c.memory_id AND mb.version=c.version WHERE c.activity_id=b.activity_id),'[]'::jsonb) AS entries
             FROM public.activity_memory_bindings b WHERE b.activity_id=%s""",(include_bodies,activity_id))
            row=await cursor.fetchone()
            if row is None:
                cursor=await connection.execute('SELECT public.activity_memory_eligible(%s) AS valid',(activity_id,))
                valid=bool((await cursor.fetchone())['valid'])
                return {"selected":not valid,"eligible":valid,"selection_sha256":None,"entries":[]}
            value=plain(row);value["selected"]=True
            _,value['dependency_sha256']=await self._memory_binding_identity(connection,activity_id)
            for entry in value["entries"]:
                if entry["body"]:entry["body"]=json.loads(entry["body"])
                if not include_bodies:entry.pop("body",None)
            return value
        return await self._transaction(operation)

    async def _memory_insert_selection(self,connection,spec,selection,create_sha):
        entries=selection.entries
        for x in entries:
            cursor=await connection.execute("""SELECT h.revision,r.body_sha256,
             public.memory_revision_eligible(h.memory_id,%s) AS valid FROM public.learning_memories h
             JOIN public.learning_memory_revisions r ON r.memory_id=h.memory_id AND r.version=%s WHERE h.memory_id=%s""",(x.version,x.version,x.memory_id))
            row=await cursor.fetchone()
            if row is None or not row["valid"] or row["revision"]!=x.revision or row["body_sha256"]!=x.body_sha256:
                raise MemoryRefusal("memory_dependency_invalid","所选记忆版本已变化")
        cursor=await connection.execute("SELECT public.memory_scope_digest(%s) AS digest",(spec.activity_id,))
        scope_sha=(await cursor.fetchone())["digest"]
        await connection.execute("""INSERT INTO public.activity_memory_bindings(activity_id,selection_sha256,create_request_sha256,
         bound_scope_revision,bound_scope_sha256,selected_count,policy_version) VALUES(%s,%s,%s,%s,%s,%s,'memory.selection.v1')""",
         (spec.activity_id,selection.digest(),create_sha,spec.scope_revision,scope_sha,len(entries)))
        for i,x in enumerate(entries,1):
            await connection.execute("""INSERT INTO public.activity_memory_choices(activity_id,memory_id,version,selected_revision,body_sha256,ordinal)
             VALUES(%s,%s,%s,%s,%s,%s)""",(spec.activity_id,x.memory_id,x.version,x.revision,x.body_sha256,i))
        cursor=await connection.execute("SELECT public.activity_memory_eligible(%s) AS valid",(spec.activity_id,))
        if not (await cursor.fetchone())["valid"]:raise MemoryRefusal("memory_scope_mismatch","所选记忆来源不在当前资料范围")
