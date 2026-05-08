"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ClockCounterClockwise,
  Database,
  DownloadSimple,
  GitBranch,
  House,
} from "@phosphor-icons/react";
import { useMissionContext } from "@/lib/state/MissionContext";
import { cn } from "@/lib/utils/cn";

const NAV_ITEMS = [
  { href: "/mission", label: "Mission", icon: House },
  { href: "/world", label: "World", icon: Database },
  { href: "/graph", label: "Graph", icon: GitBranch },
  { href: "/timeline", label: "Timeline", icon: ClockCounterClockwise },
  { href: "/export", label: "Export", icon: DownloadSimple },
] as const;

export function NavRail() {
  const pathname = usePathname();
  const { missionId } = useMissionContext();
  const query = missionId ? `?mission=${encodeURIComponent(missionId)}` : "";

  return (
    <nav className="z-20 flex border-white/[0.08] bg-[#08090b]/95 backdrop-blur-xl md:w-[76px] md:flex-col md:items-center md:border-r md:py-4 fixed inset-x-0 bottom-0 h-16 border-t md:static md:inset-auto md:h-screen md:border-t-0">
      <Link
        href={`/mission${query}`}
        className="hidden md:flex h-11 w-11 items-center justify-center rounded-md border border-cyan-400/20 bg-cyan-400/[0.08] text-cyan-200"
        aria-label="Baton Studio"
      >
        <span className="font-mono text-sm font-semibold">B</span>
      </Link>

      <div className="grid w-full grid-cols-5 md:mt-6 md:flex md:flex-col md:gap-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={`${item.href}${query}`}
              className={cn(
                "group flex min-w-0 flex-col items-center justify-center gap-1 px-1 py-2 text-[10px] transition-colors md:h-[58px] md:w-[58px] md:rounded-md",
                active
                  ? "text-cyan-100 md:bg-white/[0.08]"
                  : "text-zinc-500 hover:text-zinc-200 md:hover:bg-white/[0.05]",
              )}
            >
              <Icon
                size={20}
                weight={active ? "duotone" : "regular"}
                className={cn(active && "text-cyan-300")}
              />
              <span className="truncate leading-none">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
