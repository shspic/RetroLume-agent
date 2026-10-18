"""S06 one bounded source root: read-only deletion effects, preview first, one PDF diagnostic."""
from batch_runtime import *
from frozen_http import FrozenFlow,two_page_pdf
from urllib.parse import quote
import psycopg
MID='c110aa4b-095c-4fec-905d-37fe3922e3cc'
def deletion(flow):
    with psycopg.connect(rc.dsn('source','snapshot'),autocommit=True) as connection:
        connection.execute('SET default_transaction_read_only=on')
        rows={}
        queries={'header':('SELECT revision,current_version,state,purge_state,purged_at IS NOT NULL FROM learning_memories WHERE memory_id=%s',(MID,)),
            'body_rows':('SELECT count(*) FROM learning_memory_bodies WHERE memory_id=%s',(MID,)),
            'revisions':('SELECT version,body_sha256,body_bytes FROM learning_memory_revisions WHERE memory_id=%s ORDER BY version',(MID,)),
            'commands':('SELECT action,before_revision,after_revision,after_version,effect_applied,manifest_sha256,cleanup_manifest FROM learning_memory_commands WHERE memory_id=%s ORDER BY committed_at',(MID,)),
            'dependencies':('SELECT count(*) FROM learning_memory_dependencies WHERE memory_id=%s',(MID,)),
            'old_choices':('SELECT count(*) FROM activity_memory_choices WHERE memory_id=%s',(MID,))}
        for name,(sql,args) in queries.items():rows[name]=connection.execute(sql,args).fetchall()
    value=flow.call('GET','/api/memories/'+MID)
    assert rows['body_rows']==[(0,)] and rows['revisions'] and value.get('body') is None and value['state']=='revoked' and value['purge_state']=='done'
    revoke=next(r for r in rows['commands'] if r[0]=='revoke');manifest=json.loads(revoke[6]);assert c.sha(revoke[6].encode())==revoke[5]
    assert {(r[0],r[1],r[2]) for r in rows['revisions']}=={(r['version'],r['body_sha256'],r['body_bytes']) for r in manifest['targets']}
    c.write(C01/'X02-current-physical-deletion.json',{'sample':c.sample(),'memory_id':MID,'sql_read_only':True,'SQL':rows,'GET':value,'all_revision_bodies_removed':True,'exact_manifest_hash_verified':True,'immutable_versions_choices_dependencies_retained':True,'new_memory_tombstone_commands':0,'prior_invalidation':'continuation-02/X02-late-memory-progress.json'})
def pdf(flow):
    start=c.sample();raw=two_page_pdf();assert c.sha(raw)=='ca68cb54cfdb651e6a2d4048128a1aa5d3613a83a3192bb1321df5f2ddb8fcc4'
    c.write(C01/'PDF-diagnostic-admission.json',{'sample':start,'original_HTTP_failures_retained':2,'diagnostic_attempt':1,'max_diagnostic_attempts':1,'input_sha256':c.sha(raw),'input_bytes':len(raw),'Content-Type':flow.client.headers.get('Content-Type'),'normal_HTTP_path':True,'probe_coverage':['parse entry','worker argv/exclusion','real Job create/assign/resume/wait/exit','output existence/bytes/envelope'],'probe_sha256':c.sha((C01/'pdf_probe.py').read_bytes())})
    try:
        value=flow.call('POST','/api/materials?filename='+quote('PDF-2.pdf'),content=raw,native=1)
    except Exception as error:
        c.failure('S06_PDF_diagnostic',str(error));return
    assert value.get('query_ready') is False
    candidate=value['candidate'];assert candidate['page_count']==2
    confirmed=flow.call('POST',f"/api/pdf-candidates/{candidate['candidate_id']}/confirm",{'version_id':candidate['version_id'],'pages':[{'physical_page':1,'reviewed':True},{'physical_page':2,'reviewed':True,'supplement':'用户独立补充：本页分钟须换秒，不代替原页。'}]})
    material=confirmed['material'];detail=flow.call('GET',f"/api/materials/{material['id']}?expected_version={material['version_id']}")
    c.write(C01/'PDF-two-page-confirmed.json',{'sample':c.sample(),'started':start,'candidate':candidate,'confirmed':confirmed,'material_detail':detail,'original_sample_sha256':c.sha(raw),'manual_confirmation_gate_retained':True,'physical_pages_reviewed':[1,2],'reference_basis':'physical_page and version identities from actual GET; no model semantic claim'})
def main():
    preflight('S06-source-preview-priority',preview=True)
    with Batch(22,'S06-source-preview-PDF') as batch:
        rc.start_pg('source');batch.start_api()
        flow=FrozenFlow('source-targeted')
        try:
            try:deletion(flow)
            except Exception as error:c.failure('S06_X02_readonly_proof',str(error))
            aid='0305ee4c-be33-489e-bab6-8f2f55e59573';artifact='b263cb39-b6e8-4edf-8573-9c84ee1c5326'
            qualified=flow.call('GET',f'/api/activities/{aid}/html/artifacts/{artifact}');c.write(C01/'original-artifact-current-qualification.json',qualified)
            before=c.state()['counts']['preview_starts']
            try:
                from preview_case import run_preview
                run_preview(batch,flow,aid,artifact)
                c.write(C01/'L10-fixed-preview-completed.json',{'sample':c.sample(),'actual_ACK_PNG_and_original_StopProof':True})
            except Exception as error:
                c.failure('S06_fixed_preview',str(error));c.write(C01/'preview-attempt-outcome.json',{'sample':c.sample(),'error_type':type(error).__name__,'error':str(error),'starts_before':before,'starts_after':c.state()['counts']['preview_starts']})
                if c.state()['counts']['preview_starts']!=before:return
            pdf(flow)
        finally:flow.close()
if __name__=='__main__':main()
