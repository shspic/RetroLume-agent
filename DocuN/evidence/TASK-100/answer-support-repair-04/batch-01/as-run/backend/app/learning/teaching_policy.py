"""teaching.v1 纯策略函数：阶段转移、路径图、支持性检查与进度推导。

全部纯函数：不联网、不 exec/eval、不读数据库。模型输出只是低信任建议；
这里实现应用裁决——结构、推进、独立性、暴露资格均由本模块确定。
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
import re

from .teaching_contracts import (
    ALL_ACTIONS,
    MAX_GOAL_VERSION,
    PHASES,
    TeachingRefusal,
    parse_teaching_output,
)

# --- O01—O11 的阶段前提表（099 第 3.3 节） ---
_ACTION_PHASES = {
    "goal": None,                       # 任意阶段可保存/修正目标
    "plan": ("needs_plan", "path_review", "ready", "exercise_ready", "answer_saved", "feedback_ready"),
    "accept_path": ("path_review",),
    "exercise": ("ready", "feedback_ready"),
    "expose": ("exercise_ready", "answer_saved", "feedback_ready"),
    "answer": ("exercise_ready", "answer_saved", "feedback_ready"),
    "calculate": ("answer_saved", "feedback_ready"),
    "evaluate": ("answer_saved", "feedback_ready"),
    "correct": None,                    # 任意可读阶段可纠错
    "abandon": None,
    "select_node": ("ready", "feedback_ready"),
}


def validate_transition(action: str, phase: str, *, purpose: str | None = None) -> None:
    """校验命令动作与当前 head 阶段的兼容性；不合法抛 TeachingRefusal。

    动作必须落在 O01—O11 封闭集合内：未知动作一律拒绝，绝不按“无限制”
    静默放行（那会让绕开阶段约束的调用伪装成合法动作）。
    """
    if phase not in PHASES:
        raise TeachingRefusal("invalid_input", "教学阶段非法")
    if action not in ALL_ACTIONS or action not in _ACTION_PHASES:
        raise TeachingRefusal("invalid_input", "教学动作不在封闭集合内")
    allowed = _ACTION_PHASES[action]
    if allowed is None:
        return
    if action == "exercise":
        # initial 允许 ready 或当前节点重新练习（ready）；continuation/retest 需 feedback_ready
        if purpose in ("continuation", "retest"):
            allowed = ("feedback_ready",)
        else:
            allowed = ("ready", "exercise_ready", "answer_saved", "feedback_ready")
    if phase not in allowed:
        raise TeachingRefusal("stage_conflict", f"当前阶段 {phase} 不允许该动作")


def validate_path(nodes: list[dict]) -> list[str]:
    """校验路径图并返回服务器分配的节点 ID（n1..n6）。

    前置索引必须在当前节点之前（严格递增 DAG）；1..6 节点。
    """
    if not 1 <= len(nodes) <= 6:
        raise TeachingRefusal("invalid_input", "路径须为1至6个节点")
    assigned: list[str] = []
    for index, node in enumerate(nodes):
        for prerequisite in node.get("prerequisites", []):
            if not isinstance(prerequisite, int) or isinstance(prerequisite, bool) \
                    or prerequisite < 0 or prerequisite >= index:
                raise TeachingRefusal("invalid_input", "路径前置必须指向更早节点")
        assigned.append(f"n{index + 1}")
    return assigned


def _decimal_equal(left: Decimal, right: Decimal, tolerance: Decimal | None) -> bool:
    if tolerance is None:
        return left == right
    return abs(left - right) <= tolerance


_ANSWER_UNITS = {
    "m/s": ("speed", 1, 1), "米/秒": ("speed", 1, 1), "米每秒": ("speed", 1, 1),
    "m/min": ("speed", 1, 60),
    "s": ("time", 1, 1), "秒": ("time", 1, 1),
    "min": ("time", 60, 1), "分钟": ("time", 60, 1),
    "m": ("distance", 1, 1), "米": ("distance", 1, 1),
}
_ANSWER_NUMBER = r"-?[0-9]+(?:\.[0-9]+)?"
_ANSWER_QUANTITY = re.compile(
    rf"({_ANSWER_NUMBER})\s*(m\s*/\s*min|m\s*/\s*s|米\s*/\s*秒|米每秒|min|分钟|秒|s|m|米)"
)
_ANSWER_TIME_CONVERSION = re.compile(
    rf"({_ANSWER_NUMBER})\s*(?:分钟|min)\s*=\s*({_ANSWER_NUMBER})\s*(?:秒|s)"
)
_ANSWER_AUXILIARY_PHRASES = frozenset({
    "先统一秒", "先统一时间单位", "先换算秒", "分钟乘60",
    "单位与数量级合理", "单位与数量级正确", "数量级合理", "数量级正确",
})


def _answer_auxiliary(clause: str) -> bool:
    """封闭辅助说明：固定肯定短语，或非负且精确成立的分钟转秒等式。"""
    if clause in _ANSWER_AUXILIARY_PHRASES:
        return True
    match = _ANSWER_TIME_CONVERSION.fullmatch(clause)
    if match is None:
        return False
    minutes, seconds = Decimal(match[1]), Decimal(match[2])
    with localcontext() as context:
        context.prec = max(64, len(match[1]) + len(match[2]) + 2)
        return minutes >= 0 and seconds >= 0 and minutes * 60 == seconds


def _answer_quantity(text: str, unit: str | None):
    """完整匹配肯定答案，不从否定、引用或开放文字筛选数值。

    有单位：首部一个量值，逗号/分号分隔的后部仅允许封闭辅助说明。
    无单位：仅一个数值，可前置“约”。两者可有外围空白和一个句末句号。
    任何未识别内容（含额外量值或开放尾文）均返回 None，保留未检验。
    """
    unit = re.sub(r"\s+", "", unit or "")
    text = text.strip()
    if text.endswith(("。", ".")):
        text = text[:-1].rstrip()
    if unit in _ANSWER_UNITS:
        clauses = re.split(r"\s*[,，;；]\s*", text)
        match = _ANSWER_QUANTITY.fullmatch(clauses[0])
        if match and all(_answer_auxiliary(clause) for clause in clauses[1:]):
            return Decimal(match[1]), re.sub(r"\s+", "", match[2])
    if not unit:
        match = re.fullmatch(rf"(?:约\s*)?({_ANSWER_NUMBER})", text)
        if match:
            return Decimal(match[1]), ""
    return None


def derive_support_checks(exercise_body: dict, answer_text: str) -> list[dict]:
    """应用侧支持性检查：只做确定数值/运算对照，不评开放语义。

    对已存参考要点中的 numeric（含 operation/left/right/tolerance），按其
    有限域执行一次确定性运算，报告 value/unit/数量级符合或冲突；未提供
    数值依据的维度返回 unchecked。程序题绝不执行用户代码，仅阅读推理。
    """
    checks: list[dict] = []
    for point in exercise_body.get("reference_points", []):
        numeric = point.get("numeric")
        if not numeric:
            continue
        try:
            left = Decimal(str(numeric["left"]))
            right = Decimal(str(numeric["right"]))
            expected = Decimal(str(numeric["value_decimal"]))
        except (InvalidOperation, ValueError, TypeError, KeyError):
            checks.append({"point_id": point.get("point_id"), "status": "unchecked"})
            continue
        tolerance = None
        if numeric.get("tolerance_decimal") is not None:
            try:
                tolerance = Decimal(str(numeric["tolerance_decimal"]))
            except InvalidOperation:
                tolerance = None
        # 非有限值（NaN/Infinity）不是可核算依据：判 unchecked，绝不硬报冲突。
        # conflict 是"有据冲突"的强断言，会参与推进裁决，不能由非法数值伪造。
        if not all(item.is_finite() for item in (left, right, expected)) \
                or (tolerance is not None and not tolerance.is_finite()):
            checks.append({"point_id": point.get("point_id"), "status": "unchecked"})
            continue
        operation = numeric.get("operation")
        try:
            if operation == "add":
                computed = left + right
            elif operation == "subtract":
                computed = left - right
            elif operation == "multiply":
                computed = left * right
            elif operation == "divide":
                computed = left / right
            elif operation == "power":
                if right != right.to_integral_value() or abs(right) > 12:
                    raise ValueError
                computed = left ** int(right)
            else:
                raise ValueError
        except (InvalidOperation, ZeroDivisionError, OverflowError, ValueError):
            checks.append({"point_id": point.get("point_id"), "status": "unchecked"})
            continue
        reference_match = _decimal_equal(computed, expected, tolerance)
        actual = None if exercise_body.get("exercise_type") == "program" else _answer_quantity(answer_text, numeric.get("unit"))
        answer_status = "unchecked"
        detail = {}
        if actual is not None:
            number, unit = actual
            expected_unit = re.sub(r"\s+", "", numeric.get("unit") or "")
            unit_match = unit == expected_unit
            if unit in _ANSWER_UNITS and expected_unit in _ANSWER_UNITS:
                family, numerator, denominator = _ANSWER_UNITS[unit]
                expected_family, expected_numerator, expected_denominator = _ANSWER_UNITS[expected_unit]
                unit_match = family == expected_family
                if unit_match:
                    with localcontext() as context:
                        context.prec = 64
                        number = number * numerator * expected_denominator / (denominator * expected_numerator)
            value_match = unit_match and _decimal_equal(number, expected, tolerance)
            answer_status = "matched" if value_match else "conflict"
            detail = {"answer_value_decimal": format(number, "f"), "answer_unit": unit,
                      "unit_matched": unit_match, "value_matched": value_match}
        checks.append({
            "point_id": point.get("point_id"),
            "status": "conflict" if not reference_match or answer_status == "conflict" else answer_status,
            "reference_status": "matched" if reference_match else "conflict",
            "answer_status": answer_status,
            "dimension_ids": [d["id"] for d in exercise_body.get("dimensions", [])
                              if point.get("point_id") in d.get("point_ids", [])],
            "computed": format(computed.normalize(), "f"),
            **detail,
        })
    return checks


def derive_progress(feedback_body: dict, independent_answers: list[str],
                    node_dimensions: list[str]) -> dict:
    """按当前非争议反馈推导节点投影状态（099 第 3.2 节完成依据）。

    两个不同练习的未暴露独立作答且所有必需维度有据满足，才
    evidence_sufficient；单次正确只保留 practising；明确错误 needs_repair。
    长期掌握不在本切片表达，永不输出 mastered。
    """
    observations = {item["id"]: item["observation"]
                    for item in feedback_body.get("dimension_observations", [])}
    # 必需维度必须全部出现且为 met：缺失维度按未满足处理，不得因 all() 空集真而通过。
    all_met = bool(node_dimensions) and all(
        observations.get(dim) == "met" for dim in node_dimensions)
    has_error = any(item["observation"] == "not_met"
                    for item in feedback_body.get("dimension_observations", []))
    if has_error:
        status = "needs_repair"
    elif all_met and len(set(independent_answers)) >= 2:
        status = "evidence_sufficient"
    else:
        status = "practising"
    return {
        "status": status,
        # 观察以 answer_record_id 去重（099 第 3.2 节）：同题续答、重复提交、
        # 对同一作答的再评价都不新增独立次数。
        "independent_count": len(set(independent_answers)),
        "advance": status == "evidence_sufficient",
    }


def project_public_exercise(exercise_body: dict, exposed_parts: set[str]) -> dict:
    """题目公开投影：未暴露的参考与提示绝不返回。"""
    projection = {
        "exercise_type": exercise_body.get("exercise_type"),
        "difficulty": exercise_body.get("difficulty"),
        "stem": exercise_body.get("stem"),
        "dimensions": exercise_body.get("dimensions"),
        "variant_purpose": (exercise_body.get("variant") or {}).get("purpose"),
        "reference_available": "reference" in exposed_parts,
        "hint_available": "hint" in exposed_parts,
    }
    if "hint" in exposed_parts:
        projection["hint"] = exercise_body.get("hint")
    if "reference" in exposed_parts:
        projection["reference_points"] = exercise_body.get("reference_points")
        projection["reference_explanation"] = exercise_body.get("reference_explanation")
    return projection


def compute_view_token(head_revision: int, last_seq: int, scope_revision: int,
                       source_identity_sha: str, command_state_sha: str) -> str:
    from .contracts import canonical, sha
    return sha(canonical({
        "head_revision": head_revision, "last_seq": last_seq, "scope_revision": scope_revision,
        "source_identity_sha256": source_identity_sha, "command_state_sha256": command_state_sha,
    }))


def normalize_output_for_action(raw: str, action: str) -> dict:
    """解析模型输出联合并返回规范 dict；失败关闭抛 TeachingRefusal。"""
    try:
        return parse_teaching_output(raw, action)
    except (ValueError, TypeError) as exc:
        code = str(exc) if str(exc) in {"teaching_output_limit", "duplicate_teaching_field"} else "invalid_teaching_output"
        raise TeachingRefusal(code, "模型输出不符合教学合同，未保存为可用成果") from None


def goal_version_next(current: int) -> int:
    if current >= MAX_GOAL_VERSION:
        raise TeachingRefusal("history_limit", "目标版本已达上限，请新建活动")
    return current + 1
