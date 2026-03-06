"use client";

import type { EntityDetail as EntityDetailType } from "@/lib/api/types";
import { Badge } from "@/components/shared/Badge";
import { MonoText } from "@/components/shared/MonoText";
import { formatDate, agentName } from "@/lib/utils/formatters";
import { VersionDiff } from "./VersionDiff";

interface EntityDetailProps {
  entity: EntityDetailType;
}

export function EntityDetailView({ entity }: EntityDetailProps) {
  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <Badge variant="amber">{entity.type_name}</Badge>
          <MonoText>{entity.entity_id}</MonoText>
        </div>
        <span className="text-[11px] text-zinc-500">
          Latest version: v{entity.latest_version}
        </span>
      </div>

      {/* Current value */}
      <div className="flex flex-col gap-1">
        <h4 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
          Current Value
        </h4>
        <pre className="text-xs font-mono text-zinc-300 bg-zinc-900/80 rounded-lg p-3 overflow-x-auto border border-white/[0.06]">
          {JSON.stringify(entity.value, null, 2)}
        </pre>
      </div>

      {/* Version history */}
      {entity.versions.length > 0 && (
        <div className="flex flex-col gap-2">
          <h4 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Version History
          </h4>
          <div className="flex flex-col gap-2">
            {[...entity.versions].reverse().map((v, i, arr) => (
              <div
                key={v.version}
                className="flex flex-col gap-1 p-2 rounded-lg border border-white/[0.06] bg-zinc-900/40"
              >
                <div className="flex items-center gap-2 text-[11px]">
                  <Badge variant={v.version === entity.latest_version ? "emerald" : "default"}>
                    v{v.version}
                  </Badge>
                  <span className="text-zinc-500">{agentName(v.actor_id)}</span>
                  <span className="text-zinc-600 ml-auto">
                    {formatDate(v.created_at)}
                  </span>
                </div>
                {i < arr.length - 1 && (
                  <VersionDiff
                    oldValue={arr[i + 1].value}
                    newValue={v.value}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
