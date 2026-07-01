import type { PipelineStage } from "@/lib/research-types";

export const PIPELINE_STAGE_DEFS: Omit<PipelineStage, "status" | "elapsedMs">[] = [
  { id: "lang",      label: "Language Detection" },
  { id: "plan",      label: "Planner" },
  { id: "rewrite",   label: "Query Rewrite" },
  { id: "retrieval", label: "Retrieval" },
  { id: "graph",     label: "Knowledge Graph" },
  { id: "reason",    label: "Reasoning" },
  { id: "verify",    label: "Verification" },
  { id: "reflect",   label: "Reflection" },
  { id: "eval",      label: "Evaluation" },
  { id: "judge",     label: "Judge" },
];

export const SUGGESTED_PROMPTS = [
  "Compare the climate policies of the EU and ASEAN since 2020",
  "What does recent research say about retrieval-augmented generation?",
  "Summarize the global stablecoin regulatory landscape",
  "How are nations approaching frontier AI safety in 2025?",
];
