"use client";

import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

interface ToastItem {
  id: number;
  message: string;
  variant: "info" | "error" | "warning";
  action?: { label: string; onClick: () => void };
}

interface ToastContextType {
  toast: (
    message: string,
    opts?: {
      variant?: ToastItem["variant"];
      action?: ToastItem["action"];
    },
  ) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

let nextId = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const toast = useCallback(
    (
      message: string,
      opts?: { variant?: ToastItem["variant"]; action?: ToastItem["action"] },
    ) => {
      const id = nextId++;
      setItems((prev) => [
        ...prev,
        { id, message, variant: opts?.variant ?? "info", action: opts?.action },
      ]);
      setTimeout(() => {
        setItems((prev) => prev.filter((t) => t.id !== id));
      }, 5000);
    },
    [],
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50 pointer-events-none">
        {items.map((item) => (
          <div
            key={item.id}
            className={cn(
              "pointer-events-auto flex items-center gap-3 px-4 py-2.5 rounded-xl border shadow-lg animate-slide-in max-w-sm",
              item.variant === "error" &&
                "bg-red-500/10 border-red-500/30 text-red-400",
              item.variant === "warning" &&
                "bg-amber-500/10 border-amber-500/30 text-amber-400",
              item.variant === "info" &&
                "bg-zinc-800 border-white/[0.06] text-zinc-300",
            )}
          >
            <span className="text-sm flex-1">{item.message}</span>
            {item.action && (
              <button
                onClick={item.action.onClick}
                className="text-xs font-medium underline underline-offset-2 shrink-0"
              >
                {item.action.label}
              </button>
            )}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
