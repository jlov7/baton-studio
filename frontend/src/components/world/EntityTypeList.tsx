"use client";

import { useState } from "react";
import { CaretRight } from "@phosphor-icons/react";
import type { EntityDetail, EntityTypeSchema } from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";
import { Badge } from "@/components/shared/Badge";

interface EntityTypeListProps {
  types: EntityTypeSchema[];
  entities: EntityDetail[];
  selectedEntityId: string | null;
  onSelectEntity: (entity: EntityDetail) => void;
}

export function EntityTypeList({
  types,
  entities,
  selectedEntityId,
  onSelectEntity,
}: EntityTypeListProps) {
  const [expandedType, setExpandedType] = useState<string | null>(
    types[0]?.type_name ?? null,
  );

  const grouped = types.map((t) => ({
    type: t,
    items: entities.filter((e) => e.type_name === t.type_name),
  }));

  return (
    <div className="flex flex-col gap-1">
      {grouped.map(({ type, items }) => (
        <div key={type.type_name}>
          <button
            onClick={() =>
              setExpandedType(
                expandedType === type.type_name ? null : type.type_name,
              )
            }
            className="focus-ring flex w-full items-center gap-2 rounded-md px-3 py-2 text-left transition-colors hover:bg-white/[0.04]"
          >
            <CaretRight
              size={12}
              weight="bold"
              className={cn(
                "text-zinc-500 transition-transform",
                expandedType === type.type_name && "rotate-90",
              )}
            />
            <span className="text-sm font-medium text-zinc-300">
              {type.type_name}
            </span>
            <Badge variant="default" className="ml-auto">
              {items.length}
            </Badge>
          </button>

          {expandedType === type.type_name && (
            <div className="flex flex-col gap-0.5 ml-5 mt-0.5">
              {items.map((entity) => (
                <button
                  key={entity.entity_id}
                  onClick={() => onSelectEntity(entity)}
                  className={cn(
                    "focus-ring flex items-center gap-2 rounded-md px-3 py-1.5 text-left text-sm transition-colors",
                    selectedEntityId === entity.entity_id
                      ? "bg-cyan-400/10 text-cyan-300"
                      : "text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-300",
                  )}
                >
                  <span className="font-mono text-xs truncate">
                    {entity.entity_id}
                  </span>
                  <span className="text-[11px] text-zinc-500 ml-auto shrink-0">
                    v{entity.latest_version}
                  </span>
                </button>
              ))}
              {items.length === 0 && (
                <span className="text-xs text-zinc-600 px-3 py-1">
                  No entities
                </span>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
