"""
Neo4j Connection Utilities
"""
import logging
from typing import Optional
from neo4j import GraphDatabase
from langchain_neo4j import Neo4jGraph
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

logger = logging.getLogger(__name__)

class Neo4jConnection:
    """Neo4j database connection manager"""
    
    def __init__(self):
        self.driver = None
        self.graph = None
    
    def connect(self) -> Neo4jGraph:
        """Create Neo4j graph connection"""
        try:
            self.graph = Neo4jGraph(
                url=NEO4J_URI,
                username=NEO4J_USERNAME,
                password=NEO4J_PASSWORD,
                database=NEO4J_DATABASE,
                sanitize=True,
                refresh_schema=False
            )
            logger.info("Successfully connected to Neo4j database")
            return self.graph
            
        except Exception as e:
            logger.error(f"Error connecting to Neo4j: {e}")
            raise
    
    def get_driver(self):
        """Get Neo4j driver for direct queries"""
        try:
            if not self.driver:
                self.driver = GraphDatabase.driver(
                    NEO4J_URI,
                    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
                )
            return self.driver
            
        except Exception as e:
            logger.error(f"Error creating Neo4j driver: {e}")
            raise
    
    def close(self):
        """Close connections"""
        if self.driver:
            self.driver.close()
        if self.graph:
            self.graph._driver.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            graph = self.connect()
            # Simple test query
            result = graph.query("RETURN 1 as test")
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

def create_graph_connection() -> Neo4jGraph:
    """Create and return a Neo4j graph connection"""
    connection = Neo4jConnection()
    return connection.connect()

def test_neo4j_connection() -> bool:
    """Test Neo4j connection"""
    connection = Neo4jConnection()
    return connection.test_connection()
