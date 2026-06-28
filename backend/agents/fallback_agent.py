from graph.state import DagenGoState

from retrieval.hybrid import HybridRetriever
from knowledge_graph.graph_retriever import GraphRetriever


class FallbackAgent:

    def __init__(self):

        self.hybrid = HybridRetriever()

        self.graph = GraphRetriever()

    def invoke(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        action = state["next_action"]

        if action == "continue":
            return state

        if action == "retrieve_again":

            state = self.hybrid.retrieve(
                state
            )

            return state

        if action == "graph_retrieve":

            state = self.graph.retrieve(
                state
            )

            return state

        if action == "ask_user":

            state["answer"] = (
                "I need a little more information to answer accurately."
            )

            return state

        if action == "abort":

            state["answer"] = (
                "I couldn't verify enough evidence to answer confidently."
            )

            return state

        return state