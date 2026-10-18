"""G10 transactions and statement-snapshot reads on the native admission DB."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.interview.contracts import (InterviewRefusal, InterviewCommandInput, InterviewContext,
    InterviewProfile, InterviewCallBinding, SourceBinding, GoalBody, MAX_RECORDS, MAX_COMMANDS,
    MAX_REVISION, PREFIX, canonical, sha, load_json, operation_id, profile_for)
from app.interview.policy import transition
from app.interview.views import plain, token, verified_body, bounded_wire

TABLES=('interview_heads','interview_commands','interview_records')
FUNCTIONS=('interview_record_insert_guard','interview_record_immutable_guard','interview_command_guard','interview_head_guard','interview_result_eligible')
# Filled from the approved 011 execution/catalog in the isolated preparation root;
# an unbound or different signature fails closed, never adopts an arbitrary DB.
SCHEMA_FINGERPRINT = '13e3d8d9d78d7f6e119a226be6f4d6f3163b9bf5eaeeb1b8d66e5d44351f850b'


class InterviewLedgerMethods:
    async def _interview_shape(self, connection):
        await connection.execute('SET LOCAL search_path=pg_catalog,public')
        result={}
        queries={
            'columns':"""SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod) AS type,a.attnotnull,
              pg_get_expr(d.adbin,d.adrelid) AS default,ro.rolname AS owner,a.attacl::text AS acl
              FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles ro ON ro.oid=c.relowner
              JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped
              LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
              WHERE n.nspname='public' AND c.relname=ANY(%s) ORDER BY c.relname,a.attnum""",
            'constraints':"""SELECT c.relname,k.conname,k.contype,k.convalidated,k.condeferrable,k.condeferred,
              pg_get_constraintdef(k.oid) AS definition FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid
              JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname=ANY(%s) ORDER BY c.relname,k.conname""",
            'indexes':"""SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' AND tablename=ANY(%s) ORDER BY tablename,indexname""",
            'triggers':"""SELECT c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid) AS definition FROM pg_trigger t
              JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
              WHERE n.nspname='public' AND c.relname=ANY(%s) AND NOT t.tgisinternal ORDER BY c.relname,t.tgname""",
        }
        for key,sql in queries.items():
            cursor=await connection.execute(sql,(list(TABLES),));result[key]=plain(await cursor.fetchall())
        cursor=await connection.execute("""SELECT p.proname,pg_get_function_identity_arguments(p.oid) AS arguments,
          l.lanname,p.prosrc,p.prosecdef,p.proconfig,p.provolatile,p.proacl::text AS acl,r.rolname AS owner
          FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner
          JOIN pg_language l ON l.oid=p.prolang WHERE n.nspname='public' AND p.proname=ANY(%s) ORDER BY p.proname""",(list(FUNCTIONS),))
        result['functions']=plain(await cursor.fetchall())
        cursor=await connection.execute("""SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls
          FROM pg_roles WHERE rolname IN ('retrolume_interview_owner','retrolume_interview_app') ORDER BY rolname""")
        result['roles']=plain(await cursor.fetchall())
        cursor=await connection.execute("""SELECT c.relname,c.relacl::text AS acl FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
          WHERE n.nspname='public' AND c.relname=ANY(%s) ORDER BY c.relname""",(list(TABLES),))
        result['table_acl']=plain(await cursor.fetchall())
        return result

    async def _interview_schema_info(self,connection):
        cursor=await connection.execute("""SELECT count(*) AS n FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
          WHERE n.nspname='public' AND c.relname=ANY(%s)""",(list(TABLES),))
        n=(await cursor.fetchone())['n']
        if n==0:
            cursor=await connection.execute("""SELECT (SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
              WHERE n.nspname='public' AND p.proname=ANY(%s))+(SELECT count(*) FROM pg_roles
              WHERE rolname IN ('retrolume_interview_owner','retrolume_interview_app')) AS n""",(list(FUNCTIONS),))
            return 'absent' if (await cursor.fetchone())['n']==0 else 'damaged'
        if n!=3 or not SCHEMA_FINGERPRINT: return 'damaged'
        shape=await self._interview_shape(connection)
        return 'ready' if sha(canonical(shape))==SCHEMA_FINGERPRINT else 'damaged'

    async def _interview_domain(self,connection,activity_id, *, for_write=False):
        schema=await self._interview_schema_info(connection)
        if schema=='ready':
            cursor=await connection.execute('SELECT EXISTS(SELECT 1 FROM public.interview_heads WHERE activity_id=%s) AS found',(activity_id,))
            if (await cursor.fetchone())['found']: return 'interview'
            return 'existing'
        cursor=await connection.execute("""SELECT EXISTS(SELECT 1 FROM public.activity_operations WHERE activity_id=%s AND left(operation_id,7)='int10m.')
          OR EXISTS(SELECT 1 FROM public.activity_operation_results WHERE activity_id=%s AND
          CASE WHEN payload_format='json' THEN payload::jsonb->'value'->>'profile'='interview.v1' ELSE false END) AS found""",(activity_id,activity_id))
        residual=(await cursor.fetchone())['found']
        if residual or schema=='damaged':
            if for_write: raise InterviewRefusal('interview_schema_not_ready','面试领域资格无法核对',503)
            return 'unknown'
        return 'existing'

    async def require_non_interview(self,activity_id):
        async def read(connection):
            domain=await self._interview_domain(connection,activity_id,for_write=True)
            if domain=='interview': raise InterviewRefusal('interview_domain_conflict','此活动属于模拟面试，请使用面试工作区')
        await self._transaction(read)

    async def _interview_require_non_domain(self,connection,activity_id):
        if await self._interview_domain(connection,activity_id,for_write=True)=='interview':
            raise InterviewRefusal('interview_domain_conflict','此活动属于模拟面试')

    async def _interview_require_call(self,connection,activity,op,binding=None,tool=False):
        from app.capabilities.contracts import AdmissionDenied
        if activity is None:return
        aid=str(activity['id'])
        try:domain=await self._interview_domain(connection,aid,for_write=True)
        except InterviewRefusal as exc:raise AdmissionDenied(exc.code) from None
        if op.startswith(PREFIX) or domain=='interview':
            if domain!='interview' or tool or not op.startswith(PREFIX): raise AdmissionDenied('interview_profile_required')
            if not activity.get('_memory_eligible',True): raise AdmissionDenied('interview_memory_dependency_invalid')
            if activity.get('_memory_selected'): raise AdmissionDenied('interview_memory_not_supported')
            if binding is None: raise AdmissionDenied('interview_profile_required')

    async def _interview_lock(self,connection,aid,extra_sources=()):
        if await self._interview_schema_info(connection)!='ready': raise InterviewRefusal('interview_schema_not_ready','面试持久层未就绪',503)
        state=await self._memory_lock_prefix(connection,aid,extra_sources=extra_sources)
        if state['activity'] is None: raise InterviewRefusal('not_found','活动不存在',404)
        await self._teaching_lock_operations(connection,aid)
        cursor=await connection.execute('SELECT * FROM public.interview_heads WHERE activity_id=%s FOR UPDATE',(aid,))
        state['head']=await cursor.fetchone()
        cursor=await connection.execute('SELECT * FROM public.interview_commands WHERE activity_id=%s ORDER BY business_key FOR UPDATE',(aid,))
        state['commands']=await cursor.fetchall()
        return state

    @staticmethod
    def _interview_gate(state,action):
        a=state['activity']
        if not state['eligible']: raise InterviewRefusal('interview_memory_dependency_invalid','活动记忆资格不可核对')
        if state['selected']: raise InterviewRefusal('interview_memory_not_supported','首版面试需要未选择记忆的新活动')
        if action in ('finish','abandon'):return
        if a['status']=='cancelled': raise InterviewRefusal('cancelled','活动已取消')
        if a['status'] not in ('pending','running') or a['deadline_at']<=datetime.now(timezone.utc): raise InterviewRefusal('activity_expired','活动已过期')
        if action!='bind_scope' and not state['sources_valid']: raise InterviewRefusal('source_invalid','资料已更新，请明确确认新的范围')

    @staticmethod
    def _interview_cas(state,command):
        h=state['head'];a=state['activity']
        if (h['revision'] if h else 0)!=command.expected_head_revision: raise InterviewRefusal('interview_head_conflict')
        if (h['goal_version'] if h else 0)!=command.expected_goal_version: raise InterviewRefusal('interview_goal_conflict')
        if a['scope_revision']!=command.expected_scope_revision: raise InterviewRefusal('interview_scope_conflict')

    @staticmethod
    def _interview_slot(aid,command):
        body=command.body
        return sha(canonical(dict(activity_id=aid,action=command.action,expected_head_revision=command.expected_head_revision,
            goal_version=command.expected_goal_version,scope_revision=command.expected_scope_revision,
            question_record_id=body.get('question_record_id'),answer_record_id=body.get('answer_record_id'),
            target_record_id=body.get('answer_record_id') or body.get('pending_key') or body.get('parent_feedback_id'))))

    async def _interview_insert_command(self,connection,aid,command,slot,kind,frozen=None,duplicate=None):
        cursor=await connection.execute('SELECT count(*) AS n FROM public.interview_commands WHERE activity_id=%s',(aid,))
        if (await cursor.fetchone())['n']>=MAX_COMMANDS:raise InterviewRefusal('interview_record_limit','本场次记录已达上限')
        context=canonical(frozen.model_dump()) if frozen is not None else None
        await connection.execute("""INSERT INTO public.interview_commands(activity_id,business_key,action,request_body,request_sha256,semantic_slot,
          execution_kind,context_body,context_sha256,operation_id,status,duplicate_of,retry_of,before_revision,goal_version,scope_revision)
          VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(aid,command.business_key,command.action,
          command.request_body(aid),command.request_hash(aid),slot,kind,context,sha(context) if context else None,
          operation_id(command.business_key) if kind=='model' and not duplicate else None,
          'committed' if duplicate else 'accepted',duplicate,command.body.get('retry_of'),command.expected_head_revision,
          command.expected_goal_version,command.expected_scope_revision))

    async def _interview_replay(self,connection,state,aid,command):
        slot=self._interview_slot(aid,command); request=command.request_body(aid)
        for c in state['commands']:
            if str(c['business_key'])==command.business_key:
                if c['request_body']!=request or c['request_sha256']!=command.request_hash(aid): raise InterviewRefusal('interview_key_conflict')
                return c
        winner=next((c for c in state['commands'] if c['semantic_slot']==slot and c['duplicate_of'] is None
            and c['status'] in ('accepted','started','unknown','committed','history')),None)
        if winner:
            if winner['request_body']!=request or winner['request_sha256']!=command.request_hash(aid):raise InterviewRefusal('interview_slot_conflict')
            await self._interview_insert_command(connection,aid,command,slot,winner['execution_kind'],duplicate=str(winner['business_key']))
            return dict(winner, business_key=UUID(command.business_key),duplicate_of=winner['business_key'],effect_applied=False)
        return None

    async def _interview_record(self,connection,aid,rid):
        cursor=await connection.execute('SELECT * FROM public.interview_records WHERE activity_id=%s AND record_id=%s',(aid,rid))
        return await cursor.fetchone()

    async def _interview_obsolete(self,connection,aid, *, ancestor=None):
        if ancestor is None:
            await connection.execute("UPDATE public.interview_commands SET obsolete=true,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND action IN ('ask','review') AND duplicate_of IS NULL AND NOT obsolete",(aid,))
        else:
            await connection.execute("""WITH RECURSIVE descendants(id) AS (SELECT %s::uuid UNION
              SELECT r.record_id FROM public.interview_records r JOIN descendants d ON d.id=ANY(r.parent_ids) WHERE r.activity_id=%s)
              UPDATE public.interview_commands c SET obsolete=true,updated_at=CURRENT_TIMESTAMP WHERE c.activity_id=%s AND NOT c.obsolete
              AND (c.business_key IN (SELECT r.business_key FROM public.interview_records r JOIN descendants d ON d.id=r.record_id WHERE r.activity_id=%s AND r.kind IN ('question','probe','feedback'))
                OR (c.execution_kind='model' AND c.status IN ('accepted','started','unknown') AND c.context_body::jsonb->'parent_record_refs' @> jsonb_build_array(jsonb_build_object('record_id',%s::text))))""",
              (ancestor,aid,aid,aid,ancestor))

    async def _interview_insert_record(self,connection,aid,key,head,kind,value,sources,*,parents=(),question=None,
                                       answer_version=None,supersedes=None,origin=None,model=None,ordinal=0):
        cursor=await connection.execute('SELECT COALESCE(max(seq),0) AS n FROM public.interview_records WHERE activity_id=%s',(aid,))
        seq=(await cursor.fetchone())['n']+1
        if seq>MAX_RECORDS:raise InterviewRefusal('interview_record_limit','本场次记录已达上限')
        rid=str(uuid4());origin=origin or ('user' if kind in ('goal','answer') else 'application')
        body=canonical(dict(schema='interview.local.v1',activity_id=aid,business_key=key,kind=kind,
            goal_version=head['goal_version'],scope_revision=head['scope_revision'],round_index=head['round_index'],
            probe_depth=head['probe_depth'],parent_ids=list(parents),value=value)) if model is None else None
        digest=sha(body) if body is not None else model[1]
        await connection.execute("""INSERT INTO public.interview_records(activity_id,record_id,seq,business_key,ordinal,kind,origin,
          goal_version,scope_revision,round_index,probe_depth,answer_version,parent_ids,question_record_id,supersedes_record_id,
          source_refs,body_sha256,local_body,operation_id,payload_sha256) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s)""",
          (aid,rid,seq,key,ordinal,kind,'model' if model else origin,head['goal_version'],head['scope_revision'],head['round_index'],head['probe_depth'],
           answer_version,list(parents),question,supersedes,canonical(sources),digest,body,model[0] if model else None,model[1] if model else None))
        head['last_seq']=seq
        return rid

    async def _interview_put_head(self,connection,aid,head,old_revision=None):
        fields=('revision','goal_version','phase','last_seq','round_index','probe_depth','goal_record_id','root_question_id',
                'current_question_id','current_answer_id','current_feedback_id','pending_key','scope_revision','source_snapshot_sha256')
        if old_revision is None:
            await connection.execute('INSERT INTO public.interview_heads(activity_id,'+','.join(fields)+') VALUES('+','.join(['%s']*(len(fields)+1))+')',
                (aid,*(head.get(k) for k in fields)))
        else:
            cursor=await connection.execute('UPDATE public.interview_heads SET '+','.join(k+'=%s' for k in fields)+',updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND revision=%s',
                (*(head.get(k) for k in fields),aid,old_revision))
            if cursor.rowcount!=1:raise InterviewRefusal('interview_head_conflict')

    async def _interview_commit_command(self,connection,aid,key,head,records):
        await connection.execute("""UPDATE public.interview_commands SET status='committed',effect_applied=true,after_revision=%s,
          result_record_ids=%s,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s""",(head['revision'],records,aid,key))

    async def _interview_sources(self,connection,aid):
        cursor=await connection.execute("""SELECT s.source_id::text,s.version_id::text,s.source_revision,v.sha256 AS original_sha256
          FROM public.activity_scope_sources s JOIN public.material_versions v ON v.id=s.version_id AND v.source_id=s.source_id
          WHERE s.activity_id=%s ORDER BY s.source_id""",(aid,))
        rows=await cursor.fetchall()
        if not 1<=len(rows)<=10:raise InterviewRefusal('interview_invalid_input','面试最多选择10份资料',422)
        return [SourceBinding.model_validate(r).model_dump() for r in rows]

    @staticmethod
    def _interview_roles(roles,sources):
        ids={s['source_id'] for s in sources};mapping={s['source_id']:s['role'] for s in roles}
        if any(s not in ids for s in mapping):raise InterviewRefusal('interview_invalid_input','资料用途不属于当前范围',422)
        return [{'source_id':s['source_id'],'role':mapping.get(s['source_id'],'unspecified')} for s in sources]

    async def apply_interview_local(self,aid,command, *, application_value=None):
        extra=command.body.get('sources',[]) if command.action=='bind_scope' else []
        async def write(connection):
            state=await self._interview_lock(connection,aid,extra)
            replay=await self._interview_replay(connection,state,aid,command)
            if replay:return
            self._interview_cas(state,command); self._interview_gate(state,command.action)
            transition(command.action,state['head'],command.body)
            h=plain(state['head']) if state['head'] else dict(revision=0,goal_version=0,phase='needs_goal',last_seq=0,round_index=0,probe_depth=0,
                goal_record_id=None,root_question_id=None,current_question_id=None,current_answer_id=None,current_feedback_id=None,pending_key=None,
                scope_revision=state['activity']['scope_revision'])
            old=h['revision']; sources=await self._interview_sources(connection,aid); records=[]
            if old>=MAX_REVISION:raise InterviewRefusal('interview_version_limit')
            await self._interview_insert_command(connection,aid,command,self._interview_slot(aid,command),'local')
            h['revision']=old+1; action=command.action; b=command.body
            if action=='start':
                a=state['activity']
                cursor=await connection.execute('SELECT EXISTS(SELECT 1 FROM public.teaching_heads WHERE activity_id=%s) AS found',(aid,))
                if (await cursor.fetchone())['found'] or state['commands'] or a['status']!='pending' or a['execution_generation']!=0 or a['executor_id'] is not None or a['lease_expires_at'] is not None \
                    or any(a[k] for k in ('requests_reserved','cost_reserved_microunits','tools_reserved','running_reserved_seconds','running_settled_seconds')):
                    raise InterviewRefusal('interview_domain_conflict','请新建未选择记忆的面试活动')
                if b['goal'] is not None:h['goal_version']=1;h['phase']='ready'
                records.append(await self._interview_insert_record(connection,aid,command.business_key,h,'start',{'goal_provided':b['goal'] is not None},sources))
                if b['goal'] is not None:
                    g=GoalBody.model_validate(b['goal']).model_dump();g['material_roles']=self._interview_roles(g['material_roles'],sources)
                    h['goal_record_id']=await self._interview_insert_record(connection,aid,command.business_key,h,'goal',dict(goal=g,copied_from_goal_id=None),sources,ordinal=1)
                    records.append(h['goal_record_id'])
            elif action=='goal':
                if h['goal_version']>=32:raise InterviewRefusal('interview_version_limit')
                await self._interview_obsolete(connection,aid)
                h.update(goal_version=h['goal_version']+1,phase='ready',round_index=0,probe_depth=0,root_question_id=None,current_question_id=None,current_answer_id=None,current_feedback_id=None,pending_key=None)
                g=GoalBody.model_validate(b['goal']).model_dump();g['material_roles']=self._interview_roles(g['material_roles'],sources)
                h['goal_record_id']=await self._interview_insert_record(connection,aid,command.business_key,h,'goal',dict(goal=g,copied_from_goal_id=None),sources)
                records.append(h['goal_record_id'])
            elif action in ('answer','correct_answer'):
                prior=None
                if action=='correct_answer':
                    prior=await self._interview_record(connection,aid,b['answer_record_id'])
                    if not prior or prior['kind']!='answer' or prior['goal_version']!=h['goal_version'] or prior['scope_revision']!=h['scope_revision'] or prior['answer_version']!=b['expected_answer_version']:
                        raise InterviewRefusal('interview_parent_invalid')
                    q=await self._interview_record(connection,aid,str(prior['question_record_id']))
                    if not await self._interview_record_current(connection,q):raise InterviewRefusal('interview_parent_invalid')
                    cursor=await connection.execute('SELECT max(answer_version) AS n FROM public.interview_records WHERE activity_id=%s AND question_record_id=%s',(aid,prior['question_record_id']))
                    if (await cursor.fetchone())['n']!=prior['answer_version']:raise InterviewRefusal('interview_parent_invalid')
                    if prior['answer_version']>=256:raise InterviewRefusal('interview_version_limit')
                    await self._interview_obsolete(connection,aid,ancestor=b['answer_record_id'])
                    h.update(round_index=q['round_index'],probe_depth=q['probe_depth'],current_question_id=str(q['record_id']),pending_key=None,current_feedback_id=None)
                    question=str(q['record_id']);version=prior['answer_version']+1
                    cursor=await connection.execute("SELECT record_id::text FROM public.interview_records WHERE activity_id=%s AND kind='question' AND goal_version=%s AND scope_revision=%s AND round_index=%s ORDER BY seq DESC LIMIT 1",(aid,h['goal_version'],h['scope_revision'],h['round_index']))
                    h['root_question_id']=(await cursor.fetchone())['record_id']
                else:question=b['question_record_id'];version=1
                h['current_answer_id']=await self._interview_insert_record(connection,aid,command.business_key,h,'answer',
                    dict(question_record_id=question,answer_version=version,text=b['text'],supersedes_record_id=str(prior['record_id']) if prior else None),sources,
                    parents=[question],question=question,answer_version=version,supersedes=str(prior['record_id']) if prior else None)
                records.append(h['current_answer_id']);h.update(phase='answer_ready',current_feedback_id=None)
            elif action=='bind_scope':
                from .repository import SourceSnapshot
                new=b['sources'];new_roles=self._interview_roles(b['material_roles'],new)
                oldgoal=await self._interview_record(connection,aid,h['goal_record_id']) if h['goal_record_id'] else None
                oldg=load_json(oldgoal['local_body'])['value']['goal'] if oldgoal else None
                oldroles=oldg['material_roles'] if oldg else self._interview_roles([],sources)
                if sources==new and oldroles==new_roles:
                    await connection.execute("UPDATE public.interview_commands SET status='committed',updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s",(aid,command.business_key));return
                if oldgoal and h['goal_version']>=32:raise InterviewRefusal('interview_version_limit')
                cursor=await connection.execute('SELECT id::text,current_version::text,revision FROM public.material_sources WHERE id=ANY(%s::uuid[])',([s['source_id'] for s in new],))
                locked={r['id']:r for r in await cursor.fetchall()}
                for n in new:
                    cursor=await connection.execute('SELECT sha256 FROM public.material_versions WHERE id=%s AND source_id=%s',(n['version_id'],n['source_id']))
                    actual=await cursor.fetchone()
                    if not actual or actual['sha256']!=n['original_sha256']:raise InterviewRefusal('source_invalid')
                await self._apply_scope_locked(connection,aid,state['activity'],locked,command.expected_scope_revision,
                    tuple(SourceSnapshot(n['source_id'],n['version_id'],n['source_revision']) for n in new),force_revision=True)
                h.update(scope_revision=h['scope_revision']+1,goal_version=h['goal_version']+(1 if oldgoal else 0),phase='ready' if oldgoal else 'needs_goal',round_index=0,probe_depth=0,
                    root_question_id=None,current_question_id=None,current_answer_id=None,current_feedback_id=None,pending_key=None)
                await self._interview_obsolete(connection,aid)
                scope_id=await self._interview_insert_record(connection,aid,command.business_key,h,'scope',dict(before_sources=sources,after_sources=new,before_roles=oldroles,after_roles=new_roles),new)
                records.append(scope_id);sources=new
                if oldgoal:
                    oldg['material_roles']=new_roles
                    h['goal_record_id']=await self._interview_insert_record(connection,aid,command.business_key,h,'goal',dict(goal=oldg,copied_from_goal_id=str(oldgoal['record_id'])),new,parents=[scope_id],ordinal=1)
                    records.append(h['goal_record_id'])
            elif action=='finish':
                records.append(await self._interview_insert_record(connection,aid,command.business_key,h,'finish',{'reason':'user_end'},sources));h['phase']='ended'
            elif action=='abandon':
                c=next((c for c in state['commands'] if str(c['business_key'])==b['pending_key']),None)
                if not c or c['status'] not in ('accepted','started','unknown'):raise InterviewRefusal('interview_parent_invalid')
                await connection.execute("UPDATE public.interview_commands SET status='abandoned',obsolete=true,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s",(aid,b['pending_key']))
                records.append(await self._interview_insert_record(connection,aid,command.business_key,h,'abandon',b,sources));h['pending_key']=None
            elif action in ('ask','review') and application_value is not None:
                kind=application_value['type']
                if action=='ask':h.update(round_index=h['round_index']+1,probe_depth=0,current_answer_id=None,current_feedback_id=None)
                parents=[h['goal_record_id']] if action=='ask' else [h['current_question_id'],h['current_answer_id']]
                rid=await self._interview_insert_record(connection,aid,command.business_key,h,kind,application_value,sources,parents=parents)
                records.append(rid)
                if kind=='question':h.update(root_question_id=rid,current_question_id=rid,phase='question_ready')
                else:h.update(current_feedback_id=rid,phase='feedback_ready')
            else:raise InterviewRefusal('interview_invalid_input',status=422)
            h['source_snapshot_sha256']=sha(canonical(sources))
            await self._interview_put_head(connection,aid,h,old if old else None)
            await self._interview_commit_command(connection,aid,command.business_key,h,records)
        await self._transaction(write)
        return await self.read_interview_command(aid,command.business_key)

    async def _interview_record_current(self,connection,row):
        if row is None:return False
        cursor=await connection.execute("""SELECT r.goal_version=h.goal_version AND r.scope_revision=h.scope_revision
          AND NOT c.obsolete AND (r.origin<>'model' OR public.interview_result_eligible(r.activity_id,r.operation_id)) AS valid
          FROM public.interview_records r JOIN public.interview_heads h USING(activity_id)
          JOIN public.interview_commands c ON c.activity_id=r.activity_id AND c.business_key=r.business_key
          WHERE r.activity_id=%s AND r.record_id=%s""",(str(row['activity_id']),str(row['record_id'])))
        found=await cursor.fetchone();return bool(found and found['valid'])

    @staticmethod
    def _interview_ref_body(row,document,action):
        value=document['value']
        if row['origin']=='model' and row['kind'] in ('question','probe'):
            value={k:value[k] for k in ('type','text','reason','purpose','reference_ids') if k in value}
        elif row['kind']=='feedback' and action=='ask':
            value={k:value[k] for k in ('type','summary','gaps','next_steps') if k in value}
        return {'value':value}

    async def _interview_verify_frozen(self,connection,state,command,frozen, *, check_budget=True):
        a=state['activity'];h=state['head']
        if h is None or frozen.activity_id!=str(a['id']) or frozen.business_key!=command.business_key \
            or frozen.request_sha256!=command.request_hash(str(a['id'])) or frozen.action!=command.action \
            or frozen.expected_head_revision!=h['revision'] or frozen.expected_goal_version!=h['goal_version'] \
            or frozen.expected_scope_revision!=a['scope_revision'] or frozen.round_index!=h['round_index'] or frozen.probe_depth!=h['probe_depth'] \
            or frozen.goal_record_id!=str(h['goal_record_id']):
            raise InterviewRefusal('interview_binding_invalid')
        sources=await self._interview_sources(connection,str(a['id']))
        if sources!=[s.model_dump() for s in frozen.sources] or h['source_snapshot_sha256']!=sha(canonical(sources)):
            raise InterviewRefusal('source_invalid')
        goal=await self._interview_record(connection,str(a['id']),frozen.goal_record_id)
        if goal is None or sha(goal['local_body'])!=goal['body_sha256'] or load_json(goal['local_body'])['value']['goal']!=frozen.goal_body.model_dump():
            raise InterviewRefusal('interview_binding_invalid')
        if frozen.material_roles!=frozen.goal_body.material_roles:raise InterviewRefusal('interview_binding_invalid')
        for ref in frozen.parent_record_refs:
            row=await self._interview_record(connection,str(a['id']),ref.record_id)
            if row is None or row['kind']!=ref.kind or row['body_sha256']!=ref.body_sha256 or not await self._interview_record_current(connection,row):
                raise InterviewRefusal('interview_parent_invalid')
            if row['origin']=='model':
                cursor=await connection.execute('SELECT payload FROM public.activity_operation_results WHERE activity_id=%s AND operation_id=%s',(str(a['id']),row['operation_id']))
                payload=(await cursor.fetchone())['payload']; row=dict(row,payload=payload)
                if ref.operation_id!=row['operation_id'] or ref.payload_sha256!=row['payload_sha256']:raise InterviewRefusal('interview_parent_invalid')
            else:row=dict(row,payload=row['local_body'])
            document=verified_body(row)
            if ref.body!=self._interview_ref_body(row,document,command.action):raise InterviewRefusal('interview_parent_invalid')
        if command.action=='review':
            if str(h['current_question_id'])!=command.body['question_record_id'] or str(h['current_answer_id'])!=command.body['answer_record_id']:
                raise InterviewRefusal('interview_parent_invalid')
            cursor=await connection.execute('SELECT max(answer_version) AS n FROM public.interview_records WHERE activity_id=%s AND question_record_id=%s',(str(a['id']),h['current_question_id']))
            row=await self._interview_record(connection,str(a['id']),command.body['answer_record_id'])
            if row['answer_version']!=(await cursor.fetchone())['n']:raise InterviewRefusal('interview_parent_invalid')
        for source in frozen.sources:
            cursor=await connection.execute('SELECT sha256 FROM public.material_versions WHERE id=%s AND source_id=%s',(source.version_id,source.source_id))
            row=await cursor.fetchone()
            if row is None or row['sha256']!=source.original_sha256:raise InterviewRefusal('source_invalid')
        for item in frozen.catalog:
            source=next((s for s in frozen.sources if s.source_id==item.source_id),None)
            if source is None or source.version_id!=item.version_id or source.source_revision!=item.source_revision or source.original_sha256!=item.original_sha256:
                raise InterviewRefusal('source_invalid')
        if frozen.limits.max_output_tokens>a['max_output_tokens'] or (check_budget and (a['requests_reserved']>=a['max_requests'] or a['cost_reserved_microunits']+a['reserve_cost_microunits']>a['max_cost_microunits'])):
            raise InterviewRefusal('budget_exhausted')
        cursor=await connection.execute('SELECT 1 FROM public.activity_allowed_models WHERE activity_id=%s AND provider=%s AND model=%s',
            (str(a['id']),frozen.identity.provider,frozen.identity.model))
        if await cursor.fetchone() is None:raise InterviewRefusal('interview_binding_invalid')

    async def accept_interview_command(self,aid,command,frozen):
        async def accept(connection):
            state=await self._interview_lock(connection,aid)
            replay=await self._interview_replay(connection,state,aid,command)
            if replay:return
            self._interview_cas(state,command);self._interview_gate(state,command.action)
            transition(command.action,state['head'],command.body)
            retry=command.body.get('retry_of')
            cursor=await connection.execute("SELECT EXISTS(SELECT 1 FROM public.activity_operations WHERE activity_id=%s AND state IN ('reserved','dispatched','unknown')) AS unresolved",(aid,))
            if (await cursor.fetchone())['unresolved'] or state['activity']['running_reserved_seconds'] or state['activity']['running_owner_session_id'] is not None:
                raise InterviewRefusal('window_unavailable','原执行窗口尚未证明可重新使用；不会启动第二次监督')
            if retry:
                old=next((c for c in state['commands'] if str(c['business_key'])==retry),None)
                if not old or old['status'] not in ('not_sent','failed') or old['effect_applied'] or old['action']!=command.action:
                    raise InterviewRefusal('interview_retry_forbidden')
                old_request=load_json(old['request_body'])
                if any(old_request['body'].get(k)!=command.body.get(k) for k in ('question_record_id','answer_record_id','mode','parent_feedback_id')):
                    raise InterviewRefusal('interview_retry_forbidden')
                if state['activity']['running_reserved_seconds'] or state['activity']['running_owner_session_id'] is not None:
                    raise InterviewRefusal('window_unavailable')
            elif any(c['status']=='unknown' and c['execution_kind']=='model' for c in state['commands']):
                raise InterviewRefusal('interview_pending')
            await self._interview_verify_frozen(connection,state,command,frozen)
            if state['head']['last_seq']>=MAX_RECORDS:raise InterviewRefusal('interview_record_limit')
            await self._interview_insert_command(connection,aid,command,self._interview_slot(aid,command),'model',frozen)
            await connection.execute('UPDATE public.interview_heads SET pending_key=%s,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s',
                (command.business_key,aid))
        await self._transaction(accept)
        return await self.read_interview_command(aid,command.business_key)

    async def claim_interview_launch(self,aid,key,request_sha):
        async def claim(connection):
            state=await self._interview_lock(connection,aid)
            c=next((c for c in state['commands'] if str(c['business_key'])==key),None)
            if not c or c['request_sha256']!=request_sha:raise InterviewRefusal('interview_key_conflict')
            if c['duplicate_of'] or c['status']!='accepted' or c['launch_claimed'] or c['obsolete']:return {'launch_allowed':False}
            frozen=InterviewContext.model_validate(load_json(c['context_body']))
            req=load_json(c['request_body']);req.pop('activity_id');req['business_key']=key
            command=InterviewCommandInput.model_validate(req)
            self._interview_cas(state,command);self._interview_gate(state,command.action)
            if str(state['head']['pending_key'])!=key:raise InterviewRefusal('interview_parent_invalid')
            await self._interview_verify_frozen(connection,state,command,frozen)
            await connection.execute("UPDATE public.interview_commands SET launch_claimed=true,status='started',updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s",(aid,key))
            return {'launch_allowed':True,'operation_id':c['operation_id'],'frozen':plain(frozen.model_dump())}
        return await self._transaction(claim)

    async def _locked_interview_binding(self,connection,activity,op,binding=None,stage='mark'):
        aid=str(activity['id'])
        cursor=await connection.execute('SELECT * FROM public.interview_heads WHERE activity_id=%s FOR UPDATE',(aid,));h=await cursor.fetchone()
        cursor=await connection.execute('SELECT * FROM public.interview_commands WHERE activity_id=%s ORDER BY business_key FOR UPDATE',(aid,));commands=await cursor.fetchall()
        c=next((c for c in commands if c['operation_id']==op),None)
        if h is None or c is None or c['status']!='started' or not c['launch_claimed'] or c['obsolete'] or c['duplicate_of'] or str(h['pending_key'])!=str(c['business_key']):
            raise InterviewRefusal('interview_binding_invalid')
        frozen=InterviewContext.model_validate(load_json(c['context_body']))
        if sha(c['context_body'])!=c['context_sha256'] or sha(c['request_body'])!=c['request_sha256']:
            raise InterviewRefusal('interview_binding_invalid')
        expected=InterviewCallBinding(business_key=str(c['business_key']),request_sha256=c['request_sha256'],context_sha256=c['context_sha256'],
            expected_head_revision=c['before_revision'],goal_version=c['goal_version'])
        if binding is not None and binding!=expected:raise InterviewRefusal('interview_binding_invalid')
        state={'activity':activity,'head':h,'commands':commands,'eligible':activity.get('_memory_eligible',True),'selected':activity.get('_memory_selected',False),'sources_valid':True}
        req=load_json(c['request_body']);req.pop('activity_id');req['business_key']=str(c['business_key'])
        command=InterviewCommandInput.model_validate(req)
        self._interview_cas(state,command);self._interview_gate(state,command.action)
        # Admit checks remaining allowance; mark/result verify the already-reserved call
        # without pretending that the last legitimately admitted call is over budget.
        await self._interview_verify_frozen(connection,state,command,frozen,check_budget=(stage=='admit'))
        return h,c,frozen

    async def validate_interview_request(self,context,profile,frozen):
        async def validate(connection):
            state=await self._interview_lock(connection,context.activity_id)
            c=next((c for c in state['commands'] if str(c['business_key'])==profile.business_key),None)
            if not c:raise InterviewRefusal('interview_binding_invalid')
            h,c,current=await self._locked_interview_binding(connection,state['activity'],context.operation_id,
                InterviewCallBinding(business_key=profile.business_key,request_sha256=profile.request_sha256,context_sha256=profile.context_sha256,
                    expected_head_revision=profile.expected_head_revision,goal_version=profile.goal_version),'admit')
            if profile_for(current)!=profile or current!=frozen:raise InterviewRefusal('interview_binding_invalid')
        await self._transaction(validate)

    async def _write_interview_outcome(self,connection,activity,call,outcome,payload):
        aid=str(activity['id']);op=call['operation_id']
        cursor=await connection.execute('SELECT * FROM public.interview_heads WHERE activity_id=%s FOR UPDATE',(aid,));h=await cursor.fetchone()
        cursor=await connection.execute('SELECT * FROM public.interview_commands WHERE activity_id=%s AND operation_id=%s FOR UPDATE',(aid,op));c=await cursor.fetchone()
        if not h or not c:raise InterviewRefusal('interview_binding_invalid')
        if payload is None:
            if c['status'] in ('abandoned','committed','history'):return
            status={'not_sent':'not_sent','unknown':'unknown'}.get(outcome.disposition.value,'failed')
            await connection.execute('UPDATE public.interview_commands SET status=%s,error_code=%s,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s',
                (status,outcome.error_code,aid,c['business_key']))
            if status!='unknown' and str(h['pending_key'] or '')==str(c['business_key']):
                await connection.execute('UPDATE public.interview_heads SET pending_key=NULL,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s',(aid,))
            return
        h,c,frozen=await self._locked_interview_binding(connection,activity,op,None,'result')
        document=load_json(payload[1])
        stored=document.get('value',{})
        if document.get('format')!='json' or stored.get('profile')!='interview.v1' or stored.get('context_sha256')!=c['context_sha256'] or stored.get('request_sha256')!=c['request_sha256']:
            raise InterviewRefusal('interview_binding_invalid')
        value=stored['value'];kind=value['type']; head=plain(h);old=head['revision'];head['revision']=old+1;head['pending_key']=None
        if c['action']=='ask':
            if kind!='question':raise InterviewRefusal('interview_binding_invalid')
            head.update(round_index=head['round_index']+1,probe_depth=0,current_answer_id=None,current_feedback_id=None)
            parents=[str(h['goal_record_id'])]
            req=load_json(c['request_body'])
            if req['body'].get('parent_feedback_id'):parents.append(req['body']['parent_feedback_id'])
        else:
            if kind not in ('probe','feedback'):raise InterviewRefusal('interview_binding_invalid')
            parents=[str(h['current_question_id']),str(h['current_answer_id'])]
            if kind=='probe':head['probe_depth']+=1
        rid=await self._interview_insert_record(connection,aid,str(c['business_key']),head,kind,None,
            [s.model_dump() for s in frozen.sources],parents=parents,model=(op,payload[2]))
        if kind=='question':head.update(root_question_id=rid,current_question_id=rid,phase='question_ready')
        elif kind=='probe':head.update(current_question_id=rid,current_answer_id=None,current_feedback_id=None,phase='question_ready')
        else:head.update(current_feedback_id=rid,phase='feedback_ready')
        await self._interview_put_head(connection,aid,head,old)
        await self._interview_commit_command(connection,aid,str(c['business_key']),head,[rid])

    async def _interview_confirm_integrity(self,connection,call,payload):
        if payload is None:return
        cursor=await connection.execute("""SELECT c.effect_applied,c.status,ir.payload_sha256,ir.body_sha256 FROM public.interview_commands c
          LEFT JOIN public.interview_records ir ON ir.activity_id=c.activity_id AND ir.business_key=c.business_key AND ir.origin='model'
          WHERE c.activity_id=%s AND c.operation_id=%s""",(str(call['activity_id']),call['operation_id']))
        row=await cursor.fetchone()
        if not row or not row['effect_applied'] or row['status'] not in ('committed','history') or row['payload_sha256']!=payload[2] or row['body_sha256']!=payload[2]:
            raise InterviewRefusal('interview_binding_invalid','严格终态缺少领域引用；不会补写')

    async def finish_interview_supervision(self,aid,key,facts):
        # A new-domain result rejected after mark must retain a native UNKNOWN
        # diagnostic too. Use the existing admission permit and record_outcome;
        # never relabel it not_sent, release cost, or manufacture a stop proof.
        async def unresolved(connection):
            state=await self._interview_lock(connection,aid)
            c=next((c for c in state['commands'] if str(c['business_key'])==key),None)
            if c is None or c['status'] in ('committed','history'):return None
            cursor=await connection.execute("SELECT admission_id::text,operation_id,executor_id,state FROM public.activity_operations WHERE activity_id=%s AND operation_id=%s",(aid,c['operation_id']))
            row=await cursor.fetchone()
            return row if row and row['state'] in ('reserved','dispatched') else None
        pending_native=await self._transaction(unresolved)
        if pending_native is not None:
            from app.capabilities.contracts import AdmissionPermit,LedgerOutcome,LedgerDisposition,AdmissionDenied,AdmissionUnavailable
            permit=AdmissionPermit(pending_native['admission_id'],pending_native['operation_id'],pending_native['executor_id'])
            try:
                await self.record_outcome(permit,LedgerOutcome(LedgerDisposition.UNKNOWN,error_code='supervision_unknown'))
            except (AdmissionDenied,AdmissionUnavailable,InterviewRefusal):
                pass  # Domain remains unconfirmed; native reserve is never refunded.
        async def finish(connection):
            state=await self._interview_lock(connection,aid)
            c=next((c for c in state['commands'] if str(c['business_key'])==key),None)
            if not c or c['status'] in ('committed','history','abandoned','failed','not_sent','unknown'):return
            cursor=await connection.execute('SELECT state,disposition,error_code FROM public.activity_operations WHERE activity_id=%s AND operation_id=%s',(aid,c['operation_id']))
            row=await cursor.fetchone()
            certain=bool(facts.get('definitely_not_admitted')) and row is None
            status='not_sent' if certain else 'unknown'
            await connection.execute('UPDATE public.interview_commands SET status=%s,error_code=%s,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s',
                (status,'launch_not_started' if certain else 'supervision_unknown',aid,key))
            if certain and str(state['head']['pending_key'] or '')==key:
                await connection.execute('UPDATE public.interview_heads SET pending_key=NULL,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s',(aid,))
        await self._transaction(finish)
        return await self.read_interview_command(aid,key)

    async def _interview_result_sql(self,connection,sql):
        if '/*interview*/' not in sql:return sql
        schema=await self._interview_schema_info(connection)
        marker="(left(o.operation_id,7)='int10m.')"
        if 'THEN r.payload' in sql:
            marker="(left(o.operation_id,7)='int10m.' OR COALESCE(CASE WHEN r.payload_format='json' THEN r.payload::jsonb->'value'->>'profile'='interview.v1' ELSE false END,false))"
        guard=f'(NOT {marker} OR public.interview_result_eligible(o.activity_id,o.operation_id))' if schema=='ready' else f'(NOT {marker})' if schema=='absent' else 'FALSE'
        return sql.replace('/*interview*/TRUE',guard)

    async def _interview_snapshot(self,connection,aid, *, key=None,rid=None,limit=20,before=None,details=False):
        if await self._interview_schema_info(connection)!='ready':raise InterviewRefusal('interview_schema_not_ready','面试持久层未就绪',503)
        memory=await self._memory_sql_guard(connection,'a.id');selected=await self._memory_selected_sql(connection,'a.id')
        # Body columns exist only in the explicitly requested single-record branch.
        meta="""ir.record_id,ir.seq,ir.business_key,ir.ordinal,ir.kind,ir.origin,ir.goal_version,ir.scope_revision,
          ir.round_index,ir.probe_depth,ir.answer_version,ir.parent_ids,ir.question_record_id,ir.supersedes_record_id,
          ir.source_refs,ir.body_sha256,ir.operation_id,ir.payload_sha256,ir.created_at"""
        base=f"(ir.goal_version=h.goal_version AND ir.scope_revision=a.scope_revision AND a.status<>'cancelled' AND sg.valid AND ({memory}) AND NOT ({selected}) AND NOT c.obsolete)"
        eligible=f"(CASE WHEN ir.origin='model' THEN {base} AND public.interview_result_eligible(ir.activity_id,ir.operation_id) WHEN ir.kind IN ('question','probe','feedback') THEN {base} ELSE true END)"
        bodycol=f",CASE WHEN {eligible} THEN CASE WHEN ir.origin='model' THEN rr.payload ELSE ir.local_body END ELSE NULL END AS payload" if details else ''
        joins='LEFT JOIN public.activity_operation_results rr ON rr.activity_id=ir.activity_id AND rr.operation_id=ir.operation_id' if details else ''
        if rid:
            filter_sql='ir.record_id=%s::uuid';filter_params=[rid]
        else:
            filter_sql='ir.seq<%s';filter_params=[before if before is not None else MAX_RECORDS+1]
        command_meta="""c.activity_id,c.business_key,c.action,c.request_sha256,c.execution_kind,c.operation_id,c.status,
          c.launch_claimed,c.obsolete,c.effect_applied,c.duplicate_of,c.retry_of,c.before_revision,c.after_revision,
          c.goal_version,c.scope_revision,c.result_record_ids,c.error_code,c.created_at,c.updated_at"""
        sql=f"""WITH a AS (SELECT * FROM public.activities WHERE id=%s),
          h AS (SELECT * FROM public.interview_heads WHERE activity_id=%s),
          sg AS (SELECT EXISTS(SELECT 1 FROM public.activity_scope_sources s WHERE s.activity_id=%s)
            AND NOT EXISTS(SELECT 1 FROM public.activity_scope_sources s LEFT JOIN public.material_sources m ON m.id=s.source_id
              WHERE s.activity_id=%s AND (m.id IS NULL OR m.current_version IS DISTINCT FROM s.version_id OR m.revision<>s.source_revision)) AS valid),
          rs AS (SELECT {meta},{eligible} AS eligible{bodycol} FROM public.interview_records ir
            JOIN public.interview_commands c ON c.activity_id=ir.activity_id AND c.business_key=ir.business_key
            CROSS JOIN a CROSS JOIN h CROSS JOIN sg {joins} WHERE ir.activity_id=a.id AND {filter_sql} ORDER BY ir.seq DESC LIMIT %s),
          current_meta AS (SELECT {meta},{eligible} AS eligible FROM public.interview_records ir
            JOIN public.interview_commands c ON c.activity_id=ir.activity_id AND c.business_key=ir.business_key
            CROSS JOIN a CROSS JOIN h CROSS JOIN sg WHERE ir.activity_id=a.id AND ir.record_id=ANY(ARRAY[h.goal_record_id,h.root_question_id,h.current_question_id,h.current_answer_id,h.current_feedback_id]) ORDER BY ir.seq),
          pending AS (SELECT {command_meta} FROM public.interview_commands c JOIN h ON h.activity_id=c.activity_id AND h.pending_key=c.business_key),
          cmd AS (SELECT {command_meta} FROM public.interview_commands c WHERE c.activity_id=%s AND c.business_key=%s::uuid),
          original AS (SELECT {command_meta} FROM public.interview_commands c WHERE c.activity_id=%s AND c.business_key=(SELECT duplicate_of FROM cmd)),
          effect_record AS (SELECT ir.goal_version,ir.scope_revision FROM public.interview_records ir
            WHERE ir.activity_id=%s AND ir.record_id=ANY(COALESCE((SELECT result_record_ids FROM original),(SELECT result_record_ids FROM cmd))) ORDER BY ir.seq DESC LIMIT 1)
          SELECT to_jsonb(a) AS activity,(SELECT to_jsonb(h) FROM h) AS head,(SELECT valid FROM sg) AS sources_valid,
            ({memory}) AS memory_eligible,({selected}) AS memory_selected,
            COALESCE((SELECT jsonb_agg(x ORDER BY x->>'source_id') FROM (SELECT jsonb_build_object('source_id',s.source_id::text,
              'version_id',s.version_id::text,'source_revision',s.source_revision,'original_sha256',v.sha256,'title',v.filename,'format',v.format,
              'valid',m.current_version=s.version_id AND m.revision=s.source_revision) AS x FROM public.activity_scope_sources s
              LEFT JOIN public.material_sources m ON m.id=s.source_id LEFT JOIN public.material_versions v ON v.id=s.version_id AND v.source_id=s.source_id WHERE s.activity_id=a.id ORDER BY s.source_id LIMIT 11) src),'[]'::jsonb) AS sources,
            COALESCE((SELECT jsonb_agg(to_jsonb(rs) ORDER BY seq DESC) FROM rs),'[]'::jsonb) AS records,
            COALESCE((SELECT jsonb_agg(to_jsonb(current_meta) ORDER BY seq) FROM current_meta),'[]'::jsonb) AS current_records,
            (SELECT to_jsonb(pending) FROM pending) AS pending,
            (SELECT to_jsonb(cmd) FROM cmd) AS command,(SELECT to_jsonb(original) FROM original) AS original,
            (SELECT to_jsonb(effect_record) FROM effect_record) AS effect_record,
            EXISTS(SELECT 1 FROM public.teaching_heads WHERE activity_id=a.id) OR EXISTS(SELECT 1 FROM public.activity_operations WHERE activity_id=a.id) AS other_started
          FROM a"""
        params=[aid,aid,aid,aid,*filter_params,limit,aid,key,aid,aid]
        cursor=await connection.execute(sql,params);row=await cursor.fetchone()
        if row is None:raise InterviewRefusal('not_found','活动不存在',404)
        return plain(row)

    @staticmethod
    def _interview_view(snapshot):
        a=snapshot['activity'];h=snapshot['head'];current=snapshot['current_records']
        budget={k:a[k] for k in ('max_requests','requests_reserved','max_cost_microunits','cost_reserved_microunits','reserve_cost_microunits',
            'max_running_seconds','running_reserved_seconds','running_settled_seconds','max_tool_calls','tools_reserved','deadline_at','status')}
        fresh=(h is None and not snapshot['other_started'] and a['status']=='pending' and a['execution_generation']==0)
        safe=snapshot['memory_eligible'] and not snapshot['memory_selected'] and snapshot['sources_valid']
        reason='interview_memory_not_supported' if snapshot['memory_selected'] else 'interview_memory_dependency_invalid' if not snapshot['memory_eligible'] else 'source_invalid' if not snapshot['sources_valid'] else None
        view=dict(schema='interview.view.v1',activity_id=a['id'],domain='interview' if h else 'none' if fresh else 'existing',head=h,
            sources=snapshot['sources'],budget=budget,pending=snapshot['pending'],records=current,
            memory={'selected':snapshot['memory_selected'],'eligible':snapshot['memory_eligible'],'supported':False},
            qualification='current' if safe else 'invalid',suppression_reason=reason,
            capabilities={'local':True,'model':False,'model_reason':'interview_not_configured'})
        view['view_token']=token(dict(head=h,sources=view['sources'],memory=view['memory'],pending=view['pending'],budget=budget,
            qualifications=[(r['record_id'],r['eligible']) for r in current]))
        return view

    async def read_interview_workspace(self,aid):
        async def read(connection):return self._interview_view(await self._interview_snapshot(connection,aid,limit=1))
        view=await self._transaction(read);bounded_wire(view,131072);return view

    async def read_interview_command(self,aid,key):
        async def read(connection):
            snapshot=await self._interview_snapshot(connection,aid,key=key,limit=1)
            c=snapshot['command']
            if c is None:return None
            original=snapshot['original'] if c['duplicate_of'] else c
            if original is None:raise InterviewRefusal('interview_binding_invalid')
            view=self._interview_view(snapshot)
            effect=snapshot['effect_record'] or {}
            return dict(schema='interview.receipt.v1',activity_id=aid,business_key=key,request_sha256=c['request_sha256'],action=c['action'],
                status=original['status'],execution_kind=original['execution_kind'],operation_id=original['operation_id'],duplicate_of=c['duplicate_of'],
                retry_of=c['retry_of'],effect_applied=c['effect_applied'] if not c['duplicate_of'] else False,
                before_revision=c['before_revision'],after_revision=original['after_revision'],goal_version=effect.get('goal_version',original['goal_version']),
                scope_revision=effect.get('scope_revision',original['scope_revision']),record_ids=original['result_record_ids'],
                qualification='history' if original['obsolete'] or effect.get('goal_version',original['goal_version'])!=(snapshot['head'] or {}).get('goal_version') else view['qualification'],
                suppression_reason='obsolete' if original['obsolete'] else view['suppression_reason'],error_code=original['error_code'],
                view_token=view['view_token'],launch_claimed=original['launch_claimed'])
        result=await self._transaction(read)
        if result is not None:bounded_wire(result,65536)
        return result

    async def read_interview_frozen_command(self,aid,key,request_body):
        # Internal recovery of the exact accepted intent, not a public body getter.
        async def read(connection):
            state=await self._interview_lock(connection,aid)
            c=next((c for c in state['commands'] if str(c['business_key'])==key),None)
            if c is None:return None
            if c['request_body']!=request_body or c['request_sha256']!=sha(request_body):raise InterviewRefusal('interview_key_conflict')
            if c['status']=='accepted' and not c['launch_claimed'] and not c['obsolete'] and c['duplicate_of'] is None:
                return InterviewContext.model_validate(load_json(c['context_body'])) if c['context_body'] else None
            return False
        return await self._transaction(read)

    async def lookup_interview_replay(self,aid,command):
        async def lookup(connection):
            state=await self._interview_lock(connection,aid)
            return await self._interview_replay(connection,state,aid,command) is not None
        found=await self._transaction(lookup)
        return await self.read_interview_command(aid,command.business_key) if found else None

    async def read_interview_identity(self,aid):
        async def read(connection):
            cursor=await connection.execute('SELECT provider,model FROM public.activity_allowed_models WHERE activity_id=%s ORDER BY provider,model LIMIT 1',(aid,))
            row=await cursor.fetchone()
            if row is None:raise InterviewRefusal('interview_binding_invalid')
            return dict(row)
        return await self._transaction(read)

    async def read_interview_round_refs(self,aid,view_token):
        async def read(connection):
            snapshot=await self._interview_snapshot(connection,aid,limit=1)
            view=self._interview_view(snapshot)
            if view['view_token']!=view_token:raise InterviewRefusal('interview_view_changed')
            h=snapshot['head']
            cursor=await connection.execute("""SELECT r.record_id::text,r.kind,r.seq,r.answer_version,r.question_record_id::text
              FROM public.interview_records r JOIN public.interview_commands c ON c.activity_id=r.activity_id AND c.business_key=r.business_key
              WHERE r.activity_id=%s AND r.goal_version=%s AND r.scope_revision=%s AND r.round_index=%s
              AND r.kind IN ('question','probe','answer') AND NOT c.obsolete
              AND (r.origin<>'model' OR public.interview_result_eligible(r.activity_id,r.operation_id))
              AND (r.kind<>'answer' OR r.answer_version=(SELECT max(a.answer_version) FROM public.interview_records a
                WHERE a.activity_id=r.activity_id AND a.question_record_id=r.question_record_id)) ORDER BY r.seq LIMIT 13""",
              (aid,h['goal_version'],h['scope_revision'],h['round_index']))
            rows=await cursor.fetchall()
            if len(rows)>12:raise InterviewRefusal('interview_context_too_large',status=422)
            return plain(rows)
        return await self._transaction(read)

    async def read_interview_history(self,aid,limit=20,before_seq=None,view_token=None):
        if type(limit) is not int or not 1<=limit<=50 or (before_seq is not None and (type(before_seq) is not int or not 1<=before_seq<=4097)):
            raise InterviewRefusal('interview_invalid_input',status=422)
        async def read(connection):
            snapshot=await self._interview_snapshot(connection,aid,limit=limit,before=before_seq)
            view=self._interview_view(snapshot)
            if view_token and view_token!=view['view_token']:raise InterviewRefusal('interview_view_changed')
            records=snapshot['records']
            return dict(schema='interview.history.v1',activity_id=aid,records=records,view_token=view['view_token'],last_seq=(snapshot['head'] or {}).get('last_seq',0),
                next_before_seq=min((r['seq'] for r in records),default=None) if len(records)==limit else None)
        result=await self._transaction(read);bounded_wire(result,65536);return result

    async def read_interview_record(self,aid,rid,view_token=None):
        async def read(connection):
            snapshot=await self._interview_snapshot(connection,aid,rid=rid,limit=1,details=True)
            view=self._interview_view(snapshot)
            if view_token and view_token!=view['view_token']:raise InterviewRefusal('interview_view_changed')
            if not snapshot['records']:raise InterviewRefusal('not_found','记录不存在',404)
            row=snapshot['records'][0];document=verified_body(row)
            meta={k:v for k,v in row.items() if k!='payload'}
            return dict(schema='interview.record.v1',activity_id=aid,record=meta,body=document,
                qualification='current' if row['eligible'] else 'history_suppressed',suppression_reason=None if row['eligible'] else 'source_goal_answer_or_cancel_invalid',view_token=view['view_token'])
        result=await self._transaction(read);bounded_wire(result,65536);return result
