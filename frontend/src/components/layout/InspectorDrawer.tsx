"use client";

import { useState, type ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

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
      className="relative flex flex-col bg-zinc-950 border-l border-white/[0.06] shrink-0 overflow-hidden"
      style={{ width }}
    >
      {/* Resize handle */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-amber-500/30 z-10"
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
      <div className="flex items-center h-10 px-3 border-b border-white/[0.06] gap-2 shrink-0">
        <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider flex-1">
          {title}
        </span>
        {onClose && (
          <button
            onClick={onClose}
            className="text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
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
