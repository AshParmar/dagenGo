import { create } from "zustand";
import { persist } from "zustand/middleware";

import { PIPELINE_STAGE_DEFS } from "@/lib/research-content";
import type {
  Citation,
  KnowledgeGraphData,
  PipelineStage,
  ResearchMetadata,
  ResearchMetrics,
  ResearchResponse,
  ResearchSession,
  ResearchSettings,
  TimelineEvent,
} from "@/lib/research-types";

const DEFAULT_SETTINGS: ResearchSettings = {
  provider: "gemini",
  model: "gemini-1.5-pro",
  temperature: 0.3,
  topK: 20,
  graphRag: true,
  hybridRetrieval: true,
  streaming: true,
};

interface ResearchState {
  query: string;
  setQuery: (q: string) => void;
  stages: PipelineStage[];
  isRunning: boolean;
  answer: string;
  citations: Citation[];
  timeline: TimelineEvent[];
  knowledgeGraph: KnowledgeGraphData | null;
  metrics: ResearchMetrics;
  metadata: ResearchMetadata;
  error: string | null;
  startedAt: number | null;
  activeSessionId: string | null;
  sessions: ResearchSession[];
  settings: ResearchSettings;
  reset: () => void;
  resetForRetry: () => void;
  start: (query: string) => string;
  applyStage: (stage: PipelineStage) => void;
  appendAnswer: (answer: string) => void;
  applyResult: (result: ResearchResponse, sessionId?: string) => void;
  fail: (message: string) => void;
  setActiveSession: (id: string) => void;
  deleteSession: (id: string) => void;
  renameSession: (id: string, title: string) => void;
  toggleFavorite: (id: string) => void;
  togglePinned: (id: string) => void;
  updateSettings: (settings: Partial<ResearchSettings>) => void;
}

const initialStages = (): PipelineStage[] =>
  PIPELINE_STAGE_DEFS.map((stage) => ({ ...stage, status: "pending", elapsedMs: 0 }));

const sessionId = () =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `research-${Date.now()}-${Math.random().toString(36).slice(2)}`;

function titleFromQuery(query: string) {
  const trimmed = query.trim();
  if (!trimmed) return "Untitled research";
  return trimmed.length > 72 ? `${trimmed.slice(0, 69)}...` : trimmed;
}

function timelineFromSteps(steps: PipelineStage[]): TimelineEvent[] {
  return steps.map((step) => ({
    id: step.id,
    title: step.label,
    time: step.elapsedMs ? `${(step.elapsedMs / 1000).toFixed(2)}s` : undefined,
    detail: step.detail?.map((item) => `${item.key}: ${item.value}`).join(" | ") ?? step.status,
    status: step.status,
  }));
}

function mergeStage(existing: PipelineStage[], incoming: PipelineStage) {
  const index = existing.findIndex(
    (stage) => stage.id === incoming.id || stage.label === incoming.label,
  );

  if (index >= 0) {
    return existing.map((stage, currentIndex) =>
      currentIndex === index ? { ...stage, ...incoming } : stage,
    );
  }

  return [...existing, incoming];
}

function sessionFromResult(
  result: ResearchResponse,
  previous: ResearchSession | undefined,
  id: string,
  fallbackQuery: string,
): ResearchSession {
  const now = Date.now();
  const query = result.query || fallbackQuery;
  return {
    ...previous,
    ...result,
    id,
    query,
    title: previous?.title || titleFromQuery(query),
    createdAt: previous?.createdAt ?? now,
    updatedAt: now,
    favorite: previous?.favorite ?? false,
    pinned: previous?.pinned ?? false,
  };
}

function sortedSessions(sessions: ResearchSession[]) {
  return [...sessions].sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
    return b.updatedAt - a.updatedAt;
  });
}

export const useResearchStore = create<ResearchState>()(
  persist(
    (set, get) => ({
      query: "",
      setQuery: (q) => set({ query: q }),
      stages: initialStages(),
      isRunning: false,
      answer: "",
      citations: [],
      timeline: [],
      knowledgeGraph: null,
      metrics: {},
      metadata: {},
      error: null,
      startedAt: null,
      activeSessionId: null,
      sessions: [],
      settings: DEFAULT_SETTINGS,

      reset: () => {
        set({
          stages: initialStages(),
          answer: "",
          citations: [],
          timeline: [],
          knowledgeGraph: null,
          metrics: {},
          metadata: {},
          error: null,
          isRunning: false,
          startedAt: null,
        });
      },

      start: (query) => {
        const id = sessionId();
        set({
          query,
          stages: initialStages().map((stage, index) =>
            index === 0 ? { ...stage, status: "running" } : stage,
          ),
          answer: "",
          citations: [],
          timeline: [{ title: "Research Started", status: "running" }],
          knowledgeGraph: null,
          metrics: {},
          metadata: {},
          error: null,
          isRunning: true,
          startedAt: Date.now(),
          activeSessionId: id,
        });
        return id;
      },

      resetForRetry: () => {
        set((state) => ({
          stages: state.stages.map((stage) => {
            if (stage.id === "lang" || stage.id === "plan") {
              return stage;
            }
            return {
              ...stage,
              status: "pending" as const,
              elapsedMs: 0,
              detail: [],
            };
          }),
        }));
      },

      applyStage: (stage) => {
        set((state) => {
          const stages = mergeStage(state.stages, {
            ...stage,
            status: stage.status || "completed",
            elapsedMs: stage.elapsedMs ?? 0,
          });
          return {
            stages,
            timeline: timelineFromSteps(stages.filter((item) => item.status !== "pending")),
          };
        });
      },

      appendAnswer: (answer) => {
        set((state) => ({
          answer,
          timeline:
            state.timeline.length > 0
              ? state.timeline
              : [{ title: "Reasoning", status: "running", detail: "Answer is streaming" }],
        }));
      },

      applyResult: (result, sessionIdOverride) => {
        const state = get();
        const id = sessionIdOverride ?? state.activeSessionId ?? sessionId();
        let normalizedStages = [...state.stages];
        if (result.execution_steps && result.execution_steps.length > 0) {
          normalizedStages = initialStages();
          for (const stage of result.execution_steps) {
            normalizedStages = mergeStage(normalizedStages, {
              ...stage,
              status: stage.status === "failed" ? "failed" : "completed",
              elapsedMs: stage.elapsedMs ?? 0,
            });
          }
        } else {
          normalizedStages = state.stages.map((stage) =>
            stage.status === "pending" || stage.status === "running"
              ? { ...stage, status: "completed" as const }
              : stage,
          );
        }

        const nextResult: ResearchResponse = {
          ...result,
          answer: result.answer ?? result.final_answer ?? state.answer,
          citations: result.citations ?? [],
          timeline: result.timeline?.length ? result.timeline : timelineFromSteps(normalizedStages),
          knowledge_graph: result.knowledge_graph ?? { nodes: [], edges: [] },
          metrics: result.metrics ?? {},
          metadata: result.metadata ?? {},
        };

        const previous = state.sessions.find((session) => session.id === id);
        const nextSession = sessionFromResult(nextResult, previous, id, state.query);
        const sessions = sortedSessions([
          nextSession,
          ...state.sessions.filter((session) => session.id !== id),
        ]);

        set({
          activeSessionId: id,
          query: nextSession.query ?? state.query,
          answer: nextResult.answer ?? "",
          citations: nextResult.citations ?? [],
          timeline: nextResult.timeline ?? [],
          knowledgeGraph: nextResult.knowledge_graph ?? null,
          metrics: nextResult.metrics ?? {},
          metadata: nextResult.metadata ?? {},
          stages: normalizedStages,
          isRunning: false,
          error: null,
          sessions,
        });
      },

      fail: (message) => {
        set((state) => ({
          isRunning: false,
          error: message,
          stages: state.stages.map((stage) =>
            stage.status === "running" ? { ...stage, status: "failed" } : stage,
          ),
        }));
      },

      setActiveSession: (id) => {
        const session = get().sessions.find((item) => item.id === id);
        if (!session) return;
        set({
          activeSessionId: id,
          query: session.query ?? "",
          answer: session.answer ?? session.final_answer ?? "",
          citations: session.citations ?? [],
          timeline: session.timeline ?? [],
          knowledgeGraph: session.knowledge_graph ?? null,
          metrics: session.metrics ?? {},
          metadata: session.metadata ?? {},
          stages: session.execution_steps?.length ? session.execution_steps : initialStages(),
          error: null,
          isRunning: false,
          startedAt: null,
        });
      },

      deleteSession: (id) => {
        set((state) => ({
          sessions: state.sessions.filter((session) => session.id !== id),
          activeSessionId: state.activeSessionId === id ? null : state.activeSessionId,
        }));
      },

      renameSession: (id, title) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === id ? { ...session, title: titleFromQuery(title) } : session,
          ),
        }));
      },

      toggleFavorite: (id) => {
        set((state) => ({
          sessions: sortedSessions(
            state.sessions.map((session) =>
              session.id === id ? { ...session, favorite: !session.favorite } : session,
            ),
          ),
        }));
      },

      togglePinned: (id) => {
        set((state) => ({
          sessions: sortedSessions(
            state.sessions.map((session) =>
              session.id === id ? { ...session, pinned: !session.pinned } : session,
            ),
          ),
        }));
      },

      updateSettings: (settings) => {
        set((state) => ({ settings: { ...state.settings, ...settings } }));
      },
    }),
    {
      name: "dagengo-research",
      partialize: (state) => ({
        sessions: state.sessions,
        settings: state.settings,
      }),
    },
  ),
);
