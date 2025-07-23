"""
Configuration for Document-Folder Linker
"""

# Neo4j Aura Configuration  
NEO4J_URI = "neo4j+s://013fb011.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp4"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Relationship Configuration
RELATIONSHIP_TYPE = "HAVE"  # folder -[:HAVE]-> entity

# Query Batch Size
BATCH_SIZE = 100
