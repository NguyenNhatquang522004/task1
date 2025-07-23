// ===== CLEANUP QUERIES FOR FOLDER COURSE LINKER =====

// 🔍 KIỂM TRA DỮ LIỆU HIỆN TẠI
// Đếm folder nodes
MATCH (f)
WHERE f.created_by = 'folder-course-linker'
RETURN count(f) AS folder_nodes_count, 
       collect(DISTINCT head(labels(f))) AS folder_types;

// Đếm relationships
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
RETURN count(r) AS relationships_count;

// Xem chi tiết folder nodes
MATCH (f)
WHERE f.created_by = 'folder-course-linker'
RETURN head(labels(f)) AS folder_type, 
       f.name AS name, 
       f.course_code AS course_code,
       count(*) AS count
ORDER BY folder_type, course_code;

// ===== CLEANUP QUERIES =====

// 🗑️ OPTION 1: XÓA TẤT CẢ (RELATIONSHIPS + NODES)
// Bước 1: Xóa relationships trước
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
DELETE r
RETURN count(r) AS deleted_relationships;

// Bước 2: Xóa folder nodes
MATCH (f)
WHERE f.created_by = 'folder-course-linker'
DELETE f
RETURN count(f) AS deleted_nodes;

// 🗑️ OPTION 2: CHỈ XÓA RELATIONSHIPS
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
DELETE r
RETURN count(r) AS deleted_relationships;

// 🗑️ OPTION 3: CHỈ XÓA FOLDER NODES
MATCH (f)
WHERE f.created_by = 'folder-course-linker'
DELETE f
RETURN count(f) AS deleted_nodes;

// 🗑️ OPTION 4: XÓA THEO FOLDER TYPE CỤ THỂ
// Xóa chỉ folder nodes "đề cương"
MATCH (f:`đề cương`)
WHERE f.created_by = 'folder-course-linker'
DELETE f
RETURN count(f) AS deleted_de_cuong_nodes;

// Xóa chỉ folder nodes "giáo trình"
MATCH (f:`giáo trình`)
WHERE f.created_by = 'folder-course-linker'
DELETE f
RETURN count(f) AS deleted_giao_trinh_nodes;

// Xóa chỉ folder nodes "tham khảo"
MATCH (f:`tham khảo`)
WHERE f.created_by = 'folder-course-linker'
DELETE f
RETURN count(f) AS deleted_tham_khao_nodes;

// 🗑️ OPTION 5: XÓA THEO COURSE CODE CỤ THỂ
// Xóa folder nodes của course cụ thể (ví dụ CMP170)
MATCH (c:Course {code: 'CMP170'})-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
DELETE r, f
RETURN count(f) AS deleted_nodes_for_CMP170;

// ===== VERIFICATION QUERIES =====

// 🔍 KIỂM TRA SAU KHI CLEANUP
// Đảm bảo không còn folder nodes nào
MATCH (f)
WHERE f.created_by = 'folder-course-linker'
RETURN count(f) AS remaining_folder_nodes;

// Đảm bảo không còn relationships nào
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
RETURN count(r) AS remaining_relationships;

// Kiểm tra tổng quan
MATCH (f)
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
       END AS cleanup_status;

// ===== BACKUP QUERIES (TRƯỚC KHI XÓA) =====

// Export dữ liệu trước khi xóa (để backup)
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
RETURN c.code AS course_code,
       c.name AS course_name,
       head(labels(f)) AS folder_type,
       f.name AS folder_name,
       f.course_code AS folder_course_code,
       f.created_at AS created_at
ORDER BY c.code, folder_type;
