"""固定第二Reaper验证批的公开链与持久权限/兼容矩阵；任何失败保原件。"""
from __future__ import annotations
import asyncio
import json
import os
from pathlib import Path
import time
from uuid import uuid4
import psycopg
from psycopg import sql
from .control import ROOT,EVIDENCE,reserve,event,atomic,state
from .http_matrix import HttpMatrix
from app.preview.description import canonical


def verify(resource,built,folder,native_results):
    native=json.loads(Path(native_results).read_text(encoding="utf-8"));matrix=HttpMatrix(resource,built,folder)
    reserve("preview_reaper_validation_batches",{"purpose":"public-normal-and-fault-complete"})
    deadline=time.monotonic()+1200;atomic(folder/"reaper-batch.json",{"start_ns":time.monotonic_ns(),"deadline_ns":int(deadline*1e9),"max_preview_creates":14})
    try:
        matrix.start()
        cases=[]
        for kind in ("energy","binomial"):
            item=native[kind];aid=item["activity_id"];base=f"/api/activities/{aid}/html"
            receipt=matrix.request("GET",base+"/commands/"+item["command"]["business_key"])
            assert receipt["artifact_id"]==item["receipt"]["artifact_id"]
            # 同键POST只核原已提交身份，不能再次发送model或创建容器。
            assert matrix.request("POST",base+"/commands",item["command"])["artifact_id"]==receipt["artifact_id"]
            changed={**item["command"],"focus":"另一个输入"};matrix.request("POST",base+"/commands",changed,409)
            artifact=matrix.request("GET",base+"/artifacts/"+receipt["artifact_id"])
            assert "compiled_html" not in canonical(artifact) and "script" not in artifact
            steps=[{"label":"高度 h","value":"3","expect":"58.8"},{"label":"高度 h","value":"0","expect":"0 J"}] if kind=="energy" else [
             {"label":"成功次数 k","value":"2","expect":"0.375"},{"label":"成功概率 p","value":"1","expect":"0"}]
            cases.append({"kind":kind,"activity_id":aid,"operation_id":item["parent"]["operation_id"],"artifact_id":receipt["artifact_id"],"steps":steps})
        matrix.browser(cases)
        negative=[]
        with psycopg.connect(resource["app"]) as conn:
            for table in ("html_artifacts","html_commands","html_preview_budgets","html_preview_sessions"):
                try:
                    with conn.transaction():
                        conn.execute(sql.SQL("DELETE FROM public.{} WHERE false").format(sql.Identifier(table)))
                        raise AssertionError("direct DELETE privilege exists")
                except psycopg.errors.InsufficientPrivilege:negative.append({"table":table,"action":"DELETE","denied":True})
            try:
                with conn.transaction():conn.execute("UPDATE public.html_artifacts SET artifact_body=artifact_body WHERE false");raise AssertionError("direct artifact UPDATE privilege exists")
            except psycopg.errors.InsufficientPrivilege:negative.append({"table":"html_artifacts","action":"UPDATE","denied":True})
        atomic(folder/"sql-negative.json",negative)
        if time.monotonic()>deadline:raise RuntimeError("TASK111 Reaper validation deadline")
        atomic(folder/"matrix-result.json",{"normal_public_ui":True,"sql_direct_dml_denied":True,"remaining_high_risk":"fault/race/upgrade/stop branches require their own actual raw coverage","complete_g11":False})
    finally:matrix.close()
