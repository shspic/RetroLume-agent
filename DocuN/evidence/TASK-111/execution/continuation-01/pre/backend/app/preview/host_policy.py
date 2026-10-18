"""固定加载身份与离线审核票据。公开配置没有候选或故障绕过开关。"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
from .compiler import runtime_identity
from .description import canonical, digest


@dataclass(frozen=True)
class HostPolicy:
    image_id: str
    load_manifest_sha256: str
    renderer_sha256: str
    kernel_release: str
    docker: str
    registry_dir: Path
    authorization: str
    owner_name: str = "Local\\RetroLumePreviewV2"

    def __post_init__(self):
        if not re.fullmatch(r"sha256:[0-9a-f]{64}",self.image_id) or not re.fullmatch(r"[0-9a-f]{64}",self.load_manifest_sha256):
            raise ValueError("invalid_host_policy")
        if self.renderer_sha256 != runtime_identity()["renderer_sha256"] or not Path(self.docker).is_absolute() or not self.registry_dir.is_absolute():
            raise ValueError("invalid_host_policy")
        if self.authorization not in ("reviewed.v2","TASK-111-G11-P110-20261010") or self.kernel_release != "6.6.114.1-microsoft-standard-WSL2":
            raise ValueError("host_policy_unconfirmed")


def load_host_policy(path, registry_dir):
    """仅受信operator部署配置和HMAC签名审核文件能启用生产。缺失默认关闭。"""
    try:
        config=json.loads(Path(path).read_text(encoding="utf-8"))
        if set(config)!={"schema","image_id","load_manifest_sha256","renderer_sha256","kernel_release","docker","review_ticket","review_key_env"} or config["schema"]!="retrolume.preview.deployment.v2":
            return None
        ticket=json.loads(Path(config["review_ticket"]).read_text(encoding="utf-8"))
        if set(ticket)!={"schema","decision","image_id","load_manifest_sha256","renderer_sha256","result_sha256","signature"}:
            return None
        if ticket["schema"]!="retrolume.preview.review.v2" or ticket["decision"]!="approved" or not re.fullmatch(r"[0-9a-f]{64}",ticket["result_sha256"]):return None
        for key in ("image_id","load_manifest_sha256","renderer_sha256"):
            if ticket[key]!=config[key]:return None
        key=os.environ.get(config["review_key_env"],"")
        if len(key.encode("utf-8"))<32:return None
        signed={name:value for name,value in ticket.items() if name!="signature"}
        expected=hmac.new(key.encode("utf-8"),canonical(signed).encode("utf-8"),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,ticket["signature"]):return None
        return HostPolicy(**{name:config[name] for name in ("image_id","load_manifest_sha256","renderer_sha256","kernel_release","docker")},
                          registry_dir=Path(registry_dir).resolve(),authorization="reviewed.v2")
    except (OSError,ValueError,TypeError,KeyError):return None


def policy_config_sha256(policy):
    return digest({"profile":"html_explanation.v2","schema":"interactive_description.v1","protocol":"retrolume.preview.v2",
                   "image_id":policy.image_id,"renderer_sha256":policy.renderer_sha256,"load_manifest_sha256":policy.load_manifest_sha256,
                   "starts":3,"seconds":180,"max_window":60,"min_window":30,"viewport":[640,480]})
