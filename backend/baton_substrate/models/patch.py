from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from baton_substrate.models.common import CausalEdgeInput, Patch, Violation


class ProposePatchRequest(BaseModel):
    actor_id: str
    patch: Patch
    causal: dict[str, list[CausalEdgeInput]] | None = None


class ProposePatchResponse(BaseModel):
    proposal_id: str
    accepted: bool
    violations: list[Violation] = []


class CommitPatchRequest(BaseModel):
    actor_id: str
    proposal_id: str


class CommitPatchResponse(BaseModel):
    committed: bool
    new_versions: list[dict[str, Any]] = []
    message: str = ""
