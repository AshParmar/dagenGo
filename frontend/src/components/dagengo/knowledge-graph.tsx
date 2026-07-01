import { motion } from "motion/react";
import { useMemo, useState } from "react";
import type { KnowledgeGraphData, KnowledgeGraphEdge } from "@/lib/research-types";

interface Node {
  id: string;
  label: string;
  type: "entity" | "concept" | "source";
  x: number;
  y: number;
}
interface Edge {
  from: string;
  to: string;
  label?: string;
}

export function KnowledgeGraph({
  graph,
  searchTerm = "",
  zoom = 1,
}: {
  graph?: KnowledgeGraphData | null;
  searchTerm?: string;
  zoom?: number;
}) {
  const [hover, setHover] = useState<string | null>(null);
  const { nodes, edges } = useMemo(() => {
    if (!graph?.nodes?.length) {
      return { nodes: [], edges: [] };
    }

    const width = 860;
    const height = 560;
    const radius = Math.min(width, height) / 2.8;
    const centerX = width / 2;
    const centerY = height / 2;

    const positions = graph.nodes.map((node, index) => {
      const angle = (index / Math.max(graph.nodes.length, 1)) * Math.PI * 2;
      const offsetX = Math.cos(angle) * radius;
      const offsetY = Math.sin(angle) * radius * 0.72;
      return {
        id: node.id,
        label: node.label,
        type: (node.type as Node["type"]) || "concept",
        x: node.x ?? centerX + offsetX,
        y: node.y ?? centerY + offsetY,
      } satisfies Node;
    });

    return {
      nodes: positions,
      edges: graph.edges.map((edge: KnowledgeGraphEdge) => ({
        from: edge.from,
        to: edge.to,
        label: edge.label,
      })),
    };
  }, [graph]);

  const byId = useMemo(() => Object.fromEntries(nodes.map((n) => [n.id, n])), [nodes]);
  const search = searchTerm.trim().toLowerCase();
  const matchedNodeIds = useMemo(
    () =>
      new Set(
        nodes
          .filter((node) => search && `${node.label} ${node.type}`.toLowerCase().includes(search))
          .map((node) => node.id),
      ),
    [nodes, search],
  );
  const relatedNodeIds = useMemo(() => {
    const related = new Set<string>();
    edges.forEach((edge) => {
      if (matchedNodeIds.has(edge.from) || matchedNodeIds.has(edge.to)) {
        related.add(edge.from);
        related.add(edge.to);
      }
    });
    return related;
  }, [edges, matchedNodeIds]);

  if (nodes.length === 0) {
    return (
      <div className="flex h-full w-full items-center justify-center rounded-xl border border-dashed border-border bg-card/40 p-8 text-center text-[13px] text-muted-foreground">
        Run a research query to build an interactive knowledge graph.
      </div>
    );
  }

  return (
    <div className="relative h-full w-full overflow-hidden rounded-xl border border-border bg-card">
      <svg viewBox="0 0 860 560" className="h-full w-full">
        <defs>
          <radialGradient id="node-grad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.95" />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity="0.25" />
          </radialGradient>
          <pattern id="kg-grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="var(--border)"
              strokeWidth="0.5"
              opacity="0.4"
            />
          </pattern>
        </defs>
        <rect width="860" height="560" fill="url(#kg-grid)" />
        <g transform={`translate(${430 - 430 * zoom} ${280 - 280 * zoom}) scale(${zoom})`}>
          {edges.map((e, i) => {
            const a = byId[e.from];
            const b = byId[e.to];
            if (!a || !b) return null;
            const highlighted =
              hover === e.from ||
              hover === e.to ||
              relatedNodeIds.has(e.from) ||
              relatedNodeIds.has(e.to);
            return (
              <g key={i}>
                <motion.line
                  x1={a.x}
                  y1={a.y}
                  x2={b.x}
                  y2={b.y}
                  stroke={highlighted ? "var(--primary)" : "var(--border)"}
                  strokeWidth={highlighted ? 1.4 : 1}
                  strokeOpacity={highlighted ? 0.9 : 0.55}
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{ duration: 0.8, delay: 0.2 + i * 0.05 }}
                />
                {e.label && highlighted && (
                  <text
                    x={(a.x + b.x) / 2}
                    y={(a.y + b.y) / 2 - 4}
                    textAnchor="middle"
                    className="fill-muted-foreground text-[10px]"
                  >
                    {e.label}
                  </text>
                )}
              </g>
            );
          })}
          {nodes.map((n, i) => {
            const r = n.type === "entity" ? 30 : n.type === "concept" ? 22 : 16;
            const matched = matchedNodeIds.has(n.id);
            const dimmed = search && !matched && !relatedNodeIds.has(n.id);
            return (
              <motion.g
                key={n.id}
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: dimmed ? 0.35 : 1, scale: 1 }}
                transition={{ delay: 0.1 + i * 0.05, type: "spring", stiffness: 220, damping: 18 }}
                onMouseEnter={() => setHover(n.id)}
                onMouseLeave={() => setHover(null)}
                className="cursor-pointer"
              >
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={r + 6}
                  fill="var(--primary)"
                  opacity={hover === n.id || matched ? 0.18 : 0.06}
                />
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={r}
                  fill="url(#node-grad)"
                  stroke="var(--primary)"
                  strokeWidth={matched ? 2 : 1.2}
                  strokeOpacity={matched ? 0.95 : 0.6}
                />
                <text
                  x={n.x}
                  y={n.y + r + 14}
                  textAnchor="middle"
                  className="fill-foreground text-[11px] font-medium"
                >
                  {n.label}
                </text>
              </motion.g>
            );
          })}
        </g>
      </svg>
      <div className="absolute left-4 top-4 flex items-center gap-3 rounded-lg border border-border bg-surface/80 px-3 py-2 text-[11px] backdrop-blur">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-primary" /> Entity
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-primary/60" /> Concept
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-primary/30" /> Source
        </span>
      </div>
      <div className="absolute right-4 top-4 rounded-lg border border-border bg-surface/80 px-3 py-1.5 text-[11px] text-muted-foreground backdrop-blur">
        {nodes.length} nodes · {edges.length} edges
      </div>
    </div>
  );
}
