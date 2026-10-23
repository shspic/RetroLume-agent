"""Q v2 immutable objects. No I/O, credentials, provider calls or activation here."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

HEX = r'^[0-9a-f]{64}$'
ROSTER = tuple('01800000-0000-4000-8000-00000000000' + str(n) for n in (1, 2, 3))
LIMITS = ((48, 12000000), (28, 7000000), (24, 6000000))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def raw_digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode('utf-8')).hexdigest()


def load_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('q_duplicate_json_key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('q_nonfinite')))


class Closed(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, strict=True)


class FixedInput(Closed):
    alias: str = Field(min_length=1, max_length=128)
    purpose: str = Field(min_length=1, max_length=64)
    raw_text_sha256: str = Field(pattern=HEX)
    json_string_sha256: str = Field(pattern=HEX)
    max_utf8_bytes: int = Field(ge=0, le=65536)
    allowed_activity_ids: tuple[str, ...] = Field(min_length=1, max_length=3)
    allowed_actions: tuple[str, ...] = Field(min_length=1, max_length=16)

    @model_validator(mode='after')
    def bounds(self):
        if not set(self.allowed_activity_ids) <= set(ROSTER):
            raise ValueError('q_literal_roster')
        return self


class SourceManifestV2(Closed):
    schema: Literal['retrolume.outbound-sources.v2'] = 'retrolume.outbound-sources.v2'
    frozen_samples_sha256: Literal['304a4b131d04cd4132334bebd091f94ff62bec5660698457487e14136023c113']
    acceptance_contract_sha256: str = Field(pattern=HEX)
    sources: tuple[dict, ...] = Field(min_length=1, max_length=128)
    fragments: tuple[dict, ...] = Field(min_length=1, max_length=512)
    fixed_inputs: tuple[FixedInput, ...] = Field(min_length=1, max_length=256)
    derivation_policy_sha256: str = Field(pattern=HEX)
    template_set_sha256: str = Field(pattern=HEX)
    instance_binding_sha256: str = Field(pattern=HEX)

    @model_validator(mode='after')
    def closed_sources(self):
        from .embedding import OutboundSourceManifest
        OutboundSourceManifest.model_validate_json(canonical(dict(
            schema='retrolume.outbound-sources.v1', frozen_samples_sha256=self.frozen_samples_sha256,
            sources=self.sources, fragments=self.fragments, query_input_sha256=['0' * 64])))
        if len({x.alias for x in self.fixed_inputs}) != len(self.fixed_inputs):
            raise ValueError('q_duplicate_literal')
        return self

    @property
    def sha256(self):
        return digest(self.model_dump(mode='json'))

    def check_sources(self, rows):
        from .contracts import AdmissionDenied
        allowed = {(x['source_id'], x['source_version_id'], x['source_revision'], x['original_sha256']) for x in self.sources}
        if not rows or any((str(x['source_id']), str(x.get('source_version_id', x.get('version_id'))),
                            x['source_revision'], x.get('original_sha256', x.get('sha256'))) not in allowed for x in rows):
            raise AdmissionDenied('outbound_source_not_approved')

    def check_embedding(self, request):
        from .contracts import AdmissionDenied
        if request.binding.purpose == 'source_index':
            allowed = {x['identity_sha256']: x['input_sha256'] for x in self.fragments}
            if any(allowed.get(x.identity_sha256) != digest(x.text) for x in request.inputs):
                raise AdmissionDenied('outbound_input_not_approved')
        # Query text still requires exact per-request authority and finite provenance.

    def check_model(self, request, payload=None):
        from .embedding import approved_fragment_identity
        from .contracts import AdmissionDenied
        profile = request.learning_profile or request.teaching_profile
        if request.interview_profile is not None:
            # InterviewProfile contains bindings, not a catalog. Its actual
            # typed catalog is in the already frozen second message. Recheck
            # the exact profile/prompt pair before using those source entries.
            from app.interview.contracts import parse_context,profile_for,InterviewHybridContext
            from app.interview.prompt import messages
            try:
                value=load_json(request.messages[1].content)
                frozen=parse_context(value.get('context',value))
                background=value.get('learning_background') if isinstance(frozen,InterviewHybridContext) else None
                if (profile_for(frozen)!=request.interview_profile
                    or [m.model_dump(mode='json',exclude_none=True) for m in request.messages]!=messages(frozen,background)):
                    raise ValueError('interview_binding_invalid')
                catalog=frozen.catalog
            except (ValueError,TypeError,KeyError,IndexError):
                raise AdmissionDenied('outbound_profile_not_approved') from None
        else:
            catalog = profile.catalog if profile else load_json(request.html_profile.context_json).get('catalog', []) if request.html_profile else []
        if not catalog:
            raise AdmissionDenied('outbound_profile_required')
        allowed = {x['identity_sha256'] for x in self.fragments}
        for item in catalog:
            row = item.model_dump(mode='json') if hasattr(item, 'model_dump') else item
            if raw_digest(row['text']) != row['fragment_sha256'] or approved_fragment_identity(row) not in allowed:
                raise AdmissionDenied('outbound_fragment_not_approved')
            self.check_sources([dict(source_id=row['source_id'], version_id=row['version_id'],
                                     source_revision=row['source_revision'], original_sha256=row['original_sha256'])])


class InstanceBinding(Closed):
    hub_control_id: str
    dataset_id: str
    instance_id: str
    originals_root_id: str
    selection_generation: int = Field(ge=0)
    schema_profile: Literal['data_exit.v1.r02','data_exit.v1.r03']
    source_registration_sha256: str = Field(pattern=HEX)
    connection_target_sha256: str = Field(pattern=HEX)
    cluster_system_identifier: str = Field(min_length=1, max_length=64)
    database_oid: int = Field(gt=0)
    control_root: str
    control_volume: int
    control_file_id: int

    @model_validator(mode='after')
    def ids(self):
        for field in ('hub_control_id', 'dataset_id', 'instance_id', 'originals_root_id'):
            value = getattr(self, field)
            if str(UUID(value)) != value:
                raise ValueError('q_instance_identity')
        return self

    @property
    def sha256(self):
        return digest(self.model_dump(mode='json'))


class AuthorizationRef(Closed):
    root_sha256: str = Field(pattern=HEX)
    prepared_id: str
    prepared_sha256: str = Field(pattern=HEX)
    approval_id: str = Field(pattern=HEX)
    approval_event_seq: int = Field(gt=0)


class PreparedRequest(Closed):
    schema: Literal['retrolume.q-prepared.v2'] = 'retrolume.q-prepared.v2'
    prepared_id: str
    root_sha256: str = Field(pattern=HEX)
    grant_sha256: str = Field(pattern=HEX)
    instance_binding_sha256: str = Field(pattern=HEX)
    activity_id: str
    domain: str
    action: str
    business_key: str
    operation_id: str
    batch_ordinal: int = Field(ge=0)
    command_request_sha256: str = Field(pattern=HEX)
    frozen_context_sha256: str = Field(pattern=HEX)
    typed_request_sha256: str = Field(pattern=HEX)
    payload_object_sha256: str = Field(pattern=HEX)
    payload_bytes_sha256: str = Field(pattern=HEX)
    payload_bytes_count: int = Field(gt=0, le=65536)
    provider: Literal['deepseek_chat_completions', 'zhipu_embeddings']
    endpoint: str
    configured_model: Literal['deepseek-flash', 'embedding-3']
    service_sha256: str = Field(pattern=HEX)
    template_set_sha256: str = Field(pattern=HEX)
    snapshot: dict
    provenance_sha256: str = Field(pattern=HEX)
    max_output_tokens: int = Field(ge=0, le=4096)
    created_at: str
    valid_until: str

    @property
    def sha256(self):
        return digest(self.model_dump(mode='json'))


class ApprovalClock(Closed):
    schema: Literal['retrolume.q-clock.v1'] = 'retrolume.q-clock.v1'
    domain: str = Field(pattern=HEX)
    issued_mono_ns: int = Field(ge=0)
    issued_upper_ns: int = Field(ge=0)
    deadline_mono_ns: int = Field(gt=0)


class DecisionBody(Closed):
    schema: Literal['retrolume.q-decision.v2'] = 'retrolume.q-decision.v2'
    prepared_sha256: str = Field(pattern=HEX)
    root_sha256: str = Field(pattern=HEX)
    operator_principal_id: str
    issued_at: str
    expires_at: str
    decision: Literal['approve'] = 'approve'
    event_seq: int = Field(gt=0)
    clock: ApprovalClock | None = None

    @property
    def approval_id(self):
        # K1: this object has no approval_id field and its seq is fixed under the journal lock.
        return digest(self.model_dump(mode='json',exclude_none=True))


def utcnow():
    return datetime.now(timezone.utc)


def service_identity(service):
    value = service.model_dump(mode='json', exclude={'api_key', 'outbound_authorization'})
    return digest(value)
