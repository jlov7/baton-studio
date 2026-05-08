from __future__ import annotations

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MissionRow(Base):
    __tablename__ = "missions"
    mission_id: Mapped[str] = mapped_column(Text, primary_key=True)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False, default="")
    energy_budget: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="idle")


class EntityTypeRow(Base):
    __tablename__ = "entity_types"
    mission_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("missions.mission_id", ondelete="CASCADE"),
        primary_key=True,
    )
    type_name: Mapped[str] = mapped_column(Text, primary_key=True)
    json_schema: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    invariants_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class EntityRow(Base):
    __tablename__ = "entities"
    mission_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("missions.mission_id", ondelete="CASCADE"),
        primary_key=True,
    )
    entity_id: Mapped[str] = mapped_column(Text, primary_key=True)
    type_name: Mapped[str] = mapped_column(Text, nullable=False)
    deleted_at: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_by: Mapped[str | None] = mapped_column(Text, nullable=True)


class EntityVersionRow(Base):
    __tablename__ = "entity_versions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["mission_id", "entity_id"],
            ["entities.mission_id", "entities.entity_id"],
        ),
        Index("ix_entity_versions_mission_entity", "mission_id", "entity_id", "version"),
    )

    mission_id: Mapped[str] = mapped_column(Text, primary_key=True)
    entity_id: Mapped[str] = mapped_column(Text, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[str] = mapped_column(Text, nullable=False)
    value_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class PatchRow(Base):
    __tablename__ = "patches"
    __table_args__ = (
        Index("ix_patches_mission_status", "mission_id", "status"),
        Index("ix_patches_mission_created", "mission_id", "created_at"),
    )

    proposal_id: Mapped[str] = mapped_column(Text, primary_key=True)
    mission_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("missions.mission_id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[str] = mapped_column(Text, nullable=False)
    patch_json: Mapped[str] = mapped_column(Text, nullable=False)
    violations_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")


class CausalNodeRow(Base):
    __tablename__ = "causal_nodes"
    __table_args__ = (Index("ix_causal_nodes_mission_status", "mission_id", "status"),)

    mission_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("missions.mission_id", ondelete="CASCADE"),
        primary_key=True,
    )
    node_id: Mapped[str] = mapped_column(Text, primary_key=True)
    node_type: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="valid")


class CausalEdgeRow(Base):
    __tablename__ = "causal_edges"
    __table_args__ = (
        ForeignKeyConstraint(
            ["mission_id", "from_id"],
            ["causal_nodes.mission_id", "causal_nodes.node_id"],
        ),
        ForeignKeyConstraint(
            ["mission_id", "to_id"],
            ["causal_nodes.mission_id", "causal_nodes.node_id"],
        ),
        Index("ix_causal_edges_mission_from", "mission_id", "from_id"),
        Index("ix_causal_edges_mission_to", "mission_id", "to_id"),
    )

    mission_id: Mapped[str] = mapped_column(Text, primary_key=True)
    edge_id: Mapped[str] = mapped_column(Text, primary_key=True)
    from_id: Mapped[str] = mapped_column(Text, nullable=False)
    to_id: Mapped[str] = mapped_column(Text, nullable=False)
    edge_type: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class EnergyAccountRow(Base):
    __tablename__ = "energy_accounts"
    __table_args__ = (Index("ix_energy_accounts_mission", "mission_id"),)

    mission_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("missions.mission_id", ondelete="CASCADE"),
        primary_key=True,
    )
    actor_id: Mapped[str] = mapped_column(Text, primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class BatonStateRow(Base):
    __tablename__ = "baton_state"
    mission_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("missions.mission_id", ondelete="CASCADE"),
        primary_key=True,
    )
    holder_actor_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    queue_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    lease_expires_at: Mapped[str | None] = mapped_column(Text, nullable=True)


class EventRow(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_mission_ts_event", "mission_id", "ts", "event_id"),
        Index("ix_events_mission_type_ts", "mission_id", "type", "ts"),
    )

    event_id: Mapped[str] = mapped_column(Text, primary_key=True)
    mission_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("missions.mission_id", ondelete="CASCADE"),
        nullable=False,
    )
    ts: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    actor_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class AgentRow(Base):
    __tablename__ = "agents"
    __table_args__ = (Index("ix_agents_mission_status", "mission_id", "status"),)

    mission_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("missions.mission_id", ondelete="CASCADE"),
        primary_key=True,
    )
    actor_id: Mapped[str] = mapped_column(Text, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    role: Mapped[str] = mapped_column(Text, nullable=False, default="agent")
    joined_at: Mapped[str] = mapped_column(Text, nullable=False)
    last_seen_at: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
