import { motion, AnimatePresence } from "motion/react";
import { Check, ChevronDown, Loader2, Circle, AlertCircle } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import type { PipelineStage } from "@/lib/research-types";

interface ExecutionPanelProps {
  stages: PipelineStage[];
  totalMs: number;
}

export function ExecutionPanel({ stages, totalMs }: ExecutionPanelProps) {
  const completed = stages.filter((s) => s.status === "completed").length;
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-border px-5 py-4">
        <div>
          <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Execution
          </div>
          <div className="mt-1 text-sm font-semibold">Pipeline</div>
        </div>
        <div className="text-right">
          <div className="font-mono text-xs text-muted-foreground">
            {(totalMs / 1000).toFixed(2)}s
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            {completed}/{stages.length} stages
          </div>
        </div>
      </div>
      <div className="scrollbar-thin flex-1 overflow-y-auto px-3 py-3">
        <ol className="relative">
          {stages.map((stage, i) => (
            <StageRow key={stage.id} stage={stage} isLast={i === stages.length - 1} />
          ))}
        </ol>
      </div>
    </div>
  );
}

function StageRow({ stage, isLast }: { stage: PipelineStage; isLast: boolean }) {
  const [open, setOpen] = useState(false);
  const interactive = stage.status === "completed";
  return (
    <li className="relative">
      {!isLast && (
        <span
          className={cn(
            "absolute left-[19px] top-7 h-[calc(100%-12px)] w-px",
            stage.status === "completed" ? "bg-primary/40" : "bg-border",
          )}
          aria-hidden
        />
      )}
      <button
        type="button"
        onClick={() => interactive && setOpen((o) => !o)}
        className={cn(
          "group flex w-full items-center gap-3 rounded-lg px-2 py-2 text-left transition-colors",
          interactive ? "hover:bg-accent/60" : "cursor-default",
        )}
      >
        <StageIcon status={stage.status} />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "truncate text-[13px] font-medium transition-colors",
                stage.status === "pending" && "text-muted-foreground/70",
                stage.status === "running" && "text-foreground",
                stage.status === "completed" && "text-foreground",
                stage.status === "failed" && "text-destructive",
              )}
            >
              {stage.label}
            </span>
            {stage.status === "running" && (
              <span className="text-[10px] font-medium uppercase tracking-wider text-primary">
                running
              </span>
            )}
          </div>
        </div>
        <span className="font-mono text-[11px] text-muted-foreground">
          {stage.elapsedMs > 0 ? `${(stage.elapsedMs / 1000).toFixed(2)}s` : "--"}
        </span>
        {interactive && stage.detail && (
          <ChevronDown
            className={cn(
              "h-3.5 w-3.5 text-muted-foreground transition-transform",
              open && "rotate-180",
            )}
          />
        )}
      </button>
      <AnimatePresence initial={false}>
        {open && stage.detail && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            className="overflow-hidden"
          >
            <div className="ml-10 mr-2 mb-2 mt-1 space-y-1.5 rounded-md border border-border bg-surface/60 p-3">
              {stage.detail.map((d) => (
                <div key={d.key} className="flex items-start gap-3 text-[12px]">
                  <span className="w-24 shrink-0 text-muted-foreground">{d.key}</span>
                  <span className="text-foreground/90">{d.value}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </li>
  );
}

function StageIcon({ status }: { status: PipelineStage["status"] }) {
  const base = "flex h-6 w-6 shrink-0 items-center justify-center rounded-full border";
  if (status === "completed") {
    return (
      <motion.div
        initial={{ scale: 0.6, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 380, damping: 24 }}
        className={cn(base, "border-primary/50 bg-primary/15 text-primary")}
      >
        <Check className="h-3 w-3" strokeWidth={3} />
      </motion.div>
    );
  }
  if (status === "running") {
    return (
      <div className={cn(base, "border-primary/60 bg-primary/10 text-primary pulse-ring")}>
        <Loader2 className="h-3 w-3 animate-spin" />
      </div>
    );
  }
  if (status === "failed") {
    return (
      <div className={cn(base, "border-destructive/60 bg-destructive/10 text-destructive")}>
        <AlertCircle className="h-3 w-3" />
      </div>
    );
  }
  return (
    <div className={cn(base, "border-border bg-transparent text-muted-foreground/50")}>
      <Circle className="h-2 w-2" />
    </div>
  );
}
