"use client";

import { useCallback, useEffect } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useNodesState,
  useEdgesState,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { CausalGraphSnapshot, CausalNodeDetail } from "@/lib/api/types";
import { nodeTypes } from "./NodeTypes";
import { useGraphLayout } from "./useGraphLayout";

interface CausalGraphCanvasProps {
  graph: CausalGraphSnapshot;
  onNodeClick?: (node: CausalNodeDetail) => void;
}

export function CausalGraphCanvas({ graph, onNodeClick }: CausalGraphCanvasProps) {
  const layout = useGraphLayout(graph);
  const [nodes, setNodes, onNodesChange] = useNodesState(layout.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layout.edges);

  useEffect(() => {
    setNodes(layout.nodes);
    setEdges(layout.edges);
  }, [layout.edges, layout.nodes, setEdges, setNodes]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const detail = graph.nodes.find((n) => n.node_id === node.id);
      if (detail && onNodeClick) onNodeClick(detail);
    },
    [graph, onNodeClick],
  );

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
        className="bg-[#0b0d10]"
      >
        <Background color="#27272a" gap={20} size={1} />
        <Controls
          className="!bg-zinc-800 !border-white/[0.06] !rounded-lg [&_button]:!bg-zinc-800 [&_button]:!border-white/[0.06] [&_button]:!text-zinc-400 [&_button:hover]:!bg-zinc-700"
        />
        <MiniMap
          nodeColor={() => "#52525b"}
          maskColor="rgba(0, 0, 0, 0.7)"
          className="!bg-zinc-900 !border-white/[0.06] !rounded-lg"
        />
      </ReactFlow>
    </div>
  );
}
