"""明确确认后的有限检索。每批经原Windows监督，一键查询不在GET中发生。"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
import json
import os
from pathlib import Path
import secrets
from pydantic import BaseModel, ConfigDict, Field
from .contracts import canonical,digest,space_identity,fused_rank,RetrievalCommandInput,RetrievalRef,RetrievalRefusal
from .repository import operation_ids
from .evidence import build_fragments,verify_fragment,rank_term_candidates
from app.learning.contracts import CatalogEntry,sha
from app.learning.evidence import load_units,validate_snapshot
from app.capabilities.embedding import EmbeddingServiceConfig,EmbeddingInput,EmbeddingBinding,EmbeddingRequest,OutboundGrant,OutboundSourceManifest
from app.worker.one_call import run_one_embedding
from app.worker.session import SessionConfig
from app.data_exit.maintenance import owned_service


class _IntegrationSection(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True,frozen=True)
    schema:str=Field(pattern=r'^retrolume.integration.v1$')
    enabled:bool=False
    embedding:dict
    max_index_fragments:int=Field(default=512,ge=1,le=512)
    outbound_grant_file:str|None=None
    q_activation_receipt_file:str|None=None
    price_snapshot_file:str|None=None
    source_manifest_file:str|None=None


@dataclass(frozen=True)
class IntegrationConfig:
    service:EmbeddingServiceConfig|None=None
    reason:str|None='retrieval_not_configured'
    max_index_fragments:int=512
    @property
    def available(self):
        from app.capabilities.transport import HttpxModelTransport
        return self.service is not None and self.reason is None and (self.service.outbound_grant is not None or not HttpxModelTransport.is_external)
    def public(self):return {'available':self.available,'reason':self.reason,'method':'hybrid.cosine-terms.rrf60.v1',
      'purpose':'当前已确认资料片段与本轮必要问题','provider':self.service.provider if self.service else None,'model':self.service.model if self.service else None,'dimensions':512,
      'batch_size':4,'max_index_fragments':self.max_index_fragments,'query_limit_chars':1024,'query_limit_bytes':4096,
      'real_outbound_authorized':bool(self.service and self.service.outbound_grant and
          (self.service.outbound_grant.get('schema')!='retrolume.outbound-grant.v2' or __import__('app.capabilities.transport',fromlist=['HttpxModelTransport']).HttpxModelTransport.is_external)),'reserve_cost_microunits':250000}


def load_integration_config(path):
    """正常server env loader；文件不携口令，启用Q要求受信激活和价格原件hash。"""
    if path is None:return IntegrationConfig()
    try:
        raw=Path(path).read_bytes()
        if len(raw)>65536:raise ValueError('config_size')
        section=_IntegrationSection.model_validate_json(raw)
        if not section.enabled:return IntegrationConfig(reason='retrieval_disabled')
        key=os.environ.get('RETROLUME_EMBEDDING_API_KEY','').strip()
        if not key:return IntegrationConfig(reason='embedding_key_not_configured')
        body=dict(section.embedding)
        if set(body)-{'provider','base_url','model','dimensions','returned_models','timeout_seconds','max_request_bytes','max_response_bytes'}:raise ValueError('config_shape')
        body['api_key']=key
        if section.outbound_grant_file:
            if not section.q_activation_receipt_file or not section.price_snapshot_file or not section.source_manifest_file:raise ValueError('activation_missing')
            grant_raw=Path(section.outbound_grant_file).read_bytes()
            if len(grant_raw)>65536:raise ValueError('grant_size')
            from app.capabilities.q_protocol import load_json
            grant=OutboundGrant.from_wire(load_json(grant_raw))
            manifest_raw=Path(section.source_manifest_file).read_bytes()
            if len(manifest_raw)>65536:raise ValueError('manifest_size')
            manifest=OutboundSourceManifest.from_wire(load_json(manifest_raw))
            if manifest.sha256!=grant.source_manifest_sha256:raise ValueError('manifest_hash')
            from hashlib import sha256
            receipt_raw=Path(section.q_activation_receipt_file).read_bytes();price_raw=Path(section.price_snapshot_file).read_bytes()
            if len(receipt_raw)>65536 or len(price_raw)>65536:raise ValueError('receipt_size')
            receipt=load_json(receipt_raw)
            from app.capabilities.transport import HttpxModelTransport
            testonly=grant.schema=='retrolume.outbound-grant.v2' and receipt.get('stage')=='TESTONLY' and receipt.get('TASK')=='TASK-120' and not HttpxModelTransport.is_external
            if (sha256(receipt_raw).hexdigest()!=grant.q_activation_receipt_sha256 or sha256(price_raw).hexdigest()!=grant.price_snapshot_sha256
                or (not testonly and (receipt.get('stage')!='Q' or receipt.get('TASK') not in ('TASK-117','TASK-120'))) or receipt.get('status')!='enabled'
                or receipt.get('approved_receipt_sha256')!=grant.approved_receipt_sha256 or receipt.get('source_manifest_sha256')!=manifest.sha256 or not receipt.get('independent_audit_result_sha256')):raise ValueError('activation_invalid')
            body['outbound_grant']=grant.model_dump(mode='json')
            body['outbound_source_manifest']=manifest.model_dump(mode='json')
        # JSON模式接受数组tuple；受信配置从本地env注入，不向客户端返回秘密。
        service=EmbeddingServiceConfig.model_validate_json(json.dumps(body))
        return IntegrationConfig(service,None,section.max_index_fragments)
    except (ValueError,TypeError,OSError,KeyError):return IntegrationConfig(reason='retrieval_config_invalid')


def fragments_for(units):
    result={}
    for unit in units:
        for fragment in build_fragments(unit.unit,max_fragments=512):
            if not verify_fragment(unit.unit,fragment) or fragment.evidence_id in result:raise RetrievalRefusal('retrieval_source_integrity')
            result[fragment.evidence_id]=(fragment,unit)
            if len(result)>512:raise RetrievalRefusal('retrieval_scope_limit',413)
    return result


def fragment_manifest(fragment,unit):
    meta={'evidence_id':fragment.evidence_id,'source_id':fragment.source_id,'source_version_id':fragment.version_id,
      'source_revision':fragment.source_revision,'origin':fragment.origin_kind,'physical_page':fragment.physical_page,
      'supplement_id':unit.supplement_id,'start_codepoint':fragment.start_offset,'end_codepoint':fragment.end_offset,
      'text_sha256':fragment.text_sha256,'unit_sha256':sha(unit.unit.text),'original_sha256':unit.source['sha256']}
    return {**meta,'identity_sha256':digest(meta),'input_sha256':digest(fragment.text)}


class RetrievalService:
    def __init__(self,ledger,materials,originals):self.ledger,self.materials,self.originals=ledger,materials,originals

    async def _sources(self,activity_id):
        snapshot=await self.ledger.read_learning_snapshot(activity_id);validate_snapshot(snapshot)
        if self.materials is None:raise RetrievalRefusal('storage_unavailable',503)
        units=await asyncio.to_thread(load_units,snapshot,self.materials,self.originals)
        return snapshot,fragments_for(units)

    async def status(self,activity_id,config):
        value=config.public()
        if not config.available:return value
        snapshot,fragments=await self._sources(activity_id)
        context=await self.ledger.retrieval_context(activity_id)
        cached=await self.ledger.retrieval_cached(space_identity(config.service.provider,config.service.model),list(fragments))
        return {**value,'scope_revision':snapshot['scope_revision'],'domain_revision':context['domain_revision'],'fragments':len(fragments),'cached_fragments':len(cached),
          'index_batches':(len(fragments)-len(cached)+3)//4,'ready':len(cached)==len(fragments) and bool(fragments),
          'remaining_requests':max(0,snapshot['max_requests']-snapshot['requests_reserved']),
          'reserve_cost_microunits':snapshot['reserve_cost_microunits'],
          'remaining_cost_microunits':max(0,snapshot['max_cost_microunits']-snapshot['cost_reserved_microunits']),
          'remaining_running_seconds':max(0,snapshot['max_running_seconds']-snapshot['running_settled_seconds']-snapshot['running_reserved_seconds']),
          'query_then_model_requests':2,'query_then_model_reserve_microunits':2*snapshot['reserve_cost_microunits'],'window_reserve_seconds':SessionConfig().window_seconds}

    @owned_service
    async def submit(self,activity_id,command,config,*,run_tag=None):
        if not config.available:raise RetrievalRefusal(config.reason or 'retrieval_not_configured',503)
        if type(command) is not RetrievalCommandInput:raise RetrievalRefusal('invalid_input',400)
        previous=await self.ledger.read_retrieval_command(activity_id,command.business_key,include_body=True)
        if previous is not None:
            if previous['request_body'] is None:raise RetrievalRefusal('retrieval_invalidated')
            body=json.loads(previous['request_body'])
            if body['command']!=command.model_dump(mode='json'):raise RetrievalRefusal('retrieval_key_conflict')
            if previous['status']!='accepted':return self._public(previous)
            row=previous
            snapshot,fragments=await self._sources(activity_id)
        else:
            snapshot,fragments=await self._sources(activity_id)
            context=await self.ledger.retrieval_context(activity_id)
            if not context['current'] or context['scope_revision']!=command.expected_scope_revision or context['domain_revision']!=command.expected_domain_revision:raise RetrievalRefusal('retrieval_invalidated')
            space=space_identity(config.service.provider,config.service.model)
            cached=await self.ledger.retrieval_cached(space,list(fragments))
            if command.action=='source_index':
                missing=[fragment_manifest(*fragments[k]) for k in sorted(fragments) if k not in cached]
                if len(missing)>config.max_index_fragments:raise RetrievalRefusal('retrieval_index_limit',413)
                manifest=missing;batches=(len(missing)+3)//4
            else:
                if not fragments or len(cached)!=len(fragments):raise RetrievalRefusal('retrieval_index_required')
                query=command.query.strip()
                # 输入只为用户本轮必要query；不自动附作答或记忆正文。
                manifest=[{'identity_sha256':digest({'query':query,'scope_revision':command.expected_scope_revision,'space_id':space}),
                           'input_sha256':digest(query)}];batches=1
            source_refs=[{'source_id':r['source_id'],'source_version_id':r['version_id'],'source_revision':r['source_revision']} for r in snapshot['sources']]
            body={'schema':'retrieval.context.v1','activity_id':activity_id,'command':command.model_dump(mode='json'),
                  'domain':context['domain'],'parent_refs':context['parent_refs'],'memory_selection_sha256':context['memory_selection_sha256'],
                  'memory_dependency_sha256':context['memory_dependency_sha256'],'manifest':manifest,
                  'coverage_sha256':digest([fragment_manifest(*fragments[k]) for k in sorted(fragments)])}
            row,_=await self.ledger.retrieval_freeze(activity_id,command,body,{'space_id':space,'provider':config.service.provider,'configured_model':config.service.model},manifest,batches,source_refs,
                    digest(command.query.strip()) if command.action=='query' else None)
        if row['status']=='terminal':return self._public(row)
        # 旧接受体必须能从当前原件逐项复建，不重新检索或替换其manifest。
        if body['coverage_sha256']!=digest([fragment_manifest(*fragments[k]) for k in sorted(fragments)]):raise RetrievalRefusal('retrieval_source_invalid')
        prepared_calls=[];approvals=[]
        from app.capabilities.q_gateway import is_v2
        if is_v2(config.service) and command.action=='query' and command.query!=command.query.strip():
            raise RetrievalRefusal('q_exact_query_required')
        for ordinal,oid in enumerate(operation_ids(row)):
            part=body['manifest'][ordinal*4:ordinal*4+4] if command.action=='source_index' else body['manifest']
            inputs=[]
            for index,meta in enumerate(part):
                text=fragments[meta['evidence_id']][0].text if command.action=='source_index' else command.query.strip()
                if digest(text)!=meta['input_sha256']:raise RetrievalRefusal('retrieval_source_invalid')
                inputs.append(EmbeddingInput(ordinal=index,identity_sha256=meta['identity_sha256'],text=text))
            binding=EmbeddingBinding(business_key=command.business_key,purpose=command.action,request_sha256=row['request_sha256'],
                manifest_sha256=row['manifest_sha256'],batch_ordinal=ordinal,scope_revision=command.expected_scope_revision,domain=body['domain'],
                domain_revision=command.expected_domain_revision,memory_selection_sha256=body['memory_selection_sha256'],memory_dependency_sha256=body['memory_dependency_sha256'])
            request=EmbeddingRequest(activity_id=activity_id,space_id=row['space_id'],binding=binding,inputs=tuple(inputs))
            service=config.service
            if is_v2(service):
                from app.capabilities.q_context import prepare
                payload={'model':service.model,'input':[x.text for x in request.inputs],'dimensions':512}
                projection,service=await prepare(self.ledger,activity_id,command.business_key,oid,request,service,payload,
                    domain='retrieval',action=command.action)
                approvals.append(projection)
            prepared_calls.append((ordinal,oid,request,service))
        if approvals and not all(x['can_continue'] for x in approvals):
            from app.capabilities.q_context import public_projection
            return {**self._public(row),'outbound_approval':await public_projection(self.ledger,activity_id,command.business_key)}
        from app.capabilities.q_context import claim_approved
        if not await claim_approved(self.ledger,[item[3] for item in prepared_calls],lambda:self.ledger.retrieval_claim(activity_id,command.business_key,row['request_sha256'])):
            return self._public(await self.ledger.read_retrieval_command(activity_id,command.business_key))
        windows=[];definitely_unadmitted=False
        for ordinal,oid,request,service in prepared_calls:
            task=asyncio.create_task(asyncio.to_thread(run_one_embedding,self.ledger,SessionConfig(),activity_id,'local-ui',oid,request,service,
                  run_tag=(run_tag or 'retrieval-'+secrets.token_hex(12))+'-'+str(ordinal)))
            cancelled=False
            while True:
                try:supervision=await asyncio.shield(task);break
                except asyncio.CancelledError:
                    cancelled=True
                    if task.done():supervision=task.result();break
                except Exception:supervision=None;break
            if cancelled:raise asyncio.CancelledError
            if supervision is not None:
                windows.append({k:getattr(supervision,k,None) for k in ('run_tag','state','generation','job_name','pid','active_processes_at_end','settled_seconds','reserved_seconds','pending_fold_seconds','elapsed_seconds','cleanup_incomplete','error_type','cleanup_errors','manager_pid','manager_created_100ns','running_owner_session_id','worker_created_100ns','model_receipt')})
                definitely_unadmitted=not supervision.cleanup_incomplete and supervision.state in ('not_started','budget_exhausted','startup_deadline','partial_window_too_small') and supervision.model_receipt is None
            fact=await self.ledger.read_operation(activity_id,oid)
            if supervision is None or fact is None or fact.state!='received' or not fact.payload:break
        completed=await self.ledger.retrieval_finish(activity_id,command.business_key,definitely_unadmitted=definitely_unadmitted)
        return {**self._public(await self.ledger.read_retrieval_command(activity_id,command.business_key) or completed),'supervision':windows}

    @staticmethod
    def _public(row):
        value={k:v for k,v in row.items() if k!='request_body'}
        if row.get('action')=='query' and row.get('terminal_disposition')=='received' and row.get('result_sha256'):
            value['retrieval_ref']={'business_key':str(row['business_key']),'query_sha256':row['query_sha256'],'space_id':row['space_id'],'result_sha256':row['result_sha256']}
        return value

    async def catalog(self,activity_id,ref,request_sha,*,top_k=8,max_chars=12000,max_bytes=24000):
        ref=RetrievalRef.model_validate(ref)
        row=await self.ledger.read_retrieval_command(activity_id,ref.business_key,include_body=True)
        if (row is None or not row['current'] or row['terminal_disposition']!='received' or row['action']!='query'
            or (ref.query_sha256,ref.space_id,ref.result_sha256)!=(row['query_sha256'],row['space_id'],row['result_sha256'])):raise RetrievalRefusal('retrieval_invalidated')
        body=json.loads(row['request_body']);query=body['command']['query'].strip()
        snapshot,fragments=await self._sources(activity_id)
        if body['coverage_sha256']!=digest([fragment_manifest(*fragments[k]) for k in sorted(fragments)]):raise RetrievalRefusal('retrieval_source_invalid')
        term=rank_term_candidates(query,tuple(f[0] for f in fragments.values()),allowed_versions=frozenset((r['source_id'],r['version_id']) for r in snapshot['sources']),top_k=32,truncate_terms=True)
        vectors=await self.ledger.retrieval_vector_ranks(activity_id,ref.business_key,list(fragments))
        ids=fused_rank([c.fragment.evidence_id for c in term],vectors,top_k=top_k)
        if not ids:raise RetrievalRefusal('no_evidence')
        entries=[]
        for eid in ids:
            f,unit=fragments[eid]
            if not verify_fragment(unit.unit,f):raise RetrievalRefusal('retrieval_source_integrity')
            entries.append(CatalogEntry(source_id=f.source_id,version_id=f.version_id,source_revision=f.source_revision,citation_id='lc_'+sha(request_sha+eid)[:24],
              evidence_id=eid,title=unit.source['title'],format=unit.source['format'],original_sha256=unit.source['sha256'],unit_sha256=sha(unit.unit.text),
              fragment_sha256=f.text_sha256,start_line=f.start_line,end_line=f.end_line,start_offset=f.start_offset,end_offset=f.end_offset,
              physical_page=f.physical_page,origin_kind=f.origin_kind,supplement_id=unit.supplement_id,text=f.text))
        if sum(len(e.text) for e in entries)>max_chars or sum(len(e.text.encode('utf-8')) for e in entries)>max_bytes:raise RetrievalRefusal('retrieval_context_limit',413)
        after=await self.ledger.read_retrieval_command(activity_id,ref.business_key)
        if after is None or not after['current'] or after['result_sha256']!=ref.result_sha256:raise RetrievalRefusal('retrieval_invalidated')
        return entries
