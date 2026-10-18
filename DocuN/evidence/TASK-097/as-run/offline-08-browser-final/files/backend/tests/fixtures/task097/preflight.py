"""资源入口前离线核对实际DTO、夹具语法、角色、会话预算及执行目标。"""
import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/"backend"))
from app.learning.api import FirstInput,FollowupInput
from app.worker.windows_job import NamedJob
from app.worker.launcher import _SuspendedSupervisor
from tests.test_learning_config import config
from tests.fixtures.task097.network import install
install()
for path in [*Path(__file__).parent.glob("*.py"),*(ROOT/"backend/app/learning").glob("*.py")]:
    compile(path.read_bytes(),str(path),"exec")
FirstInput.model_validate({"business_key":"00000000-0000-0000-0000-000000000097","goal":"atomicity","confirmed":True})
assert hasattr(NamedJob,"close") and hasattr(_SuspendedSupervisor,"creation_time_100ns")
assert config()["learning"]=={"profile":"learning.v1","max_output_tokens":256}
node=subprocess.run(["node","--check",str(ROOT/"frontend/tests/task097-browser.mjs")],capture_output=True,text=True)
print(node.stdout);print(node.stderr)
assert node.returncode==0
print(json.dumps({"preflight":"PASS","planned_max_sup":15,"sup_budget":16,"browser_launches":1,"ports":[18097,55441],
    "actual_dto":list(FirstInput.model_fields),"python_sources_compiled_in_memory":True}))
