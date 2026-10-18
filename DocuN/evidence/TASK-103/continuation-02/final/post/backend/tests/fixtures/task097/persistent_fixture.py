"""从07真实首续和08显式复用谱系读取，绝不把保留样本加入清理。"""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];E=ROOT/'DocuN/evidence/TASK-097'
def retained_learning(fixture,out):
    original=E/'integration-07-browser'
    owner=json.loads((original/'retained-fixture.json').read_text(encoding='utf-8'))
    identities=json.loads((original/'fixture-identities.json').read_text(encoding='utf-8'))
    report=json.loads((original/'browser-report.json').read_text(encoding='utf-8'))
    assert owner['task']=='TASK-097' and Path(owner['root']).resolve()==fixture.root.resolve()
    names={c['name']:c['actual'] for c in report['checks']}
    reuse={'activity':owner['activities'][0],'first':names['explicit_first_one_post']['operation'],
        'followup':names['explicit_followup_one_post']['operation'],'origin':str(original.relative_to(ROOT))}
    linked=json.loads((E/'integration-08-browser/reuse-persistent-fixture.json').read_text(encoding='utf-8'))
    assert all(linked[k]==reuse[k] for k in ['activity','first','followup'])
    for s in identities['sources']:
        actual=fixture.rows('SELECT s.current_version::text AS version_id,s.revision,v.sha256 FROM material_sources s JOIN material_versions v ON v.id=s.current_version WHERE s.id=%s',(s['id'],))
        assert actual==[{'version_id':s['version_id'],'revision':s['revision'],'sha256':s['sha256']}],actual
        raw=(fixture.root/s['sha256']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['sha256']
    rows=fixture.rows('SELECT operation_id,disposition FROM activity_operations WHERE activity_id=%s AND operation_id=ANY(%s) ORDER BY operation_id',(reuse['activity'],[reuse['first'],reuse['followup']]))
    assert len(rows)==2 and all(r['disposition']=='received' for r in rows)
    (out/'reuse-persistent-fixture.json').write_text(json.dumps({'reuse':reuse,'lineage':['integration-07-browser','integration-08-browser'],'sources':identities['sources'],'persistent_rows':rows,'preserved_not_owned_for_cleanup':True},ensure_ascii=False,indent=2),encoding='utf-8')
    return reuse
