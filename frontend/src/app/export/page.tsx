"use client";

import { useCallback } from "react";
import { EmptyState } from "@/components/shared/EmptyState";
import { useMissionContext } from "@/lib/state/MissionContext";
import { ExportPanel } from "@/components/export/ExportPanel";
import { ImportPanel } from "@/components/export/ImportPanel";

export default function ExportPage() {
  const { mission, setMissionId } = useMissionContext();

  const handleImported = useCallback(
    (missionId: string) => {
      setMissionId(missionId);
    },
    [setMissionId],
  );

  if (!mission) {
    return (
      <div className="flex flex-col gap-6 p-6 max-w-2xl">
        <EmptyState
          title="No Mission Loaded"
          description="Import a mission pack or load a demo mission from Mission Control."
        />
        <ImportPanel onImported={handleImported} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6 max-w-2xl">
      <h2 className="text-lg font-semibold">Export / Mission Packs</h2>
      <ExportPanel
        missionId={mission.mission_id}
        missionTitle={mission.title}
      />
      <ImportPanel onImported={handleImported} />
    </div>
  );
}
