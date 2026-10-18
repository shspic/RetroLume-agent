"""Exact D3 scenario and deadline contracts, shared by the test runner and pure tests."""
from __future__ import annotations

import json
import time

SCENARIOS = {
    "migration": ("migration_empty", "migration_old", "migration_rollback"),
    "ledger": ("ledger_active_lease_rejected", "ledger_new_g", "ledger_exhausted", "ledger_lock_barrier"),
    "windows": ("windows_recovery",),
}
PART_ORDER = tuple(SCENARIOS)


def parse_parts(value: str) -> tuple[str, ...]:
    items = value.split(",")
    if not items or any(item not in SCENARIOS for item in items) or len(set(items)) != len(items):
        raise ValueError("invalid or duplicate D3 part selection")
    return tuple(item for item in PART_ORDER if item in items)


def expected_scenarios(parts: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(name for part in parts for name in SCENARIOS[part])


def validate_records(raw_stdout: str, parts: tuple[str, ...], exit_code: int,
                     *, cleanup_confirmed: bool, timed_out: bool = False) -> dict:
    expected = expected_scenarios(parts)
    starts, completed, all_completes = [], [], []
    active = None
    errors = []
    for line in raw_stdout.splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        phase = record.get("phase")
        if phase == "scenario_start":
            scene = record.get("scenario")
            if scene not in expected or scene in starts or active is not None:
                errors.append(f"unknown, duplicate, or overlapping scenario start: {scene}")
            starts.append(scene)
            active = scene
        elif phase in expected:
            if phase != active or phase in completed:
                errors.append(f"unpaired or duplicate result: {phase}")
            completed.append(phase)
            active = None
        elif phase == "complete":
            if active is not None or tuple(completed) != expected:
                errors.append("complete arrived before all selected scenarios")
            all_completes.append(record)
        elif phase not in ("schema",):
            errors.append(f"unknown phase: {phase}")
    if tuple(starts) != expected or tuple(completed) != expected or active is not None:
        errors.append("selected scenario sequence incomplete or out of order")
    if len(all_completes) != 1 or all_completes[0].get("all_pass") is not True or all_completes[0].get("parts") != list(parts):
        errors.append("complete/all_pass/parts contract failed")
    if exit_code != 0:
        errors.append(f"child exit={exit_code}")
    if timed_out:
        errors.append("child timeout")
    if not cleanup_confirmed:
        errors.append("outer tree cleanup not confirmed")
    return {"pass": not errors, "expected": list(expected), "started": starts,
            "completed": completed, "complete_count": len(all_completes), "errors": errors}


def deadline_left(*deadlines: float, reserve: float = 0) -> float:
    value = min(deadlines) - time.monotonic() - reserve
    if value <= 0:
        raise TimeoutError("deadline or cleanup reserve exhausted")
    return value