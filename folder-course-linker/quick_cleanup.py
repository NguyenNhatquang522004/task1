"""
Quick Cleanup Script - Simple version
Xóa nhanh tất cả folder nodes và relationships
"""

def print_cleanup_queries():
    """In ra các Cypher queries để cleanup"""
    print("=" * 60)
    print("🧹 FOLDER COURSE LINKER - CLEANUP QUERIES")
    print("=" * 60)
    
    print("\n🔍 1. KIỂM TRA DỮ LIỆU HIỆN TẠI:")
    print("// Đếm folder nodes")
    print("""MATCH (f)
WHERE f.created_by = 'folder-course-linker'
RETURN count(f) AS folder_nodes_count, 
       collect(DISTINCT head(labels(f))) AS folder_types;""")
    
    print("\n// Đếm relationships")
    print("""MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
RETURN count(r) AS relationships_count;""")
    
    print("\n🗑️ 2. XÓA TẤT CẢ (CHẠY LẦN LƯỢT):")
    print("// Bước 1: Xóa relationships trước")
    print("""MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
DELETE r
RETURN count(r) AS deleted_relationships;""")
    
    print("\n// Bước 2: Xóa folder nodes")
    print("""MATCH (f)
WHERE f.created_by = 'folder-course-linker'
DELETE f
RETURN count(f) AS deleted_nodes;""")
    
    print("\n🔍 3. KIỂM TRA SAU KHI XÓA:")
    print("""MATCH (f)
WHERE f.created_by = 'folder-course-linker'
WITH count(f) AS nodes_count
MATCH (c:Course)-[r:POINT_TO]->(f2)
WHERE size(labels(c)) = 1 AND f2.created_by = 'folder-course-linker'
WITH nodes_count, count(r) AS rels_count
RETURN nodes_count AS remaining_nodes,
       rels_count AS remaining_relationships,
       CASE 
         WHEN nodes_count = 0 AND rels_count = 0 THEN '✅ CLEAN'
         ELSE '⚠️ INCOMPLETE'
       END AS cleanup_status;""")
    
    print("\n" + "=" * 60)
    print("📋 HƯỚNG DẪN:")
    print("1. Copy và chạy query kiểm tra đầu tiên trong Neo4j Browser")
    print("2. Nếu có dữ liệu, chạy 2 query xóa theo thứ tự")
    print("3. Chạy query kiểm tra cuối để xác nhận")
    print("=" * 60)

def print_selective_cleanup():
    """In ra queries để xóa chọn lọc"""
    print("\n🎯 XÓA CHỌN LỌC:")
    
    print("\n// Xóa chỉ folder nodes 'đề cương':")
    print("""MATCH (c:Course)-[r:POINT_TO]->(f:`đề cương`)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
DELETE r, f
RETURN count(f) AS deleted_de_cuong_nodes;""")
    
    print("\n// Xóa chỉ folder nodes 'giáo trình':")
    print("""MATCH (c:Course)-[r:POINT_TO]->(f:`giáo trình`)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
DELETE r, f
RETURN count(f) AS deleted_giao_trinh_nodes;""")
    
    print("\n// Xóa chỉ folder nodes 'tham khảo':")
    print("""MATCH (c:Course)-[r:POINT_TO]->(f:`tham khảo`)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
DELETE r, f
RETURN count(f) AS deleted_tham_khao_nodes;""")

def main():
    """Main function"""
    print_cleanup_queries()
    
    print("\n🤔 Bạn muốn xem thêm queries xóa chọn lọc không? (y/N): ", end="")
    try:
        choice = input().strip().lower()
        if choice == 'y':
            print_selective_cleanup()
    except:
        pass
    
    print("\n✅ Đã xuất tất cả cleanup queries!")
    print("💡 Tip: Bạn có thể chạy 'python cleanup_tool.py' để cleanup tự động với menu")

if __name__ == "__main__":
    main()
