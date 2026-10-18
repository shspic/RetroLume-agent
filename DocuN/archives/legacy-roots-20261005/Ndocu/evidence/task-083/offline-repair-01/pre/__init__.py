"""未接产品入口的 Windows 单窗内部监督组件。"""

from .gate import ClosingCallGate, GateClosed
from .session import SessionConfig, SessionOutcome, SingleWindowSupervisor

__all__ = ["ClosingCallGate", "GateClosed", "SessionConfig", "SessionOutcome", "SingleWindowSupervisor"]
