import { createFileRoute } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import { motion } from "motion/react";
import { ArrowRight, Globe, Network, ShieldCheck, Sparkles } from "lucide-react";
import { AnimatedBackground } from "@/components/dagengo/animated-background";
import { Wordmark } from "@/components/dagengo/logo";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "DagenGo — Cross-Lingual Research & Fact Verification Agent" },
      {
        name: "description",
        content:
          "Research across multiple languages. Retrieve trusted evidence. Build knowledge graphs. Verify every answer before it reaches you.",
      },
      { property: "og:title", content: "DagenGo — Cross-Lingual Research Agent" },
      {
        property: "og:description",
        content:
          "An AI research agent that reasons across languages and verifies every claim with cited evidence.",
      },
    ],
  }),
  component: Landing,
});

function Landing() {
  return (
    <div className="relative min-h-screen text-foreground">
      <AnimatedBackground />

      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <Wordmark />
        <nav className="hidden items-center gap-7 text-[13px] text-muted-foreground md:flex">
          <a href="#features" className="transition-colors hover:text-foreground">
            Features
          </a>
          <a href="#pipeline" className="transition-colors hover:text-foreground">
            Pipeline
          </a>
          <a href="#languages" className="transition-colors hover:text-foreground">
            Languages
          </a>
        </nav>
        <div className="flex items-center gap-2">
          <Link
            to="/app"
            className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-primary px-3 text-[12px] font-medium text-primary-foreground transition-colors hover:bg-[var(--accent-hover)]"
          >
            Start Research <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </header>

      <main className="relative z-10">
        {/* Hero */}
        <section className="mx-auto max-w-7xl px-6 pt-16 pb-24 md:pt-24 md:pb-32">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="mx-auto max-w-3xl text-center"
          >
            <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 text-[11px] text-muted-foreground backdrop-blur">
              <span className="h-1.5 w-1.5 rounded-full bg-primary pulse-ring" />
              Cross-lingual research, verified at every step
            </div>

            <h1 className="text-balance text-5xl font-semibold tracking-tight text-foreground sm:text-6xl md:text-7xl">
              DagenGo
            </h1>
            <p className="mt-5 text-balance text-xl font-medium tracking-tight text-foreground/90 sm:text-2xl">
              Cross-Lingual Research &amp; Fact Verification Agent
            </p>
            <p className="mx-auto mt-6 max-w-xl text-balance text-[15px] leading-relaxed text-muted-foreground">
              Research across multiple languages. Retrieve trusted evidence. Build knowledge graphs.
              Verify every answer before it reaches you.
            </p>

            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                to="/app"
                className="group inline-flex h-11 items-center gap-2 rounded-xl bg-primary px-5 text-sm font-medium text-primary-foreground transition-all hover:bg-[var(--accent-hover)] hover:shadow-[0_10px_40px_-10px_rgba(143,188,139,0.5)]"
              >
                Start Research
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
              <a
                href="#features"
                className="inline-flex h-11 items-center gap-2 rounded-xl px-5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                Learn more
              </a>
            </div>
          </motion.div>

          {/* Hero preview card */}
          <motion.div
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25, duration: 0.7, ease: "easeOut" }}
            className="relative mx-auto mt-20 max-w-5xl"
          >
            <div className="absolute inset-x-10 -top-12 h-24 rounded-full bg-primary/20 blur-3xl" />
            <div className="glass relative overflow-hidden rounded-2xl">
              <div className="flex items-center gap-2 border-b border-border px-4 py-3">
                <span className="h-2.5 w-2.5 rounded-full bg-muted" />
                <span className="h-2.5 w-2.5 rounded-full bg-muted" />
                <span className="h-2.5 w-2.5 rounded-full bg-muted" />
                <span className="ml-3 font-mono text-[11px] text-muted-foreground">
                  dagengo.app — research session
                </span>
              </div>
              <div className="grid grid-cols-1 gap-0 md:grid-cols-[1fr_280px]">
                <div className="p-6 md:p-8">
                  <div className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    Query
                  </div>
                  <div className="mt-1 text-[15px] font-medium text-foreground">
                    Compare climate policy of the EU and ASEAN since 2020.
                  </div>
                  <div className="mt-6 space-y-2.5">
                    {[
                      "Language Detection",
                      "Planner",
                      "Cross-Lingual Expansion",
                      "Knowledge Graph",
                      "Verification",
                    ].map((s, i) => (
                      <motion.div
                        key={s}
                        initial={{ opacity: 0, x: -6 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.6 + i * 0.1 }}
                        className="flex items-center gap-3 text-[13px]"
                      >
                        <span className="flex h-5 w-5 items-center justify-center rounded-full border border-primary/40 bg-primary/15 text-primary">
                          <svg viewBox="0 0 20 20" className="h-2.5 w-2.5">
                            <path
                              d="M5 10l3 3 7-7"
                              stroke="currentColor"
                              strokeWidth="3"
                              fill="none"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        </span>
                        <span className="text-foreground">{s}</span>
                        <span className="ml-auto font-mono text-[10px] text-muted-foreground">
                          {(0.18 + i * 0.32).toFixed(2)}s
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </div>
                <div className="border-t border-border bg-surface/50 p-6 md:border-l md:border-t-0">
                  <div className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    Evidence
                  </div>
                  <div className="mt-3 space-y-2">
                    {[
                      { lang: "EN", src: "eur-lex.europa.eu", conf: 96 },
                      { lang: "FR", src: "lemonde.fr", conf: 88 },
                      { lang: "JA", src: "asia.nikkei.com", conf: 84 },
                      { lang: "DE", src: "dw.com", conf: 81 },
                    ].map((c) => (
                      <div key={c.src} className="rounded-lg border border-border bg-card/80 p-2.5">
                        <div className="flex items-center justify-between text-[10px]">
                          <span className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono">
                            {c.lang}
                          </span>
                          <span className="font-mono text-primary">{c.conf}%</span>
                        </div>
                        <div className="mt-1.5 truncate text-[11px] text-muted-foreground">
                          {c.src}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </section>

        {/* Features */}
        <section id="features" className="mx-auto max-w-7xl px-6 pb-24">
          <div className="mx-auto max-w-2xl text-center">
            <div className="text-[11px] font-medium uppercase tracking-wider text-primary">
              Why DagenGo
            </div>
            <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
              An agent that earns your trust.
            </h2>
            <p className="mt-4 text-[15px] text-muted-foreground">
              Every answer is grounded in cited evidence — across languages, and across reasoning
              steps you can audit.
            </p>
          </div>

          <div className="mt-14 grid grid-cols-1 gap-4 md:grid-cols-3">
            {[
              {
                icon: Globe,
                title: "Cross-lingual retrieval",
                body: "Expand queries across languages and rank evidence with cross-encoders.",
              },
              {
                icon: Network,
                title: "Knowledge graphs",
                body: "Extract entities and relations into a navigable graph for multi-hop reasoning.",
              },
              {
                icon: ShieldCheck,
                title: "Verified by default",
                body: "Hallucination detection, groundedness scoring and an LLM judge — on every answer.",
              },
              {
                icon: Sparkles,
                title: "Hybrid retrieval",
                body: "Dense + sparse fused with RRF, then reranked for precision over recall.",
              },
              {
                icon: Sparkles,
                title: "Transparent reasoning",
                body: "Inspect every stage of the pipeline with timing and decision traces.",
              },
              {
                icon: Sparkles,
                title: "Privacy-aware",
                body: "Runs on your keys. Your queries never train anyone else's model.",
              },
            ].map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ delay: i * 0.05 }}
                className="group rounded-2xl border border-border bg-card/60 p-6 backdrop-blur transition-colors hover:border-primary/40"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-surface text-primary">
                  <f.icon className="h-4 w-4" />
                </div>
                <div className="mt-4 text-[15px] font-semibold tracking-tight">{f.title}</div>
                <p className="mt-1.5 text-[13px] leading-relaxed text-muted-foreground">{f.body}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Languages strip */}
        <section id="languages" className="border-t border-border/60 bg-surface/40">
          <div className="mx-auto flex max-w-7xl flex-col items-center gap-6 px-6 py-12">
            <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
              Speaks the world's research
            </div>
            <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-[13px] text-muted-foreground">
              {[
                "English",
                "Français",
                "Deutsch",
                "日本語",
                "中文",
                "Español",
                "العربية",
                "Português",
                "한국어",
                "हिन्दी",
              ].map((l) => (
                <span key={l} className="transition-colors hover:text-foreground">
                  {l}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="mx-auto max-w-4xl px-6 py-24 text-center">
          <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
            Run your first verified research.
          </h2>
          <p className="mt-4 text-[15px] text-muted-foreground">
            Free during preview. No credit card.
          </p>
          <Link
            to="/app"
            className="mt-8 inline-flex h-11 items-center gap-2 rounded-xl bg-primary px-5 text-sm font-medium text-primary-foreground transition-all hover:bg-[var(--accent-hover)] hover:shadow-[0_10px_40px_-10px_rgba(143,188,139,0.5)]"
          >
            Start Research <ArrowRight className="h-4 w-4" />
          </Link>
        </section>
      </main>

      <footer className="border-t border-border/60">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-6 py-6 text-[12px] text-muted-foreground md:flex-row">
          <div className="flex items-center gap-2">
            <Wordmark />{" "}
          </div>
          <div>© {new Date().getFullYear()} DagenGo. Researching across languages.</div>
        </div>
      </footer>
    </div>
  );
}
