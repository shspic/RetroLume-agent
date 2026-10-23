"""仅检查新控制器导入、原生Windows观察与冻结输入；不启动Docker/PG/API。"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
here = Path(__file__).absolute().parent
root = here.parents[3]
paths = [here / name for name in ("run-six.py", "install-observer.py", "win-support.py", "check-docker.py")]
syntax = []
for path in paths:
    ast.parse(path.read_bytes(), filename=str(path))
    syntax.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
spec = importlib.util.spec_from_file_location("task127_controller_preparation", here / "run-six.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
native = module.WIN
payload = b"TASK127-only-native-dpapi-roundtrip-no-credential"
assert native.protect_secret(native.protect_secret(payload), decrypt=True) == payload
manifest = json.loads((here.parent / "orchestration-20261022/input-manifest.json").read_bytes())
for row in manifest["sources"]:
    assert hashlib.sha256(Path(row["absolute_path"]).read_bytes()).hexdigest() == row["sha256"]
record = {"syntax": syntax, "frozen_sources": len(manifest["sources"]), "actual_memory_mib": native.available_mib(),
          "current_sid": native.current_sid(), "root_entity": native.file_identity(root),
          "candidate_port_owners": native.port_owners({55482, 55484, 55486, 55483, 55485, 55487, 18122, 18124, 18126}),
          "private_roots_absent": {slot: not (root / ".runtime/normal-first-install" / slot).exists() for slot in ("source", "interrupted")},
          "native_dpapi_noncredential_roundtrip": True, "no_docker_pg_api_started": True}
with (here / "prepare-check.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
print(json.dumps(record, ensure_ascii=False))
