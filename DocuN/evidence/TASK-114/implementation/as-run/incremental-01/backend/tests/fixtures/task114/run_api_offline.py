import os
from budget import ROOT,Budget
os.environ['RETROLUME_TASK114_SYNTHETIC']=str(ROOT/'DocuN/evidence/TASK-114/synthetic')
raise SystemExit(Budget().offline('api-boundaries-01',[str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(ROOT/'backend/tests/test_data_exit_api.py')]))
