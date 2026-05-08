from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from baton_substrate.models.common import CausalEdgeInput, Patch, Violation


class ProposePatchRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    patch: Patch
    causal: dict[str, list[CausalEdgeInput]] | None = None


class ProposePatchResponse(BaseModel):
    proposal_id: str
    accepted: bool
    violations: list[Violation] = Field(default_factory=list)


class CommitPatchRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    proposal_id: str = Field(min_length=1)


class CommitPatchResponse(BaseModel):
    committed: bool
    new_versions: list[dict[str, Any]] = Field(default_factory=list)
    message: str = ""
