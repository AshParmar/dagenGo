import { createFileRoute, Outlet, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { toast } from "sonner";

import { AppSidebar } from "@/components/dagengo/app-sidebar";
import { MobileNav } from "@/components/dagengo/mobile-nav";
import { AnimatedBackground } from "@/components/dagengo/animated-background";

export const Route = createFileRoute("/app")({
  head: () => ({
    meta: [
      { title: "DagenGo — Research" },
      {
        name: "description",
        content: "Run cross-lingual research with a verified, auditable AI pipeline.",
      },
    ],
  }),
  component: AppLayout,
});

function AppLayout() {
  const navigate = useNavigate();

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const command = event.metaKey || event.ctrlKey;
      if (!command) return;
      if (event.key.toLowerCase() === "k") {
        event.preventDefault();
        navigate({ to: "/app/history" });
      }
      if (event.key.toLowerCase() === "n") {
        event.preventDefault();
        navigate({ to: "/app" });
      }
    };

    const offline = () => toast.error("You are offline. Research requests may fail.");
    const online = () => toast.success("Connection restored");

    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("offline", offline);
    window.addEventListener("online", online);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("offline", offline);
      window.removeEventListener("online", online);
    };
  }, [navigate]);

  return (
    <div className="relative flex min-h-screen w-full text-foreground">
      <AnimatedBackground />
      <AppSidebar />
      <div className="flex min-w-0 flex-1 flex-col pb-16 md:pb-0">
        <Outlet />
      </div>
      <MobileNav />
    </div>
  );
}
