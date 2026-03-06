import { cn } from "@/lib/utils/cn";

const VARIANTS = {
  default: "bg-zinc-800 text-zinc-300",
  amber: "bg-amber-500/15 text-amber-400",
  cyan: "bg-cyan-500/15 text-cyan-400",
  emerald: "bg-emerald-500/15 text-emerald-400",
  red: "bg-red-500/15 text-red-400",
  blue: "bg-blue-500/15 text-blue-400",
} as const;

interface BadgeProps {
  variant?: keyof typeof VARIANTS;
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant = "default", children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium",
        VARIANTS[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
