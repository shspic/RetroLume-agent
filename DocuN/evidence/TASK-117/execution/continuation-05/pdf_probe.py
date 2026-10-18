"""S06 bounded observation of the real PDF path; no text, env values or changed results."""
import sys,os,time,json,hashlib,ctypes
from pathlib import Path
def install():
    if os.environ.get('RETROLUME_TASK117_SYNTHETIC')!='TASK-117-STEP018-INTEGRATION-S06-20261016':return
    import app.pdf_import as package
    from app.pdf_import import supervisor as s,_windows_job as w
    original_parse=s.parse_pdf_bytes;original_build=s._build_worker_command;original_config=w._configure_signatures
    rows=[];current={}
    def configure(kernel):
        original_config(kernel)
        for name in ('CreateJobObjectW','SetInformationJobObject','CreateProcessW','AssignProcessToJobObject','ResumeThread','WaitForSingleObject','GetExitCodeProcess','TerminateJobObject'):
            original=getattr(kernel,name)
            def observed(*args,_original=original,_name=name):
                start=time.monotonic_ns();result=_original(*args)
                if len(rows)<24:rows.append({'stage':_name,'result':result,'last_error':ctypes.get_last_error(),'elapsed_seconds':(time.monotonic_ns()-start)/1e9,'mono_ns':time.monotonic_ns()})
                return result
            setattr(kernel,name,observed)
    def build(input_path,output_path,limits):
        command=original_build(input_path,output_path,limits);current['output']=output_path
        current['command']={'interpreter':sys.executable,'interpreter_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),'argv_shape':[command[0],'-m','app.pdf_import.worker','--input','<temp-input>','--output','<temp-output>',*command[7:]],'worker_module_matches_fixture_exclusion':command[2]=='app.pdf_import.worker','global_trace_enabled':sys.gettrace() is not None,'timeout_seconds':limits.timeout_seconds,'process_memory_bytes':limits.process_memory_bytes}
        return command
    original_run=s.run_in_job
    def job(*args,**kwargs):
        try:
            result=original_run(*args,**kwargs);current['job_result']={'exit_code':result.exit_code,'elapsed_seconds':result.elapsed_seconds};return result
        finally:
            output=current.get('output');exists=bool(output and output.is_file());current['output_observation']={'exists':exists,'bytes':output.stat().st_size if exists else 0}
            if exists:
                try:
                    payload=json.loads(output.read_text(encoding='utf-8'));current['output_observation'].update(ok=payload.get('ok'),envelope_error_code=(payload.get('error') or {}).get('code'))
                except Exception as error:current['output_observation']['decode_error_type']=type(error).__name__
    def parse(data,**kwargs):
        rows.clear();current.clear();start=time.monotonic_ns();current.update(parse_entered=True,input_sha256=hashlib.sha256(data).hexdigest(),input_bytes=len(data),pid=os.getpid())
        try:
            result=original_parse(data,**kwargs);current.update(result='success',physical_pages=result.page_count,manual_review_required=True);return result
        except Exception as error:
            current.update(result='error',error_type=type(error).__name__,error_code=getattr(error,'code',None));raise
        finally:
            current.update(elapsed_seconds=(time.monotonic_ns()-start)/1e9,job_stages=list(rows),no_text_or_private_env_recorded=True)
            Path(__file__).with_name('PDF-HTTP-bounded-probe.json').write_text(json.dumps({k:v for k,v in current.items() if k!='output'},indent=2)+'\n',encoding='utf-8')
    w._configure_signatures=configure;s._build_worker_command=build;s.run_in_job=job;s.parse_pdf_bytes=parse;package.parse_pdf_bytes=parse
    # If an ordinary import already bound the entry, preserve that exact entry with observation.
    api=sys.modules.get('app.materials.api')
    if api is not None:api.parse_pdf_bytes=parse
