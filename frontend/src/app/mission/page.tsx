"use client";

import { useCallback, useMemo, useState } from "react";
import { EmptyState } from "@/components/shared/EmptyState";
import { useMissionContext } from "@/lib/state/MissionContext";
import { startDemo } from "@/lib/api/demo";
import { HeroPanel } from "@/components/mission/HeroPanel";
import { SquadStrip } from "@/components/mission/SquadStrip";
import { KPIBar } from "@/components/mission/KPIBar";
import { API_BASE } from "@/config/constants";

export default function MissionPage() {
  const {
    mission,
    baton,
    agents,
    scMetric,
    events,
    setMissionId,
    loading,
  } = useMissionContext();
  const [demoLoading, setDemoLoading] = useState(false);

  const handleLoadDemo = useCallback(async () => {
    setDemoLoading(true);
    try {
      const res = await startDemo();
      setMissionId(res.mission_id);
    } finally {
      setDemoLoading(false);
    }
  }, [setMissionId]);

  const handleExport = useCallback(() => {
    if (!mission) return;
    window.open(`${API_BASE}/missions/${mission.mission_id}/export`, "_blank");
  }, [mission]);

  const violationCount = useMemo(
    () => events.filter((e) => e.type === "invariant.violation").length,
    [events],
  );

  const invalidationCount = useMemo(
    () => events.filter((e) => e.type === "causal.invalidated").length,
    [events],
  );

  if (!mission) {
    return (
      <EmptyState
        title="No Mission Loaded"
        description="Load a demo mission to explore Baton Studio's multi-agent coordination features."
        action={
          <button
            onClick={handleLoadDemo}
            disabled={demoLoading || loading}
            className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black font-medium text-sm rounded-lg transition-colors disabled:opacity-50"
          >
            {demoLoading ? "Loading Demo..." : "Load Demo Mission"}
          </button>
        }
      />
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6 max-w-5xl">
      <HeroPanel
        mission={mission}
        batonHolder={baton?.holder ?? null}
        batonQueue={baton?.queue ?? []}
        totalEnergy={agents.reduce((s, a) => s + a.energy_balance, 0)}
        onExport={handleExport}
      />

      <section>
        <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-3">
          Squad
        </h2>
        <SquadStrip
          agents={agents}
          batonHolder={baton?.holder ?? null}
          missionBudget={mission.energy_budget}
        />
      </section>

      <section>
        <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-3">
          Key Metrics
        </h2>
        <KPIBar
          scMetric={scMetric}
          violationCount={violationCount}
          invalidationCount={invalidationCount}
        />
      </section>
    </div>
  );
}
