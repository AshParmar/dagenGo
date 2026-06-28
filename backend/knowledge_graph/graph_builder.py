from knowledge_graph.neo4j_client import Neo4jClient


class GraphBuilder:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def add_entities(
        self,
        entities: list,
    ):

        query = """
        MERGE (e:Entity {
            name: $name,
            type: $type
        })
        """

        for entity in entities:

            self.neo4j.run_query(
                query,
                {
                    "name": entity["name"],
                    "type": entity["type"],
                },
            )

    def add_relations(
        self,
        relations: list,
    ):

        query = """
        MATCH (a:Entity {name:$source})
        MATCH (b:Entity {name:$target})

        MERGE (a)-[:RELATION {
            type:$relation
        }]->(b)
        """

        for relation in relations:

            self.neo4j.run_query(
                query,
                {
                    "source": relation["source"],
                    "target": relation["target"],
                    "relation": relation["relation"],
                },
            )

    def build(
        self,
        entities: list,
        relations: list,
    ):

        self.add_entities(entities)

        self.add_relations(relations)