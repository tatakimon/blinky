#!/usr/bin/env python3
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

CANONICAL_UART_TOKEN = "STWINBX1_ON_LINE"
ALLOWED_UART_TOKEN_MODES = {"default", "explicit", "forbid_override"}
DEFAULT_EVIDENCE_REQUIREMENTS = [
    "final_terminal_status",
    "report_path",
    "report_attempt_summary",
    "verbose_log_when_needed",
]
DEFAULT_OPERATOR_ACTION_REQUIRED_CONDITIONS = [
    "real_hardware_proof",
    "privileged_host_action",
    "claim_depends_on_operator_pasted_or_report_backed_evidence",
]
UNSAFE_INTENT_MARKERS = {
    "bypass deploy.sh": "raw intent requests bypass of deploy.sh",
    "call autofix.sh directly": "raw intent requests direct autofix.sh execution",
    "call test_runner.py directly": "raw intent requests direct test_runner.py execution",
    "skip evidence": "raw intent requests skipping evidence requirements",
    "assume hardware success": "raw intent requests unverifiable hardware success",
    "ignore operator": "raw intent weakens operator-authoritative proof boundaries",
}


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        return []
    result = []
    for item in items:
        text = _normalize_text(item)
        if text:
            result.append(text)
    return result


def normalize_taskspec(
    raw_user_intent: str,
    constraints: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize raw user intent plus constraints into a non-executing TaskSpec."""
    constraints = dict(constraints or {})
    task_intent = _normalize_text(raw_user_intent)
    target_scope = _normalize_string_list(constraints.get("target_scope"))
    allowed_edit_scope = _normalize_string_list(constraints.get("allowed_edit_scope"))
    uart_token_mode = constraints.get("uart_token_mode", "default")
    uart_token_value = _normalize_text(constraints.get("uart_token_value", ""))
    evidence_requirements = _normalize_string_list(
        constraints.get("evidence_requirements")
    ) or list(DEFAULT_EVIDENCE_REQUIREMENTS)
    operator_action_required_conditions = _normalize_string_list(
        constraints.get("operator_action_required_conditions")
    ) or list(DEFAULT_OPERATOR_ACTION_REQUIRED_CONDITIONS)
    refusal_conditions: list[str] = []

    if not task_intent:
        refusal_conditions.append("raw intent is missing or empty")

    lowered_intent = task_intent.lower()
    for marker, reason in UNSAFE_INTENT_MARKERS.items():
        if marker in lowered_intent:
            refusal_conditions.append(reason)

    if not target_scope:
        refusal_conditions.append("target_scope is required and must not be empty")
    if not allowed_edit_scope:
        refusal_conditions.append(
            "allowed_edit_scope is required and must not be empty"
        )

    if uart_token_mode not in ALLOWED_UART_TOKEN_MODES:
        refusal_conditions.append(
            "uart_token_mode must be one of: default, explicit, forbid_override"
        )
        uart_token_mode = "default"

    if uart_token_mode == "explicit":
        if not uart_token_value:
            refusal_conditions.append(
                "uart_token_value is required when uart_token_mode is explicit"
            )
    else:
        uart_token_value = uart_token_value or CANONICAL_UART_TOKEN

    taskspec = {
        "task_intent": task_intent,
        "target_scope": target_scope,
        "allowed_edit_scope": allowed_edit_scope,
        "uart_token_mode": uart_token_mode,
        "uart_token_value": uart_token_value,
        "evidence_requirements": evidence_requirements,
        "operator_action_required_conditions": operator_action_required_conditions,
        "execution_entrypoint": "deploy.sh",
        "refusal_conditions": refusal_conditions,
    }
    return taskspec

import json
import sys


def _run_self_check() -> int:
    success_path = normalize_taskspec(
        "Normalize a Layer B task request without executing Layer A",
        {
            "target_scope": ["tools/layer_b_taskspec_stub.py"],
            "allowed_edit_scope": ["tools/layer_b_taskspec_stub.py"],
            "uart_token_mode": "default",
        },
    )

    refusal_path = normalize_taskspec(
        "",
        {
            "target_scope": [],
            "allowed_edit_scope": [],
            "uart_token_mode": "explicit",
            "uart_token_value": "",
        },
    )

    expected_refusals = {
        "raw intent is missing or empty",
        "target_scope is required and must not be empty",
        "allowed_edit_scope is required and must not be empty",
        "uart_token_value is required when uart_token_mode is explicit",
    }

    if success_path.get("execution_entrypoint") != "deploy.sh":
        raise AssertionError("success_path.execution_entrypoint must be deploy.sh")
    if success_path.get("uart_token_value") != CANONICAL_UART_TOKEN:
        raise AssertionError("success_path.uart_token_value must use canonical token")
    if success_path.get("refusal_conditions") != []:
        raise AssertionError("success_path.refusal_conditions must be empty")

    refusal_conditions = set(refusal_path.get("refusal_conditions", []))
    if refusal_path.get("execution_entrypoint") != "deploy.sh":
        raise AssertionError("refusal_path.execution_entrypoint must be deploy.sh")
    if not expected_refusals.issubset(refusal_conditions):
        raise AssertionError(
            "refusal_path.refusal_conditions is missing one or more expected refusal reasons"
        )

    print(
        json.dumps(
            {
                "success_path": success_path,
                "refusal_path": refusal_path,
            },
            indent=2,
        )
    )
    print("SELF_CHECK_OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-check":
        raise SystemExit(_run_self_check())