import { cn } from "@/lib/utils/cn";

interface MonoTextProps {
  children: React.ReactNode;
  className?: string;
}

export function MonoText({ children, className }: MonoTextProps) {
  return (
    <span className={cn("font-mono text-xs text-zinc-400", className)}>
      {children}
    </span>
  );
}
