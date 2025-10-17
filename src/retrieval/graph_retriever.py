# src/retrieval/graph_retriever.py
from typing import List, Dict, Any, Optional
from src.knowledge_base.graph_store import GraphStore
from loguru import logger


class GraphRetriever:
    """Graph-based retrieval for relationship queries"""

    def __init__(self):
        self.graph_store = GraphStore()

    def find_related_entities(
        self,
        entity_name: str,
        relationship_types: Optional[List[str]] = None,
        max_depth: int = 2,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Find entities related to given entity"""

        try:
            with self.graph_store.driver.session() as session:
                # Build relationship filter
                rel_filter = ""
                if relationship_types:
                    rel_types = "|".join(relationship_types)
                    rel_filter = f":{rel_types}"

                query = f"""
                MATCH path = (e {{name: $entity_name}})-[r{rel_filter}*1..{max_depth}]-(related)
                RETURN related, r, length(path) as distance
                ORDER BY distance, related.name
                LIMIT {limit}
                """

                result = session.run(query, entity_name=entity_name)

                related_entities = []
                for record in result:
                    related = record["related"]
                    relationships = record["r"]
                    distance = record["distance"]

                    related_entities.append(
                        {
                            "entity": dict(related),
                            "relationships": [dict(rel) for rel in relationships],
                            "distance": distance,
                            "retrieval_method": "graph_traversal",
                        }
                    )

                logger.info(
                    f"Found {len(related_entities)} related entities for {entity_name}"
                )
                return related_entities

        except Exception as e:
            logger.error(f"Graph search error: {e}")
            return []

    def find_path_between_entities(
        self, entity1: str, entity2: str, max_depth: int = 4
    ) -> List[Dict[str, Any]]:
        """Find shortest path between two entities"""

        try:
            with self.graph_store.driver.session() as session:
                query = f"""
                MATCH path = shortestPath((e1 {{name: $entity1}})-[*1..{max_depth}]-(e2 {{name: $entity2}}))
                RETURN path, length(path) as distance
                """

                result = session.run(query, entity1=entity1, entity2=entity2)
                record = result.single()

                if record:
                    path = record["path"]
                    distance = record["distance"]

                    # Extract nodes and relationships from path
                    nodes = [dict(node) for node in path.nodes]
                    relationships = [dict(rel) for rel in path.relationships]

                    return [
                        {
                            "path_nodes": nodes,
                            "path_relationships": relationships,
                            "distance": distance,
                            "retrieval_method": "graph_path",
                        }
                    ]

                return []

        except Exception as e:
            logger.error(f"Graph path search error: {e}")
            return []

    def search_by_properties(
        self,
        node_labels: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search nodes by labels and properties"""

        try:
            with self.graph_store.driver.session() as session:
                # Build query
                labels = ":".join(node_labels) if node_labels else ""

                where_clauses = []
                params = {}

                if properties:
                    for key, value in properties.items():
                        param_key = f"prop_{key}"
                        where_clauses.append(f"n.{key} = ${param_key}")
                        params[param_key] = value

                where_clause = (
                    "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                )

                query = f"""
                MATCH (n{":" + labels if labels else ""})
                {where_clause}
                RETURN n
                LIMIT {limit}
                """

                result = session.run(query, **params)

                nodes = []
                for record in result:
                    node = dict(record["n"])
                    nodes.append(
                        {"entity": node, "retrieval_method": "graph_property_search"}
                    )

                logger.info(f"Found {len(nodes)} nodes matching criteria")
                return nodes

        except Exception as e:
            logger.error(f"Graph property search error: {e}")
            return []

    def get_entity_neighbors(
        self, entity_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get direct neighbors of an entity"""

        try:
            with self.graph_store.driver.session() as session:
                query = """
                MATCH (e {name: $entity_name})-[r]-(neighbor)
                RETURN neighbor, r, type(r) as relationship_type
                LIMIT $limit
                """

                result = session.run(query, entity_name=entity_name, limit=limit)

                neighbors = []
                for record in result:
                    neighbor = dict(record["neighbor"])
                    relationship = dict(record["r"])
                    rel_type = record["relationship_type"]

                    neighbors.append(
                        {
                            "entity": neighbor,
                            "relationship": relationship,
                            "relationship_type": rel_type,
                            "distance": 1,
                            "retrieval_method": "graph_neighbors",
                        }
                    )

                logger.info(f"Found {len(neighbors)} neighbors for {entity_name}")
                return neighbors

        except Exception as e:
            logger.error(f"Graph neighbors search error: {e}")
            return []
