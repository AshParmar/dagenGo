from time import perf_counter

from langgraph.graph import END, START, StateGraph

from agents.judge_agent import JudgeAgent
from agents.planner_agent import PlannerAgent
from agents.reasoning_agent import ReasoningAgent
from agents.reflection_agent import ReflectionAgent
from agents.rewrite_agent import RewriteAgent
from agents.verifier_agent import VerifierAgent
from evaluation.confidence import ConfidenceScorer
from evaluation.groundedness import GroundednessEvaluator
from evaluation.hallucination import HallucinationDetector
from graph.router import Router
from graph.state import DagenGoState
from knowledge_graph.entity_extractor import EntityExtractor
from knowledge_graph.graph_builder import GraphBuilder
from knowledge_graph.graph_retriever import GraphRetriever
from knowledge_graph.relation_extractor import RelationExtractor
from retrieval.chunker import Chunker
from retrieval.hybrid import HybridRetriever
from retrieval.multi_query import MultiQueryRetriever
from retrieval.web_search import WebSearch
from utils.language_detector import detect_language


class DagenGoGraph:
    """Constructs the frozen DagenGo LangGraph workflow."""

    def __init__(self) -> None:
        self.builder = StateGraph(DagenGoState)

        self.planner = PlannerAgent()
        self.rewrite = RewriteAgent()
        self.reasoning = ReasoningAgent()
        self.verifier = VerifierAgent()
        self.reflection = ReflectionAgent()
        self.judge = JudgeAgent()

        self.search = WebSearch()
        self.chunker = Chunker()
        self.multi_query = MultiQueryRetriever()
        self.hybrid = HybridRetriever()

        self.entity = EntityExtractor()
        self.relation = RelationExtractor()
        self.graph = GraphBuilder()
        self.graph_retriever = GraphRetriever()

        self.hallucination = HallucinationDetector()
        self.confidence = ConfidenceScorer()
        self.groundedness = GroundednessEvaluator()

    def _append_stage(
        self,
        state: DagenGoState,
        *,
        stage_id: str,
        label: str,
        status: str,
        elapsed_ms: int,
        detail: list[dict] | None = None,
        timeline_title: str | None = None,
        timeline_detail: str | None = None,
    ) -> DagenGoState:
        execution_steps = list(state.get("execution_steps", []))
        execution_steps.append(
            {
                "id": stage_id,
                "label": label,
                "status": status,
                "elapsedMs": elapsed_ms,
                "detail": detail or [],
            }
        )
        state["execution_steps"] = execution_steps

        timeline = list(state.get("timeline", []))
        timeline.append(
            {
                "title": timeline_title or label,
                "time": f"{elapsed_ms / 1000:.2f}s",
                "detail": timeline_detail or label,
                "status": status,
            }
        )
        state["timeline"] = timeline
        return state

    def _wrap_stage(self, stage_id: str, label: str, node, detail_builder=None, timeline_title: str | None = None):
        def wrapped(state: DagenGoState) -> DagenGoState:
            start = perf_counter()
            try:
                next_state = node(state)
            except Exception:
                elapsed_ms = int((perf_counter() - start) * 1000)
                self._append_stage(
                    state,
                    stage_id=stage_id,
                    label=label,
                    status="failed",
                    elapsed_ms=elapsed_ms,
                    detail=detail_builder(state) if detail_builder else [],
                    timeline_title=timeline_title,
                    timeline_detail=f"{label} failed",
                )
                raise

            elapsed_ms = int((perf_counter() - start) * 1000)
            self._append_stage(
                next_state,
                stage_id=stage_id,
                label=label,
                status="completed",
                elapsed_ms=elapsed_ms,
                detail=detail_builder(next_state) if detail_builder else [],
                timeline_title=timeline_title,
                timeline_detail=f"{label} completed",
            )
            return next_state

        return wrapped

    @staticmethod
    def _entity_count(items: list[dict] | None) -> int:
        return len(items or [])

    def _build_knowledge_graph_response(self, state: DagenGoState) -> dict:
        nodes = []
        for index, entity in enumerate(state.get("entities", [])):
            nodes.append(
                {
                    "id": entity.get("name", f"entity-{index}"),
                    "label": entity.get("name", f"Entity {index + 1}"),
                    "type": entity.get("type", "entity"),
                }
            )

        for index, document in enumerate(state.get("graph_results", [])):
            node_id = document.get("id") or document.get("e", {}).get("name") or f"source-{index}"
            nodes.append(
                {
                    "id": node_id,
                    "label": document.get("title") or document.get("e", {}).get("name") or f"Source {index + 1}",
                    "type": "source",
                }
            )

        if not nodes and state.get("query"):
            nodes.append(
                {
                    "id": "query",
                    "label": state["query"],
                    "type": "concept",
                }
            )

        edges = []
        relations = state.get("relations", [])
        for index, relation in enumerate(relations):
            edges.append(
                {
                    "from": relation.get("source", f"entity-{index}"),
                    "to": relation.get("target", f"entity-{index + 1}"),
                    "label": relation.get("relation"),
                }
            )

        if not edges and len(nodes) > 1:
            for index in range(len(nodes) - 1):
                edges.append(
                    {
                        "from": nodes[index]["id"],
                        "to": nodes[index + 1]["id"],
                    }
                )

        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def _execution_details_from_state(state: DagenGoState) -> dict:
        return {
            "detected_language": state.get("language"),
            "planner": {
                "query_type": state.get("query_type"),
                "retrieval_strategy": state.get("retrieval_strategy"),
                "web_search": state.get("web_search"),
                "graph_retrieval": state.get("graph_retrieval"),
            },
            "retrieval": {
                "queries": len(state.get("multi_queries", [])),
                "documents_retrieved": len(state.get("retrieved_documents", [])),
                "chunks": len(state.get("chunks", [])),
                "dense_results": len(state.get("dense_results", [])),
                "sparse_results": len(state.get("sparse_results", [])),
                "merged_results": len(state.get("merged_results", [])),
                "reranked_results": len(state.get("reranked_results", [])),
            },
            "graph": {
                "entities": len(state.get("entities", [])),
                "relations": len(state.get("relations", [])),
                "graph_results": len(state.get("graph_results", [])),
            },
            "evaluation": {
                "confidence": state.get("confidence", {}).get("confidence_score"),
                "groundedness": state.get("groundedness", {}).get("groundedness_score"),
                "hallucination": state.get("hallucination", {}).get("hallucination_score"),
            },
        }

    def language_node(self, state: DagenGoState) -> DagenGoState:
        """Detect query language and convert to a human-readable name."""
        code = detect_language(state["query"])
        lang_map = {
            "en": "English",
            "fr": "French",
            "de": "German",
            "ja": "Japanese",
            "zh": "Chinese",
            "es": "Spanish",
            "hi": "Hindi",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ko": "Korean",
        }
        state["language"] = lang_map.get(str(code).lower().split("-")[0], "English")
        return state

    def retrieval_wrapper(self, state: DagenGoState) -> DagenGoState:
        """Run multi-query, web retrieval, chunking, and hybrid retrieval."""
        state = self.multi_query.generate(state)

        documents = self.search.search(state.get("rewritten_query", state["query"]))
        state["retrieved_documents"] = documents

        state["chunks"] = self.chunker.chunk_documents(documents)

        state = self.hybrid.retrieve(state)
        return state

    def _knowledge_source_text(self, state: DagenGoState) -> str:
        chunks = state.get("reranked_results") or state.get("merged_results") or state.get("chunks", [])
        # Strict safety limit: max 5 chunks
        chunks = chunks[:5]
        if chunks:
            text = "\n\n".join(chunk.get("text", "") for chunk in chunks if chunk.get("text"))
            # Strict safety limit: max 12,000 characters (~3,000 tokens)
            return text[:12000]

        documents = state.get("retrieved_documents", [])
        # Strict safety limit: max 3 documents
        documents = documents[:3]
        text = "\n\n".join(document.get("text", "") for document in documents if document.get("text"))
        return text[:12000]

    def knowledge_graph_wrapper(self, state: DagenGoState) -> DagenGoState:
        """Extract entities/relations from retrieved evidence, then retrieve graph context."""
        run_settings = state.get("settings") or {}
        if not run_settings.get("graphRag", True):
            state["entities"] = []
            state["relations"] = []
            state["graph_results"] = []
            return state

        source_text = self._knowledge_source_text(state)

        if not source_text.strip():
            state["entities"] = []
            state["relations"] = []
            state["graph_results"] = []
            return state

        entities = self.entity.extract(source_text)
        relations = self.relation.extract(source_text, entities)

        self.graph.build(entities, relations)

        state["entities"] = entities
        state["relations"] = relations

        state = self.graph_retriever.retrieve(state)
        return state

    def _translate_to_english(self, text: str) -> str:
        """Translate text to English using the LLM for evaluation purposes."""
        if not text.strip():
            return text
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from llm.models import gemini_llm
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a precise translator. Translate the following text to English. Return ONLY the English translation, without any conversational preamble or markdown code blocks."),
                ("human", "{text}")
            ])
            chain = prompt | gemini_llm | StrOutputParser()
            translation = chain.invoke({"text": text}).strip()
            
            # Programmatically clean conversational preambles from translation
            prefixes_to_strip = [
                "here is the translation:",
                "here is the english translation:",
                "sure, here is the translation:",
                "translation:",
                "the translation is:"
            ]
            translation_lower = translation.lower()
            for prefix in prefixes_to_strip:
                if translation_lower.startswith(prefix):
                    translation = translation[len(prefix):].strip()
                    break
                    
            return translation.strip('`"\'* \n\t')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to translate answer to English: {e}")
            return text

    def evaluation_wrapper(self, state: DagenGoState) -> DagenGoState:
        """Run hallucination, confidence, and groundedness evaluators."""
        evidence = state.get("reranked_results", [])

        # Translate answer to English if query language is not English
        # to ensure accurate heuristic metrics (word-overlap)
        original_answer = state.get("answer", "")
        language = state.get("language", "English")
        
        eval_answer = original_answer
        if language != "English" and original_answer.strip():
            eval_answer = self._translate_to_english(original_answer)

        hallucination = self.hallucination.evaluate(
            query=state["query"],
            answer=eval_answer,
            evidence=evidence,
        )
        state["hallucination"] = hallucination

        state["confidence"] = self.confidence.evaluate(
            query=state["query"],
            answer=eval_answer,
            evidence=evidence,
            verification=state.get("verification", {}),
            hallucination=hallucination,
        )

        state["groundedness"] = self.groundedness.evaluate(
            query=state["query"],
            answer=eval_answer,
            evidence=evidence,
        )

        return state

    def build(self):
        """Register nodes and compile the frozen graph shape."""
        builder = self.builder

        builder.add_node(
            "language",
            self._wrap_stage(
                "lang",
                "Language Detection",
                self.language_node,
                lambda state: [{"key": "Detected", "value": str(state.get("language", "unknown"))}],
                "Research Started",
            ),
        )
        builder.add_node(
            "planner",
            self._wrap_stage(
                "plan",
                "Planner",
                self.planner.invoke,
                lambda state: [
                    {"key": "Decision", "value": str(state.get("retrieval_strategy", ""))},
                    {"key": "Web Search", "value": str(state.get("web_search", False))},
                    {"key": "Graph Retrieval", "value": str(state.get("graph_retrieval", False))},
                ],
            ),
        )
        builder.add_node(
            "rewrite",
            self._wrap_stage(
                "rewrite",
                "Query Rewrite",
                self.rewrite.invoke,
                lambda state: [{"key": "Rewritten Query", "value": state.get("rewritten_query", "")}],
            ),
        )
        builder.add_node(
            "retrieval",
            self._wrap_stage(
                "retrieval",
                "Retrieval Wrapper",
                self.retrieval_wrapper,
                lambda state: [
                    {"key": "Multi Queries", "value": str(len(state.get("multi_queries", [])))},
                    {"key": "Documents", "value": str(len(state.get("retrieved_documents", [])))},
                    {"key": "Chunks", "value": str(len(state.get("chunks", [])))},
                    {"key": "Dense", "value": str(len(state.get("dense_results", [])))},
                    {"key": "BM25", "value": str(len(state.get("sparse_results", [])))},
                    {"key": "Merged", "value": str(len(state.get("merged_results", [])))},
                    {"key": "Reranked", "value": str(len(state.get("reranked_results", [])))},
                ],
                "Searching Sources",
            ),
        )
        builder.add_node(
            "graph",
            self._wrap_stage(
                "graph",
                "Knowledge Graph Wrapper",
                self.knowledge_graph_wrapper,
                lambda state: [
                    {"key": "Entities", "value": str(len(state.get("entities", [])))},
                    {"key": "Relations", "value": str(len(state.get("relations", [])))},
                    {"key": "Graph Results", "value": str(len(state.get("graph_results", [])))},
                ],
                "Knowledge Graph Built",
            ),
        )
        builder.add_node(
            "reasoning",
            self._wrap_stage(
                "reason",
                "Reasoning",
                self.reasoning.invoke,
                lambda state: [{"key": "Answer Length", "value": str(len(state.get("answer", "")))}],
                "Reasoning",
            ),
        )
        builder.add_node(
            "verifier",
            self._wrap_stage(
                "verify",
                "Verification",
                self.verifier.invoke,
                lambda state: [
                    {"key": "Supported", "value": str(state.get("supported", False))},
                    {"key": "Needs Reretrieval", "value": str(state.get("needs_reretrieval", False))},
                ],
                "Verifying",
            ),
        )
        builder.add_node(
            "reflection",
            self._wrap_stage(
                "reflect",
                "Reflection",
                self.reflection.invoke,
                lambda state: [
                    {"key": "Next Action", "value": str(state.get("next_action", ""))},
                    {"key": "Improved Query", "value": state.get("improved_query", "")},
                ],
                "Reflecting",
            ),
        )
        builder.add_node(
            "evaluation",
            self._wrap_stage(
                "eval",
                "Evaluation Wrapper",
                self.evaluation_wrapper,
                lambda state: [
                    {"key": "Confidence", "value": str(state.get("confidence", {}).get("confidence_score", ""))},
                    {"key": "Groundedness", "value": str(state.get("groundedness", {}).get("groundedness_score", ""))},
                    {"key": "Hallucination", "value": str(state.get("hallucination", {}).get("hallucination_score", ""))},
                ],
                "Finalizing",
            ),
        )
        builder.add_node(
            "judge",
            self._wrap_stage(
                "judge",
                "Judge",
                self.judge.invoke,
                lambda state: [
                    {"key": "Approved", "value": str(state.get("approved", False))},
                    {"key": "Reason", "value": str(state.get("judge_reason", ""))},
                ],
                "Completed",
            ),
        )

        builder.add_edge(START, "language")
        builder.add_edge("language", "planner")
        builder.add_edge("planner", "rewrite")
        builder.add_edge("rewrite", "retrieval")
        builder.add_edge("retrieval", "graph")
        builder.add_edge("graph", "reasoning")
        builder.add_edge("reasoning", "verifier")
        builder.add_edge("verifier", "evaluation")
        builder.add_edge("evaluation", "judge")

        builder.add_conditional_edges(
            "judge",
            Router.judge_route,
            {
                "reflection": "reflection",
                "end": END,
            },
        )

        builder.add_conditional_edges(
            "reflection",
            Router.reflection_route,
            {
                "rewrite": "rewrite",
                "graph": "graph",
                "end": END,
            },
        )

        return builder
