// ===== PHÂN TÍCH DỮ LIỆU HIỆN TẠI =====

// 1. Kiểm tra các Course khung sườn (chỉ có 1 label là Course)
MATCH (c:Course)
WHERE size(labels(c)) = 1
RETURN 'Course khung sườn' AS type, 
       count(c) AS total_count, 
       collect(c.code)[0..10] AS sample_codes
UNION ALL

// 2. Kiểm tra các node Course có nhiều label (không phải khung sườn)
MATCH (c:Course)
WHERE size(labels(c)) > 1
RETURN 'Course nhiều label' AS type,
       count(c) AS total_count,
       collect(c.code)[0..10] AS sample_codes
UNION ALL

// 3. Kiểm tra các Document nodes và folder_name
MATCH (d:Document)
WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
RETURN 'Document có folder_name' AS type,
       count(d) AS total_count,
       collect(DISTINCT d.folder_name) AS unique_folder_names
UNION ALL

// 4. Kiểm tra Document nodes không có folder_name
MATCH (d:Document)
WHERE d.folder_name IS NULL OR trim(d.folder_name) = ''
RETURN 'Document không có folder_name' AS type,
       count(d) AS total_count,
       [] AS unique_folder_names;

// ===== DANH SÁCH CHI TIẾT =====

// Danh sách tất cả Course khung sườn
MATCH (c:Course)
WHERE size(labels(c)) = 1
RETURN 'COURSE KHUNG SƯỜN: ' + c.code + ' - ' + c.name AS info
ORDER BY c.code
LIMIT 20;

// Danh sách folder_name unique
MATCH (d:Document)
WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
WITH DISTINCT trim(d.folder_name) AS folder_name
RETURN 'FOLDER_NAME: ' + folder_name AS info
ORDER BY folder_name;
