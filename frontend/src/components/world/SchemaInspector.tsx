"use client";

import type { EntityTypeSchema } from "@/lib/api/types";
import { Badge } from "@/components/shared/Badge";

interface SchemaInspectorProps {
  type: EntityTypeSchema;
}

export function SchemaInspector({ type }: SchemaInspectorProps) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <Badge variant="amber">{type.type_name}</Badge>
        <span className="text-xs text-zinc-500">Schema</span>
      </div>

      <div className="flex flex-col gap-1">
        <h4 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
          JSON Schema
        </h4>
        <pre className="text-xs font-mono text-zinc-300 bg-zinc-900/80 rounded-lg p-3 overflow-x-auto border border-white/[0.06]">
          {JSON.stringify(type.json_schema, null, 2)}
        </pre>
      </div>

      {type.invariants.length > 0 && (
        <div className="flex flex-col gap-1">
          <h4 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Invariants
          </h4>
          <div className="flex flex-col gap-1">
            {type.invariants.map((inv, i) => (
              <div
                key={i}
                className="flex items-center gap-2 p-2 rounded-lg border border-white/[0.06] bg-zinc-900/40 text-xs"
              >
                <Badge
                  variant={
                    (inv as Record<string, unknown>).severity === "hard"
                      ? "red"
                      : "amber"
                  }
                >
                  {String((inv as Record<string, unknown>).severity ?? "soft")}
                </Badge>
                <span className="font-mono text-zinc-300">
                  {String((inv as Record<string, unknown>).rule ?? (inv as Record<string, unknown>).type ?? JSON.stringify(inv))}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
