import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Bookmark, Clock, Pin, Search, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";

import { PageHeader } from "@/components/dagengo/page-header";
import { useResearchStore } from "@/store/research";

export const Route = createFileRoute("/app/history")({
  component: HistoryPage,
});

function HistoryPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const {
    sessions,
    setActiveSession,
    deleteSession,
    renameSession,
    toggleFavorite,
    togglePinned,
  } = useResearchStore();

  const filtered = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) return sessions;
    return sessions.filter((session) =>
      `${session.title} ${session.query ?? ""}`.toLowerCase().includes(needle),
    );
  }, [search, sessions]);

  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-10">
      <PageHeader icon={Clock} title="History" subtitle="Every research session, fully reproducible." />

      <div className="mt-6 flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-[13px]">
        <Search className="h-3.5 w-3.5 text-muted-foreground" />
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search history..."
          className="w-full bg-transparent placeholder:text-muted-foreground focus:outline-none"
        />
      </div>

      <div className="mt-4 divide-y divide-border rounded-xl border border-border bg-card/40 backdrop-blur">
        {filtered.map((session) => (
          <div key={session.id} className="flex items-center justify-between gap-4 px-5 py-4">
            <div className="min-w-0 flex-1">
              <input
                value={session.title}
                onChange={(event) => renameSession(session.id, event.target.value)}
                className="w-full truncate bg-transparent text-[14px] font-medium focus:outline-none"
                aria-label="Session title"
              />
              <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                <span>{new Date(session.updatedAt).toLocaleString()}</span>
                {session.metadata?.provider && <span>{session.metadata.provider}</span>}
                {session.metadata?.documents_retrieved !== undefined && (
                  <span>{session.metadata.documents_retrieved} sources</span>
                )}
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-1">
              <IconButton label="Pin" active={session.pinned} onClick={() => togglePinned(session.id)}>
                <Pin className="h-3.5 w-3.5" />
              </IconButton>
              <IconButton
                label="Favorite"
                active={session.favorite}
                onClick={() => toggleFavorite(session.id)}
              >
                <Bookmark className="h-3.5 w-3.5" />
              </IconButton>
              <button
                onClick={() => {
                  setActiveSession(session.id);
                  navigate({ to: "/app/research/$id", params: { id: session.id } });
                }}
                className="rounded-lg border border-border bg-card px-3 py-1.5 text-[12px] text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
              >
                Open
              </button>
              <IconButton label="Delete" onClick={() => deleteSession(session.id)}>
                <Trash2 className="h-3.5 w-3.5" />
              </IconButton>
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="px-5 py-12 text-center text-[13px] text-muted-foreground">
            No research sessions found.
          </div>
        )}
      </div>
    </div>
  );
}

function IconButton({
  children,
  label,
  active,
  onClick,
}: {
  children: React.ReactNode;
  label: string;
  active?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className={`flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-card transition-colors hover:border-primary/40 hover:text-foreground ${
        active ? "text-primary" : "text-muted-foreground"
      }`}
    >
      {children}
    </button>
  );
}
