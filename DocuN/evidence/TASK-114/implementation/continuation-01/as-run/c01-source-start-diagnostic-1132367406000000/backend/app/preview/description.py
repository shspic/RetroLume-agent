"""封闭交互数据语言；只校验数据，不执行模型代码或数学表达式。"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

SCHEMA = "interactive_description.v1"
MAX_DESCRIPTION = 24576
ARITY = {"add": 2, "sub": 2, "mul": 2, "div": 2, "neg": 1, "abs": 1,
         "min": 2, "max": 2, "pow_int": 2, "sqrt": 1, "sin": 1, "cos": 1, "binomial_pmf": 3}
DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?\Z")
IDENTIFIERS = {name: re.compile(prefix + r"[A-Za-z0-9_]{1,24}\Z") for name, prefix in
               (("input", "hctl_"), ("result", "hcalc_"), ("view", "hview_"),
                ("readout", "hout_"), ("action", "hact_"))}


class DescriptionError(ValueError):
    def __init__(self, code="invalid_interactive_output"):
        self.code = code
        super().__init__(code)


def canonical(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError, RecursionError):
        raise DescriptionError() from None


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise DescriptionError()
        value[key] = item
    return value


def load_json(raw: bytes | str, maximum=MAX_DESCRIPTION):
    try:
        data = raw.encode("utf-8") if type(raw) is str else bytes(raw)
        if not 1 <= len(data) <= maximum:
            raise DescriptionError()
        return json.loads(data.decode("utf-8", "strict"), object_pairs_hook=_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(DescriptionError()))
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise DescriptionError() from None


def exact(value, required, optional=()):
    if type(value) is not dict or not set(required) <= set(value) or set(value) - set(required) - set(optional):
        raise DescriptionError()


def text(value, maximum, *, empty=False):
    if type(value) is not str or (not value and not empty) or len(value) > maximum or "\0" in value:
        raise DescriptionError()
    try:
        value.encode("utf-8", "strict")
    except UnicodeError:
        raise DescriptionError() from None
    return value


def bounded_list(value, maximum, minimum=0):
    if type(value) is not list or not minimum <= len(value) <= maximum:
        raise DescriptionError()
    return value


def decimal_parts(value: str) -> tuple[int, int]:
    if type(value) is not str or len(value) > 24 or not DECIMAL.fullmatch(value) or value == "-0":
        raise DescriptionError("invalid_decimal")
    negative = value.startswith("-")
    unsigned = value[1:] if negative else value
    whole, _, fraction = unsigned.partition(".")
    integer = int(whole + fraction) * (-1 if negative else 1)
    scale = len(fraction)
    if abs(integer) > 1000000 * 10**scale:
        raise DescriptionError("invalid_decimal")
    return integer, scale


def decimal_integer(value: str, scale: int) -> int:
    integer, original = decimal_parts(value)
    if original > scale:
        raise DescriptionError("invalid_decimal")
    return integer * 10**(scale-original)


def control_value(control, value):
    """范围和格点用整数缩放比较，数学解释器才使用明确的有限浮点。"""
    parts = [decimal_parts(control[name]) for name in ("min", "max", "step")]
    parts.append(decimal_parts(value))
    scale = max(x[1] for x in parts)
    low, high, step, current = [n * 10**(scale-s) for n, s in parts]
    if step <= 0 or low > high or not low <= current <= high or (current-low) % step:
        raise DescriptionError("calculation_domain_error")
    if control["kind"] == "integer" and (current % 10**scale or low % 10**scale or
                                          high % 10**scale or step % 10**scale):
        raise DescriptionError("calculation_domain_error")
    if control["kind"] == "range" and ((high-low) % step or (high-low)//step > 100):
        raise DescriptionError("calculation_domain_error")
    return value


def _validate_description(value, citation_ids=None):
    exact(value, ("schema", "title", "concept", "inputs", "calculations", "views", "actions",
                  "calculation_notes", "limitations", "citations"), ("constraints",))
    if value["schema"] != SCHEMA or len(canonical(value).encode("utf-8")) > MAX_DESCRIPTION:
        raise DescriptionError()
    text(value["title"], 128); text(value["concept"], 1024)
    seen = set()

    def identity(item, kind):
        identifier = item["id"]
        if type(identifier) is not str or not IDENTIFIERS[kind].fullmatch(identifier) or identifier in seen:
            raise DescriptionError()
        seen.add(identifier)
        return identifier

    inputs = {}
    for item in bounded_list(value["inputs"], 8, 1):
        exact(item, ("id", "kind", "label", "description", "min", "max", "step", "default"))
        if item["kind"] not in ("number", "range", "integer"):
            raise DescriptionError()
        key = identity(item, "input"); text(item["label"], 80); text(item["description"], 256, empty=True)
        control_value(item, item["default"])
        inputs[key] = item
    constraints = value.get("constraints", [])
    for item in bounded_list(constraints, 4):
        exact(item, ("kind", "left", "right"))
        if item["kind"] != "le" or item["left"] not in inputs or item["right"] not in inputs:
            raise DescriptionError()
        left, right = inputs[item["left"]]["default"], inputs[item["right"]]["default"]
        scale = max(decimal_parts(left)[1], decimal_parts(right)[1])
        if decimal_integer(left, scale) > decimal_integer(right, scale):
            raise DescriptionError("calculation_domain_error")

    nodes = 0
    results = set()

    def expression(node, depth=1, sample=False):
        nonlocal nodes
        nodes += 1
        if nodes > 256 or depth > 16 or type(node) is not dict or type(node.get("op")) is not str:
            raise DescriptionError()
        op = node["op"]
        if op == "const":
            exact(node, ("op", "value")); decimal_parts(node["value"])
        elif op in ("input", "result"):
            exact(node, ("op", "id"))
            if node["id"] not in (inputs if op == "input" else results):
                raise DescriptionError()
        elif op == "sample_x":
            exact(node, ("op",))
            if not sample:
                raise DescriptionError()
        elif op in ARITY:
            exact(node, ("op", "args"))
            bounded_list(node["args"], ARITY[op], ARITY[op])
            for child in node["args"]:
                expression(child, depth+1, sample)
        else:
            raise DescriptionError()

    for item in bounded_list(value["calculations"], 32, 1):
        exact(item, ("id", "expression"))
        key = identity(item, "result")
        expression(item["expression"])
        results.add(key)
    pictures = points = readouts = 0
    for item in bounded_list(value["views"], 4, 1):
        kind = item.get("kind") if type(item) is dict else None
        if kind == "readout":
            exact(item, ("id", "kind", "label", "calculation", "unit"))
            identity(item, "readout"); text(item["unit"], 24, empty=True)
            if item["calculation"] not in results:
                raise DescriptionError()
            readouts += 1
        elif kind in ("bar", "curve", "points_lines"):
            exact(item, ("id", "kind", "label", "source"))
            identity(item, "view"); pictures += 1
            source = item["source"]
            if kind == "bar":
                if type(source) is not dict:
                    raise DescriptionError()
                if source.get("kind") == "values":
                    exact(source, ("kind", "values"))
                    for point in bounded_list(source["values"], 21, 1):
                        exact(point, ("label", "value")); text(point["label"], 80)
                        expression(point["value"]); points += 1
                elif source.get("kind") == "binomial_distribution":
                    exact(source, ("kind", "n", "p")); expression(source["n"]); expression(source["p"])
                    # 与运行时n端点共同限制；预算预先按最大21柱计。
                    points += 21
                else:
                    raise DescriptionError()
            elif kind == "curve":
                exact(source, ("min", "max", "samples", "expression"))
                low, high = decimal_parts(source["min"]), decimal_parts(source["max"])
                scale = max(low[1], high[1])
                if low[0]*10**(scale-low[1]) >= high[0]*10**(scale-high[1]):
                    raise DescriptionError()
                if type(source["samples"]) is not int or not 2 <= source["samples"] <= 128:
                    raise DescriptionError()
                points += source["samples"]; expression(source["expression"], sample=True)
            else:
                exact(source, ("points", "join"))
                if type(source["join"]) is not bool:
                    raise DescriptionError()
                for point in bounded_list(source["points"], 128, 1):
                    exact(point, ("x", "y")); expression(point["x"]); expression(point["y"]); points += 1
        else:
            raise DescriptionError()
        text(item["label"], 80)
    if pictures > 2 or points > 128 or readouts > 8:
        raise DescriptionError()
    for item in bounded_list(value["actions"], 4):
        exact(item, ("id", "kind", "label"))
        identity(item, "action"); text(item["label"], 80)
        if item["kind"] != "reset":
            raise DescriptionError()
    for item in bounded_list(value["calculation_notes"], 4, 1):
        exact(item, ("formula", "domain", "error", "samples", "citations"))
        text(item["formula"], 512); text(item["domain"], 256); text(item["error"], 128)
        for sample in bounded_list(item["samples"], 4, 2):
            exact(sample, ("input", "expected")); text(sample["input"], 256); text(sample["expected"], 128)
        bounded_list(item["citations"], 4, 1)
    for item in bounded_list(value["limitations"], 8):
        text(item, 256)
    citations = bounded_list(value["citations"], 8, 1)
    if len(set(citations)) != len(citations):
        raise DescriptionError()
    for citation in citations:
        text(citation, 128)
        if citation_ids is not None and citation not in citation_ids:
            raise DescriptionError("invalid_citation")
    if any(c not in citations for note in value["calculation_notes"] for c in note["citations"]):
        raise DescriptionError("invalid_citation")
    # 规范描述不补默认键；同一原对象和原字节hash跨两语言对应。
    return load_json(canonical(value))


def validate_description(value, citation_ids=None):
    try:
        return _validate_description(value, citation_ids)
    except DescriptionError:
        raise
    except (TypeError, KeyError, UnicodeError, RecursionError, OverflowError):
        raise DescriptionError() from None
