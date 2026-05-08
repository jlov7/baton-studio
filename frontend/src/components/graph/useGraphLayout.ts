"use client";

import { useMemo } from "react";
import type { Edge, Node } from "@xyflow/react";
import type { CausalGraphSnapshot } from "@/lib/api/types";
import { getEdgeStyle, getEdgeLabel } from "./EdgeTypes";

interface LayoutResult {
  nodes: Node[];
  edges: Edge[];
}

export function useGraphLayout(graph: CausalGraphSnapshot | null): LayoutResult {
  return useMemo(() => {
    if (!graph || graph.nodes.length === 0) {
      return { nodes: [], edges: [] };
    }

    // Simple grid layout with type-based grouping
    const typeGroups: Record<string, typeof graph.nodes> = {};
    for (const n of graph.nodes) {
      const t = n.node_type || "other";
      (typeGroups[t] ??= []).push(n);
    }

    const nodes: Node[] = [];
    const colWidth = 250;
    const rowHeight = 80;
    let col = 0;

    for (const [, group] of Object.entries(typeGroups)) {
      group.forEach((n, row) => {
        nodes.push({
          id: n.node_id,
          type: "causal",
          position: { x: col * colWidth + 50, y: row * rowHeight + 50 },
          data: {
            label: n.label,
            nodeType: n.node_type,
            status: n.status,
            metadata: n.metadata,
          },
        });
      });
      col++;
    }

    const edges: Edge[] = graph.edges.map((e) => ({
      id: e.edge_id,
      source: e.from_id,
      target: e.to_id,
      label: getEdgeLabel(e.edge_type),
      style: getEdgeStyle(e.edge_type),
      labelStyle: { fill: "#71717a", fontSize: 10 },
      labelBgStyle: { fill: "#18181b", fillOpacity: 0.9 },
      labelBgPadding: [4, 2] as [number, number],
      animated: e.edge_type === "invalidates",
    }));

    return { nodes, edges };
  }, [graph]);
}
