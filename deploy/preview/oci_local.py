"""把已缓存镜像的只读导出安全整理为本地OCI输入，验证完整摘要链。"""
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import time


def digest_file(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while data := stream.read(1048576):
            value.update(data)
    return "sha256:" + value.hexdigest()


def normalize_archive(archive, layout, expected, deadline_ns):
    archive = archive.resolve()
    layout = layout.resolve()
    workspace = Path(__file__).resolve().parents[2]
    layout.relative_to(workspace)
    if layout.exists():
        raise ValueError("本轮OCI目录已存在，不覆盖或重做")
    layout.mkdir(parents=True)
    rows = []
    with tarfile.open(archive, "r:") as tar:
        members = {}
        for entry in tar.getmembers():
            p = PurePosixPath(entry.name)
            if p.is_absolute() or ".." in p.parts or "\\" in entry.name or ":" in entry.name:
                raise ValueError("镜像归档含非法路径")
            if entry.isdir():
                continue
            name = p.as_posix()
            if not entry.isfile() or name in members:
                raise ValueError("镜像归档含链接、设备或重复名字")
            members[name] = entry
        def read_json(name):
            item = members.get(name)
            if item is None or item.size > 1048576:
                raise ValueError("OCI元数据缺失或超限")
            with tar.extractfile(item) as stream:
                return json.loads(stream.read())
        def copy_blob(name, descriptor=None):
            item = members.get(name)
            if item is None:
                raise ValueError("镜像缺本地blob")
            target_dir = layout / "blobs/sha256"
            target_dir.mkdir(parents=True, exist_ok=True)
            temporary = target_dir / ("incoming-" + str(len(rows)))
            value = hashlib.sha256()
            with tar.extractfile(item) as source, temporary.open("xb") as output:
                while data := source.read(1048576):
                    if time.monotonic_ns() >= deadline_ns:
                        raise TimeoutError("OCI验证到达真实根截止")
                    output.write(data)
                    value.update(data)
            digest = "sha256:" + value.hexdigest()
            if descriptor and (descriptor["digest"] != digest or descriptor["size"] != item.size):
                raise ValueError("OCI blob摘要或长度不符")
            destination = target_dir / value.hexdigest()
            if destination.exists():
                raise ValueError("导出引用重复blob，不覆盖")
            temporary.rename(destination)
            rows.append({"member": name, "digest": digest, "bytes": item.size})
            return destination, digest
        if "oci-layout" in members and "index.json" in members:
            if read_json("oci-layout") != {"imageLayoutVersion": "1.0.0"}:
                raise ValueError("OCI layout版本未知")
            index = read_json("index.json")
            descriptors = index.get("manifests", [])
            selected = [d for d in descriptors if d.get("digest") == expected["id"]]
            if len(selected) != 1:
                raise ValueError("OCI index没有唯一缓存manifest")
            descriptor = selected[0]
            if descriptor["mediaType"] not in {"application/vnd.oci.image.manifest.v1+json", "application/vnd.docker.distribution.manifest.v2+json"}:
                raise ValueError("本轮仅接受已冻结单平台manifest")
            manifest_member = "blobs/sha256/" + descriptor["digest"].split(":")[1]
            manifest_path, manifest_digest = copy_blob(manifest_member, descriptor)
            manifest = json.loads(manifest_path.read_bytes())
            config_descriptor = manifest["config"]
            config_path, config_digest = copy_blob("blobs/sha256/" + config_descriptor["digest"].split(":")[1], config_descriptor)
            config = json.loads(config_path.read_bytes())
            layers = manifest["layers"]
            paths = [copy_blob("blobs/sha256/" + layer["digest"].split(":")[1], layer)[0] for layer in layers]
            original_oci = True
        else:
            metadata = read_json("manifest.json")
            if type(metadata) is not list or len(metadata) != 1:
                raise ValueError("Docker归档不是唯一固定镜像")
            entry = metadata[0]
            config_path, config_digest = copy_blob(entry["Config"])
            if expected.get("descriptor", {}).get("mediaType"):
                raise ValueError("manifest身份镜像缺OCI原manifest，不能伪造同一摘要")
            if config_digest != expected["id"]:
                raise ValueError("Docker归档config与缓存配置身份不符")
            config = json.loads(config_path.read_bytes())
            paths = [];layers = []
            for name in entry["Layers"]:
                path, digest = copy_blob(name)
                paths.append(path);layers.append({"mediaType": "application/vnd.oci.image.layer.v1.tar", "digest": digest, "size": path.stat().st_size})
            manifest = {"schemaVersion": 2, "mediaType": "application/vnd.oci.image.manifest.v1+json", "config": {"mediaType": "application/vnd.oci.image.config.v1+json", "digest": config_digest, "size": config_path.stat().st_size}, "layers": layers}
            raw = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
            manifest_digest = "sha256:" + hashlib.sha256(raw).hexdigest()
            manifest_path = layout / "blobs/sha256" / manifest_digest.split(":")[1]
            manifest_path.write_bytes(raw)
            descriptor = {"mediaType": manifest["mediaType"], "digest": manifest_digest, "size": len(raw)}
            original_oci = False
        diff_ids = config.get("rootfs", {}).get("diff_ids", [])
        if diff_ids != expected["rootfs"]["Layers"] or len(paths) != len(diff_ids) or config.get("os") != "linux" or config.get("architecture") != "amd64":
            raise ValueError("config平台或rootfs链不匹配")
        actual_diff_ids = []
        for path, layer in zip(paths, layers):
            media = layer["mediaType"]
            if media.endswith("+gzip") or media.endswith(".gzip"):
                stream = gzip.open(path, "rb")
            elif media.endswith(".tar"):
                stream = path.open("rb")
            else:
                raise ValueError("本轮标准库不识别layer压缩类型")
            value = hashlib.sha256()
            with stream:
                while data := stream.read(1048576):
                    if time.monotonic_ns() >= deadline_ns:
                        raise TimeoutError("层字节验证到达真实根截止")
                    value.update(data)
            actual_diff_ids.append("sha256:" + value.hexdigest())
        if actual_diff_ids != diff_ids:
            raise ValueError("实际layer内容与diff IDs不符")
        (layout / "oci-layout").write_text('{"imageLayoutVersion":"1.0.0"}', encoding="utf-8")
        (layout / "index.json").write_text(json.dumps({"schemaVersion": 2, "manifests": [descriptor]}, separators=(",", ":")), encoding="utf-8")
        uri = "oci-layout://" + layout.as_posix() + "@" + manifest_digest
        if Path(uri.removeprefix("oci-layout://").split("@")[0]).resolve() != layout:
            raise ValueError("本机OCI路径语法没有绑定到目标目录")
        return {"archive": str(archive), "archive_sha256": digest_file(archive), "layout": str(layout), "uri": uri, "manifest_digest": manifest_digest, "config_digest": config_digest, "cached_id_kind": "manifest" if original_oci else "config", "original_OCI_manifest_bytes_preserved": original_oci, "literal_config_equals_cached_id": config_digest == expected["id"], "binding_is_exact_cached_descriptor_and_referenced_config": True, "rootfs_diff_ids": actual_diff_ids, "blobs": rows, "config_public": {k: config.get("config", {}).get(k) for k in ["User", "Entrypoint", "Cmd", "WorkingDir"]}}
