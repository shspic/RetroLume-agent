"""续作组合：最终教学父/模板两次原生、真实正常控件/PG与停止原件。"""
import asyncio,json,os,time,traceback
from pathlib import Path
from .control import ROOT,EVIDENCE,CONTINUE_ROOT,reserve,atomic,event
from .core import Harness
from .c01_seeds import teaching_parent
from .http_matrix import HttpMatrix


async def verify(resource,built,folder):
    h=Harness(resource,built,folder);fresh={};problems=[]
    try:
        await h.controller.recover()
        assert not h.controller.blocked,"saved owner recovery unconfirmed"
        for kind,feedback in (("energy",False),("binomial",True)):
            aid,parent=await teaching_parent(h,kind,feedback)
            receipt,command=await h.generate(aid,parent,"C01 边界 二项概率 n0到20" if kind=="binomial" else "C01 机械能参数与图形")
            assert receipt["terminal_disposition"]=="succeeded",receipt
            fresh[kind]={"activity_id":aid,"parent":parent,"receipt":receipt,"command":command.model_dump()}
        atomic(folder/"native-final-template.json",fresh)
        from .c01_seeds import diagnostic_artifact
        diagnostic=[]
        for _ in range(4):diagnostic.append(await diagnostic_artifact(h,"energy"))
        atomic(folder/"diagnostic-fixtures.json",diagnostic)
    finally:await h.controller.close()
    # 数据库独立目标不放到UI正常之后；UI失败不能吞掉SQL拒绝原件。
    await pg_independent(resource,folder,fresh)
    matrix=HttpMatrix(resource,built,folder)
    try:
        matrix.start()
        cases=[]
        for kind,item in fresh.items():
            aid=item["activity_id"];base=f"/api/activities/{aid}/html"
            current=matrix.request("GET",base+"/commands/"+item["command"]["business_key"])
            assert current["artifact_id"]==item["receipt"]["artifact_id"]
            assert matrix.request("POST",base+"/commands",item["command"])["artifact_id"]==current["artifact_id"]
            matrix.request("POST",base+"/commands",{**item["command"],"focus":"不同焦点"},409)
            descriptor=matrix.request("GET",base+"/artifacts/"+current["artifact_id"])
            steps=[{"label":"高度 h","value":"3","expect":"58.8"},{"label":"高度 h","value":"0","expect":"0 J"},{"label":"质量 m","value":"0","expect":"0 J"}] if kind=="energy" else [
              {"label":"成功概率 p","value":"0.5","expect":"0.375"},{"label":"成功次数 k","value":"0","expect":"0.125"},{"label":"成功概率 p","value":"0","expect":"1"},
              {"label":"试验次数 n","value":"0","expect":"1"},{"label":"试验次数 n","value":"20","expect":"1"},{"label":"成功次数 k","value":"20","expect":"0"}]
            cases.append({"kind":kind,"activity_id":aid,"parent":item["parent"],"artifact_id":current["artifact_id"],"steps":steps})
        reserve("preview_reaper_validation_batches",{"purpose":"c01-normal-and-all-prepared-faults"})
        atomic(CONTINUE_ROOT/"reaper-combination.json",{"start_ns":time.monotonic_ns(),"deadline_ns":time.monotonic_ns()+1200*1000000000,"original_count":2,"number":3})
        matrix.browser(cases)
        from .c01_faults import verify_faults
        verify_faults(resource,built,folder,diagnostic,matrix)
        atomic(folder/"normal-result.json",{"normal_remote_ui":True,"teacher_exercise_feedback":True,"final_template":True,"all_g11":False})
    finally:matrix.close()


async def pg_independent(resource,folder,fresh):
    import psycopg
    from psycopg import sql
    negative=[]
    with psycopg.connect(resource["app"]) as conn:
        for table in ("html_artifacts","html_commands","html_preview_budgets","html_preview_sessions"):
            try:
                with conn.transaction():
                    conn.execute(sql.SQL("DELETE FROM public.{} WHERE false").format(sql.Identifier(table)))
                    raise AssertionError("unexpected direct DELETE grant")
            except psycopg.errors.InsufficientPrivilege:negative.append({"table":table,"action":"DELETE","sqlstate":"42501"})
        try:
            with conn.transaction():
                conn.execute("UPDATE public.html_artifacts SET artifact_body=artifact_body WHERE false");raise AssertionError("unexpected UPDATE grant")
        except psycopg.errors.InsufficientPrivilege:negative.append({"table":"html_artifacts","action":"UPDATE","sqlstate":"42501"})
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            for kind,item in fresh.items():
                cursor.execute("SELECT c.status,c.terminal_disposition,c.business_key::text,r.payload_sha256,a.artifact_sha256,a.body_sha256,o.state FROM html_commands c JOIN activity_operations o ON o.activity_id=c.activity_id AND o.operation_id=c.operation_id JOIN activity_operation_results r ON r.activity_id=o.activity_id AND r.operation_id=o.operation_id JOIN html_artifacts a ON a.activity_id=c.activity_id AND a.business_key=c.business_key WHERE c.activity_id=%s AND c.business_key=%s",(item["activity_id"],item["command"]["business_key"]))
                row=cursor.fetchone();assert row["status"]=="terminal" and row["state"]=="received" and row["payload_sha256"]==row["body_sha256"]
                atomic(folder/("commit-"+kind+".json"),row)
    atomic(folder/"sql-negative.json",negative)
