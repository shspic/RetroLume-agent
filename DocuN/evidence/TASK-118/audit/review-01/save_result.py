"""Prepend this independent review and preserve the exact original audit suffix."""
import datetime as dt,hashlib,json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');R=Path('D:/shspic/project_NO3_RetroLume-agent');O=R/'DocuN/evidence/TASK-118/audit/review-01';target=R/'DocuN/results/TASK-118-result.md'
old=(O/'original-TASK118-result.bytes').read_bytes();expected='dd0a5f1d2ddb2ffcd9a168496e4cca5b8292b7221977c76b8ff417f9ff0f21f1'
assert len(old)==41590 and hashlib.sha256(old).hexdigest()==expected
prefix=(O/'result-prefix.md').read_bytes();existing=target.read_bytes()
assert existing==old or existing==prefix+old,'independent result changed outside this save'
target.write_bytes(prefix+old);actual=target.read_bytes();full=actual.decode('utf-8');new=prefix.decode('utf-8')
assert actual==prefix+old and actual.endswith(old)
missing=[]
for link in re.findall(r'\]\((D:/[^)]+)\)',full):
 p=re.sub(r':\d+$','',link)
 if p.endswith('/review-execution-receipt.json'):continue
 if not Path(p).exists():missing.append(p)
result={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'path':str(target),'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),'full_utf8_readback':True,
 'review_prefix_bytes':len(prefix),'review_prefix_sha256':hashlib.sha256(prefix).hexdigest(),'old_audit_exact_suffix':True,'old_audit_bytes':len(old),'old_audit_sha256':hashlib.sha256(old).hexdigest(),
 'four_closure_recommendations':all(s in new for s in ['D01 原 P1：建议关闭','D02 原 P1、仅未来 Q','D03 原 P2：建议关闭','D04 原 P2：建议关闭']),
 'three_axes_and_Q_separate':all(s in new for s in ['代码轴：','证据轴：','执行控制轴：','Q 继续冻结','完整多步 Q 请求批准机制尚待明确']),
 'no_asterisks':not '*' in full,'missing_local_links':missing,'product_writes':0}
(O/'result-readback.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
