"""准确披露排除项计数，保留首轮及初次保存检查。"""
import hashlib,json,os,pathlib,re,time
from datetime import datetime,timezone
from review_io import ROOT,OWN,sha,save
started=time.perf_counter();prior=json.loads((OWN/'delivery-check.json').read_text(encoding='utf-8'));state=json.loads((OWN/'start.json').read_text(encoding='utf-8'))
result=ROOT/'DocuN/results/TASK-101-result.md';assert sha(result)==prior['result_sha256']
old=(OWN/'first-audit-original.md').read_bytes();assert result.read_bytes().endswith(old)
prefixfile=OWN/'result-prefix.md';prefix=prefixfile.read_text(encoding='utf-8');assert '*' not in prefix
active=time.perf_counter()-state['monotonic'];assert active<10800
prefix=re.sub(r'至本次保存检查点主动[0-9.]+秒',f'至交付保存检查点主动{active:.3f}秒',prefix)
prefix=prefix.replace('本次保存另见delivery-check','保存与计数纠正另见delivery-check-v2')
targets=[pathlib.Path(re.sub(r':\d+$','',v)) for v in re.findall(r'\]\((D:/[^)]+)\)',prefix)]
assert all(p.is_file() or p.name=='delivery-check-v2.json' for p in targets)
data=prefix.encode('utf-8')+old;tmp=OWN/'count-correction-for-atomic-save.tmp';assert not tmp.exists();tmp.write_bytes(data);os.replace(tmp,result);prefixfile.write_text(prefix,encoding='utf-8')
saved=result.read_bytes();assert saved==data
final=json.loads((OWN/'final-identities.json').read_text(encoding='utf-8'));matched=[r for r in final['objects'] if r.get('match') is True];excluded=[r for r in final['objects'] if r.get('excluded_hash_only')]
assert len(matched)==2933 and len(excluded)==1 and excluded[0]['path'].endswith('result-header.md')
check={**prior,'at':datetime.now(timezone.utc).isoformat(),'result_bytes':len(saved),'result_sha256':sha(result),'new_prefix_bytes':len(prefix.encode('utf-8')),'original_suffix_exact':saved[-len(old):]==old,'original_suffix_sha256':hashlib.sha256(saved[-len(old):]).hexdigest(),'index_objects':2934,'independently_hashed_objects':2933,'excluded_objects':excluded,'new_prefix_link_count':len(targets),'active_seconds_at_final_save':active,'count_correction_seconds':time.perf_counter()-started,'prior_check_preserved':'delivery-check.json','correction':'初判索引总量2934不能称全部hash匹配；准确为2933匹配、作者header1项依合同排除。'}
save('delivery-check-v2.json',check);assert all(p.is_file() for p in targets)
print(json.dumps({'saved':str(result),'bytes':len(saved),'sha256':sha(result),'suffix_exact':check['original_suffix_exact'],'suffix_sha256':check['original_suffix_sha256'],'matched':len(matched),'excluded':len(excluded),'missing_links':[],'active_seconds':active},ensure_ascii=False,indent=2))
