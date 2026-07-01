import type {
  Citation,
  PipelineStage,
  ResearchResponse,
  ResearchStreamEvent,
} from "@/lib/research-types";

const DEFAULT_TIMEOUT_MS = 180000;
const DEFAULT_RETRIES = 1;

function getApiBaseUrl() {
  return (import.meta.env.VITE_API_BASE_URL?.trim() || "/api").replace(/\/$/, "");
}

function createTimeoutSignal(signal?: AbortSignal, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeoutId = globalThis.setTimeout(
    () => controller.abort(new DOMException("Request timed out", "TimeoutError")),
    timeoutMs,
  );

  const onAbort = () => controller.abort(signal?.reason);
  if (signal) {
    if (signal.aborted) {
      controller.abort(signal.reason);
    } else {
      signal.addEventListener("abort", onAbort, { once: true });
    }
  }

  return {
    signal: controller.signal,
    cleanup: () => {
      globalThis.clearTimeout(timeoutId);
      signal?.removeEventListener("abort", onAbort);
    },
  };
}

function toNumber(value: unknown): number | undefined {
  if (typeof value !== "number" || Number.isNaN(value)) return undefined;
  return Math.max(0, Math.min(1, value));
}

function normalizeCitation(citation: Partial<Citation>, index: number): Citation {
  const url = citation.url;
  const domain = citation.domain ?? citation.website ?? citation.source;
  return {
    id: String(citation.id ?? url ?? `citation-${index}`),
    title: citation.title?.trim() || `Source ${index + 1}`,
    source: citation.source,
    website: citation.website ?? domain,
    domain,
    provider: citation.provider,
    publication_date: citation.publication_date,
    language: citation.language,
    confidence: toNumber(citation.confidence),
    snippet: citation.snippet,
    url,
    favicon_url: citation.favicon_url,
  };
}

export function normalizeResearchResponse(payload: ResearchResponse): ResearchResponse {
  const citations = Array.isArray(payload.citations)
    ? payload.citations
        .map((citation, index) => normalizeCitation(citation, index))
        .sort((a, b) => (b.confidence ?? 0) - (a.confidence ?? 0))
    : [];

  return {
    query: payload.query,
    answer: payload.answer ?? payload.final_answer ?? "",
    final_answer: payload.final_answer,
    citations,
    execution_steps: Array.isArray(payload.execution_steps) ? payload.execution_steps : [],
    timeline: Array.isArray(payload.timeline) ? payload.timeline : [],
    knowledge_graph: {
      nodes: payload.knowledge_graph?.nodes ?? [],
      edges: payload.knowledge_graph?.edges ?? [],
    },
    metrics: {
      confidence: toNumber(payload.metrics?.confidence),
      groundedness: toNumber(payload.metrics?.groundedness),
      hallucination: toNumber(payload.metrics?.hallucination),
    },
    metadata: payload.metadata ?? {},
  };
}

async function requestJson<T>(
  path: string,
  init: RequestInit,
  signal?: AbortSignal,
  retries = DEFAULT_RETRIES,
): Promise<T> {
  const { signal: timeoutSignal, cleanup } = createTimeoutSignal(signal);

  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...init,
      signal: timeoutSignal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...init.headers,
      },
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Request failed with status ${response.status}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    const aborted = timeoutSignal.aborted || signal?.aborted;
    if (!aborted && retries > 0) {
      return requestJson<T>(path, init, signal, retries - 1);
    }
    throw error;
  } finally {
    cleanup();
  }
}

export async function submitResearchQuery(
  query: string,
  settings?: any,
  signal?: AbortSignal,
): Promise<ResearchResponse> {
  const result = await requestJson<ResearchResponse>(
    "/query",
    {
      method: "POST",
      body: JSON.stringify({ query, settings }),
    },
    signal,
  );

  return normalizeResearchResponse(result);
}

function parseSseChunk(chunk: string): Array<{ event: string; data: unknown }> {
  return chunk
    .split(/\n\n/)
    .map((entry) => {
      const event = entry.match(/^event:\s*(.+)$/m)?.[1]?.trim() ?? "message";
      const dataLine = entry.match(/^data:\s*(.+)$/m)?.[1];
      if (!dataLine) return null;
      try {
        return { event, data: JSON.parse(dataLine) };
      } catch {
        return null;
      }
    })
    .filter((entry): entry is { event: string; data: unknown } => Boolean(entry));
}

function toStreamEvent(event: string, data: unknown): ResearchStreamEvent | null {
  if (!data || typeof data !== "object") return null;
  const payload = data as Record<string, unknown>;

  if (event === "start") return { type: "start", query: String(payload.query ?? "") };
  if (event === "stage" && payload.stage) {
    return { type: "stage", stage: payload.stage as PipelineStage };
  }
  if (event === "answer") return { type: "answer", answer: String(payload.answer ?? "") };
  if (event === "result") {
    return {
      type: "result",
      result: normalizeResearchResponse(payload as ResearchResponse),
    };
  }
  if (event === "error") return { type: "error", message: String(payload.message ?? "Stream failed") };
  return null;
}

export async function streamResearchQuery(
  query: string,
  onEvent: (event: ResearchStreamEvent) => void,
  settings?: any,
  signal?: AbortSignal,
): Promise<ResearchResponse> {
  const { signal: timeoutSignal, cleanup } = createTimeoutSignal(signal, DEFAULT_TIMEOUT_MS * 2);
  let buffer = "";
  let finalResult: ResearchResponse | null = null;

  try {
    const response = await fetch(`${getApiBaseUrl()}/query/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify({ query, settings }),
      signal: timeoutSignal,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Request failed with status ${response.status}`);
    }

    if (!response.body) {
      throw new Error("Streaming is not supported by this browser.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const entries = buffer.split(/\n\n/);
      buffer = entries.pop() ?? "";

      for (const raw of entries) {
        for (const parsed of parseSseChunk(`${raw}\n\n`)) {
          const streamEvent = toStreamEvent(parsed.event, parsed.data);
          if (!streamEvent) continue;
          if (streamEvent.type === "error") throw new Error(streamEvent.message);
          if (streamEvent.type === "result") finalResult = streamEvent.result;
          onEvent(streamEvent);
        }
      }
    }

    if (buffer.trim()) {
      for (const parsed of parseSseChunk(`${buffer}\n\n`)) {
        const streamEvent = toStreamEvent(parsed.event, parsed.data);
        if (!streamEvent) continue;
        if (streamEvent.type === "error") throw new Error(streamEvent.message);
        if (streamEvent.type === "result") finalResult = streamEvent.result;
        onEvent(streamEvent);
      }
    }

    if (!finalResult) {
      return submitResearchQuery(query, settings, signal);
    }

    return finalResult;
  } finally {
    cleanup();
  }
}
