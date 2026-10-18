"""真实app/HTTP/ledger/native会话；仅透明计数和接受回执延迟。"""
import asyncio
import functools
import os
import sys
import time
import uvicorn
from .common import EVIDENCE, atomic_json, event, load, require_runtime, reserve


def instrument(app):
    require_runtime()
    from app.worker import one_call
    original = one_call.run_one_call

    @functools.wraps(original)
    def counted(*args, **kwargs):
        reserve("SUP_attempt", dict(method="run_one_call", activity=str(args[2]), operation=str(args[4])))
        return original(*args, **kwargs)

    # 已加载的真实服务引用同一函数，透明包裹后仍执行原完整native链。
    for module in list(sys.modules.values()):
        if module is not None and getattr(module, "__name__", "").startswith("app.") and getattr(module, "run_one_call", None) is original:
            module.run_one_call = counted

    from app.activities.interview_repository import InterviewLedgerMethods
    accepted_original = InterviewLedgerMethods.accept_interview_command

    @functools.wraps(accepted_original)
    async def accepted_observer(self, aid, command, frozen):
        result = await accepted_original(self, aid, command, frozen)
        planfile = EVIDENCE / "runtime-mode.json"
        plan = load(planfile) if planfile.exists() else {}
        marker = EVIDENCE / "acceptance-observed.json"
        if plan.get("mode") == "hold-accepted-receipt" and plan.get("activity_id") == aid and not marker.exists():
            if result["status"] != "accepted" or result["launch_claimed"]:
                raise RuntimeError("107未到达真实接受且未claim窗口")
            atomic_json(marker, dict(activity_id=aid, key=command.business_key, receipt=result,
                                     actual_product_accept_completed=True, no_qualification_substitution=True,
                                     utc=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()))
            event("accepted-receipt-held", dict(activity_id=aid, key=command.business_key))
            until = time.monotonic() + 15
            while not (EVIDENCE / "cancel-accepted-caller.json").exists():
                if time.monotonic() >= until:
                    raise RuntimeError("107接受回执屏障已到15秒界限")
                await asyncio.sleep(.025)
            event("actual-caller-cancel-before-claim", dict(activity_id=aid, key=command.business_key))
            asyncio.current_task().cancel()
            await asyncio.sleep(0)
        return result

    InterviewLedgerMethods.accept_interview_command = accepted_observer


async def main():
    require_runtime()
    from app.main import create_app
    from app.worker.session import SessionConfig
    app = create_app()
    app.state.interview_session_config = SessionConfig(window_seconds=20, request_timeout_seconds=2, stop_grace_seconds=2)
    instrument(app)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=18106, log_level="warning", access_log=False, loop="asyncio"))

    async def stop_observer():
        while not server.should_exit:
            signal = EVIDENCE / "stop-api.json"
            if signal.exists() and load(signal).get("root_name") == os.environ.get("TASK107_ROOT_NAME"):
                server.should_exit = True
                return
            await asyncio.sleep(.05)

    watcher = asyncio.create_task(stop_observer())
    try:
        await server.serve()
    finally:
        watcher.cancel()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
