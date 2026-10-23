"""启动时装载事实的脱敏只读投影，不授予外发资格。"""
from __future__ import annotations

from copy import deepcopy
import re


_REASONS = frozenset({
    "config_missing", "config_invalid", "config_incompatible",
    "provider_key_not_configured", "embedding_key_not_configured",
    "retrieval_not_configured", "retrieval_disabled", "retrieval_config_invalid",
    "outbound_not_authorized", "q_disabled", "q_readiness_unknown",
    "learning_not_configured", "learning_config_invalid", "learning_config_incompatible",
    "teaching_not_configured", "teaching_config_invalid", "teaching_config_incompatible",
    "interview_not_configured", "interview_model_unavailable", "interview_config_invalid",
    "html_not_configured", "html_config_invalid",
})
_IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


def _reason(value):
    return value if type(value) is str and value in _REASONS else "load_state_unknown"


def _identity(value):
    return value if isinstance(value, str) and _IDENTITY.fullmatch(value) else None


def _layer(value):
    if value is None:
        return {"available": False, "reason": "load_state_unknown"}
    available = value.available is True
    return {"available": available, "reason": None if available else _reason(value.reason)}


def _service(value, *, embedding=False):
    if value is None:
        return {"loaded": False, "identity": None, "returned_models": None,
                "returned_models_status": "service_not_loaded", "limits": None}
    aliases = value.returned_models
    safe_aliases = (bool(aliases) and len(aliases) <= 16
                    and len(set(aliases)) == len(aliases)
                    and all(_identity(alias) is not None for alias in aliases))
    limits = {"timeout_seconds": value.timeout_seconds,
              "max_request_bytes": value.max_request_bytes,
              "max_response_bytes": value.max_response_bytes}
    if embedding:
        limits.update(dimensions=value.dimensions, max_batch_items=4,
                      max_item_codepoints=2048, max_query_codepoints=1024,
                      max_query_bytes=4096)
    else:
        limits["max_output_tokens"] = value.max_output_tokens_limit
    return {"loaded": True,
            "identity": {"provider": _identity(value.provider), "model": _identity(value.model)},
            "returned_models": list(aliases) if safe_aliases else ([] if not aliases else None),
            "returned_models_status": "configured_not_observed" if safe_aliases else (
                "allowlist_empty" if not aliases else "allowlist_not_projectable"),
            "limits": limits}


def _model(config):
    if config is None:
        return {"identity": None, "load": _layer(None), "execution": _layer(None),
                "service": _service(None), "activity_limits": None, "output_limits": None}
    quota = config.quota_preview
    activity_limits = ({name: quota.get(name) for name in ("max_request_bytes", "max_output_tokens")}
                       if quota is not None else None)
    service = config.model_service
    outputs = {}
    for name, field, fixed in (("continue", None, 256), ("learning", "learning_output_tokens", None),
                                ("teaching", "teaching_output_tokens", None),
                                ("interview_model", "interview_output_tokens", None),
                                ("html_generation", "html_output_tokens", None)):
        layer = getattr(config, name + "_layer", None)
        tokens = getattr(config, field, None) if field else fixed
        outputs[name] = {"state": _layer(layer), "max_output_tokens": (
            min(tokens, quota["max_output_tokens"], service.max_output_tokens_limit)
            if layer is not None and layer.available and service is not None
            and quota is not None and tokens is not None else None)}
    return {"identity": ({"provider": _identity(config.provider), "model": _identity(config.model)}
                         if config.provider is not None or config.model is not None else None),
            "load": _layer(config.create_layer), "execution": _layer(config.continue_layer),
            "service": _service(service), "activity_limits": activity_limits,
            "output_limits": outputs}


def _embedding(config):
    service = config.service if config is not None else None
    reason = config.reason if config is not None else None
    available = config.available if config is not None else False
    return {"load": {"available": service is not None and reason is None,
                     "reason": None if service is not None and reason is None else _reason(reason)},
            "execution": {"available": available,
                          "reason": None if available else (_reason(reason) if reason else "outbound_not_authorized")},
            "service": _service(service, embedding=True),
            "max_index_fragments": config.max_index_fragments if config is not None else None}


def _loaded_evidence(model, embedding):
    """仅核装载对象之间的一致性，引用摘要不充当原件或账号核证。"""
    grant = embedding.outbound_grant if embedding is not None else None
    model_grant = model.outbound_grant if model is not None else None
    manifest = embedding.outbound_source_manifest if embedding is not None else None
    result = {"grant": {"state": "not_loaded" if grant is None else "unknown", "sha256": None},
              "model_embedding_grant_match": None,
              "manifest": {"state": "not_loaded" if manifest is None else "unknown",
                           "sha256": None, "grant_match": None, "model_embedding_match": None},
              "price": {"state": "unknown", "reference_sha256": None, "content_match": None},
              "activation": {"state": "unknown", "reference_sha256": None, "content_match": None},
              "instance": {"state": "unknown", "reference_sha256": None, "deployment_match": None},
              "reason": "loaded_objects_only"}
    if grant is None:
        return result
    try:
        from app.capabilities.embedding import OutboundGrant, OutboundSourceManifest
        trusted = OutboundGrant.from_wire(grant)
        result["grant"] = {"state": "shape_validated", "sha256": trusted.sha256}
        result["model_embedding_grant_match"] = model_grant == grant if model_grant is not None else None
        result["price"].update(state="reference_only", reference_sha256=trusted.price_snapshot_sha256)
        result["activation"].update(state="reference_only", reference_sha256=trusted.q_activation_receipt_sha256)
        result["instance"]["reference_sha256"] = getattr(trusted, "instance_binding_sha256", None)
        if manifest is not None:
            loaded = OutboundSourceManifest.from_wire(manifest)
            result["manifest"] = {"state": "shape_validated", "sha256": loaded.sha256,
                                  "grant_match": loaded.sha256 == trusted.source_manifest_sha256,
                                  "model_embedding_match": (
                                      model.outbound_source_manifest == manifest if model is not None else None)}
    except (ValueError, TypeError, KeyError, RecursionError):
        result["reason"] = "loaded_evidence_invalid"
    return result


def build_readiness(candidate_model=None, candidate_embedding=None, *, effective_model=None,
                    effective_embedding=None, embedding_key_present=None, q_approval=None):
    """只接收正常启动已获得的对象和布尔值，不访问配置、环境、授权器或PG。"""
    service = candidate_model.model_service if candidate_model is not None else None
    model_key = True if service is not None else (
        False if candidate_model is not None
        and candidate_model.continue_layer.reason == "provider_key_not_configured" else None)
    q = q_approval or {}
    execution_class = q.get("execution_class")
    return {"schema": "retrolume.q-readiness.v1", "source": "startup_loaded_snapshot",
            "authorizes_requests": False,
            "key_presence": {"model": model_key,
                             "embedding": embedding_key_present if type(embedding_key_present) is bool else None},
            "candidate": {"model": _model(candidate_model), "embedding": _embedding(candidate_embedding)},
            "effective": {"model": _model(effective_model), "embedding": _embedding(effective_embedding)},
            "q_approval": {"available": q.get("available") is True,
                           "reason": None if q.get("available") is True else _reason(q.get("reason")),
                           "execution_class": execution_class if execution_class in ("Q", "TESTONLY") else None,
                           "real_outbound_authorized": q.get("real_outbound_authorized") is True},
            "loaded_evidence": _loaded_evidence(
                effective_model.model_service if effective_model is not None else None,
                effective_embedding.service if effective_embedding is not None else None),
            "qualification": {"state": "unknown", "account": None, "metering": None,
                              "returned_model_observed": None, "normal_deployment": None,
                              "reason": "external_evidence_not_evaluated"}}


def read_readiness(state):
    """GET仅复制启动快照；最小旧测试夹具没有快照时明确未知。"""
    value = getattr(state, "q_diagnostics", None)
    return deepcopy(value) if value is not None else build_readiness()
