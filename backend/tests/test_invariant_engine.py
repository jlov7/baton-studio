"""Tests for the invariant validation engine (no DB required)."""
from __future__ import annotations

from baton_substrate.invariants.builtin import check_required_id, check_type_registered
from baton_substrate.invariants.engine import (
    check_patch_op,
    validate_against_schema,
    validate_invariants,
)


# --- Schema validation ---

def test_schema_valid() -> None:
    schema = {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}
    violations = validate_against_schema({"title": "hello"}, schema)
    assert violations == []


def test_schema_missing_required_field() -> None:
    schema = {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}
    violations = validate_against_schema({}, schema)
    assert len(violations) == 1
    assert violations[0].severity == "hard"
    assert violations[0].code == "schema_violation"


def test_schema_wrong_type() -> None:
    schema = {"type": "object", "properties": {"count": {"type": "integer"}}}
    violations = validate_against_schema({"count": "not_a_number"}, schema)
    assert len(violations) == 1


def test_empty_schema_passes() -> None:
    assert validate_against_schema({"anything": "goes"}, {}) == []


# --- Invariant rules ---

def test_required_fields_present() -> None:
    inv = [{"rule": "required_fields", "fields": ["title", "status"], "severity": "hard"}]
    violations = validate_invariants({"title": "a", "status": "b"}, inv)
    assert violations == []


def test_required_fields_missing() -> None:
    inv = [{"rule": "required_fields", "fields": ["title", "status"], "severity": "hard"}]
    violations = validate_invariants({"title": "a"}, inv)
    assert len(violations) == 1
    assert "status" in violations[0].message


def test_required_fields_empty_string() -> None:
    inv = [{"rule": "required_fields", "fields": ["title"], "severity": "hard"}]
    violations = validate_invariants({"title": ""}, inv)
    assert len(violations) == 1


def test_positive_number_valid() -> None:
    inv = [{"rule": "positive_number", "field": "count", "severity": "soft", "message": "bad"}]
    assert validate_invariants({"count": 5}, inv) == []


def test_positive_number_zero() -> None:
    inv = [{"rule": "positive_number", "field": "count", "severity": "soft", "message": "bad"}]
    violations = validate_invariants({"count": 0}, inv)
    assert len(violations) == 1


def test_positive_number_negative() -> None:
    inv = [{"rule": "positive_number", "field": "count", "severity": "soft", "message": "bad"}]
    violations = validate_invariants({"count": -3}, inv)
    assert len(violations) == 1


def test_positive_number_not_present_skips() -> None:
    inv = [{"rule": "positive_number", "field": "count", "severity": "soft", "message": "bad"}]
    assert validate_invariants({}, inv) == []


def test_max_length_within() -> None:
    inv = [{"rule": "max_length", "field": "name", "max": 10, "severity": "soft", "message": "too long"}]
    assert validate_invariants({"name": "short"}, inv) == []


def test_max_length_exceeded() -> None:
    inv = [{"rule": "max_length", "field": "name", "max": 5, "severity": "soft", "message": "too long"}]
    violations = validate_invariants({"name": "toolongname"}, inv)
    assert len(violations) == 1


def test_enum_valid_value() -> None:
    inv = [{"rule": "enum", "field": "status", "values": ["todo", "done"], "severity": "hard"}]
    assert validate_invariants({"status": "todo"}, inv) == []


def test_enum_invalid_value() -> None:
    inv = [{"rule": "enum", "field": "status", "values": ["todo", "done"], "severity": "hard"}]
    violations = validate_invariants({"status": "invalid"}, inv)
    assert len(violations) == 1
    assert violations[0].severity == "hard"


# --- Builtin checks ---

def test_check_required_id_valid() -> None:
    assert check_required_id({}, "entity-1") == []


def test_check_required_id_empty() -> None:
    violations = check_required_id({}, "")
    assert len(violations) == 1
    assert violations[0].code == "empty_id"


def test_check_required_id_whitespace() -> None:
    violations = check_required_id({}, "   ")
    assert len(violations) == 1


def test_check_type_registered_valid() -> None:
    assert check_type_registered("Evidence", {"Evidence", "PlanStep"}) == []


def test_check_type_registered_unknown() -> None:
    violations = check_type_registered("Unknown", {"Evidence"})
    assert len(violations) == 1
    assert violations[0].code == "unknown_type"


# --- Combined check_patch_op ---

def test_check_patch_op_all_pass() -> None:
    schema = {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}
    invariants = [{"rule": "required_fields", "fields": ["title"], "severity": "hard"}]
    violations = check_patch_op({"title": "ok"}, schema, invariants)
    assert violations == []


def test_check_patch_op_schema_and_invariant_failures() -> None:
    schema = {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}
    invariants = [{"rule": "max_length", "field": "title", "max": 3, "severity": "soft", "message": "too long"}]
    violations = check_patch_op({"title": "toolong"}, schema, invariants)
    assert len(violations) == 1
    assert violations[0].code == "max_length"
