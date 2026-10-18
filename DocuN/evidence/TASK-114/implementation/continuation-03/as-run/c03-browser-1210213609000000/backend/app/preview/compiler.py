"""固定项目程序的纯数据编译包；不运行浏览器或模型脚本。"""
from __future__ import annotations
import base64
import hashlib
from functools import lru_cache
from pathlib import Path
from .description import canonical, digest, validate_description, DescriptionError

RUNTIME_ROOT = Path(__file__).resolve().parents[3] / "deploy" / "preview"
RUNTIME_FILES = ("runtime.cjs", "runtime.css", "runtime.html", "descriptor.schema.json")


@lru_cache(maxsize=1)
def _runtime_bytes():
    # 进程加载一次固定资源；同事务hook只处理已加载的不可变字节。
    return tuple((RUNTIME_ROOT/name).read_bytes() for name in RUNTIME_FILES)


def runtime_identity():
    files = {name: hashlib.sha256(data).hexdigest() for name, data in zip(RUNTIME_FILES, _runtime_bytes())}
    return {"policy": "retrolume.renderer.v2", "version": 1, "files": files,
            "renderer_sha256": digest(files), "description_schema": "interactive_description.v1"}


def runtime_html():
    script, style, template, _ = _runtime_bytes()
    script, style = script.decode("utf-8"), style.decode("utf-8")
    if "</script" in script.lower() or "</style" in style.lower():
        raise DescriptionError("renderer_integrity_error")
    script_hash = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    style_hash = base64.b64encode(hashlib.sha256(style.encode()).digest()).decode()
    policy = ("default-src 'none'; script-src 'sha256-"+script_hash+"'; style-src 'sha256-"+style_hash+
              "'; frame-src 'none'; connect-src 'none'; img-src 'none'; font-src 'none'; "
              "object-src 'none'; worker-src 'none'; form-action 'none'; base-uri 'none'")
    value = template.decode("utf-8")
    value = value.replace("__POLICY__", policy).replace("__STYLE__", style).replace("__SCRIPT__", script)
    if len(value.encode("utf-8")) > 65536:
        raise DescriptionError("renderer_size_limit")
    return value


def compile_description(value, citation_ids):
    description = validate_description(value, citation_ids)
    identity = runtime_identity()
    payload = {"schema": "compiled_interactive_html.v1", "description_json": canonical(description),
               "description_sha256": digest(description), "renderer": identity,
               "compiled_html": runtime_html()}
    execution = {"description_sha256": payload["description_sha256"], "renderer": identity}
    payload["execution_package_sha256"] = digest(execution)
    if len(canonical(payload).encode("utf-8")) > 110592:
        raise DescriptionError("artifact_size_limit")
    payload["artifact_sha256"] = digest(payload)
    return payload


def verify_package(payload):
    if type(payload) is not dict or set(payload) != {"schema", "description_json", "description_sha256",
          "renderer", "compiled_html", "execution_package_sha256", "artifact_sha256"}:
        raise DescriptionError("artifact_integrity_error")
    from .description import load_json
    description = validate_description(load_json(payload["description_json"]))
    compiled = compile_description(description, description["citations"])
    if canonical(compiled) != canonical(payload):
        raise DescriptionError("artifact_integrity_error")
    return description
