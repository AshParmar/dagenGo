import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Bookmark } from "lucide-react";

import { PageHeader } from "@/components/dagengo/page-header";
import { useResearchStore } from "@/store/research";

export const Route = createFileRoute("/app/saved")({
  component: SavedPage,
});

function SavedPage() {
  const navigate = useNavigate();
  const allSessions = useResearchStore((state) => state.sessions);
  const setActiveSession = useResearchStore((state) => state.setActiveSession);
  const sessions = allSessions.filter((session) => session.favorite || session.pinned);

  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-10">
      <PageHeader
        icon={Bookmark}
        title="Saved research"
        subtitle="Pin the answers you'll want to return to."
      />
      <div className="mt-8 divide-y divide-border rounded-xl border border-border bg-card/40 backdrop-blur">
        {sessions.map((session) => (
          <button
            key={session.id}
            onClick={() => {
              setActiveSession(session.id);
              navigate({ to: "/app/research/$id", params: { id: session.id } });
            }}
            className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition-colors hover:bg-accent/40"
          >
            <div className="min-w-0">
              <div className="truncate text-[14px] font-medium">{session.title}</div>
              <div className="mt-1 text-[11px] text-muted-foreground">
                {new Date(session.updatedAt).toLocaleString()}
              </div>
            </div>
            <span className="rounded-lg border border-border bg-card px-3 py-1.5 text-[12px] text-muted-foreground">
              Open
            </span>
          </button>
        ))}
        {sessions.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <Bookmark className="h-6 w-6 text-muted-foreground" />
            <div className="mt-3 text-[14px] font-medium">Nothing saved yet</div>
            <p className="mt-1 max-w-sm text-[12px] text-muted-foreground">
              Open any research session and tap the bookmark icon to keep it here.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
