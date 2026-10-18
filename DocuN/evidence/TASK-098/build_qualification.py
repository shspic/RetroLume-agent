"""解释全量as-run中的测试代码差异与真正构建输入的区别，只读计算。"""
from datetime import datetime, timezone
import json
import time
from probe_support import HERE, load, publish

started = time.monotonic()
all_bindings = load(HERE / "static-reconstruction.json")["as_run_bindings"]
source, value = next((p, b) for p, b in all_bindings.items() if "build-05-complete-inputs" in p)
inputs = [x for x in value["objects"] if x["path"].startswith("frontend/") and not x["path"].startswith(("frontend/tests/", "frontend/dist/"))]
result = {"at": datetime.now(timezone.utc).isoformat(), "source_manifest": source,
          "command": value["command"], "all_recorded_objects": len(value["objects"]),
          "whole_manifest_matches_current": all(x["current_match"] for x in value["objects"]),
          "different_objects": [x["path"] for x in value["objects"] if not x["current_match"]],
          "actual_build_input_objects": inputs, "build_input_count": len(inputs),
          "actual_build_inputs_all_match": all(x["current_match"] and x["saved_bytes_match"] for x in inputs),
          "scope": "全量110对象有5个后改测试/收尾脚本；frontend实际构建16输入全部同字节；不覆盖前一派生结果中的false，不新增build",
          "elapsed_seconds": time.monotonic() - started, "new_build": 0}
publish("build-input-qualification.json", result, HERE)
print(json.dumps({k: result[k] for k in ("whole_manifest_matches_current", "different_objects", "build_input_count", "actual_build_inputs_all_match", "elapsed_seconds")}, ensure_ascii=False))
