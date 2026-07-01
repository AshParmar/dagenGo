import { ArrowUp, Mic, Paperclip } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useRef, useState } from "react";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  autoFocus?: boolean;
  compact?: boolean;
  disabled?: boolean;
}

const placeholderLines = [
  "Ask anything...",
  "Research across languages...",
  "Verify facts before they reach you...",
  "Discover connections in a knowledge graph...",
];

export function ResearchInput({ value, onChange, onSubmit, autoFocus, compact, disabled }: Props) {
  const [idx, setIdx] = useState(0);
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const id = setInterval(() => setIdx((i) => (i + 1) % placeholderLines.length), 3200);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (autoFocus) ref.current?.focus();
  }, [autoFocus]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="group relative rounded-2xl border border-border bg-card/60 backdrop-blur-xl shadow-[0_30px_80px_-30px_rgba(0,0,0,0.6)] transition-all focus-within:border-primary/50 focus-within:shadow-[0_30px_80px_-20px_rgba(143,188,139,0.18)]"
    >
      <textarea
        ref={ref}
        rows={compact ? 2 : 3}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && (event.metaKey || event.ctrlKey || !event.shiftKey)) {
            event.preventDefault();
            if (value.trim()) onSubmit();
          }
        }}
        placeholder={placeholderLines[idx]}
        className="block w-full resize-none rounded-2xl bg-transparent px-5 pb-14 pt-4 text-[15px] leading-relaxed text-foreground placeholder:text-muted-foreground/70 focus:outline-none"
      />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-between px-3 py-2.5">
        <div className="pointer-events-auto flex items-center gap-1">
          <IconButton title="Upload (coming soon)" disabled>
            <Paperclip className="h-3.5 w-3.5" />
          </IconButton>
          <IconButton title="Voice (coming soon)" disabled>
            <Mic className="h-3.5 w-3.5" />
          </IconButton>
        </div>
        <div className="pointer-events-auto flex items-center gap-2">
          <span className="hidden font-mono text-[10px] text-muted-foreground sm:inline">
            Ctrl Enter
          </span>
          <button
            type="button"
            onClick={onSubmit}
            disabled={!value.trim() || disabled}
            className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-primary px-3 text-[12px] font-medium text-primary-foreground transition-colors hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:bg-accent disabled:text-muted-foreground"
          >
            Research <ArrowUp className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function IconButton({
  children,
  title,
  disabled,
}: {
  children: React.ReactNode;
  title: string;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      title={title}
      disabled={disabled}
      className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
    >
      {children}
    </button>
  );
}
