from __future__ import annotations

import json
from typing import Any

from baton_substrate.models.common import Violation


def validate_against_schema(
    value: dict[str, Any],
    json_schema: dict[str, Any],
) -> list[Violation]:
    if not json_schema:
        return []
    try:
        import jsonschema
        jsonschema.validate(instance=value, schema=json_schema)
    except jsonschema.ValidationError as e:
        return [Violation(severity="hard", code="schema_violation", message=str(e.message))]
    return []


def validate_invariants(
    value: dict[str, Any],
    invariants: list[dict[str, Any]],
) -> list[Violation]:
    violations: list[Violation] = []
    for inv in invariants:
        rule = inv.get("rule", "")
        severity = inv.get("severity", "soft")
        message = inv.get("message", f"Invariant failed: {rule}")

        if rule == "required_fields":
            fields = inv.get("fields", [])
            for f in fields:
                if f not in value or value[f] is None or value[f] == "":
                    violations.append(
                        Violation(severity=severity, code="required_field_missing", message=f"Missing required field: {f}")
                    )

        elif rule == "positive_number":
            field = inv.get("field", "")
            if field in value:
                try:
                    if float(value[field]) <= 0:
                        violations.append(Violation(severity=severity, code="positive_number", message=message))
                except (ValueError, TypeError):
                    violations.append(Violation(severity=severity, code="positive_number", message=message))

        elif rule == "max_length":
            field = inv.get("field", "")
            max_len = inv.get("max", 1000)
            if field in value and isinstance(value[field], str) and len(value[field]) > max_len:
                violations.append(Violation(severity=severity, code="max_length", message=message))

        elif rule == "enum":
            field = inv.get("field", "")
            allowed = inv.get("values", [])
            if field in value and value[field] not in allowed:
                violations.append(
                    Violation(severity=severity, code="enum_violation", message=f"{field} must be one of {allowed}")
                )

    return violations


def check_patch_op(
    value: dict[str, Any],
    json_schema: dict[str, Any],
    invariants: list[dict[str, Any]],
) -> list[Violation]:
    violations: list[Violation] = []
    violations.extend(validate_against_schema(value, json_schema))
    violations.extend(validate_invariants(value, invariants))
    return violations
