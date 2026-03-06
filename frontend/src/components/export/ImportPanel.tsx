"use client";

import { useCallback, useRef, useState } from "react";
import { API_BASE } from "@/config/constants";

interface ImportPanelProps {
  onImported: (missionId: string) => void;
}

export function ImportPanel({ onImported }: ImportPanelProps) {
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleImport = useCallback(
    async (file: File) => {
      setImporting(true);
      setError(null);
      try {
        const form = new FormData();
        form.append("file", file);
        const res = await fetch(`${API_BASE}/missions/import`, {
          method: "POST",
          body: form,
        });
        if (!res.ok) throw new Error("Import failed");
        const data = await res.json();
        onImported(data.mission_id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Import failed");
      } finally {
        setImporting(false);
      }
    },
    [onImported],
  );

  return (
    <div className="flex flex-col gap-4 p-5 rounded-2xl border border-white/[0.06] bg-zinc-900/60">
      <h3 className="text-sm font-medium text-zinc-300">Import Mission Pack</h3>
      <p className="text-xs text-zinc-500">
        Load a previously exported mission pack (.zip) to review in replay mode.
      </p>
      <input
        ref={inputRef}
        type="file"
        accept=".zip"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleImport(file);
        }}
      />
      <button
        onClick={() => inputRef.current?.click()}
        disabled={importing}
        className="self-start px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-medium text-sm rounded-lg transition-colors disabled:opacity-50"
      >
        {importing ? "Importing..." : "Choose .zip File"}
      </button>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
