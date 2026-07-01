import { Copy, ExternalLink } from "lucide-react";
import { motion } from "motion/react";
import { toast } from "sonner";
import type { Citation } from "@/lib/research-types";

export function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const confidence = citation.confidence ?? 0;
  const confColor =
    confidence >= 0.9
      ? "text-primary"
      : confidence >= 0.8
        ? "text-warning"
        : "text-muted-foreground";
  const website = citation.website ?? citation.domain ?? citation.provider ?? "Source";
  const language = citation.language ?? "--";
  const link = citation.url ?? "#";
  return (
    <motion.article
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.25, ease: "easeOut" }}
      whileHover={{ y: -2 }}
      className="group block rounded-xl border border-border bg-card p-4 transition-colors hover:border-primary/40 hover:bg-card/80"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
          {citation.favicon_url && (
            <img src={citation.favicon_url} alt="" className="h-4 w-4 rounded-sm" loading="lazy" />
          )}
          <span className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] tracking-wide">
            {language}
          </span>
          <span className="truncate">{website}</span>
        </div>
        <span className={`font-mono text-[11px] ${confColor}`}>
          {(confidence * 100).toFixed(0)}%
        </span>
      </div>
      <div className="mt-2 text-[13px] font-medium leading-snug text-foreground line-clamp-2">
        {citation.title}
      </div>
      <p className="mt-1.5 text-[12px] leading-relaxed text-muted-foreground line-clamp-2">
        {citation.snippet ?? "No snippet was returned by the backend."}
      </p>
      {(citation.publication_date || citation.domain || citation.provider) && (
        <div className="mt-2 flex flex-wrap gap-2 text-[10px] text-muted-foreground">
          {citation.publication_date && (
            <span className="rounded-full border border-border px-2 py-0.5">
              {citation.publication_date}
            </span>
          )}
          {citation.domain && (
            <span className="rounded-full border border-border px-2 py-0.5">{citation.domain}</span>
          )}
          {citation.provider && (
            <span className="rounded-full border border-border px-2 py-0.5">
              {citation.provider}
            </span>
          )}
        </div>
      )}
      <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2.5">
        <span className="text-[11px] text-muted-foreground">
          {citation.source ?? citation.website ?? citation.domain ?? "Source"}
        </span>
        <div className="flex items-center gap-1">
          {citation.url && (
            <button
              type="button"
              onClick={async () => {
                await navigator.clipboard.writeText(citation.url ?? "");
                toast.success("Source link copied");
              }}
              className="inline-flex items-center gap-1 rounded-md px-1.5 py-1 text-[11px] text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
            >
              Copy <Copy className="h-3 w-3" />
            </button>
          )}
          <a
            href={link}
            target="_blank"
            rel="noreferrer noopener"
            className="inline-flex items-center gap-1 rounded-md px-1.5 py-1 text-[11px] text-primary transition-colors hover:bg-accent"
          >
            Open <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      </div>
    </motion.article>
  );
}
