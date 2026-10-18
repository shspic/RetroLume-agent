"""23514准确约束的014前向修正，保留旧NULL/零费tool与旧model检查组合。"""
import sys,json
from control import ROOT,HERE,event,guard,state,write
from runtime_control import dsn,metadata,PG_IMAGE
sys.path.insert(0,str(ROOT/'backend'))
import psycopg
from psycopg.rows import dict_row
guard()
for slot in ('source','compat'):
    row=next(r for r in state()['resources'] if r['id']=='pg-'+slot);actual=metadata(row['cid'])
    if actual['image']!=PG_IMAGE or not actual['running'] or actual['labels'].get('retrolume.task')!='TASK-117':raise RuntimeError('own_identity')
    with psycopg.connect(dsn(slot,'admin'),row_factory=dict_row) as connection:
        old=connection.execute("SELECT pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conname='activity_operations_max_output_tokens_check'").fetchone()['definition']
        if old!='CHECK ((max_output_tokens > 0))':raise RuntimeError('unexpected_column_check')
        connection.execute('ALTER TABLE public.activity_operations DROP CONSTRAINT activity_operations_max_output_tokens_check')
        connection.execute('ALTER TABLE public.activity_operations ADD CONSTRAINT activity_operations_max_output_tokens_check CHECK(max_output_tokens>=0)')
        event('grounded_014_constraint_repair',slot=slot,cid=row['cid'],before=old,after='CHECK ((max_output_tokens >= 0))',root_cause='真实23514 Embedding零输出与002列级检查冲突；kind_shape保持model正值/tool NULL/embedding0')
path=HERE/'compat-catalog-before014.json';before=json.loads(path.read_text(encoding='utf-8'))
# 旧约束正文已有002受信原文和两个实库修正前精确读值，不冒旧快照重新采样。
before.setdefault('additional_original_constraint_observations',[]).append({'conname':'activity_operations_max_output_tokens_check','definition':'CHECK ((max_output_tokens > 0))','basis':'修正前两精确CID实际读值，与001原始列检查相同；原初版snapshot不改写'})
write(HERE/'original-column-check-observation.json',before['additional_original_constraint_observations'][-1])
print('Exact output column check repaired on same CIDs; old rows and counters retained')
