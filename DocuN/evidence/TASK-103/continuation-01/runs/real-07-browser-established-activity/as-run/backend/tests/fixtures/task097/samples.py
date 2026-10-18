"""固定中英资料及支持性正反例；不代表真实供应商质量。"""
from uuid import uuid4
from app.learning.contracts import LearningProfile, request_fingerprint, SourceIdentity, sha
from app.learning.evidence import Unit, assemble_catalog
from app.retrieval.evidence import SourceTextUnit

ENGLISH = "Atomicity means all transaction changes commit together or none commit.\r\n"
CHINESE = "事务原子性表示事务的修改一起提交，或者全部不提交。\n"
XSS = '<img src="https://outside.invalid/x" onerror="window.learningXss=1">\n'


def unit(text=ENGLISH, *, revision=0, page=None, origin="original", source=None, title="atomicity.md"):
    source_id = source or str(uuid4())
    version = str(uuid4())
    record = {"source_id": source_id, "version_id": version, "source_revision": revision,
        "title": title, "format": "pdf" if page else "md", "sha256": sha(text), "size": len(text.encode("utf-8"))}
    return Unit(record, SourceTextUnit(source_id, version, revision, page, origin, text, True),
        str(uuid4()) if origin == "user_supplement" else None)


def profile(*, units=None, goal="Explain atomicity", action="first", activity_id=None, parent=None, parent_sha=None, question=None, history=None):
    units = units or (unit(),)
    sources = [SourceIdentity(source_id=u.unit.source_id, version_id=u.unit.version_id, source_revision=u.unit.source_revision) for u in units]
    sources = list({s.source_id: s for s in sources}.values())
    sources.sort(key=lambda s: s.source_id)
    identity = dict(action=action, activity_id=activity_id or str(uuid4()), goal=goal, question=question,
        scope_revision=1, sources=[s.model_dump() for s in sources], parent_operation_id=parent,
        parent_payload_sha256=parent_sha, max_output_tokens=256)
    fingerprint = request_fingerprint(**identity)
    catalog = assemble_catalog(question or goal, tuple(units), fingerprint)
    return LearningProfile(**identity, request_sha256=fingerprint, catalog=catalog, history=history)


def answer(p):
    return {"kind": "answer", "message": "按资料组织的有限答案", "segments": [
        {"text": "Transaction changes commit together or none commit.", "citations": [p.catalog[0].citation_id]}], "questions": []}
