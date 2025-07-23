"""
Auto Cleanup Script for Folder Course Linker
Tự động xóa tất cả folder nodes và relationships
"""
import logging
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
    print(f"🗑️ {PROJECT_NAME} - AUTO CLEANUP TOOL")
    print("=" * 80)
    print("Tự động xóa tất cả folder nodes và relationships")
    print("=" * 80)

def safe_run_query(session, query, description="query"):
    """Chạy query an toàn với xử lý lỗi"""
    try:
        result = session.run(query)
        record = result.single()
        return record['deleted_count'] if record and 'deleted_count' in record else 0
    except Exception as e:
        logging.error(f"Error running {description}: {e}")
        return 0

def get_statistics(builder):
    """Lấy thống kê hiện tại"""
    stats = {'folder_nodes': 0, 'relationships': 0}
    
    try:
        with builder.driver.session() as session:
            # Đếm folder nodes
            folder_query = """
            MATCH (f)
            WHERE f.created_by = 'folder-course-linker'
            RETURN count(f) AS count
            """
            result = session.run(folder_query)
            record = result.single()
            stats['folder_nodes'] = record['count'] if record else 0
            
            # Đếm relationships
            rel_query = """
            MATCH (c:Course)-[r:POINT_TO]->(f)
            WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
            RETURN count(r) AS count
            """
            result = session.run(rel_query)
            record = result.single()
            stats['relationships'] = record['count'] if record else 0
            
    except Exception as e:
        logging.error(f"Error getting statistics: {e}")
    
    return stats

def cleanup_all_data(builder):
    """Xóa tất cả dữ liệu"""
    deleted_rels = 0
    deleted_nodes = 0
    
    try:
        with builder.driver.session() as session:
            # Bước 1: Xóa relationships trước
            rel_query = """
            MATCH (c:Course)-[r:POINT_TO]->(f)
            WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
            DELETE r
            RETURN count(r) AS deleted_count
            """
            deleted_rels = safe_run_query(session, rel_query, "relationships deletion")
            
            # Bước 2: Xóa folder nodes
            nodes_query = """
            MATCH (f)
            WHERE f.created_by = 'folder-course-linker'
            DELETE f
            RETURN count(f) AS deleted_count
            """
            deleted_nodes = safe_run_query(session, nodes_query, "nodes deletion")
            
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")
    
    return deleted_rels, deleted_nodes

def main():
    """Main function - Tự động cleanup"""
    setup_logging()
    print_header()
    
    builder = RelationshipBuilder()
    
    try:
        print("\n📊 STEP 1: CHECKING CURRENT DATA...")
        
        # Lấy thống kê hiện tại
        stats = get_statistics(builder)
        
        print(f"   - Folder nodes: {stats['folder_nodes']}")
        print(f"   - Relationships: {stats['relationships']}")
        
        if stats['folder_nodes'] == 0 and stats['relationships'] == 0:
            print("\n✅ Database is already clean! Nothing to delete.")
            return
        
        print(f"\n🗑️ STEP 2: AUTO CLEANUP...")
        print(f"   - Will delete {stats['relationships']} relationships")
        print(f"   - Will delete {stats['folder_nodes']} folder nodes")
        
        # Thực hiện cleanup
        deleted_rels, deleted_nodes = cleanup_all_data(builder)
        
        print(f"\n✅ STEP 3: CLEANUP COMPLETED!")
        print(f"   - Deleted {deleted_rels} relationships")
        print(f"   - Deleted {deleted_nodes} folder nodes")
        
        # Kiểm tra lại
        final_stats = get_statistics(builder)
        
        print(f"\n🔍 STEP 4: VERIFICATION...")
        print(f"   - Remaining folder nodes: {final_stats['folder_nodes']}")
        print(f"   - Remaining relationships: {final_stats['relationships']}")
        
        is_clean = (final_stats['folder_nodes'] == 0 and final_stats['relationships'] == 0)
        print(f"   - Status: {'✅ CLEAN' if is_clean else '⚠️ INCOMPLETE'}")
        
        print("\n" + "=" * 60)
        if is_clean:
            print("🎉 CLEANUP COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️ CLEANUP INCOMPLETE - Some data may remain")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        logging.error(f"Cleanup error: {e}", exc_info=True)
    finally:
        builder.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()
