from __future__ import annotations

from typing import Any

from baton_substrate.models.common import Violation


def check_required_id(value: dict[str, Any], entity_id: str) -> list[Violation]:
    if not entity_id or not entity_id.strip():
        return [Violation(severity="hard", code="empty_id", message="Entity ID cannot be empty")]
    return []


def check_type_registered(type_name: str, registered_types: set[str]) -> list[Violation]:
    if type_name not in registered_types:
        return [
            Violation(
                severity="hard",
                code="unknown_type",
                message=f"Entity type '{type_name}' is not registered",
            )
        ]
    return []
