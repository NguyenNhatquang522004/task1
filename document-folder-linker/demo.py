"""
Demo Script for Document-Folder Linker
Shows example usage and validates the system
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from data_analyzer import DataAnalyzer
from relationship_builder import RelationshipBuilder
from cleanup_tool import CleanupTool

def demo_analysis():
    """Demo data analysis functionality"""
    print("🔍 DEMO: Data Analysis")
    print("-" * 40)
    
    analyzer = DataAnalyzer()
    try:
        # Get document analysis
        doc_analysis = analyzer.analyze_documents()
        print(f"📄 Documents with properties: {doc_analysis['documents_with_properties']}")
        
        # Get folder analysis  
        folder_analysis = analyzer.analyze_folder_nodes()
        print(f"📁 Folder nodes: {folder_analysis['total_folder_nodes']}")
        
        # Find matches
        matches = analyzer.find_matching_pairs()
        print(f"🎯 Potential matches: {len(matches)}")
        
        if matches:
            print("📋 Sample matches:")
            for i, match in enumerate(matches[:3], 1):
                print(f"   {i}. {match['folder_label']}:{match['folder_name']} ({match['course_code']}) ↔ {match['document_count']} docs")
                
    finally:
        analyzer.close()

def demo_relationship_building():
    """Demo relationship building functionality"""
    print("\n🔗 DEMO: Relationship Building")
    print("-" * 40)
    
    builder = RelationshipBuilder()
    try:
        # Find matching entities
        matches = builder.find_matching_entities()
        print(f"🎯 Found {len(matches)} entity matches")
        
        if matches:
            print("📋 Sample entity matches:")
            for i, match in enumerate(matches[:3], 1):
                print(f"   {i}. {match['folder_label']}:{match['folder_name']} → Entity {match['entity_id']} from {match['document_name']}")
        
        # Note: We don't actually create relationships in demo mode
        print("💡 Run main.py to create actual relationships")
        
    finally:
        builder.close()

def demo_cleanup():
    """Demo cleanup functionality"""
    print("\n🧹 DEMO: Cleanup Operations")
    print("-" * 40)
    
    cleanup = CleanupTool()
    try:
        # Get statistics
        stats = cleanup.get_cleanup_statistics()
        print(f"🔗 Current HAVE relationships: {stats['relationships_count']}")
        print(f"📁 Folder combinations: {stats['total_folder_combinations']}")
        
        if stats['folder_types']:
            print("📂 Folder types with HAVE relationships:")
            for folder_type, combinations in stats['folder_types'].items():
                print(f"   • {folder_type}: {len(combinations)} combinations")
        
        print("💡 Run cleanup_tool.py to remove relationships")
        
    finally:
        cleanup.close()

def main():
    """Main demo function"""
    print("=" * 60)
    print("🚀 Document-Folder Linker - DEMO MODE")
    print("=" * 60)
    print("This demo shows the system capabilities without making changes")
    print("=" * 60)
    
    logging.basicConfig(level=logging.WARNING)  # Reduce noise in demo
    
    try:
        demo_analysis()
        demo_relationship_building() 
        demo_cleanup()
        
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETED")
        print("=" * 60)
        print("📋 Next steps:")
        print("   1. Run 'python main.py' to create HAVE relationships")
        print("   2. Run 'python cleanup_tool.py' to remove relationships")
        print("   3. Check Neo4j browser to see results")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
