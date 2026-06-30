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

    def language_node(self, state: DagenGoState) -> DagenGoState:
        """Detect query language."""
        state["language"] = detect_language(state["query"])
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
        chunks = state.get("chunks", [])
        if chunks:
            return "\n\n".join(chunk.get("text", "") for chunk in chunks if chunk.get("text"))

        documents = state.get("retrieved_documents", [])
        return "\n\n".join(document.get("text", "") for document in documents if document.get("text"))

    def knowledge_graph_wrapper(self, state: DagenGoState) -> DagenGoState:
        """Extract entities/relations from retrieved evidence, then retrieve graph context."""
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

    def evaluation_wrapper(self, state: DagenGoState) -> DagenGoState:
        """Run hallucination, confidence, and groundedness evaluators."""
        evidence = state.get("reranked_results", [])

        hallucination = self.hallucination.evaluate(
            query=state["query"],
            answer=state.get("answer", ""),
            evidence=evidence,
        )
        state["hallucination"] = hallucination

        state["confidence"] = self.confidence.evaluate(
            query=state["query"],
            answer=state.get("answer", ""),
            evidence=evidence,
            verification=state.get("verification", {}),
            hallucination=hallucination,
        )

        state["groundedness"] = self.groundedness.evaluate(
            query=state["query"],
            answer=state.get("answer", ""),
            evidence=evidence,
        )

        return state

    def build(self):
        """Register nodes and compile the frozen graph shape."""
        builder = self.builder

        builder.add_node("language", self.language_node)
        builder.add_node("planner", self.planner.invoke)
        builder.add_node("rewrite", self.rewrite.invoke)
        builder.add_node("retrieval", self.retrieval_wrapper)
        builder.add_node("graph", self.knowledge_graph_wrapper)
        builder.add_node("reasoning", self.reasoning.invoke)
        builder.add_node("verifier", self.verifier.invoke)
        builder.add_node("reflection", self.reflection.invoke)
        builder.add_node("evaluation", self.evaluation_wrapper)
        builder.add_node("judge", self.judge.invoke)

        builder.add_edge(START, "language")
        builder.add_edge("language", "planner")
        builder.add_edge("planner", "rewrite")
        builder.add_edge("rewrite", "retrieval")
        builder.add_edge("retrieval", "graph")
        builder.add_edge("graph", "reasoning")
        builder.add_edge("reasoning", "verifier")
        builder.add_edge("verifier", "reflection")
        builder.add_edge("reflection", "evaluation")
        builder.add_edge("evaluation", "judge")

        builder.add_conditional_edges(
            "judge",
            Router.judge_route,
            {
                "reflection": "reflection",
                "end": END,
            },
        )

        return builder
