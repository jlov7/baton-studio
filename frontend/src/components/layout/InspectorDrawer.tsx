"use client";

import { useState, type ReactNode } from "react";
import { X } from "@phosphor-icons/react";

interface InspectorDrawerProps {
  children: ReactNode;
  title?: string;
  open?: boolean;
  onClose?: () => void;
}

export function InspectorDrawer({
  children,
  title = "Inspector",
  open = false,
  onClose,
}: InspectorDrawerProps) {
  const [width, setWidth] = useState(360);

  if (!open) return null;

  return (
    <aside
      className="fixed inset-x-3 bottom-20 top-20 z-30 flex flex-col overflow-hidden rounded-lg border border-white/[0.1] bg-[#090a0c] shadow-2xl md:relative md:inset-auto md:rounded-none md:border-y-0 md:border-r-0 md:bg-zinc-950"
      style={{ width: `min(calc(100vw - 1.5rem), ${width}px)` }}
    >
      {/* Resize handle */}
      <div
        className="absolute left-0 top-0 bottom-0 z-10 hidden w-1 cursor-col-resize hover:bg-cyan-500/30 md:block"
        onMouseDown={(e) => {
          const startX = e.clientX;
          const startW = width;
          const onMove = (ev: MouseEvent) => {
            const delta = startX - ev.clientX;
            setWidth(Math.max(280, Math.min(600, startW + delta)));
          };
          const onUp = () => {
            document.removeEventListener("mousemove", onMove);
            document.removeEventListener("mouseup", onUp);
          };
          document.addEventListener("mousemove", onMove);
          document.addEventListener("mouseup", onUp);
        }}
      />

      {/* Header */}
      <div className="flex h-10 shrink-0 items-center gap-2 border-b border-white/[0.08] px-3">
        <span className="flex-1 truncate text-xs font-medium uppercase text-zinc-400">
          {title}
        </span>
        {onClose && (
          <button
            onClick={onClose}
            className="focus-ring rounded p-1 text-zinc-500 transition-colors hover:text-zinc-300"
            aria-label="Close inspector"
          >
            <X size={16} weight="bold" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3">{children}</div>
    </aside>
  );
}

// Context for managing inspector state from any screen
import { createContext, useCallback, useContext } from "react";

interface InspectorState {
  open: boolean;
  title: string;
  content: ReactNode;
  openInspector: (title: string, content: ReactNode) => void;
  closeInspector: () => void;
}

const InspectorContext = createContext<InspectorState | null>(null);

export function InspectorProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("Inspector");
  const [content, setContent] = useState<ReactNode>(null);

  const openInspector = useCallback((t: string, c: ReactNode) => {
    setTitle(t);
    setContent(c);
    setOpen(true);
  }, []);

  const closeInspector = useCallback(() => {
    setOpen(false);
  }, []);

  return (
    <InspectorContext.Provider
      value={{ open, title, content, openInspector, closeInspector }}
    >
      {children}
    </InspectorContext.Provider>
  );
}

export function useInspector() {
  const ctx = useContext(InspectorContext);
  if (!ctx) throw new Error("useInspector must be used within InspectorProvider");
  return ctx;
}
