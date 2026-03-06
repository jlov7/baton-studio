"use client";

import { cn } from "@/lib/utils/cn";

interface VersionDiffProps {
  oldValue: Record<string, unknown>;
  newValue: Record<string, unknown>;
}

export function VersionDiff({ oldValue, newValue }: VersionDiffProps) {
  const allKeys = Array.from(
    new Set([...Object.keys(oldValue), ...Object.keys(newValue)]),
  );

  const changes = allKeys
    .map((key) => {
      const oldV = JSON.stringify(oldValue[key]);
      const newV = JSON.stringify(newValue[key]);
      if (oldV === newV) return null;
      return { key, oldV: oldV ?? "undefined", newV: newV ?? "undefined" };
    })
    .filter(Boolean) as { key: string; oldV: string; newV: string }[];

  if (changes.length === 0) return null;

  return (
    <div className="flex flex-col gap-0.5 text-xs font-mono mt-1">
      {changes.map((c) => (
        <div key={c.key} className="flex flex-col">
          <span className="text-zinc-500">{c.key}:</span>
          <div className="flex gap-2 ml-2">
            <span className={cn("text-red-400/70")}>- {c.oldV}</span>
          </div>
          <div className="flex gap-2 ml-2">
            <span className={cn("text-emerald-400/70")}>+ {c.newV}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
