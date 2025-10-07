# src/knowledge_base/graph_store.py
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from loguru import logger
from config.settings import get_settings


class GraphStore:
    def __init__(self):
        self.settings = get_settings()
        self.driver = GraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_user, self.settings.neo4j_password),
        )
        logger.info("Graph store initialized")

    def close(self):
        self.driver.close()

    def create_entity(self, entity_type: str, properties: Dict[str, Any]):
        """Create an entity node"""
        with self.driver.session() as session:
            query = f"""
            CREATE (e:{entity_type} $properties)
            RETURN e
            """
            result = session.run(query, properties=properties)
            return result.single()

    def create_relationship(
        self,
        from_entity: str,
        to_entity: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Create relationship between entities"""
        with self.driver.session() as session:
            query = (
                """
            MATCH (a {id: $from_entity}), (b {id: $to_entity})
            CREATE (a)-[r:%s $properties]->(b)
            RETURN r
            """
                % relationship_type
            )
            result = session.run(
                query,
                from_entity=from_entity,
                to_entity=to_entity,
                properties=properties or {},
            )
            return result.single()

    def find_related_entities(
        self, entity_id: str, max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """Find entities related to given entity"""
        with self.driver.session() as session:
            query = (
                """
            MATCH path = (e {id: $entity_id})-[*1..%d]-(related)
            RETURN related, length(path) as distance
            ORDER BY distance
            """
                % max_depth
            )
            result = session.run(query, entity_id=entity_id)
            return [
                {"entity": record["related"], "distance": record["distance"]}
                for record in result
            ]

    def clear_graph(self):
        """Clear all nodes and relationships"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Graph cleared")

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        with self.driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()[
                "count"
            ]
            rel_count = session.run(
                "MATCH ()-[r]->() RETURN count(r) as count"
            ).single()["count"]
            return {"nodes": node_count, "relationships": rel_count}
