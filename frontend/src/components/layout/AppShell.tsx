"use client";

import type { ReactNode } from "react";
import { NavRail } from "./NavRail";
import { TopHUD } from "./TopHUD";
import { InspectorDrawer, useInspector } from "./InspectorDrawer";
import { useKeyboardShortcuts } from "@/lib/hooks/useKeyboard";

export function AppShell({ children }: { children: ReactNode }) {
  const { open, title, content, closeInspector } = useInspector();
  useKeyboardShortcuts();

  return (
    <div className="app-grid flex h-screen overflow-hidden bg-[#090a0c] text-zinc-100">
      <NavRail />
      <div className="flex flex-col flex-1 min-w-0">
        <TopHUD />
        <div className="flex flex-1 min-h-0 pb-16 md:pb-0">
          <main className="flex-1 overflow-y-auto">{children}</main>
          <InspectorDrawer open={open} title={title} onClose={closeInspector}>
            {content}
          </InspectorDrawer>
        </div>
      </div>
    </div>
  );
}
