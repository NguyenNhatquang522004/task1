// ===== TẠO RELATIONSHIPS POINT_TO =====

// Bước 1: Lấy tất cả Course khung sườn và folder nodes
MATCH (c:Course)
WHERE size(labels(c)) = 1  // Chỉ lấy Course khung sườn

MATCH (f)
WHERE any(label IN labels(f) WHERE label IN ['đề cương', 'giáo trình', 'tham khảo'])

// Bước 2: Set course_code cho folder nodes và tạo relationships
WITH c, f
SET f.course_code = c.code
MERGE (c)-[:POINT_TO]->(f)
RETURN 'Course ' + c.code + ' POINT_TO ' + f.name AS relationship_created;

// ===== KIỂM TRA RELATIONSHIPS ĐÃ TẠO =====

// Đếm số lượng relationships
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1
WITH count(DISTINCT c) AS course_count,
     count(DISTINCT f) AS folder_count,
     count(r) AS total_relationships
RETURN course_count AS `Số Course khung sườn`,
       folder_count AS `Số Folder nodes`,
       total_relationships AS `Tổng số relationships`,
       (course_count * folder_count) AS `Số relationships mong đợi`;

// Chi tiết relationships
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1
RETURN c.code AS course_code,
       c.name AS course_name,
       f.name AS folder_name,
       head(labels(f)) AS folder_label,
       type(r) AS relationship_type
ORDER BY c.code, f.name
LIMIT 50;

// ===== XÓA RELATIONSHIPS NẾU CẦN RESET =====
// MATCH (c:Course)-[r:POINT_TO]->(f)
// WHERE size(labels(c)) = 1
// DELETE r;

// ===== XÓA FOLDER NODES NẾU CẦN RESET =====
// MATCH (f)
// WHERE f.created_by = 'folder-course-linker'
// DELETE f;
