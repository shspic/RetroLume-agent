"""Private exact Q approvals. This journal can deny work; it never owns a balance."""
from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager, contextmanager
import contextvars
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from uuid import uuid4

from .contracts import DataError
from .files import RootLease, regular
from . import q_clock
from app.capabilities.q_protocol import (AuthorizationRef, DecisionBody, InstanceBinding, PreparedRequest,
    SourceManifestV2, canonical, digest, load_json, raw_digest, utcnow)

POLICY = contextvars.ContextVar('retrolume_q_policy', default=None)
DISPATCH_METHODS = frozenset(('admit','admit_embedding','mark_dispatch_started','mark_embedding_dispatch_started'))


def replay_event(state, kind, payload):
    if kind == 'q.bind':
        if 'q' in state:
            raise DataError('q_root_conflict')
        state['q'] = dict(payload, requests={}, approval_events=0, observed={})
        return
    q = state.get('q')
    if q is None:
        raise DataError('q_root_missing')
    pid = payload['prepared_id']
    if kind == 'q.prepared':
        if pid in q['requests']:
            raise DataError('q_prepared_conflict')
        q['requests'][pid] = dict(payload)
    elif pid not in q['requests']:
        raise DataError('q_prepared_missing')
    elif kind == 'q.approved':
        q['requests'][pid]['approval'] = payload['approval']
        q['requests'][pid].pop('revoked', None)
        q['approval_events'] += 1
        q['requests'][pid].pop('approval_seen',None)
    elif kind == 'q.approval_seen':
        row=q['requests'][pid]
        if row.get('approval',{}).get('approval_id')!=payload['approval_id']:raise DataError('q_approval_identity')
        row['approval_seen']=payload['sample']
    elif kind == 'q.approval_invalidated':
        q['requests'][pid].setdefault('invalid_approvals',{})[payload['approval_id']]=payload['reason']
    elif kind == 'q.revoked':
        q['requests'][pid]['revoked'] = True
    elif kind == 'q.claim':
        q['requests'][pid]['claim'] = payload['claim']
    elif kind == 'q.launch_claim':
        q['requests'][pid]['launch_claimed'] = True
    elif kind == 'q.admission_intent':
        q['requests'][pid]['admission_intent'] = payload['context']
        q['requests'][pid]['admission_owner'] = payload['owner']
    elif kind == 'q.admission_observed':
        q['requests'][pid]['admission'] = payload['fact']
        q['observed'][payload['fact']['admission_id']] = payload['fact']
    elif kind == 'q.closed':
        q['requests'][pid]['closed'] = payload['reason']
    elif kind == 'q.cleanup_pending':
        if q['requests'][pid].get('cleanup'):raise DataError('q_cleanup_conflict')
        q['requests'][pid]['cleanup']=payload['cleanup']
    elif kind == 'q.cleanup_done':
        row=q['requests'][pid]
        if not row.get('cleanup'):raise DataError('q_cleanup_missing')
        row['cleanup']['state']='done';row['cleanup']['outcome']=payload['outcome']


def authority_for(ledger):
    gate = getattr(ledger, 'mutation_gate', None)
    if gate is None or 'q' not in gate.hub.state():
        return None
    cached = getattr(ledger, '_q_authority', None)
    if cached is None or cached.hub is not gate.hub:
        cached = QAuthority(gate.hub)
        ledger._q_authority = cached
    # Cached lock identity is useful; cached journal authority is never sufficient.
    cached.check_root()
    return cached


def method_name(operation):
    return operation.__qualname__.split('.<locals>.')[0].split('.')[-1]


def is_read_method(name):
    return name.startswith(('read_', 'list_', 'inspect_', 'find_', 'q_snapshot')) or name in (
        'snapshot','retrieval_context','retrieval_cached','retrieval_vector_ranks','probe_storage',
        '_teaching_read_snapshot','validate_interview_request','verify_html_request')


def owned_closing(hub,state):
    from .maintenance import CLOSE_LANE
    owner=state['owned'].get(CLOSE_LANE.get(),{})
    source=state.get('source') or {};origin=owner.get('origin',{})
    return (state.get('selection') is None and (state.get('fence') or {}).get('state')=='draining'
        and owner.get('state')=='registered' and origin.get('control_id')==hub.control_id
        and all(origin.get(k)==source.get(k) for k in ('dataset_id','instance_id')))


class QAuthority:
    def __init__(self, hub):
        self.hub = hub
        state = hub.assert_writable()
        q = state.get('q')
        if q is None or state['selection'] is not None or (state['fence'] is not None and not owned_closing(hub,state)):
            raise DataError('q_normal_root_required')
        bundle = load_json(hub.read_artifact('q-root', q['root_id'], q['artifact_sha256'], 262144))
        if set(bundle) != {'schema','execution_class','grant','manifest','binding','templates','template_atoms','operator_principals'}:
            raise DataError('q_root_shape')
        if bundle['schema'] != 'retrolume.q-root.v2' or bundle['execution_class'] not in ('Q','TESTONLY'):
            raise DataError('q_root_shape')
        from app.capabilities.embedding import OutboundGrant
        self.grant = OutboundGrant.from_wire(bundle['grant'])
        self.manifest = SourceManifestV2.model_validate_json(canonical(bundle['manifest']))
        self.binding = InstanceBinding.model_validate_json(canonical(bundle['binding']))
        self.bundle = bundle
        from app.capabilities.q_context import DERIVATION_POLICY
        if self.manifest.derivation_policy_sha256!=digest(DERIVATION_POLICY):raise DataError('q_derivation_policy_unknown')
        if (self.grant.schema != 'retrolume.outbound-grant.v2' or self.grant.sha256 != q['grant_sha256']
            or self.manifest.sha256 != q['root_sha256'] or self.grant.source_manifest_sha256 != self.manifest.sha256
            or self.binding.sha256 != self.manifest.instance_binding_sha256
            or self.binding.sha256 != self.grant.instance_binding_sha256
            or digest({'messages':bundle['templates'],'atoms':bundle['template_atoms']}) != self.manifest.template_set_sha256):
            raise DataError('q_root_identity')
        stat = regular(hub.path)
        if (self.binding.hub_control_id != hub.control_id or self.binding.control_root != str(hub.root)
            or (stat.st_dev, stat.st_ino) != (self.binding.control_volume, self.binding.control_file_id)
            or digest(state['source']) != self.binding.source_registration_sha256):
            raise DataError('q_instance_identity')
        self.lock = RootLease(hub.root, '.q-policy.lock')

    def check_root(self):
        state=self.hub.assert_writable()
        q=state.get('q',{})
        if (state['selection'] is not None or (state['fence'] is not None and not owned_closing(self.hub,state))
            or q.get('grant_sha256')!=self.grant.sha256
            or digest(state['source'])!=self.binding.source_registration_sha256):
            raise DataError('q_root_changed')
        self.hub.read_artifact('q-root',q['root_id'],q['artifact_sha256'],262144)
        self.lock.check()

    @classmethod
    def bind(cls, hub, bundle):
        """Explicit trusted deployment setup, never an HTTP command or auto-approval."""
        state=hub.assert_writable()
        if set(bundle)!={'schema','execution_class','grant','manifest','binding','templates','template_atoms','operator_principals'}:
            raise DataError('q_root_shape')
        from app.capabilities.embedding import OutboundGrant
        grant=OutboundGrant.from_wire(bundle['grant'])
        manifest=SourceManifestV2.model_validate_json(canonical(bundle['manifest']))
        binding=InstanceBinding.model_validate_json(canonical(bundle['binding']))
        from app.capabilities.q_context import DERIVATION_POLICY
        if manifest.derivation_policy_sha256!=digest(DERIVATION_POLICY):raise DataError('q_derivation_policy_unknown')
        stat=regular(hub.path)
        if (bundle['schema']!='retrolume.q-root.v2' or bundle['execution_class'] not in ('Q','TESTONLY')
            or grant.schema!='retrolume.outbound-grant.v2' or grant.source_manifest_sha256!=manifest.sha256
            or grant.instance_binding_sha256!=binding.sha256 or manifest.instance_binding_sha256!=binding.sha256
            or manifest.template_set_sha256!=digest({'messages':bundle['templates'],'atoms':bundle['template_atoms']})
            or binding.hub_control_id!=hub.control_id or binding.control_root!=str(hub.root)
            or (binding.control_volume,binding.control_file_id)!=(stat.st_dev,stat.st_ino)
            or binding.source_registration_sha256!=digest(state['source'])
            or not bundle['operator_principals'] or len(bundle['operator_principals'])>8
            or not all(isinstance(x,str) and 0<len(x)<=256 for x in bundle['operator_principals'])
            or not isinstance(bundle['templates'],list) or len(bundle['templates'])>64
            or not all(isinstance(x,str) and len(x.encode('utf-8'))<=65536 for x in bundle['templates'])
            or not isinstance(bundle['template_atoms'],list) or len(bundle['template_atoms'])>2048
            or not all(isinstance(x,str) and len(x.encode('utf-8'))<=256 for x in bundle['template_atoms'])):
            raise DataError('q_root_identity')
        raw = canonical(bundle).encode('utf-8')
        if len(raw) > 262144:
            raise DataError('q_root_limit')
        root_id = str(uuid4())
        artifact_sha = hub.save_artifact('q-root', root_id, raw)
        def decide(state, seq):
            if state['selection'] is not None or state['fence'] is not None or 'q' in state:
                raise DataError('q_root_conflict')
            return {'root_id':root_id,'artifact_sha256':artifact_sha,
                    'root_sha256':digest(bundle['manifest']),'grant_sha256':digest(bundle['grant'])}
        hub.q_decide('q.bind', decide)
        return cls(hub)

    @contextmanager
    def policy(self, shared=False):
        inherited = POLICY.get()
        if inherited is not None:
            if inherited[0] != self.hub.control_id or (not shared and inherited[1]):
                raise DataError('q_policy_upgrade_forbidden')
            yield
            return
        with self.lock.acquire(not shared, timeout=1):
            token = POLICY.set((self.hub.control_id, shared))
            try:
                yield
            finally:
                POLICY.reset(token)

    @asynccontextmanager
    async def async_policy(self, shared=False):
        inherited = POLICY.get()
        if inherited is not None:
            if inherited[0] != self.hub.control_id or (not shared and inherited[1]):
                raise DataError('q_policy_upgrade_forbidden')
            yield
            return
        # Nonblocking attempts avoid starving the event loop that owns another lease.
        until = asyncio.get_running_loop().time() + 3
        while True:
            try:
                lease = self.lock.acquire(not shared, timeout=0)
                break
            except (TimeoutError, DataError) as exc:
                if asyncio.get_running_loop().time() >= until:
                    raise DataError('q_policy_busy') from exc
                await asyncio.sleep(.01)
        token = POLICY.set((self.hub.control_id, shared))
        try:
            yield
        finally:
            POLICY.reset(token)
            lease.close()

    def request(self, pid):
        row = self.hub.assert_writable()['q']['requests'].get(pid)
        if row is None:
            raise DataError('q_prepared_missing',404)
        return row

    def by_operation(self, aid, oid):
        return next((r for r in self.hub.state()['q']['requests'].values()
                     if r['prepared']['activity_id']==aid and r['prepared']['operation_id']==oid), None)

    def artifact(self, row):
        current=self.request(row['prepared_id'])
        if current.get('cleanup'):raise DataError('q_body_cleanup_closed',409)
        raw = self.hub.read_artifact('q-prepared',row['prepared_id'],row['artifact_sha256'],262144)
        value = load_json(raw)
        if set(value) != {'prepared','request','payload','provenance','intent'} or digest(value['prepared']) != row['prepared_sha256']:
            raise DataError('q_artifact_identity')
        prepared = PreparedRequest.model_validate_json(canonical(value['prepared']))
        if (digest(value['request']) != prepared.typed_request_sha256 or digest(value['payload']) != prepared.payload_object_sha256
            or raw_digest(canonical(value['payload'])) != prepared.payload_bytes_sha256
            or digest(value['provenance']) != prepared.provenance_sha256):
            raise DataError('q_artifact_identity')
        return value

    def prepare(self, prepared, request, payload, provenance, intent=None,*,dependencies=None):
        if prepared.domain=='learning':
            candidates=[r for r in self.hub.state()['q']['requests'].values() if r['prepared']['activity_id']==prepared.activity_id
                and r['prepared']['domain']=='learning' and (r['prepared']['business_key']==prepared.business_key
                or prepared.action==r['prepared']['action']=='first')]
            if any(r['prepared']['business_key']!=prepared.business_key or r['prepared']['operation_id']!=prepared.operation_id for r in candidates):
                raise DataError('q_original_key_conflict',409)
        prior = self.by_operation(prepared.activity_id, prepared.operation_id)
        if prior is not None:
            old = self.artifact(prior)
            fields=('typed_request_sha256','payload_bytes_sha256','service_sha256','snapshot','business_key')
            if any(old['prepared'][k] != prepared.model_dump(mode='json')[k] for k in fields):
                raise DataError('q_original_key_conflict',409)
            return prior
        raw=canonical({'prepared':prepared.model_dump(mode='json'),'request':request,'payload':payload,
                       'provenance':provenance,'intent':intent}).encode('utf-8')
        if len(raw)>262144:
            raise DataError('q_artifact_limit')
        artifact_sha=self.hub.save_artifact('q-prepared',prepared.prepared_id,raw)
        def decide(state, seq):
            q=state['q']
            if len(q['requests'])>=128:
                raise DataError('q_prepared_limit')
            if any(r['prepared']['activity_id']==prepared.activity_id and r['prepared']['operation_id']==prepared.operation_id for r in q['requests'].values()):
                raise DataError('q_original_key_conflict',409)
            return {'prepared_id':prepared.prepared_id,'prepared':prepared.model_dump(mode='json'),
                    'prepared_sha256':prepared.sha256,'artifact_sha256':artifact_sha,
                    'dependencies':dependencies or {'sources':[x['source_id'] for x in prepared.snapshot.get('sources',[])],
                        'memories':[x['memory_id'] for x in prepared.snapshot.get('memory',{}).get('refs',[])]}}
        self.hub.q_decide('q.prepared',decide)
        return self.request(prepared.prepared_id)

    def approval_valid(self,row):
        """Every authorizing projection/reference/consumer uses this same CAS.

        A negative observation is durable before it is returned. A later UTC
        rollback or another process cannot resurrect that exact decision.
        """
        if not row.get('approval'):return False
        result={}
        # Kind must be chosen from the same current state while holding the
        # journal lock, so use a tiny closed hub clock-observation operation.
        self.hub.q_observe_approval(row['prepared_id'],result)
        return result.get('valid',False)

    def projection(self, row, *, current=True, pg_consumed=False):
        if not row.get('cleanup'):self.artifact(row)
        now=utcnow(); approval=row.get('approval')
        state='invalidated' if not current or row.get('closed') or row.get('cleanup') else 'consumed' if pg_consumed or row.get('claim') or row.get('launch_claimed') else 'revoked' if row.get('revoked') else 'pending'
        if state=='pending' and approval:
            state='approved' if self.approval_valid(row) else 'expired'
        p=row['prepared']
        return {'state':state,'prepared_id':row['prepared_id'],'purpose':p['action'],'provider':p['provider'],
                'model':p['configured_model'],'request_count':1,'reserve_microunits':250000,
                'expires_at':approval['body']['expires_at'] if approval else None,'can_continue':state=='approved','reason':None if state=='approved' else 'q_'+state}

    def approve(self, pid, principal, *, current, pg_consumed=False):
        if principal not in self.bundle['operator_principals'] or not current:
            raise DataError('q_operator_or_currentness_denied')
        with self.policy():
            row=self.request(pid); self.artifact(row)
            if pg_consumed or row.get('claim') or row.get('launch_claimed') or row.get('closed') or row.get('cleanup'):
                raise DataError('q_approval_consumed')
            valid=self.approval_valid(row) if row.get('approval') and not row.get('revoked') else False
            sample=q_clock.sample();result={}
            def decide(state, seq):
                q=state['q']; r=q['requests'][pid]
                if r.get('claim') or r.get('launch_claimed') or r.get('closed'):
                    raise DataError('q_approval_consumed')
                old=r.get('approval'); now=datetime.fromisoformat(sample['utc'])
                if old and valid and not r.get('revoked'):
                    result.update(old); return None
                if q['approval_events']>=256:
                    raise DataError('q_approval_limit')
                end=min(now+timedelta(minutes=15),datetime.fromisoformat(r['prepared']['valid_until']))
                if end<=now:
                    raise DataError('q_prepared_expired')
                body=DecisionBody(prepared_sha256=r['prepared_sha256'],root_sha256=self.manifest.sha256,
                    operator_principal_id=principal,issued_at=now.isoformat(),expires_at=end.isoformat(),event_seq=seq,
                    clock=q_clock.certificate(sample,end))
                approval={'body':body.model_dump(mode='json'),'approval_id':body.approval_id}
                result.update(approval)
                return {'prepared_id':pid,'approval':approval}
            self.hub.q_decide('q.approved',decide)
            return result

    def revoke(self,pid,principal):
        if principal not in self.bundle['operator_principals']:
            raise DataError('q_operator_denied')
        with self.policy():
            self.hub.q_decide('q.revoked',lambda state,seq:{'prepared_id':pid})
        return {'state':'revoked','remote_cancelled':False}

    def reference(self,row):
        if self.projection(row)['state']!='approved':
            return None
        a=row['approval']
        return AuthorizationRef(root_sha256=self.manifest.sha256,prepared_id=row['prepared_id'],
            prepared_sha256=row['prepared_sha256'],approval_id=a['approval_id'],approval_event_seq=a['body']['event_seq']).model_dump(mode='json')

    def check_reference(self,ref, *, context=None, external=False, claimed=False):
        self.check_root()
        ref=AuthorizationRef.model_validate_json(canonical(ref))
        row=self.request(ref.prepared_id); self.artifact(row)
        approval=row.get('approval')
        if external and self.bundle['execution_class']!='Q':
            raise DataError('q_testonly_external_forbidden')
        if (ref.root_sha256!=self.manifest.sha256 or ref.prepared_sha256!=row['prepared_sha256'] or not approval
            or ref.approval_id!=approval['approval_id'] or ref.approval_event_seq!=approval['body']['event_seq']
            or row.get('revoked') or row.get('closed') or row.get('cleanup') or not self.approval_valid(row)
            or DecisionBody.model_validate_json(canonical(approval['body'])).approval_id!=approval['approval_id']):
            raise DataError('q_approval_invalid')
        if context is not None:
            c=context.model_dump(mode='json')
            if (c['activity_id'],c['operation_id'])!=(row['prepared']['activity_id'],row['prepared']['operation_id']):
                raise DataError('q_operation_identity')
            if claimed:
                if row.get('claim')!=c:
                    raise DataError('q_claim_identity')
            else:
                def decide(state,seq):
                    r=state['q']['requests'][ref.prepared_id]
                    if r.get('claim'):
                        raise DataError('q_approval_consumed')
                    return {'prepared_id':ref.prepared_id,'claim':c}
                self.hub.q_decide('q.claim',decide)
        return row

    def admission_intent(self,ref,context):
        row=self.check_reference(ref,context=context,claimed=True)
        value=context.model_dump(mode='json')
        from app.preview.process import birth
        from .q_kernel import AdmissionSignal
        signal=AdmissionSignal()
        owner={'pid':os.getpid(),**birth(os.getpid())}
        if owner.get('state')!='running' or not owner.get('birth'):raise DataError('q_admission_owner_unknown')
        owner['signal']=signal.name
        def decide(state,seq):
            current=state['q']['requests'][row['prepared_id']]
            if current.get('admission') or current.get('admission_intent'):
                raise DataError('q_admission_already_attempted')
            return {'prepared_id':row['prepared_id'],'context':value,'owner':owner}
        try:self.hub.q_decide('q.admission_intent',decide)
        except BaseException:
            signal.close();raise
        return signal

    def admission_failed(self,ref,*,definitely_denied):
        pid=ref['prepared_id']
        def decide(state,seq):
            row=state['q']['requests'][pid]
            if not row.get('admission_intent') or row.get('admission'):return None
            return {'prepared_id':pid,'reason':'admission_denied' if definitely_denied else 'admission_unconfirmed'}
        self.hub.q_decide('q.closed',decide)

    def admission_observed(self,ref,permit,context):
        row=self.check_reference(ref,context=context,claimed=True)
        fact={'admission_id':str(permit.admission_id),'operation_id':permit.operation_id,
              'activity_id':context.activity_id,'execution_generation':context.execution_generation}
        self.hub.q_decide('q.admission_observed',lambda state,seq:{'prepared_id':row['prepared_id'],'fact':fact})
