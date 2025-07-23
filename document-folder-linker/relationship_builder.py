"""
Relationship Builder for Document-Folder Linker
Creates HAVE relationships between folder nodes and document entities
"""

import logging
from typing import Dict, List, Tuple, Any
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, RELATIONSHIP_TYPE, BATCH_SIZE
from emoji_utils import safe_log

class RelationshipBuilder:
    def __init__(self):
        """Initialize RelationshipBuilder with Neo4j connection"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.logger = logging.getLogger(__name__)
        
    def safe_log_info(self, message):
        """Log info with emoji replacement"""
        self.logger.info(safe_log(message))
        
    def close(self):
        """Close database connection"""
        if hasattr(self, 'driver'):
            self.driver.close()
            
    def get_document_entities(self) -> List[Dict[str, Any]]:
        """Get all entities that belong to documents with folder_name and course_code"""
        with self.driver.session() as session:
            # Find entities from chunks belonging to documents via PART_OF relationship
            query_chunk_entities = """
            MATCH (c:Chunk)-[:PART_OF]->(d:Document), (c)-[:HAS_ENTITY]->(e)
            WHERE d.folder_name IS NOT NULL AND d.course_code IS NOT NULL
                AND NOT e:Document AND NOT e:Chunk
            RETURN d.folder_name as document_folder_name,
                   d.course_code as document_course_code,
                   d.fileName as document_name,
                   e as entity,
                   elementId(e) as entity_id,
                   labels(e)[0] as entity_type
            ORDER BY d.course_code, d.folder_name
            """
            
            result = session.run(query_chunk_entities)
            entities = []
            
            for record in result:
                entities.append({
                    'document_folder_name': record['document_folder_name'],
                    'document_course_code': record['document_course_code'],
                    'document_name': record['document_name'],
                    'entity': record['entity'],
                    'entity_id': record['entity_id'],
                    'entity_type': record['entity_type']
                })
            
            # If no entities found, try via FIRST_CHUNK relationship
            if not entities:
                self.logger.info("No entities via PART_OF found, trying FIRST_CHUNK relationship...")
                
                query_first_chunk = """
                MATCH (d:Document)-[:FIRST_CHUNK]->(c:Chunk)-[:HAS_ENTITY]->(e)
                WHERE d.folder_name IS NOT NULL AND d.course_code IS NOT NULL
                    AND NOT e:Document AND NOT e:Chunk
                RETURN d.folder_name as document_folder_name,
                       d.course_code as document_course_code,
                       d.fileName as document_name,
                       e as entity,
                       elementId(e) as entity_id,
                       labels(e)[0] as entity_type
                ORDER BY d.course_code, d.folder_name
                """
                
                result = session.run(query_first_chunk)
                
                for record in result:
                    entities.append({
                        'document_folder_name': record['document_folder_name'],
                        'document_course_code': record['document_course_code'],
                        'document_name': record['document_name'],
                        'entity': record['entity'],
                        'entity_id': record['entity_id'],
                        'entity_type': record['entity_type']
                    })
            
            # If still no entities, try any connection between document and chunks
            if not entities:
                self.logger.info("Trying any document-chunk connection...")
                
                query_any_connection = """
                MATCH (d:Document), (c:Chunk), (c)-[:HAS_ENTITY]->(e)
                WHERE d.folder_name IS NOT NULL AND d.course_code IS NOT NULL
                    AND ((d)-[:FIRST_CHUNK]->(c) OR (c)-[:PART_OF]->(d))
                    AND NOT e:Document AND NOT e:Chunk
                RETURN d.folder_name as document_folder_name,
                       d.course_code as document_course_code,
                       d.fileName as document_name,
                       e as entity,
                       elementId(e) as entity_id,
                       labels(e)[0] as entity_type
                ORDER BY d.course_code, d.folder_name
                """
                
                result = session.run(query_any_connection)
                
                for record in result:
                    entities.append({
                        'document_folder_name': record['document_folder_name'],
                        'document_course_code': record['document_course_code'],
                        'document_name': record['document_name'],
                        'entity': record['entity'],
                        'entity_id': record['entity_id'],
                        'entity_type': record['entity_type']
                    })
                
            return entities
    
    def get_folder_nodes(self) -> List[Dict[str, Any]]:
        """Get all folder nodes with name and course_code"""
        with self.driver.session() as session:
            query = """
            MATCH (f)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN f as folder_node,
                   elementId(f) as folder_id,
                   f.name as folder_name,
                   f.course_code as folder_course_code,
                   labels(f)[0] as folder_label
            ORDER BY f.course_code, f.name
            """
            
            result = session.run(query)
            folders = []
            
            for record in result:
                folders.append({
                    'folder_node': record['folder_node'],
                    'folder_id': record['folder_id'],
                    'folder_name': record['folder_name'],
                    'folder_course_code': record['folder_course_code'],
                    'folder_label': record['folder_label']
                })
                
            return folders
    
    def find_matching_entities(self) -> List[Dict[str, Any]]:
        """Find entities that should be linked to folder nodes"""
        entities = self.get_document_entities()
        folders = self.get_folder_nodes()
        
        # Create lookup dictionary for faster matching
        folder_lookup = {}
        for folder in folders:
            key = (folder['folder_name'], folder['folder_course_code'])
            if key not in folder_lookup:
                folder_lookup[key] = []
            folder_lookup[key].append(folder)
        
        matches = []
        
        for entity in entities:
            key = (entity['document_folder_name'], entity['document_course_code'])
            if key in folder_lookup:
                for folder in folder_lookup[key]:
                    matches.append({
                        'folder_id': folder['folder_id'],
                        'folder_name': folder['folder_name'],
                        'folder_course_code': folder['folder_course_code'],
                        'folder_label': folder['folder_label'],
                        'entity_id': entity['entity_id'],
                        'document_name': entity['document_name'],
                        'document_folder_name': entity['document_folder_name'],
                        'document_course_code': entity['document_course_code']
                    })
        
        return matches
    
    def create_have_relationships(self, matches: List[Dict[str, Any]]) -> int:
        """Create HAVE relationships between folder nodes and entities"""
        created_count = 0
        
        with self.driver.session() as session:
            # Process in batches
            for i in range(0, len(matches), BATCH_SIZE):
                batch = matches[i:i + BATCH_SIZE]
                
                # Create batch query
                query = f"""
                UNWIND $matches as match
                MATCH (f), (e)
                WHERE elementId(f) = match.folder_id AND elementId(e) = match.entity_id
                MERGE (f)-[:{RELATIONSHIP_TYPE}]->(e)
                RETURN count(*) as created
                """
                
                try:
                    result = session.run(query, matches=batch)
                    batch_created = result.single()['created']
                    created_count += batch_created
                    
                    self.safe_log_info(f"✅ Created {batch_created} HAVE relationships in batch {i//BATCH_SIZE + 1}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error creating relationships for batch {i//BATCH_SIZE + 1}: {e}")
                    continue
        
        return created_count
    
    def cleanup_existing_relationships(self) -> int:
        """Remove existing HAVE relationships between folders and entities"""
        with self.driver.session() as session:
            query = f"""
            MATCH (f)-[r:{RELATIONSHIP_TYPE}]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            DELETE r
            RETURN count(r) as deleted_count
            """
            
            result = session.run(query)
            record = result.single()
            deleted_count = record['deleted_count'] if record else 0
            
            if deleted_count > 0:
                self.safe_log_info(f"🗑️ Deleted {deleted_count} existing HAVE relationships")
            
            return deleted_count
    
    def verify_relationships(self) -> Dict[str, Any]:
        """Verify created relationships"""
        with self.driver.session() as session:
            query_total = f"""
            MATCH (f)-[:{RELATIONSHIP_TYPE}]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN count(*) as total_relationships
            """
            
            query_sample = f"""
            MATCH (f)-[:{RELATIONSHIP_TYPE}]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN f.name as folder_name,
                   f.course_code as folder_course_code,
                   labels(f)[0] as folder_label,
                   labels(e) as entity_labels,
                   elementId(e) as entity_id
            LIMIT 10
            """
            
            total = session.run(query_total).single()['total_relationships']
            sample = session.run(query_sample).data()
            
            return {
                'total_relationships': total,
                'sample_relationships': sample
            }
    
    def build_all_relationships(self) -> Dict[str, Any]:
        """Main method to build all folder-entity relationships"""
        self.safe_log_info("🚀 Starting relationship building process...")
        
        # Step 1: Find matching entities
        self.safe_log_info("📊 Finding matching entities...")
        matches = self.find_matching_entities()
        self.safe_log_info(f"🎯 Found {len(matches)} potential relationships")
        
        if not matches:
            self.logger.warning("⚠️ No matching entities found!")
            return {
                'cleanup_count': 0,
                'created_count': 0,
                'total_relationships': 0,
                'sample_relationships': [],
                'status': 'NO_MATCHES'
            }
        
        # Step 2: Cleanup existing relationships
        self.safe_log_info("🧹 Cleaning up existing relationships...")
        cleanup_count = self.cleanup_existing_relationships()
        
        # Step 3: Create new relationships
        self.safe_log_info("🔗 Creating new HAVE relationships...")
        created_count = self.create_have_relationships(matches)
        
        # Step 4: Verify results
        self.safe_log_info("✅ Verifying relationships...")
        verification = self.verify_relationships()
        
        result = {
            'cleanup_count': cleanup_count,
            'created_count': created_count,
            'total_relationships': verification['total_relationships'],
            'sample_relationships': verification['sample_relationships'],
            'expected_count': len(matches),
            'status': 'SUCCESS' if created_count > 0 else 'FAILED'
        }
        
        self.safe_log_info(f"🎉 Process completed: {created_count} relationships created")
        return result
