// ===== TẠO FOLDER NODES TỪ DOCUMENTS VÀ LIÊN KẾT VỚI COURSE KHUNG SƯỜN =====

// Bước 1: Lấy tất cả folder_name unique từ các Document nodes
MATCH (d:Document)
WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
WITH COLLECT(DISTINCT trim(d.folder_name)) AS folder_names
UNWIND folder_names AS folder_name

// Bước 2: Tạo nodes với label = folder_name và properties name = folder_name (course_code để trống ban đầu)
CALL apoc.create.node([folder_name], {name: folder_name, course_code: ''}) YIELD node
RETURN 'Created folder node: ' + folder_name AS message;

// Bước 3: Lấy tất cả Course khung sườn (chỉ có 1 label là Course)
MATCH (c:Course)
WHERE size(labels(c)) = 1  // Chỉ lấy node có đúng 1 label là Course
WITH COLLECT(c) AS courses

// Bước 4: Lấy tất cả folder_name nodes đã tạo
MATCH (f)
WHERE any(label IN labels(f) WHERE label IN ['đề cương', 'giáo trình', 'tham khảo', 'de cuong', 'giao trinh', 'tham khao'])
WITH courses, COLLECT(f) AS folder_nodes

// Bước 5: Tạo relationship POINT_TO từ mỗi Course đến tất cả folder nodes
UNWIND courses AS course
UNWIND folder_nodes AS folder_node
WITH course, folder_node
// Set course_code cho folder node bằng code của course
SET folder_node.course_code = course.code
// Tạo relationship POINT_TO
MERGE (course)-[:POINT_TO]->(folder_node)
RETURN 'Created relationship: ' + course.code + ' POINT_TO ' + folder_node.name AS message;

// ===== QUERY KIỂM TRA KẾT QUẢ =====

// Kiểm tra các Course khung sườn (chỉ có 1 label)
MATCH (c:Course)
WHERE size(labels(c)) = 1
RETURN 'Course khung sườn: ' + c.code + ' - ' + c.name AS course_info
ORDER BY c.code;

// Kiểm tra các folder nodes đã tạo
MATCH (f)
WHERE any(label IN labels(f) WHERE label IN ['đề cương', 'giáo trình', 'tham khảo', 'de cuong', 'giao trinh', 'tham khao'])
RETURN 'Folder node: ' + head(labels(f)) + ' - name: ' + f.name + ' - course_code: ' + f.course_code AS folder_info;

// Kiểm tra relationships POINT_TO
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1
RETURN 'Relationship: ' + c.code + ' (' + c.name + ') POINT_TO ' + f.name + ' (label: ' + head(labels(f)) + ')' AS relationship_info
ORDER BY c.code, f.name;

// ===== QUERY ĐẾM SỐ LƯỢNG =====
MATCH (c:Course)
WHERE size(labels(c)) = 1
WITH COUNT(c) AS course_count

MATCH (f)
WHERE any(label IN labels(f) WHERE label IN ['đề cương', 'giáo trình', 'tham khảo', 'de cuong', 'giao trinh', 'tham khao'])
WITH course_count, COUNT(f) AS folder_count

MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1
WITH course_count, folder_count, COUNT(r) AS relationship_count

RETURN 
  course_count AS `Số Course khung sườn`,
  folder_count AS `Số Folder nodes`,
  relationship_count AS `Số Relationships POINT_TO`,
  (course_count * folder_count) AS `Số relationships mong đợi (nếu mỗi course trỏ đến tất cả folder)`;
