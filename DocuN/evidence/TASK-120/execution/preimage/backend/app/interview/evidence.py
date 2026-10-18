"""Bounded term evidence and original-position checks; no full resume send."""
from app.learning.evidence import load_units, LearningRefusal
from app.retrieval.evidence import build_fragments, rank_term_candidates, verify_fragment, EvidenceFragment
from .contracts import InterviewCatalogEntry, InterviewRefusal, sha


def assemble_catalog(query,units,request_sha):
    fragments=[]; lookup={}
    for unit in units:
        parts=build_fragments(unit.unit,max_fragments=512)
        if len(fragments)+len(parts)>512: raise InterviewRefusal('interview_context_too_large','请缩小资料范围',422)
        for fragment in parts:
            if not verify_fragment(unit.unit,fragment) or fragment.evidence_id in lookup:
                raise InterviewRefusal('source_invalid','资料片段身份无法核对')
            lookup[fragment.evidence_id]=unit
        fragments.extend(parts)
    ranked=rank_term_candidates(query,tuple(fragments),allowed_versions=frozenset((u.unit.source_id,u.unit.version_id) for u in units),top_k=12)
    entries=[]; used=0
    for candidate in ranked:
        f=candidate.fragment; item=lookup[f.evidence_id]
        used+=len(f.text.encode('utf-8'))
        if used>8192: raise InterviewRefusal('interview_context_too_large','证据超过单次片段上限，请缩小范围',422)
        entries.append(InterviewCatalogEntry(source_id=f.source_id,version_id=f.version_id,source_revision=f.source_revision,
            citation_id='ic_'+sha(request_sha+f.evidence_id)[:24],evidence_id=f.evidence_id,
            title=item.source['title'],format=item.source['format'],original_sha256=item.source['sha256'],
            unit_sha256=sha(item.unit.text),fragment_sha256=f.text_sha256,start_line=f.start_line,end_line=f.end_line,
            start_offset=f.start_offset,end_offset=f.end_offset,physical_page=f.physical_page,origin_kind=f.origin_kind,
            supplement_id=item.supplement_id,text=f.text))
    return entries


def verify_citation(entry,units):
    entry=InterviewCatalogEntry.model_validate(entry)
    unit=next((u for u in units if u.unit.source_id==entry.source_id and u.unit.version_id==entry.version_id
        and u.unit.source_revision==entry.source_revision and u.unit.physical_page==entry.physical_page
        and u.unit.origin_kind==entry.origin_kind and u.supplement_id==entry.supplement_id),None)
    fragment=EvidenceFragment(entry.evidence_id,entry.source_id,entry.version_id,entry.source_revision,
        entry.physical_page,entry.origin_kind,entry.start_line,entry.end_line,entry.start_offset,entry.end_offset,
        entry.fragment_sha256,entry.text)
    return unit is not None and sha(unit.unit.text)==entry.unit_sha256 and verify_fragment(unit.unit,fragment)
