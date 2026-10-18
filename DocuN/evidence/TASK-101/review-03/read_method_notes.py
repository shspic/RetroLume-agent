from audit_io import *
raw=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
notes=load(raw/'method-applicability.json')
print(json.dumps(notes, ensure_ascii=False,indent=2))
