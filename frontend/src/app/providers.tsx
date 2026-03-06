"use client";

import type { ReactNode } from "react";
import { MissionProvider } from "@/lib/state/MissionContext";
import { InspectorProvider } from "@/components/layout/InspectorDrawer";
import { AppShell } from "@/components/layout/AppShell";
import { BackendCheck } from "@/components/onboarding/BackendCheck";
import { ToastProvider } from "@/components/shared/Toast";
import { ViolationToaster } from "@/components/shared/ViolationToaster";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <BackendCheck>
      <MissionProvider>
        <ToastProvider>
          <ViolationToaster />
          <InspectorProvider>
            <AppShell>{children}</AppShell>
          </InspectorProvider>
        </ToastProvider>
      </MissionProvider>
    </BackendCheck>
  );
}
