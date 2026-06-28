from graph.state import DagenGoState

from knowledge_graph.neo4j_client import Neo4jClient
from knowledge_graph.graph_queries import (
    GET_ENTITY,
    GET_NEIGHBORS,
    SEARCH_ENTITIES,
)


class GraphRetriever:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def search_entities(
        self,
        query: str,
    ):

        return self.neo4j.run_query(
            SEARCH_ENTITIES,
            {
                "query": query,
            },
        )

    def get_neighbors(
        self,
        entity: str,
    ):

        return self.neo4j.run_query(
            GET_NEIGHBORS,
            {
                "name": entity,
            },
        )

    def retrieve(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        query = state["rewritten_query"]

        entities = self.search_entities(query)

        graph_results = []

        for entity in entities:

            graph_results.extend(
                self.get_neighbors(
                    entity["e"]["name"]
                )
            )

        state["graph_results"] = graph_results

        return state