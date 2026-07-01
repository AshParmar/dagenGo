import { createFileRoute } from "@tanstack/react-router";
import { Info } from "lucide-react";
import { PageHeader } from "@/components/dagengo/page-header";

export const Route = createFileRoute("/app/about")({
  component: AboutPage,
});

function AboutPage() {
  return (
    <div className="mx-auto w-full max-w-2xl px-6 py-10">
      <PageHeader
        icon={Info}
        title="About DagenGo"
        subtitle="A research agent designed to be trusted."
      />
      <div className="mt-8 space-y-4 rounded-xl border border-border bg-card/40 p-6 text-[14px] leading-relaxed text-foreground/90 backdrop-blur">
        <p>
          DagenGo is a cross-lingual research and fact verification agent. It plans, retrieves and
          reasons across languages — and grounds every claim in cited, scored evidence.
        </p>
        <p className="text-muted-foreground">
          Built with hybrid retrieval, knowledge graphs, cross-encoder reranking, verification,
          hallucination detection, and a final LLM judge. Every stage is inspectable.
        </p>
      </div>
    </div>
  );
}
