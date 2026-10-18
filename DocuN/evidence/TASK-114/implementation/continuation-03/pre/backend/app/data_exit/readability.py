"""同一只读事务内的正文资格；原记录、头、哈希和墓碑不改写。"""
import json
from .contracts import DataError, uuid


def memory_projection(connection, memory_id, version):
    row = connection.execute("""WITH RECURSIVE lineage(mid,ver) AS(
      SELECT %s::uuid,%s::integer UNION
      SELECT d.upstream_memory_id,d.upstream_version FROM public.learning_memory_dependencies d
      JOIN lineage l ON d.memory_id=l.mid AND d.version=l.ver WHERE d.dependency_kind='memory'
    ), qualification AS(SELECT public.memory_revision_readable(%s,%s) AS readable), facts AS(
      SELECT EXISTS(SELECT 1 FROM public.data_tombstones t WHERE t.entity_kind='memory' AND t.entity_id=%s) AS revoked,
      EXISTS(SELECT 1 FROM lineage l JOIN public.learning_memory_dependencies d ON d.memory_id=l.mid AND d.version=l.ver
        JOIN public.data_tombstones t ON t.entity_kind='source' AND t.entity_id=d.source_id) AS source_deleted,
      EXISTS(SELECT 1 FROM lineage l JOIN public.data_tombstones t ON t.entity_kind='memory' AND t.entity_id=l.mid) AS upstream_deleted
    ) SELECT h.state,q.readable,f.revoked,f.source_deleted,f.upstream_deleted,
      CASE WHEN q.readable IS TRUE AND h.state='active' AND NOT(f.revoked OR f.source_deleted OR f.upstream_deleted)
           THEN b.body ELSE NULL END AS body
    FROM qualification q CROSS JOIN facts f
    LEFT JOIN public.learning_memories h ON h.memory_id=%s
    LEFT JOIN public.learning_memory_bodies b ON b.memory_id=h.memory_id AND b.version=%s""",
        (memory_id, version, memory_id, version, memory_id, memory_id, version)).fetchone()
    if row is None or row['readable'] is None: return None, 'qualification_unknown'
    if row['state'] == 'revoked' or row['revoked']: return None, 'revoked'
    if row['source_deleted']: return None, 'source_deleted'
    if row['readable'] is not True or row['upstream_deleted']: return None, 'dependency_invalid'
    return (row['body'], 'present') if row['body'] is not None else (None, 'unavailable')


def source_qualification(connection, ref):
    try:
        sid, vid = uuid(str(ref['source_id'])), uuid(str(ref['version_id']))
    except (KeyError, DataError): return 'qualification_unknown'
    row = connection.execute("""SELECT s.current_version::text,s.revision,v.sha256,
      EXISTS(SELECT 1 FROM public.data_tombstones WHERE entity_kind='source' AND entity_id=%s) AS deleted,
      (v.format<>'pdf' OR EXISTS(SELECT 1 FROM public.pdf_review_candidates c WHERE c.version_id=v.id AND c.status='confirmed'
        AND c.page_count BETWEEN 1 AND 50 AND(SELECT count(*) FROM public.pdf_review_pages p WHERE p.candidate_id=c.id)=c.page_count
        AND(SELECT count(*) FROM public.pdf_extracted_pages p WHERE p.version_id=c.version_id)=c.page_count)) AS ready
      FROM public.material_sources s LEFT JOIN public.material_versions v ON v.source_id=s.id AND v.id=%s WHERE s.id=%s""",
        (sid, vid, sid)).fetchone()
    if row is None: return 'dependency_invalid'
    if row['deleted']: return 'source_deleted'
    if (row['current_version'] != vid or row['ready'] is not True
        or ('source_revision' in ref and ref['source_revision'] != row['revision'])
        or ('original_sha256' in ref and ref['original_sha256'] != row['sha256'])):
        return 'dependency_invalid'
    return 'present'


def history_qualification(connection, table, row):
    """查原事实自己的sources/catalog/memory_refs/reference_hashes，非当前scope代替。"""
    derived = table == 'activity_operation_results' or (table == 'teaching_records' and row.get('kind') not in ('goal','answer','correction','exposure'))
    if derived and row.get('activity_id') is not None:
        selected = connection.execute('SELECT public.activity_memory_eligible(%s) AS eligible', (row['activity_id'],)).fetchone()
        if selected is None or selected['eligible'] is not True: return 'dependency_invalid'
    documents = []
    for name in ('source_refs', 'payload', 'body', 'local_body'):
        value = row.get(name)
        if value is None: continue
        if isinstance(value, str):
            try: value = json.loads(value)
            except (ValueError, TypeError):
                if name in ('source_refs', 'payload'): return 'qualification_unknown'
                continue  # 用户保存的纯文本没有结构化依赖。
        documents.append(value)
    refs, memories, events = [], [], []
    def walk(value, depth=0):
        if depth > 32: raise ValueError()
        if isinstance(value, list):
            for item in value: walk(item, depth+1)
        elif isinstance(value, dict):
            if 'source_id' in value and 'version_id' in value: refs.append(value)
            if 'memory_id' in value and 'version' in value: memories.append(value)
            if 'reference_hashes' in value:
                if not isinstance(value['reference_hashes'], list): raise ValueError()
                events.extend(value['reference_hashes'])
            for child in value.values(): walk(child, depth+1)
    try:
        for document in documents: walk(document)
        for ref in refs:
            reason = source_qualification(connection, ref)
            if reason != 'present': return reason
        for ref in memories:
            mid, ver = uuid(str(ref['memory_id'])), ref['version']
            if type(ver) is not int: return 'qualification_unknown'
            body, reason = memory_projection(connection, mid, ver)
            if reason != 'present': return reason
            head = connection.execute('SELECT current_version FROM public.learning_memories WHERE memory_id=%s', (mid,)).fetchone()
            revision = connection.execute('SELECT body_sha256 FROM public.learning_memory_revisions WHERE memory_id=%s AND version=%s', (mid, ver)).fetchone()
            if head is None or head['current_version'] != ver or revision is None or ref.get('body_sha256', revision['body_sha256']) != revision['body_sha256']:
                return 'dependency_invalid'
        for ref in events:
            if not isinstance(ref, dict): return 'qualification_unknown'
            rid, aid = uuid(str(ref['record_id'])), row.get('activity_id')
            if aid is None: return 'qualification_unknown'
            event = connection.execute("""SELECT body_sha256 FROM public.teaching_records t WHERE t.activity_id=%s AND t.record_id=%s
              AND NOT EXISTS(SELECT 1 FROM public.teaching_records x WHERE x.activity_id=t.activity_id
                AND((x.kind='correction' AND x.parent_record_id=t.record_id) OR(x.kind='answer' AND x.supersedes_record_id=t.record_id)
                OR(x.kind='feedback' AND t.kind IN('feedback','progress') AND x.answer_record_id=t.answer_record_id AND x.seq>t.seq)))""",
                (aid, rid)).fetchone()
            if event is None or event['body_sha256'] != ref.get('body_sha256'): return 'dependency_invalid'
    except (KeyError, ValueError, TypeError, DataError): return 'qualification_unknown'
    return 'present'
