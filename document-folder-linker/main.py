"""
Main Script for Document-Folder Linker
Automatically creates HAVE relationships between folder nodes and document entities
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from data_analyzer import DataAnalyzer
from relationship_builder import RelationshipBuilder
from config import LOG_LEVEL, LOG_FORMAT

def setup_logging():
    """Setup logging configuration with UTF-8 encoding"""
    import sys
    
    # Create file handler with UTF-8 encoding
    file_handler = logging.FileHandler('document_folder_linker.log', encoding='utf-8')
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # Create console handler with UTF-8 encoding (if possible)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        handlers=[console_handler, file_handler]
    )
    
    # Set console encoding to UTF-8 if possible
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass  # Ignore if reconfigure is not available

def main():
    """Main function - Automatically create folder-document relationships"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        print("=" * 80)
        print("🚀 Document-Folder Linker v1.0.0")
        print("=" * 80)
        print("Mục tiêu: Tạo relationships HAVE giữa folder nodes và document entities")
        print("Điều kiện: folder.name == document.folder_name AND folder.course_code == document.course_code")
        print("Relationship: (folder)-[:HAVE]->(entity_of_document)")
        print("=" * 80)
        
        print("\n🚀 STARTING AUTOMATIC PROCESS...")
        
        # Step 1: Data Analysis
        print("\n" + "=" * 60)
        print("📊 STEP 1: ANALYZING CURRENT DATA...")
        print("=" * 60)
        
        analyzer = DataAnalyzer()
        try:
            analysis_report = analyzer.generate_analysis_report()
            print(analysis_report)
        finally:
            analyzer.close()
        
        # Step 2: Relationship Building
        print("\n" + "=" * 60)
        print("🔗 STEP 2: BUILDING FOLDER-ENTITY RELATIONSHIPS...")
        print("=" * 60)
        
        builder = RelationshipBuilder()
        try:
            result = builder.build_all_relationships()
            
            print(f"\n✅ STEP 3: RESULTS SUMMARY...")
            print("=" * 60)
            print(f"🎉 PROCESS COMPLETED!")
            print("=" * 60)
            print(f"📊 FINAL RESULTS:")
            print(f"   ✅ Cleaned up relationships: {result['cleanup_count']}")
            print(f"   ✅ Created new relationships: {result['created_count']}")
            print(f"   ✅ Total HAVE relationships: {result['total_relationships']}")
            print(f"   ✅ Expected relationships: {result['expected_count']}")
            print(f"   ✅ Status: {'🟢 SUCCESS' if result['status'] == 'SUCCESS' else '🔴 FAILED'}")
            
            if result['sample_relationships']:
                print(f"\n🔗 Sample relationships created:")
                for i, rel in enumerate(result['sample_relationships'][:10], 1):
                    print(f"   {i}. {rel['folder_label']}:{rel['folder_name']} ({rel['folder_course_code']}) -[:HAVE]-> {rel['entity_labels']} ({rel['entity_id']})")
            
            # Validation
            success = (result['created_count'] == result['expected_count'] and 
                      result['total_relationships'] == result['expected_count'])
            
            print(f"\n💭 VALIDATION:")
            print(f"   - Expected vs Created: {'✅ MATCH' if result['created_count'] == result['expected_count'] else '❌ MISMATCH'}")
            print(f"   - Database consistency: {'✅ CONSISTENT' if result['total_relationships'] == result['expected_count'] else '❌ INCONSISTENT'}")
            print(f"   - Overall status: {'🟢 PERFECT' if success else '⚠️ NEEDS REVIEW'}")
            
            print("\n🎯 You can now query your Neo4j database to see the HAVE relationships!")
            print("🔍 Try this query to verify:")
            print("MATCH (f)-[:HAVE]->(e) WHERE f.name IS NOT NULL AND f.course_code IS NOT NULL RETURN f.name, f.course_code, labels(e), e.id LIMIT 20")
            
        finally:
            builder.close()
            
        print("\n" + "=" * 80)
        print("🔌 Database connections closed")
        
    except Exception as e:
        logger.error(f"❌ Process failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("📋 Check the log file for detailed error information.")
        sys.exit(1)

if __name__ == "__main__":
    main()
