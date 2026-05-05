import React, { useEffect, useMemo, useState } from "react";
import ReactFlow, { Background, Controls } from "reactflow";
import "reactflow/dist/style.css";
import dagre from "dagre";
import { getRepositoryGraph } from "../services/api";

function layout(nodes, edges) {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR" });
  g.setDefaultEdgeLabel(() => ({}));

  nodes.forEach((node) => {
    g.setNode(node.id, { width: 180, height: 40 });
  });

  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });

  dagre.layout(g);

  return nodes.map((node) => {
    const pos = g.node(node.id);
    return {
      ...node,
      position: {
        x: pos.x,
        y: pos.y,
      },
    };
  });
}

export default function DependencyGraph({ repoId }) {
  const [rawNodes, setRawNodes] = useState([]);
  const [rawEdges, setRawEdges] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        const graphData = await getRepositoryGraph(repoId);
        setRawNodes(graphData.nodes || []);
        setRawEdges(graphData.edges || []);
      } catch (err) {
        console.error("Failed to load graph:", err);
      } finally {
        setLoading(false);
      }
    }

    if (repoId) loadGraph();
  }, [repoId]);

  const nodes = useMemo(() => {
    const baseNodes = rawNodes.map((n) => ({
      id: String(n.id),
      data: { label: n.path.split(/[/\\]/).pop() },
      position: { x: 0, y: 0 },
    }));

    return layout(
      baseNodes,
      rawEdges.map((e) => ({
        id: `${e.source}-${e.target}`,
        source: String(e.source),
        target: String(e.target)
      }))
    );
  }, [rawNodes, rawEdges]);

  const edges = useMemo(() => {
    return rawEdges.map((e) => ({
      id: `${e.source}-${e.target}`,
      source: String(e.source),
      target: String(e.target)
    }));
  }, [rawEdges]);

  if (loading) {
    return <div>Loading graph...</div>;
  }

  return (
    <div style={{ width: "100%", height: "100vh" }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}