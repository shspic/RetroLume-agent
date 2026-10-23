from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
from app.capabilities.q_protocol import digest,raw_digest,InstanceBinding,PreparedRequest
from app.data_exit.control import ControlHub
from app.data_exit.files import private_file,regular
from app.data_exit.q_store import QAuthority
from app.operator.q_request import principal_id

ROOT=Path(__file__).resolve().parents[4]
AID='01800000-0000-4000-8000-000000000001'
TEXT='根据速度.md学习单位换算。'


def store(*,template_atoms_extra=()):
    import os
    private=ROOT/'.runtime/task120-audit07/offline' if os.environ.get('RETROLUME_TASK120_CONTINUATION')=='TASK-120-Q-PREP-AUDIT-REPAIR-07-20261021' else ROOT/'.runtime/TASK-120/offline'
    root=private/str(uuid4())
    root.mkdir(parents=True)
    private_file(root,directory=True)
    hub=ControlHub(root)
    source={'dataset_id':str(uuid4()),'instance_id':str(uuid4()),'originals_root_id':str(uuid4()),'schema_profile':'data_exit.v1.r02','mode':'normal','reference_epoch':0}
    hub.commit('source.register',source)
    stat=regular(hub.path)
    b=InstanceBinding(hub_control_id=hub.control_id,selection_generation=0,dataset_id=source['dataset_id'],instance_id=source['instance_id'],originals_root_id=source['originals_root_id'],schema_profile=source['schema_profile'],
        source_registration_sha256=digest(source),connection_target_sha256=digest('offline-not-a-database'),cluster_system_identifier='OFFLINE',database_oid=1,control_root=str(root),control_volume=stat.st_dev,control_file_id=stat.st_ino)
    literal={'alias':'L01.goal','purpose':'goal','raw_text_sha256':raw_digest(TEXT),'json_string_sha256':digest(TEXT),'max_utf8_bytes':4096,'allowed_activity_ids':[AID],'allowed_actions':['first','plan']}
    source_id=str(uuid4());version_id=str(uuid4())
    templates=['fixed test system'];atoms=['messages','role','system','user','content','model','max_tokens','stream','thinking','type','disabled','goal']
    atoms.extend(template_atoms_extra)
    manifest={'schema':'retrolume.outbound-sources.v2','frozen_samples_sha256':'304a4b131d04cd4132334bebd091f94ff62bec5660698457487e14136023c113',
        'acceptance_contract_sha256':digest('offline-contract'),'sources':[{'source_id':source_id,'source_version_id':version_id,'source_revision':1,'original_sha256':raw_digest('synthetic original')}],
        'fragments':[{'identity_sha256':digest('offline-fragment'),'input_sha256':digest('synthetic original')}],'fixed_inputs':[literal],
        'derivation_policy_sha256':digest(__import__('app.capabilities.q_context',fromlist=['DERIVATION_POLICY']).DERIVATION_POLICY),'template_set_sha256':digest({'messages':templates,'atoms':atoms}),'instance_binding_sha256':b.sha256}
    now=datetime.now(timezone.utc)
    grant={'schema':'retrolume.outbound-grant.v2','grant_id':str(uuid4()),'approved_receipt_sha256':digest('offline-not-activation'),'q_activation_receipt_sha256':digest('offline-not-activation'),
        'source_manifest_sha256':digest(manifest),'price_snapshot_sha256':digest('offline-zero-price'),'valid_from_utc':now.isoformat(),'valid_until_utc':(now+timedelta(hours=1)).isoformat(),
        'data_class':'synthetic','allowed_activity_ids':[AID],'provider_capabilities':['deepseek_chat_completions/deepseek-flash','zhipu_embeddings/embedding-3'],
        'global_max_requests':100,'global_max_cost_microunits':25000000,'capabilities_verified':True,'account_terms_verified':True,'token_upper_bound_verified':True,
        'input_rate_cny_per_million':'0','output_rate_cny_per_million':'0','framing_token_upper_bound':0,'margin_percent':25,'instance_binding_sha256':b.sha256}
    bundle={'schema':'retrolume.q-root.v2','execution_class':'TESTONLY','grant':grant,'manifest':manifest,'binding':b.model_dump(mode='json'),
            'templates':templates,'template_atoms':atoms,'operator_principals':[principal_id()]}
    return QAuthority.bind(hub,bundle)


def prepared(authority,*,key=None,operation_id='offline.request',request=None,payload=None,snapshot=None):
    request=request or {'goal':TEXT};payload=payload or {'messages':[{'role':'user','content':TEXT}]}
    provenance=[]
    p=PreparedRequest(prepared_id=str(uuid4()),root_sha256=authority.manifest.sha256,grant_sha256=authority.grant.sha256,
        instance_binding_sha256=authority.binding.sha256,activity_id=AID,domain='learning',action='first',business_key=key or str(uuid4()),operation_id=operation_id,batch_ordinal=0,
        command_request_sha256=digest(request),frozen_context_sha256=digest(request),typed_request_sha256=digest(request),payload_object_sha256=digest(payload),
        payload_bytes_sha256=digest(payload),payload_bytes_count=len(__import__('app.capabilities.q_protocol',fromlist=['canonical']).canonical(payload).encode('utf-8')),
        provider='deepseek_chat_completions',endpoint='https://api.deepseek.com/chat/completions',configured_model='deepseek-flash',service_sha256=digest('offline-service'),
        template_set_sha256=authority.manifest.template_set_sha256,snapshot=snapshot or {},provenance_sha256=digest(provenance),max_output_tokens=256,
        created_at=datetime.now(timezone.utc).isoformat(),valid_until=authority.grant.valid_until_utc)
    return authority.prepare(p,request,payload,provenance)
