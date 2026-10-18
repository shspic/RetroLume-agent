"""未接产品入口的 Windows 单窗内部监督组件。"""

from .command import WorkerCommand
from .gate import ClosingCallGate, GateClosed
from .launcher import run_supervised_window
from .session import SessionConfig, SessionOutcome
from .one_call import OneCallInput, run_one_call

def run_controlled_worker(*args, **kwargs):
    from .worker_main import run_controlled_worker as run
    return run(*args, **kwargs)


__all__ = ["WorkerCommand", "ClosingCallGate", "GateClosed", "SessionConfig", "SessionOutcome", "OneCallInput", "run_one_call", "run_controlled_worker", "run_supervised_window"]
