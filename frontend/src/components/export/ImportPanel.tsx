"use client";

import { useCallback, useRef, useState } from "react";
import { UploadSimple } from "@phosphor-icons/react";
import { API_BASE } from "@/config/constants";
import { authHeaders } from "@/lib/api/client";

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
          headers: authHeaders(),
          body: form,
        });
        if (!res.ok) {
          const body = await res.json().catch(() => null);
          throw new Error(body?.detail ?? "Import failed");
        }
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
    <div className="panel flex flex-col gap-4 p-5">
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
        className="focus-ring inline-flex self-start items-center gap-2 rounded-md border border-white/[0.08] bg-white/[0.04] px-4 py-2 text-sm font-medium text-zinc-200 transition-colors hover:bg-white/[0.08] disabled:opacity-50"
      >
        <UploadSimple size={15} weight="bold" />
        {importing ? "Importing..." : "Choose .zip File"}
      </button>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
