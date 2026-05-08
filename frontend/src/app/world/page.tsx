"use client";

import { useCallback, useState } from "react";
import { EmptyState } from "@/components/shared/EmptyState";
import { useMissionContext } from "@/lib/state/MissionContext";
import { useInspector } from "@/components/layout/InspectorDrawer";
import { EntityTypeList } from "@/components/world/EntityTypeList";
import { EntityDetailView } from "@/components/world/EntityDetail";
import { SchemaInspector } from "@/components/world/SchemaInspector";
import type { EntityDetail } from "@/lib/api/types";

export default function WorldPage() {
  const { mission, world } = useMissionContext();
  const { openInspector } = useInspector();
  const [selectedEntity, setSelectedEntity] = useState<EntityDetail | null>(null);

  const handleSelectEntity = useCallback(
    (entity: EntityDetail) => {
      setSelectedEntity(entity);
      const type = world?.entity_types.find(
        (t) => t.type_name === entity.type_name,
      );
      openInspector(
        entity.entity_id,
        <div className="flex flex-col gap-4">
          <EntityDetailView entity={entity} />
          {type && (
            <div className="border-t border-white/[0.06] pt-4">
              <SchemaInspector type={type} />
            </div>
          )}
        </div>,
      );
    },
    [world, openInspector],
  );

  if (!mission) {
    return (
      <EmptyState
        title="No Mission Loaded"
        description="Load a mission from Mission Control to explore the World Model."
      />
    );
  }

  if (!world || world.entities.length === 0) {
    return (
      <EmptyState
        title="World Model Empty"
        description="Load a demo mission or import a mission pack to populate the shared world model."
      />
    );
  }

  return (
    <div className="flex h-full flex-col md:flex-row">
      <div className="max-h-72 shrink-0 overflow-y-auto border-b border-white/[0.08] p-3 md:max-h-none md:w-80 md:border-b-0 md:border-r">
        <h2 className="mb-3 px-3 text-xs font-semibold uppercase text-zinc-500">
          Entity Types ({world.entity_types.length})
        </h2>
        <EntityTypeList
          types={world.entity_types}
          entities={world.entities}
          selectedEntityId={selectedEntity?.entity_id ?? null}
          onSelectEntity={handleSelectEntity}
        />
      </div>

      <div className="flex-1 overflow-y-auto p-4 md:p-6">
        {selectedEntity ? (
          <EntityDetailView entity={selectedEntity} />
        ) : (
          <div className="flex items-center justify-center h-full text-sm text-zinc-500">
            Select an entity from the list
          </div>
        )}
      </div>
    </div>
  );
}
