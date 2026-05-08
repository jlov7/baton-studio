"use client";

import type { ReactNode } from "react";
import { Tray } from "@phosphor-icons/react";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex h-full min-h-[300px] flex-col items-center justify-center p-8 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-md border border-white/[0.08] bg-white/[0.04] text-zinc-500">
        <Tray size={24} weight="duotone" />
      </div>
      <h3 className="text-sm font-medium text-zinc-300 mb-1">{title}</h3>
      {description && (
        <p className="text-xs text-zinc-500 max-w-xs mb-4">{description}</p>
      )}
      {action}
    </div>
  );
}
