"use client";

import { useCallback, useState } from "react";
import { API_BASE } from "@/config/constants";

interface ExportPanelProps {
  missionId: string;
  missionTitle: string;
}

export function ExportPanel({ missionId, missionTitle }: ExportPanelProps) {
  const [exporting, setExporting] = useState(false);

  const handleExport = useCallback(async () => {
    setExporting(true);
    try {
      const res = await fetch(`${API_BASE}/missions/${missionId}/export`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Export failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${missionId}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setExporting(false);
    }
  }, [missionId]);

  return (
    <div className="flex flex-col gap-4 p-5 rounded-2xl border border-white/[0.06] bg-zinc-900/60">
      <h3 className="text-sm font-medium text-zinc-300">Export Mission Pack</h3>
      <p className="text-xs text-zinc-500">
        Download a complete snapshot of <strong>{missionTitle}</strong> including
        all entities, causal graph, events, and energy records.
      </p>
      <button
        onClick={handleExport}
        disabled={exporting}
        className="self-start px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black font-medium text-sm rounded-lg transition-colors disabled:opacity-50"
      >
        {exporting ? "Exporting..." : "Download .zip"}
      </button>
    </div>
  );
}
