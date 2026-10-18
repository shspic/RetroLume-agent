"""仅本卡真实普通PG连接的持久事实断言；不构造收费结果。"""
def verify_persistent_retrieval(connection):
    from app.capabilities.embedding import vector_digest
    rows=connection.execute('SELECT vector_value::text AS vector,vector_sha256,public.retrieval_vector_digest(vector_value) AS sql_sha FROM retrieval_chunks ORDER BY evidence_id').fetchall()
    import json
    assert rows
    for row in rows:
        vector=json.loads(row['vector']);assert len(vector)==512
        assert vector_digest(vector)==row['vector_sha256']==row['sql_sha']
    operations=connection.execute("SELECT count(*) AS n FROM activity_operations WHERE kind='embedding' AND state='received'").fetchone()['n']
    bodies=connection.execute("SELECT count(*) AS n FROM activity_operations o JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.kind='embedding' AND o.state='received'").fetchone()['n']
    assert operations==bodies
    assert connection.execute("SELECT count(*) AS n FROM activity_operation_results r JOIN activity_operations o USING(activity_id,operation_id) WHERE o.kind='embedding' AND o.state<>'received'").fetchone()['n']==0
    return {'vectors':len(rows),'received_embedding_operations':operations,'matching_007':bodies,'float32_sql_python_equal':True,'unknown_has_no_new_body':True}
