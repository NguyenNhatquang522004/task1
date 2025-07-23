# Folder Selection Feature Documentation

## 🎯 Mục đích
Cho phép người dùng chọn `folder_name` khi upload file để tổ chức documents theo thư mục/danh mục trong Neo4j database.

## 🔧 Triển khai đã hoàn thành

### 1. Backend API Endpoints

#### A. GET /folders - Lấy danh sách folders có sẵn
```
GET http://localhost:8001/folders?uri={neo4j_uri}&userName={username}&password={password}&database={database}
```

**Response:**
```json
{
  "status": "Success",
  "message": "Folders retrieved successfully", 
  "data": [
    "đề cương",
    "giáo trình",
    "tham khảo",
    "nội bộ",
    "chính thức"
  ]
}
```

#### B. POST /upload - Upload file với folder_name
Existing endpoint đã được cập nhật để nhận parameter `folder_name`:

```
POST http://localhost:8001/upload
Content-Type: multipart/form-data

Parameters:
- file: File upload
- originalname: Tên file
- folder_name: Tên folder (mới thêm)
- course_code: Mã môn học
- model: Model để xử lý
- ... (các parameters khác)
```

### 2. Database Schema
Document node trong Neo4j đã có thuộc tính `folder_name`:

```cypher
MATCH (d:Document) 
RETURN d.fileName, d.folder_name, d.course_code, d.schema
```

### 3. Auto Schema Detection
Khi có `folder_name`, hệ thống sẽ tự động detect schema phù hợp:

| Folder Name | Schema | Triplet | Additional Instructions |
|-------------|--------|---------|------------------------|
| "đề cương" / "de cuong" | decuong | decuong | note/notedecuong.txt |
| "giáo trình" / "giao trinh" / "chính thức" | giaotrinh | giaotrinh | note/notegiaotrinh.txt |
| "tham khảo" / "ngoại bộ" / "nội bộ" | ebook | ebook | note/noteEbook.txt |
| Khác | default | default | None |

## 🧪 Testing

### Test API Folders:
```bash
c:\edu\task1\llm-graph-builder\.venv\Scripts\python.exe c:\edu\task1\llm-graph-builder\backend\test_folder_selection.py
```

### Test Upload với Folder:
Script test sẽ tự động:
1. Gọi API `/folders` để lấy danh sách
2. Upload file test với `folder_name = "đề cương"`
3. Verify kết quả

## 🎨 Frontend Integration (Cần triển khai)

### 1. Add Folder Selector to Upload Form
Thêm vào upload form:

```javascript
// Fetch available folders
const fetchFolders = async () => {
  const response = await fetch(`/api/folders?uri=${uri}&userName=${userName}&password=${password}&database=${database}`);
  const data = await response.json();
  return data.data || [];
};

// Folder selection component
<select name="folder_name" onChange={handleFolderChange}>
  <option value="">-- Chọn thư mục --</option>
  {folders.map(folder => (
    <option key={folder} value={folder}>{folder}</option>
  ))}
</select>
```

### 2. Auto-populate Schema based on Folder
```javascript
const handleFolderChange = (folder) => {
  // Auto-detect schema based on folder
  const schemaMapping = {
    'đề cương': 'decuong',
    'giáo trình': 'giaotrinh', 
    'tham khảo': 'ebook'
  };
  
  const detectedSchema = schemaMapping[folder] || 'default';
  setSelectedSchema(detectedSchema);
};
```

## 📊 Database Queries cho Admin

### Xem documents theo folder:
```cypher
MATCH (d:Document)
WHERE d.folder_name IS NOT NULL
RETURN d.folder_name, count(*) as document_count
ORDER BY document_count DESC
```

### Xem documents trong một folder cụ thể:
```cypher
MATCH (d:Document {folder_name: "đề cương"})
RETURN d.fileName, d.status, d.schema, d.course_code
ORDER BY d.createdAt DESC
```

### Thống kê theo folder và schema:
```cypher
MATCH (d:Document)
WHERE d.folder_name IS NOT NULL
RETURN d.folder_name, d.schema, count(*) as count
ORDER BY d.folder_name, count DESC
```

## 🔄 Migration cho Documents cũ

Nếu có documents cũ chưa có `folder_name`, có thể chạy migration:

```cypher
// Auto-assign folder based on filename patterns
MATCH (d:Document)
WHERE d.folder_name IS NULL
AND (toLower(d.fileName) CONTAINS "đề cương" 
     OR toLower(d.fileName) CONTAINS "de cuong")
SET d.folder_name = "đề cương"
RETURN count(*) as updated_count
```

## ✅ Tính năng đã sẵn sàng sử dụng

1. **✅ Backend API** - Hoàn thành
2. **✅ Database Schema** - Hoàn thành  
3. **✅ Auto Schema Detection** - Hoàn thành
4. **✅ Upload Logic** - Hoàn thành
5. **⏳ Frontend UI** - Cần triển khai
6. **✅ Testing Scripts** - Hoàn thành

## 🚀 Cách sử dụng ngay bây giờ

Có thể test ngay bằng cách:
1. Chạy backend server
2. Dùng Postman hoặc script test để gọi API
3. Upload file với parameter `folder_name`
4. Verify trong Neo4j browser

```cypher
MATCH (d:Document)
WHERE d.folder_name IS NOT NULL
RETURN d.fileName, d.folder_name, d.schema
LIMIT 10
```
