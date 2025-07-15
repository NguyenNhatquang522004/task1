#!/usr/bin/env python3
"""
Curriculum Link Cleaner

Script này xóa tất cả CurriculumLink nodes và các relationships liên quan:
- POINT_TO relationships (Course → CurriculumLink)
- HAVE_TO relationships (CurriculumLink → __Entity__)
- CurriculumLink nodes

Sử dụng khi cần cleanup hoặc reset curriculum linking system.
"""

import os
import logging
from typing import Dict
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CurriculumLinkCleaner:
    """Class để xóa CurriculumLink nodes và relationships"""
    
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j connection URI
            username: Neo4j username 
            password: Neo4j password
            database: Neo4j database name
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def get_cleanup_stats_before(self) -> Dict:
        """Get statistics before cleanup"""
        query = """
        // Count CurriculumLink nodes
        MATCH (cl:CurriculumLink)
        WITH count(cl) as curriculum_links
        
        // Count POINT_TO relationships
        MATCH ()-[r1:POINT_TO]->()
        WITH curriculum_links, count(r1) as point_to_rels
        
        // Count HAVE_TO relationships  
        MATCH ()-[r2:HAVE_TO]->()
        WITH curriculum_links, point_to_rels, count(r2) as have_to_rels
        
        // Count total entities linked via HAVE_TO
        MATCH (:CurriculumLink)-[:HAVE_TO]->(e:__Entity__)
        RETURN curriculum_links, point_to_rels, have_to_rels, count(DISTINCT e) as linked_entities
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            record = result.single()
            
            if record:
                return {
                    'curriculum_links': record['curriculum_links'],
                    'point_to_relationships': record['point_to_rels'],
                    'have_to_relationships': record['have_to_rels'],
                    'linked_entities': record['linked_entities']
                }
            
        return {
            'curriculum_links': 0,
            'point_to_relationships': 0,
            'have_to_relationships': 0,
            'linked_entities': 0
        }
    
    def delete_have_to_relationships(self) -> int:
        """
        Xóa tất cả HAVE_TO relationships
        
        Returns:
            Số lượng relationships đã xóa
        """
        logger.info("Deleting HAVE_TO relationships...")
        
        query = """
        MATCH (:CurriculumLink)-[r:HAVE_TO]->(:__Entity__)
        WITH r
        DELETE r
        RETURN count(*) as deleted_count
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            record = result.single()
            
            if record:
                count = record['deleted_count']
                logger.info(f"Deleted {count} HAVE_TO relationships")
                return count
                
        return 0
    
    def delete_point_to_relationships(self) -> int:
        """
        Xóa tất cả POINT_TO relationships
        
        Returns:
            Số lượng relationships đã xóa
        """
        logger.info("Deleting POINT_TO relationships...")
        
        query = """
        MATCH (:Course)-[r:POINT_TO]->(:CurriculumLink)
        WITH r
        DELETE r
        RETURN count(*) as deleted_count
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            record = result.single()
            
            if record:
                count = record['deleted_count']
                logger.info(f"Deleted {count} POINT_TO relationships")
                return count
                
        return 0
    
    def delete_curriculum_link_nodes(self) -> int:
        """
        Xóa tất cả CurriculumLink nodes
        
        Returns:
            Số lượng nodes đã xóa
        """
        logger.info("Deleting CurriculumLink nodes...")
        
        query = """
        MATCH (cl:CurriculumLink)
        WITH cl
        DELETE cl
        RETURN count(*) as deleted_count
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            record = result.single()
            
            if record:
                count = record['deleted_count']
                logger.info(f"Deleted {count} CurriculumLink nodes")
                return count
                
        return 0
    
    def verify_cleanup(self) -> Dict:
        """Verify that cleanup was successful"""
        logger.info("Verifying cleanup...")
        
        query = """
        // Check remaining CurriculumLink nodes
        MATCH (cl:CurriculumLink)
        WITH count(cl) as remaining_links
        
        // Check remaining POINT_TO relationships
        MATCH ()-[r1:POINT_TO]->()
        WITH remaining_links, count(r1) as remaining_point_to
        
        // Check remaining HAVE_TO relationships
        MATCH ()-[r2:HAVE_TO]->()
        RETURN remaining_links, remaining_point_to, count(r2) as remaining_have_to
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            record = result.single()
            
            if record:
                return {
                    'remaining_curriculum_links': record['remaining_links'],
                    'remaining_point_to': record['remaining_point_to'],
                    'remaining_have_to': record['remaining_have_to']
                }
            
        return {
            'remaining_curriculum_links': 0,
            'remaining_point_to': 0,
            'remaining_have_to': 0
        }
    
    def perform_complete_cleanup(self) -> Dict:
        """
        Thực hiện cleanup hoàn toàn theo thứ tự đúng
        
        Returns:
            Dictionary chứa thống kê cleanup
        """
        logger.info("="*60)
        logger.info("🧹 STARTING CURRICULUM LINK CLEANUP")
        logger.info("="*60)
        
        # Get stats before cleanup
        before_stats = self.get_cleanup_stats_before()
        logger.info("📊 BEFORE CLEANUP:")
        logger.info(f"  • CurriculumLink nodes: {before_stats['curriculum_links']}")
        logger.info(f"  • POINT_TO relationships: {before_stats['point_to_relationships']}")
        logger.info(f"  • HAVE_TO relationships: {before_stats['have_to_relationships']}")
        logger.info(f"  • Linked entities: {before_stats['linked_entities']}")
        
        if before_stats['curriculum_links'] == 0:
            logger.info("✅ No CurriculumLink data found. Nothing to clean up!")
            return {
                'before': before_stats,
                'deleted': {
                    'have_to_relationships': 0,
                    'point_to_relationships': 0,
                    'curriculum_link_nodes': 0
                },
                'after': before_stats,
                'success': True,
                'message': 'No data to clean up'
            }
        
        logger.info("\n🔄 CLEANUP PROCESS:")
        
        # Step 1: Delete HAVE_TO relationships first
        deleted_have_to = self.delete_have_to_relationships()
        
        # Step 2: Delete POINT_TO relationships
        deleted_point_to = self.delete_point_to_relationships()
        
        # Step 3: Delete CurriculumLink nodes (should be safe now)
        deleted_nodes = self.delete_curriculum_link_nodes()
        
        # Verify cleanup
        after_stats = self.verify_cleanup()
        
        logger.info("\n📊 AFTER CLEANUP:")
        logger.info(f"  • Remaining CurriculumLink nodes: {after_stats['remaining_curriculum_links']}")
        logger.info(f"  • Remaining POINT_TO relationships: {after_stats['remaining_point_to']}")
        logger.info(f"  • Remaining HAVE_TO relationships: {after_stats['remaining_have_to']}")
        
        # Check if cleanup was successful
        cleanup_success = (
            after_stats['remaining_curriculum_links'] == 0 and
            after_stats['remaining_point_to'] == 0 and
            after_stats['remaining_have_to'] == 0
        )
        
        if cleanup_success:
            logger.info("\n✅ CLEANUP COMPLETED SUCCESSFULLY!")
        else:
            logger.warning("\n⚠️  CLEANUP INCOMPLETE - Some items may remain")
        
        logger.info("\n📈 CLEANUP SUMMARY:")
        logger.info(f"  • HAVE_TO relationships deleted: {deleted_have_to}")
        logger.info(f"  • POINT_TO relationships deleted: {deleted_point_to}")
        logger.info(f"  • CurriculumLink nodes deleted: {deleted_nodes}")
        
        return {
            'before': before_stats,
            'deleted': {
                'have_to_relationships': deleted_have_to,
                'point_to_relationships': deleted_point_to,
                'curriculum_link_nodes': deleted_nodes
            },
            'after': after_stats,
            'success': cleanup_success,
            'message': 'Cleanup completed successfully' if cleanup_success else 'Cleanup incomplete'
        }


def main():
    """Main function"""
    # Database configuration
    uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "12345678")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    print("🧹 Curriculum Link Cleaner")
    print("This script will delete ALL CurriculumLink nodes and related relationships")
    print("="*70)
    
    # Confirmation prompt
    confirm = input("\n⚠️  Are you sure you want to proceed? (type 'yes' to confirm): ")
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled by user")
        return
    
    # Initialize cleaner
    cleaner = CurriculumLinkCleaner(uri, username, password, database)
    
    try:
        # Perform cleanup
        results = cleaner.perform_complete_cleanup()
        
        # Print final results
        print("\n" + "="*70)
        print("🎯 FINAL RESULTS")
        print("="*70)
        
        if results['success']:
            print("✅ Cleanup completed successfully!")
            print(f"   • Deleted {results['deleted']['curriculum_link_nodes']} CurriculumLink nodes")
            print(f"   • Deleted {results['deleted']['point_to_relationships']} POINT_TO relationships")
            print(f"   • Deleted {results['deleted']['have_to_relationships']} HAVE_TO relationships")
        else:
            print("⚠️  Cleanup incomplete!")
            print("   • Check the logs above for details")
            
        print("\n💡 NEXT STEPS:")
        print("   • You can now run curriculum_linker.py to recreate the links")
        print("   • Or run multi_document_linker.py for enhanced multi-document support")
        print("   • Check your Neo4j browser to verify the cleanup")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        print(f"\n❌ Error: {e}")
        
    finally:
        cleaner.close()


if __name__ == "__main__":
    import sys
    
    # Show help if requested
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
Curriculum Link Cleaner - Help
===============================

DESCRIPTION:
    This script removes all CurriculumLink-related data from Neo4j database:
    - Deletes HAVE_TO relationships (CurriculumLink → __Entity__)  
    - Deletes POINT_TO relationships (Course → CurriculumLink)
    - Deletes CurriculumLink nodes

USAGE:
    python cleanup_curriculum_links.py

ENVIRONMENT VARIABLES:
    NEO4J_URI      - Neo4j connection URI (default: neo4j://127.0.0.1:7687)
    NEO4J_USERNAME - Neo4j username (default: neo4j)
    NEO4J_PASSWORD - Neo4j password (default: 12345678)
    NEO4J_DATABASE - Neo4j database (default: neo4j)

SAFETY:
    - Script asks for confirmation before proceeding
    - Deletes relationships before nodes to avoid constraint violations
    - Provides detailed logging and verification
    - Does NOT affect Course framework nodes or extracted entities

EXAMPLES:
    # Basic cleanup
    python cleanup_curriculum_links.py
    
    # Show this help
    python cleanup_curriculum_links.py --help
    """)
        sys.exit(0)
    
    main()
