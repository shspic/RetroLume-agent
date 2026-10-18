"""只复验新增真实PID/出生/父子链，不重跑已通过的Global互斥或模型。"""
import ctypes,json,os,secrets,sys
from ctypes import wintypes
from uuid import uuid4
from .control import CONTINUE_ROOT,batch,atomic,source_snapshot
from .resources import shell_env
from app.preview.host_job import HostJob,JobChild,job_name,child_lineage
from app.preview.process import birth


def main():
    if len(sys.argv)>1:
        print(json.dumps({"pid":os.getpid(),"birth":birth(os.getpid())["birth"]}),flush=True)
        sys.stdin.buffer.read(1);return
    folder=CONTINUE_ROOT/"lineage-functional-01";folder.mkdir(exist_ok=False)
    with batch("offline","c02-actual-python-launcher-lineage",maximum=30):
        source_snapshot(folder)
        with HostJob(job_name(str(uuid4()),secrets.token_hex(32),"CALL")) as job:
            child=JobChild([sys.executable,"-B","-u","-m","tests.fixtures.task111.c02_lineage_check","child"],job,env=shell_env())
            try:
                row=json.loads(child.stdout.readline(1024))
                proof=child_lineage(row["pid"],row["birth"],child.pid,child.birth["birth"])
                child.stdin.write(b"x");child.stdin.flush();out,err=child.communicate(timeout=5)
                if child.poll()!=0 or out or err:raise RuntimeError("lineage probe exit")
                atomic(folder/"result.json",{"status":"PASS_FUNCTIONAL_LOCAL","lineage":proof,"actual_ended":birth(row["pid"]),"primary_ended":birth(child.pid),"pipe_eof":child.stdout.read()==b"","job":job.finish(),"new_PG_renderer_Model":False})
            finally:child.close()
    print("actual launcher lineage and owned process ends passed")


if __name__=="__main__":main()
