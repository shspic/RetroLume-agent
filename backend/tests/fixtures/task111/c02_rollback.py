"""强制HTML hook在写产物/terminal后异常，真实record事务整笔回滚。"""
import asyncio,json
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from .control import CONTINUE_ROOT,atomic,event
from .core import Harness
from .samples import energy
from app.preview.business_contracts import HtmlCommand,HtmlProfile,HtmlCallBinding
from app.preview.compiler import runtime_identity
from app.preview.description import canonical,load_json
from app.preview.model_policy import stored_result
from app.preview.repository import plain
from app.capabilities.contracts import AdmissionIntent,CallContext,Provider,LedgerOutcome,LedgerDisposition,build_business_payload
from app.runtime import psycopg_compatible_loop_factory


class ForcedHookError(RuntimeError):pass


def verify(resource,folder):
    built=json.loads((CONTINUE_ROOT/"active-build.json").read_text(encoding="utf-8"))
    async def run():
        h=Harness(resource,built,folder)
        try:
            await h.controller.recover()
            aid,parent=await h.parent("energy")
            command=HtmlCommand(business_key=str(uuid4()),parent=parent,focus="回滚合成前提，不发传输",expected_config_sha256=h.controller.config_sha256,confirmed=True)
            row=await h.ledger.accept_html_command(aid,command,runtime_identity()["renderer_sha256"],h.controller.config_sha256)
            profile=HtmlProfile(activity_id=aid,business_key=command.business_key,request_sha256=row["request_sha256"],context_sha256=row["context_sha256"],context_json=row["context_body"],renderer_sha256=row["renderer_sha256"],max_output_tokens=4096)
            assert await h.ledger.claim_html_command(aid,command.business_key)
            catalog=load_json(profile.context_json)["catalog"];stored=stored_result(canonical(energy(catalog[0]["citation_id"])),profile);fmt,payload,sha=build_business_payload(json_object=stored)
            lease=await h.ledger.claim_lease(aid,"task111-c02-rollback",lease_seconds=20,window_seconds=30);assert lease
            binding=HtmlCallBinding(business_key=profile.business_key,request_sha256=profile.request_sha256,context_sha256=profile.context_sha256,renderer_sha256=profile.renderer_sha256)
            permit=await h.ledger.admit(AdmissionIntent(context=CallContext(activity_id=aid,operation_id=row["operation_id"],executor_id="task111-c02-rollback",execution_generation=lease.execution_generation,scope_revision=lease.scope_revision),provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,configured_model="task111-synthetic",request_bytes=100,max_output_tokens=4096,tool_names=(),html_binding=binding))
            await h.ledger.mark_dispatch_started(permit)
            def snapshot():
                with psycopg.connect(resource["app"],row_factory=dict_row) as conn:
                    return plain({"operation":conn.execute("SELECT * FROM activity_operations WHERE activity_id=%s AND operation_id=%s",(aid,row["operation_id"])).fetchone(),
                      "command":conn.execute("SELECT status,terminal_disposition FROM html_commands WHERE activity_id=%s AND business_key=%s",(aid,command.business_key)).fetchone(),
                      "result_count":conn.execute("SELECT count(*) AS n FROM activity_operation_results WHERE activity_id=%s AND operation_id=%s",(aid,row["operation_id"])).fetchone()["n"],
                      "artifact_count":conn.execute("SELECT count(*) AS n FROM html_artifacts WHERE activity_id=%s AND business_key=%s",(aid,command.business_key)).fetchone()["n"]})
            before=snapshot();atomic(folder/"hook-before.json",before);original=h.ledger._write_html_outcome
            async def fail_after(*args,**kwargs):
                await original(*args,**kwargs);raise ForcedHookError("fixed exception after actual HTML producer writes")
            h.ledger._write_html_outcome=fail_after
            try:
                try:
                    await h.ledger.record_outcome(permit,LedgerOutcome(disposition=LedgerDisposition.RECEIVED,payload_format=fmt,payload=payload,payload_sha256=sha,remote_request_id="task111-frozen-hook-fixture",returned_model="task111-synthetic",finish_reason="stop",prompt_tokens=0,completion_tokens=0,response_bytes=len(payload.encode())))
                    raise RuntimeError("forced hook did not fail")
                except ForcedHookError:pass
            finally:h.ledger._write_html_outcome=original
            after=snapshot();atomic(folder/"hook-after.json",after)
            if before!=after or after["result_count"] or after["artifact_count"]:raise RuntimeError("hook transaction partially committed")
            await h.ledger.record_outcome(permit,LedgerOutcome(disposition=LedgerDisposition.UNKNOWN,error_code="task111_forced_hook_failure"))
            unknown=snapshot();atomic(folder/"hook-unknown.json",unknown)
            if unknown["command"]["terminal_disposition"]!="unknown" or unknown["artifact_count"] or unknown["result_count"]:raise RuntimeError("unknown repair produced artifact")
            await h.ledger.begin_window_close(aid,"task111-c02-rollback",lease.execution_generation)
            await h.ledger.settle_execution_window(aid,"task111-c02-rollback",lease.execution_generation,window_seconds=30,elapsed_seconds=0)
            atomic(folder/"hook-result.json",{"status":"PASS_REAL_TRANSACTION_ROLLBACK_AND_UNKNOWN_NO_ARTIFACT","activity_id":aid,"operation_id":row["operation_id"],"no_transport_or_OneCall":True,"not_a_model_quality_claim":True})
        finally:await h.controller.close()
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(run())
