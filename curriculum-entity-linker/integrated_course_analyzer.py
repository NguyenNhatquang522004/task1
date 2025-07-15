"""
Integration script để combine Multi-Document Curriculum Linker với Cross-Document Relationships

Script này kết hợp 2 chức năng:
1. Multi-Document Curriculum Linker: Group documents theo course code
2. Cross-Document Relationships: Tạo relationships giữa entities từ different documents

Workflow:
1. Process multi-document courses với proper grouping
2. Analyze cross-document relationships within same course (high priority)
3. Analyze cross-document relationships across different courses (lower priority)
4. Create comprehensive course-based knowledge graph
"""

import sys
import os
import asyncio
import logging
from typing import Dict, List, Any

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cross-document-relationships'))

# Imports
try:
    from multi_document_linker import MultiDocumentCurriculumLinker
    from cross_document_relationships.integration import setup_cross_document_analysis, get_cross_document_analyzer
    from cross_document_relationships.config.settings import config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure both curriculum-entity-linker and cross-document-relationships are available")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegratedCourseAnalyzer:
    """Integrated analyzer combining curriculum linking and cross-document relationships"""
    
    def __init__(self, neo4j_uri: str, neo4j_username: str, neo4j_password: str, neo4j_database: str = "neo4j"):
        """Initialize with Neo4j connection"""
        self.neo4j_uri = neo4j_uri
        self.neo4j_username = neo4j_username  
        self.neo4j_password = neo4j_password
        self.neo4j_database = neo4j_database
        
        # Initialize curriculum linker
        self.curriculum_linker = MultiDocumentCurriculumLinker(
            neo4j_uri, neo4j_username, neo4j_password, neo4j_database
        )
        
        # Cross-document analyzer will be initialized later
        self.cross_doc_analyzer = None
        
    def close(self):
        """Close connections"""
        if self.curriculum_linker:
            self.curriculum_linker.close()
    
    async def initialize_cross_document_analyzer(self):
        """Initialize cross-document analyzer with Gemini"""
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                self.neo4j_uri, 
                auth=(self.neo4j_username, self.neo4j_password)
            )
            
            # Initialize with Gemini support
            from cross_document_relationships.src.core.analyzer import CrossDocumentAnalyzer
            self.cross_doc_analyzer = CrossDocumentAnalyzer(
                neo4j_driver=driver,
                use_gemini=True,
                similarity_threshold=0.7  # Lower threshold for same course
            )
            
            logger.info("Cross-document analyzer initialized with Gemini")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cross-document analyzer: {e}")
            return False
    
    async def process_step1_curriculum_linking(self) -> Dict[str, Any]:
        """Step 1: Process multi-document curriculum linking"""
        logger.info("="*60)
        logger.info("STEP 1: Multi-Document Curriculum Linking")
        logger.info("="*60)
        
        try:
            # Process curriculum linking
            stats = self.curriculum_linker.process_all_multi_document_courses()
            
            logger.info(f"Curriculum linking completed:")
            logger.info(f"  • Total courses: {stats['total_courses']}")
            logger.info(f"  • Multi-document courses: {stats['multi_document_courses']}")
            logger.info(f"  • Successfully processed: {stats['processed']}")
            logger.info(f"  • Failed: {stats['failed']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in curriculum linking: {e}")
            raise
    
    async def get_same_course_document_pairs(self) -> List[Dict[str, Any]]:
        """Get document pairs that belong to the same course for priority analysis"""
        query = """
        MATCH (c:Course)-[:HAS_MATERIALS]->(cc:CourseConsolidation)
        MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl1:DocumentLink)
        MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl2:DocumentLink)
        WHERE dl1 <> dl2
        WITH c.code as course_code, 
             collect({doc_id: dl1.document_id, filename: dl1.original_filename}) as docs1,
             collect({doc_id: dl2.document_id, filename: dl2.original_filename}) as docs2
        
        UNWIND docs1 as d1
        UNWIND docs2 as d2
        WHERE d1.doc_id < d2.doc_id  // Avoid duplicates
        
        MATCH (doc1:Document), (doc2:Document)
        WHERE ID(doc1) = d1.doc_id AND ID(doc2) = d2.doc_id
        
        RETURN course_code, 
               doc1.fileName as document1, 
               doc2.fileName as document2,
               d1.doc_id as doc1_id,
               d2.doc_id as doc2_id
        """
        
        try:
            with self.curriculum_linker.driver.session(database=self.neo4j_database) as session:
                result = session.run(query)
                
                same_course_pairs = []
                for record in result:
                    pair_info = {
                        'course_code': record['course_code'],
                        'document1': record['document1'],
                        'document2': record['document2'],
                        'doc1_id': record['doc1_id'],
                        'doc2_id': record['doc2_id'],
                        'priority': 'same_course'
                    }
                    same_course_pairs.append(pair_info)
                
                logger.info(f"Found {len(same_course_pairs)} same-course document pairs for priority analysis")
                return same_course_pairs
                
        except Exception as e:
            logger.error(f"Error getting same-course pairs: {e}")
            return []
    
    async def process_step2_same_course_relationships(self) -> Dict[str, Any]:
        """Step 2: Analyze relationships within same course (high priority)"""
        logger.info("="*60)
        logger.info("STEP 2: Same-Course Cross-Document Relationships")
        logger.info("="*60)
        
        if not self.cross_doc_analyzer:
            if not await self.initialize_cross_document_analyzer():
                raise Exception("Failed to initialize cross-document analyzer")
        
        try:
            # Get same-course document pairs
            same_course_pairs = await self.get_same_course_document_pairs()
            
            if not same_course_pairs:
                logger.info("No same-course document pairs found")
                return {"same_course_relationships": 0}
            
            # Analyze relationships với priority cho same course
            logger.info(f"Analyzing {len(same_course_pairs)} same-course document pairs...")
            
            # Use higher confidence cho same course vì relevance cao hơn
            result = await self.cross_doc_analyzer.analyze_all_relationships(
                batch_size=25,  # Smaller batches for better quality
                confidence_threshold=0.5,  # Lower threshold for same course
                max_pairs=len(same_course_pairs) * 10  # Allow more entity pairs per doc pair
            )
            
            logger.info(f"Same-course relationship analysis completed:")
            logger.info(f"  • Relationships created: {result.get('total_created', 0)}")
            logger.info(f"  • Processing time: {result.get('processing_time', 0):.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in same-course relationship analysis: {e}")
            raise
    
    async def process_step3_cross_course_relationships(self) -> Dict[str, Any]:
        """Step 3: Analyze relationships across different courses (lower priority)"""
        logger.info("="*60)
        logger.info("STEP 3: Cross-Course Relationships")
        logger.info("="*60)
        
        try:
            # Use standard cross-document analysis for different courses
            # Higher thresholds vì cross-course relationships ít relevant hơn
            result = await self.cross_doc_analyzer.analyze_all_relationships(
                batch_size=50,
                confidence_threshold=0.7,  # Higher threshold for cross-course
                max_pairs=500  # Limit cross-course analysis
            )
            
            logger.info(f"Cross-course relationship analysis completed:")
            logger.info(f"  • Relationships created: {result.get('total_created', 0)}")
            logger.info(f"  • Processing time: {result.get('processing_time', 0):.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in cross-course relationship analysis: {e}")
            raise
    
    async def generate_comprehensive_report(self, curriculum_stats: Dict, same_course_stats: Dict, cross_course_stats: Dict):
        """Generate comprehensive analysis report"""
        logger.info("="*60)
        logger.info("COMPREHENSIVE COURSE ANALYSIS REPORT")
        logger.info("="*60)
        
        # Get final statistics
        final_curriculum_stats = self.curriculum_linker.get_multi_document_statistics()
        
        # Get cross-document relationship stats
        cross_doc_stats_query = """
        MATCH ()-[r:CROSS_DOC_RELATIONSHIP]->()
        RETURN count(r) as total_cross_doc_relationships,
               avg(r.confidence) as avg_confidence,
               collect(DISTINCT r.type) as relationship_types
        """
        
        with self.curriculum_linker.driver.session(database=self.neo4j_database) as session:
            result = session.run(cross_doc_stats_query)
            record = result.single()
            cross_doc_final_stats = {
                'total_relationships': record['total_cross_doc_relationships'] if record else 0,
                'avg_confidence': record['avg_confidence'] if record else 0,
                'relationship_types': record['relationship_types'] if record else []
            }
        
        # Print report
        print("\n" + "="*80)
        print("🎓 INTEGRATED COURSE ANALYSIS FINAL REPORT")
        print("="*80)
        
        print("\n📚 CURRICULUM STRUCTURE:")
        print(f"  • Total courses processed: {curriculum_stats.get('total_courses', 0)}")
        print(f"  • Multi-document courses: {curriculum_stats.get('multi_document_courses', 0)}")
        print(f"  • Consolidation nodes created: {final_curriculum_stats.get('total_consolidation_nodes', 0)}")
        print(f"  • Document nodes created: {final_curriculum_stats.get('total_document_nodes', 0)}")
        print(f"  • Total entities linked: {final_curriculum_stats.get('total_entities_linked', 0)}")
        
        print("\n🔗 CROSS-DOCUMENT RELATIONSHIPS:")
        print(f"  • Same-course relationships: {same_course_stats.get('total_created', 0)}")
        print(f"  • Cross-course relationships: {cross_course_stats.get('total_created', 0)}")
        print(f"  • Total relationships: {cross_doc_final_stats['total_relationships']}")
        print(f"  • Average confidence: {cross_doc_final_stats['avg_confidence']:.3f}")
        print(f"  • Relationship types: {', '.join(cross_doc_final_stats['relationship_types'])}")
        
        print("\n⏱️  PERFORMANCE:")
        same_course_time = same_course_stats.get('processing_time', 0)
        cross_course_time = cross_course_stats.get('processing_time', 0)
        total_time = same_course_time + cross_course_time
        print(f"  • Same-course analysis: {same_course_time:.2f}s")
        print(f"  • Cross-course analysis: {cross_course_time:.2f}s") 
        print(f"  • Total processing time: {total_time:.2f}s")
        
        print("\n📊 PER-COURSE BREAKDOWN:")
        for course in final_curriculum_stats.get('courses', []):
            print(f"  {course['course_code']}: {course['document_count']} docs → {course['total_entities']} entities")
        
        print("\n🎯 NEXT STEPS:")
        print("  1. Use Neo4j Browser to explore the enhanced course structure")
        print("  2. Query same-course relationships for curriculum alignment")
        print("  3. Analyze cross-course relationships for interdisciplinary connections") 
        print("  4. Use the data for advanced course recommendation systems")
        
        print("\n✅ Integrated course analysis completed successfully!")

async def main():
    """Main function to run integrated course analysis"""
    # Database configuration
    neo4j_uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j") 
    neo4j_password = os.getenv("NEO4J_PASSWORD", "12345678")
    neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    print("🚀 Starting Integrated Course Analysis...")
    print("This combines multi-document curriculum linking with cross-document relationships")
    
    # Initialize analyzer
    analyzer = IntegratedCourseAnalyzer(neo4j_uri, neo4j_username, neo4j_password, neo4j_database)
    
    try:
        # Step 1: Curriculum linking
        curriculum_stats = await analyzer.process_step1_curriculum_linking()
        
        # Step 2: Same-course relationships (high priority)
        same_course_stats = await analyzer.process_step2_same_course_relationships()
        
        # Step 3: Cross-course relationships (lower priority) 
        cross_course_stats = await analyzer.process_step3_cross_course_relationships()
        
        # Generate comprehensive report
        await analyzer.generate_comprehensive_report(curriculum_stats, same_course_stats, cross_course_stats)
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise
    finally:
        analyzer.close()

if __name__ == "__main__":
    asyncio.run(main())
