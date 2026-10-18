"""根14同截止内只读定位实际已提交目录与批准派生目录的差异。"""
from sql_and_commit import *
def main():
    preflight('root14-catalog-readback')
    with Batch(14,'S03_SQL_catalog_readback'):
        rc.start_pg('compat')
        with psycopg.connect(rc.dsn('compat','admin'),row_factory=dict_row) as db:
            shape={k:db.execute(q).fetchall() for k,q in extra_shape_queries().items()}
            actual=normalized_extra_shape(shape)
            expected=json.loads((OLD/'ordinary-db-fixes/derived-shape.json').read_text())
            c.write(C01/'compat-actual-after-first-commit.json',{'sample':c.sample(),'shape':shape,'hash':c.sha(canonical(actual).encode())})
            differences=[]
            for k in sorted(set(actual)|set(expected)):
                if actual.get(k)!=expected.get(k):
                    a=actual.get(k);b=expected.get(k)
                    differences.append({'section':k,'actual':a,'expected':b})
            c.write(C01/'catalog-exact-differences.json',differences)
            before=json.loads((C01/'compat-SQL-before.json').read_text())
            assert snapshot(db)==before['data']
            print(json.dumps({'actual':c.sha(canonical(actual).encode()),'expected':c.sha(canonical(expected).encode()),'different_sections':[x['section'] for x in differences],'business_unchanged':True}))
if __name__=='__main__':main()
