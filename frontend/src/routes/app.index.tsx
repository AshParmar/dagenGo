import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { motion } from "motion/react";
import { Clock, Sparkles } from "lucide-react";
import { ResearchInput } from "@/components/dagengo/research-input";
import { SUGGESTED_PROMPTS } from "@/lib/research-content";
import { useSubmitResearch } from "@/hooks/use-submit-research";
import { useResearchStore } from "@/store/research";

export const Route = createFileRoute("/app/")({
  component: ResearchHome,
});

function ResearchHome() {
  const navigate = useNavigate();
  const { query, setQuery, sessions, setActiveSession } = useResearchStore();
  const submitResearch = useSubmitResearch();

  const submit = (q?: string) => {
    const value = (q ?? query).trim();
    if (!value) return;
    submitResearch.mutate(value);
    navigate({ to: "/app/research/$id", params: { id: "live" } });
  };

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-8 text-center"
      >
        <div className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card/60 px-3 py-1 text-[11px] text-muted-foreground backdrop-blur">
          <Sparkles className="h-3 w-3 text-primary" /> Cross-lingual research session
        </div>
        <h1 className="mt-5 text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
          What would you like to research?
        </h1>
        <p className="mt-3 text-[14px] text-muted-foreground">
          Ask in any language. We'll search, verify, and build a knowledge graph for you.
        </p>
      </motion.div>

      <ResearchInput
        value={query}
        onChange={setQuery}
        onSubmit={() => submit()}
        autoFocus
        disabled={submitResearch.isPending}
      />

      <div className="mt-8">
        <div className="mb-3 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          Suggested prompts
        </div>
        <div className="flex flex-wrap gap-2">
          {SUGGESTED_PROMPTS.map((p, i) => (
            <motion.button
              key={p}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05 }}
              whileHover={{ y: -1 }}
              onClick={() => {
                setQuery(p);
                submit(p);
              }}
              className="rounded-full border border-border bg-card/60 px-3.5 py-1.5 text-left text-[12px] text-muted-foreground backdrop-blur transition-colors hover:border-primary/40 hover:text-foreground"
            >
              {p}
            </motion.button>
          ))}
        </div>
      </div>

      <div className="mt-12">
        <div className="mb-3 flex items-center gap-2 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          <Clock className="h-3 w-3" /> Recent
        </div>
        <div className="divide-y divide-border rounded-xl border border-border bg-card/40 backdrop-blur">
          {sessions.slice(0, 6).map((session) => (
            <button
              key={session.id}
              onClick={() => {
                setActiveSession(session.id);
                navigate({ to: "/app/research/$id", params: { id: session.id } });
              }}
              className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left transition-colors hover:bg-accent/40"
            >
              <span className="truncate text-[13px] text-foreground">{session.title}</span>
              <div className="flex shrink-0 items-center gap-2 text-[11px] text-muted-foreground">
                {session.metadata?.provider && <span>{session.metadata.provider}</span>}
                <span>{new Date(session.updatedAt).toLocaleDateString()}</span>
              </div>
            </button>
          ))}
          {sessions.length === 0 && (
            <div className="px-4 py-6 text-[13px] text-muted-foreground">
              Your completed research sessions will appear here.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
