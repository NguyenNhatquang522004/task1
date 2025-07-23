"""
Cleanup Tool for Document-Folder Linker
Removes HAVE relationships between folder nodes and entities
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, RELATIONSHIP_TYPE

class CleanupTool:
    def __init__(self):
        """Initialize CleanupTool with Neo4j connection"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.logger = logging.getLogger(__name__)
        
    def close(self):
        """Close database connection"""
        if hasattr(self, 'driver'):
            self.driver.close()
            
    def get_cleanup_statistics(self) -> Dict[str, Any]:
        """Get statistics for cleanup operations"""
        with self.driver.session() as session:
            # Count HAVE relationships
            query_relationships = f"""
            MATCH (f)-[r:{RELATIONSHIP_TYPE}]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN count(r) as relationships_count
            """
            
            # Get folder types involved
            query_folder_types = f"""
            MATCH (f)-[:{RELATIONSHIP_TYPE}]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN DISTINCT labels(f)[0] as folder_type, 
                   f.name as folder_name,
                   f.course_code as course_code
            ORDER BY folder_type, course_code, folder_name
            """
            
            relationships_count = session.run(query_relationships).single()['relationships_count']
            folder_types_result = session.run(query_folder_types).data()
            
            # Group by folder type
            folder_types = {}
            for record in folder_types_result:
                folder_type = record['folder_type']
                if folder_type not in folder_types:
                    folder_types[folder_type] = []
                folder_types[folder_type].append(f"{record['folder_name']} ({record['course_code']})")
            
            return {
                'relationships_count': relationships_count,
                'folder_types': folder_types,
                'total_folder_combinations': len(folder_types_result)
            }
    
    def cleanup_all_relationships(self) -> int:
        """Remove all HAVE relationships between folders and entities"""
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
            
            self.logger.info(f"🗑️ Deleted {deleted_count} HAVE relationships")
            return deleted_count
    
    def cleanup_by_folder_type(self, folder_type: str) -> int:
        """Remove HAVE relationships for specific folder type"""
        with self.driver.session() as session:
            query = f"""
            MATCH (f)-[r:{RELATIONSHIP_TYPE}]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
                AND labels(f)[0] = $folder_type
            DELETE r
            RETURN count(r) as deleted_count
            """
            
            result = session.run(query, folder_type=folder_type)
            record = result.single()
            deleted_count = record['deleted_count'] if record else 0
            
            self.logger.info(f"🗑️ Deleted {deleted_count} HAVE relationships for folder type: {folder_type}")
            return deleted_count
    
    def cleanup_by_course_code(self, course_code: str) -> int:
        """Remove HAVE relationships for specific course code"""
        with self.driver.session() as session:
            query = f"""
            MATCH (f)-[r:{RELATIONSHIP_TYPE}]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
                AND f.course_code = $course_code
            DELETE r
            RETURN count(r) as deleted_count
            """
            
            result = session.run(query, course_code=course_code)
            record = result.single()
            deleted_count = record['deleted_count'] if record else 0
            
            self.logger.info(f"🗑️ Deleted {deleted_count} HAVE relationships for course: {course_code}")
            return deleted_count
    
    def verify_cleanup(self) -> bool:
        """Verify cleanup was successful"""
        stats = self.get_cleanup_statistics()
        is_clean = stats['relationships_count'] == 0
        
        print(f"\n🔍 Cleanup Verification:")
        print(f"   - Remaining HAVE relationships: {stats['relationships_count']}")
        print(f"   - Status: {'✅ CLEAN' if is_clean else '⚠️ INCOMPLETE'}")
        
        return is_clean

def main():
    """Main function - Automatically cleanup all HAVE relationships"""
    logging.basicConfig(level=logging.INFO)
    cleanup = CleanupTool()
    
    try:
        print("=" * 70)
        print("🧹 DOCUMENT-FOLDER LINKER - AUTO CLEANUP TOOL")
        print("=" * 70)
        
        # Display current statistics
        print("\n📊 Current Statistics:")
        stats = cleanup.get_cleanup_statistics()
        print(f"   - HAVE relationships: {stats['relationships_count']}")
        print(f"   - Folder combinations: {stats['total_folder_combinations']}")
        
        if stats['folder_types']:
            print(f"   - Folder types involved:")
            for folder_type, combinations in stats['folder_types'].items():
                print(f"     • {folder_type}: {len(combinations)} combinations")
        
        if stats['relationships_count'] == 0:
            print("\n✅ Database is already clean!")
            return
        
        print(f"\n🗑️ AUTO CLEANUP: Deleting ALL HAVE relationships...")
        print(f"   - Will delete {stats['relationships_count']} relationships")
        print(f"   - Folder combinations affected: {stats['total_folder_combinations']}")
        
        # Automatic cleanup all
        deleted_count = cleanup.cleanup_all_relationships()
        
        print(f"\n✅ Auto cleanup completed:")
        print(f"   - Deleted {deleted_count} HAVE relationships")
        
        # Verification
        cleanup.verify_cleanup()
        
        print("\n🎉 Cleanup process finished successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Cleanup error: {e}", exc_info=True)
    finally:
        cleanup.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()
