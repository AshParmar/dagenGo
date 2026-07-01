import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { ArrowLeft, Bookmark, Clipboard, Download, FileText, Share2 } from "lucide-react";
import { toast } from "sonner";

import { useResearchStore } from "@/store/research";
import { ExecutionPanel } from "@/components/dagengo/execution-panel";
import { Markdown } from "@/components/dagengo/markdown";
import { CitationCard } from "@/components/dagengo/citation-card";
import { Timeline } from "@/components/dagengo/timeline";
import { TypingIndicator, Skeleton } from "@/components/dagengo/loading-states";

export const Route = createFileRoute("/app/research/$id")({
  component: ResultPage,
});

function ResultPage() {
  const { id } = Route.useParams();
  const {
    query,
    answer,
    stages,
    isRunning,
    startedAt,
    citations,
    timeline,
    error,
    metrics,
    metadata,
    activeSessionId,
    setActiveSession,
    toggleFavorite,
    sessions,
  } = useResearchStore();
  const [tab, setTab] = useState<"answer" | "sources" | "timeline">("answer");
  const [elapsed, setElapsed] = useState(0);
  const activeSession = sessions.find((session) => session.id === activeSessionId);

  useEffect(() => {
    if (!startedAt || !isRunning) return;
    const id = setInterval(() => setElapsed(Date.now() - startedAt), 100);
    return () => clearInterval(id);
  }, [startedAt, isRunning]);

  const totalMs = isRunning
    ? elapsed
    : stages.reduce((sum, s) => sum + (s.elapsedMs ?? 0), 0);

  useEffect(() => {
    if (id !== "live") setActiveSession(id);
  }, [id, setActiveSession]);

  const copyAnswer = async () => {
    await navigator.clipboard.writeText(answer);
    toast.success("Answer copied");
  };

  const shareResearch = async () => {
    await navigator.clipboard.writeText(window.location.href);
    toast.success("Research link copied");
  };

  const downloadMarkdown = () => {
    const blob = new Blob([`# ${query}\n\n${answer}`], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${(activeSession?.title || "dagengo-research").replace(/[^\w-]+/g, "-")}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      {/* Main content */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Header */}
        <header className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-border bg-background/80 px-5 py-3 backdrop-blur md:px-8">
          <div className="flex min-w-0 items-center gap-3">
            <Link
              to="/app"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              aria-label="Back"
            >
              <ArrowLeft className="h-4 w-4" />
            </Link>
            <div className="min-w-0">
              <div className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Query
              </div>
              <div className="truncate text-[13px] font-medium text-foreground">
                {query || "Loading..."}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <IconBtn
              label="Save"
              active={Boolean(activeSession?.favorite)}
              onClick={() => activeSessionId && toggleFavorite(activeSessionId)}
            >
              <Bookmark className="h-3.5 w-3.5" />
            </IconBtn>
            <IconBtn label="Share" onClick={shareResearch}>
              <Share2 className="h-3.5 w-3.5" />
            </IconBtn>
          </div>
        </header>

        {(metrics.confidence !== undefined ||
          metrics.groundedness !== undefined ||
          metrics.hallucination !== undefined ||
          metadata.documents_retrieved !== undefined) && (
          <div className="grid gap-2 border-b border-border px-5 py-3 md:grid-cols-4 md:px-8">
            {metrics.confidence !== undefined && (
              <Stat label="Confidence" value={`${(metrics.confidence * 100).toFixed(0)}%`} />
            )}
            {metrics.groundedness !== undefined && (
              <Stat label="Groundedness" value={`${(metrics.groundedness * 100).toFixed(0)}%`} />
            )}
            {metrics.hallucination !== undefined && (
              <Stat label="Hallucination" value={`${(metrics.hallucination * 100).toFixed(0)}%`} />
            )}
            {metadata.documents_retrieved !== undefined && (
              <Stat label="Docs Retrieved" value={`${metadata.documents_retrieved}`} />
            )}
          </div>
        )}

        {/* Tabs */}
        <div className="flex items-center gap-1 border-b border-border px-5 md:px-8">
          {(["answer", "sources", "timeline"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`relative px-3 py-2.5 text-[12px] font-medium capitalize transition-colors ${tab === t ? "text-foreground" : "text-muted-foreground hover:text-foreground"}`}
            >
              {t}
              {tab === t && (
                <motion.span
                  layoutId="tab-underline"
                  className="absolute inset-x-2 bottom-0 h-px bg-primary"
                />
              )}
            </button>
          ))}
        </div>

        <div className="mx-auto w-full max-w-3xl px-5 py-8 md:px-8">
          {tab === "answer" && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {error && (
                <div className="mb-4 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
                  {error}
                </div>
              )}
              {answer ? (
                <>
                  <div className="mb-4 flex flex-wrap gap-2">
                    <ActionButton onClick={copyAnswer} label="Copy">
                      <Clipboard className="h-3.5 w-3.5" />
                    </ActionButton>
                    <ActionButton onClick={downloadMarkdown} label="Markdown">
                      <Download className="h-3.5 w-3.5" />
                    </ActionButton>
                    <ActionButton onClick={() => window.print()} label="PDF">
                      <FileText className="h-3.5 w-3.5" />
                    </ActionButton>
                  </div>
                  <Markdown source={answer} />
                </>
              ) : (
                <div className="space-y-3">
                  <Skeleton className="h-5 w-2/3" />
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-11/12" />
                  <Skeleton className="h-3 w-10/12" />
                  {!isRunning && (
                    <div className="pt-2 text-[13px] text-muted-foreground">
                      Submit a query from the home screen to generate a live answer.
                    </div>
                  )}
                </div>
              )}
              {isRunning && (
                <div className="mt-2 inline-flex items-center gap-2 text-[12px] text-muted-foreground">
                  <TypingIndicator /> Streaming...
                </div>
              )}
            </motion.div>
          )}

          {tab === "sources" &&
            (citations.length > 0 ? (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {citations.map((c, i) => (
                  <CitationCard key={c.id} citation={c} index={i} />
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-border bg-card/40 p-6 text-sm text-muted-foreground">
                The backend has not returned citations for this query yet.
              </div>
            ))}

          {tab === "timeline" && (
            <div className="rounded-xl border border-border bg-card/40 p-6 backdrop-blur">
              <Timeline events={timeline} />
            </div>
          )}
        </div>
      </div>

      {/* Execution sidebar */}
      <aside className="border-t border-border bg-surface/60 backdrop-blur lg:w-[340px] lg:shrink-0 lg:border-l lg:border-t-0">
        <ExecutionPanel stages={stages} totalMs={totalMs} />
      </aside>
    </div>
  );
}

function IconBtn({
  children,
  label,
  active,
  onClick,
}: {
  children: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className={`flex h-8 w-8 items-center justify-center rounded-lg transition-colors hover:bg-accent hover:text-foreground ${
        active ? "text-primary" : "text-muted-foreground"
      }`}
    >
      {children}
    </button>
  );
}

function ActionButton({
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
      onClick={onClick}
      className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-border bg-card px-3 text-[12px] text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
    >
      {children}
      {label}
    </button>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-card/50 px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm font-medium text-foreground">{value}</div>
    </div>
  );
}
