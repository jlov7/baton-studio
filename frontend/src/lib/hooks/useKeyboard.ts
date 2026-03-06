"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const SCREEN_KEYS: Record<string, string> = {
  "1": "/mission",
  "2": "/world",
  "3": "/graph",
  "4": "/timeline",
  "5": "/export",
};

export function useKeyboardShortcuts() {
  const router = useRouter();

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        return;
      }

      // Number keys → navigate screens
      if (SCREEN_KEYS[e.key]) {
        e.preventDefault();
        router.push(SCREEN_KEYS[e.key]);
        return;
      }

      // / → focus search (if present)
      if (e.key === "/") {
        e.preventDefault();
        const search = document.querySelector<HTMLInputElement>(
          'input[type="text"]',
        );
        search?.focus();
        return;
      }

      // Esc → blur active element
      if (e.key === "Escape") {
        (document.activeElement as HTMLElement)?.blur();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [router]);
}
