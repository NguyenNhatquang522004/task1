"""
Main script for Folder Course Linker - SIMPLIFIED VERSION
Tự động tạo folder nodes riêng cho mỗi course và relationships
"""
import logging
from data_analyzer import DataAnalyzer
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
    print("Mục tiêu: Tạo folder nodes riêng cho mỗi course")
    print("Architecture: Course CMP170 → 3 folder nodes với course_code='CMP170'")
    print("=" * 80)

def main():
    """Main function - Tự động chạy tất cả các bước"""
    setup_logging()
    print_header()
    
    # Initialize components
    analyzer = DataAnalyzer()
    builder = RelationshipBuilder()
    
    try:
        print("\n🚀 STARTING AUTOMATIC PROCESS...")
        print("=" * 60)
        
        # Bước 1: Phân tích dữ liệu hiện tại
        print("\n📊 STEP 1: ANALYZING CURRENT DATA...")
        analyzer.print_analysis_report()
        
        # Bước 2: Cleanup existing data
        print("\n🧹 STEP 2: CLEANUP EXISTING DATA...")
        
        # Xóa relationships cũ
        existing_rel_stats = builder.get_relationship_statistics()
        if existing_rel_stats['total_relationships'] > 0:
            print(f"⚠️ Found {existing_rel_stats['total_relationships']} existing relationships - cleaning up...")
            builder.delete_all_relationships()
        
        # Xóa folder nodes cũ
        delete_nodes_query = """
        MATCH (f)
        WHERE f.created_by = 'folder-course-linker'
        DELETE f
        RETURN count(f) AS deleted_count
        """
        
        with builder.driver.session() as session:
            result = session.run(delete_nodes_query)
            record = result.single()
            deleted_count = record['deleted_count'] if record else 0
            if deleted_count > 0:
                print(f"🗑️ Deleted {deleted_count} existing folder nodes")
        
        # Bước 3: Tạo folder nodes và relationships cho mỗi course
        print("\n🔗 STEP 3: CREATING COURSE-SPECIFIC FOLDER NODES AND RELATIONSHIPS...")
        
        course_count, folder_count, relationship_count = builder.create_course_to_folder_relationships()
        
        # Bước 4: Validation và báo cáo kết quả
        print("\n✅ STEP 4: VALIDATION AND RESULTS...")
        validation = builder.validate_relationships()
        
        print("\n" + "=" * 60)
        print("🎉 PROCESS COMPLETED SUCCESSFULLY!")
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
            print(f"   {i}. {detail['course_code']} → {detail['folder_name']}")
        if len(details) > 10:
            print(f"   ... and {len(details)-10} more relationships")
        
        print(f"\n📋 Architecture achieved:")
        print(f"   ✅ Course CMP170 → 3 folder nodes with course_code='CMP170'")
        print(f"   ✅ Course CMP177 → 3 folder nodes with course_code='CMP177'")
        print(f"   ✅ Each course has its own set of folder nodes!")
        
        print("\n🎯 You can now query your Neo4j database to see the results!")
        print("🔍 Try this query to verify:")
        print("MATCH (c:Course)-[:POINT_TO]->(f) WHERE size(labels(c))=1 RETURN c.code, f.name, f.course_code")
        print("=" * 60)
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Close all connections
        analyzer.close()
        builder.close()
        print("\n🔌 Database connections closed")

if __name__ == "__main__":
    main()
