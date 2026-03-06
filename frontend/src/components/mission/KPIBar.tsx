"use client";

import type { SCMetricResponse } from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";

interface KPIBarProps {
  scMetric: SCMetricResponse | null;
  violationCount: number;
  invalidationCount: number;
}

export function KPIBar({ scMetric, violationCount, invalidationCount }: KPIBarProps) {
  const sc = scMetric?.sc_current ?? 1.0;
  const scColor = sc >= 0.7 ? "text-emerald-400" : sc >= 0.4 ? "text-amber-400" : "text-red-400";

  return (
    <div className="grid grid-cols-3 gap-4">
      <KPICard
        label="Structural Continuity"
        value={sc.toFixed(3)}
        valueClass={scColor}
      />
      <KPICard
        label="Invariant Violations"
        value={String(violationCount)}
        valueClass={violationCount > 0 ? "text-red-400" : "text-zinc-300"}
      />
      <KPICard
        label="Causal Invalidations"
        value={String(invalidationCount)}
        valueClass={invalidationCount > 0 ? "text-amber-400" : "text-zinc-300"}
      />
    </div>
  );
}

function KPICard({
  label,
  value,
  valueClass,
}: {
  label: string;
  value: string;
  valueClass: string;
}) {
  return (
    <div className="flex flex-col gap-1 p-3 rounded-xl border border-white/[0.06] bg-zinc-900/60">
      <span className="text-[11px] text-zinc-500 uppercase tracking-wider">
        {label}
      </span>
      <span className={cn("text-2xl font-mono font-semibold", valueClass)}>
        {value}
      </span>
    </div>
  );
}
