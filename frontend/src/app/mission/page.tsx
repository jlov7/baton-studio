"use client";

import { useCallback, useMemo, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Database, GitBranch, Play } from "@phosphor-icons/react";
import { EmptyState } from "@/components/shared/EmptyState";
import { useMissionContext } from "@/lib/state/MissionContext";
import { startDemo } from "@/lib/api/demo";
import { HeroPanel } from "@/components/mission/HeroPanel";
import { SquadStrip } from "@/components/mission/SquadStrip";
import { KPIBar } from "@/components/mission/KPIBar";
import { EventCard } from "@/components/timeline/EventCard";

export default function MissionPage() {
  const { mission, baton, agents, scMetric, events, world, graph, setMissionId, loading } =
    useMissionContext();
  const router = useRouter();
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
    router.push(`/export?mission=${encodeURIComponent(mission.mission_id)}`);
  }, [mission, router]);

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
        description="Load the local demo mission or import a mission pack to inspect world state, baton arbitration, causality, energy, and replay."
        action={
          <button
            onClick={handleLoadDemo}
            disabled={demoLoading || loading}
            className="focus-ring inline-flex items-center gap-2 rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-zinc-950 transition-colors hover:bg-cyan-200 disabled:opacity-50"
          >
            <Play size={15} weight="fill" />
            {demoLoading ? "Loading Demo..." : "Load Demo Mission"}
          </button>
        }
      />
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-5 p-4 md:p-6">
      <HeroPanel
        mission={mission}
        batonHolder={baton?.holder ?? null}
        batonQueue={baton?.queue ?? []}
        totalEnergy={agents.reduce((s, a) => s + a.energy_balance, 0)}
        onExport={handleExport}
      />

      <KPIBar
        scMetric={scMetric}
        violationCount={violationCount}
        invalidationCount={invalidationCount}
      />

      <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <section className="min-w-0">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-xs font-semibold uppercase text-zinc-500">Squad</h2>
            <span className="font-mono text-[11px] text-zinc-600">{agents.length} actors</span>
          </div>
          <SquadStrip
            agents={agents}
            batonHolder={baton?.holder ?? null}
            missionBudget={mission.energy_budget}
          />
        </section>

        <section className="panel min-w-0 p-3">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-xs font-semibold uppercase text-zinc-500">Recent Events</h2>
            <button
              onClick={() => router.push(`/timeline?mission=${encodeURIComponent(mission.mission_id)}`)}
              className="focus-ring inline-flex items-center gap-1 rounded px-2 py-1 text-[11px] text-zinc-400 hover:bg-white/[0.06] hover:text-zinc-200"
            >
              Timeline <ArrowRight size={12} weight="bold" />
            </button>
          </div>
          <div className="max-h-[320px] overflow-y-auto">
            {events.slice(-8).map((event) => (
              <EventCard key={event.event_id} event={event} />
            ))}
          </div>
        </section>
      </div>

      <section className="grid gap-3 md:grid-cols-2">
        <RouteTile
          icon={<Database size={18} weight="duotone" />}
          title="World Model"
          value={`${world?.entities.length ?? 0} entities`}
          detail={`${world?.entity_types.length ?? 0} schemas, ${world?.pending_proposals ?? 0} pending proposals`}
          onClick={() => router.push(`/world?mission=${encodeURIComponent(mission.mission_id)}`)}
        />
        <RouteTile
          icon={<GitBranch size={18} weight="duotone" />}
          title="Causal Graph"
          value={`${graph?.nodes.length ?? 0} nodes`}
          detail={`${graph?.edges.length ?? 0} edges, ${invalidationCount} invalidation events`}
          onClick={() => router.push(`/graph?mission=${encodeURIComponent(mission.mission_id)}`)}
        />
      </section>
    </div>
  );
}

function RouteTile({
  icon,
  title,
  value,
  detail,
  onClick,
}: {
  icon: ReactNode;
  title: string;
  value: string;
  detail: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="panel focus-ring flex items-center gap-3 p-4 text-left transition-colors hover:bg-white/[0.06]"
    >
      <div className="flex h-9 w-9 items-center justify-center rounded-md border border-cyan-400/20 bg-cyan-400/[0.08] text-cyan-300">
        {icon}
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-sm font-semibold text-zinc-200">{title}</div>
        <div className="mt-0.5 truncate text-xs text-zinc-500">{detail}</div>
      </div>
      <div className="font-mono text-sm text-zinc-300">{value}</div>
    </button>
  );
}
