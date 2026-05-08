"use client";

import { useCallback, useState } from "react";
import { DownloadSimple } from "@phosphor-icons/react";
import { API_BASE } from "@/config/constants";
import { authHeaders } from "@/lib/api/client";

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
        headers: authHeaders(),
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
    <div className="panel flex flex-col gap-4 p-5">
      <h3 className="text-sm font-medium text-zinc-300">Export Mission Pack</h3>
      <p className="text-xs text-zinc-500">
        Download a complete snapshot of <strong>{missionTitle}</strong> including
        all entities, causal graph, events, and energy records.
      </p>
      <button
        onClick={handleExport}
        disabled={exporting}
        className="focus-ring inline-flex self-start items-center gap-2 rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-zinc-950 transition-colors hover:bg-cyan-200 disabled:opacity-50"
      >
        <DownloadSimple size={15} weight="bold" />
        {exporting ? "Exporting..." : "Download .zip"}
      </button>
    </div>
  );
}
