from __future__ import annotations

from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class MissionRow(Base):
    __tablename__ = "missions"
    mission_id = Column(Text, primary_key=True)
    created_at = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    goal = Column(Text, nullable=False, default="")
    energy_budget = Column(Integer, nullable=False, default=1000)
    status = Column(Text, nullable=False, default="idle")


class EntityTypeRow(Base):
    __tablename__ = "entity_types"
    mission_id = Column(Text, primary_key=True)
    type_name = Column(Text, primary_key=True)
    json_schema = Column(Text, nullable=False, default="{}")
    invariants_json = Column(Text, nullable=False, default="[]")


class EntityRow(Base):
    __tablename__ = "entities"
    mission_id = Column(Text, primary_key=True)
    entity_id = Column(Text, primary_key=True)
    type_name = Column(Text, nullable=False)


class EntityVersionRow(Base):
    __tablename__ = "entity_versions"
    mission_id = Column(Text, primary_key=True)
    entity_id = Column(Text, primary_key=True)
    version = Column(Integer, primary_key=True)
    created_at = Column(Text, nullable=False)
    actor_id = Column(Text, nullable=False)
    value_json = Column(Text, nullable=False, default="{}")


class PatchRow(Base):
    __tablename__ = "patches"
    proposal_id = Column(Text, primary_key=True)
    mission_id = Column(Text, nullable=False)
    created_at = Column(Text, nullable=False)
    actor_id = Column(Text, nullable=False)
    patch_json = Column(Text, nullable=False)
    violations_json = Column(Text, nullable=False, default="[]")
    status = Column(Text, nullable=False, default="pending")


class CausalNodeRow(Base):
    __tablename__ = "causal_nodes"
    mission_id = Column(Text, primary_key=True)
    node_id = Column(Text, primary_key=True)
    node_type = Column(Text, nullable=False)
    label = Column(Text, nullable=False, default="")
    metadata_json = Column(Text, nullable=False, default="{}")
    status = Column(Text, nullable=False, default="valid")


class CausalEdgeRow(Base):
    __tablename__ = "causal_edges"
    mission_id = Column(Text, primary_key=True)
    edge_id = Column(Text, primary_key=True)
    from_id = Column(Text, nullable=False)
    to_id = Column(Text, nullable=False)
    edge_type = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")


class EnergyAccountRow(Base):
    __tablename__ = "energy_accounts"
    mission_id = Column(Text, primary_key=True)
    actor_id = Column(Text, primary_key=True)
    balance = Column(Integer, nullable=False, default=0)


class BatonStateRow(Base):
    __tablename__ = "baton_state"
    mission_id = Column(Text, primary_key=True)
    holder_actor_id = Column(Text, nullable=True)
    queue_json = Column(Text, nullable=False, default="[]")
    lease_expires_at = Column(Text, nullable=True)


class EventRow(Base):
    __tablename__ = "events"
    event_id = Column(Text, primary_key=True)
    mission_id = Column(Text, nullable=False)
    ts = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    actor_json = Column(Text, nullable=False, default="{}")
    payload_json = Column(Text, nullable=False, default="{}")


class AgentRow(Base):
    __tablename__ = "agents"
    mission_id = Column(Text, primary_key=True)
    actor_id = Column(Text, primary_key=True)
    display_name = Column(Text, nullable=False, default="")
    role = Column(Text, nullable=False, default="agent")
    joined_at = Column(Text, nullable=False)
    last_seen_at = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="active")
