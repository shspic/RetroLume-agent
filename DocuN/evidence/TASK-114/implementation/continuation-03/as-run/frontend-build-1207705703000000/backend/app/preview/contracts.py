"""只允许可信宿主的有限关口观测封包。"""
import hashlib
import json
import struct


def read_observation(stream, expected_sequence):
    prefix = stream.read(4)
    if not prefix:
        return None
    if len(prefix) != 4:
        raise ValueError("关口封包头不完整")
    length = struct.unpack("!I", prefix)[0]
    if not 1 <= length <= 2048:
        raise ValueError("关口封包头超限")
    raw = stream.read(length)
    if len(raw) != length:
        raise ValueError("关口封包头截断")
    head = json.loads(raw)
    if set(head) != {"protocol", "type", "seq", "body_bytes", "body_sha256"}:
        raise ValueError("关口封包字段不符")
    if head["protocol"] != "retrolume.preview.h0.v1" or head["type"] != "observation" or type(head["seq"]) is not int or head["seq"] != expected_sequence:
        raise ValueError("关口封包身份或序号不符")
    if type(head["body_bytes"]) is not int or not 1 <= head["body_bytes"] <= 4096:
        raise ValueError("关口观测超限")
    body = stream.read(head["body_bytes"])
    if len(body) != head["body_bytes"] or hashlib.sha256(body).hexdigest() != head["body_sha256"]:
        raise ValueError("关口正文身份不符")
    return json.loads(body)
