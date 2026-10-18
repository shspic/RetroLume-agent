"""每次子步骤新Python加载；专库凭据仅继承Env，无日志/argv明文。"""
import asyncio,json,os,sys,traceback
from pathlib import Path
from .control import ROOT,PERMIT,atomic,source_snapshot,event
from app.runtime import psycopg_compatible_loop_factory


async def native(resource,built,folder):
    from .control import CONTINUE_ROOT
    from .core import Harness
    from .c01_seeds import teaching_parent
    h=Harness(resource,built,folder);fresh={};progress_path=CONTINUE_ROOT/"native-progress.json"
    progress=json.loads(progress_path.read_text(encoding="utf-8")) if progress_path.exists() else {}
    def save_native():
        # 协调者既有Windows本地编码读取仅消费ASCII JSON；内容语义不变。
        (folder/"native-final-template.json").write_text(json.dumps(fresh,ensure_ascii=True,sort_keys=True,indent=2),encoding="utf-8")
    try:
        await h.controller.recover()
        if h.controller.blocked:raise RuntimeError("saved owner recovery unconfirmed")
        for kind,feedback in (("energy",False),("binomial",True)):
            if kind in progress:
                aid,parent=progress[kind]["activity_id"],progress[kind]["parent"]
                if progress[kind].get("receipt"):
                    fresh[kind]=progress[kind];save_native();continue
            else:
                aid,parent=await teaching_parent(h,kind,feedback)
                progress[kind]={"activity_id":aid,"parent":parent};atomic(progress_path,progress)
            atomic(folder/("parent-"+kind+".json"),{"activity_id":aid,"parent":parent})
            receipt,command=await h.generate(aid,parent,"C01 边界 二项概率 n0到20" if kind=="binomial" else "C01 机械能参数与图形")
            fresh[kind]={"activity_id":aid,"parent":parent,"receipt":receipt,"command":command.model_dump()}
            progress[kind]=fresh[kind];atomic(progress_path,progress)
            save_native()
            if receipt["terminal_disposition"]!="succeeded":raise RuntimeError("final native did not succeed: "+receipt["terminal_disposition"])
    finally:await h.controller.close()


def main():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("fixture permit")
    folder=Path(sys.argv[2]).resolve();action=sys.argv[1]
    from .control import CONTINUE_ROOT
    if not folder.is_relative_to(CONTINUE_ROOT.resolve()):raise RuntimeError("step evidence path")
    resource=json.loads(os.environ["RETROLUME_TASK111_RESOURCE"])
    build_path=CONTINUE_ROOT/"active-build.json"
    if not build_path.exists():build_path=ROOT/"DocuN/evidence/TASK-111/execution/real-01/production-build.json"
    built=json.loads(build_path.read_text(encoding="utf-8"))
    source_snapshot(folder)
    from .runtime import install
    install()
    try:
        if action=="native":
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(native(resource,built,folder))
        elif action=="pg":
            from .c02_pg import verify
            verify(resource,folder)
        elif action=="diagnostic":
            from .core import Harness
            from .c01_seeds import diagnostic_artifact
            async def prepare():
                h=Harness(resource,built,folder)
                try:
                    await h.controller.recover();rows=[]
                    for _ in range(4):rows.append(await diagnostic_artifact(h,"energy"))
                    atomic(folder/"diagnostic-fixtures.json",rows)
                finally:await h.controller.close()
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(prepare())
        else:raise RuntimeError("fixed step action")
        atomic(folder/"step-result.json",{"status":"PASS_STEP_ONLY","action":action})
    except Exception:
        # traceback不附bound SQL/Env；仍去除本卡DSN值，保持失败事实。
        failure=traceback.format_exc()
        for value in (resource.get("admin",""),resource.get("app",""),resource.get("denied","")):
            if value:failure=failure.replace(value,"[redacted-task-dsn]")
        (folder/"failure.txt").write_text(failure,encoding="utf-8")
        atomic(folder/"step-result.json",{"status":"FAIL","action":action});raise SystemExit(1)


if __name__=="__main__":main()
