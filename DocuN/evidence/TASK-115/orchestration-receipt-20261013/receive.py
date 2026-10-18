"""只读核报告、审计原件及冻结产品；不重跑反例或导入产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
AUDIT=ROOT/'DocuN/evidence/TASK-115/audit'


def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def info(path):
    raw=path.read_bytes()
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


delivery=load(AUDIT/'delivery.json')
report=ROOT/'DocuN/results/TASK-115-result.md'
assert info(report)=={k:delivery['report'][k] for k in ('bytes','sha256')}
for entry in delivery['evidence']:
    assert info(Path(entry['path']))=={k:entry[k] for k in ('bytes','sha256')},entry['path']
frozen=load(ROOT/'DocuN/evidence/TASK-114/implementation/continuation-01/final/manifest.json')
for entry in frozen:
    path=ROOT/entry['path']
    if entry['change']=='deleted_build_output':assert not path.exists()
    else:assert info(path)=={k:entry[k] for k in ('bytes','sha256')},entry['path']
rules=load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for entry in rules:assert info(Path(entry['absolute_path']))['sha256']==entry['sha256']
counterexamples=[]
for relative in ('offline/attempt-03/01-restore-cancel-overwritten.json','offline/attempt-03/02-publish-after-accepted-cancel.json','offline/attempt-03/04-upload-after-accepted-cancel.json','offline/attempt-03/05-post-capture-operation-deadline.json','browser/late-only/result.json','offline/readonly-projection-input-02.json'):
    path=AUDIT/relative
    counterexamples.append({'path':str(path),**info(path)})
record={'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'TASK':'TASK-115','R':'R-109','report':{'path':str(report),**info(report)},'audit_evidence_hashes_checked':len(delivery['evidence']),'current_and_saved_frozen_identity':'216当前文件+1移除登记与C01一致','rules_checked':len(rules),'delivery':{k:delivery[k] for k in ('protected_file_count','current_file_count','active_seconds_conservative','new_counts')},'counterexample_inputs':counterexamples,'accepted_audit_conclusion':'四项P1成立；前三项精确补证分层，F04代码反例动态未运行。审计交付接受，产品不通过。','defect_mapping':{'F01':'DEF-034','F02':'DEF-035','F03':'DEF-036','F04':'DEF-037'},'product_runs':0}
(OUT/'received.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report_match':True,'evidence':len(delivery['evidence']),'frozen_current':216,'removed':1,'rules':len(rules),'four_P1':True,'product_runs':0},ensure_ascii=False))
