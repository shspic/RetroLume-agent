"""仅本卡main库的六列补丁和真实角色资格；不重跑迁移、不改旧行。"""
import asyncio,hashlib,json,re
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from .control import ROOT,atomic
from app.runtime import psycopg_compatible_loop_factory
from app.preview.description import digest,canonical
from app.preview.repository import plain

PDF=('pdf_review_candidates','pdf_review_pages','pdf_extracted_pages')
PATCH='''GRANT SELECT(id,version_id,status,page_count) ON public.pdf_review_candidates TO retrolume_html_owner;
GRANT SELECT(candidate_id) ON public.pdf_review_pages TO retrolume_html_owner;
GRANT SELECT(version_id) ON public.pdf_extracted_pages TO retrolume_html_owner;'''

def snapshot(conn):
    tables=conn.execute("SELECT c.relname,c.relacl::text AS acl FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' ORDER BY c.relname").fetchall()
    columns=conn.execute("SELECT c.relname,a.attname,a.attacl::text AS acl FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped WHERE n.nspname='public' ORDER BY c.relname,a.attnum").fetchall()
    roles=conn.execute("SELECT rolname,rolcanlogin,rolsuper,rolcreaterole,rolbypassrls FROM pg_roles WHERE rolname LIKE 'retrolume_%' ORDER BY rolname").fetchall()
    memberships=conn.execute("SELECT r.rolname,m.rolname AS member,a.admin_option FROM pg_auth_members a JOIN pg_roles r ON r.oid=a.roleid JOIN pg_roles m ON m.oid=a.member ORDER BY r.rolname,m.rolname").fetchall()
    functions=conn.execute("SELECT p.proname,p.prosrc,p.prosecdef,p.proconfig,p.proacl::text AS acl,r.rolname AS owner FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner WHERE n.nspname='public' ORDER BY p.oid").fetchall()
    return plain(dict(tables=tables,columns=columns,roles=roles,memberships=memberships,functions=functions))

def apply(resource,out):
    with psycopg.connect(resource['admin'],row_factory=dict_row) as conn:
        assert conn.execute('SELECT current_database() AS db').fetchone()['db']=='retrolume_task111_main'
        before=snapshot(conn);atomic(out/'qualification-pre.json',before)
        closure=[x for x in before['functions'] if x['proname'] in ('memory_dependency_line','memory_dependency_digest','memory_scope_digest','memory_choice_digest','memory_revision_readable','memory_revision_eligible','activity_memory_eligible','html_parent_eligible')]
        assert len(closure)==8
        sql='\n'.join(x['prosrc'] for x in closure)
        for table in PDF:assert 'public.'+table in sql
        conn.execute(PATCH);after=snapshot(conn)
        assert all(before[k]==after[k] for k in ('tables','roles','memberships','functions'))
        changes=[dict(before=a,after=b) for a,b in zip(before['columns'],after['columns']) if a!=b]
        expected={('pdf_review_candidates',x) for x in ('id','version_id','status','page_count')}|{('pdf_review_pages','candidate_id'),('pdf_extracted_pages','version_id')}
        assert {(x['after']['relname'],x['after']['attname']) for x in changes}==expected
        atomic(out/'qualification-patch.json',dict(status='APPLIED_SIX_COLUMNS_ONLY',patch=PATCH,changes=changes,table_acl_unchanged=True,old_subjects_functions_memberships_unchanged=True,closure=closure))
    from app.activities.repository import PostgresAdmissionLedger
    ledger=PostgresAdmissionLedger(resource['app'])
    async def shape():return await ledger._transaction(ledger.html_schema_shape)
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:value=runner.run(shape())
    migration=ROOT/'backend/migrations/012_html_explanations.sql'
    fingerprint=dict(schema='retrolume.html.schema.v2',sha256=digest(value),migration_sha256=hashlib.sha256(migration.read_bytes()).hexdigest())
    atomic(ROOT/'backend/app/preview/schema-fingerprint.json',fingerprint);atomic(out/'schema-shape.json',value);atomic(out/'schema-fingerprint.json',fingerprint)
    effects=[]
    with psycopg.connect(resource['admin'],row_factory=dict_row) as conn:
        for role in ('retrolume_html_owner','retrolume_html_app'):
            conn.execute('SET LOCAL ROLE '+role)
            for table,col in (('pdf_extracted_pages','extracted_text'),('pdf_extracted_pages','warnings')):
                try:
                    with conn.transaction():conn.execute('SELECT '+col+' FROM public.'+table+' LIMIT 0')
                except psycopg.Error as error:assert error.sqlstate=='42501';effects.append(dict(role=role,operation='SELECT '+col,table=table,sqlstate=error.sqlstate))
                else:raise AssertionError('正文权限扩大')
            for table in PDF:
                for op,sql in (('INSERT','INSERT INTO public.'+table+' DEFAULT VALUES'),('UPDATE','UPDATE public.'+table+' SET '+('status=status' if table==PDF[0] else 'version_id=version_id')+' WHERE false'),('DELETE','DELETE FROM public.'+table+' WHERE false')):
                    try:
                        with conn.transaction():conn.execute(sql)
                    except psycopg.Error as error:assert error.sqlstate=='42501';effects.append(dict(role=role,operation=op,table=table,sqlstate=error.sqlstate))
                    else:raise AssertionError('写权限扩大')
            conn.execute('RESET ROLE')
        # 六个被授列逐项检查html_app未新增直接读取权。
        for table,col in sorted(expected):
            row=conn.execute("SELECT has_column_privilege('retrolume_html_owner',%s,%s,'SELECT') AS owner,has_column_privilege('retrolume_html_app',%s,%s,'SELECT') AS app",(table,col,table,col)).fetchone()
            assert row['owner'] and not row['app'];effects.append(dict(table=table,column=col,**row))
    atomic(out/'column-role-rejections.json',effects)
    pdf_cases(resource,out)

def pdf_cases(resource,out):
    from app.materials.repository import PostgresMaterials
    from app.pdf_import import PdfImportResult,PdfPage
    # 真实资料producer建立本卡新对象；页内容合成，无解析或Windows模型调用。
    materials=PostgresMaterials(resource['app'])
    from app.pdf_review.contracts import ReviewPage
    extraction=PdfImportResult(page_count=2,warnings=(),extraction_method='pypdf-6.17.0',pages=(PdfPage(physical_page=1,text='C04 PDF synthetic first',warnings=()),PdfPage(physical_page=2,text='C04 PDF synthetic second',warnings=())))
    candidate=materials.create_pdf_candidate(source_id=None,expected_version=None,expected_revision=0,filename='c04-qualification.pdf',sha256=hashlib.sha256(b'C04 synthetic PDF fixture').hexdigest(),size=26,extraction=extraction)
    version=candidate['version_id'];cid=candidate['candidate_id'];source=candidate['source_id']
    materials.confirm_pdf_candidate(candidate_id=cid,version_id=version,pages=[ReviewPage(physical_page=i,reviewed=True) for i in (1,2)])
    cases=[]
    with psycopg.connect(resource['admin']) as conn:
        mid,key=str(uuid4()),str(uuid4());body=canonical(dict(schema='memory.body.v1',kind='self_report',title='C04 PDF资格',text='仅资格依赖',uncertainty='self_reported'));bodyhash=hashlib.sha256(body.encode()).hexdigest()
        revision=conn.execute('SELECT revision FROM material_sources WHERE id=%s',(source,)).fetchone()[0]
        dep=hashlib.sha256(f'source|{source}|{version}|{revision}|{candidate["sha256"]}'.encode()).hexdigest()
        conn.execute("INSERT INTO learning_memories(memory_id,revision,current_version,state) VALUES(%s,1,1,'active')",(mid,))
        conn.execute("INSERT INTO learning_memory_commands(business_key,action,memory_id,request_sha256,slot_sha256,effect_applied,before_revision,after_revision,after_version,result_meta) VALUES(%s,'save',%s,%s,%s,true,0,1,1,'{}')",(key,mid,'a'*64,'b'*64))
        conn.execute("INSERT INTO learning_memory_revisions(memory_id,version,claim_kind,uncertainty,policy_version,body_sha256,body_bytes,dependencies_sha256,dependency_count,created_by_key) VALUES(%s,1,'self_report','self_reported','memory.user.v1',%s,%s,%s,1,%s)",(mid,bodyhash,len(body.encode()),dep,key))
        conn.execute('INSERT INTO learning_memory_bodies(memory_id,version,body) VALUES(%s,1,%s)',(mid,body))
        conn.execute("INSERT INTO learning_memory_dependencies(memory_id,version,ordinal,dependency_kind,source_id,source_version_id,source_revision,original_sha256) VALUES(%s,1,1,'source',%s,%s,%s,%s)",(mid,source,version,revision,candidate['sha256']))
        conn.execute('SET CONSTRAINTS ALL IMMEDIATE')
        def observe(name,expected):
            conn.execute('SET LOCAL ROLE retrolume_html_owner')
            value=conn.execute('SELECT public.memory_revision_readable(%s,1),public.memory_revision_eligible(%s,1)',(mid,mid)).fetchone()
            counts=conn.execute('SELECT (SELECT count(*) FROM pdf_review_pages WHERE candidate_id=%s),(SELECT count(*) FROM pdf_extracted_pages WHERE version_id=%s)',(cid,version)).fetchone()
            conn.execute('RESET ROLE');assert value==(expected,expected);cases.append(dict(case=name,readable=value[0],eligible=value[1],review_count=counts[0],extracted_count=counts[1],executing_role='retrolume_html_owner'))
        observe('confirmed_complete',True)
        conn.execute('SAVEPOINT case_check');conn.execute("UPDATE pdf_review_candidates SET status='pending' WHERE id=%s",(cid,));observe('unconfirmed',False);conn.execute('ROLLBACK TO SAVEPOINT case_check')
        conn.execute('UPDATE pdf_review_candidates SET page_count=3 WHERE id=%s',(cid,));conn.execute("INSERT INTO pdf_extracted_pages(version_id,physical_page,extracted_text,warnings) VALUES(%s,3,'synthetic third','[]')",(version,));observe('missing_review_page',False);conn.execute('ROLLBACK TO SAVEPOINT case_check')
        conn.execute('UPDATE pdf_review_candidates SET page_count=3 WHERE id=%s',(cid,));conn.execute('INSERT INTO pdf_review_pages(candidate_id,version_id,physical_page) VALUES(%s,%s,3)',(cid,version));observe('missing_extracted_page',False)
        conn.rollback()
    atomic(out/'pdf-complete-qualification-cases.json',dict(status='PASS_REAL_OWNER_FULL_READABLE_CLOSURE',cases=cases,candidate=candidate,memory_fixture_transaction='ROLLBACK; committed synthetic PDF retained'))
