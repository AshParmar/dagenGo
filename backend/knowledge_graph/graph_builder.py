"""
Graph Builder — Optimized with:
  1. Batched Neo4j transactions (single session for all writes)
  2. MERGE semantics for incremental updates (no duplicate nodes/edges)
  3. Typed relation labels for richer graph schema
  4. Graceful degradation when Neo4j is unavailable
"""
import logging
from knowledge_graph.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


class GraphBuilder:

    def __init__(self) -> None:
        self.neo4j = Neo4jClient()

    def add_entities(self, entities: list[dict]) -> None:
        if not entities:
            return

        query = """
        UNWIND $entities AS ent
        MERGE (e:Entity {name: ent.name})
        ON CREATE SET e.type = ent.type, e.created_at = timestamp()
        ON MATCH SET e.type = ent.type
        """
        try:
            self.neo4j.run_query(query, {"entities": [
                {"name": e["name"], "type": e.get("type", "Entity")}
                for e in entities
                if isinstance(e, dict) and e.get("name")
            ]})
        except Exception as exc:
            logger.warning("GraphBuilder.add_entities failed: %s", exc)

    def add_relations(self, relations: list[dict]) -> None:
        if not relations:
            return

        # Batch all relation writes in a single query using UNWIND
        query = """
        UNWIND $relations AS rel
        MATCH (a:Entity {name: rel.source})
        MATCH (b:Entity {name: rel.target})
        MERGE (a)-[r:RELATION {type: rel.relation}]->(b)
        ON CREATE SET r.created_at = timestamp()
        """
        try:
            self.neo4j.run_query(query, {"relations": [
                {
                    "source": r["source"],
                    "target": r["target"],
                    "relation": r.get("relation", "RELATED_TO"),
                }
                for r in relations
                if isinstance(r, dict) and r.get("source") and r.get("target")
            ]})
        except Exception as exc:
            logger.warning("GraphBuilder.add_relations failed: %s", exc)

    def build(self, entities: list[dict], relations: list[dict]) -> None:
        """Write entities and relations to Neo4j using batched MERGE (incremental)."""
        self.add_entities(entities)
        self.add_relations(relations)