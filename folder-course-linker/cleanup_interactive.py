"""
Cleanup Tool Interactive - Version có menu
Xóa tất cả folder nodes và relationships được tạo bởi tool với menu lựa chọn
"""
import logging
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE, COURSE_TO_FOLDER_RELATIONSHIP

class CleanupTool:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        self.logger = logging.getLogger(__name__)
    
    def close(self):
        """Đóng kết nối database"""
        self.driver.close()
    
    def get_cleanup_statistics(self):
        """Lấy thống kê trước khi cleanup"""
        queries = {
            'folder_nodes': """
                MATCH (f)
                WHERE f.created_by = 'folder-course-linker'
                RETURN count(f) AS count
            """,
            'relationships': f"""
                MATCH (c:Course)-[r:{COURSE_TO_FOLDER_RELATIONSHIP}]->(f)
                WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
                RETURN count(r) AS count
            """,
            'folder_types': """
                MATCH (f)
                WHERE f.created_by = 'folder-course-linker'
                RETURN DISTINCT head(labels(f)) AS folder_type
                ORDER BY folder_type
            """
        }
        
        stats = {}
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Đếm folder nodes
            result = session.run(queries['folder_nodes'])
            stats['folder_nodes_count'] = result.single()['count']
            
            # Đếm relationships
            result = session.run(queries['relationships'])
            stats['relationships_count'] = result.single()['count']
            
            # Lấy folder types
            result = session.run(queries['folder_types'])
            stats['folder_types'] = [record['folder_type'] for record in result]
        
        return stats
    
    def delete_all_relationships(self):
        """Xóa tất cả relationships POINT_TO"""
        query = f"""
        MATCH (c:Course)-[r:{COURSE_TO_FOLDER_RELATIONSHIP}]->(f)
        WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
        DELETE r
        RETURN count(r) AS deleted_count
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            deleted_count = result.single()['deleted_count']
            self.logger.info(f"🗑️ Deleted {deleted_count} relationships")
            return deleted_count
    
    def delete_all_folder_nodes(self):
        """Xóa tất cả folder nodes được tạo bởi tool"""
        query = """
        MATCH (f)
        WHERE f.created_by = 'folder-course-linker'
        DELETE f
        RETURN count(f) AS deleted_count
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            deleted_count = result.single()['deleted_count']
            self.logger.info(f"🗑️ Deleted {deleted_count} folder nodes")
            return deleted_count
    
    def delete_folder_nodes_by_type(self, folder_type):
        """Xóa folder nodes theo loại cụ thể"""
        query = f"""
        MATCH (f:`{folder_type}`)
        WHERE f.created_by = 'folder-course-linker'
        DELETE f
        RETURN count(f) AS deleted_count
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            deleted_count = result.single()['deleted_count']
            self.logger.info(f"🗑️ Deleted {deleted_count} '{folder_type}' nodes")
            return deleted_count
    
    def cleanup_all(self):
        """Xóa tất cả dữ liệu (relationships + nodes)"""
        print("🧹 Starting complete cleanup...")
        
        # Bước 1: Xóa relationships trước
        print("Step 1: Deleting relationships...")
        deleted_rels = self.delete_all_relationships()
        
        # Bước 2: Xóa folder nodes
        print("Step 2: Deleting folder nodes...")
        deleted_nodes = self.delete_all_folder_nodes()
        
        return deleted_rels, deleted_nodes
    
    def cleanup_selective(self, folder_types_to_delete):
        """Xóa chọn lọc theo folder types"""
        print(f"🧹 Starting selective cleanup for: {folder_types_to_delete}")
        
        total_deleted_rels = 0
        total_deleted_nodes = 0
        
        for folder_type in folder_types_to_delete:
            # Xóa relationships cho folder type này
            rel_query = f"""
            MATCH (c:Course)-[r:{COURSE_TO_FOLDER_RELATIONSHIP}]->(f:`{folder_type}`)
            WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
            DELETE r
            RETURN count(r) AS deleted_count
            """
            
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(rel_query)
                deleted_rels = result.single()['deleted_count']
                total_deleted_rels += deleted_rels
                print(f"  - Deleted {deleted_rels} relationships for '{folder_type}'")
            
            # Xóa nodes cho folder type này
            deleted_nodes = self.delete_folder_nodes_by_type(folder_type)
            total_deleted_nodes += deleted_nodes
            print(f"  - Deleted {deleted_nodes} '{folder_type}' nodes")
        
        return total_deleted_rels, total_deleted_nodes
    
    def verify_cleanup(self):
        """Kiểm tra cleanup đã hoàn tất chưa"""
        stats = self.get_cleanup_statistics()
        
        is_clean = (stats['folder_nodes_count'] == 0 and 
                   stats['relationships_count'] == 0)
        
        print(f"\n🔍 Cleanup Verification:")
        print(f"   - Remaining folder nodes: {stats['folder_nodes_count']}")
        print(f"   - Remaining relationships: {stats['relationships_count']}")
        print(f"   - Status: {'✅ CLEAN' if is_clean else '⚠️ INCOMPLETE'}")
        
        return is_clean

def main():
    """Main function với menu interactive"""
    logging.basicConfig(level=logging.INFO)
    cleanup = CleanupTool()
    
    try:
        print("=" * 60)
        print("🧹 FOLDER COURSE LINKER - INTERACTIVE CLEANUP TOOL")
        print("=" * 60)
        
        # Hiển thị thống kê hiện tại
        print("\n📊 Current Statistics:")
        stats = cleanup.get_cleanup_statistics()
        print(f"   - Folder nodes: {stats['folder_nodes_count']}")
        print(f"   - Relationships: {stats['relationships_count']}")
        print(f"   - Folder types: {stats['folder_types']}")
        
        if stats['folder_nodes_count'] == 0 and stats['relationships_count'] == 0:
            print("\n✅ Database is already clean!")
            return
        
        print("\n🗑️ Cleanup Options:")
        print("1. Delete ALL (relationships + folder nodes)")
        print("2. Delete only relationships")
        print("3. Delete only folder nodes")
        print("4. Delete specific folder types")
        print("0. Cancel")
        
        choice = input("\nSelect option (0-4): ").strip()
        
        if choice == "0":
            print("❌ Cleanup cancelled")
            return
        elif choice == "1":
            confirm = input("⚠️ Are you sure you want to delete ALL data? (yes/NO): ")
            if confirm.lower() == 'yes':
                deleted_rels, deleted_nodes = cleanup.cleanup_all()
                print(f"\n✅ Cleanup completed:")
                print(f"   - Deleted {deleted_rels} relationships")
                print(f"   - Deleted {deleted_nodes} folder nodes")
                cleanup.verify_cleanup()
            else:
                print("❌ Cleanup cancelled")
        elif choice == "2":
            deleted_rels = cleanup.delete_all_relationships()
            print(f"✅ Deleted {deleted_rels} relationships")
        elif choice == "3":
            deleted_nodes = cleanup.delete_all_folder_nodes()
            print(f"✅ Deleted {deleted_nodes} folder nodes")
        elif choice == "4":
            if stats['folder_types']:
                print(f"\nAvailable folder types: {stats['folder_types']}")
                types_input = input("Enter folder types to delete (comma-separated): ")
                types_to_delete = [t.strip() for t in types_input.split(',') if t.strip()]
                
                if types_to_delete:
                    deleted_rels, deleted_nodes = cleanup.cleanup_selective(types_to_delete)
                    print(f"\n✅ Selective cleanup completed:")
                    print(f"   - Deleted {deleted_rels} relationships")
                    print(f"   - Deleted {deleted_nodes} folder nodes")
                else:
                    print("❌ No valid folder types provided")
            else:
                print("❌ No folder types found")
        else:
            print("❌ Invalid option")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Cleanup error: {e}", exc_info=True)
    finally:
        cleanup.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()
