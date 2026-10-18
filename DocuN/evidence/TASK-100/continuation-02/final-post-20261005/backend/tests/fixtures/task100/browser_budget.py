"""runner 子链内在实际 Chromium launch 前持久扣 browser 尝试。"""
import os
from .control import Ledger,PERMIT
if os.environ.get('RETROLUME_TASK100_FIXTURE')!=PERMIT:raise SystemExit(2)
Ledger().consume('browser',{'parent_node':True,'entry':'frontend/tests/task100-browser.cjs'})
