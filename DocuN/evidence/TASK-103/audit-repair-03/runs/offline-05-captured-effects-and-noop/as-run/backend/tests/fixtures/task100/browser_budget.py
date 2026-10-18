"""runner 子链内在实际 Chromium launch 前持久扣 browser 尝试。"""
import os
from .control import Ledger,PERMIT
if os.environ.get('RETROLUME_TASK100_FIXTURE')!=PERMIT:raise SystemExit(2)
entry=os.environ.get('RETROLUME_TASK100_BROWSER_ENTRY') or ('frontend/tests/task100-repair-browser.cjs' if PERMIT.startswith('TASK-100-audit-repair') else 'frontend/tests/task100-browser.cjs')
if entry not in ('frontend/tests/task100-repair-browser.cjs','frontend/tests/task100-repair-readonly-browser.cjs','frontend/tests/task100-browser.cjs'):raise SystemExit(2)
Ledger().consume('browser',{'parent_node':True,'entry':entry})
