import { useMutation } from "@tanstack/react-query";

import { streamResearchQuery, submitResearchQuery } from "@/lib/api";
import { useResearchStore } from "@/store/research";

let activeController: AbortController | null = null;

export function useSubmitResearch() {
  const start = useResearchStore((state) => state.start);
  const resetForRetry = useResearchStore((state) => state.resetForRetry);
  const applyStage = useResearchStore((state) => state.applyStage);
  const appendAnswer = useResearchStore((state) => state.appendAnswer);
  const applyResult = useResearchStore((state) => state.applyResult);
  const fail = useResearchStore((state) => state.fail);
  const settings = useResearchStore((state) => state.settings);
  const streaming = settings.streaming;

  return useMutation({
    mutationFn: async (query: string) => {
      // Abort any currently running research stream
      if (activeController) {
        try {
          activeController.abort("New research query started");
        } catch (e) {
          // ignore abort errors
        }
      }

      const controller = new AbortController();
      activeController = controller;

      try {
        if (!streaming) {
          return await submitResearchQuery(query, settings, controller.signal);
        }

        return await streamResearchQuery(
          query,
          (event) => {
            if (event.type === "stage") {
              applyStage(event.stage);
              // Reset stages to pending on reflection loops
              if (event.stage.id === "reflect") {
                const nextAction = event.stage.detail?.find((d) => d.key === "Next Action")?.value;
                if (nextAction === "retrieve_again" || nextAction === "web_search" || nextAction === "graph_retrieve") {
                  resetForRetry();
                }
              }
            }
            if (event.type === "answer") appendAnswer(event.answer);
            if (event.type === "result") applyResult({ ...event.result, query });
          },
          settings,
          controller.signal,
        );
      } catch (error) {
        if (error instanceof Error && error.name === "AbortError") throw error;
        return await submitResearchQuery(query, settings, controller.signal);
      } finally {
        if (activeController === controller) {
          activeController = null;
        }
      }
    },
    onMutate: (query: string) => {
      return { sessionId: start(query) };
    },
    onSuccess: (result, query, context) => {
      applyResult({ ...result, query }, context?.sessionId);
    },
    onError: (error) => {
      const msg = error instanceof Error ? error.message : "";
      const isAbort = error instanceof Error && (error.name === "AbortError" || msg.includes("aborted") || msg.includes("abort"));
      if (isAbort) {
        return;
      }
      fail(msg || "Unable to complete the research request.");
    },
  });
}
