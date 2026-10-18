"""只交付本次授权的报告前缀和元数据，保留首轮原字节后缀。"""
from pathlib import Path
import sys,json,hashlib,time,datetime,re,decimal
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent');OUT=Path(__file__).resolve().parent
REPORT=ROOT/'DocuN/results/TASK-112-result.md'
BASE_SHA='ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522'
ANCHOR=1037597155786300;PRIOR=decimal.Decimal('3347.3488145');D=decimal.Decimal
def sha(b):return hashlib.sha256(b).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def log(name,value):
    with (OUT/name).open('a',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False)+'\n')
def read(p):
    b=p.read_bytes();log('reads.jsonl',dict(utc=utc(),mono_ns=time.perf_counter_ns(),path=str(p),bytes=len(b),sha256=sha(b),purpose='最终交付元数据及原字节校验'));return b
def obj(name):return json.loads(read(OUT/name))
log('commands.jsonl',dict(utc=utc(),mono_ns=time.perf_counter_ns(),argv=sys.argv,scope='授权结果前缀拼接、复读和交付元数据，无业务运行'))
start=obj('frozen-start.json');end=obj('frozen-end.json')
assert len(start)==len(end)==379 and all(r['match'] for r in start+end)
assert {r['path']:r['actual'] for r in start}=={r['path']:r['actual'] for r in end}
for name in ('seven-stops-independent.json','fixture-as-run-independent.json','live-packets-and-gates-independent.json','execution-budget-independent.json','phase-and-offline-independent.json'):
    assert obj(name)['failures']==[],name
diffs=obj('actual-diff-verification.json');assert len(diffs)==5 and all(r['pre_matches'] and r['post_matches'] and r['diff_text_equal_after_CRLF_normalization'] for r in diffs)
load=obj('load-manifest-independent.json');assert load['count']==651 and load['mismatches']==[]
original=read(OUT/'TASK-112-original-result.md');current=read(REPORT)
assert len(original)==36048 and sha(original)==BASE_SHA and current==original,'原报告漂移，不覆盖'
template=read(OUT/'review-01-prefix-template.md').decode('utf-8').replace('/D:/','D:/')
assert '*' not in template and not re.search(r'^\s*\|',template,re.M),'新增正文不得用星号或Markdown表格'
links=re.findall(r'\]\((D:/[^)]+)\)',template)
for link in links:
    target=re.sub(r':\d+$','',link)
    if target.endswith('/delivery-receipt.json'):continue
    assert Path(target).is_file(),target
now=time.perf_counter_ns();review=D(now-ANCHOR)/D(10**9);cumulative=PRIOR+review
assert review<D(7200) and cumulative<D(10800),'达到审计时限，停止依赖判断'
fields=dict(SAVE_UTC=utc(),SAVE_MONO=str(now),REVIEW_SECONDS=str(review),CUMULATIVE_SECONDS=str(cumulative),REVIEW_REMAINING=str(D(7200)-review),CUMULATIVE_REMAINING=str(D(10800)-cumulative))
for k,v in fields.items():template=template.replace('{{'+k+'}}',v)
assert '{{' not in template
prefix=template.encode('utf-8');(OUT/'review-01-prefix.md').write_bytes(prefix)
composed=prefix+b'\n\n'+original
REPORT.write_bytes(composed)
verified=read(REPORT);assert verified==composed and verified[-36048:]==original and sha(verified[-36048:])==BASE_SHA
final_ns=time.perf_counter_ns();final_review=D(final_ns-ANCHOR)/D(10**9);final_cumulative=PRIOR+final_review
assert final_review<D(7200) and final_cumulative<D(10800)
reads=[json.loads(l) for l in (OUT/'reads.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()];commands=[json.loads(l) for l in (OUT/'commands.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
receipt=dict(task='TASK-112',r='R-106',review='review-01',permit='TASK-112-G11-REVIEW01-20261012',conclusion=dict(DEF_031='关闭',DEF_032='关闭',DEF_033='关闭',E112_01='漏计账段一次核销；历史超限626.566秒保留',code_axis='本次限域通过',evidence_axis='本次对应原件成立，继承首轮限域结论',control_axis='本次前向账务/计数/清场成立；历史整体合规不签通过',G11='具备交编排关闭既定有限切片条件，未代签最终验收'),start_utc='2026-10-12T00:48:53.3841165Z',start_mono_ns=ANCHOR,report_save_sample=fields,final_readback_utc=utc(),final_readback_mono_ns=final_ns,review_observed_seconds=str(final_review),prior_observed_seconds=str(PRIOR),cumulative_observed_seconds=str(final_cumulative),review_cap_seconds=7200,cumulative_cap_seconds=10800,remaining_review_seconds=str(D(7200)-final_review),remaining_cumulative_seconds=str(D(10800)-final_cumulative),prior_preclock_preparation='unknown，不重置不填0',business_operations=0,model='Codex desktop，基于GPT-6；精确后缀和推理档未暴露，A+为责任标签',independence='原审计会话接续，未参与C07修复/未继承工程聊天或思考/无子Agent，无可核窗口ID',original_report=dict(bytes=36048,sha256=BASE_SHA,exact_suffix_preserved=True,suffix_offset=len(prefix)+2),report=dict(path=str(REPORT),bytes=len(verified),sha256=sha(verified)),prefix=dict(path=str(OUT/'review-01-prefix.md'),bytes=len(prefix),sha256=sha(prefix)),frozen_objects=dict(start=379,end=379,all_match=True,report_mutation='身份校验后按本卡明确授权置顶，原输入字节仍为完整后缀'),read_records=len(reads),unique_read_paths=len({r['path'] for r in reads}),metadata_command_records=len(commands),source_diff_count=5,load_objects=651,new_sessions=7,valid_final_local_links=len(links),only_write_scope=[str(REPORT),str(OUT)],checked_evidence=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted(OUT.glob('*.json')) if p.name!='delivery-receipt.json'])
(OUT/'delivery-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
saved=json.loads(read(OUT/'delivery-receipt.json'));assert saved['report']['sha256']==sha(REPORT.read_bytes()) and saved['original_report']['exact_suffix_preserved']
print(json.dumps(dict(saved=str(REPORT),report_bytes=len(verified),report_sha256=sha(verified),suffix_bytes=36048,suffix_sha256=BASE_SHA,suffix_verified=True,review_seconds=str(final_review),cumulative_seconds=str(final_cumulative),frozen_count=379,metadata_commands=len(commands),unique_read_paths=receipt['unique_read_paths']),ensure_ascii=False,indent=2))
