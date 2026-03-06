"use client";

import { useState } from "react";
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
            className="flex items-center gap-2 w-full px-3 py-2 text-left rounded-lg hover:bg-white/[0.04] transition-colors"
          >
            <svg
              className={cn(
                "w-3 h-3 text-zinc-500 transition-transform",
                expandedType === type.type_name && "rotate-90",
              )}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 5l7 7-7 7"
              />
            </svg>
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
                    "flex items-center gap-2 px-3 py-1.5 text-left rounded-lg transition-colors text-sm",
                    selectedEntityId === entity.entity_id
                      ? "bg-amber-500/10 text-amber-400"
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
