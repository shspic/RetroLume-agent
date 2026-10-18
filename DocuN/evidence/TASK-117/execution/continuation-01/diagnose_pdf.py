"""只诊断冻结PDF及实际受限worker；不启动PG/API，不放宽Job限制。"""
from batch_runtime import *
import sysconfig,traceback
from app.pdf_import import parse_pdf_bytes,PdfImportError
from app.pdf_import.worker import _extract
root=next(r for r in c.state()['roots'] if r['id']==8)
if time.monotonic_ns()>=root['business_deadline_mono_ns']:raise RuntimeError('ROOT08_original_deadline_closed')
stamp=c.sample();p=C01/'root08-inputs/PDF-2.pdf';raw=p.read_bytes()
proof={'sample':stamp,'sha256':c.sha(raw),'local_extract':_extract(raw,50,2*1024**2),'worker_executable':sys.executable,'base_executable':sys._base_executable}
os.environ['PYTHONPATH']=os.pathsep.join([str(ROOT/'backend/tests/fixtures/step018'),str(ROOT/'backend'),sysconfig.get_paths()['purelib']])
os.environ['RETROLUME_TASK117_SYNTHETIC']=c.state()['active_segment']
c.count('native_windows',2) # 补记原HTTP PDF受限worker一次＋本次实际受限worker一次；保守不减原计数。
try:
    result=parse_pdf_bytes(raw);proof['worker_result']={'pages':result.page_count,'texts':[p.text for p in result.pages]}
except PdfImportError as exc:proof['worker_error']={'type':type(exc).__name__,'code':exc.code,'message':str(exc)[:300]}
c.write(C01/'pdf-launch-diagnosis.json',proof)
value=c.state();end=c.sample();value['offline_intervals'].append({'root':8,'segment':value['active_segment'],'start_mono_ns':stamp['mono_ns'],'end_mono_ns':end['mono_ns'],'seconds':(end['mono_ns']-stamp['mono_ns'])/1e9,'basis':'ROOT08原截止内；PG/API均停止时同冻结PDF的字节/受限worker诊断'})
c.write(EXEC/'budget.json',value)
print(json.dumps(proof,ensure_ascii=False))
