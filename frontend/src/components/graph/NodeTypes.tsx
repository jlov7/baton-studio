"use client";

import { memo } from "react";
import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { cn } from "@/lib/utils/cn";

type CausalNodeData = Record<string, unknown> & {
  label: string;
  nodeType: string;
  status: string;
  metadata: Record<string, unknown>;
};

type CausalNodeType = Node<CausalNodeData, "causal">;

const TYPE_STYLES: Record<string, { bg: string; border: string; text: string }> = {
  Evidence: {
    bg: "bg-blue-500/10",
    border: "border-blue-500/40",
    text: "text-blue-400",
  },
  Decision: {
    bg: "bg-purple-500/10",
    border: "border-purple-500/40",
    text: "text-purple-400",
  },
  PlanStep: {
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/40",
    text: "text-emerald-400",
  },
  CodeArtifact: {
    bg: "bg-amber-500/10",
    border: "border-amber-500/40",
    text: "text-amber-400",
  },
  default: {
    bg: "bg-zinc-800/60",
    border: "border-white/[0.12]",
    text: "text-zinc-300",
  },
};

export const CausalNode = memo(function CausalNode({
  data,
}: NodeProps<CausalNodeType>) {
  const style = TYPE_STYLES[data.nodeType] ?? TYPE_STYLES.default;
  const stale = data.status === "stale";

  return (
    <>
      <Handle type="target" position={Position.Top} className="!bg-zinc-600 !w-2 !h-2 !border-0" />
      <div
        className={cn(
          "flex min-w-[120px] max-w-[200px] flex-col gap-0.5 rounded-lg border px-3 py-2 transition-all",
          style.bg,
          style.border,
          stale && "opacity-50 border-dashed",
        )}
      >
        <span className={cn("text-[10px] font-medium uppercase tracking-wider", style.text)}>
          {data.nodeType}
        </span>
        <span className="text-xs text-zinc-200 truncate">{data.label}</span>
        {stale && (
          <span className="text-[10px] text-red-400 font-medium">STALE</span>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-zinc-600 !w-2 !h-2 !border-0" />
    </>
  );
});

export const nodeTypes = {
  causal: CausalNode,
};
