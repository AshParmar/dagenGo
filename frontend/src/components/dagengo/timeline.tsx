import { motion } from "motion/react";
import { Check, Database, Globe, Network, ShieldCheck, Sparkles } from "lucide-react";

import type { TimelineEvent } from "@/lib/research-types";

export function Timeline({ events }: { events?: TimelineEvent[] }) {
  if (!events?.length) {
    return (
      <div className="py-6 text-center text-[13px] text-muted-foreground">
        Timeline events will appear as the backend reports progress.
      </div>
    );
  }

  const timeline = events.map((event, index) => ({
    icon:
      index === events.length - 1
        ? Check
        : index === 0
          ? Sparkles
          : index === 1
            ? Globe
            : index === 2
              ? Network
              : index === 3
                ? Database
                : ShieldCheck,
    title: event.title,
    time: event.time,
    detail: event.detail ?? event.status,
  }));

  return (
    <ol className="relative ml-3 border-l border-border">
      {timeline.map((event, index) => {
        const Icon = event.icon;
        return (
          <motion.li
            key={`${event.title}-${index}`}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.08, duration: 0.3 }}
            className="relative mb-6 pl-6"
          >
            <span className="absolute -left-[13px] top-1 flex h-6 w-6 items-center justify-center rounded-full border border-primary/40 bg-card text-primary">
              <Icon className="h-3 w-3" />
            </span>
            <div className="flex items-baseline justify-between gap-3">
              <div className="text-[13px] font-medium">{event.title}</div>
              {event.time && (
                <div className="font-mono text-[11px] text-muted-foreground">{event.time}</div>
              )}
            </div>
            {event.detail && (
              <div className="mt-0.5 text-[12px] text-muted-foreground">{event.detail}</div>
            )}
          </motion.li>
        );
      })}
    </ol>
  );
}
