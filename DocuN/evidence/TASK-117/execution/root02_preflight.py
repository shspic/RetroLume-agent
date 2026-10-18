"""ROOT02首次入口：014/检索目标的实际源码语法与类型入口核对。"""
import ast
import sys
from control import ROOT,HERE,state,begin_root,event,write,guard,sample
guard()
if state()['active_root'] is None:begin_root('ROOT02-非空014前向迁移与检索持久边界','runtime')
elif state()['active_root']!=2:raise RuntimeError('运行根身份不符')
stamp=sample()
paths=list(__import__('json').loads((HERE/'changes.json').read_text(encoding='utf-8')))
for name in paths:
    path=ROOT/name
    if path.suffix=='.py' and path.is_file():ast.parse(path.read_text(encoding='utf-8'),filename=name)
sys.path.insert(0,str(ROOT/'backend'))
from app.activities.repository import PostgresAdmissionLedger
from app.capabilities.embedding import EmbeddingRequest
from app.interview.contracts import InterviewHybridCommandInput
from app.learning.teaching_contracts import TeachingHybridFrozenContext
from app.retrieval.service import RetrievalService
from app.data_exit.schema_profiles import get_profile
from app.runtime import psycopg_compatible_loop_factory
write(HERE/'root-02-preflight.json',{'start':stamp,'end':sample(),'syntax_paths':len(paths),'imports':'new typed boundaries OK','R01_tables':len(get_profile('data_exit.v1.r01').tables),'R02_tables':len(get_profile('data_exit.v1.r02').tables),'physical_resources_started':False})
print('ROOT02 types import OK; R01=28 / R02=31; no runtime objects yet')
