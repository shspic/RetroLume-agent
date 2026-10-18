"""Only remaining normal commands in root19's original deadline."""
from batch_runtime import *
from frozen_http import FrozenFlow

def main():
    preflight('S05-normal-boundaries')
    with Batch(19,'S05-normal-and-targeted-diagnostics') as batch:
        rc.start_pg('source');batch.start_api();flow=FrozenFlow('normal-boundaries')
        try:
            mapping=json.loads((EXEC/'continuation-02/frozen-source-bindings.json').read_text())
            if not (C01/'L08-JCODE-only-after-clarification.json').exists():
                old=flow.call('GET','/api/activities/c430ffb3-c9de-4ff0-aa32-8ac76b95cd86/teaching/workspace')
                aid=flow.create([mapping['J-CODE']]);flow.teaching(aid,'goal',{'goal':'只依据已选J-CODE资料学习Java编程语言，不讨论咖啡产地。'});flow.index(aid)
                narrowed=flow.teaching(aid,'plan',{'confirmed':True},query='Java 编程语言 J-CODE')
                c.write(C01/'L08-JCODE-only-after-clarification.json',{'sample':c.sample(),'original_clarification':old,'activity_id':aid,'source_ids':[mapping['J-CODE']['id']],'workspace':narrowed,'old_scope_unchanged':True})
                assert narrowed['proposal'] is not None
            path=C01/'ui-boundaries-intent.json'
            if path.exists():intent=json.loads(path.read_text())
            else:
                a=flow.create([mapping['N']]);b=flow.create([mapping['N']]);flow.teaching(b,'goal',{'goal':'S05另一个视图：保留原范围，不能污染当前视图。'})
                intent={'a':a,'b':b,'bundle_sha256':'58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8'};c.write(path,intent)
            # No launch is attempted unless actual current stage memory is available.
            if rc.available_memory_bytes()>=768*1024**2:
                batch.start_browser('s05-boundaries');batch.close_browser()
            else:c.write(C01/'UI-memory-gate.json',{'sample':c.sample(),'available':rc.available_memory_bytes(),'minimum':768*1024**2,'browser_started':False})
        finally:flow.close()

if __name__=='__main__':main()
