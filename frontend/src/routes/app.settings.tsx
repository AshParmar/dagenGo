import { createFileRoute } from "@tanstack/react-router";
import { Settings as SettingsIcon } from "lucide-react";

import { PageHeader } from "@/components/dagengo/page-header";
import { useResearchStore } from "@/store/research";

export const Route = createFileRoute("/app/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  const settings = useResearchStore((state) => state.settings);
  const updateSettings = useResearchStore((state) => state.updateSettings);

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-10">
      <PageHeader
        icon={SettingsIcon}
        title="Settings"
        subtitle="Tune the model, retrieval and behavior of your research agent. Language is detected automatically from your query."
      />

      <div className="mt-8 space-y-6">
        <Section title="LLM provider" hint="Powers reasoning, verification and judging.">
          <div className="grid grid-cols-3 gap-2">
            {(["gemini", "claude", "gpt"] as const).map((provider) => (
              <button
                key={provider}
                type="button"
                onClick={() => updateSettings({ provider })}
                className={`rounded-lg border px-3 py-2.5 text-[13px] font-medium capitalize transition-colors ${
                  settings.provider === provider
                    ? "border-primary/60 bg-primary/10 text-foreground"
                    : "border-border bg-card text-muted-foreground hover:text-foreground"
                }`}
              >
                {provider}
              </button>
            ))}
          </div>
        </Section>

        <Section title="Model" hint="Specific model under the selected provider.">
          <input
            value={settings.model}
            onChange={(event) => updateSettings({ model: event.target.value })}
            className="w-full rounded-lg border border-border bg-card px-3 py-2 text-[13px] focus:border-primary/50 focus:outline-none"
          />
        </Section>

        <Section
          title="Temperature"
          hint={`Lower is more deterministic - currently ${settings.temperature.toFixed(2)}.`}
        >
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={settings.temperature}
            onChange={(event) => updateSettings({ temperature: parseFloat(event.target.value) })}
            className="w-full accent-[var(--primary)]"
          />
        </Section>

        <Section
          title="Top K"
          hint={`Number of chunks retained after reranking - currently ${settings.topK}.`}
        >
          <input
            type="range"
            min={5}
            max={50}
            step={1}
            value={settings.topK}
            onChange={(event) => updateSettings({ topK: parseInt(event.target.value, 10) })}
            className="w-full accent-[var(--primary)]"
          />
        </Section>

        <Section title="Retrieval">
          <div className="space-y-2">
            <Toggle
              label="GraphRAG"
              desc="Augment retrieval with the knowledge graph."
              value={settings.graphRag}
              onChange={(graphRag) => updateSettings({ graphRag })}
            />
            <Toggle
              label="Hybrid Retrieval"
              desc="Combine dense and sparse retrieval with reciprocal rank fusion."
              value={settings.hybridRetrieval}
              onChange={(hybridRetrieval) => updateSettings({ hybridRetrieval })}
            />
            <Toggle
              label="Streaming"
              desc="Render backend events and answer updates as they arrive."
              value={settings.streaming}
              onChange={(streaming) => updateSettings({ streaming })}
            />
          </div>
        </Section>
      </div>
    </div>
  );
}

function Section({
  title,
  hint,
  children,
}: {
  title: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-card/40 p-5 backdrop-blur">
      <div className="flex items-baseline justify-between gap-4">
        <div>
          <div className="text-[13px] font-semibold">{title}</div>
          {hint && <div className="mt-0.5 text-[11px] text-muted-foreground">{hint}</div>}
        </div>
      </div>
      <div className="mt-4">{children}</div>
    </div>
  );
}

function Select({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="w-full rounded-lg border border-border bg-card px-3 py-2 text-[13px] focus:border-primary/50 focus:outline-none"
    >
      {options.map((option) => (
        <option key={option} value={option} className="bg-card">
          {option}
        </option>
      ))}
    </select>
  );
}

function Toggle({
  label,
  desc,
  value,
  onChange,
}: {
  label: string;
  desc: string;
  value: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!value)}
      className="flex w-full items-center justify-between gap-4 rounded-lg border border-border bg-surface/60 px-3 py-2.5 text-left transition-colors hover:border-primary/30"
    >
      <div>
        <div className="text-[13px] font-medium">{label}</div>
        <div className="text-[11px] text-muted-foreground">{desc}</div>
      </div>
      <span
        className={`relative h-5 w-9 rounded-full transition-colors ${value ? "bg-primary" : "bg-border"}`}
      >
        <span
          className={`absolute top-0.5 h-4 w-4 rounded-full bg-background transition-transform ${
            value ? "translate-x-[18px]" : "translate-x-0.5"
          }`}
        />
      </span>
    </button>
  );
}
