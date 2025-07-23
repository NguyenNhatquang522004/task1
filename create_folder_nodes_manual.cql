// ===== TẠO FOLDER NODES TỪ DOCUMENTS VÀ LIÊN KẾT VỚI COURSE KHUNG SƯỜN (KHÔNG CẦN APOC) =====

// Bước 1: Xem trước các folder_name unique từ Documents
MATCH (d:Document)
WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
RETURN DISTINCT trim(d.folder_name) AS folder_name
ORDER BY folder_name;

// Bước 2: Tạo nodes cho từng folder_name cụ thể (thay thế bằng các folder_name thực tế)
// Ví dụ tạo node cho "đề cương"
MERGE (f1 {name: 'đề cương'})
SET f1:`đề cương`
SET f1.course_code = ''
WITH f1

// Ví dụ tạo node cho "giáo trình"  
MERGE (f2 {name: 'giáo trình'})
SET f2:`giáo trình`
SET f2.course_code = ''
WITH f2

// Ví dụ tạo node cho "tham khảo"
MERGE (f3 {name: 'tham khảo'})
SET f3:`tham khảo`
SET f3.course_code = ''
RETURN 'Tạo xong các folder nodes' AS message;

// Bước 3: Tạo relationships từ mỗi Course khung sườn đến tất cả folder nodes
MATCH (c:Course)
WHERE size(labels(c)) = 1  // Chỉ lấy Course khung sườn (1 label)

MATCH (f1 {name: 'đề cương'}), (f2 {name: 'giáo trình'}), (f3 {name: 'tham khảo'})

// Set course_code cho các folder nodes
SET f1.course_code = c.code,
    f2.course_code = c.code,
    f3.course_code = c.code

// Tạo relationships POINT_TO
MERGE (c)-[:POINT_TO]->(f1)
MERGE (c)-[:POINT_TO]->(f2)  
MERGE (c)-[:POINT_TO]->(f3)

RETURN 'Course ' + c.code + ' đã tạo relationships POINT_TO đến các folder nodes' AS message;

// ===== QUERIES KIỂM TRA =====

// 1. Kiểm tra Course khung sườn
MATCH (c:Course)
WHERE size(labels(c)) = 1
RETURN count(c) AS `Số Course khung sườn`, collect(c.code) AS `Codes`;

// 2. Kiểm tra folder nodes
MATCH (f)
WHERE f.name IN ['đề cương', 'giáo trình', 'tham khảo']
RETURN f.name AS `Folder name`, 
       head(labels(f)) AS `Label`, 
       f.course_code AS `Course code`;

// 3. Kiểm tra relationships
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1
RETURN c.code AS `Course code`,
       c.name AS `Course name`,
       f.name AS `Folder name`,
       type(r) AS `Relationship`
ORDER BY c.code, f.name;

// 4. Đếm tổng số relationships
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1
WITH count(DISTINCT c) AS course_count, 
     count(DISTINCT f) AS folder_count,
     count(r) AS total_relationships
RETURN course_count AS `Số Course khung sườn`,
       folder_count AS `Số Folder nodes`, 
       total_relationships AS `Tổng số relationships`,
       (course_count * folder_count) AS `Số relationships mong đợi`;

// ===== XÓA DỮ LIỆU NẾU CẦN RESET =====
// MATCH (c:Course)-[r:POINT_TO]->(f)
// WHERE size(labels(c)) = 1
// DELETE r;

// MATCH (f)
// WHERE f.name IN ['đề cương', 'giáo trình', 'tham khảo']
// DELETE f;
