"""
Main script for Folder Course Linker
Chạy toàn bộ quá trình tạo folder nodes v        print("🎉 PROCESS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 FINAL RESULTS:")
        print(f"   ✅ Course khung sườn: {validation['course_count']}")
        print(f"   ✅ Folder types: {validation['folder_types_count']} unique folder names")
        print(f"   ✅ Expected folder nodes: {validation['expected_folder_nodes']} (courses × folder types)")
        print(f"   ✅ Actual folder nodes: {validation['actual_folder_nodes']}")
        print(f"   ✅ Expected relationships: {validation['expected_relationships']}")
        print(f"   ✅ Actual relationships: {validation['actual_relationships']}")
        print(f"   ✅ Folder nodes status: {'🟢 CORRECT' if validation['folder_nodes_valid'] else '🔴 INCORRECT'}")
        print(f"   ✅ Relationships status: {'🟢 CORRECT' if validation['relationships_valid'] else '🔴 INCORRECT'}")
        print(f"   ✅ Overall status: {'🟢 PERFECT' if validation['is_valid'] else '🟡 CHECK NEEDED'}")
        
        # Hiển thị sample relationships
        print(f"\n🔗 Sample relationships (showing course-specific folder nodes):")
        details = builder.get_relationship_details(15)
        for i, detail in enumerate(details[:10], 1):
            print(f"   {i}. {detail['course_code']} → {detail['folder_name']} (course_code in node: check in Neo4j)")
        if len(details) > 10:
            print(f"   ... and {len(details)-10} more relationships")
        
        print(f"\n📋 Architecture achieved:")
        print(f"   Course CMP170 → 3 folder nodes with course_code='CMP170'")
        print(f"   Course CMP177 → 3 folder nodes with course_code='CMP177'")
        print(f"   Each course has its own set of folder nodes!")
"""
import logging
import sys
from data_analyzer import DataAnalyzer
from folder_node_creator import FolderNodeCreator
from relationship_builder import RelationshipBuilder
from config import PROJECT_NAME, VERSION, LOG_FORMAT, LOG_LEVEL

def setup_logging():
    """Thiết lập logging"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )

def print_header():
    """In header của project"""
    print("=" * 80)
    print(f"🚀 {PROJECT_NAME} v{VERSION}")
    print("=" * 80)
    print("Chức năng:")
    print("1. Phân tích dữ liệu hiện tại")
    print("2. Tạo folder nodes với label = folder_name")
    print("3. Tạo relationships POINT_TO từ Course khung sườn đến folder nodes")
    print("=" * 80)

def main():
    """Main function - Tự động chạy tất cả các bước"""
    setup_logging()
    print_header()
    
    # Initialize components
    analyzer = DataAnalyzer()
    creator = FolderNodeCreator()
    builder = RelationshipBuilder()
    
    try:
        print("\n🚀 STARTING AUTOMATIC PROCESS...")
        print("=" * 60)
        
        # Bước 1: Phân tích dữ liệu hiện tại
        print("\n📊 STEP 1: ANALYZING CURRENT DATA...")
        analyzer.print_analysis_report()
        
        # Bước 2: Tạo folder nodes
        print("\n📁 STEP 2: CREATING FOLDER NODES...")
        folder_names = creator.get_folder_names_from_documents()
        if not folder_names:
            print("❌ No folder names found in documents. Exiting...")
            return
        
        print(f"� Found {len(folder_names)} unique folder names: {folder_names}")
        
        # Kiểm tra nodes đã tồn tại
        existing_nodes = creator.check_existing_folder_nodes()
        if existing_nodes:
            print(f"⚠️ Found {len(existing_nodes)} existing folder nodes - cleaning up first...")
            creator.delete_all_folder_nodes()
        
        # Tạo folder nodes
        created_count, failed_count = creator.create_all_folder_nodes(folder_names)
        if failed_count > 0:
            print(f"⚠️ Warning: {failed_count} folder nodes failed to create")
        
        # Bước 3: Tạo relationships
        print("\n🔗 STEP 3: CREATING RELATIONSHIPS...")
        
        # Kiểm tra relationships đã tồn tại
        existing_rel_stats = builder.get_relationship_statistics()
        if existing_rel_stats['total_relationships'] > 0:
            print(f"⚠️ Found {existing_rel_stats['total_relationships']} existing relationships - cleaning up first...")
            builder.delete_all_relationships()
        
        # Tạo relationships
        course_count, folder_count, relationship_count = builder.create_course_to_folder_relationships()
        
        # Bước 4: Validation và báo cáo kết quả
        print("\n✅ STEP 4: VALIDATION AND RESULTS...")
        validation = builder.validate_relationships()
        
        print("\n" + "=" * 60)
        print("🎉 PROCESS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"� FINAL RESULTS:")
        print(f"   ✅ Course khung sườn: {validation['course_count']}")
        print(f"   ✅ Folder nodes created: {validation['folder_count']}")
        print(f"   ✅ Relationships created: {validation['actual_relationships']}")
        print(f"   ✅ Expected relationships: {validation['expected_relationships']}")
        print(f"   ✅ Status: {'🟢 PERFECT' if validation['is_valid'] else '🟡 CHECK NEEDED'}")
        
        # Hiển thị sample relationships
        print(f"\n🔗 Sample relationships:")
        details = builder.get_relationship_details(10)
        for i, detail in enumerate(details[:5], 1):
            print(f"   {i}. {detail['course_code']} → {detail['folder_name']}")
        if len(details) > 5:
            print(f"   ... and {len(details)-5} more relationships")
        
        print("\n🎯 You can now query your Neo4j database to see the results!")
        print("=" * 60)
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Close all connections
        analyzer.close()
        creator.close()
        builder.close()
        print("\n🔌 Database connections closed")

if __name__ == "__main__":
    main()
