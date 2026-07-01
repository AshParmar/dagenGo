import { motion } from "motion/react";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  size?: number;
  animated?: boolean;
}

export function Logo({ className, size = 28, animated = false }: LogoProps) {
  const ring = (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="dg-grad" x1="0" y1="0" x2="32" y2="32">
          <stop offset="0%" stopColor="var(--primary)" />
          <stop offset="100%" stopColor="var(--accent-hover)" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="13" stroke="url(#dg-grad)" strokeWidth="1.5" opacity="0.6" />
      <circle cx="16" cy="16" r="8" stroke="url(#dg-grad)" strokeWidth="1.5" />
      <circle cx="16" cy="16" r="2.4" fill="url(#dg-grad)" />
      <circle cx="29" cy="16" r="1.4" fill="var(--primary)" />
      <circle cx="3" cy="16" r="1.4" fill="var(--primary)" opacity="0.5" />
      <circle cx="16" cy="3" r="1.4" fill="var(--primary)" opacity="0.7" />
    </svg>
  );

  return (
    <div className={cn("inline-flex items-center justify-center", className)}>
      {animated ? (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 16, repeat: Infinity, ease: "linear" }}
        >
          {ring}
        </motion.div>
      ) : (
        ring
      )}
    </div>
  );
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <Logo />
      <span className="text-[15px] font-semibold tracking-tight">DagenGo</span>
    </div>
  );
}
