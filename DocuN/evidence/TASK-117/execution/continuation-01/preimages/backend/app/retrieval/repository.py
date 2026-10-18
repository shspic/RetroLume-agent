"""检索的持久意图、独立Embedding凭证及原子向量事实。网络只在事务外。"""
from __future__ import annotations
from datetime import datetime, timezone
import json
import re
from uuid import UUID, uuid4
from .contracts import canonical, digest, fused_rank, RetrievalRef, RetrievalRefusal
from app.capabilities.contracts import AdmissionDenied, AdmissionPermit, LedgerDisposition, RecordOutcome
from app.capabilities.embedding import (EmbeddingAdmissionIntent, EmbeddingAdmissionPermit, EmbeddingLedgerOutcome,
                                      OutboundGrant, validate_stored_value, vector_digest)

ROSTER=('01800000-0000-4000-8000-000000000001','01800000-0000-4000-8000-000000000002','01800000-0000-4000-8000-000000000003')


def plain(value):
    if isinstance(value,dict):return {k:plain(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [plain(v) for v in value]
    if isinstance(value,UUID):return str(value)
    if isinstance(value,datetime):return value.isoformat()
    return value


def operation_ids(row):
    prefix='emb18i.' if row['action']=='source_index' else 'emb18q.'
    return [prefix+str(row['business_key'])+'.'+str(i) for i in range(row['batch_count'])]


class RetrievalLedgerMethods:
    async def retrieval_context(self,activity_id):
        async def operation(connection):
            state=await self._memory_lock_prefix(connection,activity_id);activity=state['activity']
            if activity is None:raise RetrievalRefusal('not_found',404)
            domain,revision,parents=await self._retrieval_domain_locked(connection,activity)
            return {'domain':domain,'domain_revision':revision,'parent_refs':parents,
                    'memory_selection_sha256':activity.get('_memory_selection_sha256'),
                    'memory_dependency_sha256':activity.get('_memory_dependency_sha256'),
                    'current':bool(state['sources_valid'] and state['eligible'] and activity['status']!='cancelled'),
                    'scope_revision':activity['scope_revision']}
        return await self._transaction(operation)

    async def _outbound_lock(self,connection,activity_id,grant,provider,model,request_bytes,output_tokens):
        """全许可固定锁先于source锁；不同grant或provider不能另起费用账。"""
        if grant is None:return
        grant=OutboundGrant.from_wire(grant)
        grant.check(activity_id,provider,model,request_bytes,output_tokens)
        await connection.execute("SELECT pg_advisory_xact_lock(hashtextextended('retrolume.outbound-roster.v1',0))")
        cursor=await connection.execute('SELECT outbound_grant_sha256,reserve_cost_microunits FROM activities WHERE id=%s',(activity_id,))
        row=await cursor.fetchone()
        if row is None or row['outbound_grant_sha256']!=grant.sha256 or row['reserve_cost_microunits']!=250000:
            raise AdmissionDenied('outbound_grant_binding_invalid')
        cursor=await connection.execute('SELECT COALESCE(sum(requests_reserved),0) AS requests,COALESCE(sum(cost_reserved_microunits),0) AS cost FROM activities WHERE id=ANY(%s::uuid[])',(list(ROSTER),))
        used=await cursor.fetchone()
        if used['requests']>=80 or used['cost']+250000>20000000:raise AdmissionDenied('outbound_grant_exhausted')

    async def _retrieval_domain_locked(self,connection,activity):
        """沿现有活动→operations→head锁序，禁止在多个域之间挪用资格。"""
        aid=str(activity['id'])
        await self._teaching_lock_operations(connection,aid)
        cursor=await connection.execute('SELECT * FROM interview_heads WHERE activity_id=%s FOR UPDATE',(aid,))
        interview=await cursor.fetchone()
        cursor=await connection.execute('SELECT * FROM teaching_heads WHERE activity_id=%s FOR UPDATE',(aid,))
        teaching=await cursor.fetchone()
        if interview and teaching:raise RetrievalRefusal('domain_conflict')
        head=interview or teaching
        refs=[]
        if head:
            table='interview_records' if interview else 'teaching_records'
            names=('goal_record_id','current_question_id','current_answer_id','current_feedback_id') if interview else ('goal_record_id','path_record_id','exercise_record_id','answer_record_id','feedback_record_id','reason_record_id')
            ids=sorted({str(head[x]) for x in names if head.get(x)})
            if ids:
                cursor=await connection.execute('SELECT record_id,body_sha256 FROM '+table+' WHERE activity_id=%s AND record_id=ANY(%s::uuid[]) ORDER BY record_id',(aid,ids))
                refs=[{'record_id':str(r['record_id']),'body_sha256':r['body_sha256']} for r in await cursor.fetchall()]
                if len(refs)!=len(ids):raise RetrievalRefusal('domain_parent_invalid')
        return ('interview' if interview else 'learning'),0 if head is None else head['revision'],refs

    async def _retrieval_current_locked(self,connection,activity,row,valid):
        if (activity is None or not valid or not activity.get('_memory_eligible',True)
            or activity['status']=='cancelled' or activity['scope_revision']!=row['scope_revision']
            or activity['deadline_at']<=datetime.now(timezone.utc) or row['request_body'] is None):return False
        domain,revision,parents=await self._retrieval_domain_locked(connection,activity)
        if domain=='interview':
            cursor=await connection.execute("SELECT phase='ended' AS ended FROM interview_heads WHERE activity_id=%s",(activity['id'],))
            if (await cursor.fetchone())['ended']:return False
        body=json.loads(row['request_body'])
        return (domain==row['domain'] and revision==row['domain_revision'] and parents==row['parent_refs']
                and body.get('memory_selection_sha256')==activity.get('_memory_selection_sha256')
                and body.get('memory_dependency_sha256')==activity.get('_memory_dependency_sha256'))

    async def retrieval_freeze(self,activity_id,command,body,space,manifest,batches,source_refs,query_sha):
        from psycopg.types.json import Jsonb
        request_body=canonical(body);request_sha=digest(body)
        if len(request_body.encode('utf-8'))>65536:raise RetrievalRefusal('retrieval_context_limit',413)
        async def operation(connection):
            state=await self._memory_lock_prefix(connection,activity_id)
            activity=state['activity']
            if activity is None:raise RetrievalRefusal('not_found',404)
            domain,revision,parents=await self._retrieval_domain_locked(connection,activity)
            cursor=await connection.execute('SELECT * FROM retrieval_commands WHERE activity_id=%s AND business_key=%s FOR UPDATE',(activity_id,command.business_key))
            old=await cursor.fetchone()
            if old:
                if old['request_sha256']!=request_sha or old['request_body']!=request_body:raise RetrievalRefusal('retrieval_key_conflict')
                return plain(old),False
            if (not state['sources_valid'] or not state['eligible'] or activity['status']=='cancelled'
                or activity['deadline_at']<=datetime.now(timezone.utc) or activity['scope_revision']!=command.expected_scope_revision
                or revision!=command.expected_domain_revision or body['domain']!=domain or body['parent_refs']!=parents
                or body.get('memory_selection_sha256')!=activity.get('_memory_selection_sha256')
                or body.get('memory_dependency_sha256')!=activity.get('_memory_dependency_sha256')):raise RetrievalRefusal('retrieval_invalidated')
            if plain(state['snapshots'])!=[{'source_id':x['source_id'],'version_id':x['source_version_id'],'source_revision':x['source_revision']} for x in source_refs]:
                raise RetrievalRefusal('retrieval_source_invalid')
            await connection.execute("INSERT INTO retrieval_spaces(space_id,provider,configured_model,dimensions,normalization,chunk_recipe) VALUES(%s,%s,%s,512,'l2.v1','lossless-line-2048cp.v1') ON CONFLICT(space_id) DO NOTHING",(space['space_id'],space['provider'],space['configured_model']))
            cache=batches==0
            cursor=await connection.execute('''INSERT INTO retrieval_commands(activity_id,business_key,action,space_id,scope_revision,domain,domain_revision,request_body,request_sha256,source_refs,parent_refs,query_sha256,manifest_sha256,batch_count,status,terminal_disposition,result_sha256)
              VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *''',
                (activity_id,command.business_key,command.action,space['space_id'],command.expected_scope_revision,domain,revision,request_body,request_sha,
                 Jsonb(source_refs),Jsonb(parents),query_sha,digest(manifest),batches,'terminal' if cache else 'accepted','cache_ready' if cache else None,
                 digest({'manifest_sha256':digest(manifest),'space_id':space['space_id']}) if cache else None))
            return plain(await cursor.fetchone()),True
        return await self._transaction(operation)

    async def retrieval_claim(self,activity_id,key,request_sha):
        async def operation(connection):
            state=await self._memory_lock_prefix(connection,activity_id);activity=state['activity']
            if activity is None:return False
            await self._retrieval_domain_locked(connection,activity)
            cursor=await connection.execute('SELECT * FROM retrieval_commands WHERE activity_id=%s AND business_key=%s FOR UPDATE',(activity_id,key))
            row=await cursor.fetchone()
            if row is None or row['status']!='accepted' or row['request_sha256']!=request_sha:return False
            if not await self._retrieval_current_locked(connection,activity,row,state['sources_valid']):raise RetrievalRefusal('retrieval_invalidated')
            await connection.execute("UPDATE retrieval_commands SET status='launch_claimed',updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s",(activity_id,key))
            return True
        return await self._transaction(operation)

    async def _embedding_command_locked(self,connection,activity,operation_id,valid):
        match=re.fullmatch(r'emb18([iq])\.([0-9a-f-]{36})\.(0|[1-9][0-9]{0,2})',operation_id)
        if match is None:raise AdmissionDenied('embedding_binding_invalid')
        await self._retrieval_domain_locked(connection,activity)
        cursor=await connection.execute('SELECT * FROM retrieval_commands WHERE activity_id=%s AND business_key=%s FOR UPDATE',(activity['id'],match[2]))
        row=await cursor.fetchone()
        if row is None or operation_id not in operation_ids(row) or row['status']!='launch_claimed':raise AdmissionDenied('embedding_command_invalid')
        if not await self._retrieval_current_locked(connection,activity,row,valid):raise AdmissionDenied('embedding_invalidated')
        return row,int(match[3])

    async def admit_embedding(self,intent):
        if type(intent) is not EmbeddingAdmissionIntent:raise AdmissionDenied('embedding_intent_invalid')
        context=intent.context;aid=self._uuid(context.activity_id,'activity_id');oid=self._bounded_name(context.operation_id,'operation_id')
        executor=self._bounded_name(context.executor_id,'executor_id')
        if type(intent.request_bytes) is not int or not 0<intent.request_bytes<=65536 or intent.max_output_tokens!=0:raise AdmissionDenied('embedding_limits_invalid')
        async def operation(connection):
            await self._outbound_lock(connection,aid,intent.outbound_grant,intent.provider,intent.configured_model,intent.request_bytes,0)
            state=await self._memory_lock_prefix(connection,aid);activity=state['activity']
            if activity is None or not self._activity_allows(activity,intent,executor,now=datetime.now(timezone.utc)) or not state['eligible']:raise AdmissionDenied('embedding_activity_invalid')
            row,ordinal=await self._embedding_command_locked(connection,activity,oid,state['sources_valid'])
            binding=intent.binding;body=json.loads(row['request_body'])
            if (binding.business_key!=str(row['business_key']) or binding.purpose!=row['action'] or binding.batch_ordinal!=ordinal
                or binding.request_sha256!=row['request_sha256'] or binding.manifest_sha256!=row['manifest_sha256']
                or binding.scope_revision!=row['scope_revision'] or binding.domain!=row['domain'] or binding.domain_revision!=row['domain_revision']
                or binding.memory_selection_sha256!=body.get('memory_selection_sha256') or binding.memory_dependency_sha256!=body.get('memory_dependency_sha256')
                or intent.request.space_id!=row['space_id']):raise AdmissionDenied('embedding_binding_invalid')
            expected=body['manifest'][ordinal*4:ordinal*4+4] if row['action']=='source_index' else body['manifest']
            if [x.identity_sha256 for x in intent.request.inputs]!=[x['identity_sha256'] for x in expected]:raise AdmissionDenied('embedding_manifest_invalid')
            for inp,meta in zip(intent.request.inputs,expected):
                if digest(inp.text)!=meta['input_sha256']:raise AdmissionDenied('embedding_input_invalid')
            cursor=await connection.execute('SELECT 1 FROM activity_allowed_models WHERE activity_id=%s AND provider=%s AND model=%s',(aid,intent.provider,intent.configured_model))
            if await cursor.fetchone() is None:raise AdmissionDenied('embedding_model_not_allowed')
            cursor=await connection.execute('SELECT 1 FROM activity_operations WHERE activity_id=%s AND operation_id=%s',(aid,oid))
            if await cursor.fetchone():raise AdmissionDenied('embedding_already_claimed')
            admission=str(uuid4())
            await connection.execute('UPDATE activities SET requests_reserved=requests_reserved+1,cost_reserved_microunits=cost_reserved_microunits+reserve_cost_microunits,updated_at=CURRENT_TIMESTAMP WHERE id=%s',(aid,))
            await connection.execute("INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,execution_generation,scope_revision,provider,configured_model,request_bytes,max_output_tokens,tool_names,reserved_cost_microunits,kind) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,0,ARRAY[]::varchar(64)[],%s,'embedding')",
              (aid,oid,admission,executor,context.execution_generation,context.scope_revision,intent.provider,intent.configured_model,intent.request_bytes,activity['reserve_cost_microunits']))
            return EmbeddingAdmissionPermit(admission,oid,executor)
        return await self._transaction(operation)

    @staticmethod
    def _embedding_permit(permit):
        if type(permit) is not EmbeddingAdmissionPermit:raise AdmissionDenied('embedding_permit_invalid')
        return AdmissionPermit(permit.admission_id,permit.operation_id,permit.executor_id)

    async def mark_embedding_dispatch_started(self,permit):
        value=self._embedding_permit(permit)
        async def operation(connection):
            activity,call,valid=await self._locked_operation(connection,value,kind='embedding')
            await self._embedding_command_locked(connection,activity,call['operation_id'],valid)
            if call['state']!='reserved' or activity['dispatch_closed'] or not self._operation_is_current(activity,call,valid):raise AdmissionDenied('embedding_send_invalidated')
            await connection.execute("UPDATE activity_operations SET state='dispatched',dispatch_started_at=CURRENT_TIMESTAMP WHERE admission_id=%s",(permit.admission_id,))
        await self._transaction(operation)

    async def record_embedding_outcome(self,permit,outcome):
        value=self._embedding_permit(permit)
        if type(outcome) is not EmbeddingLedgerOutcome:raise AdmissionDenied('embedding_outcome_invalid')
        values=self._outcome_values(outcome);triple=self._payload_values(outcome)
        stored=None if triple is None else json.loads(triple[1])['value']
        if stored is not None:validate_stored_value(stored)
        async def operation(connection):
            activity,call,valid=await self._locked_operation(connection,value,kind='embedding')
            confirmed=await self._terminal_confirmation(connection,call,values,triple)
            if confirmed is not None:return confirmed
            row=None
            if outcome.disposition is not LedgerDisposition.UNKNOWN:
                if not self._operation_is_current(activity,call,valid) or activity['dispatch_closed'] or call['state']!='dispatched':raise AdmissionDenied('embedding_result_invalidated')
                row,ordinal=await self._embedding_command_locked(connection,activity,call['operation_id'],valid)
                if stored is not None:
                    expected=json.loads(row['request_body'])['manifest']
                    expected=expected[ordinal*4:ordinal*4+4] if row['action']=='source_index' else expected
                    if (stored['space_id']!=row['space_id'] or stored['purpose']!=row['action'] or stored['request_sha256']!=row['request_sha256']
                        or stored['manifest_sha256']!=row['manifest_sha256'] or [x['identity_sha256'] for x in stored['inputs']]!=[x['identity_sha256'] for x in expected]):raise AdmissionDenied('embedding_result_binding_invalid')
            await self._write_outcome(connection,call,values,triple)
            if stored is not None and row['action']=='source_index':
                for meta,inp in zip(expected,stored['inputs']):
                    await connection.execute('''INSERT INTO retrieval_chunks(space_id,evidence_id,source_id,source_version_id,source_revision,origin,physical_page,start_codepoint,end_codepoint,text_sha256,vector_value,vector_sha256,committed_activity_id,committed_operation_id)
                      VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::public.vector,%s,%s,%s) ON CONFLICT(space_id,evidence_id) DO NOTHING''',
                      (row['space_id'],meta['evidence_id'],meta['source_id'],meta['source_version_id'],meta['source_revision'],meta['origin'],meta['physical_page'],meta['start_codepoint'],meta['end_codepoint'],meta['text_sha256'],canonical(inp['vector']),inp['vector_sha256'],call['activity_id'],call['operation_id']))
                    cursor=await connection.execute('SELECT vector_value::text AS vector,vector_sha256 FROM retrieval_chunks WHERE space_id=%s AND evidence_id=%s',(row['space_id'],meta['evidence_id']))
                    actual=await cursor.fetchone()
                    if actual is None or vector_digest(json.loads(actual['vector']))!=actual['vector_sha256']:raise AdmissionDenied('embedding_storage_integrity_invalid')
            return RecordOutcome.RECORDED
        return await self._transaction(operation)

    async def retrieval_cached(self,space_id,evidence_ids):
        async def operation(connection):
            cursor=await connection.execute('''SELECT c.evidence_id,c.vector_sha256 FROM retrieval_chunks c JOIN material_sources s ON s.id=c.source_id
              WHERE c.space_id=%s AND c.evidence_id=ANY(%s) AND c.vector_value IS NOT NULL AND c.vector_sha256=public.retrieval_vector_digest(c.vector_value)
              AND s.current_version=c.source_version_id AND s.revision=c.source_revision
              AND NOT EXISTS(SELECT 1 FROM data_tombstones t WHERE t.entity_kind='source' AND t.entity_id=c.source_id)''',(space_id,evidence_ids))
            return {r['evidence_id']:r['vector_sha256'] for r in await cursor.fetchall()}
        return await self._transaction(operation)

    async def retrieval_finish(self,activity_id,key,*,definitely_unadmitted=False):
        async def operation(connection):
            state=await self._memory_lock_prefix(connection,activity_id);activity=state['activity']
            if activity is None:raise RetrievalRefusal('not_found',404)
            await self._retrieval_domain_locked(connection,activity)
            cursor=await connection.execute('SELECT * FROM retrieval_commands WHERE activity_id=%s AND business_key=%s FOR UPDATE',(activity_id,key));row=await cursor.fetchone()
            if row is None:raise RetrievalRefusal('not_found',404)
            if row['status']=='terminal':return plain(row)
            current=await self._retrieval_current_locked(connection,activity,row,state['sources_valid'])
            cursor=await connection.execute('SELECT o.operation_id,o.state,r.payload FROM activity_operations o LEFT JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s AND o.operation_id=ANY(%s) ORDER BY o.operation_id',(activity_id,operation_ids(row)))
            calls=await cursor.fetchall();complete=len(calls)==row['batch_count'] and all(c['state']=='received' and c['payload'] for c in calls)
            uncertain=any(c['state'] in ('dispatched','unknown','reserved') for c in calls) or not calls and not definitely_unadmitted
            outcome='invalidated' if not current else 'received' if complete else 'unknown' if uncertain else 'partial' if any(c['state']=='received' for c in calls) else 'not_sent'
            result=None
            if complete and current:
                result=digest({'space_id':row['space_id'],'manifest_sha256':row['manifest_sha256'],'results':[digest(json.loads(c['payload'])['value']) for c in calls]})
            await connection.execute("UPDATE retrieval_commands SET status='terminal',terminal_disposition=%s,result_sha256=%s,error_code=%s,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s",(outcome,result,None if complete and current else 'retrieval_'+outcome,activity_id,key))
            return plain({**row,'status':'terminal','terminal_disposition':outcome,'result_sha256':result})
        return await self._transaction(operation)

    async def read_retrieval_command(self,activity_id,key,*,include_body=False):
        async def operation(connection):
            state=await self._memory_lock_prefix(connection,activity_id);activity=state['activity']
            cursor=await connection.execute('SELECT * FROM retrieval_commands WHERE activity_id=%s AND business_key=%s',(activity_id,key));row=await cursor.fetchone()
            if row is None:return None
            current=activity is not None and await self._retrieval_current_locked(connection,activity,row,state['sources_valid'])
            cursor=await connection.execute('SELECT operation_id,state,disposition,error_code,reserved_cost_microunits FROM activity_operations WHERE activity_id=%s AND operation_id=ANY(%s) ORDER BY operation_id',(activity_id,operation_ids(row)))
            value=plain(row);value['current']=current;value['operations']=plain(await cursor.fetchall())
            value['retry_policy']='same_key_before_claim' if current and row['status']=='accepted' else 'read_only'
            if not include_body:value.pop('request_body')
            return value
        return await self._transaction(operation)

    async def _require_retrieval_ref(self,connection,activity,ref,*,domain=None,expected_revision=None):
        if not isinstance(ref,RetrievalRef):raise AdmissionDenied('retrieval_ref_required')
        cursor=await connection.execute('SELECT * FROM retrieval_commands WHERE activity_id=%s AND business_key=%s',(activity['id'],ref.business_key));row=await cursor.fetchone()
        if (row is None or row['action']!='query' or row['status']!='terminal' or row['terminal_disposition']!='received'
            or row['query_sha256']!=ref.query_sha256 or row['space_id']!=ref.space_id or row['result_sha256']!=ref.result_sha256
            or domain is not None and row['domain']!=domain or expected_revision is not None and row['domain_revision']!=expected_revision
            or row['scope_revision']!=activity['scope_revision'] or row['request_body'] is None or not activity.get('_memory_eligible',True)):
            raise AdmissionDenied('retrieval_ref_invalidated')
        # 已接受的领域动作可以占用head；冻结的revision由领域binding另行复核，不从新head追认。
        body=json.loads(row['request_body'])
        if body.get('memory_selection_sha256')!=activity.get('_memory_selection_sha256') or body.get('memory_dependency_sha256')!=activity.get('_memory_dependency_sha256'):
            raise AdmissionDenied('retrieval_ref_invalidated')
        if expected_revision is None:
            current_domain,current_revision,parents=await self._retrieval_domain_locked(connection,activity)
            if (current_domain,current_revision,parents)!=(row['domain'],row['domain_revision'],row['parent_refs']):raise AdmissionDenied('retrieval_ref_invalidated')
        return row

    async def retrieval_vector_ranks(self,activity_id,key,evidence_ids):
        async def operation(connection):
            state=await self._memory_lock_prefix(connection,activity_id);activity=state['activity']
            if activity is None:raise RetrievalRefusal('not_found',404)
            cursor=await connection.execute('SELECT * FROM retrieval_commands WHERE activity_id=%s AND business_key=%s',(activity_id,key));row=await cursor.fetchone()
            if row is None or row['terminal_disposition']!='received' or not await self._retrieval_current_locked(connection,activity,row,state['sources_valid']):raise RetrievalRefusal('retrieval_invalidated')
            cursor=await connection.execute('SELECT payload FROM activity_operation_results WHERE activity_id=%s AND operation_id=%s',(activity_id,operation_ids(row)[0]));result=await cursor.fetchone()
            if result is None:raise RetrievalRefusal('retrieval_integrity_invalid')
            stored=json.loads(result['payload'])['value'];validate_stored_value(stored);vector=stored['inputs'][0]['vector']
            cursor=await connection.execute('''SELECT c.evidence_id FROM retrieval_chunks c JOIN activity_scope_sources x ON x.source_id=c.source_id AND x.version_id=c.source_version_id AND x.source_revision=c.source_revision
              JOIN material_sources s ON s.id=c.source_id AND s.current_version=c.source_version_id AND s.revision=c.source_revision
              WHERE x.activity_id=%s AND c.space_id=%s AND c.evidence_id=ANY(%s) AND c.vector_value IS NOT NULL
              AND c.vector_sha256=public.retrieval_vector_digest(c.vector_value)
              AND NOT EXISTS(SELECT 1 FROM data_tombstones t WHERE t.entity_kind='source' AND t.entity_id=c.source_id)
              ORDER BY c.vector_value OPERATOR(public.<=>) %s::public.vector,c.evidence_id LIMIT 32''',(activity_id,row['space_id'],evidence_ids,canonical(vector)))
            return [r['evidence_id'] for r in await cursor.fetchall()]
        return await self._transaction(operation)
