import { Link, useRouterState } from "@tanstack/react-router";
import { Sparkles, Clock, Bookmark, Network, Settings, Info, Plus, User } from "lucide-react";
import { Wordmark } from "./logo";
import { cn } from "@/lib/utils";

type NavItem = { to: string; label: string; icon: typeof Sparkles; exact?: boolean };
const nav: NavItem[] = [
  { to: "/app", label: "New Research", icon: Sparkles, exact: true },
  { to: "/app/history", label: "History", icon: Clock },
  { to: "/app/saved", label: "Saved", icon: Bookmark },
  { to: "/app/graph", label: "Knowledge Graph", icon: Network },
  { to: "/app/settings", label: "Settings", icon: Settings },
  { to: "/app/about", label: "About", icon: Info },
];

export function AppSidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <aside className="hidden md:flex md:w-[248px] md:shrink-0 md:flex-col md:border-r md:border-border md:bg-sidebar">
      <div className="flex h-14 items-center px-5">
        <Link to="/">
          <Wordmark />
        </Link>
      </div>
      <div className="px-3">
        <Link
          to="/app"
          className="flex w-full items-center justify-between rounded-lg border border-border bg-card px-3 py-2 text-[13px] font-medium text-foreground transition-colors hover:border-primary/50 hover:bg-card/80"
        >
          <span className="flex items-center gap-2">
            <Plus className="h-3.5 w-3.5 text-primary" />
            New research
          </span>
          <kbd className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
            ⌘N
          </kbd>
        </Link>
      </div>
      <nav className="mt-6 flex-1 px-3">
        <div className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          Workspace
        </div>
        <ul className="space-y-0.5">
          {nav.map((item) => {
            const active = item.exact ? pathname === item.to : pathname.startsWith(item.to);
            const Icon = item.icon;
            return (
              <li key={item.to}>
                <Link
                  to={item.to as "/app"}
                  className={cn(
                    "group flex items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-[13px] transition-colors",
                    active
                      ? "bg-accent text-foreground"
                      : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
                  )}
                >
                  <Icon
                    className={cn("h-3.5 w-3.5", active ? "text-primary" : "text-muted-foreground")}
                  />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="border-t border-border p-3">
        <button className="flex w-full items-center gap-2.5 rounded-lg p-2 text-left transition-colors hover:bg-accent/60">
          <div className="flex h-8 w-8 items-center justify-center rounded-full border border-border bg-card">
            <User className="h-3.5 w-3.5 text-muted-foreground" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="truncate text-[12px] font-medium">Researcher</div>
            <div className="truncate text-[10px] text-muted-foreground">Free plan</div>
          </div>
        </button>
      </div>
    </aside>
  );
}
