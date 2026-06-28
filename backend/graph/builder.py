from langgraph.graph import StateGraph, START, END

from graph.state import DagenGoState
from graph.router import Router

# --------------------------
# Agents
# --------------------------

from agents.planner_agent import PlannerAgent
from agents.rewrite_agent import RewriteAgent
from agents.reasoning_agent import ReasoningAgent
from agents.verifier_agent import VerifierAgent
from agents.reflection_agent import ReflectionAgent
from agents.judge_agent import JudgeAgent

# --------------------------
# Retrieval
# --------------------------

from retrieval.web_search import WebSearch
from retrieval.chunker import Chunker
from retrieval.multi_query import MultiQueryRetriever
from retrieval.hybrid import HybridRetriever
from retrieval.merge import RetrievalMerger
from retrieval.reranker import Reranker

# --------------------------
# Knowledge Graph
# --------------------------

from knowledge_graph.entity_extractor import EntityExtractor
from knowledge_graph.relation_extractor import RelationExtractor
from knowledge_graph.graph_builder import GraphBuilder
from knowledge_graph.graph_retriever import GraphRetriever

# --------------------------
# Evaluation
# --------------------------

from evaluation.hallucination import HallucinationDetector
from evaluation.confidence import ConfidenceScorer
from evaluation.groundedness import GroundednessEvaluator

# --------------------------
# Utils
# --------------------------

from utils.language_detector import detect_language


class DagenGoGraph:

    def __init__(self):

        self.builder = StateGraph(DagenGoState)

        # ----------------------
        # Agents
        # ----------------------

        self.planner = PlannerAgent()
        self.rewrite = RewriteAgent()
        self.reasoning = ReasoningAgent()
        self.verifier = VerifierAgent()
        self.reflection = ReflectionAgent()
        self.judge = JudgeAgent()

        # ----------------------
        # Retrieval
        # ----------------------

        self.search = WebSearch()
        self.chunker = Chunker()
        self.multi_query = MultiQueryRetriever()
        self.hybrid = HybridRetriever()
        self.merge = RetrievalMerger()
        self.reranker = Reranker()

        # ----------------------
        # Graph
        # ----------------------

        self.entity = EntityExtractor()
        self.relation = RelationExtractor()
        self.graph = GraphBuilder()
        self.graph_retriever = GraphRetriever()

        # ----------------------
        # Evaluation
        # ----------------------

        self.hallucination = HallucinationDetector()
        self.confidence = ConfidenceScorer()
        self.groundedness = GroundednessEvaluator()
    # ==========================================================
# Wrapper Nodes
# ==========================================================

def language_node(
    self,
    state: DagenGoState,
) -> DagenGoState:

    state["language"] = detect_language(
        state["query"]
    )

    return state


def retrieval_node(
    self,
    state: DagenGoState,
) -> DagenGoState:

    # Multi Query Generation
    state = self.multi_query.generate(state)

    # Web Search
    documents = self.search.search(
        state["rewritten_query"]
    )

    state["retrieved_documents"] = documents

    # Chunking
    chunks = self.chunker.chunk_documents(
        documents
    )

    state["chunks"] = chunks

    # Hybrid Retrieval
    state = self.hybrid.retrieve(state)

    # Merge
    state = self.merge.merge(state)

    # Cross Encoder Reranking
    state = self.reranker.rerank(state)

    return state


def graph_node(
    self,
    state: DagenGoState,
) -> DagenGoState:

    entities = self.entity.extract(
        state["answer"]
    )

    relations = self.relation.extract(
        state["answer"],
        entities,
    )

    self.graph.build(
        entities,
        relations,
    )

    state["entities"] = entities
    state["relations"] = relations

    state = self.graph_retriever.retrieve(
        state
    )

    return state


def evaluation_node(
    self,
    state: DagenGoState,
) -> DagenGoState:

    hallucination = self.hallucination.evaluate(
        query=state["query"],
        answer=state["answer"],
        evidence=state["reranked_results"],
    )

    state["hallucination"] = hallucination

    confidence = self.confidence.evaluate(
        query=state["query"],
        answer=state["answer"],
        evidence=state["reranked_results"],
        verification=state["verification"],
        hallucination=hallucination,
    )

    state["confidence"] = confidence

    groundedness = self.groundedness.evaluate(
        query=state["query"],
        answer=state["answer"],
        evidence=state["reranked_results"],
    )

    state["groundedness"] = groundedness

    return state
def build(self):

    builder = self.builder

    # ==========================================================
    # Register Nodes
    # ==========================================================

    builder.add_node(
        "language",
        self.language_node,
    )

    builder.add_node(
        "planner",
        self.planner.invoke,
    )

    builder.add_node(
        "rewrite",
        self.rewrite.invoke,
    )

    builder.add_node(
        "retrieval",
        self.retrieval_node,
    )

    builder.add_node(
        "graph",
        self.graph_node,
    )

    builder.add_node(
        "reasoning",
        self.reasoning.invoke,
    )

    builder.add_node(
        "verifier",
        self.verifier.invoke,
    )

    builder.add_node(
        "reflection",
        self.reflection.invoke,
    )

    builder.add_node(
        "evaluation",
        self.evaluation_node,
    )

    builder.add_node(
        "judge",
        self.judge.invoke,
    )
        # ==========================================================
    # Normal Flow
    # ==========================================================

    builder.add_edge(
        START,
        "language",
    )

    builder.add_edge(
        "language",
        "planner",
    )

    builder.add_edge(
        "planner",
        "rewrite",
    )
    builder.add_conditional_edges(
        "rewrite",
        Router.planner_route,
        {
            "retrieval": "retrieval",
            "graph": "graph",
        },
    )
    builder.add_edge(
        "retrieval",
        "graph",
    )

    builder.add_edge(
        "graph",
        "reasoning",
    )

    builder.add_edge(
        "reasoning",
        "verifier",
    )

    builder.add_edge(
        "verifier",
        "reflection",
    )

    builder.add_edge(
        "reflection",
        "evaluation",
    )

    builder.add_edge(
        "evaluation",
        "judge",
    )
    builder.add_conditional_edges(
        "judge",
        Router.judge_route,
        {
            "reflection": "reflection",
            "end": END,
        },
    )

    return builder
    