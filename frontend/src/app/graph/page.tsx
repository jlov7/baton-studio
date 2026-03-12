"use client";

import { useCallback, useState } from "react";
import { ReactFlowProvider } from "reactflow";
import { EmptyState } from "@/components/shared/EmptyState";
import { useMissionContext } from "@/lib/state/MissionContext";
import { useInspector } from "@/components/layout/InspectorDrawer";
import { CausalGraphCanvas } from "@/components/graph/CausalGraphCanvas";
import { GraphToolbar } from "@/components/graph/GraphToolbar";
import { Badge } from "@/components/shared/Badge";
import { MonoText } from "@/components/shared/MonoText";
import type { CausalNodeDetail } from "@/lib/api/types";

export default function GraphPage() {
  const { mission, graph } = useMissionContext();
  const { openInspector } = useInspector();
  const [lens, setLens] = useState("all");

  const handleNodeClick = useCallback(
    (node: CausalNodeDetail) => {
      openInspector(
        node.label,
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Badge variant="amber">{node.node_type}</Badge>
            {node.status === "stale" && <Badge variant="red">STALE</Badge>}
          </div>
          <MonoText>{node.node_id}</MonoText>
          <div>
            <h4 className="text-xs text-zinc-500 uppercase tracking-wider mb-1">
              Label
            </h4>
            <p className="text-sm text-zinc-300">{node.label}</p>
          </div>
          {Object.keys(node.metadata).length > 0 && (
            <div>
              <h4 className="text-xs text-zinc-500 uppercase tracking-wider mb-1">
                Metadata
              </h4>
              <pre className="text-xs font-mono text-zinc-400 bg-zinc-900/80 rounded-lg p-2 border border-white/[0.06]">
                {JSON.stringify(node.metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>,
      );
    },
    [openInspector],
  );

  if (!mission) {
    return (
      <EmptyState
        title="No Mission Loaded"
        description="Load a mission from Mission Control to view the Causal Graph."
      />
    );
  }

  if (!graph || graph.nodes.length === 0) {
    return (
      <EmptyState
        title="Causal Graph Empty"
        description="Load a demo mission or import a mission pack to build causal relationships between entities."
      />
    );
  }

  return (
    <div className="flex flex-col h-full">
      <GraphToolbar
        activeLens={lens}
        onLensChange={setLens}
        onSearch={() => {}}
        nodeCount={graph.nodes.length}
        edgeCount={graph.edges.length}
      />
      <div className="flex-1">
        <ReactFlowProvider>
          <CausalGraphCanvas graph={graph} onNodeClick={handleNodeClick} />
        </ReactFlowProvider>
      </div>
    </div>
  );
}
