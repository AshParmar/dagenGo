import { Link, useRouterState } from "@tanstack/react-router";
import { Sparkles, Clock, Network, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

type Item = { to: string; label: string; icon: typeof Sparkles; exact?: boolean };
const items: Item[] = [
  { to: "/app", label: "Research", icon: Sparkles, exact: true },
  { to: "/app/history", label: "History", icon: Clock },
  { to: "/app/graph", label: "Graph", icon: Network },
  { to: "/app/settings", label: "Settings", icon: Settings },
];

export function MobileNav() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 border-t border-border bg-sidebar/95 backdrop-blur md:hidden">
      <ul className="grid grid-cols-4">
        {items.map((it) => {
          const Icon = it.icon;
          const active = it.exact ? pathname === it.to : pathname.startsWith(it.to);
          return (
            <li key={it.to}>
              <Link
                to={it.to as "/app"}
                className={cn(
                  "flex flex-col items-center justify-center gap-1 py-2.5 text-[10px]",
                  active ? "text-primary" : "text-muted-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {it.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
