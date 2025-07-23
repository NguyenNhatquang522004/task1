# 🚀 Hướng dẫn sử dụng Folder Course Linker

## 📋 Tổng quan
Project này tạo và liên kết folder nodes với course khung sườn trong Neo4j database.

## ⚙️ Cài đặt

### 1. Copy file cấu hình
```bash
cd folder-course-linker
cp .env.example .env
```

### 2. Chỉnh sửa file .env
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_actual_password
NEO4J_DATABASE=neo4j
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Cách sử dụng nhanh

### Chạy tự động (KHUYẾN NGHỊ)
```bash
cd folder-course-linker
cp .env.example .env
# Chỉnh sửa .env với thông tin Neo4j của bạn
pip install -r requirements.txt
python main.py
```

Script sẽ tự động:
1. ✅ Phân tích dữ liệu hiện tại
2. ✅ Tạo folder nodes với label = folder_name
3. ✅ Tạo relationships POINT_TO
4. ✅ Validation và báo cáo kết quả

### Chạy với menu (CHO ADVANCED USER)
```bash
python main_interactive.py
```

## 🎯 Chức năng chính

### 1. Phân tích dữ liệu hiện tại
```bash
python data_analyzer.py
```
Hoặc trong menu chọn option 1.

Báo cáo sẽ hiển thị:
- Số lượng Course khung sườn (node chỉ có 1 label là Course)
- Số lượng Document nodes có/không có folder_name
- Danh sách folder_name unique
- Thống kê folder nodes và relationships đã tồn tại

### 2. Tạo folder nodes
```bash
python folder_node_creator.py
```

Quá trình này sẽ:
- Lấy tất cả folder_name từ Document nodes
- Tạo node với label = folder_name
- Set properties: name, course_code, created_at, created_by

### 3. Tạo relationships
```bash
python relationship_builder.py
```

Quá trình này sẽ:
- Tạo relationship POINT_TO từ mỗi Course khung sườn đến tất cả folder nodes
- Set course_code cho folder nodes
- Validate số lượng relationships

### 4. Chạy toàn bộ (TỰ ĐỘNG)
```bash
python main.py
```

Script sẽ tự động thực hiện tất cả các bước:
1. Phân tích dữ liệu hiện tại
2. Tạo folder nodes (tự động xóa nodes cũ nếu có)
3. Tạo relationships (tự động xóa relationships cũ nếu có)
4. Validation và báo cáo kết quả

### 5. Chạy với menu interactive (TÙY CHỌN)
```bash
python main_interactive.py
```

Menu interactive với các options:
- 1: Phân tích dữ liệu
- 2: Tạo folder nodes
- 3: Tạo relationships  
- 4: Chạy toàn bộ (2+3)
- 5: Xóa tất cả dữ liệu đã tạo
- 0: Thoát

## 🗃️ Cấu trúc dữ liệu được tạo

### Folder Nodes
```
(folder_node:folder_name {
    name: "đề cương",
    course_code: "CMP170",
    created_at: "2025-01-20T...",
    created_by: "folder-course-linker"
})
```

### Relationships
```
(course:Course)-[:POINT_TO]->(folder_node:folder_name)
```

## 📊 Ví dụ kết quả

Nếu có:
- 60 Course khung sườn
- 3 folder_name unique: ["đề cương", "giáo trình", "tham khảo"]

Sẽ tạo:
- 3 folder nodes
- 180 relationships POINT_TO (60 × 3)

## 🔍 Queries kiểm tra

### Xem tất cả folder nodes
```cypher
MATCH (f)
WHERE f.created_by = 'folder-course-linker'
RETURN f.name, head(labels(f)), f.course_code
```

### Xem relationships
```cypher
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
RETURN c.code, c.name, f.name
ORDER BY c.code, f.name
```

### Đếm relationships
```cypher
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
RETURN count(DISTINCT c) AS courses,
       count(DISTINCT f) AS folders,
       count(r) AS total_relationships
```

## 🧹 Cleanup

### Xóa tất cả relationships
```cypher
MATCH (c:Course)-[r:POINT_TO]->(f)
WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
DELETE r
```

### Xóa tất cả folder nodes
```cypher
MATCH (f)
WHERE f.created_by = 'folder-course-linker'
DELETE f
```

## ⚠️ Lưu ý quan trọng

1. **Backup database** trước khi chạy
2. Tool chỉ tạo relationships với Course khung sườn (size(labels(c)) = 1)
3. Tool không ảnh hưởng đến dữ liệu hiện có
4. Tất cả thay đổi được đánh dấu với `created_by = 'folder-course-linker'`
5. Có thể chạy lại nhiều lần (sẽ merge, không duplicate)

## 🐛 Troubleshooting

### Lỗi kết nối Neo4j
- Kiểm tra file .env
- Đảm bảo Neo4j đang chạy
- Kiểm tra username/password

### Không tìm thấy folder_name
- Chạy phân tích trước: `python data_analyzer.py`
- Kiểm tra Document nodes có property folder_name

### Số relationships không đúng
- Chạy validation trong menu option 3
- Kiểm tra có Course nodes bị duplicate không
