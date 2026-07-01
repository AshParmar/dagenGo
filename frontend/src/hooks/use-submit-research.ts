import { useMutation } from "@tanstack/react-query";

import { streamResearchQuery, submitResearchQuery } from "@/lib/api";
import { useResearchStore } from "@/store/research";

export function useSubmitResearch() {
  const start = useResearchStore((state) => state.start);
  const applyStage = useResearchStore((state) => state.applyStage);
  const appendAnswer = useResearchStore((state) => state.appendAnswer);
  const applyResult = useResearchStore((state) => state.applyResult);
  const fail = useResearchStore((state) => state.fail);
  const settings = useResearchStore((state) => state.settings);
  const streaming = settings.streaming;

  return useMutation({
    mutationFn: async (query: string) => {
      const controller = new AbortController();
      if (!streaming) {
        return submitResearchQuery(query, settings, controller.signal);
      }

      try {
        return await streamResearchQuery(
          query,
          (event) => {
            if (event.type === "stage") applyStage(event.stage);
            if (event.type === "answer") appendAnswer(event.answer);
            if (event.type === "result") applyResult({ ...event.result, query });
          },
          settings,
          controller.signal,
        );
      } catch (error) {
        if (error instanceof Error && error.name === "AbortError") throw error;
        return submitResearchQuery(query, settings, controller.signal);
      }
    },
    onMutate: (query: string) => {
      return { sessionId: start(query) };
    },
    onSuccess: (result, query, context) => {
      applyResult({ ...result, query }, context?.sessionId);
    },
    onError: (error) => {
      fail(error instanceof Error ? error.message : "Unable to complete the research request.");
    },
  });
}
