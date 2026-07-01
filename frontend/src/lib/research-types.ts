export type PipelineStageStatus = "pending" | "running" | "completed" | "failed";

export interface PipelineStage {
  id: string;
  label: string;
  status: PipelineStageStatus;
  elapsedMs: number;
  detail?: { key: string; value: string }[];
}

export interface Citation {
  id: string;
  title: string;
  source?: string;
  website?: string;
  domain?: string;
  provider?: string;
  publication_date?: string;
  language?: string;
  confidence?: number;
  snippet?: string;
  url?: string;
  favicon_url?: string;
}

export interface TimelineEvent {
  id?: string;
  title: string;
  time?: string;
  detail?: string;
  status?: "pending" | "running" | "completed" | "failed";
}

export interface KnowledgeGraphNode {
  id: string;
  label: string;
  type?: "entity" | "concept" | "source" | string;
  x?: number;
  y?: number;
}

export interface KnowledgeGraphEdge {
  from: string;
  to: string;
  label?: string;
}

export interface KnowledgeGraphData {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

export interface ResearchMetrics {
  confidence?: number;
  groundedness?: number;
  hallucination?: number;
}

export interface ResearchMetadata {
  documents_retrieved?: number;
  chunks?: number;
  provider?: string;
  latency?: number;
}

export interface ResearchResponse {
  query?: string;
  answer?: string;
  final_answer?: string;
  citations?: Citation[];
  execution_steps?: PipelineStage[];
  timeline?: TimelineEvent[];
  knowledge_graph?: KnowledgeGraphData;
  metrics?: ResearchMetrics;
  metadata?: ResearchMetadata;
}

export type ResearchStreamEvent =
  | { type: "start"; query: string }
  | { type: "stage"; stage: PipelineStage }
  | { type: "answer"; answer: string }
  | { type: "result"; result: ResearchResponse }
  | { type: "error"; message: string };

export interface ResearchSettings {
  provider: "gemini" | "claude" | "gpt";
  model: string;
  temperature: number;
  topK: number;
  graphRag: boolean;
  hybridRetrieval: boolean;
  streaming: boolean;
}

export interface ResearchSession extends ResearchResponse {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  favorite: boolean;
  pinned: boolean;
}
