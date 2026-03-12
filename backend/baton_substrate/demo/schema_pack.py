from __future__ import annotations

ENTITY_TYPES: list[dict[str, object]] = [
    {
        "type_name": "PlanStep",
        "json_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["draft", "active", "done"]},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5},
            },
            "required": ["title", "status"],
        },
        "invariants": [
            {"rule": "required_fields", "fields": ["title", "status"], "severity": "hard"},
            {
                "rule": "enum",
                "field": "status",
                "values": ["draft", "active", "done"],
                "severity": "hard",
            },
        ],
    },
    {
        "type_name": "Evidence",
        "json_schema": {
            "type": "object",
            "properties": {
                "claim": {"type": "string"},
                "source": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["claim"],
        },
        "invariants": [
            {"rule": "required_fields", "fields": ["claim"], "severity": "hard"},
            {"rule": "max_length", "field": "claim", "max": 500, "severity": "soft"},
        ],
    },
    {
        "type_name": "Decision",
        "json_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "resolution": {"type": "string"},
                "rationale": {"type": "string"},
                "decided_by": {"type": "string"},
            },
            "required": ["question"],
        },
        "invariants": [
            {"rule": "required_fields", "fields": ["question"], "severity": "hard"},
        ],
    },
    {
        "type_name": "CodeArtifact",
        "json_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "language": {"type": "string"},
                "content_hash": {"type": "string"},
                "lines_of_code": {"type": "integer", "minimum": 0},
                "description": {"type": "string"},
            },
            "required": ["filename", "language"],
        },
        "invariants": [
            {"rule": "required_fields", "fields": ["filename", "language"], "severity": "hard"},
            {
                "rule": "positive_number",
                "field": "lines_of_code",
                "severity": "soft",
                "message": "lines_of_code should be positive",
            },
        ],
    },
]
