"""Small presentation helpers; DB statement snapshots decide eligibility."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from .contracts import canonical,sha,InterviewRefusal,load_json


def plain(value):
    if isinstance(value,(UUID,datetime)): return str(value) if isinstance(value,UUID) else value.isoformat()
    if isinstance(value,Decimal): return str(value)
    if isinstance(value,dict): return {str(k):plain(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [plain(v) for v in value]
    return value


def token(snapshot):
    head=snapshot.get('head')
    return sha(canonical(dict(head=head,sources=snapshot.get('sources'),memory=snapshot.get('memory'),
        pending=snapshot.get('pending'),budget=snapshot.get('budget'),qualifications=snapshot.get('qualifications',[]))))


def bounded_wire(value,maximum):
    raw=canonical(plain(value)).encode('utf-8')
    if len(raw)>maximum: raise InterviewRefusal('interview_snapshot_limit','本次读取超过上限，请读取单条记录',413)
    return raw


def verified_body(row):
    payload=row.get('payload')
    if payload is None: return None
    if sha(payload)!=row['body_sha256']: raise InterviewRefusal('interview_binding_invalid','持久正文身份不一致',503)
    document=load_json(payload)
    if row['origin']=='model':
        if document.get('format')!='json' or document.get('value',{}).get('profile')!='interview.v1':
            raise InterviewRefusal('interview_binding_invalid','持久正文类型不一致',503)
        document=document['value']
    return document
