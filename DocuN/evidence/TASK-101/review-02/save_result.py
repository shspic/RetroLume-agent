"""保存获准审计报告；历史按原字节尾段保留。"""
import hashlib,json,os,pathlib,re,time
from datetime import datetime,timezone
from review_io import ROOT,OWN,sha,save
started=time.perf_counter()
state=json.loads((OWN/'start.json').read_text(encoding='utf-8'))
final=json.loads((OWN/'final-identities.json').read_text(encoding='utf-8'))
assert len(final['objects'])==2934 and not any(v.get('match') is False for v in final['objects'])
result=ROOT/'DocuN/results/TASK-101-result.md';old=OWN/'first-audit-original.md';prefixfile=OWN/'result-prefix.md'
assert sha(result)==sha(old)==state['old_report_sha256']
assert old.stat().st_size==state['old_report_bytes']==39114
prefix=prefixfile.read_text(encoding='utf-8')
assert '*' not in prefix and '__AUDIT_USAGE__' in prefix
helper=[json.loads(line) for line in (OWN/'helpers.jsonl').read_text(encoding='utf-8').splitlines()]
known=sum(v['seconds'] for v in helper)
active=time.perf_counter()-state['monotonic']
assert active<10800 and known<600
usage=(f'本轮从首核后登记的固定单调时点2026-10-05T12:29:39.338110+00:00起，至本次保存检查点主动{active:.3f}秒（含续执行期间同一窗口时间，未清零）。'
       f'已登记纯辅助实际执行累计{known:.3f}秒/{len(helper)}条完成记录；本次保存另见delivery-check。'
       '首读shell约1.0秒、计时前采样段及未逐次登记的shell启动/聚合开销保留未知，不把已登记值冒称精确全量。'
       '新增许可为主动10800/元数据600秒；没有新增业务或资源运行，未借旧许可余额。')
prefix=prefix.replace('__AUDIT_USAGE__',usage)
prefixfile.write_text(prefix,encoding='utf-8')
targets=[]
for raw in re.findall(r'\]\((D:/[^)]+)\)',prefix):
    name=re.sub(r':\d+$','',raw);targets.append(pathlib.Path(name))
missing=[str(p) for p in targets if not p.is_file() and p.name!='delivery-check.json']
assert not missing,missing
prefix_bytes=prefix.encode('utf-8');original=old.read_bytes();complete=prefix_bytes+original
temporary=OWN/'result-for-atomic-save.tmp'
assert not temporary.exists()
temporary.write_bytes(complete);os.replace(temporary,result)
saved=result.read_bytes();tail=saved[len(prefix_bytes):]
assert tail==original and hashlib.sha256(tail).hexdigest()==state['old_report_sha256']
assert saved.decode('utf-8').startswith('# TASK-101 / R-095 review-02')
delivery={'at':datetime.now(timezone.utc).isoformat(),'result':str(result),'result_bytes':len(saved),'result_sha256':sha(result),'new_prefix_bytes':len(prefix_bytes),'original_suffix_bytes':len(tail),'original_suffix_sha256':hashlib.sha256(tail).hexdigest(),'original_suffix_exact':tail==original,'new_prefix_asterisks':prefix.count('*'),'new_prefix_link_count':len(targets),'new_prefix_missing_links':[],'last_identity_match_count':sum(v.get('match') is True for v in final['objects']),'active_seconds_at_save':active,'known_helper_seconds_before_save':known,'completed_helper_records_before_save':len(helper),'save_check_seconds':time.perf_counter()-started,'business_resource_counts':state['resource_counts'],'local_result_saved_readable':True,'limits':'首读采样和未逐次登记shell开销为未知项；本轮未进行新业务运行；保存不表示编排验收。'}
save('delivery-check.json',delivery)
assert all(p.is_file() for p in targets)
print(json.dumps(delivery,ensure_ascii=False,indent=2))
