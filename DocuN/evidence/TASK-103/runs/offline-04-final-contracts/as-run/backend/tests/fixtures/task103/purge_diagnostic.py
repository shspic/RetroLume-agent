"""受控只读根诊断：已发生清理失败的本卡PG错误，不重放业务。"""
import json
import time
from .control import Control,EVIDENCE,atomic_json,redact
from .resources import OwnedDocker

def run():
 control=Control();control.reserve("entry",{"name":"purge-diagnostic"})
 start=time.monotonic();docker=OwnedDocker(control);resource=control.load()["resources"][0]
 docker.inspect(resource);docker.admin_dsn(resource)
 result=docker.cli(["logs","--tail","160",resource["cid"]])
 text=redact(result.stdout.decode("utf-8","replace")+result.stderr.decode("utf-8","replace"))
 lines=[x for x in text.splitlines() if "ERROR:" in x or "CONTEXT:" in x or "DETAIL:" in x]
 value={"kind":"只读既有错误诊断，非产品测试","lines":[x[:600] for x in lines[-16:]]}
 atomic_json(EVIDENCE/"purge-diagnostic.json",value)
 control.charge("real",time.monotonic()-start,{"name":"purge-diagnostic"})
 print(json.dumps(value,ensure_ascii=False))

if __name__=="__main__":run()

