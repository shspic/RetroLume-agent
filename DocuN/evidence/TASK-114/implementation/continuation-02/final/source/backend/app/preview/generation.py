"""显式生成、单键claim和原生OneCall；不在事务内等待模型或Docker。"""
from __future__ import annotations
import asyncio
from .business_contracts import HtmlRefusal, HtmlProfile, messages_for
from .compiler import runtime_identity
from .description import canonical


class HtmlGenerationService:
    def __init__(self, ledger, controller):
        self.ledger, self.controller = ledger, controller

    async def generate(self, aid, command, config, *, run_tag):
        if self.controller is None or not self.controller.available:
            raise HtmlRefusal("html_host_not_authorized", "交互组件尚未取得完整验证与终审票据",503)
        if not config.html_generation_layer.available or config.model_service is None:
            raise HtmlRefusal(config.html_generation_layer.reason or "html_not_configured",status=503)
        if self.controller.has_unconfirmed(aid):
            raise HtmlRefusal("cleanup_unconfirmed", "停止尚未确认，暂不能生成或再次打开")
        row = await self.ledger.accept_html_command(aid,command,runtime_identity()["renderer_sha256"],self.controller.config_sha256)
        if row["status"] != "accepted": return await self.ledger.read_html_command(aid,command.business_key)
        snapshot = await self.ledger.read_learning_snapshot(aid)
        if snapshot is None: raise HtmlRefusal("result_invalidated")
        tokens = min(config.html_output_tokens,4096,snapshot["max_output_tokens"],config.model_service.max_output_tokens_limit)
        profile = HtmlProfile(activity_id=aid,business_key=command.business_key,request_sha256=row["request_sha256"],
            context_sha256=row["context_sha256"],context_json=row["context_body"],renderer_sha256=row["renderer_sha256"],max_output_tokens=tokens)
        from app.capabilities.contracts import ModelCallRequest
        from app.capabilities.gateway import ControlledModelGateway
        from app.worker.one_call import OneCallInput,run_one_call
        from app.worker.session import SessionConfig
        request = ModelCallRequest(messages=messages_for(profile),max_output_tokens=tokens,allowed_tools=frozenset(),html_profile=profile)
        encoded = canonical(ControlledModelGateway(config.model_service)._build_payload(request)).encode("utf-8")
        if len(encoded)>min(snapshot["max_request_bytes"],config.model_service.max_request_bytes):
            raise HtmlRefusal("html_context_limit",status=413)
        OneCallInput(row["operation_id"],request,config.model_service).to_wire()
        session = SessionConfig()
        if config.model_service.timeout_seconds>session.request_timeout_seconds:
            raise HtmlRefusal("html_config_incompatible",status=503)
        if not await self.ledger.claim_html_command(aid,command.business_key):
            return await self.ledger.read_html_command(aid,command.business_key)
        task = asyncio.create_task(asyncio.to_thread(run_one_call,self.ledger,session,aid,"local-ui",row["operation_id"],request,
                                                  config.model_service,run_tag=run_tag))
        supervision=None;cancelled=False
        while True:
            try:
                supervision=await asyncio.shield(task);break
            except asyncio.CancelledError:
                cancelled=True
                if task.done():
                    try:supervision=task.result()
                    except Exception:pass
                    break
            except Exception:break
        await self.ledger.finish_html_supervision(aid,command.business_key,supervision)
        if cancelled:raise asyncio.CancelledError
        return await self.ledger.read_html_command(aid,command.business_key)
