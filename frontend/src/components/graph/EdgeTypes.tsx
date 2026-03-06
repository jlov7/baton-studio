"use client";

const EDGE_COLORS: Record<string, string> = {
  supports: "#22c55e",
  contradicts: "#ef4444",
  depends_on: "#a855f7",
  derived_from: "#3b82f6",
  invalidates: "#f59e0b",
};

export function getEdgeStyle(edgeType: string) {
  const color = EDGE_COLORS[edgeType] ?? "#52525b";
  const dashed = edgeType === "contradicts" || edgeType === "invalidates";

  return {
    stroke: color,
    strokeWidth: 1.5,
    strokeDasharray: dashed ? "5 3" : undefined,
  };
}

export function getEdgeLabel(edgeType: string): string {
  return edgeType.replace(/_/g, " ");
}
