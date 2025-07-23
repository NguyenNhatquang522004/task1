// ===== TẠO FOLDER NODES =====

// Bước 1: Lấy tất cả folder_name unique từ Documents
MATCH (d:Document)
WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
WITH COLLECT(DISTINCT trim(d.folder_name)) AS folder_names
UNWIND folder_names AS folder_name

// Bước 2: Tạo nodes với label = folder_name
CALL apoc.create.node([folder_name], {
    name: folder_name,
    course_code: '',
    created_at: datetime(),
    created_by: 'folder-course-linker'
}) YIELD node
RETURN 'Created folder node: ' + folder_name AS message;

// ===== TẠO FOLDER NODES (PHIÊN BẢN KHÔNG CẦN APOC) =====

// Lệnh này cần chạy riêng cho từng folder_name cụ thể
// Thay thế 'FOLDER_NAME_HERE' bằng tên folder thực tế

MERGE (f:FOLDER_NAME_HERE {name: 'FOLDER_NAME_HERE'})
SET f.course_code = '',
    f.created_at = datetime(),
    f.created_by = 'folder-course-linker'
RETURN 'Created folder node: ' + f.name AS message;

// ===== VÍ DỤ TẠO CÁC FOLDER NODES PHỔ BIẾN =====

// Tạo node cho "đề cương"
MERGE (f1:`đề cương` {name: 'đề cương'})
SET f1.course_code = '',
    f1.created_at = datetime(),
    f1.created_by = 'folder-course-linker';

// Tạo node cho "giáo trình"
MERGE (f2:`giáo trình` {name: 'giáo trình'})
SET f2.course_code = '',
    f2.created_at = datetime(),
    f2.created_by = 'folder-course-linker';

// Tạo node cho "tham khảo"
MERGE (f3:`tham khảo` {name: 'tham khảo'})
SET f3.course_code = '',
    f3.created_at = datetime(),
    f3.created_by = 'folder-course-linker';

// ===== KIỂM TRA FOLDER NODES ĐÃ TẠO =====
MATCH (f)
WHERE any(label IN labels(f) WHERE label IN ['đề cương', 'giáo trình', 'tham khảo'])
RETURN f.name AS folder_name,
       head(labels(f)) AS label,
       f.course_code AS course_code,
       f.created_at AS created_at
ORDER BY f.name;
