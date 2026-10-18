"""C02有据合并离线根入口，保留每次FAIL和as-run。"""
import os
from pathlib import Path
import sys
import time
from budget import Budget, ROOT, EVIDENCE
from freeze import freeze

budget=Budget();budget.root('c02-boundary-group')
label='c02-boundaries-'+str(time.monotonic_ns())
os.environ['C02_CASE_ATTEMPT']=label
freeze(label)
os.environ['RETROLUME_TASK114_SCRATCH']=str(EVIDENCE/'synthetic/scratch/c02-offline')
Path(os.environ['RETROLUME_TASK114_SCRATCH']).mkdir(parents=True,exist_ok=True)
code=budget.offline(label,[str(ROOT/'backend/.venv/Scripts/python.exe'),'-B','-X','utf8',str(ROOT/'backend/tests/test_data_exit_c02.py'),*sys.argv[1:]],timeout=25)
raise SystemExit(code)
