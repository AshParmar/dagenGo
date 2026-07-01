import { createFileRoute } from "@tanstack/react-router";
import { Maximize2, Network, Search, ZoomIn, ZoomOut } from "lucide-react";
import { useState } from "react";

import { KnowledgeGraph } from "@/components/dagengo/knowledge-graph";
import { PageHeader } from "@/components/dagengo/page-header";
import { useResearchStore } from "@/store/research";

export const Route = createFileRoute("/app/graph")({
  component: GraphPage,
});

function GraphPage() {
  const graph = useResearchStore((state) => state.knowledgeGraph);
  const [searchTerm, setSearchTerm] = useState("");
  const [zoom, setZoom] = useState(1);

  return (
    <div className="flex h-screen flex-col">
      <div className="px-6 pt-10">
        <PageHeader
          icon={Network}
          title="Knowledge Graph"
          subtitle="Entities, relations and evidence synthesized across languages."
        />
        <div className="mt-4 flex items-center justify-between gap-3">
          <div className="flex flex-1 items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5 text-[13px]">
            <Search className="h-3.5 w-3.5 text-muted-foreground" />
            <input
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search nodes..."
              className="w-full bg-transparent placeholder:text-muted-foreground focus:outline-none"
            />
          </div>
          <div className="flex items-center gap-1">
            <Tool label="Zoom in" onClick={() => setZoom((value) => Math.min(1.8, value + 0.15))}>
              <ZoomIn className="h-3.5 w-3.5" />
            </Tool>
            <Tool
              label="Zoom out"
              onClick={() => setZoom((value) => Math.max(0.65, value - 0.15))}
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </Tool>
            <Tool label="Reset" onClick={() => setZoom(1)}>
              <Maximize2 className="h-3.5 w-3.5" />
            </Tool>
          </div>
        </div>
      </div>
      <div className="flex-1 p-6">
        <KnowledgeGraph graph={graph} searchTerm={searchTerm} zoom={zoom} />
      </div>
    </div>
  );
}

function Tool({
  children,
  label,
  onClick,
}: {
  children: React.ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-card text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
    >
      {children}
    </button>
  );
}
