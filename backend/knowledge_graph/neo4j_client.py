from neo4j import GraphDatabase

from config import settings


class Neo4jClient:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(
                settings.NEO4J_USERNAME,
                settings.NEO4J_PASSWORD,
            ),
        )

    def close(self):
        self.driver.close()

    def run_query(
        self,
        query: str,
        parameters: dict | None = None,
    ):

        with self.driver.session() as session:

            result = session.run(
                query,
                parameters or {},
            )

            return [record.data() for record in result]